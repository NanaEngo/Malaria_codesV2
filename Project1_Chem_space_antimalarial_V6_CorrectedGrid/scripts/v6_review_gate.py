#!/usr/bin/env python3
"""V6 hash-bound independent-review promotion gate.

This module is intentionally promotion-only: it verifies a human-signed review
artifact and never authorizes pre-submission development. During
``PRE_SUBMISSION_DEVELOPMENT``, use the phase-aware V6 generation workflow;
``development_execution_authorized=true`` permits exploratory outputs while
this gate correctly remains closed. It never edits the register, creates a
signature, or treats automated integrity audit as acceptance.

Signature format: binary Ed25519 signature created with OpenSSL over the exact
bytes of the current review dossier, using the trusted public key recorded in
the register. The reviewer must also bind the current audit and candidate
manifest hashes in the register.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

V6 = Path(__file__).resolve().parents[1]
REGISTER = V6 / "results/v6_review_register.json"
REQUIRED_TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def resolve(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else V6 / p


def check_gate(path: Path = REGISTER) -> tuple[bool, str]:
    if not path.exists():
        return False, f"FAIL-CLOSED: V6 review register missing: {path}"
    try:
        reg = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"FAIL-CLOSED: unreadable V6 review register: {exc}"

    if reg.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED":
        return False, "FAIL-CLOSED: authorization mode is not INDEPENDENT_REVIEW_REQUIRED"
    if reg.get("internal_work_authorized") is not False:
        return False, "FAIL-CLOSED: internal_work_authorized must be false"
    if reg.get("submission_gate_active") is not True:
        return False, "FAIL-CLOSED: submission_gate_active must be true"
    if reg.get("submission_restrictions_reactivation_requested") is not True:
        return False, "FAIL-CLOSED: explicit author reactivation is missing"
    if reg.get("accepted_for_full_run") is not True:
        return False, "FAIL-CLOSED: independent review has not accepted the V6 evidence"
    if reg.get("status") != "INDEPENDENT_REVIEW_ACCEPTED":
        return False, f"FAIL-CLOSED: register status={reg.get('status')}"

    if not reg.get("reviewer_identity") or not reg.get("reviewer_role"):
        return False, "FAIL-CLOSED: reviewer identity/role missing"
    if reg.get("reviewer_independence_attestation") is not True:
        return False, "FAIL-CLOSED: reviewer independence attestation missing"
    if not reg.get("conflict_of_interest_declaration"):
        return False, "FAIL-CLOSED: conflict-of-interest declaration missing"
    for target in REQUIRED_TARGETS:
        if reg.get("target_decisions", {}).get(target) != "ACCEPTED":
            return False, f"FAIL-CLOSED: target {target} is not ACCEPTED"

    audit = resolve(reg.get("integrity_audit", ""))
    dossier = resolve(reg.get("review_dossier", ""))
    manifest = resolve(reg.get("candidate_manifest", ""))
    signature = resolve(reg.get("detached_signature_artifact", ""))
    public_key = resolve(reg.get("trusted_public_key_artifact", ""))
    signed_artifact = resolve(reg.get("signed_review_artifact", ""))
    for label, artifact in (("audit", audit), ("dossier", dossier), ("candidate manifest", manifest), ("signature", signature), ("public key", public_key), ("signed review", signed_artifact)):
        if not str(artifact) or not artifact.exists():
            return False, f"FAIL-CLOSED: {label} artifact missing: {artifact}"

    try:
        audit_data = json.loads(audit.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"FAIL-CLOSED: audit unreadable: {exc}"
    if audit_data.get("status") not in {"AUDIT_PASS_REVIEW_REQUIRED", "AUDIT_WARN_REVIEW_REQUIRED"}:
        return False, f"FAIL-CLOSED: audit status={audit_data.get('status')}"
    if audit_data.get("errors"):
        return False, "FAIL-CLOSED: current integrity audit contains errors"
    if audit_data.get("accepted_for_full_run") is not False or audit_data.get("self_authorization_forbidden") is not True:
        return False, "FAIL-CLOSED: audit authorization invariants are invalid"
    if audit_data.get("candidate_manifest", {}).get("usable") is not True:
        return False, "FAIL-CLOSED: candidate manifest is not marked usable by the current audit"
    if audit_data.get("candidate_manifest", {}).get("sha256") != reg.get("candidate_manifest_sha256"):
        return False, "FAIL-CLOSED: audit candidate-manifest hash does not match register"

    expected_hashes = {
        "review_dossier_sha256": dossier,
        "integrity_audit_sha256": audit,
        "candidate_manifest_sha256": manifest,
        "signed_review_sha256": signed_artifact,
        "detached_signature_sha256": signature,
        "trusted_public_key_sha256": public_key,
    }
    for field, artifact in expected_hashes.items():
        expected = reg.get(field)
        if not expected:
            return False, f"FAIL-CLOSED: hash binding missing: {field}"
        actual = sha256(artifact)
        if actual != expected:
            return False, f"FAIL-CLOSED: hash mismatch for {field}"

    # Verify the detached Ed25519 signature over the canonical signed review
    # payload, which binds decisions, reviewer independence, and all hashes.
    cmd = [
        "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key),
        "-rawin", "-in", str(signed_artifact), "-sigfile", str(signature),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return False, f"FAIL-CLOSED: Ed25519 signature verification failed: {proc.stderr.strip() or proc.stdout.strip()}"
    try:
        payload = json.loads(signed_artifact.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"FAIL-CLOSED: signed review payload unreadable: {exc}"
    if payload.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED" or payload.get("internal_work_authorized") is not False or payload.get("submission_gate_active") is not True or payload.get("submission_restrictions_reactivation_requested") is not True:
        return False, "FAIL-CLOSED: signed payload authorization boundary is invalid"
    if payload.get("target_decisions") != reg.get("target_decisions"):
        return False, "FAIL-CLOSED: signed payload target decisions do not match register"
    for field in ("reviewer_identity", "reviewer_role", "reviewer_independence_attestation", "conflict_of_interest_declaration", "review_date_utc", "status", "accepted_for_full_run", "experimental_claims_certified", "target_decisions", "authorization_mode", "internal_work_authorized", "submission_gate_active", "submission_restrictions_reactivation_requested"):
        if payload.get(field) != reg.get(field) and not (field == "experimental_claims_certified" and payload.get(field) is False):
            return False, f"FAIL-CLOSED: signed payload field does not match register: {field}"
    if payload.get("reviewer_independence_attestation") is not True or payload.get("experimental_claims_certified") is not False:
        return False, "FAIL-CLOSED: signed payload attestation boundary invalid"
    if payload.get("review_dossier_sha256") != reg.get("review_dossier_sha256") or payload.get("integrity_audit_sha256") != reg.get("integrity_audit_sha256") or payload.get("candidate_manifest_sha256") != reg.get("candidate_manifest_sha256"):
        return False, "FAIL-CLOSED: signed payload hash bindings do not match register"
    return True, "GATE PASSED: hash-bound signed independent V6 review payload is present for all four targets"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", action="store_true", help="print status without authorizing anything")
    args = ap.parse_args()
    allowed, message = check_gate()
    print(message)
    if args.status:
        return 0
    return 0 if allowed else 1


if __name__ == "__main__":
    sys.exit(main())
