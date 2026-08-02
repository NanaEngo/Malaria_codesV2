#!/bin/bash
#SBATCH --job-name=p3_sota_full
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_sota_full_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_sota_full_%j.err
#SBATCH --partition=production
#SBATCH --time=06:00:00
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

echo "=== P3 SOTA Benchmark (Full Library) ==="
echo "Date: $(date)"
echo "Node: $(hostname)"
echo "Project root: $PROJECT_ROOT"

# Ensure log directory exists
mkdir -p "${PROJECT_ROOT}/logs/slurm"

# Labels CSV: 19,849 molecules (eos80ch activity + TDA FP merge)
LABELS_CSV="${PROJECT_ROOT}/results/p3_labels_production.csv"
if [ ! -f "$LABELS_CSV" ]; then
    echo "ERROR: Labels CSV not found at $LABELS_CSV" >&2
    exit 1
fi

# Run benchmark:
#   --rf-max-mols 0 = RF runs on ALL 19,849 molecules (O(N log N), fast)
#   --svm-max-mols 5000 = SVM runs on stratified subsample (O(N^2), feasible)
# Output to versioned CSV to preserve n=5000 pilot results
cd "$SCRIPT_DIR"
python3 p3_sota_benchmark.py \
    --n-folds 5 \
    --rf-max-mols 0 \
    --svm-max-mols 5000 \
    --labels-csv "$LABELS_CSV" \
    --output-csv "${PROJECT_ROOT}/results/p3_sota_benchmark_full.csv" \
    2>&1 | tee "${PROJECT_ROOT}/logs/slurm/p3_sota_full_detail.log"

echo ""
echo "=== Completed at $(date) ==="
echo "Results: ${PROJECT_ROOT}/results/p3_sota_benchmark_full.csv"
echo "Summary: ${PROJECT_ROOT}/results/p3_sota_benchmark_full_summary.txt"
