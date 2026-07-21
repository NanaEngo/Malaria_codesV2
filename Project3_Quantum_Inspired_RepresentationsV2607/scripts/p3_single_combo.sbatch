#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P3 Single Combo — bd6_nr1_nk30 optimisé
#
# Évalue AUC du descripteur Hybrid pour LE MEILLEUR combo uniquement.
# Pipeline optimisé : précalcul du kernel UNE FOIS → extraction par fold.
#
# Temps estimé : ~2-3 min pour n=1000, bd6, nr1
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p3_bd6_nr1_nk30
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_single_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_single_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1

PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_DIR}/results"
N_MOLS="${N_MOLS:-500}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Single Combo — bd6_nr1_nk30 optimisé                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  bond_dim=6, n_repeats=1, n_kpca=30"
echo "║  N molecules: ${N_MOLS}"
echo "║  CPUs: $(nproc)"
echo "║  Start: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"

OUT_CSV="${RESULTS_DIR}/p3_single_bd6_nr1_nk30.csv"

time "${PYTHON}" "${PROJECT_DIR}/scripts/p3_quantum_param_search.py" \
  --bond-dim 6 \
  --n-repeats 1 \
  --n-kpca 30 \
  --n-mols "${N_MOLS}" \
  --block-size 200 \
  --n-jobs 1 \
  --output-csv "${OUT_CSV}" 2>&1

if [ -f "${OUT_CSV}" ]; then
  echo "  ▶ Sauvegardé : ${OUT_CSV}"
  cat "${OUT_CSV}"
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Single Combo COMPLETE ✓"
echo "║  End: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
