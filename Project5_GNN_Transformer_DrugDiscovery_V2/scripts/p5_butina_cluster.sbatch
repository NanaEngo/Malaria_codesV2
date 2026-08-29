#!/bin/bash
#SBATCH --job-name=p5_butina
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=2-00:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2/results/butina_cluster_20260829/slurm_%j.out
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2/results/butina_cluster_20260829/slurm_%j.err

set -eo pipefail
ROOT=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2
cd "$ROOT"
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

mkdir -p results/butina_cluster_20260829

python -u scripts/p5_butina_cluster.py --device cuda 2>&1 | tee results/butina_cluster_20260829/run.log
