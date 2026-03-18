"""
joint_reliability.py — Monte Carlo joint-failure reliability simulation

Simulates system-level failure probability P_sys as a function of joint
efficiency (eta_j), segment count (N), and inspection cadence over a
10-year mission.

Joint lifetime model:
    lambda_j(T) = lambda_0 * exp(-Q / (k_B * T)) * (0.97 / eta_j)^4

System failure = any joint eta_j drops below eta_crit with no repair
before cascade propagation.

Outputs:
    data/processed/psys_surface.npz  — P_sys(N, eta_j) matrix
    paper/figures/fig_psys_heatmap.pdf
    paper/figures/fig_mttr_distribution.pdf
    paper/figures/fig_inspection_cadence.pdf

Reference:
    Wright, Patel & Liddle (2023) — joint efficiency data
    Luo et al. (2022) — segmented tether optimization
"""

from pathlib import Path
import numpy as np
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
# Joint hazard rate model
# ---------------------------------------------------------------------------
def joint_hazard_rate(eta_j: float, T_kelvin: float, params: dict) -> float:
    """
    Compute joint failure hazard rate lambda_j.

    lambda_j(T) = lambda_0 * exp(-Q / (k_B * T)) * (0.97 / eta_j)^4

    Parameters
    ----------
    eta_j : float
        Joint efficiency (0 < eta_j <= 1).
    T_kelvin : float
        Local temperature at joint position [K].
    params : dict
        Must contain joints.lambda_0, joints.Q_activation, physical.k_B.

    Returns
    -------
    float
        Hazard rate [1/h].
    """
    lambda_0 = params["joints"]["lambda_0"]
    Q = params["joints"]["Q_activation"]
    k_B = params["physical"]["k_B"]

    return lambda_0 * np.exp(-Q / (k_B * T_kelvin)) * (0.97 / eta_j) ** 4


# ---------------------------------------------------------------------------
# Thermal profile along tether (placeholder)
# ---------------------------------------------------------------------------
def thermal_profile(y: np.ndarray) -> np.ndarray:
    """
    Temperature profile T(y) along tether [K].

    TODO: Replace with proper thermal environment model from
    simulations/thermal/ once built. For now, uses a simplified
    profile based on altitude.

    Parameters
    ----------
    y : ndarray
        Radial positions from Earth center [m].

    Returns
    -------
    ndarray
        Temperature at each position [K].
    """
    # Placeholder: ~290 K near surface, dropping to ~200 K in shadow,
    # rising to ~300 K in sunlit GEO region
    R_earth = 6.3781e6
    altitude = y - R_earth
    h_GEO = 3.5786e7

    T = np.where(
        altitude < h_GEO * 0.3,
        290 - 90 * (altitude / (h_GEO * 0.3)),  # cool down through atmosphere
        200 + 100 * ((altitude - h_GEO * 0.3) / (h_GEO * 0.7)),  # warm in sunlight
    )
    return np.clip(T, 180, 350)


# ---------------------------------------------------------------------------
# Single trajectory simulation
# ---------------------------------------------------------------------------
def simulate_trajectory(N: int, eta_j: float, inspection_cadence: int,
                        params: dict, rng: np.random.Generator) -> dict:
    """
    Simulate one 10-year trajectory of a tether with N joints.

    Parameters
    ----------
    N : int
        Number of joints (= N_segments - 1).
    eta_j : float
        Joint efficiency for hazard rate calculation.
    inspection_cadence : int
        Inspection every `inspection_cadence` climber passages.
    params : dict
        Master parameter dictionary.
    rng : numpy.random.Generator
        Random number generator for reproducibility.

    Returns
    -------
    dict with keys:
        survived : bool — True if system survived full mission
        failure_time : float or None — time of system failure [h]
        repairs : int — number of repairs performed
        mttr : list[float] — repair times for each repair event [h]
    """
    t_mission = params["monte_carlo"]["t_mission"]
    p_detection = params["monte_carlo"]["p_detection"]
    t_replace = params["monte_carlo"]["t_joint_replace"]

    # TODO: Implement full trajectory simulation
    # 1. Generate time-to-failure for each joint from exponential(1/lambda_j)
    # 2. Step through time: at each inspection, detect degraded joints
    #    with probability p_detection
    # 3. If detected, repair (add t_replace to clock)
    # 4. If undetected and eta drops below eta_crit, system fails
    # 5. Record survival, failure time, repairs, MTTR

    return {
        "survived": True,
        "failure_time": None,
        "repairs": 0,
        "mttr": [],
    }


# ---------------------------------------------------------------------------
# Parameter sweep
# ---------------------------------------------------------------------------
def run_sweep(params: dict) -> dict:
    """
    Run the full Monte Carlo parameter sweep over N x eta_j x inspection cadence.

    Returns
    -------
    dict with keys:
        N_values : list[int]
        eta_j_values : list[float]
        cadence_values : list[int]
        P_sys : ndarray — shape (len(N), len(eta_j), len(cadence))
                          system survival probability
        MTTR_median : ndarray — same shape, median repair time [h]
    """
    N_sweep = params["monte_carlo"]["N_sweep"]
    eta_sweep = params["monte_carlo"]["eta_j_sweep"]
    cadence_sweep = params["monte_carlo"]["inspection_cadence_sweep"]
    n_traj = params["monte_carlo"]["n_trajectories"]

    shape = (len(N_sweep), len(eta_sweep), len(cadence_sweep))
    P_sys = np.zeros(shape)
    MTTR_median = np.zeros(shape)

    rng = np.random.default_rng(seed=42)

    for i, N in enumerate(N_sweep):
        for j, eta_j in enumerate(eta_sweep):
            for k, cadence in enumerate(cadence_sweep):
                survivals = 0
                all_mttr = []

                for _ in range(n_traj):
                    result = simulate_trajectory(N, eta_j, cadence, params, rng)
                    if result["survived"]:
                        survivals += 1
                    all_mttr.extend(result["mttr"])

                P_sys[i, j, k] = survivals / n_traj
                MTTR_median[i, j, k] = (
                    np.median(all_mttr) if all_mttr else 0.0
                )

    return {
        "N_values": N_sweep,
        "eta_j_values": eta_sweep,
        "cadence_values": cadence_sweep,
        "P_sys": P_sys,
        "MTTR_median": MTTR_median,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_psys_heatmap(sweep_results: dict, cadence_idx: int = 0,
                      output_path: Path = None):
    """
    Plot P_sys(N, eta_j) heatmap — THE central figure of the paper.

    Parameters
    ----------
    sweep_results : dict
        Output from run_sweep().
    cadence_idx : int
        Index into cadence_values for which to plot.
    output_path : Path, optional
        Save location.
    """
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    P = sweep_results["P_sys"][:, :, cadence_idx]
    N_vals = sweep_results["N_values"]
    eta_vals = sweep_results["eta_j_values"]

    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(
        P.T, origin="lower", aspect="auto",
        extent=[N_vals[0] - 0.5, N_vals[-1] + 0.5,
                eta_vals[0] - 0.005, eta_vals[-1] + 0.005],
        cmap="RdYlGn", vmin=0.9, vmax=1.0,
    )
    cbar = fig.colorbar(im, ax=ax, label="$P_{\\mathrm{sys}}$ (10-year survival)")
    ax.set_xlabel("Number of segments $N$")
    ax.set_ylabel("Joint efficiency $\\eta_j$")
    ax.set_title("System survival probability")

    # TODO: Add contour lines at 0.99, 0.999
    # TODO: Annotate baseline point (N=18, eta_j=0.95)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)


def plot_mttr_distribution(sweep_results: dict, output_path: Path = None):
    """Plot MTTR distribution with 72h target line."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    # TODO: Collect MTTR samples from detailed trajectory runs
    # Placeholder
    fig, ax = plt.subplots()
    ax.set_xlabel("Mean time to repair [h]")
    ax.set_ylabel("Frequency")
    ax.set_title("MTTR distribution")
    ax.axvline(72, color="red", linestyle="--", label="72 h target")
    ax.legend()

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
    plt.close(fig)


def plot_inspection_cadence(sweep_results: dict, output_path: Path = None):
    """Plot system availability vs. inspection cadence."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    # TODO: Extract availability curves from sweep results
    fig, ax = plt.subplots()
    ax.set_xlabel("Inspection cadence [climber passages]")
    ax.set_ylabel("System availability")
    ax.set_title("Availability vs. inspection frequency")

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

    print("Running Monte Carlo joint reliability sweep...")
    print(f"  N sweep:       {params['monte_carlo']['N_sweep']}")
    print(f"  eta_j sweep:   {params['monte_carlo']['eta_j_sweep']}")
    print(f"  Cadence sweep: {params['monte_carlo']['inspection_cadence_sweep']}")
    print(f"  Trajectories:  {params['monte_carlo']['n_trajectories']}")

    # Run sweep
    results = run_sweep(params)

    # Save data
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    np.savez(
        OUTPUT_DIR / "psys_surface.npz",
        N_values=results["N_values"],
        eta_j_values=results["eta_j_values"],
        cadence_values=results["cadence_values"],
        P_sys=results["P_sys"],
        MTTR_median=results["MTTR_median"],
    )

    # Plots
    plot_psys_heatmap(results, output_path=FIGURES_DIR / "fig_psys_heatmap.pdf")
    plot_mttr_distribution(results, output_path=FIGURES_DIR / "fig_mttr_distribution.pdf")
    plot_inspection_cadence(results, output_path=FIGURES_DIR / "fig_inspection_cadence.pdf")

    # Summary
    baseline_N_idx = results["N_values"].index(18)
    baseline_eta_idx = results["eta_j_values"].index(0.95)
    P_baseline = results["P_sys"][baseline_N_idx, baseline_eta_idx, 0]
    print(f"\nBaseline P_sys (N=18, eta_j=0.95): {P_baseline:.4f}")
    print("Done. Outputs saved to data/processed/ and paper/figures/.")


if __name__ == "__main__":
    main()
