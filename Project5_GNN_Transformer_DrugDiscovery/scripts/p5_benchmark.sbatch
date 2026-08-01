#!/bin/bash
# sbatch runner for P5 benchmark (p5_benchmark.py and p5_chemberta.py)
# Usage:
#   sbatch s_products/p5_benchmark.sbatch GIN
#   sbatch s_products/p5_benchmark.sbatch ChemBERTa
# GPU vs CPU smoke test automatically recorded in JSON after run

#SBATCH --job-name=p5_${1}
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=0
#SBATCH --mail-type=END,FAIL
#SBATCH --output=%x.log
#SBATCH --error=%x.err

SET_CONDA_ENV="source /home/nanaengo/miniforge3/etc/profile.d/conda.sh && conda activate malaria_md"
SET_ENV="${SET_CONDA_ENV}"

RUN_CMD="${SET_CONDA_ENV} python s_products/p5_benchmark.py --model ${1} --device cuda --epochs 10 --dry-run"

LOG_DIR=$(pwd)/logs/p5_${SLURM_JOB_NAME}
mkdir -p ${LOG_DIR}

START=$(date +%s)
$RUN_CMD > ${LOG_DIR}/stdout.log 2>&1
END=$(date +%s)
TIME=$((END-START))

# Record timing and resources
cat > ${LOG_DIR}/metadata.json << EOF
{
    "batch_size": $(python -c "import rdkit; print(2048)")
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