#!/bin/bash
#SBATCH --job-name=p3_5000_precompute
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_5000_precompute_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_5000_precompute_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=85G
#SBATCH --time=06:00:00
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
RESULTS_DIR="${PROJECT_DIR}/results"

cd "${PROJECT_DIR}"

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  P3 Hybrid Benchmark (n=5,000) — PRECOMPUTE KERNEL                  ║"
echo "╠══════════════════════════════════════════════════════════════════════╣"
echo "║  CPUs:    $(nproc)                                                    ║"
echo "║  Device:  lightning.qubit (CPU, optimal)                             ║"
echo "║  Mode:    --precompute-kernel (kernel ONCE, ~5x QK speedup)         ║"
echo "║  Ablation: INCLUDED (free with precompute)                           ║"
echo "║  Start:   $(date -u -Iseconds)                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"

"${PYTHON}" "${PROJECT_DIR}/scripts/p3_hybrid_benchmark.py" \
  --n-mols 5000 \
  --block-size 200 \
  --n-repeats 1 \
  --n-kpca 10 \
  --n-qubits 8 \
  --device lightning.qubit \
  --precompute-kernel \
  --hpc \
  --checkpoint "${RESULTS_DIR}/p3_5000_precompute_checkpoint.json"

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  P3 Hybrid Benchmark COMPLETE ✓                                      ║"
echo "║  End: $(date -u -Iseconds)                                            ║"
echo "║  CSV:   ${RESULTS_DIR}/p3_hybrid_benchmark.csv                        ║"
echo "║  Summary: ${RESULTS_DIR}/p3_hybrid_summary.txt                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
