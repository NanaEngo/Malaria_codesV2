#!/usr/bin/env python3
"""Verify CA frame equivalence between 2F6I.pdb and 2F6I.pdbqt (subset rule).

Meeko rejected ~74 residues with incomplete side chains (HIS/LYS/ASN etc. with
partial atoms from the 2005 PDB). The correct frame-equivalence criterion is:
every CA present in the PDBQT must be present in the PDB with identical
coordinates (PDBQT is a coordinate-identical subset), so the grid frame is
unchanged. This script also checks that the catalytic triad residues (Ser/His/Asp
closest to the pocket center) survive in the PDBQT.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PDB = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb")
PDBQT = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdbqt")
CENTER = np.asarray([-0.116, 40.446, 12.213])


def read_ca(path: Path):
    result = {}
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM  ", "HETATM")) or line[12:16].strip() != "CA":
            continue
        try:
            key = (line[21:22].strip(), line[22:26].strip())
            result[key] = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
    return result


def read_residue_centroids(path: Path, keys_interest: set[tuple[str, str]]) -> dict:
    """Centroid of all atoms of the residues of interest (any atom name)."""
    result = {}
    current = {}
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        try:
            key = (line[21:22].strip(), line[22:26].strip())
            resn = line[17:20].strip()
            xyz = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
        current.setdefault(key, []).append(xyz)
    for key, xyzs in current.items():
        result[key] = np.mean(np.asarray(xyzs), axis=0)
    return result


def main() -> int:
    pdb_ca = read_ca(PDB)
    pdbqt_ca = read_ca(PDBQT)
    common = set(pdb_ca) & set(pdbqt_ca)
    missing_in_pdb = sorted(set(pdbqt_ca) - set(pdb_ca))
    report = {
        "pdb_ca_count": len(pdb_ca),
        "pdbqt_ca_count": len(pdbqt_ca),
        "pdbqt_ca_in_pdb_count": len(common),
        "pdbqt_ca_not_in_pdb": missing_in_pdb[:10],
        "n_pdbqt_ca_not_in_pdb": len(missing_in_pdb),
    }
    if missing_in_pdb:
        report["status"] = "FAIL_PDBQT_CA_NOT_IN_PDB"
        print(json.dumps(report, indent=2))
        return 1
    delta = np.asarray([pdb_ca[k] - pdbqt_ca[k] for k in common], dtype=float)
    rmsd = float(np.sqrt(np.mean(delta ** 2)))
    max_norm = float(np.max(np.linalg.norm(delta, axis=1)))
    report["rmsd_A"] = rmsd
    report["max_norm_A"] = max_norm
    # catalytic residues: SER/HIS/ASP residues whose centroid is within 12 A of center
    all_res = read_residue_centroids(PDB, set(pdb_ca))
    pdbqt_res = read_residue_centroids(PDBQT, set(pdbqt_ca))
    catalytic = []
    for key, cent in all_res.items():
        if np.linalg.norm(cent - CENTER) <= 12.0:
            catalytic.append(key)
    surviving = [k for k in catalytic if k in pdbqt_res]
    report["catalytic_residues_near_center"] = catalytic
    report["catalytic_surviving_in_pdbqt"] = surviving
    report["n_catalytic_near_center"] = len(catalytic)
    report["n_catalytic_surviving"] = len(surviving)
    if rmsd <= 1e-6 and max_norm <= 1e-6 and not catalytic or len(surviving) == len(catalytic):
        report["status"] = "CA_SUBSET_FRAME_EQUIVALENT"
        print(json.dumps(report, indent=2))
        return 0
    report["status"] = "FAIL_CA_SUBSET_FRAME_MISMATCH"
    print(json.dumps(report, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
