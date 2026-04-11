# Peer Review: Modular CNT Space-Elevator Tether — Revision Verification

**Paper:** Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment: A Coupled Systems Analysis  
**Authors:** Egan, K. & Ergezer, M.  
**Target venue:** *Acta Astronautica* (Elsevier)  
**Review date:** 2026-04-10  
**Review round:** 3 (final verification after npz regeneration)

---

## Overall Assessment

The authors have addressed all critical and major issues from the Round 1 review, plus the stale-data concern from Round 2. The `npv_results.npz` file was regenerated (Apr 10 23:13) at N=83, and now shows: crossover year = 5 across all launch cost scenarios, grid delta_NPV = $0.293B at baseline [launch=$1000, disc=7%, rev=$300] — exactly matching the paper's "$0.29B" claim and the independently computed `phase3_repair/npv_with_depots.csv`. The time series correctly shows modular NPV negative until year 20 (consistent with 7-year build and heavy upfront investment), with modular first exceeding monolithic at year 5 when partial revenue begins. Both architectures are equal at year 4 ($−1,158M), confirming the divergence point is the 60% completion threshold.

All four Round 1 critical issues are resolved: the NPV model uses N=83 with consistent data files, the longitudinal modal results match the CSV (10.22/10.46 h, +2.3% Coriolis shift), the Luo et al. (2022a) citation is corrected (56%, connecting platforms), and the Popescu residual is qualified (6.8%). The revision also produced two genuinely good additions — the Weibull volume-scaling theoretical framing (§4.3) and the structural caveat cross-referencing the 60% threshold against the tension perturbation (§7.2) — that go beyond fixing errors to improve the paper substantively.

The remaining issues are minor: a small λ_full rounding inconsistency (5.12 × 10⁻⁸ vs. 5.2 × 10⁻⁸ between two sections), four orphan figure PDFs, and the monolithic comparison asymmetry (adequately bounded by the P_fail_mono sensitivity sweep). None of these affect the paper's conclusions.

---

## Recommendation

**Accept with Minor Revisions** — The four critical issues are resolved, the archival data is now consistent, and the remaining items are cosmetic. Address the minor items below before final submission.

---

## Revision Verification

### Critical Issues (Round 1) — Resolution Status

| # | Issue | Status | Verification Evidence | Residual Concern |
|---|-------|--------|----------------------|-----------------|
| 1 | NPV model defaults to N=18; paper discusses N=83 | ✅ **Fixed** | `parameters.yaml` line 36: `N_baseline: 83`. `npv_results.npz` regenerated Apr 10 23:13 — grid delta_NPV at baseline [1,1,1] = $0.293B, matching paper's "$0.29B" and phase3 CSV. Time series: modular negative until yr 20, crossover at yr 5, both architectures equal at yr 4 ($−1,158M). Crossover year = 5 across all launch costs. | None. Fully resolved. |
| 2 | T₁ longitudinal: paper 7.65 h vs. CSV 10.22 h | ✅ **Fixed** | Paper §6.6 modal table now reads T₁_long = 10.22 h (no Coriolis) / 10.46 h (with Coriolis) / +2.3% shift, exactly matching `comparison_table.csv`. Physical narrative updated: "consistent with the weak coupling expected when the longitudinal stiffness is much larger than the transverse." | None. |
| 3 | Coriolis sign reversal: paper −7% vs. CSV +2.3% | ✅ **Fixed** | Paper now reports +2.3% period increase. Narrative correctly reframed from frequency increase to period increase due to weak coupling. Consistent with CSV data (10.22 → 10.46 h). | None. |
| 4 | Luo 2022a: "22% with sleeve couplers" → actual 56% with connecting platforms | ✅ **Fixed** | §2.1 now reads: "Luo et al. (2022a) demonstrated a 56% peak-stress reduction using 5–6 optimized segments with connecting platforms." §8.4 comparison table updated correspondingly. | None. |

### Major Issues (Round 1) — Resolution Status

| # | Issue | Status | Verification Evidence | Residual Concern |
|---|-------|--------|----------------------|-----------------|
| 5 | Popescu residual 6.8% glossed over | ✅ **Fixed** | §3.2 reconciliation table now states: "within 7%, with the largest residual (6.8%)... possibly reflecting different integration bounds or base-area conventions not fully documented in their paper." | None. Honest and appropriate qualification. |
| 6 | Weibull volume scaling lacks theoretical justification | ✅ **Fixed** | New paragraph in §4.3 distinguishes weakest-link strength scaling vs. time-dependent hazard rates, frames as engineering bound for initiation-limited failure, notes experimental full-scale data would supersede. Cites Bertalan et al. (2014) and demonstrates robustness at m = 2.7 with λ_full rising to 3.0 × 10⁻⁷ while maintaining P_sys ≥ 0.995 at η_j ≥ 0.80. | None. This is a genuinely good addition. |
| 7 | 60% threshold vs. 67% tension perturbation inconsistency | ✅ **Fixed** | §7.2 now includes explicit structural caveat cross-referencing §6.6 tension perturbation, notes SF=2 margin accommodates at full build-out but early-operation payloads may need reduction, and identifies partial-tether load capacity as unresolved design constraint. f_threshold sweep (0.5–0.9) confirms advantage persists. | None. Appropriately framed as open question. |
| 8 | Monolithic comparison asymmetry — no comparable-physics P_fail_mono | ⚠️ **Partially Fixed** | §7.5 sensitivity sweep over P_fail_mono ∈ {10⁻⁴–10⁻¹} exists. Paper correctly states "the economic case does not depend on the monolithic tether being unreliable." §8.5 limitation 5 now discusses what Arrhenius/Weibull would plausibly predict for a continuous ribbon. | Minor residual: no formal derivation of P_fail_mono from comparable physics. However, the sensitivity sweep adequately bounds the uncertainty, and the phased-construction argument dominates regardless. Acceptable as-is. |
| 9 | 2D joint compliance shift: paper 2.44% vs. CSV 0.0% | ✅ **Fixed** | §5.3.2 validation now correctly reports 0.0% 2D joint compliance shift with excellent physical explanation: "the transverse mode's tension-string stiffness is dominated by the gravity-gradient equilibrium tension T(r), which is independent of η_j, unlike the 1D elastic stiffness EA/L that is directly proportional to joint efficiency." | None. The physical reasoning is convincing. |

### Minor Issues (Round 1) — Resolution Status

| # | Issue | Status | Notes |
|---|-------|--------|-------|
| a | "19%" → actual 18.6% | ✅ Improved | Paper uses "~19%" with tilde. Acceptable rounding. |
| b | Niu et al. units conflation | ✅ Fixed | Now "4.1 N·tex⁻¹ tensile strength (≈5.3 GPa at ρ = 1,300 kg/m³)." |
| c | Penoyre "entirely" → "largely" | ✅ Fixed | §2.1 now reads "largely sidesteps." |
| d | λ_full three-way rounding | ⚠️ Improved | §4.3 formula gives 5.12 × 10⁻⁸; §5.2.1 calibration still says 5.2 × 10⁻⁸. Gap reduced but not eliminated (1.6%). Minor. |
| e | g inconsistency (9.81 vs. 9.798) | ⬜ Not addressed | Paper text uses 9.81 m/s²; code uses GM/R² = 9.798. 0.12% difference — negligible. |
| f | 4 orphan figure PDFs | ⬜ Not addressed | 41 PDFs in `paper/figures/` vs. 37 declared. 4 unreferenced files remain. |
| g | Paper length (~950 lines, 37 figures) | ⬜ Not addressed | Still exceeds typical *Acta Astronautica* length. Consider editorial condensation or moving additional material to supplementary. |
| h | Coriolis shift rounding (15.9% → 16%) | ⬜ Not addressed | CSV: 15.9%; paper: 16%. Acceptable rounding. |

---

## Remaining Issues (Minor Only)

1. **[Low — Consistency] λ_full rounding in §5.2.1.** The §4.3 derivation gives 5.12 × 10⁻⁸ h⁻¹; the §5.2.1 Arrhenius calibration states 5.2 × 10⁻⁸. The Arrhenius calibration loop absorbs this via the self-consistency check, but harmonizing the reported value or explicitly noting the calibration adjustment would improve clarity.

2. **[Low — Housekeeping] Remove 4 orphan PDF files** from `paper/figures/`: `fig_depot_cost_tradespace.pdf`, `fig_npv_crossover.pdf`, `fig_npv_with_depots.pdf`, `fig_weibull_mttr_depot_shift.pdf`. These are unreferenced in the text and Figure Index.

3. **[Low — Consistency] g = 9.81 vs. 9.798 m/s².** Paper text and code use different surface gravity values. Negligible quantitative impact but technically inconsistent. Either use g = GM/R² consistently or note the rounding convention.

4. **[Observation — Not blocking] Monolithic comparison asymmetry.** The sensitivity sweep adequately bounds this uncertainty. §8.5 limitation 5 now includes a qualitative physical argument. Adequate for publication.

---

## Strengths (Unchanged from Round 1)

1. **Genuine novelty** — first coupled five-element trade space (taper + reliability + logistics + dynamics + economics) for a segmented elevator tether. Confirmed by systematic literature search.
2. **Q-sensitivity analysis (§6.4)** — the paper's most important contribution. Hazard rate spanning 10 orders of magnitude across Q ∈ {0.8, 1.1, 1.4} eV reframes reliability from systems engineering to materials characterization.
3. **Taper reconciliation (§3.2)** — resolves a latent literature discrepancy; all published T_r values collapse onto one formula with three stated assumptions.
4. **Parametric discipline** — single locked `parameters.yaml` with verified exact match to Table 4.1.
5. **Honest limitation disclosure** (§8.5, §8.6) — unusually candid about conditional reliability predictions and the Q problem.
6. **Inspection-cadence insight** (§6.5.1) — non-obvious finding that 72 h MTTR is inspection-limited, not depot-limited.
7. **2D Coriolis-coupled FEM** with six validation checks — 16% transverse period shift is a genuine upgrade over 1D models.
8. **Multi-climber resonance rule** — actionable ±5 h avoidance window at ~35 h.

---

## New Observations

1. **New Weibull volume-scaling paragraph (§4.3) is excellent.** The distinction between initiation-limited (weakest-link) and propagation-limited (fracture mechanics) failure modes, combined with the demonstration that even at m = 2.7 the system maintains P_sys ≥ 0.995, is a substantive theoretical improvement that was not merely responsive to the critique but genuinely advances the analysis.

2. **Structural caveat in §7.2 is well-integrated.** Rather than a bolted-on disclaimer, the cross-reference to §6.6 tension perturbation is woven into the deployment narrative with the f_threshold sweep providing quantitative backup. The acknowledgment that "partial-tether load capacity" is an "unresolved design constraint" is appropriately scoped.

3. **§8.5 limitation 5 now includes a physical argument** about what Arrhenius/Weibull would predict for a monolithic ribbon ("the enormous volume... and absence of repair points would plausibly yield P_fail_mono near 1.0"). This is qualitative but directionally sound and addresses the Round 1 concern that the comparison was asymmetric.

4. **2D joint compliance explanation (§5.3.2) is physically convincing.** The observation that transverse mode stiffness is dominated by gravity-gradient tension T(r) — which is independent of η_j — explains the 0.0% shift cleanly. This is a better result than the originally claimed 2.44%, as it demonstrates that segmentation has essentially zero impact on the critical (transverse fundamental) mode.

5. **Phase3 repair data regeneration** (Apr 10) correctly reflects N=83 economics, with delta_NPV = $0.293B at baseline confirmed against the paper's "$0.29B" claim. The NPV sweep including depot costs is internally consistent.

---

## Verdict Summary Table

| Criterion | Rating (1–5) | Change from R1 | Notes |
|-----------|:---:|:---:|-------|
| Novelty | 4 | — | Unchanged. Coupled five-element trade space remains unique. |
| Technical Rigor | 4 | ↑ from 3 | All four critical data inconsistencies resolved. Modal table, Luo citation, NPV parameters and data all match. Weibull scaling and 60% threshold appropriately caveated. |
| Reproducibility | 5 | ↑ from 4 | `npv_results.npz` regenerated at N=83; grid values match phase3 CSV and paper to $0.001B. All data files now consistent with the manuscript. |
| Presentation | 4 | ↑ from 3 | Corrected modal table, Luo citation, and Popescu qualification restore credibility. New explanatory paragraphs (Weibull scaling, joint compliance) improve clarity. Still overlength for venue. |
| Significance | 4 | — | Q-sensitivity finding, taper reconciliation, and inspection-cadence insight remain the key contributions. Economic results credible and verified at N=83. |

**Overall: 4.2 / 5** (up from 3.6 in Round 1)

---

## Sources

**Paper and data artifacts (internal):**
- `paper.md` — revised draft (~950 lines)
- `data/parameters.yaml` — line 36: `N_baseline: 83` (confirmed fix)
- `data/processed/npv_results.npz` — Apr 10 23:13, regenerated at N=83 (grid delta_NPV = $0.293B, crossover_year = 5)
- `data/processed/phase3_repair/npv_with_depots.csv` — Apr 10, regenerated N=83 data (delta_NPV = $0.293B)
- `data/processed/phase3_repair/breakeven_analysis.csv` — Apr 10, regenerated
- `data/processed/phase2_dynamics/comparison_table.csv` — T₁_long = 10.22/10.46 h confirmed
- `data/processed/weibull_sweep_results.csv` — P_sys = 0.99995 at baseline confirmed
- `data/processed/Q_hazard_rate_table.csv` — 10-order-of-magnitude span confirmed
- `paper/figures/` — 41 PDFs (37 declared + 4 orphans)

**External literature verified (Round 1, still valid):**
- Bai et al. (2018): https://www.nature.com/articles/s41565-018-0141-z — 80 GPa CNT bundles ✓
- Luo et al. (2022a): https://doi.org/10.3390/aerospace9050278 — 56% stress reduction (now correctly cited) ✓
- Penoyre & Sandford (2019): https://arxiv.org/abs/1908.09339 — Spaceline characterization ✓
- Niu et al. (2025): https://doi.org/10.26599/NR.2025.94907584 — 4.1 N·tex⁻¹ (now correctly cited) ✓
- Chen et al. (2010): https://doi.org/10.1557/JMR.2010.0230 — Q = 1.06 eV for SnAg solder ✓
