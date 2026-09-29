#!/bin/bash
#SBATCH --job-name=p2_setc_eq_retry
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=06:00:00
#SBATCH --array=0-11%4
#SBATCH --output=logs/p2_setc_eq_retry_%A_%a.log
#SBATCH --error=logs/p2_setc_eq_retry_%A_%a.err
#
# Retry of the 12 Set-C systems that crashed with an OpenMP (libgomp) error in
# array 15054. Root cause: the original array (--array=0-15, no concurrency
# limit, --mem=16G) launched all 16 tasks simultaneously on a 48-CPU / 128G node
# (16x4 CPU=64 > 48; 16x16G=256G > 128G) -> resource oversubscription -> OpenMP
# thread/memory allocation failure -> crash during EM.
# This retry: max 4 concurrent tasks (12x4 CPU=48 fits the node), --mem=8G
# (gmx_mpi CPU on ~316k atoms uses far less than 16G).
# The 4 systems that survived the original array (indices 3,4,13,15) are NOT
# included here; they continue running to completion in 15054.

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
mkdir -p logs

# 12 failed systems only (the 4 that survived 15054 are excluded)
SYSTEMS=(PP-01_PfDHFR_WT PP-01_PfDHFR_N51I PP-01_PfDHFR_C59R \
         PP-01_PfCRT_WT PP-01_PfCRT_K76T PP-01_PfCRT_K76A \
         PP-02_PfDHFR_WT PP-02_PfDHFR_N51I PP-02_PfDHFR_C59R PP-02_PfDHFR_S108N \
         PP-02_PfDHFR_I164L PP-02_PfCRT_K76T)

SYS="${SYSTEMS[$SLURM_ARRAY_TASK_ID]}"
echo "=== equilibration retry: $SYS (array index $SLURM_ARRAY_TASK_ID) ==="
python scripts/p2_setc_equilibrate.py --system "$SYS"
echo "EQUILIBRATION_RETRY_DONE $SYS RC=$?"
