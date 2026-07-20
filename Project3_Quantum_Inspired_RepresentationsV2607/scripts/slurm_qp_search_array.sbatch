#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# Quantum Parameter Search — PARALLEL Array (60 tasks on 48 CPUs)
#
# Instead of 1 sequential job taking ~8 hours (47/48 CPUs idle),
# this array runs all 60 combos in parallel (~20 min total).
#
# Usage:
#   sbatch --array=0-59%48 /tmp/slurm_qp_search_array.sbatch
#
# Mapping: array_id → (bond_dim, n_repeats, n_kpca)
#   bond_dim  = [4, 6, 8]     → array_id // 20
#   n_repeats = [1, 2, 3, 4, 6] → (array_id // 4) % 5
#   n_kpca    = [5, 10, 20, 30] → array_id % 4
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p3_qp_array
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qp_array_%a_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qp_array_%a_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

# ── Environment ─────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_DIR}/results"

# ── Map array task ID → parameters ──────────────────────────────────
BD_LIST=(4 6 8)
NR_LIST=(1 2 3 4 6)
NK_LIST=(5 10 20 30)

ID=${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}

BD_IDX=$((ID / 20))
NR_IDX=$(((ID / 4) % 5))
NK_IDX=$((ID % 4))

BD=${BD_LIST[$BD_IDX]}
NR=${NR_LIST[$NR_IDX]}
NK=${NK_LIST[$NK_IDX]}

echo "═══ QP Array Task ${ID} ═══"
echo "  bond_dim=${BD}  n_repeats=${NR}  n_kpca=${NK}"
echo "  Host: $(hostname)"
echo "  CPUs: $(nproc)"
echo "  Mem:  $(free -h | grep Mem)"
echo "  Start: $(date -u -Iseconds)"

# ── Run evaluation for this single combination ──────────────────────
# The p3_quantum_param_search.py script accepts single values as
# comma-separated lists of length 1. It will run only 1 combo and
# write to the shared CSV. To avoid race conditions with concurrent
# writes across the array, each task writes to its own output file,
# and a final merge step combines them.
#
# We call the script with --hpc to enable parallel fold evaluation
# (n_jobs = available CPUs on the compute node).
"${PYTHON}" "${PROJECT_DIR}/scripts/p3_quantum_param_search.py" \
  --bond-dim "${BD}" \
  --n-repeats "${NR}" \
  --n-kpca "${NK}" \
  --n-mols 200 \
  --hpc

# ── Rename output to per-task to avoid overwrites from other tasks ──
# Each task writes to the shared CSV; rename to unique per-task file.
if [ -f "${RESULTS_DIR}/p3_quantum_params_sweep.csv" ]; then
  mv -f "${RESULTS_DIR}/p3_quantum_params_sweep.csv" \
        "${RESULTS_DIR}/p3_qp_sweep_array_${ID}.csv"
fi

echo "═══ Task ${ID} complete: $(date -u -Iseconds) ═══"
