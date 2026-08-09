#!/usr/bin/env python3
"""Apply a verified external V6 review payload to the register.

This command does not create a signature and does not infer reviewer
acceptance. It verifies the external canonical payload/signature against the
current dossier, audit, candidate manifest, and trusted public key. Only then
it writes the register fields supplied by the signed payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

V6 = Path(__file__).resolve().parents[1]
REGISTER = V6 / "results/v6_review_register.json"
REQUIRED = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def resolve(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else V6 / p


def canonical(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload", type=Path, required=True)
    ap.add_argument("--signature", type=Path, required=True)
    ap.add_argument("--public-key", type=Path, required=True)
    args = ap.parse_args()

    payload = json.loads(args.payload.read_text())
    sig = args.signature
    pub = args.public_key
    dossier = resolve(payload.get("review_dossier", ""))
    audit = resolve(payload.get("integrity_audit", ""))
    manifest = resolve(payload.get("candidate_manifest", ""))
    for label, path in (("payload", args.payload), ("signature", sig), ("public key", pub), ("dossier", dossier), ("audit", audit), ("candidate manifest", manifest)):
        if not path.exists():
            raise SystemExit(f"FAIL-CLOSED missing {label}: {path}")

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
    if set(payload.get("target_decisions", {})) != set(REQUIRED):
        raise SystemExit("FAIL-CLOSED target decision set is incomplete")
    if any(payload["target_decisions"].get(t) not in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS", "REJECTED"} for t in REQUIRED):
        raise SystemExit("FAIL-CLOSED target decision contains an invalid value")

    proc = subprocess.run([
        "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pub),
        "-rawin", "-in", str(args.payload), "-sigfile", str(sig),
    ], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"FAIL-CLOSED Ed25519 verification failed: {proc.stderr.strip() or proc.stdout.strip()}")

    reg = json.loads(REGISTER.read_text())
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
    })
    REGISTER.write_text(json.dumps(reg, indent=2, sort_keys=True) + "\n")
    print(f"Applied externally signed review payload: {REGISTER}")
    print(f"status={reg['status']} accepted_for_full_run={reg['accepted_for_full_run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
