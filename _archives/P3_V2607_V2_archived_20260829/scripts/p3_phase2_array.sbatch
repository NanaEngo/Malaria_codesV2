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
#SBATCH --array=0-2%3
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_phase2_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_phase2_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
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
# Optimized for penavoraserver (48 CPUs, 125 GB RAM). 3 jobs × 8 CPUs = 24 CPUs total.
export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8

# Force JAX to use CPU backend when no GPU is requested
export JAX_PLATFORMS=cpu
export CUDA_VISIBLE_DEVICES=""

# ── Configuration ────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_DIR}/results"
N_MOLS="${N_MOLS:-5000}"

# ── Log redirect (after PROJECT_DIR is defined) ──────────────────────
# The %%a SLURM directive in #SBATCH --output expands to 4294967294
# (invalid sentinel) for the master array job. Using $SLURM_ARRAY_TASK_ID
# env var directly gives the correct task ID at runtime.
_LOG_DIR="${PROJECT_DIR}/logs/slurm"
mkdir -p "${_LOG_DIR}"
_LOG_PATH="${_LOG_DIR}/p3_phase2_${SLURM_ARRAY_TASK_ID:-unknown}_${SLURM_JOB_ID}.log"
exec > "${_LOG_PATH}" 2>&1

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
read -r _ mem_total mem_used _ < <(free -h | grep '^Mem:') && mem_info="${mem_used}/${mem_total}"
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
# Note : --n-jobs 4 pour le RF classifier, OMP_NUM_THREADS=4 pour lightning.qubit.
#       Le kernel chunké (block_size=200) offre ~2-4× speedup via OpenMP.

echo "  ▶ Lancement de l'évaluation (5-fold CV, n=${N_MOLS})..."
echo "  ▶ Paramètres : bond_dim=${BD}, n_repeats=${NR}, n_kpca=${NK}"

OUT_CSV="${RESULTS_DIR}/p3_phase2_${LABEL}_raw.csv"

time "${PYTHON}" "${PROJECT_DIR}/scripts/p3_quantum_param_search.py" \
  --bond-dim "${BD}" \
  --n-repeats "${NR}" \
  --n-kpca "${NK}" \
  --n-mols "${N_MOLS}" \
  --block-size 200 \
  --n-jobs 8 \
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
