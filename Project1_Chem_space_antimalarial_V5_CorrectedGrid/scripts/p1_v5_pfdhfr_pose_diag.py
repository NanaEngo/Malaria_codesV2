#!/usr/bin/env python3
"""Diagnose the PfDHFR Vina pose geometry vs the MTX anchor and receptor."""
from __future__ import annotations

from pathlib import Path

import numpy as np

PROJ2 = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins")
PDB = PROJ2 / "7F3Y.pdb"
POSE = Path("/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/vina_dock_7F3Y_PfDHFR_smoke/PP-01_PfDHFR/vina_out.pdbqt")


def read_atoms(path: Path, kind: str):
    atoms = []
    for line in path.read_text(errors="replace").splitlines():
        if kind == "receptor" and not line.startswith("ATOM  "):
            continue
        if kind == "mtx" and not (line.startswith("HETATM") and line[17:20].strip() == "MTX"):
            continue
        if kind == "pose" and not (line.startswith(("ATOM  ", "HETATM"))):
            continue
        try:
            atoms.append({
                "resn": line[17:20].strip(), "resi": line[22:26].strip(),
                "chain": line[21:22].strip(), "name": line[12:16].strip(),
                "xyz": np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])]),
            })
        except ValueError:
            continue
    return atoms


def main() -> int:
    rec = read_atoms(PDB, "receptor")
    mtx = read_atoms(PDB, "mtx")
    pose_atoms = read_atoms(POSE, "pose")
    # pose model 1 only
    pose = []
    mc = 0
    for a in pose_atoms:
        pass
    for line in POSE.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            mc += 1
            if mc > 1:
                break
            continue
        if line.startswith(("ATOM  ", "HETATM")) and mc == 1:
            try:
                pose.append(np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])]))
            except ValueError:
                continue
    pose = np.asarray(pose, dtype=float)
    mtx_xyz = np.asarray([a["xyz"] for a in mtx], dtype=float)
    rec_xyz = np.asarray([a["xyz"] for a in rec], dtype=float)
    print(f"receptor atoms: {len(rec)}, MTX atoms: {len(mtx)}, pose atoms: {len(pose)}")
    print(f"receptor centroid: {np.round(rec_xyz.mean(axis=0), 2)}")
    print(f"MTX centroid: {np.round(mtx_xyz.mean(axis=0), 2)}")
    print(f"MTX min/max: {np.round(mtx_xyz.min(axis=0), 2)} / {np.round(mtx_xyz.max(axis=0), 2)}")
    print(f"pose centroid: {np.round(pose.mean(axis=0), 2)}")
    print(f"pose min/max: {np.round(pose.min(axis=0), 2)} / {np.round(pose.max(axis=0), 2)}")
    d = np.linalg.norm(mtx_xyz[:, None, :] - pose[None, :, :], axis=2)
    print(f"pose-to-MTX min dist: {d.min():.2f} A")
    # nearest MTX atom index to pose
    idx = np.unravel_index(d.argmin(), d.shape)
    print(f"nearest: pose atom {idx[1]} <-> MTX atom {idx[0]} ({mtx[idx[0]]['name']} {mtx[idx[0]]['resn']}{mtx[idx[0]]['resi']})")
    # residues near pose
    dd = np.linalg.norm(rec_xyz[:, None, :] - pose[None, :, :], axis=2)
    contact_idx = np.where(dd.min(axis=1) < 4.0)[0]
    res = sorted({(rec[i]["chain"], rec[i]["resn"], rec[i]["resi"]) for i in contact_idx})
    print(f"receptor contact residues (<4A): {len(res)}")
    print("  ", res[:25])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
