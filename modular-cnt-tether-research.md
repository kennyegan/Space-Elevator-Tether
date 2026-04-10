# Research Evidence: modular-cnt-tether

## 1. Numerical Verification of Key Claims

### 1.1 Taper Integral I_geo

**Paper claims:** I_geo = ∫_R^{R+L} |a_net(r)| dr ≈ 4.84 × 10⁷ m²/s²

**Verification:** The value 4.84 × 10⁷ is correct ONLY for the integral from surface to GEO (∫_R^{r_GEO}), NOT from surface to tip (∫_R^{R+L}). The integral from surface to tip gives 6.81 × 10⁷.

**FINDING:** The stated integral bounds are wrong. The paper writes "Integrating Eq. (1) from the surface to the tether tip" but T_r = A(GEO)/A(base), so the relevant integral is surface→GEO. The numerical value is correct; the description is wrong. This is a labeling error, not a calculation error, but it's in a section the paper calls a "first-class finding."

### 1.2 Taper Ratios — All Verified ✓

| Source | T_r (paper) | T_r (calculated) | Match |
|--------|-------------|-------------------|-------|
| Edwards & Westling (σ=100, ρ=1300) | 1.88 | 1.88 | ✓ |
| Pearson (σ=46.5, ρ=2200) | 9.88 | 9.92 | ✓ |
| Aravind (σ=50, ρ=1500) | 4.27 | 4.28 | ✓ |
| This paper optimistic (σ=50, ρ=1300) | 3.52 | 3.53 | ✓ |
| This paper conservative (σ=25, ρ=1300) | 12.40 | 12.45 | ✓ |
| Popescu & Sun low (σ=21.5, ρ=1631) | 39.4 | 39.59 | ✓ |

### 1.3 Wave Speed and Pendulum Period ✓
- c = √(25e9/1300) = 4385.3 m/s ✓
- T₁ = 4 × 10⁸ / 4385.3 / 3600 = 25.3 h ✓

### 1.4 MTTR Wait Time ✓
- Traversal: 10⁸/150 = 6.67×10⁵ s = 185.2 h ✓
- Expected wait: 92.6 h > 72 h ✓ → confirms binding constraint claim

### 1.5 Volume Scaling ✓
- V_ratio = (3.0×1.2×0.004)/(0.050×0.012×0.004) = 6000× ✓
- Scale factor (m=6): 6000^(1/6) = 4.26 ✓
- λ_fullscale = 1.2e-8 × 4.26 = 5.12e-8 ≈ 5.2e-8 ✓

## 2. Code Review

### 2.1 Repository Structure
29 Python scripts found across:
- `simulations/fea/` — taper profile, modal analysis, 2D dynamics (14 files)
- `simulations/monte_carlo/` — joint reliability, Weibull extension (7 files)
- `simulations/cost_model/` — NPV model (1 file)
- `scripts/` — figure merging (1 file)

### 2.2 Key Code Observations

**Hazard model (`hazard_model.py`):** Correctly implements Weibull TTF draws with age-dependent remaining life via cumulative hazard tracking. The `conditional_weibull_remaining` function properly chains through scale changes using accumulated hazard H_accum. Overflow guard at H_CLIP=700 is appropriate.

**Element matrices (`element_matrices.py`):** 
- Mass: consistent formulation ✓
- Elastic: rod EA/L, longitudinal only ✓
- Tension: T/L, transverse only ✓
- Gravity-gradient: longitudinal only (ω² + 2GM/r³), 2-point Gauss quadrature ✓
- Coriolis: skew-symmetric by construction ✓
- **Confirmed omission:** transverse gravity-gradient body force NOT included, as acknowledged in paper

**Joint reliability (`joint_reliability.py`):**
- Loads from centralized `parameters.yaml`
- Arrhenius calibration with 3-zone thermal profile
- Cascade model: 2 adjacent failures → system loss
- Stress-hazard coupling exponent = 4

**Validation (`validate.py`):** 6 automated checks including K positive-definite, 1D recovery, Coriolis skew-symmetry, energy conservation, mesh convergence, joint compliance shift.

### 2.3 Missing Code
- `simulations/repair_infrastructure/run_all.py` is referenced in the paper (§5.5) but NOT found in the repository. Only data outputs exist in `data/processed/phase3_repair/`.
- No `sensitivity_analysis.py` found under `phase1_weibull/` (referenced in §5.2.3).
- The Weibull sweep runner script is not present (only config, hazard_model, merge_results, plot_figures).

## 3. Novelty Assessment

### 3.1 Popescu & Sun (2018) — arXiv:1804.06453
**What they did:** Age-structured stochastic birth-death model for filament bundles with repair. Kevlar-based analysis. Showed high working stress ratios are sustainable with autonomous repair. Used Weibull-distributed creep-rupture.

**What they did NOT do:**
- No system-level integration across segments
- No taper geometry coupling
- No joint efficiency parameterization
- No economics or lifecycle cost
- No dynamics (modal analysis, Coriolis)
- No inspection cadence or detection probability
- No cascade failure model
- No repair depot infrastructure

**Assessment:** Popescu & Sun's bio-inspired repair concept is the closest prior work in spirit, but operates at a fundamentally different level (individual filament bundles vs. system-level joint reliability). The paper's claim of being the first coupled system-level analysis appears justified.

### 3.2 Luo et al. (2022a,b) — Aerospace journal
Referenced as showing 22% stress reduction with 10-100 km segments. Published in MDPI Aerospace. Focus was on stress optimization and stability, not reliability, economics, or dynamics integration.

### 3.3 Gassend (2024) — arXiv:2412.17198
Recent paper on exponential tethers for accelerated deployment. Different focus (deployment strategy vs. modular reliability).

### 3.4 Overall Novelty
The "coupled system-level analysis" claim — integrating taper, reliability, dynamics, economics, and repair infrastructure — appears to be genuinely novel. No prior work combines all five.

## 4. Key Concerns

### 4.1 CRITICAL: Material Gap Understatement
The paper acknowledges σ_u = 50 GPa is "aspirational" but buries the scale of the gap. Current best:
- Lab coupons: 80 GPa (Bai 2018) — centimeter scale
- Continuous fibers: ~5 GPa specific strength (Niu 2025) — kilometer scale
- Required: 50 GPa at ribbon scale (100,000 km)

This is a **10× gap** from the best continuous fiber to the baseline assumption. The paper treats this as a parameter to sweep (30-70 GPa) but the entire Monte Carlo reliability analysis assumes the material problem is solved.

### 4.2 CRITICAL: Activation Energy Q = 1.1 eV Is Assumed, Not Measured
The paper's own sensitivity analysis shows Q dominates everything (~7 orders of magnitude per ±40%). The entire reliability surface is conditional on this assumed value. The paper acknowledges this clearly in §6.4 but the abstract and conclusions need to foreground this more strongly.

### 4.3 MAJOR: No Experimental Validation of Any Kind
- Joint efficiency η_j = 0.95: "notional design target" — no CNT sleeve coupler exists
- Hazard rate model: Arrhenius + Weibull + volume scaling — all assumed
- Weibull modulus m = 6: assumed (Pugno & Ruoff report m ≈ 2.7 for CNT bundles)
- Shear-lap sizing: τ_s = 0.42 × σ_allow assumed
- Damping ζ = 0.01: placeholder

### 4.4 MAJOR: Monolithic Baseline May Be Unfairly Simple
The monolithic comparison uses "simplified annual probability rather than detailed degradation model." If the monolithic model underestimates reliability, the modular advantage is inflated.

### 4.5 MODERATE: Integral Bounds Error in §3.2
As documented in §1.1 above. The taper ratio is A(GEO)/A(base), so the integral is surface→GEO, not surface→tip.

### 4.6 MODERATE: 60% Operational Threshold
The phased-construction revenue advantage — the primary driver of modular NPV superiority — depends on the assumption that the tether is operational at 60% completion via GEO-outward/inward deployment. This is a strong structural assumption that drives the central economic result.

### 4.7 MODERATE: Transverse Gravity-Gradient Omission
Acknowledged in §5.3.2 and §8.5. The paper argues tension-string stiffness dominates 5-50×, but the omission may contribute to the 19% discrepancy in T₁_trans. This is properly flagged as a limitation.

### 4.8 MINOR: Counterweight Mass Sensitivity
600,000 kg from Edwards & Westling. Paper notes ±50% → ±8% in T₁_trans but doesn't sweep this parameter.

### 4.9 MINOR: Parameters File Inconsistency
`parameters.yaml` has `eta_j_baseline: 0.95` but `joint_reliability.py` docstring mentions `(0.97/η_j)⁴` while the paper uses `(0.95/η_j)⁴`. Need to verify which is actually used in the code.

## 5. Strengths

1. **Taper ratio reconciliation** is genuinely useful for the field — a definitive reference table
2. **Comprehensive parameter sweeps** — 12,600 Weibull combinations × 10⁵ trajectories is serious computational work
3. **Self-awareness of limitations** — §8.5 is unusually honest; Q-sensitivity flagged prominently
4. **Code availability** — 29 scripts with centralized parameters
5. **Dual design envelope** approach is pedagogically valuable
6. **Repair infrastructure analysis** — identifying inspection cadence as binding constraint is actionable
7. **Multi-climber resonance design rule** (avoid ±5 h of 35 h) is a concrete engineering contribution
8. **2D Coriolis coupling** — 16% frequency shift is significant and novel for space elevator dynamics

## 6. Sources Consulted

- Paper under review: `paper.md`
- Simulation code: 29 Python scripts in `simulations/`
- Parameters: `data/parameters.yaml`
- Popescu & Sun (2018): arXiv:1804.06453 — full text via alpha_get_paper
- Luo et al. (2022a): https://doi.org/10.3390/aerospace9050278
- Luo et al. (2022b): https://doi.org/10.3390/aerospace9070376
- Bai et al. (2018): https://doi.org/10.1038/s41565-018-0141-z
- Niu et al. (2025): https://doi.org/10.26599/NR.2025.94907584
- Gassend (2024): arXiv:2412.17198
- Bertalan et al. (2014): arXiv:1404.04584
