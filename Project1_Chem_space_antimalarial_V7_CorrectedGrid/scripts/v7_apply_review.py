#!/usr/bin/env python3
"""Apply a verified external V7 review payload to the register.

This command does not create a signature and does not infer reviewer
acceptance. It verifies the external canonical payload/signature against the
current dossier, audit, candidate manifest, and trusted public key. Only then
it writes the register fields supplied by the signed payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import re
from pathlib import Path

V7 = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
V5_SCRIPT_DIR = V7.parent / "Project1_Chem_space_antimalarial_V5_CorrectedGrid" / "scripts"
sys.path.insert(0, str(V5_SCRIPT_DIR))
from p1_development_policy import is_submission_reactivation_active  # noqa: E402
REGISTER = V7 / "results/v7_review_register.json"
REQUIRED = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def resolve(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else V7 / p


def canonical(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload", type=Path, required=True)
    ap.add_argument("--signature", type=Path, required=True)
    ap.add_argument("--public-key", type=Path, required=True)
    args = ap.parse_args()

    payload = json.loads(args.payload.read_text())
    if not isinstance(payload, dict):
        raise SystemExit("FAIL-CLOSED payload must be a JSON object")
    if not is_submission_reactivation_active():
        raise SystemExit("PROMOTION DORMANT: explicit author reactivation is not active in P1_DEVELOPMENT_PHASE.json")
    if payload.get("status") != "INDEPENDENT_REVIEW_ACCEPTED":
        raise SystemExit("FAIL-CLOSED only a fully accepted V7 review can promote the register; limitations remain non-promoting")
    decisions = payload.get("target_decisions")
    if not isinstance(decisions, dict) or set(decisions) != set(REQUIRED):
        raise SystemExit("FAIL-CLOSED payload target decision set is incomplete")
    if any(decisions[target] != "ACCEPTED" for target in REQUIRED):
        raise SystemExit("FAIL-CLOSED full V7 promotion requires ACCEPTED for all four targets")
    all_accepted = True
    if payload.get("accepted_for_full_run") is not True:
        raise SystemExit("FAIL-CLOSED payload accepted_for_full_run does not agree with target decisions")
    sig = args.signature
    pub = args.public_key
    dossier = resolve(payload.get("review_dossier", ""))
    audit = resolve(payload.get("integrity_audit", ""))
    manifest = resolve(payload.get("candidate_manifest", ""))
    for label, path in (("payload", args.payload), ("signature", sig), ("public key", pub), ("dossier", dossier), ("audit", audit), ("candidate manifest", manifest)):
        if not path.exists():
            raise SystemExit(f"FAIL-CLOSED missing {label}: {path}")

    trusted_fp = os.environ.get("P1_TRUSTED_REVIEWER_PUBKEY_SHA256", "").lower()
    trusted_identity = os.environ.get("P1_TRUSTED_REVIEWER_IDENTITY", "")
    actual_fp = sha256(pub)
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_fp) or trusted_fp != actual_fp:
        raise SystemExit("FAIL-CLOSED public key is not bound to the external trust anchor")
    if not trusted_identity.strip() or payload.get("reviewer_identity") != trusted_identity:
        raise SystemExit("FAIL-CLOSED reviewer identity is not bound to the external trust anchor")
    if not isinstance(payload.get("reviewer_identity"), str) or not payload["reviewer_identity"].strip():
        raise SystemExit("FAIL-CLOSED reviewer identity is missing")
    if not isinstance(payload.get("reviewer_role"), str) or not payload["reviewer_role"].strip():
        raise SystemExit("FAIL-CLOSED reviewer role is missing")

    audit_data = json.loads(audit.read_text())
    if audit_data.get("status") not in {"AUDIT_PASS_REVIEW_REQUIRED", "AUDIT_WARN_REVIEW_REQUIRED"} or audit_data.get("errors"):
        raise SystemExit("FAIL-CLOSED current integrity audit is not clean")
    if audit_data.get("candidate_manifest", {}).get("usable") is not True:
        raise SystemExit("FAIL-CLOSED current candidate manifest is not usable")

    expected = {
        "review_dossier_sha256": sha256(dossier),
        "integrity_audit_sha256": sha256(audit),
        "candidate_manifest_sha256": sha256(manifest),
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise SystemExit(f"FAIL-CLOSED payload hash mismatch: {key}")
    if payload.get("reviewer_independence_attestation") is not True:
        raise SystemExit("FAIL-CLOSED reviewer independence attestation is not true")
    if not payload.get("conflict_of_interest_declaration"):
        raise SystemExit("FAIL-CLOSED conflict-of-interest declaration is missing")
    if payload.get("experimental_claims_certified") is not False:
        raise SystemExit("FAIL-CLOSED experimental claims boundary is invalid")
    if payload.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED":
        raise SystemExit("FAIL-CLOSED signed payload authorization_mode is invalid")
    if payload.get("internal_work_authorized") is not False:
        raise SystemExit("FAIL-CLOSED signed payload cannot authorize internal work")
    if payload.get("submission_gate_active") is not True:
        raise SystemExit("FAIL-CLOSED signed payload must activate the submission gate")
    if payload.get("submission_restrictions_reactivation_requested") is not True:
        raise SystemExit("FAIL-CLOSED signed payload lacks explicit author reactivation")
    if set(payload.get("target_decisions", {})) != set(REQUIRED):
        raise SystemExit("FAIL-CLOSED target decision set is incomplete")
    if any(payload["target_decisions"].get(t) != "ACCEPTED" for t in REQUIRED):
        raise SystemExit("FAIL-CLOSED full V7 promotion requires ACCEPTED for all four targets")

    proc = subprocess.run([
        "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pub),
        "-rawin", "-in", str(args.payload), "-sigfile", str(sig),
    ], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"FAIL-CLOSED Ed25519 verification failed: {proc.stderr.strip() or proc.stdout.strip()}")

    reg = json.loads(REGISTER.read_text())
    if reg.get("status") != "PENDING_INDEPENDENT_REVIEW" or reg.get("accepted_for_full_run") is not False or reg.get("submission_gate_active") is not False or reg.get("submission_restrictions_reactivation_requested") is not False:
        raise SystemExit("FAIL-CLOSED current V7 register is not the untouched pending pre-submission register")
    reg.update({
        "status": "INDEPENDENT_REVIEW_ACCEPTED" if all(payload["target_decisions"][t] == "ACCEPTED" for t in REQUIRED) else "INDEPENDENT_REVIEW_ACCEPTED_WITH_LIMITATIONS",
        "reviewer_identity": payload.get("reviewer_identity"),
        "reviewer_role": payload.get("reviewer_role"),
        "reviewer_independence_attestation": payload.get("reviewer_independence_attestation"),
        "conflict_of_interest_declaration": payload.get("conflict_of_interest_declaration"),
        "review_date_utc": payload.get("review_date_utc"),
        "review_dossier_sha256": expected["review_dossier_sha256"],
        "integrity_audit_sha256": expected["integrity_audit_sha256"],
        "candidate_manifest_sha256": expected["candidate_manifest_sha256"],
        "signed_review_artifact": str(args.payload),
        "signed_review_sha256": sha256(args.payload),
        "detached_signature_artifact": str(sig),
        "detached_signature_sha256": sha256(sig),
        "trusted_public_key_artifact": str(pub),
        "trusted_public_key_sha256": sha256(pub),
        "accepted_for_full_run": all(payload["target_decisions"][t] == "ACCEPTED" for t in REQUIRED),
        "target_decisions": payload["target_decisions"],
        "authorization_mode": "INDEPENDENT_REVIEW_REQUIRED",
        "internal_work_authorized": False,
        "submission_gate_active": payload["submission_gate_active"],
        "submission_restrictions_reactivation_requested": payload["submission_restrictions_reactivation_requested"],
    })
    REGISTER.write_text(json.dumps(reg, indent=2, sort_keys=True) + "\n")
    print(f"Applied externally signed review payload: {REGISTER}")
    print(f"status={reg['status']} accepted_for_full_run={reg['accepted_for_full_run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
