#!/bin/bash
#SBATCH --job-name=p3_hybrid_nystrom
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G
#SBATCH --time=24:00:00
#SBATCH --partition=production
#SBATCH --output=logs/slurm/p3_hybrid_nystrom_%j.log
#SBATCH --error=logs/slurm/p3_hybrid_nystrom_%j.log
#SBATCH --mail-type=BEGIN,END,FAIL

set -euo pipefail
export PYTHONUNBUFFERED=1

cd /home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607

PYTHON=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK

$PYTHON scripts/p3_hybrid_benchmark.py \
    --n-mols 5000 \
    --n-kpca 5 \
    --n-jobs $SLURM_CPUS_PER_TASK \
    --block-size 500 \
    --skip-classical \
    --nystrom-m 500 \
    --checkpoint results/p3_hybrid_nystrom_checkpoint.csv

echo "=== DONE $(date) ==="
