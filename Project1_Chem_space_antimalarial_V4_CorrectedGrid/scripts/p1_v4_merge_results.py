#!/usr/bin/env python3
"""Merge uniform + fix results into a complete 484-centroid dataset."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P2 = ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
SMILES_FILE = P2 / "data/from_project1/data/cluster_representatives_smiles.csv"

UNIFORM_DIR = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_uniform_seed20260809"
FIX_DIR = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_fix_seed20260809"
MERGED_DIR = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_merged_seed20260809"

# Unfixable centroids (embed failures + tiny molecules that can't reach triad)
UNFIXABLE = {30, 43, 70, 99, 136, 145, 167, 170, 194, 195, 228, 340, 361, 390, 416}
REGISTER = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_independent_review.json"
AUDIT_ROOT = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results"
AUDIT_GLOB = "pfclpp_2f6i_484*/aggregation_provenance.json"


def _audit_candidates() -> list[tuple[str, Path, dict]]:
    candidates = []
    for path in AUDIT_ROOT.glob(AUDIT_GLOB):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        stamp = str(data.get("created_utc") or "")
        candidates.append((stamp, path, data))
    return sorted(candidates, key=lambda item: item[0], reverse=True)


def _complete_audit() -> tuple[Path | None, dict]:
    for _, path, data in _audit_candidates():
        if (data.get("status") == "RAW_ARRAY_COMPLETE_PENDING_INDEPENDENT_REVIEW"
                and data.get("target") == "PfClpP" and data.get("pdb_id") == "2F6I"
                and data.get("records") == 484 and data.get("failures", 0) == 0
                and data.get("skipped_unfixable", 0) == 0
                and data.get("consensus_written") is False
                and data.get("rrs_pns_updated") is False
                and isinstance(data.get("aggregate_csv_artifact"), str)
                and isinstance(data.get("aggregate_csv_sha256"), str)):
            return path, data
    return None, {}


def _safe_artifact(value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = Path(value)
    path = raw if raw.is_absolute() else ROOT / raw
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    return path


def _verify_signed_review(register: dict) -> tuple[bool, str]:
    if register.get("status") != "INDEPENDENT_REVIEW_ACCEPTED" or register.get("accepted_for_promotion") is not True:
        return False, "V4 independent-review register is not accepted_for_promotion"
    if register.get("target") != "PfClpP" or register.get("pdb_id") != "2F6I" or register.get("panel_size") != 484:
        return False, "V4 register target/panel identity is invalid"
    if register.get("reviewer_independence_attestation") is not True or not isinstance(register.get("conflict_of_interest_declaration"), str) or not register["conflict_of_interest_declaration"].strip():
        return False, "V4 reviewer attestations are missing or incorrectly typed"
    dossier = _safe_artifact(register.get("signed_review_artifact"))
    sig = _safe_artifact(register.get("detached_signature_artifact"))
    pub = _safe_artifact(register.get("trusted_public_key_artifact"))
    if not all(p is not None and p.is_file() for p in (dossier, sig, pub)):
        return False, "V4 detached review binding files are missing"
    assert dossier is not None and sig is not None and pub is not None
    if register.get("signed_review_sha256") != _sha256(dossier) or register.get("detached_signature_sha256") != _sha256(sig) or register.get("trusted_public_key_sha256") != _sha256(pub):
        return False, "V4 detached review binding hashes do not match"
    trusted_fp = os.environ.get("P1_TRUSTED_REVIEWER_PUBKEY_SHA256", "").lower()
    trusted_identity = os.environ.get("P1_TRUSTED_REVIEWER_IDENTITY", "")
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_fp) or trusted_fp != _sha256(pub):
        return False, "V4 public key is not bound to external trust anchor"
    if not trusted_identity.strip() or trusted_identity != register.get("reviewer_identity"):
        return False, "V4 reviewer identity is not bound to external trust anchor"
    verified = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pub), "-rawin", "-in", str(dossier), "-sigfile", str(sig)], capture_output=True, text=True, check=False)
    if verified.returncode != 0 or "Signature Verified" not in verified.stdout + verified.stderr:
        return False, "V4 detached review signature verification failed"
    try:
        payload = json.loads(dossier.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"V4 signed review payload is not valid JSON: {exc}"
    for field in ("status", "reviewer_identity", "review_date_utc", "review_decision",
                  "reviewer_independence_attestation", "conflict_of_interest_declaration",
                  "accepted_for_promotion", "target", "pdb_id", "panel_size",
                  "current_audit_artifact", "current_audit_sha256", "current_audit_records",
                  "current_aggregate_csv_artifact", "current_aggregate_csv_sha256",
                  "current_aggregate_csv_records", "review_criteria",
                  "authorization_mode", "internal_work_authorized"):
        if payload.get(field) != register.get(field):
            return False, f"V4 signed payload/register mismatch: {field}"
    if payload.get("status") != "INDEPENDENT_REVIEW_ACCEPTED" or payload.get("review_decision") != "PASS":
        return False, "V4 signed payload is not an explicit accepted PASS"
    if payload.get("authorization_mode") != "INDEPENDENT_REVIEW_REQUIRED" or payload.get("internal_work_authorized") is not False:
        return False, "V4 signed payload authorization invariants are invalid"
    required = ["genuine_pfclpp_identity_2f6i", "all_484_centroid_inputs_bound_to_canonical_smiles", "pdb_pdbqt_frame_equivalence_verified", "target_specific_triad_box_reviewed", "all_484_records_independently_pass_raw_checks", "failure_records_resolved_or_explicitly_excluded_by_protocol", "aggregate_reproducibly_reconstructed", "independent_reviewer_acceptance"]
    criteria = payload.get("review_criteria", {})
    if any(criteria.get(key) is not True for key in required):
        return False, "V4 signed payload review criteria are incomplete"
    return True, "accepted"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def promotion_gate() -> tuple[bool, str]:
    """Refuse legacy merging unless current evidence and signed review agree."""
    try:
        register = json.loads(REGISTER.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"cannot read V4 promotion register: {exc}"
    signed, reason = _verify_signed_review(register)
    if not signed:
        return False, reason
    audit_path, audit = _complete_audit()
    if audit_path is None:
        return False, "no explicit successful 484-record audit artifact exists"
    if register.get("current_audit_artifact") != str(audit_path):
        return False, "register is not bound to the current complete audit artifact"
    if register.get("current_audit_sha256") != _sha256(audit_path):
        return False, "register current-audit hash does not match"
    if register.get("current_audit_records") != 484:
        return False, "current audit is not a complete 484-record panel"
    csv_path = _safe_artifact(register.get("current_aggregate_csv_artifact"))
    if csv_path is None or not csv_path.is_file():
        return False, "current aggregate CSV artifact is missing"
    if register.get("current_aggregate_csv_sha256") != _sha256(csv_path):
        return False, "current aggregate CSV hash does not match"
    if register.get("current_aggregate_csv_records") != 484:
        return False, "current aggregate CSV record count is not 484"
    if audit.get("aggregate_csv_artifact") != register.get("current_aggregate_csv_artifact") or audit.get("aggregate_csv_sha256") != register.get("current_aggregate_csv_sha256"):
        return False, "current audit/register aggregate CSV binding does not match"
    try:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        ids = sorted(int(row["centroid_id"]) for row in rows)
    except (OSError, KeyError, ValueError) as exc:
        return False, f"current aggregate CSV cannot be parsed: {exc}"
    if len(rows) != 484 or ids != list(range(484)):
        return False, "current aggregate CSV does not contain exactly centroid IDs 0..483"
    try:
        with SMILES_FILE.open(newline="", encoding="utf-8") as handle:
            canonical = [row["SMILES"].strip() for row in csv.DictReader(handle)]
        if len(canonical) != 484 or any(row.get("smiles", "").strip() != canonical[int(row["centroid_id"])] for row in rows):
            return False, "current aggregate CSV SMILES do not correspond to canonical 484-row source"
    except (OSError, KeyError, ValueError) as exc:
        return False, f"cannot verify aggregate/canonical correspondence: {exc}"
    # A stale FAILED_CLOSED artifact is historical evidence only once a newer,
    # explicitly complete audit has been selected and hash-bound above.
    return True, "accepted"


def main():
    allowed, reason = promotion_gate()
    if not allowed:
        print(f"FAIL-CLOSED: legacy V4 merge/promotion refused: {reason}")
        return 2
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read SMILES
    with SMILES_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    smiles = [r["SMILES"].strip() for r in rows]
    
    passed = 0
    failed_unfixable = 0
    failed_other = 0
    
    for i in range(484):
        merged_out = MERGED_DIR / f"centroid_{i:04d}"
        
        # Check if already merged
        if (merged_out / "result.json").exists():
            passed += 1
            continue
        
        # Priority: fix results > uniform results
        fix_result = FIX_DIR / f"centroid_{i:04d}" / "result.json"
        uniform_result = UNIFORM_DIR / f"centroid_{i:04d}" / "result.json"
        
        merged_out.mkdir(parents=True, exist_ok=True)
        
        if fix_result.exists():
            # Use fix result
            shutil.copytree(FIX_DIR / f"centroid_{i:04d}", merged_out, dirs_exist_ok=True)
            passed += 1
        elif uniform_result.exists():
            # Use uniform result
            shutil.copytree(UNIFORM_DIR / f"centroid_{i:04d}", merged_out, dirs_exist_ok=True)
            passed += 1
        elif i in UNFIXABLE:
            # Known unfixable
            merged_out.mkdir(parents=True, exist_ok=True)
            failed_unfixable += 1
            (merged_out / "failure.json").write_text(json.dumps({
                "schema": "p1-v4-clpp-2f6i-merged/v1",
                "status": "UNFIXABLE",
                "message": f"Centroid {i} is unfixable (exotic structure or too small for triad contact)",
                "centroid_id": i,
                "smiles": smiles[i],
            }, indent=2) + "\n")
        else:
            # Unexpected failure
            merged_out.mkdir(parents=True, exist_ok=True)
            failed_other += 1
            (merged_out / "failure.json").write_text(json.dumps({
                "schema": "p1-v4-clpp-2f6i-merged/v1",
                "status": "UNEXPECTED_FAILURE",
                "message": f"Centroid {i} has no valid result",
                "centroid_id": i,
                "smiles": smiles[i],
            }, indent=2) + "\n")
    
    print(f"=== Merge complete ===")
    print(f"Total centroids: 484")
    print(f"Passed: {passed}")
    print(f"Unfixable (exotic/tiny): {failed_unfixable}")
    print(f"Other failures: {failed_other}")
    print(f"Pass rate: {passed}/484 ({100*passed/484:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
