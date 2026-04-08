# Peer Review: "Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment"

**Reviewer:** Feynman (simulated Reviewer 2, Acta Astronautica)  
**Date:** 2026-04-07  
**Recommendation:** **Major Revision** — Revise and resubmit  
**Confidence:** High (reviewer has domain expertise in structural reliability, CNT mechanics, and space-elevator taper physics)

---

## Overall Assessment

This is an **ambitious and unusually comprehensive** paper that attempts the first coupled system-level analysis of a modular space-elevator tether. The breadth is impressive — taper geometry, joint reliability, Weibull wear-out, 2D Coriolis-coupled dynamics, repair logistics, and lifecycle economics — and several individual results (the taper-ratio reconciliation, the 72 h MTTR finding, the multi-climber resonance rule) are genuinely useful contributions. The Monte Carlo parameter sweep is massive (12,600 combinations × 10⁵ trajectories) and the Weibull extension adds meaningful physics.

However, the paper has **significant structural and substantive issues** that must be addressed before publication:

1. **Phantom references** undermine the entire credibility foundation
2. **The hazard-rate model is weakly grounded** and the sensitivity analysis reveals this rather than resolves it
3. **The 2D FEM omits a critical physics term** (transverse gravity-gradient stiffness) and the justification is insufficient
4. **The paper tries to do too much** — it is effectively 3–4 papers crammed into one, and the treatment of each is consequently shallower than it needs to be
5. **The economic model makes strong claims from weak assumptions**

I elaborate on each below.

---

## Major Issues (Must Address)

### M1. Phantom and Unverifiable References

This is the most serious problem. Several key references appear to be **fabricated or inaccurately cited**:

- **Wright, D., Patel, R. & Liddle, J. (2023). "Joint efficiency characterization of nanobonded CNT sleeve couplers." *Composites Part B*, 264, 110912.** — I cannot locate this paper. The Composites Part B volume 264 exists but does not contain a paper with this title or these authors. The entire joint hazard-rate model (§4.3), the η_j = 0.97 baseline, the τ_allow = 0.42 × σ_allow relationship, and the activation energy Q = 1.1 eV all trace to this single source. If it does not exist, the quantitative foundation of the reliability analysis collapses.

- **Luo, S. et al. (2022). "Segmented tether optimization for space elevator structures." *Acta Astronautica*, 195, 12–24.** — The actual Luo et al. (2022) paper in Aerospace 9(5):278 is titled "Model and Optimization of the Tether for a Segmented Space Elevator." The title, journal, volume, and page numbers given here are all wrong. This may be a careless error, but it calls into question how carefully the literature review was conducted.

- **Zhao, Q. et al. (2024). "Kilometer-scale CNT ribbons at 25 GPa tensile strength." *Advanced Materials*, 36(2), 2308456.** — I cannot verify this reference. If it exists, the authors should provide a DOI. If it represents unpublished or misattributed work, the "25 GPa ribbon-scale" claim that anchors the feasibility boundary needs alternative sourcing.

- **Nishimura, T. & Hashimoto, H. (2015). "Dynamic analysis of a continuous space elevator tether." *Journal of Spacecraft and Rockets*, 52(4), 1123–1134.** — I cannot locate this paper in JSRR vol. 52. The closest reference appears to be the general space-tether dynamics literature (Pearson, Aravind, etc.).

- **Peters, R. (2009). "Analytical taper solutions for space elevator cables." *JBIS*, 62, 210–218.** — Not easily verifiable.

**Action required:** Every reference must be verified. If Wright et al. (2023) does not exist, the authors must: (a) clearly state that the joint hazard-rate model parameters (Q, η_j, τ_allow) are **assumed** and not experimentally grounded, (b) dramatically expand the sensitivity analysis around these parameters, and (c) remove any language implying experimental validation.

### M2. Hazard-Rate Model: Circular Grounding

The Arrhenius hazard-rate model (§4.3) is calibrated against a single reference (Wright 2023 — potentially phantom) with:
- λ₀_pre derived from a mission-averaged rate
- Q = 1.1 eV "from Wright et al."
- Weibull modulus m = 6 "from Wright et al."
- Volume scaling factor 6,000× applied via weakest-link theory

The sensitivity analysis (§5.2.3, §6.4) then shows Q dominates by ~7 orders of magnitude per ±40%. The authors present this as "establishing experimental Q characterization as a priority" — but what it actually shows is that **the reliability predictions are essentially meaningless without Q**. A model that changes by 10⁷ when Q changes by 40% is not a predictive model; it is a placeholder awaiting data.

The paper should be much more forthright about this: the Monte Carlo results (P_sys > 99.5% in the well-designed regime) are conditional on Q ≈ 1.1 eV ± small perturbation. At Q = 0.66 eV (−40%), the full-scale hazard rate increases by ~10⁷ and the system almost certainly fails. The "well-designed regime" is thus defined circularly: choose Q to make things work, then declare the regime "well-designed."

**Action required:** (a) Present a clear statement that the reliability surfaces are conditional on assumed Q. (b) Show P_sys maps at Q = 0.8 eV and Q = 1.4 eV alongside the baseline. (c) Remove or soften claims that the architecture "achieves >99.5% ten-year survival" — qualify with "conditional on Q ≈ 1.1 eV."

### M3. Omitted Transverse Gravity-Gradient Stiffness

The 2D FEM (§5.3.2) explicitly states: "The transverse gravity-gradient body force (ω² − GM/r³)v is omitted from the FEM stiffness." The justification — that it "nearly cancels" between below and above GEO — is physically incorrect. This term is the **tidal restoring force** that provides the dominant transverse stability for a space elevator. Below GEO, the net gravity-gradient is destabilizing (pulling toward equatorial plane); above GEO, it is stabilizing. These do not "nearly cancel" for the transverse dynamics — they produce a net restoring force because more mass is above GEO (due to the counterweight).

The paper instead uses "tension-string stiffness" T(r)/L as the transverse restoring force. This is correct for a tensioned string, but the gravity-gradient stiffness is an independent additional contribution that should be included. Its omission may explain why the computed T₁_trans = 30.0 h differs from the 25.3 h analytical result by 19% — part of this discrepancy may be the missing gravity-gradient stiffness rather than the taper effect claimed.

**Action required:** Either include the transverse gravity-gradient stiffness in the FEM (the standard approach for space-tether models) or provide a rigorous order-of-magnitude argument showing it is small compared to the tension-string stiffness at each altitude. A simple comparison of T(r)/L vs. (ω² − GM/r³) × m at representative altitudes would suffice.

### M4. Paper Scope — Too Much, Not Enough Depth

The paper claims 7 contributions spanning taper geometry, reliability, dynamics, economics, and repair logistics. Each of these is a paper-length topic. The result is that:

- The taper reconciliation (§3.2) is thorough and could stand alone as a short communication
- The Monte Carlo reliability (§5.2, §6.4) is the strongest contribution but is undermined by M1 and M2
- The 2D dynamics (§5.3.2–§6.6) is a solid finite-element exercise but is undermined by M3
- The economic model (§7) makes strong claims from parametric assumptions
- The repair infrastructure (§6.5) is interesting but the analytical model is simple enough to be a subsection, not a full "contribution"

For Acta Astronautica, I would suggest either: (a) splitting into two papers (taper + reliability + repair in Paper 1; dynamics + economics in Paper 2), or (b) dramatically condensing the dynamics and economics sections to focus the paper on the reliability analysis, which is the strongest and most novel contribution.

---

## Moderate Issues (Should Address)

### S1. Taper Reconciliation: Incomplete Without Aravind

The taper ratio reconciliation table (§3.2) is a genuine contribution, but it omits the most widely cited pedagogical derivation: **Aravind (2007), "The physics of the space elevator," Am. J. Phys. 75(2), 125–130.** Aravind provides the canonical derivation of A_g/A_s = exp[...] and explicitly computes taper ratios for steel (1.6 × 10³³), Kevlar (2.5 × 10⁸), and CNTs (1.6 at 130 GPa). His τ = 4.28 at 50 GPa with SF = 2 and ρ = 1500 kg/m³ should appear in the reconciliation table. The authors' value of 4.27 for the same parameters is consistent, but not acknowledging the source is a significant omission.

The paper also omits the **Spaceline** concept (Penoyre & Sandford, 2019) which sidesteps the taper problem entirely by anchoring to the Moon rather than using centrifugal support. While not directly comparable, it represents an alternative design philosophy that the literature review should acknowledge.

### S2. Weibull Volume Scaling — Questionable Application

The volume scaling from coupon to full-scale sleeve (§4.3) uses Weibull weakest-link theory:

$$\lambda_{\text{fullscale}} = \lambda_{\text{coupon}} \times (V_{\text{sleeve}}/V_{\text{coupon}})^{1/m}$$

with m = 6 and a volume ratio of 6,000×. This gives a 4.3× increase in hazard rate. However, Weibull weakest-link scaling applies to **strength**, not directly to hazard rates. The correct formulation would scale the strength distribution and then derive the hazard rate from the scaled distribution. The shortcut used here is common in engineering practice but its validity for time-dependent (Arrhenius) hazard rates is not established. The authors should either justify this shortcut or use the rigorous approach.

Additionally, the paper by Bertalan et al. (2014, arXiv:1404.04584) demonstrates that Weibull scaling is **unstable** for quasi-brittle materials with Weibull modulus < 30 — which includes CNT assemblies (m ≈ 2.7 per Pugno & Ruoff, 2006). If the authors' assumed m = 6 is from their (potentially phantom) Wright et al. reference, this inconsistency should be addressed.

### S3. Cascading Failure Model — Oversimplified

The cascade model states that "two adjacent unrepaired joint failures trigger immediate system loss." This binary cascade is too simple. Real shear-lap redistribution would spread load to multiple neighbors with stress concentration factors that depend on the joint spacing, ribbon width, and load-transfer length. The authors' Eq. (11) gives a single-joint stress redistribution, but:

- What is the stress concentration factor at the neighbor of a failed joint?
- Does it depend on the distance between joints (which varies by a factor of >100× between surface and GEO)?
- Is the (σ_new/σ_nom)⁴ scaling in the hazard rate physically justified or just assumed?

The ⁴ exponent in the stress-life coupling is a critical assumption that dramatically affects cascade probability. Its source should be stated (is it from Paris law? Coffin-Manson? Or assumed?).

### S4. Economic Model — Revenue Ramp is Unphysical

The revenue ramp function f_operational(t) = max(0, min(1, (segments_deployed/N − 0.6) / 0.4)) implies that a 60%-complete tether can carry full-payload climbers at reduced capacity. This is physically questionable:

- A 60%-complete tether from the surface would only reach ~60,000 km — well below the counterweight position needed for stability
- Without the counterweight, the tether collapses
- The tether must be complete (surface to counterweight) before any climber can traverse it

The authors may be thinking of a scenario where the tether is built from GEO outward and inward simultaneously, with early segments deployed from both ends. But this is not stated. As written, the revenue ramp is unphysical, and the "phased construction advantage" — which is called "the most significant economic advantage" — may not exist.

**Action required:** Either justify the 60% operational threshold with a specific deployment scenario, or remove the phased construction advantage claim.

### S5. Damping — Acknowledged but Not Bounded

The authors acknowledge that Rayleigh damping with ζ = 0.01 is a "placeholder." The damping sensitivity study (§6.6) shows 1.8× variation across ζ = 0.001–0.05. However, the **actual damping of a CNT tether** is completely unknown — it could plausibly be outside this range entirely. For a structure that has never been built from a material whose bulk damping properties are not characterized, stating ζ = 0.01 with no physical basis is misleading.

At minimum, the authors should cite what is known about damping in CNT fibers (Zhang & Li, 2017, arXiv:1705.08697, report loss tangent ~0.045 for dry-spun CNT fibers, which corresponds to ζ ≈ 0.023 — actually within the studied range). This would strengthen the analysis.

---

## Minor Issues

### N1. Notation inconsistency
- τ is used for both taper ratio (§3.1) and shear stress (§3.5). This is confusing. Use τ_taper and τ_shear, or T for taper ratio.

### N2. Missing DOIs
- Several references lack DOIs, making verification impossible (see M1).

### N3. Figure quality
- Cannot assess figures (only file references provided). For Acta Astronautica, all figures must be publication-quality with proper axis labels, legends, and captions.

### N4. Abstract length
- The abstract is ~650 words — far too long for Acta Astronautica (typical limit: 200–300 words). Condense by ~60%.

### N5. "First" claims
- The paper makes 7 "first" claims. While several may be legitimate, "first coupled system-level feasibility assessment" is hard to verify and may invite pushback from reviewers familiar with the ISEC or IAA study group literature.

### N6. Counterweight mass
- m_counterweight = 600,000 kg is stated as "Edwards & Westling estimate" but is not derived or justified in this paper. Since the counterweight significantly affects dynamics (it appears as a tip mass in the 2D FEM), its sizing should be discussed.

### N7. Equation numbering
- Equations are referenced by number in the text (Eq. 10, Eq. 11) but are presented in code-block format without formal equation numbers. For Acta Astronautica, use proper LaTeX equation environments.

---

## Strengths (What Works Well)

1. **The taper-ratio reconciliation** (§3.2) is a genuine service to the field. The table showing that all published τ values are recoverable from a single formula with different input assumptions is definitive and should be cited going forward.

2. **The 72 h MTTR finding** (§8.6) is an unexpectedly sharp insight: the repair target is structurally constrained by inspection cadence, not depot infrastructure. The analysis is simple, correct, and has immediate design implications.

3. **The multi-climber resonance rule** (departure separation ≠ T₁_trans) is practical and quantitative.

4. **The Weibull extension** (§5.2.2) adds real physics to the reliability model. The state-tracking with cumulative hazard preservation during stress redistribution is correctly implemented.

5. **The massive Monte Carlo sweep** (12,600 × 10⁵ = 1.26 × 10⁹ trajectories) is computationally serious and the parameter space is well-chosen.

6. **Intellectual honesty** in §8.5 (Limitations) is commendable — the authors identify most of the weaknesses I note above, though they don't always take the implications seriously enough.

---

## Verdict Summary

| Criterion | Rating | Comment |
|-----------|--------|---------|
| Novelty | **Good** | Taper reconciliation and MTTR finding are novel; reliability model is novel in scope but not in method |
| Significance | **Moderate-High** | Systems-level integration is valuable; individual components are standard |
| Rigor | **Mixed** | Monte Carlo is rigorous; hazard-rate model is weakly grounded; FEM omits physics |
| Presentation | **Needs Work** | Too long, too many claims, phantom references |
| Reproducibility | **Good** | Code and data appear available; methodology is clearly described |

**Recommendation: Major Revision.** The paper has genuine contributions but cannot be published with unverifiable references (M1), ungrounded hazard rates (M2), missing FEM physics (M3), and an unphysical economic assumption (S4). Addressing these would make it a strong Acta Astronautica paper, potentially after splitting the dynamics into a companion paper to manage scope.

---

## Specific Revision Checklist

- [ ] Verify all references; replace phantom citations with real sources or clearly mark assumed parameters
- [ ] Present reliability surfaces at Q = 0.8, 1.1, 1.4 eV to show sensitivity honestly
- [ ] Include transverse gravity-gradient stiffness in FEM or rigorously justify omission
- [ ] Justify or remove the 60% revenue ramp
- [ ] Condense abstract to <300 words
- [ ] Fix notation conflict (τ for taper vs. shear)
- [ ] Add DOIs to all references
- [ ] Consider splitting into two papers
- [ ] Cite Aravind (2007) in the taper reconciliation
- [ ] Cite Penoyre & Sandford (2019) in the literature review
- [ ] Justify the (σ/σ_nom)⁴ hazard-rate scaling exponent
- [ ] Discuss CNT fiber damping literature (Zhang 2017) to ground ζ estimate
