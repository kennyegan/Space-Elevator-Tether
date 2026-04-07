"""
config.py — Physical constants, mesh parameters, and paths for phase2_dynamics.

Imports load_params from the existing taper_profile module to maintain a single
source of truth (data/parameters.yaml).
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]
PARAMS_FILE = ROOT / "data" / "parameters.yaml"
OUTPUT_DIR = ROOT / "data" / "processed" / "phase2_dynamics"
FIGURES_DIR = ROOT / "paper" / "figures"
STYLE_FILE = ROOT / "scripts" / "acta_astronautica.mplstyle"

# Ensure project root is on sys.path so we can import sibling packages
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulations.fea.taper_profile import load_params  # noqa: E402

# ---------------------------------------------------------------------------
# Default simulation parameters
# ---------------------------------------------------------------------------
N_NODES = 500          # Number of mesh nodes (2 DOF each -> 1000 total DOFs)
N_MODES = 20           # Number of modes to extract
DT = 500.0             # Time step [s] for Newmark-beta
T_FREE = 180_000.0     # Free-vibration time after climber detaches [s] (50 h)
OUTPUT_STRIDE = 10     # Save every Nth time step
ZETA_TARGET = 0.01     # Target damping ratio for Rayleigh damping


def get_constants(params: dict) -> dict:
    """Extract frequently used physical constants from the master params dict."""
    return {
        "GM": float(params["physical"]["GM_earth"]),
        "R_earth": float(params["physical"]["R_earth"]),
        "omega": float(params["physical"]["omega_earth"]),
        "rho": float(params["material"]["rho"]),
        "E": float(params["material"]["E_yarn"]),
        "sigma_design": float(params["design"]["sigma_allow"]),
        "eta_j": float(params["design"]["eta_j_baseline"]),
        "L_total": float(params["tether"]["L_total"]),
        "m_climber": float(params["climber"]["m_climber"]),
        "v_climber": float(params["climber"]["v_climber"]),
        "m_counterweight": float(params["climber"]["m_counterweight"]),
        "r_GEO": float(params["orbital"]["r_GEO"]),
    }
