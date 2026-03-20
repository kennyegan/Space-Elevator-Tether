#!/bin/bash
#SBATCH --job-name=elevator-modal
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=jobs/modal_output_%j.log
#SBATCH --error=jobs/modal_error_%j.log

# ── Load environment ──
module load conda/latest
conda activate elevator

# ── Verify environment ──
echo "=== Environment Check ==="
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo "Node: $(hostname)"
echo "========================="

# ── Run simulation ──
cd ~/Space-Elevator-Tether
python simulations/fea/modal_analysis.py
