#!/usr/bin/env python3
"""Independent, read-only audit of the V5 68-pair DiffDock run.

This script does not run docking and does not modify scientific scores. It validates
rank-1 pose SDFs and rank-1 confidence SDFs, audits all secondary confidence poses,
extracts confidence values from filenames, measures compatibility with the
predeclared Vina grids, and records why Vina/RRS/PNS remain blocked.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from rdkit import Chem

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
RAW = V5 / "results/diffdock_full_68_verified"
AUDIT_CSV = RAW / "independent_rank1_audit.csv"
AUDIT_JSON = RAW / "independent_rank1_audit.provenance.json"
TARGETS = {
    "PfDHFR": {"receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt", "center": (1.33, -1.733, -23.842)},
    "PfCRT": {"receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/6UKJ.pdbqt", "center": (152.99, 151.042, 159.379)},
    "PfClpP": {"receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/4GM2.pdbqt", "center": (26.19, 35.09, 24.72)},
    "PfATP4": {"receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/9N10.pdbqt", "center": (134.84, 133.10, 97.63)},
}
BOX = np.array((25.0, 25.0, 25.0))
CONFIDENCE_RE = re.compile(r"^rank1_confidence(?P<score>[-+]?\d+(?:\.\d+)?)\.sdf$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pdbqt_coords(path: Path) -> np.ndarray:
    coords = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith(("ATOM  ", "HETATM")):
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
    return np.asarray(coords, dtype=float)


def sdf_coords(path: Path) -> tuple[bool, np.ndarray, int]:
    try:
        mol = next((m for m in Chem.SDMolSupplier(str(path), removeHs=False, sanitize=False) if m is not None), None)
        if mol is None or mol.GetNumConformers() == 0:
            return False, np.empty((0, 3)), 0
        coords = np.asarray(mol.GetConformer().GetPositions(), dtype=float)
        return bool(np.isfinite(coords).all()), coords, mol.GetNumAtoms()
    except Exception:
        return False, np.empty((0, 3)), 0


def raw_tree_hash() -> tuple[str, int]:
    lines = []
    for path in sorted(RAW.rglob("*")):
        if path.is_file() and path.name not in {AUDIT_CSV.name, AUDIT_JSON.name}:
            lines.append(f"{sha256(path)}  {path.relative_to(RAW)}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest(), len(lines)


def main() -> int:
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 68 or len({r["complex_name"] for r in rows}) != 68:
        raise SystemExit("FAIL-CLOSED manifest is not the expected unique 68-pair panel")
    if any(r["target"] == "PfClpP" and r["pdb_id"] == "4GM2" for r in rows):
        raise SystemExit("FAIL-CLOSED target identity mismatch: 4GM2 is PfClpR, not PfClpP")
    receptor_coords = {}
    for target, spec in TARGETS.items():
        require = spec["receptor"]
        if not require.is_file() or require.stat().st_size == 0:
            raise SystemExit(f"FAIL-CLOSED missing/empty Vina receptor PDBQT for {target}: {require}")
        receptor_coords[target] = pdbqt_coords(require)
        if receptor_coords[target].size == 0:
            raise SystemExit(f"FAIL-CLOSED receptor PDBQT has no atom coordinates for {target}: {require}")
    records = []
    secondary_invalid = 0
    secondary_total = 0
    for row in rows:
        name = row["complex_name"]
        directory = RAW / name
        rank1 = directory / "rank1.sdf"
        confidence_files = sorted(directory.glob("rank*_confidence*.sdf"))
        if len(confidence_files) != 10:
            raise SystemExit(f"FAIL-CLOSED expected 10 confidence SDFs for {name}, found {len(confidence_files)}")
        rank1_conf_files = [path for path in confidence_files if path.name.startswith("rank1_confidence")]
        if len(rank1_conf_files) != 1:
            raise SystemExit(f"FAIL-CLOSED expected one rank1 confidence file for {name}")
        conf_file = rank1_conf_files[0]
        match = CONFIDENCE_RE.match(conf_file.name)
        if not match:
            raise SystemExit(f"FAIL-CLOSED malformed rank1 confidence filename: {conf_file.name}")
        rank1_confidence_valid, confidence_coords, confidence_atom_count = sdf_coords(conf_file)
        if not rank1_confidence_valid:
            raise SystemExit(f"FAIL-CLOSED unreadable rank1 confidence SDF for {name}: {conf_file}")
        secondary_total += len(confidence_files) - 1
        for path in confidence_files:
            valid, _, _ = sdf_coords(path)
            if path != conf_file and not valid:
                secondary_invalid += 1
        rank1_valid, coords, atom_count = sdf_coords(rank1)
        confidence = float(match.group("score"))
        target = row["target"]
        center = np.asarray(TARGETS[target]["center"], dtype=float)
        inside_fraction = float(np.all((coords >= center - BOX / 2) & (coords <= center + BOX / 2), axis=1).mean()) if len(coords) else 0.0
        distances = np.sqrt(((coords[:, None, :] - receptor_coords[target][None, :, :]) ** 2).sum(axis=2)) if len(coords) else np.empty((0, 0))
        min_distance = float(distances.min()) if distances.size else math.nan
        if inside_fraction == 1.0:
            grid_status = "IN_GRID"
        elif inside_fraction > 0.0:
            grid_status = "PARTIAL_GRID"
        else:
            grid_status = "OUTSIDE_GRID"
        records.append({
            "candidate_id": row["candidate_id"], "target": target, "complex_name": name,
            "rank1_sdf": str(rank1.resolve()), "rank1_sdf_sha256": sha256(rank1),
            "rank1_valid": rank1_valid, "rank1_atom_count": atom_count,
            "rank1_confidence_file": str(conf_file.resolve()), "rank1_confidence_sdf_sha256": sha256(conf_file),
            "rank1_confidence_valid": rank1_confidence_valid, "rank1_confidence_atom_count": confidence_atom_count,
            "rank1_confidence_coordinate_count": int(len(confidence_coords)),
            "diffdock_rank1_confidence": confidence, "grid_status": grid_status,
            "grid_inside_fraction": inside_fraction, "min_receptor_distance_A": min_distance,
            "vina_score_only_status": "BLOCKED_OUT_OF_PREDECLARED_GRID" if grid_status != "IN_GRID" else "NOT_RUN_PENDING_RESCORING_GATE",
            "consensus_status": "NOT_COMPUTED", "rrs_pns_status": "NOT_UPDATED",
        })
    fields = list(records[0])
    with AUDIT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)
    tree_hash, tree_files = raw_tree_hash()
    summary = {
        "schema": "p1-v5-diffdock-rank1-independent-audit/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RANK1_VERIFIED_SECONDARIES_PARTIAL_VINA_GATE_BLOCKED",
        "manifest_sha256": sha256(MANIFEST), "raw_diffdock_tree_sha256_before_audit": tree_hash,
        "raw_diffdock_tree_file_count_before_audit": tree_files, "raw_log_sha256": sha256(RAW / "diffdock_execution.log"),
        "receptor_coordinate_source": "Vina receptor PDBQT files used by score-only runner",
        "receptor_pdbqt_sha256": {target: sha256(spec["receptor"]) for target, spec in TARGETS.items()},
        "expected_pairs": 68, "rank1_records": len(records),
        "rank1_valid": int(sum(bool(r["rank1_valid"]) for r in records)),
        "rank1_confidence_records": len(records),
        "rank1_confidence_valid": int(sum(bool(r["rank1_confidence_valid"]) for r in records)),
        "secondary_pose_total": secondary_total,
        "secondary_pose_invalid": secondary_invalid,
        "grid_status_counts": {status: sum(r["grid_status"] == status for r in records) for status in ("IN_GRID", "PARTIAL_GRID", "OUTSIDE_GRID")},
        "confidence_sdf_policy": "10 confidence SDFs expected per pair; rank1 confidence SDF must be readable; secondary failures are counted but not repaired",
        "vina_score_only": "BLOCKED_FOR_OUTSIDE_OR_PARTIAL_PREDECLARED_GRID; no arbitrary translation or box expansion",
        "diffdock_confidence_is_not_affinity": True,
        "consensus_scores_written": False, "rrs_pns_updated": False,
        "existing_mutant_vina_panel": "136 rows, PfDHFR/PfCRT WT+mutants only; not expanded by this audit",
        "audit_csv_sha256": sha256(AUDIT_CSV),
        "audit_self_consistency": {
            "all_rank1_pose_sdfs_valid": int(sum(bool(r["rank1_valid"]) for r in records)) == 68,
            "all_rank1_confidence_sdfs_valid": int(sum(bool(r["rank1_confidence_valid"]) for r in records)) == 68,
            "secondary_total_matches_expected": secondary_total == 68 * 9,
            "secondary_invalid_is_derived": True,
        },
    }
    AUDIT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
