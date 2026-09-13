#!/bin/bash
# P5 — GIN computational replication (action 2b): re-run GIN on frozen splits
# with output tag "_replic" so canonical files are never overwritten.
#SBATCH --job-name=p5_gin_repl
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=logs/p5_gin_repl_%j.log
#SBATCH --error=logs/p5_gin_repl_%j.err

LOG_DIR=$(pwd)/logs/p5_gin_repl
mkdir -p ${LOG_DIR}

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

set -e
echo "=== [1/2] GIN random replication ==="
python scripts/p5_benchmark.py --model GIN --split random --device cuda --tag _replic 2>&1 | tee ${LOG_DIR}/stdout_random.log
echo "=== [2/2] GIN scaffold replication ==="
python scripts/p5_benchmark.py --model GIN --split scaffold --device cuda --tag _replic 2>&1 | tee ${LOG_DIR}/stdout_scaffold.log
echo "=== GIN replication DONE ==="
