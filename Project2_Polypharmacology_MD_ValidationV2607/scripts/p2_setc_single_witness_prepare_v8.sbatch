#!/bin/bash
#SBATCH --job-name=p2_setc_wit_prep
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --mem=24G
#SBATCH --output=logs/p2_setc_wit_prep_%j.log
#SBATCH --error=logs/p2_setc_wit_prep_%j.err

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
ROOT=results/md_systems/set_c_publication_witness_v8_20260811
[ ! -e "$ROOT" ] || { echo "REFUSING non-fresh output root: $ROOT" >&2; exit 2; }
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
export P2_OBABEL=/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel
python scripts/p2_setc_prepare_openff.py --system PP-01_PfDHFR_WT --output-root "$ROOT"
