#!/bin/bash
# P5 — Zenodo package finalization (fail-closed).
# Waits for SLURM job 15617 (light GNN sensitivity) to leave the queue, audits
# the fold-level outputs (25 records/config, finite metrics), rebuilds the
# Zenodo package, and verifies the manifest flips to READY_FOR_UPLOAD.
# The package is NOT uploaded; only staged and verified.
set -euo pipefail

P5ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$P5ROOT/scripts"
RESULTS="$P5ROOT/results"
STAMP="20260827"
OUT="$P5ROOT/zenodo_package_$STAMP"
TARBALL="$P5ROOT/zenodo_package_$STAMP.tar.gz"

CONFIGS=(h64_d02 h256_d01)
EXPECTED_RECORDS=25

echo "=== [1/4] Waiting for job 15617 to complete ==="
while true; do
    if ! squeue -j 15617 -h 2>/dev/null | grep -q .; then
        echo "Job 15617 no longer in queue."
        break
    fi
    echo "$(date -u +%H:%M:%S) — 15617 $(squeue -j 15617 -h -o '%T' 2>/dev/null) (polling every 60 s)"
    sleep 60
done

echo "=== [2/4] Fold-level audit of sensitivity outputs ==="
declare -a MISSING
for cfg in "${CONFIGS[@]}"; do
    csv="$RESULTS/p5_GIN_scaffold_results_sens_$cfg.csv"
    curves="$RESULTS/p5_GIN_scaffold_curves_sens_$cfg.json"
    salience="$RESULTS/p5_GIN_scaffold_salience_sens_$cfg.json"
    ckpt="$RESULTS/p5_GIN_scaffold_ckpt_sens_$cfg.json"
    for f in "$csv" "$curves" "$salience" "$ckpt"; do
        if [[ ! -s "$f" ]]; then
            MISSING+=("$(basename "$f")")
        fi
    done
    if [[ -s "$csv" ]]; then
        n=$(tail -n +2 "$csv" | wc -l)
        nfinite=$(python3 -c "
import csv, math
rows = list(csv.DictReader(open('$csv')))
vals = [float(r['test_auc']) for r in rows if r.get('test_auc') not in (None, '')]
print(len(rows), sum(math.isfinite(v) for v in vals))
")
        nrec=$(echo "$nfinite" | awk '{print $1}')
        nfinite=$(echo "$nfinite" | awk '{print $2}')
        echo "  $cfg: $nrec rows, $nfinite finite AUC"
        if [[ "$nrec" -ne "$EXPECTED_RECORDS" || "$nfinite" -ne "$EXPECTED_RECORDS" ]]; then
            echo "FATAL: $cfg does not meet 25-record finite audit; aborting."
            exit 2
        fi
    fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "FATAL: missing sensitivity files: ${MISSING[*]}; aborting."
    exit 2
fi
echo "Fold-level audit PASS (2 configs x 25 records, finite AUC)."

echo "=== [3/4] Rebuild Zenodo package ==="
python "$SCRIPTS/build_zenodo_package.py"

echo "=== [4/4] Verify manifest + refresh tarball ==="
status=$(python3 -c "import json; print(json.load(open('$OUT/ZENODO_PACKAGE_MANIFEST.json'))['status'])")
pending=$(python3 -c "import json; print(len(json.load(open('$OUT/ZENODO_PACKAGE_MANIFEST.json'))['sensitivity_files_pending']))")
staged=$(python3 -c "import json; print(json.load(open('$OUT/ZENODO_PACKAGE_MANIFEST.json'))['files_staged'])")
echo "Manifest status: $status | staged: $staged | sensitivity pending: $pending"
if [[ "$status" != "READY_FOR_UPLOAD_NOT_UPLOADED" || "$pending" != "0" || "$staged" != "35" ]]; then
    echo "FATAL: package not READY_FOR_UPLOAD; aborting (no tarball refresh)."
    exit 2
fi
rm -f "$TARBALL"
tar -czf "$TARBALL" "$(basename "$OUT")"
echo "Tarball refreshed: $TARBALL ($(stat -c%s "$TARBALL") bytes)"
echo "=== Zenodo package finalization COMPLETE — READY_FOR_UPLOAD (DOI 10.5281/zenodo.19608875) ==="
