#!/bin/bash
#SBATCH --job-name=p5_gnn_metrics
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=20G
#SBATCH --time=04:00:00
#SBATCH --output=logs/p5_gnn_metrics_%j.log
#SBATCH --error=logs/p5_gnn_metrics_%j.err
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
export OMP_NUM_THREADS=8
for m in GIN GIN-TFP GIN-TNE; do
  python scripts/p5_benchmark.py --model $m --split scaffold --device cuda --tag _metrics
  python scripts/p5_benchmark.py --model $m --split random   --device cuda --tag _metrics
done
