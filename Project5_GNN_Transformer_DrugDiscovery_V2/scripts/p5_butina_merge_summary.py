#!/usr/bin/env python3
"""Merge the ChemBERTa-only run's summary block into the 4-arm backup, producing
the final canonical butina_summary.json."""
import json, sys
from pathlib import Path

# Absolute paths derived from this script's location: safe from any cwd.
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "butina_cluster_20260829" / "butina_summary.json"
BACKUP = ROOT / "results" / "butina_cluster_20260829" / "butina_summary_backup_4arms.json"

if not BACKUP.exists():
    print("ERROR: 4-arm backup not found"); sys.exit(1)

with open(OUT) as f:
    cb_only = json.load(f)          # from the ChemBERTa-only run
with open(BACKUP) as f:
    merged = json.load(f)           # has ECFP4-RF/GIN/GIN-TFP/GIN-TNE

chem = cb_only.get("ChemBERTa", {})
if not chem:
    print("ERROR: no ChemBERTa block in ChemBERTa-only summary"); sys.exit(1)

# sanity: ChemBERTa should have real mean_auc now (no NaN)
bad = {k: v.get("mean_auc") for k, v in chem.items() if v.get("mean_auc") is None}
if bad:
    print("WARN: ChemBERTa seeds with NaN mean_auc:", bad)

merged["ChemBERTa"] = chem
with open(OUT, "w") as f:
    json.dump(merged, f, indent=2)
print("Merged. Arms:", sorted(merged.keys()))
for arm in ["ECFP4-RF", "GIN", "GIN-TFP", "GIN-TNE", "ChemBERTa"]:
    ma = [merged[arm][f"seed{s}"].get("mean_auc") for s in range(5)]
    print(f"  {arm}: mean_auc per seed = {[round(x,4) if x is not None else None for x in ma]}")
print("Checksums: e4arm ok")
