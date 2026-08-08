#!/usr/bin/env python3
"""Diagnose where the Vina rank-1 pose sits relative to the 2F6I catalytic triads.

For each chain of 2F6I, locate the catalytic Ser-His-Asp residues (by residue
identity near the published catalytic site) and report the distance from the
Vina rank-1 pose centroid to every catalytic residue. Also reports the nearest
receptor atoms and whether the pose contacts genuine catalytic residues.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJ2 = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins")
PDB = PROJ2 / "2F6I.pdb"
POSE = Path(sys.argv[1] if len(sys.argv) > 1 else
           "/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/vina_dock_2F6I_PfClpP_smoke/PP-01_PfClpP/vina_out.pdbqt")

# Catalytic residues of P. falciparum ClpP (2F6I): Ser189-His123-Asp179 (mature numbering, chain A)
# Known catalytic triad per El Bakkouri et al. 2010: His123, Asp179, Ser189
TARGET = {"SER": 189, "HIS": 123, "ASP": 179}


def read_receptor(path: Path):
    atoms = []
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM  "):
            continue
        chain = line[21:22].strip()
        resi = int(line[22:26])
        resn = line[17:20].strip()
        try:
            xyz = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
        atoms.append({"chain": chain, "resi": resi, "resn": resn, "xyz": xyz})
    return atoms


def read_pose_model1(path: Path):
    coords = []
    mc = 0
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            mc += 1
            if mc > 1:
                break
            continue
        if line.startswith(("ATOM  ", "HETATM")) and mc == 1:
            try:
                coords.append(np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])]))
            except ValueError:
                continue
    return np.asarray(coords)


def main() -> int:
    atoms = read_receptor(PDB)
    pose = read_pose_model1(POSE)
    print(f"pose atoms: {len(pose)}")
    centroid = pose.mean(axis=0)
    print(f"pose centroid: {np.round(centroid, 3)}")
    chains = sorted({a["chain"] for a in atoms})
    print(f"chains: {chains}")
    for chain in chains:
        for resn, resi in TARGET.items():
            hits = [a for a in atoms if a["chain"] == chain and a["resn"] == resn and a["resi"] == resi]
            if not hits:
                continue
            d = float(np.linalg.norm(hits[0]["xyz"] - centroid))
            nearest_pose = float(np.min(np.linalg.norm(pose - hits[0]["xyz"], axis=1)))
            print(f"  chain {chain} {resn}{resi}: centroid_dist={d:.2f} A  pose_atom_min={nearest_pose:.2f} A")
    # Nearest receptor atom overall
    all_xyz = np.asarray([a["xyz"] for a in atoms])
    d_all = np.linalg.norm(all_xyz - centroid, axis=1)
    idx = int(np.argmin(d_all))
    print(f"nearest receptor atom: chain {atoms[idx]['chain']} {atoms[idx]['resn']}{atoms[idx]['resi']} at {d_all[idx]:.2f} A from pose centroid")
    # Contact residues (< 4 A from any pose atom)
    contacts = set()
    for a in atoms:
        if np.min(np.linalg.norm(pose - a["xyz"], axis=1)) < 4.0:
            contacts.add((a["chain"], a["resn"], a["resi"]))
    print(f"contact residues (<4A): {len(contacts)}")
    for c in sorted(contacts)[:40]:
        print("   ", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
