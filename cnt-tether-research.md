# Peer Review Research: "Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment"
**Egan & Ergezer — Acta Astronautica target**
**Reviewer research compiled:** 2026-04-10

---

## Task 1 — Taper Formula Verification

### 1a. Numerical Computation of I_geo

Using the locked constants from `data/parameters.yaml`:
- R = 6.3781 × 10⁶ m, r_GEO = 4.21642 × 10⁷ m, ω = 7.2921159 × 10⁻⁵ rad/s, GM = 3.986004418 × 10¹⁴ m³/s²

Analytical closed form (below-GEO only, where |a_net| = GM/r² − ω²r):

```
I_geo = (GM/R − GM/r_GEO) − ω²(r_GEO² − R²)/2
       = (6.2495e7 − 9.4530e6) − 5.3175e-9 × (1.7378e15)/2
       = 5.3042e7 − 4.6192e6
       = 4.8423 × 10⁷ m²/s²
```

Numerical trapezoid integration with 100,000 intervals gives the same value: **4.8423 × 10⁷ m²/s²**.

**Result:** Paper claims I_geo ≈ 4.84 × 10⁷ m²/s². Confirmed to 0.05% accuracy. ✓

> Note: the formula integrates only from R to r_GEO (below GEO, where |a_net| = GM/r² − ω²r). The above-GEO integral is omitted by convention since T_r = A(GEO)/A(base) involves only the below-GEO cumulation. This is correct.

### 1b. Reconciliation Table Spot-Checks

Three rows verified against ln(T_r) = ρ × I_geo / σ_design using computed I_geo = 4.8423 × 10⁷:

| Source | ρ [kg/m³] | σ_design [Pa] | T_r (calculated here) | T_r (paper) | Δ |
|--------|-----------|---------------|----------------------|-------------|---|
| Edwards & Westling (2003) | 1300 | 100e9 | **1.877** | 1.88 | 0.18% ✓ |
| Aravind (2007) | 1500 | 50e9 | **4.275** | 4.27 | 0.11% ✓ |
| Pearson (1975) | 2200 | 46.5e9 | **9.885** | 9.88 | 0.05% ✓ |
| This paper (conservative) | 1300 | 25e9 | **12.404** | 12.40 | 0.03% ✓ |
| Popescu & Sun (2018) last row | 1631 | 21.5e9 | **39.385** | 39.4 | 0.04% ✓ |

All five rows pass within rounding. The formula is arithmetically self-consistent.

### 1c. Residual Discrepancy Flag

The paper states: *"Every published ratio is recoverable from ln(T_r) = ρ × I_geo / σ_design with **no residual discrepancy**."*

However, the table itself shows:

| Popescu & Sun (2018) last row | T_r (published) = **36.9** | T_r (calculated) = **39.4** |

The gap between the *published* value (36.9) and the formula-derived value (39.4) is **6.8%** — a meaningful residual discrepancy the paper does not explain. The formula reproduces the *paper's own calculated column* but not the original published value. The claim of "no residual discrepancy" should be qualified: the formula reproduces the *authors' calculated column*, but the Popescu & Sun published value of 36.9 remains 6.8% below the formula prediction at the stated inputs. This either means Popescu & Sun used slightly different inputs (undisclosed), or the formula does not fully account for their methodology. **This should be noted in the manuscript.**

---

## Task 2 — Code Parameter Consistency

### 2a. Table 4.1 vs `data/parameters.yaml`

All baseline parameters from Table 4.1 match `data/parameters.yaml` exactly:

| Parameter | Table 4.1 | parameters.yaml | Match |
|-----------|-----------|-----------------|-------|
| L_total | 100,000 km | 1.0e8 m | ✓ |
| ρ | 1,300 kg/m³ | 1300.0 | ✓ |
| σ_u (baseline) | 50 GPa | 50.0e9 Pa | ✓ |
| SF | 2.0 | 2.0 | ✓ |
| η_j (baseline) | 0.95 | 0.95 | ✓ |
| m★ | 18,000 kg | 18000.0 | ✓ |
| m_launch_cap | 30,000 kg | 30000.0 | ✓ |
| m_climber | 20,000 kg | 20000.0 | ✓ |
| v_climber | 150 m/s | 150.0 | ✓ |
| m_counterweight | 600,000 kg | 600000.0 | ✓ |

### 2b. Weibull MC Config (`simulations/monte_carlo/phase1_weibull/config.py`)

- **N_SWEEP** = [12, 15, 18, 21, 24, 50, **83**, 100, 200, 500] — N=83 correctly present ✓
- **BETA_SWEEP** = [1.0, 1.3, 1.5, 2.0, 2.5] ✓
- **TOTAL_COMBOS** = 10 × 9 × 4 × 7 × 5 = **12,600** ✓
- Exponential baseline in yaml: `N_sweep: [12, 15, 18, 21, 24, 50, 100, 200, 500]` — N=83 absent ✓ (consistent with §5.2.1 note)

### 2c. NPV Model (`simulations/cost_model/npv_model.py`) — **SIGNIFICANT BUG**

The `build_cost_assumptions()` function reads:
```python
N = N_override if N_override is not None else int(params["segments"]["N_baseline"])
```
`parameters.yaml` sets `N_baseline: 18`. Therefore, the main `run_sweep()` call (with no override) uses **N=18**, giving:
- `years_to_build = 18 / 12 = 1.5 years`
- Revenue starts at ~year 0.9

But **§7 discusses N=83 throughout**:
- Table 7.1: "Tether mass (optimistic, N=83): 1,502 t"
- "Years to build: ~7 (83 segments / 12 per year)"

The `sweep_p_fail_mono()` and `sweep_f_threshold()` functions (§7.5) do pass `N_override=83`, but the *main NPV comparison* in `run_sweep()` runs at N=18. This means the build cost, revenue timeline, and NPV curves shown in the paper's **Fig. 14** and Table 7.1 are inconsistent with the underlying code: the code defaults to a 1.5-year build while the paper claims a 7-year build. **This is a significant code-paper inconsistency that affects the NPV results.** The `N_baseline` in `parameters.yaml` should be updated to 83 (or `run_sweep()` should receive an explicit override).

Also: the `get_mc_failure_rates()` function hardcodes `n_idx = list.index(18)` — it extracts reliability data at N=18 from the MC grid, not N=83. Since N=83 is not in the exponential MC grid (only in the Weibull extension), the MC-linked P_fail estimate used by the NPV model is for a different configuration than the one described in §7.

### 2d. FEA Phase 2 Config (`simulations/fea/phase2_dynamics/config.py`)

- Reads parameters via `load_params()` from `data/parameters.yaml` — single source of truth ✓
- `sigma_design` → `params["design"]["sigma_allow"]` = 25 GPa (conservative) ✓
- `N_NODES = 500`, `ZETA_TARGET = 0.01`, `DT = 500 s` — consistent with §5.3.2 ✓

### 2e. Volume Scale Factor Minor Inconsistency

```
6000^(1/6) = 4.2628   (exact)
parameters.yaml:  volume_scale_factor: 4.3   (rounded)
→ lambda_0 = 1.2e-8 × 4.3 = 5.16e-8   (yaml value: 5.2e-8, inconsistent with 5.16)
```
Three-way inconsistency: calculated = 5.115e-8, yaml `lambda_0` = 5.2e-8, Q-table at Q=1.1 eV = 5.293e-8. The Q-table value is ~3.6% higher than `lambda_0` in yaml and ~4.8% above the calculated value. Minor, but the pre-exponential λ_0_pre calibration might be absorbing part of this via the Arrhenius calibration loop. Worth clarifying in the paper's Methods section (or checking whether the calibration reruns are correct).

### 2f. Taper Profile Script (`simulations/fea/taper_profile.py`)

Integrates `d(ln A)/dr = −(ρ/σ) × a_net(r)` at 100,001 points, A_base from payload requirement — consistent with paper's §5.1 description ✓. Uses `GM/R²` for g_surface (= 9.798 m/s²), while the paper states `g = 9.81 m/s²` in the A_base formula. This gives a 0.12% difference in A_base:
- Code: A_base = 20000 × 9.798 / 25e9 = **7.838e-6 m²**
- Paper text: A_base = 20000 × 9.81 / 25e9 = **7.848e-6 m²** (= 7.85 × 10⁻⁶ m²)

Trivially small but technically inconsistent.

---

## Task 3 — Data Spot-Checks

### 3a. Weibull Sweep Results — §6.4 Claim Check

**Target row:** N=83, η_j=0.95, cadence=1, p_det=0.995, β=1.0

From `data/processed/weibull_sweep_results.csv`:
```
83,0.950000,1,0.995000,1.000000,0.999950,0.414560,217.879486,...
```

- **P_sys = 0.999950 = 0.99995** ✓ — matches §6.4 claim exactly
- Mean repairs = 0.41456 (paper Table §6.4: "0.41") ✓
- Median MTTR = 217.9 h (paper §6.6 says "median MTTR ~218 h at cadence=1") ✓

### 3b. Q Hazard Rate Table

From `data/processed/Q_hazard_rate_table.csv`:

| Q [eV] | λ_full [h⁻¹] | p_fail_10yr | Paper claim | Match |
|--------|--------------|-------------|-------------|-------|
| 0.8 | 5.991e-3 | 1.0 (all fail) | "~6 × 10⁻³ h⁻¹", P_sys=0 | ✓ |
| 1.1 | 5.293e-8 | 4.626e-3 | "baseline" | ✓ (≈5.2e-8) |
| 1.4 | 4.760e-13 | ~4.2e-8 | "effectively zero" | ✓ |

- Ratio Q=0.8 to Q=1.4: 5.991e-3 / 4.760e-13 = **1.26 × 10¹⁰** — paper claims "10 orders of magnitude" ✓ (rounded from log₁₀(1.26e10) = 10.1)
- p_fail_10yr at Q=0.8: 1.0 confirms P_sys = 0 claim ✓
- Minor: λ_full at Q=1.1 eV = 5.293e-8, slightly above yaml `lambda_0 = 5.2e-8`. Consistent with the Arrhenius formula using the exact Q/kT vs. the volume-scaled approximation.

### 3c. Phase 2 Dynamics Comparison Table

From `data/processed/phase2_dynamics/comparison_table.csv`:

```
T_1 analytical [h],    25.3,  ---,   ---,   ---
T_1 transverse (2D) [h], N/A, 30.04, 34.80, 15.9%
T_1 longitudinal [h],   8.60, 10.22, 10.46, 21.6%
Joint shift (eta_j 1.0to0.95), 2.3%, 0.0%, ---, ---
```

The paper's modal results table in §6.6 states:

| Property | No Coriolis | With Coriolis | Shift |
|----------|-------------|---------------|-------|
| T₁ transverse [h] | 30.0 | 34.8 | +16% |
| T₂ transverse [h] | 10.2 | 10.5 | +2.5% |
| T₁ longitudinal [h] | **7.65** | **7.12** | **−7%** |

**MAJOR DISCREPANCY — T₁ longitudinal:**

The paper reports T₁_long = 7.65 h (No Coriolis) and 7.12 h (With Coriolis, −7% shift), but the comparison CSV shows:
- 2D No Coriolis: **10.22 h**
- 2D With Coriolis: **10.46 h** (+21.6%, not −7%)
- 1D: **8.60 h** (paper's "T₁_elastic ≈ 7.7 h" also doesn't match)

The paper's longitudinal modal periods are inconsistent with the CSV data file by factors of 1.34–1.47×. The sign of the Coriolis shift is also reversed: CSV shows the 2D longitudinal frequency *decreases* (period increases from 10.22→10.46, +21.6%) while the paper claims it *increases* (7.65→7.12, −7%). **This is a significant internal inconsistency between the paper text and the data file.** Either the paper table was populated from an earlier code version that produced different results, or there is a labeling error (the paper may have the "transverse" T₂ and "longitudinal" T₁ swapped — note that T₂ transverse = 10.2 h from the paper is close to the CSV's T₁ longitudinal 2D No Coriolis = 10.22 h).

Additionally, the CSV shows joint compliance shift for **1D = 2.3%** but **2D No Coriolis = 0.0%**, yet §5.3.2 states "Joint compliance shift (2.44% vs 1D's 2.32%)." The 2D joint compliance shift of 2.44% is not reflected in the CSV.

**Transverse modes are consistent:**
- T₁ trans: paper 30.0 h vs CSV 30.04 h ✓ (rounding)
- Coriolis shift: paper 16%, CSV 15.9% ✓ (rounding)
- T₂ trans: paper 10.2 h — plausible given CSV context

### 3d. Figure Count

**Declared:** 18 main + 19 supplementary = **37 figures**  
**Actual PDFs in `paper/figures/`:** **41 files**

All 37 declared figures are present ✓. Four **orphan figures** exist but are not listed in the Figure Index and are not referenced in the text:
1. `fig_depot_cost_tradespace.pdf` — appears to be an alternate depot cost plot
2. `fig_npv_crossover.pdf` — generated by `npv_model.py` but superseded by `fig_npv_merged.pdf`
3. `fig_npv_with_depots.pdf` — unlisted version of NPV+depot comparison
4. `fig_weibull_mttr_depot_shift.pdf` — appears to be an unmerged version of Fig. S7

These are likely intermediate outputs left over from figure consolidation. They do not constitute an error in the declared count, but should be removed from the submission archive to avoid confusion.

---

## Task 4 — Literature Verification

### 4a. Bai et al. 2018 — "80 GPa tensile strength for CNT bundles"

**CONFIRMED.** Paper title: *"Carbon nanotube bundles with tensile strength over 80 GPa"*, Nature Nanotechnology 13, 589–595 (2018), DOI: 10.1038/s41565-018-0141-z. The paper is explicitly titled with this claim. The Egan/Ergezer characterization ("80 GPa on centimeter gauges") is accurate. ✓

### 4b. Luo et al. 2022a — "22% stress reduction with segmentation"

**MISCHARACTERIZED — SIGNIFICANT ERROR.**

The Egan/Ergezer paper states: *"Luo et al. (2022a) quantified a **22% stress reduction with 10–100 km segments joined by sleeve couplers**."*

The actual Luo et al. 2022a paper (*Model and Optimization of the Tether for a Segmented Space Elevator*, Aerospace 9(5), 278) reports:

- Peak stress of **63 GPa** for uniform-cross-section (1 segment)
- With **5–6 optimal segments** (not 10–100 km length segments): peak stress ≈ **27.69–32.73 GPa**
- Reduction vs uniform section: **56%** peak stress lower (from conclusion: *"the peak stress is 56% lower than that of the constant section space elevator model"*)
- The 22% figure **does not appear anywhere** in Luo et al. 2022a
- There is **no mention of "sleeve couplers"** — the paper uses "connecting platforms"
- Segment lengths are not described as "10–100 km" — the segment points are at altitudes of 7,000–21,000 km
- The Luo et al. methodology is stress optimization by varying segment positions and cross-sectional area ratios, not the mass-equalized segmentation used in Egan/Ergezer

**The 22% and "10–100 km with sleeve couplers" characterization appears to be either a misremembering of a different source or an entirely fabricated citation.** The actual Luo et al. result is 56% stress reduction, not 22%, and applies to optimized 5-6 segment configurations, not sleeve-jointed 10-100 km ribbons.

*Recommendation: This citation must be corrected before publication. Authors should identify the actual source of the 22%/10–100 km claim, or remove it.*

### 4c. Penoyre & Sandford 2019 — "Spaceline" characterization

**CORRECT with one minor qualification.**

The paper characterizes the Spaceline as: *"anchored to the Moon rather than supported centrifugally — sidesteps the taper problem entirely and is feasible with existing materials, though it cannot provide direct surface-to-orbit access."*

From the arXiv abstract (1908.09339): *"By extending a line, anchored on the moon, to deep within Earth's gravity well, we can construct a stable, traversable cable allowing free movement from the vicinity of Earth to the Moon's surface. With current materials, it is feasible to build a cable extending to close to the height of geostationary orbit."*

- "Cannot provide direct surface-to-orbit access" ✓ — the cable only reaches to ~GEO altitude, not Earth's surface
- "Feasible with existing materials" ✓ — confirmed by abstract
- "Anchored to the Moon" ✓

**Minor qualification:** The phrase "sidesteps the taper problem **entirely**" is an overstatement. The Spaceline still requires adequate material strength and has taper considerations (it must support its own weight in the Moon-Earth gravity gradient). The correct statement is that the Spaceline *significantly reduces* the specific strength requirement relative to an Earth-anchored elevator, but does not eliminate it. The word "entirely" should be softened to "largely."

### 4d. Niu et al. 2025 — "~5 GPa specific strength, km-scale"

**CONFIRMED but with units confusion.**

The actual paper: *"Continuous carbon nanotube fiber with an extremely high average specific strength of 4.1 N·tex⁻¹"*, Nano Research, DOI: 10.26599/NR.2025.94907584.

The Egan/Ergezer paper says **"~5 GPa specific strength"** for Niu et al. 2025. The actual paper reports **4.1 N/tex**.

Converting: for CNT fiber density ρ ≈ 1300 kg/m³:
- 1 N/tex = 1 N/(g/km) = 10⁶ N/kg = 10⁶ m²/s² (mass-specific force)
- Absolute strength ≈ 4.1 × 10⁶ N/kg × 1300 kg/m³ ≈ **5.33 GPa**

So "~5 GPa" is approximately correct (~4% understatement) if interpreted as converting N/tex to absolute tensile strength via bulk density. However, "specific strength" properly refers to strength/density (N·m/kg = m²/s²), not absolute stress (Pa = N/m²). The paper conflates the two units. The Niu et al. result should be cited as "4.1 N·tex⁻¹ specific strength" or "≈5.3 GPa absolute strength at ρ=1,300 kg/m³," not "~5 GPa specific strength." **Minor correction needed.**

---

## Task 5 — Novelty Assessment

**The novelty claim (§2.5) is supported.**

A systematic search for published work coupling joint reliability + segment geometry + repair logistics + lifecycle economics for space elevator tethers found no prior art that integrates all five elements (modular taper geometry, position-dependent joint failure, cascading redistribution, inspection/repair logistics, phased-construction economics) in a single coupled analysis:

- **Luo et al. (2022a, 2022b)**: Stress optimization and stability of segmented tethers — no reliability model, no lifecycle cost
- **Popescu & Sun (2018)**: Bio-inspired repair concept with qualitative maintainability argument — no quantified MTTR, no Monte Carlo, no NPV
- **ISEC/Wright et al. (2023)** (*Acta Astronautica* 211, 631–649): Climber-tether interface mechanics — no joint reliability model, no lifecycle economics
- **Edwards & Westling (2003)**: Monolithic baseline — no segmentation, no joint model
- No published study found that performs coupled Monte Carlo reliability + MTTR analytics + lifecycle NPV for a segmented/modular elevator tether

The contribution is novel. The modular tether reliability surface P_sys(N, η_j, cadence, p_det, β) over 12,600 combinations is the first quantified result of this kind in the literature.

---

## Task 6 — Internal Consistency Checks

### 6a. N=83 in Exponential MC Grid

The paper (§5.2.1) states: *"The exponential baseline grid does not include N = 83."*

**Confirmed.** `parameters.yaml` MC sweep: `[12, 15, 18, 21, 24, 50, 100, 200, 500]` — N=83 absent.  
Weibull extension (`phase1_weibull/config.py`): `[12, 15, 18, 21, 24, 50, 83, 100, 200, 500]` — N=83 present.

The paper also states N=83 exponential results are obtained "by interpolation from N ∈ {50, 100}." This is adequate methodology but should note that interpolation in N (a parameter affecting exponential cascade probabilities) is not strictly linear. The Weibull extension directly computes N=83, so this matters only for the exponential baseline results. ✓

### 6b. Coriolis Shift — "16%"

Calculation: (34.8 − 30.0) / 30.0 = **16.00%** ✓ (using paper's rounded values)

However, using the CSV's more precise values: (34.80 − 30.04) / 30.04 = **15.85%**. The paper rounds 15.85% to "16%" — acceptable rounding, but the underlying data value (30.04 h, not 30.0 h) should ideally be reported consistently. The paper states "T₁ transverse [h]: 30.0" but the CSV says 30.04 h. Minor.

### 6c. "19% discrepancy" (2D vs analytical)

Paper states: *"The 30.0 h no-Coriolis transverse period is 19% longer than the 25.3 h analytical pendulum period."*

Calculation: (30.0 − 25.3) / 25.3 = **18.58%** ≠ 19%

Using CSV value: (30.04 − 25.3) / 25.3 = **18.74%** ≠ 19%

The paper overstates the discrepancy by rounding 18.6% to 19%. Should be reported as "~18.6%" or "~19%." Technically an error (18.6% is not "19%"), though within journalistic rounding. More importantly, the "19%" framing suggests a round number was chosen for readability — the actual computed discrepancy is 18.6%.

### 6d. A_base = 7.85 × 10⁻⁶ m²

Paper states: *"A_base = m_climber × g / σ_design = 20000 × 9.81 / (25 × 10⁹) = 7.85 × 10⁻⁶ m²"*

Calculation: 20000 × 9.81 / 25e9 = **7.848 × 10⁻⁶ m² ≈ 7.85 × 10⁻⁶ m²** ✓

Using physically consistent g = GM/R² = 9.798 m/s²: A_base = **7.838 × 10⁻⁶ m²** (0.1% lower). The paper uses standard sea-level g = 9.81 m/s² rather than the GM/R² value consistent with the rest of the simulation. The code uses GM/R². Negligible impact but inconsistent in principle.

---

## Task 7 — Methodology Concerns

### 7a. Arrhenius Hazard Model — Is it applied correctly?

**Applied correctly with appropriate caveats.** The Arrhenius form for hazard rate:

```
λ_j(T) = λ_0_pre × exp(−Q / (k_B × T)) × (0.97 / η_j)⁴
```

is a standard time-to-failure model for thermally activated failure mechanisms. The Chen et al. (2010) citation for Q = 1.06 eV for SnAg solder electromigration is a reasonable analog. The mission-averaged integration over three thermal zones is appropriate.

**Concern:** The hazard model combines the Arrhenius exponential with a stress-coupling power law `(0.97/η_j)⁴`. The exponent 4 is assumed without experimental CNT-specific data (acknowledged in §4.3). At η_j = 0.95, (0.97/0.95)⁴ = 1.085 — only an 8.5% modulation. At η_j = 0.70, (0.97/0.70)⁴ = 3.47 — a 3.5× increase. The sensitivity of results to this exponent (which could range from 2 to 10 per §4.3) is not explicitly quantified in a sensitivity figure, though §4.3 notes cascade threshold binary insensitivity. A supplementary figure sweeping the exponent would strengthen the analysis.

**Also:** The `lambda_0_pre` calibration uses the Arrhenius formula calibrated to λ̄_fullscale = 5.2e-8 h⁻¹. However, the Q-sensitivity analysis holds λ_0_pre **fixed** when varying Q (§5.2.3: "The calibration of λ_0_pre is held fixed when perturbing Q"). This means the Q=0.8 and Q=1.4 eV cases represent physical changes in Q with the reference state held at Q=1.1 eV — which is the correct way to isolate physical sensitivity. ✓

### 7b. Weibull Volume Scaling Applied to Hazard Rates

**The paper explicitly acknowledges this as an approximation:**

> "This hazard-rate scaling is a common engineering approximation; rigorously, Weibull weakest-link theory applies to strength distributions rather than directly to time-dependent hazard rates."

This is correct and well-disclosed. However, the implications are more serious than the paper acknowledges:

1. **Rigorous issue:** Weibull weakest-link theory predicts that the *characteristic strength* of a larger specimen is lower (V_sleeve/V_coupon)^(1/m) relative to a coupon. This applies to static failure load, not to time-dependent hazard rates of a chemically driven degradation process. The two are formally different: diffusion-controlled void growth kinetics depend on geometric path lengths and surface-to-volume ratios, not on the number of independent failure sites. Applying strength-distribution volume scaling to hazard rates introduces an undefined approximation that may over- or underestimate size effects by orders of magnitude.

2. **Acknowledged partially:** The paper cites Bertalan et al. (2014) on Weibull instability at m < 30, and Carpinteri & Pugno (2008) on size-effect scaling, but does not provide a physical derivation justifying why diffusion-controlled void growth would scale as V^(1/m). This should be flagged as a substantive limitation beyond "common approximation."

3. **Practical impact:** The m=6 volume scaling factor 6000^(1/6) = 4.26 inflates λ from coupon to full-scale. With m=2.7 (Pugno & Ruoff, 2006), the factor becomes 6000^(1/2.7) ≈ 25.1 — a 6× increase. The paper's Fig. S19 sweeps m ∈ {2.7, 4, 6, 8, 10} and claims viability persists at m=2.7, which is reassuring. ✓

**Recommendation for reviewers:** Request that the authors add a paragraph quantifying the theoretical basis for their volume scaling assumption and distinguishing between weakest-link strength scaling and time-dependent hazard rate scaling.

### 7c. Monolithic Comparison Asymmetry

**Acknowledged but not fully resolved.** The paper addresses this in §8.5 (limitation 5) and §7.5:

> "The monolithic failure model uses a simplified annual probability rather than a detailed degradation model comparable to the modular Weibull-cascade framework."

The §7.5 sensitivity sweep showing modular advantage persists across P_fail_mono ∈ {10⁻⁴, 10⁻¹} is appropriate. However:

- The monolithic NPV advantage claim depends primarily on the **phased-construction revenue** mechanism, not the failure cost comparison. The paper correctly notes this.
- The asymmetric failure models introduce a *narrative asymmetry*: the modular architecture gets a sophisticated, mechanistic reliability argument, while the monolithic alternative is treated as a simple annual probability with no mechanistic basis. A reviewer may ask: if a comparable Weibull-cascade model were applied to microcrack propagation in a monolithic ribbon, would the reliability comparison change? The paper does not address this.
- **No cross-check** is provided of whether P_fail_mono values of 10⁻⁴–10⁻¹/year are physically reasonable for a 100,000 km CNT ribbon under the same failure physics. If P_fail_mono were derived from the same Arrhenius/Weibull framework applied to the full ribbon, it would presumably be near 1.0 (catastrophic) — which would make the modular advantage even larger, but that comparison is not made explicit.

### 7d. The 60% Operational Threshold — Physical Soundness

**The deployment model is idealized and the 60% threshold is weakly justified.**

The paper claims modular revenue begins at ~60% tether completion under a GEO-outward/inward simultaneous deployment. Key assumptions:

1. **GEO-outward/inward deployment enabling surface contact at 60%:** The paper cites Edwards & Westling (2003) §4.3, but this reference appears to describe a seeding strategy for growing an initial thin ribbon, not the specific 60% operational threshold. No quantitative justification for 60% (rather than, say, 70% or 80%) is provided from the deployment mechanics.

2. **Revenue at partial completion:** The claim that "low-capacity climber traversals" are possible once the surface anchor is reached implies the partially deployed tether can bear climber loads. At 60% of N=83 segments = 50 segments, the cross-section at the base is set by σ_design, meaning the design tension is marginally met. The dynamic analysis (§6.6) shows 67% tension perturbation from a single climber at the base — meaning a climber at 60% completion would push the base tension to 167% of design, well above the safety factor allowance. **This undermines the 60% revenue assumption on structural grounds.**

3. **Sensitivity analysis:** The f_threshold sweep (f ∈ {0.5, 0.9}) confirms the economic advantage persists, which partially addresses the uncertainty. But the paper should explicitly note that the 60% threshold assumes structural certification at partial completion — which may not be physically achievable given the tension perturbation results. The narrative that "phased construction generates revenue" is the paper's strongest economic claim; its physical basis deserves more scrutiny.

---

## Summary of Key Findings

### Confirmed / Correct
| # | Finding | Status |
|---|---------|--------|
| T1 | I_geo = 4.8423 × 10⁷ m²/s² | ✓ Matches paper to 0.05% |
| T1 | Taper formula T_r spot-checks (5 rows) | ✓ All within 0.2% |
| T2 | All Table 4.1 parameters match yaml | ✓ Exact match |
| T2 | Weibull grid correctly includes N=83 | ✓ |
| T2 | N=83 absent from exponential baseline grid | ✓ (as stated) |
| T3 | P_sys = 0.99995 at baseline N=83 config | ✓ Exactly matches claim |
| T3 | Q=0.8 eV gives P_sys=0, Q=1.4 eV gives P_sys≈1 | ✓ |
| T3 | "10 orders of magnitude" hazard rate span | ✓ (actual: 1.26×10¹⁰) |
| T3 | T₁ transverse: 30.0 h / 34.8 h / 16% shift | ✓ (CSV: 30.04/34.80/15.9%) |
| T4 | Bai et al. 2018: 80 GPa CNT bundles | ✓ Nature Nanotechnology confirmed |
| T4 | Penoyre & Sandford 2019: Spaceline cannot reach surface | ✓ |
| T4 | Niu et al. 2025: km-scale CNT fiber | ✓ (4.1 N/tex ≈ 5.3 GPa) |
| T5 | Novelty claim: no prior coupled study found | ✓ Supported |
| T6 | Coriolis shift arithmetic (16%) | ✓ |
| T6 | A_base = 7.85 × 10⁻⁶ m² | ✓ (using g=9.81) |
| T6 | N=83 handled via Weibull extension grid | ✓ |

### Errors, Discrepancies, and Concerns
| # | Issue | Severity |
|---|-------|----------|
| T1 | Popescu last row: published 36.9 vs calculated 39.4 (6.8% gap) glossed over | **Medium** |
| T2 | NPV model defaults to N=18, paper discusses N=83 (years_to_build 1.5 vs 7) | **HIGH** |
| T2 | MC failure rate extraction at N=18, not N=83 | **Medium** |
| T2 | λ_full three-way inconsistency (5.115 vs 5.2 vs 5.293 × 10⁻⁸) | Low |
| T2 | A_base: code uses GM/R², paper text uses 9.81 | Low |
| T3 | T₁ longitudinal: paper 7.65/7.12 h vs CSV 10.22/10.46 h — factor ~1.4× mismatch | **HIGH** |
| T3 | Sign of Coriolis shift on longitudinal mode: paper says −7%, CSV shows +21.6% | **HIGH** |
| T3 | 2D joint compliance shift: paper claims 2.44%, CSV shows 0.0% | **Medium** |
| T3 | 4 orphan PDFs not in figure index | Low |
| T4 | Luo et al. 2022a: paper claims "22% stress reduction with 10–100 km sleeve couplers"; actual = 56% reduction, 5–6 segments, no sleeve couplers | **HIGH** |
| T4 | Niu et al. 2025: "5 GPa specific strength" conflates N/tex with GPa | Low |
| T4 | Penoyre 2019: "sidesteps taper problem entirely" overstated | Low |
| T6 | "19% discrepancy" is actually 18.6% | Low |
| T7 | Weibull volume scaling applied to hazard rates lacks theoretical justification | **Medium** |
| T7 | 60% revenue threshold not physically verified against tension perturbation results | **Medium** |
| T7 | Stress-coupling exponent (4) sensitivity not explicitly quantified in a figure | Low |
| T7 | Monolithic comparison uses simplified failure model without physical derivation | **Medium** |

---

## Source Notes

- `paper.md` — full draft read
- `data/parameters.yaml` — master parameters (locked)
- `simulations/monte_carlo/phase1_weibull/config.py`
- `simulations/fea/phase2_dynamics/config.py`
- `simulations/cost_model/npv_model.py`
- `simulations/fea/taper_profile.py`
- `data/processed/weibull_sweep_results.csv` — verified row grep
- `data/processed/Q_hazard_rate_table.csv` — all 3 rows checked
- `data/processed/phase2_dynamics/comparison_table.csv` — full table read
- `paper/figures/` — 41 PDFs counted vs 37 declared
- Bai et al. 2018: https://www.nature.com/articles/s41565-018-0141-z — confirmed
- Luo et al. 2022a: https://mdpi-res.com/...aerospace-09-00278-v2.pdf — full text read, 18 pages
- Penoyre & Sandford 2019: https://arxiv.org/abs/1908.09339 — abstract confirmed
- Niu et al. 2025: https://www.sciopen.com/article/10.26599/NR.2025.94907584 — confirmed 4.1 N/tex
- Novelty search: no prior coupled reliability+logistics+economics study found

---

## Recommended Actions Before Submission

1. **[Critical]** Fix NPV model to use N=83 throughout — update `N_baseline` in `parameters.yaml` to 83 or pass `N_override=83` in `run_sweep()`. Regenerate Fig. 14, Table 7.1, and crossover year claims.

2. **[Critical]** Investigate and resolve T₁ longitudinal discrepancy: paper text says 7.65/7.12 h but CSV says 10.22/10.46 h. Determine which value is correct and whether the modal table in §6.6 needs to be updated. Check whether Coriolis shift sign on longitudinal is −7% or +21.6%.

3. **[Critical]** Correct or remove the Luo et al. 2022a citation claiming "22% stress reduction with 10–100 km sleeve couplers." This is a material misrepresentation of the source paper, which reports 56% stress reduction for 5–6 optimized segments with no sleeve couplers. Find the actual source for the "22%" figure or delete the claim.

4. **[Important]** Qualify the "no residual discrepancy" claim: the Popescu & Sun (2018) published T_r = 36.9 vs. formula-calculated 39.4 is a 6.8% gap that should be acknowledged and explained (different I_geo integration bounds? Different A_base convention?).

5. **[Important]** Add physical justification for Weibull volume scaling applied to hazard rates, distinguishing from strength distribution scaling. Alternatively, frame it explicitly as a bounding assumption with ±order-of-magnitude error bars.

6. **[Important]** Verify the 60% operational threshold against the tension perturbation analysis: §6.6 shows 67% tension perturbation from a single climber at the base. Does a partial tether at 60% completion survive a climber traversal within the SF=2 envelope?

7. **[Minor]** Correct "19%" to "~18.6%" for the 2D-vs-analytical discrepancy.

8. **[Minor]** Clarify Niu et al. 2025 units: report as "4.1 N·tex⁻¹ (≈5.3 GPa at ρ=1,300 kg/m³)" not "~5 GPa specific strength."

9. **[Minor]** Remove 4 orphan PDFs from submission archive. Update figure count if any are promoted to supplementary.
