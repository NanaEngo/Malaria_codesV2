#!/bin/bash
# P2 — External docking finalization chain (fail-closed).
# Runs ONLY when the 15605 array is COMPLETE:
#   audit -> (declared repair of the systematic prep failures: salt-strip,
#             embedding-fallback, and EXT-007 time-limit partial)
#   -> audit -> aggregate -> RRS.
# Each stage gates the next; any failure aborts with a non-zero exit code and
# no partial RRS claims are produced.
set -euo pipefail

P2ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$P2ROOT/scripts"
AUDIT_OUT="$P2ROOT/results/robustness_transfer_20260827/external_docking_integrity_audit_20260827.json"
AGG_OUT="$P2ROOT/results/robustness_transfer_20260827/external_docking_aggregate_20260827/aggregate_manifest.json"

# The exact set of ligands for which a DECLARED, deterministic repair exists
# (arrays 15605 prep failures). This is a closed set: any OTHER missing ligand
# aborts the chain (no silent repair of an undeclared failure).
# NOTE: EXT-039 is intentionally NOT here — it is a DECLARED EMBED_FAILURE
# (see the repair script + ledger): its 8 states are excluded from the audit's
# expected panel (312 = 39 ligands x 8 states), so it never appears as a gap.
REPAIRABLE="EXT-007 EXT-008 EXT-019 EXT-021 EXT-032 EXT-033 EXT-036 EXT-037 EXT-038"

classify_gaps() {
  python3 - "$AUDIT_OUT" "$REPAIRABLE" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
reparable = set(sys.argv[2].split())
missing = {x["ligand"] for x in m["missing"]}
invalid = {x["ligand"] for x in m["invalid"]}
gaps = missing | invalid
if not gaps:
    print("NO_GAPS")
elif gaps <= reparable:
    print("REPAIR_NEEDED")
else:
    print("UNEXPECTED_GAPS:" + ",".join(sorted(gaps)))
PY
}

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

# --- [3/5] Declared repair (generalized) ---------------------------------
if [ "$status" != "PASS_READY_FOR_AGGREGATION" ]; then
    echo "=== [3/5] Declared repair of the systematic prep failures ==="
    repair_status=$(classify_gaps)
    echo "Gap classification: $repair_status"

    if [ "$repair_status" = "REPAIR_NEEDED" ]; then
        echo "Running generalized repair for: $(echo "$REPAIRABLE")"
        bash "$SCRIPTS/p2_external_docking_repair.sh"
        echo "=== Re-audit after repair ==="
        python "$SCRIPTS/p2_external_docking_integrity_audit.py"
        status=$(python3 -c "import json; print(json.load(open('$AUDIT_OUT'))['status'])")
        echo "Audit status after repair: $status"
    elif [ "$repair_status" = "UNEXPECTED_GAPS" ]; then
        extra=${repair_status#UNEXPECTED_GAPS:}
        echo "FATAL: audit blocked by ligands outside the declared repairable set: $extra"
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