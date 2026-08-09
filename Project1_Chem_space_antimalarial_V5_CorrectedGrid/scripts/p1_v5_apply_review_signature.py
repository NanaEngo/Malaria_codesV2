#!/usr/bin/env python3
"""Apply a verified external V5 review payload to the structural register.

The reviewer signs an immutable JSON payload, not the mutable register. This
script verifies the Ed25519 signature and payload invariants before writing the
register. It never creates a signature and has no force/bypass option.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

V5 = Path(__file__).resolve().parents[1]
REPO = V5.parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(SCRIPT_DIR))
from p1_development_policy import is_pre_submission, is_submission_reactivation_active  # noqa: E402
REGISTER = V5 / "results/structural_pocket_independent_review.json"
REQUIRED = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--payload", type=Path, required=True,
                    help="immutable JSON review payload that was signed externally")
    ap.add_argument("--sig", type=Path, required=True,
                    help="detached Ed25519 signature over --payload")
    ap.add_argument("--pubkey", type=Path, required=True,
                    help="trusted public key for --sig")
    ap.add_argument("--register", type=Path, default=REGISTER)
    args = ap.parse_args()

    for label, path in (("payload", args.payload), ("signature", args.sig),
                        ("public key", args.pubkey), ("register", args.register)):
        if not path.is_file():
            print(f"FAIL-CLOSED: missing {label}: {path}")
            return 1
    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        reg = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL-CLOSED: invalid JSON input: {exc}")
        return 1
    if not isinstance(payload, dict):
        print("FAIL-CLOSED: payload is not a JSON object")
        return 1
    if not is_submission_reactivation_active():
        print("PROMOTION DORMANT: explicit author reactivation is not active in P1_DEVELOPMENT_PHASE.json")
        print("The V5 register was not modified.")
        return 1
    proc = subprocess.run([
        "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(args.pubkey),
        "-rawin", "-in", str(args.payload), "-sigfile", str(args.sig),
    ], capture_output=True, text=True, check=False)
    if proc.returncode != 0 or "Signature Verified" not in proc.stdout + proc.stderr:
        print("FAIL-CLOSED: detached Ed25519 signature verification failed")
        print("The V5 register was not modified.")
        return 1
    trusted_fp = os.environ.get("P1_TRUSTED_REVIEWER_PUBKEY_SHA256", "").lower()
    trusted_identity = os.environ.get("P1_TRUSTED_REVIEWER_IDENTITY", "")
    actual_fp = sha256(args.pubkey)
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_fp) or trusted_fp != actual_fp:
        print("FAIL-CLOSED: public key is not bound to the external trust anchor")
        return 1
    if not trusted_identity.strip() or payload.get("reviewer_identity") != trusted_identity:
        print("FAIL-CLOSED: reviewer identity is not bound to the external trust anchor")
        return 1
    if payload.get("status") != "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED":
        print("FAIL-CLOSED: payload status is not STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED")
        return 1
    if payload.get("accepted_for_full_run") is not True:
        print("FAIL-CLOSED: payload does not accept the full run")
        return 1
    if not isinstance(payload.get("reviewer_identity"), str) or not payload["reviewer_identity"].strip():
        print("FAIL-CLOSED: reviewer identity missing")
        return 1
    if payload.get("reviewer_independence_attestation") is not True or not isinstance(payload.get("conflict_of_interest_declaration"), str) or not payload["conflict_of_interest_declaration"].strip():
        print("FAIL-CLOSED: reviewer attestations are missing or incorrectly typed")
        return 1
    if payload.get("experimental_claims_certified") is not False:
        print("FAIL-CLOSED: payload must explicitly exclude experimental certification")
        return 1
    authorization = reg.get("authorization", {})
    if authorization.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED" or authorization.get("internal_work_authorized") is not False or authorization.get("submission_gate_active") is not False:
        print("FAIL-CLOSED: pending register authorization invariants are invalid")
        return 1
    if payload.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED" or payload.get("internal_work_authorized") is not False or payload.get("submission_gate_active") is not True:
        print("FAIL-CLOSED: signed payload authorization invariants are invalid")
        return 1
    required_criteria = ["target_identity_verified", "pocket_residues_or_reference_ligand_justified", "receptor_grid_frame_equivalence_verified", "exact_config_smoke_rank1_100pct_in_grid", "all_four_targets_individually_accepted"]
    criteria = payload.get("criteria")
    if not isinstance(criteria, dict) or any(criteria.get(key) is not True for key in required_criteria):
        print("FAIL-CLOSED: payload criteria are incomplete")
        return 1
    decisions = payload.get("target_decisions")
    if set(decisions or {}) != set(REQUIRED) or any(decisions[t] != "ACCEPTED" for t in REQUIRED):
        print("FAIL-CLOSED: payload must ACCEPT all four targets")
        return 1
    if payload.get("criteria", {}).get("all_four_targets_individually_accepted") is not True:
        print("FAIL-CLOSED: payload criteria do not accept all four targets")
        return 1

    # Bind the accepted payload to the current evidence before mutating the
    # register. The reviewer may include these hashes in the signed payload.
    for field, path in (("four_target_table_sha256", V5 / "results/v5_four_target_vina_affinities.csv"),
                        ("review_table_sha256", V5 / "results/v5_four_target_vina_review_table.json"),
                        ("target_identity_audit_sha256", V5 / "results/target_identity_audit.json")):
        if not path.is_file() or payload.get(field) != sha256(path):
            print(f"FAIL-CLOSED: payload evidence hash mismatch: {field}")
            return 1

    reg.update({
        "status": payload["status"],
        "reviewer_identity": payload["reviewer_identity"],
        "review_date": payload.get("review_date"),
        "reviewer_independence_attestation": payload["reviewer_independence_attestation"],
        "conflict_of_interest_declaration": payload["conflict_of_interest_declaration"],
        "accepted_for_full_run": True,
        "signed_review_artifact": str(args.payload),
        "signed_review_sha256": sha256(args.payload),
        "detached_signature_artifact": str(args.sig),
        "detached_signature_sha256": sha256(args.sig),
        "trusted_public_key_artifact": str(args.pubkey),
        "trusted_public_key_sha256": sha256(args.pubkey),
        "experimental_claims_certified": False,
        "criteria": criteria,
        "authorization": {
            "authorization_mode": payload["authorization_mode"],
            "internal_work_authorized": payload["internal_work_authorized"],
            "submission_gate_active": payload["submission_gate_active"],
        },
        "four_target_table_sha256": payload["four_target_table_sha256"],
        "review_table_sha256": payload["review_table_sha256"],
        "target_identity_audit_sha256": payload["target_identity_audit_sha256"],
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    })
    for target in REQUIRED:
        reg.setdefault("targets", {}).setdefault(target, {})["decision"] = "ACCEPTED"
        reg["targets"][target]["independent_signature"] = "ACCEPTED"
        reg["targets"][target]["review_date"] = payload.get("review_date")
    args.register.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"V5 review applied: {args.register}")
    print("status=STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED accepted_for_full_run=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
