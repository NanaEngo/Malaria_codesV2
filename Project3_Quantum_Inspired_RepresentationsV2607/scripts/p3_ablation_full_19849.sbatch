#!/bin/bash
#SBATCH --job-name=p3_ablation_full_19849
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_ablation_full_19849_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_ablation_full_19849_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=80G
#SBATCH --time=12:00:00
#SBATCH --partition=production
#SBATCH --dependency=afterok:12696
#SBATCH --export=ALL

set -euo pipefail

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
export NUMEXPR_NUM_THREADS=$SLURM_CPUS_PER_TASK
export PYTHONUNBUFFERED=1

PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

cd "${PROJECT_DIR}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Full-Library ABLATION (n = 19,849)                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  CPUs: $(nproc)                                               ║"
echo "║  Start: $(date -u -Iseconds)                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "  BMAD v50 FIX (Aug 1, 2026): ablation-only run resuming the"
echo "  p3_hybrid_full_checkpoint.json written by job 12696."
echo "  Uses the Phase-2 winning combo: --n-qubits 6 --n-repeats 1"
echo "  --n-kpca 30. The hybrid folds already in the checkpoint are"
echo "  skipped; only the 3-component ablation (Hybrid-TFP/TNE/QK)"
echo "  is computed. Relaunched after job 12695 was killed for using"
echo "  defaults (n_qubits=8, n_kpca=10) instead of the winning combo."

"${PYTHON}" "${PROJECT_DIR}/scripts/p3_hybrid_benchmark.py" \
  --n-mols 19849 \
  --hpc \
  --block-size 200 \
  --n-qubits 6 \
  --n-repeats 1 \
  --n-kpca 30 \
  --skip-classical \
  --precompute-kernel \
  --checkpoint "${PROJECT_DIR}/results/p3_hybrid_full_checkpoint.json"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P3 Full-Library ABLATION COMPLETE ✓"
echo "║  End: $(date -u -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
