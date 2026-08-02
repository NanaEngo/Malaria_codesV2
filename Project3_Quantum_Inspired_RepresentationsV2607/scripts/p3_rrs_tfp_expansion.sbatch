#!/bin/bash
#SBATCH --job-name=p3_rrs_tfp
#SBATCH --output=logs/slurm/p3_rrs_tfp_%j.log
#SBATCH --error=logs/slurm/p3_rrs_tfp_%j.err
#SBATCH --partition=production
#SBATCH --time=04:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --array=0-9

# P3 H1-RRS Definitive Expansion: Compute TFP for 500+ RRS compounds
# (10 tasks × 50 compounds = 500 total)
#
# Usage: sbatch p3_rrs_tfp_expansion.sbatch
#
# This script:
# 1. Loads the 501-compound RRS dataset
# 2. Computes 78-D TFP for compounds lacking topological features
# 3. Outputs per-task CSV files for later merging

set -eo pipefail

# Environment
CONDA_ENV="malaria_md"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"
set -u

PROJECT_ROOT="/home/nanaengo/Malaria_codesV2"
SCRIPT_DIR="$PROJECT_ROOT/Project3_Quantum_Inspired_RepresentationsV2607/scripts"

# Ensure output directories exist
mkdir -p "$PROJECT_ROOT/Project3_Quantum_Inspired_RepresentationsV2607/results"

# Task-specific parameters
TASK_ID=${SLURM_ARRAY_TASK_ID}
N_MOLS=50
START_IDX=$((TASK_ID * N_MOLS))
END_IDX=$((START_IDX + N_MOLS))

echo "=== P3 RRS-TFP Expansion ==="
echo "Task ID: $TASK_ID"
echo "Processing compounds $START_IDX to $END_IDX"
echo "Conda env: $CONDA_ENV"
echo "Start time: $(date)"
echo "Node: $(hostname)"
echo ""

# Run the Python expansion script
python3 "$SCRIPT_DIR/p3_rrs_tfp_expansion.py" \
    --start-idx "$START_IDX" \
    --end-idx "$END_IDX" \
    --task-id "$TASK_ID"

echo ""
echo "=== Task $TASK_ID completed at $(date) ==="
