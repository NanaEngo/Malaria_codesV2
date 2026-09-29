#!/bin/bash
#SBATCH --job-name=p2_pfcrt_graft
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/p2_pfcrt_graft_%j.log
#SBATCH --error=logs/p2_pfcrt_graft_%j.err

# Activate Conda before enabling nounset: this environment's GROMACS hook
# references optional variables during shell initialization.
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u
PROJECT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
cd "$PROJECT"
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
"$PY" -m py_compile scripts/p2_pfcrt_graft_colabfold_loop.py
"$PY" scripts/p2_pfcrt_graft_colabfold_loop.py \
  --reference data/proteins/6UKJ.pdb \
  --prediction-dir results/md_systems/pfcrt_colabfold_gpu_retry_20260811 \
  --output-dir results/md_systems/pfcrt_colabfold_gpu_retry_grafted_20260811 \
  --mapping results/md_systems/pfcrt_uniprot_pdb_mapping_20260811.json \
  --chain A
