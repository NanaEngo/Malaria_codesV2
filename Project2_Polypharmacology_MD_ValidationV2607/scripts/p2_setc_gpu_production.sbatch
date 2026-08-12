#!/bin/bash
#SBATCH --job-name=p2_setc_gpu_prod
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --array=0-15%1
#SBATCH --output=logs/p2_setc_gpu_prod_%A_%a.log
#SBATCH --error=logs/p2_setc_gpu_prod_%A_%a.err

# Set-C pilot GPU production: PP-01/PP-02 x PfDHFR/PfCRT mutation states.
#
# Submit only after the actual equilibration array has produced npt.gro/npt.cpt
# and all 16 system manifests pass the read-only workflow preflight:
#   sbatch --dependency=afterany:<EQ_JOB_ID> scripts/p2_setc_gpu_production.sbatch
#
# The %1 throttle is intentional: one A4000 is available. Each task owns an
# explicit system name and writes a task-specific provenance directory. Missing
# or invalid inputs fail closed; no partial task is eligible for MD-RRS.
#
# GPU flags are the measured stable configuration from benchmark 15262 and
# witness 15270: -nb gpu -pme gpu -bonded cpu -update cpu. GPU update/constraints
# are not enabled because that historical path was unstable.

set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=8
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
export P2_SETC_ROOT="${P2_SETC_ROOT:-/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c}"
export P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND

PROJ=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
cd "$PROJ"

SYSTEMS=(
  PP-01_PfDHFR_WT PP-01_PfDHFR_N51I PP-01_PfDHFR_C59R PP-01_PfDHFR_S108N PP-01_PfDHFR_I164L
  PP-01_PfCRT_WT PP-01_PfCRT_K76T PP-01_PfCRT_K76A
  PP-02_PfDHFR_WT PP-02_PfDHFR_N51I PP-02_PfDHFR_C59R PP-02_PfDHFR_S108N PP-02_PfDHFR_I164L
  PP-02_PfCRT_WT PP-02_PfCRT_K76T PP-02_PfCRT_K76A
)
SYS="${SYSTEMS[$SLURM_ARRAY_TASK_ID]}"
OUT="$PWD/results/set_c_md/gpu_pilot_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$OUT"

# The shared guard validates the explicit execution authorization and binary.
source "$PWD/scripts/md_execution_guard.sh"
md_guard_parse --execute
md_guard_require_authorization

printf 'system=%s\narray_job=%s\narray_task=%s\nbackend=gpu_mixed\ngate_job_id=%s\nequilibration_job_id=%s\npreflight_manifest=%s\n' \
  "$SYS" "$SLURM_ARRAY_JOB_ID" "$SLURM_ARRAY_TASK_ID" \
  "${P2_GATE_JOB_ID:-UNKNOWN}" "${P2_EQUILIBRATION_JOB_ID:-UNKNOWN}" \
  "${P2_PREFLIGHT_MANIFEST:-UNKNOWN}" > "$OUT/launch_context.txt"

python scripts/p2_setc_md_workflow.py \
  --n-candidates 2 \
  --targets PfDHFR PfCRT \
  --target-ns 10 \
  --replicates 1 \
  --backend gpu \
  --gpu-id 0 \
  --ntomp 8 \
  --system-name "$SYS" \
  --output-dir "$OUT" \
  --auto-approved \
  --execute

printf 'terminal_status=PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC\n' >> "$OUT/launch_context.txt"
