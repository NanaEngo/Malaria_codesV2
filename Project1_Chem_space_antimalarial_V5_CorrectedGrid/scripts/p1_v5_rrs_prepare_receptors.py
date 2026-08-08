#!/usr/bin/env python3
"""P1 V5 — docking-RRS pilot, receptor preparation (uniform protein-only protocol).

Rationale (08/08/2026, after the 17x4 WT Vina runs):
  The existing WT receptor PDBQTs include co-crystallized HETATM content
  (7F3Y: MTX/NDP/UMP/GOL; 6UKJ: Y01) as rigid receptor atoms, while the
  P2-derived mutant PDBs carry a DIFFERENT HETATM inventory (e.g. 165 MTX
  atoms vs 126 in the WT PDBQT). A Resistance-Resilience Score (RRS) is a
  RATIO of WT and mutant affinities, so any ligand-content asymmetry would
  bias the ratio. This pilot therefore uses a UNIFORM protein-only receptor
  protocol for the WHOLE panel (WT + mutants): only ATOM records (protein,
  all chains), no HETATM, no water; PDBQT via Open Babel -xr (AD4 types,
  polar H added); the box/anchor definitions are unchanged and the anchor
  atom set is still read from the co-crystallized PDB (gate contact only).

PfCRT numbering note: PDB 6UKJ is the 7G8 isoform (CQ-resistant), whose
structural position 76 is already THR (K76T background; SEQRES
...LSVSVMNTIFAKRTL...). Therefore, in the 6UKJ frame:
    WT-K76   = T76 -> K76 revertant (wild-type allele baseline)
    K76T     = 6UKJ as-is (the 7G8 resistant variant)
    K76A     = T76 -> A76
The P2 mutant files PfCRT_K76T/K76A are frame-incompatible with 6UKJ
(rmsd ~3.6 A, 232 residues missing) and are NOT used here.

PfDHFR numbering note: all four antifolate-resistance mutants (N51I, C59R,
S108N, I164L) are regenerated from 7F3Y chain A with the SAME
backbone-preserving tool, so the whole DHFR panel shares the 7F3Y frame
and an identical side-chain-completeness policy (the P2 PyMOL mutants carry
hydrogens and extra side-chain atoms and are not used).

Outputs:
  results/rrs_pilot/receptors/<LABEL>.pdb       (protein-only)
  results/rrs_pilot/receptors/<LABEL>.pdbqt     (obabel -xr)
  results/rrs_pilot/receptors/frame_check.json  (CA rmsd vs WT PDB)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
P2P = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins"
OUT = V5 / "results/rrs_pilot/receptors"
OBABEL = "/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel"
# note: the miniforge base obabel wrapper is broken (py3.13 site-packages);
# malaria_md ships a working Open Babel 3.1.0 binary.

WT_PDBS = {
    "PfDHFR": P2P / "7F3Y.pdb",
    "PfCRT": P2P / "6UKJ.pdb",
}
# Note: the P2-derived PfDHFR mutant PDBs (data/proteins/mutants/*.pdb) are NOT
# used here — they carry PyMOL-added hydrogens and extra side-chain atoms, which
# would break the uniform receptor protocol. All mutants are regenerated from
# the WT PDBs with the same backbone-preserving tool.


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def strip_to_protein(pdb_in: Path, pdb_out: Path) -> int:
    """Keep only protein ATOM records; drop HETATM/water AND HYDROGENS.

    The P2-derived PfDHFR mutant PDBs carry explicit hydrogens added by
    PyMOL (9957 H per mutant vs 0 in the raw PDB WT). For a uniform
    protein-only receptor protocol the input must be hydrogen-free; the
    single shared obabel -xr step adds polar hydrogens for every receptor
    identically.
    """
    kept = 0
    with pdb_in.open(errors="replace") as fi, pdb_out.open("w") as fo:
        for line in fi:
            if line.startswith(("TER", "END")):
                fo.write(line)
                continue
            if not line.startswith("ATOM  "):
                continue
            atomname = line[12:16].strip()
            if atomname and atomname[0] == "H":
                continue  # hydrogen atom
            fo.write(line)
            kept += 1
    return kept


def read_ca(p: Path):
    out = {}
    for line in p.read_text(errors="replace").splitlines():
        if line.startswith("ATOM  ") and line[12:16].strip() == "CA":
            try:
                out[(line[21:22].strip(), int(line[22:26]))] = np.asarray(
                    [float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
    return out


def frame_vs_wt(candidate_pdb: Path, wt_pdb: Path) -> dict:
    a, b = read_ca(wt_pdb), read_ca(candidate_pdb)
    common = sorted(set(a) & set(b))
    if not common:
        return {"status": "FAIL", "reason": "no common CA"}
    d = np.asarray([a[k] - b[k] for k in common])
    rmsd = float(np.sqrt(np.mean(d ** 2)))
    missing = len(set(a) - set(b))
    return {"status": "OK" if rmsd < 1e-6 and missing == 0 else "PARTIAL",
            "common_ca": len(common), "missing_vs_wt": missing,
            "rmsd_A": round(rmsd, 6), "max_A": round(float(np.max(np.linalg.norm(d, axis=1))), 6)}


def mutate_pdb_frame(src: Path, chain: str, pos: int, from_aa: str, to_aa: str) -> Path:
    """Backbone-preserving single-point mutation (mutate_pdb.py logic).

    Keeps N/CA/C/O/CB of the target residue (renamed to the mutant amino
    acid) and drops its sidechain atoms; every other atom keeps identical
    coordinates -> the CA frame is preserved by construction (rmsd 0).
    Used uniformly for the PfCRT panel (6UKJ) and the PfDHFR panel (7F3Y).
    """
    from3 = {"N": "ASN", "C": "CYS", "S": "SER", "I": "ILE",
             "T": "THR", "K": "LYS", "A": "ALA"}
    dst = OUT / f"{src.stem}_{from_aa}{pos}{to_aa}.pdb"
    to3 = {"K": "LYS", "A": "ALA", "I": "ILE", "R": "ARG", "N": "ASN", "L": "LEU"}[to_aa]
    found = mutated = 0
    with src.open(errors="replace") as fi, dst.open("w") as fo:
        for line in fi:
            if line.startswith("ATOM  "):
                try:
                    ch = line[21]
                    resi = int(line[22:26])
                    resn = line[17:20].strip()
                except ValueError:
                    fo.write(line)
                    continue
                if ch == chain and resi == pos:
                    found += 1
                    if from3.get(from_aa) and resn != from3[from_aa]:
                        raise SystemExit(
                            f"FAIL-CLOSED expected {from3[from_aa]} at {chain}{pos}, found {resn}")
                    atom = line[12:16].strip()
                    if atom in ("N", "CA", "C", "O", "CB"):
                        fo.write(line[:17] + f"{to3:>3}" + line[20:])
                        if atom in ("N", "CA", "C", "O"):
                            mutated += 1
                    # sidechain atoms removed
                else:
                    fo.write(line)
            else:
                fo.write(line)
    if found == 0 or mutated == 0:
        raise SystemExit(f"FAIL-CLOSED mutation {from_aa}{pos}{to_aa}: found={found} mutated={mutated}")
    return dst


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW = OUT / "raw_mutated"
    RAW.mkdir(parents=True, exist_ok=True)
    frame_report = {}
    _prev_dst = None

    def _mutate(src: Path, chain: str, pos: int, from_aa: str, to_aa: str) -> Path:
        nonlocal _prev_dst
        dst = mutate_pdb_frame(src, chain, pos, from_aa, to_aa)
        _prev_dst = dst
        return dst

    # ---- PfDHFR mutagenesis (7F3Y frame, uniform backbone tool) --------
    dhfr_wt = WT_PDBS["PfDHFR"]
    dhfr_muts = {
        "PfDHFR_N51I": _mutate(dhfr_wt, "A", 51, "N", "I"),
        "PfDHFR_C59R": _mutate(dhfr_wt, "A", 59, "C", "R"),
        "PfDHFR_S108N": _mutate(dhfr_wt, "A", 108, "S", "N"),
        "PfDHFR_I164L": _mutate(dhfr_wt, "A", 164, "I", "L"),
    }

    # ---- PfCRT mutagenesis (6UKJ frame) -------------------------------
    # WT-K76 revertant: structural T76 -> K76
    rev = _mutate(WT_PDBS["PfCRT"], "A", 76, "T", "K")
    # K76A: structural T76 -> A76
    k76a = _mutate(WT_PDBS["PfCRT"], "A", 76, "T", "A")
    # K76T = 6UKJ as-is (7G8 already has T76)
    k76t = WT_PDBS["PfCRT"]

    receptor_sources = {
        # DHFR panel (WT + 4 mutants, protein-only, 7F3Y frame)
        "PfDHFR_WT": dhfr_wt,
        **dhfr_muts,
        # CRT panel (WT-K76 revertant, K76T = 6UKJ, K76A) — all 6UKJ frame
        "PfCRT_WT_K76": rev,
        "PfCRT_K76T": k76t,
        "PfCRT_K76A": k76a,
    }

    for label, src in receptor_sources.items():
        # move intermediates (raw mutated PDBs) into raw_mutated/
        if src != k76t and src not in (WT_PDBS["PfDHFR"], WT_PDBS["PfCRT"]):
            src.rename(RAW / src.name)
            src = RAW / src.name
        prot = OUT / f"{label}.pdb"
        n_atoms = strip_to_protein(src, prot)
        pdbqt = OUT / f"{label}.pdbqt"
        r = subprocess.run([OBABEL, str(prot), "-O", str(pdbqt), "-xr"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not pdbqt.exists() or pdbqt.stat().st_size == 0:
            raise SystemExit(f"FAIL-CLOSED obabel failed for {label}: {r.stderr[:200]}")
        # frame check against the corresponding WT PDB (fail-closed)
        wt = WT_PDBS["PfDHFR"] if label.startswith("PfDHFR") else WT_PDBS["PfCRT"]
        fr = frame_vs_wt(prot, wt)
        if fr["status"] != "OK":
            raise SystemExit(f"FAIL-CLOSED frame mismatch for {label}: {fr}")
        frame_report[label] = {
            "source": str(src), "protein_atoms": n_atoms,
            "pdbqt_bytes": pdbqt.stat().st_size,
            "pdb_sha256": sha256(prot), "pdbqt_sha256": sha256(pdbqt),
            "frame": fr,
        }
        print(f"{label:16s} atoms={n_atoms:6d} frame={fr['status']} rmsd={fr['rmsd_A']}")

    (OUT / "frame_check.json").write_text(json.dumps(frame_report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "RECEPTORS_READY", "n": len(receptor_sources), "out": str(OUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
