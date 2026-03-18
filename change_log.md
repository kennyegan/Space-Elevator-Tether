# Change Log

All notable changes to this project, in reverse chronological order.

---

## 2026-03-18 — Repository Skeleton Setup

### Added
- **Directory structure** matching RESEARCH_PLAN.md layout:
  - `simulations/fea/`, `simulations/monte_carlo/`, `simulations/thermal/`, `simulations/cost_model/`
  - `data/raw/`, `data/processed/`
  - `scripts/`, `references/`
  - `paper/sections/`, `paper/figures/`, `paper/tables/`
- **`data/parameters.yaml`** — locked master parameter file with all physical constants, orbital parameters, material properties, design factors, segment/joint specs, Monte Carlo sweep ranges, sensitivity values, and cost model inputs
- **`requirements.txt`** — Python dependencies: numpy, scipy, matplotlib, pandas, pyyaml, h5py
- **`.gitignore`** — Python bytecode, LaTeX build artifacts, large data files (.npz, .h5), IDE files, Jupyter checkpoints
- **`scripts/acta_astronautica.mplstyle`** — Matplotlib publication style: Elsevier double-column width (7.48 in), serif fonts, Wong (2011) colorblind-safe palette, 300 DPI PDF output
- **`simulations/fea/taper_profile.py`** — Starter script with:
  - `load_params()` loading from parameters.yaml
  - `net_acceleration()` for gravity-gradient + centrifugal force
  - `integrate_taper_profile()` using ODE integration of ln(A)
  - `compute_stepped_profile()` placeholder for variable-length segmentation
  - `sigma_u_sensitivity()` sweep over {30, 35, 40, 50, 60, 70} GPa
  - Plotting functions for taper validation and sensitivity figures
- **`simulations/monte_carlo/joint_reliability.py`** — Starter script with:
  - `joint_hazard_rate()` implementing λ_j(T) = λ_0 · exp(−Q/(k_B·T)) · (0.97/η_j)⁴
  - `thermal_profile()` placeholder for temperature along tether
  - `simulate_trajectory()` placeholder for single 10-year trajectory
  - `run_sweep()` over N × η_j × inspection cadence parameter space
  - Plotting: P_sys heatmap, MTTR distribution, inspection cadence
- **`references/main.bib`** — Empty BibTeX database with header comment
- **`context.md`** — Project context reference document
- **`change_log.md`** — This file

### Notes
- Both simulation scripts are skeletons with TODO markers where core logic needs implementation
- Taper ratio blocker (τ ≈ 1.6 vs. τ ≈ 12.4) must be resolved before running simulations (see RESEARCH_PLAN.md)
