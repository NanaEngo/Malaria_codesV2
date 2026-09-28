#!/usr/bin/env bash
# p2_m1_stop_at_25ns.sh — stop the M1 continuation (job 15715) at 25 ns and run post-kill QC.
# Author decision (30 Aug 2026): M1 target reduced 100 ns -> 25 ns (JCIM does not mandate 100 ns;
# 25 ns is a round, defensible length for the secondary structural-stress pilot; frees ~60 h GPU).
set -u

LOG=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1/production.log
REP=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
TARGET_STEP=12500000   # 25 ns at dt=0.002 ps (25e3 ps / 0.002 = 12,500,000)
JOB=15715_0
OUT=/tmp/m1_stop_at_25ns_watcher.log

echo "[$(date -u +%FT%TZ)] watcher started; target step ${TARGET_STEP} (25 ns)" >> "$OUT"

while :; do
  if ! squeue -j "$JOB" -h 2>/dev/null | grep -q .; then
    echo "[$(date -u +%FT%TZ)] job ${JOB} no longer in queue" >> "$OUT"
    break
  fi
  STEP=$(grep -oE 'step [0-9]+' "$LOG" 2>/dev/null | tail -1 | awk '{print $2}')
  if [ -n "${STEP:-}" ] && [ "$STEP" -ge "$TARGET_STEP" ]; then
    echo "[$(date -u +%FT%TZ)] step ${STEP} >= ${TARGET_STEP} -> scancel ${JOB}" >> "$OUT"
    scancel "$JOB"
    sleep 20
    break
  fi
  sleep 120
done

echo "[$(date -u +%FT%TZ)] running post-kill QC (--termination USER_DECISION --target-ns 25)" >> "$OUT"
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607 && \
  "$PY" scripts/p2_m1_postkill_qc.py \
    --replicate "$REP" \
    --target-ns 25 \
    --termination USER_DECISION \
    --max-frames 100000 >> "$OUT" 2>&1
echo "[$(date -u +%FT%TZ)] QC exit code: $?" >> "$OUT"
echo "[$(date -u +%FT%TZ)] watcher done" >> "$OUT"
