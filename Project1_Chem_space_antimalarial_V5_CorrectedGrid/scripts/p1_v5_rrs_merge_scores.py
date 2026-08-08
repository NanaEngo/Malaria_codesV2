#!/usr/bin/env python3
"""P1 V5 — merge per-target mutant Vina score CSVs into v5_mutant_vina_scores.csv.

The PfDHFR and PfCRT mutant panels run as two parallel SLURM jobs
(p1_v5_rrs_mutants.sbatch with TARGET=PfDHFR/PfCRT), each writing its own
per-target CSV to avoid clobbering. This script concatenates them into the
single CSV consumed by p1_v5_rrs_pilot.py.

Outputs:
  results/rrs_pilot/vina_scores/v5_mutant_vina_scores.csv   (merged)
  results/rrs_pilot/vina_scores/merge_provenance.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

V5 = Path(__file__).resolve().parents[1]
SCORES_DIR = V5 / "results/rrs_pilot/vina_scores"
TARGETS = ["PfDHFR", "PfCRT"]
OUT_CSV = SCORES_DIR / "v5_mutant_vina_scores.csv"
OUT_PROV = SCORES_DIR / "merge_provenance.json"

EXPECTED_COLS = ["candidate_id", "target", "receptor", "mutation",
                 "vina_affinity_kcal_mol", "rank1_inside_fraction",
                 "rank1_atom_count", "rank1_anchor_min_A",
                 "rank1_centroid_in_box", "ligand_pdbqt_sha256",
                 "vina_out_pdbqt_sha256"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    frames = []
    sources = {}
    for t in TARGETS:
        p = SCORES_DIR / f"v5_mutant_vina_scores_{t}.csv"
        if not p.exists():
            print(f"FAIL-CLOSED missing per-target CSV: {p}")
            return 1
        df = pd.read_csv(p)
        missing = [c for c in EXPECTED_COLS if c not in df.columns]
        if missing:
            print(f"FAIL-CLOSED {p.name} missing columns: {missing}")
            return 1
        if set(df["target"].unique()) != {t}:
            print(f"FAIL-CLOSED {p.name} target mismatch: {df['target'].unique()}")
            return 1
        frames.append(df)
        sources[p.name] = sha256(p)
    merged = pd.concat(frames, ignore_index=True)
    # integrity: exactly 17 candidates per target and every receptor represented
    per_target = merged.groupby("target")["candidate_id"].nunique().to_dict()
    expected = {t: 17 for t in TARGETS}
    if per_target != expected:
        print(f"FAIL-CLOSED candidate counts {per_target} != {expected}")
        return 1
    merged.to_csv(OUT_CSV, index=False)
    prov = {
        "schema": "p1-v5-rrs-pilot-vina-merge/v1",
        "status": "MERGED_OK",
        "sources": sources,
        "rows": int(len(merged)),
        "candidates_per_target": per_target,
        "output_csv_sha256": sha256(OUT_CSV),
    }
    OUT_PROV.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")
    print(json.dumps(prov, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
