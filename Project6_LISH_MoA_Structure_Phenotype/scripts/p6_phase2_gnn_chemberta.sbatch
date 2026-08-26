#!/bin/bash
#SBATCH --job-name=p6_gnn_arms
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=12
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/p6_gnn_arms_%A_%a.log
#SBATCH --error=logs/p6_gnn_arms_%A_%a.err
set -euo pipefail
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
ROOT=/home/nanaengo/Malaria_codesV2/Project6_LISH_MoA_Structure_Phenotype
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$ROOT"
mkdir -p logs results/p6_phase2

if [ ! -f results/p6_phase2/p6_tfp_tne_descriptors.npz ]; then
  echo "[sbatch] computing TFP/TNE descriptors"
  $PY scripts/p6_desc_tfp_tne.py
fi

for MODEL in GIN GIN-TFP GIN-TNE; do
  echo "[sbatch] arm $MODEL"
  $PY scripts/p6_phase2_gnn.py --model "$MODEL" --split collision_group
  echo "[sbatch] arm $MODEL done"
done

echo "[sbatch] arm chemberta"
$PY scripts/p6_phase2_chemberta.py --split collision_group
echo "[sbatch] arm chemberta done"
echo "[sbatch] ALL ARMS COMPLETE"
