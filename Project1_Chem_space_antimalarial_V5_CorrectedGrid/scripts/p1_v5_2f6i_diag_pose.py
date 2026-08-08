#!/usr/bin/env python3
"""Diagnose rank1 pose placement for PP-01_PfClpP (2F6I) vs declared pocket center."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from rdkit import Chem

V5 = Path("/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid")
RUN = V5 / "results/diffdock_2F6I_PfClpP_17"
RANK1 = RUN / "PP-01_PfClpP" / "rank1.sdf"
RECEPTOR = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb")
CENTER = np.asarray([-0.116, 40.446, 12.213])
BOX = np.asarray([25.0, 25.0, 25.0])


def read_coords(path: Path) -> np.ndarray:
    coords = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith(("ATOM  ", "HETATM")):
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
    return np.asarray(coords, dtype=float)


def sdf_coords(path: Path) -> np.ndarray:
    mol = next((m for m in Chem.SDMolSupplier(str(path), removeHs=False, sanitize=False) if m is not None), None)
    if mol is None or mol.GetNumConformers() == 0:
        return np.asarray([])
    return np.asarray(mol.GetConformer().GetPositions(), dtype=float)


def main() -> int:
    rec = read_coords(RECEPTOR)
    lig = sdf_coords(RANK1)
    rep = {
        "receptor_atoms": len(rec),
        "ligand_atoms": len(lig),
        "declared_center": CENTER.tolist(),
        "receptor_centroid": rec.mean(axis=0).tolist() if len(rec) else None,
        "ligand_centroid": lig.mean(axis=0).tolist() if len(lig) else None,
    }
    if len(lig):
        d = np.linalg.norm(lig.mean(axis=0) - CENTER)
        rep["ligand_center_to_declared_center_A"] = float(d)
        frac = float(np.all((lig >= CENTER - BOX / 2) & (lig <= CENTER + BOX / 2), axis=1).mean())
        rep["inside_fraction"] = frac
    if len(rec):
        d_rec = np.linalg.norm(lig.mean(axis=0) - rec.mean(axis=0)) if len(lig) else None
        rep["ligand_center_to_receptor_centroid_A"] = float(d_rec) if d_rec is not None else None
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
