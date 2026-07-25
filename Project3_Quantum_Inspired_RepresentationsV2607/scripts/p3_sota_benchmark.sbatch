#!/bin/bash
#SBATCH --job-name=p3_sota_benchmark
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_sota_benchmark_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_sota_benchmark_%j.err
#SBATCH --partition=production
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=16
#SBATCH --nodes=1
#SBATCH --ntasks=1

set -eo pipefail

# Hardcode paths — compute-node $0 resolves to slurm spool, not project dir
PROJECT_ROOT="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
SCRIPT_DIR="${PROJECT_ROOT}/scripts"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate malaria_md

echo "=== P3 SOTA Benchmark ==="
echo "Date: $(date)"
echo "Node: $(hostname)"
echo "Project root: $PROJECT_ROOT"

# Ensure log directory exists
mkdir -p "${PROJECT_ROOT}/logs/slurm"

# Labels CSV: must have 'smiles' + any of activity/label/true_label columns
# PRODUCTION: p3_labels_production.csv = 19,849 molecules (eos80ch activity + TDA FP merge)
# Previous pilot: p3_rrs_labels_for_sota.csv had only 77 molecules (unreliable AUC)
LABELS_CSV="${PROJECT_ROOT}/results/p3_labels_production.csv"
if [ ! -f "$LABELS_CSV" ]; then
    echo "ERROR: Labels CSV not found at $LABELS_CSV" >&2
    exit 1
fi

# Run benchmark on n=5000 stratified subsample (SVM kernel O(N^2) limits full-library eval)
cd "$SCRIPT_DIR"
python3 p3_sota_benchmark.py \
    --n-folds 5 \
    --max-mols 5000 \
    --labels-csv "$LABELS_CSV" \
    --output-csv "${PROJECT_ROOT}/results/p3_sota_benchmark.csv" \
    2>&1 | tee "${PROJECT_ROOT}/logs/slurm/p3_sota_benchmark_detail.log"

echo ""
echo "=== Completed at $(date) ==="
echo "Results: ${PROJECT_ROOT}/results/p3_sota_benchmark.csv"
echo "Summary: ${PROJECT_ROOT}/results/p3_sota_benchmark_summary.txt"
