#!/bin/bash
#SBATCH --job-name=p1v5_rrs_post
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=logs/p1_v5_rrs_post_%j.log
#SBATCH --error=logs/p1_v5_rrs_post_%j.err
# Submit with:
#   sbatch --dependency=afterok:12894:12895 scripts/p1_v5_rrs_postprocess.sbatch
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid

echo "=== [1/2] merge per-target mutant scores ==="
python scripts/p1_v5_rrs_merge_scores.py

echo "=== [2/2] per-target RRS pilot ==="
python scripts/p1_v5_rrs_pilot.py

echo "=== DONE ==="
