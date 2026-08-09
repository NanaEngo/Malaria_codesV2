#!/bin/bash
# Reproducible v2 rescue specification for the already submitted job 13478.
# This file is intentionally not a second submission script: job 13478 was
# launched from the same tracked v1 wrapper with output-root substitution.
#SBATCH --job-name=p1v4_2f6i_retry_v2
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --array=13,30,40,43,47,70,73,99,100,125,136,145,167,170,189,194,195,228,237,257,258,339,340,358,361,368,373,390,408,416,423,435,440,452,468%12
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/logs/p1_v4_2f6i_retry_v2_%A_%a.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/logs/p1_v4_2f6i_retry_v2_%A_%a.err
set -euo pipefail
ROOT=/home/nanaengo/Malaria_codesV2
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
OUT=$ROOT/Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_rescue_seed20260809_v2
mkdir -p "$OUT"
exec "$PY" "$ROOT/Project1_Chem_space_antimalarial_V4_CorrectedGrid/scripts/p1_v4_retry_clpp_2f6i.py" \
  --centroid-id "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}" \
  --output-root "$OUT"
