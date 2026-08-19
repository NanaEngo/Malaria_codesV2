#!/usr/bin/env python3
"""Build/verify the canonical payload signed by the V7 independent reviewer.

The payload binds reviewer identity, independence attestation, target decisions,
current audit/dossier/manifest hashes, and the explicit no-experimental-claims
boundary. It is intentionally separate from the project register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

V7 = Path(__file__).resolve().parents[1]
TEMPLATE = V7 / "docs/review_artifact_template.json"


def canonical_bytes(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    data = json.loads(args.input.read_text())
    required = {"reviewer_identity", "reviewer_role", "reviewer_independence_attestation", "conflict_of_interest_declaration", "review_date_utc", "review_dossier", "review_dossier_sha256", "integrity_audit", "integrity_audit_sha256", "candidate_manifest", "candidate_manifest_sha256", "target_decisions", "accepted_for_full_run", "status", "experimental_claims_certified", "reviewer_rationale", "authorization_mode", "internal_work_authorized", "submission_gate_active", "submission_restrictions_reactivation_requested"}
    missing = sorted(required - set(data))
    if missing:
        raise SystemExit(f"PAYLOAD_INVALID missing fields: {missing}")
    if set(data["target_decisions"]) != {"PfDHFR", "PfCRT", "PfClpP", "PfATP4"}:
        raise SystemExit("PAYLOAD_INVALID target_decisions must contain exactly four targets")
    expected_decision = "PENDING" if data["status"] == "PENDING_INDEPENDENT_REVIEW" else "ACCEPTED"
    if any(data["target_decisions"][target] != expected_decision for target in data["target_decisions"]):
        raise SystemExit("PAYLOAD_INVALID target decisions do not agree with status")
    if data["reviewer_independence_attestation"] is not True or data["experimental_claims_certified"] is not False:
        raise SystemExit("PAYLOAD_INVALID attestation boundary")
    if data["status"] not in {"PENDING_INDEPENDENT_REVIEW", "INDEPENDENT_REVIEW_ACCEPTED"}:
        raise SystemExit("PAYLOAD_INVALID status: limitations are non-promoting and cannot be signed as a V7 promotion payload")
    if data["authorization_mode"] != "INDEPENDENT_REVIEW_REQUIRED":
        raise SystemExit("PAYLOAD_INVALID authorization_mode")
    if data["internal_work_authorized"] is not False:
        raise SystemExit("PAYLOAD_INVALID internal_work_authorized must be false")
    accepted_status = data["status"] in {"INDEPENDENT_REVIEW_ACCEPTED", "INDEPENDENT_REVIEW_ACCEPTED_WITH_LIMITATIONS"}
    if data["submission_gate_active"] is not accepted_status:
        raise SystemExit("PAYLOAD_INVALID submission_gate_active does not agree with status")
    if data["submission_restrictions_reactivation_requested"] is not accepted_status:
        raise SystemExit("PAYLOAD_INVALID reactivation flag does not agree with status")
    if data["accepted_for_full_run"] is not (data["status"] == "INDEPENDENT_REVIEW_ACCEPTED"):
        raise SystemExit("PAYLOAD_INVALID accepted_for_full_run does not agree with status")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(data))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
