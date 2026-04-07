"""
hazard_model.py — Arrhenius hazard rates + Weibull TTF draws + volume scaling.

Imports the calibrated Arrhenius model from the existing joint_reliability.py
and adds Weibull-specific draw functions:
  - draw_weibull_ttf:              initial TTF for fresh joints
  - fresh_weibull_ttf:             TTF for a repaired (new-clock) joint
  - conditional_weibull_remaining: remaining life under changed hazard (aging)

Variable naming:
  beta / beta_shape  = Weibull shape for time-to-failure (swept 1.0–2.5)
  m_weibull          = Weibull modulus for volume scaling   (fixed = 6)
"""

import numpy as np

from simulations.monte_carlo.joint_reliability import (
    calibrate_arrhenius,
    compute_hazard_rates,
    compute_joint_positions,
    load_params,
    thermal_profile_3zone,
)

__all__ = [
    "calibrate_arrhenius",
    "compute_hazard_rates",
    "compute_joint_positions",
    "load_params",
    "thermal_profile_3zone",
    "draw_weibull_ttf",
    "fresh_weibull_ttf",
    "conditional_weibull_remaining",
]

# Maximum cumulative hazard before clipping (exp(700) ≈ 1e304, safe for float64).
_H_CLIP = 700.0


def draw_weibull_ttf(beta: float, scales, rng: np.random.Generator,
                     size=None):
    """
    Draw initial time-to-failure from Weibull(beta, scale) for each joint.

    Parameters
    ----------
    beta : float
        Weibull shape parameter (β = 1 → exponential).
    scales : ndarray of shape (n_joints,)
        Characteristic life per joint = 1 / λ_j.
    rng : numpy Generator
    size : tuple, optional
        Output shape.  If (n_traj, n_joints), scales is broadcast over axis 0.

    Returns
    -------
    ndarray — time-to-failure draws.
    """
    return rng.weibull(beta, size=size) * scales


def fresh_weibull_ttf(beta: float, scale: float,
                      rng: np.random.Generator) -> float:
    """
    Draw a single TTF for a repaired (fresh) joint — new clock from t = 0.

    Parameters
    ----------
    beta : float  — Weibull shape.
    scale : float — characteristic life = 1 / λ_j.
    rng : numpy Generator.

    Returns
    -------
    float — time-to-failure (relative to repair moment).
    """
    return scale * rng.weibull(beta)


def conditional_weibull_remaining(
    H_accum: float,
    new_scale: float,
    beta: float,
    rng: np.random.Generator,
) -> float:
    """
    Remaining life for a surviving joint given its total accumulated hazard.

    The caller is responsible for computing the total accumulated hazard
    H_accum = H_snapshot + (t_age / current_scale)^β, which correctly
    chains through arbitrary sequences of scale changes.

    Algorithm:
      E        ~ Exp(1)                          (new hazard increment)
      Δt       = new_scale × [(H_accum + E)^(1/β) − H_accum^(1/β)]

    At β = 1 this reduces to Δt = new_scale × E  (memoryless exponential).

    Parameters
    ----------
    H_accum   : total accumulated cumulative hazard (caller computes this).
    new_scale : Weibull scale after the stress change (= 1/λ_new).
    beta      : Weibull shape parameter.
    rng       : numpy Generator.

    Returns
    -------
    float — additional time until failure (Δt ≥ 0).
    """
    H_accum = min(H_accum, _H_CLIP)  # overflow guard
    E = rng.standard_exponential()
    H_total = H_accum + E
    delta_t = new_scale * (H_total ** (1.0 / beta) - H_accum ** (1.0 / beta))
    return max(delta_t, 0.0)
