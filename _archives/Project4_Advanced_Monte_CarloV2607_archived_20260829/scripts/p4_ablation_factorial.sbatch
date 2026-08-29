#!/bin/bash
#SBATCH --job-name=p4_ablation
#SBATCH --output=logs/slurm/p4_ablation_%A_%a.log
#SBATCH --error=logs/slurm/p4_ablation_%A_%a.err
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --array=0-31%8

set -euo pipefail

# ── Error trap ─────────────────────────────────────────────────────────
err_handler() {
  echo "ERROR: Task ${SLURM_ARRAY_TASK_ID:-?} failed with exit code $1" >&2
  exit "$1"
}
trap 'err_handler $?' ERR

# ── Threading (respect --cpus-per-task=4) ──────────────────────────────
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4

# ── Robust conda activation (works in non-interactive SLURM shells) ────
if [ -d "${HOME}/miniforge3" ]; then
  CONDA_BASE="${HOME}/miniforge3"
elif [ -d "${HOME}/miniconda3" ]; then
  CONDA_BASE="${HOME}/miniconda3"
else
  echo "ERROR: No conda installation found in ${HOME}" >&2
  exit 1
fi
source "${CONDA_BASE}/etc/profile.d/conda.sh"
set +u
conda activate malaria_md
set -u

# ── Project paths (hard-coded: robust under SLURM temp copy) ─────────
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"
SCRIPT_DIR="${PROJECT_DIR}/scripts"
cd "${SCRIPT_DIR}"

# Ensure log directory exists before SLURM tries to write to it
mkdir -p "${PROJECT_DIR}/logs/slurm"

# ── Run 2^5 factorial generator for this ConfigID (5 replicates each) ─
# M2 (2026-08-03): previously called `p4_mcts_ablation.py --array-id` which
# is the vocab-ANALYSIS script (no such flag) — the factorial generator was
# lost. Reconstructed generator: `p4_mcts_factorial_run.py` (same 5-factor
# binary design, LSB first). Appends one row per replicate to the config CSV.
echo "Starting array job ${SLURM_ARRAY_TASK_ID} on $(hostname) at $(date -u -Iseconds)"
for REP in 0 1 2 3 4; do
  python p4_mcts_factorial_run.py \
    --array-id "${SLURM_ARRAY_TASK_ID}" \
    --replicate "${REP}" \
    --n-iterations 200 \
    --max-steps 8 \
    --output "${PROJECT_DIR}/results/ablation/p4_ablation_config_${SLURM_ARRAY_TASK_ID}.csv"
done
echo "Finished array job ${SLURM_ARRAY_TASK_ID} at $(date -u -Iseconds)"
