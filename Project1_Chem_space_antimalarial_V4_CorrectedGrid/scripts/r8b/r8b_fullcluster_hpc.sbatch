#!/bin/bash
#SBATCH --job-name=r8b_fullcluster
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Projet1_Chem_space_antimalarialV2607/logs/r8b_fullcluster/r8b_fullcluster_%j.out
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Projet1_Chem_space_antimalarialV2607/logs/r8b_fullcluster/r8b_fullcluster_%j.err

# ======================================================================
# R8-B Full-Cluster Rescoring — HPC Slurm submission
# Project 1: JCIM Manuscript (V2607)
# Runs: Full fingerprinting + Tanimoto cluster extraction + Vina docking
# ======================================================================

set -euo pipefail

# Environment
source /home/nanaengo/miniconda3/etc/profile.d/conda.sh
conda activate malaria_md

# Paths
PROJECT_ROOT="/home/nanaengo/Malaria_codesV2/Projet1_Chem_space_antimalarialV2607"
SCRIPT_DIR="${PROJECT_ROOT}/scripts/r8b"
OUTPUT_DIR="${PROJECT_ROOT}/results/r8b/fullcluster_rescoring"
LOG_DIR="${PROJECT_ROOT}/logs/r8b_fullcluster"

mkdir -p "${OUTPUT_DIR}" "${LOG_DIR}"

# Print job info
echo "============================================================"
echo "R8-B Full-Cluster Rescoring started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "CPUs: ${SLURM_CPUS_PER_TASK}"
echo "============================================================"

cd "${PROJECT_ROOT}"

# Run the pipeline
python scripts/r8b/r8b_fullcluster_rescoring.py \
    --tanimoto 0.50 \
    --n-clusters 5

echo "============================================================"
echo "R8-B Full-Cluster Rescoring completed: $(date)"
echo "============================================================"