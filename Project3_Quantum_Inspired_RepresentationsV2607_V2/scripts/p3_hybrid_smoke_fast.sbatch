#!/bin/bash
#SBATCH --job-name=p3_smoke_fast
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_smoke_fast_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_smoke_fast_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1

PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
RESULTS_DIR="${PROJECT_DIR}/results"

cd "${PROJECT_DIR}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Smoke Test (n=500) — FAST (skip-ablation)              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  CPUs:    $(nproc)                                          ║"
echo "║  Start:   $(date -u -Iseconds)                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"

"${PYTHON}" "${PROJECT_DIR}/scripts/p3_hybrid_benchmark.py" \
  --n-mols 500 \
  --block-size 200 \
  --n-repeats 1 \
  --n-kpca 10 \
  --device lightning.qubit \
  --hpc \
  --skip-ablation \
  --checkpoint "${RESULTS_DIR}/p3_smoke_fast_checkpoint.json"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Smoke Test COMPLETE ✓                                   ║"
echo "║  End: $(date -u -Iseconds)                                  ║"
echo "║  Summary: ${RESULTS_DIR}/p3_hybrid_summary.txt              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
