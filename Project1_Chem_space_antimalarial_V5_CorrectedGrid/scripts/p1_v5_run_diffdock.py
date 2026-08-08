#!/usr/bin/env python3
"""Run pinned DiffDock inference with fail-closed provenance.

This runner is the only approved entry point for the P1 V5 DiffDock execution.
It records the exact command, environment, hashes, timestamps, and return code.
It refuses to overwrite an existing run directory and rejects nonzero exits,
missing outputs, skipped complexes, and failed complexes.

It does not calculate Vina consensus, RRS, or PNS. Full 68-pair execution is
also blocked unless a separate, machine-readable authorization artifact exists;
that artifact is intentionally absent while the current technical smoke gate is
failed. Those downstream steps remain separate and blocked.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
try:
    from rdkit import Chem
except ImportError:  # pragma: no cover - the diffdock environment must provide RDKit
    Chem = None

ROOT = Path(__file__).resolve().parents[2]
DIFFDOCK_HOME = Path("/home/nanaengo/software/DiffDock")
CONFIG = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_diffdock_inference_config.yaml"
MANIFEST = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/diffdock_polypharm/diffdock_input_manifest.csv"
MIGRATION_MANIFEST = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/v5_migration_manifest.json"
TARGET_IDENTITY_AUDIT = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/target_identity_audit.json"
ENTRYPOINT = DIFFDOCK_HOME / "inference.py"
PYTHON = Path("/home/nanaengo/miniforge3/envs/diffdock/bin/python")
FULL_AUTHORIZATION = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/provenance/diffdock_full_execution_authorization.json"
SMOKE_GATE = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/diffdock_pocket_smoke_PP01_PfDHFR_rerun6/failure_provenance.json"
STRUCTURAL_PREFLIGHT = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/structural_pocket_preflight.json"
REFERENCE_LIGAND_PREFLIGHT = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/reference_ligand_preflight_rerun6.json"
INDEPENDENT_REVIEW = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/structural_pocket_independent_review.json"
PINNED_DIFFDOCK_PYTHON = Path("/home/nanaengo/miniforge3/envs/diffdock/bin/python")
VINA_GRID = {
    "PfDHFR": {"pdb_id": "7F3Y", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt", "center": [1.33, -1.733, -23.842], "box": [25.0, 25.0, 25.0]},
    "PfCRT": {"pdb_id": "6UKJ", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/6UKJ.pdbqt", "center": [152.99, 151.042, 159.379], "box": [25.0, 25.0, 25.0]},
    # CORRECTED 08/08/2026: old center was the barrel-channel centroid of all Ser/His/Asp;
    # genuine 2F6I catalytic triad (mature numbering; UniProt O97252 active-site Ser289 = 2F6I
    # Ser252, offset 37) is Ser252/His223/Asp219, canonical pocket = chain A triad centroid.
    "PfClpP": {"pdb_id": "2F6I", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/2F6I.pdbqt", "center": [-24.276, 17.28, -2.901], "box": [25.0, 25.0, 25.0]},
    "PfATP4": {"pdb_id": "9N10", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/9N10.pdbqt", "center": [134.84, 133.10, 97.63], "box": [25.0, 25.0, 25.0]},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"FAIL-CLOSED missing/empty {label}: {path}")


def require_full_authorization() -> None:
    """Refuse the 68-pair run until an explicit reviewed authorization exists."""
    require_file(FULL_AUTHORIZATION, "explicit full-run authorization artifact")
    require_file(PINNED_DIFFDOCK_PYTHON, "pinned DiffDock environment interpreter")
    try:
        authorization = json.loads(FULL_AUTHORIZATION.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL-CLOSED invalid full-run authorization artifact: {exc}") from exc
    if authorization.get("status") != "AUTHORIZED_68_PAIR_EXECUTION":
        raise SystemExit("FAIL-CLOSED full-run authorization status is not AUTHORIZED_68_PAIR_EXECUTION")
    if authorization.get("smoke_provenance") != str(SMOKE_GATE.resolve()):
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to the canonical smoke gate")
    require_file(SMOKE_GATE, "canonical smoke provenance")
    if authorization.get("smoke_provenance_sha256") != sha256(SMOKE_GATE):
        raise SystemExit("FAIL-CLOSED full-run authorization smoke provenance hash mismatch")
    require_file(MIGRATION_MANIFEST, "V5 migration manifest")
    require_file(TARGET_IDENTITY_AUDIT, "target-identity audit")
    if authorization.get("v5_migration_manifest") != str(MIGRATION_MANIFEST.resolve()):
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to the current V5 migration manifest")
    if authorization.get("v5_migration_manifest_sha256") != sha256(MIGRATION_MANIFEST):
        raise SystemExit("FAIL-CLOSED V5 migration manifest hash mismatch")
    if authorization.get("target_identity_audit") != str(TARGET_IDENTITY_AUDIT.resolve()):
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to the target-identity audit")
    if authorization.get("target_identity_audit_sha256") != sha256(TARGET_IDENTITY_AUDIT):
        raise SystemExit("FAIL-CLOSED target-identity audit hash mismatch")
    identity_audit = json.loads(TARGET_IDENTITY_AUDIT.read_text(encoding="utf-8"))
    if identity_audit.get("status") == "IDENTITY_MISMATCH_BLOCKS_INHERITED_V5_PANEL":
        raise SystemExit("FAIL-CLOSED target-identity audit blocks the inherited 4GM2/PfClpP panel")
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    if any(row.get("target") == "PfClpP" and row.get("pdb_id") == "4GM2" for row in manifest_rows):
        raise SystemExit("FAIL-CLOSED current input manifest still pairs PfClpP with 4GM2")
    require_file(STRUCTURAL_PREFLIGHT, "structural-pocket preflight")
    try:
        structural = json.loads(STRUCTURAL_PREFLIGHT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL-CLOSED invalid structural-pocket preflight: {exc}") from exc
    if structural.get("status") != "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED":
        raise SystemExit("FAIL-CLOSED structural-pocket preflight is not independently accepted")
    if structural.get("independent_review_status") != "PASSED":
        raise SystemExit("FAIL-CLOSED structural-pocket preflight lacks independent review")
    if structural.get("accepted_for_full_run") is not True:
        raise SystemExit("FAIL-CLOSED structural-pocket preflight has not accepted the full run")
    if structural.get("read_only") is not True or structural.get("review_required") is not False:
        raise SystemExit("FAIL-CLOSED structural-pocket preflight semantic flags are unsafe")
    if any(structural.get(key) is not False for key in ("diffdock_launched", "vina_launched", "gromacs_launched", "consensus_scores_written", "rrs_pns_updated")):
        raise SystemExit("FAIL-CLOSED structural-pocket preflight records a forbidden prior launch or score update")
    expected_pdbs = {
        "PfDHFR": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb",
        "PfCRT": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/6UKJ.pdb",
        "PfClpP": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb",
        "PfATP4": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/9N10.pdb",
    }
    if set(structural.get("targets", {})) != set(expected_pdbs):
        raise SystemExit("FAIL-CLOSED structural-pocket preflight target set is not exactly the four production targets")
    if structural["targets"].get("PfClpP", {}).get("evidence_class") == "TARGET_IDENTITY_MISMATCH_BLOCKED":
        raise SystemExit("FAIL-CLOSED 4GM2 is PfClpR, not PfClpP; replace the receptor before any future authorization")
    if any(target.get("evidence_class") in {"TARGET_IDENTITY_MISMATCH_BLOCKED", "HETATM_PROXY_REVIEW_REQUIRED", "GEOMETRY_ONLY_REVIEW_REQUIRED", "HETATM_LIGAND_CANDIDATE_REVIEW_REQUIRED"} for target in structural.get("targets", {}).values()):
        raise SystemExit("FAIL-CLOSED structural evidence classes are not accepted for full execution")
    for target, pdb in expected_pdbs.items():
        if structural["targets"][target].get("pdb_sha256") != sha256(pdb):
            raise SystemExit(f"FAIL-CLOSED structural-pocket preflight receptor hash mismatch: {target}")
    if authorization.get("structural_preflight") != str(STRUCTURAL_PREFLIGHT.resolve()):
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to structural-pocket preflight")
    if authorization.get("structural_preflight_sha256") != sha256(STRUCTURAL_PREFLIGHT):
        raise SystemExit("FAIL-CLOSED structural-pocket preflight hash mismatch")
    require_file(REFERENCE_LIGAND_PREFLIGHT, "complete reference-ligand preflight")
    try:
        reference = json.loads(REFERENCE_LIGAND_PREFLIGHT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL-CLOSED invalid reference-ligand preflight: {exc}") from exc
    if reference.get("schema") != "p1-v5-reference-ligand-preflight/v3":
        raise SystemExit("FAIL-CLOSED reference-ligand preflight schema is not v3")
    if reference.get("completion_status") != "COMPLETE_INVENTORY":
        raise SystemExit("FAIL-CLOSED reference-ligand preflight is incomplete")
    if reference.get("accepted_for_full_run") is not False:
        raise SystemExit("FAIL-CLOSED reference-ligand preflight acceptance flag is unsafe")
    if reference.get("diffdock_launched") is not False or reference.get("vina_launched") is not False or reference.get("gromacs_launched") is not False:
        raise SystemExit("FAIL-CLOSED reference-ligand preflight records a forbidden launch")
    sentinel = Path(reference.get("output_dir", "")) / "PREFLIGHT_COMPLETE.json"
    require_file(sentinel, "reference-ligand preflight completion sentinel")
    sentinel_data = json.loads(sentinel.read_text(encoding="utf-8"))
    if sentinel_data.get("result_json_sha256") != sha256(REFERENCE_LIGAND_PREFLIGHT):
        raise SystemExit("FAIL-CLOSED reference-ligand preflight sentinel content hash mismatch")
    if authorization.get("reference_ligand_preflight_sentinel") != str(sentinel.resolve()):
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to reference-ligand sentinel")
    if authorization.get("reference_ligand_preflight_sentinel_sha256") != sha256(sentinel):
        raise SystemExit("FAIL-CLOSED reference-ligand preflight sentinel hash mismatch")
    if authorization.get("reference_ligand_preflight") != str(REFERENCE_LIGAND_PREFLIGHT.resolve()):
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to reference-ligand preflight")
    if authorization.get("reference_ligand_preflight_sha256") != sha256(REFERENCE_LIGAND_PREFLIGHT):
        raise SystemExit("FAIL-CLOSED reference-ligand preflight hash mismatch")
    reference_script = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_reference_ligand_preflight.py"
    if reference.get("script_sha256") != sha256(reference_script):
        raise SystemExit("FAIL-CLOSED reference-ligand preflight script hash mismatch")
    require_file(INDEPENDENT_REVIEW, "independent structural-pocket review")
    try:
        independent_review = json.loads(INDEPENDENT_REVIEW.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL-CLOSED invalid independent structural-pocket review: {exc}") from exc
    if independent_review.get("status") != "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED":
        raise SystemExit("FAIL-CLOSED independent structural-pocket review is not accepted")
    if independent_review.get("accepted_for_full_run") is not True:
        raise SystemExit("FAIL-CLOSED independent structural-pocket review has not accepted the full run")
    reviewer_identity = independent_review.get("reviewer_identity")
    signed_review_sha256 = independent_review.get("signed_review_sha256")
    signed_review_artifact = independent_review.get("signed_review_artifact")
    detached_signature_artifact = independent_review.get("detached_signature_artifact")
    trusted_public_key_artifact = independent_review.get("trusted_public_key_artifact")
    if not isinstance(reviewer_identity, str) or not reviewer_identity.strip():
        raise SystemExit("FAIL-CLOSED independent review lacks reviewer identity")
    if not isinstance(signed_review_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", signed_review_sha256):
        raise SystemExit("FAIL-CLOSED independent review lacks a valid signed-review SHA-256")
    if not isinstance(signed_review_artifact, str) or not signed_review_artifact.strip():
        raise SystemExit("FAIL-CLOSED independent review lacks a detached signed-review artifact")
    if not isinstance(detached_signature_artifact, str) or not detached_signature_artifact.strip() or not isinstance(trusted_public_key_artifact, str) or not trusted_public_key_artifact.strip():
        raise SystemExit("FAIL-CLOSED independent review lacks detached signature/public-key artifacts")
    signed_artifact_path = Path(signed_review_artifact)
    require_file(signed_artifact_path, "detached signed structural review artifact")
    if sha256(signed_artifact_path) != signed_review_sha256:
        raise SystemExit("FAIL-CLOSED detached signed structural review hash mismatch")
    # The detached signature must cover the same decision record that the
    # machine-readable register presents. Signature validity alone is not enough
    # if the signed artifact is unrelated to this register.
    try:
        signed_content = json.loads(signed_artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL-CLOSED signed structural review artifact is not JSON: {exc}") from exc
    decision_fields = ("status", "reviewer_identity", "review_date", "accepted_for_full_run", "criteria", "targets")
    if any(signed_content.get(field) != independent_review.get(field) for field in decision_fields):
        raise SystemExit("FAIL-CLOSED signed review decision content does not match the review register")
    signature_path = Path(detached_signature_artifact)
    public_key_path = Path(trusted_public_key_artifact)
    require_file(signature_path, "detached structural review signature")
    require_file(public_key_path, "trusted structural review public key")
    if independent_review.get("detached_signature_sha256") != sha256(signature_path) or independent_review.get("trusted_public_key_sha256") != sha256(public_key_path):
        raise SystemExit("FAIL-CLOSED detached signature/public-key hash mismatch")
    verify = subprocess.run(["openssl", "dgst", "-sha256", "-verify", str(public_key_path), "-signature", str(signature_path), str(signed_artifact_path)], capture_output=True, text=True)
    if verify.returncode != 0 or "Verified OK" not in verify.stdout:
        raise SystemExit("FAIL-CLOSED detached structural review signature verification failed")
    if authorization.get("signed_review_artifact") != str(signed_artifact_path.resolve()) or authorization.get("signed_review_artifact_sha256") != signed_review_sha256:
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to detached signed review")
    criteria = independent_review.get("criteria", {})
    if criteria.get("all_four_targets_individually_accepted") is not True:
        raise SystemExit("FAIL-CLOSED independent review has not accepted all four targets")
    target_decisions = independent_review.get("targets", {})
    if set(target_decisions) != {"PfDHFR", "PfCRT", "PfClpP", "PfATP4"} or any(v.get("decision") != "PASS" for v in target_decisions.values()):
        raise SystemExit("FAIL-CLOSED independent review target decisions are incomplete")
    if authorization.get("independent_review") != str(INDEPENDENT_REVIEW.resolve()):
        raise SystemExit("FAIL-CLOSED full-run authorization is not bound to independent structural review")
    if authorization.get("independent_review_sha256") != sha256(INDEPENDENT_REVIEW):
        raise SystemExit("FAIL-CLOSED independent structural review hash mismatch")
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    score_dir = Path(config["model_dir"])
    confidence_dir = Path(config["confidence_model_dir"])
    if not score_dir.is_absolute():
        score_dir = DIFFDOCK_HOME / score_dir
    if not confidence_dir.is_absolute():
        confidence_dir = DIFFDOCK_HOME / confidence_dir
    source_clean = subprocess.run(
        ["git", "-C", str(DIFFDOCK_HOME), "status", "--porcelain", "--untracked-files=all"],
        check=True, capture_output=True, text=True,
    ).stdout.strip() == ""
    if not source_clean:
        raise SystemExit("FAIL-CLOSED DiffDock source tree has uncommitted tracked changes")
    target_configs = {
        target: {
            "pdb_id": spec["pdb_id"],
            "receptor": str(spec["receptor"].resolve()),
            "receptor_sha256": sha256(spec["receptor"]),
            "center": spec["center"],
            "box": spec["box"],
        }
        for target, spec in VINA_GRID.items()
    }
    artifacts = {
        "runner_sha256": sha256(Path(__file__).resolve()),
        "config_sha256": sha256(CONFIG),
        "manifest_sha256": sha256(MANIFEST),
        "diffdock_entrypoint_sha256": sha256(ENTRYPOINT),
        "diffdock_source_clean": source_clean,
        "vina_target_configs": target_configs,
        "diffdock_source_git_head": subprocess.run(
            ["git", "-C", str(DIFFDOCK_HOME), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip(),
        "score_checkpoint_sha256": sha256(score_dir / config["ckpt"]),
        "confidence_checkpoint_sha256": sha256(confidence_dir / config["confidence_ckpt"]),
        "score_parameters_sha256": sha256(score_dir / "model_parameters.yml"),
        "confidence_parameters_sha256": sha256(confidence_dir / "model_parameters.yml"),
    }
    for key, expected in artifacts.items():
        if authorization.get(key) != expected:
            raise SystemExit(f"FAIL-CLOSED full-run authorization {key} mismatch")
    smoke = json.loads(SMOKE_GATE.read_text(encoding="utf-8"))
    if smoke.get("status") != "TECHNICAL_SMOKE_RANK1_VERIFIED_NO_BIOLOGICAL_VALIDATION":
        raise SystemExit("FAIL-CLOSED canonical smoke gate is not a verified technical smoke")
    if smoke.get("accepted_for_full_run") is not True:
        raise SystemExit("FAIL-CLOSED canonical smoke has not explicitly accepted the full run")
    if smoke.get("status") != "TECHNICAL_SMOKE_RANK1_VERIFIED_NO_BIOLOGICAL_VALIDATION":
        raise SystemExit("FAIL-CLOSED canonical smoke status is not the accepted technical status")


def write_failure_provenance(output: Path, base: dict, reason: str, **details) -> None:
    failure = dict(base)
    failure.update({
        "status": "TECHNICAL_SMOKE_FAILED_CLOSED",
        "reason": reason,
        "accepted_for_full_run": False,
        "consensus_scores_written": False,
        "rrs_pns_updated": False,
        **details,
    })
    (output / "failure_provenance.json").write_text(
        json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def read_manifest() -> list[dict[str, str]]:
    require_file(MANIFEST, "input manifest")
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) not in {1, 68}:
        raise SystemExit(f"FAIL-CLOSED expected smoke manifest of 1 or full manifest of 68 rows, found {len(rows)}")
    names = [row["complex_name"] for row in rows]
    if len(names) != len(set(names)):
        raise SystemExit("FAIL-CLOSED duplicate complex_name in input manifest")
    for row in rows:
        protein = Path(row["protein_path"])
        require_file(protein, f"protein for {row['complex_name']}")
        if sha256(protein) != row["protein_sha256"]:
            raise SystemExit(f"FAIL-CLOSED protein hash mismatch: {row['complex_name']}")
        if not row["ligand_description"] or not row["candidate_id"]:
            raise SystemExit(f"FAIL-CLOSED incomplete manifest row: {row}")
    return rows


def parse_counts(log_text: str) -> tuple[int | None, int | None]:
    match = re.search(r"Failed for (\d+) / \d+ complexes\.\s+Skipped (\d+) / \d+ complexes", log_text, re.S)
    return (int(match.group(1)), int(match.group(2))) if match else (None, None)


def _readable_sdf(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    if Chem is None:
        raise SystemExit("FAIL-CLOSED RDKit is unavailable; cannot validate SDF readability")
    supplier = Chem.SDMolSupplier(str(path), removeHs=False, sanitize=False)
    return any(mol is not None for mol in supplier)


def verify_outputs(out_dir: Path, rows: list[dict[str, str]], log_text: str, expected_samples: int) -> dict:
    failures, skipped = parse_counts(log_text)
    if failures is None or skipped is None:
        raise SystemExit("FAIL-CLOSED DiffDock log lacks the final failure/skip summary")
    expected = {row["complex_name"] for row in rows}
    actual_dirs = {p.name for p in out_dir.iterdir() if p.is_dir()}
    if actual_dirs != expected:
        raise SystemExit(f"FAIL-CLOSED output directories mismatch; missing={sorted(expected-actual_dirs)}, unexpected={sorted(actual_dirs-expected)}")
    if failures != 0 or skipped != 0:
        raise SystemExit(f"FAIL-CLOSED DiffDock log reports failures={failures}, skipped={skipped}")
    output_records = []
    confidence_pattern = re.compile(r"^rank(\d+)_confidence[-+]?\d+(?:\.\d+)?\.sdf$")
    expected_ranks = set(range(1, expected_samples + 1))
    for row in rows:
        directory = out_dir / row["complex_name"]
        rank1 = directory / "rank1.sdf"
        confidence = sorted(directory.glob("rank*_confidence*.sdf"))
        rank_map = {}
        for path in confidence:
            match = confidence_pattern.match(path.name)
            if match:
                rank_map.setdefault(int(match.group(1)), []).append(path)
        if set(rank_map) != expected_ranks or any(len(paths) != 1 for paths in rank_map.values()):
            raise SystemExit(f"FAIL-CLOSED confidence outputs mismatch for {row['complex_name']}: expected ranks {sorted(expected_ranks)}, found {sorted(rank_map)}")
        if not _readable_sdf(rank1):
            raise SystemExit(f"FAIL-CLOSED unreadable or empty rank1.sdf for {row['complex_name']}")
        if any(not _readable_sdf(paths[0]) for paths in rank_map.values()):
            raise SystemExit(f"FAIL-CLOSED unreadable confidence SDF for {row['complex_name']}")
        rank1_confidence = rank_map[1][0]
        output_records.append({
            "complex_name": row["complex_name"],
            "candidate_id": row["candidate_id"],
            "target": row["target"],
            "rank1_sdf": str(rank1.resolve()),
            "rank1_sdf_sha256": sha256(rank1),
            "rank1_confidence_sdf": str(rank1_confidence.resolve()),
            "rank1_confidence_sdf_sha256": sha256(rank1_confidence),
            "confidence_sdf_count": len(confidence),
            "confidence_ranks": sorted(rank_map),
        })
    return {"expected_pairs": len(rows), "failures": failures, "skipped": skipped, "samples_per_complex": expected_samples, "outputs": output_records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "full"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "full":
        # This gate runs before creating an output directory or launching any
        # subprocess. No reviewed authorization currently exists.
        require_full_authorization()
    output = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"FAIL-CLOSED output directory exists and is non-empty: {output}")
    rows = read_manifest()
    if args.mode == "full" and len(rows) != 68:
        raise SystemExit(f"FAIL-CLOSED full mode requires exactly 68 manifest rows, found {len(rows)}")
    output.mkdir(parents=True, exist_ok=False)
    if PYTHON != PINNED_DIFFDOCK_PYTHON:
        raise SystemExit("FAIL-CLOSED runner interpreter is not the pinned DiffDock interpreter")
    if args.mode == "smoke":
        rows = [row for row in rows if row["candidate_id"] == "PP-01" and row["target"] == "PfDHFR"]
        if len(rows) != 1:
            raise SystemExit("FAIL-CLOSED smoke row PP-01/PfDHFR not found")
        smoke_manifest = output / "smoke_input_manifest.csv"
        with smoke_manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        input_csv = smoke_manifest
    else:
        input_csv = MANIFEST
    require_file(CONFIG, "pinned DiffDock config")
    require_file(ENTRYPOINT, "DiffDock entrypoint")
    with CONFIG.open(encoding="utf-8") as handle:
        config_values = yaml.safe_load(handle)
    expected_samples = int(config_values["samples_per_complex"])
    if expected_samples < 1:
        raise SystemExit("FAIL-CLOSED invalid samples_per_complex in pinned config")
    command = [
        str(PYTHON), str(ENTRYPOINT),
        "--config", str(CONFIG.resolve()),
        "--loglevel", "INFO",
        "--protein_ligand_csv", str(input_csv.resolve()),
        "--out_dir", str(output.resolve()),
    ]
    started = datetime.now(timezone.utc).isoformat()
    log_path = output / "diffdock_execution.log"
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["DIFFDOCK_RUN_MODE"] = args.mode
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.run(command, cwd=DIFFDOCK_HOME, env=env, stdout=log, stderr=subprocess.STDOUT, text=True)
    ended = datetime.now(timezone.utc).isoformat()
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    failure_base = {
        "schema": "p1-v5-diffdock-execution-failure/v1",
        "mode": args.mode,
        "started_utc": started,
        "ended_utc": ended,
        "command": command,
        "cwd": str(DIFFDOCK_HOME),
        "python": str(PYTHON),
        "python_version": platform.python_version(),
        "config_sha256": sha256(CONFIG),
        "entrypoint_sha256": sha256(ENTRYPOINT),
        "input_manifest_sha256": sha256(input_csv),
        "log_sha256": sha256(log_path),
        "returncode": process.returncode,
    }
    if process.returncode != 0:
        write_failure_provenance(output, failure_base, "DIFFDOCK_NONZERO_EXIT", log=str(log_path))
        raise SystemExit(f"FAIL-CLOSED DiffDock returned exit code {process.returncode}; see {log_path}")
    if f"Results saved in {output.resolve()}" not in log_text:
        write_failure_provenance(output, failure_base, "LOG_MISSING_EXPECTED_OUTPUT_PATH")
        raise SystemExit("FAIL-CLOSED DiffDock log lacks expected output path")
    try:
        output_summary = verify_outputs(output, rows, log_text, expected_samples)
    except SystemExit as exc:
        write_failure_provenance(output, failure_base, "OUTPUT_VERIFICATION_FAILED", verification_error=str(exc))
        raise
    provenance = {
        "schema": "p1-v5-diffdock-execution/v1",
        "status": "RAW_OUTPUTS_VERIFIED",
        "mode": args.mode,
        "started_utc": started,
        "ended_utc": ended,
        "command": command,
        "cwd": str(DIFFDOCK_HOME),
        "python": str(PYTHON),
        "python_version": platform.python_version(),
        "config_sha256": sha256(CONFIG),
        "entrypoint_sha256": sha256(ENTRYPOINT),
        "input_manifest_sha256": sha256(input_csv),
        "log_sha256": sha256(log_path),
        "returncode": process.returncode,
        "raw_output_summary": output_summary,
        "consensus_scores_written": False,
        "rrs_pns_updated": False,
    }
    (output / "execution_provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": provenance["status"], "mode": args.mode, "pairs": len(rows), "output": str(output), "returncode": process.returncode}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
