#!/bin/bash
# Single-system rerun chain (Set-C single_rerun_20260825):
#   trajectory QC -> (only if qc_status == PASS) MM-GBSA.
# Protocol identical to the canonical pilot chain:
#   - QC: scripts/p2_setc_trajectory_qc.py, rule setc_p2_minheavy_5A_ge10percent_v1
#   - MM-GBSA: gmx_MMPBSA v1.5, GB OBC2 igb=5, saltcon 0.15 M, 100 frames
# Usage: sbatch scripts/p2_setc_single_rerun_qc_mmgbsa.sbatch <SYSTEM_NAME> <RUN_DIR>
#SBATCH --job-name=p2_setc_rr_qcmm
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=08:00:00
#SBATCH --mem=16G
#SBATCH --output=logs/p2_setc_rr_qcmm_%j.log

# NOTE: no `set -u` — conda activate sources GMXRC which is not nounset-safe (cf. job 15293)
set -epipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
[ $# -eq 2 ] || { echo "usage: $0 <SYSTEM_NAME> <RUN_DIR>" >&2; exit 64; }
SYS="$1"; RUN="$2"

OUTROOT=results/set_c_md/single_rerun_20260825
mkdir -p "$OUTROOT"
CHAIN_LOG="$OUTROOT/chain_log.jsonl"

note() {
  printf '{"utc":"%s","system":"%s","event":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SYS" "$1" >> "$CHAIN_LOG"
}

# Fail-closed completion gate: exactly 5,000,000 steps.
LAST_STEP=$(awk '/^ *[0-9]+ +[0-9]+\.[0-9]+$/{s=$1} END{print s}' "$RUN/production.log")
if [ "$LAST_STEP" != "5000000" ]; then
  echo "FAIL: last logged step is '$LAST_STEP', expected 5000000 — refusing QC" >&2
  note "ABORTED_STEPS_${LAST_STEP}"
  exit 3
fi

export P2_SETC_ROOT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_preparation_20260812_v1
export P2_SETC_QC_OUTPUT="$PWD/$OUTROOT/qc_${SYS}.csv"

note "TRAJECTORY_QC_STARTED"
python scripts/p2_setc_trajectory_qc.py --system "$SYS"

QC_STATUS=$(python - "$P2_SETC_QC_OUTPUT" <<'PY'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
assert len(rows) == 1, f"expected 1 QC row, got {len(rows)}"
print(rows[0]["qc_status"])
PY
)
echo "QC status: $QC_STATUS"
note "TRAJECTORY_QC_${QC_STATUS}"

if [ "$QC_STATUS" != "PASS" ]; then
  echo "QC did not pass ($QC_STATUS) — MM-GBSA not launched (fail-closed)." >&2
  exit 4
fi

note "MMGBSA_STARTED"
python scripts/p2_setc_mmgbsa_single.py "$SYS" "$RUN"
note "MMGBSA_FINISHED"
