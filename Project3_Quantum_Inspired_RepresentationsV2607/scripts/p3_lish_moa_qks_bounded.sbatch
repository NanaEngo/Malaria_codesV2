#!/bin/bash
#SBATCH --job-name=p3_lish_qks
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=logs/slurm/p3_lish_qks_%j.log
#SBATCH --error=logs/slurm/p3_lish_qks_%j.err
set -euo pipefail
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
ROOT=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$ROOT"
mkdir -p logs/slurm
$PY scripts/p3_lish_moa_qks_bounded.py --limit-drugs 500 --labels top3 --n-jobs 8 --block-size 100
