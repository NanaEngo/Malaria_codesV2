#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P4 MCTS+RL — Array job for molecular generation (production)
#
# Uses:
# - Fragment vocabulary selected via FRAGMENT_SET (default: medium, filtered for valence)
# - Real oracles (MPO + docking + SYBA + SA from P1/P2 libraries)
# - 20 independent seeds (n=20 for valid variance, per adversarial audit) per run
#
# Usage:
#   sbatch --array=0-19%8 \
#     --export=INITIAL_SMILES="C",MAX_STEPS=8,N_ITERATIONS=1000,FRAGMENT_SET=medium \
#     scripts/p4_mcts_array.sbatch
#
# Each array task runs an independent MCTS search with a unique seed.
# Results are written per-task and merged post-hoc via p4_mcts_merge.py.
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_mcts
#SBATCH --array=0-19%8
#SBATCH --output=%x_%j.log
#SBATCH --error=%x_%j.err
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

# ── Robust conda activation ───────────────────────────────────────
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
RESULTS_DIR="${PROJECT_DIR}/results/mcts"

mkdir -p "${RESULTS_DIR}" "${PROJECT_DIR}/logs/slurm"

# ── Log redirect (fix %a→4294967294) ────────────────────────────────
_LOG_PATH="${PROJECT_DIR}/logs/slurm/p4_mcts_${SLURM_ARRAY_TASK_ID:-unknown}_${SLURM_JOB_ID}.log"
exec > "${_LOG_PATH}" 2>&1

# ── Configuration (override via --export) ────────────────────────────
INITIAL_SMILES="${INITIAL_SMILES:-C}"
MAX_STEPS="${MAX_STEPS:-8}"
N_ITERATIONS="${N_ITERATIONS:-1000}"
FRAGMENT_SET="${FRAGMENT_SET:-medium}"

# Unique seed per array task for independent searches
SEED="${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}"
OUT_CSV="${RESULTS_DIR}/p4_mcts_seed_${SEED}.csv"
OUT_LOG="${RESULTS_DIR}/p4_mcts_seed_${SEED}.log"

echo "═══ P4 MCTS+RL — Task ${SEED} ═══"
echo "  Initial SMILES:  ${INITIAL_SMILES}"
echo "  Max steps:       ${MAX_STEPS}"
echo "  Iterations:      ${N_ITERATIONS}"
echo "  Fragment set:    ${FRAGMENT_SET}"
echo "  Seed:            ${SEED}"
echo "  Host:            $(hostname)"
echo "  Start:           $(date -u -Iseconds)"

# ── Run MCTS search (ScafVAE policy + real oracles) ─────────────────
"${PYTHON}" "${SCRIPT_DIR}/p4_mcts_run.py" \
  --initial-smiles "${INITIAL_SMILES}" \
  --max-steps "${MAX_STEPS}" \
  --n-iterations "${N_ITERATIONS}" \
  --fragment-set "${FRAGMENT_SET}" \
  --c-puct 1.414 \
  --policy-temperature 0.8 \
  --seed "${SEED}" \
  --output-csv "${OUT_CSV}"

echo "═══ Task ${SEED} complete: $(date -u -Iseconds) ═══"
