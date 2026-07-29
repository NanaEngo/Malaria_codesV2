#!/bin/bash
#SBATCH --job-name=p1_dekois_auc_v2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/logs/slurm/dekois_auc_%j.log
#
# DEKOIS v2 ROC-AUC computation (post-docking)
# Computes ROC-AUC, bootstrap 95% CI, and enrichment factors
# from Meeko-uniform docked PDBQT files (40 actives, 1200 decoys)
#
# Dependency: results/v2_dekois/actives/*.docked.pdbqt and decoys/*.docked.pdbqt
# Must be submitted AFTER v2_slurm_dekois_fixed.sbatch array completes

set -eo pipefail
. /home/nanaengo/miniforge3/etc/profile.d/conda.sh
set +u
conda activate malaria_md
set -u

V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
cd "$V2DIR"

python scripts/compute_dekois_auc.py \
    --actives-dir results/v2_dekois/actives \
    --decoys-dir results/v2_dekois/decoys \
    --output results/v2_dekois/dekois_v2_roc_auc.csv \
    --seed 42

echo "=== DEKOIS AUC done: $(date) ==="
