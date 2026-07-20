#!/usr/bin/env python3
"""
fix_pdb_missing_atoms.py
------------------------
Extracts chain A, diagnoses missing heavy sidechain atoms that cause pdb2gmx
(GROMACS) to fail with:
  "Fatal error: atom <X> used in topology entry is not found in the input file"

The script:
  1. Extracts only chain A from the input PDB (writes a temporary chain-A-only file)
  2. Scans all chain A residues for missing sidechain heavy atoms
  3. Reports the problematic residues with their GROMACS internal residue index
  4. Uses pdbfixer (OpenMM) to rebuild missing atoms with ideal geometry
  5. Writes a corrected chain-A-only PDB ready for pdb2gmx

Dependencies:
    pip install pdbfixer openmm

Usage:
    python fix_pdb_missing_atoms.py input.pdb [output.pdb]

    If output.pdb is not specified, writes <input_stem>_chainA_fixed.pdb
"""

import sys
import argparse
import tempfile
import os
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Atom completeness reference (heavy atoms only; H are added by pdb2gmx)
# ---------------------------------------------------------------------------
REQUIRED_ATOMS = {
    "ALA": ["CB"],
    "ARG": ["CB", "CG", "CD", "NE", "CZ", "NH1", "NH2"],
    "ASN": ["CB", "CG", "OD1", "ND2"],
    "ASP": ["CB", "CG", "OD1", "OD2"],
    "CYS": ["CB", "SG"],
    "GLN": ["CB", "CG", "CD", "OE1", "NE2"],
    "GLU": ["CB", "CG", "CD", "OE1", "OE2"],
    "GLY": [],                          # no sidechain
    "HIS": ["CB", "CG", "ND1", "CD2", "CE1", "NE2"],
    "ILE": ["CB", "CG1", "CG2", "CD1"],
    "LEU": ["CB", "CG", "CD1", "CD2"],
    "LYS": ["CB", "CG", "CD", "CE", "NZ"],
    "MET": ["CB", "CG", "SD", "CE"],
    "PHE": ["CB", "CG", "CD1", "CD2", "CE1", "CE2", "CZ"],
    "PRO": ["CB", "CG", "CD"],
    "SER": ["CB", "OG"],
    "THR": ["CB", "OG1", "CG2"],
    "TRP": ["CB", "CG", "CD1", "CD2", "NE1", "CE2", "CE3", "CZ2", "CZ3", "CH2"],
    "TYR": ["CB", "CG", "CD1", "CD2", "CE1", "CE2", "CZ", "OH"],
    "VAL": ["CB", "CG1", "CG2"],
}

BACKBONE_ATOMS = {"N", "CA", "C", "O"}


# ---------------------------------------------------------------------------
# Chain extraction
# ---------------------------------------------------------------------------

def extract_chain(pdb_path: str, chain_id: str, out_path: str) -> int:
    """
    Writes a new PDB containing only ATOM/HETATM records for chain_id,
    followed by a TER record and END.
    Returns the number of ATOM lines written.
    """
    atom_count = 0
    with open(pdb_path) as fh_in, open(out_path, "w") as fh_out:
        for line in fh_in:
            record = line[:6].strip()
            if record in ("ATOM", "HETATM"):
                if line[21] == chain_id:
                    fh_out.write(line)
                    if record == "ATOM":
                        atom_count += 1
            elif record == "TER":
                if len(line) > 21 and line[21] == chain_id:
                    fh_out.write(line)
        fh_out.write("END\n")
    return atom_count


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def parse_pdb_atoms(pdb_path: str) -> dict:
    """
    Returns a dict:
        {(chain, resseq, resname): set_of_atom_names}
    preserving insertion order for GROMACS residue indexing.
    """
    residues = {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM"):
                continue
            atom    = line[12:16].strip()
            resname = line[17:20].strip()
            chain   = line[21]
            resseq  = int(line[22:26].strip())
            key = (chain, resseq, resname)
            if key not in residues:
                residues[key] = set()
            residues[key].add(atom)
    return residues


def diagnose(residues: dict) -> list[dict]:
    """
    Returns a list of problem records, each containing:
        chain, resseq, resname, missing_atoms, gromacs_chain_index
    """
    # Build per-chain GROMACS index (1-based, sequential)
    chain_counters = defaultdict(int)
    problems = []

    for (chain, resseq, resname), present in residues.items():
        chain_counters[chain] += 1
        gmx_idx = chain_counters[chain]

        if resname not in REQUIRED_ATOMS:
            continue

        missing = [a for a in REQUIRED_ATOMS[resname] if a not in present]
        if missing:
            problems.append({
                "chain": chain,
                "resseq": resseq,
                "resname": resname,
                "missing_atoms": missing,
                "gromacs_chain_index": gmx_idx,
            })

    return problems


def print_report(problems: list[dict]) -> None:
    if not problems:
        print("✓ No missing heavy sidechain atoms detected.")
        return

    print(f"{'─'*62}")
    print(f"  {'Chain':6} {'PDB ResSeq':10} {'ResName':8} {'GMX Idx':8}  Missing atoms")
    print(f"{'─'*62}")
    for p in problems:
        atoms = ", ".join(p["missing_atoms"])
        print(f"  {p['chain']:6} {p['resseq']:<10} {p['resname']:8} {p['gromacs_chain_index']:<8}  {atoms}")
    print(f"{'─'*62}")
    print(f"  {len(problems)} problem(s) found.\n")


# ---------------------------------------------------------------------------
# Fix
# ---------------------------------------------------------------------------

def fix_with_pdbfixer(chain_a_pdb: str, output_pdb: str) -> None:
    """
    Uses pdbfixer to add missing heavy atoms on the chain-A-only PDB.
    Gaps (missing loop residues) are left as-is; only existing residues
    with incomplete sidechains are repaired.
    """
    try:
        from pdbfixer import PDBFixer
        from openmm.app import PDBFile
    except ImportError:
        print("\nERROR: pdbfixer is not installed.")
        print("Install it with:  pip install pdbfixer openmm")
        sys.exit(1)

    fixer = PDBFixer(filename=chain_a_pdb)

    # Identify gaps but do NOT rebuild missing loop residues
    fixer.findMissingResidues()
    fixer.missingResidues = {}

    # Find and add only missing heavy atoms on existing residues
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()

    with open(output_pdb, "w") as fh:
        PDBFile.writeFile(fixer.topology, fixer.positions, fh, keepIds=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract chain A, diagnose and fix missing sidechain atoms for GROMACS pdb2gmx."
    )
    parser.add_argument("input_pdb", help="Input PDB file (may contain multiple chains)")
    parser.add_argument(
        "output_pdb",
        nargs="?",
        default=None,
        help="Output fixed chain-A PDB (default: <input_stem>_chainA_fixed.pdb)",
    )
    parser.add_argument(
        "--chain",
        default="A",
        metavar="ID",
        help="Chain to extract and process (default: A)",
    )
    parser.add_argument(
        "--diagnose-only",
        action="store_true",
        help="Print the diagnosis report without writing a fixed file",
    )
    args = parser.parse_args()

    input_path  = args.input_pdb
    chain_id    = args.chain.upper()
    output_path = args.output_pdb or f"{Path(input_path).stem}_chain{chain_id}_fixed.pdb"

    print(f"\n{'='*62}")
    print("  PDB sidechain completeness checker for GROMACS pdb2gmx")
    print(f"{'='*62}")
    print(f"  Input : {input_path}")
    print(f"  Chain : {chain_id}\n")

    # Step 1 – extract chain A into a temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".pdb", delete=False)
    tmp.close()
    chain_atom_count = extract_chain(input_path, chain_id, tmp.name)

    if chain_atom_count == 0:
        print(f"  ERROR: No ATOM records found for chain '{chain_id}' in {input_path}")
        os.unlink(tmp.name)
        sys.exit(1)

    print(f"  Extracted {chain_atom_count} ATOM records for chain {chain_id}.\n")

    # Step 2 – diagnose
    residues = parse_pdb_atoms(tmp.name)
    problems = diagnose(residues)
    print_report(problems)

    if args.diagnose_only or not problems:
        if not problems:
            print(f"  No fix needed. Chain {chain_id} PDB is ready for pdb2gmx.")
            print(f"  Chain-only file written to: {output_path}\n")
            # Still write the clean chain-A-only file even if no fix needed
            import shutil
            shutil.copy(tmp.name, output_path)
        os.unlink(tmp.name)
        return

    # Step 3 – fix
    print("  Rebuilding missing atoms with pdbfixer …")
    fix_with_pdbfixer(tmp.name, output_path)
    os.unlink(tmp.name)
    print(f"  Output: {output_path}")

    # Step 4 – verify
    print("\n  Verifying fix …")
    residues_fixed = parse_pdb_atoms(output_path)
    remaining = diagnose(residues_fixed)

    if not remaining:
        original_count = chain_atom_count
        fixed_count    = sum(1 for line in open(output_path) if line.startswith("ATOM"))
        print("  ✓ All missing atoms rebuilt successfully.")
        print(f"  ✓ Chain {chain_id} atom count: {original_count} → {fixed_count} (+{fixed_count - original_count})\n")
        print("  ⚠  Note: rebuilt sidechains use ideal geometry (not crystallographic).")
        print("     Run energy minimization before production MD.\n")
    else:
        print("  ✗ Some issues remain after fix:")
        print_report(remaining)


if __name__ == "__main__":
    main()
