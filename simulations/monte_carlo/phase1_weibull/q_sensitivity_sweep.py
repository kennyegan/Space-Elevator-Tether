"""
q_sensitivity_sweep.py — Q-activation-energy sensitivity Monte Carlo sweep.

Runs the Weibull MC engine at three activation energies Q = {0.8, 1.1, 1.4} eV
on a reduced parameter grid to show how the reliability surface shifts with Q.
Addresses reviewer concern M2.

Calibration strategy:
    λ_0_pre is calibrated ONCE at baseline Q = 1.1 eV, then held fixed.
    Changing Q while holding λ_0_pre fixed isolates the physical sensitivity
    of the Arrhenius rate to activation energy.  This matches the approach
    in sensitivity_analysis.py (lambda_0_pre_fixed for Q perturbations).

Usage:
    cd ~/Space-Elevator-Tether

    # Quick test (1K trajectories)
    python -m simulations.monte_carlo.phase1_weibull.q_sensitivity_sweep --quick

    # Full sweep (100K trajectories)
    python -m simulations.monte_carlo.phase1_weibull.q_sensitivity_sweep

    # Single Q index (for SLURM array)
    python -m simulations.monte_carlo.phase1_weibull.q_sensitivity_sweep \\
        --q-index 0 --n-trajectories 100000

Outputs:
    data/processed/psys_Q_sensitivity.npz
    data/processed/Q_sensitivity_results.csv
    data/processed/Q_hazard_rate_table.csv
    paper/figures/fig_psys_vs_Q.pdf
    paper/figures/fig_Q_reliability_envelope.pdf
"""

import argparse
import copy
import csv
import hashlib
import struct
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulations.monte_carlo.phase1_weibull.config import (
    FIGURES_DIR,
    OUTPUT_DIR,
    RESULTS_DIR,
    STYLE_FILE,
)
from simulations.monte_carlo.phase1_weibull.hazard_model import (
    calibrate_arrhenius,
    compute_hazard_rates,
    compute_joint_positions,
    load_params,
    thermal_profile_3zone,
)
from simulations.monte_carlo.phase1_weibull.simulate import run_batch_weibull


# ===================================================================
# Sweep grid
# ===================================================================
Q_EV_SWEEP = [0.8, 1.1, 1.4]
N_SWEEP = [12, 24, 83, 200, 500]
ETA_J_SWEEP = [0.70, 0.80, 0.88, 0.90, 0.95, 0.97]
BETA_SWEEP = [1.0, 1.5, 2.5]
CADENCE = 1
P_DET = 0.995

TOTAL_PER_Q = len(N_SWEEP) * len(ETA_J_SWEEP) * len(BETA_SWEEP)  # 90
TOTAL_COMBOS = len(Q_EV_SWEEP) * TOTAL_PER_Q                      # 270

# eV to Joules (exact NIST 2019 value)
EV_TO_J = 1.602176634e-19


# ===================================================================
# Seed function (includes Q to avoid collision with main sweep)
# ===================================================================
def q_combo_seed(Q_eV: float, N: int, eta_j: float,
                 cadence: int, p_det: float, beta: float) -> int:
    """SHA-256 hash of (Q, N, η_j, cadence, p_det, β) → uint32 seed."""
    key = f"Q{Q_eV:.2f}_{N}_{eta_j:.4f}_{cadence}_{p_det:.4f}_{beta:.2f}"
    h = hashlib.sha256(key.encode()).digest()[:4]
    return struct.unpack("<I", h)[0]


# ===================================================================
# Params override
# ===================================================================
def make_params_with_Q(params: dict, Q_eV: float) -> dict:
    """Return a deep copy of params with Q_activation overridden."""
    p = copy.deepcopy(params)
    p["joints"]["Q_activation"] = Q_eV * EV_TO_J
    return p


# ===================================================================
# Main sweep
# ===================================================================
def run_q_sweep(params: dict, n_traj: int,
                q_index: int = None) -> dict:
    """
    Run the Q-sensitivity sweep.

    Parameters
    ----------
    params : dict
        Master parameters (baseline Q = 1.1 eV).
    n_traj : int
        Trajectories per combo.
    q_index : int or None
        If set, run only this Q value (0, 1, or 2).  For SLURM array.

    Returns
    -------
    dict with 4D arrays (Q × N × η_j × β).
    """
    # Calibrate λ_0_pre ONCE at baseline (Q = 1.1 eV)
    lambda_0_pre = calibrate_arrhenius(params)

    q_list = [Q_EV_SWEEP[q_index]] if q_index is not None else Q_EV_SWEEP

    # Allocate result arrays
    nQ = len(Q_EV_SWEEP)
    nN = len(N_SWEEP)
    nE = len(ETA_J_SWEEP)
    nB = len(BETA_SWEEP)

    P_sys = np.full((nQ, nN, nE, nB), np.nan)
    mean_repairs = np.full((nQ, nN, nE, nB), np.nan)
    median_MTTR = np.full((nQ, nN, nE, nB), np.nan)

    # CSV rows
    csv_rows = []

    t0 = time.time()
    combo_num = 0
    total = len(q_list) * TOTAL_PER_Q

    for Q_eV in q_list:
        qi = Q_EV_SWEEP.index(Q_eV)
        params_Q = make_params_with_Q(params, Q_eV)

        print(f"\n  === Q = {Q_eV} eV (index {qi}) ===")

        for ni, N in enumerate(N_SWEEP):
            for ei, eta_j in enumerate(ETA_J_SWEEP):
                for bi, beta in enumerate(BETA_SWEEP):
                    combo_num += 1
                    seed = q_combo_seed(Q_eV, N, eta_j, CADENCE, P_DET, beta)

                    result = run_batch_weibull(
                        N, eta_j, CADENCE, P_DET,
                        lambda_0_pre, params_Q,
                        n_traj, beta=beta, seed=seed,
                    )

                    P_sys[qi, ni, ei, bi] = result["P_sys"]
                    mean_repairs[qi, ni, ei, bi] = result["mean_repairs"]
                    median_MTTR[qi, ni, ei, bi] = result["median_MTTR"]

                    csv_rows.append({
                        "Q_eV": Q_eV,
                        "N": N,
                        "eta_j": eta_j,
                        "beta": beta,
                        "P_sys": result["P_sys"],
                        "mean_repairs": result["mean_repairs"],
                        "median_MTTR": result["median_MTTR"],
                    })

                    if combo_num % 10 == 0 or combo_num == total:
                        elapsed = time.time() - t0
                        print(f"    [{combo_num:>4d}/{total}] Q={Q_eV} N={N:>3d} "
                              f"η_j={eta_j:.2f} β={beta:.1f} → "
                              f"P_sys={result['P_sys']:.5f}  "
                              f"({elapsed:.0f}s)")

    return {
        "Q_values": np.array(Q_EV_SWEEP),
        "N_values": np.array(N_SWEEP),
        "eta_j_values": np.array(ETA_J_SWEEP),
        "beta_values": np.array(BETA_SWEEP),
        "P_sys": P_sys,
        "mean_repairs": mean_repairs,
        "median_MTTR": median_MTTR,
        "csv_rows": csv_rows,
    }


# ===================================================================
# Validation: Q=1.1 must match existing data
# ===================================================================
def validate_baseline(results: dict, tolerance: float = 0.002) -> bool:
    """
    Compare Q=1.1 results against existing psys_weibull_surface.npz.

    The existing surface has axes (N, eta_j, cadence, p_det, beta) with:
        cadence index 0 = 1, p_det index 6 = 0.995
    """
    existing_path = OUTPUT_DIR / "psys_weibull_surface.npz"
    if not existing_path.exists():
        print("  [VALIDATE] Existing surface not found — skipping.")
        return True

    data = np.load(existing_path)
    existing_Psys = data["P_sys"]  # shape (10, 9, 4, 7, 5)
    existing_N = list(data["N_values"])
    existing_eta = list(data["eta_j_values"])
    existing_beta = list(data["beta_values"])

    qi = Q_EV_SWEEP.index(1.1)
    max_delta = 0.0
    n_compared = 0

    for ni, N in enumerate(N_SWEEP):
        if N not in existing_N:
            continue
        ei_exist = existing_N.index(N)
        for ei, eta_j in enumerate(ETA_J_SWEEP):
            if eta_j not in existing_eta:
                continue
            ej_exist = existing_eta.index(eta_j)
            for bi, beta in enumerate(BETA_SWEEP):
                if beta not in existing_beta:
                    continue
                bk_exist = existing_beta.index(beta)

                new_val = results["P_sys"][qi, ni, ei, bi]
                # cadence=1 → index 0; p_det=0.995 → index 6
                old_val = existing_Psys[ei_exist, ej_exist, 0, 6, bk_exist]

                if np.isnan(new_val) or np.isnan(old_val):
                    continue

                delta = abs(new_val - old_val)
                max_delta = max(max_delta, delta)
                n_compared += 1

    passed = max_delta < tolerance
    status = "PASS" if passed else "FAIL"
    print(f"  [VALIDATE] {status}: max |ΔP_sys| = {max_delta:.5f} "
          f"(tolerance {tolerance}, {n_compared} points compared)")
    return passed


# ===================================================================
# Hazard rate summary table
# ===================================================================
def print_hazard_table(params: dict, lambda_0_pre: float):
    """Print hazard rate table for each Q value."""
    k_B = float(params["physical"]["k_B"])
    t_mission = float(params["monte_carlo"]["t_mission"])

    print(f"\n  {'Q [eV]':>8s} | {'λ_full [1/h]':>14s} | "
          f"{'10-yr joint P_fail':>18s} | {'Comment'}")
    print(f"  {'-' * 70}")

    rows = []
    for Q_eV in Q_EV_SWEEP:
        Q_J = Q_eV * EV_TO_J
        params_Q = make_params_with_Q(params, Q_eV)
        N_base = int(params["segments"]["N_baseline"])
        alts = compute_joint_positions(N_base, params)
        temps = thermal_profile_3zone(alts)
        rates = compute_hazard_rates(0.95, temps, lambda_0_pre, params_Q)
        lambda_full = float(np.mean(rates))
        p_fail = 1.0 - np.exp(-lambda_full * t_mission)

        if Q_eV == 0.8:
            comment = "System likely fails"
        elif Q_eV == 1.1:
            comment = "Baseline"
        else:
            comment = "Essentially no failures"

        print(f"  {Q_eV:>8.1f} | {lambda_full:>14.3e} | "
              f"{p_fail:>18.4e} | {comment}")
        rows.append({"Q_eV": Q_eV, "lambda_full": lambda_full,
                      "p_fail_10yr": p_fail, "comment": comment})

    # Save CSV
    csv_path = OUTPUT_DIR / "Q_hazard_rate_table.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Q_eV", "lambda_full",
                                           "p_fail_10yr", "comment"])
        w.writeheader()
        w.writerows(rows)
    print(f"  Saved: {csv_path}")


# ===================================================================
# Figure 1: 3-panel P_sys heatmap (one per Q)
# ===================================================================
def _cell_borders(values):
    """Compute pcolormesh cell borders from non-uniform grid values."""
    borders = np.empty(len(values) + 1)
    borders[1:-1] = 0.5 * (np.array(values[:-1]) + np.array(values[1:]))
    borders[0] = values[0] - (borders[1] - values[0])
    borders[-1] = values[-1] + (values[-1] - borders[-2])
    return borders


def plot_heatmap_panels(results: dict):
    """3×1 panel: P_sys(N, η_j) heatmap at β=1.0 for Q = {0.8, 1.1, 1.4}."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    bi = BETA_SWEEP.index(1.0)

    N_borders = _cell_borders(N_SWEEP)
    eta_borders = _cell_borders(ETA_J_SWEEP)

    fig, axes = plt.subplots(1, 3, figsize=(7.48, 3.0), sharey=True)

    vmin, vmax = 0.0, 1.0

    for ax_idx, (ax, Q_eV) in enumerate(zip(axes, Q_EV_SWEEP)):
        qi = Q_EV_SWEEP.index(Q_eV)
        # P_sys shape: (Q, N, eta_j, beta)
        Z = results["P_sys"][qi, :, :, bi].T  # shape (eta_j, N) for pcolormesh

        im = ax.pcolormesh(N_borders, eta_borders, Z,
                           vmin=vmin, vmax=vmax, cmap="RdYlGn", shading="flat")

        # Contour at P_sys = 0.995
        N_centers = np.array(N_SWEEP, dtype=float)
        eta_centers = np.array(ETA_J_SWEEP, dtype=float)
        try:
            ax.contour(N_centers, eta_centers, Z, levels=[0.995],
                       colors="black", linewidths=0.8, linestyles="--")
        except ValueError:
            pass  # no contour if all above or below

        ax.set_title(f"$Q = {Q_eV}$ eV", fontsize=9)
        ax.set_xlabel("$N$ (segments)")
        if ax_idx == 0:
            ax.set_ylabel(r"$\eta_j$ (joint efficiency)")

    fig.colorbar(im, ax=axes, label=r"$P_{\mathrm{sys}}$", shrink=0.9)
    fig.suptitle(r"System reliability at $\beta = 1.0$, cadence = 1",
                 fontsize=10, y=1.02)

    out = FIGURES_DIR / "fig_psys_vs_Q.pdf"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"  Saved: {out}")
    plt.close(fig)


# ===================================================================
# Figure 2: Reliability envelope (P_sys vs η_j for each Q)
# ===================================================================
def plot_reliability_envelope(results: dict):
    """P_sys vs η_j at N=83, β=1.5 for all Q. Shaded band Q=0.8 to Q=1.4."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    ni = N_SWEEP.index(83)
    bi = BETA_SWEEP.index(1.5)
    eta = np.array(ETA_J_SWEEP)

    colors = ["#D55E00", "#000000", "#0072B2"]
    labels = [f"$Q = {q}$ eV" for q in Q_EV_SWEEP]

    fig, ax = plt.subplots(figsize=(3.74, 3.0))

    psys_curves = []
    for qi, Q_eV in enumerate(Q_EV_SWEEP):
        curve = results["P_sys"][qi, ni, :, bi]
        psys_curves.append(curve)
        ax.plot(eta, curve, "o-", color=colors[qi], markersize=3,
                linewidth=1.2, label=labels[qi])

    # Shaded band between Q=0.8 and Q=1.4
    ax.fill_between(eta, psys_curves[0], psys_curves[2],
                    alpha=0.15, color="#56B4E9",
                    label="$Q$ uncertainty band")

    ax.axhline(0.995, color="gray", linestyle=":", linewidth=0.6,
               label="$P_{\\mathrm{sys}} = 0.995$")

    ax.set_xlabel(r"$\eta_j$ (joint efficiency)")
    ax.set_ylabel(r"$P_{\mathrm{sys}}$")
    ax.set_title(r"Reliability cliff shift with $Q$ ($N=83$, $\beta=1.5$)",
                 fontsize=9)
    ax.legend(fontsize=6, loc="lower right")
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()
    out = FIGURES_DIR / "fig_Q_reliability_envelope.pdf"
    fig.savefig(out, dpi=300)
    print(f"  Saved: {out}")
    plt.close(fig)


# ===================================================================
# Save results
# ===================================================================
def save_results(results: dict):
    """Save NPZ and CSV."""
    # NPZ
    npz_path = OUTPUT_DIR / "psys_Q_sensitivity.npz"
    np.savez_compressed(
        npz_path,
        Q_values=results["Q_values"],
        N_values=results["N_values"],
        eta_j_values=results["eta_j_values"],
        beta_values=results["beta_values"],
        P_sys=results["P_sys"],
        mean_repairs=results["mean_repairs"],
    )
    print(f"  Saved: {npz_path}")

    # CSV
    csv_path = OUTPUT_DIR / "Q_sensitivity_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Q_eV", "N", "eta_j", "beta",
                                           "P_sys", "mean_repairs",
                                           "median_MTTR"])
        w.writeheader()
        for row in results["csv_rows"]:
            w.writerow(row)
    print(f"  Saved: {csv_path}")


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Q-sensitivity Monte Carlo sweep (reviewer M2)")
    parser.add_argument("--n-trajectories", type=int, default=None,
                        help="Trajectories per combo (default: from YAML)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test: 1000 trajectories")
    parser.add_argument("--q-index", type=int, default=None,
                        help="Run only this Q index (0, 1, or 2) for SLURM")
    args = parser.parse_args()

    params = load_params()

    if args.quick:
        n_traj = 1000
    elif args.n_trajectories is not None:
        n_traj = args.n_trajectories
    else:
        n_traj = int(params["monte_carlo"]["n_trajectories"])

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("Q-SENSITIVITY MONTE CARLO SWEEP (Reviewer M2)")
    print("=" * 65)
    print(f"  Q values:        {Q_EV_SWEEP}")
    print(f"  Grid:            {len(N_SWEEP)} N × {len(ETA_J_SWEEP)} η_j "
          f"× {len(BETA_SWEEP)} β = {TOTAL_PER_Q} per Q")
    print(f"  Total combos:    {TOTAL_COMBOS}")
    print(f"  Trajectories:    {n_traj:,}")
    if args.q_index is not None:
        print(f"  SLURM mode:      Q index {args.q_index} "
              f"(Q = {Q_EV_SWEEP[args.q_index]} eV)")

    # Run sweep
    results = run_q_sweep(params, n_traj, q_index=args.q_index)

    # Validate Q=1.1 against existing data
    if args.q_index is None or args.q_index == Q_EV_SWEEP.index(1.1):
        validate_baseline(results)

    # Save
    save_results(results)

    # Hazard rate table
    lambda_0_pre = calibrate_arrhenius(params)
    print_hazard_table(params, lambda_0_pre)

    # Figures (only if all Q values were run)
    if args.q_index is None:
        print(f"\n  Generating figures...")
        plot_heatmap_panels(results)
        plot_reliability_envelope(results)

    print(f"\nDone.")


if __name__ == "__main__":
    main()
