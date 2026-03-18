"""
taper_profile.py — Static taper profile and NIAC validation

Integrates the continuous cross-sectional area A(y) and tension T(y) along
a space-elevator tether from Earth's surface to the counterweight, then
computes the piecewise-constant N-segment stepped profile.

Outputs:
    data/processed/taper_profiles.npz
    data/processed/sigma_u_sensitivity.json
    paper/figures/fig_taper_validation.pdf
    paper/figures/fig_sigma_sensitivity.pdf

Reference:
    Edwards & Westling (2003) NIAC Phase II — validation target
    Peters (2009) — analytical taper solutions
"""

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
    """Load the locked master parameter file."""
    with open(path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Physics: gravity-gradient + centrifugal net acceleration
# ---------------------------------------------------------------------------
def net_acceleration(y: float, params: dict) -> float:
    """
    Net outward acceleration at radial distance y from Earth center.

    g_net(y) = -GM/y² + omega² * y

    Parameters
    ----------
    y : float
        Radial distance from Earth center [m].
    params : dict
        Must contain physical.GM_earth and physical.omega_earth.

    Returns
    -------
    float
        Net outward acceleration [m/s²]. Positive = outward (above GEO).
    """
    GM = params["physical"]["GM_earth"]
    omega = params["physical"]["omega_earth"]
    return -GM / y**2 + omega**2 * y


# ---------------------------------------------------------------------------
# Continuous taper profile A(y)
# ---------------------------------------------------------------------------
def integrate_taper_profile(params: dict, sigma_design: float = None,
                            n_points: int = 100_000):
    """
    Numerically integrate the continuous taper profile A(y).

    The cross-sectional area follows:
        dA/dy = -(rho / sigma_design) * g_net(y) * A(y)

    which gives exponential tapering with the ratio tau = A_max / A_base.

    Parameters
    ----------
    params : dict
        Master parameter dictionary.
    sigma_design : float, optional
        Design stress for taper sizing [Pa]. Defaults to sigma_allow from params.
    n_points : int
        Number of radial integration points.

    Returns
    -------
    dict with keys:
        y : ndarray — radial positions [m]
        A : ndarray — normalized cross-sectional area A(y)/A_base
        T : ndarray — tension profile [N] (per unit A_base)
        sigma : ndarray — stress profile [Pa]
        tau : float — taper ratio A_max / A_base
    """
    R = params["physical"]["R_earth"]
    L = params["tether"]["L_total"]
    rho = params["material"]["rho"]

    if sigma_design is None:
        sigma_design = params["design"]["sigma_allow"]

    y = np.linspace(R, R + L, n_points)

    # Integrate ln(A) to avoid numerical overflow
    # d(ln A)/dy = -(rho / sigma_design) * g_net(y)
    def d_lnA_dy(y_val, _):
        return -(rho / sigma_design) * net_acceleration(y_val, params)

    lnA_solution = integrate.odeint(d_lnA_dy, 0.0, y)
    lnA = lnA_solution.flatten()

    A_ratio = np.exp(lnA)  # A(y) / A(R_earth)
    tau = np.max(A_ratio)

    # Tension: T(y) = integral from R to y of rho * A(y') * g_net(y') dy'
    # For now, compute stress sigma(y) = T(y) / A(y)
    T = np.zeros_like(y)
    sigma = np.zeros_like(y)

    # TODO: Compute tension profile via cumulative integration
    # TODO: Validate against Edwards & Westling Fig. 4

    return {"y": y, "A": A_ratio, "T": T, "sigma": sigma, "tau": tau}


# ---------------------------------------------------------------------------
# Stepped (segmented) profile
# ---------------------------------------------------------------------------
def compute_stepped_profile(y, A_ratio, params: dict, N: int = None):
    """
    Compute the piecewise-constant N-segment stepped profile.

    Variable-length segments equalize mass at m_star per segment:
        L_j = m_star / (rho * A(y_j,mid))

    Parameters
    ----------
    y : ndarray
        Radial positions [m].
    A_ratio : ndarray
        Normalized cross-sectional area profile.
    params : dict
        Master parameter dictionary.
    N : int, optional
        Number of segments. Defaults to N_baseline from params.

    Returns
    -------
    dict with keys:
        boundaries : ndarray — segment boundary positions [m]
        lengths : ndarray — segment lengths [m]
        areas : ndarray — segment cross-sectional areas (normalized)
        masses : ndarray — segment masses [kg] (require A_base to be physical)
    """
    if N is None:
        N = params["segments"]["N_baseline"]

    rho = params["material"]["rho"]
    m_star = params["segments"]["m_star"]

    # TODO: Implement variable-length segmentation (Eq. 10)
    # 1. Start from base, find L_j such that integral of rho*A*dy = m_star
    # 2. Assign piecewise-constant A_j = A(y_j,mid)
    # 3. Check m_j <= m_launch_cap for all segments

    boundaries = np.array([])
    lengths = np.array([])
    areas = np.array([])
    masses = np.array([])

    return {
        "boundaries": boundaries,
        "lengths": lengths,
        "areas": areas,
        "masses": masses,
    }


# ---------------------------------------------------------------------------
# Sensitivity sweep over sigma_u
# ---------------------------------------------------------------------------
def sigma_u_sensitivity(params: dict):
    """
    Sweep ultimate tensile strength and recompute taper ratio, total mass,
    segment count, and max segment mass for each value.

    Returns
    -------
    list[dict]
        One entry per sigma_u value with keys: sigma_u, tau, M_total, N, m_j_max.
    """
    sweep_values = params["sensitivity"]["sigma_u_sweep"]
    SF = params["design"]["SF"]
    results = []

    for sigma_u in sweep_values:
        sigma_design = sigma_u / SF
        profile = integrate_taper_profile(params, sigma_design=sigma_design)
        results.append({
            "sigma_u": sigma_u,
            "sigma_design": sigma_design,
            "tau": profile["tau"],
            # TODO: compute M_total, N, m_j_max from stepped profile
            "M_total": None,
            "N": None,
            "m_j_max": None,
        })

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_taper_validation(profile: dict, output_path: Path = None):
    """
    Plot continuous vs. stepped taper profile, overlay on NIAC baseline.
    """
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.5))

    y_km = (profile["y"] - profile["y"][0]) / 1e3  # altitude in km

    # Left: A(y)
    axes[0].plot(y_km, profile["A"], label="Continuous taper")
    axes[0].set_xlabel("Altitude [km]")
    axes[0].set_ylabel("$A(y) / A_{\\mathrm{base}}$")
    axes[0].set_title("Cross-sectional area profile")
    axes[0].legend()

    # Right: T(y) — placeholder until tension is computed
    axes[1].plot(y_km, profile["T"], label="Tension")
    axes[1].set_xlabel("Altitude [km]")
    axes[1].set_ylabel("Tension [N]")
    axes[1].set_title("Tension profile")
    axes[1].legend()

    # TODO: Overlay digitized Edwards & Westling Fig. 4

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)


def plot_sigma_sensitivity(results: list, output_path: Path = None):
    """
    Plot taper ratio and total mass vs. sigma_u.
    """
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    sigma_u_GPa = [r["sigma_u"] / 1e9 for r in results]
    tau_vals = [r["tau"] for r in results]

    fig, ax = plt.subplots()
    ax.plot(sigma_u_GPa, tau_vals, "o-")
    ax.set_xlabel("$\\sigma_u$ [GPa]")
    ax.set_ylabel("Taper ratio $\\tau$")
    ax.set_title("Material sensitivity: taper ratio vs. CNT strength")

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    params = load_params()

    # 1. Continuous taper profile at baseline sigma_allow
    profile = integrate_taper_profile(params)
    print(f"Taper ratio (baseline): tau = {profile['tau']:.2f}")

    # 2. Stepped profile
    stepped = compute_stepped_profile(profile["y"], profile["A"], params)

    # 3. Sigma_u sensitivity sweep
    sensitivity = sigma_u_sensitivity(params)
    for r in sensitivity:
        print(f"  sigma_u = {r['sigma_u']/1e9:.0f} GPa  →  tau = {r['tau']:.2f}")

    # 4. Plots
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    plot_taper_validation(profile, FIGURES_DIR / "fig_taper_validation.pdf")
    plot_sigma_sensitivity(sensitivity, FIGURES_DIR / "fig_sigma_sensitivity.pdf")

    # 5. Save data
    np.savez(
        OUTPUT_DIR / "taper_profiles.npz",
        y=profile["y"],
        A=profile["A"],
        T=profile["T"],
        sigma=profile["sigma"],
        tau=profile["tau"],
    )

    print("Done. Outputs saved to data/processed/ and paper/figures/.")


if __name__ == "__main__":
    main()
