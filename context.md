# Project Context

**Project:** Modular CNT Space-Elevator Tether — Systems Engineering Analysis
**Target Journal:** Acta Astronautica (Elsevier), Q1 Aerospace Engineering
**Lead Author:** Kenneth Egan, Wentworth Institute of Technology
**Advisor:** M. Ergezer
**Submission Target:** October 2026
**Parallel:** ISEC 2026 conference abstract by June 1, 2026

---

## What This Paper Is About

First coupled system-level feasibility assessment of a **modular** CNT space-elevator tether — treating joint reliability, segment geometry, repair logistics, and lifecycle cost as one integrated trade space. No prior work does this.

## Five Core Contributions

1. **C1** — Validated modular tether profile matching Edwards & Westling (2003) NIAC baseline within 2%
2. **C2** — Variable-length mass-equalized segmentation methodology
3. **C3** — Monte Carlo reliability surface P_sys(N, η_j) — first published quantification
4. **C4** — Minimum viable CNT strength for modular architecture (sensitivity down to 30 GPa)
5. **C5** — Lifecycle NPV comparison: repair-in-place vs. full replacement

## Critical Design Rule

**All simulations load from `data/parameters.yaml`.** No hardcoded physical constants in scripts. Any parameter change triggers a full re-run.

## Known Blocker

**Taper ratio discrepancy:** Draft claims τ ≈ 1.6 at σ_allow = 25 GPa, but numerical integration gives τ ≈ 12.4. Must resolve before any other simulation work — likely the draft used σ_u (50 GPa) instead of σ_allow (25 GPa) for the taper calculation.

## Repository Layout

```
├── docs/                        # Research proposal + plan
├── paper/                       # Manuscript, figures, tables
│   ├── sections/                # Individual .tex files
│   ├── figures/                 # Publication-quality PDFs
│   └── tables/
├── simulations/
│   ├── fea/                     # taper_profile.py, modal_analysis.py
│   ├── monte_carlo/             # joint_reliability.py
│   ├── thermal/                 # Thermal environment modeling
│   └── cost_model/              # npv_model.py
├── data/
│   ├── parameters.yaml          # LOCKED master parameters
│   ├── raw/                     # Simulation outputs
│   └── processed/               # Cleaned results for figures
├── scripts/                     # Matplotlib style, utilities
└── references/                  # main.bib
```

## Key References

| Cite Key | Relevance |
|----------|-----------|
| Edwards & Westling (2003) | NIAC baseline we validate against |
| Luo et al. (2022) | Segmented optimization we extend with coupled reliability |
| Wright et al. (2023) | Joint efficiency data (η_j = 0.97) our Monte Carlo uses |
| Peters (2009) | Analytical taper solutions |
| Popescu & Sun (2018) | Bio-inspired repair concept we quantify |
| Nishimura & Hashimoto (2015) | Continuous tether dynamics we compare against |

## Tool Stack

Python 3.11+ (NumPy, SciPy, Matplotlib, pandas, PyYAML, h5py), LaTeX (elsarticle.cls), Git/GitHub
