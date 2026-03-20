"""
modal_analysis.py — Modal analysis of segmented tether with joint-compliance comparison

Primary result: analytical fundamental period from the continuous gravity-gradient
string model.  The discrete lumped-mass-spring model (N = 500) is run twice —
once with perfect joints (eta_j = 1.0) and once with reduced joint stiffness —
to quantify how segmentation and joint compliance shift the natural frequencies.

Also computes quasi-static forced response to a 20 t climber traversal.

Usage:
    python simulations/fea/modal_analysis.py

Outputs:
    data/processed/modal_results.npz
    paper/figures/fig_modal_comparison.pdf
"""

from pathlib import Path
import numpy as np
from scipy import sparse, integrate
from scipy.sparse.linalg import eigsh, spsolve
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
# Analytical solution (PRIMARY)
# ---------------------------------------------------------------------------
def analytical_frequencies(params: dict, n_modes: int = 10) -> dict:
    """
    Compute natural frequencies for the continuous gravity-gradient string.

    For a fixed-free uniform string under constant stress sigma_design:
        c = sqrt(sigma_design / rho)
        T_1 = 4L / c
        f_n = (2n - 1) / (4L) * c    for n = 1, 2, 3, ...

    Returns
    -------
    dict with c, T1_h, freq_hz (array of n_modes frequencies)
    """
    L = float(params["tether"]["L_total"])
    rho = float(params["material"]["rho"])
    sigma_design = float(params["design"]["sigma_allow"])

    c = np.sqrt(sigma_design / rho)  # wave speed [m/s]
    T1 = 4.0 * L / c                # fundamental period [s]

    n = np.arange(1, n_modes + 1)
    freq_hz = (2 * n - 1) * c / (4.0 * L)

    return {
        "c": c,
        "T1_s": T1,
        "T1_h": T1 / 3600.0,
        "freq_hz": freq_hz,
    }


# ---------------------------------------------------------------------------
# Segment geometry from taper profile (N = 500)
# ---------------------------------------------------------------------------
def compute_segment_properties(params: dict, N: int = 500):
    """
    Compute segment lengths, areas, and masses for an N-segment tether.

    A_base = m_climber * g_surface / sigma_design  (payload requirement).

    Parameters
    ----------
    params : dict
    N : int
        Number of segments (default 500).

    Returns
    -------
    dict with N, L_j, A_j, m_j, A_base, joint_positions, midpoints
    """
    L_total = float(params["tether"]["L_total"])
    rho = float(params["material"]["rho"])
    sigma_design = float(params["design"]["sigma_allow"])
    GM = float(params["physical"]["GM_earth"])
    omega = float(params["physical"]["omega_earth"])
    R = float(params["physical"]["R_earth"])
    m_climber = float(params["climber"]["m_climber"])

    # A_base from payload requirement
    g_surface = GM / R**2
    A_base = m_climber * g_surface / sigma_design

    # Continuous taper profile
    n_pts = 10_001
    r = np.linspace(R, R + L_total, n_pts)
    a_net = omega**2 * r - GM / r**2
    integrand = -(rho / sigma_design) * a_net
    lnA = integrate.cumulative_trapezoid(integrand, r, initial=0.0)
    A_ratio = np.exp(lnA)

    # Equal-length segments
    L_j = np.full(N, L_total / N)

    # Area at midpoint of each segment
    midpoints = np.array([(i + 0.5) * L_total / N for i in range(N)])
    A_j = A_base * np.interp(R + midpoints, r, A_ratio)

    # Segment masses
    m_j = rho * A_j * L_j

    # Joint positions (N-1 internal joints)
    joint_positions = np.array([(i + 1) * L_total / N for i in range(N - 1)])

    return {
        "N": N,
        "L_j": L_j,
        "A_j": A_j,
        "m_j": m_j,
        "A_base": A_base,
        "joint_positions": joint_positions,
        "midpoints": midpoints,
    }


# ---------------------------------------------------------------------------
# Assemble stiffness and mass matrices
# ---------------------------------------------------------------------------
def assemble_matrices(seg: dict, params: dict, eta_j_override: float = None):
    """
    Assemble K and M for the lumped-mass-spring chain.

    k_j = k_material_j + k_geo_j
        k_material_j = eta_j * E * A_j / L_j
        k_geo_j      = sigma_design * A_j / L_j   (tension / length)

    Parameters
    ----------
    seg : dict
        Output from compute_segment_properties().
    params : dict
        Master parameters.
    eta_j_override : float or None
        If given, use this joint efficiency instead of the one in params.

    Returns
    -------
    K, M (sparse), M_diag, k_total, k_material, k_geo
    """
    N = seg["N"]
    L_j = seg["L_j"]
    A_j = seg["A_j"]
    m_j = seg["m_j"]

    E = float(params["material"]["E_yarn"])
    eta_j = eta_j_override if eta_j_override is not None else float(params["design"]["eta_j_baseline"])
    sigma_design = float(params["design"]["sigma_allow"])
    m_counterweight = float(params["climber"]["m_counterweight"])

    # Material stiffness
    k_material = eta_j * E * A_j / L_j

    # Geometric stiffness: k_geo = sigma_design * A_j / L_j
    k_geo = sigma_design * A_j / L_j

    # Total spring stiffness
    k = k_material + k_geo

    # Lumped masses at nodes 0..N
    node_masses = np.zeros(N + 1)
    for i in range(N):
        node_masses[i] += 0.5 * m_j[i]
        node_masses[i + 1] += 0.5 * m_j[i]

    # Counterweight at tip
    node_masses[N] += m_counterweight

    # Remove node 0 (fixed base) -> N DOFs
    n_dof = N
    M_diag = node_masses[1:]

    # Build tridiagonal K
    diag_main = np.zeros(n_dof)
    diag_off = np.zeros(n_dof - 1)

    for d in range(n_dof):
        spring_left = d
        diag_main[d] += k[spring_left]
        if d + 1 < N:
            spring_right = d + 1
            diag_main[d] += k[spring_right]
            diag_off[d] = -k[spring_right]

    K = sparse.diags([diag_off, diag_main, diag_off],
                      offsets=[-1, 0, 1], shape=(n_dof, n_dof),
                      format="csc")
    M = sparse.diags([M_diag], offsets=[0], shape=(n_dof, n_dof),
                      format="csc")

    return K, M, M_diag, k, k_material, k_geo


# ---------------------------------------------------------------------------
# Eigenvalue solve
# ---------------------------------------------------------------------------
def solve_modes(K, M, n_modes: int = 10):
    """
    Solve K * phi = omega^2 * M * phi for the lowest n_modes modes.
    """
    n_dof = K.shape[0]
    n_modes = min(n_modes, n_dof - 2)

    eigenvalues, eigenvectors = eigsh(K, k=n_modes, M=M, which="LM",
                                       sigma=1e-6, mode="normal",
                                       maxiter=10000)

    omega_sq = np.real(eigenvalues)
    omega_sq = np.maximum(omega_sq, 0)
    omega = np.sqrt(omega_sq)

    idx = np.argsort(omega)
    omega = omega[idx]
    eigenvectors = eigenvectors[:, idx]

    freq_hz = omega / (2 * np.pi)
    period = np.where(freq_hz > 0, 1.0 / freq_hz, np.inf)

    return {
        "omega": omega,
        "freq_hz": freq_hz,
        "period_s": period,
        "period_h": period / 3600.0,
        "modes": eigenvectors,
    }


# ---------------------------------------------------------------------------
# Forced response: climber traversal
# ---------------------------------------------------------------------------
def forced_response_climber(seg: dict, K, params: dict):
    """
    Quasi-static displacement response to a 20 t climber traversal.

    K includes BOTH material AND geometric stiffness.
    """
    N = seg["N"]
    L_total = float(params["tether"]["L_total"])
    m_climber = float(params["climber"]["m_climber"])
    GM = float(params["physical"]["GM_earth"])
    omega = float(params["physical"]["omega_earth"])
    R = float(params["physical"]["R_earth"])

    # Sample every 5th midpoint to keep computation tractable for N=500
    all_midpoints = seg["midpoints"]
    step = max(1, N // 100)
    sample_idx = np.arange(0, N, step)
    climber_alts = all_midpoints[sample_idx]
    n_positions = len(climber_alts)

    max_displacements = np.zeros(n_positions)

    for p, alt in enumerate(climber_alts):
        node_alts = np.array([(d + 1) * L_total / N for d in range(N)])
        closest_dof = int(np.argmin(np.abs(node_alts - alt)))

        # Net gravity-gradient force on climber at that altitude
        r_climber = R + alt
        F_climber = m_climber * (omega**2 * r_climber - GM / r_climber**2)

        F = np.zeros(N)
        F[closest_dof] = F_climber

        # Solve K * u = F  (K has material + geometric stiffness)
        u = spsolve(K, F)
        max_displacements[p] = np.max(np.abs(u))

    return {
        "climber_positions": climber_alts,
        "max_displacement": max_displacements,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_results(analytical: dict, perfect: dict, joints: dict,
                 forced: dict, n_show: int = 10, output_path: Path = None):
    """
    Two panels:
      Left:  frequency spectrum — analytical (dashed), perfect joints (circles),
             reduced joints (crosses).
      Right: forced response displacement vs climber altitude.
    """
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    n_modes = min(n_show, len(analytical["freq_hz"]),
                  len(perfect["freq_hz"]), len(joints["freq_hz"]))
    mode_numbers = np.arange(1, n_modes + 1)

    fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.5))

    # --- Left panel: frequency spectrum ---
    ax = axes[0]
    ax.plot(mode_numbers, analytical["freq_hz"][:n_modes] * 1e6, "--",
            color="gray", linewidth=1.2, label="Analytical (continuous)")
    ax.plot(mode_numbers, perfect["freq_hz"][:n_modes] * 1e6, "o",
            color="#0072B2", markersize=5, fillstyle="none",
            label=r"Discrete, $\eta_j=1.0$")
    ax.plot(mode_numbers, joints["freq_hz"][:n_modes] * 1e6, "x",
            color="#D55E00", markersize=5,
            label=r"Discrete, $\eta_j=0.95$")

    ax.set_xlabel("Mode number")
    ax.set_ylabel(r"Frequency [$\mu$Hz]")
    ax.set_title("Natural frequency spectrum")
    ax.legend(fontsize=7)

    # Annotate fundamental period
    T1_a = analytical["T1_h"]
    ax.annotate(f"$T_1$ = {T1_a:.1f} h (analytical)",
                xy=(1, analytical["freq_hz"][0] * 1e6),
                xytext=(3, analytical["freq_hz"][0] * 1e6 * 1.8),
                fontsize=7, arrowprops=dict(arrowstyle="->", color="gray"))

    # --- Right panel: forced response ---
    ax = axes[1]
    alt_km = forced["climber_positions"] / 1e3
    ax.plot(alt_km, forced["max_displacement"], "-", color="#009E73",
            linewidth=1.0)
    ax.set_xlabel("Climber altitude [km]")
    ax.set_ylabel("Max node displacement [m]")
    ax.set_title("Quasi-static response to 20 t climber")

    # Mark GEO
    ax.axvline(35786, color="gray", linewidth=0.5, linestyle=":", alpha=0.5)
    ax.annotate("GEO", xy=(35786, ax.get_ylim()[1] * 0.9), fontsize=7,
                color="gray")

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
    params = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    N_NODES = 500
    N_MODES = 10
    eta_j_baseline = float(params["design"]["eta_j_baseline"])

    # ===================================================================
    # PRIMARY RESULT: Analytical continuous gravity-gradient string model
    # ===================================================================
    analytical = analytical_frequencies(params, n_modes=N_MODES)

    print("=" * 65)
    print("PRIMARY RESULT: Continuous gravity-gradient string model")
    print("=" * 65)
    print(f"  sigma_design    = {float(params['design']['sigma_allow'])/1e9:.1f} GPa")
    print(f"  rho             = {float(params['material']['rho']):.0f} kg/m^3")
    print(f"  L_total         = {float(params['tether']['L_total'])/1e6:.0f} Mm")
    print(f"  Wave speed c    = {analytical['c']:.1f} m/s")
    print(f"  T_1 = 4L/c     = {analytical['T1_h']:.1f} h")
    print()
    print(f"  {'Mode':>5} {'Freq [uHz]':>12} {'Period [h]':>12}")
    print("  " + "-" * 32)
    for i in range(N_MODES):
        f = analytical["freq_hz"][i]
        T = 1.0 / f / 3600.0 if f > 0 else float("inf")
        print(f"  {i+1:>5} {f*1e6:>12.4f} {T:>12.2f}")

    # ===================================================================
    # Discrete model setup (N = 500)
    # ===================================================================
    print()
    print("=" * 65)
    print(f"DISCRETE MODEL: N = {N_NODES} segments")
    print("=" * 65)

    seg = compute_segment_properties(params, N=N_NODES)
    print(f"  A_base            = {seg['A_base']*1e6:.2f} mm^2")
    print(f"  Segment length    = {seg['L_j'][0]/1e3:.0f} km (equal-length)")
    print(f"  Segment mass range= {np.min(seg['m_j'])/1e3:.1f} -- {np.max(seg['m_j'])/1e3:.1f} t")

    # --- Stiffness breakdown ---
    E = float(params["material"]["E_yarn"])
    sigma_design = float(params["design"]["sigma_allow"])

    k_mat_ex = eta_j_baseline * E * seg["A_j"][0] / seg["L_j"][0]
    k_geo_ex = sigma_design * seg["A_j"][0] / seg["L_j"][0]
    print()
    print(f"  Stiffness comparison (segment 0):")
    print(f"    k_material = eta_j * E * A / L   = {k_mat_ex:.4e} N/m")
    print(f"    k_geo      = sigma * A / L        = {k_geo_ex:.4e} N/m")
    print(f"    ratio k_geo / k_material          = {k_geo_ex / k_mat_ex:.1f}x")

    # ===================================================================
    # Joint compliance comparison
    # ===================================================================
    print()
    print("=" * 65)
    print("JOINT COMPLIANCE COMPARISON")
    print("=" * 65)

    # Case 1: Perfect joints (eta_j = 1.0)
    print(f"\n  Case 1: Perfect joints (eta_j = 1.0)")
    K_perf, M_perf, M_diag_perf, k_perf, _, _ = assemble_matrices(seg, params, eta_j_override=1.0)
    print(f"    Solving {N_MODES} lowest modes...")
    modes_perfect = solve_modes(K_perf, M_perf, n_modes=N_MODES)
    for i in range(N_MODES):
        print(f"    Mode {i+1:>2}: {modes_perfect['freq_hz'][i]*1e6:>10.4f} uHz "
              f"({modes_perfect['period_h'][i]:>8.2f} h)")

    # Case 2: Reduced joints (eta_j = baseline from params)
    print(f"\n  Case 2: Reduced joints (eta_j = {eta_j_baseline})")
    K_jnt, M_jnt, M_diag_jnt, k_jnt, _, _ = assemble_matrices(seg, params, eta_j_override=eta_j_baseline)
    print(f"    Solving {N_MODES} lowest modes...")
    modes_joints = solve_modes(K_jnt, M_jnt, n_modes=N_MODES)
    for i in range(N_MODES):
        print(f"    Mode {i+1:>2}: {modes_joints['freq_hz'][i]*1e6:>10.4f} uHz "
              f"({modes_joints['period_h'][i]:>8.2f} h)")

    # Frequency shift
    print(f"\n  Frequency shift (joint compliance effect):")
    print(f"  {'Mode':>5} {'f_perfect [uHz]':>16} {'f_joints [uHz]':>16} {'Shift [%]':>10}")
    print("  " + "-" * 48)
    for i in range(N_MODES):
        f_p = modes_perfect["freq_hz"][i]
        f_j = modes_joints["freq_hz"][i]
        shift = abs(f_p - f_j) / f_p * 100.0 if f_p > 0 else 0.0
        print(f"  {i+1:>5} {f_p*1e6:>16.4f} {f_j*1e6:>16.4f} {shift:>10.4f}")

    shift_mode1 = abs(modes_perfect["freq_hz"][0] - modes_joints["freq_hz"][0]) / modes_perfect["freq_hz"][0] * 100.0
    print()
    print(f"  >>> Joint compliance frequency shift: {shift_mode1:.4f}% (mode 1)")

    # ===================================================================
    # Forced response (using joint-reduced K, which has k_material + k_geo)
    # ===================================================================
    print()
    print("=" * 65)
    print("FORCED RESPONSE: 20 t climber traversal")
    print("=" * 65)
    forced = forced_response_climber(seg, K_jnt, params)
    print(f"  Max node displacement: {np.max(forced['max_displacement']):.4f} m")

    # Climber separation check
    T1 = analytical["T1_h"]
    sep_min = float(params["climber"]["separation_min"])
    v_climber = float(params["climber"]["v_climber"])
    t_sep = sep_min / v_climber / 3600.0
    print(f"  Fundamental period T_1 = {T1:.1f} h")
    print(f"  Climber separation transit time = {t_sep:.0f} h")
    if T1 < t_sep:
        print(f"  CHECK: T_1 < t_sep -> oscillations decay between climbers")
    else:
        print(f"  WARNING: T_1 >= t_sep -> resonance risk between successive climbers")

    # ===================================================================
    # Simplification note
    # ===================================================================
    print()
    print("Note: This model omits Coriolis coupling, non-uniform tension")
    print("distribution along mode shapes, and lateral dynamics. It provides")
    print("a first-order estimate suitable for validating that segmentation")
    print("does not destabilise the tether.")

    # ===================================================================
    # Save results
    # ===================================================================
    np.savez(
        OUTPUT_DIR / "modal_results.npz",
        analytical_freq_hz=analytical["freq_hz"],
        analytical_T1_h=analytical["T1_h"],
        analytical_c=analytical["c"],
        perfect_freq_hz=modes_perfect["freq_hz"],
        perfect_period_h=modes_perfect["period_h"],
        joints_freq_hz=modes_joints["freq_hz"],
        joints_period_h=modes_joints["period_h"],
        climber_positions=forced["climber_positions"],
        max_displacement=forced["max_displacement"],
    )
    print(f"\n  Saved: {OUTPUT_DIR / 'modal_results.npz'}")

    # ===================================================================
    # Plot
    # ===================================================================
    plot_results(analytical, modes_perfect, modes_joints, forced,
                 n_show=N_MODES,
                 output_path=FIGURES_DIR / "fig_modal_comparison.pdf")

    print("\nDone.")


if __name__ == "__main__":
    main()
