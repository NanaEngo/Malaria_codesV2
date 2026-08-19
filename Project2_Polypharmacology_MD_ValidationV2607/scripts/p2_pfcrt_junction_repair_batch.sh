#!/bin/bash
# Batch junction repair over all grafted PfCRT candidates.
# Usage: p2_pfcrt_junction_repair_batch.sh <graft_audit.json> [output_root]
set -eo pipefail
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
# GMXRC in malaria_md is not nounset-safe (same fix as the SLURM wrappers).
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u

AUDIT="${1:-results/md_systems/pfcrt_colabfold_gpu_ensemble_grafted_20260811/graft_audit.json}"
OUTROOT="${2:-results/md_systems/pfcrt_junction_repair_ensemble_20260818}"
REF=data/proteins/6UKJ.pdb
MAP=results/md_systems/pfcrt_uniprot_pdb_mapping_20260811.json

mkdir -p "$OUTROOT"
SUMMARY="$OUTROOT/_summary.csv"
echo "candidate,status" > "$SUMMARY"

python - "$AUDIT" "$OUTROOT" "$REF" "$MAP" "$SUMMARY" <<'PY'
import json, subprocess, sys
from pathlib import Path

audit_path, outroot, ref, mapping, summary = map(Path, sys.argv[1:6])
audit = json.loads(audit_path.read_text())
# The grafted candidates live next to the graft audit (same output dir).
graft_dir = audit_path.parent
prediction_dir = Path(audit["prediction_dir"])
records = audit["records"]

results = []
for r in records:
    cand = Path(r["candidate"]).name
    src_model = prediction_dir / r["model"]
    outdir = outroot / cand.replace(".pdb", "")
    cmd = [
        sys.executable, "scripts/p2_pfcrt_junction_repair_openmm.py",
        "--grafted", str(graft_dir / cand),
        "--reference", str(ref),
        "--prediction", str(src_model),
        "--mapping", str(mapping),
        "--output-dir", str(outdir),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    status = "PASS_GEOMETRY" if proc.returncode == 0 else "FAILED"
    # read manifest status if present
    mf = outdir / "junction_repair_audit.json"
    if mf.is_file():
        d = json.loads(mf.read_text())
        status = d.get("status", status)
    results.append((cand, status))
    print(f"{cand}: {status}", flush=True)

with summary.open("w") as fh:
    fh.write("candidate,status\n")
    for cand, status in results:
        fh.write(f"{cand},{status}\n")
passing = sum(1 for _, s in results if s == "PASS_GEOMETRY")
print(f"SUMMARY: {passing}/{len(results)} PASS_GEOMETRY")
PY
