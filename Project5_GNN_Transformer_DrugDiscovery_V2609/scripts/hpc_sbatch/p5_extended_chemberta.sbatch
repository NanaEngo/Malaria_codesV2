#!/bin/bash
#SBATCH --job-name=p5_cbta_ext
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=7-00:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --array=0-4%4
#SBATCH --chdir=/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2609
#SBATCH --output=results/extended_campaign_20260825/chemberta/slurm_%A_%a.out
#SBATCH --error=results/extended_campaign_20260825/chemberta/slurm_%A_%a.err

set -euo pipefail
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
PARTITIONS=(canonical_random canonical_scaffold novel_101 novel_202 novel_303)
PARTITION=${PARTITIONS[$SLURM_ARRAY_TASK_ID]}
mkdir -p results/extended_campaign_20260825/chemberta
exec /home/nanaengo/miniforge3/envs/malaria_md/bin/python3 scripts/p5_extended_chemberta.py --partition "$PARTITION" --device cuda
