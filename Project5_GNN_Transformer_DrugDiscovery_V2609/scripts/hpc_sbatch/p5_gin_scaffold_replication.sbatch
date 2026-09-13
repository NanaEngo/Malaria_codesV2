#!/bin/bash
# P5 — GIN scaffold replication (action 2b, rerun): the first scaffold attempt
# crashed on a deepchem import (jax/numpy incompatibility) now guarded in
# p5_data.py. Outputs carry the "_replic" tag; canonical files untouched.
#SBATCH --job-name=p5_gin_scr
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=logs/p5_gin_scr_%j.log
#SBATCH --error=logs/p5_gin_scr_%j.err

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery
mkdir -p logs/p5_gin_repl

set -e
echo "=== GIN scaffold replication (deepchem-guard fixed) ==="
python scripts/p5_benchmark.py --model GIN --split scaffold --device cuda --tag _replic 2>&1 | tee logs/p5_gin_repl/stdout_scaffold.log
echo "=== GIN scaffold replication DONE ==="
