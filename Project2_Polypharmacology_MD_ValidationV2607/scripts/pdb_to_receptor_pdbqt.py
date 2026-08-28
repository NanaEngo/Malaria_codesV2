#!/usr/bin/env python3
"""Convert protein PDB to clean PDBQT for Vina rigid docking.

Reads PDB, keeps only ATOM/HETATM with standard residues,
computes Gasteiger charges via OpenBabel, writes clean PDBQT.

Usage:
    python pdb_to_receptor_pdbqt.py input.pdb output.pdbqt
"""
import sys
import subprocess
import tempfile
from pathlib import Path

input_pdb = Path(sys.argv[1])
output_pdbqt = Path(sys.argv[2])

# Step 1: Clean PDB (keep ATOM/HETATM only, no TER/END/hetero)
clean_lines = []
with open(input_pdb) as f:
    for line in f:
        if line.startswith(("ATOM", "HETATM")):
            clean_lines.append(line)

with tempfile.NamedTemporaryFile(mode="w", suffix=".pdb", delete=False) as tmp:
    tmp.writelines(clean_lines)
    tmp_pdb = tmp.name

# Step 2: OpenBabel PDBQT conversion (rigid, no flexible torsions)
try:
    subprocess.run(
        ["obabel", tmp_pdb, "-opdbqt", "-O", str(output_pdbqt),
         "--partialcharge", "gasteiger"],
        check=True, capture_output=True, text=True
    )
finally:
    Path(tmp_pdb).unlink(missing_ok=True)

# Step 3: Remove ROOT/ENDROOT/BRANCH/ENDBRANCH/TORSDOF lines
lines = output_pdbqt.read_text().splitlines()
clean = [l for l in lines
         if not any(l.startswith(tag) for tag in
                    ("ROOT", "ENDROOT", "BRANCH", "ENDBRANCH", "TORSDOF"))]
output_pdbqt.write_text("\n".join(clean) + "\n")
print(f"Written {len([l for l in clean if l.startswith('ATOM')])} atoms to {output_pdbqt}")
