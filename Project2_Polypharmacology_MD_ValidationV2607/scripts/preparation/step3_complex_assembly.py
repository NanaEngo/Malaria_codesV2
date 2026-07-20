"""
STEP 3: Complex Assembly — combine protein + ligand, solvate, add ions
=====================================================================

Prepare GROMACS-ready files and a copy-pasteable run script to:
  - insert the ligand into the protein box
  - merge ligand topology into the protein topology
  - solvate with TIP3P and add 0.15 M NaCl
  - create minimal `ions.mdp` and `em.mdp` templates

This script does not execute GROMACS commands; it writes `complex_assembly/run_step3.sh`
that you can run in a terminal where `gmx` is available.
"""

import os
import sys
from pathlib import Path

# CONFIG — update if your files are named differently
PROTEIN_GRO = Path("protein_prep/pfdhfr_processed.gro")
PROTEIN_TOP = Path("protein_prep/pfdhfr.top")
LIGAND_GRO  = Path("ligand_prep/LIG001.gro")
LIGAND_TOP  = Path("ligand_prep/LIG001.top")
LIGAND_ITP  = Path("ligand_prep/LIG001.itp")
OUTPUT_DIR  = Path("complex_assembly")
BOX_PADDING = 1.2   # nm
ION_CONC    = 0.15  # mol/L (M)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_inputs():
    missing = [p for p in (PROTEIN_GRO, PROTEIN_TOP, LIGAND_GRO) if not p.exists()]
    if missing:
        sys.exit("ERROR: Missing required input files:\n" + "\n".join(str(m) for m in missing))

def create_combined_top(protein_top: Path, ligand_itp: Path, out_top: Path, ligand_name: str = "LIG001"):
    with open(protein_top, 'r') as f:
        lines = f.readlines()

    # Find position to insert include (after initial includes)
    insert_idx = 0
    for i, L in enumerate(lines[:80]):
        if L.strip().lower().startswith('#include'):
            insert_idx = i + 1

    include_line = f'#include "{ligand_itp.as_posix()}"\n'
    # Insert include for ligand ITP if not already present
    if not any(l.strip() == include_line.strip() for l in lines):
        lines.insert(insert_idx, include_line)

    # Ensure [ molecules ] section contains ligand entry (avoid duplicates)
    mol_start = None
    for i, L in enumerate(lines):
        if L.strip().lower().startswith('[ molecules ]'):
            mol_start = i
            break

    def molecules_section_range(start_idx):
        # returns (start, end) indices of molecules section
        end = start_idx + 1
        for j in range(start_idx + 1, len(lines)):
            if lines[j].strip().startswith('['):
                end = j
                break
            end = j + 1
        return start_idx, end

    if mol_start is not None:
        s, e = molecules_section_range(mol_start)
        section = lines[s:e]
        # check if ligand already listed
        if any(ligand_name in L for L in section):
            pass
        else:
            # insert just before end of molecules section
            insert_pos = e
            lines.insert(insert_pos, f'{ligand_name:<16} 1\n')
    else:
        lines.append('\n[ molecules ]\n')
        lines.append('; Compound        nmol\n')
        lines.append(f'{ligand_name:<16} 1\n')

    out_top.write_text(''.join(lines))
    print(f"Wrote combined topology: {out_top}")

def write_mdp_templates(outdir: Path):
    ions = outdir / 'ions.mdp'
    em   = outdir / 'em.mdp'
    ions.write_text("""
integrator  = steep
emtol       = 1000.0
emstep      = 0.01
nsteps      = 500
""".lstrip())
    em.write_text("""
integrator  = steep
emtol       = 100.0
emstep      = 0.01
nsteps      = 50000
nstenergy   = 10
nstlog      = 10
""".lstrip())
    print(f"Wrote mdp templates: {ions}, {em}")
    return ions, em

def write_run_script(outdir: Path, combined_top: Path):
    sh = outdir / 'run_step3.sh'
    cmds = [
        f"gmx editconf -f {PROTEIN_GRO.as_posix()} -o {outdir/'pfdhfr_box.gro'} -c -d {BOX_PADDING} -bt dodecahedron",
        f"gmx insert-molecules -f {outdir/'pfdhfr_box.gro'} -ci {LIGAND_GRO.as_posix()} -o {outdir/'complex.gro'} -nmol 1 -try 1000",
        f"# Inspect {combined_top.as_posix()} now and ensure molecule counts are correct",
        f"gmx solvate -cp {outdir/'complex.gro'} -cs spc216.gro -o {outdir/'complex_solv.gro'} -p {combined_top.as_posix()}",
        f"gmx grompp -f {outdir/'ions.mdp'} -c {outdir/'complex_solv.gro'} -p {combined_top.as_posix()} -o {outdir/'ions.tpr'}",
        f"gmx genion -s {outdir/'ions.tpr'} -o {outdir/'complex_solv_ions.gro'} -p {combined_top.as_posix()} -pname NA -nname CL -neutral -conc {ION_CONC}",
        f"gmx grompp -f {outdir/'em.mdp'} -c {outdir/'complex_solv_ions.gro'} -p {combined_top.as_posix()} -o {outdir/'em.tpr'}",
        f"gmx mdrun -deffnm {outdir/'em'}"
    ]

    content = "#! /usr/bin/env bash\nset -euo pipefail\n\n# Run these commands in a shell with GROMACS available\n\n" + "\n".join(cmds) + "\n"
    sh.write_text(content)
    sh.chmod(0o755)
    print(f"Wrote run script: {sh}")

def main():
    check_inputs()
    combined_top = OUTPUT_DIR / 'combined.top'
    ligand_itp = LIGAND_ITP if LIGAND_ITP.exists() else LIGAND_TOP
    create_combined_top(PROTEIN_TOP, ligand_itp, combined_top)
    ions, em = write_mdp_templates(OUTPUT_DIR)
    write_run_script(OUTPUT_DIR, combined_top)
    print('\nDone — inspect files in', OUTPUT_DIR)

if __name__ == '__main__':
    main()
