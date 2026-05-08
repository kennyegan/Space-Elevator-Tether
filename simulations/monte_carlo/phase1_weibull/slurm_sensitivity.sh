#!/bin/bash
#SBATCH --job-name=weibull-sens
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --partition=cpu
#SBATCH --output=jobs/weibull_sensitivity_%j.log
#SBATCH --error=jobs/weibull_sensitivity_%j.log

module load conda/latest
conda activate elevator

cd ~/Space-Elevator-Tether
python -m simulations.monte_carlo.phase1_weibull.sensitivity_analysis
