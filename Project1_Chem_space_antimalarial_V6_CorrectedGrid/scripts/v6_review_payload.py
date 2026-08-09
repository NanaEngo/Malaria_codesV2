#!/usr/bin/env python3
"""Build/verify the canonical payload signed by the V6 independent reviewer.

The payload binds reviewer identity, independence attestation, target decisions,
current audit/dossier/manifest hashes, and the explicit no-experimental-claims
boundary. It is intentionally separate from the project register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

V6 = Path(__file__).resolve().parents[1]
TEMPLATE = V6 / "docs/review_artifact_template.json"


def canonical_bytes(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    data = json.loads(args.input.read_text())
    required = {"reviewer_identity", "reviewer_role", "reviewer_independence_attestation", "conflict_of_interest_declaration", "review_date_utc", "review_dossier", "review_dossier_sha256", "integrity_audit", "integrity_audit_sha256", "candidate_manifest", "candidate_manifest_sha256", "target_decisions", "accepted_for_full_run", "status", "experimental_claims_certified", "reviewer_rationale"}
    missing = sorted(required - set(data))
    if missing:
        raise SystemExit(f"PAYLOAD_INVALID missing fields: {missing}")
    if set(data["target_decisions"]) != {"PfDHFR", "PfCRT", "PfClpP", "PfATP4"}:
        raise SystemExit("PAYLOAD_INVALID target_decisions must contain exactly four targets")
    if data["reviewer_independence_attestation"] is not True or data["experimental_claims_certified"] is not False:
        raise SystemExit("PAYLOAD_INVALID attestation boundary")
    if data["status"] not in {"PENDING_INDEPENDENT_REVIEW", "INDEPENDENT_REVIEW_ACCEPTED", "INDEPENDENT_REVIEW_ACCEPTED_WITH_LIMITATIONS"}:
        raise SystemExit("PAYLOAD_INVALID status")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(data))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
