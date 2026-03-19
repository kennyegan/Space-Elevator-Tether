# Change Log

All notable changes to this project, in reverse chronological order.

---

## 2026-03-18 — Final Simulation Fixes + paper.md (Fixes A–D)

### Fix A — Taper dual design envelope
- Added `--taper-stress {sigma_u, sigma_allow, both}` flag to `taper_profile.py`
- Sensitivity sweep runs at BOTH stress levels: σ_u (optimistic, Edwards & Westling approach) and σ_allow (conservative)
- New figure `fig_design_envelope_comparison.pdf`: 2×2 grid comparing both envelopes
- Saves `sigma_u_sensitivity_optimistic.json` and `sigma_u_sensitivity_conservative.json`
- Key finding: N ≈ 18 only at σ_u tapering; σ_allow gives N ≈ 505

### Fix B — Monte Carlo wider parameter sweep
- Extended YAML sweep ranges: N ∈ {12..500}, η_j ∈ {0.70..0.97}, p_det ∈ {0.50..0.995}
- Total combinations: 2,268 (was 400)
- Heatmap plotting handles non-uniform N spacing and 9×9 grid
- N=500 tests cascade dynamics at scale

### Fix C — Modal analysis restructured
- Analytical solution (T₁ = 25.3 h) presented as primary result
- 500-node discrete model (was 18) for joint compliance comparison
- Runs with and without joint compliance: reports frequency shift %
- Forced response includes geometric stiffness in K matrix

### Fix D — paper.md research document
- Created `paper.md` at project root: full research paper in markdown
- Structured as Acta Astronautica submission: Abstract, §1–10, References, Figure Index
- All quantitative claims reference specific simulation outputs
- [RUN_VALUE] placeholders for numbers requiring final simulation runs
- Includes: dual design envelope finding, cascade model, phased construction advantage

---

## 2026-03-18 — Publication-Quality Physics Fixes (Fixes 1–5)

### Root Causes Fixed
1. **Taper integration sign** — missing negative sign in d(ln A)/dr corrected in prior pass
2. **Arrhenius double-counting** — λ̄=1.2e-8/h is mission-averaged (§4.2.3), NOT the pre-exponential. Old code applied Arrhenius twice → rates of ~10⁻²⁸/h → zero failures. Now derives true λ_0_pre from mission-averaged value.
3. **Missing geometric stiffness** — modal analysis only had material EA/L. Added gravity-gradient k_geo = T/L which dominates.

### Changed — `data/parameters.yaml`
- `joints.lambda_0` → 5.2e-8 (full-scale, Weibull volume-scaled from coupons)
- Added: `lambda_0_bar`, `T_ref`, `weibull_modulus`, `volume_ratio`, `volume_scale_factor`, `ts_sleeve`, `tau_shear_fraction`
- Added: `climber.m_counterweight: 600000.0` (Edwards & Westling estimate)
- Added: `monte_carlo.p_detection_sweep: [0.90, 0.95, 0.99, 0.995]`
- Added: `cost.construction_cadence: 12`

### Changed — `simulations/fea/taper_profile.py` (Fix 1)
- `compute_stepped_profile()`: A_base from payload requirement (m_climber × g / σ_design ≈ 7.8 mm²), mass-equalization walk determines N from physics, no hardcoded L_MIN/L_MAX
- `sigma_u_sensitivity()`: recomputes A_base at each σ_u, reports real N, M_total, feasibility
- `plot_sigma_sensitivity()`: 2×2 grid (τ, N, M_total, m_j_max vs σ_u) with 30t launch cap line

### Changed — `simulations/monte_carlo/joint_reliability.py` (Fix 2)
- **Arrhenius calibration**: derives λ_0_pre from mission-averaged λ̄ weighted by joint count per thermal zone (not tether length). Self-consistency check printed at startup.
- **Weibull volume scaling**: coupon-to-sleeve scaling factor 4.3 (m=6, V_ratio=6000) physically derived
- **Cascading failure model**: load redistribution to neighbors via shear-lap Eq. 11, cascade threshold at σ > σ_allow, stress-life exponent (σ/σ_nom)⁴, two adjacent failures = instant system failure
- **4D sweep**: N × η_j × cadence × p_detection (400 combos vs previous 100)
- **GPU support**: `--gpu` flag for CuPy vectorization, falls back to NumPy

### Changed — `simulations/fea/modal_analysis.py` (Fix 3)
- Added geometric stiffness: k_j = k_material + k_geo, where k_geo = σ_design × A_j / L_j
- Counterweight: 600,000 kg (was using 20,000 kg climber mass)
- A_base from payload requirement (~7.8 mm²)
- Analytical comparison uses correct average tension
- Simplification acknowledgment printed (no Coriolis, no variable tension along modes)

### Changed — `simulations/cost_model/npv_model.py` (Fix 4)
- Loads Monte Carlo P_sys data for physics-based failure rates (falls back to analytical)
- **Phased construction revenue ramp**: modular earns partial revenue during build (60% completion threshold), monolithic earns nothing until 100% complete
- Construction spending spread over build period
- Consistent with taper mass data

---

## 2026-03-18 — Core Simulation Implementation (Tasks 1–5)

### Added
- **`simulations/fea/taper_ratio_investigation.py`** (Task 1 — NEW)
  - Loads all constants from parameters.yaml with float casting
  - Computes taper ratio τ at σ_u=50 GPa, σ_allow=25 GPa, and σ_allow_net=20.2 GPa
  - Prints comparison table with specific strength in MYuri
  - Includes sensitivity sweep across all σ_u values
  - Resolves the τ ≈ 1.6 vs τ ≈ 12.4 discrepancy (draft likely used σ_u not σ_allow)

- **`simulations/cost_model/npv_model.py`** (Task 4 — NEW)
  - 30-year NPV for modular (construction + ops + repair) vs monolithic (construction + ops + P_fail×rebuild)
  - Triple sweep: launch cost {500,1000,1500,2000} $/kg × discount rate {5,7,10}% × revenue {200,300,500} $/kg
  - Cost assumptions derived from physical parameters (tether mass, climber fleet, repair events)
  - Crossover year detection (when modular NPV exceeds monolithic)
  - Plots: NPV crossover time series + sensitivity panel, cost tornado diagram
  - Saves to data/processed/npv_results.npz

- **`simulations/fea/modal_analysis.py`** (Task 5 — NEW)
  - Assembles K and M sparse matrices for N-segment lumped-mass-spring chain
  - Spring stiffness: k_j = η_j · E · A_j / L_j
  - Eigenvalue solve via scipy.sparse.linalg.eigsh for first 20 modes
  - Continuous-string analytical frequency comparison (fixed-free)
  - Forced response: quasi-static displacement from 20 t climber at 150 m/s
  - Climber separation rule verification (12 Mm minimum)
  - Saves to data/processed/modal_results.npz

### Modified
- **`simulations/fea/taper_profile.py`** (Task 2 — COMPLETE REWRITE)
  - Filled all TODOs with working implementations
  - Tension T(r) computed via cumulative trapezoid integration of ρ·A(r)·a_net(r)
  - Force-balance consistency check (T_force_balance vs uniform-stress T)
  - Stress σ(r) = T(r)/A(r) with uniformity verification
  - Stepped profile: variable-length segments with mass equalization, L_j clamped to [10 km, 50 km]
  - A_base estimated from total mass budget (N × m_star)
  - σ_u sensitivity sweep computes τ, M_total, N_segments, m_j_max, feasibility flag
  - Plotting: taper validation (A(r) + T(r) with stepped overlay), sensitivity (dual-axis τ + M_total)
  - argparse CLI: `--mode {baseline, sensitivity, all}`
  - Saves taper_profiles.npz and sigma_u_sensitivity.json

- **`simulations/monte_carlo/joint_reliability.py`** (Task 3 — COMPLETE REWRITE)
  - Filled all TODOs with working implementations
  - 3-zone thermal profile: 250K (<200km), 280K (200km–GEO), 300K (>GEO)
  - Full trajectory simulation: exponential TTF per joint, inspection epochs, detection with p=0.995
  - Repair time = wait_for_inspection + travel_distance/v_climber + 1.4h replacement
  - Undetected failure → system failure (cascade risk model)
  - Batch runner with per-combination seeding for reproducibility
  - Full parameter sweep: N × η_j × cadence with progress reporting
  - Plotting: P_sys heatmap with contour lines + baseline annotation, MTTR histogram with 72h target, availability vs cadence
  - argparse CLI: `--n-trajectories` (1000 for quick test, 100000 for full), `--single` for baseline-only
  - Saves psys_surface.npz and mttr_samples.npz

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
