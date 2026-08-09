#!/bin/bash
#SBATCH --job-name=p1v4_2f6i_uniform
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --array=0-483%24
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/logs/p1_v4_2f6i_uniform_%A_%a.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/logs/p1_v4_2f6i_uniform_%A_%a.err
set -euo pipefail
ROOT=/home/nanaengo/Malaria_codesV2
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
OUT=$ROOT/Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_uniform_seed20260809
mkdir -p "$OUT"
exec "$PY" "$ROOT/Project1_Chem_space_antimalarial_V4_CorrectedGrid/scripts/p1_v4_retry_clpp_2f6i.py" \
  --centroid-id "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}" \
  --output-root "$OUT"
