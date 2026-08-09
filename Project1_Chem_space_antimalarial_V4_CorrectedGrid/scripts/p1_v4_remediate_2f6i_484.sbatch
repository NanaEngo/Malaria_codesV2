#!/bin/bash
#SBATCH --job-name=p1_v4_rem_2f6i
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --array=0-34
#SBATCH --output=logs/p1_v4_rem_2f6i_%A_%a.log
#SBATCH --error=logs/p1_v4_rem_2f6i_%A_%a.err
set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock
# The 35 requested centroid IDs from pfclpp_2f6i_484_failure_inventory.json
# (order preserved: the 3 PASS_RAW_VINA from rescue_v2 are re-classified here).
IDS=(13 30 40 43 47 70 73 99 100 125 136 145 167 170 189 194 195 228 237 257 258 339 340 358 361 368 373 390 408 416 423 435 440 452 468)
CID=${IDS[$SLURM_ARRAY_TASK_ID]}
RUN_ROOT=${RUN_ROOT:-/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_remediation_20260809}
mkdir -p "$RUN_ROOT"
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid
python scripts/p1_v4_remediate_2f6i_484.py --centroid-id "$CID" --output-root "$RUN_ROOT"
echo "DONE cid=$CID"
