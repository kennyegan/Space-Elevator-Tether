"""
damping.py — Rayleigh damping calibration and assembly.

C = alpha_M * M + alpha_K * K

Coefficients chosen so that damping ratio = zeta at the first two
natural frequencies.
"""

from scipy import sparse


def compute_rayleigh_coefficients(omega_1: float, omega_2: float,
                                  zeta: float = 0.01) -> tuple:
    """
    Compute Rayleigh damping coefficients for target damping ratio zeta
    at angular frequencies omega_1 and omega_2.

    alpha_M = 2 * zeta * omega_1 * omega_2 / (omega_1 + omega_2)
    alpha_K = 2 * zeta / (omega_1 + omega_2)

    Returns
    -------
    (alpha_M, alpha_K) : tuple of floats
    """
    alpha_M = 2.0 * zeta * omega_1 * omega_2 / (omega_1 + omega_2)
    alpha_K = 2.0 * zeta / (omega_1 + omega_2)
    return alpha_M, alpha_K


def assemble_damping(M: sparse.spmatrix, K: sparse.spmatrix,
                     alpha_M: float, alpha_K: float) -> sparse.spmatrix:
    """Return C = alpha_M * M + alpha_K * K in sparse CSC format."""
    return (alpha_M * M + alpha_K * K).tocsc()
