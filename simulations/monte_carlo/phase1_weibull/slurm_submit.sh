#!/bin/bash
#SBATCH --job-name=weibull-mc
#SBATCH --array=0-251
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/weibull_%A_%a.log
#SBATCH --error=jobs/weibull_%A_%a.log

# ── Load environment ──
module load conda/latest
conda activate elevator

# ── Verify environment ──
echo "=== Weibull MC Task ${SLURM_ARRAY_TASK_ID} ==="
echo "Python: $(which python)"
echo "Node: $(hostname)"
echo "Start: $(date)"
echo "========================================="

# ── Run task ──
cd ~/Space-Elevator-Tether
python -m simulations.monte_carlo.phase1_weibull.slurm_task \
    --task-id ${SLURM_ARRAY_TASK_ID} \
    --n-trajectories 100000

echo "End: $(date)"
