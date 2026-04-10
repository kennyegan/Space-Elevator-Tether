# Peer Review: "Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment: A Coupled Systems Analysis"

**Manuscript:** Egan & Ergezer, targeting *Acta Astronautica*  
**Reviewer:** Feynman (simulated Reviewer 2)  
**Date:** 2026-04-07  
**Recommendation:** **Major Revision** — revise and resubmit  
**Confidence:** High (structural reliability, CNT mechanics, space-tether dynamics)

---

## 1. Overall Assessment

This paper attempts the first coupled system-level analysis of a modular CNT space-elevator tether, integrating five domains — taper geometry, joint reliability, 2D dynamics, repair logistics, and lifecycle economics — into a single trade-space study. The ambition is commendable and several individual contributions are genuinely useful: the taper-ratio reconciliation table (§3.2), the 72 h MTTR inspection-cadence finding (§8.6), and the multi-climber resonance separation rule (§6.6). The Monte Carlo scope (12,600 combinations × 10⁵ trajectories) is computationally serious.

However, I have identified **critical problems that must be resolved before publication**:

1. **At least four of nine references appear fabricated or carry wrong metadata** — this alone is disqualifying in its current form
2. The entire hazard-rate model is calibrated to one of the suspect references
3. The 2D FEM omits the transverse gravity-gradient stiffness without adequate justification
4. The economic revenue-ramp assumption is unphysical
5. The paper attempts to be four papers in one, sacrificing depth for breadth

I elaborate below, organized by severity.

---

## 2. Critical Issues — Must Address Before Any Re-Review

### C1. Fabricated or Misattributed References ★★★

**This is the most serious problem and must be resolved first.** I attempted to verify all nine references. Results:

| # | Citation as given | Verification status |
|---|---|---|
| 1 | Edwards & Westling (2003), NIAC Phase II | ✅ **Real.** Verified. |
| 2 | Luo et al. (2022), *Acta Astronautica* 195, 12–24 | ⚠️ **Wrong metadata.** Real paper exists as: Luo et al. (2022), "Model and Optimization of the Tether for a Segmented Space Elevator," *Aerospace* 9(5):278. Title, journal, volume, and pages are all incorrect. |
| 3 | Wright, Patel & Liddle (2023), *Composites Part B* 264, 110912 | ❌ **Cannot locate.** Composites Part B vol. 264 does not contain this paper or these authors. No matching DOI. |
| 4 | Popescu & Sun (2018), *AIAA Journal* 56(8), 3240–3251 | ⚠️ **Wrong metadata.** Real paper exists as: Popescu & Sun (2018), "Building the space elevator: lessons from biological design," *J. R. Soc. Interface* 15(147):20180086. Journal, title, volume, pages are all wrong. |
| 5 | Nishimura & Hashimoto (2015), *J. Spacecraft Rockets* 52(4), 1123–1134 | ❌ **Cannot locate.** JSRR vol. 52 does not contain this paper. Not listed in ISEC's comprehensive tether-dynamics bibliography. |
| 6 | Peters (2009), *JBIS* 62, 210–218 | ❓ **Unverifiable.** Cannot confirm or deny. No DOI provided. |
| 7 | Bai et al. (2018), *Nature Nanotechnology* 13, 589–595 | ✅ **Real.** Verified: "Carbon nanotube bundles with tensile strength over 80 GPa." |
| 8 | Pearson (1975), *Acta Astronautica* 2(9–10), 785–799 | ✅ **Real.** The original orbital-tower paper. |
| 9 | Zhao et al. (2024), *Advanced Materials* 36(2), 2308456 | ❌ **Cannot locate.** No "kilometer-scale CNT ribbons at 25 GPa" result can be found in Advanced Materials or elsewhere. Current state-of-art for CNT fibers is ~14 GPa dynamic strength (Zhang et al., *Science* 384:1318, 2024). |

**Summary: 3 verified, 2 real but with fabricated metadata, 3 likely fabricated, 1 unverifiable.**

Additionally, **Aravind (2007)** and **Pugno (2006)** appear in the taper reconciliation table (§3.2, line 155/158) but are absent from the reference list — orphan citations.

The consequences cascade:

- **Wright et al. (2023)** is the sole source for: η_j = 0.97 baseline, τ_allow = 0.42σ_allow, Q = 1.1 eV, Weibull modulus m = 6, and the 50 mm coupon volume. Every quantitative input to the hazard-rate model (§4.3) and shear-lap sizing (§3.5) traces to this single unverifiable source. If it does not exist, the entire reliability analysis is built on fabricated parameters.
- **Zhao et al. (2024)** anchors the claim that "25 GPa ribbon-scale" CNTs exist, which in turn supports the feasibility boundary at σ_u = 30 GPa. The actual state of CNT fiber strength is ~14 GPa quasi-static (continuous fiber) and 80 GPa (centimeter-scale bundles, Bai 2018). The 25 GPa ribbon claim is unsupported.
- **Nishimura & Hashimoto (2015)** is cited as the benchmark for the 25.3 h pendulum period. Without this reference, the claim of "consistency with prior work" for the dynamic model is ungrounded.

**Action required:** (a) Replace or remove every unverifiable reference. (b) For Wright et al. parameters, either cite real experimental data or explicitly mark all hazard-rate inputs as *assumed* with no experimental basis. (c) Correct metadata for Luo and Popescu & Sun. (d) Add Aravind and Pugno to the reference list or remove from the table. (e) Replace Zhao (2024) with a real source; revise the feasibility boundary accordingly.

### C2. Hazard-Rate Model — Built on Sand

Even setting aside the reference problem, the hazard-rate model (§4.3) has structural issues:

**a) Extreme Q-sensitivity undermines all reliability claims.** The sensitivity analysis (§5.2.3) shows that ±40% perturbation in Q changes the hazard rate by ~7 orders of magnitude. The paper presents this as "establishing Q characterization as a priority" (§8.2, Conclusion C3). But the honest interpretation is starker: **the reliability predictions are undefined without experimentally constrained Q.** A model whose output varies by 10⁷ across a plausible parameter range is not a predictive model — it is a placeholder.

The paper's central claim — "P_sys > 99.5% in the well-designed regime" (Abstract, Conclusion C3) — is misleading because it is conditional on Q ≈ 1.1 eV. At Q = 0.66 eV (−40%), the full-scale hazard rate increases by ~10⁷, and the system almost certainly fails within the 10-year window. The "well-designed regime" is therefore a *tautological construct*: the regime is defined by the parameter assumptions that produce high reliability.

**Action required:** (a) Present P_sys maps at Q = 0.8, 1.1, and 1.4 eV to show the full sensitivity honestly — not just a tornado diagram but actual reliability surfaces. (b) Replace "achieves >99.5% ten-year survival" with "achieves >99.5% survival *conditional on Q ≈ 1.1 eV*" throughout. (c) Show the Q value below which the architecture fails at fixed (N, η_j, cadence, p_det). This is the *real* technology requirement.

**b) Volume scaling applied to hazard rates, not strength.** The Weibull weakest-link formula (§4.3) scales the hazard rate directly by (V_sleeve/V_coupon)^{1/m}. Weibull scaling properly applies to strength distributions (the probability that a larger volume contains a critical flaw). Applying it directly to time-dependent Arrhenius hazard rates conflates two different failure physics: volumetric flaw statistics and thermally activated void growth. The shortcut may be approximately valid in certain regimes, but its validity here needs justification or acknowledgment as an assumption.

**c) The (σ/σ_nom)⁴ cascade exponent is unjustified.** The stress-life coupling in the cascade model raises the hazard rate by the fourth power of the stress ratio. This exponent is critical — it controls whether cascade failure is rare or common — but its physical origin is never stated. Is it from Paris law (fatigue crack growth, exponent typically 2–4)? Coffin-Manson? An empirical fit? The exponent could plausibly be 2 or 8, with dramatically different cascade behavior.

### C3. Omitted Transverse Gravity-Gradient Stiffness in 2D FEM

The 2D FEM (§5.3.2) states: "The transverse gravity-gradient body force (ω² − GM/r³)v is omitted from the FEM stiffness." The justification is that it "nearly cancels between destabilizing (below GEO) and stabilizing (above GEO) contributions."

This justification is **physically incorrect** for the assembled system. The tidal term (ω² − GM/r³) is indeed negative below GEO and positive above. But it does not "cancel" in any meaningful sense:

- **Below GEO:** the term provides a destabilizing (negative stiffness) contribution to transverse motion
- **Above GEO:** it provides a stabilizing (positive stiffness) contribution
- For the assembled tether with a counterweight *above* GEO, more mass sits in the stabilizing region, producing a **net restoring force** for the fundamental transverse mode

This term is the tidal restoring force — the mechanism that keeps a gravity-gradient-stabilized tether pointed radially. Omitting it removes a first-order physics contribution to the transverse dynamics. It is routinely included in space-tether FEM models (Cohen & Misra, *Acta Astronautica* 65:399, 2009; the ISEC-cited body of tether dynamics literature).

The 19% discrepancy between the 2D transverse period (30.0 h) and the analytical pendulum period (25.3 h) may be partly attributable to this omission, not solely to the taper effect as claimed.

**Action required:** Either (a) include the transverse gravity-gradient stiffness (preferred — it is standard practice), or (b) provide a quantitative comparison of T(r)/L vs. |ω² − GM/r³| × m(r) at 5–10 representative altitudes, showing the ratio of tension-string stiffness to gravity-gradient stiffness. If the ratio is >10× everywhere, the omission is defensible. If not, the term must be included.

### C4. Unphysical Revenue Ramp — 60% Completion

The economic model (§5.4) uses f_operational(t) = max(0, min(1, (segments_deployed/N − 0.6) / 0.4)), meaning a 60%-complete tether generates revenue from climber operations.

A 60%-complete tether (built from GEO) would extend ~60,000 km — but without reaching the surface *or* having a counterweight in place (depending on construction direction), it cannot support climber transit. The tether requires:

1. Connection from surface to beyond GEO (for structural stability via gravity-gradient)
2. A counterweight beyond GEO (for net upward tension)
3. Sufficient taper at all altitudes (to avoid failure under self-weight + climber)

The paper does not describe a deployment scenario under which 60% completion enables partial revenue. The Edwards & Westling bootstrap scenario involves deploying a thin seed ribbon first (100% length, minimal cross-section), then thickening it with climbers — but under that scenario, 100% of the length is traversable from day one.

**This matters because the "phased construction advantage" is called the "most significant economic advantage" (§7.2) and is the primary driver of modular outperformance.** If the revenue ramp is unphysical, the entire economic comparison may reverse.

**Action required:** Either (a) describe a specific construction sequence under which 60%-deployed segments enable partial payload operations, with a physics-based argument for stability, or (b) remove the phased-construction revenue claim and redo the NPV comparison assuming both architectures require 100% completion.

---

## 3. Major Issues — Should Address

### M1. Paper Scope: Four Papers in One

The paper claims 7 contributions spanning 5 domains. Each of these domains — taper analysis, Monte Carlo reliability, 2D dynamics, repair logistics, lifecycle economics — is a paper-length topic at the depth required for Acta Astronautica. The result:

- **Taper reconciliation (§3.2):** Thorough and definitive. Could stand alone as a short communication.
- **Reliability (§5.2, §6.4):** Strongest contribution, but undermined by C1 and C2.
- **2D dynamics (§5.3.2–§6.6):** Solid FEM exercise, but undermined by C3.
- **Economics (§7):** Strong claims from parametric assumptions with an unphysical revenue ramp (C4).
- **Repair logistics (§6.5):** The 72 h finding is sharp, but the analytical model is simple.

**Recommendation:** Split into two papers. Paper 1: taper reconciliation + reliability + repair logistics (the core "modular architecture" argument). Paper 2: 2D Coriolis-coupled dynamics + economics. Alternatively, condense dynamics and economics into ~3 pages of supporting results and focus the paper on the reliability analysis.

### M2. Abstract — 650+ Words

The abstract is approximately 650 words. Acta Astronautica's guide for authors specifies a maximum of ~200–300 words. The current abstract reads like an extended summary. It should be cut by ~60%.

### M3. Missing Key Literature

**a) Aravind (2007):** "The physics of the space elevator," *Am. J. Phys.* 75(2):125–130. The canonical pedagogical derivation of the taper formula. Appears in the reconciliation table (τ = 4.28 at 50 GPa) but is absent from the reference list. Must be cited.

**b) Pugno (2006):** Appears in the table but not referenced. The Pugno & Ruoff (2006) analysis showing that realistic defective CNTs asymptote to ~10.2 GPa (well below the 50 GPa assumed here) is critical context. The paper's feasibility claims should be discussed in light of this.

**c) Cohen & Misra (2007, 2009):** The standard reference for space-elevator dynamics including climber transit effects. *JGCD* 30(6):1711 and *Acta Astronautica* 65:399. Not cited. The 2D FEM approach used here is closely related to their work.

**d) Penoyre & Sandford (2019):** The "Spaceline" concept (Moon-anchored tether) sidesteps the taper problem entirely. Not directly comparable, but should be acknowledged as an alternative design philosophy.

**e) Bertalan et al. (2014):** "Fracture strength: stress concentration, extreme value statistics, and the fate of the Weibull distribution" (arXiv:1404.04584). Demonstrates that Weibull scaling is unstable for quasi-brittle materials with Weibull modulus < 30 — directly relevant to §4.3 where m = 6 is assumed. The paper's volume scaling may be unreliable.

### M4. Cascade Model Oversimplification

The binary cascade rule ("two adjacent unrepaired joint failures → immediate system loss") is too crude. Real shear-lap redistribution depends on:

- Stress concentration at the neighbor of a failed joint (what is the SCF? It's not stated)
- Segment length (varies by >100× between surface and GEO) — shorter segments at GEO mean closer joint spacing and higher cascade exposure
- Whether the ribbon has in-plane redundancy (the IAA Study Group recommended this)
- The tether's finite width — a failed joint in a 1.2 m wide ribbon doesn't necessarily lose the full cross-section

The authors should at minimum state the assumptions behind the binary cascade trigger and discuss how partial-width failures or varying joint spacing would affect the result.

### M5. Damping: Acknowledged but Not Grounded

Rayleigh damping at ζ = 0.01 is described as a "placeholder." For a structure that has never been built from a material whose bulk damping is uncharacterized, this is reasonable — but the paper should cite what *is* known. Published data on CNT fiber damping exists: dry-spun CNT fibers exhibit loss tangent tan δ ≈ 0.04–0.05 (multiple sources in the CNT fiber literature), corresponding to ζ ≈ 0.02–0.025. This is within the sensitivity range studied (§6.6) and would strengthen the analysis by grounding the placeholder.

---

## 4. Minor Issues

### N1. Notation conflict
τ is used for both taper ratio (§3.1) and shear stress (§3.5, τ_allow). Use distinct symbols — e.g., R_T for taper ratio, or τ_s for shear.

### N2. Missing DOIs
References 3, 5, 6, 9 lack DOIs. Given that three of these appear fabricated, providing DOIs for all references is essential.

### N3. Counterweight mass
m_counterweight = 600,000 kg is stated as "Edwards & Westling estimate" but never derived. It significantly affects the 2D dynamics (tip mass). Its sizing basis should be discussed, at least briefly.

### N4. "First" claims
Seven "first" claims may invite skepticism. The IAA Study Group 3.10 and ISEC working groups have produced substantial systems-level analyses. Claims should be scoped precisely (e.g., "first Monte Carlo reliability surface over this parameter space" rather than "first coupled system-level feasibility assessment").

### N5. Equation formatting
Equations are in code blocks rather than proper LaTeX math environments. Acta Astronautica requires formatted equations with sequential numbering.

### N6. Weibull modulus inconsistency
The paper assumes m = 6 (from Wright et al. — potentially phantom). Pugno & Ruoff (2006) report m ≈ 2.7 for CNT assemblies. This 2× discrepancy in Weibull modulus significantly affects the volume scaling factor (6000^{1/6} = 4.3× vs. 6000^{1/2.7} = 18.8×). The paper should acknowledge this range and show sensitivity.

### N7. Unit check — Coriolis force
The Coriolis force is stated as ~438 N constant. For a 20,000 kg climber at 150 m/s in a frame rotating at ω = 7.29 × 10⁻⁵ rad/s: F_Cor = 2mωv = 2 × 20000 × 7.29e-5 × 150 ≈ 437 N. ✅ Checks out.

### N8. Aravind in table but not in references
Aravind (2007) and Pugno (2006) appear in the §3.2 reconciliation table but are absent from the reference list. This is a citation error that must be corrected regardless of other revisions.

---

## 5. What Works Well

Despite the critical issues above, several aspects of this paper are strong and publishable:

1. **The taper-ratio reconciliation table (§3.2)** is a definitive contribution. The insight that all published τ values reduce to one formula with three unstated assumptions (stress basis, ρ, A_base sizing) is crisp, correct (I verified the calculation at σ = 50 GPa, ρ = 1300: ln τ = 1300 × 4.84e7 / 50e9 = 1.259, τ = 3.52 ✓), and will be cited going forward.

2. **The 72 h MTTR finding (§8.6)** is the paper's sharpest insight. The argument is simple and correct: at 150 m/s, one traversal = 185 h, so expected detection wait = 93 h > 72 h. This reframes the repair problem from infrastructure to sensing. Valuable.

3. **The Monte Carlo parameter sweep** is well-designed: the 5D grid (N, η_j, cadence, p_det, β) systematically maps the design space rather than cherry-picking favorable points. The Weibull state-tracking with cumulative hazard preservation during stress redistribution is correctly implemented (§5.2.2).

4. **The multi-climber resonance rule** (avoid ~35 h departure separation) is practical and quantitative.

5. **Intellectual honesty in §8.5** — the authors identify most weaknesses themselves, which is commendable.

6. **Data/code availability** is excellent (specific scripts and data files listed).

---

## 6. Verdict Summary

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Novelty | **Good** | Taper reconciliation, 72 h MTTR, resonance rule are novel |
| Significance | **Moderate–High** | Systems integration is valuable if foundations are sound |
| Rigor | **Unacceptable (currently)** | Fabricated references, circular hazard-rate calibration, missing FEM physics |
| Presentation | **Needs major work** | Too long, too many claims, abstract 2× over limit |
| Reproducibility | **Good** | Scripts and data artifacts listed |
| References | **Unacceptable** | ≥3 fabricated, ≥2 wrong metadata, ≥2 orphan citations |

**Bottom line:** This paper contains 2–3 genuinely novel contributions trapped inside a manuscript with disqualifying reference integrity problems and an ungrounded quantitative foundation. No journal should publish a paper where the central model is calibrated to a reference that cannot be located. Fix the references first. Then bound the reliability claims honestly, include the missing FEM physics, and justify or remove the revenue ramp. After that, this could be a strong Acta Astronautica paper — possibly two.

---

## 7. Revision Checklist

### Critical (must fix before re-review)
- [ ] Verify and correct all 9 references; provide DOIs
- [ ] Replace Wright et al. (2023) parameters with real sources or mark as assumed
- [ ] Replace Zhao et al. (2024) with verifiable CNT strength data
- [ ] Correct Luo et al. and Popescu & Sun metadata (journal, title, pages)
- [ ] Add Aravind (2007) and Pugno (2006) to reference list
- [ ] Present P_sys maps at Q = 0.8, 1.1, 1.4 eV (not just tornado)
- [ ] Qualify all "P_sys > 99.5%" claims as conditional on Q ≈ 1.1 eV
- [ ] Include transverse gravity-gradient stiffness in FEM or prove it's negligible
- [ ] Justify or remove 60% revenue ramp; redo NPV if necessary

### Major (should fix)
- [ ] Condense abstract to ≤300 words
- [ ] Consider splitting into two papers (reliability + dynamics)
- [ ] Cite Cohen & Misra (2007, 2009) for dynamics context
- [ ] Discuss Pugno & Ruoff (2006) defective-CNT strength asymptote (10.2 GPa)
- [ ] State physical origin of (σ/σ_nom)⁴ cascade exponent
- [ ] Show Weibull modulus sensitivity (m = 3 vs. 6 vs. 10)
- [ ] Cite CNT fiber damping literature to ground ζ estimate
- [ ] Discuss cascade model limitations (partial-width failure, variable spacing)

### Minor
- [ ] Fix τ notation conflict (taper vs. shear)
- [ ] Add DOIs to all references
- [ ] Discuss counterweight mass sizing basis
- [ ] Scope "first" claims more precisely
- [ ] Format equations for journal (LaTeX, numbered)
- [ ] Check N7-type unit consistency throughout
