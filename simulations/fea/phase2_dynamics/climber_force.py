"""
climber_force.py — Time-varying climber force vector.

The climber is a point mass traversing the tether at constant radial velocity.
Its weight is distributed to the two bracketing nodes via linear shape functions.
Forces include:
  - Longitudinal: gravity-gradient (net centrifugal - gravitational)
  - Transverse: Coriolis force on the climbing mass (-2*m*omega*v_radial)
"""

import numpy as np
from simulations.fea.phase2_dynamics.config import get_constants


def climber_force_at_t(t: float, r_nodes: np.ndarray, params: dict,
                       n_free_dof: int, t_start: float = 0.0) -> np.ndarray:
    """
    Compute the global force vector from a single climber at time t.

    Parameters
    ----------
    t : float
        Current time [s].
    r_nodes : ndarray, shape (N,)
        Node radial positions [m].
    params : dict
        Master parameters.
    n_free_dof : int
        Number of free DOFs (after BC elimination).
    t_start : float
        Departure time of this climber [s].

    Returns
    -------
    F : ndarray, shape (n_free_dof,)
        Force vector in free-DOF space (node 0 eliminated).
    """
    c = get_constants(params)
    F = np.zeros(n_free_dof)

    elapsed = t - t_start
    if elapsed < 0:
        return F  # climber hasn't departed yet

    r_climber = c["R_earth"] + c["v_climber"] * elapsed

    # Check bounds
    r_min = r_nodes[0]
    r_max = r_nodes[-1]
    if r_climber < r_min or r_climber > r_max:
        return F  # climber not on tether

    # Find bracketing element
    idx = np.searchsorted(r_nodes, r_climber) - 1
    idx = max(0, min(idx, len(r_nodes) - 2))

    r_left = r_nodes[idx]
    r_right = r_nodes[idx + 1]
    xi = (r_climber - r_left) / (r_right - r_left)
    xi = np.clip(xi, 0.0, 1.0)

    # Forces on the climber (applied as reaction to tether)
    # Longitudinal: net gravity-gradient force
    F_u = c["m_climber"] * (c["omega"] ** 2 * r_climber - c["GM"] / r_climber ** 2)

    # Transverse: Coriolis force on climbing mass
    # In rotating frame, radially moving mass experiences -2*m*omega*v_r (prograde deflection)
    # For outward climb (v_r > 0), Coriolis pushes retrograde: F_v = -2*m*omega*v_climber
    F_v = -2.0 * c["m_climber"] * c["omega"] * c["v_climber"]

    # Distribute to nodes using shape functions
    # Global DOFs for node idx: (2*idx, 2*idx+1)
    # After BC elimination (node 0 removed): shift by -2
    # Free DOF for node i: (2*i - 2, 2*i - 1) for i >= 1
    for node_idx, weight in [(idx, 1.0 - xi), (idx + 1, xi)]:
        if node_idx == 0:
            continue  # fixed node, force absorbed by support
        free_u = 2 * node_idx - 2
        free_v = 2 * node_idx - 1
        if 0 <= free_u < n_free_dof:
            F[free_u] += weight * F_u
        if 0 <= free_v < n_free_dof:
            F[free_v] += weight * F_v

    return F


def multi_climber_force(t: float, r_nodes: np.ndarray, params: dict,
                        n_free_dof: int,
                        schedule: list) -> np.ndarray:
    """
    Sum forces from multiple climbers.

    Parameters
    ----------
    schedule : list of dict
        Each dict has 't_start': departure time [s].

    Returns
    -------
    F : ndarray, shape (n_free_dof,)
    """
    F = np.zeros(n_free_dof)
    for climber in schedule:
        F += climber_force_at_t(t, r_nodes, params, n_free_dof,
                                t_start=climber["t_start"])
    return F
