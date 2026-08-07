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

ALLOWED_SYSTEMS = {"201_DHFR", "438_ATP4", "164_ClpP", "214_CRT"}
REQUIRED = {
    "system_name", "cohort_id", "temperature_k", "protein_force_field",
    "ligand_force_field", "water_model", "topology_sha256", "coordinates_sha256",
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
    if payload.get("system_name") not in ALLOWED_SYSTEMS:
        errors.append(f"system_name is not allowlisted: {payload.get('system_name')!r}")
    if payload.get("temperature_k") != 310.15:
        errors.append(f"temperature_k must be 310.15, got {payload.get('temperature_k')!r}")
    if payload.get("protein_force_field") != "CHARMM36m":
        errors.append("protein_force_field must be CHARMM36m")
    if payload.get("ligand_force_field") != "CGenFF":
        errors.append("ligand_force_field must be CGenFF for a publication-grade future rerun")
    if payload.get("water_model") != "TIP3P":
        errors.append("water_model must be TIP3P")
    for key in ("topology_sha256", "coordinates_sha256"):
        value = payload.get(key)
        if not isinstance(value, str) or len(value) != 64:
            errors.append(f"{key} must be a 64-character SHA-256 hex string")
    if system_dir is not None:
        expected_dir_name = payload.get("system_name")
        if system_dir.name != expected_dir_name:
            errors.append(f"manifest system_name {expected_dir_name!r} does not match directory {system_dir.name!r}")
        for filename, key in (("topol.top", "topology_sha256"), ("npt.gro", "coordinates_sha256")):
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
    parser.add_argument("--system-dir", type=Path, default=None)
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
