"""
gravity_gradient_comparison.py — Transverse gravity-gradient vs tension stiffness.

Computes the ratio of tension-string stiffness to transverse gravity-gradient
stiffness at every element along the tether.  Addresses reviewer concern M3:
whether omitting the transverse gravity-gradient term (ω² − GM/r³)v from the
2D FEM is justified.

Per element at midpoint radius r_mid:
    k_tension = T_e / L_e                                     [N/m]
    k_gg      = |ρ A_e L_e (ω² − GM/r_mid³)|                 [N/m]
    ratio     = k_tension / k_gg

If ratio >> 1 everywhere (except near GEO where k_gg → 0), the omission is
physically justified.

Usage:
    cd ~/Space-Elevator-Tether
    python -m simulations.fea.phase2_dynamics.gravity_gradient_comparison
"""

import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulations.fea.phase2_dynamics.config import (
    FIGURES_DIR,
    OUTPUT_DIR,
    STYLE_FILE,
    get_constants,
)
from simulations.fea.phase2_dynamics.mesh import generate_mesh
from simulations.fea.taper_profile import load_params


# ===================================================================
# Stiffness comparison
# ===================================================================
def compute_stiffness_comparison(params: dict, N_mesh: int = 2000) -> dict:
    """
    Compute tension-string and gravity-gradient transverse stiffness at every
    element along the tether.

    Parameters
    ----------
    params : dict
        Master parameter dictionary.
    N_mesh : int
        Number of mesh nodes (fine mesh for smooth curves).

    Returns
    -------
    dict with arrays indexed by element (length N_mesh-1):
        alt_mid_km : altitude above surface [km]
        r_mid      : geocentric radius [m]
        k_tension  : tension-string stiffness per element [N/m]
        k_gg_abs   : |gravity-gradient transverse stiffness| per element [N/m]
        k_gg_raw   : signed gravity-gradient stiffness [N/m]
        ratio      : k_tension / k_gg_abs (inf at GEO)
        T_MN       : tension [MN]
    """
    c = get_constants(params)
    mesh = generate_mesh(params, N=N_mesh, eta_j=1.0, refine_geo=True)

    r_mid = mesh["r_mid"]
    L_e = mesh["L_e"]
    A_e = mesh["A_e"]
    T_e = mesh["T_e"]

    # Tension-string stiffness per element: T/L [N/m]
    k_tension = T_e / L_e

    # Gravity-gradient transverse coefficient at element midpoints:
    #   ρ A_e (ω² − GM/r³)  [N/m³]  (force per length per displacement)
    # Integrated over element length L_e → ρ A_e L_e (ω² − GM/r³) [N/m]
    gg_coeff = c["omega"] ** 2 - c["GM"] / r_mid ** 3
    k_gg_raw = c["rho"] * A_e * L_e * gg_coeff
    k_gg_abs = np.abs(k_gg_raw)

    # Ratio (protect against division by zero at GEO)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = k_tension / k_gg_abs
    ratio[~np.isfinite(ratio)] = np.inf

    alt_mid_km = (r_mid - c["R_earth"]) / 1e3

    return {
        "alt_mid_km": alt_mid_km,
        "r_mid": r_mid,
        "k_tension": k_tension,
        "k_gg_abs": k_gg_abs,
        "k_gg_raw": k_gg_raw,
        "ratio": ratio,
        "T_MN": T_e / 1e6,
    }


# ===================================================================
# Table at representative altitudes
# ===================================================================
TARGET_ALTITUDES_KM = [0, 200, 1_000, 5_000, 15_000, 35_000,
                       35_786, 50_000, 75_000, 100_000]


def print_table(comp: dict, altitudes_km: list = None) -> list[dict]:
    """Print and return a table of stiffness comparison at target altitudes."""
    if altitudes_km is None:
        altitudes_km = TARGET_ALTITUDES_KM

    alt = comp["alt_mid_km"]
    rows = []
    header = (f"  {'Altitude [km]':>14s} | {'T(r) [MN]':>10s} | "
              f"{'k_tension [N/m]':>16s} | {'k_gg [N/m]':>14s} | "
              f"{'Ratio':>10s} | {'Sign of k_gg':>14s}")
    print(header)
    print(f"  {'-' * len(header)}")

    for target_km in altitudes_km:
        idx = int(np.argmin(np.abs(alt - target_km)))
        sign_str = ("zero" if abs(comp["k_gg_raw"][idx]) < 1e-20
                     else "destabilizing" if comp["k_gg_raw"][idx] < 0
                     else "stabilizing")
        ratio_str = ("∞ (k_gg = 0)" if comp["ratio"][idx] == np.inf
                      else f"{comp['ratio'][idx]:.1f}")
        row = {
            "altitude_km": target_km,
            "T_MN": comp["T_MN"][idx],
            "k_tension": comp["k_tension"][idx],
            "k_gg": comp["k_gg_abs"][idx],
            "ratio": comp["ratio"][idx],
            "sign": sign_str,
        }
        rows.append(row)
        print(f"  {target_km:>14,.0f} | {row['T_MN']:>10.3f} | "
              f"{row['k_tension']:>16.4e} | {row['k_gg']:>14.4e} | "
              f"{ratio_str:>10s} | {sign_str:>14s}")

    return rows


# ===================================================================
# Figure: 2-panel stiffness comparison
# ===================================================================
def plot_comparison(comp: dict):
    """Two-panel figure: stiffnesses and ratio vs altitude."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    alt = comp["alt_mid_km"]
    GEO_KM = 35_786.0

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.48, 5.5), sharex=True)

    # --- Top panel: stiffness magnitudes ---
    ax1.semilogy(alt / 1e3, comp["k_tension"], color="#0072B2",
                 linewidth=1.2, label=r"$k_{\mathrm{tension}} = T/L$")
    ax1.semilogy(alt / 1e3, comp["k_gg_abs"], color="#D55E00",
                 linewidth=1.2, label=r"$|k_{\mathrm{gg}}|$")

    ax1.axvline(GEO_KM / 1e3, color="gray", linestyle="--", linewidth=0.6,
                label="GEO")
    ax1.axvspan((GEO_KM - 1000) / 1e3, (GEO_KM + 1000) / 1e3,
                alpha=0.08, color="gray")

    ax1.set_ylabel("Stiffness [N/m]")
    ax1.legend(fontsize=7)
    ax1.set_title("Transverse stiffness: tension-string vs gravity-gradient")

    # --- Bottom panel: ratio ---
    # Clip ratio for plotting (inf → large number)
    ratio_plot = np.clip(comp["ratio"], 1e-1, 1e8)
    ax2.semilogy(alt / 1e3, ratio_plot, color="#000000", linewidth=1.0)
    ax2.axhline(10, color="#E69F00", linestyle=":", linewidth=0.8,
                label="Ratio = 10")
    ax2.axhline(100, color="#009E73", linestyle=":", linewidth=0.8,
                label="Ratio = 100")
    ax2.axvline(GEO_KM / 1e3, color="gray", linestyle="--", linewidth=0.6)
    ax2.axvspan((GEO_KM - 1000) / 1e3, (GEO_KM + 1000) / 1e3,
                alpha=0.08, color="gray")

    ax2.set_xlabel(r"Altitude [$\times 10^3$ km]")
    ax2.set_ylabel(r"$k_{\mathrm{tension}} \;/\; |k_{\mathrm{gg}}|$")
    ax2.legend(fontsize=7)

    plt.tight_layout()
    out = FIGURES_DIR / "fig_stiffness_ratio.pdf"
    fig.savefig(out, dpi=300)
    print(f"\n  Saved: {out}")
    plt.close(fig)


# ===================================================================
# Decision assessment
# ===================================================================
def assess_decision(comp: dict, exclusion_km: float = 1000.0,
                    threshold: float = 10.0) -> str:
    """
    Check if k_tension / |k_gg| > threshold everywhere outside the GEO
    exclusion zone (GEO ± exclusion_km).

    Returns verdict string.
    """
    GEO_KM = 35_786.0
    alt = comp["alt_mid_km"]
    ratio = comp["ratio"]

    # Mask: elements outside the GEO exclusion zone
    outside = np.abs(alt - GEO_KM) > exclusion_km
    min_ratio_outside = np.min(ratio[outside])

    if min_ratio_outside > threshold:
        verdict = (f"JUSTIFIED — minimum ratio outside GEO ± {exclusion_km:.0f} km "
                   f"is {min_ratio_outside:.1f} (> {threshold:.0f})")
    else:
        # Find where ratio is smallest
        worst_idx = np.argmin(ratio[outside])
        worst_alt = alt[outside][worst_idx]
        verdict = (f"NOT JUSTIFIED — ratio drops to {min_ratio_outside:.1f} "
                   f"at altitude {worst_alt:.0f} km (< {threshold:.0f})")
    return verdict


# ===================================================================
# Save CSV
# ===================================================================
def save_csv(comp: dict, path: Path):
    """Save full element-level comparison as CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["altitude_km", "r_m", "k_tension_N_per_m",
                     "k_gg_trans_N_per_m", "k_gg_sign", "ratio"])
        for i in range(len(comp["alt_mid_km"])):
            sign = ("destabilizing" if comp["k_gg_raw"][i] < 0
                    else "stabilizing" if comp["k_gg_raw"][i] > 0
                    else "zero")
            ratio_val = comp["ratio"][i] if np.isfinite(comp["ratio"][i]) else "inf"
            w.writerow([
                f"{comp['alt_mid_km'][i]:.2f}",
                f"{comp['r_mid'][i]:.2f}",
                f"{comp['k_tension'][i]:.6e}",
                f"{comp['k_gg_abs'][i]:.6e}",
                sign,
                ratio_val,
            ])
    print(f"  Saved: {path}")


# ===================================================================
# Main
# ===================================================================
def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("GRAVITY-GRADIENT vs TENSION STIFFNESS COMPARISON (Reviewer M3)")
    print("=" * 65)

    params = load_params()
    c = get_constants(params)
    print(f"\n  Physical constants:")
    print(f"    ω       = {c['omega']:.6e} rad/s")
    print(f"    GM      = {c['GM']:.6e} m³/s²")
    print(f"    ρ       = {c['rho']:.0f} kg/m³")
    print(f"    σ_design= {c['sigma_design']:.2e} Pa")

    print(f"\n  Generating mesh (N=2000 nodes)...")
    comp = compute_stiffness_comparison(params, N_mesh=2000)

    print(f"\n  Stiffness comparison at representative altitudes:\n")
    rows = print_table(comp)

    verdict = assess_decision(comp, exclusion_km=1000.0, threshold=10.0)
    print(f"\n  DECISION: {verdict}")

    # Also check with stricter threshold
    verdict_strict = assess_decision(comp, exclusion_km=1000.0, threshold=100.0)
    print(f"  STRICT:   {verdict_strict}")

    print(f"\n  Generating figure...")
    plot_comparison(comp)

    csv_path = OUTPUT_DIR / "stiffness_comparison.csv"
    save_csv(comp, csv_path)

    print(f"\nDone.")


if __name__ == "__main__":
    main()
