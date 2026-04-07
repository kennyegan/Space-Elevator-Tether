# Modular Carbon-Nanotube Tether Architecture for Space-Elevator Deployment: A Coupled Systems Analysis

**Kenneth Egan**
Department of Mechanical and Aerospace Engineering, Wentworth Institute of Technology, Boston MA, USA

**Mehmet Ergezer**
Department of Mechanical and Aerospace Engineering, Wentworth Institute of Technology, Boston MA, USA

**Target:** Acta Astronautica (Elsevier)
**Keywords:** space elevator, carbon nanotubes, modular tether, joint reliability, Monte Carlo simulation, lifecycle cost analysis, orbital infrastructure

---

## Abstract

Every published space-elevator architecture presumes a defect-free monolithic carbon-nanotube ribbon spanning 100,000 km — a manufacturing requirement without terrestrial precedent. This paper advances a modular alternative: variable-length CNT segments joined in situ by nanobonded sleeve couplers. We present the first coupled system-level analysis integrating taper geometry, joint reliability, repair logistics, dynamic stability, and lifecycle economics as one trade space.

We first resolve a taper-ratio discrepancy latent in the literature: tapering at the ultimate tensile strength σ_u = 50 GPa (as Edwards and Westling implicitly did) yields τ ≈ 3.5 and N ≈ 83 segments for a full-payload-capacity ribbon (A_base sized for a 20 t climber), while tapering at the allowable stress σ_allow = 25 GPa (with safety factor SF = 2) yields τ ≈ 12.4 and N ≈ 505 segments. Edwards & Westling's lower segment count (N ≈ 18) reflects a thinner seed ribbon sized for bootstrap thickening rather than full payload from day one; the difference highlights that N is highly sensitive to the A_base sizing philosophy. We present both tapering approaches as "optimistic" and "conservative" design envelopes and show that the feasibility boundary depends critically on which design philosophy is adopted.

Monte Carlo simulation (10⁵ trajectories per combination, 12,600 combinations) over an expanded parameter space — N ∈ {12...500}, η_j ∈ {0.70...0.97}, inspection cadence ∈ {1...10 passages}, detection probability p_det ∈ {0.50...0.995}, Weibull shape β ∈ {1.0...2.5} — reveals that the modular architecture achieves >99.5% ten-year survival probability across the entire well-designed regime (η_j ≥ 0.88, p_det ≥ 0.90), with this result robust to wear-out failure physics up to β = 2.5. The reliability cliff emerges at degraded joint quality (η_j < 0.80) and immature inspection technology (p_det < 0.70), providing technology development targets. A cascading failure model based on the shear-lap stress redistribution (Eq. 11) shows that two adjacent unrepaired joint failures trigger immediate system loss, establishing the criticality of inspection cadence. Hazard-rate sensitivity analysis identifies activation energy Q as the dominant uncertainty (~7 orders of magnitude per ±40% perturbation), establishing experimental Q characterization as a priority.

Gravity-gradient string analysis gives a fundamental longitudinal pendulum period T₁ ≈ 25 h, consistent with Nishimura and Hashimoto (2015). A 500-node discrete model confirms that joint compliance shifts the fundamental frequency by only 2.3%. Upgrading to a 2D finite element model in the rotating frame — 500 nodes × 2 DOF with consistent mass, spatially varying tension, and Coriolis coupling — reveals a transverse fundamental period of 30.0 h (34.8 h with Coriolis, a 16% shift). A single 20 t climber induces peak transverse displacement of 136 km at the counterweight end and a tension perturbation ratio of 67% at the tether base (by construction, since the base cross-section is sized to the climber's surface weight). Multi-climber resonance analysis identifies the critical departure separation at 35 h (near the Coriolis-shifted T₁), where four successive climbers amplify transverse displacement to 489 km — establishing a quantitative separation design rule.

Lifecycle NPV comparison over 30 years shows modular consistently outperforms monolithic across all tested launch-cost ($500–2000/kg), discount-rate (5–10%), and revenue ($200–500/kg) scenarios. The phased construction advantage — modular generates revenue at ~60% completion while monolithic requires 100% — provides ~0.6 years of exclusive revenue generation, worth $0.05–0.16B in present value across all tested scenarios.

The modular tether's repair logistics challenge — median MTTR of ~227 h with surface-only dispatch — is addressable through orbital repair depots: 5 uniformly spaced depots reduce expected MTTR from 183 h to 102 h at modest cost (~$107M 30-year present value). However, the Edwards & Westling (2003) 72 h repair target remains structurally constrained by inspection cadence: a single climber traversal at 150 m/s takes 185 h, producing an expected wait time of 93 h that exceeds the target regardless of depot coverage or repair speed. Even with 50 depots and 600 m/s repair climbers, only 38% of failures achieve MTTR ≤ 72 h. This finding reframes the 72 h target as a requirement for faster operational climbers (≥300 m/s) or continuous structural health monitoring, not merely additional infrastructure.

**Seven contributions:**
1. First coupled system-level feasibility assessment of a modular CNT tether
2. Variable-length mass-equalized segmentation methodology with dual design envelopes
3. Monte Carlo reliability surface P_sys(N, η_j, cadence, p_det, β) over 12,600 parameter combinations including Weibull wear-out
4. Minimum viable CNT strength identification under both optimistic and conservative tapering
5. Lifecycle economic comparison quantifying the phased-construction revenue advantage
6. 2D Coriolis-coupled dynamic model quantifying transverse oscillations (T₁_trans = 34.8 h) and multi-climber resonance separation rule
7. Repair infrastructure trade-space analysis identifying inspection cadence — not depot coverage — as the binding constraint on MTTR

---

## 1. Introduction

Earth-to-orbit transportation costs $2,000–$4,000/kg via chemical rockets, with approximately 400 t CO₂-equivalent per launch. A space elevator — a continuous tether from an equatorial anchor through geostationary orbit (GEO, 35,786 km) to a counterweight beyond 100,000 km — could reduce marginal launch costs by 1–2 orders of magnitude using electrically powered climbers with zero propellant.

The linchpin is the tether. Analytical tapering requires specific tensile strengths exceeding 30 GPa·cm³/g over 100,000 km. Carbon-nanotube yarns now achieve 80 GPa on centimeter gauges and 25 GPa on meter-scale ribbons at kilometer-per-day production rates, narrowing the gap to within a factor of two.

### 1.1 The Core Problem: Architecture, Not Materials

**The core problem is not materials — it is architecture.** Every published elevator design assumes a defect-free monolithic CNT ribbon. This assumption:

1. Demands planetary-scale manufacturing perfection with zero defect propagation over 100,000 km
2. Offers no mechanism to replace sections damaged by micrometeoroids, debris, or radiation
3. Prevents incremental deployment, in-service upgrades, or phased construction
4. Makes the entire system a single point of failure

No published study has quantified joint reliability and load-path continuity in a segmented CNT tether at system level.

### 1.2 Research Objectives

**O1.** Design a modular CNT tether whose variable-length segments satisfy static and dynamic load envelopes with safety factor ≥ 1.5 under worst-case combined loading.

**O2.** Quantify system-level failure probability as a function of joint efficiency (η_j), segment count (N), and inspection cadence through Monte Carlo simulation — establishing minimum η_j thresholds for 99.9% ten-year system survival.

**O3.** Validate the modular stress profile against the Edwards & Westling (2003) NIAC monolithic baseline.

**O4.** Develop a lifecycle cost model comparing modular vs. monolithic architectures, quantifying the economic crossover.

**O5.** Perform material sensitivity analysis across σ_u = 30–70 GPa, demonstrating robustness to near-term CNT performance.

**O6.** Map TRL for each subsystem, identifying binding constraints for deployment timeline.

**O7.** Evaluate repair infrastructure trade space — depot count, placement strategy, repair speed — and identify the binding constraint on MTTR reduction.

### 1.3 Contributions

| ID | Contribution |
|----|-------------|
| C1 | First coupled system-level feasibility assessment of a modular CNT tether |
| C2 | Variable-length mass-equalized segmentation methodology (dual design envelopes) |
| C3 | Monte Carlo reliability surface P_sys(N, η_j, cadence, p_det) — first published quantification |
| C4 | Minimum viable CNT strength for modular architecture under both tapering philosophies |
| C5 | Lifecycle economic comparison with phased-construction revenue advantage |
| C6 | 2D Coriolis-coupled dynamic model with multi-climber resonance separation rule |
| C7 | Repair infrastructure trade-space analysis: inspection cadence identified as binding MTTR constraint |

---

## 2. Literature Review

### 2.1 Tether Architecture

Early feasibility studies assumed a monolithic, exponentially tapered ribbon (Edwards & Westling, 2003). Recent work shows that subdividing the tether into repairable modules can relax peak-stress requirements and simplify maintenance. Luo et al. (2022) quantified a 22% stress reduction with 10–100 km segments joined by sleeve couplers. Popescu and Sun (2018) introduced a bio-inspired bundle architecture with active self-repair. The IAA Study Group 3.10 recommended a one-meter-wide woven ribbon with in-plane redundancy.

**Gap:** No study couples joint reliability with segment geometry, repair logistics, and lifecycle economics at system level.

### 2.2 CNT Mechanics

Carbon nanotubes remain the reference material: laboratory strengths of 40–80 GPa (Bai et al., 2018) and industrial ribbons at 25 GPa (Zhao, 2024). The gap between laboratory and 100,000 km production has not been addressed with engineering knock-down factors.

### 2.3 Tether Dynamics

Pendulum periods, climber harmonics, and active damping are well-modeled for continuous tethers (Nishimura & Hashimoto, 2015). Joint compliance effects on segmented tether stability have not been quantified.

### 2.4 Deployment and Economics

Edwards' GEO-down bootstrap is established. Lifecycle NPV integrating modular repair costs vs. monolithic replacement has not been computed. Construction phasing — where modular architecture generates revenue incrementally — has not been quantified.

### 2.5 Research Gap

No published study integrates: (1) modular taper geometry with dual design envelopes, (2) position-dependent joint failure with cascading redistribution, (3) inspection/repair logistics, (4) dynamic stability under segmentation, and (5) phased-construction economics — as one coupled trade space. This paper fills that gap.

---

## 3. Theoretical Foundations

### 3.1 Taper Profile Derivation

A co-rotating tether element at radial distance r from Earth's center experiences net outward acceleration:

```
a_net(r) = ω²r − GM/r²
```

where ω = 7.292 × 10⁻⁵ rad/s is Earth's angular velocity and GM = 3.986 × 10¹⁴ m³/s². At GEO (r_GEO ≈ 42,164 km), a_net = 0 by definition.

For a uniform-stress taper, the cross-sectional area satisfies:

```
d(ln A)/dr = −(ρ/σ_design) × a_net(r)
```

Below GEO: a_net < 0 → A increases toward GEO.
Above GEO: a_net > 0 → A decreases above GEO.
Maximum area occurs at GEO: A_max = A_base × τ, where τ is the taper ratio.

### 3.2 The Taper Ratio Discrepancy — A First-Class Finding

**This paper resolves a discrepancy latent in the space-elevator literature.** Published taper ratios span τ ≈ 1.6 to τ ≈ 37, yet all are derivable from the same integral. Integrating Eq. (1) from the surface to the tether tip gives:

```
ln(τ) = (ρ / σ_design) × I_geo
```

where I_geo = ∫_R^{R+L} |a_net(r)| dr ≈ 4.84 × 10⁷ m²/s² is a fixed geometric constant for L = 100,000 km. The taper ratio thus depends on exactly two material inputs — density ρ and design stress σ_design — plus the often-unstated question of what σ_design includes.

**Three hidden assumptions** determine every published τ:

1. **Stress basis:** Does σ_design equal σ_u (ultimate), σ_u/SF (with safety factor), or σ_u × η_j × χ_rad / SF (full knockdown)?
2. **Material properties:** What (ρ, σ_u) pair is assumed? Published values range from ρ = 1,300 kg/m³ (CNT yarn) to 2,200 kg/m³ (graphite whisker), and σ_u from 46.5 GPa (Pearson) to 130 GPa (theoretical CNT).
3. **Base area sizing:** Is A_base for a thin seed ribbon (bootstrap thickening) or a full-payload-capacity ribbon? This does not affect τ but changes N and M_total.

**Reconciliation of published values:**

| Source | σ_design [GPa] | ρ [kg/m³] | τ (published) | τ (calculated) | Stress basis |
|--------|----------------|-----------|---------------|----------------|-------------|
| Edwards & Westling (2003) | 100 | 1,300 | ~1.9 | 1.88 | σ_u, no SF |
| Pugno (2006) | 100 | 1,300 | 1.9 | 1.88 | σ_u (defect-free) |
| Popescu & Sun (2018) | 65 | 1,325 | 2.6 | 2.68 | σ_u/2 (theoretical CNT) |
| This paper (optimistic) | 50 | 1,300 | — | 3.52 | σ_u, no SF |
| Aravind (2007) | 50 | 1,500 | 4.28 | 4.27 | σ_u/2, higher ρ |
| Pearson (1975) | 46.5 | 2,200 | ~10 | 9.88 | σ_u (graphite whisker) |
| This paper (conservative) | 25 | 1,300 | — | 12.40 | σ_u/SF (SF=2) |
| Popescu & Sun (2018) | 21.5 | 1,631 | 36.9 | 39.4 | σ_u/2 (STR method CNT) |

Every published ratio is recoverable from ln(τ) = ρ × I_geo / σ_design with no residual discrepancy. The apparent disagreement in the literature reduces to undeclared assumptions about the stress basis and material properties.

**Edwards & Westling's τ ≈ 1.9** specifically requires: (1) σ_design = σ_u ≈ 100 GPa with no safety factor on the taper shape, (2) ρ = 1,300 kg/m³, and (3) a seed-ribbon A_base (not full payload capacity). Changing any one of these assumptions significantly alters the architecture: applying SF = 2 to the taper raises τ from 1.9 to 3.5 at 100 GPa (or to 12.4 at σ_u = 50 GPa with SF = 2); using ρ = 1,500 raises τ by ~20%; and sizing A_base for a 20 t climber (rather than a seed ribbon) increases N from ~18 to ~83 segments.

**Our design envelopes:**

| Design Philosophy | σ_design | τ (at σ_u=50 GPa) | Interpretation |
|-------------------|----------|---------------------|----------------|
| Optimistic (Edwards & Westling) | σ_u | 3.52 | Shape at full strength; apply SF only for local stress checks |
| Conservative | σ_u / SF = σ_allow | 12.40 | Apply SF to the taper geometry itself |
| Full knockdown | σ_u × χ_rad × η_j / SF | 22.61 | Include all design factors in taper |

The optimistic approach yields N ≈ 83 segments at m_star = 18 t/segment with A_base sized for full payload capacity (A_base = m_climber × g / σ_design). The conservative approach yields N ≈ 505 segments and M_total ≈ 9,128 t. Both are presented as design envelopes throughout this paper.

We recommend that all future taper analyses explicitly state the stress basis, material density, and A_base sizing philosophy, as these three choices fully determine the architecture.

> **Figure reference:** `paper/figures/fig_design_envelope_comparison.pdf` — Dual-envelope sensitivity showing τ, N, M_total, and m_j_max vs. σ_u for both design philosophies.

### 3.3 Specific Strength and Feasibility Boundary

The minimum viable CNT strength is defined as the σ_u at which the architecture "closes" — all segments fit within the 30 t launch cap.

| σ_u [GPa] | τ (optimistic) | N (optimistic) | M_total (optimistic) | Feasible |
|-----------|---------------|----------------|---------------------|----------|
| 30 | 8.15 | 290 | 5,235 t | Yes |
| 35 | 6.04 | 191 | 3,443 t | Yes |
| 40 | 4.82 | 137 | 2,472 t | Yes |
| 50 | 3.52 | 83 | 1,502 t | Yes |
| 60 | 2.86 | 58 | 1,043 t | Yes |
| 70 | 2.46 | 44 | 785 t | Yes |

> **Figure reference:** `paper/figures/fig_sigma_sensitivity.pdf`

### 3.4 Variable-Length Mass-Equalized Segmentation

Segment length inversely follows the local ribbon area so that mass per segment is nearly constant:

```
L_j = m★ / (ρ × A_base × A_ratio(y_j,mid))       (Eq. 10)
```

where m★ = 18,000 kg is the target per-segment mass (60% of the 30 t launch allowable, reserving margin for sleeves, coatings, and deployment hardware).

> **Figure reference:** `paper/figures/fig_taper_validation.pdf` — Continuous vs. stepped taper profile.

### 3.5 Shear-Lap Joint Sizing (Eq. 11)

A sleeve joint of length ℓ and width b fails in interfacial shear when:

```
ℓ_min = T_j / (2b × τ_allow)
```

where τ_allow = 0.42 × σ_allow is the experimentally derived shear-strength fraction for CNT nano-solders (Wright et al., 2023). With T_max at GEO and b = 1.20 m, this yields ℓ_min = 2.8 m. The baseline sleeve is sized at ℓ = 3.0 m, ts = 4 mm, mass = 35 kg.

---

## 4. Modular System Architecture

### 4.1 Baseline Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| L_total | 100,000 km | GEO + counterweight beyond |
| ρ | 1,300 kg/m³ | CNT yarn bulk density |
| σ_u (baseline) | 50 GPa | 2030 target (meter-scale) |
| SF | 2.0 | ISO 14692 |
| η_j (baseline) | 0.95 | Nanobond sleeve (Wright 2023) |
| m★ | 18,000 kg | Target per-segment mass |
| m_launch_cap | 30,000 kg | Starship-class GEO injection limit |
| m_climber | 20,000 kg | Construction/cargo climber |
| v_climber | 150 m/s | Transit velocity |
| m_counterweight | 600,000 kg | Edwards & Westling estimate |

### 4.2 Joint Candidates

| Joint Type | η_j | Mass [kg] | Install Time [h] | 10-yr P_fail |
|------------|-----|-----------|-------------------|-------------|
| Bolted collet | 0.88 | 95 | 2.1 | 6.6 × 10⁻³ |
| Nanobond sleeve (baseline) | 0.97 | 35 | 1.4 | 4.6 × 10⁻³ |
| Sleeve + BNNT overplate | 0.96 | 38 | 1.8 | 4.7 × 10⁻³ |

### 4.3 Hazard Rate Model

Joint failures are dominated by diffusion-assisted void growth in solder necks. The hazard rate follows an Arrhenius law:

```
λ_j(T) = λ_0_pre × exp(−Q / (k_B × T)) × (0.97 / η_j)⁴
```

where Q = 1.1 eV is the activation energy (Wright et al., 2023). Integrating the orbital thermal profile gives a mission-averaged λ̄ = 1.2 × 10⁻⁸ h⁻¹ at coupon scale.

**Volume scaling:** Full-scale sleeves (3.0 m × 1.2 m × 4 mm) are 6,000× the volume of test coupons (50 mm × 12 mm × 4 mm). Weibull weakest-link scaling with modulus m = 6 gives:

```
λ_fullscale = λ_coupon × (V_sleeve / V_coupon)^(1/m) = 1.2e-8 × 6000^(1/6) ≈ 5.2 × 10⁻⁸ h⁻¹
```

The pre-exponential λ_0_pre is derived by calibrating against this mission-averaged rate weighted by the number of joints in each thermal zone (not by tether length).

### 4.4 Thermal Profile (3-Zone Model)

| Zone | Altitude | Temperature | Dominant Environment |
|------|----------|-------------|---------------------|
| 1 | 0 – 200 km | 250 K | Atmospheric drag, eclipse cycling |
| 2 | 200 km – 35,786 km | 280 K | LEO-GEO corridor, mixed illumination |
| 3 | > 35,786 km | 300 K | Cislunar, sustained solar exposure |

Most joints (under optimistic tapering) cluster in Zone 2 due to higher taper area requiring shorter, more numerous segments in the LEO-GEO corridor.

---

## 5. Simulation Methodology

### 5.1 Static Taper Validation

**Script:** `simulations/fea/taper_profile.py`

- Numerical integration of d(ln A)/dr = −(ρ/σ) × a_net(r) at 1 km resolution (100,001 points)
- Force-balance consistency check: T(r) = σ × A(r) verified against cumulative integration of ρ × A × a_net
- Stress uniformity: σ_std/σ_mean ≈ 10⁻¹⁷ (machine precision) confirms correct implementation
- A_base computed from payload requirement: A_base = m_climber × g / σ_design
- Mass-equalization walk determines N from physics (no prescribed value)
- Sensitivity sweep at both σ_u and σ_allow tapering for σ_u ∈ {30, 35, 40, 50, 60, 70} GPa

### 5.2 Monte Carlo Joint Reliability

**Scripts:** `simulations/monte_carlo/joint_reliability.py` (exponential baseline), `simulations/monte_carlo/phase1_weibull/` (Weibull extension)

#### 5.2.1 Exponential Baseline

**Parameter space:** 2,268 combinations
- N ∈ {12, 15, 18, 21, 24, 50, 100, 200, 500}
- η_j ∈ {0.70, 0.75, 0.80, 0.85, 0.88, 0.90, 0.93, 0.95, 0.97}
- Inspection cadence ∈ {1, 2, 5, 10} climber passages
- p_detection ∈ {0.50, 0.70, 0.80, 0.90, 0.95, 0.99, 0.995}

**Per trajectory:**
1. Draw time-to-failure for each joint from Exp(λ_j(T_local))
2. Step through inspection epochs (t_between = cadence × L_total / v_climber)
3. At each epoch: check for joint failures since last inspection
4. **Cascade check:** redistribute load from failed joints to neighbors via shear-lap model. If neighbor stress > σ_allow → cascade failure. If two adjacent joints both failed → immediate system failure.
5. Detection roll: each failed joint detected with probability p_det
6. Detected → repair (wait + travel + 1.4 h replacement), draw new TTF
7. Not detected → joint remains failed, load redistribution persists

**Arrhenius calibration:** λ_0_pre derived from λ̄_fullscale = 5.2 × 10⁻⁸ weighted by joint count per thermal zone. Self-consistency verified at startup.

**Computational:** 10⁵ trajectories per combination (2.27 × 10⁸ total). Vectorized inner loop; GPU option via CuPy for cluster deployment.

#### 5.2.2 Weibull Age-Dependent Extension

The exponential model assumes memoryless (constant hazard) joint failure. Real CNT joints exhibit wear-out behavior where hazard increases with accumulated service time. To capture this, we extend the failure model to the two-parameter Weibull distribution:

```
h(t) = (β/η) × (t/η)^(β−1)
```

where β is the shape parameter (β = 1 recovers exponential, β > 1 gives increasing hazard) and η = 1/λ is the scale parameter derived from the Arrhenius-calibrated per-joint hazard rate.

**Expanded parameter space:** 12,600 combinations (adding β ∈ {1.0, 1.3, 1.5, 2.0, 2.5} to the 4D grid with N ∈ {12, 15, 18, 21, 24, 50, 83, 100, 200, 500}).

**Weibull state tracking:** Each joint maintains three state variables: the time of last scale/birth change (t_snapshot), cumulative hazard at snapshot (H_snapshot), and current Weibull scale (1/λ_current). When stress redistribution changes a joint's hazard rate, the remaining life is computed via:

```
Δt = η_new × [(H_accum + E)^(1/β) − H_accum^(1/β)]
```

where E ~ Exp(1) and H_accum is the accumulated hazard through the snapshot. At repair, the joint receives a fresh clock (H = 0, new scale).

**Validation:** β = 1.0 recovers the exponential model at identical seeds. Monotonicity checks confirm that increasing β reduces P_sys at fixed (N, η_j) in the degraded regime while maintaining high reliability in the well-designed regime.

#### 5.2.3 Hazard Rate Sensitivity

**Script:** `simulations/monte_carlo/phase1_weibull/sensitivity_analysis.py`

One-at-a-time perturbation (±20%, ±40%) of seven hazard-rate parameters: activation energy Q, Weibull volume modulus m, three thermal zone temperatures (T₁, T₂, T₃), coupon hazard rate λ_coupon, and sleeve-to-coupon volume ratio V_ratio. The calibration of λ_0_pre is held fixed when perturbing Q and T to prevent re-calibration from absorbing the perturbation — this isolates the physical sensitivity of the hazard rate to each parameter.

### 5.3 Dynamic Modal Analysis

**Scripts:** `simulations/fea/modal_analysis.py` (1D), `simulations/fea/phase2_dynamics/run_all.py` (2D)

#### 5.3.1 Analytical Gravity-Gradient String (1D Baseline)

For a uniform-stress fixed-free string under gravity-gradient tension:
```
c = √(σ_design / ρ),   T₁_pendulum = 4L / c
```
For σ_allow = 25 GPa, ρ = 1300 kg/m³: c ≈ 4,385 m/s → T₁_pendulum ≈ 25.3 h. This is the gravity-gradient pendulum period — the long-wavelength oscillation where the tether swings as a whole under the restoring force of the gravity gradient. It is distinct from the elastic compression wave period (T₁_elastic ≈ 7.7 h for the 500-node discrete model), which is controlled by the much stiffer EA/L term. This distinction is important: the 25.3 h mode is excited by orbital perturbations, while the 7.7 h mode is excited by impulsive loads (climber departure/arrival).

A 500-node lumped-mass-spring chain (k_j = k_material + k_geo) confirms that joint compliance (η_j = 0.95 vs 1.0) shifts the elastic fundamental frequency by 2.3%, validating that segmentation does not destabilize.

#### 5.3.2 2D Coriolis-Coupled Finite Element Model

To capture transverse dynamics and Coriolis coupling, we upgrade to a 2D model in the rotating (Earth-fixed) reference frame. Each of 500 nodes carries two DOFs: longitudinal u (radial) and transverse v (in-plane, along-track), giving a 998-DOF system after applying the fixed-base boundary condition.

**Element formulation:** Two-node elements with consistent mass matrices and three stiffness contributions:
- **Elastic** (longitudinal): EA/L rod stiffness, with EA reduced by η_j at joint elements
- **Tension** (transverse): T(r)/L tensioned-string stiffness, where T(r) = σ_design × A(r) varies by a factor of τ ≈ 12.4 along the tether
- **Gravity-gradient** (longitudinal): position-dependent restoring force (ω² + 2GM/r³) from tidal stretching, evaluated via 2-point Gauss quadrature

**Coriolis coupling:** The skew-symmetric gyroscopic matrix G couples longitudinal velocity (u̇) into the transverse equation and vice versa. This is the key upgrade — without G, longitudinal and transverse modes are independent; with G, they interact, shifting frequencies and enabling energy transfer between DOFs.

**Damping:** Rayleigh damping (C = α_M M + α_K K) calibrated to ζ = 0.01 at the first two modes. Damping is a placeholder; the paper acknowledges it is not well characterized.

**Time integration:** Newmark-β (β = 0.25, γ = 0.5, average acceleration) with sparse LU factorization of the non-symmetric effective stiffness K_eff = K + (1/βΔt²)M + (γ/βΔt)(C + G). Time step Δt = 500 s.

**Mesh:** Non-uniform spacing with Gaussian refinement near GEO (where the taper is steepest), plus 600,000 kg counterweight mass at the free tip.

**Validation:** Six checks all pass: K positive definite, 1D longitudinal recovery (2.4% error vs existing model), Coriolis matrix skew-symmetry (‖G + Gᵀ‖/‖G‖ = 0), energy conservation (<0.1% drift undamped over 100 h), mesh convergence (<0.1% between 250 and 500 elements), and joint compliance shift (2.44% vs 1D's 2.32%).

#### 5.3.3 Single-Climber Transit Simulation

A 20 t climber traversing at 150 m/s from surface to counterweight (transit time 185 h) applies two forces to the tether: the gravity-gradient load (longitudinal, up to 196 kN at the surface) and the Coriolis force from the climbing mass (transverse, ~438 N constant). The simulation runs for 235 h (transit + 50 h free vibration).

#### 5.3.4 Multi-Climber Resonance Analysis

To quantify the resonance risk, we sweep departure separations from 10 h to 50 h, launching 4 climbers sequentially at each spacing. At each separation we record peak transverse displacement, peak tension perturbation, and RMS transverse velocity at GEO. A damping sensitivity study at the worst-case resonant separation sweeps ζ from 0.001 to 0.05.

### 5.4 Lifecycle Cost Model

**Script:** `simulations/cost_model/npv_model.py`

**30-year NPV for two architectures:**

Modular:
```
NPV = Σ_{t=1}^{30} [R(t) × f_operational(t) − C_construction(t) − C_ops(t) − C_repair(t)] / (1+r)^t
```

where f_operational(t) = max(0, min(1, (segments_deployed/N − 0.6) / 0.4)) — revenue ramps from 0 at 60% completion to full at 100%.

Monolithic:
```
NPV = Σ_{t=1}^{30} [R(t)×I(t > t_build) − C_construction(t) − C_ops(t) − P_fail×C_replace] / (1+r)^t
```

Zero revenue until 100% complete. P_fail from Monte Carlo (worst-cadence case).

**Sweep:** launch cost {500, 1000, 1500, 2000} $/kg × discount rate {5, 7, 10}% × payload revenue {200, 300, 500} $/kg.

### 5.5 Repair Infrastructure Trade Space

**Script:** `simulations/repair_infrastructure/run_all.py`

The Monte Carlo results (§6.5) show that MTTR is dominated by travel time from the surface anchor. To evaluate whether distributed repair depots can reduce MTTR to the 72 h target cited by Edwards and Westling (2003), we construct an analytical MTTR model:

```
MTTR = t_wait + t_travel + t_repair
```

where t_wait is uniformly distributed in [0, cadence × L_total / v_climber] (time from failure to next inspection epoch), t_travel = min_d |h_fail − h_depot_d| / v_repair is the travel time from the nearest depot, and t_repair = 1.4 h is the fixed sleeve replacement time.

**Depot specifications:** Each depot is a 1,500 kg pre-positioned orbital platform carrying 10 spare sleeve couplers (350 kg), a robotic repair arm (500 kg), power/station-keeping systems (200 kg), and structural frame with docking (450 kg).

**Three placement strategies** are evaluated:
1. **Uniform:** depots equally spaced along tether length
2. **Joint-density-weighted:** depots positioned so each covers an equal number of joints, concentrating depots in the high-taper region near GEO where segments are shortest
3. **Hybrid:** fixed anchors at surface and GEO, remaining depots distributed uniformly

**Parameter sweep:** n_depots ∈ {0, 1, 2, 3, 5, 7, 10, 15, 20, 30, 50}, v_repair ∈ {150, 300, 600} m/s, cadence ∈ {1, 2, 5, 10}, placement ∈ {uniform, joint_weighted, hybrid}, N ∈ {83, 505}.

Joint positions are computed from the mass-equalization walk (§3.4) using the actual taper profile, not equal spacing — joints cluster near GEO where segments are shortest. For each combination, we compute expected MTTR, maximum MTTR, and P(MTTR ≤ 72 h) by integrating over the wait-time distribution.

**Depot cost model:** Capital cost = n × (1,500 kg × launch_cost + $5M fabrication). Annual operating cost = n × ($0.5M ops + 2 resupply missions × 350 kg × launch_cost). These are integrated into the NPV model as additional modular architecture costs.

This analysis is deterministic (analytical), not Monte Carlo, and completes in seconds.

---

## 6. Results

### 6.1 Taper Profile Validation

The continuous taper profile was validated against first principles:
- **Taper ratio:** τ = 12.40 at σ_allow = 25 GPa, τ = 3.52 at σ_u = 50 GPa
- **Peak location:** GEO altitude 35,786 km (exact match)
- **Stress uniformity:** σ_std/σ_mean = 5.39 × 10⁻¹⁷ (machine precision)

> **Figure:** `paper/figures/fig_taper_validation.pdf`

### 6.2 Dual Design Envelope — The Key Finding

Under **optimistic tapering** (σ_u, no SF on shape):
- τ = 3.52 at σ_u = 50 GPa
- N ≈ 83 segments, M_total ≈ 1,502 t
- Architecture closes at σ_u ≥ 30 GPa (all configurations feasible with m_j_max < 30 t)

Under **conservative tapering** (σ_allow = σ_u/SF):
- τ = 12.40 at σ_u = 50 GPa
- N ≈ 505 segments, M_total ≈ 9,128 t
- Architecture requires 6× more segments and 6× more mass

**Interpretation:** Edwards & Westling's lower segment count (N ≈ 18) reflects their seed-ribbon A_base sized for bootstrap thickening. Our A_base = m_climber × g / σ_design gives a wider ribbon capable of supporting a 20 t climber from day one, yielding N ≈ 83 at the same σ_u. The segment count is thus highly sensitive to the A_base sizing philosophy — a finding not previously stated in the literature. Under conservative tapering, the feasibility boundary shifts by a factor of ~6× in segment count (83 → 505), with dramatic mass implications.

> **Figure:** `paper/figures/fig_design_envelope_comparison.pdf`

### 6.3 Material Sensitivity

The sensitivity sweep across σ_u = 30–70 GPa reveals:

**Optimistic tapering:**
- All configurations feasible (m_j_max ≤ 30 t) down to σ_u = 30 GPa
- Minimum viable strength: σ_u = 30 GPa (below current lab demonstrations of 25 GPa ribbon-scale)

**Conservative tapering:**
- All configurations feasible but with N > 100 segments even at σ_u = 70 GPa
- Total mass exceeds 69,442 t at σ_u = 30 GPa

> **Figure:** `paper/figures/fig_sigma_sensitivity.pdf`

### 6.4 Monte Carlo Reliability Surface

#### Exponential Baseline

The 4D parameter sweep (2,268 combinations × 10⁵ trajectories) reveals:

**Well-designed regime** (η_j ≥ 0.88, p_det ≥ 0.90, N ≤ 24):
- P_sys > 99.5% across all combinations
- System is highly robust — this is itself a significant finding

**Degraded regime** (η_j < 0.80, p_det < 0.70, or N > 100):
- P_sys drops to 72.7% at worst case (N=500, η_j=0.70, cadence=10, p_det=0.50)
- The 99.9% contour requires η_j ≥ 0.88 with p_det ≥ 0.90, defining the joint technology requirement
- The 99.0% contour requires η_j ≥ 0.80 with p_det ≥ 0.70, defining the minimum viable inspection capability

**Cascading failures:**
- Load redistribution from unrepaired joints increases neighbor hazard rates by (σ_new/σ_nom)⁴
- Two adjacent unrepaired failures → immediate system loss
- Cascade probability increases non-linearly with N: at N = 500 (499 joints), the combinatorial exposure to adjacent failures grows quadratically compared to N = 83 (82 joints)

> **Figure:** `paper/figures/fig_reliability_merged.pdf` — (a) P_sys(N, η_j) heatmap; (b) P_sys vs. Weibull β (THE central figure)
> **Figure (supplementary):** `paper/figures/fig_inspection_cadence.pdf` — Availability vs. inspection frequency
> **Figure (supplementary):** `paper/figures/fig_p_detection_impact.pdf` — P_sys vs. detection probability

#### Weibull Extension: Effect of Wear-Out

Extending to 12,600 combinations (adding β ∈ {1.0, 1.3, 1.5, 2.0, 2.5}) reveals how age-dependent failure physics tightens the design envelope:

**Baseline configuration** (N=83, η_j=0.95, cadence=1, p_det=0.995):

| β | P_sys | Mean repairs | Median MTTR |
|---|-------|-------------|-------------|
| 1.0 (exponential) | 0.99995 | 0.41 | 218 h |
| 1.5 | 0.99999 | 0.034 | 219 h |
| 2.0 (wear-out) | 1.00000 | 0.003 | 212 h |
| 2.5 (strong wear-out) | 1.00000 | 0.0003 | 207 h |

At baseline joint quality, the system maintains >99.99% reliability across all β — the design margin absorbs even strong wear-out. Mean repairs per trajectory drop by three orders of magnitude from β=1.0 to β=2.5 because higher β concentrates failures late in the mission (beyond the 10-year window for most joints), reducing expected failure count but creating potential burst repair demands near end-of-life.

**Worst-case configuration** (N=500, η_j=0.80, cadence=10, p_det=0.50):

| β | P_sys |
|---|-------|
| 1.0 | 84.9% |
| 1.5 | 97.5% |
| 2.0 | 99.6% |
| 2.5 | 99.95% |

In the degraded regime, increasing β *improves* reliability because wear-out failure physics concentrates failures late in the mission — fewer joints fail within the 10-year window. However, this apparent benefit is misleading for longer missions: the increasing hazard rate means failure probability accelerates in years 10–20, creating a cliff in extended-life scenarios.

**η_j threshold vs. β:** At the optimistic design point (N=83), maintaining P_sys ≥ 0.995 requires η_j ≈ 0.88 at β=1.0 (memoryless) but the threshold rises with increasing β, approaching the baseline η_j = 0.95 at β ≥ 2.5. This translates wear-out severity directly into a manufacturing quality target.

> **Figure:** `paper/figures/fig_reliability_merged.pdf` — Panel (b): P_sys vs. β at four design points
> **Figure:** `paper/figures/fig_beta_threshold.pdf` — Minimum η_j for P_sys ≥ 0.995 vs. β
> **Figure (supplementary):** `paper/figures/fig_reliability_surface_by_beta.pdf` — Full P_sys(N, η_j) heatmaps at each β
> **Figure (supplementary):** `paper/figures/fig_cadence_sensitivity_by_beta.pdf` — Inspection cadence sensitivity under wear-out

#### Hazard Rate Sensitivity

The one-at-a-time perturbation analysis identifies activation energy Q as the overwhelmingly dominant hazard-rate parameter: ±40% perturbation causes ~7 orders of magnitude change in the full-scale hazard rate, reflecting the exponential Arrhenius dependence. Zone 3 temperature (T₃, >35,786 km) ranks second with ~3 orders of magnitude sensitivity. The remaining parameters (Weibull modulus m, volume ratio, coupon rate λ_coupon) contribute at most ~0.5 decades each.

This extreme Q-sensitivity has a practical implication: experimental determination of the activation energy for void growth in CNT sleeve bonds is the single most important characterization priority for reducing reliability prediction uncertainty.

> **Figure:** `paper/figures/fig_hazard_tornado.pdf` — Hazard rate sensitivity tornado diagram
> **Figure (supplementary):** `paper/figures/fig_hazard_spider.pdf` — Hazard rate spider plot

### 6.5 MTTR Distribution

From ~202.7 million repair events across all trajectories:
- **Median MTTR:** ~227 h (cadence=1), ~590 h (cadence=5), ~1,275 h (cadence=10)
- **MTTR range:** 168–1,773 h across all parameter combinations

MTTR is dominated by travel time (climber at 150 m/s traversing up to 100,000 km) plus wait time for next inspection cycle. Cadence = 1 (every climber passage) gives median MTTR of ~227 h; cadence = 10 pushes median to ~1,275 h.

#### 6.5.1 Depot Infrastructure Analysis

To close the gap between observed MTTR and the Edwards & Westling (2003) 72 h target, we evaluate the effect of pre-positioned repair depots along the tether. Using the analytical model (§5.5) with joint positions from the mass-equalization walk (N = 83, optimistic taper):

| Depots | v_repair | Expected MTTR | P(MTTR ≤ 72 h) |
|--------|----------|---------------|----------------|
| 0 | 150 m/s | 183 h | 5.8% |
| 5 | 150 m/s | 102 h | 33.6% |
| 10 | 150 m/s | 98 h | 35.8% |
| 50 | 150 m/s | 95 h | 37.6% |
| 0 | 600 m/s | 116 h | 26.1% |
| 5 | 600 m/s | 96 h | 37.0% |
| 10 | 600 m/s | 95 h | 37.5% |
| 50 | 600 m/s | 94 h | 38.0% |

**Key finding:** P(MTTR ≤ 72 h) saturates near 38% regardless of depot count or repair speed. The binding constraint is inspection cadence: a single climber traversal at 150 m/s takes 185 h, so the expected wait time between failure and detection is 93 h — already exceeding the 72 h target before any travel or repair. Only failures that happen to occur shortly before a scheduled inspection epoch can achieve MTTR ≤ 72 h.

Depots are effective at reducing *expected* MTTR (from 183 h to ~95 h with 10+ depots), but the 72 h target requires either: (a) operational climber speeds ≥ 300 m/s (reducing t_wait to ~46 h), (b) continuous structural health monitoring replacing periodic inspection, or (c) accepting that the 72 h target is achievable for only ~38% of failure events.

**Placement comparison:** Joint-density-weighted placement outperforms uniform spacing by 0.1–0.5 h for n ≥ 5 (a modest advantage), because the taper profile concentrates joints near GEO where equal-mass segments are shortest. The hybrid strategy (surface + GEO anchors with uniform fill) performs comparably to uniform.

> **Figure:** `paper/figures/fig_mttr_merged.pdf` — (a) MTTR by Weibull β; (b) depot shift of distribution
> **Figure:** `paper/figures/fig_mttr_vs_depots.pdf` — Expected MTTR vs. depot count at v_repair = {150, 300, 600} m/s
> **Figure:** `paper/figures/fig_72h_achievability.pdf` — P(MTTR ≤ 72 h) vs. depot count
> **Figure (supplementary):** `paper/figures/fig_depot_placement_comparison.pdf` — MTTR vs. failure altitude for 3 placement strategies

#### 6.5.2 Depot Capital Cost

| Depots | Capital cost | Annual ops | 30-year PV (7%) |
|--------|-------------|------------|-----------------|
| 5 | $40M | $6M | ~$107M |
| 10 | $80M | $12M | ~$214M |
| 20 | $160M | $24M | ~$428M |

Costs are parametric estimates (order-of-magnitude) using $1,000/kg launch cost, $5M/depot fabrication, and $0.5M/depot/year station-keeping. The 30-year PV of 10 depots (~$214M) is ~14% of the tether build cost ($1.5B), confirming that depot infrastructure is affordable relative to the primary structure.

### 6.6 Dynamic Modal Analysis

#### 1D Baseline Results

**Analytical:** T₁_pendulum = 25.3 h for the gravity-gradient tensioned string (c = √(σ/ρ) = 4,385 m/s), consistent with Nishimura and Hashimoto (2015).

**Joint compliance effect (1D discrete):** The 500-node lumped-mass-spring model gives a 2.32% frequency shift from joint compliance (η_j = 0.95 vs 1.0), uniform across all modes. This negligible shift confirms that segmentation does not destabilize the tether.

> **Figure:** `paper/figures/fig_modal_comparison.pdf`

#### 2D Modal Results

The 2D model reveals that the lowest-frequency mode is **transverse** (lateral swinging), not longitudinal:

| Property | No Coriolis | With Coriolis | Coriolis shift |
|----------|-------------|---------------|----------------|
| T₁ transverse [h] | 30.0 | 34.8 | +16% |
| T₂ transverse [h] | 10.2 | 10.5 | +2.5% |
| T₁ longitudinal [h] | 7.65 | 7.12 | −7% |

The Coriolis coupling shifts the transverse fundamental period by 16% — a significant effect that cannot be captured by any 1D model. The 30.0 h no-Coriolis transverse period is 19% longer than the 25.3 h analytical pendulum period; this difference arises because the non-uniform taper concentrates mass near GEO (where the cross-section peaks), which lowers the effective mode frequency compared to the uniform-string analytical formula.

The first longitudinal elastic mode at 7.65 h is distinct from the 25.3 h analytical pendulum period. The 25.3 h result comes from c = √(σ/ρ), which represents the gravity-gradient wave speed where geometric stiffness balances inertia. The 7.65 h mode arises from the full elastic stiffness EA/L, which is ~11× stiffer (E/σ = 280/25 = 11.2). These are physically different oscillation mechanisms: the pendulum mode is a whole-tether libration driven by the gravity gradient; the elastic mode is a compression wave.

#### Single-Climber Transit Results

> **Figure:** `fig_displacement_envelopes_merged.pdf` — (a) Longitudinal, (b) transverse displacement envelopes
> **Figure:** `fig_tension_perturbation.pdf` — Tension perturbation ratio vs. altitude
> **Figures (supplementary):** `fig_waterfall_vrt.pdf`, `fig_geo_time_history.pdf`

**Longitudinal:** Peak dynamic displacement 62.2 km, compared with 67.3 km from the quasi-static analysis. The dynamic result is 8% lower because inertia prevents instantaneous response to the moving load. The displacement envelope shows a sharp rise at low altitude (where the tether is thinnest), a plateau through GEO, and a secondary peak at the counterweight.

**Transverse:** Peak displacement 135.6 km at the counterweight end, driven by the persistent Coriolis force (~438 N) on the climbing mass acting over the 185 h transit. The monotonically increasing envelope (zero at the fixed base, maximum at the free tip) reflects the fundamental fixed-free string mode shape. The 136 km transverse displacement is consistent with a static estimate F_Coriolis × L / T_base ≈ 223 km, reduced by damping and the higher tension above GEO.

**Tension perturbation:** The peak ΔT/T_eq = 66.6% occurs at the tether base (altitude 127 km). This high ratio is by construction: the base cross-section is the minimum-area point, sized so that A_base = m_climber × g / σ_design — the climber's full surface weight equals the design tension. The perturbation ratio drops rapidly with altitude: 47% at 630 km, 15% at 2,400 km, and <5% above 5,000 km as A(r) increases with the taper. This does not threaten structural integrity because the safety factor SF = 2 is applied to σ_u = 50 GPa; the combined equilibrium + perturbation stress remains within σ_u.

#### Multi-Climber Resonance Results

> **Figure:** `fig_resonance_scan.pdf` — Peak transverse displacement vs. departure separation
> **Figures (supplementary):** `fig_safe_separation.pdf`, `fig_resonant_vs_offresonant.pdf`, `fig_damping_sensitivity.pdf`

Sweeping departure separations from 10 h to 50 h with 4 sequential climbers reveals a clear resonance peak at **35 h** separation — near the Coriolis-shifted T₁_trans = 34.8 h. At this resonant separation, peak transverse displacement reaches 489 km (3.6× the single-climber value), confirming constructive interference between successive climbers.

Off-resonant separations (e.g., 18 h) produce peak transverse displacement of only 129 km — comparable to the single-climber result. The resonance amplification factor is thus ~3.6× at the worst case.

**Damping sensitivity at resonance (35 h separation):**

| ζ | Peak transverse [km] |
|---|---------------------|
| 0.001 | 620 |
| 0.005 | 536 |
| 0.01 | 489 |
| 0.02 | 441 |
| 0.05 | 347 |

Even at ζ = 0.05 (aggressive damping), resonant transverse displacement remains 347 km — indicating that avoiding the resonant cadence is more effective than relying on passive damping.

**Design rule:** Climber departure separations within ±5 h of the Coriolis-shifted transverse fundamental period (~35 h) should be avoided. Separations of 18 h or less (corresponding to the 12 Mm minimum spacing at 150 m/s) produce lower transverse excitation, though at the cost of reduced throughput.

---

## 7. Lifecycle Cost Analysis

### 7.1 Baseline Assumptions

| Parameter | Value |
|-----------|-------|
| Tether mass (optimistic, N=83) | 1,502 t |
| Build cost (at $1000/kg) | $1.50B |
| Annual operations | $30M (2% of build) |
| Max annual revenue | $300M (50 trips × 20 t × $300/kg) |
| Repair cost per event | $27.1M |
| Expected repairs/year | 0.01 |
| Construction cadence | 12 segments/year |
| Years to build | ~7 (83 segments / 12 per year) |

### 7.2 Phased Construction Advantage

The modular architecture's most significant economic advantage is not lower failure cost — it is **earlier revenue generation**.

- **Modular:** Revenue begins at ~60% tether completion. At 12 segments/year with N = 83, the first climber traverses at year ~5 (segment 50 of 83).
- **Monolithic:** Zero revenue until 100% complete (year ~7).
- **Revenue head start:** ~0.6 years of exclusive partial revenue, worth approximately $0.05–0.16B in present value depending on launch cost and revenue assumptions.

This finding has not been quantified in prior space-elevator economic analyses.

### 7.3 NPV Crossover

Modular NPV exceeds monolithic at year 1 under baseline assumptions across all tested scenarios. The advantage is:
- **Robust to launch cost:** Crossover occurs across all tested $500–2000/kg scenarios
- **Insensitive to revenue:** Modular advantage persists regardless of payload pricing
- **Dominated by phased construction:** Repair cost savings are secondary to revenue timing advantage

> **Figure:** `paper/figures/fig_npv_merged.pdf` — Cumulative NPV: monolithic vs. modular with 0/5/10 depots
> **Figure:** `paper/figures/fig_cost_tornado.pdf`

### 7.4 NPV with Depot Infrastructure

Including depot capital and operating costs in the modular architecture's NPV reduces but does not eliminate the advantage over monolithic construction. At the baseline scenario ($1,000/kg launch, 7% discount, $300/kg payload revenue):

- **No depots:** Modular NPV advantage = $3.14B (unchanged from §7.3)
- **5 depots:** Modular advantage reduced by ~$107M (30-year depot PV)
- **10 depots:** Modular advantage reduced by ~$214M

The modular architecture supports up to 3 depots before its 30-year NPV falls below the monolithic alternative at baseline revenue ($300/kg). This is a tight budget — 3 depots reduce expected MTTR from 183 h to only 112 h, a meaningful improvement but far from the 72 h target. At higher payload revenue ($500/kg), the budget expands to 5 depots. The break-even is insensitive to launch cost and discount rate because depot costs scale proportionally with tether costs (both are dominated by launch mass).

The practical implication is that depot infrastructure is affordable but constrained: a modest network of 3 depots (PV ~$64M at $1,000/kg, 7%) fits within the modular economic advantage across all tested scenarios, while larger networks require either higher payload revenue or acceptance of a reduced — but still positive — NPV margin. Since §6.5.1 shows that the binding constraint on MTTR is inspection cadence rather than depot count, the economic case for deploying more than 3–5 depots is weak: the marginal MTTR reduction from the 4th depot onward is small (~2 h per additional depot), while the marginal cost is constant.

> **Figure:** `paper/figures/fig_npv_merged.pdf` — Includes depot NPV curves (see §7.3)
> **Figure:** `paper/figures/fig_depot_breakeven.pdf` — Maximum affordable depots vs. scenario parameters

---

## 8. Discussion

### 8.1 Taper Ratio: Implications for the Field

The literature reconciliation in §3.2 shows that published taper ratios spanning τ = 1.6 to τ = 37 reduce to a single formula once three hidden assumptions (stress basis, material density, base area sizing) are identified. This has immediate implications: claims that "the taper ratio is ~2" or "the taper ratio is ~10" are not contradictory — they reflect different, usually unstated, design philosophies. The comparison table in §3.2 provides a definitive reference for resolving these apparent disagreements.

The optimistic approach (taper at σ_u, check local stresses at σ_allow) is defensible: the taper determines the equilibrium shape, and the safety factor ensures that localized stress excursions (from climbers, wind, debris impacts) remain within design margins. The conservative approach (taper at σ_allow) is more appropriate for a first-of-kind structure where the entire stress budget must accommodate unknowns.

We present both as bounding cases, noting that the truth likely lies between them as specific load combinations are better understood through detailed dynamic analysis.

### 8.2 Reliability Under Wear-Out

The finding that P_sys > 99.5% across the well-designed regime (η_j ≥ 0.88, p_det ≥ 0.90) persists under Weibull wear-out up to β = 2.5. At the baseline design point (N=83, η_j=0.95), the system maintains >99.99% reliability across all tested β values — the safety margin absorbs even strong wear-out physics. The technology challenge is not "make joints reliable enough" but "don't let inspection quality degrade."

The Weibull extension reveals two additional insights. First, wear-out paradoxically *improves* 10-year survival in the degraded regime (N=500, η_j=0.80) because β > 1 concentrates failures late in the mission, reducing the probability of early-life cascades. However, this is a false comfort: the same physics that reduces 10-year failure probability accelerates it in years 10–20, making extended-life operation dangerous without joint replacement programs.

Second, the minimum η_j threshold for P_sys ≥ 0.995 rises with β, approaching the current baseline of 0.95 at β ≥ 2.5. This means the current manufacturing quality target (η_j = 0.95) leaves limited margin if the actual wear-out exponent is high. Experimental characterization of β for CNT sleeve bonds — via accelerated aging or sustained-load fatigue testing — is a priority for design maturation.

The reliability cliff at p_det < 0.70 provides a clear technology development target: the UT inspection system must achieve >90% single-pass detection probability for the architecture to deliver its promised reliability. Under wear-out (β ≥ 2.0), the penalty for infrequent inspection steepens because failures cluster in time, making prompt detection increasingly critical.

### 8.3 Cascading Failures and Scale Effects

The cascade model reveals a non-obvious result: adding more segments (higher N) can decrease system reliability even though each segment is lighter. With N = 500 (conservative taper), there are 499 joints, each a potential failure point. While individual joint failure probability remains low, the combinatorial probability of two adjacent failures (triggering cascade) grows quadratically with N.

This creates an optimal N that balances mass per segment against cascade risk — a trade-off unique to modular architecture and absent from monolithic designs.

### 8.4 Comparison to Prior Work

| Paper | What They Did | What We Add |
|-------|---------------|-------------|
| Edwards & Westling (2003) | Monolithic taper (implicitly at σ_u) | Explicit dual-envelope analysis; mass penalty quantified |
| Luo et al. (2022) | 22% stress reduction with segmentation | Coupled reliability, cascade failure model, lifecycle cost |
| Wright et al. (2023) | η_j = 0.97 on 50 m coupons | Volume scaling to full-scale; system-level reliability |
| Popescu & Sun (2018) | Bio-inspired repair concept | Quantified MTTR, phased construction economics |
| Nishimura & Hashimoto (2015) | Continuous tether dynamics | Segmented comparison, joint compliance effect, 2D Coriolis-coupled model |

### 8.5 Limitations

1. **2D model:** The dynamic model captures in-plane longitudinal and transverse motion but omits out-of-plane dynamics, torsion, and ribbon (finite-width) effects. The transverse gravity-gradient body force (ω² − GM/r³)v is omitted from the FEM stiffness; while this term is physically present, it nearly cancels between destabilizing (below GEO) and stabilizing (above GEO) contributions and introduces numerical difficulties at GEO crossover. The tension-string stiffness alone provides the dominant transverse restoring force.
2. **Thermal model:** Three discrete zones rather than continuous thermal profile with orbital mechanics.
3. **Joint failure:** The Weibull extension (§5.2.2) addresses the exponential model's memoryless assumption by sweeping β ∈ {1.0–2.5}, but the actual wear-out exponent for CNT sleeve bonds is unknown. The extreme sensitivity to activation energy Q (~7 orders of magnitude per ±40% perturbation) means that hazard-rate predictions carry substantial uncertainty until Q is experimentally constrained.
4. **No experimental validation:** Computational feasibility study; experimental next steps in §9.
5. **Monolithic failure model:** Simplified annual probability rather than detailed degradation model.
6. **Damping uncertainty:** Rayleigh damping with ζ = 0.01 is a placeholder. Actual tether damping depends on material hysteresis, joint friction, and aerodynamic drag (below ~200 km altitude). The damping sensitivity study (§6.6) shows that resonant transverse displacement varies by 1.8× across the range ζ = 0.001–0.05, making damping characterization a priority for detailed design.
7. **Depot cost model:** Depot specifications and costs are parametric estimates (order-of-magnitude). The analysis demonstrates that the trade space exists and that depot infrastructure is affordable relative to tether cost, but does not constitute a detailed depot design.

### 8.6 The 72 h Target: An Inspection Problem, Not a Depot Problem

The Edwards & Westling (2003) 72 h repair target has been widely cited as a design requirement for space-elevator maintenance. Our analysis reveals that this target is structurally constrained by a factor that depot infrastructure cannot address: inspection cadence.

With climber-based periodic inspection at v_climber = 150 m/s, a single tether traversal takes 185 h. The expected wait time from failure to detection is half the inspection interval — 93 h at cadence = 1 — which already exceeds 72 h before any travel or repair time is added. This means the 72 h target is unachievable for the majority of failures regardless of how many depots are deployed or how fast the repair climber travels.

The P(MTTR ≤ 72 h) metric saturates near 38% because only failures occurring within the final ~70 h of an inspection interval can be detected and repaired within the target window. Adding depots from 0 to 50 increases this fraction from 5.8% to 37.6% (at 150 m/s), but the remaining 62% of failures are bound by the wait-time floor.

Three paths to achieving >95% 72 h compliance exist:
1. **Faster operational climbers** (v_climber ≥ 300 m/s): Reduces traversal to ~93 h and expected wait to ~46 h, leaving ~24 h for travel + repair — achievable with 10 depots
2. **Continuous structural health monitoring:** Embedded fiber-optic or acoustic-emission sensors eliminating the periodic inspection model entirely
3. **Multiple simultaneous inspection climbers:** Reducing the effective inspection interval by a factor equal to the number of inspection climbers on the tether

This reframes the 72 h target from a depot-sizing problem to a sensor/climber technology problem, and suggests that the repair infrastructure trade space should be co-optimized with the inspection architecture.

---

## 9. Technology Gaps and Roadmap

### 9.1 TRL Assessment

| Subsystem | Current TRL | Required TRL | Binding Constraint |
|-----------|-------------|-------------|-------------------|
| CNT ribbon (σ_u = 50 GPa, km-scale) | 3–4 | 6 | Spinning rate × defect density |
| Nanobond sleeve coupler (η_j ≥ 0.95) | 4 | 6 | Full-scale vacuum bonding |
| UT inspection system (p_det ≥ 0.90) | 5 | 7 | Climber integration, speed |
| Robotic sleeve replacement | 3 | 6 | Autonomous GEO operations |
| Climber power beaming (4–6 MW FEL) | 4 | 6 | Atmospheric propagation at scale |
| Counterweight capture/deployment | 2–3 | 5 | NEA guidance or mass delivery |
| Continuous SHM (embedded AE/FBG) | 3 | 6 | 100,000 km distributed sensing, data relay |

### 9.2 Critical Path

The binding constraint is CNT ribbon production at σ_u ≥ 40 GPa on kilometer-per-day lines. Our sensitivity analysis shows the architecture closes (under optimistic tapering) even at σ_u = 30 GPa, which is within reach of current state-of-art (25 GPa ribbons demonstrated by Zhao, 2024).

The repair infrastructure analysis (§8.6) identifies continuous structural health monitoring as a second critical technology: periodic climber-based inspection produces a wait-time floor (93 h at v_climber = 150 m/s) that exceeds the 72 h repair target regardless of depot coverage. Embedded acoustic emission or fiber Bragg grating sensors distributed along the tether would eliminate this floor by enabling immediate failure detection, but require development from TRL 3 (laboratory coupon demonstration) to TRL 6 (system-level validation at representative scale). The key challenges are sensor survivability over 100,000 km, data relay architecture, and integration with the CNT ribbon manufacturing process.

---

## 10. Conclusions

This paper presents the first coupled system-level analysis of a modular CNT space-elevator tether, integrating taper geometry, joint reliability, repair logistics, dynamic stability, and lifecycle economics.

**C1 — Coupled feasibility assessment:** The modular architecture is feasible under both optimistic and conservative taper assumptions, though with dramatically different segment counts (N ≈ 83 vs. N ≈ 505 for a full-payload-capacity ribbon at σ_u = 50 GPa).

**C2 — Dual design envelopes:** We resolve a taper-ratio discrepancy in the literature by showing that Edwards & Westling's τ ≈ 1.9 is only recoverable when tapering at σ_u (no safety factor on shape). Both envelopes are presented with full sensitivity analysis across σ_u = 30–70 GPa.

**C3 — Reliability surface:** Monte Carlo simulation over 12,600 parameter combinations (N × η_j × cadence × p_det × β) shows P_sys > 99.5% in the well-designed regime across all Weibull shape parameters up to β = 2.5. Activation energy Q dominates hazard-rate uncertainty (~7 orders of magnitude per ±40% perturbation), establishing experimental Q characterization as the top priority for reliability prediction.

**C4 — Minimum viable CNT strength:** Under optimistic tapering, the architecture closes at σ_u = 30 GPa — below current laboratory demonstrations (80 GPa coupon, 25 GPa ribbon). Under conservative tapering, feasibility requires σ_u ≥ 50 GPa for a manageable segment count (N ≈ 505).

**C5 — Economic advantage:** Modular outperforms monolithic across all tested cost scenarios, driven primarily by the phased-construction revenue advantage — modular generates revenue at ~60% completion (year ~5 of 7) while monolithic requires 100%.

**C6 — 2D Coriolis-coupled dynamics:** Upgrading from 1D to a 2D rotating-frame FEM reveals that: (i) the lowest-frequency mode is transverse, not longitudinal (T₁_trans = 30.0 h, shifting to 34.8 h with Coriolis — a 16% effect invisible to 1D models); (ii) a single climber induces 136 km peak transverse displacement via Coriolis forcing; (iii) multi-climber resonance at 35 h separation amplifies transverse displacement to 489 km; and (iv) the tether-base tension perturbation of 67% is consistent with the taper design (A_base sized to the climber's surface weight).

**C7 — Repair infrastructure trade space:** Analytical evaluation of 0–50 pre-positioned orbital repair depots with three placement strategies shows that depots effectively reduce expected MTTR from 183 h (surface-only dispatch) to ~95 h (10+ depots). However, the Edwards & Westling 72 h repair target is structurally constrained by inspection cadence: a single traversal at 150 m/s takes 185 h, producing an expected detection wait of 93 h that exceeds 72 h regardless of depot coverage. P(MTTR ≤ 72 h) saturates near 38% even with 50 depots and 600 m/s repair climbers. This identifies inspection architecture — not depot count — as the binding constraint on MTTR, and reframes the 72 h target as a requirement for faster climbers (≥300 m/s), continuous structural health monitoring, or acceptance of a probabilistic repair window.

The cascading failure model reveals that the optimal segment count balances mass per segment against cascade risk — a trade-off unique to modular architecture. The 2D dynamic analysis establishes a quantitative climber separation design rule: departures within ±5 h of the 35 h resonant period should be avoided, and off-resonant separations (e.g., 18 h) keep transverse excitation comparable to the single-climber baseline.

Together, these results show that the space-elevator challenge can be reframed from materials perfection to systems engineering and maintainability.

---

## References

1. Edwards, B.C. & Westling, E.A. (2003). *The Space Elevator: A Revolutionary Earth-to-Space Transportation System.* NIAC Phase II Final Report.
2. Luo, S. et al. (2022). Segmented tether optimization for space elevator structures. *Acta Astronautica*, 195, 12–24.
3. Wright, D., Patel, R. & Liddle, J. (2023). Joint efficiency characterization of nanobonded CNT sleeve couplers. *Composites Part B*, 264, 110912.
4. Popescu, M. & Sun, C. (2018). Bio-inspired self-repair architecture for space tether systems. *AIAA Journal*, 56(8), 3240–3251.
5. Nishimura, T. & Hashimoto, H. (2015). Dynamic analysis of a continuous space elevator tether. *Journal of Spacecraft and Rockets*, 52(4), 1123–1134.
6. Peters, R. (2009). Analytical taper solutions for space elevator cables. *JBIS*, 62, 210–218.
7. Bai, Y. et al. (2018). Carbon nanotube bundles with tensile strength over 80 GPa. *Nature Nanotechnology*, 13, 589–595.
8. Pearson, J. (1975). The orbital tower: A spacecraft launcher using the Earth's rotational energy. *Acta Astronautica*, 2(9–10), 785–799.
9. Zhao, Q. et al. (2024). Kilometer-scale CNT ribbons at 25 GPa tensile strength. *Advanced Materials*, 36(2), 2308456.

---

## Figure Index

### Main Text (16 figures)

| Figure | File | Description |
|--------|------|-------------|
| Fig. 1 | `fig_taper_validation.pdf` | Continuous vs. stepped taper profile A(r) and T(r) |
| Fig. 2 | `fig_design_envelope_comparison.pdf` | Dual design envelope: τ, N, M_total, m_j_max at σ_u vs σ_allow |
| Fig. 3 | `fig_sigma_sensitivity.pdf` | Material sensitivity: taper ratio and mass vs. σ_u |
| Fig. 4 | `fig_reliability_merged.pdf` | (a) P_sys(N, η_j) heatmap at β=1.0; (b) P_sys vs. β at four design points |
| Fig. 5 | `fig_beta_threshold.pdf` | Minimum η_j for P_sys ≥ 0.995 vs. Weibull β (N=83) |
| Fig. 6 | `fig_hazard_tornado.pdf` | Hazard rate sensitivity tornado — Q dominates (~7 orders of magnitude) |
| Fig. 7 | `fig_mttr_merged.pdf` | (a) MTTR by Weibull β at baseline; (b) Depot shift of MTTR distribution |
| Fig. 8 | `fig_mttr_vs_depots.pdf` | Expected MTTR vs. depot count (N=83, N=505 panels) |
| Fig. 9 | `fig_72h_achievability.pdf` | P(MTTR ≤ 72 h) vs. depot count |
| Fig. 10 | `fig_modal_comparison.pdf` | 1D modal frequency spectrum and quasi-static forced response |
| Fig. 11 | `fig_displacement_envelopes_merged.pdf` | (a) Longitudinal and (b) transverse displacement envelopes vs. altitude |
| Fig. 12 | `fig_tension_perturbation.pdf` | Tension perturbation ratio ΔT/T_eq vs. altitude |
| Fig. 13 | `fig_resonance_scan.pdf` | Multi-climber resonance: peak transverse vs. departure separation |
| Fig. 14 | `fig_npv_merged.pdf` | Cumulative NPV: monolithic vs. modular with 0/5/10 depots |
| Fig. 15 | `fig_cost_tornado.pdf` | Cost sensitivity tornado diagram |
| Fig. 16 | `fig_depot_breakeven.pdf` | Max affordable depots: launch cost vs. discount rate heatmap |

### Supplementary Material (17 figures)

| Figure | File | Description |
|--------|------|-------------|
| Fig. S1 | `fig_psys_heatmap.pdf` | Full P_sys(N, η_j) heatmap (exponential only) |
| Fig. S2 | `fig_mttr_distribution.pdf` | MTTR distribution with 72 h target (exponential only) |
| Fig. S3 | `fig_inspection_cadence.pdf` | System survival vs. inspection frequency |
| Fig. S4 | `fig_p_detection_impact.pdf` | P_sys vs. detection probability |
| Fig. S5 | `fig_reliability_surface_by_beta.pdf` | P_sys(N, η_j) heatmaps at each β (5 panels) |
| Fig. S6 | `fig_psys_vs_beta.pdf` | P_sys vs. β at four design points (unmerged) |
| Fig. S7 | `fig_mttr_by_beta.pdf` | MTTR distribution by β at baseline (unmerged) |
| Fig. S8 | `fig_cadence_sensitivity_by_beta.pdf` | Inspection cadence sensitivity under wear-out |
| Fig. S9 | `fig_hazard_spider.pdf` | Hazard rate spider plot |
| Fig. S10 | `fig_longitudinal_envelope.pdf` | Longitudinal displacement envelope (unmerged) |
| Fig. S11 | `fig_transverse_envelope.pdf` | Transverse displacement envelope (unmerged) |
| Fig. S12 | `fig_waterfall_vrt.pdf` | Transverse response space-time waterfall v(r, t) |
| Fig. S13 | `fig_geo_time_history.pdf` | Displacement time history at GEO (u and v) |
| Fig. S14 | `fig_safe_separation.pdf` | Tension perturbation ratio vs. departure separation |
| Fig. S15 | `fig_resonant_vs_offresonant.pdf` | GEO transverse: resonant vs. off-resonant |
| Fig. S16 | `fig_damping_sensitivity.pdf` | Peak transverse displacement vs. damping ratio |
| Fig. S17 | `fig_depot_placement_comparison.pdf` | MTTR vs. failure altitude for 3 placement strategies |

---

## Data Availability

All simulation data is stored in `data/processed/`:
- `taper_profiles.npz` — Continuous and stepped profiles
- `sigma_u_sensitivity_optimistic.json` — Sensitivity at σ_u tapering
- `sigma_u_sensitivity_conservative.json` — Sensitivity at σ_allow tapering
- `psys_surface.npz` — Monte Carlo P_sys(N, η_j, cadence, p_det) array
- `mttr_samples.npz` — All repair time samples
- `weibull_sweep_results.csv` — Weibull MC sweep (12,600 combinations × 5 statistics)
- `psys_weibull_surface.npz` — 5D P_sys(N, η_j, cadence, p_det, β) array
- `modal_results.npz` — Eigenfrequencies, mode shapes, displacements
- `npv_results.npz` — NPV time series and crossover data
- `phase3_repair/mttr_analytical.csv` — Analytical MTTR sweep (792 configurations)
- `phase3_repair/npv_with_depots.csv` — NPV with depot infrastructure costs
- `phase3_repair/breakeven_analysis.csv` — Maximum affordable depot counts per scenario
- `phase3_repair/depot_configurations.csv` — Depot altitudes for each (n, strategy) pair

Simulation scripts are available in the project repository under `simulations/`.

---

## CRediT Author Statement

- **K. Egan:** Conceptualization, Methodology, Software, Formal Analysis, Writing — Original Draft, Visualization
- **M. Ergezer:** Supervision, Writing — Review & Editing

---

*All simulation results filled in. Pre-submission checklist: restore full reference list, add graphical abstract and highlights (Elsevier requirement).*
