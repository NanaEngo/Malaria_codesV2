#!/bin/bash
#SBATCH --job-name=p5_ext_rf
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=2-00:00:00
#SBATCH --gpus=0
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2/results/extended_campaign_20260825/thresholds_%j.out
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2/results/extended_campaign_20260825/thresholds_%j.err

set -eo pipefail
ROOT=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2
cd "$ROOT"
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
python -u scripts/p5_extended_campaign.py thresholds --n-estimators 500
