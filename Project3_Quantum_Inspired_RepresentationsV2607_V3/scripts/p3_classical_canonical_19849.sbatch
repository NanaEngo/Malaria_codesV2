#!/bin/bash
#SBATCH --job-name=p3_classical_canonical
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_classical_canonical_19849_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_classical_canonical_19849_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=80G
#SBATCH --time=12:00:00
#SBATCH --partition=production
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

echo "P3 Canonical Classical Benchmark (n=19,849 panel, RF-only)"
echo "  BMAD v51 — Appendix K: shared canonical panel (C2/M3);"
echo "  output seeds the hybrid benchmark via --skip-classical."
echo "  Start: $(date -u -Iseconds)"

"${PYTHON}" "${PROJECT_DIR}/scripts/p3_classical_benchmark_19849.py"

echo "COMPLETE. End: $(date -u -Iseconds)"
