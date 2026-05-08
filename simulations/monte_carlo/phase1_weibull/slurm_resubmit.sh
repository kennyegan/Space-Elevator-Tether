#!/bin/bash
#SBATCH --job-name=weibull-resub
#SBATCH --array=227-230
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/weibull_%A_%a.log
#SBATCH --error=jobs/weibull_%A_%a.log

# Longer wall time (4h) for N=500 tasks that timed out at 2h.
# The script skips combos whose output files already exist.

module load conda/latest
conda activate elevator

echo "=== Weibull MC Resubmit Task ${SLURM_ARRAY_TASK_ID} ==="
echo "Node: $(hostname), Start: $(date)"

cd ~/Space-Elevator-Tether
python -m simulations.monte_carlo.phase1_weibull.slurm_task \
    --task-id ${SLURM_ARRAY_TASK_ID} \
    --n-trajectories 100000

echo "End: $(date)"
