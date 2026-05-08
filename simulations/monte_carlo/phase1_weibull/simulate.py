"""
simulate.py — Weibull Monte Carlo engine for joint-failure reliability.

Ports the exponential simulation from joint_reliability.py to Weibull(β, η)
with three additional per-joint state arrays:
  t_snapshot[j]     — absolute time of last scale change or birth
  H_snapshot[j]     — cumulative hazard at t_snapshot
  current_scale[j]  — current Weibull scale = 1/λ_current

TTF draw sites (4 in the original code) are replaced:
  1. Initial draw          → rng.weibull(β) * scale
  2. Stress-change redraw  → conditional_weibull_remaining (aging, chained H)
  3. Repair redraw         → fresh_weibull_ttf (new clock)
"""

import numpy as np

from simulations.monte_carlo.phase1_weibull.hazard_model import (
    calibrate_arrhenius,
    compute_hazard_rates,
    compute_joint_positions,
    conditional_weibull_remaining,
    draw_weibull_ttf,
    fresh_weibull_ttf,
    load_params,
    thermal_profile_3zone,
)

# Maximum cumulative hazard (must match hazard_model._H_CLIP)
_H_CLIP = 700.0


# ---------------------------------------------------------------------------
# Single-trajectory Weibull simulation (with cascading failures)
# ---------------------------------------------------------------------------
def simulate_one_weibull(
    ttf: np.ndarray,
    joint_alts: np.ndarray,
    base_hazard: np.ndarray,
    N: int,
    eta_j: float,
    cadence: int,
    p_detection: float,
    lambda_0_pre: float,
    params: dict,
    beta: float,
    rng: np.random.Generator,
) -> dict:
    """
    Simulate one 10-year trajectory with Weibull failure model.

    Port of _simulate_one_from_ttf() (joint_reliability.py lines 572-696)
    with added Weibull state tracking: t_snapshot, H_snapshot, current_scale.

    Parameters
    ----------
    ttf : ndarray (n_joints,) — pre-drawn initial time-to-failure.
    joint_alts : ndarray (n_joints,) — joint altitudes [m].
    base_hazard : ndarray (n_joints,) — baseline hazard rates [1/h].
    N : int — number of tether segments.
    eta_j : float — joint efficiency.
    cadence : int — inspection cadence [climber passages].
    p_detection : float — detection probability per inspection.
    lambda_0_pre : float — calibrated Arrhenius pre-exponential [1/h].
    params : dict — master parameters.
    beta : float — Weibull shape parameter.
    rng : numpy Generator.

    Returns
    -------
    dict with keys: survived, failure_time, repairs, mttr
    """
    t_mission = float(params["monte_carlo"]["t_mission"])
    t_replace = float(params["monte_carlo"]["t_joint_replace"])
    v_climber = float(params["climber"]["v_climber"])
    L_total = float(params["tether"]["L_total"])

    n_joints = N - 1
    t_traversal = L_total / v_climber / 3600.0  # hours
    t_between = cadence * t_traversal

    # Stress state (normalised: 1.0 = nominal)
    sigma_nominal = np.ones(n_joints)
    sigma_current = sigma_nominal.copy()
    eff_hazard = base_hazard.copy()
    cascade_threshold = 2.0  # SF = 2

    # --- Weibull state arrays ---
    t_snapshot = np.zeros(n_joints)            # birth time (init: 0)
    H_snapshot = np.zeros(n_joints)            # cumulative hazard at snapshot
    current_scale = 1.0 / base_hazard.copy()   # η = 1/λ

    failed_set = set()
    repairs = 0
    mttr_list = []
    t_current = 0.0

    while t_current < t_mission:
        t_next = min(t_current + t_between, t_mission)

        # --- New failures in [t_current, t_next) ---
        new_fail_mask = (ttf >= t_current) & (ttf < t_next)
        new_fail_indices = np.where(new_fail_mask)[0]

        if len(new_fail_indices) > 0:
            order = np.argsort(ttf[new_fail_indices])
            new_fail_indices = new_fail_indices[order]

            for idx in new_fail_indices:
                if idx in failed_set:
                    continue
                failed_set.add(idx)

                # Adjacent unrepaired → instant system failure
                if (idx - 1) in failed_set or (idx + 1) in failed_set:
                    return {"survived": False, "failure_time": float(ttf[idx]),
                            "repairs": repairs, "mttr": mttr_list}

                # --- Load redistribution ---
                load = sigma_current[idx]
                left = idx - 1 if idx > 0 else None
                right = idx + 1 if idx < n_joints - 1 else None
                if left is not None and right is not None:
                    sigma_current[left] += load / 2.0
                    sigma_current[right] += load / 2.0
                elif left is not None:
                    sigma_current[left] += load
                elif right is not None:
                    sigma_current[right] += load

                # --- Cascade check ---
                for nb in [left, right]:
                    if nb is not None and nb not in failed_set:
                        if sigma_current[nb] > cascade_threshold:
                            return {"survived": False,
                                    "failure_time": float(ttf[idx]),
                                    "repairs": repairs, "mttr": mttr_list}

                # --- Sub-critical overload: Weibull conditional remaining life ---
                t_event = float(ttf[idx])
                for nb in [left, right]:
                    if nb is not None and nb not in failed_set:
                        sr = sigma_current[nb] / sigma_nominal[nb]
                        eff_hazard[nb] = base_hazard[nb] * sr ** 4

                        # Compute total accumulated hazard up to t_event
                        # (includes H_snapshot from any prior scale changes)
                        t_age = t_event - t_snapshot[nb]
                        H_accum = H_snapshot[nb] + (t_age / current_scale[nb]) ** beta
                        H_accum = min(H_accum, _H_CLIP)

                        new_scale = 1.0 / eff_hazard[nb]
                        delta_t = conditional_weibull_remaining(
                            H_accum, new_scale, beta, rng)
                        ttf[nb] = t_event + delta_t

                        # Update Weibull state
                        H_snapshot[nb] = H_accum
                        t_snapshot[nb] = t_event
                        current_scale[nb] = new_scale

        # --- End of mission with unrepaired failures ---
        if t_next >= t_mission:
            if failed_set:
                earliest = min(ttf[j] for j in failed_set)
                return {"survived": False, "failure_time": float(earliest),
                        "repairs": repairs, "mttr": mttr_list}
            break

        # --- Inspection at t_next ---
        repaired = []
        for idx in list(failed_set):
            if rng.random() < p_detection:
                travel = float(joint_alts[idx]) / v_climber / 3600.0
                wait = t_next - float(ttf[idx])
                mttr_list.append(wait + travel + t_replace)
                repairs += 1
                repaired.append(idx)

        # --- Apply repairs (fresh Weibull draws, reset state) ---
        for idx in repaired:
            failed_set.discard(idx)
            eff_hazard[idx] = base_hazard[idx]
            sigma_current[idx] = sigma_nominal[idx]

            # Fresh joint — new clock
            H_snapshot[idx] = 0.0
            t_snapshot[idx] = t_next
            current_scale[idx] = 1.0 / base_hazard[idx]
            ttf[idx] = t_next + fresh_weibull_ttf(beta, current_scale[idx], rng)

        # --- Recalculate stress state after repairs ---
        if repaired:
            sigma_current[:] = sigma_nominal[:]
            eff_hazard[:] = base_hazard[:]
            # Reset Weibull state for non-failed joints whose stress returns to nominal
            for j_idx in range(n_joints):
                if j_idx not in failed_set:
                    # Accumulate hazard up to t_next before resetting scale
                    t_age = t_next - t_snapshot[j_idx]
                    H_accum = H_snapshot[j_idx] + (t_age / current_scale[j_idx]) ** beta
                    H_accum = min(H_accum, _H_CLIP)
                    H_snapshot[j_idx] = H_accum
                    t_snapshot[j_idx] = t_next
                    current_scale[j_idx] = 1.0 / base_hazard[j_idx]

            # Re-apply load redistribution for remaining failures
            for fidx in failed_set:
                load = sigma_nominal[fidx]
                left = fidx - 1 if fidx > 0 else None
                right = fidx + 1 if fidx < n_joints - 1 else None
                if left is not None and right is not None:
                    sigma_current[left] += load / 2.0
                    sigma_current[right] += load / 2.0
                elif left is not None:
                    sigma_current[left] += load
                elif right is not None:
                    sigma_current[right] += load

            for fidx in failed_set:
                for nb in [fidx - 1 if fidx > 0 else None,
                           fidx + 1 if fidx < n_joints - 1 else None]:
                    if nb is not None and nb not in failed_set:
                        sr = sigma_current[nb] / sigma_nominal[nb]
                        eff_hazard[nb] = base_hazard[nb] * sr ** 4

                        # Update scale (hazard snapshot already set above)
                        new_scale = 1.0 / eff_hazard[nb]
                        current_scale[nb] = new_scale

                        # Redraw TTF under new stress
                        E = rng.standard_exponential()
                        H_total = H_snapshot[nb] + E
                        delta_t = new_scale * (
                            H_total ** (1.0 / beta)
                            - H_snapshot[nb] ** (1.0 / beta))
                        ttf[nb] = t_next + max(delta_t, 0.0)

        t_current = t_next

    return {"survived": True, "failure_time": None,
            "repairs": repairs, "mttr": mttr_list}


# ---------------------------------------------------------------------------
# Vectorized batch simulation
# ---------------------------------------------------------------------------
def run_batch_weibull(
    N: int,
    eta_j: float,
    cadence: int,
    p_detection: float,
    lambda_0_pre: float,
    params: dict,
    n_traj: int,
    beta: float,
    seed: int,
) -> dict:
    """
    Run n_traj Monte Carlo trajectories for a single parameter combination.

    Vectorises the initial TTF draw, pre-screens trivial survivors, then
    falls back to per-trajectory simulate_one_weibull() for cascade logic.

    Returns
    -------
    dict with keys: P_sys, mean_repairs, median_MTTR, p05_MTTR, p95_MTTR,
                    n_failures, MTTR_samples
    """
    t_mission = float(params["monte_carlo"]["t_mission"])
    v_climber = float(params["climber"]["v_climber"])
    L_total = float(params["tether"]["L_total"])

    n_joints = N - 1
    if n_joints <= 0:
        return {
            "P_sys": 1.0, "mean_repairs": 0.0,
            "median_MTTR": 0.0, "p05_MTTR": 0.0, "p95_MTTR": 0.0,
            "n_failures": 0, "MTTR_samples": np.array([]),
        }

    # Joint geometry and hazard
    joint_alts = compute_joint_positions(N, params)
    joint_temps = thermal_profile_3zone(joint_alts)
    hazard = compute_hazard_rates(eta_j, joint_temps, lambda_0_pre, params)
    scales = 1.0 / hazard  # Weibull characteristic life per joint

    # --- Vectorized initial TTF draw: shape (n_traj, n_joints) ---
    rng = np.random.default_rng(seed=seed)
    ttf_all = draw_weibull_ttf(beta, scales, rng, size=(n_traj, n_joints))

    # --- Pre-screen: trajectories with min(TTF) > t_mission trivially survive ---
    min_ttf = np.min(ttf_all, axis=1)
    trivial_survive = min_ttf > t_mission
    need_sim = np.where(~trivial_survive)[0]

    survivals = int(np.sum(trivial_survive))
    all_mttr = []
    total_repairs = 0

    # --- Per-trajectory cascade simulation ---
    for traj_idx in need_sim:
        traj_rng = np.random.default_rng(seed=seed + 2_000_000 + int(traj_idx))
        result = simulate_one_weibull(
            ttf_all[traj_idx].copy(),
            joint_alts, hazard,
            N, eta_j, cadence, p_detection, lambda_0_pre,
            params, beta, traj_rng,
        )
        if result["survived"]:
            survivals += 1
        total_repairs += result["repairs"]
        all_mttr.extend(result["mttr"])

    P_sys = min(1.0, max(0.0, survivals / n_traj))
    mttr_arr = np.array(all_mttr) if all_mttr else np.array([])
    median_mttr = float(np.median(mttr_arr)) if len(mttr_arr) > 0 else 0.0
    p05_mttr = float(np.percentile(mttr_arr, 5)) if len(mttr_arr) > 0 else 0.0
    p95_mttr = float(np.percentile(mttr_arr, 95)) if len(mttr_arr) > 0 else 0.0

    return {
        "P_sys": P_sys,
        "mean_repairs": total_repairs / n_traj,
        "median_MTTR": median_mttr,
        "p05_MTTR": p05_mttr,
        "p95_MTTR": p95_mttr,
        "n_failures": n_traj - survivals,
        "MTTR_samples": mttr_arr,
    }
