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
#SBATCH --dependency=afterok:15111

# Submit from Project2_Polypharmacology_MD_ValidationV2607/:
#   sbatch scripts/p2_setc_qc_and_md_rrs.sbatch

# =============================================================================
# Post-production chain: Set-C MD trajectory QC  ->  MD-RRS classification
# Launched after array 15111 (16×10 ns production) completes.
# =============================================================================
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

set -euo pipefail
export PYTHONUNBUFFERED=1

cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
RESULTS_DIR="results/set_c_md"
SCRIPTS_DIR="scripts"
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)

echo "=== Post-production chain started: $TIMESTAMP ==="

# ---- Step 1: Trajectory QC ----
echo "--- Step 1/2: trajectory QC (uses hardcoded OUTPUT path in script) ---"
python "$SCRIPTS_DIR/p2_setc_trajectory_qc.py"

QC_RC=$?
echo "Trajectory QC exit code: $QC_RC"
if [ $QC_RC -ne 0 ]; then
    echo "FATAL: trajectory QC failed"
    exit $QC_RC
fi

# Verify QC CSV exists
QC_CSV="$RESULTS_DIR/set_c_trajectory_qc.csv"
if [ ! -f "$QC_CSV" ]; then
    echo "FATAL: QC CSV not found at $QC_CSV"
    exit 1
fi
echo "QC CSV found: $(wc -l < "$QC_CSV") rows"

# ---- Step 2: MD-RRS classification ----
echo "--- Step 2/2: MD-RRS classification ---"
python "$SCRIPTS_DIR/p2_setc_md_rrs.py" \
    --qc-file "$QC_CSV"

MD_RRS_RC=$?
echo "MD-RRS classification exit code: $MD_RRS_RC"
if [ $MD_RRS_RC -ne 0 ]; then
    echo "FATAL: MD-RRS classification failed"
    exit $MD_RRS_RC
fi

# ---- Provenance manifest ----
cat > "$RESULTS_DIR/post_production_manifest.json" <<MANIFEST_EOF
{
  "schema_version": 2,
  "created_utc": "$TIMESTAMP",
  "cohort_id": "P2_SET_C_POLYPHARM_17",
  "production_job": "15111",
  "equilibration_job": "15106",
  "qc_script": "p2_setc_trajectory_qc.py",
  "md_rrs_script": "p2_setc_md_rrs.py",
  "qc_exit_code": $QC_RC,
  "md_rrs_exit_code": $MD_RRS_RC,
  "qc_output": "results/set_c_md/set_c_trajectory_qc.csv",
  "md_rrs_output": "results/set_c_md/md_rrs_classification.csv",
  "md_rrs_status": "COMPUTED"
}
MANIFEST_EOF

echo "=== Post-production chain COMPLETE: $(date -u +%Y%m%dT%H%M%SZ) ==="