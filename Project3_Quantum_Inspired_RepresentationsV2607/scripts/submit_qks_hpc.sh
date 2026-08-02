#!/bin/bash
#===============================================================================
# Paper 3 — QKS Benchmark HPC Submission Script
#
# Submits the QKS benchmark to a SLURM HPC cluster with:
#   - 48 CPU cores (block decomposition for kernel matrix)
#   - 64 GB RAM (kernel matrix ~72 MB — negligible)
#   - 2-hour wall time (3000 mol × 5 folds × chunked parallel)
#   - Checkpoint resume (survives SLURM preemption)
#
# Usage (SLURM — if controller available):
#   sbatch scripts/submit_qks_hpc.sh
#
# Usage (nohup — SLURM controller down):
#   nohup bash scripts/submit_qks_hpc.sh --nohup > results/p3_qks_full.log 2>&1 &
#
# Customisation:
#   N_MOLS:      number of molecules (default: 3000)
#   BLOCK_SIZE:  block size for chunked kernel (default: 200)
#===============================================================================
#SBATCH --job-name=p3_qks
#SBATCH --output=logs/p3_qks_%j.out
#SBATCH --error=logs/p3_qks_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=48
#SBATCH --mem=64G
#SBATCH --nodes=1
#SBATCH --partition=cpu

set -eo pipefail  # no -u: GROMACS env scripts use unbound vars (GMXLIB, GMXLDLIB)

# ── Config ── Adapted for penavoraserver HPC ────────────────────────────────
N_MOLS=3000
BLOCK_SIZE=200
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
ENV_NAME="malaria_md"             # pennylane 0.45.1 + joblib 1.5.3
CONDA_BASE="/home/nanaengo/miniforge3"
CHECKPOINT="/tmp/p3_qks_checkpoint.json"
N_JOBS=48                          # penavoraserver: 48 CPUs, 125 GB RAM

# ── Detect mode: SLURM vs nohup ────────────────────────────────────────────
if [ "${1:-}" = "--nohup" ]; then
    # nohup mode: use direct CPU count instead of $SLURM_CPUS_PER_TASK
    CPUS="${N_JOBS}"
    echo "=== NOHUP MODE ==="
else
    # SLURM mode
    CPUS="${SLURM_CPUS_PER_TASK:-${N_JOBS}}"
fi

# Create logs directory
mkdir -p logs

echo "=== QKS Benchmark — $(date) ==="
echo "Host: $(hostname)"
echo "CPUs: $(nproc)"
echo "Memory: $(free -g | grep Mem | awk '{print $2}') GB"
echo "Cores for joblib: ${CPUS}"

# Activate conda environment (malaria_md)
if [ -f "${CONDA_BASE}/etc/profile.d/conda.sh" ]; then
    source "${CONDA_BASE}/etc/profile.d/conda.sh"
    conda activate "${ENV_NAME}"
    echo "Conda env: ${ENV_NAME}"
else
    echo "Warning: conda.sh not found at ${CONDA_BASE}. Trying direct python..."
fi

# Prevent thread oversubscription inside numpy/PennyLane
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

echo "Python: $(which python)"
echo "N_MOLS=${N_MOLS}, BLOCK_SIZE=${BLOCK_SIZE}, N_JOBS=${CPUS}"

# ── Run benchmark (with checkpoint resume) ───────────────────────────────────
cd "${PROJECT_DIR}"

python scripts/p3_qks_benchmark.py \
    --n-mols "${N_MOLS}" \
    --block-size "${BLOCK_SIZE}" \
    --n-jobs "${CPUS}" \
    --checkpoint "${CHECKPOINT}"

# ── Post-processing ──────────────────────────────────────────────────────────
echo "=== Done — $(date) ==="
echo "Results: results/p3_qks_benchmark.csv"
echo "Summary: results/p3_qks_summary.txt"
rm -f "${CHECKPOINT}"  # clean up on success
