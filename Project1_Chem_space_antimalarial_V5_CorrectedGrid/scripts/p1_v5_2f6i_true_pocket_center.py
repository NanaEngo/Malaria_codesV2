#!/usr/bin/env python3
"""Compute the TRUE 2F6I catalytic-triad pocket center (chain A triad) and report it.

V5 previously used the centroid of ALL Ser/His/Asp residues across the heptamer
as the PfClpP pocket center, which collapses to the barrel channel centroid and
is NOT a catalytic site (verified: Vina poses land ~22 A from the nearest triad).
The correct pocket center is a single catalytic triad. 2F6I (mature numbering)
uses Ser252 / His223 / Asp219 per chain; the canonical pocket is chain A.

Outputs the triad-atom centroid (OG, NE2, OD1/OD2) for every chain so the
report can justify the chosen center and the box keeps the triad inside.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PDB = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb")

TRIAD = {"SER": 252, "HIS": 223, "ASP": 219}


def main() -> int:
    atoms = []
    for line in PDB.read_text(errors="replace").splitlines():
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
    chains = sorted({a["chain"] for a in atoms})
    report = {}
    best = None
    for chain in chains:
        ser = [a["xyz"] for a in atoms if a["chain"] == chain and a["resn"] == "SER" and a["resi"] == 252 and a["name"] == "OG"]
        his = [a["xyz"] for a in atoms if a["chain"] == chain and a["resn"] in ("HIS", "HID", "HIE") and a["resi"] == 223 and a["name"] == "NE2"]
        asp = [a["xyz"] for a in atoms if a["chain"] == chain and a["resn"] == "ASP" and a["resi"] == 219 and a["name"] in ("OD1", "OD2")]
        entry = {"ser252_og": [np.round(s, 3).tolist() for s in ser],
                 "his223_ne2": [np.round(h, 3).tolist() for h in his],
                 "asp219_od": [np.round(d, 3).tolist() for d in asp]}
        if ser and his and asp:
            center = (ser[0] + his[0] + asp[0]) / 3
            entry["triad_centroid"] = np.round(center, 3).tolist()
            entry["complete"] = True
            if best is None:
                best = (chain, center)
        else:
            entry["complete"] = False
        report[chain] = entry
    print(json.dumps({"triad_numbering": "mature: Ser252/His223/Asp219", "chains": report,
                      "recommended_pocket_center": (np.round(best[1], 3).tolist() if best else None),
                      "recommended_chain": best[0] if best else None}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
