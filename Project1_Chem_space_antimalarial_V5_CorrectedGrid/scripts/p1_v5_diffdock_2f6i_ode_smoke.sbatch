#!/bin/bash
#SBATCH --job-name=p1v5_2f6i_odesmoke
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/p1_v5_diffdock_2f6i_ode_smoke_%j.log
#SBATCH --error=logs/p1_v5_diffdock_2f6i_ode_smoke_%j.err
set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid
rm -rf results/diffdock_2F6I_PfClpP_ode_smoke
python scripts/p1_v5_run_diffdock_clpp_2f6i.py --limit-pairs 1 --output-dir /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/diffdock_2F6I_PfClpP_ode_smoke
