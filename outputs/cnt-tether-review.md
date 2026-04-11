# Peer Review: Modular CNT Space-Elevator Tether

**Paper:** Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment: A Coupled Systems Analysis  
**Authors:** Egan, K. & Ergezer, M.  
**Target venue:** *Acta Astronautica* (Elsevier)  
**Review date:** 2026-04-10

---

## Overall Assessment

This paper presents an ambitious coupled-systems analysis of a modular carbon-nanotube space-elevator tether, integrating taper geometry, joint reliability via Monte Carlo simulation, dynamic modal analysis (1D and 2D Coriolis-coupled), repair logistics, and lifecycle economics into a single design trade space. The scope is genuinely impressive: 12,600 parameter combinations × 10⁵ trajectories for the Weibull reliability surface, a 998-DOF finite element model with Coriolis coupling, and an analytical repair-depot trade space — all grounded in a single locked parameter file. The paper identifies a real gap (no prior study couples all five elements for a segmented elevator tether) and fills it with quantitative results.

The strongest contributions are: (i) the Q-sensitivity analysis revealing that activation energy uncertainty dominates all other reliability parameters by ~7 orders of magnitude — a genuinely important finding that reframes the entire reliability question; (ii) the taper-ratio reconciliation showing that all published T_r values collapse onto a single integral once three hidden assumptions are stated; and (iii) the inspection-cadence insight that the Edwards & Westling 72 h repair target is structurally unachievable via depots alone. The paper is also unusually self-aware about its limitations (§8.5, §8.6), explicitly flagging the conditional nature of its reliability predictions and the monolithic comparison asymmetry.

However, the review uncovered four critical errors — a code-paper inconsistency in the NPV model (N=18 vs. N=83), a data-paper mismatch in the longitudinal modal results (including a sign reversal of the Coriolis shift), a material mischaracterization of Luo et al. (2022a), and an unresolved Popescu residual — that must be corrected before publication. Several major issues (Weibull volume-scaling justification, 60% threshold vs. tension perturbation, monolithic comparison asymmetry) also require strengthening. The paper is publishable after substantial revision.

---

## Recommendation

**Major Revision** — The four critical issues (NPV bug, longitudinal modal data mismatch, Luo 2022a mischaracterization, and Coriolis sign reversal) each individually warrant revision. Collectively they erode trust in the reported numbers, even though the paper's core contributions (Q-sensitivity, taper reconciliation, reliability surface) appear sound upon independent verification.

---

## Strengths

1. **Genuine novelty, independently confirmed.** A systematic literature search found no prior work coupling joint reliability + segment geometry + repair logistics + dynamic stability + lifecycle economics for a segmented space-elevator tether. The claim in §2.5 is supported. The 12,600-combination reliability surface P_sys(N, η_j, cadence, p_det, β) is the first published result of its kind.

2. **The Q-sensitivity analysis (§6.4) is the paper's most important contribution.** The demonstration that the hazard rate spans 10 orders of magnitude across Q ∈ {0.8, 1.1, 1.4} eV — collapsing P_sys to zero at Q = 0.8 eV and saturating at unity at Q = 1.4 eV — is a genuinely significant finding. It reframes space-elevator joint reliability from a systems-engineering problem to a materials-characterization problem and establishes Q measurement as the binding experimental priority. The hazard rate data (Q_hazard_rate_table.csv) was independently verified: λ_full ratios span 1.26 × 10¹⁰, confirming the "10 orders of magnitude" claim.

3. **Taper reconciliation (§3.2) is a real contribution to the field.** The demonstration that all published T_r values (1.6–37) are recoverable from ln(T_r) = ρ·I_geo/σ_design with I_geo ≈ 4.84 × 10⁷ m²/s² was verified by independent numerical integration (confirmed to 0.05%). Five spot-checks of the reconciliation table all pass within 0.2%. The recommendation that future analyses state their stress basis, material density, and A_base philosophy is excellent practice guidance.

4. **Parametric discipline.** All simulations read from a single locked `parameters.yaml`. Verified exact match between Table 4.1 and the YAML file across all 10 baseline parameters. The Weibull grid correctly includes N=83 (absent from the exponential baseline, as stated). This level of parameter traceability is exemplary.

5. **Honest limitation disclosure (§8.5, §8.6).** The paper explicitly acknowledges: the conditional nature of all reliability predictions on Q; the monolithic comparison asymmetry (limitation 5); the absence of experimental validation (limitation 4); damping uncertainty; and the 2D model's omissions. §8.6 ("The Q Problem") is remarkably candid — it states that "no amount of engineering optimization can compensate for the wrong Q." This level of intellectual honesty is rare and should be commended.

6. **Inspection-cadence finding (§6.5.1, §8.7).** The insight that P(MTTR ≤ 72 h) saturates near 38% regardless of depot count because the expected detection wait time (93 h) already exceeds 72 h is non-obvious and practically important. The three identified paths to 72 h compliance (faster climbers, continuous SHM, multiple inspection climbers) are well-motivated.

7. **Dynamic model validation (§5.3.2).** Six validation checks for the 2D FEM (positive-definite K, 1D recovery, Coriolis skew-symmetry, energy conservation, mesh convergence, joint compliance) demonstrate careful implementation. The Coriolis coupling result (16% transverse period shift) is a genuine upgrade over 1D models.

8. **Multi-climber resonance design rule (§6.6).** The identification of a resonance peak at ~35 h separation with 3.6× amplification, and the practical recommendation to avoid departures within ±5 h of this period, provides actionable engineering guidance.

---

## Critical Issues (Must Fix)

### 1. NPV Model Defaults to N=18; Paper Discusses N=83

**What's wrong:** The lifecycle cost model (`npv_model.py`) reads `N_baseline: 18` from `parameters.yaml` when `run_sweep()` is called without an override. This produces a 1.5-year build time (18/12), not the 7-year build time (83/12) discussed throughout §7. The `get_mc_failure_rates()` function also hardcodes extraction at N=18 from the Monte Carlo grid — a configuration not even in the Weibull extension's design space.

**Where:** §7 (all subsections), Table 7.1 ("Years to build: ~7"), Fig. 14 (NPV curves), `simulations/cost_model/npv_model.py`, `data/parameters.yaml`.

**Evidence:** Research file Task 2c documents the code path: `N = int(params["segments"]["N_baseline"])` → 18. The `sweep_p_fail_mono()` and `sweep_f_threshold()` functions do pass `N_override=83`, but the main sweep does not.

**What to do:** Update `N_baseline` in `parameters.yaml` to 83, or pass `N_override=83` in `run_sweep()`. Regenerate all NPV figures and tables. Verify that the crossover year, delta_NPV values, and depot break-even counts still hold at N=83. If the main NPV comparison was actually run at N=18, all economic claims in §7.3–7.4 are quantitatively wrong and must be re-derived.

### 2. T₁ Longitudinal Data Mismatch — Paper vs. CSV

**What's wrong:** The paper's modal results table (§6.6) reports T₁_longitudinal = 7.65 h (no Coriolis) and 7.12 h (with Coriolis, −7% shift). The actual data file (`phase2_dynamics/comparison_table.csv`) shows T₁_longitudinal = 10.22 h (no Coriolis) and 10.46 h (with Coriolis, +21.6% shift). The paper values are 1.34–1.47× smaller than the data, and the direction of the Coriolis effect is reversed.

**Where:** §6.6 modal results table, `data/processed/phase2_dynamics/comparison_table.csv`.

**Evidence:** Research file Task 3c documents the CSV values verbatim. The transverse modes are consistent (30.0 h / 34.8 h / 16% — all confirmed), so this is specific to the longitudinal row.

**What to do:** Determine which values are correct — the paper text or the CSV. If the CSV is authoritative (as a direct simulation output), the paper table must be updated to T₁_long = 10.22 / 10.46 h with a +2.3% Coriolis shift, and all downstream discussion of longitudinal modes must be revised. The paper's narrative that "the first longitudinal elastic mode at 7.65 h is distinct from the 25.3 h analytical pendulum period" would need re-examination at 10.22 h. Also check the 2D joint compliance shift: the paper claims 2.44% but the CSV shows 0.0% for the 2D case.

### 3. Coriolis Sign Reversal on Longitudinal Mode

**What's wrong:** Closely related to Issue 2 but conceptually distinct. The paper claims the Coriolis coupling *increases* the longitudinal frequency (period decreases from 7.65 → 7.12 h, a −7% shift). The CSV shows the opposite: the period *increases* from 10.22 → 10.46 h (a +2.3% or +21.6% shift depending on the reference). A sign error in the Coriolis effect would undermine the physical interpretation of longitudinal-transverse energy transfer discussed in §5.3.2 and §6.6.

**Where:** §6.6 modal table, §5.3.2 Coriolis coupling discussion.

**Evidence:** Research file Task 3c. The transverse Coriolis shift is correctly reported as positive (+16%), so the sign convention is not globally wrong — the error is specific to the longitudinal mode.

**What to do:** Re-examine the eigenvalue extraction for the longitudinal fundamental. It is possible that the paper table has T₂_transverse (10.2 h from the paper) confused with T₁_longitudinal, given their numerical proximity (CSV T₁_long_2D_noCoriolis = 10.22 h ≈ paper T₂_trans = 10.2 h). If this is a labeling error, the correction is straightforward.

### 4. Luo et al. (2022a) Mischaracterization

**What's wrong:** The paper states "Luo et al. (2022a) quantified a 22% stress reduction with 10–100 km segments joined by sleeve couplers" (§2.1, repeated in §8.4 comparison table). The actual Luo et al. 2022a paper reports a **56% stress reduction** for **5–6 optimized segments** using **connecting platforms** (not sleeve couplers), with segment division points at altitudes of 7,000–21,000 km (not 10–100 km length segments). The figure "22%" does not appear anywhere in the source.

**Where:** §2.1, §8.4 (comparison table row for Luo et al.).

**Evidence:** Research file Task 4b provides a detailed comparison against the full text of Luo et al. 2022a (*Aerospace* 9(5), 278). The paper's methodology is stress optimization by varying segment positions and cross-sectional area ratios — fundamentally different from the mass-equalized segmentation described in Egan & Ergezer.

**What to do:** Correct the citation to: "Luo et al. (2022a) demonstrated a 56% peak-stress reduction using 5–6 optimized segments with connecting platforms." If the 22% figure originates from a different source, identify and cite it. Update the §8.4 comparison table accordingly.

---

## Major Issues

### 5. Popescu & Sun Residual Discrepancy Glossed Over

**What's wrong:** The reconciliation table (§3.2) claims "no residual discrepancy" for all published T_r values. However, the Popescu & Sun (2018) last row shows T_r(published) = 36.9 vs. T_r(calculated) = 39.4 — a 6.8% gap. The formula reproduces the authors' own calculated column but not the original published value.

**Where:** §3.2 reconciliation table and the "no residual discrepancy" claim.

**Evidence:** Research file Task 1c. The 6.8% gap is reproducible: ln(39.4) = 1631 × 4.8423e7 / 21.5e9 = 3.674, T_r = 39.4. Popescu & Sun report 36.9 at the same stated inputs.

**What to do:** Qualify the claim: "Every published ratio is recoverable within 7%, with the largest residual (6.8%) occurring for Popescu & Sun's STR-method value — possibly reflecting different integration bounds or A_base conventions not fully documented in their paper." Alternatively, investigate whether Popescu & Sun used a slightly different I_geo (e.g., a different Earth radius or integration limit).

### 6. Weibull Volume Scaling Applied to Hazard Rates Lacks Theoretical Justification

**What's wrong:** The paper applies Weibull weakest-link scaling (λ_full = λ_coupon × (V/V_0)^(1/m)) to time-dependent hazard rates. Weakest-link theory rigorously applies to static strength distributions, not to diffusion-controlled void growth kinetics. The paper acknowledges this as "a common engineering approximation" (§4.3) and cites Bertalan et al. (2014) on Weibull instability at low modulus, but does not provide a physical derivation for why diffusion-controlled void growth would scale as V^(1/m).

**Where:** §4.3 (volume scaling paragraph).

**Evidence:** Research file Task 7b. Diffusion kinetics depend on geometric path lengths and surface-to-volume ratios, not on the number of independent failure sites. The approximation may over- or underestimate size effects by orders of magnitude.

**What to do:** Add a paragraph distinguishing between weakest-link strength scaling and time-dependent hazard rate scaling, and explicitly bound the error this introduces. The m ∈ {2.7–10} sweep (Fig. S19) partially addresses this, but the paper should state that the volume-scaling formulation is an engineering bound, not a physical model, and that experimental full-scale hazard rate data would supersede it.

### 7. 60% Operational Threshold vs. Tension Perturbation Inconsistency

**What's wrong:** The NPV model assumes revenue begins at 60% tether completion (§7.2). However, the dynamic analysis (§6.6) shows a 66.6% peak tension perturbation from a single 20 t climber at the tether base. At 60% completion, the tether cross-section at the base is at design stress — adding a climber pushes it to ~167% of design tension, which exceeds the SF=2 allowable at the design stress (since σ_allow = σ_u/SF, the climber brings the base to σ_allow + 0.67×σ_allow = 1.67×σ_allow, within σ_u but consuming most of the safety factor).

**Where:** §7.2 (60% threshold), §6.6 (tension perturbation results).

**Evidence:** Research file Task 7d. The paper does sweep f_threshold ∈ {0.5–0.9} and shows the advantage persists, but does not cross-reference the 60% assumption against its own structural analysis.

**What to do:** Either (a) demonstrate that a partial tether at 60% completion can structurally support a climber within the design envelope (accounting for the reduced cross-section in incomplete segments), or (b) raise the baseline threshold to a value supported by the tension perturbation analysis, or (c) explicitly note this as an unresolved coupling between the economic and structural models.

### 8. Monolithic Comparison Asymmetry

**What's wrong:** The modular architecture receives a sophisticated Weibull-cascade reliability model, while the monolithic alternative is treated as a simple annual failure probability P_fail_mono with no mechanistic basis. The sensitivity sweep (§7.5) over P_fail_mono ∈ {10⁻⁴–10⁻¹} is appropriate but does not address whether these values are physically consistent with the same failure physics used for the modular model.

**Where:** §5.4 (monolithic NPV formulation), §7.5, §8.5 (limitation 5).

**Evidence:** Research file Task 7c. If the same Arrhenius/Weibull framework were applied to a continuous 100,000 km ribbon with no joints but with microcrack propagation, P_fail_mono would presumably be near 1.0 — which would strengthen the modular case but is never stated.

**What to do:** Add a brief derivation or bounding estimate of what P_fail_mono would be under comparable failure physics for a monolithic ribbon. If this is intractable, state explicitly that the comparison assumes the monolithic ribbon has a fundamentally different (and more favorable) failure mechanism than the jointed modular tether.

### 9. 2D Joint Compliance Shift — Paper vs. CSV

**What's wrong:** The paper (§5.3.2 validation list) claims the 2D model shows a 2.44% joint compliance frequency shift (vs. 1D's 2.32%). The comparison CSV shows a 2D joint compliance shift of 0.0%.

**Where:** §5.3.2 validation bullet point 6.

**Evidence:** Research file Task 3c, `comparison_table.csv`.

**What to do:** Verify the 2D joint compliance result. If the CSV is correct (0.0%), the validation claim must be corrected. If the result was computed separately and not recorded in the CSV, add it or cite the specific output file.

---

## Minor Issues

1. **"19% discrepancy" is 18.6%.** §5.3.2 and §6.6 state that the 2D transverse period (30.0 h) is "19% longer" than the analytical estimate (25.3 h). Actual: (30.0 − 25.3)/25.3 = 18.6%. Using the CSV value (30.04 h): 18.7%. Report as "~19%" or "18.6%."

2. **Niu et al. (2025) units conflation.** The paper cites "~5 GPa specific strength." The actual result is 4.1 N·tex⁻¹, which converts to ~5.3 GPa *absolute tensile strength* at ρ = 1,300 kg/m³. "Specific strength" has units of N·m/kg, not Pa. Report as "4.1 N·tex⁻¹ (≈5.3 GPa at ρ = 1,300 kg/m³)."

3. **Penoyre & Sandford (2019) overstatement.** "Sidesteps the taper problem *entirely*" — the Spaceline still has taper considerations in the Moon-Earth gradient. Soften to "largely sidesteps."

4. **λ_full three-way rounding inconsistency.** Calculated: 5.115 × 10⁻⁸; `parameters.yaml`: 5.2 × 10⁻⁸; Q-table at Q=1.1 eV: 5.293 × 10⁻⁸. The Arrhenius calibration loop likely absorbs this, but the 3.6% spread across three representations of the same quantity should be harmonized.

5. **A_base gravitational constant mismatch.** The paper text uses g = 9.81 m/s²; the code uses GM/R² = 9.798 m/s². Difference is 0.12% — negligible but technically inconsistent. Pick one.

6. **Four orphan PDF figures** in `paper/figures/` (`fig_depot_cost_tradespace.pdf`, `fig_npv_crossover.pdf`, `fig_npv_with_depots.pdf`, `fig_weibull_mttr_depot_shift.pdf`) are not in the Figure Index and not referenced in the text. Remove from the submission archive.

7. **Paper length.** At ~950 lines of dense technical content with 37 figures (18 main + 19 supplementary), this exceeds typical *Acta Astronautica* research articles (usually 8,000–12,000 words with 10–15 figures). Consider whether some supplementary figures could be moved to an online-only appendix, and whether §8.7 (the 72 h target discussion) could be condensed.

8. **Rounding in Coriolis shift.** The CSV gives 15.9% for the transverse Coriolis shift; the paper reports 16%. Acceptable but the underlying values (30.04 h, not 30.0 h) should be reported consistently.

---

## Questions for Authors

1. Was the main NPV sweep (`run_sweep()`) actually executed at N=18 or N=83? If at N=18, which figures and table values in §7 are affected? Please provide the NPV comparison regenerated at N=83.

2. Which values for T₁_longitudinal are correct — the paper's 7.65/7.12 h or the CSV's 10.22/10.46 h? Is it possible that the paper's "T₁ longitudinal" row was populated from the T₂ transverse mode (which the paper reports as 10.2 h — suspiciously close to the CSV's T₁_long = 10.22 h)?

3. What is the source of the "22% stress reduction" attributed to Luo et al. (2022a)? The actual paper reports 56%. Was this figure from a different reference that was inadvertently attributed to Luo?

4. For the Popescu & Sun (2018) T_r = 36.9: have the authors contacted Popescu & Sun to clarify their integration bounds or A_base convention? The 6.8% residual is the only row in the reconciliation table that doesn't close to <1%.

5. Has the 60% operational threshold been verified against the tension perturbation analysis? Specifically: at 60% segment deployment, can the partial tether sustain a 20 t climber within SF ≥ 1.5 at the base, given the 67% tension perturbation documented in §6.6?

6. The stress-coupling exponent 4 in the hazard model (§4.3) is assumed from composite fatigue analogy. Have the authors considered sweeping this exponent (e.g., 2–8) in a supplementary sensitivity figure? The cascade threshold is binary, but the rate of cascade initiation depends on this exponent.

7. For the monolithic comparison: what would P_fail_mono be if derived from the same Arrhenius/Weibull framework applied to a continuous ribbon (with microcrack propagation replacing joint void growth)? Even a rough bounding estimate would strengthen §7.5.

---

## Verdict Summary Table

| Criterion | Rating (1–5) | Notes |
|-----------|:---:|-------|
| Novelty | 4 | Genuine gap filled; coupled 5-element trade space is new. Confirmed by literature search. |
| Technical Rigor | 3 | Strong methodology (MC, FEM, analytical MTTR) undermined by critical data inconsistencies (NPV N=18 bug, longitudinal modal mismatch, Luo citation error). Core results (taper formula, Q-sensitivity, reliability surface) independently verified. |
| Reproducibility | 4 | Single locked parameter file, scripts named and described, data files provided. Would be 5 if the NPV bug were fixed and the longitudinal modal discrepancy resolved. |
| Presentation | 3 | Well-structured with honest limitations, but overlength for the venue. Critical errors in the modal table and Luo citation damage credibility. Self-aware caveating (§8.5, §8.6) is commendable. |
| Significance | 4 | The Q-sensitivity finding alone is worth publishing — it reframes the field's reliability question. The taper reconciliation and inspection-cadence insight are also valuable. Economic results contingent on NPV bug fix. |

---

## Sources

All findings are grounded in evidence from the following sources inspected during this review:

**Paper and code artifacts (internal):**
- `paper.md` — full draft (950 lines)
- `data/parameters.yaml` — master parameter file
- `simulations/cost_model/npv_model.py` — NPV model code (N=18 bug source)
- `simulations/monte_carlo/phase1_weibull/config.py` — Weibull MC grid config
- `simulations/fea/phase2_dynamics/config.py` — 2D FEM config
- `simulations/fea/taper_profile.py` — taper integration script
- `data/processed/weibull_sweep_results.csv` — MC reliability data
- `data/processed/Q_hazard_rate_table.csv` — Q-sensitivity hazard rates
- `data/processed/phase2_dynamics/comparison_table.csv` — 2D modal results (source of T₁_long discrepancy)
- `paper/figures/` — 41 PDFs counted vs. 37 declared

**External literature verified:**
- Bai et al. (2018): https://www.nature.com/articles/s41565-018-0141-z — 80 GPa CNT bundles confirmed
- Luo et al. (2022a): https://doi.org/10.3390/aerospace9050278 — 56% stress reduction (not 22%), no sleeve couplers
- Penoyre & Sandford (2019): https://arxiv.org/abs/1908.09339 — Spaceline characterization confirmed
- Niu et al. (2025): https://doi.org/10.26599/NR.2025.94907584 — 4.1 N·tex⁻¹ confirmed
- Novelty search: no prior coupled reliability+logistics+economics study found for segmented elevator tethers
