#!/usr/bin/env python3
"""Verify the PfDHFR (7F3Y) V5 pocket center against the co-crystallized MTX anchor.

Computes: (1) MTX heavy-atom centroid (the genuine co-crystallized inhibitor
anchor), (2) NDP centroid (cofactor), (3) the distance between the current V5
center (1.33, -1.733, -23.842) and the MTX centroid, and (4) CA frame equivalence
between 7F3Y.pdb and 7F3Y.pdbqt. A defensible docking center should sit within
~6 A of the MTX centroid (grid half-size 12.5-14 A).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

PROJ2 = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins")
PDB = PROJ2 / "7F3Y.pdb"
PDBQT = PROJ2 / "data/from_project1/data/proteins/7F3Y.pdbqt" if (PROJ2 / "data/from_project1/data/proteins/7F3Y.pdbqt").is_file() else Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt")
V5_CENTER = np.asarray([1.33, -1.733, -23.842], dtype=float)


def centroid_of(path: Path, resname: str):
    pts = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("HETATM") and line[17:20].strip() == resname:
            try:
                pts.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
    if not pts:
        return None
    return np.mean(np.asarray(pts, dtype=float), axis=0)


def ca_frame(pdb: Path, pdbqt: Path) -> dict:
    def read_ca(path: Path):
        out = {}
        for line in path.read_text(errors="replace").splitlines():
            if not line.startswith(("ATOM  ", "HETATM")) or line[12:16].strip() != "CA":
                continue
            try:
                key = (line[21:22].strip(), line[22:26].strip())
                out[key] = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
        return out
    a, b = read_ca(pdb), read_ca(pdbqt)
    if not a or not b:
        return {"status": "NO_CA_FOUND"}
    common = sorted(set(a) & set(b))
    missing_in_pdbqt = sorted(set(a) - set(b))
    delta = np.asarray([a[k] - b[k] for k in common], dtype=float)
    rmsd = float(np.sqrt(np.mean(delta ** 2)))
    return {
        "pdb_ca": len(a), "pdbqt_ca": len(b), "common_ca": len(common),
        "missing_in_pdbqt": len(missing_in_pdbqt), "rmsd_A": rmsd,
        "status": "CA_FRAME_MATCH" if rmsd < 1e-4 else "CA_FRAME_MISMATCH",
    }


def main() -> int:
    mtx = centroid_of(PDB, "MTX")
    ndp = centroid_of(PDB, "NDP")
    frame = ca_frame(PDB, PDBQT)
    report = {
        "pdb": str(PDB), "pdbqt": str(PDBQT),
        "v5_center": V5_CENTER.tolist(),
        "mtx_centroid": mtx.tolist() if mtx is not None else None,
        "ndp_centroid": ndp.tolist() if ndp is not None else None,
        "v5_to_mtx_A": float(np.linalg.norm(V5_CENTER - mtx)) if mtx is not None else None,
        "v5_to_ndp_A": float(np.linalg.norm(V5_CENTER - ndp)) if ndp is not None else None,
        "ca_frame": frame,
        "verdict": "CENTER_DEFENSIBLE" if (mtx is not None and float(np.linalg.norm(V5_CENTER - mtx)) <= 6.0) else "CENTER_NEEDS_REVIEW",
    }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
