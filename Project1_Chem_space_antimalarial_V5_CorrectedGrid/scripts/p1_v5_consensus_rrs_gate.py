#!/usr/bin/env python3
"""P1 V5 — phase-aware gate for consensus / RRS / PNS computation.

During author-controlled pre-submission development, a truthful pending
register permits scientific development and returns an explicit development-
allowed status; all scientific QC remains active and outputs must retain
exploratory provenance. After explicit author reactivation, this gate verifies
the immutable signed review payload, detached Ed25519 signature, hashes,
reviewer attestations, and all four target decisions. Mutable register fields
alone can never open the submission-facing gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

V5 = Path(__file__).resolve().parents[1]
REPO = V5.parent
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from p1_development_policy import is_pre_submission as _policy_is_pre_submission, is_submission_reactivation_active  # noqa: E402


def pre_submission_development_enabled() -> bool:
    """Use the shared phase predicate; never duplicate phase semantics here."""
    return _policy_is_pre_submission()

REGISTER = V5 / "results/structural_pocket_independent_review.json"
REQUIRED_TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def safe_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = Path(value)
    path = raw if raw.is_absolute() else REPO / raw
    try:
        path.resolve().relative_to(REPO.resolve())
    except ValueError:
        return None
    return path


def verify_accepted_register(reg: dict) -> tuple[bool, str]:
    if reg.get("status") != "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED":
        return False, f"FAIL-CLOSED: register status={reg.get('status')}"
    if reg.get("accepted_for_full_run") is not True:
        return False, "FAIL-CLOSED: accepted_for_full_run is not true"
    authorization = reg.get("authorization", {})
    if authorization.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED":
        return False, "FAIL-CLOSED: authorization mode is not INDEPENDENT_REVIEW_REQUIRED"
    if authorization.get("internal_work_authorized") is not False:
        return False, "FAIL-CLOSED: internal_work_authorized must remain false"
    if authorization.get("submission_gate_active") is not True:
        return False, "FAIL-CLOSED: submission gate is not active"
    if not isinstance(reg.get("reviewer_identity"), str) or not reg["reviewer_identity"].strip():
        return False, "FAIL-CLOSED: reviewer identity missing"
    if reg.get("reviewer_independence_attestation") is not True:
        return False, "FAIL-CLOSED: reviewer independence attestation is not boolean true"
    if not isinstance(reg.get("conflict_of_interest_declaration"), str) or not reg["conflict_of_interest_declaration"].strip():
        return False, "FAIL-CLOSED: conflict-of-interest declaration missing or not text"
    targets = reg.get("targets", {})
    if set(targets) != set(REQUIRED_TARGETS):
        return False, "FAIL-CLOSED: register target set is incomplete"
    if any(targets[t].get("decision") != "ACCEPTED" for t in REQUIRED_TARGETS):
        return False, "FAIL-CLOSED: not all target decisions are ACCEPTED"

    payload_path = safe_path(reg.get("signed_review_artifact"))
    sig_path = safe_path(reg.get("detached_signature_artifact"))
    pub_path = safe_path(reg.get("trusted_public_key_artifact"))
    if not all(p is not None and p.is_file() for p in (payload_path, sig_path, pub_path)):
        return False, "FAIL-CLOSED: signed payload, detached signature, or public key is missing"
    assert payload_path is not None and sig_path is not None and pub_path is not None
    if reg.get("signed_review_sha256") != sha256(payload_path):
        return False, "FAIL-CLOSED: signed payload hash mismatch"
    if reg.get("detached_signature_sha256") != sha256(sig_path):
        return False, "FAIL-CLOSED: detached signature hash mismatch"
    if reg.get("trusted_public_key_sha256") != sha256(pub_path):
        return False, "FAIL-CLOSED: public-key hash mismatch"
    trusted_fp = os.environ.get("P1_TRUSTED_REVIEWER_PUBKEY_SHA256", "").lower()
    trusted_identity = os.environ.get("P1_TRUSTED_REVIEWER_IDENTITY", "")
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_fp) or trusted_fp != sha256(pub_path):
        return False, "FAIL-CLOSED: public key is not bound to external trust anchor"
    if not trusted_identity.strip() or trusted_identity != reg.get("reviewer_identity"):
        return False, "FAIL-CLOSED: reviewer identity is not bound to external trust anchor"
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"FAIL-CLOSED: signed review payload is not valid JSON: {exc}"
    proc = subprocess.run(
        ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pub_path),
         "-rawin", "-in", str(payload_path), "-sigfile", str(sig_path)],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0 or "Signature Verified" not in proc.stdout + proc.stderr:
        return False, "FAIL-CLOSED: detached Ed25519 signature verification failed"
    expected = {
        "status": reg.get("status"),
        "reviewer_identity": reg.get("reviewer_identity"),
        "review_date": reg.get("review_date"),
        "reviewer_independence_attestation": reg.get("reviewer_independence_attestation"),
        "conflict_of_interest_declaration": reg.get("conflict_of_interest_declaration"),
        "accepted_for_full_run": True,
        "target_decisions": {t: "ACCEPTED" for t in REQUIRED_TARGETS},
        "authorization_mode": "INDEPENDENT_REVIEW_REQUIRED",
        "internal_work_authorized": False,
        "submission_gate_active": True,
    }
    if payload.get("status") != expected["status"]:
        return False, "FAIL-CLOSED: signed payload status does not match register"
    for field in ("reviewer_identity", "review_date", "reviewer_independence_attestation", "conflict_of_interest_declaration"):
        if payload.get(field) != expected[field]:
            return False, f"FAIL-CLOSED: signed payload field mismatch: {field}"
    if payload.get("accepted_for_full_run") is not True or payload.get("target_decisions") != expected["target_decisions"]:
        return False, "FAIL-CLOSED: signed payload acceptance/target decisions are invalid"
    for field in ("authorization_mode", "internal_work_authorized", "submission_gate_active"):
        if payload.get(field) != expected[field]:
            return False, f"FAIL-CLOSED: signed payload authorization mismatch: {field}"
    if payload.get("experimental_claims_certified") is not False:
        return False, "FAIL-CLOSED: signed payload lacks explicit no-experimental-claims boundary"
    if reg.get("criteria") != payload.get("criteria"):
        return False, "FAIL-CLOSED: register criteria do not match signed payload"
    if reg.get("four_target_table_sha256") != payload.get("four_target_table_sha256") or reg.get("review_table_sha256") != payload.get("review_table_sha256") or reg.get("target_identity_audit_sha256") != payload.get("target_identity_audit_sha256"):
        return False, "FAIL-CLOSED: register evidence hashes do not match signed payload"
    if reg.get("authorization", {}).get("authorization_mode") != payload.get("authorization_mode") or reg.get("authorization", {}).get("internal_work_authorized") != payload.get("internal_work_authorized") or reg.get("authorization", {}).get("submission_gate_active") != payload.get("submission_gate_active"):
        return False, "FAIL-CLOSED: register authorization does not match signed payload"
    criteria = payload.get("criteria")
    required_criteria = ["target_identity_verified", "pocket_residues_or_reference_ligand_justified", "receptor_grid_frame_equivalence_verified", "exact_config_smoke_rank1_100pct_in_grid", "all_four_targets_individually_accepted"]
    if not isinstance(criteria, dict) or any(criteria.get(key) is not True for key in required_criteria):
        return False, "FAIL-CLOSED: signed payload review criteria are incomplete"
    evidence_hashes = {
        "four_target_table_sha256": V5 / "results/v5_four_target_vina_affinities.csv",
        "review_table_sha256": V5 / "results/v5_four_target_vina_review_table.json",
        "target_identity_audit_sha256": V5 / "results/target_identity_audit.json",
    }
    for field, artifact in evidence_hashes.items():
        if not artifact.is_file() or payload.get(field) != sha256(artifact):
            return False, f"FAIL-CLOSED: signed payload evidence binding invalid: {field}"
    return True, "GATE PASSED: signed independent V5 review verified for all four targets"


def check_gate(register_path: Path = REGISTER) -> tuple[bool, str]:
    """Return whether the current invocation may run.

    In pre-submission development, ``True`` means DEVELOPMENT_ALLOWED only;
    it never means that the register is independently accepted. Callers must
    preserve exploratory provenance. After explicit reactivation, ``True``
    means the cryptographic promotion gate passed.
    """
    if not register_path.exists():
        return False, f"SCIENTIFIC QC FAILED: register missing: {register_path}"
    try:
        reg = json.loads(register_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"SCIENTIFIC QC FAILED: unreadable register: {exc}"

    # Before the author explicitly reactivates submission restrictions, a
    # truthful pending register does not block scientific development. It still
    # cannot be treated as accepted evidence: callers must preserve the
    # exploratory/not-submission-ready provenance label.
    if pre_submission_development_enabled():
        pending = (
            reg.get("status") == "PENDING_INDEPENDENT_REVIEW"
            and reg.get("accepted_for_full_run") is False
        )
        authorization = reg.get("authorization", {})
        development_policy = reg.get("development_policy", {})
        authorization_consistent = (
            reg.get("development_execution_authorized") is True
            and development_policy.get("development_execution_authorized") is True
            and authorization.get("development_execution_authorized") is True
        )
        if pending and authorization_consistent and (
            reg.get("development_execution_authorized") is True
            and authorization.get("development_execution_authorized") is True
            and authorization.get("authorization_mode") == "INDEPENDENT_REVIEW_REQUIRED"
            and authorization.get("internal_work_authorized") is False
        ):
            return True, "DEVELOPMENT ALLOWED: development_execution_authorized=true; pre-submission editorial restrictions are inactive; scientific QC remains mandatory"
        # A malformed or acceptance-like register is a scientific/provenance
        # error, not an editorial restriction, and must never be trusted.
        return False, "SCIENTIFIC QC FAILED: pending register invariants are malformed"

    if reg.get("accepted_for_full_run") is not True:
        return False, ("SUBMISSION REVIEW GATE CLOSED: independent review is not signed; "
                       "this gate is dormant until explicit author reactivation.")
    return verify_accepted_register(reg)


def promotion_gate_passed(register_path: Path = REGISTER) -> tuple[bool, str]:
    """Check submission-facing acceptance only; development is never acceptance."""
    if not is_submission_reactivation_active():
        return False, "PROMOTION DORMANT: author has not explicitly reactivated submission restrictions"
    if not register_path.exists():
        return False, f"PROMOTION CLOSED: register missing: {register_path}"
    try:
        reg = json.loads(register_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"PROMOTION CLOSED: unreadable register: {exc}"
    return verify_accepted_register(reg)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", action="store_true", help="print register summary without authorizing")
    args = ap.parse_args()
    if args.status:
        if not REGISTER.exists():
            print(f"SCIENTIFIC QC FAILED: register missing: {REGISTER}")
            return 1
        reg = json.loads(REGISTER.read_text(encoding="utf-8"))
        print(f"status: {reg.get('status')}")
        print(f"reviewer: {reg.get('reviewer_identity')} ({reg.get('review_date')})")
        print(f"accepted_for_full_run: {reg.get('accepted_for_full_run')}")
        for t in REQUIRED_TARGETS:
            print(f"  {t}: {reg.get('targets', {}).get(t, {}).get('decision')}")
        return 0
    allowed, message = check_gate()
    print(message)
    return 0 if allowed else 1


if __name__ == "__main__":
    sys.exit(main())
