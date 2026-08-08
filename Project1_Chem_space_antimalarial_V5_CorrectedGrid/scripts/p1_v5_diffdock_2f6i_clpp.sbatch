#!/bin/bash
#SBATCH --job-name=p1v5_clpp_2f6i
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=logs/p1_v5_diffdock_2f6i_clpp_%j.log
#SBATCH --error=logs/p1_v5_diffdock_2f6i_clpp_%j.err
set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid
# ODE mode: deterministic score-guided refinement keeps rank-1 in the declared
# catalytic grid (stochastic Langevin sampling drifted poses 10-17 A out).
python scripts/p1_v5_run_diffdock_clpp_2f6i.py --output-dir results/diffdock_2F6I_PfClpP_17_ode
