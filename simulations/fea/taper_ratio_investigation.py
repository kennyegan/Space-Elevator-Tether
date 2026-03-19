"""
taper_ratio_investigation.py — Resolve the taper ratio discrepancy

The draft claims τ ≈ 1.6 at σ_allow = 25 GPa, ρ = 1300 kg/m³.
Numerical integration gives τ ≈ 12.4 at the same parameters.
Hypothesis: the draft used σ_u = 50 GPa (not σ_allow = 25 GPa).

This script computes τ for BOTH assumptions side-by-side and prints
a clear comparison table to resolve the discrepancy.

Usage:
    python simulations/fea/taper_ratio_investigation.py

No figures — print output only.
"""

from pathlib import Path
import numpy as np
from scipy import integrate
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
PARAMS_FILE = ROOT / "data" / "parameters.yaml"


def load_params(path: Path = PARAMS_FILE) -> dict:
    """Load master parameter file, casting all numeric values to float."""
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

    def cast_floats(d):
        out = {}
        for k, v in d.items():
            if isinstance(v, dict):
                out[k] = cast_floats(v)
            elif isinstance(v, list):
                out[k] = [try_float(x) for x in v]
            else:
                out[k] = try_float(v)
        return out

    return cast_floats(raw)


def net_acceleration(r: float, GM: float, omega: float) -> float:
    """
    Net outward acceleration at radial distance r from Earth center.

    a_net(r) = ω²·r - GM/r²

    Positive = outward (above GEO), negative = inward (below GEO).
    """
    return omega**2 * r - GM / r**2


def compute_taper_ratio(sigma_design: float, rho: float, GM: float,
                        omega: float, R_earth: float, L_total: float,
                        n_points: int = 200_000) -> dict:
    """
    Compute the exponential taper ratio τ = A_max / A_base.

    The cross-sectional area satisfies:
        d(ln A)/dr = (ρ / σ_design) · a_net(r)

    where a_net(r) = ω²r - GM/r². We integrate ln(A) from the surface
    (r = R_earth) to the tip (r = R_earth + L_total).

    The maximum area occurs at GEO where a_net = 0.

    Parameters
    ----------
    sigma_design : float
        Stress used for taper sizing [Pa].
    rho : float
        Tether density [kg/m³].
    GM, omega, R_earth, L_total : float
        Physical and geometric constants.
    n_points : int
        Integration resolution.

    Returns
    -------
    dict with tau, lnA_max, r_peak, altitude_peak_km
    """
    r = np.linspace(R_earth, R_earth + L_total, n_points)

    # d(ln A)/dr = (rho / sigma) * a_net(r)
    # Positive a_net above GEO means A increases outward from base to GEO,
    # then decreases from GEO outward.
    # But we want uniform stress: dA/dr = -(ρ/σ) * g_net * A  where g_net
    # is the net DOWNWARD acceleration. a_net = -g_net.
    # So d(ln A)/dr = -(ρ/σ) * g_net = (ρ/σ) * a_net
    #
    # Actually let's be careful with signs.
    # Force balance on an element at radius r, rotating with Earth:
    #   dT/dr = -ρ A(r) [GM/r² - ω²r]  (net inward body force)
    # For uniform stress σ = T/A:
    #   d(σA)/dr = -ρ A [GM/r² - ω²r]
    #   σ dA/dr + A dσ/dr = -ρ A [GM/r² - ω²r]
    # For UNIFORM stress (dσ/dr = 0):
    #   σ dA/dr = -ρ A [GM/r² - ω²r]
    #   d(ln A)/dr = -(ρ/σ) [GM/r² - ω²r]
    #              = (ρ/σ) [ω²r - GM/r²]
    #              = (ρ/σ) * a_net(r)

    integrand = -(rho / sigma_design) * (omega**2 * r - GM / r**2)
    lnA = integrate.cumulative_trapezoid(integrand, r, initial=0.0)

    # τ = exp(max(lnA) - lnA[0]) = exp(max(lnA)) since lnA[0] = 0
    idx_peak = np.argmax(lnA)
    lnA_max = lnA[idx_peak]
    tau = np.exp(lnA_max)
    r_peak = r[idx_peak]
    alt_peak_km = (r_peak - R_earth) / 1e3

    # Also compute lnA at the tip (counterweight end)
    lnA_tip = lnA[-1]
    tau_tip = np.exp(lnA_tip)  # A_tip / A_base — should be ~1 if tip ≈ base

    return {
        "tau": tau,
        "lnA_max": lnA_max,
        "lnA_tip": lnA_tip,
        "tau_tip": tau_tip,
        "r_peak": r_peak,
        "altitude_peak_km": alt_peak_km,
    }


def main():
    params = load_params()

    GM = params["physical"]["GM_earth"]
    omega = params["physical"]["omega_earth"]
    R_earth = params["physical"]["R_earth"]
    rho = params["material"]["rho"]
    L_total = params["tether"]["L_total"]
    sigma_u = params["material"]["sigma_u_baseline"]
    SF = params["design"]["SF"]
    sigma_allow = params["design"]["sigma_allow"]
    chi_rad = params["design"]["chi_rad"]
    eta_j = params["design"]["eta_j_baseline"]

    # GEO check
    r_GEO = (GM / omega**2) ** (1.0 / 3.0)
    h_GEO = r_GEO - R_earth
    print(f"Computed GEO altitude: {h_GEO/1e3:.0f} km  (expected ~35,786 km)")
    print()

    # -------------------------------------------------------------------
    # Case 1: Taper at σ_u = 50 GPa (full ultimate strength, no SF)
    # -------------------------------------------------------------------
    case1 = compute_taper_ratio(sigma_u, rho, GM, omega, R_earth, L_total)
    specific_strength_1 = (sigma_u / rho) / 1e6  # MYuri = MPa·m³/kg

    # -------------------------------------------------------------------
    # Case 2: Taper at σ_allow = σ_u / SF = 25 GPa
    # -------------------------------------------------------------------
    case2 = compute_taper_ratio(sigma_allow, rho, GM, omega, R_earth, L_total)
    specific_strength_2 = (sigma_allow / rho) / 1e6

    # -------------------------------------------------------------------
    # Case 3: Taper at σ_allow_net = σ_u · χ_rad · η_j / SF = 20.2 GPa
    # -------------------------------------------------------------------
    sigma_allow_net = sigma_u * chi_rad * eta_j / SF
    case3 = compute_taper_ratio(sigma_allow_net, rho, GM, omega, R_earth, L_total)
    specific_strength_3 = (sigma_allow_net / rho) / 1e6

    # -------------------------------------------------------------------
    # Print comparison table
    # -------------------------------------------------------------------
    print("=" * 80)
    print("TAPER RATIO INVESTIGATION — RESOLVING THE DISCREPANCY")
    print("=" * 80)
    print()
    print(f"  Material:  ρ = {rho:.0f} kg/m³")
    print(f"  σ_u       = {sigma_u/1e9:.1f} GPa  (baseline ultimate)")
    print(f"  SF        = {SF:.1f}")
    print(f"  χ_rad     = {chi_rad:.2f}")
    print(f"  η_j       = {eta_j:.2f}")
    print(f"  σ_allow   = σ_u / SF = {sigma_allow/1e9:.1f} GPa")
    print(f"  σ_allow,net = σ_u·χ·η/SF = {sigma_allow_net/1e9:.1f} GPa")
    print(f"  L_total   = {L_total/1e3:.0f} km")
    print()

    header = f"{'Case':<35} {'σ_design [GPa]':>14} {'Sp.Str [MYuri]':>15} {'τ':>12} {'ln(τ)':>8} {'Peak alt [km]':>14}"
    print(header)
    print("-" * len(header))

    for label, case, ss, sd in [
        ("1. σ_u (no safety factor)", case1, specific_strength_1, sigma_u),
        ("2. σ_allow = σ_u/SF", case2, specific_strength_2, sigma_allow),
        ("3. σ_allow,net (full knockdown)", case3, specific_strength_3, sigma_allow_net),
    ]:
        print(f"{label:<35} {sd/1e9:>14.1f} {ss:>15.2f} {case['tau']:>12.2f} {case['lnA_max']:>8.3f} {case['altitude_peak_km']:>14.0f}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()
    print("  If the draft claims τ ≈ 1.6, it almost certainly used σ_u = 50 GPa")
    print("  (specific strength ~38.5 MYuri) for the taper calculation, NOT σ_allow.")
    print()
    print("  At σ_allow = 25 GPa (SF=2), τ ≈ 12 — much more demanding.")
    print("  At σ_allow,net = 20.2 GPa (full knockdown), τ is even larger.")
    print()
    print("  DECISION NEEDED: Which stress to use for taper sizing?")
    print("    - σ_u:         optimistic, matches draft τ ≈ 1.6")
    print("    - σ_allow:     conservative, accounts for safety factor")
    print("    - σ_allow,net: most conservative, includes χ_rad and η_j")
    print()

    # -------------------------------------------------------------------
    # Also sweep σ_u to show sensitivity
    # -------------------------------------------------------------------
    print("=" * 80)
    print("SENSITIVITY: τ vs σ_u (taper sized at σ_u, no SF)")
    print("=" * 80)
    print()
    sweep = params["sensitivity"]["sigma_u_sweep"]
    header2 = f"{'σ_u [GPa]':>10} {'Sp.Str [MYuri]':>15} {'τ (at σ_u)':>12} {'τ (at σ_u/SF)':>14}"
    print(header2)
    print("-" * len(header2))
    for su in sweep:
        su = float(su)
        c_u = compute_taper_ratio(su, rho, GM, omega, R_earth, L_total)
        c_a = compute_taper_ratio(su / SF, rho, GM, omega, R_earth, L_total)
        ss = (su / rho) / 1e6
        print(f"{su/1e9:>10.0f} {ss:>15.2f} {c_u['tau']:>12.2f} {c_a['tau']:>14.2f}")

    print()
    print("  Literature reference: Edwards & Westling (2003) quote τ ≈ 1.9")
    print("  at ~38 MYuri, consistent with Case 1 (σ_u = 50 GPa).")


if __name__ == "__main__":
    main()
