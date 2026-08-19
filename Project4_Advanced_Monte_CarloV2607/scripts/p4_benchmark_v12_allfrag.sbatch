#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P4 Benchmark v12 — ALL fragments (2026-08-10)
#
# Re-run of v12 with FRAGMENT_SET=all (80 fragments vs 37 in medium).
# Hypothesis: the medium vocabulary creates a flat reward landscape where
# Random already covers the space. All-fragments should increase landscape
# complexity and give MCTS room to demonstrate tree-search advantages.
#
# Same MCTS config as v12: c_PUCT=5.0, ν=0.01, T=0.8, ScafVAE policy.
# Same reward: v12 — MPO/docking/SYBA/SA + ACTIVITY (0.10).
#
# Output: results/benchmark_v12_allfrag/
# Usage:
#   sbatch --array=0-19%8 scripts/p4_benchmark_v12_allfrag.sbatch
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_bench_v12a
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

err_handler() {
  local exit_code="$1"
  echo "ERROR: Task ${SLURM_ARRAY_TASK_ID} failed with exit code ${exit_code}" >&2
  exit "${exit_code}"
}
trap 'err_handler $?' ERR

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

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

PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"
SCRIPT_DIR="${PROJECT_DIR}/scripts"
PYTHON="${CONDA_BASE}/envs/malaria_md/bin/python"
RESULTS_DIR="${PROJECT_DIR}/results/benchmark_v12_allfrag"

mkdir -p "${RESULTS_DIR}" "${PROJECT_DIR}/logs/slurm"

_LOG_PATH="${PROJECT_DIR}/logs/slurm/p4_bench_v12a_${SLURM_ARRAY_TASK_ID:-unknown}_${SLURM_JOB_ID}.log"
exec > "${_LOG_PATH}" 2>&1

N_ITERATIONS="${N_ITERATIONS:-1000}"
GA_POPULATION="${GA_POPULATION:-50}"
GA_GENERATIONS="${GA_GENERATIONS:-20}"
MAX_STEPS="${MAX_STEPS:-10}"
INITIAL_SMILES="${INITIAL_SMILES:-C}"
FRAGMENT_SET="all"

SEED="${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}"
OUT_CSV="${RESULTS_DIR}/p4_benchmark_seed_${SEED}.csv"
OUT_MOL="${RESULTS_DIR}/p4_benchmark_molecules_seed_${SEED}.csv"

echo "═══ P4 Benchmark v12 ALL-fragments — Task ${SEED} ═══"
echo "  MCTS config: c_PUCT=5.0, ν=0.01, T=0.8, ScafVAE policy"
echo "  Reward:      v12 — MPO/docking/SYBA/SA + ACTIVITY (0.10)"
echo "  Fragment set: all (80 fragments)"
echo "  N_iterations:  ${N_ITERATIONS}"
echo "  GA:            ${GA_POPULATION} × ${GA_GENERATIONS}"
echo "  Max steps:     ${MAX_STEPS}"
echo "  Seed:          ${SEED}"
echo "  Host:          $(hostname)"
echo "  Start:         $(date -u -Iseconds)"

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
  --latex-table "${RESULTS_DIR}/p4_benchmark_table_seed_${SEED}.tex" \
  --molecules-out "${OUT_MOL}" \
  2>&1

echo "═══ Task ${SEED} complete: $(date -u -Iseconds) ═══"
