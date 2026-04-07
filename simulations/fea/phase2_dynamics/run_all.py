"""
run_all.py — Top-level orchestrator for Phase 2 dynamics pipeline.

Usage:
    python simulations/fea/phase2_dynamics/run_all.py
    python simulations/fea/phase2_dynamics/run_all.py --validate-only
    python simulations/fea/phase2_dynamics/run_all.py --skip-multi
    python simulations/fea/phase2_dynamics/run_all.py --n-workers 4
"""

import argparse
import sys
import time
import numpy as np
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulations.fea.phase2_dynamics.config import (
    load_params, OUTPUT_DIR, FIGURES_DIR, N_NODES, N_MODES, DT, ZETA_TARGET,
)
from simulations.fea.phase2_dynamics.validate import (
    run_all_validations, write_validation_report,
)
from simulations.fea.phase2_dynamics.modal_analysis import run_modal_comparison
from simulations.fea.phase2_dynamics.single_climber import run_single_transit
from simulations.fea.phase2_dynamics.multi_climber import (
    run_resonance_sweep, run_damping_sensitivity,
)
from simulations.fea.phase2_dynamics.plot_figures import (
    plot_all_single, plot_all_multi,
)
from simulations.fea.phase2_dynamics.comparison_table import (
    generate_comparison_table,
)


def main():
    parser = argparse.ArgumentParser(description="Phase 2 Dynamics Pipeline")
    parser.add_argument("--validate-only", action="store_true",
                        help="Run validation checks only")
    parser.add_argument("--skip-multi", action="store_true",
                        help="Skip multi-climber resonance sweep")
    parser.add_argument("--skip-validate", action="store_true",
                        help="Skip validation checks")
    parser.add_argument("--n-workers", type=int, default=1,
                        help="Number of parallel workers for resonance sweep")
    parser.add_argument("--N", type=int, default=N_NODES,
                        help="Number of mesh nodes")
    args = parser.parse_args()

    t0 = time.time()

    print("=" * 65)
    print("PHASE 2: 2D Coriolis-Coupled Dynamic Model")
    print("=" * 65)

    params = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ==================================================================
    # 1. Validation
    # ==================================================================
    if not args.skip_validate:
        print("\n" + "=" * 65)
        print("STEP 1: Validation Checks")
        print("=" * 65)
        val_results = run_all_validations(params)
        write_validation_report(val_results, OUTPUT_DIR / "validation_report.txt")

        n_pass = sum(r["passed"] for r in val_results)
        if n_pass < len(val_results):
            print(f"\n  WARNING: {len(val_results) - n_pass} validation checks FAILED!")
            print("  Proceeding anyway (results may be unreliable).")

        if args.validate_only:
            print(f"\n  Total time: {time.time() - t0:.1f} s")
            return

    # ==================================================================
    # 2. Modal comparison (Part C)
    # ==================================================================
    print("\n" + "=" * 65)
    print("STEP 2: Modal Analysis (4 cases)")
    print("=" * 65)
    modal_results = run_modal_comparison(params, N=args.N, n_modes=N_MODES)

    # Print summary table
    print("\n  Modal Comparison Table:")
    print(f"  {'Case':<30} {'T1 [h]':>10} {'T2 [h]':>10} {'Mode 1 Type':>12}")
    print("  " + "-" * 65)
    for case_name, modal in modal_results.items():
        print(f"  {case_name:<30} {modal['period_h'][0]:>10.2f} "
              f"{modal['period_h'][1]:>10.2f} {modal['mode_types'][0]:>12}")

    # Save modal results
    modal_save = {}
    for case_name, modal in modal_results.items():
        modal_save[f"{case_name}_freq_hz"] = modal["freq_hz"]
        modal_save[f"{case_name}_period_h"] = modal["period_h"]
    np.savez(OUTPUT_DIR / "modal_results.npz", **modal_save)

    # ==================================================================
    # 3. Single climber transit (Part D)
    # ==================================================================
    print("\n" + "=" * 65)
    print("STEP 3: Single Climber Transit")
    print("=" * 65)
    transit = run_single_transit(params, N=args.N, dt=DT, zeta=ZETA_TARGET)

    print(f"\n  Peak longitudinal displacement: {transit['peak_u_km']:.1f} km")
    print(f"  Peak transverse displacement:  {transit['peak_v_km']:.1f} km")
    print(f"  Peak tension perturbation:     {transit['peak_dT_ratio']:.4f}")

    # Save transit results
    np.savez(
        OUTPUT_DIR / "single_climber_results.npz",
        time=transit["time"],
        u_envelope=transit["u_envelope"],
        v_envelope=transit["v_envelope"],
        dT_ratio_envelope=transit["dT_ratio_envelope"],
        u_geo=transit["u_geo"],
        v_geo=transit["v_geo"],
        alt_nodes=transit["alt_nodes"],
        peak_u_km=transit["peak_u_km"],
        peak_v_km=transit["peak_v_km"],
        peak_dT_ratio=transit["peak_dT_ratio"],
    )

    # Generate single-climber figures
    print("\n  Generating figures...")
    plot_all_single(transit)

    # ==================================================================
    # 4. Multi-climber resonance sweep (Part E)
    # ==================================================================
    sweep_results = None
    damp_results = None

    if not args.skip_multi:
        print("\n" + "=" * 65)
        print("STEP 4: Multi-Climber Resonance Sweep")
        print("=" * 65)
        sweep_results = run_resonance_sweep(
            params, N=args.N, dt=DT, zeta=ZETA_TARGET,
            n_workers=args.n_workers,
        )

        print(f"\n  Worst-case resonant separation: {sweep_results['worst_sep_hours']:.0f} h")
        print(f"  Peak transverse at resonance:   "
              f"{sweep_results['peak_v'][np.argmax(sweep_results['peak_v'])]/1e3:.1f} km")

        # Save sweep results
        np.savez(
            OUTPUT_DIR / "resonance_sweep.npz",
            separations=sweep_results["separations"],
            peak_u=sweep_results["peak_u"],
            peak_v=sweep_results["peak_v"],
            peak_dT_ratio=sweep_results["peak_dT_ratio"],
            rms_v_geo=sweep_results["rms_v_geo"],
        )

        # Damping sensitivity at resonance
        print("\n  Damping sensitivity...")
        damp_results = run_damping_sensitivity(
            params, sep_hours=sweep_results["worst_sep_hours"],
            N=args.N, dt=DT,
        )

        np.savez(
            OUTPUT_DIR / "damping_sensitivity.npz",
            zeta_values=damp_results["zeta_values"],
            peak_v=damp_results["peak_v"],
            peak_u=damp_results["peak_u"],
        )

        # Generate multi-climber figures
        print("\n  Generating figures...")
        plot_all_multi(sweep_results, damp_results)

    # ==================================================================
    # 5. Comparison table (Part F)
    # ==================================================================
    print("\n" + "=" * 65)
    print("STEP 5: Comparison Table")
    print("=" * 65)
    if sweep_results is None:
        sweep_results = {"worst_sep_hours": np.nan,
                         "separations": np.array([]),
                         "peak_dT_ratio": np.array([])}
    generate_comparison_table(modal_results, transit, sweep_results,
                              params, output_dir=OUTPUT_DIR)

    # ==================================================================
    # Summary
    # ==================================================================
    elapsed = time.time() - t0
    print("\n" + "=" * 65)
    print(f"COMPLETE — Total time: {elapsed:.1f} s ({elapsed/60:.1f} min)")
    print("=" * 65)
    print(f"  Output directory:  {OUTPUT_DIR}")
    print(f"  Figures directory: {FIGURES_DIR}")
    print(f"  Validation report: {OUTPUT_DIR / 'validation_report.txt'}")
    print(f"  Comparison table:  {OUTPUT_DIR / 'comparison_table.tex'}")


if __name__ == "__main__":
    main()
