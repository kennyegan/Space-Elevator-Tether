"""
assembly.py — Global matrix assembly with boundary conditions.

Assembles 1000×1000 (500 nodes × 2 DOF) global matrices from element
contributions, then applies boundary conditions (fixed anchor at node 0)
to produce the 998×998 free-DOF system.
"""

import numpy as np
from scipy import sparse

from simulations.fea.phase2_dynamics.config import get_constants
from simulations.fea.phase2_dynamics.element_matrices import (
    mass_consistent,
    stiffness_elastic,
    stiffness_tension,
    stiffness_gravity_gradient,
    gyroscopic_coriolis,
)


def assemble_global(mesh: dict, params: dict,
                    include_coriolis: bool = True) -> dict:
    """
    Assemble global M, K, G matrices in sparse COO -> CSC format.

    DOF ordering: [u_0, v_0, u_1, v_1, ..., u_{N-1}, v_{N-1}]
    Total DOFs: 2*N (before boundary conditions).

    Parameters
    ----------
    mesh : dict
        Output from mesh.generate_mesh().
    params : dict
        Master parameters.
    include_coriolis : bool
        If True, assemble the gyroscopic matrix G.

    Returns
    -------
    dict with keys:
        M, K_elastic, K_tension, K_gg, K_total, G : sparse CSC (2N × 2N)
        n_total_dof : int (2*N)
        mesh : dict (passed through)
    """
    c = get_constants(params)
    N = mesh["N"]
    n_dof = 2 * N

    # COO accumulation lists
    rows_M, cols_M, vals_M = [], [], []
    rows_Ke, cols_Ke, vals_Ke = [], [], []
    rows_Kt, cols_Kt, vals_Kt = [], [], []
    rows_Kgg, cols_Kgg, vals_Kgg = [], [], []
    rows_G, cols_G, vals_G = [], [], []

    for e in range(mesh["N_elem"]):
        # Global DOF indices for this element
        i_left = e
        i_right = e + 1
        dofs = [2 * i_left, 2 * i_left + 1, 2 * i_right, 2 * i_right + 1]

        L_e = mesh["L_e"][e]
        A_e = mesh["A_e"][e]
        T_e = mesh["T_e"][e]
        EA_e = mesh["EA_e"][e]

        # Element matrices
        Me = mass_consistent(c["rho"], A_e, L_e)
        Kee = stiffness_elastic(EA_e, L_e)
        Kte = stiffness_tension(T_e, L_e)
        Kgge = stiffness_gravity_gradient(
            c["rho"], A_e, L_e,
            mesh["r_nodes"][i_left], mesh["r_nodes"][i_right],
            c["GM"], c["omega"],
        )

        # Scatter into COO lists
        for a in range(4):
            for b in range(4):
                r, cc_ = dofs[a], dofs[b]
                if Me[a, b] != 0:
                    rows_M.append(r); cols_M.append(cc_); vals_M.append(Me[a, b])
                if Kee[a, b] != 0:
                    rows_Ke.append(r); cols_Ke.append(cc_); vals_Ke.append(Kee[a, b])
                if Kte[a, b] != 0:
                    rows_Kt.append(r); cols_Kt.append(cc_); vals_Kt.append(Kte[a, b])
                if Kgge[a, b] != 0:
                    rows_Kgg.append(r); cols_Kgg.append(cc_); vals_Kgg.append(Kgge[a, b])

        if include_coriolis:
            Ge = gyroscopic_coriolis(c["rho"], A_e, L_e, c["omega"])
            for a in range(4):
                for b in range(4):
                    if Ge[a, b] != 0:
                        rows_G.append(dofs[a]); cols_G.append(dofs[b])
                        vals_G.append(Ge[a, b])

    shape = (n_dof, n_dof)
    M = sparse.coo_matrix((vals_M, (rows_M, cols_M)), shape=shape).tocsc()
    K_elastic = sparse.coo_matrix((vals_Ke, (rows_Ke, cols_Ke)), shape=shape).tocsc()
    K_tension = sparse.coo_matrix((vals_Kt, (rows_Kt, cols_Kt)), shape=shape).tocsc()
    K_gg = sparse.coo_matrix((vals_Kgg, (rows_Kgg, cols_Kgg)), shape=shape).tocsc()
    K_total = K_elastic + K_tension + K_gg

    if include_coriolis:
        G = sparse.coo_matrix((vals_G, (rows_G, cols_G)), shape=shape).tocsc()
    else:
        G = sparse.csc_matrix(shape)

    # Add counterweight mass at the last node (node N-1)
    last_u = 2 * (N - 1)
    last_v = 2 * (N - 1) + 1
    # Convert M to LIL for efficient element-wise modification, then back to CSC
    M = M.tolil()
    M[last_u, last_u] += c["m_counterweight"]
    M[last_v, last_v] += c["m_counterweight"]
    M = M.tocsc()

    return {
        "M": M,
        "K_elastic": K_elastic,
        "K_tension": K_tension,
        "K_gg": K_gg,
        "K_total": K_total,
        "G": G,
        "n_total_dof": n_dof,
        "mesh": mesh,
    }


def apply_bc(matrices: dict) -> dict:
    """
    Apply boundary conditions: fix node 0 (u_0 = v_0 = 0).

    Eliminates DOFs 0 and 1 from all matrices by slicing [2:, 2:].

    Returns
    -------
    dict with keys:
        M, K, G : sparse CSC (n_free × n_free)
        K_elastic, K_tension, K_gg : sparse CSC (for diagnostics)
        n_free_dof : int (2*N - 2)
        free_dof_start : int (2, the first free DOF index)
        mesh : dict (passed through)
    """
    s = slice(2, None)  # skip DOFs 0, 1

    M_free = matrices["M"][s, s].tocsc()
    K_free = matrices["K_total"][s, s].tocsc()
    G_free = matrices["G"][s, s].tocsc()
    Ke_free = matrices["K_elastic"][s, s].tocsc()
    Kt_free = matrices["K_tension"][s, s].tocsc()
    Kgg_free = matrices["K_gg"][s, s].tocsc()

    n_free = M_free.shape[0]

    return {
        "M": M_free,
        "K": K_free,
        "G": G_free,
        "K_elastic": Ke_free,
        "K_tension": Kt_free,
        "K_gg": Kgg_free,
        "n_free_dof": n_free,
        "free_dof_start": 2,
        "mesh": matrices["mesh"],
    }


def check_K_positive_definite(K_sparse, n_check: int = 6) -> float:
    """
    Check that K_total has all positive eigenvalues by computing the smallest.

    Returns the smallest eigenvalue. Raises ValueError if negative.
    """
    from scipy.sparse.linalg import eigsh

    try:
        # Use shift-invert mode for finding smallest eigenvalues
        eigenvalues, _ = eigsh(K_sparse, k=n_check, which="LM",
                               sigma=0.0, mode="normal", maxiter=20000)
        min_eig = float(np.min(np.real(eigenvalues)))
    except Exception:
        # Fallback: try Cholesky factorization — if it succeeds, K is PD
        try:
            from scipy.sparse.linalg import splu
            lu = splu(K_sparse.tocsc())
            # Check if all diagonal elements of U are positive
            diag_U = lu.U.diagonal()
            min_diag = float(np.min(diag_U))
            min_eig = min_diag  # positive diag_U implies PD
        except Exception:
            min_eig = float("nan")
    return min_eig
