#!/usr/bin/env python3
"""Validate provenance inputs before any future parent-study MD execution.

This validator is intentionally side-effect free: it reads a manifest and
checks policy; it never calls GROMACS and never creates simulation inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CANONICAL_SYSTEMS = {"201_PfDHFR", "438_PfATP4", "164_PfClpP", "214_PfCRT"}
REQUIRED = {
    "system_name", "cohort_id", "temperature_k", "protein_force_field",
    "ligand_force_field", "water_model", "topology_sha256", "coordinates_sha256",
    "checkpoint_sha256", "ions_sha256", "parameter_source", "parameter_version",
    "cgenff_provenance", "parameter_files", "source_manifest_path",
    "source_manifest_sha256", "ligand_formal_charge", "ligand_stereochemistry",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(payload: dict, system_dir: Path | None = None) -> list[str]:
    errors = []
    missing = sorted(REQUIRED - payload.keys())
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if payload.get("cohort_id") != "P2_PARENT_STUDY_MD_4":
        errors.append("cohort_id is not P2_PARENT_STUDY_MD_4")
    if payload.get("system_name") not in CANONICAL_SYSTEMS:
        errors.append(f"system_name must be canonical ({sorted(CANONICAL_SYSTEMS)}), got {payload.get('system_name')!r}")
    if payload.get("temperature_k") != 310.15:
        errors.append(f"temperature_k must be 310.15, got {payload.get('temperature_k')!r}")
    if payload.get("protein_force_field") != "CHARMM36m":
        errors.append("protein_force_field must be CHARMM36m")
    if payload.get("ligand_force_field") != "CGenFF":
        errors.append("ligand_force_field must be CGenFF for a publication-grade future rerun")
    if payload.get("water_model") != "TIP3P":
        errors.append("water_model must be TIP3P")
    for key in ("parameter_source", "parameter_version", "source_manifest_path", "ligand_stereochemistry"):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must record non-empty provenance")
    if not isinstance(payload.get("ligand_formal_charge"), int):
        errors.append("ligand_formal_charge must be an integer")
    provenance = payload.get("cgenff_provenance")
    if not isinstance(provenance, dict):
        errors.append("cgenff_provenance must be an object with stream_file, converter, and penalty_max")
    else:
        for key in ("stream_file", "converter"):
            if not isinstance(provenance.get(key), str) or not provenance[key].strip():
                errors.append(f"cgenff_provenance.{key} must be non-empty")
        if not isinstance(provenance.get("penalty_max"), (int, float)):
            errors.append("cgenff_provenance.penalty_max must be numeric")
    parameter_files = payload.get("parameter_files")
    if not isinstance(parameter_files, list) or not parameter_files:
        errors.append("parameter_files must list hashed CGenFF parameter files")
    else:
        for index, item in enumerate(parameter_files):
            if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
                errors.append(f"parameter_files[{index}] must contain path and sha256")
                continue
            if len(item["sha256"]) != 64:
                errors.append(f"parameter_files[{index}].sha256 must be a 64-character SHA-256 string")
    for key in ("topology_sha256", "coordinates_sha256", "checkpoint_sha256", "ions_sha256", "source_manifest_sha256"):
        value = payload.get(key)
        if not isinstance(value, str) or len(value) != 64:
            errors.append(f"{key} must be a 64-character SHA-256 hex string")
    if system_dir is not None:
        system_dir = system_dir.resolve()
        project_root = Path(__file__).resolve().parents[1]

        def confined(path: Path) -> bool:
            try:
                path.resolve().relative_to(project_root)
                return True
            except ValueError:
                return False

        source_path = payload.get("source_manifest_path")
        if isinstance(source_path, str) and isinstance(payload.get("source_manifest_sha256"), str) and len(payload["source_manifest_sha256"]) == 64:
            source_file = Path(source_path)
            if not source_file.is_absolute():
                source_file = system_dir / source_file
            if not confined(source_file):
                errors.append(f"source_manifest_path escapes project root: {source_file}")
            elif not source_file.is_file():
                errors.append(f"missing source manifest for hash verification: {source_file}")
            elif sha256(source_file) != payload["source_manifest_sha256"]:
                errors.append("source_manifest_sha256 does not match source_manifest_path")
        parameter_files = payload.get("parameter_files")
        if isinstance(parameter_files, list):
            for index, item in enumerate(parameter_files):
                if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
                    continue
                parameter_file = Path(item["path"])
                if not parameter_file.is_absolute():
                    parameter_file = system_dir / parameter_file
                if not confined(parameter_file):
                    errors.append(f"parameter_files[{index}].path escapes project root: {parameter_file}")
                elif not parameter_file.is_file():
                    errors.append(f"missing parameter file for hash verification: {parameter_file}")
                elif sha256(parameter_file) != item["sha256"]:
                    errors.append(f"parameter_files[{index}].sha256 does not match {parameter_file}")
        manifest_name = payload.get("system_name")
        expected_dir_name = manifest_name
        if system_dir.name != expected_dir_name:
            errors.append(f"manifest system_name {manifest_name!r} does not match canonical directory {system_dir.name!r}")
        for filename, key in (("ions.gro", "ions_sha256"), ("topol.top", "topology_sha256"), ("npt.gro", "coordinates_sha256"), ("npt.cpt", "checkpoint_sha256")):
            path = system_dir / filename
            if not path.is_file():
                errors.append(f"missing file for hash verification: {path}")
            elif isinstance(payload.get(key), str) and len(payload[key]) == 64:
                actual = sha256(path)
                if actual != payload[key]:
                    errors.append(f"{key} does not match {path.name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--system-dir", type=Path, required=True,
        help="canonical parent-study system directory used for all file-hash checks",
    )
    args = parser.parse_args()
    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL-CLOSED: cannot read manifest: {exc}")
        return 2
    errors = validate(payload, args.system_dir)
    if errors:
        print("FAIL-CLOSED: force-field manifest rejected")
        for error in errors:
            print(f"- {error}")
        return 2
    print("PASS: force-field manifest is eligible for explicit review")
    print("GROMACS launched: no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
