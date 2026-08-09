#!/bin/bash
#SBATCH --job-name=p1_v4_rem_agg
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --mem=4G
#SBATCH --output=logs/p1_v4_rem_agg_%j.log
#SBATCH --error=logs/p1_v4_rem_agg_%j.err
set -euo pipefail
RUN_ROOT=${RUN_ROOT:-/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_remediation_20260809}
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid
python scripts/p1_v4_remediate_2f6i_aggregate.py --output-root "$RUN_ROOT"
echo "AGGREGATE_DONE"
