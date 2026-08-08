#!/usr/bin/env python3
"""Check 2F6I residue numbering: list all Ser/His/Asp residues per chain with positions.

Purpose: confirm which Ser/His/Asp residues form the catalytic triad and what
numbering 2F6I uses (mature vs propeptide-inclusive). Prints a compact residue
table per chain so the true catalytic residues can be identified.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

PDB = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb")


def main() -> int:
    residues = {}
    for line in PDB.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM  "):
            continue
        try:
            chain = line[21:22].strip()
            resi = int(line[22:26])
            resn = line[17:20].strip()
            name = line[12:16].strip()
            xyz = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
        key = (chain, resi)
        residues.setdefault(key, {"resn": resn, "atoms": {}})
        residues[key]["atoms"][name] = xyz
    chains = sorted({k[0] for k in residues})
    print("catalytic-candidate residues (Ser/His/Asp) per chain:")
    for chain in chains:
        cand = [(resi, r["resn"]) for (c, resi), r in sorted(residues.items())
                if c == chain and r["resn"] in ("SER", "HIS", "HID", "HIE", "ASP")]
        # cluster: positions 180-340
        near = [(resi, resn) for resi, resn in cand if 180 <= resi <= 340]
        print(f"  chain {chain}: {near}")
    # Verify the specific triad candidates: Ser252/His223/Asp219 per chain completeness
    print("\ntriad atom completeness (Ser252 OG, His223 NE2, Asp219 OD1/OD2):")
    for chain in chains:
        def get(resi, resn, names):
            key = (chain, resi)
            r = residues.get(key)
            if r is None or r["resn"] != resn:
                return None
            present = [n for n in names if n in r["atoms"]]
            return present
        ser = get(252, "SER", ["OG"])
        his = get(223, "HIS", ["NE2"])
        asp = get(219, "ASP", ["OD1", "OD2"])
        print(f"  chain {chain}: Ser252 OG={ser} | His223 NE2={his} | Asp219 OD={asp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
