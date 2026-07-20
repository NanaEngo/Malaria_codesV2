#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P4 QMC — Array job for preparing Quantum Monte Carlo inputs
#
# Usage:
#   sbatch --array=0-19%8 \
#     --export=SMILES_FILE=/path/to/candidates.csv,CHUNK_SIZE=10,SKIP_HEADER=1 \
#     scripts/p4_qmc_array.sbatch
#
# Each array task processes a chunk of SMILES from the input CSV and
# writes QMC input directories under results/qmc_inputs/.
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_qmc
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_qmc_%a_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/logs/slurm/p4_qmc_%a_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=01:00:00
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
RESULTS_DIR="${PROJECT_DIR}/results"

mkdir -p "${RESULTS_DIR}/qmc_inputs" "${PROJECT_DIR}/logs/slurm"

# ── Configuration (override via --export) ────────────────────────────
SMILES_FILE="${SMILES_FILE:-${PROJECT_DIR}/data/candidates.csv}"
CHUNK_SIZE="${CHUNK_SIZE:-10}"
SKIP_HEADER="${SKIP_HEADER:-1}"
METHOD="${METHOD:-dft}"
BASIS="${BASIS:-cc-pVTZ}"

ID=${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}

# Compute zero-based line range for this task
START=$((ID * CHUNK_SIZE + SKIP_HEADER))
END=$((START + CHUNK_SIZE - 1))

echo "═══ P4 QMC — Task ${ID} ═══"
echo "  SMILES file: ${SMILES_FILE}"
echo "  Chunk:       lines ${START}-${END}"
echo "  Skip header: ${SKIP_HEADER}"
echo "  Method:      ${METHOD}"
echo "  Basis:       ${BASIS}"
echo "  Host:        $(hostname)"
echo "  Start:       $(date -u -Iseconds)"

# ── Validate input file ─────────────────────────────────────────────
if [ ! -f "${SMILES_FILE}" ]; then
  echo "ERROR: SMILES file not found: ${SMILES_FILE}" >&2
  exit 1
fi

# ── Extract chunk of SMILES ────────────────────────────────────────
# Read the requested lines into a bash array, then join with spaces for
# the Python argparse nargs="+" argument.
mapfile -t SMILES_ARRAY < <(sed -n "${START},${END}p" "${SMILES_FILE}" 2>/dev/null || true)

if [ ${#SMILES_ARRAY[@]} -eq 0 ]; then
  echo "WARNING: No SMILES found for task ${ID} (lines ${START}-${END}); exiting cleanly."
  exit 0
fi

# ── Run QMC input preparation ──────────────────────────────────────
"${PYTHON}" "${PROJECT_DIR}/scripts/p4_qmc_prepare.py" \
  --smiles "${SMILES_ARRAY[@]}" \
  --output-dir "${RESULTS_DIR}/qmc_inputs/task_${ID}" \
  --method "${METHOD}" \
  --basis "${BASIS}"

echo "═══ Task ${ID} complete: $(date -u -Iseconds) ═══"
