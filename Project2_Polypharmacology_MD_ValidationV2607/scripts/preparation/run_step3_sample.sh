#!/usr/bin/env bash
# Sample run script for auditing — DO NOT execute on the audit server
# This mirrors the commands that `step3_complex_assembly.py` would generate.

set -euo pipefail

# 1) Center protein and create a box with 1.2 nm padding (dodecahedron)
gmx editconf -f protein_prep/pfdhfr_processed.gro -o complex_assembly/pfdhfr_box.gro -c -d 1.2 -bt dodecahedron

# 2) Insert ligand (attempt up to 1000 placements)
gmx insert-molecules -f complex_assembly/pfdhfr_box.gro -ci ligand_prep/LIG001.gro -o complex_assembly/complex.gro -nmol 1 -try 1000

# 3) IMPORTANT: inspect complex_assembly/combined.top now and verify the
#    [ molecules ] counts and that the ligand include is present.

# 4) Solvate the complex (spc216.gro used as generic solvent file here)
gmx solvate -cp complex_assembly/complex.gro -cs spc216.gro -o complex_assembly/complex_solv.gro -p complex_assembly/combined.top

# 5) Prepare ions tpr and add ions (neutralize + 0.15 M NaCl)
gmx grompp -f complex_assembly/ions.mdp -c complex_assembly/complex_solv.gro -p complex_assembly/combined.top -o complex_assembly/ions.tpr
gmx genion -s complex_assembly/ions.tpr -o complex_assembly/complex_solv_ions.gro -p complex_assembly/combined.top -pname NA -nname CL -neutral -conc 0.15

# 6) Energy minimization
gmx grompp -f complex_assembly/em.mdp -c complex_assembly/complex_solv_ions.gro -p complex_assembly/combined.top -o complex_assembly/em.tpr
gmx mdrun -deffnm complex_assembly/em

echo "Sample run script complete (this file is for auditing only)."
