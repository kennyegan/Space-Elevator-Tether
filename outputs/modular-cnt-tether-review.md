# Peer Review: Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment

**Manuscript:** "Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment: A Coupled Systems Analysis"
**Authors:** Kenneth Egan, Mehmet Ergezer (Wentworth Institute of Technology)
**Target Venue:** Acta Astronautica (Elsevier)
**Reviewer:** Anonymous
**Date:** 2026-04-09

---

## 1. Summary

This paper proposes a modular alternative to the monolithic carbon-nanotube (CNT) space-elevator tether, where variable-length segments are joined by nanobonded sleeve couplers. The authors integrate five analysis domains into a single coupled framework: (i) taper geometry with dual design envelopes (optimistic vs. conservative stress basis), (ii) Monte Carlo joint reliability over 12,600 parameter combinations × 10⁵ trajectories, (iii) a 2D Coriolis-coupled finite element dynamic model, (iv) repair infrastructure trade-space analysis with pre-positioned depots, and (v) lifecycle NPV comparison against a monolithic baseline. The paper resolves an apparent discrepancy in published taper ratios (T_r ≈ 1.6 to ≈ 37) by tracing all values to a single integral with three hidden assumptions (stress basis, material density, base-area sizing).

The central reliability finding is that system survival exceeds 99.5% over 10 years in the "well-designed regime" (η_j ≥ 0.88, p_det ≥ 0.90), but this result is explicitly conditional on the assumed activation energy Q ≈ 1.1 eV for void growth in CNT nano-solder bonds. A Q-sensitivity sweep shows the hazard rate spans ~10 orders of magnitude across Q ∈ {0.8, 1.1, 1.4} eV — the entire reliability surface collapses to zero at Q = 0.8 eV and saturates at unity at Q = 1.4 eV. The paper identifies experimental characterization of Q as the single most important priority.

The lifecycle economics analysis shows a modular NPV advantage driven by phased-construction revenue (partial operation at ~60% completion), and the dynamics analysis reveals a 16% Coriolis-induced shift in the transverse fundamental period with a concrete multi-climber resonance avoidance rule (±5 h of ~35 h). The repair infrastructure analysis identifies inspection cadence — not depot count — as the binding constraint on MTTR.

---

## 2. Verdict

**MINOR REVISION**

The paper is a substantial, well-structured systems-engineering feasibility study with genuine novelty in its coupled analysis framework and several useful contributions to the space-elevator literature. However, it contains a textual error in its self-described "first-class finding" (§3.2 integral bounds), a confirmed code-vs-paper inconsistency in the stress-hazard coupling (0.97 in code vs. 0.95 in paper), missing simulation scripts that undermine reproducibility, and an unfairly simplified monolithic baseline. These are correctable without fundamental changes to the methodology or conclusions.

---

## 3. Strengths

1. **Taper ratio reconciliation (§3.2, Table)** — The demonstration that all published T_r values (1.6–37) reduce to `ln(T_r) = ρ × I_geo / σ_design` with three explicitly identified hidden assumptions is a genuinely useful reference contribution. The comparison table with six literature sources is a definitive clarification that will prevent future confusion.

2. **Computational scale (§5.2)** — 12,600 Weibull parameter combinations × 10⁵ trajectories = 1.26 × 10⁹ trajectories is serious computational work. The Weibull age-dependent extension with proper cumulative hazard tracking (§5.2.2, Eq. for Δt) is technically sound.

3. **Exceptional self-awareness of limitations (§8.5, §8.6)** — The paper's treatment of the Q-sensitivity problem is unusually honest for a feasibility study. Explicitly stating that all reliability results are conditional on Q ∈ [1.0, 1.2] eV, and that a 0.3 eV shift in either direction "collapses or trivializes the reliability question," is commendable scientific practice.

4. **2D Coriolis dynamics (§5.3.2, §6.6)** — The 16% frequency shift from Coriolis coupling is a non-trivial finding invisible to 1D models. The six-check validation suite (K positive-definite, 1D recovery, Coriolis skew-symmetry, energy conservation, mesh convergence, joint compliance) demonstrates careful implementation.

5. **Multi-climber resonance design rule (§6.6)** — The concrete recommendation to avoid departure separations within ±5 h of 35 h is an actionable engineering contribution with immediate design utility.

6. **Repair infrastructure insight (§6.5.1, §8.7)** — Identifying that the 72 h MTTR target is structurally constrained by inspection cadence (expected wait = 93 h > 72 h) rather than depot coverage is a non-obvious and valuable result that reframes the maintenance problem.

7. **Dual design envelopes (§3.2)** — Presenting both optimistic (σ_u taper) and conservative (σ_allow taper) cases as bounding envelopes, rather than choosing one, is methodologically mature.

8. **Code availability** — 29 Python scripts with centralized `parameters.yaml` is significantly above the median for this class of paper.

---

## 4. Issues

### FATAL — None

### MAJOR

**M1. Code-vs-Paper Inconsistency in Stress-Hazard Coupling (§4.3 / `joint_reliability.py`)**
- **What's wrong:** The paper states the hazard rate formula as `λ_j = λ_0_pre × exp(−Q/(k_BT)) × (0.95/η_j)⁴`, but `joint_reliability.py` (lines 18, 213, 229, 245) implements `(0.97/η_j)⁴`. The `parameters.yaml` file specifies `eta_j_baseline: 0.95`, so the code uses a reference efficiency (0.97) that differs from both the paper's formula (0.95) and the config's baseline (0.95).
- **Why it matters:** At the critical η_j = 0.88 threshold, the stress-hazard coupling factor changes from (0.95/0.88)⁴ = 1.36 to (0.97/0.88)⁴ = 1.47 — an 8% increase in hazard rate. This could shift the P_sys = 0.995 contour boundary, meaning the reported minimum η_j thresholds may not match the actual simulation results. It is unclear which value produced the reported results.
- **Fix:** Reconcile the reference efficiency across paper, code, and config. Report which value was actually used in the simulations that generated the published results. If 0.97 was used, update the paper's formula; if 0.95, re-run the Monte Carlo sweep.

**M2. Missing Simulation Scripts (§5.2.3, §5.5)**
- **What's wrong:** `simulations/repair_infrastructure/run_all.py` (referenced in §5.5) does not exist in the repository — only pre-computed outputs in `data/processed/phase3_repair/`. The `sensitivity_analysis.py` (referenced in §5.2.3) is also absent. The Weibull sweep runner script is missing.
- **Why it matters:** These are claimed as reproducibility artifacts. Missing scripts prevent independent verification of the repair trade-space analysis and the hazard sensitivity tornado (Fig. 6), which underpins the paper's most important finding (Q dominance).
- **Fix:** Include all referenced scripts in the repository. If they were run as one-off analyses, reconstruct and commit them.

**M3. Unfairly Simplified Monolithic Baseline (§5.4, §8.5)**
- **What's wrong:** The monolithic comparison uses a "simplified annual probability rather than detailed degradation model" (§8.5, limitation 5). The modular architecture receives a sophisticated Arrhenius-Weibull-cascade treatment with 12,600 parameter combinations, while the monolithic alternative is modeled with a flat annual failure probability.
- **Why it matters:** If the monolithic failure rate is overestimated by the simple model, the modular NPV advantage (§7.3) is inflated. The central economic claim — "modular consistently outperforms monolithic" — rests on an asymmetric comparison.
- **Fix:** Either (a) apply a comparable degradation model to the monolithic tether (Weibull wear-out of continuous ribbon), or (b) explicitly quantify the sensitivity of the NPV crossover to the monolithic failure probability (e.g., sweep P_fail_mono from 10⁻⁴ to 10⁻¹ per year and report the crossover threshold).

### MODERATE

**Mo1. Integral Bounds Error in §3.2**
- **What's wrong:** §3.2 states "Integrating Eq. (1) from the surface to the tether tip gives ln(T_r) = (ρ/σ_design) × I_geo where I_geo = ∫_R^{R+L} |a_net(r)| dr ≈ 4.84 × 10⁷ m²/s²." The taper ratio T_r = A(GEO)/A(base), so the relevant integral is surface → GEO, not surface → tip. The integral from surface to tip yields ~6.81 × 10⁷, not 4.84 × 10⁷. The numerical value 4.84 × 10⁷ is correct for the surface-to-GEO integral, and all downstream taper ratios verify correctly, so this is a labeling error rather than a calculation error.
- **Why it matters:** This appears in what the paper calls a "first-class finding" — the taper ratio reconciliation. The incorrect integral bounds undermine the pedagogical value of the derivation and will confuse readers attempting to reproduce it. The definition of I_geo must also account for the sign change at GEO (a_net < 0 below, > 0 above), which the absolute-value notation obscures.
- **Fix:** Correct the integral bounds to ∫_R^{r_GEO} and clarify that T_r represents the area ratio at GEO relative to the base, with a separate integral governing the above-GEO taper down to the counterweight.

**Mo2. 10× Material Gap Understatement (§2.2, §9.2)**
- **What's wrong:** The baseline assumes σ_u = 50 GPa. The best continuous kilometer-scale CNT fibers achieve ~5 GPa specific strength (Niu et al., 2025). This is a 10× gap from the best demonstrated continuous performance to the assumed baseline, and the gap widens further when considering ribbon-scale (meter-wide) production. While the paper acknowledges this as "aspirational" (§2.2) and sweeps 30–70 GPa, the sensitivity analysis treats σ_u as a free parameter without weighting by plausibility.
- **Why it matters:** A reader could conclude that σ_u = 30 GPa (the lowest sweep value) is within reach, when even 30 GPa is 6× the current continuous-fiber state of the art. The entire architecture analysis — including the Monte Carlo reliability surface — assumes the material problem is solved.
- **Fix:** Add a figure or table showing the historical trajectory of CNT fiber strength at increasing gauge lengths, with an explicit annotation of the assumed baseline vs. current demonstrated values. Consider weighting the sensitivity sweep to indicate which σ_u values are near-term plausible vs. aspirational.

**Mo3. η_j = 0.95 Is Entirely Notional (§4.2)**
- **What's wrong:** The baseline joint efficiency η_j = 0.95 is described as a "notional design target" (§4.2 note). No CNT sleeve coupler has been fabricated at any scale. The paper sweeps η_j ∈ {0.70–0.97} parametrically, but the baseline used for headline results (P_sys > 99.99% at N=83) is the upper end of a completely hypothetical range.
- **Why it matters:** The reliability conclusions are dominated by η_j (via the stress-hazard coupling). Presenting results at η_j = 0.95 as the baseline, when no experimental data exists, risks misleading readers about the maturity of the design.
- **Fix:** Consider presenting results at η_j = 0.88 (the identified 99.5% threshold) as the primary baseline, with η_j = 0.95 shown as a "target" scenario. Alternatively, frame the η_j sweep as the primary result and de-emphasize the specific η_j = 0.95 point.

**Mo4. 60% Operational Threshold (§5.4, §7.2)**
- **What's wrong:** The phased-construction revenue advantage — which the paper identifies as the primary driver of modular NPV superiority — depends on the assumption that the tether becomes operational at 60% segment completion via simultaneous GEO-outward/inward deployment.
- **Why it matters:** This is a structural assumption with no engineering validation. The actual load capacity at 60% completion, the certification pathway for partial-tether operations, and the climber mass limits during construction are unaddressed. If the 60% threshold is optimistic (e.g., 80% is more realistic), the revenue advantage shrinks substantially.
- **Fix:** Sweep the operational threshold (e.g., 50%, 60%, 70%, 80%, 90%) and report the NPV sensitivity. This would show how robust the modular advantage is to the phased-construction assumption.

### MINOR

**m1. Counterweight Mass Not Swept (§4.1)**
- The 600,000 kg counterweight is adopted from Edwards & Westling (2003). The paper notes ±50% → ±8% shift in T₁_trans but does not include this in the parametric sweeps. A single sensitivity plot would suffice.

**m2. Weibull Modulus m = 6 vs. Literature m ≈ 2.7 (§4.3)**
- Pugno & Ruoff (2006) report m ≈ 2.7 for CNT bundles. The paper acknowledges this and sweeps m ∈ {2.7–10}, but the baseline uses m = 6 without justification for why a value 2.2× the literature value is appropriate as default. The volume scaling at m = 2.7 increases λ_full by 6×.

**m3. Missing N = 83 in Exponential Baseline Sweep (§5.2.1)**
- The exponential baseline sweeps N ∈ {12, 15, 18, 21, 24, 50, 100, 200, 500} but omits N = 83 — the paper's own optimistic design point. It appears in the Weibull extension (§5.2.2) but not the exponential baseline. This means the headline exponential results at N = 83 are interpolated.

**m4. Damping Ratio Source (§5.3.2)**
- Zhang (2017) reports a loss tangent of ~0.045 for dry-spun CNT fibers, corresponding to ζ ≈ 0.023. The baseline ζ = 0.01 is below this value. The discrepancy is minor but should be noted: the baseline underestimates damping relative to the only cited source.

**m5. Formatting for Journal Submission**
- The manuscript contains markdown formatting artifacts (code blocks for equations, figure references as file paths). These must be converted to proper LaTeX equation environments and figure floats for Acta Astronautica submission. The note at the top acknowledges this, but the current draft needs significant reformatting.

---

## 5. Verification Results

Independent numerical checks on the paper's key claims:

| Claim | Paper Value | Verified Value | Status |
|-------|------------|----------------|--------|
| I_geo (surface→GEO) | 4.84 × 10⁷ m²/s² | 4.84 × 10⁷ | ✓ (but bounds mislabeled as surface→tip) |
| T_r at σ=100, ρ=1300 (Edwards) | 1.88 | 1.88 | ✓ |
| T_r at σ=46.5, ρ=2200 (Pearson) | 9.88 | 9.92 | ✓ (within rounding) |
| T_r at σ=50, ρ=1300 (optimistic) | 3.52 | 3.53 | ✓ |
| T_r at σ=25, ρ=1300 (conservative) | 12.40 | 12.45 | ✓ |
| T_r at σ=21.5, ρ=1631 (Popescu) | 39.4 | 39.59 | ✓ |
| Wave speed c = √(25e9/1300) | 4,385 m/s | 4,385.3 m/s | ✓ |
| Pendulum period T₁ = 4L/c | 25.3 h | 25.3 h | ✓ |
| Traversal time at 150 m/s | 185 h | 185.2 h | ✓ |
| Expected wait (half traversal) | 93 h | 92.6 h | ✓ → confirms binding constraint |
| Volume ratio V_sleeve/V_coupon | 6,000× | 6,000× | ✓ |
| Weibull scale factor (m=6) | 4.3× | 4.26× | ✓ |
| λ_fullscale | 5.2 × 10⁻⁸ h⁻¹ | 5.12 × 10⁻⁸ | ✓ |

**All numerical values verify correctly.** The sole discrepancy is the labeling of the integral bounds (surface→tip written where surface→GEO is meant), which is a textual error, not a computational one.

---

## 6. Missing or Weak Points

1. **No experimental validation of any kind.** Every physical parameter in the reliability model (η_j, Q, m, λ_coupon, τ_s, ζ) is assumed. This is acknowledged but should be more prominently framed as a boundary on the paper's claims — the paper is a parametric design study, not a validated feasibility assessment.

2. **No out-of-plane dynamics.** The 2D model captures in-plane longitudinal and transverse motion but omits out-of-plane (lateral) dynamics, torsion, and ribbon finite-width effects. For a meter-wide ribbon, aerodynamic flutter below 200 km and solar radiation pressure torques could excite out-of-plane modes not captured here.

3. **No debris/micrometeoroid impact model.** The hazard rate model addresses diffusion-controlled void growth but not impact-induced damage, which is a primary failure mode for long-duration orbital structures. The ORDEM/MASTER debris flux at LEO-GEO altitudes should at least be cited for context.

4. **No manufacturing defect model.** The Weibull volume scaling addresses statistical strength variability but not systematic manufacturing defects (e.g., splice misalignment, incomplete curing, contamination). These are likely dominant failure modes for first-generation CNT sleeve couplers.

5. **No thermal cycling fatigue.** The 3-zone thermal model uses static temperatures. LEO eclipse cycling (250–350 K every 90 minutes below 2,000 km) imposes thermal fatigue on joints that could significantly accelerate void growth beyond the Arrhenius steady-state prediction.

6. **No comparison with the Penoyre & Sandford (2019) "Spaceline" alternative.** The paper cites this Moon-anchored concept as "feasible with existing materials" but does not compare its economics or reliability against the modular CNT tether, which would provide valuable context.

7. **Cascade model assumes only adjacent failures matter.** The load redistribution model triggers system loss on two adjacent joint failures. In practice, a failed joint redistributes load to all neighboring segments (not just the two immediate neighbors), and the redistribution pattern depends on the shear-lag length. A more detailed load-path analysis could reveal non-adjacent cascade modes.

---

## 7. Questions for Authors

1. **Which stress-hazard reference efficiency was actually used in the Monte Carlo simulations?** The code uses `(0.97/η_j)⁴` while the paper states `(0.95/η_j)⁴`. Were the published reliability surfaces generated with 0.97 or 0.95? If 0.97, please update the paper's equation; if 0.95, the simulations need re-running.

2. **Why were the `repair_infrastructure/run_all.py` and `sensitivity_analysis.py` scripts excluded from the repository?** Are pre-computed outputs in `data/processed/` sufficient for reproducibility, or were these scripts lost during development? Can they be reconstructed and committed?

3. **What is the basis for Q = 1.1 eV beyond the single SnAg/Cu solder citation (Chen et al., 2010)?** CNT nano-solder void growth may have fundamentally different kinetics than bulk Sn-Ag-Cu electromigration. Have the authors considered that the activation energy for CNT-metal interface diffusion could be substantially lower (Q < 0.8 eV), which would invalidate the entire reliability framework?

4. **How sensitive is the NPV crossover to the 60% operational threshold?** If certification requirements push the threshold to 80% or 90%, does the modular architecture still outperform monolithic? A threshold sweep would strengthen the economic argument considerably.

5. **Why is the monolithic baseline modeled with a flat annual failure probability rather than a degradation model comparable in sophistication to the modular Weibull-cascade framework?** The asymmetric treatment creates a structural bias toward the modular architecture. Would the NPV advantage survive if the monolithic tether received a similar Arrhenius-Weibull treatment?

6. **Can the authors bound the effect of the omitted transverse gravity-gradient stiffness more tightly?** The 3,000× stiffness ratio is compelling far from GEO, but the ±1,000 km exclusion zone around GEO is where joints are densest (due to the taper profile). How many joints fall within this zone, and what is the maximum local frequency error?

7. **What happens to the Weibull age-dependent model beyond 10 years?** The paper notes that β > 1 "paradoxically improves" 10-year survival but creates a "cliff in extended-life scenarios." Has any simulation been run to 20 or 30 years to quantify this cliff? Given the 30-year NPV horizon, this seems essential.

8. **Why was m = 6 chosen as the baseline Weibull volume modulus when the only CNT-specific reference (Pugno & Ruoff, 2006) reports m ≈ 2.7?** The volume scaling factor increases from 4.3× to 25.1× at m = 2.7 — a 6× change. While the paper shows robustness to this variation, the choice of baseline should be justified.

---

## 8. Sources Consulted

### Paper & Repository
- `paper.md` — manuscript under review (full text, 942 lines)
- `data/parameters.yaml` — centralized simulation parameters
- `simulations/monte_carlo/joint_reliability.py` — Monte Carlo implementation (stress-hazard coupling at lines 18, 213, 229, 245)
- `simulations/monte_carlo/phase1_weibull/config.py` — Weibull sweep configuration
- `modular-cnt-tether-research.md` — independent research evidence file

### Literature Verified Against
- Popescu & Sun (2018), arXiv:1804.06453 — bio-inspired bundle architecture
- Luo et al. (2022a), https://doi.org/10.3390/aerospace9050278 — segmented tether stress
- Luo et al. (2022b), https://doi.org/10.3390/aerospace9070376 — segmented tether stability
- Bai et al. (2018), https://doi.org/10.1038/s41565-018-0141-z — CNT coupon strength
- Niu et al. (2025), https://doi.org/10.26599/NR.2025.94907584 — continuous CNT fiber strength
- Gassend (2024), arXiv:2412.17198 — exponential tethers
- Bertalan et al. (2014), arXiv:1404.04584 — Weibull scaling instability
- Pugno & Ruoff (2006), https://doi.org/10.1063/1.2158491 — nanoscale Weibull modulus
- Chen et al. (2010), https://doi.org/10.1557/JMR.2010.0230 — SnAg/Cu activation energy

---

*End of review.*
