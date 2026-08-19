#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P4 Novelty N2 — Selection-mode ablation (scalar proxy vs ParetoPUCT)
#
# Each array task runs Pareto MCTS with a fixed selection mode and seed.
# Mode is chosen via --export=SELECTION_MODE=proxy|pareto.
# Outputs go to results/pareto/n2_{mode}/p4_pareto_seed_{seed}.csv so the
# two modes never overwrite each other.
#
# Usage:
#   sbatch --array=0-4%5 --export=SELECTION_MODE=proxy,  N_ITERATIONS=700 scripts/p4_novelty_n2.sbatch
#   sbatch --array=0-4%5 --export=SELECTION_MODE=pareto, N_ITERATIONS=700 scripts/p4_novelty_n2.sbatch
#
# Merge afterwards:
#   python3 scripts/p4_merge_pareto_fronts.py --input results/pareto/n2_proxy
#   python3 scripts/p4_merge_pareto_fronts.py --input results/pareto/n2_pareto
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_n2
#SBATCH --array=0-4%5
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_n2_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_n2_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail
err_handler() { echo "ERROR: task ${SLURM_ARRAY_TASK_ID} exit ${1}" >&2; exit "${1}"; }
trap 'err_handler $?' ERR

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"
SELECTION_MODE="${SELECTION_MODE:?SELECTION_MODE required (proxy|pareto)}"
N_ITERATIONS="${N_ITERATIONS:-700}"
MAX_STEPS="${MAX_STEPS:-10}"
FRAGMENT_SET="${FRAGMENT_SET:-medium}"
INITIAL_SMILES="${INITIAL_SMILES:-c1ccccc1}"

RESULTS_DIR="${PROJECT_DIR}/results/pareto/n2_${SELECTION_MODE}"
mkdir -p "${RESULTS_DIR}" "${PROJECT_DIR}/logs/slurm"

SEED="${SLURM_ARRAY_TASK_ID:?}"
OUT_CSV="${RESULTS_DIR}/p4_pareto_seed_${SEED}.csv"

echo "═══ P4 N2 — seed=${SEED} mode=${SELECTION_MODE} it=${N_ITERATIONS} ═══"
"${PYTHON}" "${PROJECT_DIR}/scripts/p4_mcts_pareto_run.py" \
  --initial-smiles "${INITIAL_SMILES}" \
  --max-steps "${MAX_STEPS}" \
  --n-iterations "${N_ITERATIONS}" \
  --seed "${SEED}" \
  --fragment-set "${FRAGMENT_SET}" \
  --c-puct 5.0 \
  --policy-temperature 0.8 \
  --selection-mode "${SELECTION_MODE}" \
  --output-csv "${OUT_CSV}"
echo "═══ Task ${SEED} done: $(date -u -Iseconds) ═══"
