#!/usr/bin/env python3
"""
P5 — Public-dataset builder: ChEMBL P. falciparum activities (action 4).

The canonical MoleculeNet malaria.csv (Wu et al. 2018; 9,999 compounds from the
GSK TCAMS screen) is no longer directly downloadable: the deepchemdata S3 bucket
returns 403 AccessDenied, PyTDC 1.1.15 does not expose an HTS 'Malaria' loader,
and public mirrors (HuggingFace, figshare, Zenodo, OGB, chemprop) do not carry
the file. This script therefore builds an equivalent PUBLIC benchmark directly
from ChEMBL (the primary source of the TCAMS data, Gamo et al. 2010 Nature):

  - target: CHEMBL364 (Plasmodium falciparum)
  - activities: standard_type in {IC50, EC50} with a numeric pChEMBL value
  - binarization: active iff pChEMBL >= 6.0 (i.e. potency <= 1 uM),
    inactive iff pChEMBL < 5.0; 5.0-6.0 excluded (ambiguous band)
  - deduplication: canonical SMILES (RDKit), keep most potent per compound

Output: results/p5_public_chembl_malaria.csv (smiles, activity) + a provenance
JSON (download date, ChEMBL query, thresholds, n per class).

The downstream benchmark (p5_public_benchmark.py --csv ...) reuses the frozen
P5 protocol: ECFP4-RF vs GIN, 5 folds x 5 seeds, random + scaffold splits.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import CanonSmiles

P5_ROOT = Path(__file__).resolve().parent.parent
OUT_CSV = P5_ROOT / "results" / "p5_public_chembl_malaria.csv"
OUT_JSON = P5_ROOT / "results" / "p5_public_chembl_malaria_provenance.json"

BASE = "https://www.ebi.ac.uk/chembl/api/data"
ACTIVE_MIN_PCHEMBL = 6.0
INACTIVE_MAX_PCHEMBL = 5.0


def fetch_activities(target_id: str = "CHEMBL364", page_size: int = 1000) -> list[dict]:
    """Paginate ChEMBL activities for the target with numeric pChEMBL."""
    out: list[dict] = []
    offset = 0
    while True:
        q = urllib.parse.urlencode({
            "target_chembl_id": target_id,
            "pchembl_value__isnull": "false",
            "standard_type__in": "IC50,EC50",  # server-side filter (avoids paging 1M+ rows)
            "limit": page_size,
            "offset": offset,
        })
        url = f"{BASE}/activity.json?{q}"
        with urllib.request.urlopen(url, timeout=60) as r:
            d = json.load(r)
        acts = d.get("activities", [])
        if not acts:
            break
        for a in acts:
            st = (a.get("standard_type") or "").upper()
            if st in ("IC50", "EC50"):
                try:
                    pc = float(a["pchembl_value"])
                except (TypeError, ValueError):
                    continue
                out.append({
                    "smiles": a.get("canonical_smiles"),
                    "pchembl": pc,
                    "standard_type": st,
                    "assay_chembl_id": a.get("assay_chembl_id"),
                })
        offset += page_size
        if len(acts) < page_size:
            break
        print(f"  fetched {len(out)} activities (offset={offset})", flush=True)
    return out


def build_dataset() -> tuple[list[dict], dict]:
    activities = fetch_activities()
    # deduplicate by canonical SMILES, keep most potent
    best: dict[str, dict] = {}
    n_skipped = 0
    for a in activities:
        smi = a["smiles"]
        if not smi:
            n_skipped += 1
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            n_skipped += 1
            continue
        canon = CanonSmiles(smi)
        if canon not in best or a["pchembl"] > best[canon]["pchembl"]:
            best[canon] = {"smiles": canon, "pchembl": a["pchembl"],
                           "standard_type": a["standard_type"],
                           "assay_chembl_id": a["assay_chembl_id"]}

    rows = []
    for canon, info in best.items():
        if info["pchembl"] >= ACTIVE_MIN_PCHEMBL:
            rows.append({"smiles": canon, "activity": 1, "pchembl": info["pchembl"]})
        elif info["pchembl"] < INACTIVE_MAX_PCHEMBL:
            rows.append({"smiles": canon, "activity": 0, "pchembl": info["pchembl"]})
        # 5.0-6.0 ambiguous band excluded

    provenance = {
        "source": "ChEMBL REST API",
        "target_chembl_id": "CHEMBL364",
        "target_name": "Plasmodium falciparum",
        "standard_types": ["IC50", "EC50"],
        "active_min_pchembl": ACTIVE_MIN_PCHEMBL,
        "inactive_max_pchembl": INACTIVE_MAX_PCHEMBL,
        "raw_activities": len(activities),
        "skipped_no_smiles_or_invalid": n_skipped,
        "unique_canonical_compounds": len(best),
        "rows": len(rows),
        "n_active": sum(1 for r in rows if r["activity"] == 1),
        "n_inactive": sum(1 for r in rows if r["activity"] == 0),
        "download_date": time.strftime("%Y-%m-%d"),
        "note": ("MoleculeNet malaria.csv not directly downloadable (S3 403, "
                 "TDC no loader); built from ChEMBL primary source."),
    }
    return rows, provenance


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-csv", default=str(OUT_CSV))
    ap.add_argument("--out-json", default=str(OUT_JSON))
    args = ap.parse_args()

    print("Building public ChEMBL antimalarial benchmark...", flush=True)
    rows, prov = build_dataset()
    out_csv = Path(args.out_csv)
    import csv

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["smiles", "activity", "pchembl"])
        w.writeheader()
        w.writerows(rows)
    out_json = Path(args.out_json)
    out_json.write_text(json.dumps(prov, indent=2))

    print(f"Saved {len(rows)} rows -> {out_csv}")
    print(f"  active={prov['n_active']} inactive={prov['n_inactive']}")
    print(f"Provenance -> {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
