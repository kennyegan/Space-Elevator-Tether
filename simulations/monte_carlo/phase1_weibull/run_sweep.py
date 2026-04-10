"""
run_sweep.py — Local sweep orchestrator for Weibull Monte Carlo.

Usage:
    cd ~/Space-Elevator-Tether

    # Quick test (1K trajectories, baseline only)
    python -m simulations.monte_carlo.phase1_weibull.run_sweep \\
        --n-trajectories 1000 --single

    # Full sweep (100K trajectories, all 12,600 combos)
    python -m simulations.monte_carlo.phase1_weibull.run_sweep \\
        --n-trajectories 100000

    # Filter by beta
    python -m simulations.monte_carlo.phase1_weibull.run_sweep \\
        --n-trajectories 10000 --beta 1.5
"""

import argparse
import time

import numpy as np

from simulations.monte_carlo.phase1_weibull.config import (
    BETA_SWEEP,
    CADENCE_SWEEP,
    ETA_J_SWEEP,
    N_SWEEP,
    P_DET_SWEEP,
    RESULTS_DIR,
    TOTAL_COMBOS,
    combo_seed,
    flat_index,
)
from simulations.monte_carlo.phase1_weibull.hazard_model import (
    calibrate_arrhenius,
    load_params,
)
from simulations.monte_carlo.phase1_weibull.simulate import run_batch_weibull


def main():
    parser = argparse.ArgumentParser(
        description="Weibull Monte Carlo sweep (local execution)")
    parser.add_argument("--n-trajectories", type=int, default=None,
                        help="Trajectories per combo. Default: from YAML (100K)")
    parser.add_argument("--single", action="store_true",
                        help="Run only baseline (N=18, η_j=0.95, cad=1, "
                             "p_det=0.995, β=1.5)")
    parser.add_argument("--beta", type=float, default=None,
                        help="Run only this beta value")
    args = parser.parse_args()

    params = load_params()
    n_traj = args.n_trajectories or int(params["monte_carlo"]["n_trajectories"])

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("WEIBULL MONTE CARLO SWEEP (LOCAL)")
    print("=" * 60)
    print(f"  Trajectories per combo: {n_traj}")

    lambda_0_pre = calibrate_arrhenius(params)

    t_start = time.time()

    if args.single:
        # Baseline point
        N, eta_j, cad, pdet, beta = 18, 0.95, 1, 0.995, 1.5
        print(f"\n  Mode: SINGLE (N={N}, η_j={eta_j}, cad={cad}, "
              f"p_det={pdet}, β={beta})")
        seed = combo_seed(N, eta_j, cad, pdet, beta)
        result = run_batch_weibull(N, eta_j, cad, pdet, lambda_0_pre,
                                   params, n_traj, beta=beta, seed=seed)
        print(f"\n  P_sys       = {result['P_sys']:.5f}")
        print(f"  Mean repairs= {result['mean_repairs']:.2f}")
        print(f"  MTTR median = {result['median_MTTR']:.1f} h")
        print(f"  MTTR p05    = {result['p05_MTTR']:.1f} h")
        print(f"  MTTR p95    = {result['p95_MTTR']:.1f} h")
        print(f"  Failures    = {result['n_failures']}/{n_traj}")
    else:
        # Full sweep
        betas = [args.beta] if args.beta else BETA_SWEEP
        total = (len(N_SWEEP) * len(ETA_J_SWEEP) * len(CADENCE_SWEEP)
                 * len(P_DET_SWEEP) * len(betas))
        print(f"\n  N sweep:       {N_SWEEP}")
        print(f"  η_j sweep:     {ETA_J_SWEEP}")
        print(f"  Cadence sweep: {CADENCE_SWEEP}")
        print(f"  p_det sweep:   {P_DET_SWEEP}")
        print(f"  β sweep:       {betas}")
        print(f"  Total combos:  {total}")
        print(f"  Total trajs:   {total * n_traj:,}")
        print()

        combo = 0
        for i, N in enumerate(N_SWEEP):
            for j, eta_j in enumerate(ETA_J_SWEEP):
                for k, cad in enumerate(CADENCE_SWEEP):
                    for m, pdet in enumerate(P_DET_SWEEP):
                        for b, beta in enumerate(betas):
                            combo += 1
                            seed = combo_seed(N, eta_j, cad, pdet, beta)
                            idx = flat_index(
                                i, j, k, m,
                                BETA_SWEEP.index(beta) if args.beta else b)

                            result = run_batch_weibull(
                                N, eta_j, cad, pdet, lambda_0_pre,
                                params, n_traj, beta=beta, seed=seed)

                            # Save per-combo result
                            out = RESULTS_DIR / f"combo_{idx:05d}.npz"
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

                            if combo % 20 == 0 or combo == total:
                                elapsed = time.time() - t_start
                                print(
                                    f"  [{combo}/{total}] N={N}, "
                                    f"η={eta_j:.2f}, cad={cad}, "
                                    f"p={pdet:.3f}, β={beta:.1f}  →  "
                                    f"P_sys={result['P_sys']:.4f}  "
                                    f"({elapsed:.0f}s)")

        print(f"\n  Results saved to: {RESULTS_DIR}")

    elapsed = time.time() - t_start
    print(f"\n  Elapsed: {elapsed:.1f} s")
    print("Done.")


if __name__ == "__main__":
    main()
