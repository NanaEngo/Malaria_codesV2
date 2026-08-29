#!/bin/bash
# sbatch runner for P5 benchmark pipeline (full workflow)
# Usage: sbatch s_products/p5_run_all.sbatch

#SBATCH --job-name=p5_pipeline
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=0
#SBATCH --mail-type=END,FAIL
#SBATCH --output=p5_pipeline_%j.log
#SBATCH --error=p5_pipeline_%j.err

# Activate conda environment
SET_CONDA="source /home/nanaengo/miniforge3/etc/profile.d/conda.sh && conda activate malaria_md"
RUN_CMD="${SET_CONDA}"

set -e

echo "========================================="
echo "P5 Full Pipeline — $(date)"
echo "========================================="

# Activate environment
eval "$SET_CONDA"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${LEFT_CWD:-.}"

# Step 1: Build graphs + DeepChem descriptors
echo "[1/6] Building PyG graphs + DeepChem descriptors..."
$RUN_CMD python scripts/p5_data.py --deepchem --n-jobs 32

# Step 2: Run GNN benchmarks for each model
echo "[2/6] Running GNN benchmarks..."
# NOTE: This will generate CSV files with test_auc results
for model in GCN GIN GAT GIN-FP GIN-TFP GIN-TNE Hybrid-All; do
    echo "  -> Training $model..."
    $RUN_CMD python scripts/p5_benchmark.py --model "$model" --device cuda --epochs 30 || true
done

# Step 3: Run ChemBERTa benchmark
echo "[3/6] Running ChemBERTa fine-tune..."
$RUN_CMD python scripts/p5_chemberta.py --device cuda --epochs 10 || true

# Step 4: Build ensemble
echo "[4/6] Building ensemble..."
$RUN_CMD python scripts/p5_ensemble.py --mode vote --output results/p5_ensemble_results.csv || true

# Step 5: Generate visualizations
echo "[5/6] Generating figures..."
$RUN_CMD python scripts/p5_figure.py --output results/figures/p5_auc_benchmark.png || true

# Step 6: Final summary
echo "[6/6] Pipeline complete."
echo "Results saved to results/"
echo "Figures saved to results/figures/"
echo "Done at $(date)"