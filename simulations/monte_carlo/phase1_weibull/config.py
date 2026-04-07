"""
config.py — Constants, sweep grids, and SLURM task mapping for Weibull MC sweep.

The Weibull shape parameter beta (time-to-failure aging) is distinct from the
Weibull modulus m (volume scaling for weakest-link statistics). They are never
conflated in variable names.
"""

import hashlib
import math
import struct
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]  # Space-Elevator-Tether/
PARAMS_FILE = ROOT / "data" / "parameters.yaml"
OUTPUT_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "paper" / "figures"
STYLE_FILE = ROOT / "scripts" / "acta_astronautica.mplstyle"
RESULTS_DIR = Path(__file__).resolve().parent / "results"

# ---------------------------------------------------------------------------
# 5-D sweep grid
# ---------------------------------------------------------------------------
N_SWEEP = [12, 15, 18, 21, 24, 50, 83, 100, 200, 500]
ETA_J_SWEEP = [0.70, 0.75, 0.80, 0.85, 0.88, 0.90, 0.93, 0.95, 0.97]
CADENCE_SWEEP = [1, 2, 5, 10]
P_DET_SWEEP = [0.50, 0.70, 0.80, 0.90, 0.95, 0.99, 0.995]
BETA_SWEEP = [1.0, 1.3, 1.5, 2.0, 2.5]

GRID_SIZES = (len(N_SWEEP), len(ETA_J_SWEEP), len(CADENCE_SWEEP),
              len(P_DET_SWEEP), len(BETA_SWEEP))
TOTAL_COMBOS = math.prod(GRID_SIZES)  # 12,600

# SLURM chunking
CHUNK_SIZE = 50
N_TASKS = math.ceil(TOTAL_COMBOS / CHUNK_SIZE)  # 252


# ---------------------------------------------------------------------------
# Index mapping
# ---------------------------------------------------------------------------
def flat_index(i: int, j: int, k: int, m: int, b: int) -> int:
    """Map 5-D sweep indices to a flat combo ID (row-major)."""
    _, nj, nk, nm, nb = GRID_SIZES
    return ((((i * nj + j) * nk + k) * nm + m) * nb + b)


def index_to_params(flat_idx: int) -> dict:
    """Recover parameter values from a flat combo index."""
    _, nj, nk, nm, nb = GRID_SIZES
    b = flat_idx % nb
    flat_idx //= nb
    m = flat_idx % nm
    flat_idx //= nm
    k = flat_idx % nk
    flat_idx //= nk
    j = flat_idx % nj
    flat_idx //= nj
    i = flat_idx
    return {
        "N": N_SWEEP[i],
        "eta_j": ETA_J_SWEEP[j],
        "cadence": CADENCE_SWEEP[k],
        "p_det": P_DET_SWEEP[m],
        "beta": BETA_SWEEP[b],
        "flat_idx": flat_index(i, j, k, m, b),
    }


def task_to_combos(task_id: int) -> list[dict]:
    """Return the list of parameter dicts for a given SLURM task."""
    start = task_id * CHUNK_SIZE
    end = min(start + CHUNK_SIZE, TOTAL_COMBOS)
    return [index_to_params(idx) for idx in range(start, end)]


# ---------------------------------------------------------------------------
# Deterministic, collision-free seed from parameter tuple
# ---------------------------------------------------------------------------
def combo_seed(N: int, eta_j: float, cadence: int,
               p_det: float, beta: float) -> int:
    """SHA-256 hash of parameter tuple → unsigned 32-bit int seed."""
    key = f"{N}_{eta_j:.4f}_{cadence}_{p_det:.4f}_{beta:.2f}"
    h = hashlib.sha256(key.encode()).digest()[:4]
    return struct.unpack("<I", h)[0]
