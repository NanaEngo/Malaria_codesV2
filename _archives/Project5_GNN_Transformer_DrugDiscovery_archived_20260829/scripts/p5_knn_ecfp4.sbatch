#!/bin/bash
#SBATCH --job-name=p5_knn_ecfp4
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --output=logs/p5_knn_ecfp4_%j.log
#SBATCH --error=logs/p5_knn_ecfp4_%j.err
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
export OMP_NUM_THREADS=32
python scripts/p5_knn_ecfp4.py --split scaffold --k 5
python scripts/p5_knn_ecfp4.py --split random --k 5
