#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P4 Pareto MCTS — Array job for multi-objective Pareto front generation
#
# Regenerates the Pareto front from ACTUAL Pareto MCTS runs (NOT synthetic
# data). Each array task runs an independent Pareto MCTS search with a
# unique seed and outputs its Pareto front of non-dominated solutions.
#
# Fragment set defaults to 'medium' (valence-filtered) for consistency with
# the benchmark and standard MCTS arrays. Override via --export=FRAGMENT_SET=all.
#
# After completion, merge all per-seed CSVs with:
#   python3 scripts/p4_merge_pareto_fronts.py
#
# Usage:
#   sbatch --array=0-19%8 --export=FRAGMENT_SET=medium scripts/p4_pareto_array.sbatch
#
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_pareto
#SBATCH --array=0-19%8
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_pareto_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_pareto_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=08:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

# ── Error trap ───────────────────────────────────────────────────────
err_handler() {
  local exit_code="$1"
  echo "ERROR: Task ${SLURM_ARRAY_TASK_ID} failed with exit code ${exit_code}" >&2
  exit "${exit_code}"
}
trap 'err_handler $?' ERR

# ── Threading ────────────────────────────────────────────────────────
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# ── Environment ─────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"
RESULTS_DIR="${PROJECT_DIR}/results/pareto"

mkdir -p "${RESULTS_DIR}" "${PROJECT_DIR}/logs/slurm"

# ── Log redirect ─────────────────────────────────────────────────────
_LOG_PATH="${PROJECT_DIR}/logs/slurm/p4_pareto_${SLURM_ARRAY_TASK_ID:-unknown}_${SLURM_JOB_ID}.log"
exec > "${_LOG_PATH}" 2>&1

# ── Configuration ───────────────────────────────────────────────────
INITIAL_SMILES="${INITIAL_SMILES:-c1ccccc1}"
MAX_STEPS="${MAX_STEPS:-10}"
N_ITERATIONS="${N_ITERATIONS:-1000}"
FRAGMENT_SET="${FRAGMENT_SET:-medium}"

# Unique seed per array task
SEED="${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}"
OUT_CSV="${RESULTS_DIR}/p4_pareto_seed_${SEED}.csv"

echo "═══ P4 Pareto MCTS — Task ${SEED} ═══"
echo "  Initial SMILES:  ${INITIAL_SMILES}"
echo "  Max steps:       ${MAX_STEPS}"
echo "  Iterations:      ${N_ITERATIONS}"
echo "  Seed:            ${SEED}"
echo "  Fragment set:    ${FRAGMENT_SET}"
echo "  Host:            $(hostname)"
echo "  Start:           $(date -u -Iseconds)"

# ── Run Pareto MCTS search ──────────────────────────────────────────
"${PYTHON}" "${PROJECT_DIR}/scripts/p4_mcts_pareto_run.py" \
  --initial-smiles "${INITIAL_SMILES}" \
  --max-steps "${MAX_STEPS}" \
  --n-iterations "${N_ITERATIONS}" \
  --seed "${SEED}" \
  --fragment-set "${FRAGMENT_SET}" \
  --c-puct 5.0 \
  --policy-temperature 0.8 \
  --output-csv "${OUT_CSV}"

echo "═══ Task ${SEED} complete: $(date -u -Iseconds) ═══"
