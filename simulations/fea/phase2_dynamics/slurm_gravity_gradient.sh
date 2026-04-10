#!/bin/bash
#SBATCH --job-name=gg-compare
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/gg_compare_%j.log
#SBATCH --error=jobs/gg_compare_%j.log

# Single task, <1 minute runtime (analytical, no MC).

# ── Load environment ──
module load conda/latest
conda activate elevator

# ── Verify environment ──
echo "=== Gravity-Gradient Comparison ==="
echo "Python: $(which python)"
echo "Node: $(hostname)"
echo "Start: $(date)"
echo "========================================="

# ── Run task ──
cd ~/Space-Elevator-Tether
python -m simulations.fea.phase2_dynamics.gravity_gradient_comparison

echo "End: $(date)"
