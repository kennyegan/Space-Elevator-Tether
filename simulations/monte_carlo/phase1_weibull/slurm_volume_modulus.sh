#!/bin/bash
#SBATCH --job-name=vol-mod-mc
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/vol_mod_%j.log
#SBATCH --error=jobs/vol_mod_%j.log

# Single task: 50 combos × 100K trajectories (~30 min).

# ── Load environment ──
module load conda/latest
conda activate elevator

# ── Verify environment ──
echo "=== Volume Modulus Sweep ==="
echo "Python: $(which python)"
echo "Node: $(hostname)"
echo "Start: $(date)"
echo "========================================="

# ── Run task ──
cd ~/Space-Elevator-Tether
python -m simulations.monte_carlo.phase1_weibull.volume_modulus_sweep \
    --n-trajectories 100000

echo "End: $(date)"
