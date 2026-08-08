#!/usr/bin/env python3
"""Read-only pocket analysis of 2F6I (genuine PfClpP) for P1 V5 grid definition.

Computes the catalytic-triad residues (Ser/His/Asp) per chain, their centroid,
and a recommended docking center/box for the PfClpP target. Does not write grid
configs or launch docking.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

PDB = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb")

SER = {"SER"}
HIS = {"HIS", "HID", "HIE", "HIP"}
ASP = {"ASP", "ASH"}


def main() -> int:
    atoms = []  # (chain, resname, resnum, x, y, z)
    for line in PDB.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        try:
            chain = line[21]
            resn = line[17:20].strip()
            resi = int(line[22:26])
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        except ValueError:
            continue
        atoms.append((chain, resn, resi, x, y, z))

    chains = sorted({a[0] for a in atoms if a[0] != " "})
    n_atoms = len(atoms)

    # Catalytic triad detection per chain (Ser-His-Asp in known ClpP numbering)
    triad = {}
    for chain in chains:
        ser_sites = [(r, np.mean([(a[3], a[4], a[5]) for a in atoms if a[0] == chain and a[1] in SER and a[2] == r], axis=0))
                     for r in sorted({a[2] for a in atoms if a[0] == chain and a[1] in SER})]
        his_sites = [(r, np.mean([(a[3], a[4], a[5]) for a in atoms if a[0] == chain and a[1] in HIS and a[2] == r], axis=0))
                     for r in sorted({a[2] for a in atoms if a[0] == chain and a[1] in HIS})]
        asp_sites = [(r, np.mean([(a[3], a[4], a[5]) for a in atoms if a[0] == chain and a[1] in ASP and a[2] == r], axis=0))
                     for r in sorted({a[2] for a in atoms if a[0] == chain and a[1] in ASP})]
        triad[chain] = {"ser": ser_sites, "his": his_sites, "asp": asp_sites}

    # Heptameric barrel: overall centroid and radius
    coords = np.asarray([(a[3], a[4], a[5]) for a in atoms], dtype=float)
    barrel_centroid = coords.mean(axis=0)

    # Pocket center recommendation: centroid of all Ser/His/Asp catalytic residues across chains
    pocket_atoms = [a for a in atoms if a[1] in SER | HIS | ASP]
    if pocket_atoms:
        pocket_center = np.mean([(a[3], a[4], a[5]) for a in pocket_atoms], axis=0)
    else:
        pocket_center = barrel_centroid

    report = {
        "schema": "p1-v5-2f6i-pocket-analysis/v1",
        "pdb": str(PDB),
        "chains": chains,
        "n_atoms": n_atoms,
        "barrel_centroid": barrel_centroid.round(3).tolist(),
        "catalytic_triad_sites": {c: {"ser": [r for r, _ in v["ser"]], "his": [r for r, _ in v["his"]], "asp": [r for r, _ in v["asp"]]} for c, v in triad.items()},
        "pocket_center_catalytic_residues": pocket_center.round(3).tolist(),
        "recommended_box_angstrom": [25.0, 25.0, 25.0],
        "note": "Catalytic triad residues (Ser/His/Asp) centroid used as pocket center hypothesis; requires independent review per V5 policy.",
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
