"""
modal_analysis.py — Eigenvalue problems for the 2D tether model.

Two solvers:
  1. Standard (no Coriolis): K*phi = omega^2*M*phi via eigsh
  2. Gyroscopic (with Coriolis): state-space via scipy.linalg.eig

Also provides mode classification and 4-case comparison driver.
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.linalg import eig as dense_eig

from simulations.fea.phase2_dynamics.config import get_constants, N_MODES
from simulations.fea.phase2_dynamics.mesh import generate_mesh
from simulations.fea.phase2_dynamics.assembly import assemble_global, apply_bc


def solve_standard(K: sparse.spmatrix, M: sparse.spmatrix,
                   n_modes: int = 20) -> dict:
    """
    Solve the standard generalized eigenvalue problem (no Coriolis):
        K * phi = omega^2 * M * phi

    Uses shift-invert mode for the smallest eigenvalues.

    Returns
    -------
    dict with:
        omega    : (n_modes,) angular frequencies [rad/s]
        freq_hz  : (n_modes,) frequencies [Hz]
        period_s : (n_modes,) periods [s]
        period_h : (n_modes,) periods [h]
        modes    : (n_dof, n_modes) eigenvectors
    """
    n_dof = K.shape[0]
    n_modes = min(n_modes, n_dof - 2)

    eigenvalues, eigenvectors = eigsh(K, k=n_modes, M=M, which="LM",
                                       sigma=1e-10, mode="normal",
                                       maxiter=20000)

    omega_sq = np.real(eigenvalues)
    omega_sq = np.maximum(omega_sq, 0.0)
    omega = np.sqrt(omega_sq)

    idx = np.argsort(omega)
    omega = omega[idx]
    eigenvectors = eigenvectors[:, idx]

    freq_hz = omega / (2.0 * np.pi)
    period_s = np.where(freq_hz > 0, 1.0 / freq_hz, np.inf)

    return {
        "omega": omega,
        "freq_hz": freq_hz,
        "period_s": period_s,
        "period_h": period_s / 3600.0,
        "modes": eigenvectors,
    }


def solve_gyroscopic(K: sparse.spmatrix, M: sparse.spmatrix,
                     G: sparse.spmatrix, C: sparse.spmatrix = None,
                     n_modes: int = 20) -> dict:
    """
    Solve the gyroscopic eigenvalue problem in state-space form.

    Equation: M*x_ddot + (C + G)*x_dot + K*x = 0

    State vector: z = [x; x_dot]  (2*n_dof)

    First-order form: E * z_dot = A_mat * z

    where E = [[I, 0], [0, M]]  and  A_mat = [[0, I], [-K, -(C+G)]]

    Or equivalently: z_dot = S * z where S = E^{-1} * A_mat

    We form S as a dense matrix and use scipy.linalg.eig.

    Returns
    -------
    dict with:
        eigenvalues   : (n_modes,) complex eigenvalues (positive-freq set)
        omega_d       : (n_modes,) damped natural frequencies [rad/s]
        freq_hz       : (n_modes,) frequencies [Hz]
        period_h      : (n_modes,) periods [h]
        growth_rate   : (n_modes,) real parts of eigenvalues
        zeta_eff      : (n_modes,) effective damping ratios
        modes         : (n_dof, n_modes) complex eigenvectors (displacement part)
    """
    n_dof = K.shape[0]

    # Convert to dense
    K_d = K.toarray()
    M_d = M.toarray()
    G_d = G.toarray()

    if C is not None:
        CG = C.toarray() + G_d
    else:
        CG = G_d

    # Solve M_d * M_inv = I to get M_inv
    M_inv = np.linalg.inv(M_d)

    # State-space system matrix S (2n x 2n):
    # z_dot = S * z where z = [x; v]
    # [x_dot]   [    0        I   ] [x]
    # [v_dot] = [-M^{-1}K  -M^{-1}(C+G)] [v]
    S = np.zeros((2 * n_dof, 2 * n_dof))
    S[:n_dof, n_dof:] = np.eye(n_dof)
    S[n_dof:, :n_dof] = -M_inv @ K_d
    S[n_dof:, n_dof:] = -M_inv @ CG

    # Dense eigenvalue solve
    eigvals, eigvecs = dense_eig(S)

    # Extract positive-frequency eigenvalues (Im > 0) and sort by frequency
    mask = eigvals.imag > 0
    eigvals_pos = eigvals[mask]
    eigvecs_pos = eigvecs[:, mask]

    # Sort by frequency magnitude
    freq_mag = np.abs(eigvals_pos.imag)
    idx = np.argsort(freq_mag)
    eigvals_pos = eigvals_pos[idx]
    eigvecs_pos = eigvecs_pos[:, idx]

    # Take first n_modes
    n_out = min(n_modes, len(eigvals_pos))
    eigvals_out = eigvals_pos[:n_out]
    # Extract displacement part of eigenvectors (first n_dof components)
    modes_out = eigvecs_pos[:n_dof, :n_out]

    omega_d = np.abs(eigvals_out.imag)
    growth_rate = eigvals_out.real
    freq_hz = omega_d / (2.0 * np.pi)
    period_s = np.where(freq_hz > 0, 1.0 / freq_hz, np.inf)

    # Effective damping ratio: zeta = -Re(lambda) / |lambda|
    abs_lambda = np.abs(eigvals_out)
    zeta_eff = np.where(abs_lambda > 0, -growth_rate / abs_lambda, 0.0)

    return {
        "eigenvalues": eigvals_out,
        "omega_d": omega_d,
        "freq_hz": freq_hz,
        "period_s": period_s,
        "period_h": period_s / 3600.0,
        "growth_rate": growth_rate,
        "zeta_eff": zeta_eff,
        "modes": modes_out,
    }


def classify_mode(phi: np.ndarray) -> str:
    """
    Classify a mode shape as longitudinal (L), transverse (T), or coupled (C).

    phi has interleaved DOF ordering: [u_0, v_0, u_1, v_1, ...]
    """
    if np.iscomplexobj(phi):
        phi = np.abs(phi)
    u_energy = np.sum(phi[0::2] ** 2)
    v_energy = np.sum(phi[1::2] ** 2)
    total = u_energy + v_energy
    if total == 0:
        return "C"
    ratio = u_energy / total
    if ratio > 0.9:
        return "L"
    elif ratio < 0.1:
        return "T"
    else:
        return "C"


def run_modal_comparison(params: dict, N: int = 500,
                         n_modes: int = 20) -> dict:
    """
    Run all 4 modal analysis cases and return results.

    Cases:
      1. eta_j=1.0,  Coriolis=off
      2. eta_j=0.95, Coriolis=off
      3. eta_j=1.0,  Coriolis=on
      4. eta_j=0.95, Coriolis=on

    Returns dict keyed by case name, each containing modal results + mode types.
    """
    results = {}
    eta_values = [1.0, float(params["design"]["eta_j_baseline"])]
    coriolis_flags = [False, True]

    for eta_j in eta_values:
        for coriolis in coriolis_flags:
            case_name = f"eta{eta_j:.2f}_coriolis{'_on' if coriolis else '_off'}"
            print(f"  Modal analysis: {case_name} ...", end=" ", flush=True)

            mesh = generate_mesh(params, N=N, eta_j=eta_j)
            mats = assemble_global(mesh, params, include_coriolis=coriolis)
            free = apply_bc(mats)

            if not coriolis:
                modal = solve_standard(free["K"], free["M"], n_modes=n_modes)
            else:
                modal = solve_gyroscopic(free["K"], free["M"], free["G"],
                                         n_modes=n_modes)

            # Classify modes
            mode_types = []
            for i in range(len(modal["freq_hz"])):
                mode_types.append(classify_mode(modal["modes"][:, i]))
            modal["mode_types"] = mode_types

            results[case_name] = modal
            print(f"T1 = {modal['period_h'][0]:.2f} h")

    return results
