#!/bin/bash
#SBATCH --job-name=p1v5_rrs_mut
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p1_v5_rrs_mut_%x_%j.log
#SBATCH --error=logs/p1_v5_rrs_mut_%x_%j.err
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid

# Usage: sbatch --export=ALL,TARGET=PfDHFR scripts/p1_v5_rrs_mutants.sbatch
: "${TARGET:?set TARGET=PfDHFR or PfCRT}"

python scripts/p1_v5_vina_dock_mutants.py --target "$TARGET" \
    --output-root results/rrs_pilot/vina_scores

# When both panels have finished, merge the per-target CSVs:
#   python scripts/p1_v5_rrs_merge_scores.py
# (run via the chained postprocess job after both panels COMPLETE)
