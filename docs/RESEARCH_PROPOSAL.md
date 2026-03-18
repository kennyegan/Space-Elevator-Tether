# Research Proposal: Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment

**Target Journal:** Acta Astronautica (Elsevier) — Q1 Aerospace Engineering, IF 3.4, h-index 114  
**Lead Author:** Kenneth Egan, Wentworth Institute of Technology  
**Advisor:** M. Ergezer  
**Submission Portal:** https://www.editorialmanager.com/aastronautica/default.aspx  
**Author Guidelines:** https://www.sciencedirect.com/journal/acta-astronautica/publish/guide-for-authors  

---

## 1. Problem Statement

Earth-to-orbit transportation costs $2,000–$4,000/kg via chemical rockets, with ~400 t CO₂-equivalent per launch. A space elevator — a continuous tether from an equatorial anchor through GEO (35,786 km) to a counterweight beyond 100,000 km — could reduce launch costs by 1–2 orders of magnitude using electrically powered climbers with zero propellant.

The linchpin is the tether. Analytic tapering requires specific tensile strength exceeding 45 GPa·cm³/g over ~100,000 km. Carbon-nanotube yarns now achieve 80 GPa on centimeter gauges and 25 GPa on meter-scale ribbons at kilometer-per-day production rates, narrowing the gap to within a factor of two.

**The core problem is not materials — it is architecture.** Every published elevator design assumes a defect-free monolithic CNT ribbon. This assumption:

1. Demands planetary-scale manufacturing perfection with zero defect propagation over 100,000 km
2. Offers no mechanism to replace sections damaged by micrometeoroids, debris, or radiation
3. Prevents incremental deployment, in-service upgrades, or phased construction
4. Makes the entire system a single point of failure

No published study has quantified joint reliability and load-path continuity in a segmented CNT tether at system level.

---

## 2. Research Gap

| Research Thread | State of the Art | What's Missing |
|----------------|-----------------|----------------|
| Tether architecture | Luo et al. (2022): 22% stress reduction with segmentation; Popescu & Sun (2018): bio-inspired bundle repair | No system-level quantification coupling joint reliability × segment count × repair logistics |
| CNT mechanics | 80 GPa lab samples (Bai 2018), 25 GPa km-scale ribbons (Zhao 2024) | Gap between lab and 100,000-km production not addressed with engineering knock-down factors |
| Tether dynamics | Pendulum periods, climber harmonics, active damping well-modeled | Joint compliance effects on segmented tether stability not quantified |
| Deployment | Edwards' GEO-down bootstrap established | No study sizes prefabricated mass-equalized variable-length modules |
| Risk/repair | Redundant multi-strand ribbons, robotic inspection proposed conceptually | Mean-time-to-repair never validated; no Monte Carlo coupling joint failure to system availability |
| Economics | $10–100B estimates, <$300/kg projections | No lifecycle NPV integrating modular repair costs vs. monolithic replacement |

**This research fills the gap:** A rigorous coupled system-level analysis integrating modular tether geometry, joint reliability, dynamic stability, repair logistics, and lifecycle economics — demonstrated through validated simulation.

---

## 3. Research Objectives

### Primary

**O1.** Design a modular CNT tether whose variable-length segments satisfy static and dynamic load envelopes with safety factor ≥ 1.5 under worst-case combined loading.

**O2.** Quantify system-level failure probability as a function of joint efficiency (η_j), segment count (N), and inspection cadence through Monte Carlo simulation — establishing minimum η_j thresholds for 99.9% ten-year system survival.

**O3.** Validate the modular stress profile against the Edwards & Westling (2003) NIAC monolithic baseline, demonstrating segmented architecture closes feasibility at ≤ 4% mass penalty.

**O4.** Develop a lifecycle cost model comparing modular vs. monolithic architectures, quantifying the economic crossover where repair-in-place outperforms full replacement.

### Secondary

**O5.** Perform material sensitivity analysis across σ_u = 30–70 GPa, demonstrating robustness to near-term CNT performance (not only aspirational 50 GPa targets).

**O6.** Map TRL for each subsystem, identifying binding constraints for deployment timeline.

---

## 4. Methodology

### 4.1 Analytical Framework (Existing — §§3–4 of current draft)

Already derived from first principles:
- GEO anchor placement from Keplerian mechanics
- Exponential taper profile A(y) via uniform-stress design: σ_allow = σ_u · χ_rad · η_j / SF
- Variable-length segmentation: L_j = m★ / (ρ · A(y_j,mid)), equalizing segment mass at m★ = 18 t
- Shear-lap joint sizing: ℓ_min = T_j / (2b · τ_allow), yielding 3.0 m sleeves at 35 kg
- N = 18 segment baseline architecture

### 4.2 Finite-Element Stress Validation (To build — §5)

- 1D beam-element model of full 100,000 km tether (Python NumPy/SciPy or ANSYS)
- Gravity-gradient + centrifugal loading as distributed body forces
- Joint interfaces as spring elements: k_j = η_j · E · A / ℓ
- Mesh convergence study: 1 km down to 10 m near joints
- **Validation target:** Match Edwards & Westling (2003) peak tension location and magnitude to < 2%

**Key outputs:** σ(y) profile overlaid on NIAC prediction; joint stress concentration factors; stepped vs. continuous taper deviation (target Δσ/σ < 1%)

### 4.3 Monte Carlo Joint-Failure Reliability (To build — §6) — CORE NOVEL RESULT

- Each joint: Weibull time-to-failure with Arrhenius temperature dependence (Q = 1.1 eV, Wright et al. 2023)
- Thermal profile along tether drives position-dependent failure rates
- System failure: any joint η_j drops below η_crit
- Parameter sweep: N ∈ {12,15,18,21,24} × η_j ∈ {0.88,0.90,0.93,0.95,0.97} × inspection cadence ∈ {1,2,5,10 passages}
- 10⁵ trajectories per combination (100 parameter points × 10⁵ = 10⁷ total)
- Repair model: detected failure → climber patch within t_repair; undetected → cascade

**Key outputs:** P_sys(10yr) heatmap over (N, η_j) — **the central figure of the paper**; critical η_j threshold for 99.9% survival; MTTR distribution validating 72h target; optimal inspection cadence for SIL-3 compliance

### 4.4 Material Sensitivity Analysis (To build — §6)

- Sweep σ_u across {30, 35, 40, 50, 60, 70} GPa
- For each: recompute taper ratio τ, total mass M_t, segment count N, max segment mass m_j
- Hold fixed: ρ = 1300 kg/m³, SF = 2, η_j = 0.95, χ_rad = 0.85
- Identify minimum σ_u where architecture closes (m_j ≤ 30 t)

**Key outputs:** τ, M_t, N vs. σ_u table/figure; "minimum viable CNT strength" identification

### 4.5 Dynamic Modal Analysis (To build — §5)

- Lumped-mass-spring chain: eigenvalue problem K·φ = ω²·M·φ (SciPy sparse eigensolver)
- First 20 modes, compared against continuous-string model (Nishimura & Hashimoto 2015)
- Forced response: 20 t climber at 150 m/s, track joint-node displacements
- Verify 12 Mm climber separation rule

### 4.6 Lifecycle Cost Model (To build — §7)

- 30-year NPV, discount rate 5–8%
- Modular: construction launches + operations + repair frequency × patch cost
- Monolithic: construction + operations + failure probability × full rebuild cost
- Revenue: cargo at $300/kg baseline, parametric over $200–500/kg
- Sweep launch cost $500–2000/kg to GTO

**Key outputs:** NPV crossover plot; sensitivity tornado; break-even launch cost vs. η_j

---

## 5. Expected Contributions

**C1.** First coupled system-level feasibility assessment of a modular CNT tether (joint reliability × geometry × repair × cost as one trade space)

**C2.** Variable-length mass-equalized segmentation methodology (Eq. 10 — generalizable to any tapered cable)

**C3.** Monte Carlo reliability surface P_sys(N, η_j) — first published quantification of joint count vs. quality tolerance

**C4.** Minimum viable CNT strength for modular architecture — showing this threshold is lower than for monolithic

**C5.** Lifecycle economic comparison: first quantitative answer to "repair in place vs. replace the tether?"

---

## 6. Anticipated Reviewer Concerns

| Concern | Mitigation |
|---------|-----------|
| σ_u = 50 GPa is aspirational (SOTA = 25 GPa at meter scale) | Sensitivity analysis down to 30 GPa; bracket as near-term vs. mid-term |
| η_j = 0.97 only on 50 m coupons, not 3 m full-scale sleeves | Monte Carlo at η_j = 0.88–0.97; derive minimum η_j required |
| 72 h repair time is assumed | Derive from climber velocity × distance + replacement; parametric sweep |
| FEA is 1D beam elements | Justified: L/D > 10⁸; 3D effects local to joints captured by SCFs |
| No experimental validation | Clearly stated as computational feasibility study; experimental next steps in §9 |

---

## 7. Key References This Work Extends

1. Edwards & Westling (2003) — NIAC Phase II monolithic baseline we validate against
2. Luo et al. (2022) — Segmented tether optimization (22% stress reduction) we extend with coupled reliability
3. Wright, Patel & Liddle (2023) — Joint efficiency data (η_j = 0.97) our Monte Carlo parameterizes on
4. Peters (2009) — Analytical taper solutions our profile matches
5. Bai et al. (2018) — 80 GPa CNT bundles (upper bound of σ_u sensitivity)
6. Popescu & Sun (2018) — Bio-inspired repair concept we operationalize with quantified logistics
7. Nishimura & Hashimoto (2015) — Continuous tether dynamics our segmented modal analysis compares against

---

## 8. Known Issue: Taper Ratio Discrepancy

**The current draft claims τ ≈ 1.6 at σ_allow = 25 GPa, ρ = 1300 kg/m³. Numerical integration of the same equations yields τ ≈ 12.4.**

Possible causes:
- Draft may be using σ_u (50 GPa) not σ_allow (25 GPa) for taper sizing — at σ_u/ρ = 38.5 MYuri, τ ≈ 1.9
- Sign convention difference in Eq. 6
- The 1.6 figure may be from a different source using different parameters

**This must be resolved first** — it changes segment count, mass budget, and Table 4 significantly. Resolving it correctly is itself a contribution: showing the modular architecture works at realistic τ is more impressive than at τ ≈ 1.6.

Action: verify against Peters (2009), re-derive Eq. 6 sign from first principles, clarify σ_u vs. σ_allow for taper sizing.
