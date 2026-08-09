#!/usr/bin/env python3
"""Reconcile V4 2F6I audit scopes without changing scientific outputs.

The rescue-v2 scope (35 IDs) and the older excluded-centroid cross-pass audit
(17 IDs) are related but not identical. This artifact makes their denominators
and intersection explicit so neither layer is misreported as the other.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

V4 = Path(__file__).resolve().parents[1]
RESULTS = V4 / "results"
MANIFEST = RESULTS / "pfclpp_2f6i_484_run_manifests.json"
RESCUE_AUDIT = RESULTS / "pfclpp_2f6i_484_rescue_aggregate" / "rescue_audit_provenance.json"
EXCLUDED_AUDIT = RESULTS / "pfclpp_2f6i_484_excluded_centroids_audit.json"
OUT = RESULTS / "pfclpp_2f6i_audit_reconciliation_20260809.json"


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load(MANIFEST)
    rescue_audit = load(RESCUE_AUDIT)
    excluded_audit = load(EXCLUDED_AUDIT)

    rescue_ids = sorted({int(x) for x in manifest.get("rescue_v2", {}).get("requested_centroid_ids", [])})
    rescue_audit_ids = sorted({int(x) for x in rescue_audit.get("requested_rescue_ids", [])})
    excluded_ids = sorted({int(row["centroid_id"]) for row in excluded_audit.get("records", []) if "centroid_id" in row})

    rescue_set = set(rescue_ids)
    rescue_audit_set = set(rescue_audit_ids)
    excluded_set = set(excluded_ids)
    record = {
        "schema": "p1-v4-2f6i-audit-reconciliation/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "panel_total": 484,
        "rescue_v2_scope": {
            "ids": rescue_ids,
            "count": len(rescue_ids),
            "source_manifest": str(MANIFEST.relative_to(V4)),
            "audit_ids_match_manifest": rescue_set == rescue_audit_set,
            "audit_status": rescue_audit.get("status"),
            "records_audited": rescue_audit.get("rescue_records_audited"),
            "records_failed_or_missing": len(rescue_audit.get("rescue_records_failed_or_missing", [])),
            "records_unaccounted": rescue_audit.get("rescue_records_unaccounted"),
        },
        "excluded_cross_pass_scope": {
            "ids": excluded_ids,
            "count": len(excluded_ids),
            "source_audit": str(EXCLUDED_AUDIT.relative_to(V4)),
            "audit_status": excluded_audit.get("status"),
            "verdict_counts": excluded_audit.get("verdict_counts", {}),
        },
        "set_relationship": {
            "intersection_ids": sorted(rescue_set & excluded_set),
            "intersection_count": len(rescue_set & excluded_set),
            "excluded_cross_pass_only_ids": sorted(excluded_set - rescue_set),
            "excluded_cross_pass_only_count": len(excluded_set - rescue_set),
            "rescue_v2_only_ids": sorted(rescue_set - excluded_set),
            "rescue_v2_only_count": len(rescue_set - excluded_set),
            "known_scope_note": "Centroid 171 is present only in the older excluded-cross-pass audit; it is not part of the 35-ID rescue-v2 request.",
        },
        "promotion": {
            "canonical_panel_promoted": False,
            "consensus_written": False,
            "rrs_pns_updated": False,
            "status": "BLOCKED_PENDING_COMPLETE_484_RECORD_ACCOUNTING_AND_V4_INDEPENDENT_REVIEW",
        },
        "source_hashes": {
            "run_manifest": sha256(MANIFEST),
            "rescue_audit": sha256(RESCUE_AUDIT),
            "excluded_cross_pass_audit": sha256(EXCLUDED_AUDIT),
        },
    }
    if len(rescue_ids) != 35 or rescue_ids != rescue_audit_ids or len(excluded_ids) != 17:
        record["status"] = "RECONCILIATION_WARNING"
        rc = 2
    else:
        record["status"] = "RECONCILED_SCOPES_NO_PROMOTION"
        rc = 0
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
