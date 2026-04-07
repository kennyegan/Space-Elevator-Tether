"""
comparison_table.py — Part F: LaTeX (booktabs) and CSV comparison table.

Compares 1D model (existing), 2D no-Coriolis, and 2D with Coriolis results.
"""

import csv
import numpy as np
from pathlib import Path

from simulations.fea.phase2_dynamics.config import OUTPUT_DIR


def generate_comparison_table(modal_results: dict,
                              transit_results: dict,
                              sweep_results: dict,
                              params: dict,
                              output_dir: Path = OUTPUT_DIR) -> dict:
    """
    Generate the comparison table for the revised manuscript.

    Parameters
    ----------
    modal_results : dict
        Output from run_modal_comparison (4 cases).
    transit_results : dict
        Output from run_single_transit.
    sweep_results : dict
        Output from run_resonance_sweep.
    params : dict
        Master parameters.

    Returns
    -------
    dict with 'rows' (list of dicts) and file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract modal periods
    # Keys: 'eta1.00_coriolis_off', 'eta0.95_coriolis_off',
    #        'eta1.00_coriolis_on', 'eta0.95_coriolis_on'
    T1_1d_analytical = 25.3  # analytical uniform-string result [h]
    T1_1d_discrete = 8.60    # existing 500-segment discrete model [h]

    def _get_T(case_key, mode_idx=0):
        if case_key in modal_results:
            return modal_results[case_key]["period_h"][mode_idx]
        return np.nan

    T1_2d_noc = _get_T("eta1.00_coriolis_off")
    T1_2d_cor = _get_T("eta1.00_coriolis_on")
    T2_2d_noc = _get_T("eta1.00_coriolis_off", 1)
    T2_2d_cor = _get_T("eta1.00_coriolis_on", 1)

    # Joint compliance shift (no Coriolis)
    f1_perfect = 1.0 / _get_T("eta1.00_coriolis_off") if _get_T("eta1.00_coriolis_off") > 0 else 0
    f1_joints = 1.0 / _get_T("eta0.95_coriolis_off") if _get_T("eta0.95_coriolis_off") > 0 else 0
    shift_2d = abs(f1_perfect - f1_joints) / f1_perfect * 100 if f1_perfect > 0 else 0

    # Transit results
    peak_u = transit_results.get("peak_u_km", np.nan)
    peak_v = transit_results.get("peak_v_km", np.nan)
    peak_dT = transit_results.get("peak_dT_ratio", np.nan)

    # Multi-climber
    worst_sep = sweep_results.get("worst_sep_hours", np.nan)
    # Find min safe separation (where dT_ratio < 0.10)
    seps = sweep_results.get("separations", np.array([]))
    dT_arr = sweep_results.get("peak_dT_ratio", np.array([]))
    safe_mask = dT_arr < 0.10
    min_safe = float(np.min(seps[safe_mask])) if np.any(safe_mask) else np.nan

    rows = [
        {"Property": r"$T_1$ analytical [h]",
         "1D Model": f"{T1_1d_analytical:.1f}",
         "2D No Coriolis": "---",
         "2D With Coriolis": "---",
         "Delta": "---"},
        {"Property": r"$T_1$ transverse (2D) [h]",
         "1D Model": "N/A",
         "2D No Coriolis": f"{T1_2d_noc:.2f}",
         "2D With Coriolis": f"{T1_2d_cor:.2f}",
         "Delta": f"{abs(T1_2d_cor - T1_2d_noc)/T1_2d_noc*100:.1f}\\%"},
        {"Property": r"$T_1$ longitudinal [h]",
         "1D Model": f"{T1_1d_discrete:.2f}",
         "2D No Coriolis": f"{T2_2d_noc:.2f}",
         "2D With Coriolis": f"{T2_2d_cor:.2f}",
         "Delta": f"{abs(T2_2d_cor - T1_1d_discrete)/T1_1d_discrete*100:.1f}\\%"},
        {"Property": r"Joint shift ($\eta_j$ 1.0$\to$0.95)",
         "1D Model": "2.3\\%",
         "2D No Coriolis": f"{shift_2d:.1f}\\%",
         "2D With Coriolis": "---",
         "Delta": "---"},
        {"Property": "Max longitudinal [km]",
         "1D Model": "67.3 (quasi-static)",
         "2D No Coriolis": "---",
         "2D With Coriolis": f"{peak_u:.1f} (dynamic)",
         "Delta": "---"},
        {"Property": "Max transverse [km]",
         "1D Model": "N/A",
         "2D No Coriolis": "---",
         "2D With Coriolis": f"{peak_v:.1f}",
         "Delta": "NEW"},
        {"Property": r"Peak $\Delta T / T_\mathrm{eq}$",
         "1D Model": "N/A",
         "2D No Coriolis": "---",
         "2D With Coriolis": f"{peak_dT:.4f}",
         "Delta": "NEW"},
        {"Property": "Critical climber sep [h]",
         "1D Model": r"$\sim$25 (noted)",
         "2D No Coriolis": "---",
         "2D With Coriolis": f"{worst_sep:.0f}",
         "Delta": "QUANTIFIED"},
        {"Property": "Min safe separation [h]",
         "1D Model": "N/A",
         "2D No Coriolis": "---",
         "2D With Coriolis": f"{min_safe:.0f}" if not np.isnan(min_safe) else "---",
         "Delta": "NEW RULE"},
    ]

    # Write LaTeX
    tex_path = output_dir / "comparison_table.tex"
    _write_latex(rows, tex_path)

    # Write CSV
    csv_path = output_dir / "comparison_table.csv"
    _write_csv(rows, csv_path)

    return {"rows": rows, "tex_path": tex_path, "csv_path": csv_path}


def _write_latex(rows: list, path: Path):
    """Write booktabs LaTeX table."""
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Comparison of 1D and 2D tether dynamic models.}",
        r"\label{tab:dynamics_comparison}",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"Property & 1D Model & 2D (no Coriolis) & 2D (Coriolis) & $\Delta$ \\",
        r"\midrule",
    ]
    for row in rows:
        line = " & ".join([row["Property"], row["1D Model"],
                           row["2D No Coriolis"], row["2D With Coriolis"],
                           row["Delta"]]) + r" \\"
        lines.append(line)
    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    print(f"  Saved: {path}")


def _write_csv(rows: list, path: Path):
    """Write CSV table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["Property", "1D Model", "2D No Coriolis",
                  "2D With Coriolis", "Delta"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Strip LaTeX for CSV
            clean = {k: v.replace(r"\%", "%").replace("\\", "").replace("$", "")
                     for k, v in row.items()}
            writer.writerow(clean)
    print(f"  Saved: {path}")
