#!/bin/bash
# P5 — Public-dataset benchmark on ChEMBL malaria (action 4): ECFP4-RF vs GIN,
# random + scaffold splits, same protocol as the canonical P5 benchmark.
#SBATCH --job-name=p5_pub_bench
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=20:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=logs/p5_pub_bench_%j.log
#SBATCH --error=logs/p5_pub_bench_%j.err

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery
mkdir -p logs

set -e
# DISJOINT dataset: P5-panel-overlap molecules (180) excluded so the public
# benchmark is an independent generalization test (labels: ChEMBL experimental
# IC50/EC50, not Ersilia predictions).
echo "=== [1/2] Public benchmark (disjoint): random split ==="
python scripts/p5_public_benchmark.py --csv results/p5_public_chembl_malaria_disjoint.csv --split random --device cuda 2>&1 | tail -30
echo "=== [2/2] Public benchmark (disjoint): scaffold split ==="
python scripts/p5_public_benchmark.py --csv results/p5_public_chembl_malaria_disjoint.csv --split scaffold --device cuda 2>&1 | tail -30
echo "=== Public benchmark DONE ==="
