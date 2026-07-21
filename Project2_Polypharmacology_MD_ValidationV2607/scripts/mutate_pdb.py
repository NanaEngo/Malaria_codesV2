#!/usr/bin/env python3
"""
Simple PDB single-point mutation tool.
Replaces residue type at specified position and removes old sidechain atoms.
Sidechains will be rebuilt during MD energy minimization.

Usage:
    python scripts/mutate_pdb.py --pdb 7F3Y --chain A --position 51 --from N --to I
"""

import argparse
import shutil
from pathlib import Path

# Backbone atoms to keep (N, CA, C, O, CB for most residues)
BACKBONE_ATOMS = {"N", "CA", "C", "O", "CB"}

# Allowed amino acids
AA_3TO1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLU": "E", "GLN": "Q", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}
AA_1TO3 = {v: k for k, v in AA_3TO1.items()}


def mutate_pdb(input_pdb: Path, output_pdb: Path, chain: str,
               position: int, from_aa: str, to_aa: str) -> bool:
    """Mutate a single residue in a PDB file."""

    to_aa_3 = AA_1TO3.get(to_aa, to_aa)
    from_aa_3 = AA_1TO3.get(from_aa, from_aa)

    lines = input_pdb.read_text().splitlines()
    out_lines = []
    found = False
    mutation_done = False

    for line in lines:
        if not line.startswith(("ATOM", "HETATM", "TER", "END")):
            out_lines.append(line)
            continue

        # PDB format: ATOM serial atomname altloc resname chain resi icode xyz...
        if len(line) < 27:
            out_lines.append(line)
            continue

        try:
            resname = line[17:20].strip()
            reschain = line[21]
            resnum = int(line[22:26].strip())
        except (ValueError, IndexError):
            out_lines.append(line)
            continue

        if reschain == chain and resnum == position:
            if not found:
                found = True
                print(f"  Found residue: {resname} {chain}:{position}")

            if resname.upper() != from_aa_3.upper():
                print(f"  WARNING: Expected residue {from_aa_3} at {chain}:{position}, "
                      f"found {resname}")
                out_lines.append(line)
                continue

            # For ATOM records: keep backbone atoms, remove sidechains
            if line.startswith("ATOM"):
                atomname = line[12:16].strip()
                if atomname in {"N", "CA", "C", "O"}:  # keep backbone
                    # Change residue name
                    new_line = line[:17] + f"{to_aa_3:>3}" + line[20:]
                    out_lines.append(new_line)
                    mutation_done = True
                elif atomname == "CB":  # keep CB as placeholder
                    new_line = line[:17] + f"{to_aa_3:>3}" + line[20:]
                    out_lines.append(new_line)
                # else: skip sidechain atoms (they'll be rebuilt by MD prep)
            elif line.startswith("TER"):
                out_lines.append(line)
            # else: skip HETATM at this residue (e.g. water)
        else:
            out_lines.append(line)

    if not found:
        print(f"  ERROR: Residue {chain}:{position} not found in {input_pdb}")
        return False

    if not mutation_done:
        print(f"  WARNING: No backbone atoms were mutated at {chain}:{position}")
        print(f"  The PDB file may have alternate conformations or unusual residue numbering")
        # Still save the file
        output_pdb.write_text("\n".join(out_lines) + "\n")
        return True

    output_pdb.write_text("\n".join(out_lines) + "\n")
    n_original = sum(1 for l in lines if l.startswith("ATOM") and l[21] == chain)
    n_mutated = sum(1 for l in out_lines if l.startswith("ATOM") and l[21] == chain)
    print(f"  Atoms: {n_original} → {n_mutated} (removed {n_original - n_mutated} sidechain atoms)")
    print(f"  Mutant saved: {output_pdb}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Single-point PDB mutation tool")
    parser.add_argument("--pdb", required=True, help="PDB ID (e.g., 7F3Y) or path")
    parser.add_argument("--chain", default="A", help="Chain ID (default: A)")
    parser.add_argument("--position", type=int, required=True, help="Residue position")
    parser.add_argument("--from", dest="from_aa", required=True, help="Original AA (1-letter)")
    parser.add_argument("--to", dest="to_aa", required=True, help="Target AA (1-letter)")
    parser.add_argument("--output", default=None, help="Output PDB path (default: auto)")
    args = parser.parse_args()

    # Resolve PDB path
    pdb_path = Path(args.pdb)
    if not pdb_path.exists():
        pdb_path = Path(__file__).parent.parent / "data" / "proteins" / f"{args.pdb}.pdb"
    if not pdb_path.exists():
        print(f"ERROR: PDB file not found: {args.pdb}")
        return

    # Output path
    if args.output:
        output_path = Path(args.output)
    else:
        mutant_dir = Path(__file__).parent.parent / "data" / "proteins" / "mutants"
        mutant_dir.mkdir(parents=True, exist_ok=True)
        # Use format: {PDB}_{WT}{POS}{MUT}.pdb
        pdb_id = pdb_path.stem
        output_path = mutant_dir / f"{pdb_id}_{args.from_aa}{args.position}{args.to_aa}.pdb"

    print(f"  Template: {pdb_path}")
    print(f"  Mutation: {args.from_aa}{args.position}{args.to_aa} (chain {args.chain})")
    print(f"  Output:   {output_path}")

    success = mutate_pdb(pdb_path, output_path, args.chain,
                         args.position, args.from_aa, args.to_aa)
    if success:
        print("  ✓ Mutation complete")
    else:
        print("  ✗ Mutation failed")


if __name__ == "__main__":
    main()
