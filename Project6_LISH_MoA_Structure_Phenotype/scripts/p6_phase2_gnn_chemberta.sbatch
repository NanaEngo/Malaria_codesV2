#!/bin/bash
#SBATCH --job-name=p6_phase2
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=12
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --array=0-3%4
#SBATCH --output=logs/p6_phase2_%A_%a.log
#SBATCH --error=logs/p6_phase2_%A_%a.err

set -euo pipefail
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-12}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-12}"
export P6_NUM_WORKERS="${P6_NUM_WORKERS:-2}"
ROOT=/home/nanaengo/Malaria_codesV2/Project6_LISH_MoA_Structure_Phenotype
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$ROOT"
mkdir -p logs results/p6_phase2

MODELS=(GIN GIN-TFP GIN-TNE CHEMBERTA)
MODEL=${MODELS[$SLURM_ARRAY_TASK_ID]}
META="results/p6_phase2/task_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.meta"
START=$(date -u +%FT%TZ)
printf 'job=%s task=%s model=%s host=%s start=%s\n' \
  "${SLURM_ARRAY_JOB_ID:-unknown}" "${SLURM_ARRAY_TASK_ID:-unknown}" "$MODEL" "$(hostname)" "$START" > "$META"

if [[ "$MODEL" != "GIN" && ! -s results/p6_phase2/p6_tfp_tne_descriptors.npz ]]; then
  echo "Missing descriptor cache; fail closed. Prepare it before submitting the array." >&2
  exit 2
fi

case "$MODEL" in
  GIN|GIN-TFP|GIN-TNE)
    "$PY" scripts/p6_phase2_gnn.py --model "$MODEL" --split collision_group
    ;;
  CHEMBERTA)
    "$PY" scripts/p6_phase2_chemberta.py --split collision_group
    ;;
esac

printf 'completed=%s\n' "$(date -u +%FT%TZ)" >> "$META"
