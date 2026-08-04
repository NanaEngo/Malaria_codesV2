#!/bin/bash
# ChemBERTa fine-tune (H2 arm) — random + scaffold, 5-fold x 5 seeds.
# Usage: sbatch scripts/p5_chemberta.sbatch [random|scaffold]

#SBATCH --job-name=p5_chemberta
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=p5_chemberta.log
#SBATCH --error=p5_chemberta.err

SPLIT=${1:-random}
LOG_DIR=$(pwd)/logs/p5_chemberta_${SPLIT}
mkdir -p ${LOG_DIR}

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
python scripts/p5_chemberta.py --split ${SPLIT} --device cuda > ${LOG_DIR}/stdout.log 2>&1
