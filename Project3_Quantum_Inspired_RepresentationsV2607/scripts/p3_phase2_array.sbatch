#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P3 Phase 2 — Benchmark des 3 meilleurs combos QK sur n=5,000
#
# Array 3 tâches (0-2), parallélisées via le nouveau SLURM optimisé.
# Chaque tâche évalue l'AUC du descripteur Hybrid avec un combo QK différent.
#
# Meilleurs combos (issus du job 7962, n=200):
#   Task 0: bond_dim=6, n_repeats=1, n_kpca=30  → AUC 0.8534
#   Task 1: bond_dim=6, n_repeats=6, n_kpca=30  → AUC 0.8464
#   Task 2: bond_dim=6, n_repeats=6, n_kpca=20  → AUC 0.8456
#
# Sortie : results/p3_phase2_array_N.csv  (fichier unique par tâche)
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p3_phase2
#SBATCH --array=0-2
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_phase2_%a_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_phase2_%a_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=48:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

# ── Error trap ───────────────────────────────────────────────────────
# Log failures before bash exits because of set -e.
err_handler() {
  local exit_code="$1"
  {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "Task ${ID}: label=${LABEL} bd=${BD} nr=${NR} nk=${NK}"
    echo "  Status: FAILED"
    echo "  Exit code: ${exit_code}"
    echo "  End: $(date -u -Iseconds)"
    echo "═══════════════════════════════════════════════════════════════"
  } >> "${RESULTS_DIR}/p3_phase2_done.log" || true
  exit "${exit_code}"
}
trap 'err_handler $?' ERR

# ── Threading limits ─────────────────────────────────────────────────
# lightning.qubit uses OpenMP and will auto-detect all node CPUs even when
# SLURM allocates only one.  Limit each process to a single thread to
# avoid oversubscription and context-switching overhead.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# ── Configuration ────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_DIR}/results"
N_MOLS=5000

# ── 3 meilleurs combos de la recherche de paramètres ─────────────────
# Format: bond_dim,n_repeats,n_kpca
declare -a BD_LIST=(6 6 6)
declare -a NR_LIST=(1 6 6)
declare -a NK_LIST=(30 30 20)
declare -a LABEL_LIST=("bd6_nr1_nk30" "bd6_nr6_nk30" "bd6_nr6_nk20")

ID=${SLURM_ARRAY_TASK_ID:?ERROR: not running as array job?}

BD=${BD_LIST[$ID]}
NR=${NR_LIST[$ID]}
NK=${NK_LIST[$ID]}
LABEL=${LABEL_LIST[$ID]}

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Phase 2 — Task ${ID}                                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Combo: bond_dim=${BD}, n_repeats=${NR}, n_kpca=${NK}"
echo "║  Label: ${LABEL}"
echo "║  N molecules: ${N_MOLS}"
echo "║  Host: $(hostname)"
echo "║  CPUs avail: $(nproc)"
mem_info=$(free -h | awk '/Mem/{print $3 " / " $2}')
echo "║  Mem: ${mem_info}"
echo "║  Start: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"

# ── Exécution du benchmark Hybrid pour ce combo ─────────────────────
# p3_quantum_param_search.py évalue AUC du descripteur Hybrid (RF, 5-fold CV)
# avec les paramètres QK spécifiés, sur N_MOLS molécules.
#
# Note : Seulement 994 molécules ont des TFP précalculés. Les molécules
# au-delà de 994 reçoivent un vecteur TFP nul. Ceci est un facteur contrôlé
# (identique pour les 3 combos) qui ne biaise pas la comparaison relative.
#
# Note : --n-jobs 1 car lightning.qubit est mono-thread (pas de gain en parallélisant).

echo "  ▶ Lancement de l'évaluation (5-fold CV, n=${N_MOLS})..."
echo "  ▶ Paramètres : bond_dim=${BD}, n_repeats=${NR}, n_kpca=${NK}"

OUT_CSV="${RESULTS_DIR}/p3_phase2_${LABEL}_raw.csv"

time "${PYTHON}" "${PROJECT_DIR}/scripts/p3_quantum_param_search.py" \
  --bond-dim "${BD}" \
  --n-repeats "${NR}" \
  --n-kpca "${NK}" \
  --n-mols "${N_MOLS}" \
  --block-size 200 \
  --n-jobs 1 \
  --output-csv "${OUT_CSV}" 2>&1

# ── Sauvegarde unique par tâche (évite les races conditions) ────────
if [ -f "${OUT_CSV}" ]; then
  echo "  ▶ Sauvegardé : ${OUT_CSV}"
fi

# ── Journalisation ──────────────────────────────────────────────────
{
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "Task ${ID}: label=${LABEL} bd=${BD} nr=${NR} nk=${NK}"
  echo "  Status: DONE"
  echo "  End: $(date -u -Iseconds)"
  echo "═══════════════════════════════════════════════════════════════"
} >> "${RESULTS_DIR}/p3_phase2_done.log" || true

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Task ${ID} COMPLETE ✓"
echo "║  End: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
