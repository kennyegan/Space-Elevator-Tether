#!/bin/bash
#SBATCH --job-name=weibull-validate
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/weibull_validate_%j.log
#SBATCH --error=jobs/weibull_validate_%j.log

# ── Load environment ──
module load conda/latest
conda activate elevator

# ── Verify environment ──
echo "=== Weibull Validation ==="
echo "Python: $(which python)"
echo "NumPy: $(python -c 'import numpy; print(numpy.__version__)')"
echo "Node: $(hostname)"
echo "Start: $(date)"
echo "========================="

# ── Run validation (100K trajectories) ──
cd ~/Space-Elevator-Tether
python -m simulations.monte_carlo.phase1_weibull.validate --n-trajectories 100000

echo "Exit code: $?"
echo "End: $(date)"
