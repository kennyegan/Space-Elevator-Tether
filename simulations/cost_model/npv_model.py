"""
npv_model.py — Lifecycle NPV comparison: modular vs. monolithic tether

Computes 30-year Net Present Value for two architectures:
  Modular:    NPV = -C_build(t) + Σ (Revenue(t) - C_ops - C_repair) / (1+r)^t
              Revenue ramps during phased construction.
  Monolithic: NPV = -C_build + Σ (Revenue_t - C_ops - P_fail·C_replace) / (1+r)^t
              Zero revenue until full tether is complete.

Failure rates and repair frequencies are loaded from Monte Carlo results
when available, falling back to analytical estimates otherwise.

Usage:
    python simulations/cost_model/npv_model.py

Outputs:
    data/processed/npv_results.npz
    paper/figures/fig_npv_crossover.pdf
    paper/figures/fig_cost_tornado.pdf
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
PARAMS_FILE = ROOT / "data" / "parameters.yaml"
OUTPUT_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "paper" / "figures"
STYLE_FILE = ROOT / "scripts" / "acta_astronautica.mplstyle"
MC_FILE = ROOT / "data" / "processed" / "psys_surface.npz"
TAPER_FILE = ROOT / "data" / "processed" / "sigma_u_sensitivity.json"


def load_params(path: Path = PARAMS_FILE) -> dict:
    """Load the locked master parameter file, casting all numerics to float."""
    with open(path) as f:
        raw = yaml.safe_load(f)

    def try_float(v):
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v
        return v

    def cast(d):
        out = {}
        for k, v in d.items():
            if isinstance(v, dict):
                out[k] = cast(v)
            elif isinstance(v, list):
                out[k] = [try_float(x) for x in v]
            else:
                out[k] = try_float(v)
        return out

    return cast(raw)


# ---------------------------------------------------------------------------
# Load Monte Carlo results (if available)
# ---------------------------------------------------------------------------
def load_mc_results():
    """
    Load Monte Carlo P_sys data. Returns dict or None if not available.
    """
    if not MC_FILE.exists():
        return None
    try:
        data = np.load(MC_FILE, allow_pickle=True)
        return {k: data[k] for k in data.files}
    except Exception:
        return None


def load_taper_sensitivity():
    """Load taper sensitivity results for consistent mass estimates."""
    taper_file = OUTPUT_DIR / "sigma_u_sensitivity.json"
    if not taper_file.exists():
        return None
    with open(taper_file) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Failure rate extraction from Monte Carlo
# ---------------------------------------------------------------------------
def get_mc_failure_rates(mc_data: dict, params: dict) -> dict:
    """
    Extract annualized failure rate and repair frequency from MC data.

    Returns dict with:
        P_fail_annual_modular : float (annualized from 10-year P_sys at baseline)
        P_fail_annual_mono    : float (from worst-case cadence, no repair effectively)
        repairs_per_year      : float (estimated from failure rate and detection)
    """
    if mc_data is None:
        return None

    P_sys = mc_data["P_sys"]
    N_vals = mc_data["N_values"]
    eta_vals = mc_data["eta_j_values"]
    cadence_vals = mc_data["cadence_values"]

    # Find baseline indices
    N_vals_list = list(N_vals)
    eta_vals_list = list(eta_vals)

    try:
        n_idx = N_vals_list.index(18)
    except ValueError:
        n_idx = len(N_vals_list) // 2

    try:
        e_idx = eta_vals_list.index(0.95)
    except ValueError:
        e_idx = len(eta_vals_list) // 2

    # Handle 3D or 4D P_sys array
    if P_sys.ndim == 4:
        # (N, eta, cadence, p_det) — use baseline p_det (last index)
        P_sys_10yr_modular = float(P_sys[n_idx, e_idx, 0, -1])  # cadence=1, best p_det
        P_sys_10yr_mono = float(P_sys[n_idx, e_idx, -1, 0])  # worst cadence, worst p_det
    elif P_sys.ndim == 3:
        P_sys_10yr_modular = float(P_sys[n_idx, e_idx, 0])  # cadence=1
        P_sys_10yr_mono = float(P_sys[n_idx, e_idx, -1])  # worst cadence
    else:
        return None

    # Annualize: P_fail_annual = 1 - P_sys^(1/10)
    P_fail_annual_mod = 1.0 - P_sys_10yr_modular ** 0.1 if P_sys_10yr_modular < 1.0 else 0.0
    P_fail_annual_mono = 1.0 - P_sys_10yr_mono ** 0.1 if P_sys_10yr_mono < 1.0 else 0.001

    # Ensure monolithic has meaningful failure rate
    P_fail_annual_mono = max(P_fail_annual_mono, 0.01)

    # Repair frequency: from the hazard rate model
    # At baseline: lambda_fullscale × n_joints × hours_per_year
    lambda_0 = float(params["joints"]["lambda_0"])
    n_joints = 17  # N=18 segments → 17 joints
    hours_per_year = 8760.0
    repairs_per_year = lambda_0 * n_joints * hours_per_year

    return {
        "P_fail_annual_modular": P_fail_annual_mod,
        "P_fail_annual_mono": P_fail_annual_mono,
        "repairs_per_year": repairs_per_year,
        "P_sys_10yr_modular": P_sys_10yr_modular,
        "P_sys_10yr_mono": P_sys_10yr_mono,
    }


# ---------------------------------------------------------------------------
# Cost model
# ---------------------------------------------------------------------------
def build_cost_assumptions(params: dict, launch_cost_per_kg: float,
                           payload_revenue_per_kg: float,
                           mc_rates: dict = None) -> dict:
    """
    Derive cost model inputs from physical parameters and cost rates.
    """
    N = int(params["segments"]["N_baseline"])
    m_star = float(params["segments"]["m_star"])
    m_sleeve = float(params["segments"]["m_sleeve"])
    m_climber = float(params["climber"]["m_climber"])

    # Total tether mass
    M_tether = N * m_star + (N - 1) * m_sleeve

    # Construction: tether + climber fleet (4 climbers)
    n_climbers = 4
    M_total_launch = M_tether + n_climbers * m_climber
    C_build = M_total_launch * launch_cost_per_kg

    # Annual ops: 2% of build cost
    C_ops_annual = 0.02 * C_build

    # Revenue
    trips_per_year = 50
    payload_per_trip = m_climber
    annual_payload = trips_per_year * payload_per_trip
    Revenue_annual_max = annual_payload * payload_revenue_per_kg

    # Repair cost per event
    C_repair_event = (m_star + m_sleeve) * launch_cost_per_kg

    # Failure and repair rates
    if mc_rates is not None:
        repairs_per_year = mc_rates["repairs_per_year"]
        P_fail_annual_mono = mc_rates["P_fail_annual_mono"]
    else:
        # Analytical fallback
        lambda_0 = float(params["joints"]["lambda_0"])
        n_joints = N - 1
        repairs_per_year = lambda_0 * n_joints * 8760.0
        P_fail_annual_mono = 0.05  # conservative

    # Monolithic rebuild cost
    C_replace_full = M_total_launch * launch_cost_per_kg

    # Construction phasing
    construction_cadence = float(params["cost"]["construction_cadence"])
    years_to_build = N / construction_cadence  # time to deploy all segments

    return {
        "C_build": C_build,
        "C_ops_annual": C_ops_annual,
        "Revenue_annual_max": Revenue_annual_max,
        "C_repair_event": C_repair_event,
        "repairs_per_year": repairs_per_year,
        "C_replace_full": C_replace_full,
        "P_fail_annual_mono": P_fail_annual_mono,
        "M_tether": M_tether,
        "annual_payload": annual_payload,
        "N": N,
        "years_to_build": years_to_build,
        "construction_cadence": construction_cadence,
    }


# ---------------------------------------------------------------------------
# NPV calculations
# ---------------------------------------------------------------------------
def compute_npv_modular(cost: dict, discount_rate: float,
                        lifetime: int) -> np.ndarray:
    """
    Compute cumulative NPV for modular architecture with phased construction.

    Key innovation: modular tether generates revenue incrementally as segments
    are deployed. Revenue ramps linearly from 0 to full over construction period.
    """
    npv = np.zeros(lifetime + 1)
    N = cost["N"]
    years_to_build = cost["years_to_build"]
    C_build_total = cost["C_build"]
    C_repair_annual = cost["repairs_per_year"] * cost["C_repair_event"]

    for y in range(1, lifetime + 1):
        # Construction spending: spread evenly over build period
        if y <= years_to_build:
            C_construction = C_build_total / years_to_build
        else:
            C_construction = 0.0

        # Revenue ramp: proportional to segments deployed
        # Minimum viable tether needs ~60% of segments for first climber path
        segments_deployed = min(N, y * cost["construction_cadence"])
        operational_fraction = max(0.0, (segments_deployed / N - 0.6) / 0.4)
        operational_fraction = min(1.0, operational_fraction)
        Revenue = cost["Revenue_annual_max"] * operational_fraction

        # Ops + repair only when operational
        C_ops = cost["C_ops_annual"] * operational_fraction
        C_repair = C_repair_annual * operational_fraction

        annual_cf = Revenue - C_construction - C_ops - C_repair
        npv[y] = npv[y - 1] + annual_cf / (1 + discount_rate) ** y

    return npv


def compute_npv_monolithic(cost: dict, discount_rate: float,
                           lifetime: int) -> np.ndarray:
    """
    Compute cumulative NPV for monolithic architecture.

    Monolithic: zero revenue until full tether is complete (same build time),
    then full revenue but with annual catastrophic failure risk.
    """
    npv = np.zeros(lifetime + 1)
    years_to_build = cost["years_to_build"]
    C_build_total = cost["C_build"]

    for y in range(1, lifetime + 1):
        if y <= years_to_build:
            # Construction phase — spending, no revenue
            C_construction = C_build_total / years_to_build
            annual_cf = -C_construction
        else:
            # Operational phase
            Revenue = cost["Revenue_annual_max"]
            C_ops = cost["C_ops_annual"]
            expected_replace = cost["P_fail_annual_mono"] * cost["C_replace_full"]
            annual_cf = Revenue - C_ops - expected_replace

        npv[y] = npv[y - 1] + annual_cf / (1 + discount_rate) ** y

    return npv


def find_crossover_year(npv_mod: np.ndarray, npv_mono: np.ndarray) -> int:
    """Find first year where modular NPV exceeds monolithic, or -1."""
    diff = npv_mod - npv_mono
    crossings = np.where(diff[1:] > 0)[0]
    return int(crossings[0] + 1) if len(crossings) > 0 else -1


# ---------------------------------------------------------------------------
# Parameter sweep
# ---------------------------------------------------------------------------
def run_sweep(params: dict, mc_rates: dict = None) -> dict:
    """Sweep launch cost × discount rate × payload revenue."""
    launch_costs = [float(x) for x in params["cost"]["launch_cost_sweep"]]
    discount_rates = [float(x) for x in params["cost"]["discount_rate_sweep"]]
    revenues = [float(x) for x in params["cost"]["payload_revenue_sweep"]]
    lifetime = int(params["cost"]["system_lifetime"])

    shape = (len(launch_costs), len(discount_rates), len(revenues))
    npv_mod_final = np.zeros(shape)
    npv_mono_final = np.zeros(shape)
    crossover_year = np.full(shape, -1, dtype=int)

    baseline_curves = None

    for i, lc in enumerate(launch_costs):
        for j, dr in enumerate(discount_rates):
            for k, rev in enumerate(revenues):
                cost = build_cost_assumptions(params, lc, rev, mc_rates)
                npv_m = compute_npv_modular(cost, dr, lifetime)
                npv_o = compute_npv_monolithic(cost, dr, lifetime)

                npv_mod_final[i, j, k] = npv_m[-1]
                npv_mono_final[i, j, k] = npv_o[-1]
                crossover_year[i, j, k] = find_crossover_year(npv_m, npv_o)

                # Store baseline (middle values)
                if (lc == launch_costs[len(launch_costs) // 2] and
                        dr == discount_rates[len(discount_rates) // 2] and
                        rev == revenues[len(revenues) // 2]):
                    baseline_curves = {
                        "years": np.arange(lifetime + 1),
                        "npv_modular": npv_m,
                        "npv_monolithic": npv_o,
                        "cost_assumptions": cost,
                    }

    if baseline_curves is None:
        lc_mid = launch_costs[len(launch_costs) // 2]
        dr_mid = discount_rates[len(discount_rates) // 2]
        rev_mid = revenues[len(revenues) // 2]
        cost = build_cost_assumptions(params, lc_mid, rev_mid, mc_rates)
        npv_m = compute_npv_modular(cost, dr_mid, lifetime)
        npv_o = compute_npv_monolithic(cost, dr_mid, lifetime)
        baseline_curves = {
            "years": np.arange(lifetime + 1),
            "npv_modular": npv_m,
            "npv_monolithic": npv_o,
            "cost_assumptions": cost,
        }

    return {
        "launch_costs": launch_costs,
        "discount_rates": discount_rates,
        "revenues": revenues,
        "lifetime": lifetime,
        "npv_mod_final": npv_mod_final,
        "npv_mono_final": npv_mono_final,
        "crossover_year": crossover_year,
        "baseline_curves": baseline_curves,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_npv_crossover(sweep: dict, output_path: Path = None):
    """NPV over time + crossover sensitivity."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    fig, axes = plt.subplots(1, 2, figsize=(7.48, 3.5))

    bc = sweep["baseline_curves"]
    years = bc["years"]
    ca = bc["cost_assumptions"]

    # Left: NPV time series
    ax = axes[0]
    ax.plot(years, bc["npv_modular"] / 1e9, "-", color="#0072B2",
            linewidth=1.2, label="Modular (phased)")
    ax.plot(years, bc["npv_monolithic"] / 1e9, "--", color="#D55E00",
            linewidth=1.2, label="Monolithic")
    ax.axhline(0, color="gray", linewidth=0.4, linestyle=":")

    # Shade construction period
    ytb = ca["years_to_build"]
    ax.axvspan(0, ytb, alpha=0.08, color="blue", label=f"Build ({ytb:.1f} yr)")

    # Revenue start for modular (at 60% completion)
    rev_start = ytb * 0.6
    ax.axvline(rev_start, color="#009E73", linewidth=0.6, linestyle="--", alpha=0.7)
    ax.annotate("Modular\nrevenue\nstarts", xy=(rev_start, 0), fontsize=6,
                xytext=(rev_start + 1, ax.get_ylim()[0] * 0.3 if ax.get_ylim()[0] < 0 else 0),
                color="#009E73")

    cx = find_crossover_year(bc["npv_modular"], bc["npv_monolithic"])
    if cx > 0:
        ax.axvline(cx, color="gray", linewidth=0.6, linestyle="--", alpha=0.5)
        ax.annotate(f"Crossover yr {cx}", xy=(cx, 0), fontsize=7,
                    xytext=(cx + 1.5, ax.get_ylim()[1] * 0.3 if ax.get_ylim()[1] > 0 else 0),
                    arrowprops=dict(arrowstyle="->", color="gray"))

    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative NPV [\\$B]")
    ax.set_title("NPV comparison (baseline)")
    ax.legend(fontsize=6, loc="lower right")

    # Right: crossover year vs launch cost
    ax = axes[1]
    dr_idx = len(sweep["discount_rates"]) // 2
    colors = ["#000000", "#E69F00", "#56B4E9"]
    for k, rev in enumerate(sweep["revenues"]):
        cy = sweep["crossover_year"][:, dr_idx, k]
        cy_plot = np.where(cy > 0, cy, np.nan)
        ax.plot(sweep["launch_costs"], cy_plot, "o-",
                color=colors[k % len(colors)], markersize=4, linewidth=1.0,
                label=f"Rev = \\${rev:.0f}/kg")

    ax.set_xlabel("Launch cost [\\$/kg to GTO]")
    ax.set_ylabel("Crossover year")
    ax.set_title(f"Crossover sensitivity ($r$ = {sweep['discount_rates'][dr_idx]:.0%})")
    ax.legend(fontsize=7)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
        print(f"  Saved: {output_path}")
    plt.close(fig)


def plot_cost_tornado(sweep: dict, output_path: Path = None):
    """Tornado diagram: sensitivity of NPV difference to each parameter."""
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))

    diff = sweep["npv_mod_final"] - sweep["npv_mono_final"]
    i_mid = len(sweep["launch_costs"]) // 2
    j_mid = len(sweep["discount_rates"]) // 2
    k_mid = len(sweep["revenues"]) // 2
    base_diff = diff[i_mid, j_mid, k_mid]

    sensitivities = []

    # Launch cost
    diffs_lc = diff[:, j_mid, k_mid]
    sensitivities.append({
        "name": f"Launch cost (\\${sweep['launch_costs'][0]:.0f}–\\${sweep['launch_costs'][-1]:.0f}/kg)",
        "low": float(diffs_lc[0] - base_diff),
        "high": float(diffs_lc[-1] - base_diff),
    })

    # Discount rate
    diffs_dr = diff[i_mid, :, k_mid]
    sensitivities.append({
        "name": f"Discount rate ({sweep['discount_rates'][0]:.0%}–{sweep['discount_rates'][-1]:.0%})",
        "low": float(diffs_dr[0] - base_diff),
        "high": float(diffs_dr[-1] - base_diff),
    })

    # Revenue
    diffs_rev = diff[i_mid, j_mid, :]
    sensitivities.append({
        "name": f"Payload revenue (\\${sweep['revenues'][0]:.0f}–\\${sweep['revenues'][-1]:.0f}/kg)",
        "low": float(diffs_rev[0] - base_diff),
        "high": float(diffs_rev[-1] - base_diff),
    })

    sensitivities.sort(key=lambda s: abs(s["high"] - s["low"]), reverse=True)

    fig, ax = plt.subplots(figsize=(5.5, 3))
    for i, s in enumerate(sensitivities):
        lo = min(s["low"], s["high"]) / 1e9
        hi = max(s["low"], s["high"]) / 1e9
        ax.barh(i, hi - lo, left=lo, height=0.5,
                color="#56B4E9", edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(sensitivities)))
    ax.set_yticklabels([s["name"] for s in sensitivities], fontsize=7)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_xlabel("$\\Delta$NPV (modular $-$ monolithic) vs. baseline [\\$B]")
    ax.set_title("Cost sensitivity tornado")
    ax.invert_yaxis()

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path)
        print(f"  Saved: {output_path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    params = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("LIFECYCLE NPV MODEL: MODULAR vs. MONOLITHIC")
    print("=" * 60)

    # Load Monte Carlo results if available
    mc_data = load_mc_results()
    mc_rates = None
    if mc_data is not None:
        mc_rates = get_mc_failure_rates(mc_data, params)
        if mc_rates:
            print(f"  Monte Carlo data loaded:")
            print(f"    P_sys(10yr, modular):  {mc_rates['P_sys_10yr_modular']:.4f}")
            print(f"    P_sys(10yr, mono):     {mc_rates['P_sys_10yr_mono']:.4f}")
            print(f"    P_fail/yr (modular):   {mc_rates['P_fail_annual_modular']:.6f}")
            print(f"    P_fail/yr (monolithic):{mc_rates['P_fail_annual_mono']:.4f}")
            print(f"    Repairs/yr:            {mc_rates['repairs_per_year']:.2f}")
    else:
        print("  No Monte Carlo data found — using analytical estimates.")

    print(f"\n  Lifetime:      {params['cost']['system_lifetime']} years")
    print(f"  Launch costs:  {params['cost']['launch_cost_sweep']} $/kg")
    print(f"  Discount rates:{params['cost']['discount_rate_sweep']}")
    print(f"  Revenue:       {params['cost']['payload_revenue_sweep']} $/kg")
    print(f"  Construction:  {params['cost']['construction_cadence']} segments/yr")
    print()

    sweep = run_sweep(params, mc_rates)

    # Print baseline
    bc = sweep["baseline_curves"]
    ca = bc["cost_assumptions"]
    print("  Baseline cost assumptions:")
    print(f"    Tether mass:       {ca['M_tether']/1e3:.0f} t")
    print(f"    Build cost:        ${ca['C_build']/1e9:.2f}B")
    print(f"    Years to build:    {ca['years_to_build']:.1f}")
    print(f"    Annual ops:        ${ca['C_ops_annual']/1e6:.0f}M")
    print(f"    Max annual revenue:${ca['Revenue_annual_max']/1e6:.0f}M")
    print(f"    Repair cost/event: ${ca['C_repair_event']/1e6:.1f}M")
    print(f"    Repairs/year:      {ca['repairs_per_year']:.2f}")
    print(f"    P_fail/yr (mono):  {ca['P_fail_annual_mono']:.4f}")
    print()

    # Phased revenue advantage
    rev_start_yr = ca["years_to_build"] * 0.6
    print(f"  PHASED CONSTRUCTION ADVANTAGE:")
    print(f"    Modular revenue starts at year {rev_start_yr:.1f} (60% completion)")
    print(f"    Monolithic revenue starts at year {ca['years_to_build']:.1f} (100% completion)")
    print(f"    Modular earns {ca['years_to_build'] - rev_start_yr:.1f} years of partial revenue before monolithic starts")
    print()

    # Summary table
    diff = sweep["npv_mod_final"] - sweep["npv_mono_final"]
    dr_idx = len(sweep["discount_rates"]) // 2
    print("  NPV_modular - NPV_monolithic at year 30 [$B]:")
    header = f"  {'LC $/kg':>10}" + "".join(f"  Rev=${r:.0f}" for r in sweep["revenues"])
    print(header)
    for i, lc in enumerate(sweep["launch_costs"]):
        row = f"  {lc:>10.0f}"
        for k in range(len(sweep["revenues"])):
            row += f"  {diff[i, dr_idx, k]/1e9:>8.2f}"
        print(row)

    # Crossover years
    print(f"\n  Crossover year (modular NPV > monolithic):")
    print(header)
    for i, lc in enumerate(sweep["launch_costs"]):
        row = f"  {lc:>10.0f}"
        for k in range(len(sweep["revenues"])):
            cy = sweep["crossover_year"][i, dr_idx, k]
            row += f"  {cy:>8d}" if cy > 0 else "    never"
        print(row)

    # Save
    np.savez(
        OUTPUT_DIR / "npv_results.npz",
        launch_costs=sweep["launch_costs"],
        discount_rates=sweep["discount_rates"],
        revenues=sweep["revenues"],
        npv_mod_final=sweep["npv_mod_final"],
        npv_mono_final=sweep["npv_mono_final"],
        crossover_year=sweep["crossover_year"],
        baseline_npv_modular=bc["npv_modular"],
        baseline_npv_monolithic=bc["npv_monolithic"],
    )
    print(f"\n  Saved: {OUTPUT_DIR / 'npv_results.npz'}")

    plot_npv_crossover(sweep, FIGURES_DIR / "fig_npv_crossover.pdf")
    plot_cost_tornado(sweep, FIGURES_DIR / "fig_cost_tornado.pdf")

    print("\nDone.")


if __name__ == "__main__":
    main()
