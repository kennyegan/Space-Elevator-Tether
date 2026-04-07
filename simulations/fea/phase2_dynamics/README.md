# Phase 2: 2D Coriolis-Coupled Dynamic Model

Finite element model for longitudinal and transverse tether dynamics in the rotating (Earth-fixed) reference frame, including Coriolis coupling, spatially varying tension, and gravity-gradient restoring forces.

## Model Description

- **DOFs**: 500 nodes x 2 (longitudinal u + transverse v) = 1000 total, 998 after fixed-base BC
- **Elements**: 2-node bar/string elements with consistent mass matrices
- **Stiffness**: EA/L (elastic, longitudinal) + T/L (tension, transverse) + gravity-gradient body force
- **Coriolis**: Skew-symmetric gyroscopic matrix coupling u_dot and v_dot
- **Damping**: Rayleigh (alpha_M * M + alpha_K * K), targeting zeta=0.01 at first two modes
- **Time integration**: Newmark-beta (average acceleration, unconditionally stable)
- **Mesh**: Non-uniform spacing with Gaussian refinement near GEO

## Usage

```bash
# Full pipeline (validation + modal + single climber + multi-climber sweep)
python simulations/fea/phase2_dynamics/run_all.py

# Validation only
python simulations/fea/phase2_dynamics/run_all.py --validate-only

# Skip multi-climber sweep (faster)
python simulations/fea/phase2_dynamics/run_all.py --skip-multi
```

## Output

- `data/processed/phase2_dynamics/` — numerical results (.npz, .csv)
- `paper/figures/` — 9 publication-quality PDF figures
- `data/processed/phase2_dynamics/comparison_table.tex` — LaTeX table
- `data/processed/phase2_dynamics/validation_report.txt` — validation results

## Validation Checks

1. K_total positive definite (stable equilibrium)
2. 1D recovery (T1 matches existing discrete model within 5%)
3. Coriolis matrix skew-symmetry (G + G^T = 0)
4. Energy conservation (undamped, <0.1% drift over 100h)
5. Mesh convergence (251 vs 501 nodes, <5% difference)
6. Joint compliance shift (~2.3%, matching 1D result)

## Dependencies

Python 3.10+, numpy, scipy, matplotlib, pyyaml
