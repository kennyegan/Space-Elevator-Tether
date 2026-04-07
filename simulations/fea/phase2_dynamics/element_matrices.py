"""
element_matrices.py — 4×4 element matrices for 2-node, 2-DOF-per-node elements.

DOF ordering per element: [u_i, v_i, u_{i+1}, v_{i+1}]
where u = longitudinal (radial) and v = transverse (in-plane, along-track).

Five matrix types:
  M_e  — consistent mass
  Ke   — elastic stiffness (longitudinal, EA/L)
  Kt   — tension-string stiffness (transverse, T/L)
  Kgg  — gravity-gradient stiffness (position-dependent, EXCLUDES tension term)
  G_e  — Coriolis/gyroscopic (skew-symmetric)
"""

import numpy as np


def mass_consistent(rho: float, A_e: float, L_e: float) -> np.ndarray:
    """
    Consistent mass matrix for a 2-DOF-per-node bar element.

    M_e = (rho * A * L / 6) * [[2, 0, 1, 0],
                                 [0, 2, 0, 1],
                                 [1, 0, 2, 0],
                                 [0, 1, 0, 2]]
    """
    c = rho * A_e * L_e / 6.0
    return c * np.array([
        [2, 0, 1, 0],
        [0, 2, 0, 1],
        [1, 0, 2, 0],
        [0, 1, 0, 2],
    ], dtype=np.float64)


def stiffness_elastic(EA_e: float, L_e: float) -> np.ndarray:
    """
    Elastic stiffness (longitudinal only): rod element EA/L.

    Ke = (EA/L) * [[ 1, 0, -1, 0],
                    [ 0, 0,  0, 0],
                    [-1, 0,  1, 0],
                    [ 0, 0,  0, 0]]
    """
    c = EA_e / L_e
    return c * np.array([
        [ 1, 0, -1, 0],
        [ 0, 0,  0, 0],
        [-1, 0,  1, 0],
        [ 0, 0,  0, 0],
    ], dtype=np.float64)


def stiffness_tension(T_e: float, L_e: float) -> np.ndarray:
    """
    Geometric stiffness from pre-tension (transverse only): tensioned string T/L.

    Kt = (T/L) * [[0, 0,  0,  0],
                    [0, 1,  0, -1],
                    [0, 0,  0,  0],
                    [0,-1,  0,  1]]

    T_e = sigma_design * A_e is the spatially varying equilibrium tension.
    """
    c = T_e / L_e
    return c * np.array([
        [0, 0,  0,  0],
        [0, 1,  0, -1],
        [0, 0,  0,  0],
        [0, -1, 0,  1],
    ], dtype=np.float64)


def stiffness_gravity_gradient(rho: float, A_e: float, L_e: float,
                                r_i: float, r_ip1: float,
                                GM: float, omega: float) -> np.ndarray:
    """
    Gravity-gradient stiffness — LONGITUDINAL ONLY.

    For a radial perturbation u at equilibrium radius r, the linearized
    gravity-gradient restoring force is:
        f_gg = rho * A * (omega^2 + 2*GM/r^3) * u    [always positive = restoring]

    This enters as a positive-definite contribution to the u-u block of K.

    The TRANSVERSE gravity-gradient is NOT included here. The transverse
    restoring force comes entirely from the tension-string stiffness
    d/dr[T dv/dr], which is captured by K_tension. The weak form of this
    operator (integral of T * dw/dr * dv/dr) with piecewise-constant T per
    element correctly accounts for the spatially varying tension, including
    the tension gradient. Any residual transverse body force from the
    gravity-gradient (order omega^2*v) is negligible compared to the tension
    restoring force and would require careful treatment of the sign change
    at GEO — omitting it is both physically justified and numerically safer.

    Uses 2-point Gauss quadrature for the longitudinal coefficient.

    Parameters
    ----------
    rho : density [kg/m^3]
    A_e : element cross-sectional area [m^2]
    L_e : element length [m]
    r_i, r_ip1 : node radii [m]
    GM : gravitational parameter [m^3/s^2]
    omega : Earth rotation rate [rad/s]
    """
    # 2-point Gauss quadrature on [0, 1]
    xi_pts = np.array([0.5 - 0.5 / np.sqrt(3), 0.5 + 0.5 / np.sqrt(3)])
    w_pts = np.array([0.5, 0.5])

    Kgg = np.zeros((4, 4), dtype=np.float64)

    for xi, w in zip(xi_pts, w_pts):
        r = r_i + xi * (r_ip1 - r_i)
        cL = omega ** 2 + 2.0 * GM / r ** 3

        N1 = 1.0 - xi
        N2 = xi

        # Only u-u block (indices 0,2 for u_i, u_{i+1})
        Kgg[0, 0] += w * cL * N1 * N1
        Kgg[0, 2] += w * cL * N1 * N2
        Kgg[2, 0] += w * cL * N2 * N1
        Kgg[2, 2] += w * cL * N2 * N2

    Kgg *= rho * A_e * L_e
    return Kgg


def gyroscopic_coriolis(rho: float, A_e: float, L_e: float,
                        omega: float) -> np.ndarray:
    """
    Coriolis/gyroscopic matrix (skew-symmetric: G + G^T = 0).

    In the rotating frame, Coriolis acceleration on a mass element:
      a_coriolis = -2 * omega x v_dot
    For 2D (u = radial outward, v = prograde):
      F_u = +2 * m * omega * v_dot   (Coriolis from transverse velocity)
      F_v = -2 * m * omega * u_dot   (Coriolis from radial velocity)

    Using consistent mass weighting:

    G_e = 2*omega * (rho*A*L/6) * [[ 0,  2,  0,  1],
                                     [-2,  0, -1,  0],
                                     [ 0,  1,  0,  2],
                                     [-1,  0, -2,  0]]

    This is skew-symmetric by construction.
    """
    c = 2.0 * omega * rho * A_e * L_e / 6.0
    return c * np.array([
        [ 0,  2,  0,  1],
        [-2,  0, -1,  0],
        [ 0,  1,  0,  2],
        [-1,  0, -2,  0],
    ], dtype=np.float64)
