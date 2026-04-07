"""
multi_climber.py — Part E: multi-climber resonance sweep.

Launches 4 climbers at regular intervals and sweeps the departure separation
to find resonance with the fundamental mode. Also runs damping sensitivity
at the worst-case resonant separation.
"""

import numpy as np
from multiprocessing import Pool, cpu_count
from functools import partial

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
from simulations.fea.phase2_dynamics.climber_force import multi_climber_force
from simulations.fea.phase2_dynamics.time_integration import newmark_beta


# Departure separations to sweep [hours]
SEPARATION_HOURS = [10, 12, 15, 18, 20, 22, 24, 25, 26, 28, 30, 35, 40, 50]
N_CLIMBERS = 4
ZETA_SWEEP = [0.001, 0.005, 0.01, 0.02, 0.05]


def _build_system(params, N, eta_j, zeta):
    """Build mesh, assemble matrices, calibrate damping. Shared setup."""
    c = get_constants(params)
    mesh = generate_mesh(params, N=N, eta_j=eta_j)
    mats = assemble_global(mesh, params, include_coriolis=True)
    free = apply_bc(mats)

    # Modal solve for damping calibration
    modal = solve_standard(free["K"], free["M"], n_modes=2)
    omega_1, omega_2 = modal["omega"][0], modal["omega"][1]
    alpha_M, alpha_K = compute_rayleigh_coefficients(omega_1, omega_2, zeta=zeta)
    C_damp = assemble_damping(free["M"], free["K"], alpha_M, alpha_K)
    C_total = (C_damp + free["G"]).tocsc()

    return mesh, free, C_total, modal, c


def _run_one_separation(sep_hours, params, N, eta_j, zeta, dt):
    """Worker function for a single separation value."""
    mesh, free, C_total, modal, c = _build_system(params, N, eta_j, zeta)

    r_nodes = mesh["r_nodes"]
    n_free = free["n_free_dof"]
    t_transit = c["L_total"] / c["v_climber"]
    sep_s = sep_hours * 3600.0

    # Schedule: 4 climbers departing at 0, sep, 2*sep, 3*sep
    schedule = [{"t_start": i * sep_s} for i in range(N_CLIMBERS)]

    # Total simulation time: last climber finishes + T_FREE
    t_total = (N_CLIMBERS - 1) * sep_s + t_transit + T_FREE

    def force_func(t):
        return multi_climber_force(t, r_nodes, params, n_free, schedule)

    result = newmark_beta(free["M"], C_total, free["K"], force_func,
                          t_start=0.0, t_end=t_total, dt=dt,
                          output_stride=OUTPUT_STRIDE)

    # Post-process peaks
    x = result["x"]
    N_nodes = mesh["N"]

    # Full displacement arrays (add fixed node 0 back)
    u_full = np.vstack([np.zeros((1, x.shape[1])), x[0::2, :]])
    v_full = np.vstack([np.zeros((1, x.shape[1])), x[1::2, :]])

    peak_u = float(np.max(np.abs(u_full)))
    peak_v = float(np.max(np.abs(v_full)))

    # Tension perturbation
    N_elem = mesh["N_elem"]
    max_dT_ratio = 0.0
    for e in range(N_elem):
        du = u_full[e + 1, :] - u_full[e, :]
        dT_e = np.abs(mesh["EA_e"][e] * du / mesh["L_e"][e])
        ratio_e = np.max(dT_e) / mesh["T_e"][e]
        max_dT_ratio = max(max_dT_ratio, ratio_e)

    # RMS transverse velocity at GEO
    i_geo = int(np.argmin(np.abs(r_nodes - c["r_GEO"])))
    if i_geo > 0:
        v_vel = result["v"]
        v_geo_vel = v_vel[2 * (i_geo - 1) + 1, :]  # v DOF of GEO node in free system
        rms_v_geo = float(np.sqrt(np.mean(v_geo_vel ** 2)))
    else:
        rms_v_geo = 0.0

    # GEO time histories for resonant/off-resonant comparison
    if i_geo > 0:
        u_geo = u_full[i_geo, :]
        v_geo = v_full[i_geo, :]
    else:
        u_geo = np.zeros(x.shape[1])
        v_geo = np.zeros(x.shape[1])

    return {
        "sep_hours": sep_hours,
        "peak_u": peak_u,
        "peak_v": peak_v,
        "peak_dT_ratio": max_dT_ratio,
        "rms_v_geo": rms_v_geo,
        "t": result["t"],
        "u_geo": u_geo,
        "v_geo": v_geo,
    }


def run_resonance_sweep(params: dict, N: int = N_NODES,
                        eta_j: float = None, zeta: float = ZETA_TARGET,
                        dt: float = DT,
                        separations: list = None,
                        n_workers: int = None) -> dict:
    """
    Sweep departure separations to characterize multi-climber resonance.

    Returns dict with arrays of peak values and the resonant separation.
    """
    c = get_constants(params)
    if eta_j is None:
        eta_j = c["eta_j"]
    if separations is None:
        separations = SEPARATION_HOURS
    if n_workers is None:
        n_workers = min(cpu_count(), len(separations))

    print(f"  Resonance sweep: {len(separations)} separations, "
          f"{n_workers} workers", flush=True)

    # Run sweep (serial for reproducibility and to avoid memory issues;
    # parallelization via multiprocessing can be enabled if needed)
    all_results = []
    for sep in separations:
        print(f"    sep = {sep} h ...", end=" ", flush=True)
        res = _run_one_separation(sep, params, N, eta_j, zeta, dt)
        print(f"peak_v = {res['peak_v']/1e3:.1f} km, "
              f"dT/T = {res['peak_dT_ratio']:.4f}", flush=True)
        all_results.append(res)

    # Collect into arrays
    sep_arr = np.array([r["sep_hours"] for r in all_results])
    peak_u = np.array([r["peak_u"] for r in all_results])
    peak_v = np.array([r["peak_v"] for r in all_results])
    peak_dT = np.array([r["peak_dT_ratio"] for r in all_results])
    rms_v = np.array([r["rms_v_geo"] for r in all_results])

    # Find worst-case resonant separation
    i_worst = int(np.argmax(peak_v))

    return {
        "separations": sep_arr,
        "peak_u": peak_u,
        "peak_v": peak_v,
        "peak_dT_ratio": peak_dT,
        "rms_v_geo": rms_v,
        "worst_sep_hours": float(sep_arr[i_worst]),
        "all_results": all_results,
    }


def run_damping_sensitivity(params: dict, sep_hours: float,
                            N: int = N_NODES, eta_j: float = None,
                            dt: float = DT,
                            zeta_values: list = None) -> dict:
    """
    At the resonant separation, sweep damping ratios.

    Returns dict with zeta values and corresponding peak displacements.
    """
    c = get_constants(params)
    if eta_j is None:
        eta_j = c["eta_j"]
    if zeta_values is None:
        zeta_values = ZETA_SWEEP

    print(f"  Damping sensitivity at sep = {sep_hours} h", flush=True)

    results = []
    for z in zeta_values:
        print(f"    zeta = {z} ...", end=" ", flush=True)
        res = _run_one_separation(sep_hours, params, N, eta_j, z, dt)
        print(f"peak_v = {res['peak_v']/1e3:.1f} km", flush=True)
        results.append(res)

    return {
        "zeta_values": np.array(zeta_values),
        "peak_u": np.array([r["peak_u"] for r in results]),
        "peak_v": np.array([r["peak_v"] for r in results]),
        "peak_dT_ratio": np.array([r["peak_dT_ratio"] for r in results]),
        "sep_hours": sep_hours,
    }
