#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P4 Benchmark — MCTS vs Random vs Greedy vs GA (array job)
#
# Runs the unified benchmark across multiple seeds for statistical
# robustness. Each task runs one seed and writes per-seed CSV results.
#
# Usage:
#   sbatch --array=0-19%8 scripts/p4_benchmark_array.sbatch
#
# Note: Uses 108-fragment vocabulary (same as MCTS array) for fair comparison.
#
# Output:
#   results/benchmark/p4_benchmark_seed_N.csv  (per-task)
#   results/benchmark/p4_benchmark_merged.csv   (merged, after last task)
#   results/benchmark/p4_benchmark_table.tex    (LaTeX table)
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_benchmark
#SBATCH --array=0-19%8
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_benchmark_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_benchmark_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=06:00:00
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

# ── Environment ──────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"
RESULTS_DIR="${PROJECT_DIR}/results/benchmark"

mkdir -p "${RESULTS_DIR}" "${PROJECT_DIR}/logs/slurm"

# ── Log redirect (fix %a→4294967294: use env var instead of %%a) ────
_LOG_PATH="${PROJECT_DIR}/logs/slurm/p4_benchmark_${SLURM_ARRAY_TASK_ID:-unknown}_${SLURM_JOB_ID}.log"
exec > "${_LOG_PATH}" 2>&1

# ── Configuration ────────────────────────────────────────────────────
N_ITERATIONS="${N_ITERATIONS:-1000}"
GA_POPULATION="${GA_POPULATION:-50}"
GA_GENERATIONS="${GA_GENERATIONS:-20}"
MAX_STEPS="${MAX_STEPS:-10}"
INITIAL_SMILES="${INITIAL_SMILES:-C}"

SEED="${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}"
OUT_CSV="${RESULTS_DIR}/p4_benchmark_seed_${SEED}.csv"
OUT_TEX="${RESULTS_DIR}/p4_benchmark_table.tex"

echo "═══ P4 Benchmark — Task ${SEED} ═══"
echo "  N_iterations:  ${N_ITERATIONS}"
echo "  GA:            ${GA_POPULATION} × ${GA_GENERATIONS}"
echo "  Max steps:     ${MAX_STEPS}"
echo "  Seed:          ${SEED}"
echo "  Host:          $(hostname)"
echo "  Start:         $(date -u -Iseconds)"

# ── Run benchmark (single seed) ──────────────────────────────────────
"${PYTHON}" "${PROJECT_DIR}/scripts/p4_mcts_benchmark.py" \
  --n-iterations "${N_ITERATIONS}" \
  --ga-population "${GA_POPULATION}" \
  --ga-generations "${GA_GENERATIONS}" \
  --n-seeds 1 \
  --seed "${SEED}" \
  --initial-smiles "${INITIAL_SMILES}" \
  --max-steps "${MAX_STEPS}" \
  --output "${OUT_CSV}" \
  --latex-table "${OUT_TEX}" \
  2>&1

echo "═══ Task ${SEED} complete: $(date -u -Iseconds) ═══"
