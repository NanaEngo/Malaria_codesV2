#!/bin/bash
# P2 — External docking finalization chain (fail-closed).
# Runs ONLY when the 15605 array is COMPLETE:
#   audit -> (declared repair of EXT-008/EXT-019 if they are the only missing)
#   -> audit -> aggregate -> RRS.
# Each stage gates the next; any failure aborts with a non-zero exit code and
# no partial RRS claims are produced.
set -euo pipefail

P2ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$P2ROOT/scripts"
AUDIT_OUT="$P2ROOT/results/robustness_transfer_20260827/external_docking_integrity_audit_20260827.json"
AGG_OUT="$P2ROOT/results/robustness_transfer_20260827/external_docking_aggregate_20260827/aggregate_manifest.json"

echo "=== [1/5] Waiting for array 15605 to complete ==="
while true; do
    if ! squeue -j 15605 -h 2>/dev/null | grep -q .; then
        echo "Array 15605 no longer in queue."
        break
    fi
    running=$(squeue -j 15605 -h -t RUNNING 2>/dev/null | wc -l)
    pending=$(squeue -j 15605 -h -t PENDING 2>/dev/null | wc -l)
    echo "$(date -u +%H:%M:%S) — RUNNING=$running PENDING=$pending (polling every 60 s)"
    sleep 60
done

echo "=== [2/5] Integrity audit (first pass) ==="
python "$SCRIPTS/p2_external_docking_integrity_audit.py" || true
status=$(python3 -c "import json; print(json.load(open('$AUDIT_OUT'))['status'])")
echo "Audit status: $status"

if [ "$status" != "PASS_READY_FOR_AGGREGATION" ]; then
    echo "=== [3/5] Declared repair of EXT-008 / EXT-019 (if they are the only gaps) ==="
    python3 - "$AUDIT_OUT" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
missing = {x["ligand"] for x in m["missing"]}
invalid = {x["ligand"] for x in m["invalid"]}
gaps = missing | invalid
if gaps <= {"EXT-008", "EXT-019"} and gaps:
    print("REPAIR_NEEDED")
elif not gaps:
    print("NO_GAPS")
else:
    print("UNEXPECTED_GAPS:" + ",".join(sorted(gaps)))
PY
    repair_status=$(python3 - "$AUDIT_OUT" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
missing = {x["ligand"] for x in m["missing"]}
invalid = {x["ligand"] for x in m["invalid"]}
gaps = missing | invalid
if gaps <= {"EXT-008", "EXT-019"} and gaps:
    print("REPAIR_NEEDED")
elif not gaps:
    print("NO_GAPS")
else:
    print("UNEXPECTED_GAPS:" + ",".join(sorted(gaps)))
PY
)
    if [ "$repair_status" = "REPAIR_NEEDED" ]; then
        echo "Repairing EXT-008 + EXT-019 (16 states)..."
        bash "$SCRIPTS/p2_external_docking_repair.sh"
        echo "=== Re-audit after repair ==="
        python "$SCRIPTS/p2_external_docking_integrity_audit.py"
        status=$(python3 -c "import json; print(json.load(open('$AUDIT_OUT'))['status'])")
        echo "Audit status after repair: $status"
    elif [ "$repair_status" = "UNEXPECTED_GAPS" ]; then
        echo "FATAL: audit blocked by ligands other than EXT-008/EXT-019; aborting."
        exit 2
    fi
fi

if [ "$status" != "PASS_READY_FOR_AGGREGATION" ]; then
    echo "FATAL: integrity audit not PASS after repair; aborting (no aggregation)."
    exit 2
fi

echo "=== [4/5] Aggregate ==="
python "$SCRIPTS/p2_external_docking_aggregate.py"
agg_status=$(python3 -c "import json; print(json.load(open('$AGG_OUT'))['status'])")
echo "Aggregate status: $agg_status"
if [ "$agg_status" != "READY_FOR_RRS_POSTPROCESSING" ]; then
    echo "FATAL: aggregate not ready; aborting (no RRS)."
    exit 2
fi

echo "=== [5/5] RRS post-processing ==="
python "$SCRIPTS/p2_external_docking_rrs.py"

echo "=== External docking replication chain COMPLETE ==="
