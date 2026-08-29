#!/bin/bash
#SBATCH --job-name=p4_qmc
#SBATCH --output=../logs/slurm/p4_qmc_%A_%a.log
#SBATCH --error=../logs/slurm/p4_qmc_%A_%a.err
#SBATCH --partition=production
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --array=0-3%2

set -euo pipefail

# ── Error trap ─────────────────────────────────────────────────────────
err_handler() {
  echo "ERROR: Task ${SLURM_ARRAY_TASK_ID:-?} failed with exit code $1" >&2
  exit "$1"
}
trap 'err_handler $?' ERR

# ── Threading (respect --cpus-per-task=8, PySCF uses OpenMP) ──────────
export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8

# ── Robust conda activation (absolute paths — conda is not on PATH in batch) ──
CONDA_BASE="/home/nanaengo/miniforge3"
source "${CONDA_BASE}/etc/profile.d/conda.sh"
set +u && conda activate malaria_md && set -u
PYTHON="${CONDA_BASE}/envs/malaria_md/bin/python"

# ── Portable paths ─────────────────────────────────────────────────
PROJECT_DIR="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SCRIPT_DIR="${PROJECT_DIR}/scripts"
cd "${SCRIPT_DIR}"
mkdir -p "${PROJECT_DIR}/logs/slurm"

# Run QMC pipeline for specific Pareto candidate
echo "Starting QMC Tier 1/2 for candidate ${SLURM_ARRAY_TASK_ID} on $(hostname) at $(date -u -Iseconds)"
"${PYTHON}" p4_qmc_pipeline.py --array-id "${SLURM_ARRAY_TASK_ID}"
echo "Finished QMC Tier 1/2 for candidate ${SLURM_ARRAY_TASK_ID} at $(date -u -Iseconds)"
