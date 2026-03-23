"""
taper_profile.py — Static taper profile and NIAC validation

Integrates the continuous cross-sectional area A(y) and tension T(y) along
a space-elevator tether from Earth's surface to the counterweight, then
computes the piecewise-constant N-segment stepped profile.

Supports dual design envelopes:
  - sigma_u:     taper at full ultimate strength (optimistic, Edwards & Westling)
  - sigma_allow: taper at sigma_u / SF (conservative, with safety factor)
  - both:        run both and produce comparison figures

Usage:
    python simulations/fea/taper_profile.py --mode baseline
    python simulations/fea/taper_profile.py --mode sensitivity
    python simulations/fea/taper_profile.py --mode sensitivity --taper-stress sigma_u
    python simulations/fea/taper_profile.py --mode all --taper-stress both

Outputs:
    data/processed/taper_profiles.npz
    data/processed/sigma_u_sensitivity.json
    data/processed/sigma_u_sensitivity_optimistic.json
    data/processed/sigma_u_sensitivity_conservative.json
    paper/figures/fig_taper_validation.pdf
    paper/figures/fig_sigma_sensitivity.pdf
    paper/figures/fig_design_envelope_comparison.pdf

Reference:
    Edwards & Westling (2003) NIAC Phase II — validation target
    Peters (2009) — analytical taper solutions
"""

import argparse
import json
from pathlib import Path
import numpy as np
from scipy import integrate
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
# Physics: gravity-gradient + centrifugal net acceleration
# ---------------------------------------------------------------------------
def net_acceleration(r: np.ndarray, params: dict) -> np.ndarray:
    """
    Net outward acceleration at radial distance r from Earth center.

    a_net(r) = omega^2 * r - GM / r^2

    Positive above GEO (outward), negative below GEO (inward toward Earth).

    Parameters
    ----------
    r : float or ndarray
        Radial distance from Earth center [m].
    params : dict
        Must contain physical.GM_earth and physical.omega_earth.

    Returns
    -------
    float or ndarray
        Net outward acceleration [m/s^2].
    """
    GM = float(params["physical"]["GM_earth"])
    omega = float(params["physical"]["omega_earth"])
    return omega**2 * r - GM / r**2


# ---------------------------------------------------------------------------
# Continuous taper profile A(y), T(y), sigma(y)
# ---------------------------------------------------------------------------
def integrate_taper_profile(params: dict, sigma_design: float = None,
                            n_points: int = 100_001):
    """
    Numerically integrate the continuous taper profile A(r), T(r), sigma(r).

    The uniform-stress cross-sectional area satisfies:
        d(ln A)/dr = (rho / sigma_design) * [omega^2 r - GM/r^2]

    Tension is computed via:
        T(r) = sigma_design * A(r)    (uniform stress by construction)

    but we also compute the physical tension from force balance:
        dT/dr = -rho * A(r) * [GM/r^2 - omega^2 r]

    Parameters
    ----------
    params : dict
        Master parameter dictionary.
    sigma_design : float, optional
        Design stress for taper sizing [Pa]. Defaults to sigma_allow from params.
    n_points : int
        Number of radial integration points (~1 km resolution at 100,001).

    Returns
    -------
    dict with keys:
        r       : ndarray — radial positions from Earth center [m]
        alt     : ndarray — altitude above surface [m]
        A_ratio : ndarray — normalized cross-sectional area A(r)/A(R_surface)
        T       : ndarray — tension profile [N per unit A_base in m^2]
        sigma   : ndarray — stress profile [Pa]
        tau     : float   — taper ratio A_max / A_base
        r_peak  : float   — radial position of peak area [m]
    """
    R = float(params["physical"]["R_earth"])
    L = float(params["tether"]["L_total"])
    rho = float(params["material"]["rho"])

    if sigma_design is None:
        sigma_design = float(params["design"]["sigma_allow"])

    r = np.linspace(R, R + L, n_points)
    dr = r[1] - r[0]
    alt = r - R

    # --- Area profile via ln(A) integration ---
    # d(ln A)/dr = (rho/sigma) * a_net(r)
    a_net = net_acceleration(r, params)
    integrand_lnA = -(rho / sigma_design) * a_net
    lnA = integrate.cumulative_trapezoid(integrand_lnA, r, initial=0.0)
    A_ratio = np.exp(lnA)  # A(r) / A(R_surface)

    tau = float(np.max(A_ratio))
    idx_peak = int(np.argmax(A_ratio))
    r_peak = r[idx_peak]

    # --- Tension profile ---
    # For uniform-stress taper: T(r) = sigma * A(r), so T/A_base = sigma * A_ratio
    # This gives tension per unit base area [Pa*(dimensionless) = N/m^2*m^2 = N per m^2 of A_base]
    T_per_Abase = sigma_design * A_ratio  # [N per m^2 of base area]

    # Physical tension from force balance (integrating from the base upward):
    # dT/dr = -rho * A(r) * [GM/r^2 - omega^2 r] = rho * A(r) * a_net(r)
    # T(R_surface) = boundary tension (from counterweight or = sigma*A_base)
    # Integrate: T(r) = T(R) + integral_R^r rho*A(r')*a_net(r') dr'
    # With A(r') = A_base * A_ratio(r'):
    # T(r)/A_base = sigma_design*A_ratio(R) + integral rho*A_ratio*a_net dr'
    # But for uniform stress: T(r)/A_base = sigma_design*A_ratio(r) exactly.
    # We use the force-balance integral as a consistency check.
    force_integrand = rho * A_ratio * a_net  # [kg/m^3 * (dimless) * m/s^2 = Pa/m per m^2 of A_base]
    # Force balance: dT/dr = -rho * A(r) * a_net(r) for uniform-stress taper.
    # Integrating from tip (T(L)=0) inward:
    #   T(r)/A_base = ∫_r^L rho * A_ratio(r') * a_net(r') dr'
    # This must match sigma_design * A_ratio(r) exactly.
    T_force_balance = integrate.cumulative_trapezoid(
        force_integrand[::-1], r[::-1], initial=0.0
    )[::-1]

    # Stress: sigma(r) = T(r) / A(r) — should be uniform = sigma_design
    sigma = T_per_Abase / A_ratio  # Should be constant = sigma_design

    return {
        "r": r,
        "alt": alt,
        "A_ratio": A_ratio,
        "T": T_per_Abase,
        "T_force_balance": T_force_balance,
        "sigma": sigma,
        "tau": tau,
        "r_peak": r_peak,
        "sigma_design": sigma_design,
    }


# ---------------------------------------------------------------------------
# Stepped (segmented) profile — mass-equalization walk
# ---------------------------------------------------------------------------
def compute_stepped_profile(profile: dict, params: dict,
                            sigma_design: float = None):
    """
    Compute the piecewise-constant stepped profile via mass-equalization walk.

    Algorithm:
    1. Compute A_base from the PAYLOAD requirement:
       A_base = m_climber * g_surface / sigma_design
       where g_surface = GM / R_earth^2.
    2. Walk from the surface along the tether, integrating
       rho * A_base * A_ratio(r) dr until the accumulated mass reaches
       m_star. That defines one segment. Continue until the tether is
       consumed. N is determined by the physics, not prescribed.
    3. If the last segment mass is less than 0.5 * m_star, merge it into
       the previous segment.
    4. Report feasibility: every segment mass <= m_launch_cap.

    Parameters
    ----------
    profile : dict
        Output from integrate_taper_profile().
    params : dict
        Master parameter dictionary.
    sigma_design : float, optional
        Design stress [Pa]. If None, uses profile["sigma_design"].

    Returns
    -------
    dict with keys:
        N           : int     — number of segments
        boundaries  : ndarray — segment boundary altitudes [m]
        midpoints   : ndarray — segment midpoint altitudes [m]
        lengths     : ndarray — segment lengths [m]
        A_ratios    : ndarray — area ratio at each segment midpoint
        A_base      : float   — physical base cross-sectional area [m^2]
        masses      : ndarray — segment masses [kg]
        m_max       : float   — heaviest segment mass [kg]
        M_total     : float   — total tether mass incl. joints [kg]
        m_sleeve    : float   — joint sleeve mass [kg]
        total_joint_mass : float
        feasible    : bool    — all segments <= m_launch_cap
    """
    rho = float(params["material"]["rho"])
    m_star = float(params["segments"]["m_star"])
    m_launch_cap = float(params["segments"]["m_launch_cap"])
    m_sleeve = float(params["segments"]["m_sleeve"])
    GM = float(params["physical"]["GM_earth"])
    R = float(params["physical"]["R_earth"])
    L_total = float(params["tether"]["L_total"])
    m_climber = float(params["climber"]["m_climber"])

    if sigma_design is None:
        sigma_design = profile["sigma_design"]

    r = profile["r"]
    A_ratio = profile["A_ratio"]

    # ------------------------------------------------------------------
    # 1. A_base from payload requirement
    # ------------------------------------------------------------------
    g_surface = GM / R**2
    A_base = m_climber * g_surface / sigma_design

    # ------------------------------------------------------------------
    # 2. Mass-equalization walk
    # ------------------------------------------------------------------
    # Linear mass density along the profile: dm/dr = rho * A_base * A_ratio(r)
    # We integrate this cumulatively and cut whenever it reaches m_star.
    mass_density = rho * A_base * A_ratio  # [kg/m] at each r
    cum_mass = integrate.cumulative_trapezoid(mass_density, r, initial=0.0)

    boundaries_alt = [0.0]  # altitudes from surface
    seg_masses = []
    mass_so_far = 0.0

    for i in range(1, len(cum_mass)):
        seg_mass = cum_mass[i] - mass_so_far
        if seg_mass >= m_star:
            # Place boundary at this radial position
            alt_i = float(r[i] - R)
            boundaries_alt.append(alt_i)
            seg_masses.append(seg_mass)
            mass_so_far = cum_mass[i]

    # Last partial segment: whatever remains
    remaining = cum_mass[-1] - mass_so_far
    if remaining > 0:
        boundaries_alt.append(L_total)
        seg_masses.append(remaining)

    # ------------------------------------------------------------------
    # 3. Merge small trailing segment
    # ------------------------------------------------------------------
    if len(seg_masses) > 1 and seg_masses[-1] < 0.5 * m_star:
        combined = seg_masses[-2] + seg_masses[-1]
        if combined <= m_star:
            # Simple merge — combined is within launch-cap budget
            seg_masses[-2] = combined
            seg_masses.pop()
            boundaries_alt.pop(-2)  # remove internal boundary between merged segments
        # else: leave small trailing segment as-is.
        # Merging would exceed m_star (launch cap violation).
        # A sub-target trailing segment is acceptable.

    boundaries = np.array(boundaries_alt)
    masses = np.array(seg_masses)
    N_actual = len(masses)

    lengths = np.diff(boundaries)
    midpoints = boundaries[:-1] + lengths / 2.0

    # Area ratio at each midpoint
    A_ratios = np.interp(R + midpoints, r, A_ratio)

    # Joint mass (N-1 internal joints)
    total_joint_mass = (N_actual - 1) * m_sleeve

    feasible = bool(np.all(masses <= m_launch_cap))

    return {
        "N": N_actual,
        "boundaries": boundaries,
        "midpoints": midpoints,
        "lengths": lengths,
        "A_ratios": A_ratios,
        "A_base": A_base,
        "masses": masses,
        "m_max": float(np.max(masses)),
        "M_total": float(np.sum(masses)) + total_joint_mass,
        "m_sleeve": m_sleeve,
        "total_joint_mass": total_joint_mass,
        "feasible": feasible,
    }


# ---------------------------------------------------------------------------
# Sensitivity sweep over sigma_u
# ---------------------------------------------------------------------------
def sigma_u_sensitivity(params: dict, use_sigma_u_for_taper: bool = False):
    """
    Sweep ultimate tensile strength and recompute taper ratio, total mass,
    segment count, and max segment mass for each value.

    Parameters
    ----------
    params : dict
        Master parameter dictionary.
    use_sigma_u_for_taper : bool
        If True, sigma_design = sigma_u (optimistic, Edwards & Westling approach).
            Expected: tau ~ 3.5 at 50 GPa, N ~ 18.
        If False, sigma_design = sigma_u / SF (conservative, with safety factor).
            Expected: tau ~ 12.4 at 50 GPa, N ~ 505.

    For each sigma_u:
    1. sigma_design = sigma_u (if use_sigma_u_for_taper) or sigma_u / SF
    2. Integrate continuous taper profile at that sigma_design
    3. Compute A_base from payload: A_base = m_climber * GM/R^2 / sigma_design
    4. Run mass-equalization walk with that A_base
    5. Report: sigma_u, tau, N, M_total, m_j_max, feasible (all m_j <= 30 t)

    Returns
    -------
    list[dict]
        One entry per sigma_u value with keys:
        sigma_u, sigma_design, tau, M_total, N, m_j_max, feasible,
        specific_strength, A_base
    """
    sweep_values = params["sensitivity"]["sigma_u_sweep"]
    SF = float(params["design"]["SF"])
    results = []

    for sigma_u in sweep_values:
        sigma_u = float(sigma_u)
        if use_sigma_u_for_taper:
            sigma_design = sigma_u
        else:
            sigma_design = sigma_u / SF

        profile = integrate_taper_profile(params, sigma_design=sigma_design)
        stepped = compute_stepped_profile(profile, params,
                                          sigma_design=sigma_design)

        specific_strength = (sigma_u / float(params["material"]["rho"])) / 1e6  # MYuri

        results.append({
            "sigma_u": sigma_u,
            "sigma_design": sigma_design,
            "specific_strength": specific_strength,
            "tau": profile["tau"],
            "M_total": stepped["M_total"],
            "N": stepped["N"],
            "m_j_max": stepped["m_max"],
            "A_base": stepped["A_base"],
            "feasible": stepped["feasible"],
        })

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_taper_validation(profile: dict, stepped: dict,
                          output_path: Path = None):
    """
    Plot continuous vs. stepped taper profile.

    Left panel: A(r)/A_base vs altitude
    Right panel: Tension T(r) vs altitude
    Both panels overlay the stepped (segmented) profile.
    """
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.5))

    alt_km = profile["alt"] / 1e3
    R = profile["r"][0]

    # --- Left panel: Area profile ---
    ax = axes[0]
    ax.plot(alt_km, profile["A_ratio"], linewidth=1.0, label="Continuous taper")

    # Overlay stepped profile
    for i in range(stepped["N"]):
        lo = stepped["boundaries"][i] / 1e3
        hi = stepped["boundaries"][i + 1] / 1e3
        A_step = stepped["A_ratios"][i]
        ax.plot([lo, hi], [A_step, A_step], color="#D55E00", linewidth=0.8,
                label="Stepped profile" if i == 0 else None)

    ax.set_xlabel("Altitude [km]")
    ax.set_ylabel("$A(r) / A_{\\mathrm{base}}$")
    ax.set_title("Cross-sectional area profile")
    ax.legend(fontsize=7)
    ax.set_xlim(0, float(profile["alt"][-1]) / 1e3)

    # Annotate taper ratio
    tau = profile["tau"]
    ax.annotate(f"$\\tau$ = {tau:.1f}",
                xy=(float(profile["r_peak"] - R) / 1e3, tau),
                xytext=(50000, tau * 0.6),
                arrowprops=dict(arrowstyle="->", color="gray"),
                fontsize=8)

    # --- Right panel: Tension profile ---
    ax = axes[1]
    ax.plot(alt_km, profile["T"] / 1e9, linewidth=1.0, label="$T(r)$ (uniform stress)")
    ax.plot(alt_km, profile["T_force_balance"] / 1e9, "--", linewidth=0.8,
            alpha=0.7, label="$T(r)$ (force balance check)")
    ax.set_xlabel("Altitude [km]")
    ax.set_ylabel("Tension / $A_{\\mathrm{base}}$ [GN/m$^2$]")
    ax.set_title("Tension profile")
    ax.legend(fontsize=7)
    ax.set_xlim(0, float(profile["alt"][-1]) / 1e3)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
        print(f"  Saved: {output_path}")
    plt.close(fig)


def plot_sigma_sensitivity(results: list, output_path: Path = None):
    """
    2x2 subplot grid for sigma_u sensitivity sweep.

    Panels: tau vs sigma_u, N vs sigma_u, M_total vs sigma_u,
            m_j_max vs sigma_u (with 30 t launch-cap line).
    Feasible points are green, infeasible points are red.
    """
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    sigma_u_GPa = np.array([r["sigma_u"] / 1e9 for r in results])
    tau_vals = np.array([r["tau"] for r in results])
    N_vals = np.array([r["N"] for r in results])
    M_total_t = np.array([r["M_total"] / 1e3 for r in results])
    m_max_t = np.array([r["m_j_max"] / 1e3 for r in results])
    feasible = np.array([r["feasible"] for r in results])
    # Recover launch cap from first result context — use 30 t directly
    m_cap_t = 30.0

    colors = np.where(feasible, "#009E73", "#D55E00")

    fig, axes = plt.subplots(2, 2, figsize=(7.48, 6.0))

    # --- (0,0): tau vs sigma_u ---
    ax = axes[0, 0]
    for i in range(len(results)):
        ax.plot(sigma_u_GPa[i], tau_vals[i], "o", color=colors[i], markersize=6)
    ax.plot(sigma_u_GPa, tau_vals, "-", color="gray", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Taper ratio $\\tau$")
    ax.set_yscale("log")
    ax.set_title("Taper ratio")

    # --- (0,1): N vs sigma_u ---
    ax = axes[0, 1]
    for i in range(len(results)):
        ax.plot(sigma_u_GPa[i], N_vals[i], "o", color=colors[i], markersize=6)
    ax.plot(sigma_u_GPa, N_vals, "-", color="gray", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Number of segments $N$")
    ax.set_title("Segment count")

    # --- (1,0): M_total vs sigma_u ---
    ax = axes[1, 0]
    for i in range(len(results)):
        ax.plot(sigma_u_GPa[i], M_total_t[i], "o", color=colors[i], markersize=6)
    ax.plot(sigma_u_GPa, M_total_t, "-", color="gray", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Total tether mass [t]")
    ax.set_title("Total mass")

    # --- (1,1): m_j_max vs sigma_u ---
    ax = axes[1, 1]
    for i in range(len(results)):
        ax.plot(sigma_u_GPa[i], m_max_t[i], "o", color=colors[i], markersize=6)
    ax.plot(sigma_u_GPa, m_max_t, "-", color="gray", linewidth=0.8, alpha=0.5)
    ax.axhline(m_cap_t, color="red", linestyle="--", linewidth=1.0,
               label=f"Launch cap = {m_cap_t:.0f} t")
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Max segment mass [t]")
    ax.set_title("Heaviest segment")
    ax.legend(fontsize=7)

    # Add a shared legend for feasibility
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#009E73",
               markersize=7, label="Feasible"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#D55E00",
               markersize=7, label="Infeasible"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=2,
               fontsize=8, frameon=False,
               bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
        print(f"  Saved: {output_path}")
    plt.close(fig)


def plot_design_envelope_comparison(results_optimistic: list,
                                    results_conservative: list,
                                    output_path: Path = None):
    """
    Side-by-side comparison of optimistic (sigma_u taper) and conservative
    (sigma_allow taper) design envelopes.

    2x2 grid:
        (0,0) tau vs sigma_u
        (0,1) N vs sigma_u
        (1,0) M_total vs sigma_u
        (1,1) m_j_max vs sigma_u  (with 30 t red dashed launch cap)

    Each subplot has TWO lines: optimistic and conservative.
    """
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    # --- Extract arrays ---
    sig_opt = np.array([r["sigma_u"] / 1e9 for r in results_optimistic])
    sig_con = np.array([r["sigma_u"] / 1e9 for r in results_conservative])

    tau_opt = np.array([r["tau"] for r in results_optimistic])
    tau_con = np.array([r["tau"] for r in results_conservative])

    N_opt = np.array([r["N"] for r in results_optimistic])
    N_con = np.array([r["N"] for r in results_conservative])

    M_opt = np.array([r["M_total"] / 1e3 for r in results_optimistic])
    M_con = np.array([r["M_total"] / 1e3 for r in results_conservative])

    m_opt = np.array([r["m_j_max"] / 1e3 for r in results_optimistic])
    m_con = np.array([r["m_j_max"] / 1e3 for r in results_conservative])

    m_cap_t = 30.0

    fig, axes = plt.subplots(2, 2, figsize=(7.48, 6.0))

    label_opt = "$\\sigma_u$ taper (optimistic)"
    label_con = "$\\sigma_{\\mathrm{allow}}$ taper (conservative)"
    color_opt = "#0072B2"
    color_con = "#D55E00"

    # --- (0,0): tau vs sigma_u ---
    ax = axes[0, 0]
    ax.plot(sig_opt, tau_opt, "o-", color=color_opt, markersize=5,
            linewidth=1.2, label=label_opt)
    ax.plot(sig_con, tau_con, "s-", color=color_con, markersize=5,
            linewidth=1.2, label=label_con)
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Taper ratio $\\tau$")
    ax.set_yscale("log")
    ax.set_title("Taper ratio")
    ax.legend(fontsize=6)

    # --- (0,1): N vs sigma_u ---
    ax = axes[0, 1]
    ax.plot(sig_opt, N_opt, "o-", color=color_opt, markersize=5,
            linewidth=1.2, label=label_opt)
    ax.plot(sig_con, N_con, "s-", color=color_con, markersize=5,
            linewidth=1.2, label=label_con)
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Number of segments $N$")
    ax.set_title("Segment count")
    ax.legend(fontsize=6)

    # --- (1,0): M_total vs sigma_u ---
    ax = axes[1, 0]
    ax.plot(sig_opt, M_opt, "o-", color=color_opt, markersize=5,
            linewidth=1.2, label=label_opt)
    ax.plot(sig_con, M_con, "s-", color=color_con, markersize=5,
            linewidth=1.2, label=label_con)
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Total tether mass [t]")
    ax.set_title("Total mass")
    ax.legend(fontsize=6)

    # --- (1,1): m_j_max vs sigma_u ---
    ax = axes[1, 1]
    ax.plot(sig_opt, m_opt, "o-", color=color_opt, markersize=5,
            linewidth=1.2, label=label_opt)
    ax.plot(sig_con, m_con, "s-", color=color_con, markersize=5,
            linewidth=1.2, label=label_con)
    ax.axhline(m_cap_t, color="red", linestyle="--", linewidth=1.0,
               label=f"Launch cap = {m_cap_t:.0f} t")
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Max segment mass [t]")
    ax.set_title("Heaviest segment")
    ax.legend(fontsize=6)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")
        print(f"  Saved: {output_path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Helpers for JSON serialization and table printing
# ---------------------------------------------------------------------------
def _clean_for_json(results: list) -> list:
    """Convert numpy types for JSON serialization."""
    clean = []
    for r in results:
        clean.append({k: (bool(v) if isinstance(v, (bool, np.bool_))
                          else float(v) if isinstance(v, (int, float, np.floating, np.integer))
                          else v)
                      for k, v in r.items()})
    return clean


def _print_sensitivity_table(results: list, label: str):
    """Print a formatted sensitivity sweep table."""
    print(f"\n  --- {label} ---")
    header = (f"  {'sigma_u [GPa]':>12} {'Sp.Str':>8} {'tau':>10} "
              f"{'M_total [t]':>12} {'N_seg':>6} {'m_max [t]':>10} "
              f"{'A_base [mm^2]':>14} {'OK?':>5}")
    print(header)
    print("  " + "-" * 80)
    for r in results:
        ok = "YES" if r["feasible"] else "NO"
        print(f"  {r['sigma_u']/1e9:>12.0f} {r['specific_strength']:>8.1f} "
              f"{r['tau']:>10.1f} {r['M_total']/1e3:>12.0f} "
              f"{r['N']:>6d} {r['m_j_max']/1e3:>10.1f} "
              f"{r['A_base']*1e6:>14.2f} {ok:>5}")

    feasible_results = [r for r in results if r["feasible"]]
    if feasible_results:
        min_feasible = min(feasible_results, key=lambda x: x["sigma_u"])
        print(f"\n  Minimum feasible sigma_u: {min_feasible['sigma_u']/1e9:.0f} GPa")
    else:
        print("\n  WARNING: No feasible configuration found in sweep range!")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Static taper profile and NIAC validation"
    )
    parser.add_argument(
        "--mode", choices=["baseline", "sensitivity", "all"],
        default="all",
        help="baseline: single profile + stepped. "
             "sensitivity: sigma_u sweep. "
             "all: both (default)."
    )
    parser.add_argument(
        "--taper-stress",
        choices=["sigma_u", "sigma_allow", "both"],
        default="both",
        help="Design stress for taper shape: "
             "sigma_u = taper at full ultimate strength (optimistic). "
             "sigma_allow = taper at sigma_u/SF (conservative). "
             "both = run both and produce comparison figures (default)."
    )
    args = parser.parse_args()

    params = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if args.mode in ("baseline", "all"):
        print("=" * 60)
        print("BASELINE TAPER PROFILE")
        print("=" * 60)

        sigma_design = float(params["design"]["sigma_allow"])
        print(f"  sigma_design = sigma_allow = {sigma_design/1e9:.1f} GPa")

        # 1. Continuous profile
        profile = integrate_taper_profile(params)
        print(f"  Taper ratio tau = {profile['tau']:.2f}")
        print(f"  Peak area at altitude = {(profile['r_peak'] - profile['r'][0])/1e3:.0f} km")

        # Verify uniform stress
        sigma_std = np.std(profile["sigma"])
        sigma_mean = np.mean(profile["sigma"])
        print(f"  Stress uniformity: sigma_mean = {sigma_mean/1e9:.3f} GPa, "
              f"sigma_std/sigma_mean = {sigma_std/sigma_mean:.2e}")

        # 2. Stepped profile
        stepped = compute_stepped_profile(profile, params)
        print(f"\n  Stepped profile (mass-equalization walk):")
        print(f"    N segments   = {stepped['N']}")
        print(f"    M_total      = {stepped['M_total']/1e3:.1f} t")
        print(f"    m_j_max      = {stepped['m_max']/1e3:.1f} t")
        print(f"    A_base       = {stepped['A_base']*1e6:.2f} mm^2")
        print(f"    Feasible     = {stepped['feasible']}")
        print(f"    Joint mass   = {stepped['total_joint_mass']:.0f} kg "
              f"({stepped['N']-1} joints x {stepped['m_sleeve']:.0f} kg)")

        # Segment details
        print(f"\n  {'Seg':>4} {'Alt_lo [km]':>12} {'Alt_hi [km]':>12} "
              f"{'Length [km]':>12} {'A_ratio':>10} {'Mass [t]':>10}")
        print("  " + "-" * 68)
        for i in range(min(stepped["N"], 30)):  # cap display at 30
            print(f"  {i+1:>4} {stepped['boundaries'][i]/1e3:>12.0f} "
                  f"{stepped['boundaries'][i+1]/1e3:>12.0f} "
                  f"{stepped['lengths'][i]/1e3:>12.1f} "
                  f"{stepped['A_ratios'][i]:>10.3f} "
                  f"{stepped['masses'][i]/1e3:>10.2f}")
        if stepped["N"] > 30:
            print(f"  ... ({stepped['N'] - 30} more segments)")

        # 3. Plot
        plot_taper_validation(profile, stepped,
                              FIGURES_DIR / "fig_taper_validation.pdf")

        # 4. Save data
        np.savez(
            OUTPUT_DIR / "taper_profiles.npz",
            r=profile["r"],
            alt=profile["alt"],
            A_ratio=profile["A_ratio"],
            T=profile["T"],
            sigma=profile["sigma"],
            tau=profile["tau"],
            stepped_boundaries=stepped["boundaries"],
            stepped_lengths=stepped["lengths"],
            stepped_A_ratios=stepped["A_ratios"],
            stepped_masses=stepped["masses"],
        )
        print(f"\n  Saved: {OUTPUT_DIR / 'taper_profiles.npz'}")

    if args.mode in ("sensitivity", "all"):
        print()
        print("=" * 60)
        print("sigma_u SENSITIVITY SWEEP")
        print("=" * 60)

        taper_stress = args.taper_stress

        # Determine which sweeps to run
        run_optimistic = taper_stress in ("sigma_u", "both")
        run_conservative = taper_stress in ("sigma_allow", "both")

        sensitivity_optimistic = None
        sensitivity_conservative = None

        # --- Optimistic: taper at sigma_u ---
        if run_optimistic:
            sensitivity_optimistic = sigma_u_sensitivity(
                params, use_sigma_u_for_taper=True
            )
            _print_sensitivity_table(sensitivity_optimistic,
                                     "OPTIMISTIC (taper at sigma_u)")

            plot_sigma_sensitivity(
                sensitivity_optimistic,
                FIGURES_DIR / "fig_sigma_sensitivity_optimistic.pdf"
            )

            with open(OUTPUT_DIR / "sigma_u_sensitivity_optimistic.json", "w") as f:
                json.dump(_clean_for_json(sensitivity_optimistic), f, indent=2)
            print(f"  Saved: {OUTPUT_DIR / 'sigma_u_sensitivity_optimistic.json'}")

        # --- Conservative: taper at sigma_allow = sigma_u / SF ---
        if run_conservative:
            sensitivity_conservative = sigma_u_sensitivity(
                params, use_sigma_u_for_taper=False
            )
            _print_sensitivity_table(sensitivity_conservative,
                                     "CONSERVATIVE (taper at sigma_allow = sigma_u / SF)")

            plot_sigma_sensitivity(
                sensitivity_conservative,
                FIGURES_DIR / "fig_sigma_sensitivity_conservative.pdf"
            )

            with open(OUTPUT_DIR / "sigma_u_sensitivity_conservative.json", "w") as f:
                json.dump(_clean_for_json(sensitivity_conservative), f, indent=2)
            print(f"  Saved: {OUTPUT_DIR / 'sigma_u_sensitivity_conservative.json'}")

        # --- Also save the combined/default sensitivity file ---
        # Use conservative as default (backward-compatible behavior)
        if sensitivity_conservative is not None:
            with open(OUTPUT_DIR / "sigma_u_sensitivity.json", "w") as f:
                json.dump(_clean_for_json(sensitivity_conservative), f, indent=2)
            print(f"  Saved: {OUTPUT_DIR / 'sigma_u_sensitivity.json'}")
            plot_sigma_sensitivity(
                sensitivity_conservative,
                FIGURES_DIR / "fig_sigma_sensitivity.pdf"
            )
        elif sensitivity_optimistic is not None:
            with open(OUTPUT_DIR / "sigma_u_sensitivity.json", "w") as f:
                json.dump(_clean_for_json(sensitivity_optimistic), f, indent=2)
            print(f"  Saved: {OUTPUT_DIR / 'sigma_u_sensitivity.json'}")
            plot_sigma_sensitivity(
                sensitivity_optimistic,
                FIGURES_DIR / "fig_sigma_sensitivity.pdf"
            )

        # --- Comparison figure (both envelopes) ---
        if taper_stress == "both":
            print()
            print("  Generating design envelope comparison figure...")
            plot_design_envelope_comparison(
                sensitivity_optimistic,
                sensitivity_conservative,
                FIGURES_DIR / "fig_design_envelope_comparison.pdf"
            )

    print("\nDone.")


if __name__ == "__main__":
    main()
