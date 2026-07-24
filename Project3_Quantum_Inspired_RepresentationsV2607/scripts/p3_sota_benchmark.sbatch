#!/bin/bash
#SBATCH --job-name=p3_sota_benchmark
#SBATCH --output=../logs/slurm/p3_sota_benchmark_%j.log
#SBATCH --error=../logs/slurm/p3_sota_benchmark_%j.err
#SBATCH --time=01:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --ntasks=1

set -euo pipefail

# Environment
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate malaria_md

echo "=== P3 SOTA Benchmark ==="
echo "Date: $(date)"
echo "Node: $(hostname)"
echo "Project root: $PROJECT_ROOT"

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/logs/slurm"

# Labels CSV: must have 'smiles' + any of activity/label/true_label columns
# NOTE: p3_mc_uncertainty.csv has only 100 rows (pilot run). For production
# results, use a larger CSV with 500+ molecules (e.g., P1 Ersilia predictions
# merged with TDA fingerprints).
LABELS_CSV="$PROJECT_ROOT/results/p3_mc_uncertainty.csv"
if [ ! -f "$LABELS_CSV" ]; then
    echo "WARNING: Labels CSV not found at $LABELS_CSV — will use random labels"
fi

# Run benchmark (max-mols=2000 for SVM compatibility)
cd "$SCRIPT_DIR"
python3 p3_sota_benchmark.py \
    --n-folds 5 \
    --max-mols 2000 \
    --labels-csv "$LABELS_CSV" \
    --output-csv "$PROJECT_ROOT/results/p3_sota_benchmark.csv" \
    2>&1 | tee "$PROJECT_ROOT/logs/slurm/p3_sota_benchmark_detail.log"

echo ""
echo "=== Completed at $(date) ==="
echo "Results: $PROJECT_ROOT/results/p3_sota_benchmark.csv"
echo "Summary: $PROJECT_ROOT/results/p3_sota_benchmark_summary.txt"
