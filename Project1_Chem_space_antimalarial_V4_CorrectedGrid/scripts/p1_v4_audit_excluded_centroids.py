#!/usr/bin/env python3
"""Audit-only cross-pass classification of excluded V4 PfClpP/2F6I centroids.

This is not an independent replication analysis. Several rescue passes share
 deterministic preparation settings, so the output deliberately reports
``BIOLOGICAL_GATE_CONSISTENT_ACROSS_AVAILABLE_PASSES`` rather than claiming
reproducibility. It never relaunches docking, changes a pose, relaxes a
biological gate, or promotes a partial aggregate. For every centroid excluded
from the 467/484 partial panel, it compares the available raw, uniform, fix,
rescue-v1 and rescue-v2 failure/result records and classifies the observed
outcome.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

V4 = Path(__file__).resolve().parents[1]
RESULTS = V4 / "results"
PARTIAL = RESULTS / "pfclpp_2f6i_484_aggregate_partial" / "aggregation_provenance.json"
OUT = RESULTS / "pfclpp_2f6i_484_excluded_centroids_audit.json"
PASSES = {
    "raw": RESULTS / "pfclpp_2f6i_484_raw",
    "uniform": RESULTS / "pfclpp_2f6i_484_uniform_seed20260809",
    "fix": RESULTS / "pfclpp_2f6i_484_fix_seed20260809",
    "rescue_v1": RESULTS / "pfclpp_2f6i_484_rescue_seed20260809",
    "rescue_v2": RESULTS / "pfclpp_2f6i_484_rescue_seed20260809_v2",
}


def read_record(root: Path, cid: int) -> dict:
    directory = root / f"centroid_{cid:04d}"
    result = directory / "result.json"
    failure = directory / "failure.json"
    if result.is_file():
        try:
            data = json.loads(result.read_text(encoding="utf-8"))
            return {"status": data.get("status", "RESULT_UNKNOWN"), "path": str(result), "data": data}
        except Exception as exc:
            return {"status": "INVALID_RESULT_JSON", "path": str(result), "message": str(exc)}
    if failure.is_file():
        try:
            data = json.loads(failure.read_text(encoding="utf-8"))
            message = str(data.get("message") or data.get("error") or data.get("reason") or "unspecified")
            return {"status": "FAILED", "path": str(failure), "message": message, "data": data}
        except Exception as exc:
            return {"status": "INVALID_FAILURE_JSON", "path": str(failure), "message": str(exc)}
    return {"status": "MISSING", "path": str(directory)}


def category(record: dict) -> str:
    text = str(record.get("message", "")).lower()
    if record.get("status") == "PASS_RAW_VINA":
        return "PASS_RAW_VINA"
    if "biological gate" in text or "triad" in text or "inside_fraction" in text:
        return "BIOLOGICAL_GATE_FAILURE"
    if "embedding failed" in text or ("rdkit" in text and "embed" in text):
        return "RDKit_EMBEDDING_FAILURE"
    if "gasteiger" in text or "non-finite" in text:
        return "NONFINITE_CHARGE"
    if "multi-fragment" in text or "fragment" in text:
        return "MULTI_FRAGMENT_INPUT"
    if "vina returned" in text or "runtime" in text:
        return "VINA_RUNTIME_FAILURE"
    if record.get("status") == "MISSING":
        return "MISSING_ARTIFACT"
    return "OTHER_FAILURE"


def triad_distance(record: dict) -> float | None:
    data = record.get("data", {})
    gate = data.get("gate") if isinstance(data, dict) else None
    if isinstance(gate, dict) and isinstance(gate.get("triad_min_distance_A"), (int, float)):
        return float(gate["triad_min_distance_A"])
    message = str(record.get("message", ""))
    match = re.search(r"triad_min_distance_A['\"]?\\s*[:=]\\s*([-+]?\\d+(?:\\.\\d+)?)", message)
    if match:
        return float(match.group(1))
    # Some worker messages contain a Python dict representation. Parse only
    # literal data; never execute or eval arbitrary artifact text.
    try:
        start = message.find("{")
        if start >= 0:
            value = ast.literal_eval(message[message.find("{", start):])
            if isinstance(value, dict) and isinstance(value.get("triad_min_distance_A"), (int, float)):
                return float(value["triad_min_distance_A"])
    except (SyntaxError, ValueError):
        pass
    return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    partial = json.loads(PARTIAL.read_text(encoding="utf-8"))
    required_partial = {
        "status": "RAW_ARRAY_COMPLETE_PENDING_INDEPENDENT_REVIEW",
        "target": "PfClpP",
        "pdb_id": "2F6I",
        "records": 467,
        "failures": 0,
        "skipped_unfixable": 17,
        "consensus_written": False,
        "rrs_pns_updated": False,
    }
    mismatches = {key: (partial.get(key), value) for key, value in required_partial.items() if partial.get(key) != value}
    if mismatches:
        raise SystemExit(f"FAIL-CLOSED source partial aggregate mismatch: {mismatches}")
    skipped = partial.get("skipped_centroids", [])
    ids = sorted(int(item["centroid_id"]) for item in skipped)
    if len(ids) != 17 or len(set(ids)) != 17 or ids != sorted(set(range(484)) & set(ids)):
        raise SystemExit("FAIL-CLOSED excluded centroid IDs are not unique and in 0..483")
    records = []
    for cid in ids:
        passes = {name: read_record(root, cid) for name, root in PASSES.items()}
        # Preserve the preparation/protocol metadata next to each verdict. This
        # makes the consistency classification auditable and prevents it from
        # being mistaken for independent replication.
        for name, root in PASSES.items():
            directory = root / f"centroid_{cid:04d}"
            preparation = directory / "ligand_preparation.json"
            artifact_hashes = {}
            for artifact in (directory / "result.json", directory / "failure.json", preparation):
                if artifact.is_file():
                    artifact_hashes[artifact.name] = sha256(artifact)
            passes[name]["artifact_hashes"] = artifact_hashes
            if preparation.is_file():
                try:
                    passes[name]["preparation"] = json.loads(preparation.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    passes[name]["preparation_error"] = str(exc)
        categories = {name: category(record) for name, record in passes.items()}
        distances = [d for d in (triad_distance(record) for record in passes.values()) if d is not None]
        biological = [c for c in categories.values() if c == "BIOLOGICAL_GATE_FAILURE"]
        prep = [c for c in categories.values() if c in {"RDKit_EMBEDDING_FAILURE", "NONFINITE_CHARGE", "MULTI_FRAGMENT_INPUT"}]
        runtime = [c for c in categories.values() if c == "VINA_RUNTIME_FAILURE"]
        # The rescue passes are not independent replications. Require at least
        # two observed biological failures and two numerically distinct gate
        # distances, then use deliberately non-replicative wording.
        unique_distances = {round(distance, 6) for distance in distances}
        if (
            len(biological) >= 2
            and len(unique_distances) >= 2
            and not any(c == "PASS_RAW_VINA" for c in categories.values())
        ):
            verdict = "BIOLOGICAL_GATE_CONSISTENT_ACROSS_AVAILABLE_PASSES"
        elif prep and not biological:
            verdict = "PREPARATION_FAILURE_REQUIRES_SEPARATE_REMEDIATION"
        elif runtime and not biological:
            verdict = "RUNTIME_FAILURE_REQUIRES_LOG_REVIEW"
        else:
            verdict = "MIXED_OR_UNRESOLVED_REQUIRES_REVIEW"
        records.append({
            "centroid_id": cid,
            "passes": {
                name: {
                    "status": r.get("status"),
                    "category": categories[name],
                    "message": r.get("message"),
                    "path": r.get("path"),
                    "preparation": r.get("preparation"),
                    "preparation_error": r.get("preparation_error"),
                    "rescue_protocol": (r.get("data") or {}).get("rescue_protocol") if isinstance(r.get("data"), dict) else None,
                    "artifact_hashes": r.get("artifact_hashes", {}),
                }
                for name, r in passes.items()
            },
            "triad_distance_A_observed": distances,
            "triad_distance_range_A": [min(distances), max(distances)] if distances else None,
            "n_biological_gate_failures": len(biological),
            "n_unique_triad_distances_rounded_1e-6": len({round(distance, 6) for distance in distances}),
            "independent_replication_claim": False,
            "verdict": verdict,
        })
    counts = Counter(record["verdict"] for record in records)
    summary = {
        "schema": "p1-v4-clpp-2f6i-excluded-centroids-cross-pass-audit/v3",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_partial_aggregate": str(PARTIAL),
        "source_partial_aggregate_sha256": sha256(PARTIAL),
        "audit_script": str(Path(__file__).resolve()),
        "audit_script_sha256": sha256(Path(__file__).resolve()),
        "partial_panel_records": partial.get("records"),
        "partial_panel_total": 484,
        "excluded_centroids": len(records),
        "verdict_counts": dict(sorted(counts.items())),
        "canonical_panel_promotion": False,
        "promotion_block": True,
        "gate_relaxed": False,
        "docking_relaunched": False,
        "records": records,
        "classification_scope": "available-pass consistency only; not an independent replication",
        "protocol_metadata_recorded": True,
        "pass_artifact_hashes_recorded": True,
        "protocol_metadata_note": "Pass-level ligand-preparation and rescue-protocol metadata are retained where available; result/failure/preparation files are SHA-256 recorded when present. Shared deterministic preparation means these passes are not independent replications.",
        "independent_replication_claim": False,
        "promotion_note": "This cross-pass classification is audit evidence only. Rescue passes are not independent replications. The V4 replacement panel remains incomplete and requires a complete provenance-bound run plus independent review before promotion.",
    }
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("partial_panel_records", "excluded_centroids", "verdict_counts", "canonical_panel_promotion", "gate_relaxed", "docking_relaunched")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
