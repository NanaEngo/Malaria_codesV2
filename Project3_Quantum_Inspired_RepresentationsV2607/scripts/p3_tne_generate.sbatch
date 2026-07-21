#!/bin/bash
#SBATCH --job-name=p3_tne_bd8
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_tne_bd8_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_tne_bd8_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --partition=production

set -euo pipefail

PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

cd "${PROJECT_DIR}"

echo "=== TNE Generation: bond_dim=8, n_jobs=4 ==="
echo "Started at: $(date)"
echo "Host: $(hostname)"
echo "============================================"

time "${PYTHON}" "${PROJECT_DIR}/scripts/p3_tne_pipeline.py" \
  --bond-dim 8 \
  --n-jobs 4 2>&1

echo "=== Completed at: $(date) ==="
