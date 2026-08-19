#!/usr/bin/env python3
"""Fail-closed preflight for isolated PfCRT 114--122 loop reconstruction.

This script detects the declared sequence gap and checks whether a supported
internal-loop modeling backend is available. It deliberately does not call
PDBFixer's private residue-building helper, write a candidate PDB, modify a
canonical structure, or launch molecular dynamics.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_version(name: str) -> dict[str, object]:
    try:
        return {"available": True, "version": metadata.version(name)}
    except metadata.PackageNotFoundError:
        return {"available": False, "version": None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--mapping-artifact", type=Path, required=True)
    parser.add_argument("--uniprot-provenance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chain", default="A")
    parser.add_argument("--gap-start", type=int, default=114)
    parser.add_argument("--gap-end", type=int, default=122)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    reference = args.reference.resolve()
    mapping_path = args.mapping_artifact.resolve()
    provenance_path = args.uniprot_provenance.resolve()
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

    from pdbfixer import PDBFixer
    import openmm
    import pdbfixer

    fixer = PDBFixer(filename=str(reference))
    fixer.findMissingResidues()
    target = ["ASN", "LYS", "LYS", "GLY", "ASN", "SER", "LYS", "GLU", "ARG"]
    matching_regions = [
        {"key": list(key), "residues": residues}
        for key, residues in fixer.missingResidues.items()
        if residues == target
    ]
    mapping_key = mapping.get("key_checks", {})
    missing_numbers = mapping_key.get("missing_loop_pdb_numbers", [])
    gap_ok = missing_numbers == list(range(args.gap_start, args.gap_end + 1))
    mapping_ok = (
        mapping.get("status") == "MAPPING_AUDIT_ONLY"
        and mapping.get("reference", {}).get("path")
        and Path(mapping["reference"]["path"]).resolve() == reference
        and mapping.get("reference", {}).get("sha256") == sha256(reference)
        and gap_ok
        and mapping_key.get("pdb_residue_76_observed", {}).get("one_letter") == "T"
    )
    provenance_ok = (
        provenance.get("status") == "FETCHED_AUTHORITATIVE_SEQUENCE"
        and provenance.get("accession") == "W7FI62"
        and provenance.get("fasta", {}).get("residue_76") == "T"
        and provenance.get("fasta", {}).get("path")
        and Path(provenance["fasta"]["path"]).is_file()
        and provenance.get("fasta", {}).get("sha256") == sha256(Path(provenance["fasta"]["path"]))
    )
    modeller_available = importlib.util.find_spec("modeller") is not None
    status = (
        "READY_FOR_EXTERNAL_LOOP_MODELING_BACKEND"
        if len(matching_regions) == 1 and mapping_ok and provenance_ok and modeller_available
        else "BLOCKED_NO_LOOP_MODELING_BACKEND"
    )
    result = {
        "schema_version": 2,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "scientific_interpretation": "PREFLIGHT_ONLY_NO_CANDIDATE_NO_LOOP_RECONSTRUCTION_NO_MD",
        "preflight_provenance": {
            "script": str(script_path),
            "script_sha256": sha256(script_path),
            "python": sys.executable,
            "python_version": sys.version,
            "packages": {"pdbfixer": {"available": True, "version": getattr(pdbfixer, "__version__", None)}, "openmm": {"available": True, "version": getattr(openmm, "__version__", None)}, "modeller": package_version("modeller")},
        },
        "reference": {"path": str(reference), "sha256": sha256(reference), "chain": args.chain},
        "mapping_artifact": {"path": str(mapping_path), "sha256": sha256(mapping_path), "status": mapping.get("status"), "reference_hash_match": mapping.get("reference", {}).get("sha256") == sha256(reference), "missing_loop_pdb_numbers": missing_numbers, "critical_checks_pass": mapping_ok},
        "uniprot_provenance": {"path": str(provenance_path), "sha256": sha256(provenance_path), "status": provenance.get("status"), "accession": provenance.get("accession"), "critical_checks_pass": provenance_ok},
        "gap_detection": {"requested_pdb_window": [args.gap_start, args.gap_end], "expected_sequence": target, "matching_pdbfixer_regions": matching_regions, "exactly_one_matching_region": len(matching_regions) == 1, "mapping_gap_exact": gap_ok},
        "backend": {"pdbfixer": {"available": True, "version": getattr(pdbfixer, "__version__", None)}, "openmm": {"available": True, "version": getattr(openmm, "__version__", None)}, "modeller": package_version("modeller")},
        "boundary": "No candidate coordinates were generated. No PDBFixer private residue-builder was called. No canonical PDB, mutant PDB, Set-C directory, trajectory, QC output, or MD-RRS output was modified.",
        "next_required_input": "Provide a licensed/available internal-loop modeling backend (e.g., MODELLER, Rosetta, or a validated external comparative-model artifact) with sequence, template, seed, and output hashes before candidate generation.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "matching_regions": matching_regions, "mapping_ok": mapping_ok, "provenance_ok": provenance_ok, "modeller_available": modeller_available, "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
