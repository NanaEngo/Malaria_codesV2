#!/bin/bash
#SBATCH --job-name=p1v4_2f6i_audit
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/logs/p1_v4_2f6i_audit_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/logs/p1_v4_2f6i_audit_%j.err
set -euo pipefail
ROOT=/home/nanaengo/Malaria_codesV2
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
RAW="$ROOT/Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_uniform_seed20260809"
OUT="$ROOT/Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_uniform_aggregate_afterany"
export P1_CLPP_RAW_DIR="$RAW"
export P1_CLPP_AGG_OUT="$OUT"
exec "$PY" "$ROOT/Project1_Chem_space_antimalarial_V4_CorrectedGrid/scripts/p1_v4_aggregate_clpp_2f6i.py"
