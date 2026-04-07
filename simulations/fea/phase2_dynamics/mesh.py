"""
mesh.py — Non-uniform 2D mesh generation for the space-elevator tether.

Generates N node positions with Gaussian refinement near GEO (where the taper
is steepest), then computes per-element properties (area, tension, mass,
gravity-gradient coefficients) by interpolating the continuous taper profile.
"""

import numpy as np
from simulations.fea.phase2_dynamics.config import ROOT, get_constants
from simulations.fea.taper_profile import integrate_taper_profile, net_acceleration


def generate_node_positions(params: dict, N: int = 500,
                            refine_geo: bool = True) -> np.ndarray:
    """
    Return N radial positions from R_earth to R_earth + L_total.

    Parameters
    ----------
    params : dict
        Master parameter dictionary.
    N : int
        Number of nodes.
    refine_geo : bool
        If True, use Gaussian density weighting to place more nodes near GEO.
        If False, use uniform spacing.

    Returns
    -------
    r_nodes : ndarray, shape (N,)
        Geocentric radial positions [m].
    """
    c = get_constants(params)
    r_min = c["R_earth"]
    r_max = c["R_earth"] + c["L_total"]

    if not refine_geo:
        return np.linspace(r_min, r_max, N)

    # Density function: higher weight near GEO
    r_GEO = c["r_GEO"]
    sigma_GEO = 5.0e6  # width of refinement region [m]
    alpha = 3.0         # refinement factor

    # Build CDF of the density on a fine auxiliary grid, then invert
    n_aux = 100_001
    r_aux = np.linspace(r_min, r_max, n_aux)
    w = 1.0 + alpha * np.exp(-((r_aux - r_GEO) / sigma_GEO) ** 2)
    cdf = np.cumsum(w)
    cdf = (cdf - cdf[0]) / (cdf[-1] - cdf[0])  # normalize to [0, 1]

    # Invert: uniform samples in CDF space -> non-uniform in r
    cdf_target = np.linspace(0.0, 1.0, N)
    r_nodes = np.interp(cdf_target, cdf, r_aux)

    # Force exact endpoints
    r_nodes[0] = r_min
    r_nodes[-1] = r_max
    return r_nodes


def identify_joint_elements(r_nodes: np.ndarray, params: dict) -> np.ndarray:
    """
    Return boolean mask of length N-1 indicating which elements contain a
    modular joint (segment boundary).

    Joint positions are at equal-mass segment boundaries from the baseline
    segmentation (N_baseline segments from parameters.yaml).
    """
    c = get_constants(params)
    N_seg = int(params["segments"]["N_baseline"])

    # Simple equal-length segmentation for joint identification
    # (the real segmentation uses mass-equalization, but for joint compliance
    # purposes we approximate with equal-length since the existing 1D model does)
    L_total = c["L_total"]
    joint_alts = np.array([(i + 1) * L_total / N_seg for i in range(N_seg - 1)])
    joint_radii = c["R_earth"] + joint_alts

    # For each element, check if any joint falls within it
    N = len(r_nodes)
    is_joint = np.zeros(N - 1, dtype=bool)
    for e in range(N - 1):
        r_left, r_right = r_nodes[e], r_nodes[e + 1]
        if np.any((joint_radii >= r_left) & (joint_radii < r_right)):
            is_joint[e] = True
    return is_joint


def compute_element_properties(r_nodes: np.ndarray, params: dict,
                               eta_j: float = 1.0) -> dict:
    """
    Compute per-element and per-node physical properties.

    Parameters
    ----------
    r_nodes : ndarray, shape (N,)
        Node radial positions [m].
    params : dict
        Master parameters.
    eta_j : float
        Joint efficiency factor. Elements spanning joints have EA reduced
        by this factor.

    Returns
    -------
    dict with:
        r_nodes     : (N,) node positions
        N           : number of nodes
        N_elem      : number of elements (N-1)
        L_e         : (N-1,) element lengths [m]
        r_mid       : (N-1,) element midpoint radii [m]
        A_e         : (N-1,) cross-sectional area at midpoint [m^2]
        T_e         : (N-1,) equilibrium tension at midpoint [N]
        m_e         : (N-1,) element mass [kg]
        EA_e        : (N-1,) axial stiffness [N] (reduced at joints)
        is_joint    : (N-1,) bool mask for joint elements
        A_base      : float, base cross-sectional area [m^2]
        k_long      : (N,) longitudinal gravity-gradient coeff at nodes [N/m^3]
        k_trans     : (N,) transverse gravity-gradient coeff at nodes [N/m^3]
        alt_nodes   : (N,) altitude above surface [m]
    """
    c = get_constants(params)
    N = len(r_nodes)
    N_elem = N - 1

    # Continuous taper profile for interpolation
    taper = integrate_taper_profile(params, sigma_design=c["sigma_design"])
    r_taper = taper["r"]
    A_ratio_taper = taper["A_ratio"]

    # Base area from payload requirement
    g_surface = c["GM"] / c["R_earth"] ** 2
    A_base = c["m_climber"] * g_surface / c["sigma_design"]

    # Element lengths and midpoints
    L_e = np.diff(r_nodes)
    r_mid = 0.5 * (r_nodes[:-1] + r_nodes[1:])

    # Cross-sectional area at element midpoints
    A_ratio_mid = np.interp(r_mid, r_taper, A_ratio_taper)
    A_e = A_base * A_ratio_mid

    # Equilibrium tension: T = sigma_design * A (uniform-stress taper)
    T_e = c["sigma_design"] * A_e

    # Element masses
    m_e = c["rho"] * A_e * L_e

    # Joint identification and axial stiffness
    is_joint = identify_joint_elements(r_nodes, params)
    EA_e = c["E"] * A_e.copy()
    EA_e[is_joint] *= eta_j  # reduce at joints

    # Gravity-gradient stiffness coefficients at each NODE
    # Longitudinal: k_long = rho * A * (omega^2 + 2*GM/r^3)  [positive = restoring]
    # Transverse:   k_trans = rho * A * (omega^2 - GM/r^3)    [changes sign at GEO]
    A_ratio_nodes = np.interp(r_nodes, r_taper, A_ratio_taper)
    A_nodes = A_base * A_ratio_nodes

    k_long = c["rho"] * A_nodes * (c["omega"] ** 2 + 2.0 * c["GM"] / r_nodes ** 3)
    k_trans = c["rho"] * A_nodes * (c["omega"] ** 2 - c["GM"] / r_nodes ** 3)

    return {
        "r_nodes": r_nodes,
        "N": N,
        "N_elem": N_elem,
        "L_e": L_e,
        "r_mid": r_mid,
        "A_e": A_e,
        "T_e": T_e,
        "m_e": m_e,
        "EA_e": EA_e,
        "is_joint": is_joint,
        "A_base": A_base,
        "k_long": k_long,
        "k_trans": k_trans,
        "alt_nodes": r_nodes - c["R_earth"],
    }


def generate_mesh(params: dict, N: int = 500, eta_j: float = 1.0,
                  refine_geo: bool = True) -> dict:
    """High-level convenience: generate nodes + element properties."""
    r_nodes = generate_node_positions(params, N=N, refine_geo=refine_geo)
    return compute_element_properties(r_nodes, params, eta_j=eta_j)
