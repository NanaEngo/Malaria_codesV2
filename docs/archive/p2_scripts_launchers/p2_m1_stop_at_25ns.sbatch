#!/usr/bin/env bash
#SBATCH --job-name=p2_m1_stop25
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/logs/slurm/p2_m1_stop25_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/logs/slurm/p2_m1_stop25_%j.log
#SBATCH --time=02:00:00
#SBATCH --partition=production
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
# Stop the M1 continuation (job 15715_0) at 25 ns and run the post-kill QC.
set -u

LOG=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1/production.log
REP=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
TARGET_STEP=12500000   # 25 ns at dt=0.002 ps
JOB=15715_0

echo "[$(date -u +%FT%TZ)] watcher started; target step ${TARGET_STEP} (25 ns)"

while :; do
  if ! squeue -j "$JOB" -h 2>/dev/null | grep -q .; then
    echo "[$(date -u +%FT%TZ)] job ${JOB} no longer in queue"
    break
  fi
  STEP=$(grep -oE 'step [0-9]+' "$LOG" 2>/dev/null | tail -1 | awk '{print $2}')
  if [ -n "${STEP:-}" ] && [ "$STEP" -ge "$TARGET_STEP" ]; then
    echo "[$(date -u +%FT%TZ)] step ${STEP} >= ${TARGET_STEP} -> scancel ${JOB}"
    scancel "$JOB"
    sleep 30
    break
  fi
  sleep 60
done

echo "[$(date -u +%FT%TZ)] running post-kill QC (--termination USER_DECISION --target-ns 25)"
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607 || exit 2
"$PY" scripts/p2_m1_postkill_qc.py \
  --replicate "$REP" \
  --target-ns 25 \
  --termination USER_DECISION \
  --max-frames 100000
RC=$?
echo "[$(date -u +%FT%TZ)] QC exit code: ${RC}"
echo "[$(date -u +%FT%TZ)] watcher done"
exit 0
