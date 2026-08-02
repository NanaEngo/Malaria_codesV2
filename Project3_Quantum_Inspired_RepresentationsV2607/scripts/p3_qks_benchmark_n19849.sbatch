#!/bin/bash
#SBATCH --job-name=p3_qks_n19849
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --partition=production
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qks_n19849_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qks_n19849_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL

set -euo pipefail
export PYTHONUNBUFFERED=1

# ─────────────────────────────────────────────────────────────────────────────
# P3 QKS standalone benchmark, n=19,849 (FULL LIBRARY, 5-fold CV)
#   p3_qks_benchmark.py --n-mols 19849
#
# BMAD v51 (Aug 1, 2026): C3 fix + optimal params. The canonical quantum
# hyperparameters are now n_qubits=6, n_repeats=1 (Phase-2 winning combo,
# p3_quantum_params_sweep.csv), passed explicitly below. One StandardScaler
# fit on TRAIN is applied to BOTH train and test kernels (C3), so QK, RBF and
# linear baselines live in the same Hilbert-space embedding.
#
# BMAD v50 (July 31, 2026): Phase 3 RESTORED. The state-vector kernel (~1000×
# faster than pairwise) makes the full-library QKS tractable (~2.7 h at 32 cores;
# UMAP fit on 15,879×2048 is now the bottleneck ~19 min/fold; kernel memory
# 2.5 GB/fold within 64 GB). Table 4 kernel comparison will be reported at the
# same n as the canonical classical benchmark (§3.4).
#
# Previous decision (v47) dropped n=19,849 as prohibitive (~100 h+ single-core
# pairwise). This sbatch supersedes that assessment.
#
# The script writes fixed output names (p3_qks_benchmark.csv /
#    p3_qks_summary.txt). Canonical n=500 / n=5,000 files are preserved below by
#    copying them to _n500 / _n5000-suffixed names BEFORE the run, then moving the
#    new outputs to _n19849-suffixed names AFTER, leaving the canonical names
#    untouched.
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_ROOT}/results"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

echo "=== P3 QKS Standalone Benchmark n=19,849 ==="
echo "Date: $(date)"
echo "Node: $(hostname)"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Project root: $PROJECT_ROOT"

mkdir -p "${PROJECT_ROOT}/logs/slurm"

# 1. Preserve canonical n=500 / n=5,000 files (no-op if already preserved)
cp -n "${RESULTS_DIR}/p3_qks_benchmark.csv"  "${RESULTS_DIR}/p3_qks_benchmark_n500.csv"  || echo "  [skip] n500 csv already preserved"
cp -n "${RESULTS_DIR}/p3_qks_summary.txt"    "${RESULTS_DIR}/p3_qks_summary_n500.txt"    || echo "  [skip] n500 summary already preserved"
cp -n "${RESULTS_DIR}/p3_qks_benchmark.csv"  "${RESULTS_DIR}/p3_qks_benchmark_n5000.csv" || echo "  [skip] n5000 csv already preserved"
cp -n "${RESULTS_DIR}/p3_qks_summary.txt"    "${RESULTS_DIR}/p3_qks_summary_n5000.txt"   || echo "  [skip] n5000 summary already preserved"
echo "  Preserved canonical n=500 / n=5,000 results as *_n500 / *_n5000"

# 2. Run standalone QKS benchmark on the full library
cd "${PROJECT_ROOT}"
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK

$PYTHON scripts/p3_qks_benchmark.py \
    --n-mols 19849 \
    --n-qubits 6 \
    --n-repeats 1 \
    --state-vector \
    --hpc \
    2>&1 | tee "${PROJECT_ROOT}/logs/slurm/p3_qks_n19849_detail.log"

# 3. Rename new outputs to _n19849-suffixed names (keep canonical names untouched)
if [ -f "${RESULTS_DIR}/p3_qks_benchmark.csv" ]; then
    mv "${RESULTS_DIR}/p3_qks_benchmark.csv" "${RESULTS_DIR}/p3_qks_benchmark_n19849.csv"
    echo "  Moved new output → p3_qks_benchmark_n19849.csv"
fi
if [ -f "${RESULTS_DIR}/p3_qks_benchmark.csv.gz" ]; then
    mv "${RESULTS_DIR}/p3_qks_benchmark.csv.gz" "${RESULTS_DIR}/p3_qks_benchmark_n19849.csv.gz"
fi
if [ -f "${RESULTS_DIR}/p3_qks_summary.txt" ]; then
    mv "${RESULTS_DIR}/p3_qks_summary.txt" "${RESULTS_DIR}/p3_qks_summary_n19849.txt"
    echo "  Moved new output → p3_qks_summary_n19849.txt"
fi

echo ""
echo "=== Completed at $(date) ==="
echo "Results: ${RESULTS_DIR}/p3_qks_benchmark_n19849.csv"
echo "Summary: ${RESULTS_DIR}/p3_qks_summary_n19849.txt"
