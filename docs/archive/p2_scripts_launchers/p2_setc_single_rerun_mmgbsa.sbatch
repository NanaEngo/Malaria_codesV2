#!/bin/bash
# Single-system MM-GBSA rerun (Set-C single_rerun_20260825) — protocol identical
# to scripts/p2_setc_mmgbsa_batch.py (gmx_MMPBSA v1.5, GB OBC2 igb=5, saltcon
# 0.15 M, frames startframe=1 endframe=1000 interval=10 => 100 frames).
# Usage: sbatch scripts/p2_setc_single_rerun_mmgbsa.sbatch <SYSTEM_NAME> <RUN_DIR>
#SBATCH --job-name=p2_setc_rr_mmgbsa
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=08:00:00
#SBATCH --mem=16G
#SBATCH --output=logs/p2_setc_rr_mmgbsa_%j.log

# NOTE: no `set -u` — conda activate sources GMXRC which is not nounset-safe (cf. job 15293)
set -epipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
[ $# -eq 2 ] || { echo "usage: sbatch scripts/p2_setc_single_rerun_mmgbsa.sbatch <SYSTEM_NAME> <RUN_DIR>" >&2; exit 64; }
python scripts/p2_setc_mmgbsa_single.py "$1" "$2"
