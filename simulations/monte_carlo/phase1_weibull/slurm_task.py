"""
slurm_task.py — Single SLURM array task: processes a chunk of ~50 combos.

Usage:
    # From SLURM (automatic):
    python -m simulations.monte_carlo.phase1_weibull.slurm_task \\
        --task-id ${SLURM_ARRAY_TASK_ID}

    # Manual test (task 0 = first 50 combos):
    python -m simulations.monte_carlo.phase1_weibull.slurm_task \\
        --task-id 0 --n-trajectories 1000
"""

import argparse
import os
import sys
import time

import numpy as np

from simulations.monte_carlo.phase1_weibull.config import (
    RESULTS_DIR,
    combo_seed,
    task_to_combos,
)
from simulations.monte_carlo.phase1_weibull.hazard_model import (
    calibrate_arrhenius,
    load_params,
)
from simulations.monte_carlo.phase1_weibull.simulate import run_batch_weibull


def main():
    parser = argparse.ArgumentParser(description="Weibull MC — single SLURM task")
    parser.add_argument("--task-id", type=int, default=None,
                        help="SLURM array task ID. Default: read from "
                             "$SLURM_ARRAY_TASK_ID")
    parser.add_argument("--n-trajectories", type=int, default=None,
                        help="Trajectories per combo. Default: from YAML")
    args = parser.parse_args()

    task_id = args.task_id
    if task_id is None:
        task_id = int(os.environ.get("SLURM_ARRAY_TASK_ID", 0))

    params = load_params()
    n_traj = args.n_trajectories or int(params["monte_carlo"]["n_trajectories"])
    lambda_0_pre = calibrate_arrhenius(params)

    combos = task_to_combos(task_id)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Task {task_id}: {len(combos)} combinations, {n_traj} traj each")

    t_start = time.time()
    for i, c in enumerate(combos):
        N = c["N"]
        eta_j = c["eta_j"]
        cad = c["cadence"]
        pdet = c["p_det"]
        beta = c["beta"]
        idx = c["flat_idx"]

        # Skip if output already exists (resume support)
        out = RESULTS_DIR / f"combo_{idx:05d}.npz"
        if out.exists():
            elapsed = time.time() - t_start
            print(f"  [{i+1}/{len(combos)}] combo={idx} SKIP (exists)  ({elapsed:.0f}s)")
            continue

        seed = combo_seed(N, eta_j, cad, pdet, beta)
        result = run_batch_weibull(
            N, eta_j, cad, pdet, lambda_0_pre,
            params, n_traj, beta=beta, seed=seed)

        np.savez(
            out,
            N=N, eta_j=eta_j, cadence=cad,
            p_det=pdet, beta=beta,
            P_sys=result["P_sys"],
            mean_repairs=result["mean_repairs"],
            median_MTTR=result["median_MTTR"],
            p05_MTTR=result["p05_MTTR"],
            p95_MTTR=result["p95_MTTR"],
            n_failures=result["n_failures"],
        )

        elapsed = time.time() - t_start
        print(f"  [{i+1}/{len(combos)}] combo={idx} N={N} η={eta_j:.2f} "
              f"cad={cad} p={pdet:.3f} β={beta:.1f}  →  "
              f"P_sys={result['P_sys']:.4f}  ({elapsed:.0f}s)")

    elapsed = time.time() - t_start
    print(f"Task {task_id} complete: {len(combos)} combos in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
