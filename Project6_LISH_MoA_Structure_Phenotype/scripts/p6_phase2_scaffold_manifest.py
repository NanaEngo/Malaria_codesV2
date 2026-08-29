#!/usr/bin/env python3
"""P6 scaffold-split arm manifest.

Audits the scaffold-split deliverables that exist on disk and reports one row
per declared arm. Two arm families are tracked:

- **rf_scaffold** (phenotype, structure, both): the ECFP4-RF / phenotype-logistic
  scaffold deliverables produced by `p6_phase2_benchmark.py` under
  ``--split scaffold``. Each row requires a ``p6_lish_moa_<arm>_scaffold_report.json``
  and a 25-record fold CSV (5 seeds x 5 folds).
- **gnn_scaffold** (gin, gin-tfp, gin-tne, chemberta): the deep molecular
  scaffold deliverables. These are *not* produced by the same launcher; the
  manifest only reports their existence and fold-record count, never infers
  a metric from a collision-group result.

The manifest distinguishes ``exists`` (file presence) from ``fold_records``
(record count) and emits a single overall ``status``:
  - ``COMPUTED_SCAFFOLD_ALL_ARMS`` if every declared arm is present and
    has 25 fold records,
  - ``COMPUTED_SCAFFOLD_RF_ONLY`` if the rf_scaffold family is complete but
    the gnn_scaffold family is not,
  - ``COMPUTED_SCAFFOLD_PARTIAL`` if at least one arm has files,
  - ``NOT_COMPUTED`` otherwise.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "p6_phase2"

RF_ARMS = ("phenotype", "structure", "both")
GNN_ARMS = ("gin", "gin-tfp", "gin-tne", "chemberta")
EXPECTED_FOLDS = 25


def _audit(csv_path: Path, json_path: Path) -> dict:
    exists_csv = csv_path.exists()
    exists_json = json_path.exists()
    n = 0
    if exists_csv:
        try:
            n = sum(1 for _ in csv.DictReader(csv_path.open(newline="")))
        except Exception:
            n = 0
    if exists_json:
        try:
            data = json.loads(json_path.read_text())
        except Exception:
            data = None
    else:
        data = None
    return {
        "fold_csv": str(csv_path.relative_to(ROOT)),
        "report_json": str(json_path.relative_to(ROOT)),
        "exists": exists_csv and exists_json,
        "fold_records": n,
        "expected_folds": EXPECTED_FOLDS,
    }


def main() -> int:
    rf_rows = []
    for arm in RF_ARMS:
        info = _audit(
            OUT / f"p6_lish_moa_{arm}_scaffold_folds.csv",
            OUT / f"p6_lish_moa_{arm}_scaffold_report.json",
        )
        info["arm"] = arm
        info["family"] = "rf_scaffold"
        rf_rows.append(info)
    gnn_rows = []
    for arm in GNN_ARMS:
        info = _audit(
            OUT / f"p6_lish_moa_{arm}_scaffold_folds.csv",
            OUT / f"p6_lish_moa_{arm}_scaffold_report.json",
        )
        info["arm"] = arm
        info["family"] = "gnn_scaffold"
        gnn_rows.append(info)

    rf_complete = all(r["exists"] and r["fold_records"] == EXPECTED_FOLDS for r in rf_rows)
    gnn_complete = all(r["exists"] and r["fold_records"] == EXPECTED_FOLDS for r in gnn_rows)
    any_exists = any(r["exists"] for r in rf_rows + gnn_rows)

    if rf_complete and gnn_complete:
        status = "COMPUTED_SCAFFOLD_ALL_ARMS"
    elif rf_complete:
        status = "COMPUTED_SCAFFOLD_RF_ONLY"
    elif any_exists:
        status = "COMPUTED_SCAFFOLD_PARTIAL"
    else:
        status = "NOT_COMPUTED"

    result = {
        "status": status,
        "rf_scaffold": rf_rows,
        "gnn_scaffold": gnn_rows,
        "contract": (
            f"{EXPECTED_FOLDS} scaffold-disjoint folds per arm; "
            "no result inferred from collision-group metrics; "
            "gnn_scaffold arms are reported by presence only"
        ),
    }
    out_path = OUT / "p6_scaffold_molecular_arm_manifest.json"
    out_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

