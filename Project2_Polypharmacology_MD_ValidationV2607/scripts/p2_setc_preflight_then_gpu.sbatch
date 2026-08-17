#!/bin/bash
#SBATCH --job-name=p2_setc_gate_gpu
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --mem=8G
#SBATCH --output=logs/p2_setc_gate_gpu_%j.log
#SBATCH --error=logs/p2_setc_gate_gpu_%j.err

# Fail-closed transition: equilibration -> aggregate preflight -> GPU array.
# This job is submitted with --dependency=afterok:<equilibration-job-id>.
# It never promotes a partial panel and never launches GPU production when
# the exact 16-system contract is not READY.
set -euo pipefail

# Validate lineage inputs before Conda/GROMACS initialization.
: "${P2_EQUILIBRATION_JOB_ID:?FATAL: gate requires the actual equilibration job ID}"
[[ "$P2_EQUILIBRATION_JOB_ID" =~ ^[0-9]+$ ]] || {
  echo "FAIL-CLOSED: invalid P2_EQUILIBRATION_JOB_ID=$P2_EQUILIBRATION_JOB_ID" >&2
  exit 22
}

# The malaria_md activation scripts source GROMACS' GMXRC, which references
# optional shell variables that are not nounset-safe. Keep errexit/pipefail,
# but suspend nounset only for this controlled environment initialization.
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u

PROJECT_DIR=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
: "${P2_SETC_ROOT:?FATAL: P2_SETC_ROOT must be explicitly exported}"
ROOT="$(realpath -m "$P2_SETC_ROOT")"
EXPECTED_ROOT="$PROJECT_DIR/results/md_systems/set_c_preparation_20260812_v1"
[ "$ROOT" = "$EXPECTED_ROOT" ] || { echo "FAIL-CLOSED: gate root must be $EXPECTED_ROOT, got $ROOT" >&2; exit 91; }
PRE_OUT="$PROJECT_DIR/results/set_c_md/preflight_after_equilibration_${SLURM_JOB_ID}"
mkdir -p "$PRE_OUT" "$PROJECT_DIR/logs"
cd "$PROJECT_DIR"
export P2_SETC_ROOT="$ROOT"

python scripts/p2_setc_md_workflow.py \
  --n-candidates 2 \
  --targets PfDHFR PfCRT \
  --target-ns 10 \
  --replicates 1 \
  --backend gpu \
  --output-dir "$PRE_OUT"

MANIFEST="$PRE_OUT/set_c_md_execution_manifest.json"
[ -s "$MANIFEST" ] || { echo "FAIL-CLOSED: preflight manifest missing: $MANIFEST" >&2; exit 20; }

READY=$(python - "$MANIFEST" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
print(p.get("ready_system_count", -1))
PY
)
REQUIRED=$(python - "$MANIFEST" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
print(p.get("required_system_count", -1))
PY
)
STATUS=$(python - "$MANIFEST" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
print(p.get("status", "UNKNOWN"))
PY
)

# The GPU launcher has a fixed 16-system pilot panel.  Refuse any preflight
# whose candidate IDs do not match that exact panel, even if its cardinality
# happens to be 16.
python - "$MANIFEST" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
expected = ["PP-01", "PP-02"]
if p.get("selected_ids") != expected:
    raise SystemExit(
        f"FAIL-CLOSED: preflight candidate panel {p.get('selected_ids')!r} "
        f"does not equal production panel {expected!r}"
    )
PY

printf 'equilibration_job_id=%s\nroot=%s\npreflight_manifest=%s\nready=%s\nrequired=%s\nstatus=%s\n' \
  "${P2_EQUILIBRATION_JOB_ID:-UNKNOWN}" "$ROOT" "$MANIFEST" "$READY" "$REQUIRED" "$STATUS" \
  > "$PRE_OUT/gate_context.txt"

if [ "$STATUS" != "READY_FOR_AUTHORIZED_EXECUTION" ] || [ "$READY" != "16" ] || [ "$REQUIRED" != "16" ]; then
  echo "FAIL-CLOSED: Set-C preflight is $READY/$REQUIRED ($STATUS); GPU production not submitted." >&2
  exit 21
fi

PREFLIGHT_SHA256=$(sha256sum "$MANIFEST" | awk '{print $1}')
GATE_PROVENANCE="$PRE_OUT/gate_provenance.json"
python - "$GATE_PROVENANCE" "$MANIFEST" "$PREFLIGHT_SHA256" <<'PY'
import json, os, sys
out, manifest, manifest_sha = sys.argv[1:]
with open(out, "w") as fh:
    json.dump({
        "gate_job_id": os.environ["SLURM_JOB_ID"],
        "equilibration_job_id": os.environ.get("P2_EQUILIBRATION_JOB_ID", "UNKNOWN"),
        "root": os.environ["P2_SETC_ROOT"],
        "preflight_manifest": manifest,
        "preflight_manifest_sha256": manifest_sha,
        "status": "READY_FOR_AUTHORIZED_EXECUTION",
        "ready_system_count": 16,
        "required_system_count": 16,
    }, fh, indent=2)
PY

PROD=$(sbatch --parsable \
  --export=ALL,P2_SETC_ROOT="$ROOT",P2_GATE_JOB_ID="$SLURM_JOB_ID",P2_EQUILIBRATION_JOB_ID="${P2_EQUILIBRATION_JOB_ID:-UNKNOWN}",P2_PREFLIGHT_MANIFEST="$MANIFEST",P2_GATE_PROVENANCE="$GATE_PROVENANCE" \
  scripts/p2_setc_gpu_production.sbatch)

echo "PREFLIGHT_STATUS=PASS"
echo "PRODUCTION_JOB_ID=$PROD"
echo "PRODUCTION_ROOT=$ROOT"
echo "PREFLIGHT_MANIFEST=$MANIFEST"
printf 'production_job_id=%s\n' "$PROD" >> "$PRE_OUT/gate_context.txt"
