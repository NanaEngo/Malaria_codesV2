#!/bin/bash
# Watcher: wait for the local K76A mdrun to finish, then submit the SLURM
# QC->conditional-MM-GBSA chain. Poll-only; no compute. Logs to the run dir.
set -uo pipefail
PROJ=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
SYS=PP-01_PfCRT_K76A
RUN=$PROJ/results/md_systems/set_c_preparation_20260812_v1/$SYS/runs/20260825T063226Z/replicate_1
LOG=$RUN/post_run_chain.log
echo "$(date -u +%FT%TZ) watcher started (pid $$)" >> "$LOG"

while true; do
  ST=$(python3 - "$RUN/production_provenance.json" <<'PY' 2>/dev/null
import json, sys
print(json.load(open(sys.argv[1])).get("status", ""))
PY
)
  FIN=$(grep -c "Finished mdrun" "$RUN/production.log" 2>/dev/null || echo 0)
  if [ "$ST" = "PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC" ] || [ "${FIN:-0}" -ge 1 ]; then
    break
  fi
  sleep 300
done

# Grace period so the workflow parent can flip provenance after mdrun exit.
for i in $(seq 1 12); do
  ST=$(python3 - "$RUN/production_provenance.json" <<'PY' 2>/dev/null
import json, sys
print(json.load(open(sys.argv[1])).get("status", ""))
PY
)
  [ "$ST" = "PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC" ] && break
  sleep 60
done

if [ "$ST" != "PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC" ]; then
  echo "$(date -u +%FT%TZ) PROVENANCE_NOT_UPDATED ($ST) — aborting fail-closed, no QC submitted" >> "$LOG"
  exit 5
fi

cd "$PROJ"
JID=$(sbatch scripts/p2_setc_single_rerun_qc_mmgbsa.sbatch "$SYS" \
  results/md_systems/set_c_preparation_20260812_v1/$SYS/runs/20260825T063226Z/replicate_1 \
  | awk '{print $4}')
echo "$(date -u +%FT%TZ) QC+MMGBSA chain submitted: job $JID" >> "$LOG"
