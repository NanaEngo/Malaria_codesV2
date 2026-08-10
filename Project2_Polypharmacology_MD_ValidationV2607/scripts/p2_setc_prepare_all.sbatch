#!/bin/bash
#SBATCH --job-name=p2_setc_prep_all
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=10:00:00
#SBATCH --mem=24G
#SBATCH --output=logs/p2_setc_prep_all_%j.log
#SBATCH --error=logs/p2_setc_prep_all_%j.err

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
mkdir -p logs results/md_systems/set_c
python scripts/p2_setc_prepare_openff.py --all
echo "PREPARATION_ALL_DONE RC=$?"
