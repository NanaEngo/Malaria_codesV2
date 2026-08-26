#!/bin/bash
#SBATCH --job-name=p6_lish_rf
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --array=0-2
#SBATCH --output=logs/p6_lish_moa_%A_%a.log
#SBATCH --error=logs/p6_lish_moa_%A_%a.err
set -euo pipefail
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
ROOT=/home/nanaengo/Malaria_codesV2/Project6_LISH_MoA_Structure_Phenotype
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$ROOT"
mkdir -p logs results/p6_phase2

case "$SLURM_ARRAY_TASK_ID" in
  0) ARGS="--features structure --split collision_group --model rf --jobs 12" ;;
  1) ARGS="--features structure --split scaffold --model rf --jobs 12" ;;
  2) ARGS="--features both --split collision_group --model rf --jobs 12" ;;
  *) echo "unknown task id"; exit 1 ;;
esac

echo "[sbatch] arm $SLURM_ARRAY_TASK_ID: $ARGS"
$PY scripts/p6_phase2_benchmark.py $ARGS
echo "[sbatch] arm $SLURM_ARRAY_TASK_ID done"
