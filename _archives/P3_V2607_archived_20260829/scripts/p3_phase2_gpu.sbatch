#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P3 Phase 2 — GPU-optimised (pennylane-lightning + JAX GPU)
#
# Array 3 tâches (0-2), avec accélération GPU via lightning.gpu
# et/ou lightning.qubit avec JAX JIT.
#
# Skills: optimize-for-gpu (CuPy), pennylane (best_device()), parallel-web
#
# Meilleurs combos (issus du job 7962, n=200):
#   Task 0: bond_dim=6, n_repeats=1, n_kpca=30  → AUC 0.8534
#   Task 1: bond_dim=6, n_repeats=6, n_kpca=30  → AUC 0.8464
#   Task 2: bond_dim=6, n_repeats=6, n_kpca=20  → AUC 0.8456
#
# Sortie : results/p3_phase2_N.csv
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p3_phase2_gpu
#SBATCH --array=0-2
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_phase2_gpu_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_phase2_gpu_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --time=12:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

# ── Error trap ───────────────────────────────────────────────────────
err_handler() {
  local exit_code="$1"
  {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "GPU Task ${ID}: label=${LABEL} bd=${BD} nr=${NR} nk=${NK}"
    echo "  Status: FAILED"
    echo "  Exit code: ${exit_code}"
    echo "  End: $(date -u -Iseconds)"
    echo "═══════════════════════════════════════════════════════════════"
  } >> "${RESULTS_DIR}/p3_phase2_done.log" || true
  exit "${exit_code}"
}
trap 'err_handler $?' ERR

# ── Threading ────────────────────────────────────────────────────────
# lightning.gpu utilise CUDA streams; OMP threads for CPU->GPU transfer.
# 4 CPU cores optimaux pour la gestion des transferts CPU↔GPU.
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export JAX_PLATFORMS=cuda,cpu
export JAX_ENABLE_X64=True

# ── Configuration ────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_DIR}/results"
N_MOLS="${N_MOLS:-5000}"

# ── Log redirect (fix %a→4294967294) ────────────────────────────────
_LOG_DIR="${PROJECT_DIR}/logs/slurm"
mkdir -p "${_LOG_DIR}"
_LOG_PATH="${_LOG_DIR}/p3_phase2_gpu_${SLURM_ARRAY_TASK_ID:-unknown}_${SLURM_JOB_ID}.log"
exec > "${_LOG_PATH}" 2>&1
BLOCK_SIZE="${BLOCK_SIZE:-400}"

# ── 3 meilleurs combos ───────────────────────────────────────────────
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
echo "║  P3 Phase 2 GPU — Task ${ID}                                ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Combo: bond_dim=${BD}, n_repeats=${NR}, n_kpca=${NK}"
echo "║  Label: ${LABEL}"
echo "║  N molecules: ${N_MOLS}"
echo "║  Block size: ${BLOCK_SIZE}"
echo "║  Host: $(hostname)"
echo "║  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
echo "║  CPUs avail: $(nproc)"
read -r _ mem_total mem_used _ < <(free -h | grep '^Mem:') && mem_info="${mem_used}/${mem_total}"
echo "║  Mem: ${mem_info}"
echo "║  JAX backend: ${JAX_PLATFORMS}"
echo "║  Start: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"

# ── Vérification GPU ──────────────────────────────────────────────────
echo "  ▶ Vérification GPU..."
"${PYTHON}" -c "
import jax
import pennylane as qml
try:
    import cupy as cp
    print(f'  CuPy: available={cp.is_available()}')
except ImportError:
    print('  CuPy: not available')
devices = jax.devices()
for d in devices:
    print(f'  JAX device: {d.platform} — {d}')
for nq in [${BD}]:
    for d in ['lightning.gpu', 'lightning.qubit']:
        try:
            dev = qml.device(d, wires=nq)
            print(f'  PennyLane {d} ({nq}q): OK')
            break
        except Exception:
            continue
    else:
        print(f'  PennyLane ({nq}q): default.qubit fallback')
" 2>&1

# ── Exécution ────────────────────────────────────────────────────────
echo ""
echo "  ▶ Lancement évaluation (5-fold CV, n=${N_MOLS})..."
echo "  ▶ Paramètres : bond_dim=${BD}, n_repeats=${NR}, n_kpca=${NK}"
echo "  ▶ Block size : ${BLOCK_SIZE}"

OUT_CSV="${RESULTS_DIR}/p3_phase2_gpu_${LABEL}_raw.csv"

time "${PYTHON}" "${PROJECT_DIR}/scripts/p3_quantum_param_search.py" \
  --bond-dim "${BD}" \
  --n-repeats "${NR}" \
  --n-kpca "${NK}" \
  --n-mols "${N_MOLS}" \
  --block-size "${BLOCK_SIZE}" \
  --n-jobs 1 \
  --output-csv "${OUT_CSV}" 2>&1

# ── Sauvegarde ────────────────────────────────────────────────────────
if [ -f "${OUT_CSV}" ]; then
  echo "  ▶ Sauvegardé : ${OUT_CSV}"
fi

# ── Journalisation ──────────────────────────────────────────────────
{
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "GPU Task ${ID}: label=${LABEL} bd=${BD} nr=${NR} nk=${NK}"
  echo "  Status: DONE"
  echo "  End: $(date -u -Iseconds)"
  echo "═══════════════════════════════════════════════════════════════"
} >> "${RESULTS_DIR}/p3_phase2_done.log" || true

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  GPU Task ${ID} COMPLETE ✓                                  ║"
echo "║  End: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
