"""
single_climber.py — Part D: single-climber transit simulation.

Assembles the full 2D model, calibrates Rayleigh damping, integrates
a 20 t climber traversal from surface to counterweight, then post-processes
displacement envelopes, tension perturbations, and GEO time histories.
"""

import numpy as np

from simulations.fea.phase2_dynamics.config import (
    get_constants, DT, T_FREE, OUTPUT_STRIDE, ZETA_TARGET, N_NODES,
)
from simulations.fea.phase2_dynamics.mesh import generate_mesh
from simulations.fea.phase2_dynamics.assembly import (
    assemble_global, apply_bc, check_K_positive_definite,
)
from simulations.fea.phase2_dynamics.damping import (
    compute_rayleigh_coefficients, assemble_damping,
)
from simulations.fea.phase2_dynamics.modal_analysis import solve_standard
from simulations.fea.phase2_dynamics.climber_force import climber_force_at_t
from simulations.fea.phase2_dynamics.time_integration import newmark_beta


def run_single_transit(params: dict, N: int = N_NODES,
                       eta_j: float = None, dt: float = DT,
                       zeta: float = ZETA_TARGET,
                       method: str = "newmark") -> dict:
    """
    Execute single climber transit simulation (Part D).

    Parameters
    ----------
    params : dict
        Master parameters.
    N : int
        Number of mesh nodes.
    eta_j : float or None
        Joint efficiency. None uses baseline from params.
    dt : float
        Time step [s].
    zeta : float
        Damping ratio for Rayleigh damping.
    method : str
        'newmark' or 'bdf'.

    Returns
    -------
    dict with simulation results and post-processed envelopes.
    """
    c = get_constants(params)
    if eta_j is None:
        eta_j = c["eta_j"]

    # 1. Build mesh and assemble matrices
    print("  Building mesh and assembling matrices...", flush=True)
    mesh = generate_mesh(params, N=N, eta_j=eta_j)
    mats = assemble_global(mesh, params, include_coriolis=True)
    free = apply_bc(mats)

    # Validation gate: check K is positive definite
    min_eig = check_K_positive_definite(free["K"])
    print(f"  K_total min eigenvalue: {min_eig:.6e}", flush=True)
    if min_eig < 0:
        raise ValueError(
            f"K_total is not positive definite (min eigenvalue = {min_eig:.6e}). "
            "Check gravity-gradient stiffness assembly."
        )

    # 2. Modal solve (undamped, no Coriolis) for damping calibration
    print("  Modal solve for damping calibration...", flush=True)
    # Use the no-Coriolis K for damping calibration (standard approach)
    K_no_gg_coriolis = free["K"]  # already assembled with gravity-gradient
    modal_undamped = solve_standard(K_no_gg_coriolis, free["M"], n_modes=2)
    omega_1 = modal_undamped["omega"][0]
    omega_2 = modal_undamped["omega"][1]
    print(f"  omega_1 = {omega_1:.6e} rad/s (T1 = {modal_undamped['period_h'][0]:.2f} h)")
    print(f"  omega_2 = {omega_2:.6e} rad/s (T2 = {modal_undamped['period_h'][1]:.2f} h)")

    # 3. Assemble Rayleigh damping
    alpha_M, alpha_K = compute_rayleigh_coefficients(omega_1, omega_2, zeta=zeta)
    C_damp = assemble_damping(free["M"], free["K"], alpha_M, alpha_K)
    C_total = (C_damp + free["G"]).tocsc()

    # 4. Build force function
    r_nodes = mesh["r_nodes"]
    n_free = free["n_free_dof"]

    def force_func(t):
        return climber_force_at_t(t, r_nodes, params, n_free)

    # 5. Time integration
    t_transit = c["L_total"] / c["v_climber"]
    t_total = t_transit + T_FREE
    print(f"  Transit time: {t_transit/3600:.1f} h, total: {t_total/3600:.1f} h", flush=True)
    print(f"  Integrating ({method})...", flush=True)

    if method == "newmark":
        result = newmark_beta(free["M"], C_total, free["K"], force_func,
                              t_start=0.0, t_end=t_total, dt=dt,
                              output_stride=OUTPUT_STRIDE)
    else:
        from simulations.fea.phase2_dynamics.time_integration import solve_bdf
        result = solve_bdf(free["M"], C_total, free["K"], force_func,
                           t_start=0.0, t_end=t_total,
                           max_step=dt, output_stride=OUTPUT_STRIDE)

    # 6. Post-process
    print("  Post-processing...", flush=True)
    pp = _postprocess(result, mesh, free, params)

    return {
        "time": result["t"],
        "x_history": result["x"],
        "v_history": result["v"],
        "mesh": mesh,
        "modal_undamped": modal_undamped,
        **pp,
    }


def _postprocess(result: dict, mesh: dict, free: dict, params: dict) -> dict:
    """Compute envelopes, tension perturbations, and GEO time histories."""
    c = get_constants(params)
    t = result["t"]
    x = result["x"]  # (n_free_dof, n_out)
    n_free = free["n_free_dof"]
    N = mesh["N"]

    # Extract u and v components from interleaved DOFs
    # Free DOFs: [u_1, v_1, u_2, v_2, ..., u_{N-1}, v_{N-1}]
    # Node 0 is fixed (u_0 = v_0 = 0)
    n_free_nodes = N - 1

    # u displacements at free nodes (indices 0, 2, 4, ...)
    u_nodes = x[0::2, :]  # (n_free_nodes, n_out)
    v_nodes = x[1::2, :]  # (n_free_nodes, n_out)

    # Add fixed node 0 back for full-tether profiles
    u_full = np.vstack([np.zeros((1, x.shape[1])), u_nodes])  # (N, n_out)
    v_full = np.vstack([np.zeros((1, x.shape[1])), v_nodes])  # (N, n_out)

    # Displacement envelopes: max |u|, max |v| over time at each node
    u_envelope = np.max(np.abs(u_full), axis=1)  # (N,)
    v_envelope = np.max(np.abs(v_full), axis=1)  # (N,)

    # Tension perturbation: delta_T_e = EA_e * (u_{i+1} - u_i) / L_e
    N_elem = mesh["N_elem"]
    n_out = x.shape[1]
    dT = np.zeros((N_elem, n_out))
    for e in range(N_elem):
        du = u_full[e + 1, :] - u_full[e, :]
        dT[e, :] = mesh["EA_e"][e] * du / mesh["L_e"][e]

    # Tension perturbation ratio
    T_eq = mesh["T_e"]  # (N_elem,) equilibrium tension
    dT_ratio = np.abs(dT) / T_eq[:, np.newaxis]  # (N_elem, n_out)
    dT_ratio_envelope = np.max(dT_ratio, axis=1)  # (N_elem,)

    # GEO node: closest to r_GEO
    r_nodes = mesh["r_nodes"]
    i_geo = int(np.argmin(np.abs(r_nodes - c["r_GEO"])))
    if i_geo == 0:
        u_geo = np.zeros(n_out)
        v_geo = np.zeros(n_out)
    else:
        u_geo = u_full[i_geo, :]
        v_geo = v_full[i_geo, :]

    return {
        "u_full": u_full,
        "v_full": v_full,
        "u_envelope": u_envelope,
        "v_envelope": v_envelope,
        "dT": dT,
        "dT_ratio_envelope": dT_ratio_envelope,
        "T_eq": T_eq,
        "u_geo": u_geo,
        "v_geo": v_geo,
        "i_geo": i_geo,
        "alt_nodes": mesh["alt_nodes"],
        "alt_elem_mid": mesh["r_mid"] - c["R_earth"],
        "peak_u_km": float(np.max(u_envelope)) / 1e3,
        "peak_v_km": float(np.max(v_envelope)) / 1e3,
        "peak_dT_ratio": float(np.max(dT_ratio_envelope)),
    }
