#!/bin/bash
#SBATCH --job-name=p5_lish_moa
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/p5_lish_moa_%j.log
#SBATCH --error=logs/p5_lish_moa_%j.err
set -euo pipefail
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
ROOT=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$ROOT"
mkdir -p logs
$PY scripts/p5_lish_moa_benchmark.py --features phenotype --split drug_grouped
$PY scripts/p5_lish_moa_benchmark.py --features phenotype --split drug_grouped --exclude-controls
if [ -f results/lish_moa/lish_moa_structure_mapped.csv ]; then
  $PY scripts/p5_lish_moa_benchmark.py --features structure --split scaffold
fi
