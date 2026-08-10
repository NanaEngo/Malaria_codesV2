#!/usr/bin/env python3
"""Apply a verified external V4 independent-review payload (final-accounting bound).

The reviewer signs an immutable JSON payload. The mutable V4 register is only
updated after the Ed25519 signature, attestations, evidence hashes, and a
complete final-accounting audit (484 rows, IDs 1..484, statuses sum to 484)
have all been verified. No bypass exists.

Binding target (supersedes the obsolete uniform-run aggregate):
    results/pfclpp_2f6i_484_final_accounting.json   (final_counts sum to 484)
    results/pfclpp_2f6i_484_final_accounting.csv    (484 rows, IDs 1..484)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

V4 = Path(__file__).resolve().parents[1]
REPO = V4.parents[1]
RESULTS = V4 / "results"
REGISTER = RESULTS / "pfclpp_2f6i_484_independent_review.json"
FINAL_ACCOUNTING_JSON = RESULTS / "pfclpp_2f6i_484_final_accounting.json"
FINAL_ACCOUNTING_CSV = RESULTS / "pfclpp_2f6i_484_final_accounting.csv"
CANONICAL_SMILES = REPO / "Project2_Polypharmacology_MD_ValidationV2607" / "data/from_project1/data/cluster_representatives_smiles.csv"
REQUIRED = ("reviewer_identity", "review_date_utc", "review_decision",
            "reviewer_independence_attestation", "conflict_of_interest_declaration")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$")


def find_final_accounting() -> tuple[Path | None, dict | None]:
    """Locate and integrity-check the canonical final accounting (484).

    Returns (json_path, accounting_json, accounting_rows) or (None, None, None).
    The accounting is accepted as the review target only if:
      - both JSON and CSV exist;
      - CSV has exactly 484 rows with centroid_id covering 1..484 exactly once;
      - final_counts in the JSON sum to 484;
      - each CSV final_status is in the JSON final_counts keys.
    """
    if not (FINAL_ACCOUNTING_JSON.is_file() and FINAL_ACCOUNTING_CSV.is_file()):
        return None, None, None
    try:
        data = json.loads(FINAL_ACCOUNTING_JSON.read_text(encoding="utf-8"))
        with FINAL_ACCOUNTING_CSV.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL-CLOSED: cannot parse final accounting: {exc}")
        return None, None, None
    if not isinstance(data, dict):
        return None, None, None
    counts = data.get("final_counts")
    if not isinstance(counts, dict) or sum(counts.values()) != 484:
        print("FAIL-CLOSED: final accounting final_counts do not sum to 484")
        return None, None
    try:
        ids = sorted(int(row["centroid_id"]) for row in rows)
    except (KeyError, ValueError):
        print("FAIL-CLOSED: final accounting CSV lacks valid centroid_id column")
        return None, None
    if len(rows) != 484 or ids != list(range(1, 485)):
        print("FAIL-CLOSED: final accounting CSV is not a complete 1..484 panel")
        return None, None
    observed = Counter(row.get("final_status") for row in rows)
    if dict(observed) != counts:
        print("FAIL-CLOSED: final accounting CSV status distribution contradicts JSON final_counts")
        return None, None
    return FINAL_ACCOUNTING_JSON, data


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
    review_date = payload.get("review_date_utc")
    if not isinstance(review_date, str) or not ISO_UTC_RE.fullmatch(review_date):
        print("FAIL-CLOSED: review_date_utc is not a valid ISO-8601 UTC timestamp")
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
        "final_accounting_reconciled_484",
        "protocol_exclusions_verified",
        "gate_and_embed_failures_verified",
        "final_accounting_reproducible_from_artifacts",
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
    acct_path, acct_json = find_final_accounting()
    if acct_path is None:
        print("FAIL-CLOSED: no current complete 484 final-accounting audit exists")
        return 1
    if not CANONICAL_SMILES.is_file():
        print("FAIL-CLOSED: canonical SMILES source missing")
        return 1
    with CANONICAL_SMILES.open(newline="", encoding="utf-8") as handle:
        canonical = [row["SMILES"].strip() for row in csv.DictReader(handle)]
    if len(canonical) != 484:
        print("FAIL-CLOSED: canonical SMILES source is not 484 rows")
        return 1
    if payload.get("current_accounting_artifact") != str(acct_path):
        print("FAIL-CLOSED: signed payload is not bound to the current final accounting JSON")
        return 1
    if payload.get("current_accounting_sha256") != sha256(acct_path):
        print("FAIL-CLOSED: signed payload final-accounting JSON hash mismatch")
        return 1
    if payload.get("current_accounting_csv_artifact") != str(FINAL_ACCOUNTING_CSV):
        print("FAIL-CLOSED: signed payload is not bound to the current final accounting CSV")
        return 1
    if payload.get("current_accounting_csv_sha256") != sha256(FINAL_ACCOUNTING_CSV):
        print("FAIL-CLOSED: signed payload final-accounting CSV hash mismatch")
        return 1
    if payload.get("current_accounting_records") != 484:
        print("FAIL-CLOSED: signed payload final-accounting record count is not 484")
        return 1
    evidence = payload.get("evidence", {})
    if evidence.get("canonical_smiles_sha256") != sha256(CANONICAL_SMILES):
        print("FAIL-CLOSED: signed payload canonical source hash mismatch")
        return 1
    if payload.get("current_aggregate_csv_artifact") or payload.get("current_audit_artifact"):
        print("FAIL-CLOSED: payload still references the obsolete uniform-run audit; use final accounting fields")
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
        "current_accounting_artifact": str(acct_path),
        "current_accounting_sha256": sha256(acct_path),
        "current_accounting_csv_artifact": str(FINAL_ACCOUNTING_CSV),
        "current_accounting_csv_sha256": sha256(FINAL_ACCOUNTING_CSV),
        "current_accounting_records": 484,
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
