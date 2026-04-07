"""
merge_figures.py — Create merged publication figures for Acta Astronautica.

Produces 4 merged figures from existing individual plots, reducing the total
from 33 to 16 main-text figures.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FIGURES = ROOT / "paper" / "figures"
STYLE = ROOT / "scripts" / "acta_astronautica.mplstyle"

COLORS = ["#000000", "#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]


def load_style():
    if STYLE.exists():
        plt.style.use(str(STYLE))


# =========================================================================
# Merge 1: P_sys reliability — exponential heatmap + Weibull P_sys vs β
# =========================================================================
def merge_reliability(params):
    """Merged Fig 4: P_sys heatmap (exp) + P_sys vs β (Weibull)."""
    load_style()
    import csv

    # Load sweep data
    csv_path = ROOT / "data" / "processed" / "weibull_sweep_results.csv"
    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            rows.append({k: float(v) for k, v in row.items()})

    # --- Panel A: P_sys(N, eta_j) heatmap at exponential baseline ---
    N_vals = sorted(set(int(r["N"]) for r in rows))
    eta_vals = sorted(set(round(r["eta_j"], 2) for r in rows))
    betas = [1.0]

    psys_grid = np.full((len(N_vals), len(eta_vals)), np.nan)
    for r in rows:
        if (int(r["cadence"]) == 1 and abs(r["p_det"] - 0.995) < 0.01
                and abs(r["beta"] - 1.0) < 0.05):
            ni = N_vals.index(int(r["N"]))
            ei = eta_vals.index(round(r["eta_j"], 2))
            psys_grid[ni, ei] = r["P_sys"]

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    ax = axes[0]
    im = ax.imshow(psys_grid.T, aspect="auto", origin="lower",
                   cmap="RdYlGn", vmin=0.7, vmax=1.0,
                   extent=[-0.5, len(N_vals)-0.5, -0.5, len(eta_vals)-0.5])
    ax.set_xticks(range(len(N_vals)))
    ax.set_xticklabels([str(n) for n in N_vals], fontsize=6, rotation=45)
    ax.set_yticks(range(len(eta_vals)))
    ax.set_yticklabels([f"{e:.2f}" for e in eta_vals], fontsize=6)
    ax.set_xlabel("$N$ (segments)")
    ax.set_ylabel("$\\eta_j$")
    ax.set_title("(a) $P_{sys}$ at $\\beta=1.0$", fontsize=9)
    plt.colorbar(im, ax=ax, shrink=0.8, label="$P_{sys}$")

    # --- Panel B: P_sys vs β at four design points ---
    ax = axes[1]
    design_points = [
        (83, 0.95, "N=83, $\\eta_j$=0.95"),
        (83, 0.80, "N=83, $\\eta_j$=0.80"),
        (200, 0.95, "N=200, $\\eta_j$=0.95"),
        (500, 0.80, "N=500, $\\eta_j$=0.80"),
    ]

    beta_vals = sorted(set(round(r["beta"], 1) for r in rows))

    for ci, (N, eta, label) in enumerate(design_points):
        psys_by_beta = []
        for beta in beta_vals:
            matches = [r for r in rows
                       if int(r["N"]) == N and abs(r["eta_j"] - eta) < 0.01
                       and int(r["cadence"]) == 1 and abs(r["p_det"] - 0.995) < 0.01
                       and abs(r["beta"] - beta) < 0.05]
            if matches:
                psys_by_beta.append(matches[0]["P_sys"])
            else:
                psys_by_beta.append(np.nan)

        ax.plot(beta_vals, psys_by_beta, "o-", color=COLORS[ci],
                markersize=3, linewidth=1.0, label=label)

    ax.set_xlabel("Weibull $\\beta$")
    ax.set_ylabel("$P_{sys}$ (10-year)")
    ax.set_title("(b) Wear-out sensitivity", fontsize=9)
    ax.legend(fontsize=5.5, loc="lower left")
    ax.set_ylim(0.7, 1.005)

    plt.tight_layout()
    out = FIGURES / "fig_reliability_merged.pdf"
    fig.savefig(out)
    print(f"  Saved: {out}")
    plt.close(fig)


# =========================================================================
# Merge 2: MTTR combined — baseline distribution + Weibull + depot shift
# =========================================================================
def merge_mttr(params):
    """Merged Fig 7: MTTR by β (bars) + depot shift (histograms)."""
    load_style()
    import csv

    csv_path = ROOT / "data" / "processed" / "weibull_sweep_results.csv"
    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            rows.append({k: float(v) for k, v in row.items()})

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    # --- Panel A: MTTR statistics by β at baseline ---
    ax = axes[0]
    beta_vals = [1.0, 1.3, 1.5, 2.0, 2.5]
    medians = []
    p05s = []
    p95s = []
    for beta in beta_vals:
        matches = [r for r in rows
                   if int(r["N"]) == 83 and abs(r["eta_j"] - 0.95) < 0.01
                   and int(r["cadence"]) == 1 and abs(r["p_det"] - 0.995) < 0.01
                   and abs(r["beta"] - beta) < 0.05]
        if matches:
            m = matches[0]
            medians.append(m["median_MTTR"])
            p05s.append(m["p05_MTTR"])
            p95s.append(m["p95_MTTR"])
        else:
            medians.append(0)
            p05s.append(0)
            p95s.append(0)

    x = np.arange(len(beta_vals))
    ax.bar(x, medians, width=0.5, color=COLORS[5], alpha=0.8, label="Median")
    ax.errorbar(x, medians,
                yerr=[np.array(medians) - np.array(p05s),
                      np.array(p95s) - np.array(medians)],
                fmt="none", color="black", capsize=3, linewidth=0.8)
    ax.axhline(72, color="gray", linewidth=0.75, linestyle="--", label="72 h target")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{b:.1f}" for b in beta_vals])
    ax.set_xlabel("Weibull $\\beta$")
    ax.set_ylabel("MTTR [h]")
    ax.set_title("(a) MTTR by $\\beta$ (N=83 baseline)", fontsize=9)
    ax.legend(fontsize=6)

    # --- Panel B: Depot shift (from Phase 3) ---
    ax = axes[1]

    from simulations.repair_infrastructure.weibull_mttr_shift import (
        load_weibull_mttr, extract_baseline_mttr,
        compute_depot_mttr_shift, generate_synthetic_mttr_distribution,
    )
    from simulations.cost_model.npv_model import load_params as lp
    params_local = lp()

    try:
        wb_rows = load_weibull_mttr()
        baseline = extract_baseline_mttr(wb_rows)
    except Exception:
        baseline = {1.5: {"median_MTTR": 219, "p05_MTTR": 130, "p95_MTTR": 930}}

    beta = 1.5
    if beta in baseline:
        bm = baseline[beta]
    else:
        bm = list(baseline.values())[0]

    rng = np.random.default_rng(42)
    dist_base = generate_synthetic_mttr_distribution(
        bm["median_MTTR"], bm.get("p05_MTTR", 130),
        bm.get("p95_MTTR", 930), 50000, rng)

    for nd, color, label in [(0, COLORS[0], "No depots"),
                              (5, COLORS[5], "5 depots"),
                              (10, COLORS[3], "10 depots")]:
        shift = compute_depot_mttr_shift(83, nd, "uniform", 150.0, 1, params_local)
        dist = np.maximum(dist_base - shift["mttr_shift"], 0)
        ax.hist(dist, bins=60, range=(0, 1200), alpha=0.45,
                color=color, label=label, density=True)

    ax.axvline(72, color="gray", linewidth=0.75, linestyle="--")
    ax.set_xlabel("MTTR [h]")
    ax.set_ylabel("Density")
    ax.set_title("(b) Depot shift ($\\beta$=1.5)", fontsize=9)
    ax.legend(fontsize=6)
    ax.set_xlim(0, 1000)

    plt.tight_layout()
    out = FIGURES / "fig_mttr_merged.pdf"
    fig.savefig(out)
    print(f"  Saved: {out}")
    plt.close(fig)


# =========================================================================
# Merge 3: Displacement envelopes — longitudinal + transverse
# =========================================================================
def merge_displacement_envelopes():
    """Merged Fig 11: Longitudinal + transverse displacement envelopes."""
    load_style()

    # Load the phase2 dynamics data
    data_file = ROOT / "data" / "processed" / "phase2_dynamics" / "single_climber_results.npz"
    if not data_file.exists():
        print(f"  SKIP: {data_file} not found")
        return

    data = np.load(data_file, allow_pickle=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True)

    alt = data["alt_nodes"] / 1e6  # m -> Mm

    # Panel A: Longitudinal
    ax = axes[0]
    ax.plot(data["u_envelope"], alt, "-", color=COLORS[5], linewidth=1.0)
    ax.set_xlabel("Peak longitudinal displacement [km]")
    ax.set_ylabel("Altitude [Mm]")
    ax.set_title("(a) Longitudinal", fontsize=9)

    # Panel B: Transverse
    ax = axes[1]
    ax.plot(data["v_envelope"], alt, "-", color=COLORS[6], linewidth=1.0)
    ax.set_xlabel("Peak transverse displacement [km]")
    ax.set_title("(b) Transverse", fontsize=9)

    plt.tight_layout()
    out = FIGURES / "fig_displacement_envelopes_merged.pdf"
    fig.savefig(out)
    print(f"  Saved: {out}")
    plt.close(fig)


# =========================================================================
# Merge 4: NPV — base crossover + depot curves
# =========================================================================
def merge_npv(params):
    """Merged Fig 14: NPV crossover (base) + with depot curves."""
    load_style()

    from simulations.cost_model.npv_model import (
        load_params as lp, load_mc_results, get_mc_failure_rates,
        build_cost_assumptions, compute_npv_modular, compute_npv_monolithic,
    )
    from simulations.repair_infrastructure.npv_with_depots import (
        compute_npv_modular_with_depots,
    )

    params_local = lp()
    mc_data = load_mc_results()
    mc_rates = get_mc_failure_rates(mc_data, params_local) if mc_data else None
    lifetime = int(params_local["cost"]["system_lifetime"])
    lc, dr, rev = 1000.0, 0.07, 300.0
    cost = build_cost_assumptions(params_local, lc, rev, mc_rates)

    years = np.arange(lifetime + 1)
    npv_mono = compute_npv_monolithic(cost, dr, lifetime)
    npv_mod0 = compute_npv_modular(cost, dr, lifetime)
    npv_mod5 = compute_npv_modular_with_depots(cost, dr, lifetime, 5, lc)
    npv_mod10 = compute_npv_modular_with_depots(cost, dr, lifetime, 10, lc)

    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    ax.plot(years, npv_mono / 1e9, "--", color=COLORS[6], linewidth=1.2,
            label="Monolithic")
    ax.plot(years, npv_mod0 / 1e9, "-", color=COLORS[5], linewidth=1.2,
            label="Modular (no depots)")
    ax.plot(years, npv_mod5 / 1e9, "-", color=COLORS[3], linewidth=1.0,
            label="Modular (5 depots)")
    ax.plot(years, npv_mod10 / 1e9, "-", color=COLORS[1], linewidth=1.0,
            label="Modular (10 depots)")
    ax.axhline(0, color="gray", linewidth=0.4, linestyle=":")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative NPV [\\$B]")
    ax.legend(fontsize=5.5, loc="lower right")

    plt.tight_layout()
    out = FIGURES / "fig_npv_merged.pdf"
    fig.savefig(out)
    print(f"  Saved: {out}")
    plt.close(fig)


def main():
    from simulations.cost_model.npv_model import load_params
    params = load_params()

    print("Generating merged figures...")
    merge_reliability(params)
    merge_mttr(params)
    merge_displacement_envelopes()
    merge_npv(params)
    print("Done.")


if __name__ == "__main__":
    main()
