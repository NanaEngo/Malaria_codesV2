#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P4 MCTS+RL — Array job for molecular generation
#
# Usage:
#   sbatch --array=0-99%16 \
#     --export=INITIAL_SMILES="C",MAX_STEPS=10,N_ITERATIONS=500 \
#     scripts/p4_mcts_array.sbatch
#
# Each array task runs an independent MCTS search with a unique seed.
# Results are written per-task and can be merged post-hoc.
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_mcts
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_mcts_%a_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_mcts_%a_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00
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

# ── Environment ─────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"
RESULTS_DIR="${PROJECT_DIR}/results/mcts"

mkdir -p "${RESULTS_DIR}" "${PROJECT_DIR}/logs/slurm"

# ── Configuration (override via --export) ────────────────────────────
INITIAL_SMILES="${INITIAL_SMILES:-C}"
MAX_STEPS="${MAX_STEPS:-10}"
N_ITERATIONS="${N_ITERATIONS:-100}"

# Unique seed per array task for independent searches
SEED="${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}"
OUT_CSV="${RESULTS_DIR}/p4_mcts_seed_${SEED}.csv"

echo "═══ P4 MCTS+RL — Task ${SEED} ═══"
echo "  Initial SMILES: ${INITIAL_SMILES}"
echo "  Max steps:      ${MAX_STEPS}"
echo "  Iterations:     ${N_ITERATIONS}"
echo "  Seed:           ${SEED}"
echo "  Host:           $(hostname)"
echo "  Start:          $(date -u -Iseconds)"

# ── Run MCTS search ─────────────────────────────────────────────────
"${PYTHON}" "${PROJECT_DIR}/scripts/p4_mcts_run.py" \
  --initial-smiles "${INITIAL_SMILES}" \
  --max-steps "${MAX_STEPS}" \
  --n-iterations "${N_ITERATIONS}" \
  --seed "${SEED}" \
  --output-csv "${OUT_CSV}"

echo "═══ Task ${SEED} complete: $(date -u -Iseconds) ═══"
