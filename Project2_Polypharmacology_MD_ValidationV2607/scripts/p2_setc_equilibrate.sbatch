#!/bin/bash
#SBATCH --job-name=p2_setc_eq
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=06:00:00
#SBATCH --mem=16G
#SBATCH --array=0-15
# NOTE: submit with --dependency=afterok:<PREP_JOB_ID> once preparation completes
#SBATCH --output=logs/p2_setc_eq_%A_%a.log
#SBATCH --error=logs/p2_setc_eq_%A_%a.err

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
mkdir -p logs

# 16 systems: PP-01/PP-02 x (PfDHFR WT,N51I,C59R,S108N,I164L; PfCRT WT,K76T,K76A)
SYSTEMS=(PP-01_PfDHFR_WT PP-01_PfDHFR_N51I PP-01_PfDHFR_C59R PP-01_PfDHFR_S108N \
         PP-01_PfDHFR_I164L PP-01_PfCRT_WT PP-01_PfCRT_K76T PP-01_PfCRT_K76A \
         PP-02_PfDHFR_WT PP-02_PfDHFR_N51I PP-02_PfDHFR_C59R PP-02_PfDHFR_S108N \
         PP-02_PfDHFR_I164L PP-02_PfCRT_WT PP-02_PfCRT_K76T PP-02_PfCRT_K76A)

SYS="${SYSTEMS[$SLURM_ARRAY_TASK_ID]}"
echo "=== equilibration: $SYS ==="
python scripts/p2_setc_equilibrate.py --system "$SYS"
echo "EQUILIBRATION_DONE $SYS RC=$?"
