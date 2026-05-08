#!/bin/bash
#SBATCH --job-name=q-sens-mc
#SBATCH --array=0-2
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=08:00:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/q_sens_%A_%a.log
#SBATCH --error=jobs/q_sens_%A_%a.log

# Each array task runs one Q value (0=0.8eV, 1=1.1eV, 2=1.4eV).
# 90 combos per Q × 100K trajectories each.

# ── Load environment ──
module load conda/latest
conda activate elevator

# ── Verify environment ──
echo "=== Q-Sensitivity Task ${SLURM_ARRAY_TASK_ID} ==="
echo "Python: $(which python)"
echo "Node: $(hostname)"
echo "Start: $(date)"
echo "========================================="

# ── Run task ──
cd ~/Space-Elevator-Tether
python -m simulations.monte_carlo.phase1_weibull.q_sensitivity_sweep \
    --q-index ${SLURM_ARRAY_TASK_ID} \
    --n-trajectories 100000

echo "End: $(date)"
