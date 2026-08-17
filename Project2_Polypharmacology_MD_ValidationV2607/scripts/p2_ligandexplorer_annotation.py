#!/usr/bin/env python3
"""Run LigandExplorer as an independent structural-ligand annotation step for P2.

This workflow annotates ligands present in the receptor structures used by P2.
It is deliberately separate from candidate ranking, docking-RRS, MD, and
MD-RRS.  It must not be interpreted as an activity or binding oracle.

The default panel uses the accepted P2 receptor identities:
    2F6I  PfClpP
    7F3Y  PfDHFR
    6UKJ  PfCRT
    9N10  PfATP4

4GM2 is intentionally excluded because it is PfClpR rather than active PfClpP.
The local LigandExplorer checkout is used only as an execution dependency; the
output manifest records its Git commit and the exact input hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
PROTEIN_DIR = PROJECT_DIR / "data" / "proteins"
DEFAULT_OUTPUT = PROJECT_DIR / "results" / "ligandexplorer_annotation_20260812"
DEFAULT_BIN = Path("/home/nanaengo/ligandexplorer/venv/bin/ligandexplorer")
PANEL = {
    "2F6I.pdb": {"target": "PfClpP", "pdb_id": "2F6I"},
    "7F3Y.pdb": {"target": "PfDHFR", "pdb_id": "7F3Y"},
    "6UKJ.pdb": {"target": "PfCRT", "pdb_id": "6UKJ"},
    "9N10.pdb": {"target": "PfATP4", "pdb_id": "9N10"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ligandexplorer_commit() -> str:
    checkout = Path("/home/nanaengo/ligandexplorer")
    result = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNAVAILABLE"


def audit_classifier_output(classifier_output: Path, records: list[dict]) -> dict:
    """Return a fail-closed, per-receptor audit of classifier artifacts.

    LigandExplorer may return zero while producing only copied receptor/water
    files.  Those files are not evidence of ligand classification, so only
    valid ligand-box JSON files with finite spatial fields count as artifacts.
    """
    required = ("center_x", "center_y", "center_z", "size_x", "size_y", "size_z")
    per_pdb = {}
    for record in records:
        pdb_id = record["pdb_id"]
        pdb_dir = classifier_output / pdb_id
        json_files = sorted(pdb_dir.glob("*.json")) if pdb_dir.is_dir() else []
        valid = []
        invalid = []
        for path in json_files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict) or any(key not in payload for key in required):
                    raise ValueError("missing required ligand-box fields")
                if not all(math.isfinite(float(payload[key])) for key in required):
                    raise ValueError("non-finite ligand-box field")
                valid.append({
                    "file": str(path.relative_to(classifier_output)),
                    "sha256": sha256(path),
                })
            except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
                invalid.append({
                    "file": str(path.relative_to(classifier_output)),
                    "reason": str(exc),
                })
        per_pdb[pdb_id] = {
            "target": record["target"],
            "json_count": len(json_files),
            "valid_json_count": len(valid),
            "invalid_json": invalid,
            "valid_artifacts": valid,                "artifact_status": "LIGAND_BOX_ARTIFACT_PRESENT" if valid else "NO_CLASSIFICATION_ARTIFACT",

        }
    return {
        "per_pdb": per_pdb,
        "all_pdbs_have_valid_artifacts": all(
            item["valid_json_count"] > 0 for item in per_pdb.values()
        ),
    }


def cli_help(binary: Path) -> str:
    result = subprocess.run([str(binary), "--help"], text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"LigandExplorer help failed: {result.stderr[-1000:]}")
    return result.stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=PROTEIN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--binary", type=Path, default=DEFAULT_BIN)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--backend", choices=("gnn", "lgbm"), default="gnn")
    parser.add_argument("--dry-run", action="store_true", help="Create no archive and run no classifier.")
    parser.add_argument("--force", action="store_true", help="Allow reuse of an existing output directory.")
    parser.add_argument(
        "--audit-existing",
        action="store_true",
        help="Audit an existing run and update its provenance without running LigandExplorer.",
    )
    return parser.parse_args()


def write_manifest(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    binary = args.binary.resolve()
    output = args.output_dir.resolve()
    if args.audit_existing:
        manifest_path = output / "annotation_provenance.json"
        if not manifest_path.is_file():
            raise SystemExit(f"Cannot audit existing run without provenance: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = manifest.get("receptor_panel", [])
        expected_by_id = {meta["pdb_id"]: {"filename": filename, "target": meta["target"]} for filename, meta in PANEL.items()}
        observed_ids = [record.get("pdb_id") for record in records]
        panel_valid = (
            len(records) == len(expected_by_id)
            and len(set(observed_ids)) == len(expected_by_id)
            and set(observed_ids) == set(expected_by_id)
            and all(
                record.get("filename") == expected_by_id.get(record.get("pdb_id"), {}).get("filename")
                and record.get("target") == expected_by_id.get(record.get("pdb_id"), {}).get("target")
                for record in records
            )
        )
        audit = audit_classifier_output(output / "ligandexplorer_output", records) if panel_valid else {
            "per_pdb": {},
            "all_pdbs_have_valid_artifacts": False,
        }
        manifest["artifact_audit"] = audit
        recorded_commit = manifest.get("ligandexplorer", {}).get("git_commit", "UNAVAILABLE")
        current_commit = ligandexplorer_commit()
        input_audit = {"panel_valid": panel_valid, "pdb": {}, "archive": {}}
        for record in records:
            source = Path(record.get("source", ""))
            exists = source.is_file()
            current_hash = sha256(source) if exists else None
            input_audit["pdb"][record.get("pdb_id", "UNKNOWN")] = {
                "exists": exists,
                "recorded_sha256": record.get("sha256"),
                "current_sha256": current_hash,
                "hash_match": bool(exists and current_hash == record.get("sha256")),
            }
        archive = manifest.get("input_archive", {}).get("path")
        archive_path = Path(archive) if archive else None
        archive_exists = bool(archive_path and archive_path.is_file())
        archive_hash = sha256(archive_path) if archive_exists else None
        input_audit["archive"] = {
            "exists": archive_exists,
            "recorded_sha256": manifest.get("input_archive", {}).get("sha256"),
            "current_sha256": archive_hash,
            "hash_match": bool(archive_exists and archive_hash == manifest.get("input_archive", {}).get("sha256")),
        }
        input_audit["git_commit"] = {
            "recorded": recorded_commit,
            "current": current_commit,
            "match": bool(recorded_commit != "UNAVAILABLE" and current_commit == recorded_commit),
        }
        manifest["input_integrity_audit"] = input_audit
        integrity_ok = (
            panel_valid
            and all(item["hash_match"] for item in input_audit["pdb"].values())
            and input_audit["archive"]["hash_match"]
            and input_audit["git_commit"]["match"]
        )
        if manifest.get("return_code") != 0:
            manifest["status"] = "FAILED"
        elif not integrity_ok:
            manifest["status"] = "FAILED_PROVENANCE"
        elif audit["all_pdbs_have_valid_artifacts"]:
            manifest["status"] = "COMPLETED_REQUIRES_MANUAL_REVIEW"
        else:
            manifest["status"] = "COMPLETED_PARTIAL_REQUIRES_MANUAL_REVIEW"
        write_manifest(manifest_path, manifest)
        print(json.dumps({"status": manifest["status"], "artifact_audit": audit, "input_integrity_audit": input_audit}, indent=2))
        return 2 if manifest["status"] in {"FAILED", "FAILED_PROVENANCE"} else 0

    if not binary.is_file() or not binary.stat().st_mode & 0o111:
        raise SystemExit(f"LigandExplorer executable unavailable: {binary}")
    if output.exists() and any(output.iterdir()) and not args.force:
        raise SystemExit(f"Refusing to reuse non-empty output directory: {output}; use --force only for an intentional rerun")

    records = []
    missing = []
    for filename, metadata in PANEL.items():
        source = (args.input_dir / filename).resolve()
        if not source.is_file() or source.stat().st_size == 0:
            missing.append(str(source))
            continue
        records.append({
            **metadata,
            "filename": filename,
            "source": str(source),
            "sha256": sha256(source),
            "size_bytes": source.stat().st_size,
        })
    if missing:
        raise SystemExit("Missing P2 receptor inputs:\n" + "\n".join(missing))

    help_text = cli_help(binary)
    now = datetime.now(timezone.utc).isoformat()
    commit = ligandexplorer_commit()
    manifest = {
        "schema_version": 1,
        "created_utc": now,
        "status": "DRY_RUN" if args.dry_run else "PREPARED",
        "analysis_role": "STRUCTURAL_LIGAND_ANNOTATION_ONLY",
        "claim_boundary": {
            "can_support": "annotation of ligands present in receptor PDB structures and structural relevance review",
            "cannot_support": [
                "IC50/EC50 or biological activity",
                "docking affinity or docking-RRS",
                "MD stability or MD-RRS",
                "experimental target engagement",
            ],
        },
        "receptor_panel": records,
        "excluded_receptor": {
            "filename": "4GM2.pdb",
            "reason": "PfClpR paralog, not active PfClpP; excluded from the P2 PfClpP annotation panel",
        },
        "ligandexplorer": {
            "binary": str(binary),
            "git_commit": commit,
            "backend": args.backend,
            "device": args.device,
            "help_sha256": hashlib.sha256(help_text.encode()).hexdigest(),
            "help_first_line": help_text.splitlines()[0] if help_text.splitlines() else "",
        },
    }

    if not args.dry_run and commit == "UNAVAILABLE":
        output.mkdir(parents=True, exist_ok=True)
        manifest["status"] = "FAILED_PROVENANCE"
        write_manifest(output / "annotation_provenance.json", manifest)
        raise SystemExit("LigandExplorer Git commit unavailable; refusing an untraceable run")

    if args.dry_run:
        output.mkdir(parents=True, exist_ok=True)
        write_manifest(output / "annotation_provenance.json", manifest)
        print(json.dumps({"status": "DRY_RUN", "inputs": len(records), "output": str(output)}, indent=2))
        return 0

    output.mkdir(parents=True, exist_ok=True)
    archive = output / "p2_receptor_panel.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for record in records:
            handle.write(record["source"], arcname=record["filename"])
    manifest["input_archive"] = {
        "path": str(archive),
        "sha256": sha256(archive),
        "size_bytes": archive.stat().st_size,
    }

    classifier_output = output / "ligandexplorer_output"
    if classifier_output.exists() and any(classifier_output.iterdir()):
        if not args.force:
            raise SystemExit(f"Refusing to reuse non-empty classifier output: {classifier_output}")
        shutil.rmtree(classifier_output)
    command = [
        str(binary), "-i", str(archive), "-o", str(classifier_output),
        "--backend", args.backend, "--device", args.device,
    ]
    manifest["command"] = command
    manifest["status"] = "RUNNING"
    write_manifest(output / "annotation_provenance.json", manifest)

    result = subprocess.run(command, cwd=output, text=True, capture_output=True)
    (output / "ligandexplorer.stdout.log").write_text(result.stdout, encoding="utf-8")
    (output / "ligandexplorer.stderr.log").write_text(result.stderr, encoding="utf-8")
    artifact_audit = audit_classifier_output(classifier_output, records)
    if result.returncode != 0:
        final_status = "FAILED"
    elif commit == "UNAVAILABLE":
        final_status = "FAILED_PROVENANCE"
    elif artifact_audit["all_pdbs_have_valid_artifacts"]:
        final_status = "COMPLETED_REQUIRES_MANUAL_REVIEW"
    else:
        final_status = "COMPLETED_PARTIAL_REQUIRES_MANUAL_REVIEW"
    manifest.update({
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "return_code": result.returncode,
        "stdout_sha256": sha256(output / "ligandexplorer.stdout.log"),
        "stderr_sha256": sha256(output / "ligandexplorer.stderr.log"),
        "output_files": sorted(
            str(path.relative_to(output)) for path in classifier_output.rglob("*") if path.is_file()
        ) if classifier_output.is_dir() else [],
        "artifact_audit": artifact_audit,
        "status": final_status,
    })
    write_manifest(output / "annotation_provenance.json", manifest)
    print(json.dumps({
        "status": manifest["status"],
        "return_code": result.returncode,
        "output": str(classifier_output),
        "files": len(manifest["output_files"]),
    }, indent=2))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
