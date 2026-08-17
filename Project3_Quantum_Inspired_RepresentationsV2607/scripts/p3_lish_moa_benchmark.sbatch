#!/bin/bash
#SBATCH --job-name=p3_lish_moa
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=12:00:00
#SBATCH --output=logs/slurm/p3_lish_moa_%j.log
#SBATCH --error=logs/slurm/p3_lish_moa_%j.err
set -euo pipefail
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
ROOT=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$ROOT"
mkdir -p logs/slurm
$PY scripts/p3_lish_moa_benchmark.py --n-jobs 16
