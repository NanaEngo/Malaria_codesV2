#!/bin/bash
# P5 — Light GNN hyperparameter sensitivity (Levier 3).
# Two configs bracket the canonical HIDDEN=128 / DROPOUT=0.1 benchmark on the
# scaffold split: narrower+wetter (64 / 0.2) and wider (256 / 0.1). Same frozen
# 5-fold x 5-seed protocol and epoch budget as the canonical run, so per-seed
# means are directly comparable. Outputs carry the "_sens_*" tag; canonical
# results/checkpoints are never overwritten.
#SBATCH --job-name=p5_gnn_sens
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=logs/p5_gnn_sens_%j.log
#SBATCH --error=logs/p5_gnn_sens_%j.err

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2609
mkdir -p logs

set -e
echo "=== GIN sensitivity: hidden=64 dropout=0.2 ==="
python scripts/p5_benchmark.py --model GIN --split scaffold \
    --device cuda --hidden 64 --dropout 0.2 --tag _sens_h64_d02

echo "=== GIN sensitivity: hidden=256 dropout=0.1 ==="
python scripts/p5_benchmark.py --model GIN --split scaffold \
    --device cuda --hidden 256 --dropout 0.1 --tag _sens_h256_d01

echo "=== P5 GNN sensitivity DONE ==="
