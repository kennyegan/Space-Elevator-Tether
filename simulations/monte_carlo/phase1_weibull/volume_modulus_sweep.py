"""
volume_modulus_sweep.py — Weibull volume modulus (m) sensitivity sweep.

Runs the Weibull MC engine at five values of volume modulus m = {2.7, 4, 6, 8, 10}
to show how uncertainty in the weakest-link scaling exponent affects system
reliability.  Addresses reviewer concern S2.

Calibration strategy (OPPOSITE of q_sensitivity_sweep.py):
    λ_0_pre is RECALIBRATED for each m value.  When m changes:
        volume_scale = V_ratio^(1/m)   changes
        λ_fullscale  = λ_coupon × volume_scale   changes
        λ_0_pre      = λ_fullscale / <exp(-Q/kT)>   changes

    This is consistent with sensitivity_analysis.py, where m_weibull
    perturbation does NOT use lambda_0_pre_fixed (only Q and T do).

Usage:
    cd ~/Space-Elevator-Tether

    # Quick test (1K trajectories)
    python -m simulations.monte_carlo.phase1_weibull.volume_modulus_sweep --quick

    # Full sweep (100K trajectories)
    python -m simulations.monte_carlo.phase1_weibull.volume_modulus_sweep

Outputs:
    data/processed/psys_volume_modulus.npz
    data/processed/volume_modulus_sensitivity.csv
    paper/figures/fig_volume_modulus_psys.pdf
"""

import argparse
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
    compute_joint_positions,
    load_params,
    thermal_profile_3zone,
)
from simulations.monte_carlo.phase1_weibull.simulate import run_batch_weibull


# ===================================================================
# Sweep grid
# ===================================================================
M_SWEEP = [2.7, 4.0, 6.0, 8.0, 10.0]
N_SWEEP = [83, 505]
ETA_J_SWEEP = [0.80, 0.88, 0.90, 0.95, 0.97]
BETA = 1.5
CADENCE = 1
P_DET = 0.995

TOTAL_COMBOS = len(M_SWEEP) * len(N_SWEEP) * len(ETA_J_SWEEP)  # 50


# ===================================================================
# Seed function (includes m to avoid collision)
# ===================================================================
def m_combo_seed(m_weibull: float, N: int, eta_j: float,
                 cadence: int, p_det: float, beta: float) -> int:
    """SHA-256 hash of (m, N, η_j, cadence, p_det, β) → uint32 seed."""
    key = f"m{m_weibull:.2f}_{N}_{eta_j:.4f}_{cadence}_{p_det:.4f}_{beta:.2f}"
    h = hashlib.sha256(key.encode()).digest()[:4]
    return struct.unpack("<I", h)[0]


# ===================================================================
# Recalibration with custom volume modulus
# ===================================================================
def calibrate_arrhenius_custom_m(params: dict, m_weibull: float) -> float:
    """
    Recalibrate λ_0_pre with a custom Weibull modulus for volume scaling.

    IMPORTANT: Calibration uses the BASELINE segment count (N=18) to compute
    the mean Arrhenius factor — this determines the material property λ_0_pre.
    The sweep then runs simulations at different N values (83, 505), which
    changes the number and positions of joints but NOT the calibration.
    λ_0_pre is a material/coupon property, not a system geometry property.

    Parameters
    ----------
    params : dict
        Master parameters.
    m_weibull : float
        Weibull modulus for volume scaling (weakest-link statistics).

    Returns
    -------
    lambda_0_pre : float
        Recalibrated pre-exponential [1/h].
    """
    lambda_0_bar = float(params["joints"]["lambda_0_bar"])       # 1.2e-8
    V_ratio = float(params["joints"]["volume_ratio"])            # 6000
    Q = float(params["joints"]["Q_activation"])                  # 1.76e-19 J
    k_B = float(params["physical"]["k_B"])                       # 1.38e-23 J/K

    volume_scale = V_ratio ** (1.0 / m_weibull)
    lambda_fullscale = lambda_0_bar * volume_scale

    # Calibrate on baseline N=18 geometry (material property, NOT per-system-N)
    N_base = int(params["segments"]["N_baseline"])               # 18
    alts = compute_joint_positions(N_base, params)
    temps = thermal_profile_3zone(alts)
    mean_arrhenius = float(np.mean(np.exp(-Q / (k_B * temps))))

    return lambda_fullscale / mean_arrhenius


# ===================================================================
# Main sweep
# ===================================================================
def run_m_sweep(params: dict, n_traj: int) -> dict:
    """
    Run the volume modulus sensitivity sweep.

    Returns dict with 3D arrays (m × N × η_j).
    """
    nM = len(M_SWEEP)
    nN = len(N_SWEEP)
    nE = len(ETA_J_SWEEP)

    P_sys = np.full((nM, nN, nE), np.nan)
    mean_repairs = np.full((nM, nN, nE), np.nan)
    median_MTTR = np.full((nM, nN, nE), np.nan)
    lambda_full_arr = np.full(nM, np.nan)

    csv_rows = []
    t0 = time.time()
    combo_num = 0

    for mi, m_val in enumerate(M_SWEEP):
        # Recalibrate for this m value (once per m, on baseline N=18)
        lambda_0_pre_m = calibrate_arrhenius_custom_m(params, m_val)
        V_ratio = float(params["joints"]["volume_ratio"])
        volume_scale = V_ratio ** (1.0 / m_val)
        lambda_fullscale = float(params["joints"]["lambda_0_bar"]) * volume_scale
        lambda_full_arr[mi] = lambda_fullscale

        print(f"\n  === m = {m_val:.1f} ===")
        print(f"    Volume scale factor: {volume_scale:.2f}")
        print(f"    λ_fullscale:         {lambda_fullscale:.3e} 1/h")
        print(f"    λ_0_pre:             {lambda_0_pre_m:.6e} 1/h")

        for ni, N in enumerate(N_SWEEP):
            for ei, eta_j in enumerate(ETA_J_SWEEP):
                combo_num += 1
                seed = m_combo_seed(m_val, N, eta_j, CADENCE, P_DET, BETA)

                # Note: N here is the *simulation* segment count (83 or 505),
                # NOT the calibration N. The same λ_0_pre_m is used for both.
                result = run_batch_weibull(
                    N, eta_j, CADENCE, P_DET,
                    lambda_0_pre_m, params,
                    n_traj, beta=BETA, seed=seed,
                )

                P_sys[mi, ni, ei] = result["P_sys"]
                mean_repairs[mi, ni, ei] = result["mean_repairs"]
                median_MTTR[mi, ni, ei] = result["median_MTTR"]

                csv_rows.append({
                    "m": m_val,
                    "N": N,
                    "eta_j": eta_j,
                    "lambda_full": lambda_fullscale,
                    "P_sys": result["P_sys"],
                    "mean_repairs": result["mean_repairs"],
                    "median_MTTR": result["median_MTTR"],
                })

                elapsed = time.time() - t0
                print(f"    [{combo_num:>3d}/{TOTAL_COMBOS}] "
                      f"N={N:>3d} η_j={eta_j:.2f} → "
                      f"P_sys={result['P_sys']:.5f}  "
                      f"({elapsed:.0f}s)")

    return {
        "m_values": np.array(M_SWEEP),
        "N_values": np.array(N_SWEEP),
        "eta_j_values": np.array(ETA_J_SWEEP),
        "P_sys": P_sys,
        "mean_repairs": mean_repairs,
        "median_MTTR": median_MTTR,
        "lambda_full": lambda_full_arr,
        "csv_rows": csv_rows,
    }


# ===================================================================
# Validation: m=6 must match standard calibration
# ===================================================================
def validate_m6(params: dict) -> bool:
    """
    Verify calibrate_arrhenius_custom_m(params, 6.0) is consistent with
    calibrate_arrhenius(params).

    Note: calibrate_arrhenius reads a pre-rounded volume_scale_factor (4.3)
    from parameters.yaml, while custom_m computes 6000^(1/6) = 4.2636...
    exactly.  The ~0.9% discrepancy is expected from this rounding.
    We validate that the exact computation is within 1% of the YAML-rounded
    calibration, confirming correctness of the recalibration logic.
    """
    lambda_std = calibrate_arrhenius(params)
    lambda_custom = calibrate_arrhenius_custom_m(params, 6.0)
    rel_err = abs(lambda_std - lambda_custom) / abs(lambda_std)
    # Tolerance: volume_scale_factor in YAML is rounded to 4.3;
    # 6000^(1/6) = 4.2636, so ~0.9% discrepancy is expected
    passed = rel_err < 0.01
    status = "PASS" if passed else "FAIL"
    print(f"  [VALIDATE] {status}: λ_0_pre(m=6, exact) = {lambda_custom:.6e}, "
          f"λ_0_pre(YAML rounded) = {lambda_std:.6e}, "
          f"rel_err = {rel_err:.4f} (expected ~0.009 from 4.3 vs 4.264 rounding)")
    return passed


# ===================================================================
# Volume scaling summary table
# ===================================================================
def print_volume_table(results: dict):
    """Print table: m, scale_factor, λ_full, min η_j for P_sys ≥ 0.995 at N=83."""
    ni = N_SWEEP.index(83)
    eta_arr = np.array(ETA_J_SWEEP)

    print(f"\n  {'m':>5s} | {'Scale factor':>12s} | {'λ_full [1/h]':>14s} | "
          f"{'Min η_j for P_sys ≥ 0.995 (N=83)':>35s}")
    print(f"  {'-' * 75}")

    rows = []
    for mi, m_val in enumerate(M_SWEEP):
        V_ratio = 6000.0
        scale = V_ratio ** (1.0 / m_val)
        lf = results["lambda_full"][mi]

        psys_slice = results["P_sys"][mi, ni, :]  # shape (nE,)
        above = eta_arr[psys_slice >= 0.995]
        min_eta = f"{above.min():.2f}" if len(above) > 0 else "> 0.97"

        note = " (baseline)" if m_val == 6.0 else ""
        print(f"  {m_val:>5.1f} | {scale:>12.2f} | {lf:>14.3e} | "
              f"{min_eta:>35s}{note}")

        rows.append({
            "m": m_val, "scale_factor": scale, "lambda_full": lf,
            "min_eta_j_N83": min_eta,
        })

    return rows


# ===================================================================
# Figure: P_sys vs η_j by m
# ===================================================================
def plot_psys_vs_eta(results: dict):
    """P_sys vs η_j, one curve per m, two panels (N=83 and N=505)."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    eta = np.array(ETA_J_SWEEP)
    colors = ["#D55E00", "#E69F00", "#000000", "#56B4E9", "#0072B2"]

    fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.2), sharey=True)

    for ax_idx, (ax, N) in enumerate(zip(axes, N_SWEEP)):
        ni = N_SWEEP.index(N)
        for mi, m_val in enumerate(M_SWEEP):
            curve = results["P_sys"][mi, ni, :]
            lw = 1.6 if m_val == 6.0 else 1.0
            ax.plot(eta, curve, "o-", color=colors[mi], markersize=3,
                    linewidth=lw, label=f"$m = {m_val}$")

        ax.axhline(0.995, color="gray", linestyle=":", linewidth=0.6)
        ax.set_xlabel(r"$\eta_j$ (joint efficiency)")
        ax.set_title(f"$N = {N}$", fontsize=9)
        if ax_idx == 0:
            ax.set_ylabel(r"$P_{\mathrm{sys}}$")
        ax.legend(fontsize=6, loc="lower right")
        ax.set_ylim(-0.05, 1.05)

    fig.suptitle(r"Volume modulus sensitivity ($\beta = 1.5$, cadence = 1)",
                 fontsize=10, y=1.02)
    plt.tight_layout()

    out = FIGURES_DIR / "fig_volume_modulus_psys.pdf"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"  Saved: {out}")
    plt.close(fig)


# ===================================================================
# Save results
# ===================================================================
def save_results(results: dict):
    """Save NPZ and CSV."""
    npz_path = OUTPUT_DIR / "psys_volume_modulus.npz"
    np.savez_compressed(
        npz_path,
        m_values=results["m_values"],
        N_values=results["N_values"],
        eta_j_values=results["eta_j_values"],
        P_sys=results["P_sys"],
        mean_repairs=results["mean_repairs"],
        lambda_full=results["lambda_full"],
    )
    print(f"  Saved: {npz_path}")

    csv_path = OUTPUT_DIR / "volume_modulus_sensitivity.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["m", "N", "eta_j", "lambda_full",
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
        description="Weibull volume modulus sensitivity sweep (reviewer S2)")
    parser.add_argument("--n-trajectories", type=int, default=None,
                        help="Trajectories per combo (default: from YAML)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test: 1000 trajectories")
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
    print("WEIBULL VOLUME MODULUS SENSITIVITY SWEEP (Reviewer S2)")
    print("=" * 65)
    print(f"  m values:        {M_SWEEP}")
    print(f"  N values:        {N_SWEEP}")
    print(f"  η_j values:      {ETA_J_SWEEP}")
    print(f"  Fixed: β={BETA}, cadence={CADENCE}, p_det={P_DET}")
    print(f"  Total combos:    {TOTAL_COMBOS}")
    print(f"  Trajectories:    {n_traj:,}")

    # Validate m=6 calibration consistency
    validate_m6(params)

    # Run sweep
    results = run_m_sweep(params, n_traj)

    # Save
    save_results(results)

    # Volume table
    print_volume_table(results)

    # Figure
    print(f"\n  Generating figure...")
    plot_psys_vs_eta(results)

    print(f"\nDone.")


if __name__ == "__main__":
    main()
