#!/usr/bin/env python3
"""Check CA-frame equivalence between 2F6I.pdb and 2F6I.pdbqt (precondition for the DiffDock PfClpP rerun)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PDB = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb")
PDBQT = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdbqt")


def read_ca(path: Path):
    result = {}
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM  ") or line[12:16].strip() != "CA":
            continue
        try:
            key = (line[21:22].strip(), line[22:26].strip())
            result[key] = [float(line[30:38]), float(line[38:46]), float(line[46:54])]
        except ValueError:
            continue
    return result


def main() -> int:
    a, b = read_ca(PDB), read_ca(PDBQT)
    common = sorted(set(a) & set(b))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    report = {
        "pdb_ca_count": len(a),
        "pdbqt_ca_count": len(b),
        "common_ca_count": len(common),
        "only_in_pdb": only_a[:20],
        "only_in_pdbqt": only_b[:20],
        "n_only_in_pdb": len(only_a),
        "n_only_in_pdbqt": len(only_b),
    }
    if set(a) != set(b) or not common:
        report["status"] = "FAIL_IDENTITY_MISMATCH"
        print(json.dumps(report, indent=2))
        return 1
    delta = np.asarray([np.asarray(a[k]) - np.asarray(b[k]) for k in common], dtype=float)
    rmsd = float(np.sqrt(np.mean(delta ** 2)))
    max_norm = float(np.max(np.linalg.norm(delta, axis=1)))
    report["status"] = "CA_FRAME_EQUIVALENT" if (rmsd <= 1e-6 and max_norm <= 1e-6) else "CA_COORD_MISMATCH"
    report["rmsd_A"] = rmsd
    report["max_norm_A"] = max_norm
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "CA_FRAME_EQUIVALENT" else 1


if __name__ == "__main__":
    sys.exit(main())
