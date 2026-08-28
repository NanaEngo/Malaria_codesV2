#!/bin/bash
# P2 — Wait for the declared repair to finish, then run the 312-record
# audit -> aggregate -> RRS chain (fail-closed). The repair
# (p2_external_docking_repair.sh) is launched separately; this watcher only
# mediates the downstream chain so it does not attempt a parallel repair.
set -euo pipefail

P2ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$P2ROOT/scripts"
AUDIT_OUT="$P2ROOT/results/robustness_transfer_20260827/external_docking_integrity_audit_20260827.json"
AGG_OUT="$P2ROOT/results/robustness_transfer_20260827/external_docking_aggregate_20260827/aggregate_manifest.json"

echo "=== Waiting for repair process to finish (pid arg: $1) ==="
REPAIR_PID="${1:-}"
if [[ -n "$REPAIR_PID" ]]; then
    while kill -0 "$REPAIR_PID" 2>/dev/null; do
        echo "$(date -u +%H:%M:%S) — repair still running (pid $REPAIR_PID)"
        sleep 120
    done
    echo "Repair process finished."
else
    echo "No repair pid given; proceeding to audit (assumes repair already done)."
fi

echo "=== [1/4] Integrity audit ==="
python "$SCRIPTS/p2_external_docking_integrity_audit.py" || true
status=$(python3 -c "import json; print(json.load(open('$AUDIT_OUT'))['status'])")
expected=$(python3 -c "import json; print(json.load(open('$AUDIT_OUT'))['expected'])")
valid=$(python3 -c "import json; print(json.load(open('$AUDIT_OUT'))['valid'])")
echo "Audit: $status | expected=$expected valid=$valid"
if [ "$status" != "PASS_READY_FOR_AGGREGATION" ]; then
    echo "FATAL: not PASS after repair; aborting (no aggregation). Check /tmp/p2_repair.log"
    exit 2
fi

echo "=== [2/4] Aggregate ==="
python "$SCRIPTS/p2_external_docking_aggregate.py"
agg_status=$(python3 -c "import json; print(json.load(open('$AGG_OUT'))['status'])")
echo "Aggregate status: $agg_status"
if [ "$agg_status" != "READY_FOR_RRS_POSTPROCESSING" ]; then
    echo "FATAL: aggregate not ready; aborting (no RRS)."
    exit 2
fi

echo "=== [3/4] RRS post-processing ==="
python "$SCRIPTS/p2_external_docking_rrs.py"

echo "=== [4/4] External docking replication chain COMPLETE ==="