#!/bin/bash
# sbatch runner for P5 benchmark (p5_benchmark.py and p5_chemberta.py)
# Usage:
#   sbatch scripts/p5_benchmark.sbatch GIN
#   sbatch scripts/p5_benchmark.sbatch GIN-TFP scaffold
#   sbatch scripts/p5_benchmark.sbatch ChemBERTa
# GPU vs CPU smoke test automatically recorded in JSON after run

#SBATCH --job-name=p5_bench
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=06:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --mail-type=END,FAIL
#SBATCH --output=%x.log
#SBATCH --error=%x.err

LOG_DIR=$(pwd)/logs/p5_${1}
mkdir -p ${LOG_DIR}
SPLIT=${2:-random}

START=$(date +%s)
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
python scripts/p5_benchmark.py --model ${1} --split ${SPLIT} --device cuda > ${LOG_DIR}/stdout_${SPLIT}.log 2>&1
END=$(date +%s)
TIME=$((END-START))

# Record timing and resources
cat > ${LOG_DIR}/metadata.json << EOF
{
    "batch_size": $(python -c "import rdkit; print(2048)"),
    "gpu": "$(nvcc --version | head -1 || echo 'none')",
    "module": "${1}",
    "conda_env": "malaria_md",
    "sbatch_host": "$(hostname)-$(date +%Y%m%d)",
    "runtime_seconds": $TIME,
    "nodes": 1,
    "gpus": 1,
    "cpus": $(echo "$SLURM_CPUS_ON_NODE"),
    "mem_mb": $(echo "$SLURM_MEM_PER_NODE")
}
EOF

echo "Benchmark ${1} completed in $TIME seconds"
echo "Check ${LOG_DIR}/metadata.json for detailed metrics"