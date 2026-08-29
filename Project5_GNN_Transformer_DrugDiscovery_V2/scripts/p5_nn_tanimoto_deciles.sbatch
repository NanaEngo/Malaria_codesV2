#!/bin/bash
# P5 — #2 NN-Tanimoto decile stratification. CPU only.
# Usage: sbatch scripts/p5_nn_tanimoto_deciles.sbatch

#SBATCH --job-name=p5_nn_deciles
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --output=%x.log
#SBATCH --error=%x.err

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

cd /home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2
python scripts/p5_nn_tanimoto_deciles.py
