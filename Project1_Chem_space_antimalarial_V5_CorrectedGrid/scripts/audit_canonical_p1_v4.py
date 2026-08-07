#!/usr/bin/env python3
"""Read-only integrity audit for the canonical P1 V4 evidence files.

This script deliberately does not rerun docking, MD, or external APIs.  It verifies
claims that can be checked locally and writes a small JSON report only when an
output path is supplied.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_csv(name: str) -> list[dict[str, str]]:
    path = ROOT / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def audit() -> dict[str, Any]:
    centroid_rows = read_csv("v2_centroid_scores.csv")
    lead_rows = read_csv("c6_primary_leads_synthesisable.csv")
    si_rows = read_csv("c3_selectivity_index.csv")

    target_columns = ("pfDHFR", "pfCRT", "pfATP4", "pfClpP")
    failed_by_target: dict[str, int] = {}
    nonnegative_by_target: dict[str, int] = {}
    for target in target_columns:
        values = [finite_float(row.get(target)) for row in centroid_rows]
        failed_by_target[target] = sum(value is None for value in values)
        nonnegative_by_target[target] = sum(
            value is not None and value >= 0 for value in values
        )

    si_values = [finite_float(row.get("SI")) for row in si_rows]
    valid_si = [value for value in si_values if value is not None]
    result: dict[str, Any] = {
        "project": "P1",
        "canonical_root": str(ROOT),
        "inputs": {
            "centroids": {"path": "v2_centroid_scores.csv", "rows": len(centroid_rows)},
            "leads": {
                "path": "c6_primary_leads_synthesisable.csv",
                "rows": len(lead_rows),
            },
            "si_proxy": {"path": "c3_selectivity_index.csv", "rows": len(si_rows)},
        },
        "docking": {
            "expected_records": len(centroid_rows) * len(target_columns),
            "no_pose_by_target": failed_by_target,
            "nonnegative_by_target": nonnegative_by_target,
            "no_pose_records": sum(failed_by_target.values()),
            "nonnegative_records": sum(nonnegative_by_target.values()),
            "failed_records": sum(failed_by_target.values()) + sum(nonnegative_by_target.values()),
        },
        "si_proxy": {
            "valid_rows": len(valid_si),
            "all_above_10": bool(valid_si) and all(value > 10 for value in valid_si),
            "minimum": min(valid_si) if valid_si else None,
            "median": statistics.median(valid_si) if valid_si else None,
            "maximum": max(valid_si) if valid_si else None,
            "interpretation": "unvalidated ranking heuristic; not an experimental IC50 ratio",
        },
        "status": "PASS",
        "limitations": [
            "This audit does not establish docking accuracy or biological activity.",
            "Score-derived MMV labels remain retrodictive consistency checks.",
            "The P1 V4 top-20 safety/polypharmacology table is audited separately from P2 Sets B/C.",
        ],
    }
    if len(centroid_rows) != 484:
        result["status"] = "FAIL"
    if len(lead_rows) != 19913:
        result["status"] = "FAIL"
    if len(si_rows) != 810 or not result["si_proxy"]["all_above_10"]:
        result["status"] = "FAIL"
    if result["docking"]["no_pose_records"] != 67 or result["docking"]["nonnegative_records"] != 4:
        result["status"] = "FAIL"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
