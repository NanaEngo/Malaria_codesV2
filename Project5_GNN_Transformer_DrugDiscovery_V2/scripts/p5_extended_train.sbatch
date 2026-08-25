#!/bin/bash
#SBATCH --job-name=p5_ext_gnn
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=7-00:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --array=0-24%4
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2/results/extended_campaign_20260825/slurm_%A_%a.out
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2/results/extended_campaign_20260825/slurm_%A_%a.err

set -eo pipefail
ROOT=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2
cd "$ROOT"
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

# Task order: partition-major, then configuration.
# Each task owns one output directory and is independently resumable.
# 5 partitions x 5 configurations = 25 tasks.
PARTITIONS=(canonical_random canonical_scaffold novel_101 novel_202 novel_303)
MODELS=(GIN GIN-TFP GIN-TFP GIN-TNE GIN-TNE)
MODES=(native native permuted native permuted)
PARTITION_INDEX=$((SLURM_ARRAY_TASK_ID / 5))
CONFIG_INDEX=$((SLURM_ARRAY_TASK_ID % 5))
PARTITION=${PARTITIONS[$PARTITION_INDEX]}
MODEL=${MODELS[$CONFIG_INDEX]}
DESCRIPTOR_MODE=${MODES[$CONFIG_INDEX]}

mkdir -p results/extended_campaign_20260825/slurm_logs
printf 'job=%s task=%s partition=%s model=%s descriptor_mode=%s host=%s start=%s\n' \
  "$SLURM_ARRAY_JOB_ID" "$SLURM_ARRAY_TASK_ID" "$PARTITION" "$MODEL" "$DESCRIPTOR_MODE" "$(hostname)" "$(date -u +%FT%TZ)" \
  > "results/extended_campaign_20260825/slurm_logs/task_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.meta"

python -u scripts/p5_extended_campaign.py train \
  --partition "$PARTITION" \
  --model "$MODEL" \
  --descriptor-mode "$DESCRIPTOR_MODE" \
  --device cuda

printf 'completed=%s\n' "$(date -u +%FT%TZ)" >> "results/extended_campaign_20260825/slurm_logs/task_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.meta"
