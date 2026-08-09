#!/usr/bin/env python3
"""Aggregate the 35-centroid V4 2F6I remediation outcomes into a single table.

Reads every `remediation_result.json` under the run root, classifies the
outcome, and writes:

  - c_v4_2f6i_remediation_summary.csv
  - c_v4_2f6i_remediation_provenance.json

No canonical file is written or modified.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUESTED = [13, 30, 40, 43, 47, 70, 73, 99, 100, 125, 136, 145, 167, 170, 189,
             194, 195, 228, 237, 257, 258, 339, 340, 358, 361, 368, 373, 390,
             408, 416, 423, 435, 440, 452, 468]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()
    run_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    if not run_root.is_dir():
        raise SystemExit(f"run root missing: {run_root}")

    rows = []
    missing = []
    for cid in REQUESTED:
        p = run_root / f"centroid_{cid:04d}" / "remediation_result.json"
        if not p.is_file():
            missing.append(cid)
            continue
        rec = json.loads(p.read_text())
        rows.append({
            "centroid_id": cid,
            "status": rec.get("status"),
            "vina_affinity_kcal_mol": rec.get("vina_affinity_kcal_mol"),
            "charge_method": rec.get("charge_method"),
            "embed_method": rec.get("embed_method"),
            "n_fragments_after_cleanup": rec.get("n_fragments_after_cleanup"),
            "unsupported_elements": ",".join(rec.get("unsupported_elements") or []),
            "gate": json.dumps(rec.get("gate")) if rec.get("gate") else None,
            "error": (rec.get("error") or "")[:160],
        })

    if not rows:
        raise SystemExit(f"FAIL-CLOSED: no remediation_result.json found under {run_root}")
    if missing:
        raise SystemExit(
            f"FAIL-CLOSED: {len(missing)} centroid(s) missing remediation_result.json: {sorted(missing)}"
        )
    rows.sort(key=lambda r: r["centroid_id"])
    summary = run_root / "c_v4_2f6i_remediation_summary.csv"
    with summary.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter
    counts = Counter(r["status"] for r in rows)
    provenance = {
        "schema": "p1-v4-clpp-2f6i-remediation-aggregate/v1",
        "run_root": str(run_root),
        "requested_centroids": REQUESTED,
        "n_requested": len(REQUESTED),
        "n_records_found": len(rows),
        "n_missing": len(missing),
        "missing_centroids": missing,
        "status_counts": dict(counts),
        "summary_csv": str(summary),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "promotion": "EXPLORATORY_REMEDIATION_NOT_SUBMISSION_READY",
        "canonical_outputs_modified": False,
        "note": "UNSUPPORTED_ELEMENT_FOR_AD4 = AutoDock Vina cannot type these "
                "elements (e.g. boron); a protocol exclusion, not a pipeline bug. "
                "DOCKED_GATE_FAILED = Vina succeeded but rank-1 pose failed the "
                "composite biological gate (pose outside the catalytic triad).",
    }
    prov_path = run_root / "c_v4_2f6i_remediation_provenance.json"
    prov_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
