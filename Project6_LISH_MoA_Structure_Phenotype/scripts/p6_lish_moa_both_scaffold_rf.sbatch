#!/bin/bash
#SBATCH --job-name=p6_both_scaff_rf
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p6_both_scaffold_rf_%A.log
#SBATCH --error=logs/p6_both_scaffold_rf_%A.err
set -euo pipefail
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
ROOT=/home/nanaengo/Malaria_codesV2/Project6_LISH_MoA_Structure_Phenotype
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$ROOT"
mkdir -p logs results/p6_phase2

# Scaffold fusion arm: phenotype + ECFP4, RandomForest, with per-drug prediction
# dumps (required by the pooled calibration and QKS analyses).
# Rationale (DAR decision record 30 Aug 2026): the manuscript baseline/fusion arms
# are RandomForest on every split; the scaffold fusion RF run was the only missing
# arm (collision-group fusion RF already on disk).
ARGS="--features both --split scaffold --model rf --dump-predictions --jobs 12"
echo "[sbatch] $ARGS"
$PY scripts/p6_phase2_benchmark.py $ARGS
echo "[sbatch] done"
