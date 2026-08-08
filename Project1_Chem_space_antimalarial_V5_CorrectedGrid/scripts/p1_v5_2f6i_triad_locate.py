#!/usr/bin/env python3
"""Locate the genuine 2F6I catalytic triads geometrically and measure the pose distance.

Rather than trusting published residue numbers, find triads by geometry: in each
chain, the catalytic Ser N/O, His imidazole N, and Asp carboxyl O cluster within
~4-6 A. Then report the distance from the Vina rank-1 pose to each triad's
catalytic atoms and centroid.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJ2 = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins")
PDB = PROJ2 / "2F6I.pdb"
POSE = Path(sys.argv[1] if len(sys.argv) > 1 else
           "/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/vina_dock_2F6I_PfClpP_smoke/PP-01_PfClpP/vina_out.pdbqt")

SER_ATOMS = {"N", "CA", "C", "O", "CB", "OG"}
HIS_ATOMS = {"N", "CA", "C", "O", "CB", "CG", "ND1", "CD2", "CE1", "NE2"}
ASP_ATOMS = {"N", "CA", "C", "O", "CB", "CG", "OD1", "OD2"}


def read_atoms(path: Path):
    atoms = []
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM  "):
            continue
        try:
            atoms.append({
                "chain": line[21:22].strip(), "resi": int(line[22:26]),
                "resn": line[17:20].strip(), "name": line[12:16].strip(),
                "xyz": np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])]),
            })
        except ValueError:
            continue
    return atoms


def main() -> int:
    atoms = read_atoms(PDB)
    chains = sorted({a["chain"] for a in atoms})
    by_chain = {}
    for chain in chains:
        residues = {}
        for a in atoms:
            if a["chain"] != chain:
                continue
            residues.setdefault(a["resi"], {"resn": a["resn"], "atoms": {}})
            residues[a["resi"]]["atoms"][a["name"]] = a["xyz"]
        by_chain[chain] = residues
    # Find candidate triads: a Ser with OG, His with NE2, Asp with OD1/OD2 within 6 A
    triads = []
    for chain in chains:
        res = by_chain[chain]
        sers = [(i, r) for i, r in res.items() if r["resn"] == "SER" and "OG" in r["atoms"]]
        hiss = [(i, r) for i, r in res.items() if r["resn"] in ("HIS", "HID", "HIE", "HIS") and "NE2" in r["atoms"]]
        asps = [(i, r) for i, r in res.items() if r["resn"] == "ASP" and ("OD1" in r["atoms"] or "OD2" in r["atoms"])]
        for si, s in sers:
            for hi, h in hiss:
                if np.linalg.norm(s["atoms"]["OG"] - h["atoms"]["NE2"]) > 6.0:
                    continue
                for ai, a in asps:
                    od = a["atoms"]["OD1"] if "OD1" in a["atoms"] else a["atoms"]["OD2"]
                    if np.linalg.norm(h["atoms"]["NE2"] - od) > 6.0:
                        continue
                    triads.append({"chain": chain, "ser": si, "his": hi, "asp": ai,
                                   "ser_xyz": s["atoms"]["OG"], "his_xyz": h["atoms"]["NE2"],
                                   "asp_xyz": od})
    print(f"geometric triads found: {len(triads)}")
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
    pose = np.asarray(pose)
    pc = pose.mean(axis=0)
    print(f"pose atoms: {len(pose)}, centroid: {np.round(pc, 2)}")
    best = None
    for t in triads:
        triad_centroid = (t["ser_xyz"] + t["his_xyz"] + t["asp_xyz"]) / 3
        d_c = float(np.linalg.norm(pc - triad_centroid))
        d_ser = float(np.min(np.linalg.norm(pose - t["ser_xyz"], axis=1)))
        d_his = float(np.min(np.linalg.norm(pose - t["his_xyz"], axis=1)))
        d_asp = float(np.min(np.linalg.norm(pose - t["asp_xyz"], axis=1)))
        tag = ""
        if best is None or d_c < best[0]:
            best = (d_c, t)
        print(f"  chain {t['chain']} Ser{t['ser']}/His{t['his']}/Asp{t['asp']}: "
              f"centroid_dist={d_c:.2f} A  pose-min Ser={d_ser:.2f} His={d_his:.2f} Asp={d_asp:.2f}")
    print(f"BEST triad: chain {best[1]['chain']} Ser{best[1]['ser']}/His{best[1]['his']}/Asp{best[1]['asp']} at {best[0]:.2f} A from pose centroid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
