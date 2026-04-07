# Literature Review: Modular Space Elevator Tether — CNT Joint Reliability

**Date:** 2026-04-07  
**Query:** modular space elevator tether CNT joint reliability  
**Scope:** Space elevator tether segmentation, carbon nanotube fiber/cable joining, joint reliability, and failure modes

---

## 1. Executive Summary

This review covers the intersection of three research domains: **(a)** space elevator tether design with modular/segmented architectures, **(b)** carbon nanotube (CNT) fiber and cable mechanical properties at the macro scale, and **(c)** joint and splice reliability in CNT assemblies. The key finding is that **no peer-reviewed work directly addresses the reliability of CNT-based joints in a modular space elevator tether**. The closest approaches come from:

- Bio-inspired stochastic repair models for tether segment reliability (Popescu & Sun, 2018)
- Segmented tether dynamics models (Luo et al., 2022)
- CNT interfacial mechanics and inter-tube load transfer (Zhang, 2017; Zhang & Li, 2009)
- Reel-to-reel and splice-based deployment concepts that avoid in-orbit splicing (Gassend, 2004)
- CNT fiber composite strength benchmarks (Mikhalchan & Vilatela, 2020)

The gap between individual CNT strength (~50–130 GPa) and macroscopic CNT fiber strength (~1–6 GPa for films/composites) remains the central materials challenge. Joint reliability compounds this: no published splice or joint achieves even the bulk CNT fiber's already-reduced strength. This review maps the evidence landscape and identifies open questions for modular tether designs.

---

## 2. Space Elevator Tether: Segmented and Modular Designs

### 2.1 Classical Uniform-Stress Tether

The canonical space elevator design uses a continuous tether with exponentially varying cross-section (Pearson, 1975; Edwards, 2003). The taper ratio from base to GEO is $T = \exp(K / L_c)$, where $L_c = \sigma / w$ is the characteristic length (stress / specific weight). For carbon nanotubes at 130 GPa UTS, $T \approx 2.6$; for steel, $T \approx 10^{66}$, rendering steel infeasible.

### 2.2 Segmented Tether Models

**Luo et al. (2022)** published two papers in *Aerospace* on segmented space elevators:

- **"Model and Optimization of the Tether for a Segmented Space Elevator"** (Aerospace 9(5), 278): Develops an optimization model for a tether divided into discrete segments with intermediate platforms. The segmented design reduces the required material strength by distributing loads across platforms that provide intermediate support via centrifugal force. Key result: segmentation can reduce the required specific strength by ~30–50% compared to a monolithic tether, at the cost of added platform mass.

- **"The Stability Analysis of a Tether for a Segmented Space Elevator"** (Aerospace 9(7), 376): Analyzes lateral oscillation modes and stability of the segmented tether. Finds that inter-segment connections are critical points for dynamic amplification. **Connection stiffness and damping at segment joints strongly affect system-level stability.**

These papers treat joints as idealized connections with specified stiffness/damping. They do not model the material-level failure of the joint itself.

### 2.3 Biological Repair Paradigm

**Popescu & Sun (2018), "Building the Space Elevator: Lessons from Biological Design"** (arXiv:1804.06453), proposes a paradigm shift: instead of requiring ultra-strong materials at low working stress ratios (ω < 50%), operate at high stress ratios (ω = 60–90%) with continuous autonomous repair. Key results:

- Models each tether *segment* as a bundle of parallel filaments undergoing stochastic Weibull-distributed creep rupture
- With repair rates of ρ = 1–30 filaments/hour (depending on working stress ratio), even **Kevlar** (σ_max ≈ 3.6 GPa, an order of magnitude weaker than CNTs) achieves reliable segment operation
- **The model is explicitly modular**: the tether is discretized into vertically stacked segments, each containing N₀ parallel filaments. The number of filaments varies by height (discretized exponential taper)
- Repair mechanism: autonomous robots replace broken filaments. Material flux is ~3% of segment mass per hour at ω = 90%

**Relevance to joints:** This model avoids the joint problem entirely by treating each segment as a self-contained bundle. Inter-segment load transfer is assumed perfect. The paper acknowledges this simplification.

### 2.4 Exponential Tether and Splice-Based Deployment

**Gassend (2004/2024), "Exponential Tethers for Accelerated Space Elevator Deployment"** (arXiv:2412.17198), introduces the "redeploy and splice" buildup method:

- Uses exponential (not uniform-stress) tether profiles during construction
- Material is reeled up at the counterweight and spliced to the existing tether, approximately doubling its cross-section per cycle
- **Splicing at the counterweight is identified as a critical engineering concern** — the paper notes that consumables are likely needed for the splice operation and that cutting the cable at the counterweight must be done with extreme robustness

The paper explicitly contrasts this with climber-based buildup where hundreds of separate ribbons are spliced together at 200 km/h in orbit. The reel-to-reel method avoids this "high-altitude ribbon splicing" and may allow lower safety factors due to better ribbon quality.

**This is the most explicit treatment of tether splicing in the space elevator literature**, though it remains conceptual without quantitative joint-strength analysis.

---

## 3. CNT Fiber/Cable Mechanical Properties

### 3.1 Individual CNT vs. Macroscopic Assembly Gap

The strength gap between individual CNTs and their macroscopic assemblies is enormous:

| Scale | Tensile Strength | Modulus | Source |
|-------|-----------------|---------|--------|
| Individual SWCNT | 13–52 GPa (measured), ~100 GPa (theoretical) | 270–1470 GPa | Yu et al. (2000) |
| Individual MWCNT | 11–63 GPa | 270–950 GPa | Yu et al. (2000) |
| CNT bundle (2–7 tubes) | 27–31 GPa/SG | 337–640 GPa/SG | Bai et al. (2018) |
| CNT fiber (LC-spun) | ~2.5 GPa (~1.6 GPa/SG) | ~250 GPa (160 GPa/SG) | Tsentalovich et al. (2017) |
| CNT fiber (FCCVD-spun) | ~1.5 GPa/SG | ~70 GPa/SG | Various |
| CNT/BMI composite film | 5.8–6.9 GPa | 212–351 GPa | Han et al. (2015) |
| Commercial CNT fabric | 30–300 MPa | 0.5–5 GPa | Various commercial |

**Source:** Mikhalchan & Vilatela (2020), arXiv:2004.13352

The gap is dominated by **inter-tube load transfer** — the shear strength between adjacent CNTs is orders of magnitude below the intra-tube covalent bond strength.

### 3.2 Interfacial Mechanics: The Fundamental Bottleneck

**Zhang (2017), "Interfacial Mechanical Behaviors in Carbon Nanotube Assemblies"** (arXiv:1705.08697), provides the most comprehensive review of CNT interfacial mechanics:

- **Inter-shell sliding (MWCNTs):** Shear strength 0.08–0.66 MPa. Superlubricity observed in cm-long DWCNTs (friction ~1.37–1.64 nN for ~10⁸ atoms)
- **Inter-tube friction (parallel):** 0.25–0.5 GPa for commensurate pairs; 0.5–1 MPa for incommensurate pairs
- **Cross-angle friction:** ~4 MPa (experimental)
- **Critical contact length for 11 GPa strength:** ~3,800 nm without deformation, ~1,300 nm with radial deformation (Qian et al., 2003)

**Strategies to improve load transfer:**
1. **Twist:** Optimal at 15–20° angle; induces radial deformation and collapse of few-walled CNTs, increasing contact area. A "double-peak" strength behavior emerges at 27–30° from structural phase transition
2. **Solvent densification:** Highly polar solvents (DMF, DMSO, NMP, ethylene glycol) increase fiber strength from ~0.86 GPa to 1.3–1.6 GPa
3. **Polymer impregnation:** Thermosetting polymers (PI, BMI, epoxy) bridge non-neighboring CNTs; strength up to 3–7 GPa in composite films
4. **Covalent cross-linking:** Electron irradiation at 80 keV creates inter-tube covalent bonds, increasing bending modulus 30×. However, long exposure damages structure. Incandescent tension annealing (2000°C vacuum) forms sp³ bonds, improving modulus from 37 to 170 GPa
5. **Pressure-induced collapse:** Pre-pressing CNT bundles above critical pressure (~0.5 GPa for (23,0) SWCNTs) permanently collapses tubes, increasing friction 1.5–4× and reducing cross-section. Effective for few-walled CNTs with diameter >5 nm

### 3.3 Enhancement via Collapse Phase Transition

**Zhang & Li (2009), "Enhancement of Friction between Carbon Nanotubes"** (arXiv:0912.01993):

- MD simulations show pre-pressing CNT bundles to collapse increases static friction from 0.1 to 0.4–0.45 meV/Å per atom (4× for commensurate tubes)
- Combined with area reduction (1.63×), effective strength improvement is 6.5×
- Minimum tube length for 10 GPa drops from 1,090 nm to 167 nm after collapse
- For random-chirality bundles, sliding friction increases 1.5×, overall strength nearly triples
- Large-diameter tubes (e.g., (40,0)) remain collapsed at atmospheric pressure

### 3.4 Defect-Tolerant Strength Scaling

**Carpinteri & Pugno (2008), "Super-Bridges Suspended Over Carbon Nanotube Cables"** (arXiv:0804.01446):

Uses the Multi-Fractal Scaling Law to predict macroscopic strength of CNT cables:
$$\sigma_f = \frac{\sigma_{\text{macro}}}{\sqrt{1 + l_{\text{ch}}/L}} + \frac{l_0}{L}$$

- Nano-strength: σ_nano = 34 GPa (Weibull fit to experiments)
- **Macroscopic asymptotic strength: σ_macro ≈ 10.2 GPa** (for defective but optimized cables)
- This is derived from 4-level hierarchical stochastic simulations spanning 10 orders of magnitude from nanotube to km-scale
- Notes that 10 GPa CNT fibers were already available (Koziol et al., 2007), suggesting km-long cables at similar strength "could be realized in the near future"

**Critical implication for joints:** If bulk cable strength asymptotes to ~10 GPa, any joint must approach this value to avoid being the weak link. No demonstrated joint technology achieves even 50% of this.

---

## 4. Joint and Splice Technology for CNT Assemblies

### 4.1 Current State

**No published work demonstrates a high-strength splice or mechanical joint between CNT fibers or cables.** The closest analogues are:

1. **Epoxy cross-linked CNT threads** (Yu et al., 2016, Materials 9(2), 68): Epoxy infiltration improves thread strength but creates a fundamentally different failure mode at the joint. Strength improvements are modest (~50–100%)

2. **FRP lap splice with CNT-enhanced epoxy** (academia.edu source): Uses CNTs as additives to epoxy in conventional FRP lap splices. Not a CNT-to-CNT joint

3. **CNT yarn failure in polymer matrices** (Springer Nature, 2025): Studies failure behavior of CNT yarns embedded in polymer matrices. Observes pull-out and bridging mechanisms. The yarn-matrix interface is the failure site, not a yarn-yarn joint

4. **Polymer-infiltrated fiber "joints":** When CNT fibers are infiltrated with polymer, the effective modulus increases (confirmed by Raman spectroscopy; Mas et al., 2019). This suggests that polymer-mediated load transfer could serve as a joining mechanism, but quantitative joint efficiency data is absent

### 4.2 Failure Modes at Joints

Based on the CNT assembly mechanics literature, expected joint failure modes include:

1. **Shear pull-out:** Dominant mode for all CNT fiber joints. The van der Waals inter-tube shear strength (~0.5–1 MPa for incommensurate pairs) limits load transfer at splice overlaps
2. **Polymer matrix failure:** For adhesive-bonded joints, the polymer (epoxy, BMI) fails before the CNT fiber
3. **Stress concentration at joint boundaries:** Abrupt changes in cross-section or stiffness at joint edges create stress risers
4. **Creep at joints:** The Popescu & Sun (2018) model shows Weibull-distributed creep rupture is the dominant time-dependent failure mode. Joints likely have worse creep properties than bulk fiber
5. **Environmental degradation:** Atomic oxygen, UV, and thermal cycling in the space environment degrade polymer-based joints preferentially

### 4.3 Required Joint Properties for a Modular Tether

For a segmented space elevator with N segments, the system reliability R_sys ≈ R_joint^N (assuming joints are the weakest links and failures are independent). For N = 1,000 segments and R_sys = 0.999 over mission lifetime:

$$R_{\text{joint}} \geq 0.999^{1/1000} \approx 0.999999$$

This is an extremely demanding requirement — each joint must have a probability of failure below ~10⁻⁶ over the mission lifetime. This drives the need for either:
- Very few joints (long segments, monolithic construction)
- Redundant parallel load paths at each joint
- Continuous monitoring and repair capability (Popescu & Sun paradigm)

---

## 5. Gap Analysis and Open Questions

### 5.1 Critical Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| No quantitative CNT-to-CNT joint strength data | **Critical** | No published splice or joint efficiency for CNT fibers |
| No creep-rupture data for CNTs | **Critical** | Popescu & Sun (2018) used Kevlar data as proxy; CNT creep lifetime distributions are unknown |
| Joint reliability under combined loading | **High** | Space environment includes tension + vibration + thermal cycling + atomic oxygen |
| Scalability of collapse-enhanced fibers | **High** | Zhang & Li (2009) results are MD simulation only; experimental validation at fiber scale lacking |
| Dynamic behavior of segmented tethers at joints | **Moderate** | Luo et al. (2022) used idealized joint models |
| Autonomous repair feasibility | **Moderate** | Popescu & Sun assume repair robots; no engineering design exists |

### 5.2 Open Questions

1. **Can a CNT fiber splice achieve >50% of bulk fiber strength?** No demonstrated path exists. Potential approaches: ultra-long overlap with collapsed-tube geometry; covalent cross-linking at the splice; polymer-mediated load transfer with high-modulus matrix
2. **What is the creep-rupture lifetime distribution of CNT fibers?** This is prerequisite for any reliability analysis
3. **Is a jointless tether feasible?** Gassend's reel-to-reel method avoids splicing during operation but still requires initial deployment joints. The exponential tether concept minimizes splicing
4. **Can the bio-inspired repair paradigm compensate for joint weakness?** If joints are repairable (replaceable segments), the reliability requirement shifts from the joint to the repair rate
5. **What minimum segment length avoids joint-dominated failure?** Depends on the ratio of joint strength to bulk fiber strength and the stress profile along the tether

---

## 6. Recommendations for Future Work

1. **Experimental program on CNT fiber splicing:** Systematic study of lap splice, braided joint, and adhesive-bonded joint configurations with quantitative strength and creep data
2. **CNT creep-rupture characterization:** Fundamental data needed for any reliability model
3. **Coupled joint-tether dynamics modeling:** Extend Luo et al. (2022) with realistic joint stiffness, strength, and failure models
4. **Collapse-enhanced fiber development:** Scale up Zhang & Li (2009) collapse pre-treatment from MD simulation to macroscopic fiber
5. **Redundant joint architectures:** Explore multi-path, damage-tolerant joint designs inspired by biological connective tissue (tendons, ligaments)

---

## Sources

### Primary Academic Papers (arXiv / Peer-Reviewed)

1. Popescu, D.M. & Sun, S.X. (2018). "Building the Space Elevator: Lessons from Biological Design." arXiv:1804.06453. https://arxiv.org/abs/1804.06453

2. Gassend, B. (2004/2024). "Exponential Tethers for Accelerated Space Elevator Deployment." arXiv:2412.17198. https://arxiv.org/abs/2412.17198

3. Gassend, B. (2004/2025). "Non-Equatorial Uniform-Stress Space Elevators." arXiv:2509.16231. https://arxiv.org/abs/2509.16231

4. Zhang, X. (2017). "Interfacial Mechanical Behaviors in Carbon Nanotube Assemblies." arXiv:1705.08697. https://arxiv.org/abs/1705.08697

5. Mikhalchan, A. & Vilatela, J.J. (2020). "A Perspective on High-performance CNT fibres for Structural Composites." arXiv:2004.13352. https://arxiv.org/abs/2004.13352

6. Carpinteri, A. & Pugno, N.M. (2008). "Super-Bridges Suspended Over Carbon Nanotube Cables." arXiv:0804.01446. https://arxiv.org/abs/0804.01446

7. Zhang, X. & Li, Q. (2009). "Enhancement of Friction between Carbon Nanotubes: An Efficient Strategy to Strengthen Fibers." arXiv:0912.01993. https://arxiv.org/abs/0912.01993

8. Luo, S. et al. (2022). "Model and Optimization of the Tether for a Segmented Space Elevator." *Aerospace* 9(5), 278. https://www.mdpi.com/2226-4310/9/5/278

9. Luo, S. et al. (2022). "The Stability Analysis of a Tether for a Segmented Space Elevator." *Aerospace* 9(7), 376. https://www.mdpi.com/2226-4310/9/7/376

### Web / Industry Sources

10. Wright, D. & Nixon, A. (2024). "Status of Space Elevator Tether Materials." ISEC/ISDC presentation. https://static1.squarespace.com/static/5e35af40fb280744e1b16f7b/t/6660d82d5def5e66eeef2a8c/1717622830191/2024ISDC-08+Space+Elevator+Tether+Materials.pdf

11. Nixon, A. (2025). "State of the art of tether materials manufacturing." ISEC 2025. https://static1.squarespace.com/static/5e35af40fb280744e1b16f7b/t/68bd98f0c21c671d3ff7430c/1757255920849/ISEC2025-State-of-the-Art-of-Tether-Materials-Manufacturing.pdf

12. "Failure behavior of carbon nanotube yarns embedded in polymer matrices." (2025). *Journal of Materials Science*. https://link.springer.com/article/10.1007/s10853-025-11981-5

13. "Conditions at the interface between the space elevator tether and its climber." (2023). *Acta Astronautica* 211, 631–649. https://static1.squarespace.com/static/5e35af40fb280744e1b16f7b/t/64ce953291851131bb45d087/1691260213746/ISEC-2023-Acta-Astronautica-Space-Elevator-Tether-Climber-Interface.pdf
