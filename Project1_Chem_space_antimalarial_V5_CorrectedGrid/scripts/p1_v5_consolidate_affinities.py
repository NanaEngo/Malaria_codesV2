#!/usr/bin/env python3
"""
P1 V5 — Consolidated 17×4 Vina affinity table for the INDEPENDENT REVIEW.

Merges the four target docking panels (PfDHFR/7F3Y, PfCRT/6UKJ, PfClpP/2F6I,
PfATP4/9N10) into a single reviewer artifact:

  - 17 polypharm candidates (PP-01..PP-17) × 4 targets of rank-1 Vina affinity
  - per-target gate metrics (pose-to-anchor min distance, in-box fraction,
    centroid-in-box) — the raw evidence the reviewer needs
  - provenance (PDB, anchor, center, box, Vina version, job evidence)

This is a RAW DATA ARTIFACT for the reviewer: it performs NO scoring, NO
consensus, NO RRS/PNS. The fail-closed consensus gate
(`p1_v5_consensus_rrs_gate.py`) still refuses downstream computation until the
independent-review register is signed.

Usage:
    python scripts/p1_v5_consolidate_affinities.py
    # re-run at any time: completes the PfATP4 block once job 12864 lands
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

V5 = Path(__file__).resolve().parents[1]
RESULTS = V5 / "results"

# (target, pdb, results dir, anchor label, anchor-min distance column)
TARGETS = [
    ("PfDHFR", "7F3Y", "vina_dock_7F3Y_PfDHFR_17",
     "MTX A702 co-crystallized inhibitor (catalytic-site copy)", "rank1_anchor_min_A"),
    ("PfCRT", "6UKJ", "vina_dock_6UKJ_PfCRT_17",
     "Y01 A501 cholesterol hemisuccinate (PROXY — not an inhibitor)", "rank1_anchor_min_A"),
    ("PfClpP", "2F6I", "vina_dock_2F6I_PfClpP_17",
     "chain A catalytic triad Ser252/His223/Asp219", "rank1_triad_min_A"),
    ("PfATP4", "9N10", "vina_dock_9N10_PfATP4_17",
     "conserved P-type ATPase residues 449-458 (CSDKTGT, phospho-D451) + 751-754 (DPPR)", "rank1_anchor_min_A"),
]
CANDIDATES = [f"PP-{i:02d}" for i in range(1, 18)]


def load_target(target: str, pdb: str, dirname: str) -> tuple[pd.DataFrame, dict]:
    """Load the per-pair CSV + provenance for one target."""
    d = RESULTS / dirname
    csv_files = list(d.glob(f"vina_dock_{pdb}_{target}.csv"))
    prov = {}
    prov_path = d / "execution_provenance.json"
    if prov_path.exists():
        prov = json.loads(prov_path.read_text())
    if not csv_files:
        return None, prov
    df = pd.read_csv(csv_files[0])
    return df, prov


def main() -> int:
    aff = pd.DataFrame({"candidate_id": CANDIDATES}).set_index("candidate_id")
    anchors = {}
    gates = {}
    completeness = {}

    for target, pdb, dirname, anchor_label, anchor_col in TARGETS:
        df, prov = load_target(target, pdb, dirname)
        if df is None or len(df) < 17:
            completeness[target] = "PENDING" if df is not None else "NOT_STARTED"
            for c in CANDIDATES:
                aff.loc[c, f"aff_{target}"] = np.nan
            anchors[target] = {
                "pdb": pdb, "anchor": anchor_label,
                "status": completeness[target],
                "center": prov.get("center"), "box": prov.get("box_A"),
                "provenance_status": prov.get("status"),
            }
            continue

        df = df.set_index("candidate_id")
        for c in CANDIDATES:
            if c in df.index:
                aff.loc[c, f"aff_{target}"] = df.loc[c, "vina_affinity_kcal_mol"]
                gates.setdefault(c, {})[target] = {
                    "anchor_min_A": round(float(df.loc[c, anchor_col]), 2),
                    "inside_fraction": round(float(df.loc[c, "rank1_inside_fraction"]), 3),
                    "centroid_in_box": bool(df.loc[c, "rank1_centroid_in_box"]),
                }
            else:
                aff.loc[c, f"aff_{target}"] = np.nan
        completeness[target] = "COMPLETE_17"
        anchors[target] = {
            "pdb": pdb, "anchor": anchor_label,
            "status": "COMPLETE_17",
            "center": prov.get("center"), "box": prov.get("box_A"),
            "provenance_status": prov.get("status"),
            "affinity_range_kcal_mol": [round(float(df["vina_affinity_kcal_mol"].min()), 2),
                                        round(float(df["vina_affinity_kcal_mol"].max()), 2)],
            "n_pairs": int(len(df)),
        }

    # Per-candidate mean over COMPLETE targets only (reviewer convenience, raw mean)
    completed = [t for t, _, _, _, _ in TARGETS if completeness[t] == "COMPLETE_17"]
    if completed:
        aff["mean_completed_targets"] = aff[[f"aff_{t}" for t in completed]].mean(axis=1)

    out_csv = RESULTS / "v5_four_target_vina_affinities.csv"
    aff_export = aff.copy()
    aff_export = aff_export.reset_index()
    aff_export.to_csv(out_csv, index=False)

    # Full review artifact with gate metrics + provenance
    gates_rows = []
    for c in CANDIDATES:
        row = {"candidate_id": c}
        for t, _, _, _, _ in TARGETS:
            row[f"aff_{t}"] = (None if pd.isna(aff.loc[c, f"aff_{t}"])
                               else round(float(aff.loc[c, f"aff_{t}"]), 2))
        for t, _, _, _, _ in TARGETS:
            g = gates.get(c, {}).get(t)
            if g:
                row[f"gate_{t}_anchor_min_A"] = g["anchor_min_A"]
                row[f"gate_{t}_frac"] = g["inside_fraction"]
        gates_rows.append(row)

    review = {
        "schema": "p1-v5-vina-4-target-consolidated/v1",
        "status": "RAW_DATA_ARTIFACT_FOR_INDEPENDENT_REVIEW",
        "generated_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "note": "Raw rank-1 Vina affinities + composite-gate metrics per candidate per target. "
                "NO scoring, NO consensus, NO RRS/PNS. Consensus gate remains fail-closed until "
                "the independent-review register is signed.",
        "targets": anchors,
        "completeness": completeness,
        "rows": gates_rows,
    }
    out_json = RESULTS / "v5_four_target_vina_review_table.json"
    out_json.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")

    print(f"Completeness: {completeness}")
    print(f"Saved: {out_csv}")
    print(f"Saved: {out_json}")
    print("\nAffinity matrix (completed targets):")
    print(aff_export.round(2).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
