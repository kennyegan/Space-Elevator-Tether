"""
plot_figures.py — Generate all 9 publication figures for Phase 2 dynamics.

Figures 1-5: Single climber transit (Part D)
Figures 6-9: Multi-climber resonance (Part E)

All figures use the acta_astronautica.mplstyle for Elsevier formatting.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from simulations.fea.phase2_dynamics.config import STYLE_FILE, FIGURES_DIR


def _apply_style():
    if STYLE_FILE.exists():
        plt.style.use(str(STYLE_FILE))


# =========================================================================
# Part D: Single climber figures
# =========================================================================

def plot_longitudinal_envelope(transit: dict, output_dir: Path = FIGURES_DIR):
    """Fig 1: max|u| vs altitude, with quasi-static comparison."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(3.54, 3.0))

    alt_km = transit["alt_nodes"] / 1e3
    u_km = transit["u_envelope"] / 1e3

    ax.plot(alt_km, u_km, "-", color="#0072B2", linewidth=1.2,
            label="2D dynamic")
    ax.axhline(67.3, color="gray", linewidth=0.75, linestyle="--",
               label="Quasi-static peak (67.3 km)")
    ax.axvline(35786, color="gray", linewidth=0.5, linestyle=":", alpha=0.5)

    ax.set_xlabel("Altitude [km]")
    ax.set_ylabel("Max longitudinal displacement [km]")
    ax.set_title("Longitudinal displacement envelope")
    ax.legend(fontsize=7)

    _save(fig, output_dir / "fig_longitudinal_envelope.pdf")


def plot_transverse_envelope(transit: dict, output_dir: Path = FIGURES_DIR):
    """Fig 2: max|v| vs altitude."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(3.54, 3.0))

    alt_km = transit["alt_nodes"] / 1e3
    v_km = transit["v_envelope"] / 1e3

    ax.plot(alt_km, v_km, "-", color="#D55E00", linewidth=1.2)
    ax.axvline(35786, color="gray", linewidth=0.5, linestyle=":", alpha=0.5)

    ax.set_xlabel("Altitude [km]")
    ax.set_ylabel("Max transverse displacement [km]")
    ax.set_title("Transverse displacement envelope")
    ax.annotate(f"Peak: {transit['peak_v_km']:.1f} km",
                xy=(alt_km[np.argmax(transit["v_envelope"])],
                    transit["peak_v_km"]),
                fontsize=7, color="#D55E00")

    _save(fig, output_dir / "fig_transverse_envelope.pdf")


def plot_waterfall(transit: dict, output_dir: Path = FIGURES_DIR):
    """Fig 3: v(r,t) color map — altitude vs time."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.48, 4.0))

    t_h = transit["time"] / 3600.0
    alt_km = transit["alt_nodes"] / 1e3
    v_full_km = transit["v_full"] / 1e3

    # Create meshgrid for pcolormesh
    T, A = np.meshgrid(t_h, alt_km)
    vmax = np.max(np.abs(v_full_km)) * 0.8
    if vmax == 0:
        vmax = 1.0

    im = ax.pcolormesh(T, A, v_full_km, cmap="RdBu_r",
                        vmin=-vmax, vmax=vmax, shading="auto", rasterized=True)
    cbar = fig.colorbar(im, ax=ax, label="Transverse displacement [km]")

    ax.axhline(35786, color="white", linewidth=0.5, linestyle="--", alpha=0.7)
    ax.set_xlabel("Time [h]")
    ax.set_ylabel("Altitude [km]")
    ax.set_title("Transverse response — space-time waterfall")

    _save(fig, output_dir / "fig_waterfall_vrt.pdf")


def plot_tension_perturbation(transit: dict, output_dir: Path = FIGURES_DIR):
    """Fig 4: max|dT/T_eq| vs altitude."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(3.54, 3.0))

    alt_km = transit["alt_elem_mid"] / 1e3
    dT_pct = transit["dT_ratio_envelope"] * 100.0

    ax.plot(alt_km, dT_pct, "-", color="#009E73", linewidth=1.2)
    ax.axhline(10.0, color="red", linewidth=0.75, linestyle="--",
               label="10% threshold")
    ax.axvline(35786, color="gray", linewidth=0.5, linestyle=":", alpha=0.5)

    ax.set_xlabel("Altitude [km]")
    ax.set_ylabel(r"Max $|\Delta T / T_\mathrm{eq}|$ [%]")
    ax.set_title("Tension perturbation ratio")
    ax.legend(fontsize=7)

    _save(fig, output_dir / "fig_tension_perturbation.pdf")


def plot_geo_time_history(transit: dict, output_dir: Path = FIGURES_DIR):
    """Fig 5: u(t) and v(t) at GEO node."""
    _apply_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.48, 4.5), sharex=True)

    t_h = transit["time"] / 3600.0

    ax1.plot(t_h, transit["u_geo"] / 1e3, "-", color="#0072B2", linewidth=0.8)
    ax1.set_ylabel("Longitudinal [km]")
    ax1.set_title("Displacement at GEO")

    ax2.plot(t_h, transit["v_geo"] / 1e3, "-", color="#D55E00", linewidth=0.8)
    ax2.set_ylabel("Transverse [km]")
    ax2.set_xlabel("Time [h]")

    # Mark transit end
    from simulations.fea.phase2_dynamics.config import get_constants, load_params
    params = load_params()
    c = get_constants(params)
    t_transit_h = c["L_total"] / c["v_climber"] / 3600.0
    for ax in (ax1, ax2):
        ax.axvline(t_transit_h, color="gray", linewidth=0.5, linestyle=":",
                   alpha=0.5)

    _save(fig, output_dir / "fig_geo_time_history.pdf")


# =========================================================================
# Part E: Multi-climber resonance figures
# =========================================================================

def plot_resonance_scan(sweep: dict, output_dir: Path = FIGURES_DIR):
    """Fig 6: peak transverse displacement vs departure separation."""
    _apply_style()
    fig, ax1 = plt.subplots(figsize=(3.54, 3.0))

    sep = sweep["separations"]
    peak_v_km = sweep["peak_v"] / 1e3

    ax1.plot(sep, peak_v_km, "o-", color="#0072B2", linewidth=1.2,
             markersize=4, label="Peak transverse")
    ax1.set_xlabel(r"Departure separation $\Delta t$ [h]")
    ax1.set_ylabel("Peak transverse displacement [km]")
    ax1.set_title("Multi-climber resonance scan")

    # Mark worst case
    i_worst = int(np.argmax(peak_v_km))
    ax1.annotate(f"Resonance: {sep[i_worst]:.0f} h",
                 xy=(sep[i_worst], peak_v_km[i_worst]),
                 xytext=(sep[i_worst] + 3, peak_v_km[i_worst] * 0.9),
                 fontsize=7, arrowprops=dict(arrowstyle="->", color="#D55E00"),
                 color="#D55E00")

    _save(fig, output_dir / "fig_resonance_scan.pdf")


def plot_safe_separation(sweep: dict, output_dir: Path = FIGURES_DIR):
    """Fig 7: tension perturbation ratio vs separation with 10% line."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(3.54, 3.0))

    sep = sweep["separations"]
    dT_pct = sweep["peak_dT_ratio"] * 100.0

    ax.plot(sep, dT_pct, "s-", color="#009E73", linewidth=1.2, markersize=4)
    ax.axhline(10.0, color="red", linewidth=0.75, linestyle="--",
               label="10% safety threshold")
    ax.fill_between(sep, 0, 10.0, alpha=0.1, color="green")

    ax.set_xlabel(r"Departure separation $\Delta t$ [h]")
    ax.set_ylabel(r"Peak $|\Delta T / T_\mathrm{eq}|$ [%]")
    ax.set_title("Safe climber separation envelope")
    ax.legend(fontsize=7)

    _save(fig, output_dir / "fig_safe_separation.pdf")


def plot_resonant_vs_offresonant(sweep: dict, output_dir: Path = FIGURES_DIR):
    """Fig 8: side-by-side GEO v(t) for worst-case and best-case separations."""
    _apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.48, 3.0), sharey=True)

    results = sweep["all_results"]
    peak_v_arr = sweep["peak_v"]

    i_worst = int(np.argmax(peak_v_arr))
    i_best = int(np.argmin(peak_v_arr))

    for ax, idx, label in [(ax1, i_worst, "Resonant"),
                            (ax2, i_best, "Off-resonant")]:
        r = results[idx]
        t_h = r["t"] / 3600.0
        ax.plot(t_h, r["v_geo"] / 1e3, "-", color="#D55E00", linewidth=0.6)
        ax.set_xlabel("Time [h]")
        ax.set_title(f"{label} ({r['sep_hours']:.0f} h)")

    ax1.set_ylabel("Transverse at GEO [km]")

    _save(fig, output_dir / "fig_resonant_vs_offresonant.pdf")


def plot_damping_sensitivity(damp: dict, output_dir: Path = FIGURES_DIR):
    """Fig 9: peak v vs damping ratio at resonant separation."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(3.54, 3.0))

    ax.plot(damp["zeta_values"], damp["peak_v"] / 1e3, "o-",
            color="#0072B2", linewidth=1.2, markersize=5)
    ax.set_xlabel(r"Damping ratio $\zeta$")
    ax.set_ylabel("Peak transverse displacement [km]")
    ax.set_title(f"Damping sensitivity (sep = {damp['sep_hours']:.0f} h)")
    ax.set_xscale("log")

    _save(fig, output_dir / "fig_damping_sensitivity.pdf")


# =========================================================================
# Utility
# =========================================================================

def _save(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    print(f"  Saved: {path}")
    plt.close(fig)


def plot_all_single(transit: dict, output_dir: Path = FIGURES_DIR):
    """Generate all 5 single-climber figures."""
    plot_longitudinal_envelope(transit, output_dir)
    plot_transverse_envelope(transit, output_dir)
    plot_waterfall(transit, output_dir)
    plot_tension_perturbation(transit, output_dir)
    plot_geo_time_history(transit, output_dir)


def plot_all_multi(sweep: dict, damp: dict, output_dir: Path = FIGURES_DIR):
    """Generate all 4 multi-climber figures."""
    plot_resonance_scan(sweep, output_dir)
    plot_safe_separation(sweep, output_dir)
    plot_resonant_vs_offresonant(sweep, output_dir)
    plot_damping_sensitivity(damp, output_dir)
