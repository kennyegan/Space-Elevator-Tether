"""
sensitivity_analysis.py — Hazard rate sensitivity (Part B).

One-at-a-time perturbation (±20%, ±40%) of 8 parameters controlling the
full-scale mission-averaged hazard rate λ_full. Produces:
  - Tornado diagram   (fig_hazard_tornado.pdf)
  - Spider plot        (fig_hazard_spider.pdf)
  - Appends notes to   results/figure_notes.md

Usage:
    cd ~/Space-Elevator-Tether
    python -m simulations.monte_carlo.phase1_weibull.sensitivity_analysis
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulations.monte_carlo.phase1_weibull.config import (
    FIGURES_DIR,
    RESULTS_DIR,
    STYLE_FILE,
)
from simulations.monte_carlo.phase1_weibull.hazard_model import (
    compute_joint_positions,
    load_params,
    thermal_profile_3zone,
)


def _apply_style():
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))


# ===================================================================
# Hazard rate model for perturbation analysis
# ===================================================================
def compute_lambda_full(
    Q_eV: float = 1.1,
    m_weibull: float = 6.0,
    tau_frac: float = 0.42,
    T1: float = 250.0,
    T2: float = 280.0,
    T3: float = 300.0,
    lambda_coupon: float = 1.2e-8,
    V_ratio: float = 6000.0,
    eta_j: float = 0.95,
    N_baseline: int = 18,
    params: dict = None,
    lambda_0_pre_fixed: float = None,
) -> float:
    """
    Compute the full-scale mission-averaged hazard rate.

    When lambda_0_pre_fixed is provided, it is used directly (no re-calibration).
    This is the correct mode for Q and T sensitivity: the pre-exponential is
    calibrated ONCE at baseline, then Q/T perturbations propagate through the
    Arrhenius factors without the calibration absorbing them.

    When lambda_0_pre_fixed is None, the pre-exponential is re-derived from
    λ_coupon and volume scaling (appropriate for m, V_ratio, λ_coupon sweeps).
    """
    k_B_eV = 8.617e-5  # eV/K

    # Volume scaling
    volume_scale = V_ratio ** (1.0 / m_weibull)
    lambda_fullscale = lambda_coupon * volume_scale

    # Joint positions and temperatures
    L_total = float(params["tether"]["L_total"]) if params is not None else 1.0e8
    n_joints = N_baseline - 1
    alts = np.linspace(L_total / N_baseline, L_total * (N_baseline - 1) / N_baseline,
                       n_joints)

    # 3-zone model with (possibly perturbed) temperatures
    temps = np.full(n_joints, T2)
    temps[alts < 200e3] = T1
    temps[alts > 35.786e6] = T3

    # Arrhenius factors
    arrhenius = np.exp(-Q_eV / (k_B_eV * temps))
    mean_arrhenius = np.mean(arrhenius)

    if lambda_0_pre_fixed is not None:
        # Fixed pre-exponential (for Q/T sensitivity)
        lambda_0_pre = lambda_0_pre_fixed
    else:
        # Re-derive from volume-scaled coupon rate (for m/V/λ_coupon sensitivity)
        lambda_0_pre = lambda_fullscale / mean_arrhenius

    # Per-joint rates with efficiency correction
    efficiency_factor = (0.97 / eta_j) ** 4
    per_joint = lambda_0_pre * arrhenius * efficiency_factor

    return float(np.mean(per_joint))


# ===================================================================
# Perturbation sweep
# ===================================================================

# Parameter definitions: (name, display_name, baseline_value, unit)
SENSITIVITY_PARAMS = [
    ("Q_eV",          "$Q$ (activation energy)",     1.1,     "eV"),
    ("m_weibull",     "$m$ (Weibull modulus)",        6.0,     "—"),
    ("T1",            "$T_1$ (Zone 1)",              250.0,   "K"),
    ("T2",            "$T_2$ (Zone 2)",              280.0,   "K"),
    ("T3",            "$T_3$ (Zone 3)",              300.0,   "K"),
    ("lambda_coupon", r"$\lambda_{\mathrm{coupon}}$", 1.2e-8, "1/h"),
    ("V_ratio",       "$V_{sleeve}/V_{coupon}$",     6000.0,  "—"),
]
# Note: τ_allow/σ_allow is excluded — it affects structural capacity
# but does not enter the hazard rate model.

PERTURBATIONS = [-0.4, -0.2, 0.0, 0.2, 0.4]


def run_sensitivity(params=None):
    """Run one-at-a-time perturbation sweep. Returns dict of results."""
    baselines = {p[0]: p[2] for p in SENSITIVITY_PARAMS}
    lambda_baseline = compute_lambda_full(**baselines, params=params)

    # Calibrate λ_0_pre at baseline Q and T, then hold it fixed when
    # perturbing Q or T so the Arrhenius sensitivity is not absorbed
    # by re-calibration.
    k_B_eV = 8.617e-5
    L_total = float(params["tether"]["L_total"]) if params is not None else 1.0e8
    N_base = 18
    n_joints = N_base - 1
    alts = np.linspace(L_total / N_base, L_total * (N_base - 1) / N_base, n_joints)
    temps_base = np.full(n_joints, baselines["T2"])
    temps_base[alts < 200e3] = baselines["T1"]
    temps_base[alts > 35.786e6] = baselines["T3"]
    arr_base = np.exp(-baselines["Q_eV"] / (k_B_eV * temps_base))
    vsf_base = baselines["V_ratio"] ** (1.0 / baselines["m_weibull"])
    lfs_base = baselines["lambda_coupon"] * vsf_base
    lambda_0_pre_baseline = lfs_base / np.mean(arr_base)

    # Parameters whose perturbation should use fixed λ_0_pre
    # (Q and temperatures — otherwise calibration absorbs the change)
    fixed_pre_params = {"Q_eV", "T1", "T2", "T3"}

    results = {}
    for key, display, baseline, unit in SENSITIVITY_PARAMS:
        ratios = []
        lambdas = []
        for delta in PERTURBATIONS:
            perturbed = dict(baselines)
            perturbed[key] = baseline * (1.0 + delta)
            if key in fixed_pre_params:
                lam = compute_lambda_full(**perturbed, params=params,
                                          lambda_0_pre_fixed=lambda_0_pre_baseline)
            else:
                lam = compute_lambda_full(**perturbed, params=params)
            ratios.append(lam / lambda_baseline)
            lambdas.append(lam)
        results[key] = {
            "display": display,
            "baseline": baseline,
            "unit": unit,
            "perturbations": PERTURBATIONS,
            "ratios": ratios,
            "lambdas": lambdas,
        }

    results["_baseline_lambda"] = lambda_baseline
    return results


# ===================================================================
# Figure 6: Tornado diagram
# ===================================================================
def plot_tornado(results, notes):
    _apply_style()

    sensitivities = []
    for key, display, baseline, unit in SENSITIVITY_PARAMS:
        r = results[key]
        ratios = r["ratios"]
        # Use log10 of ratio for the tornado (Arrhenius is exponentially
        # sensitive, so linear scale is meaningless)
        lo_log = np.log10(max(ratios[0], 1e-10))   # -40%
        hi_log = np.log10(max(ratios[-1], 1e-10))  # +40%
        span = abs(hi_log - lo_log)
        sensitivities.append({
            "name": r["display"],
            "lo": lo_log,
            "hi": hi_log,
            "span": span,
        })

    sensitivities.sort(key=lambda s: s["span"], reverse=True)

    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    y_pos = np.arange(len(sensitivities))

    for i, s in enumerate(sensitivities):
        left = min(s["lo"], s["hi"])
        width = abs(s["hi"] - s["lo"])
        ax.barh(i, width, left=left, height=0.5,
                color="#56B4E9", edgecolor="white", linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([s["name"] for s in sensitivities], fontsize=7)
    ax.axvline(0.0, color="black", linewidth=0.6)
    ax.set_xlabel(
        r"$\log_{10}(\lambda_{\mathrm{full}} / \lambda_{\mathrm{full,baseline}})$")
    ax.set_title("Hazard rate sensitivity (±40%)")
    ax.invert_yaxis()

    plt.tight_layout()
    out = FIGURES_DIR / "fig_hazard_tornado.pdf"
    fig.savefig(out)
    print(f"  Saved: {out}")
    plt.close(fig)

    notes.append(
        "## Figure 6: Hazard Rate Tornado\n\n"
        "Tornado diagram (log scale) showing the sensitivity of the full-scale "
        "mission-averaged hazard rate to ±40% perturbation of each input "
        "parameter. The activation energy Q dominates overwhelmingly, reflecting "
        "the exponential Arrhenius dependence — a 40% reduction in Q increases "
        "the hazard rate by ~7 orders of magnitude. Zone 3 temperature (T₃, "
        "where the majority of joints reside) ranks second, also via the "
        "exponential. The Weibull modulus m, volume ratio, and coupon rate "
        "contribute at most ~0.4 decades. This underscores that the single "
        "most critical parameter for the reliability prediction is the "
        "activation energy assumed for CNT joint degradation.\n"
    )


# ===================================================================
# Figure 7: Spider plot
# ===================================================================
def plot_spider(results, notes):
    _apply_style()

    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    colors = ["#000000", "#E69F00", "#56B4E9", "#009E73",
              "#D55E00", "#CC79A7", "#0072B2"]
    pct = [d * 100 for d in PERTURBATIONS]

    for idx, (key, display, baseline, unit) in enumerate(SENSITIVITY_PARAMS):
        r = results[key]
        # Clip ratios to avoid log(0)
        ratios_clipped = [max(v, 1e-10) for v in r["ratios"]]
        ax.plot(pct, ratios_clipped, "o-", color=colors[idx % len(colors)],
                markersize=3, linewidth=1.0, label=r["display"])

    ax.set_xlabel("Parameter perturbation [%]")
    ax.set_ylabel(
        r"$\lambda_{\mathrm{full}} / \lambda_{\mathrm{full,baseline}}$")
    ax.set_yscale("log")
    ax.set_title("Hazard rate spider plot")
    ax.axhline(1.0, color="gray", linestyle=":", linewidth=0.5)
    ax.legend(fontsize=5, loc="upper left", ncol=2)

    plt.tight_layout()
    out = FIGURES_DIR / "fig_hazard_spider.pdf"
    fig.savefig(out)
    print(f"  Saved: {out}")
    plt.close(fig)

    notes.append(
        "## Figure 7: Hazard Rate Spider Plot\n\n"
        "Spider plot (log scale) showing λ_full/λ_baseline as a function of "
        "perturbation percentage. Q exhibits extreme nonlinearity — its curve "
        "spans ~7 orders of magnitude, confirming that the Arrhenius activation "
        "energy is the dominant source of uncertainty. Underestimating Q (lower "
        "activation barrier) is catastrophic for reliability; overestimating it "
        "is conservative. T₃ shows similar exponential sensitivity. The "
        "remaining parameters (m, V_ratio, λ_coupon) contribute at most "
        "half a decade, entering as power-law or linear factors. This plot "
        "makes the case that experimental determination of Q for CNT "
        "nanobonded joints is the single highest-priority measurement for "
        "reducing uncertainty in the reliability prediction.\n"
    )


# ===================================================================
# Main
# ===================================================================
def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("HAZARD RATE SENSITIVITY ANALYSIS (Part B)")
    print("=" * 60)

    params = load_params()
    results = run_sensitivity(params=params)

    lambda_base = results["_baseline_lambda"]
    print(f"\n  Baseline λ_full = {lambda_base:.4e} 1/h")
    print(f"\n  {'Parameter':<30s} {'−40%':>10s} {'−20%':>10s} "
          f"{'base':>10s} {'+20%':>10s} {'+40%':>10s}")
    print(f"  {'-'*80}")
    for key, display, baseline, unit in SENSITIVITY_PARAMS:
        r = results[key]
        vals = "".join(f"{v:10.4f}" for v in r["ratios"])
        print(f"  {display:<30s}{vals}")

    notes = []
    plot_tornado(results, notes)
    plot_spider(results, notes)

    # Append to figure_notes.md
    notes_path = RESULTS_DIR / "figure_notes.md"
    mode = "a" if notes_path.exists() else "w"
    with open(notes_path, mode) as f:
        if mode == "w":
            f.write("# Weibull Extension — Figure Interpretation Notes\n\n")
        for note in notes:
            f.write(note + "\n")
    print(f"\n  Notes appended to: {notes_path}")
    print("Done.")


if __name__ == "__main__":
    main()
