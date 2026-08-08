#!/bin/bash
#SBATCH --job-name=p3_qks_extval
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --partition=production
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qks_extval_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qks_extval_%j.err

set -euo pipefail
export PYTHONUNBUFFERED=1

# ─────────────────────────────────────────────────────────────────────────────
# P3 QKS EXTERNAL VALIDATION on the public ChEMBL malaria IC50/EC50 dataset
# (22,447 molecules) — mirrors the canonical QKS benchmark (job 12700: 6-qubit
# IQPEmbedding, n_repeats=1, state-vector kernel, C3 train-only StandardScaler).
#
# Env fix (Aug 8, 2026): malaria_md was inconsistent (jax 0.10.2 requires
# numpy>=2.0, env shipped numpy 1.26.4 → `import pennylane` crashed). numpy
# upgraded to 2.4.6 to restore the documented state (AGENTS.md: JAX 0.10.2
# CUDA) — verified: pennylane 0.45.1 imports, full stack OK.
#
# Thread-control: OMP/MKL/OPENBLAS=1 with 32 joblib workers (loky) — proven
# ~2x faster than letting each worker oversubscribe the node (see
# p3_external_validation.sbatch fix, job 12860).
#
# Optional trailing arg: --limit N  (smoke test) — sbatch CLI overrides --time.
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_ROOT}/results"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

mkdir -p "${PROJECT_ROOT}/logs/slurm"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

cd "${PROJECT_ROOT}"

# Parse optional trailing args passed by sbatch (e.g. `sbatch x.sbatch --limit 150`
# arrives as positional "--limit" "150").
LIMIT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --limit) LIMIT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [ -n "$LIMIT" ]; then
    echo "=== P3 QKS EXTERNAL VALIDATION (smoke: --limit $LIMIT) ==="
    $PYTHON scripts/p3_qks_external_validation.py \
        --n-jobs 32 \
        --block-size 200 \
        --checkpoint "${RESULTS_DIR}/p3_external_validation_qks_ckpt.json" \
        --limit "$LIMIT"
else
    echo "=== P3 QKS EXTERNAL VALIDATION (full 22,447 panel) ==="
    $PYTHON scripts/p3_qks_external_validation.py \
        --n-jobs 32 \
        --block-size 200 \
        --checkpoint "${RESULTS_DIR}/p3_external_validation_qks_ckpt.json"
fi

echo ""
echo "=== Completed at $(date) ==="
echo "Results: ${RESULTS_DIR}/p3_external_validation_qks_benchmark.csv"
echo "Summary: ${RESULTS_DIR}/p3_external_validation_qks_summary.txt"
echo "Report:  ${RESULTS_DIR}/p3_external_validation_qks_report.json"
