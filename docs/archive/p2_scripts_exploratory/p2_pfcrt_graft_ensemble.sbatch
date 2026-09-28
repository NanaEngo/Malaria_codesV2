#!/bin/bash
#SBATCH --job-name=p2_pfcrt_graft_ens
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/p2_pfcrt_graft_ens_%j.log
#SBATCH --error=logs/p2_pfcrt_graft_ens_%j.err

set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u

PROJECT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
cd "$PROJECT"
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
PRED=results/md_systems/pfcrt_colabfold_gpu_ensemble_20260811
OUT=results/md_systems/pfcrt_colabfold_gpu_ensemble_grafted_20260811
MAP=results/md_systems/pfcrt_uniprot_pdb_mapping_20260811.json
REF=data/proteins/6UKJ.pdb

"$PY" -m py_compile scripts/p2_pfcrt_graft_colabfold_loop.py
"$PY" scripts/p2_pfcrt_graft_colabfold_loop.py \
  --reference "$REF" \
  --prediction-dir "$PRED" \
  --output-dir "$OUT" \
  --mapping "$MAP" \
  --chain A
