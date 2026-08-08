#!/usr/bin/env python3
"""Geometry-only preflight for a proposed V5 Vina-grid revision.

This script deliberately does not run Vina, DiffDock, GROMACS, or downstream
consensus/RRS/PNS calculations. It compares the currently declared V5 grid
centers with the historical V2 corrected centers against the same raw DiffDock
rank-1 SDFs and the exact receptor PDBQTs used by the V5 score-only runner.

The proposed centers are hypotheses, not accepted scores. No ligand or receptor
coordinates are translated or modified.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from rdkit import Chem

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
RAW = V5 / "results/diffdock_full_68_verified"
MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
AUDIT = RAW / "independent_rank1_audit.csv"
OUT_CSV = V5 / "results/grid_revision_preflight.csv"
OUT_JSON = V5 / "results/grid_revision_preflight.provenance.json"
BOX = np.array((25.0, 25.0, 25.0), dtype=float)
TARGETS = {
    "PfDHFR": {
        "pdb_id": "7F3Y",
        "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt",
        "current_center": (1.33, -1.733, -23.842),
        "proposed_v2_center": (8.34, -13.9, -41.754),
        "historical_config": "Project1_Chem_space_antimalarial_V2_CorrectedGrid/Docking/Docking_7F3Y/config.txt",
    },
    "PfCRT": {
        "pdb_id": "6UKJ",
        "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/6UKJ.pdbqt",
        "current_center": (152.99, 151.042, 159.379),
        "proposed_v2_center": (152.5, 148.0, 154.5),
        "historical_config": "Project1_Chem_space_antimalarial_V2_CorrectedGrid/Docking/Docking_6UKJ/config.txt",
    },
    "PfClpP": {
        "pdb_id": "2F6I",
        "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/2F6I.pdbqt",
        "current_center": (-0.116, 40.446, 12.213),
        "proposed_v2_center": (-0.116, 40.446, 12.213),
        "historical_config": "P1V5_2F6I_PfClpP_verified_20260808",
    },
    "PfATP4": {
        "pdb_id": "9N10",
        "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/9N10.pdbqt",
        "current_center": (134.84, 133.10, 97.63),
        "proposed_v2_center": (129.3, 130.9, 92.4),
        "historical_config": "Project1_Chem_space_antimalarial_V2_CorrectedGrid/Docking/Docking_9N10/config.txt",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def receptor_coords(path: Path) -> np.ndarray:
    coords = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith(("ATOM  ", "HETATM")):
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
    return np.asarray(coords, dtype=float)


def ligand_coords(path: Path) -> np.ndarray:
    mol = next((m for m in Chem.SDMolSupplier(str(path), removeHs=False, sanitize=False) if m is not None), None)
    if mol is None or mol.GetNumConformers() == 0:
        raise SystemExit(f"FAIL-CLOSED unreadable rank-1 SDF: {path}")
    coords = np.asarray(mol.GetConformer().GetPositions(), dtype=float)
    if not np.isfinite(coords).all():
        raise SystemExit(f"FAIL-CLOSED non-finite rank-1 coordinates: {path}")
    return coords


def inside_fraction(coords: np.ndarray, center: tuple[float, float, float]) -> float:
    c = np.asarray(center, dtype=float)
    return float(np.all((coords >= c - BOX / 2) & (coords <= c + BOX / 2), axis=1).mean())


def status(fraction: float) -> str:
    if fraction == 1.0:
        return "IN_GRID"
    if fraction > 0.0:
        return "PARTIAL_GRID"
    return "OUTSIDE_GRID"


def main() -> int:
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        manifest_rows = list(csv.DictReader(f))
    with AUDIT.open(encoding="utf-8", newline="") as f:
        audit_rows = list(csv.DictReader(f))
    if len(manifest_rows) != 68 or len(audit_rows) != 68:
        raise SystemExit("FAIL-CLOSED expected 68 manifest and audit rows")
    if any(r["target"] == "PfClpP" and r["pdb_id"] == "4GM2" for r in manifest_rows):
        raise SystemExit("FAIL-CLOSED target identity mismatch: 4GM2 is PfClpR, not PfClpP")
    if any(r["target"] == "PfClpP" and r["pdb_id"] != "2F6I" for r in manifest_rows):
        raise SystemExit("FAIL-CLOSED PfClpP rows must reference the verified 2F6I receptor (EC 3.4.21.92)")
    audit_by_name = {r["complex_name"]: r for r in audit_rows}
    records = []
    receptor_hashes = {}
    for target, spec in TARGETS.items():
        receptor = spec["receptor"]
        if not receptor.is_file() or receptor.stat().st_size == 0:
            raise SystemExit(f"FAIL-CLOSED missing receptor PDBQT: {receptor}")
        receptor_hashes[target] = sha256(receptor)
    for row in manifest_rows:
        target = row["target"]
        name = row["complex_name"]
        rank1 = RAW / name / "rank1.sdf"
        coords = ligand_coords(rank1)
        current_fraction = inside_fraction(coords, TARGETS[target]["current_center"])
        proposed_fraction = inside_fraction(coords, TARGETS[target]["proposed_v2_center"])
        audit_row = audit_by_name.get(name)
        if audit_row is None or audit_row["rank1_sdf_sha256"] != sha256(rank1):
            raise SystemExit(f"FAIL-CLOSED audit hash mismatch for {name}")
        records.append({
            "candidate_id": row["candidate_id"],
            "target": target,
            "complex_name": name,
            "rank1_sdf_sha256": sha256(rank1),
            "current_center": ";".join(map(str, TARGETS[target]["current_center"])),
            "proposed_v2_center": ";".join(map(str, TARGETS[target]["proposed_v2_center"])),
            "box_size": ";".join(map(str, BOX.tolist())),
            "current_inside_fraction": current_fraction,
            "current_status": status(current_fraction),
            "proposed_inside_fraction": proposed_fraction,
            "proposed_status": status(proposed_fraction),
            "pose_was_translated": False,
            "receptor_was_modified": False,
            "vina_run": False,
            "consensus_status": "NOT_COMPUTED",
            "rrs_pns_status": "NOT_UPDATED",
        })
    fields = list(records[0])
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    summary = {
        "schema": "p1-v5-grid-revision-preflight/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PROPOSED_V2_GRID_GEOMETRY_ONLY_NOT_ACCEPTED",
        "manifest_sha256": sha256(MANIFEST),
        "audit_csv_sha256": sha256(AUDIT),
        "output_csv_sha256": sha256(OUT_CSV),
        "receptor_pdbqt_sha256": receptor_hashes,
        "box": BOX.tolist(),
        "historical_basis": "V2 config.txt files; historical configuration evidence, not new scores",
        "targets": {target: {"pdb_id": spec["pdb_id"], "current_center": spec["current_center"], "proposed_v2_center": spec["proposed_v2_center"], "historical_config": spec["historical_config"]} for target, spec in TARGETS.items()},
        "current_status_counts": {s: sum(r["current_status"] == s for r in records) for s in ("IN_GRID", "PARTIAL_GRID", "OUTSIDE_GRID")},
        "proposed_status_counts": {s: sum(r["proposed_status"] == s for r in records) for s in ("IN_GRID", "PARTIAL_GRID", "OUTSIDE_GRID")},
        "pose_translations": False,
        "receptor_modifications": False,
        "vina_launched": False,
        "consensus_scores_written": False,
        "rrs_pns_updated": False,
        "accepted_for_scoring": False,
        "acceptance_rule": "Do not score until proposed grid has 68/68 IN_GRID poses and receptor/grid identity is reviewed.",
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
