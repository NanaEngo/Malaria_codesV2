#!/usr/bin/env python3
"""Analyze MTX instances in 7F3Y (PfDHFR) to select the catalytic-site copy.

Reports per-instance: chain, residue, atom count, centroid, and which MTX
copy is closest to the canonical PfDHFR catalytic residues (e.g. Asp54,
Phe58, Ser108 / Ile14, Cys15 in PfDHFR numbering — derived from known
DHFR-TS folate pocket). Also reports the distance of each MTX centroid to
the receptor bounding-box centre (the old V5 centre was the receptor
centroid — same error class as the PfClpP barrel channel).
"""
from __future__ import annotations

import sys
from collections import defaultdict
import numpy as np


def load_atoms(pdb_path: str):
    """Return (hetatm_instances, protein_atoms) parsed from a PDB file."""
    het = defaultdict(list)      # (chain, resname, resi) -> list of (atom_name, xyz)
    prot = []                    # (chain, resname, resi, xyz)
    for line in open(pdb_path):
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        try:
            name = line[12:16].strip()
            resn = line[17:20].strip()
            chain = line[21:22].strip()
            resi = int(line[22:26])
            xyz = np.array([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
        if line.startswith("HETATM"):
            het[(chain, resn, resi)].append((name, xyz))
        else:
            prot.append((chain, resn, resi, xyz))
    return het, prot


def main() -> int:
    pdb = sys.argv[1] if len(sys.argv) > 1 else "7F3Y.pdb"
    het, prot = load_atoms(pdb)

    print(f"Receptor: {pdb}")
    prot_xyz = np.array([p[3] for p in prot])
    bb_center = prot_xyz.mean(axis=0)
    print(f"Protein atoms: {len(prot_xyz):,} | bounding-box centre: {bb_center.round(2)}")

    # MTX instances
    mtx = {k: v for k, v in het.items() if k[1] == "MTX"}
    print(f"\nMTX instances: {len(mtx)}")
    print(f"{'chain':<6s}{'resi':<6s}{'n_atoms':<9s}{'centroid':<40s}{'d_to_bb':<10s}")
    for (chain, resn, resi), atoms in sorted(mtx.items()):
        c = np.mean([a[1] for a in atoms], axis=0)
        d_bb = float(np.linalg.norm(c - bb_center))
        print(f"{chain:<6s}{resi:<6d}{len(atoms):<9d}{str(c.round(2)):<40s}{d_bb:.1f}")

    # Catalytic-site proxy: residue closest to each MTX instance in terms of
    # protein heavy-atom contacts (any protein residue with >=3 heavy atoms
    # within 4.5 A of MTX atoms indicates a genuine binding site).
    print("\nContact analysis (protein residues with >=3 heavy atoms within 4.5 A of MTX):")
    for (chain, resn, resi), atoms in sorted(mtx.items()):
        mtx_xyz = np.atleast_2d(np.array([a[1] for a in atoms], dtype=float))
        contacts = defaultdict(int)
        for p_chain, p_resn, p_resi, p_xyz in prot:
            if p_chain != chain:
                continue
            d = np.linalg.norm(mtx_xyz[:, None, :] - p_xyz[None, :], axis=2)
            if (d < 4.5).any():
                contacts[(p_chain, p_resn, p_resi)] += 1
        n_contact = sum(1 for v in contacts.values() if v >= 3)
        res_list = ", ".join(f"{k[1]}{k[2]}" for k, v in sorted(contacts.items(), key=lambda kv: -kv[1])[:6])
        print(f"  MTX {chain}{resi}: {n_contact} contact residues | top: {res_list}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
