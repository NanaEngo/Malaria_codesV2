#!/bin/bash
#SBATCH --job-name=p3_rrs_expansion
#SBATCH --output=logs/slurm/p3_rrs_expansion_%j.log
#SBATCH --error=logs/slurm/p3_rrs_expansion_%j.err
#SBATCH --time=04:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --array=0-3

# P3 H₁-RRS Expansion: Compute RRS for 200+ compounds
# to expand the headline correlation from n=14 to n≥30
#
# Usage: sbatch p3_rrs_expansion.sbatch
#
# This script:
# 1. Loads the Tartarus docking results (19,913 compounds × 3 targets)
# 2. Filters to compounds with valid docking scores across ≥2 targets
# 3. Computes RRS for 200+ compounds across 4 resistance classes
# 4. Outputs p3_rrs_expanded.csv for H₁-RRS re-analysis

set -euo pipefail

# Environment
CONDA_ENV="malaria_md"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Task-specific parameters
TASK_ID=${SLURM_ARRAY_TASK_ID}
N_MOLS=50  # compounds per task (4 tasks × 50 = 200 total)
START_IDX=$((TASK_ID * N_MOLS))
END_IDX=$((START_IDX + N_MOLS))

echo "=== P3 RRS Expansion ==="
echo "Task ID: $TASK_ID"
echo "Processing compounds $START_IDX to $END_IDX"
echo "Conda env: $CONDA_ENV"
echo "Start time: $(date)"
echo "Node: $(hostname)"
echo ""

# Run the Python expansion script
python3 "$SCRIPT_DIR/p3_rrs_expansion.py" \
    --start-idx "$START_IDX" \
    --end-idx "$END_IDX" \
    --output-dir "$PROJECT_ROOT/results/p3_rrs_expansion" \
    --task-id "$TASK_ID"

echo ""
echo "=== Task $TASK_ID completed at $(date) ==="
