#!/usr/bin/env python3
"""List MTX instances in 7F3Y with per-instance centroids and pose proximity.

7F3Y (PfDHFR-TS dimer) may contain multiple MTX copies across chains. The V5
anchor must be the MTX copy bound at the DHFR catalytic site of chain A, not the
global centroid of all copies. This script reports each MTX instance (chain+resi),
its centroid, and its distance to the Vina pose and to the DHFR catalytic
residues (Asp54/Arg59/Ser111 region by sequence homology; reported as-is).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

PDB = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb")
POSE = Path("/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/vina_dock_7F3Y_PfDHFR_smoke/PP-01_PfDHFR/vina_out.pdbqt")


def main() -> int:
    instances = {}
    for line in PDB.read_text(errors="replace").splitlines():
        if not line.startswith("HETATM") or line[17:20].strip() != "MTX":
            continue
        key = (line[21:22].strip(), line[22:26].strip())
        try:
            xyz = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
        instances.setdefault(key, []).append(xyz)
    print("MTX instances in 7F3Y:")
    pose = []
    mc = 0
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
    pc = pose.mean(axis=0)
    for key in sorted(instances):
        arr = np.asarray(instances[key], dtype=float)
        cent = arr.mean(axis=0)
        d_pc = float(np.linalg.norm(cent - pc))
        d_min = float(np.min(np.linalg.norm(arr[:, None, :] - pose[None, :, :], axis=2)))
        print(f"  chain {key[0]} resi {key[1]}: n_atoms={len(arr)} centroid={np.round(cent, 2)}  "
              f"dist_to_pose_centroid={d_pc:.1f} A  pose_atom_min={d_min:.1f} A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
