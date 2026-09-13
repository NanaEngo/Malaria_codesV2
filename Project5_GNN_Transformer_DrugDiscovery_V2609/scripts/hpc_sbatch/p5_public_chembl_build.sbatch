#!/bin/bash
# P5 — Build public ChEMBL antimalarial benchmark dataset (action 4).
#SBATCH --job-name=p5_chembl_build
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --output=logs/p5_chembl_build_%j.log
#SBATCH --error=logs/p5_chembl_build_%j.err

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery
mkdir -p logs

python scripts/p5_public_malaria_chembl.py
echo "BUILD_EXIT=$?"
