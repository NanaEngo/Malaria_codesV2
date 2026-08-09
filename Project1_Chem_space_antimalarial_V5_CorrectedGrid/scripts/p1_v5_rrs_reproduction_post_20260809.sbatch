#!/usr/bin/env bash
#SBATCH --job-name=p1v5_rrs_post
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=logs/p1_v5_rrs_post_%j.log
#SBATCH --error=logs/p1_v5_rrs_post_%j.err
set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock

ROOT=/home/nanaengo/Malaria_codesV2
V5=$ROOT/Project1_Chem_space_antimalarial_V5_CorrectedGrid
RUN_ROOT=${RUN_ROOT:?set RUN_ROOT to the isolated absolute output directory}
cd "$V5"

PYTHONPATH="$V5/scripts" python - "$RUN_ROOT" <<'PY'
import json
import sys
from pathlib import Path
import pandas as pd

run_root = Path(sys.argv[1]).resolve()
approved_root = (Path.cwd() / "results/exploratory/rrs_reproduction_20260809").resolve()
try:
    run_root.relative_to(approved_root)
except ValueError:
    raise SystemExit(f"FAIL-CLOSED: run root outside approved exploratory root: {run_root}")
scores = run_root / "vina_scores"
# The currently running 15013/15014 jobs use the legacy shared layout. Future
# submissions use target-isolated children. Reject mixed layouts rather than
# silently selecting stale files.
legacy_inputs = [scores / "v5_mutant_vina_scores_PfDHFR.csv", scores / "v5_mutant_vina_scores_PfCRT.csv"]
isolated_inputs = [
    run_root / "PfDHFR" / "vina_scores" / "v5_mutant_vina_scores_PfDHFR.csv",
    run_root / "PfCRT" / "vina_scores" / "v5_mutant_vina_scores_PfCRT.csv",
]
legacy_complete = all(p.is_file() for p in legacy_inputs)
isolated_complete = all(p.is_file() for p in isolated_inputs)
if legacy_complete == isolated_complete:
    raise SystemExit("FAIL-CLOSED: require exactly one complete output layout; mixed or absent layouts rejected")
inputs = legacy_inputs if legacy_complete else isolated_inputs
expected = {
    "PfDHFR": {"PfDHFR_WT", "PfDHFR_N51I", "PfDHFR_C59R", "PfDHFR_S108N", "PfDHFR_I164L"},
    "PfCRT": {"PfCRT_WT_K76", "PfCRT_K76T", "PfCRT_K76A"},
}
frames = []
for path, target in zip(inputs, ["PfDHFR", "PfCRT"]):
    frame = pd.read_csv(path)
    required = {"candidate_id", "target", "receptor", "mutation", "vina_affinity_kcal_mol", "rank1_inside_fraction", "rank1_atom_count", "rank1_anchor_min_A", "rank1_centroid_in_box"}
    missing = required - set(frame.columns)
    if missing:
        raise SystemExit(f"FAIL-CLOSED: {path.name} missing columns {sorted(missing)}")
    if len(frame) != 17 * len(expected[target]):
        raise SystemExit(f"FAIL-CLOSED: {path.name} expected {17 * len(expected[target])} rows, found {len(frame)}")
    if set(frame.target) != {target} or set(frame.receptor) != expected[target]:
        raise SystemExit(f"FAIL-CLOSED: {path.name} target/receptor set mismatch")
    if set(frame.candidate_id) != {f"PP-{i:02d}" for i in range(1, 18)}:
        raise SystemExit(f"FAIL-CLOSED: {path.name} candidate set mismatch")
    if not pd.to_numeric(frame.vina_affinity_kcal_mol, errors="coerce").notna().all():
        raise SystemExit(f"FAIL-CLOSED: {path.name} contains non-finite affinity")
    if not pd.to_numeric(frame.rank1_inside_fraction, errors="coerce").ge(0.90).all():
        raise SystemExit(f"FAIL-CLOSED: {path.name} contains a failed containment gate")
    if not pd.to_numeric(frame.rank1_anchor_min_A, errors="coerce").le(10.0).all():
        raise SystemExit(f"FAIL-CLOSED: {path.name} contains a failed anchor gate")
    if not frame.rank1_centroid_in_box.astype(str).str.lower().isin(["true", "1"]).all():
        raise SystemExit(f"FAIL-CLOSED: {path.name} contains a failed centroid gate")
    if frame.duplicated(["candidate_id", "target", "receptor"]).any():
        raise SystemExit(f"FAIL-CLOSED: duplicate rows in {path.name}")
    frames.append(frame)
merged = pd.concat(frames, ignore_index=True)
if len(merged) != 136:
    raise SystemExit(f"FAIL-CLOSED: expected 136 rows, found {len(merged)}")
merged_path = scores / "v5_mutant_vina_scores_merged.csv"
merged.to_csv(merged_path, index=False)

out = []
for target, wt_label, mutants in [
    ("PfDHFR", "PfDHFR_WT", ["PfDHFR_N51I", "PfDHFR_C59R", "PfDHFR_S108N", "PfDHFR_I164L"]),
    ("PfCRT", "PfCRT_WT_K76", ["PfCRT_K76T", "PfCRT_K76A"]),
]:
    sub = merged[merged.target == target]
    for cid in sorted(sub.candidate_id.unique()):
        wt = sub[(sub.candidate_id == cid) & (sub.receptor == wt_label)]
        if len(wt) != 1:
            raise SystemExit(f"FAIL-CLOSED: WT count for {target}/{cid} is {len(wt)}")
        dwt = float(wt.vina_affinity_kcal_mol.iloc[0])
        if abs(dwt) < 5.0:
            continue
        vals = {}
        for receptor in mutants:
            row = sub[(sub.candidate_id == cid) & (sub.receptor == receptor)]
            if len(row) != 1:
                raise SystemExit(f"FAIL-CLOSED: mutant count for {target}/{cid}/{receptor} is {len(row)}")
            vals[receptor] = abs(float(row.vina_affinity_kcal_mol.iloc[0])) / abs(dwt) * 100.0
        mean = sum(vals.values()) / len(vals)
        if all(v >= 80 for v in vals.values()):
            cls = "A*" if abs(dwt) >= 7.0 else "A"
        elif all(v >= 70 for v in vals.values()):
            cls = "B"
        elif any(v >= 80 for v in vals.values()):
            cls = "C"
        else:
            cls = "D"
        out.append({"candidate_id": cid, "target": target, "dG_WT_kcal_mol": dwt,
                    **{f"RRS_{k}": v for k, v in vals.items()},
                    "RRS_mean": mean, "RRS_class": cls})
rrs = pd.DataFrame(out).sort_values(["target", "RRS_mean"], ascending=[True, False])
out_csv = run_root / "c_rrs_reproduction_per_target.csv"
rrs.to_csv(out_csv, index=False)
prov = {
    "schema": "p1-v5-rrs-reproduction-20260809/v2",
    "status": "PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY",
    "protocol_identity": "isolated V5-protocol reproduction; not a common-protocol replication of canonical P2",
    "source_csvs": [str(p) for p in inputs],
    "merged_csv": str(merged_path),
    "output_csv": str(out_csv),
    "rows_vina": int(len(merged)),
    "rows_rrs": int(len(rrs)),
    "targets": sorted(merged.target.unique()),
    "canonical_outputs_modified": False,
    "canonical_p2_rrs_overwritten": False,
    "review_required_for_submission": True,
}
(run_root / "reproduction_provenance.json").write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")
print(json.dumps(prov, indent=2, sort_keys=True))
print(rrs.to_string(index=False))
PY
