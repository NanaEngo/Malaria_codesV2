#!/bin/bash
#SBATCH --job-name=p3_qks_n5000
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --partition=production
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qks_n5000_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qks_n5000_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL

set -euo pipefail
export PYTHONUNBUFFERED=1

# ─────────────────────────────────────────────────────────────────────────────
# P3 QKS standalone benchmark, n=5,000 (5-fold CV)
#   p3_qks_benchmark.py --n-mols 5000
#
# BMAD v51 (Aug 1, 2026): C3 fix + optimal params. Canonical n_qubits=6,
# n_repeats=1 (Phase-2 winning combo). One StandardScaler fit on TRAIN applied
# to both train and test kernels (C3) so QK/RBF/linear share one embedding.
#
# BMAD §3.3 (July 31, 2026): align Table 4 kernel comparison with the completed
# n=5,000 hybrid benchmark (§3.4b) and consolidate the n=500 null result
# (Quantum AUC 0.751 vs RBF 0.701, p=0.088 ns) with greater statistical power.
#
# Phase-scope: (200 → 500 → 5,000); full-library n=19,849 QKS dropped (O(N²)
# prohibitive, ~100 h+ single-core) — classical-only n=19,849 remains canonical.
#
# Expected cost: ~12M pairs/fold × 5 folds ≈ 60M pairs → ~2 h at 16 cores
#   (block_size=200 via --hpc, n_jobs auto = SLURM_CPUS_PER_TASK).
#
# ⚠️ The script writes fixed output names (p3_qks_benchmark.csv /
#    p3_qks_summary.txt). Canonical n=500 files are preserved below by copying
#    them to _n500-suffixed names BEFORE the run, then moving the new outputs to
#    _n5000-suffixed names AFTER, leaving the canonical names untouched.
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_ROOT}/results"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

echo "=== P3 QKS Standalone Benchmark n=5,000 ==="
echo "Date: $(date)"
echo "Node: $(hostname)"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Project root: $PROJECT_ROOT"

mkdir -p "${PROJECT_ROOT}/logs/slurm"

# 1. Preserve canonical n=500 files (no-op if already preserved)
cp -n "${RESULTS_DIR}/p3_qks_benchmark.csv"  "${RESULTS_DIR}/p3_qks_benchmark_n500.csv"  || echo "  [skip] n500 csv already preserved"
cp -n "${RESULTS_DIR}/p3_qks_summary.txt"    "${RESULTS_DIR}/p3_qks_summary_n500.txt"    || echo "  [skip] n500 summary already preserved"
echo "  Preserved canonical n=500 results as *_n500.csv / *_n500.txt"

# 2. Run standalone QKS benchmark on 5,000 molecules
cd "${PROJECT_ROOT}"
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK

$PYTHON scripts/p3_qks_benchmark.py \
    --n-mols 5000 \
    --n-qubits 6 \
    --n-repeats 1 \
    --state-vector \
    --hpc \
    2>&1 | tee "${PROJECT_ROOT}/logs/slurm/p3_qks_n5000_detail.log"

# 3. Rename new outputs to _n5000-suffixed names (keep canonical names untouched)
if [ -f "${RESULTS_DIR}/p3_qks_benchmark.csv" ]; then
    mv "${RESULTS_DIR}/p3_qks_benchmark.csv" "${RESULTS_DIR}/p3_qks_benchmark_n5000.csv"
    echo "  Moved new output → p3_qks_benchmark_n5000.csv"
fi
if [ -f "${RESULTS_DIR}/p3_qks_benchmark.csv.gz" ]; then
    mv "${RESULTS_DIR}/p3_qks_benchmark.csv.gz" "${RESULTS_DIR}/p3_qks_benchmark_n5000.csv.gz"
fi
if [ -f "${RESULTS_DIR}/p3_qks_summary.txt" ]; then
    mv "${RESULTS_DIR}/p3_qks_summary.txt" "${RESULTS_DIR}/p3_qks_summary_n5000.txt"
    echo "  Moved new output → p3_qks_summary_n5000.txt"
fi

echo ""
echo "=== Completed at $(date) ==="
echo "Results: ${RESULTS_DIR}/p3_qks_benchmark_n5000.csv"
echo "Summary: ${RESULTS_DIR}/p3_qks_summary_n5000.txt"
