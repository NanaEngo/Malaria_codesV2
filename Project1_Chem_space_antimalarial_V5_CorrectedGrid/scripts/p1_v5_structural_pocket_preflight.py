#!/usr/bin/env python3
"""Read-only structural-pocket preflight for P1 V5.

This script never launches DiffDock/Vina/GROMACS and never authorizes the 68-pair
run. It inventories non-water HETATM anchors and compares them to historical V2
grid centers. Missing or ambiguous anchors remain REVIEW_REQUIRED; geometry alone
cannot promote a grid to an accepted biological pocket definition.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
OUT = V5 / "results/structural_pocket_preflight.json"
BOX = [25.0, 25.0, 25.0]
WATER_IONS = {"HOH", "WAT", "SOL", "NA", "CL", "K", "CA", "MG", "ZN", "SO4", "PO4"}
TARGETS = {
    "PfDHFR": {
        "pdb_id": "7F3Y",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb",
        "center": [8.34, -13.9, -41.754],
        "evidence_class": "HETATM_LIGAND_CANDIDATE_REVIEW_REQUIRED",
        "anchor_policy": "MTX-like HETATM identity is inventoried but not independently validated here; site definition must be explicit and is not replaced by raw centroid",
    },
    "PfCRT": {
        "pdb_id": "6UKJ",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/6UKJ.pdb",
        "center": [152.5, 148.0, 154.5],
        "evidence_class": "HETATM_PROXY_REVIEW_REQUIRED",
        "anchor_policy": "Y01 identity and relevance to the inhibitor cavity require independent review",
    },
    "PfClpP": {
        "pdb_id": "2F6I",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb",
        "center": [-24.276, 17.28, -2.901],
        "evidence_class": "CATALYTIC_TRIAD_REVIEW_REQUIRED",
        "anchor_policy": "RCSB 2F6I is the genuine PfClpP catalytic domain (EC 3.4.21.92, UniProt O97252, El Bakkouri et al. 2010); 4GM2 is PfClpR (inactive, UniProt Q8IL98) and must not be used. CORRECTED 08/08/2026: pocket center = chain A catalytic triad Ser252/His223/Asp219 (geometrically complete in all 7 chains; UniProt active-site Ser289 corresponds to 2F6I Ser252, offset 37). The previous centroid of all Ser/His/Asp residues collapsed to the barrel channel and is NOT a catalytic site; independent review still required.",
    },
    "PfATP4": {
        "pdb_id": "9N10",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/9N10.pdb",
        "center": [129.3, 130.9, 92.4],
        "evidence_class": "GEOMETRY_ONLY_REVIEW_REQUIRED",
        "anchor_policy": "No non-water HETATM anchor detected; membrane-protein site definition must be documented",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anchors(path: Path) -> dict[str, list[list[float]]]:
    groups: dict[str, list[list[float]]] = defaultdict(list)
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("HETATM"):
            continue
        residue = line[17:20].strip()
        if residue in WATER_IONS:
            continue
        try:
            groups[residue].append([
                float(line[30:38]), float(line[38:46]), float(line[46:54])
            ])
        except ValueError:
            continue
    return dict(groups)


def main() -> int:
    targets = {}
    review_required = False
    for name, spec in TARGETS.items():
        if not spec["pdb"].is_file() or spec["pdb"].stat().st_size == 0:
            raise SystemExit(f"FAIL-CLOSED missing receptor PDB: {spec['pdb']}")
        grouped = anchors(spec["pdb"])
        center = np.asarray(spec["center"], dtype=float)
        entries = []
        for residue, values in sorted(grouped.items()):
            centroid = np.mean(np.asarray(values, dtype=float), axis=0)
            entries.append({
                "residue": residue,
                "atom_count": len(values),
                "centroid_A": centroid.round(6).tolist(),
                "distance_to_historical_center_A": float(np.linalg.norm(centroid - center)),
            })
        if spec["evidence_class"] != "HETATM_LIGAND_CANDIDATE_REVIEW_REQUIRED":
            review_required = True
        targets[name] = {
            "pdb_id": spec["pdb_id"],
            "pdb": str(spec["pdb"]),
            "pdb_sha256": sha256(spec["pdb"]),
            "historical_v2_center_A": spec["center"],
            "box_A": BOX,
            "evidence_class": spec["evidence_class"],
            "anchor_policy": spec["anchor_policy"],
            "non_water_hetatm_anchors": entries,
        }
    record = {
        "schema": "p1-v5-structural-pocket-preflight/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "REVIEW_REQUIRED_NOT_AUTHORIZED",
        "read_only": True,
        "diffdock_launched": False,
        "vina_launched": False,
        "gromacs_launched": False,
        "consensus_scores_written": False,
        "rrs_pns_updated": False,
        "full_run_authorized": False,
        "review_required": review_required,
        "independent_review_status": "PENDING",
        "accepted_for_full_run": False,
        "acceptance_rule": "No grid or 68-pair run may be accepted from geometry/IN_GRID improvement alone; require target-specific structural justification, independent review, exact-config smoke with rank1 100% IN_GRID, and cryptographically bound authorization.",
        "targets": targets,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
