"""
merge_results.py — Combine per-combination .npz outputs into merged files.

Usage:
    cd ~/Space-Elevator-Tether
    python -m simulations.monte_carlo.phase1_weibull.merge_results

Outputs:
    data/processed/psys_weibull_surface.npz  — 5D array + metadata
    data/processed/weibull_sweep_results.csv  — flat table
"""

import sys
from pathlib import Path

import csv

import numpy as np

from simulations.monte_carlo.phase1_weibull.config import (
    BETA_SWEEP,
    CADENCE_SWEEP,
    ETA_J_SWEEP,
    GRID_SIZES,
    N_SWEEP,
    OUTPUT_DIR,
    P_DET_SWEEP,
    RESULTS_DIR,
    TOTAL_COMBOS,
    index_to_params,
)


def main():
    print("=" * 60)
    print("MERGE WEIBULL SWEEP RESULTS")
    print("=" * 60)

    # --- Discover available combo files ---
    combo_files = sorted(RESULTS_DIR.glob("combo_*.npz"))
    found_indices = set()
    for f in combo_files:
        idx = int(f.stem.split("_")[1])
        found_indices.add(idx)

    expected = set(range(TOTAL_COMBOS))
    missing = expected - found_indices
    extra = found_indices - expected

    print(f"  Found:    {len(found_indices)} / {TOTAL_COMBOS} combo files")
    if missing:
        print(f"  Missing:  {len(missing)} combos")
        if len(missing) <= 20:
            for idx in sorted(missing):
                p = index_to_params(idx)
                print(f"            combo_{idx:05d}: N={p['N']}, "
                      f"η={p['eta_j']:.2f}, cad={p['cadence']}, "
                      f"p={p['p_det']:.3f}, β={p['beta']:.1f}")
    if extra:
        print(f"  Extra:    {len(extra)} unexpected files (ignored)")

    if not found_indices:
        print("  ERROR: No combo files found. Nothing to merge.")
        sys.exit(1)

    # --- Build flat table ---
    rows = []
    for idx in sorted(found_indices):
        f = RESULTS_DIR / f"combo_{idx:05d}.npz"
        data = np.load(f)
        rows.append({
            "N": int(data["N"]),
            "eta_j": float(data["eta_j"]),
            "cadence": int(data["cadence"]),
            "p_det": float(data["p_det"]),
            "beta": float(data["beta"]),
            "P_sys": float(data["P_sys"]),
            "mean_repairs": float(data["mean_repairs"]),
            "median_MTTR": float(data["median_MTTR"]),
            "p05_MTTR": float(data["p05_MTTR"]),
            "p95_MTTR": float(data["p95_MTTR"]),
        })

    # --- Save CSV (pure stdlib, no pandas) ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "weibull_sweep_results.csv"
    fieldnames = ["N", "eta_j", "cadence", "p_det", "beta",
                  "P_sys", "mean_repairs", "median_MTTR", "p05_MTTR", "p95_MTTR"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: f"{v:.6f}" if isinstance(v, float) else v
                             for k, v in row.items()})
    print(f"  Saved: {csv_path} ({len(rows)} rows)")

    # --- Build 5D arrays ---
    nN, nE, nC, nP, nB = GRID_SIZES
    P_sys_5d = np.full((nN, nE, nC, nP, nB), np.nan)
    MTTR_med_5d = np.full((nN, nE, nC, nP, nB), np.nan)
    repairs_5d = np.full((nN, nE, nC, nP, nB), np.nan)

    for row in rows:
        try:
            i = N_SWEEP.index(int(row["N"]))
            j = ETA_J_SWEEP.index(float(row["eta_j"]))
            k = CADENCE_SWEEP.index(int(row["cadence"]))
            m = P_DET_SWEEP.index(float(row["p_det"]))
            b = BETA_SWEEP.index(float(row["beta"]))
        except ValueError:
            continue
        P_sys_5d[i, j, k, m, b] = row["P_sys"]
        MTTR_med_5d[i, j, k, m, b] = row["median_MTTR"]
        repairs_5d[i, j, k, m, b] = row["mean_repairs"]

    npz_path = OUTPUT_DIR / "psys_weibull_surface.npz"
    np.savez(
        npz_path,
        N_values=N_SWEEP,
        eta_j_values=ETA_J_SWEEP,
        cadence_values=CADENCE_SWEEP,
        p_detection_values=P_DET_SWEEP,
        beta_values=BETA_SWEEP,
        P_sys=P_sys_5d,
        MTTR_median=MTTR_med_5d,
        mean_repairs=repairs_5d,
    )
    print(f"  Saved: {npz_path}")
    print(f"         P_sys shape: {P_sys_5d.shape}")

    # --- Summary ---
    n_filled = int(np.sum(~np.isnan(P_sys_5d)))
    n_total = P_sys_5d.size
    print(f"\n  5D array fill: {n_filled}/{n_total} "
          f"({100*n_filled/n_total:.1f}%)")

    if missing:
        print(f"\n  WARNING: {len(missing)} combos missing — "
              f"partial merge completed")
    else:
        print("\n  All combos present — merge complete")


if __name__ == "__main__":
    main()
