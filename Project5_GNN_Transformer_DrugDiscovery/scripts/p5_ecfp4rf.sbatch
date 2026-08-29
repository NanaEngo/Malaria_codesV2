#!/bin/bash
# ECFP4-RF baseline (random + scaffold, 5-fold x 5 seeds) — CPU only.
# Usage: sbatch scripts/p5_ecfp4rf.sbatch

#SBATCH --job-name=p5_ecfp4rf
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=%x.log
#SBATCH --error=%x.err

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
python scripts/p5_sanity_ecfp4_rf.py --split random
python scripts/p5_sanity_ecfp4_rf.py --split scaffold
