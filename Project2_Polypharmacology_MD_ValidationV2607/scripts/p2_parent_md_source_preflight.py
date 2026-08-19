#!/usr/bin/env python3
"""Read-only source-identity preflight for the four parent-study MD systems.

The script inventories receptor and ligand candidates, hashes every file, and
marks unresolved identity/selection issues explicitly. It never copies,
modifies, parameterizes, or runs any molecular-dynamics input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
ROOT = PROJECT_DIR.parent
DEFAULT_OUTPUT = PROJECT_DIR / "results" / "metrics" / "parent_md_source_inventory.json"

SYSTEMS = {
    "201_PfDHFR": {"lead": "201", "target": "PfDHFR", "pdb_id": "7F3Y"},
    "438_PfATP4": {"lead": "438", "target": "PfATP4", "pdb_id": "9N10"},
    "164_PfClpP": {"lead": "164", "target": "PfClpP", "pdb_id": "4GM2"},
    "214_PfCRT": {"lead": "214", "target": "PfCRT", "pdb_id": "6UKJ"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atom_count(path: Path) -> int:
    try:
        return sum(
            line.startswith(("ATOM", "HETATM"))
            for line in path.read_text(errors="replace").splitlines()
        )
    except OSError:
        return 0


def describe(path: Path) -> dict:
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "exists": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256(path) if path.is_file() and path.stat().st_size else None,
        "atom_count": atom_count(path) if path.is_file() else None,
    }


def receptor_candidates(pdb_id: str) -> list[Path]:
    candidates = []
    for base in (
        PROJECT_DIR / "data" / "proteins",
        PROJECT_DIR / "data" / "from_project1" / "data" / "proteins",
        ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid",
        ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid",
    ):
        candidates.extend(base.glob(f"**/{pdb_id}.pdb"))
    return sorted({p.resolve() for p in candidates})


def ligand_candidates(lead: str) -> list[Path]:
    candidates = []
    for base in (
        PROJECT_DIR / "data" / "from_project1" / "data" / "pdb_ligands",
        PROJECT_DIR / "data" / "from_project1" / "data" / "pdb_ligands_mmv",
        PROJECT_DIR / "data" / "from_project1" / "results" / "ligands" / "pdb",
        PROJECT_DIR / "MD_systems",
    ):
        candidates.extend(base.glob(f"**/ligand_{lead}*.pdb"))
    return sorted({p.resolve() for p in candidates})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    systems = []
    for system_name, spec in SYSTEMS.items():
        receptors = receptor_candidates(spec["pdb_id"])
        ligands = ligand_candidates(spec["lead"])
        blockers = []
        if not receptors:
            blockers.append("no receptor PDB candidate found")
        if not ligands:
            blockers.append("no ligand PDB candidate found")
        if len(ligands) != 1:
            blockers.append(
                f"ambiguous ligand source selection: {len(ligands)} candidates; canonical SMILES/identity review required"
            )
        if system_name == "164_PfClpP":
            blockers.append("target identity blocked: historical PDB 4GM2 is PfClpR, not PfClpP")
        blockers.append("independent receptor-ligand correspondence review required")
        blockers.append("canonical SMILES, formal charge, stereochemistry, and docking-pose linkage not yet bound")
        systems.append(
            {
                "system_name": system_name,
                "lead": spec["lead"],
                "declared_target": spec["target"],
                "target_identity_status": (
                    "HISTORICAL_PFCLPR_LABEL_NOT_PFCLPP"
                    if system_name == "164_PfClpP" else "REQUIRES_INDEPENDENT_REVIEW"
                ),
                "declared_pdb_id": spec["pdb_id"],
                "receptor_candidates": [describe(path) for path in receptors],
                "ligand_candidates": [describe(path) for path in ligands],
                "status": "SOURCE_IDENTITY_BLOCKED",
                "blockers": blockers,
            }
        )

    record = {
        "schema": "p2-parent-md-source-preflight/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "read_only_inputs": True,
        "derived_report_only": True,
        "inventory_only": True,
        "final_source_manifest": False,
        "selected_source_records": [],
        "canonical_smiles_bound": False,
        "gromacs_launched": False,
        "parameters_generated": False,
        "coordinates_modified": False,
        "overall_status": "FAIL_CLOSED_SOURCE_IDENTITY_REVIEW_REQUIRED",
        "eligible_system_count": 0,
        "blocked_system_count": len(systems),
        "policy_note": "This candidate inventory does not select source files, does not bind canonical chemistry, does not authorize MD, and cannot replace a reviewed parent_md_source_manifest.json or forcefield_manifest.json.",
        "systems": systems,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
