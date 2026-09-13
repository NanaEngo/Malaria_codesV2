#!/bin/bash
#SBATCH --job-name=p5_replic
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=06:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --output=logs/p5_replication_%j.log
#SBATCH --error=logs/p5_replication_%j.err
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery
python scripts/p5_replication_verification.py
