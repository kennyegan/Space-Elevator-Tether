#!/bin/bash
#SBATCH --job-name=elevator-mc
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --constraint=sm_75
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=2-00:00:00
#SBATCH --output=jobs/mc_output_%j.log
#SBATCH --error=jobs/mc_error_%j.log

# ── Load environment ──
module load cuda/12.8
module load conda/latest
conda activate elevator

# CUDA runtime libs (nvrtc-builtins) needed by CuPy
export LD_LIBRARY_PATH="/modules/opt/linux-ubuntu24.04-x86_64/nvhpc/Linux_x86_64/24.9/cuda/12.8/targets/x86_64-linux/lib:${LD_LIBRARY_PATH}"

# Allow deprecated GPU architectures (TITAN X = sm_52)
export CUPY_NUM_NVRTC_OPTIONS=1
export CUPY_NVRTC_OPTIONS="--allow-deprecated-gpu-targets"

# ── Verify environment ──
echo "=== Environment Check ==="
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo "NumPy: $(python -c 'import numpy; print(numpy.__version__)')"
echo "CuPy: $(python -c 'import cupy; print(cupy.__version__)' 2>&1)"
echo "Working dir: $(pwd)"
echo "Node: $(hostname)"
nvidia-smi
echo "========================="

# ── Run simulation ──
cd ~/Space-Elevator-Tether
python simulations/monte_carlo/joint_reliability.py --n-trajectories 100000 --gpu
