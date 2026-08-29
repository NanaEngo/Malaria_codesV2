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
# Note: Defaults to the 'medium' fragment subset to reduce RDKit valence/kekulization
# errors. Override with --export=FRAGMENT_SET=all (or aromatic_only/minimal).
#
# Output:
#   results/benchmark/p4_benchmark_seed_N.csv  (per-task)
#   results/benchmark/p4_benchmark_merged.csv   (merged, after last task)
#   results/benchmark/p4_benchmark_table.tex    (LaTeX table)
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_benchmark
#SBATCH --array=0-19%8
#SBATCH --output=%x_%j.log
#SBATCH --error=%x_%j.err
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

# ── Robust conda activation ───────────────────────────────────
# ── Robust conda activation (with fallback) ───────────────────────────
if [ -d "${HOME}/miniforge3" ]; then
  CONDA_BASE="${HOME}/miniforge3"
elif [ -d "${HOME}/miniconda3" ]; then
  CONDA_BASE="${HOME}/miniconda3"
else
  echo "ERROR: No conda installation found in ${HOME}" >&2
  exit 1
fi
source "${CONDA_BASE}/etc/profile.d/conda.sh"
set +u && conda activate malaria_md && set -u

# ── Project paths (hard-coded: robust under SLURM temp copy) ─────────
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"
SCRIPT_DIR="${PROJECT_DIR}/scripts"
PYTHON="${CONDA_BASE}/envs/malaria_md/bin/python"
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
FRAGMENT_SET="${FRAGMENT_SET:-medium}"

SEED="${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}"
OUT_CSV="${RESULTS_DIR}/p4_benchmark_seed_${SEED}.csv"
# Each task writes its own .tex to avoid race conditions; merge post-hoc
OUT_TEX="${RESULTS_DIR}/p4_benchmark_table_seed_${SEED}.tex"

echo "═══ P4 Benchmark — Task ${SEED} ═══"
echo "  N_iterations:  ${N_ITERATIONS}"
echo "  GA:            ${GA_POPULATION} × ${GA_GENERATIONS}"
echo "  Max steps:     ${MAX_STEPS}"
echo "  Seed:          ${SEED}"
echo "  Host:          $(hostname)"
echo "  Start:         $(date -u -Iseconds)"

# ── Run benchmark (single seed) ──────────────────────────────────────
"${PYTHON}" "${SCRIPT_DIR}/p4_mcts_benchmark.py" \
  --n-iterations "${N_ITERATIONS}" \
  --ga-population "${GA_POPULATION}" \
  --ga-generations "${GA_GENERATIONS}" \
  --n-seeds 1 \
  --seed "${SEED}" \
  --initial-smiles "${INITIAL_SMILES}" \
  --max-steps "${MAX_STEPS}" \
  --fragment-set "${FRAGMENT_SET}" \
  --output "${OUT_CSV}" \
  --latex-table "${OUT_TEX}" \
  2>&1

echo "═══ Task ${SEED} complete: $(date -u -Iseconds) ═══"
