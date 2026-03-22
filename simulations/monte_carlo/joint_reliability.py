"""
joint_reliability.py — Monte Carlo joint-failure reliability simulation

Simulates system-level failure probability P_sys as a function of joint
efficiency (eta_j), segment count (N), inspection cadence, and detection
probability over a 10-year mission.

Joint lifetime model (corrected Arrhenius — see §4.2.3):
    The paper states λ̄_j = 1.2e-8 h⁻¹ is the MISSION-AVERAGED hazard rate
    obtained by integrating λ_0·exp(−Q/kT) over the orbital thermal profile.
    We back-derive the true pre-exponential λ_0_pre so that averaging
    λ_0_pre·exp(−Q/kT_j) over the 3-zone profile recovers λ̄.

    Weibull volume scaling (coupon → full-scale sleeve) is applied first:
        λ̄_fullscale = λ̄_coupon × volume_scale_factor

    Per-joint hazard rate:
        λ_j = λ_0_pre × exp(−Q/(k_B T_j)) × (0.97/η_j)⁴

Cascading failure model:
    When a joint fails and is not yet detected, its load is redistributed
    to neighbours.  If the resulting stress exceeds σ_allow, the neighbour
    fails immediately (cascade).  Two adjacent unrepaired failures → instant
    system failure.

Usage:
    # Quick test (1K trajectories)
    python simulations/monte_carlo/joint_reliability.py --n-trajectories 1000

    # Full sweep (100K trajectories)
    python simulations/monte_carlo/joint_reliability.py --n-trajectories 100000

    # Single baseline point
    python simulations/monte_carlo/joint_reliability.py --n-trajectories 1000 --single

    # GPU-accelerated
    python simulations/monte_carlo/joint_reliability.py --gpu --n-trajectories 100000

Outputs:
    data/processed/psys_surface.npz
    data/processed/mttr_samples.npz
    paper/figures/fig_psys_heatmap.pdf
    paper/figures/fig_mttr_distribution.pdf
    paper/figures/fig_inspection_cadence.pdf
    paper/figures/fig_p_detection_impact.pdf

Reference:
    Wright, Patel & Liddle (2023) — joint efficiency data
    Luo et al. (2022) — segmented tether optimization
"""

import argparse
import time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
PARAMS_FILE = ROOT / "data" / "parameters.yaml"
OUTPUT_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "paper" / "figures"
STYLE_FILE = ROOT / "scripts" / "acta_astronautica.mplstyle"


def load_params(path: Path = PARAMS_FILE) -> dict:
    """Load the locked master parameter file, casting all numerics to float."""
    with open(path) as f:
        raw = yaml.safe_load(f)

    def try_float(v):
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v
        return v

    def cast(d):
        out = {}
        for k, v in d.items():
            if isinstance(v, dict):
                out[k] = cast(v)
            elif isinstance(v, list):
                out[k] = [try_float(x) for x in v]
            else:
                out[k] = try_float(v)
        return out

    return cast(raw)


# ---------------------------------------------------------------------------
# Array library selector (numpy / cupy)
# ---------------------------------------------------------------------------
def get_array_module(use_gpu: bool):
    """Return numpy or cupy depending on --gpu flag."""
    if use_gpu:
        try:
            import cupy as cp
            print("  GPU backend: CuPy (CUDA)")
            return cp
        except ImportError:
            print("  WARNING: CuPy not available — falling back to NumPy CPU")
            return np
    return np


# ---------------------------------------------------------------------------
# Thermal profile: 3-zone simplified model
# ---------------------------------------------------------------------------
def thermal_profile_3zone(altitude, xp=np):
    """
    Simplified 3-zone temperature profile along the tether.

    Zone 1: 0 – 200 km         → 250 K  (atmosphere/low LEO, shadowed)
    Zone 2: 200 km – 35,786 km → 280 K  (LEO to GEO, mixed illumination)
    Zone 3: > 35,786 km        → 300 K  (cislunar, full sunlight)

    Parameters
    ----------
    altitude : ndarray
        Altitude above Earth's surface [m].
    xp : module
        numpy or cupy.

    Returns
    -------
    ndarray  — Temperature at each position [K].
    """
    T = xp.full_like(altitude, 280.0, dtype=xp.float64)
    T[altitude < 200e3] = 250.0
    T[altitude > 35.786e6] = 300.0
    return T


# ---------------------------------------------------------------------------
# Joint geometry helpers
# ---------------------------------------------------------------------------
def compute_joint_positions(N: int, params: dict, xp=np):
    """
    Compute the altitude of each joint for an N-segment tether.
    Joints are at segment boundaries (N-1 internal joints), equal spacing.
    Returns ndarray of shape (N-1,) — joint altitudes [m].
    """
    L_total = float(params["tether"]["L_total"])
    return xp.linspace(L_total / N, L_total * (N - 1) / N, N - 1)


# ---------------------------------------------------------------------------
# Arrhenius calibration  (FIX A — the key physics correction)
# ---------------------------------------------------------------------------
def calibrate_arrhenius(params: dict, xp=np):
    """
    Back-derive the true pre-exponential λ_0_pre from the mission-averaged
    hazard rate reported in the paper.

    Steps:
      1. Compute full-scale mission-averaged rate:
         λ̄_fullscale = λ̄_coupon × volume_scale_factor
      2. Get joint positions for baseline N=18 and their temperatures.
      3. Compute mean Arrhenius factor <exp(-Q/kT)> weighted by joint count.
      4. λ_0_pre = λ̄_fullscale / <exp(-Q/kT)>

    Returns
    -------
    lambda_0_pre : float
        The true pre-exponential factor [1/h].
    """
    lambda_0_bar = float(params["joints"]["lambda_0_bar"])       # 1.2e-8
    volume_scale = float(params["joints"]["volume_scale_factor"])  # 4.3
    Q = float(params["joints"]["Q_activation"])                    # 1.76e-19 J
    k_B = float(params["physical"]["k_B"])                         # 1.38e-23 J/K

    lambda_0_fullscale_bar = lambda_0_bar * volume_scale  # 5.16e-8

    # Baseline geometry for calibration
    N_base = int(params["segments"]["N_baseline"])  # 18
    alts = compute_joint_positions(N_base, params, xp=np)  # always numpy here
    temps = thermal_profile_3zone(alts, xp=np)

    # Mean Arrhenius factor over joints
    arrhenius_factors = np.exp(-Q / (k_B * temps))
    mean_arrhenius = float(np.mean(arrhenius_factors))

    lambda_0_pre = lambda_0_fullscale_bar / mean_arrhenius

    # ---------- Self-consistency check ----------
    recovered = float(lambda_0_pre * mean_arrhenius)
    per_joint_rates = lambda_0_pre * arrhenius_factors  # no efficiency correction
    mean_recovered = float(np.mean(per_joint_rates))

    print(f"\n  ARRHENIUS CALIBRATION (FIX A)")
    print(f"  {'lambda_0_bar (coupon)':.<40s} {lambda_0_bar:.3e} 1/h")
    print(f"  {'volume_scale_factor':.<40s} {volume_scale:.2f}")
    print(f"  {'lambda_0_fullscale_bar':.<40s} {lambda_0_fullscale_bar:.3e} 1/h")
    print(f"  {'<exp(-Q/kT)> over {N_base} baseline joints':.<40s} {mean_arrhenius:.6e}")
    print(f"  {'Derived lambda_0_pre':.<40s} {lambda_0_pre:.6e} 1/h")
    print(f"  {'Self-check: lambda_0_pre * <exp>':.<40s} {recovered:.3e} 1/h "
          f"(target {lambda_0_fullscale_bar:.3e})")
    print(f"  {'Mean recovered per-joint rate':.<40s} {mean_recovered:.3e} 1/h")

    # 10-year failure probability at baseline eta_j=0.95
    eta_base = float(params["design"]["eta_j_baseline"])
    t_mission = float(params["monte_carlo"]["t_mission"])
    baseline_rate = mean_recovered * (0.97 / eta_base) ** 4
    p_fail_10yr = 1.0 - np.exp(-baseline_rate * t_mission)
    print(f"  {'Baseline per-joint 10yr P_fail':.<40s} {p_fail_10yr:.6f} "
          f"(rate={baseline_rate:.3e} 1/h)")

    return lambda_0_pre


# ---------------------------------------------------------------------------
# Per-joint hazard rates (vectorized)
# ---------------------------------------------------------------------------
def compute_hazard_rates(eta_j: float, temps, lambda_0_pre: float,
                         params: dict, xp=np):
    """
    Compute hazard rate for each joint given local temperatures.

    λ_j = λ_0_pre × exp(−Q/(k_B T_j)) × (0.97/η_j)⁴

    Parameters
    ----------
    eta_j : float
    temps : ndarray of shape (n_joints,) — temperatures [K]
    lambda_0_pre : float — calibrated pre-exponential [1/h]
    params : dict
    xp : array module

    Returns
    -------
    ndarray of shape (n_joints,) — hazard rates [1/h]
    """
    Q = float(params["joints"]["Q_activation"])
    k_B = float(params["physical"]["k_B"])
    efficiency_factor = (0.97 / eta_j) ** 4
    return lambda_0_pre * xp.exp(-Q / (k_B * temps)) * efficiency_factor


# ---------------------------------------------------------------------------
# Single trajectory simulation — with cascading failures (FIX C)
# ---------------------------------------------------------------------------
def simulate_trajectory(N: int, eta_j: float, inspection_cadence: int,
                        p_detection: float, lambda_0_pre: float,
                        params: dict, rng: np.random.Generator) -> dict:
    """
    Simulate one 10-year trajectory of a tether with N segments (N-1 joints).

    Cascading failure model:
      - When joint j fails (undetected), its tension is shared by neighbours.
      - If redistributed stress > sigma_allow → immediate cascade (system fail).
      - Two adjacent unrepaired failures → instant system failure.
      - Sub-critical overload: neighbour hazard rate × (σ_new/σ_nom)^4.

    Returns
    -------
    dict with keys: survived, failure_time, repairs, mttr
    """
    t_mission = float(params["monte_carlo"]["t_mission"])
    t_replace = float(params["monte_carlo"]["t_joint_replace"])
    v_climber = float(params["climber"]["v_climber"])
    L_total = float(params["tether"]["L_total"])
    sigma_allow = float(params["design"]["sigma_allow"])

    n_joints = N - 1
    if n_joints <= 0:
        return {"survived": True, "failure_time": None, "repairs": 0, "mttr": []}

    # Joint positions and temperatures
    joint_alts = compute_joint_positions(N, params)
    joint_temps = thermal_profile_3zone(joint_alts)

    # Baseline hazard rates (no stress amplification yet)
    base_hazard = compute_hazard_rates(eta_j, joint_temps, lambda_0_pre, params)

    # Nominal tension per joint (simplified: equal share of design load)
    # sigma_design * A  spread over N-1 joints → each carries T_nominal
    # We work in normalised stress: σ_nominal = 1.0 (relative units)
    sigma_nominal = np.ones(n_joints)
    sigma_current = sigma_nominal.copy()

    # Current effective hazard rates (may increase with overload)
    eff_hazard = base_hazard.copy()

    # Climber traversal time
    t_traversal = L_total / v_climber / 3600.0  # s → h
    t_between = inspection_cadence * t_traversal

    # Draw initial TTF for each joint
    ttf = rng.exponential(1.0 / eff_hazard)

    # State tracking
    failed_set = set()  # indices of currently-failed (unrepaired) joints
    repairs = 0
    mttr_list = []
    t_current = 0.0

    while t_current < t_mission:
        t_next = min(t_current + t_between, t_mission)

        # --- Check for new failures in [t_current, t_next) ---
        # Sort pending failures by time
        new_fail_mask = (ttf >= t_current) & (ttf < t_next)
        new_fail_indices = np.where(new_fail_mask)[0]

        if len(new_fail_indices) > 0:
            # Process in chronological order
            order = np.argsort(ttf[new_fail_indices])
            new_fail_indices = new_fail_indices[order]

            for idx in new_fail_indices:
                if idx in failed_set:
                    continue  # already failed

                failed_set.add(idx)

                # --- Check for two adjacent unrepaired failures ---
                if (idx - 1) in failed_set or (idx + 1) in failed_set:
                    return {
                        "survived": False,
                        "failure_time": float(ttf[idx]),
                        "repairs": repairs,
                        "mttr": mttr_list,
                    }

                # --- Load redistribution ---
                # Failed joint's normalised load shared by neighbours
                load_share = sigma_current[idx]
                left = idx - 1 if idx > 0 else None
                right = idx + 1 if idx < n_joints - 1 else None

                if left is not None and right is not None:
                    # Split equally
                    sigma_current[left] += load_share / 2.0
                    sigma_current[right] += load_share / 2.0
                elif left is not None:
                    sigma_current[left] += load_share
                elif right is not None:
                    sigma_current[right] += load_share
                # else: single joint, no neighbours (N=2 edge case)

                # --- Check cascade: does any neighbour exceed σ_allow? ---
                # In normalised units, σ_allow corresponds to
                # sigma_allow / sigma_design.  With SF=2:
                # sigma_design = sigma_allow (since sigma_allow = sigma_u/SF
                # and design stress = sigma_allow).  So threshold in
                # normalised units = sigma_allow / (sigma_allow * eta_j)
                # = 1/eta_j.  But more simply: cascade if the new stress
                # exceeds twice nominal (the safety factor).
                cascade_threshold = 2.0  # SF = 2 → can tolerate 2× nominal

                for nb in [left, right]:
                    if nb is not None and nb not in failed_set:
                        if sigma_current[nb] > cascade_threshold:
                            return {
                                "survived": False,
                                "failure_time": float(ttf[idx]),
                                "repairs": repairs,
                                "mttr": mttr_list,
                            }

                # --- Sub-critical overload: amplify neighbour hazard ---
                for nb in [left, right]:
                    if nb is not None and nb not in failed_set:
                        stress_ratio = sigma_current[nb] / sigma_nominal[nb]
                        eff_hazard[nb] = base_hazard[nb] * stress_ratio ** 4
                        # Redraw remaining TTF from this point with new rate
                        remaining = rng.exponential(1.0 / eff_hazard[nb])
                        ttf[nb] = ttf[idx] + remaining  # from failure time

        # --- Inspection at t_next (if not past mission end) ---
        if t_next >= t_mission:
            # Any unrepaired failures at mission end → system failure
            if failed_set:
                earliest = min(ttf[j] for j in failed_set)
                return {
                    "survived": False,
                    "failure_time": float(earliest),
                    "repairs": repairs,
                    "mttr": mttr_list,
                }
            break

        # Process inspection: try to detect each failed joint
        repaired_this_epoch = []
        for idx in list(failed_set):
            detected = rng.random() < p_detection

            if detected:
                # Repair
                travel_time = float(joint_alts[idx]) / v_climber / 3600.0
                wait_time = t_next - float(ttf[idx])
                repair_time = wait_time + travel_time + t_replace
                mttr_list.append(repair_time)
                repairs += 1
                repaired_this_epoch.append(idx)
            # else: stays failed, load redistribution persists

        # Apply repairs
        for idx in repaired_this_epoch:
            failed_set.discard(idx)

            # Restore stress on neighbours
            load_share = sigma_current[idx]  # its load was redistributed
            # Reset this joint's stress to nominal
            # Actually we need to undo the redistribution.  For simplicity,
            # recalculate from scratch based on remaining failures.

            # Reset hazard
            eff_hazard[idx] = base_hazard[idx]
            sigma_current[idx] = sigma_nominal[idx]

            # Draw new TTF for repaired joint
            ttf[idx] = t_next + rng.exponential(1.0 / eff_hazard[idx])

        # After repairs, recalculate stress redistribution for remaining failures
        if repaired_this_epoch and failed_set:
            # Reset all to nominal first
            sigma_current[:] = sigma_nominal[:]
            eff_hazard[:] = base_hazard[:]

            for fidx in failed_set:
                load_share = sigma_nominal[fidx]
                left = fidx - 1 if fidx > 0 else None
                right = fidx + 1 if fidx < n_joints - 1 else None
                if left is not None and right is not None:
                    sigma_current[left] += load_share / 2.0
                    sigma_current[right] += load_share / 2.0
                elif left is not None:
                    sigma_current[left] += load_share
                elif right is not None:
                    sigma_current[right] += load_share

            for fidx in failed_set:
                for nb in [fidx - 1 if fidx > 0 else None,
                           fidx + 1 if fidx < n_joints - 1 else None]:
                    if nb is not None and nb not in failed_set:
                        stress_ratio = sigma_current[nb] / sigma_nominal[nb]
                        eff_hazard[nb] = base_hazard[nb] * stress_ratio ** 4
        elif not failed_set and repaired_this_epoch:
            # All failures repaired — reset everything
            sigma_current[:] = sigma_nominal[:]
            eff_hazard[:] = base_hazard[:]

        t_current = t_next

    return {
        "survived": True,
        "failure_time": None,
        "repairs": repairs,
        "mttr": mttr_list,
    }


# ---------------------------------------------------------------------------
# Vectorized batch simulation (GPU-ready)  (FIX E)
# ---------------------------------------------------------------------------
def run_batch_vectorized(N: int, eta_j: float, cadence: int,
                         p_detection: float, lambda_0_pre: float,
                         params: dict, n_traj: int, seed: int = 42,
                         xp=np) -> dict:
    """
    Vectorized batch: draw all TTFs at once, process inspection epochs
    as array operations.  Falls back to per-trajectory loop for cascading
    failure book-keeping.

    For the GPU path (xp=cupy), the TTF draw and initial survival check
    are fully vectorized; cascade logic stays on CPU per-trajectory.
    """
    t_mission = float(params["monte_carlo"]["t_mission"])
    v_climber = float(params["climber"]["v_climber"])
    L_total = float(params["tether"]["L_total"])

    n_joints = N - 1
    if n_joints <= 0:
        return {
            "P_sys": 1.0, "MTTR_median": 0.0, "MTTR_mean": 0.0,
            "MTTR_samples": np.array([]), "n_repairs_mean": 0.0,
            "n_failures": 0,
        }

    # Joint positions and temperatures
    joint_alts = compute_joint_positions(N, params, xp=xp)
    joint_temps = thermal_profile_3zone(joint_alts, xp=xp)
    hazard = compute_hazard_rates(eta_j, joint_temps, lambda_0_pre, params, xp=xp)

    t_traversal = L_total / v_climber / 3600.0
    t_between = cadence * t_traversal

    # --- Vectorized TTF draw: shape (n_traj, n_joints) ---
    rng_xp = xp.random.default_rng if hasattr(xp.random, 'default_rng') else None

    if xp is np:
        rng = np.random.default_rng(seed=seed)
        # Draw all TTFs at once
        scales = 1.0 / hazard  # shape (n_joints,)
        ttf_all = rng.exponential(scale=scales, size=(n_traj, n_joints))
    else:
        # CuPy path
        rng_cp = xp.random.default_rng if hasattr(xp.random, 'default_rng') else None
        scales = 1.0 / hazard
        # CuPy exponential via uniform transform
        U = xp.random.uniform(0, 1, size=(n_traj, n_joints))
        ttf_all = -xp.log(U) * scales[xp.newaxis, :]

    # --- Quick vectorized pre-screen ---
    # Trajectories where NO joint fails within t_mission have P(survive)
    # dependent on detection.  But with cascading we need per-trajectory sim.
    # However, trajectories where min(TTF) > t_mission trivially survive.
    if xp is not np:
        ttf_all_np = xp.asnumpy(ttf_all)
        joint_alts_np = xp.asnumpy(joint_alts)
        joint_temps_np = xp.asnumpy(joint_temps)
        hazard_np = xp.asnumpy(hazard)
    else:
        ttf_all_np = ttf_all
        joint_alts_np = joint_alts
        hazard_np = hazard

    min_ttf = np.min(ttf_all_np, axis=1)  # (n_traj,)
    trivial_survive = min_ttf > t_mission

    # Trajectories that need detailed simulation
    need_sim = np.where(~trivial_survive)[0]

    survivals = int(np.sum(trivial_survive))
    all_mttr = []
    total_repairs = 0

    # Run detailed sim only for trajectories with at least one failure
    base_rng = np.random.default_rng(seed=seed + 1_000_000)
    for traj_idx in need_sim:
        # Use trajectory-specific RNG for detection/repair rolls
        traj_rng = np.random.default_rng(
            seed=seed + 2_000_000 + int(traj_idx)
        )
        result = _simulate_one_from_ttf(
            ttf_all_np[traj_idx].copy(),
            joint_alts_np, hazard_np,
            N, eta_j, cadence, p_detection, lambda_0_pre,
            params, traj_rng,
        )
        if result["survived"]:
            survivals += 1
        total_repairs += result["repairs"]
        all_mttr.extend(result["mttr"])

    P_sys = min(1.0, max(0.0, survivals / n_traj))
    mttr_arr = np.array(all_mttr) if all_mttr else np.array([])
    mttr_median = float(np.median(mttr_arr)) if len(mttr_arr) > 0 else 0.0
    mttr_mean = float(np.mean(mttr_arr)) if len(mttr_arr) > 0 else 0.0

    return {
        "P_sys": P_sys,
        "MTTR_median": mttr_median,
        "MTTR_mean": mttr_mean,
        "MTTR_samples": mttr_arr,
        "n_repairs_mean": total_repairs / n_traj,
        "n_failures": n_traj - survivals,
    }


def _simulate_one_from_ttf(ttf, joint_alts, base_hazard,
                            N, eta_j, cadence, p_detection, lambda_0_pre,
                            params, rng):
    """
    Simulate one trajectory given pre-drawn initial TTFs.
    Includes cascading failure logic.
    """
    t_mission = float(params["monte_carlo"]["t_mission"])
    t_replace = float(params["monte_carlo"]["t_joint_replace"])
    v_climber = float(params["climber"]["v_climber"])
    L_total = float(params["tether"]["L_total"])

    n_joints = N - 1
    t_traversal = L_total / v_climber / 3600.0
    t_between = cadence * t_traversal

    sigma_nominal = np.ones(n_joints)
    sigma_current = sigma_nominal.copy()
    eff_hazard = base_hazard.copy()
    cascade_threshold = 2.0  # SF = 2

    failed_set = set()
    repairs = 0
    mttr_list = []
    t_current = 0.0

    while t_current < t_mission:
        t_next = min(t_current + t_between, t_mission)

        # New failures in [t_current, t_next)
        new_fail_mask = (ttf >= t_current) & (ttf < t_next)
        new_fail_indices = np.where(new_fail_mask)[0]

        if len(new_fail_indices) > 0:
            order = np.argsort(ttf[new_fail_indices])
            new_fail_indices = new_fail_indices[order]

            for idx in new_fail_indices:
                if idx in failed_set:
                    continue
                failed_set.add(idx)

                # Adjacent unrepaired → instant failure
                if (idx - 1) in failed_set or (idx + 1) in failed_set:
                    return {"survived": False, "failure_time": float(ttf[idx]),
                            "repairs": repairs, "mttr": mttr_list}

                # Load redistribution
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

                # Cascade check
                for nb in [left, right]:
                    if nb is not None and nb not in failed_set:
                        if sigma_current[nb] > cascade_threshold:
                            return {"survived": False,
                                    "failure_time": float(ttf[idx]),
                                    "repairs": repairs, "mttr": mttr_list}

                # Sub-critical overload
                for nb in [left, right]:
                    if nb is not None and nb not in failed_set:
                        sr = sigma_current[nb] / sigma_nominal[nb]
                        eff_hazard[nb] = base_hazard[nb] * sr ** 4
                        remaining = rng.exponential(1.0 / eff_hazard[nb])
                        ttf[nb] = ttf[idx] + remaining

        # End of mission with unrepaired failures
        if t_next >= t_mission:
            if failed_set:
                earliest = min(ttf[j] for j in failed_set)
                return {"survived": False, "failure_time": float(earliest),
                        "repairs": repairs, "mttr": mttr_list}
            break

        # Inspection
        repaired = []
        for idx in list(failed_set):
            if rng.random() < p_detection:
                travel = float(joint_alts[idx]) / v_climber / 3600.0
                wait = t_next - float(ttf[idx])
                mttr_list.append(wait + travel + t_replace)
                repairs += 1
                repaired.append(idx)

        for idx in repaired:
            failed_set.discard(idx)
            eff_hazard[idx] = base_hazard[idx]
            sigma_current[idx] = sigma_nominal[idx]
            ttf[idx] = t_next + rng.exponential(1.0 / eff_hazard[idx])

        # Recalculate stress state after repairs
        if repaired:
            sigma_current[:] = sigma_nominal[:]
            eff_hazard[:] = base_hazard[:]
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

        t_current = t_next

    return {"survived": True, "failure_time": None,
            "repairs": repairs, "mttr": mttr_list}


# ---------------------------------------------------------------------------
# Full parameter sweep (4D: N × eta_j × cadence × p_detection)  (FIX D)
# ---------------------------------------------------------------------------
def run_sweep(params: dict, lambda_0_pre: float,
              n_traj: int = None, xp=np) -> dict:
    """
    Run the full Monte Carlo sweep over N × eta_j × cadence × p_detection.

    Returns dict with 4D P_sys array and metadata.
    """
    N_sweep = [int(x) for x in params["monte_carlo"]["N_sweep"]]
    eta_sweep = [float(x) for x in params["monte_carlo"]["eta_j_sweep"]]
    cadence_sweep = [int(x) for x in params["monte_carlo"]["inspection_cadence_sweep"]]
    pdet_sweep = [float(x) for x in params["monte_carlo"]["p_detection_sweep"]]

    if n_traj is None:
        n_traj = int(params["monte_carlo"]["n_trajectories"])

    shape = (len(N_sweep), len(eta_sweep), len(cadence_sweep), len(pdet_sweep))
    P_sys = np.zeros(shape)
    MTTR_median = np.zeros(shape)

    all_mttr_samples = []
    total_combos = len(N_sweep) * len(eta_sweep) * len(cadence_sweep) * len(pdet_sweep)
    combo = 0

    for i, N in enumerate(N_sweep):
        for j, eta_j in enumerate(eta_sweep):
            for k, cadence in enumerate(cadence_sweep):
                for m, pdet in enumerate(pdet_sweep):
                    combo += 1
                    seed = 42 + i * 10000 + j * 1000 + k * 100 + m * 10

                    batch = run_batch_vectorized(
                        N, eta_j, cadence, pdet, lambda_0_pre,
                        params, n_traj, seed=seed, xp=xp,
                    )
                    P_sys[i, j, k, m] = batch["P_sys"]
                    MTTR_median[i, j, k, m] = batch["MTTR_median"]

                    if len(batch["MTTR_samples"]) > 0:
                        all_mttr_samples.append(batch["MTTR_samples"])

                    if combo % 20 == 0 or combo == total_combos:
                        print(
                            f"  [{combo}/{total_combos}] N={N}, "
                            f"eta_j={eta_j:.2f}, cad={cadence}, "
                            f"p_det={pdet:.3f}  ->  P_sys={batch['P_sys']:.4f}, "
                            f"MTTR_med={batch['MTTR_median']:.1f}h"
                        )

    mttr_combined = (np.concatenate(all_mttr_samples)
                     if all_mttr_samples else np.array([]))

    return {
        "N_values": N_sweep,
        "eta_j_values": eta_sweep,
        "cadence_values": cadence_sweep,
        "p_detection_values": pdet_sweep,
        "P_sys": P_sys,
        "MTTR_median": MTTR_median,
        "MTTR_all_samples": mttr_combined,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def _apply_style():
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))


def plot_psys_heatmap(sweep_results: dict, cadence_idx: int = 0,
                      pdet_idx: int = -1, output_path: Path = None):
    """
    Plot P_sys(N, eta_j) heatmap at a fixed cadence and p_detection.
    Default: cadence index 0, last p_detection (highest = baseline 0.995).
    """
    _apply_style()

    # 4D: [N, eta, cadence, pdet]
    P = sweep_results["P_sys"][:, :, cadence_idx, pdet_idx]
    N_vals = sweep_results["N_values"]
    eta_vals = sweep_results["eta_j_values"]

    fig, ax = plt.subplots(figsize=(7.0, 5.5))

    N_edges = np.array(N_vals, dtype=float)
    eta_edges = np.array(eta_vals, dtype=float)

    # Build cell borders at midpoints between values (handles non-uniform spacing)
    def _cell_borders(vals):
        """Return len(vals)+1 border positions from midpoints of non-uniform vals."""
        v = np.asarray(vals, dtype=float)
        if len(v) < 2:
            return np.array([v[0] - 0.5, v[0] + 0.5])
        mids = (v[:-1] + v[1:]) / 2.0
        lo = v[0] - (mids[0] - v[0])
        hi = v[-1] + (v[-1] - mids[-1])
        return np.concatenate([[lo], mids, [hi]])

    N_borders = _cell_borders(N_edges)
    eta_borders = _cell_borders(eta_edges)

    im = ax.pcolormesh(N_borders, eta_borders, P.T,
                       cmap="RdYlGn", vmin=0.9, vmax=1.0, shading="flat")
    fig.colorbar(im, ax=ax, label=r"$P_{\mathrm{sys}}$ (10-year survival)")

    # Explicit tick positions so non-uniform N values are readable
    ax.set_xticks(N_vals)
    ax.set_xticklabels([str(int(v)) for v in N_vals], fontsize=7, rotation=45)
    ax.set_yticks(eta_vals)
    ax.set_yticklabels([f"{v:.2f}" for v in eta_vals], fontsize=7)

    N_grid, eta_grid = np.meshgrid(N_vals, eta_vals, indexing="ij")
    for level, style in [(0.99, "--"), (0.999, "-")]:
        try:
            cs = ax.contour(N_grid.T, eta_grid.T, P.T,
                            levels=[level], colors="black",
                            linewidths=0.8, linestyles=style)
            ax.clabel(cs, fmt=f"{level:.3f}", fontsize=7)
        except ValueError:
            pass

    if 18 in N_vals and 0.95 in eta_vals:
        ax.plot(18, 0.95, "k*", markersize=10, zorder=5)
        ax.annotate("Baseline", xy=(18, 0.95), xytext=(19.5, 0.935),
                    fontsize=7, arrowprops=dict(arrowstyle="->", color="black"))

    cadence_val = sweep_results["cadence_values"][cadence_idx]
    pdet_val = sweep_results["p_detection_values"][pdet_idx]
    ax.set_xlabel("Number of segments $N$")
    ax.set_ylabel(r"Joint efficiency $\eta_j$")
    ax.set_title(
        f"System survival probability "
        f"(cadence={cadence_val}, $p_{{det}}$={pdet_val})"
    )

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
        print(f"  Saved: {output_path}")
    plt.close(fig)


def plot_mttr_distribution(sweep_results: dict, output_path: Path = None):
    """Plot MTTR distribution histogram with 72h target line."""
    _apply_style()
    mttr = sweep_results["MTTR_all_samples"]
    fig, ax = plt.subplots(figsize=(5, 3.5))

    if len(mttr) > 0:
        mttr_display = mttr[mttr < 500]
        ax.hist(mttr_display, bins=50, density=True, alpha=0.7,
                color="#56B4E9", edgecolor="white", linewidth=0.3)
        ax.axvline(72, color="#D55E00", linestyle="--", linewidth=1.2,
                   label="72 h target")
        med = np.median(mttr)
        ax.axvline(med, color="#009E73", linestyle="-", linewidth=1.0,
                   label=f"Median = {med:.1f} h")
        pct = 100.0 * np.mean(mttr < 72)
        ax.annotate(f"{pct:.1f}% < 72 h", xy=(0.95, 0.95),
                    xycoords="axes fraction", ha="right", va="top", fontsize=8)
    else:
        ax.text(0.5, 0.5, "No repair events recorded",
                transform=ax.transAxes, ha="center", va="center", fontsize=10)

    ax.set_xlabel("Mean time to repair [h]")
    ax.set_ylabel("Probability density")
    ax.set_title("MTTR distribution (all parameter combinations)")
    ax.legend(fontsize=7)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
        print(f"  Saved: {output_path}")
    plt.close(fig)


def plot_inspection_cadence(sweep_results: dict, pdet_idx: int = -1,
                            output_path: Path = None):
    """
    Plot P_sys vs. inspection cadence for baseline N=18 at each eta_j,
    using the baseline p_detection.
    """
    _apply_style()
    N_vals = sweep_results["N_values"]
    eta_vals = sweep_results["eta_j_values"]
    cadence_vals = sweep_results["cadence_values"]
    P = sweep_results["P_sys"]

    fig, ax = plt.subplots(figsize=(5, 3.5))

    n_idx = N_vals.index(18) if 18 in N_vals else len(N_vals) // 2

    colors = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#D55E00",
              "#CC79A7", "#0072B2", "#F0E442", "#882255"]
    for j, eta_j in enumerate(eta_vals):
        P_vs_cad = P[n_idx, j, :, pdet_idx]
        ax.plot(cadence_vals, P_vs_cad, "o-",
                color=colors[j % len(colors)], markersize=4, linewidth=1.0,
                label=rf"$\eta_j$ = {eta_j:.2f}")

    ax.set_xlabel("Inspection cadence [climber passages]")
    ax.set_ylabel(r"$P_{\mathrm{sys}}$ (10-year survival)")
    ax.set_title(f"System survival vs. inspection frequency ($N$ = {N_vals[n_idx]})")
    ax.legend(fontsize=6, loc="lower left", ncol=2)
    ax.set_ylim(bottom=max(0, ax.get_ylim()[0]), top=1.0)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
        print(f"  Saved: {output_path}")
    plt.close(fig)


def plot_p_detection_impact(sweep_results: dict, output_path: Path = None):
    """
    NEW PLOT: P_sys vs. p_detection at baseline N=18 and various eta_j,
    with cadence=1.
    """
    _apply_style()
    N_vals = sweep_results["N_values"]
    eta_vals = sweep_results["eta_j_values"]
    cadence_vals = sweep_results["cadence_values"]
    pdet_vals = sweep_results["p_detection_values"]
    P = sweep_results["P_sys"]

    fig, ax = plt.subplots(figsize=(5, 3.5))

    n_idx = N_vals.index(18) if 18 in N_vals else len(N_vals) // 2
    c_idx = cadence_vals.index(1) if 1 in cadence_vals else 0

    colors = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#D55E00",
              "#CC79A7", "#0072B2", "#F0E442", "#882255"]
    for j, eta_j in enumerate(eta_vals):
        P_vs_pdet = P[n_idx, j, c_idx, :]
        ax.plot(pdet_vals, P_vs_pdet, "s-",
                color=colors[j % len(colors)], markersize=5, linewidth=1.0,
                label=rf"$\eta_j$ = {eta_j:.2f}")

    ax.set_xlabel(r"Detection probability $p_{\mathrm{det}}$")
    ax.set_ylabel(r"$P_{\mathrm{sys}}$ (10-year survival)")
    ax.set_title(
        f"Impact of detection probability ($N$={N_vals[n_idx]}, cadence=1)"
    )
    ax.legend(fontsize=6, loc="lower right", ncol=2)
    ax.set_ylim(bottom=max(0, ax.get_ylim()[0]), top=1.0)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
        print(f"  Saved: {output_path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Monte Carlo joint reliability simulation"
    )
    parser.add_argument(
        "--n-trajectories", type=int, default=None,
        help="Number of trajectories per combination. "
             "Default: from parameters.yaml (100000). Use 1000 for quick test."
    )
    parser.add_argument(
        "--single", action="store_true",
        help="Run only the baseline point (N=18, eta_j=0.95, cadence=1, "
             "p_det=0.995) instead of full sweep."
    )
    parser.add_argument(
        "--gpu", action="store_true",
        help="Use CuPy for GPU-accelerated TTF draws (requires CUDA + CuPy)."
    )
    args = parser.parse_args()

    params = load_params()
    n_traj = args.n_trajectories or int(params["monte_carlo"]["n_trajectories"])
    xp = get_array_module(args.gpu)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("MONTE CARLO JOINT RELIABILITY SIMULATION")
    print("=" * 60)
    print(f"  Trajectories per combo: {n_traj}")
    print(f"  Backend: {'GPU (CuPy)' if args.gpu and xp is not np else 'CPU (NumPy)'}")

    # --- Arrhenius calibration (FIX A) ---
    lambda_0_pre = calibrate_arrhenius(params, xp=xp)

    t_start = time.time()

    if args.single:
        N = int(params["segments"]["N_baseline"])
        eta_j = float(params["design"]["eta_j_baseline"])
        cadence = 1
        pdet = float(params["monte_carlo"]["p_detection_baseline"])
        print(f"\n  Mode: SINGLE (N={N}, eta_j={eta_j}, cadence={cadence}, "
              f"p_det={pdet})")
        print()

        batch = run_batch_vectorized(
            N, eta_j, cadence, pdet, lambda_0_pre,
            params, n_traj, xp=xp,
        )
        print(f"\n  P_sys       = {batch['P_sys']:.4f}")
        print(f"  MTTR median = {batch['MTTR_median']:.1f} h")
        print(f"  MTTR mean   = {batch['MTTR_mean']:.1f} h")
        print(f"  Avg repairs = {batch['n_repairs_mean']:.2f}")
        print(f"  Failures    = {batch['n_failures']}/{n_traj}")

    else:
        N_sweep = params["monte_carlo"]["N_sweep"]
        eta_sweep = params["monte_carlo"]["eta_j_sweep"]
        cadence_sweep = params["monte_carlo"]["inspection_cadence_sweep"]
        pdet_sweep = params["monte_carlo"]["p_detection_sweep"]

        total = (len(N_sweep) * len(eta_sweep) *
                 len(cadence_sweep) * len(pdet_sweep))

        print(f"\n  N sweep:       {N_sweep}")
        print(f"  eta_j sweep:   {eta_sweep}")
        print(f"  Cadence sweep: {cadence_sweep}")
        print(f"  p_det sweep:   {pdet_sweep}")
        print(f"  Total combinations: {total}")
        print(f"  Total trajectories: {total * n_traj:,}")
        print()

        results = run_sweep(params, lambda_0_pre, n_traj=n_traj, xp=xp)

        # Save data
        np.savez(
            OUTPUT_DIR / "psys_surface.npz",
            N_values=results["N_values"],
            eta_j_values=results["eta_j_values"],
            cadence_values=results["cadence_values"],
            p_detection_values=results["p_detection_values"],
            P_sys=results["P_sys"],
            MTTR_median=results["MTTR_median"],
        )
        print(f"\n  Saved: {OUTPUT_DIR / 'psys_surface.npz'}")

        if len(results["MTTR_all_samples"]) > 0:
            np.savez(
                OUTPUT_DIR / "mttr_samples.npz",
                mttr=results["MTTR_all_samples"],
            )
            print(f"  Saved: {OUTPUT_DIR / 'mttr_samples.npz'}")

        # --- Find baseline indices for plots ---
        pdet_vals = results["p_detection_values"]
        pdet_baseline = float(params["monte_carlo"]["p_detection_baseline"])
        if pdet_baseline in pdet_vals:
            pdet_base_idx = pdet_vals.index(pdet_baseline)
        else:
            pdet_base_idx = -1  # last = highest

        cadence_vals = results["cadence_values"]
        cad_base_idx = cadence_vals.index(1) if 1 in cadence_vals else 0

        # Plots
        plot_psys_heatmap(
            results, cadence_idx=cad_base_idx, pdet_idx=pdet_base_idx,
            output_path=FIGURES_DIR / "fig_psys_heatmap.pdf",
        )
        plot_mttr_distribution(
            results,
            output_path=FIGURES_DIR / "fig_mttr_distribution.pdf",
        )
        plot_inspection_cadence(
            results, pdet_idx=pdet_base_idx,
            output_path=FIGURES_DIR / "fig_inspection_cadence.pdf",
        )
        plot_p_detection_impact(
            results,
            output_path=FIGURES_DIR / "fig_p_detection_impact.pdf",
        )

        # Summary table (at baseline cadence=1, p_det=baseline)
        print(f"\n  Summary (cadence=1, p_det={pdet_baseline}):")
        N_vals = results["N_values"]
        eta_vals = results["eta_j_values"]
        header = f"  {'':>8}" + "".join(f"{'eta='+str(e):>10}" for e in eta_vals)
        print(header)
        for i, N in enumerate(N_vals):
            row = f"  N={N:>3} "
            for j in range(len(eta_vals)):
                row += f"{results['P_sys'][i, j, cad_base_idx, pdet_base_idx]:>10.4f}"
            print(row)

        # Headline numbers
        if 18 in N_vals and 0.95 in eta_vals:
            ni = N_vals.index(18)
            ei = eta_vals.index(0.95)
            P_base = results["P_sys"][ni, ei, cad_base_idx, pdet_base_idx]
            print(f"\n  HEADLINE: P_sys(N=18, eta_j=0.95, cadence=1, "
                  f"p_det={pdet_baseline}) = {P_base:.4f}")

    elapsed = time.time() - t_start
    print(f"\n  Elapsed: {elapsed:.1f} s")
    print("Done.")


if __name__ == "__main__":
    main()
