#!/usr/bin/env python3
"""Inventory the V4 2F6I 484-centroid failures without changing any result.

The report distinguishes input/preparation failures from Vina/runtime failures
and biological-gate failures. It is an audit artifact, not a promotion step.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "pfclpp_2f6i_484_run_manifests.json"
RESCUE = ROOT / "results" / "pfclpp_2f6i_484_rescue_seed20260809_v2"
OUT = ROOT / "results" / "pfclpp_2f6i_484_failure_inventory.json"


def classify(message: str) -> str:
    text = message.lower()
    if "multi-fragment" in text or "fragment" in text:
        return "MULTI_FRAGMENT_INPUT"
    if "embedding failed" in text or "rdkit" in text and "embed" in text:
        return "RDKit_EMBEDDING_FAILURE"
    if "gasteiger" in text or "non-finite" in text:
        return "NONFINITE_CHARGE"
    if "vina returned" in text or "exit" in text:
        return "VINA_RUNTIME_FAILURE"
    if "biological gate" in text or "triad" in text or "inside_fraction" in text:
        return "BIOLOGICAL_GATE_FAILURE"
    return "OTHER_FAILURE"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rescue = manifest["rescue_v2"]
    ids = [int(x) for x in rescue["requested_centroid_ids"]]
    records = []
    for cid in ids:
        base = RESCUE / f"centroid_{cid:04d}"
        result_path = base / "result.json"
        failure_path = base / "failure.json"
        if result_path.exists():
            data = json.loads(result_path.read_text(encoding="utf-8"))
            records.append({
                "centroid_id": cid,
                "status": data.get("status", "UNKNOWN_RESULT"),
                "category": "PASS_RAW_VINA" if data.get("status") == "PASS_RAW_VINA" else "OTHER_RESULT",
                "artifact": str(result_path.relative_to(ROOT)),
                "message": None,
            })
        elif failure_path.exists():
            data = json.loads(failure_path.read_text(encoding="utf-8"))
            message = str(data.get("error") or data.get("message") or data.get("reason") or "unspecified failure")
            records.append({
                "centroid_id": cid,
                "status": "FAILED",
                "category": classify(message),
                "artifact": str(failure_path.relative_to(ROOT)),
                "message": message,
            })
        else:
            records.append({
                "centroid_id": cid,
                "status": "MISSING",
                "category": "MISSING_ARTIFACT",
                "artifact": None,
                "message": "neither result.json nor failure.json exists",
            })

    counts = Counter(r["category"] for r in records)
    summary = {
        "schema": "p1-v4-pfclpp-2f6i-484-failure-inventory/v1",
        "scope": "rescue_v2 requested failed IDs only",
        "source_manifest": str(MANIFEST.relative_to(ROOT)),
        "source_rescue_root": str(RESCUE.relative_to(ROOT)),
        "requested_records": len(ids),
        "pass_raw_vina": sum(r["status"] == "PASS_RAW_VINA" for r in records),
        "failed_records": sum(r["status"] == "FAILED" for r in records),
        "missing_records": sum(r["status"] == "MISSING" for r in records),
        "category_counts": dict(sorted(counts.items())),
        "promotion": "PROHIBITED_PENDING_COMPLETE_484_AUDIT_AND_INDEPENDENT_REVIEW",
        "records": records,
    }
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("requested_records", "pass_raw_vina", "failed_records", "missing_records", "category_counts")}, indent=2))
    return 0 if summary["missing_records"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
