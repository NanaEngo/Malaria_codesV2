#!/bin/bash
#SBATCH --job-name=p3_hybrid_canonical
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_canonical_19849_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_canonical_19849_%j.err
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
echo "║  P3 Canonical Hybrid Benchmark (n = 19,849 panel)          ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  CPUs: $(nproc)                                               ║"
echo "║  Start: $(date -u -Iseconds)                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "  BMAD v51 (Aug 1, 2026) — Appendix K remediation (peer-review audit):"
echo "  * C2/M3: canonical panel (TFP order ∩ dedup activity ∩ finite-TNE) shared"
echo "           by hybrid + classical + ablation; no silent imputation."
echo "  * C1/M2: checkpoint resume now merges completed-fold records (full 5-fold"
echo "           statistics), ablation honors completed_folds."
echo "  * M1: per-fold UMAP (fit on train only) — NO --precompute-kernel,"
echo "           no transductive leakage. State-vector kernel (~70 s/fold)."
echo "  * Phase-2 winning combo: --n-qubits 6 --n-repeats 1 --n-kpca 30."
echo "  * --skip-classical: seeds classical rows from the canonical RF-only"
echo "    benchmark CSV (p3_classical_benchmark_19849.csv) — avoids the slow"
echo "    per-descriptor SVM path (job 12693 incident); run the classical"
echo "    sbatch FIRST."

"${PYTHON}" "${PROJECT_DIR}/scripts/p3_hybrid_benchmark.py" \
  --n-mols 19849 \
  --hpc \
  --block-size 200 \
  --n-qubits 6 \
  --n-repeats 1 \
  --n-kpca 30 \
  --skip-classical \
  --checkpoint "${PROJECT_DIR}/results/p3_hybrid_canonical_checkpoint.json"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Canonical Hybrid Benchmark COMPLETE ✓"
echo "║  End: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
