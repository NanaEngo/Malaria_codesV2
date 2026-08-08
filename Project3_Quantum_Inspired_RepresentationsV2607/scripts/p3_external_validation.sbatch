#!/bin/bash
#SBATCH --job-name=p3_extval
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p3_external_validation_%j.log
#SBATCH --error=logs/p3_external_validation_%j.err
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607
python scripts/p3_external_validation.py --n-jobs 16
