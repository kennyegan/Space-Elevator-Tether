#!/bin/bash
#SBATCH --job-name=weibull-post
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/weibull_postprocess_%j.log
#SBATCH --error=jobs/weibull_postprocess_%j.log

module load conda/latest
conda activate elevator

cd ~/Space-Elevator-Tether

echo "=== Step 1: Merge Results ==="
python -m simulations.monte_carlo.phase1_weibull.merge_results

echo ""
echo "=== Step 2: Sensitivity Analysis (Figs 6-7) ==="
python -m simulations.monte_carlo.phase1_weibull.sensitivity_analysis

echo ""
echo "=== Step 3: MC Figures (Figs 1-5) ==="
python -m simulations.monte_carlo.phase1_weibull.plot_figures

echo ""
echo "=== Done ==="
echo "Outputs:"
ls -la paper/figures/fig_*beta*.pdf paper/figures/fig_hazard_*.pdf paper/figures/fig_mttr_by_beta.pdf paper/figures/fig_cadence_sensitivity_by_beta.pdf 2>/dev/null
echo "---"
ls -la data/processed/psys_weibull_surface.npz data/processed/weibull_sweep_results.csv 2>/dev/null
echo "---"
cat simulations/monte_carlo/phase1_weibull/results/figure_notes.md
