#!/bin/bash
#SBATCH --job-name=p2_setc_wit_eq
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --mem=16G
#SBATCH --output=logs/p2_setc_wit_eq_%j.log
#SBATCH --error=logs/p2_setc_wit_eq_%j.err

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

export P2_SETC_NTOMP=8
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
export P2_SETC_ROOT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_publication_witness_v8_20260811

cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
python scripts/p2_setc_equilibrate.py --system PP-01_PfDHFR_WT
