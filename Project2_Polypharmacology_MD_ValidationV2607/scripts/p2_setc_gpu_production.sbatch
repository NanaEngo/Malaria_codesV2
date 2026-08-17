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
# Do not submit this launcher directly. The active chain is:
#   15282 (equilibration array) --afterok--> 15287 (fail-closed gate)
# and 15287 submits this production array only after the exact 16/16
# preflight passes. The actual IDs are exported into launch_context.txt.
#
# The %1 throttle is intentional: one A4000 is available. Each task owns an
# explicit system name and writes a task-specific provenance directory. Missing
# or invalid inputs fail closed; no partial task is eligible for MD-RRS.
#
# GPU flags are the measured stable configuration from benchmark 15262 and
# witness 15270: -nb gpu -pme gpu -bonded cpu -update cpu. GPU update/constraints
# are not enabled because that historical path was unstable.

set -euo pipefail

# Check required provenance before Conda/GROMACS initialization so a direct
# or malformed submission fails closed even if the environment is incomplete.
PROJ=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
: "${P2_SETC_ROOT:?FATAL: P2_SETC_ROOT must be explicitly exported}"
: "${P2_GATE_JOB_ID:?FATAL: production requires P2_GATE_JOB_ID from the preflight gate}"
: "${P2_EQUILIBRATION_JOB_ID:?FATAL: production requires P2_EQUILIBRATION_JOB_ID}"
: "${P2_PREFLIGHT_MANIFEST:?FATAL: production requires P2_PREFLIGHT_MANIFEST from the preflight gate}"
: "${P2_GATE_PROVENANCE:?FATAL: production requires P2_GATE_PROVENANCE from the preflight gate}"
[[ "$P2_GATE_JOB_ID" =~ ^[0-9]+$ ]] || { echo "FAIL-CLOSED: invalid P2_GATE_JOB_ID=$P2_GATE_JOB_ID" >&2; exit 92; }
[[ "$P2_EQUILIBRATION_JOB_ID" =~ ^[0-9]+$ ]] || { echo "FAIL-CLOSED: invalid P2_EQUILIBRATION_JOB_ID=$P2_EQUILIBRATION_JOB_ID" >&2; exit 94; }
[ -s "$P2_PREFLIGHT_MANIFEST" ] || { echo "FAIL-CLOSED: missing preflight manifest: $P2_PREFLIGHT_MANIFEST" >&2; exit 93; }
[ -s "$P2_GATE_PROVENANCE" ] || { echo "FAIL-CLOSED: missing gate provenance: $P2_GATE_PROVENANCE" >&2; exit 95; }

ROOT="$(realpath -m "$P2_SETC_ROOT")"
EXPECTED_ROOT="$PROJ/results/md_systems/set_c_preparation_20260812_v1"
[ "$ROOT" = "$EXPECTED_ROOT" ] || { echo "FAIL-CLOSED: production root must be $EXPECTED_ROOT, got $ROOT" >&2; exit 91; }

# Keep nounset disabled only while activating malaria_md: its GROMACS
# GMXRC contains optional variables that are not nounset-safe.
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=8
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
cd "$PROJ"
export P2_SETC_ROOT="$ROOT"

# Runtime guard: the gate provenance must bind this production launch to the
# actual gate, equilibration job, exact root, and hashed 16/16 preflight.
python - "$P2_PREFLIGHT_MANIFEST" "$P2_GATE_PROVENANCE" "$ROOT" "$P2_GATE_JOB_ID" "$P2_EQUILIBRATION_JOB_ID" <<'PY'
import hashlib, json, sys
manifest_path, provenance_path, root, gate_id, eq_id = sys.argv[1:]
manifest = json.load(open(manifest_path))
provenance = json.load(open(provenance_path))
if provenance.get("gate_job_id") != gate_id:
    raise SystemExit("FAIL-CLOSED: gate ID does not match gate provenance")
if provenance.get("equilibration_job_id") != eq_id:
    raise SystemExit("FAIL-CLOSED: equilibration ID does not match gate provenance")
if provenance.get("root") != root:
    raise SystemExit("FAIL-CLOSED: root does not match gate provenance")
if provenance.get("preflight_manifest") != manifest_path:
    raise SystemExit("FAIL-CLOSED: manifest path does not match gate provenance")
sha = hashlib.sha256(open(manifest_path, "rb").read()).hexdigest()
if provenance.get("preflight_manifest_sha256") != sha:
    raise SystemExit("FAIL-CLOSED: preflight manifest hash mismatch")
if manifest.get("status") != "READY_FOR_AUTHORIZED_EXECUTION":
    raise SystemExit(f"FAIL-CLOSED: preflight status={manifest.get('status')!r}")
if manifest.get("ready_system_count") != 16 or manifest.get("required_system_count") != 16:
    raise SystemExit("FAIL-CLOSED: preflight cardinality is not 16/16")
if manifest.get("selected_ids") != ["PP-01", "PP-02"]:
    raise SystemExit(f"FAIL-CLOSED: unexpected candidate panel={manifest.get('selected_ids')!r}")
PY
export P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND

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
printf 'gate_provenance=%s\n' "$P2_GATE_PROVENANCE" >> "$OUT/launch_context.txt"

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
