#!/usr/bin/env python3
"""Read-only fail-closed validator for the V4 484-centroid review gate."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

V4 = Path(__file__).resolve().parents[1]
REPO = V4.parents[1]
RESULTS = V4 / "results"
REGISTER = RESULTS / "pfclpp_2f6i_484_independent_review.json"
INVENTORY = RESULTS / "pfclpp_2f6i_484_failure_inventory.json"
RESCUE_AUDIT = RESULTS / "pfclpp_2f6i_484_rescue_aggregate" / "rescue_audit_provenance.json"
CANONICAL_SMILES = REPO / "Project2_Polypharmacology_MD_ValidationV2607" / "data/from_project1/data/cluster_representatives_smiles.csv"
AUDIT_GLOB = "pfclpp_2f6i_484*/aggregation_provenance.json"


def load(path: Path, label: str, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            errors.append(f"{label} is not a JSON object")
            return {}
        return value
    except Exception as exc:
        errors.append(f"cannot read {label}: {exc}")
        return {}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def safe_artifact(value: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} path is missing")
        return None
    raw = Path(value)
    path = raw if raw.is_absolute() else REPO / raw
    try:
        path.resolve().relative_to(REPO.resolve())
    except ValueError:
        errors.append(f"{label} path escapes repository: {path}")
        return None
    return path


def discover_audits(errors: list[str]) -> tuple[dict, Path | None, list[dict]]:
    candidates: list[tuple[str, Path, dict]] = []
    for path in sorted(RESULTS.glob(AUDIT_GLOB)):
        if not path.is_file():
            continue
        data = load(path, f"audit {path}", errors)
        if data:
            candidates.append((str(data.get("created_utc") or datetime.min.isoformat()), path, data))
    candidates.sort(key=lambda item: item[0], reverse=True)
    current = (candidates[0][2], candidates[0][1]) if candidates else ({}, None)
    complete = [
        {"path": str(path), "data": data}
        for _, path, data in candidates
        if data.get("status") == "RAW_ARRAY_COMPLETE_PENDING_INDEPENDENT_REVIEW"
        and data.get("target") == "PfClpP" and data.get("pdb_id") == "2F6I"
        and data.get("records") == 484 and data.get("failures", 0) == 0
        and data.get("skipped_unfixable", 0) == 0
        and data.get("consensus_written") is False and data.get("rrs_pns_updated") is False
        and isinstance(data.get("aggregate_csv_artifact"), str)
        and isinstance(data.get("aggregate_csv_sha256"), str)
    ]
    return current[0], current[1], complete


def verify_dossier_binding(register: dict, errors: list[str]) -> None:
    dossier = safe_artifact(register.get("signed_review_artifact"), "signed review", errors)
    signature = safe_artifact(register.get("detached_signature_artifact"), "detached signature", errors)
    pubkey = safe_artifact(register.get("trusted_public_key_artifact"), "trusted public key", errors)
    if register.get("reviewer_independence_attestation") is not True:
        errors.append("reviewer independence attestation is not boolean true")
    if not isinstance(register.get("conflict_of_interest_declaration"), str) or not register.get("conflict_of_interest_declaration").strip():
        errors.append("conflict-of-interest declaration is missing or not text")
    if not all(p is not None and p.is_file() for p in (dossier, signature, pubkey)):
        errors.append("accepted V4 register lacks dossier/signature/public-key files")
        return
    assert dossier is not None and signature is not None and pubkey is not None
    if register.get("signed_review_sha256") != sha256(dossier): errors.append("signed review SHA-256 mismatch")
    if register.get("detached_signature_sha256") != sha256(signature): errors.append("detached signature SHA-256 mismatch")
    if register.get("trusted_public_key_sha256") != sha256(pubkey): errors.append("public-key SHA-256 mismatch")
    trusted_fp = os.environ.get("P1_TRUSTED_REVIEWER_PUBKEY_SHA256", "").lower()
    trusted_identity = os.environ.get("P1_TRUSTED_REVIEWER_IDENTITY", "")
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_fp) or trusted_fp != sha256(pubkey): errors.append("public key is not bound to external trust anchor")
    if not trusted_identity.strip() or trusted_identity != register.get("reviewer_identity"): errors.append("reviewer identity is not bound to external trust anchor")
    result = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pubkey), "-rawin", "-in", str(dossier), "-sigfile", str(signature)], capture_output=True, text=True, check=False)
    if result.returncode != 0 or "Signature Verified" not in result.stdout + result.stderr: errors.append("V4 detached signature verification failed")
    try: payload = json.loads(dossier.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"signed V4 payload is not JSON: {exc}"); return
    for field in ("reviewer_identity", "review_date_utc", "review_decision", "reviewer_independence_attestation", "conflict_of_interest_declaration", "current_audit_artifact", "current_audit_sha256", "current_audit_records"):
        if payload.get(field) != register.get(field): errors.append(f"signed V4 payload mismatch: {field}")
    if payload.get("review_decision") != "PASS" or payload.get("accepted_for_promotion") is not True: errors.append("signed V4 decision is not PASS/accepted")
    if payload.get("target") != register.get("target") or payload.get("pdb_id") != register.get("pdb_id") or payload.get("panel_size") != register.get("panel_size"): errors.append("signed V4 target/panel identity mismatch")
    if payload.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED" or payload.get("internal_work_authorized") is not False: errors.append("signed V4 authorization invariants are invalid")
    if register.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED" or register.get("internal_work_authorized") is not False: errors.append("accepted V4 authorization invariants are invalid")
    if payload.get("review_criteria") != register.get("review_criteria"): errors.append("signed V4 review criteria mismatch")
    required = ["genuine_pfclpp_identity_2f6i", "all_484_centroid_inputs_bound_to_canonical_smiles", "pdb_pdbqt_frame_equivalence_verified", "target_specific_triad_box_reviewed", "all_484_records_independently_pass_raw_checks", "failure_records_resolved_or_explicitly_excluded_by_protocol", "aggregate_reproducibly_reconstructed", "independent_reviewer_acceptance"]
    if any(register.get("review_criteria", {}).get(key) is not True for key in required): errors.append("accepted V4 criteria are incomplete")
    if payload.get("current_aggregate_csv_artifact") != register.get("current_aggregate_csv_artifact") or payload.get("current_aggregate_csv_sha256") != register.get("current_aggregate_csv_sha256") or payload.get("current_aggregate_csv_records") != 484: errors.append("signed V4 aggregate CSV binding mismatch")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    register = load(REGISTER, "V4 review register", errors)
    inventory = load(INVENTORY, "failure inventory", errors)
    rescue = load(RESCUE_AUDIT, "rescue audit", errors)
    current_audit, current_path, complete_audits = discover_audits(errors)
    if register.get("schema") != "p1-v4-pfclpp-2f6i-484-independent-review/v1": errors.append("unexpected V4 review-register schema")
    if register.get("scope") != "V4 historical 484-centroid replacement panel only": errors.append("review scope is not V4-specific")
    if register.get("target") != "PfClpP" or register.get("pdb_id") != "2F6I": errors.append("target identity is not PfClpP/2F6I")
    if register.get("panel_size") != 484: errors.append("panel size is not 484")
    if not isinstance(inventory.get("records"), list): errors.append("failure inventory records are missing")
    else:
        records = inventory["records"]
        if inventory.get("requested_records") != len(records): errors.append("failure inventory requested_records mismatch")
        if inventory.get("pass_raw_vina") != sum(r.get("status") == "PASS_RAW_VINA" for r in records): errors.append("failure inventory pass count mismatch")
        if inventory.get("failed_records") != sum(r.get("status") == "FAILED" for r in records): errors.append("failure inventory fail count mismatch")
        if inventory.get("missing_records") != 0: errors.append("failure inventory reports missing records")
    if rescue.get("status") not in {"RESCUE_SENSITIVITY_INCOMPLETE", "RESCUE_SENSITIVITY_AUDITED_PENDING_INDEPENDENT_REVIEW"}: errors.append("rescue audit status invalid")
    if rescue.get("consensus_written") is not False or rescue.get("rrs_pns_updated") is not False: errors.append("rescue audit records forbidden promotion")
    status = register.get("status")
    if status not in {"PENDING_INDEPENDENT_REVIEW", "INDEPENDENT_REVIEW_ACCEPTED", "INDEPENDENT_REVIEW_REJECTED"}: errors.append("invalid V4 review status")
    accepted = status == "INDEPENDENT_REVIEW_ACCEPTED" and register.get("accepted_for_promotion") is True
    if accepted:
        if not complete_audits: errors.append("accepted V4 state lacks complete 484 audit")
        else:
            selected = complete_audits[0]; audit_path = Path(selected["path"]); audit = selected["data"]
            if register.get("current_audit_artifact") != str(audit_path): errors.append("accepted register not bound to current audit")
            if register.get("current_audit_sha256") != sha256(audit_path): errors.append("accepted current-audit hash mismatch")
            if register.get("current_audit_records") != 484: errors.append("accepted current-audit record count mismatch")
            if not CANONICAL_SMILES.is_file() or audit.get("source_smiles_sha256") != sha256(CANONICAL_SMILES): errors.append("accepted audit source hash mismatch")
            if audit.get("aggregate_csv_artifact") != register.get("current_aggregate_csv_artifact"):
                errors.append("accepted audit/register aggregate CSV artifact mismatch")
            csv_value = audit.get("aggregate_csv_artifact")
            if not csv_value:
                errors.append("selected audit lacks explicit aggregate_csv_artifact")
            csv_path = safe_artifact(csv_value, "aggregate CSV", errors) if csv_value else None
            if csv_path is None or not csv_path.is_file():
                errors.append("accepted aggregate CSV artifact is missing")
            elif audit.get("aggregate_csv_sha256") != sha256(csv_path):
                errors.append("accepted aggregate CSV hash mismatch")
            elif register.get("current_aggregate_csv_artifact") != str(csv_path):
                errors.append("accepted register is not bound to aggregate CSV artifact")
            elif register.get("current_aggregate_csv_sha256") != sha256(csv_path):
                errors.append("accepted register aggregate CSV hash mismatch")
            elif register.get("current_aggregate_csv_records") != 484:
                errors.append("accepted aggregate CSV record count is not 484")
            else:
                try:
                    import csv
                    with csv_path.open(newline="", encoding="utf-8") as handle:
                        rows = list(csv.DictReader(handle))
                    canonical_rows = list(csv.DictReader(CANONICAL_SMILES.open(newline="", encoding="utf-8")))
                    if len(rows) != 484 or len(canonical_rows) != 484:
                        errors.append("accepted aggregate/canonical row counts are not 484")
                    else:
                        canonical = [row["SMILES"].strip() for row in canonical_rows]
                        observed = sorted(int(row["centroid_id"]) for row in rows)
                        if observed != list(range(484)):
                            errors.append("accepted aggregate IDs are not exactly 0..483")
                        for row in rows:
                            cid = int(row["centroid_id"])
                            if row.get("smiles", "").strip() != canonical[cid]:
                                errors.append(f"accepted aggregate SMILES mismatch at centroid {cid}")
                                break
                except (OSError, KeyError, ValueError) as exc:
                    errors.append(f"accepted aggregate/canonical correspondence check failed: {exc}")
        criteria = register.get("review_criteria", {})
        required = ["genuine_pfclpp_identity_2f6i", "all_484_centroid_inputs_bound_to_canonical_smiles", "pdb_pdbqt_frame_equivalence_verified", "target_specific_triad_box_reviewed", "all_484_records_independently_pass_raw_checks", "failure_records_resolved_or_explicitly_excluded_by_protocol", "aggregate_reproducibly_reconstructed", "independent_reviewer_acceptance"]
        if any(criteria.get(k) is not True for k in required): errors.append("accepted V4 review criteria are incomplete")
        verify_dossier_binding(register, errors)
        print("V4_REVIEW_GATE: ACCEPTED_FOR_PROMOTION")
    else:
        if register.get("accepted_for_promotion") is not False: errors.append("non-accepted state is not fail-closed")
        if register.get("internal_work_authorized") is not False: errors.append("internal_work_authorized is not false")
        warnings.append(f"current audit: {current_path} status={current_audit.get('status', 'MISSING')} records={current_audit.get('records', 'NA')}")
        warnings.append(f"complete 484-record audits available: {len(complete_audits)}")
        warnings.append("no signed independent review is active")
        print("V4_REVIEW_GATE: FAIL_CLOSED_PENDING_INDEPENDENT_REVIEW")
    if errors:
        print("V4_REVIEW_GATE: FAIL_CLOSED_INVALID_REGISTER")
        for error in errors: print(f"ERROR: {error}")
        return 2
    for warning in warnings: print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
