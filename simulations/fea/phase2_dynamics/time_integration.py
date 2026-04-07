"""
time_integration.py — Newmark-beta (primary) and BDF (backup) time integrators.

The Newmark-beta implementation handles the gyroscopic (skew-symmetric) matrix G
by using a general sparse LU factorization (splu) rather than Cholesky, since
K_eff = K + (1/beta/dt^2)*M + (gamma/beta/dt)*(C+G) is non-symmetric when G != 0.
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu, spsolve

from simulations.fea.phase2_dynamics.config import DT, OUTPUT_STRIDE


def newmark_beta(M: sparse.spmatrix, C_total: sparse.spmatrix,
                 K: sparse.spmatrix, F_func,
                 t_start: float, t_end: float, dt: float = DT,
                 beta: float = 0.25, gamma: float = 0.5,
                 x0: np.ndarray = None, v0: np.ndarray = None,
                 output_stride: int = OUTPUT_STRIDE) -> dict:
    """
    Newmark-beta time integration with gyroscopic terms.

    Solves: M*a + C_total*v + K*x = F(t)
    where C_total = C_damping + G_coriolis (non-symmetric).

    Parameters
    ----------
    M, C_total, K : sparse matrices (n_dof × n_dof)
        C_total includes both Rayleigh damping and Coriolis matrix.
    F_func : callable
        F_func(t) -> ndarray of shape (n_dof,)
    t_start, t_end : float
        Time span [s].
    dt : float
        Time step [s].
    beta, gamma : float
        Newmark parameters. Default (0.25, 0.5) = average acceleration
        (unconditionally stable, no numerical damping).
    x0, v0 : ndarray or None
        Initial displacement and velocity. Default: zeros.
    output_stride : int
        Save every Nth step.

    Returns
    -------
    dict with:
        t       : (n_out,) time array [s]
        x       : (n_dof, n_out) displacement history
        v       : (n_dof, n_out) velocity history
    """
    n_dof = M.shape[0]

    if x0 is None:
        x0 = np.zeros(n_dof)
    if v0 is None:
        v0 = np.zeros(n_dof)

    # Newmark constants
    a0 = 1.0 / (beta * dt ** 2)
    a1 = gamma / (beta * dt)
    a2 = 1.0 / (beta * dt)
    a3 = 1.0 / (2.0 * beta) - 1.0
    a4 = gamma / beta - 1.0
    a5 = dt / 2.0 * (gamma / beta - 2.0)

    # Effective stiffness: K_eff = K + a0*M + a1*C_total
    # NOT symmetric because C_total contains the skew-symmetric G
    K_eff = (K + a0 * M + a1 * C_total).tocsc()

    # Sparse LU factorization (handles non-symmetric matrices)
    K_eff_lu = splu(K_eff)

    # Initial acceleration
    F0 = F_func(t_start)
    # a0_vec = M^{-1} * (F0 - C_total*v0 - K*x0)
    rhs_init = F0 - C_total @ v0 - K @ x0
    a_n = spsolve(M.tocsc(), rhs_init)

    # Time stepping
    n_steps = int(np.ceil((t_end - t_start) / dt))
    n_out = n_steps // output_stride + 1

    t_out = np.zeros(n_out)
    x_out = np.zeros((n_dof, n_out))
    v_out = np.zeros((n_dof, n_out))

    # Store initial state
    t_out[0] = t_start
    x_out[:, 0] = x0
    v_out[:, 0] = v0

    x_n = x0.copy()
    v_n = v0.copy()
    out_idx = 1
    t_n = t_start

    for step in range(1, n_steps + 1):
        t_np1 = t_start + step * dt

        # Effective force
        F_np1 = F_func(t_np1)
        F_eff = (F_np1
                 + M @ (a0 * x_n + a2 * v_n + a3 * a_n)
                 + C_total @ (a1 * x_n + a4 * v_n + a5 * a_n))

        # Solve for x_{n+1}
        x_np1 = K_eff_lu.solve(F_eff)

        # Update acceleration and velocity
        a_np1 = a0 * (x_np1 - x_n) - a2 * v_n - a3 * a_n
        v_np1 = v_n + dt * ((1.0 - gamma) * a_n + gamma * a_np1)

        # Store output
        if step % output_stride == 0 and out_idx < n_out:
            t_out[out_idx] = t_np1
            x_out[:, out_idx] = x_np1
            v_out[:, out_idx] = v_np1
            out_idx += 1

        # Advance
        x_n = x_np1
        v_n = v_np1
        a_n = a_np1
        t_n = t_np1

    # Store final state if not already stored
    if out_idx < n_out:
        t_out[out_idx] = t_n
        x_out[:, out_idx] = x_n
        v_out[:, out_idx] = v_n
        out_idx += 1

    # Trim
    t_out = t_out[:out_idx]
    x_out = x_out[:, :out_idx]
    v_out = v_out[:, :out_idx]

    return {"t": t_out, "x": x_out, "v": v_out}


def solve_bdf(M: sparse.spmatrix, C_total: sparse.spmatrix,
              K: sparse.spmatrix, F_func,
              t_start: float, t_end: float,
              x0: np.ndarray = None, v0: np.ndarray = None,
              max_step: float = 500.0,
              output_stride: int = OUTPUT_STRIDE) -> dict:
    """
    BDF time integration via scipy.integrate.solve_ivp.

    Converts to first-order state-space: z = [x; v], z_dot = f(t, z).
    Uses pre-computed M_inv to avoid solving M at every RHS evaluation.

    This is slower than Newmark-beta but useful for validation.
    """
    from scipy.integrate import solve_ivp

    n_dof = M.shape[0]
    if x0 is None:
        x0 = np.zeros(n_dof)
    if v0 is None:
        v0 = np.zeros(n_dof)

    # Pre-compute M_inv (dense, for RHS evaluation speed)
    M_inv = np.linalg.inv(M.toarray())
    K_d = K.toarray()
    CG_d = C_total.toarray()

    def rhs(t, z):
        x = z[:n_dof]
        v = z[n_dof:]
        F = F_func(t)
        a = M_inv @ (F - CG_d @ v - K_d @ x)
        return np.concatenate([v, a])

    z0 = np.concatenate([x0, v0])

    # Time points for output
    dt_out = max_step * output_stride
    t_eval = np.arange(t_start, t_end + dt_out, dt_out)
    t_eval = t_eval[t_eval <= t_end]

    sol = solve_ivp(rhs, (t_start, t_end), z0, method="BDF",
                    t_eval=t_eval, max_step=max_step,
                    rtol=1e-6, atol=1e-9)

    return {
        "t": sol.t,
        "x": sol.y[:n_dof, :],
        "v": sol.y[n_dof:, :],
    }
