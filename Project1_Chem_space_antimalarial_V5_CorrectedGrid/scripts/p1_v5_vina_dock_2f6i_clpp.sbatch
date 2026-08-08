#!/bin/bash
#SBATCH --job-name=p1v5_vina_2f6i
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p1_v5_vina_dock_2f6i_clpp_%j.log
#SBATCH --error=logs/p1_v5_vina_dock_2f6i_clpp_%j.err
set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid
python scripts/p1_v5_vina_dock_clpp_2f6i.py --output-dir /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/vina_dock_2F6I_PfClpP_17
