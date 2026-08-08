#!/usr/bin/env python3
"""Inspect 2F6I residues that failed Meeko template matching (A:177, A:181, ...)."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

PDB = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I_prot.pdb")

BAD = [
    ("A", 177), ("A", 181), ("A", 185), ("A", 275), ("A", 296), ("A", 305),
    ("A", 333), ("A", 357), ("A", 366),
]


def main() -> int:
    atoms = defaultdict(list)
    for line in PDB.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM  "):
            continue
        try:
            chain = line[21:22]
            resn = line[17:20].strip()
            resi = int(line[22:26])
            aname = line[12:16].strip()
            atoms[(chain, resi)].append({"resn": resn, "aname": aname})
        except ValueError:
            continue

    report = {}
    for key in BAD:
        info = atoms.get(key, [])
        # count atoms and list missing standard backbone atoms
        names = {a["aname"] for a in info}
        resn = info[0]["resn"] if info else "?"
        missing = [n for n in ("N", "CA", "C", "O") if n not in names]
        report[f"{key[0]}:{key[1]}"] = {
            "resname": resn,
            "n_atoms": len(info),
            "atom_names": sorted(names),
            "missing_backbone": missing,
        }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
