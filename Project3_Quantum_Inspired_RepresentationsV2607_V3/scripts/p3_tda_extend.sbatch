#!/bin/bash
#SBATCH --job-name=p3_tda_full
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_tda_full_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_tda_full_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --partition=production

set -euo pipefail

PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

cd "${PROJECT_DIR}"

echo "=== TDA Fingerprint Generation (full c6_primary) ==="
echo "Started at: $(date)"
echo "Host: $(hostname)"
echo "Input: results/c6_primary_leads_synthesisable.csv"
echo "===================================================="

time "${PYTHON}" "${PROJECT_DIR}/scripts/p3_tda_pipeline.py" \
  --n-jobs 4 2>&1

echo ""
echo "=== Vérification ==="
echo "Lines in output:"
wc -l results/p3_tda_fingerprints.csv 2>/dev/null || echo "FILE NOT FOUND"
echo ""
echo "=== Completed at: $(date) ==="
