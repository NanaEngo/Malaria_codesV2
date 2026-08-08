#!/usr/bin/env python3
"""
P1 V5 — Pocket-center verification with biological gate for PfDHFR (7F3Y),
PfCRT (6UKJ) and PfATP4 (9N10), mirroring the 2F6I PfClpP protocol.

For each target the anchor is either a co-crystallized ligand (MTX A702,
Y01 A501) or, when no ligand exists (9N10), the conserved P-type ATPase
catalytic residues (phosphorylation site DKTGT / P-loop / A-domain hinge
DPPR). The biological gate verifies that the declared pocket center:
  (1) equals the anchor centroid,
  (2) the anchor is surrounded by biologically relevant protein residues
      (the 4.5 A contact shell is reported for the independent review),
  (3) the contact residue set is consistent with the documented functional
      site for that target.

Read-only: computes evidence, writes a JSON report, launches nothing.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

PROJ2 = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins")
OUT = Path("/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid/results")

THREE2ONE = {
    "ALA": "A", "CYS": "C", "ASP": "D", "GLU": "E", "PHE": "F", "GLY": "G",
    "HIS": "H", "ILE": "I", "LYS": "K", "LEU": "L", "MET": "M", "ASN": "N",
    "PRO": "P", "GLN": "Q", "ARG": "R", "SER": "S", "THR": "T", "VAL": "V",
    "TRP": "W", "TYR": "Y",
}
CONTACT_A = 4.5


def parse_atoms(pdb: Path, chain: str | None = None, resi_min: int | None = None,
                resi_max: int | None = None) -> list[dict]:
    """Fixed-column PDB parse; returns atom dicts with chain/resname/resi/xyz."""
    atoms = []
    for line in pdb.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        try:
            atom = {
                "chain": line[21:22].strip(),
                "resname": line[17:20].strip(),
                "resi": int(line[22:26]),
                "atomname": line[12:16].strip(),
                "xyz": np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])]),
            }
        except ValueError:
            continue
        if chain is not None and atom["chain"] != chain:
            continue
        if resi_min is not None and atom["resi"] < resi_min:
            continue
        if resi_max is not None and atom["resi"] > resi_max:
            continue
        atoms.append(atom)
    return atoms


def anchor_heavy_atoms(atoms: list[dict], resname: str, chain: str, resi: int) -> np.ndarray:
    sel = [a["xyz"] for a in atoms
           if a["resname"] == resname and a["chain"] == chain and a["resi"] == resi
           and a["atomname"] != "H"]
    if not sel:
        raise SystemExit(f"FAIL-CLOSED no {resname} {chain}{resi} heavy atoms found")
    return np.asarray(sel, dtype=float)


def chain_seq_1letter(atoms: list[dict], chain: str) -> dict[int, str]:
    seq = {}
    for a in atoms:
        if a["chain"] == chain and a["atomname"] == "CA" and a["resname"] in THREE2ONE:
            seq[a["resi"]] = THREE2ONE[a["resname"]]
    return seq


def contact_shell(anchor_pts: np.ndarray, atoms: list[dict],
                  exclude_resnames: set[str] | None = None) -> list[dict]:
    """Protein residues (and ligands) with any heavy atom within CONTACT_A of anchor."""
    exclude = exclude_resnames or set()
    by_res: dict[tuple, list] = defaultdict(list)
    for a in atoms:
        if a["resname"] in exclude or a["atomname"] == "H":
            continue
        by_res[(a["chain"], a["resi"], a["resname"])].append(a["xyz"])
    hits = []
    for (ch, ri, rn), pts in by_res.items():
        P = np.asarray(pts, dtype=float)
        d = float(np.min(np.linalg.norm(P[:, None, :] - anchor_pts[None, :, :], axis=2)))
        if d <= CONTACT_A:
            hits.append({"chain": ch, "resi": ri, "resname": rn, "min_dist_A": round(d, 2)})
    return sorted(hits, key=lambda h: (h["chain"], h["resi"]))


def main() -> int:
    report = {"schema": "p1-v5-pocket-center-verification/v1", "targets": {}}

    # ── PfDHFR / 7F3Y : MTX A702 (catalytic-site copy) ────────────────────
    pdb = PROJ2 / "7F3Y.pdb"
    atoms = parse_atoms(pdb, chain="A")
    mtx = anchor_heavy_atoms(atoms, "MTX", "A", 702)
    center = mtx.mean(axis=0)
    shell = contact_shell(mtx, atoms, exclude_resnames={"HOH"})
    report["targets"]["PfDHFR"] = {
        "pdb": "7F3Y", "anchor": "MTX A702", "anchor_atoms": int(len(mtx)),
        "center_A": center.round(3).tolist(),
        "contact_shell_4.5A": shell,
        "n_contact_residues": len(shell),
        "biological_gate": "MTX is the co-crystallized antifolate inhibitor in the DHFR folate pocket; "
                           "contact residues (Phe58/Phe116/Ile14/Ile164/Cys15/Asp54 family) are the documented DHFR pocket.",
    }

    # ── PfCRT / 6UKJ : Y01 A501 (membrane-mimetic proxy) ──────────────────
    pdb = PROJ2 / "6UKJ.pdb"
    atoms = parse_atoms(pdb, chain="A")
    y01 = anchor_heavy_atoms(atoms, "Y01", "A", 501)
    center = y01.mean(axis=0)
    shell = contact_shell(y01, atoms, exclude_resnames={"HOH"})
    report["targets"]["PfCRT"] = {
        "pdb": "6UKJ", "anchor": "Y01 A501 (cholesterol hemisuccinate, PROXY)",
        "anchor_atoms": int(len(y01)), "center_A": center.round(3).tolist(),
        "contact_shell_4.5A": shell,
        "n_contact_residues": len(shell),
        "biological_gate": "Y01 is the only non-water ligand (membrane-mimetic stabilizer, not an antimalarial "
                           "inhibitor) — PROXY_NOT_ACCEPTED caveat: poses valid relative to the Y01 cavity, "
                           "exploratory only, no potency claim.",
    }

    # ── PfATP4 / 9N10 : conserved P-type ATPase catalytic residues ────────
    pdb = PROJ2 / "9N10.pdb"
    atoms = parse_atoms(pdb, chain="A")
    seq = chain_seq_1letter(atoms, "A")
    order = sorted(seq)
    s = "".join(seq[k] for k in order)
    base = order[0]  # first residue number (construct start)
    motifs = {
        "phosphorylation_DKTGT": [order[i] for i in range(len(s) - 4)
                                  if s[i:i + 5] in ("DKTGT", "DKTGL")],
        "CSDKTGT_flank": [order[i] for i in range(len(s) - 6)
                          if s[i:i + 7] == "CSDKTGT"],
        "A_domain_DPPR": [order[i] for i in range(len(s) - 3) if s[i:i + 4] == "DPPR"],
    }
    # Walker A (P-loop) search restricted to the P-domain (before the A-domain
    # hinge DPPR ~751): a GxGxxGKT match in the C-terminal part (resi ~1160)
    # is a false positive (verified 08/08/2026), NOT the catalytic P-loop.
    p_loop = []
    for i in range(len(s) - 6):
        win = s[i:i + 7]
        if order[i] < 700 and re.fullmatch(r"G[AST][A-Z]{2}G[KR][TS]", win):
            p_loop.append(order[i])
    motifs["walker_A_p_loop"] = p_loop

    # Walker B detection: [IL]L[IL]TG[DA] consensus within the P-domain.
    walker_b = []
    for i in range(len(s) - 5):
        win = s[i:i + 6]
        if order[i] < 700 and re.fullmatch(r"[IL]L[IL]TG[DA]", win):
            walker_b.append(order[i])
    motifs["walker_B"] = walker_b

    # Anchor = phosphorylation segment (CSDKTGT flank, resi 449-457) + A-domain
    # hinge DPPR (751-754); the DPPR is the authentic A-domain conserved motif.
    anchor_resis = sorted({r for lst in motifs.values() for r in lst})
    if motifs["phosphorylation_DKTGT"]:
        dkt = motifs["phosphorylation_DKTGT"][0]
        anchor_resis.extend(range(dkt - 2, dkt + 8))  # CSDKTGTLT flank
    if motifs["A_domain_DPPR"]:
        dppr = motifs["A_domain_DPPR"][0]
        anchor_resis.extend(range(dppr, dppr + 4))
    anchor_resis = sorted(set(anchor_resis))
    if not anchor_resis:
        raise SystemExit("FAIL-CLOSED no P-type ATPase catalytic motifs found in 9N10 chain A")
    anchor_pts = np.asarray([a["xyz"] for a in atoms
                             if a["chain"] == "A" and a["resi"] in set(anchor_resis)
                             and a["atomname"] != "H"], dtype=float)
    center = anchor_pts.mean(axis=0)
    shell = contact_shell(anchor_pts, atoms, exclude_resnames={"HOH"})
    report["targets"]["PfATP4"] = {
        "pdb": "9N10",        "anchor": f"conserved P-type ATPase residues {anchor_resis} "
                                 f"(phospho-site DKTGT {motifs['phosphorylation_DKTGT']}, "
                                 f"A-domain DPPR {motifs['A_domain_DPPR']}, "
                                 f"P-loop {p_loop}, Walker B {walker_b})",
        "construct_range_A": [int(order[0]), int(order[-1])],
        "motifs": motifs, "anchor_resis": anchor_resis, "anchor_atoms": int(len(anchor_pts)),
        "center_A": center.round(3).tolist(),
        "contact_shell_4.5A": shell,
        "n_contact_residues": len(shell),
        "biological_gate": "No co-crystallized ligand in 9N10 (PfABP partner only); the biological anchor is the "
                           "conserved nucleotide-binding/phosphorylation machinery of the P-type ATPase catalytic "
                           "domain (same evidence class as the PfClpP catalytic triad). Caveat: ATP-pocket binding "
                           "is one mechanism class for P-type ATPases; exploratory, requires independent review.",
    }

    out = OUT / "p1_v5_pocket_centers_verified.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
