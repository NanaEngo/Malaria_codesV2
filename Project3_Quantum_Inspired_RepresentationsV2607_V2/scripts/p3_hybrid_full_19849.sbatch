#!/bin/bash
#SBATCH --job-name=p3_hybrid_full_19849
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_full_19849_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_full_19849_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=128G
#SBATCH --time=96:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

export OMP_NUM_THREADS=48
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1

PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

cd "${PROJECT_DIR}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Full-Library Hybrid Benchmark (n = 19,849)             ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  CPUs: $(nproc)                                               ║"
echo "║  Start: $(date -u -Iseconds)                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"

"${PYTHON}" "${PROJECT_DIR}/scripts/p3_hybrid_benchmark.py" \
  --n-mols 19849 \
  --hpc \
  --block-size 400 \
  --skip-ablation \
  --checkpoint "${PROJECT_DIR}/results/p3_hybrid_full_checkpoint.json"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Full-Library Hybrid Benchmark COMPLETE ✓"
echo "║  End: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
