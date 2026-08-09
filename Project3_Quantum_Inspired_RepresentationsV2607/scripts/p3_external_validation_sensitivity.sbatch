#!/bin/bash
#SBATCH --job-name=p3_ext_sens
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=06:00:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_ext_sens_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_ext_sens_%j.err

set -eo pipefail
# Do not source GMXRC in this CPU-only Python job: GMXRC is incompatible with
# nounset on this cluster and GROMACS is not used by the sensitivity analysis.
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
"$PY" -m py_compile Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_external_validation_sensitivity.py
"$PY" Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_external_validation_sensitivity.py
