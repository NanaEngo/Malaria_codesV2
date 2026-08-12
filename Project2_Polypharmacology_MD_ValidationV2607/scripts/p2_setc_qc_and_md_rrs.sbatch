#!/bin/bash
#SBATCH --job-name=p2_setc_qc_rrs
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --output=logs/p2_setc_qc_rrs_%j.log
#SBATCH --error=logs/p2_setc_qc_rrs_%j.err

# No literal dependency is encoded here. Submit only after recording the actual
# production/equilibration IDs, for example:
#   sbatch --dependency=afterok:${PROD_JOB_ID} \
#     --export=ALL,P2_PRODUCTION_JOB_ID=${PROD_JOB_ID},P2_EQUILIBRATION_JOB_ID=${EQ_JOB_ID},P2_SETC_COHORT_MODE=pilot \
#     scripts/p2_setc_qc_and_md_rrs.sbatch
#
# The default cohort mode is the predeclared 16-system PP-01/PP-02 pilot.
# Set P2_SETC_COHORT_MODE=full only after the complete 17-candidate/136-system
# production contract has been prepared and independently verified.

set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
export PYTHONUNBUFFERED=1

cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
RESULTS_DIR="results/set_c_md"
SCRIPTS_DIR="scripts"
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
COHORT_MODE="${P2_SETC_COHORT_MODE:-pilot}"
PRODUCTION_JOB_ID="${P2_PRODUCTION_JOB_ID:-UNSPECIFIED}"
EQUILIBRATION_JOB_ID="${P2_EQUILIBRATION_JOB_ID:-UNSPECIFIED}"

case "$COHORT_MODE" in
  pilot) MD_OUTPUT="$RESULTS_DIR/md_rrs_pilot_PP01_PP02.csv" ;;
  full)  MD_OUTPUT="$RESULTS_DIR/md_rrs_classification.csv" ;;
  *) echo "FATAL: P2_SETC_COHORT_MODE must be pilot or full" >&2; exit 2 ;;
esac

[[ "$PRODUCTION_JOB_ID" =~ ^[0-9]+$ ]] || {
  echo "FATAL: P2_PRODUCTION_JOB_ID must be supplied from the actual production submission" >&2
  exit 2
}
[[ "$EQUILIBRATION_JOB_ID" =~ ^[0-9]+$ ]] || {
  echo "FATAL: P2_EQUILIBRATION_JOB_ID must be supplied from the actual equilibration submission" >&2
  exit 2
}

# Keep pilot and full QC artifacts disjoint: a later run must not overwrite
# the QC input contract of the other cohort mode.
QC_CSV="$RESULTS_DIR/set_c_trajectory_qc_${COHORT_MODE}.csv"
MANIFEST="$RESULTS_DIR/post_production_manifest_${COHORT_MODE}.json"

write_manifest() {
  local status="$1"
  local qc_rc="$2"
  local md_rc="$3"
  cat > "$MANIFEST" <<MANIFEST_EOF
{
  "schema_version": 3,
  "created_utc": "$TIMESTAMP",
  "cohort_id": "$( [ "$COHORT_MODE" = pilot ] && echo P2_SET_C_MD_RRS_PILOT_PP01_PP02 || echo P2_SET_C_POLYPHARM_17 )",
  "cohort_mode": "$COHORT_MODE",
  "production_job": "$PRODUCTION_JOB_ID",
  "equilibration_job": "$EQUILIBRATION_JOB_ID",
  "qc_script": "scripts/p2_setc_trajectory_qc.py",
  "md_rrs_script": "scripts/p2_setc_md_rrs.py",
  "qc_exit_code": $qc_rc,
  "md_rrs_exit_code": $md_rc,
  "qc_output": "$QC_CSV",
  "md_rrs_output": "$MD_OUTPUT",
  "md_rrs_status": "$status"
}
MANIFEST_EOF
}

echo "=== Post-production chain started: $TIMESTAMP ==="
echo "cohort_mode=$COHORT_MODE production_job=$PRODUCTION_JOB_ID equilibration_job=$EQUILIBRATION_JOB_ID"

# ---- Step 1: Trajectory QC ----
echo "--- Step 1/2: trajectory QC ---"
if python "$SCRIPTS_DIR/p2_setc_trajectory_qc.py"; then
  QC_RC=0
else
  QC_RC=$?
  write_manifest "QC_FAILED" "$QC_RC" 125
  echo "FATAL: trajectory QC failed; manifest=$MANIFEST" >&2
  exit "$QC_RC"
fi

if [ ! -s "$QC_CSV" ]; then
  write_manifest "QC_OUTPUT_MISSING" "$QC_RC" 125
  echo "FATAL: QC CSV not found at $QC_CSV" >&2
  exit 1
fi

echo "QC CSV found: $(wc -l < "$QC_CSV") rows"

# ---- Step 2: MD-RRS classification ----
echo "--- Step 2/2: MD-RRS classification ($COHORT_MODE) ---"
if python "$SCRIPTS_DIR/p2_setc_md_rrs.py" \
    --qc-file "$QC_CSV" \
    --cohort-mode "$COHORT_MODE" \
    --output "$MD_OUTPUT"; then
  MD_RRS_RC=0
else
  MD_RRS_RC=$?
  write_manifest "MD_RRS_FAILED_COHORT_GATE" "$QC_RC" "$MD_RRS_RC"
  echo "FATAL: MD-RRS classification failed; manifest=$MANIFEST" >&2
  exit "$MD_RRS_RC"
fi

write_manifest "COMPUTED_WITH_COHORT_CONTRACT" "$QC_RC" "$MD_RRS_RC"
echo "=== Post-production chain COMPLETE: $(date -u +%Y%m%dT%H%M%SZ) ==="
echo "Manifest: $MANIFEST"
echo "MD-RRS output: $MD_OUTPUT"
