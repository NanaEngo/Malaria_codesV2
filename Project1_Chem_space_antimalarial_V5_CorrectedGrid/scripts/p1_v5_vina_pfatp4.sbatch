#!/bin/bash
#SBATCH --job-name=p1v5_vina_pfatp4
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p1_v5_vina_pfatp4_%j.log
#SBATCH --error=logs/p1_v5_vina_pfatp4_%j.err
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid
python scripts/p1_v5_vina_dock_target.py --target PfATP4 --output-dir /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/vina_dock_9N10_PfATP4_17
