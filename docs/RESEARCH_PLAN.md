# Research Plan: Modular CNT Space-Elevator Tether → Acta Astronautica

**Goal:** Submit publication-ready manuscript to Acta Astronautica by October 2026  
**Review cycle:** ~38 weeks → expected acceptance mid-2027  
**Parallel:** Submit ISEC 2026 conference abstract by June 1, 2026  

---

## Strategic Positioning

### Why This Paper Will Be SOTA

The space-elevator field is split between materials scientists pushing CNT numbers and systems engineers drawing conceptual architectures. No one does rigorous quantified systems analysis bridging both. We are the first to treat the modular tether as a **systems engineering problem with coupled trade-offs**.

Five strategic moves:

1. **Validate against the established baseline.** Match static profile to Edwards & Westling (2003) NIAC within 2% — inherit credibility before extending.
2. **Produce a novel decision surface.** The P_sys(N, η_j) Monte Carlo heatmap doesn't exist in the literature. This is the figure that gets cited.
3. **Show robustness, not just performance.** σ_u sensitivity down to 30 GPa proves architecture works with today's materials.
4. **Frame modular as an economic argument.** NPV crossover answers "is repair cheaper than replacement?" — the question funders care about.
5. **Engage the active community.** Cite and extend Luo, Wright, Popescu, Nixon, Swan — position as contributing to an active conversation.

### Differentiation vs. Prior Work

| Paper | What They Did | What We Add |
|-------|---------------|-------------|
| Edwards & Westling (2003) | Monolithic taper, baseline architecture | Modular extension + validated match + mass penalty |
| Luo et al. (2022) | Segmented stress optimization (22% reduction) | Coupled reliability (Monte Carlo), mass equalization, lifecycle cost |
| Wright et al. (2023) | Joint efficiency η = 0.97 on coupons | System-level reliability — what η_j threshold does the system need? |
| Popescu & Sun (2018) | Bio-inspired repair concept | Quantified MTTR, repair cost in NPV model |
| Nishimura & Hashimoto (2015) | Continuous tether dynamics | Segmented modal comparison |
| Peters (2009) | Analytical taper solutions | Multi-σ_u parametric sweep showing feasibility envelope |

---

## Repository Structure

```
modular-cnt-tether/
├── docs/
│   ├── RESEARCH_PROPOSAL.md       # This file's companion — what and why
│   └── RESEARCH_PLAN.md           # This file — how and when
├── paper/
│   ├── main.tex                   # Manuscript (Elsevier elsarticle.cls)
│   ├── sections/                  # Individual section .tex files
│   ├── figures/                   # Publication-quality PDFs
│   └── tables/                    # Standalone table files
├── simulations/
│   ├── fea/
│   │   ├── taper_profile.py       # Static taper + NIAC validation
│   │   └── modal_analysis.py      # Segmented vs. continuous modes
│   ├── monte_carlo/
│   │   └── joint_reliability.py   # P_sys Monte Carlo (core result)
│   ├── thermal/                   # Thermal environment modeling
│   └── cost_model/
│       └── npv_model.py           # Lifecycle NPV comparison
├── data/
│   ├── parameters.yaml            # LOCKED master parameter file
│   ├── raw/                       # Simulation outputs
│   └── processed/                 # Cleaned results for figures
├── scripts/
│   └── acta_astronautica.mplstyle # Matplotlib publication style
└── references/
    └── main.bib                   # BibTeX database
```

### Critical Rule

**All simulations load from `data/parameters.yaml`.** No hardcoded physical constants in scripts. Any parameter change triggers a full re-run.

---

## Locked Parameters (`data/parameters.yaml`)

```yaml
physical:
  GM_earth: 3.986004418e14   # m³/s²
  R_earth: 6.3781e6          # m
  omega_earth: 7.2921159e-5  # rad/s
  k_B: 1.380649e-23          # J/K

orbital:
  r_GEO: 4.21642e7           # m
  h_GEO: 3.5786e7            # m

tether:
  L_total: 1.0e8             # m (100,000 km)
  w_max: 1.2                 # m

material:
  rho: 1300.0                # kg/m³
  sigma_u_baseline: 50.0e9   # Pa
  E_yarn: 280.0e9            # Pa
  k_parallel: 500.0          # W/(m·K)
  CTE: 4.0e-6                # 1/K

design:
  SF: 2.0
  chi_rad: 0.85
  eta_j_baseline: 0.95
  sigma_allow: 25.0e9        # Pa (= sigma_u / SF)
  sigma_allow_net: 20.2e9    # Pa (= sigma_u * chi_rad * eta_j / SF)

segments:
  m_star: 18000.0            # kg (target per-segment mass)
  m_launch_cap: 30000.0      # kg (hard limit)
  N_baseline: 18
  m_sleeve: 35.0             # kg per joint

joints:
  ell_sleeve: 3.0            # m
  lambda_0: 1.2e-8           # 1/h (hazard rate)
  Q_activation: 1.76e-19     # J (1.1 eV)

climber:
  m_climber: 20000.0         # kg
  v_climber: 150.0           # m/s
  separation_min: 1.2e7      # m (12 Mm)

monte_carlo:
  n_trajectories: 100000
  t_mission: 87600.0         # h (10 years)
  N_sweep: [12, 15, 18, 21, 24]
  eta_j_sweep: [0.88, 0.90, 0.93, 0.95, 0.97]
  inspection_cadence_sweep: [1, 2, 5, 10]
  p_detection: 0.995
  t_joint_replace: 1.4       # h

sensitivity:
  sigma_u_sweep: [30.0e9, 35.0e9, 40.0e9, 50.0e9, 60.0e9, 70.0e9]

cost:
  discount_rate_sweep: [0.05, 0.07, 0.10]
  launch_cost_sweep: [500, 1000, 1500, 2000]  # $/kg to GTO
  payload_revenue_sweep: [200, 300, 500]       # $/kg to GEO
  system_lifetime: 30        # years
```

---

## BLOCKER: Taper Ratio Discrepancy — Resolve First

**The current draft claims τ ≈ 1.6. Our numerical integration gives τ ≈ 12.4 at the same σ_allow = 25 GPa, ρ = 1300 kg/m³.**

The peak area location is correct (GEO ± 1 km), so the physics model is right. The magnitude discrepancy likely comes from:

1. Draft may use σ_u = 50 GPa (not σ_allow = 25 GPa) for the taper calculation — at σ_u/ρ = 38.5 MYuri, τ ≈ 1.9, close to claimed 1.6
2. Sign convention issue in Eq. 6 of the draft
3. The 1.6 figure may come from Peters (2009) under different assumptions

**Before any other simulation work:**
- Re-derive Eq. 6 from force balance, verify sign convention
- Check Peters (2009) and Gassend (2024) for their τ values and assumptions
- Decide: do we taper at σ_u (full strength) or σ_allow (with safety factor)?
- If τ ≈ 12 is correct, recompute N, segment masses, and all of Table 4
- Run taper_profile.py at both σ_u and σ_allow to see which matches the literature

This changes the paper significantly but makes it more honest. Showing the architecture works at realistic τ is a stronger contribution.

---

## Phase 0: Foundation & Setup (Mar 17 – Mar 31)

| Task | Description | Output |
|------|-------------|--------|
| P0.1 | Resolve taper ratio discrepancy (see blocker above) | Updated parameters.yaml, corrected §3.2 |
| P0.2 | Set up Elsevier LaTeX template (elsarticle.cls, single-column review) | paper/main.tex compiles |
| P0.3 | Modularize current draft into section .tex files | paper/sections/*.tex |
| P0.4 | Build BibTeX database from current 48 refs, verify each entry | references/main.bib |
| P0.5 | Literature search: space elevator tether 2024–2026, CNT strength 2024–2026 | 3–5 new must-cite papers |
| P0.6 | Verify Python environment: NumPy, SciPy, Matplotlib, pandas, PyYAML, h5py | requirements.txt |

---

## Phase 1: Core Simulations (Apr 1 – May 15) — CRITICAL PATH

### 1A. Static Taper Validation (Apr 1–15)

**Script:** `simulations/fea/taper_profile.py` (starter code exists, needs refinement after blocker resolved)

Tasks:
- Integrate Eq. 7 numerically for continuous A(y), T(y), σ(y) at 1 km resolution
- Compute piecewise-constant N-segment stepped profile via Eq. 10
- Overlay our T(y) on Edwards & Westling Fig. 4 (digitize from NIAC report)
  - Validation target: peak tension location within 50 km, magnitude within 2%
- σ_u sensitivity sweep: {30, 35, 40, 50, 60, 70} GPa
  - Record τ, M_total, N, m_j_max for each
  - Find minimum σ_u where architecture closes (m_j ≤ 30 t, τ reasonable)

**Outputs:**
- `data/processed/taper_profiles.npz`
- `data/processed/sigma_u_sensitivity.json`
- `paper/figures/fig_taper_validation.pdf`
- `paper/figures/fig_sigma_sensitivity.pdf`

### 1B. Monte Carlo Joint Reliability (Apr 15 – May 10) ⚡ THE MONEY RESULT

**Script:** `simulations/monte_carlo/joint_reliability.py` (skeleton exists, needs tuning after blocker)

Joint lifetime model:
```
λ_j(T) = λ_0 · exp(-Q / (k_B · T)) · (0.97 / η_j)^4
```
- T = T(y) from thermal profile along tether
- System failure = any joint η_j < η_crit with no repair before cascade

Parameter sweep:
- N ∈ {12, 15, 18, 21, 24}
- η_j ∈ {0.88, 0.90, 0.93, 0.95, 0.97}
- Inspection cadence ∈ {every 1, 2, 5, 10 climber passages}
- 10⁵ trajectories per combination → 10⁷ total
- Runtime estimate: 2–4 hours on single A100 (embarrassingly parallel)

**Outputs:**
- `data/processed/psys_surface.npz` — P_sys(N, η_j) matrix
- `paper/figures/fig_psys_heatmap.pdf` ← **Most important figure in the paper**
- `paper/figures/fig_mttr_distribution.pdf`
- `paper/figures/fig_inspection_cadence.pdf`

**Headline numbers needed for abstract:**
- "System survival probability of X% over 10 years with N segments and η_j ≥ Y"
- "Minimum joint efficiency for 99.9% survival: η_j = Z"
- "Mean time to repair: W h (median) for representative 50 km spans"

### 1C. Dynamic Modal Analysis (May 1–15)

**Script:** `simulations/fea/modal_analysis.py` (to build)

- Lumped-mass-spring model: N+1 masses, springs k_j = η_j · E · A_j / L_j
- Eigenvalue problem via scipy.sparse.linalg.eigsh, first 20 modes
- Compare against continuous string (N → ∞ limit)
- Forced response: 20 t climber traversing at 150 m/s
- Verify 12 Mm separation rule and max joint-node displacement

**Outputs:**
- `paper/figures/fig_modal_comparison.pdf`
- Go/no-go on the climber separation rule

### 1D. Lifecycle Cost Model (May 5–15)

**Script:** `simulations/cost_model/npv_model.py` (to build)

```
Modular NPV  = -C_build + Σ(Revenue_t - C_ops - C_repair) / (1+r)^t
Monolithic NPV = -C_build + Σ(Revenue_t - C_ops - P_fail · C_replace) / (1+r)^t
```

Sweep: launch cost × discount rate × payload revenue  

**Outputs:**
- `paper/figures/fig_npv_crossover.pdf`
- `paper/figures/fig_cost_tornado.pdf`

---

## Phase 2: Paper Writing (May 15 – Jul 31)

### New Sections to Write

| Section | Content | Pages | Priority |
|---------|---------|-------|----------|
| §5 Simulation Methodology | FEA setup, Monte Carlo framework, cost model, validation approach | 3–4 | HIGH |
| §6 Results | Taper validation, σ_u sensitivity, P_sys surface, modal comparison, MTTR | 5–7 | HIGH |
| §7 Lifecycle Cost Analysis | NPV crossover, sensitivity, economic interpretation | 2–3 | MEDIUM |
| §8 Discussion | Interpretation, comparison to prior work, limitations | 2–3 | HIGH |
| §9 Technology Gaps | TRL table per subsystem, binding constraints, roadmap | 1–2 | MEDIUM |
| §10 Conclusions | Summary of quantitative findings, restate C1–C5 | 1 | HIGH |

### Revisions to Existing Sections

**§1 Introduction:**
- Remove all placeholder text ("Will update this abstract", duplicate org paragraphs)
- Fix all `??` cross-references
- Rewrite to frame around five contributions C1–C5
- Write abstract LAST with specific numbers from §6

**§2 Literature Review:**
- Convert annotated bibliography → critical synthesis
- For each thread: what was done → what's missing → how we fill it
- Add 2024–2026 citations
- End with explicit "Research Gap" paragraph

**§3 Theoretical Foundations:**
- Light edits only (section is solid)
- Add framing: "presented at baseline σ_u = 50 GPa; §6.2 explores robustness to 30 GPa"
- Fix the taper ratio issue (see blocker)

**§4 Modular System Architecture:**
- Add missing mass-safety trade-off figure (§4.2.4)
- Complete §4.3(c) sentence fragments about coating mass
- Clarify requirements vs. assumptions in §4.4

### Front/Back Matter

**Abstract** (200–250 words): context (1 sent) → gap (1) → method (2) → results (3) → significance (1). Specific numbers only.

**Highlights** (3–5, max 85 chars each):
```
• Modular CNT tether achieves XX.X% 10-year survival with 18 segments
• Variable-length segmentation equalizes mass at ≤4% penalty vs monolithic
• Joint efficiency η ≥ 0.93 required for 99.9% system reliability
• Architecture closes at σ_u = XX GPa, below current lab demonstrations
• Modular repair breaks even vs replacement below $X/kg launch cost
```

**Graphical abstract:** Tether schematic with P_sys heatmap overlay (531 × 1328 px min)

**CRediT statement:**
- K. Egan: Conceptualization, Methodology, Software, Formal Analysis, Writing – Original Draft, Visualization
- M. Ergezer: Supervision, Writing – Review & Editing

**Keywords:** space elevator, carbon nanotubes, modular tether, joint reliability, Monte Carlo simulation, lifecycle cost analysis, orbital infrastructure

---

## Phase 3: Review & Polish (Aug 1 – Sep 15)

- Send to Ergezer Aug 1 — budget 2–3 weeks for feedback
- Incorporate feedback Aug 15–31
- Technical proofread: equations, dimensions, references, figure refs
- Writing quality pass: tighten to 20–25 pages, eliminate hedging in results
- Figure quality: vector PDF, 300 DPI, colorblind-safe (Wong 2011 palette), self-contained captions
- Reference audit: all DOIs verified, no orphans, no retracted papers
- Optional: send to ISEC contacts (Dennis Wright, Peter Swan) for informal feedback

---

## Phase 4: Submission (Sep 15 – Oct 1)

### Submission Package
- Manuscript PDF (LaTeX compiled)
- Separate high-res figure files (PDF/EPS)
- Highlights file
- Graphical abstract (TIFF/EPS)
- Cover letter to Editor-in-Chief Zheng Hong George Zhu
- 3–5 suggested reviewers with justification
- CRediT statement
- Data availability statement
- Declaration of competing interests

### Suggested Reviewers
- S. Luo — segmented tether optimization (we extend their work)
- H. Wright or D. Patel — joint efficiency data (our Monte Carlo parameterizes on their data)
- T. Nishimura — tether dynamics (our modal analysis compares against their model)
- 1–2 from adjacent fields (structural reliability, composite tethers)

### Cover Letter
One page. State: what, why novel (C1–C5 in one sentence each), why Acta Astronautica. Mention NIAC validation. Do not oversell.

---

## Phase 5: Review & Revision (Oct 2026 – Jul 2027)

| Event | Expected Date |
|-------|--------------|
| Editor acknowledges | Oct 2026 |
| Reviewer assignment | Oct–Nov 2026 |
| First decision (R1) | Apr–Jun 2027 |
| Revision submitted | Jun–Jul 2027 |
| Final decision | Aug–Sep 2027 |

**If reject:** pivot to AIAA Journal of Spacecraft and Rockets or JBIS (ISEC publishes there).

---

## Parallel: ISEC Conference 2026

- **Dates:** Sep 12–13, virtual
- **Abstract deadline:** June 1 → send to dennis.wright@isec.org by May 25
- **Talk:** 15–20 minutes
- **Content:** Present Monte Carlo reliability results (Phase 1B)
- **Purpose:** Community feedback before journal reviewers see it; build name recognition

---

## Tool Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | All simulations |
| NumPy/SciPy | Integration, sparse eigensolvers, optimization |
| Matplotlib | Figures (custom .mplstyle for consistency) |
| h5py | Monte Carlo data storage |
| LaTeX (elsarticle.cls) | Manuscript |
| Git/GitHub | Version control |
| SLURM/A100 | Monte Carlo parallelization |

---

## Figure List (Minimum 8–12 for Acta Astronautica)

| # | Figure | Source | Priority |
|---|--------|--------|----------|
| 1 | Taper profile A(y) and T(y) — continuous vs. stepped | Phase 1A | HIGH |
| 2 | NIAC validation overlay | Phase 1A | HIGH |
| 3 | σ_u sensitivity: τ, M_total, N vs. σ_u | Phase 1A | HIGH |
| 4 | **P_sys heatmap over (N, η_j)** | Phase 1B | CRITICAL |
| 5 | System availability vs. inspection cadence | Phase 1B | HIGH |
| 6 | MTTR distribution with 72h target line | Phase 1B | HIGH |
| 7 | Modal frequency spectrum: segmented vs. continuous | Phase 1C | MEDIUM |
| 8 | NPV crossover: modular vs. monolithic over 30 years | Phase 1D | HIGH |
| 9 | Cost sensitivity tornado diagram | Phase 1D | MEDIUM |
| 10 | Mass-safety trade-off: ΔM vs. η_j for N = 12–24 | Phase 2 (§4.2.4 fix) | MEDIUM |
| 11 | Graphical abstract: tether schematic + P_sys overlay | Phase 2 | HIGH |
| 12 | TRL roadmap bar chart | Phase 2 (§9) | LOW |

---

## Risk Register

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| σ_u sensitivity shows architecture fails below 40 GPa | Med | High | Reframe as "feasibility boundary" — still publishable |
| Monte Carlo shows P_sys < 99% at η_j = 0.97 | Low | High | Add redundant load paths (4 sub-ribbons); re-run with redistribution |
| Modal analysis reveals climber-speed resonance | Med | Med | Adjust separation rule; becomes a design constraint |
| Reviewer requests experimental validation | High | Low | Acknowledged as future work from start; cite computational-only precedent |
| Review takes > 12 months | Med | Med | Use wait time for ISEC talk and SciTech abstract |

---

## Success Criteria (All Must Be True Before Submission)

- [ ] Taper ratio discrepancy resolved and documented
- [ ] Static profile matches NIAC baseline within 2% at peak tension
- [ ] P_sys surface computed over full (N, η_j) parameter space
- [ ] At least one σ_u < 40 GPa shows viable (if penalized) architecture
- [ ] NPV crossover point identified with sensitivity
- [ ] All figures publication quality (vector, consistent style, colorblind-safe)
- [ ] Abstract contains 4+ specific quantitative results
- [ ] Every abstract claim backed by a result in §6 or §7
- [ ] Advisor reviewed and approved
- [ ] All LaTeX cross-references resolve
- [ ] BibTeX compiles with zero warnings
- [ ] Paper is 20–25 pages total
