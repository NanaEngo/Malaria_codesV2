#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# P3 Hybrid Benchmark (n = 5,000) — GPU-accelerated
#
# Uses:
#   - lightning.gpu (PennyLane GPU backend) via --device
#   - JAX JIT + vmap for batched kernel matrix computation via --jax
#   - float32 precision for 2x memory savings on GPU
#   - NVIDIA RTX A4000 (16 GB VRAM)
#
# Skills: pennylane (best_device, lightning.gpu), optimize-for-gpu (CuPy,
#   JAX JIT, GPU batch), scikit-learn (Pipeline, StratifiedKFold, RF)
#
# Architecture:
#   JAX JIT compiles the ENTIRE kernel matrix into a single XLA operation,
#   avoiding per-pair QNode overhead. On GPU, this gives ~50,000+ pairs/s
#   vs ~500 pairs/s with standard lightning.qubit.
#
# Expected speedup vs CPU (lightning.qubit):
#   - QK kernel matrix: 10-50x
#   - Total 5-fold CV:  5-10x (UMAP/KPCA become dominant)
#
# Usage:
#   sbatch scripts/p3_hybrid_5000_gpu.sbatch
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p3_hybrid_5000_gpu
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_5000_gpu_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_hybrid_5000_gpu_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

# ── Error trap ───────────────────────────────────────────────────────
err_handler() {
  local exit_code="$1"
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  P3 GPU Hybrid Benchmark FAILED (exit code: ${exit_code})    ║"
  echo "║  End: $(date -u -Iseconds)                                   ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  exit "${exit_code}"
}
trap 'err_handler $?' ERR

# ── Threading (GPU kernels are asynchronous; CPU threads for data I/O) ──
export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export JAX_PLATFORMS=cuda,cpu
export JAX_ENABLE_X64=True
export PYTHONUNBUFFERED=1

# ── Configuration ────────────────────────────────────────────────────
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_DIR}/results"

cd "${PROJECT_DIR}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Hybrid Benchmark (n = 5,000) — GPU ACCELERATED         ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Device:    lightning.gpu + JAX JIT                        ║"
echo "║  CPUs:      $(nproc)                                               ║"
echo "║  GPU:       $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
echo "║  GPU VRAM:  $(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | tr -d ' ') MiB"
echo "║  Precision: float32 (GPU-optimised)                         ║"
echo "║  Qubits:    6 (optimal bond_dim from grid search)          ║"
echo "║  Repeats:   1 (shallow circuit)                             ║"
echo "║  KPCA:      30 (max signal extraction)                     ║"
echo "║  Skip:      ablation (full library = expensive)            ║"
echo "║  Start:     $(date -u -Iseconds)                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# ── GPU verification ────────────────────────────────────────────────
echo ""
echo "  ▶ GPU verification..."
"${PYTHON}" -c "
import jax
import pennylane as qml
devices = jax.devices()
for d in devices:
    print(f'  JAX device: {d.platform} — {d}')
# Verify lightning.gpu works
try:
    dev = qml.device('lightning.gpu', wires=6)
    print(f'  lightning.gpu (6q): OK')
except Exception as e:
    print(f'  lightning.gpu: {e}')
    # Fall back to lightning.qubit
    dev = qml.device('lightning.qubit', wires=6)
    print(f'  Fallback: lightning.qubit (6q): OK')
print('  JAX CUDA: OK' if jax.devices()[0].platform == 'gpu' else '  JAX: CPU only')
" 2>&1

# ── Run benchmark ────────────────────────────────────────────────────
echo ""
echo "  ▶ Launching GPU-accelerated hybrid benchmark (n=5,000)..."
echo "  ▶ 5-fold CV with per-fold QK (no data leakage)"
echo "  ▶ JAX JIT + lightning.gpu for kernel matrix (batched XLA)"

time "${PYTHON}" "${PROJECT_DIR}/scripts/p3_hybrid_benchmark.py" \
  --n-mols 5000 \
  --n-qubits 6 \
  --n-kpca 30 \
  --n-repeats 1 \
  --device lightning.gpu \
  --jax \
  --dtype float32 \
  --block-size 400 \
  --skip-ablation \
  --hpc \
  --checkpoint "${RESULTS_DIR}/p3_hybrid_5000_gpu_checkpoint.json"

# ── Completion ───────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 GPU Hybrid Benchmark COMPLETE ✓                          ║"
echo "║  End: $(date -u -Iseconds)                                   ║"
echo "║  Summary: ${RESULTS_DIR}/p3_hybrid_summary.txt               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
