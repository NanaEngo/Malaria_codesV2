#!/usr/bin/env python3
"""Apply a verified external V4 independent-review payload.

The reviewer signs an immutable JSON payload. The mutable V4 register is only
updated after the Ed25519 signature, attestations, evidence hashes, and a
current complete 484-record audit have all been verified. No bypass exists.
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

V4 = Path(__file__).resolve().parents[1]
REPO = V4.parents[1]
RESULTS = V4 / "results"
REGISTER = RESULTS / "pfclpp_2f6i_484_independent_review.json"
CANONICAL_SMILES = REPO / "Project2_Polypharmacology_MD_ValidationV2607" / "data/from_project1/data/cluster_representatives_smiles.csv"
REQUIRED = ("reviewer_identity", "review_date_utc", "review_decision",
            "reviewer_independence_attestation", "conflict_of_interest_declaration")


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


def find_complete_audit() -> tuple[Path | None, dict]:
    candidates = []
    for path in (RESULTS).glob("pfclpp_2f6i_484*/aggregation_provenance.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (data.get("status") == "RAW_ARRAY_COMPLETE_PENDING_INDEPENDENT_REVIEW"
                and data.get("target") == "PfClpP" and data.get("pdb_id") == "2F6I"
                and data.get("records") == 484 and data.get("failures", 0) == 0
                and data.get("skipped_unfixable", 0) == 0
                and data.get("consensus_written") is False
                and data.get("rrs_pns_updated") is False):
            candidates.append((str(data.get("created_utc") or ""), path, data))
    if not candidates:
        return None, {}
    _, path, data = sorted(candidates, reverse=True)[0]
    return path, data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--payload", type=Path, required=True)
    ap.add_argument("--sig", type=Path, required=True)
    ap.add_argument("--pubkey", type=Path, required=True)
    ap.add_argument("--register", type=Path, default=REGISTER)
    args = ap.parse_args()
    for label, path in (("payload", args.payload), ("signature", args.sig),
                        ("public key", args.pubkey), ("register", args.register)):
        if not path.is_file():
            print(f"FAIL-CLOSED: missing {label}: {path}")
            return 1
    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        register = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL-CLOSED: invalid JSON: {exc}")
        return 1
    proc = subprocess.run([
        "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(args.pubkey),
        "-rawin", "-in", str(args.payload), "-sigfile", str(args.sig),
    ], capture_output=True, text=True, check=False)
    if proc.returncode != 0 or "Signature Verified" not in proc.stdout + proc.stderr:
        print("FAIL-CLOSED: detached V4 signature verification failed")
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
    missing = [field for field in REQUIRED if not payload.get(field)]
    if missing:
        print(f"FAIL-CLOSED: payload missing fields: {missing}")
        return 1
    if payload.get("review_decision") != "PASS" or payload.get("accepted_for_promotion") is not True:
        print("FAIL-CLOSED: V4 payload must be an explicit PASS/accepted_for_promotion decision")
        return 1
    if payload.get("reviewer_independence_attestation") is not True:
        print("FAIL-CLOSED: reviewer independence attestation must be the boolean true")
        return 1
    if not isinstance(payload.get("conflict_of_interest_declaration"), str) or not payload["conflict_of_interest_declaration"].strip():
        print("FAIL-CLOSED: conflict-of-interest declaration must be explicit")
        return 1
    required_criteria = [
        "genuine_pfclpp_identity_2f6i",
        "all_484_centroid_inputs_bound_to_canonical_smiles",
        "pdb_pdbqt_frame_equivalence_verified",
        "target_specific_triad_box_reviewed",
        "all_484_records_independently_pass_raw_checks",
        "failure_records_resolved_or_explicitly_excluded_by_protocol",
        "aggregate_reproducibly_reconstructed",
        "independent_reviewer_acceptance",
    ]
    criteria = payload.get("review_criteria")
    if not isinstance(criteria, dict) or any(criteria.get(key) is not True for key in required_criteria):
        print("FAIL-CLOSED: signed V4 payload does not contain all required true review criteria")
        return 1
    if payload.get("target") != "PfClpP" or payload.get("pdb_id") != "2F6I" or payload.get("panel_size") != 484:
        print("FAIL-CLOSED: signed V4 payload target/panel identity is invalid")
        return 1
    if payload.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED" or payload.get("internal_work_authorized") is not False:
        print("FAIL-CLOSED: signed V4 authorization invariants are invalid")
        return 1
    audit_path, audit = find_complete_audit()
    if audit_path is None:
        print("FAIL-CLOSED: no current complete 484-record audit exists")
        return 1
    if not CANONICAL_SMILES.is_file() or audit.get("source_smiles_sha256") != sha256(CANONICAL_SMILES):
        print("FAIL-CLOSED: current audit is not bound to canonical SMILES")
        return 1
    if payload.get("current_audit_artifact") != str(audit_path) or payload.get("current_audit_sha256") != sha256(audit_path):
        print("FAIL-CLOSED: signed payload is not bound to the current complete audit")
        return 1
    if payload.get("current_audit_records") != 484:
        print("FAIL-CLOSED: signed payload current-audit record count is not 484")
        return 1
    evidence = payload.get("evidence", {})
    if evidence.get("canonical_smiles_sha256") != sha256(CANONICAL_SMILES):
        print("FAIL-CLOSED: signed payload canonical source hash mismatch")
        return 1
    aggregate_csv = safe_path(payload.get("current_aggregate_csv_artifact"))
    if aggregate_csv is None or not aggregate_csv.is_file():
        print("FAIL-CLOSED: signed payload lacks current aggregate CSV artifact")
        return 1
    if payload.get("current_aggregate_csv_sha256") != sha256(aggregate_csv):
        print("FAIL-CLOSED: signed payload aggregate CSV hash mismatch")
        return 1
    if audit.get("aggregate_csv_artifact") != payload.get("current_aggregate_csv_artifact") or audit.get("aggregate_csv_sha256") != payload.get("current_aggregate_csv_sha256"):
        print("FAIL-CLOSED: signed payload CSV is not the CSV declared by the current audit")
        return 1
    try:
        with aggregate_csv.open(newline="", encoding="utf-8") as handle:
            rows = list(__import__("csv").DictReader(handle))
        with CANONICAL_SMILES.open(newline="", encoding="utf-8") as handle:
            canonical = [row["SMILES"].strip() for row in __import__("csv").DictReader(handle)]
        if len(rows) != 484 or len(canonical) != 484 or sorted(int(row["centroid_id"]) for row in rows) != list(range(484)) or any(row.get("smiles", "").strip() != canonical[int(row["centroid_id"])] for row in rows):
            print("FAIL-CLOSED: signed payload aggregate CSV does not match canonical 484-row source")
            return 1
    except (OSError, KeyError, ValueError) as exc:
        print(f"FAIL-CLOSED: cannot verify aggregate/canonical correspondence: {exc}")
        return 1
    if payload.get("current_aggregate_csv_records") != 484:
        print("FAIL-CLOSED: signed payload aggregate CSV is not 484 records")
        return 1
    register.update({
        "status": "INDEPENDENT_REVIEW_ACCEPTED",
        "reviewer_identity": payload["reviewer_identity"],
        "review_date_utc": payload["review_date_utc"],
        "review_decision": "PASS",
        "reviewer_independence_attestation": payload["reviewer_independence_attestation"],
        "conflict_of_interest_declaration": payload["conflict_of_interest_declaration"],
        "accepted_for_promotion": True,
        "signed_review_artifact": str(args.payload),
        "signed_review_sha256": sha256(args.payload),
        "detached_signature_artifact": str(args.sig),
        "detached_signature_sha256": sha256(args.sig),
        "trusted_public_key_artifact": str(args.pubkey),
        "trusted_public_key_sha256": actual_fp,
        "trusted_reviewer_identity": trusted_identity,
        "current_audit_artifact": str(audit_path),
        "current_audit_sha256": sha256(audit_path),
        "current_audit_records": 484,
        "current_aggregate_csv_artifact": payload["current_aggregate_csv_artifact"],
        "current_aggregate_csv_sha256": payload["current_aggregate_csv_sha256"],
        "current_aggregate_csv_records": 484,
        "authorization_mode": payload["authorization_mode"],
        "internal_work_authorized": payload["internal_work_authorized"],
        "review_criteria": payload["review_criteria"],
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    })
    args.register.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"V4 review applied: {args.register}")
    print("status=INDEPENDENT_REVIEW_ACCEPTED accepted_for_promotion=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
