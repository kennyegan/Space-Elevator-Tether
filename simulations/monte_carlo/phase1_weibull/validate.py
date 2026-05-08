"""
validate.py — 5 validation checks for the Weibull Monte Carlo engine.

Run before submitting SLURM jobs:
    cd ~/Space-Elevator-Tether
    python -m simulations.monte_carlo.phase1_weibull.validate

Checks:
  1. β=1 consistency with existing exponential code (same seed)
  2. Baseline sanity: β=1.0, N=18, η_j=0.95 → P_sys > 0.999
  3. β monotonicity at high-failure configuration
  4. η_j monotonicity: increasing η_j increases P_sys
  5. Analytical single-joint at β=1.0, 2.0, 2.5
"""

import sys
import time
from pathlib import Path

import numpy as np

from simulations.monte_carlo.phase1_weibull.config import (
    RESULTS_DIR,
    combo_seed,
)
from simulations.monte_carlo.phase1_weibull.hazard_model import (
    calibrate_arrhenius,
    draw_weibull_ttf,
    load_params,
    compute_hazard_rates,
    compute_joint_positions,
    thermal_profile_3zone,
)
from simulations.monte_carlo.phase1_weibull.simulate import run_batch_weibull

# Also import exponential code for cross-validation
from simulations.monte_carlo.joint_reliability import (
    run_batch_vectorized as run_batch_exponential,
)


def _header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def _result(name, passed, detail=""):
    tag = "PASS" if passed else "FAIL"
    print(f"  [{tag}] {name}")
    if detail:
        print(f"         {detail}")
    return passed


def run_validation(n_traj: int = 100_000):
    """Run all 5 validation checks. Returns True if all pass."""
    params = load_params()
    lambda_0_pre = calibrate_arrhenius(params)

    results = []
    report_lines = []

    def record(name, passed, detail=""):
        ok = _result(name, passed, detail)
        results.append(ok)
        tag = "PASS" if ok else "FAIL"
        report_lines.append(f"[{tag}] {name}: {detail}")

    # ------------------------------------------------------------------
    # Check 1: β=1 consistency with existing exponential
    # ------------------------------------------------------------------
    _header("Check 1: β=1 consistency with exponential code")
    N, eta_j, cad, pdet = 18, 0.95, 1, 0.995
    seed = combo_seed(N, eta_j, cad, pdet, 1.0)

    t0 = time.time()
    wb = run_batch_weibull(N, eta_j, cad, pdet, lambda_0_pre,
                           params, n_traj, beta=1.0, seed=seed)
    t1 = time.time()
    print(f"  Weibull β=1:  P_sys={wb['P_sys']:.5f}  ({t1-t0:.1f}s)")

    # Run existing exponential with same seed
    t0 = time.time()
    exp = run_batch_exponential(N, eta_j, cad, pdet, lambda_0_pre,
                                params, n_traj, seed=seed)
    t1 = time.time()
    print(f"  Exponential:  P_sys={exp['P_sys']:.5f}  ({t1-t0:.1f}s)")

    diff = abs(wb["P_sys"] - exp["P_sys"])
    record("β=1 matches exponential",
           diff <= 0.001,
           f"ΔP_sys = {diff:.5f} (tolerance ±0.001)")

    # ------------------------------------------------------------------
    # Check 2: Baseline sanity — P_sys > 0.999 at β=1.0
    # ------------------------------------------------------------------
    _header("Check 2: Baseline sanity (β=1.0 → P_sys > 0.999)")
    record("Baseline P_sys > 0.999",
           wb["P_sys"] > 0.999,
           f"P_sys = {wb['P_sys']:.5f}")

    # ------------------------------------------------------------------
    # Check 3: β monotonicity at high-failure configuration
    # ------------------------------------------------------------------
    _header("Check 3: β monotonicity (N=100, η_j=0.80)")
    # At baseline (N=18, η_j=0.95), λt << 1 so higher β REDUCES P_fail
    # (Weibull defers failures past the mission). Use a configuration
    # with enough failures that wear-out dominates, but not so large
    # that cascade simulation is prohibitively slow for validation.
    N_mono, eta_mono, cad_mono, pdet_mono = 100, 0.80, 1, 0.995
    betas = [1.0, 1.3, 1.5, 2.0, 2.5]
    psys_by_beta = []
    for beta in betas:
        seed_b = combo_seed(N_mono, eta_mono, cad_mono, pdet_mono, beta)
        r = run_batch_weibull(N_mono, eta_mono, cad_mono, pdet_mono,
                              lambda_0_pre, params, n_traj,
                              beta=beta, seed=seed_b)
        psys_by_beta.append(r["P_sys"])
        print(f"  β={beta:.1f}:  P_sys={r['P_sys']:.5f}")

    # Check non-increasing trend (allow ties from rounding at P_sys ≈ 1 or 0)
    monotonic = all(psys_by_beta[i] >= psys_by_beta[i+1] - 0.002
                    for i in range(len(psys_by_beta)-1))
    record("P_sys non-increasing in β (within noise)",
           monotonic,
           f"P_sys = {[f'{p:.5f}' for p in psys_by_beta]}")

    # ------------------------------------------------------------------
    # Check 4: η_j monotonicity (increasing η_j → increasing P_sys)
    # ------------------------------------------------------------------
    _header("Check 4: η_j monotonicity (at β=1.5)")
    beta_test = 1.5
    etas = [0.80, 0.85, 0.90, 0.95, 0.97]
    psys_by_eta = []
    for eta in etas:
        seed_e = combo_seed(N, eta, cad, pdet, beta_test)
        r = run_batch_weibull(N, eta, cad, pdet, lambda_0_pre,
                              params, n_traj, beta=beta_test, seed=seed_e)
        psys_by_eta.append(r["P_sys"])
        print(f"  η_j={eta:.2f}:  P_sys={r['P_sys']:.5f}")

    monotonic_eta = all(psys_by_eta[i] <= psys_by_eta[i+1] + 0.002
                        for i in range(len(psys_by_eta)-1))
    record("P_sys non-decreasing in η_j (within noise)",
           monotonic_eta,
           f"P_sys = {[f'{p:.5f}' for p in psys_by_eta]}")

    # ------------------------------------------------------------------
    # Check 5: Analytical single-joint (N=2, no inspection)
    # ------------------------------------------------------------------
    _header("Check 5: Analytical single-joint (N=2, cadence→∞)")
    # With N=2, there's 1 joint. Set cadence very high so no inspections
    # occur during the mission. No cascade possible (single joint).
    # P_fail = 1 - exp(-(t_mission * λ)^β)  for Weibull

    N_test = 2
    eta_test = 0.95
    pdet_test = 0.0   # zero detection → no repair → pure survival test
    cad_test = 1      # cadence irrelevant with p_det=0

    joint_alts = compute_joint_positions(N_test, params)
    joint_temps = thermal_profile_3zone(joint_alts)
    hazard = compute_hazard_rates(eta_test, joint_temps, lambda_0_pre, params)
    lam = float(hazard[0])
    t_mission = float(params["monte_carlo"]["t_mission"])
    scale = 1.0 / lam

    print(f"  λ_j = {lam:.6e} 1/h")
    print(f"  scale (1/λ) = {scale:.6e} h")
    print(f"  λ*t_mission = {lam * t_mission:.6f}")

    # --- Direct draw test: verify distribution matches theory ---
    _header("Check 5a: Direct distribution test")
    rng_test = np.random.default_rng(seed=12345)
    draws = draw_weibull_ttf(1.0, np.array([scale]), rng_test,
                             size=(n_traj, 1)).flatten()
    frac_fail = np.mean(draws < t_mission)
    expected_fail = 1.0 - np.exp(-lam * t_mission)
    print(f"  Direct draw test (β=1.0, {n_traj} draws):")
    print(f"    Fraction < t_mission: {frac_fail:.6f}")
    print(f"    Analytical expected:  {expected_fail:.6f}")
    print(f"    Draw mean: {np.mean(draws):.2e} (expected: {scale:.2e})")
    print(f"    Draw min:  {np.min(draws):.2e}")
    direct_ok = abs(frac_fail - expected_fail) < 3 * np.sqrt(
        expected_fail * (1 - expected_fail) / n_traj) + 0.002
    record("Direct Weibull draw matches analytical CDF",
           direct_ok,
           f"draw_frac={frac_fail:.6f}, expected={expected_fail:.6f}")

    # --- Targeted diagnostic: manually trace run_batch_weibull logic ---
    # (Diagnostic section removed — root cause identified: t_traversal ≈ 185h
    # not 185,185h. Previous test used p_det=0.995 which allowed repairs.
    # Now using p_det=0.0 to disable repair for pure analytical comparison.)

    # --- MC simulation test ---
    _header("Check 5c: Full MC simulation vs analytical")
    for beta_a in [1.0, 2.0, 2.5]:
        P_fail_analytical = 1.0 - np.exp(-(t_mission * lam) ** beta_a)
        P_sys_analytical = 1.0 - P_fail_analytical

        seed_a = combo_seed(N_test, eta_test, cad_test, pdet_test, beta_a)
        r = run_batch_weibull(N_test, eta_test, cad_test, pdet_test,
                              lambda_0_pre, params, n_traj,
                              beta=beta_a, seed=seed_a)

        # Print diagnostics
        print(f"  β={beta_a:.1f}: MC P_sys={r['P_sys']:.5f}, "
              f"analytical={P_sys_analytical:.5f}, "
              f"failures={r['n_failures']}/{n_traj}")

        diff_a = abs(r["P_sys"] - P_sys_analytical)
        P_a = P_sys_analytical
        tol = 3.0 * np.sqrt(P_a * (1 - P_a) / n_traj) if P_a < 1 else 0.005
        tol = max(tol, 0.003)

        passed_a = diff_a <= tol
        record(f"Analytical β={beta_a:.1f}",
               passed_a,
               f"MC={r['P_sys']:.5f}, analytical={P_sys_analytical:.5f}, "
               f"Δ={diff_a:.5f}, tol={tol:.5f}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _header("VALIDATION SUMMARY")
    n_pass = sum(results)
    n_total = len(results)
    all_pass = n_pass == n_total
    print(f"  {n_pass}/{n_total} checks passed")
    if all_pass:
        print("  ✓ ALL CHECKS PASSED — safe to submit SLURM jobs")
    else:
        print("  ✗ SOME CHECKS FAILED — investigate before proceeding")

    # Save report
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_DIR / "validation_report.txt"
    with open(report_path, "w") as f:
        f.write("Weibull Monte Carlo Validation Report\n")
        f.write(f"Trajectories per check: {n_traj}\n")
        f.write(f"{'='*50}\n")
        for line in report_lines:
            f.write(line + "\n")
        f.write(f"{'='*50}\n")
        f.write(f"Result: {n_pass}/{n_total} PASSED\n")
    print(f"\n  Report saved: {report_path}")

    return all_pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate Weibull MC engine")
    parser.add_argument("--n-trajectories", type=int, default=100_000,
                        help="Trajectories per check (default 100K)")
    args = parser.parse_args()

    ok = run_validation(n_traj=args.n_trajectories)
    sys.exit(0 if ok else 1)
