#!/bin/bash
#SBATCH --job-name=p3_ext_audit
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_ext_audit_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_ext_audit_%j.err
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2
/home/nanaengo/miniforge3/envs/malaria_md/bin/python Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_external_validation_statistical_audit.py
