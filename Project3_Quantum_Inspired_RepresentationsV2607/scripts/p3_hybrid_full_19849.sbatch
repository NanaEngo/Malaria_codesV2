#!/bin/bash
#SBATCH --job-name=p3_hybrid_full_19849
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_full_19849_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_full_19849_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=80G
#SBATCH --time=12:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
export NUMEXPR_NUM_THREADS=$SLURM_CPUS_PER_TASK
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
echo "  BMAD v50 (July 31, 2026): Phase 3b RESTORED — state-vector kernel."
echo "  OPTIMISED (Aug 1, 2026): --skip-classical (classical RF n=19,849 already"
echo "  exist in p3_classical_benchmark_19849.csv; partial seeded with those 40"
echo "  rows) + --precompute-kernel (QK kernel computed ONCE on all data instead"
echo "  of 5x per-fold — avoids 4/5 of QK computation). Expected < 1 h (vs ~5h+"
echo "  wasted on per-descriptor SVC in the aborted job 12693)."
echo "  FIX (Aug 1, 2026): job 12695 was launched with script DEFAULTS"
echo "  (n_qubits=8, n_kpca=10) instead of the Phase-2 winning combo"
echo "  (bond_dim=6 -> n_qubits=6, n_repeats=1, n_kpca=30). Killed + resubmitted"
echo "  with --n-qubits 6 --n-repeats 1 --n-kpca 30."

"${PYTHON}" "${PROJECT_DIR}/scripts/p3_hybrid_benchmark.py" \
  --n-mols 19849 \
  --hpc \
  --block-size 200 \
  --n-qubits 6 \
  --n-repeats 1 \
  --n-kpca 30 \
  --skip-ablation \
  --skip-classical \
  --precompute-kernel \
  --checkpoint "${PROJECT_DIR}/results/p3_hybrid_full_checkpoint.json"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Full-Library Hybrid Benchmark COMPLETE ✓"
echo "║  End: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
