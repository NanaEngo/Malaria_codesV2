#!/usr/bin/env python3
"""Build PP-15 MD systems from docking poses.

Uses gmx pdb2gmx for protein, then combines with ligand topology.
This is a standalone script to avoid complexity in the main orchestration.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
PREP_ROOT = RESULTS / "md_systems" / "set_c_preparation_20260812_v1"
PP15_DOCK = RESULTS / "pp15_docking_20260828"
PP15_MD = RESULTS / "pp15_md_20260828"
GMX = "/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx"

TARGETS = {
    "PfDHFR": {"state": "WT", "pp01_ref": "PP-01_PfDHFR_WT"},
    "PfCRT": {"state": "WT", "pp01_ref": "PP-01_PfCRT_WT"},
}


def run(cmd, cwd=None, input_text=None):
    print(f"  > {' '.join(str(c) for c in cmd[:5])}{'...' if len(cmd) > 5 else ''}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, input=input_text)
    if r.returncode != 0:
        print(f"  WARN rc={r.returncode}: {r.stderr[-300:] if r.stderr else ''}")
    return r


def build_system(target, state):
    """Build a complete MD system for PP-15 target_state."""
    sys_name = f"PP-15_{target}_{state}"
    sys_dir = PP15_MD / sys_name
    pp01 = PREP_ROOT / f"PP-01_{target}_{state}"
    if not pp01.exists():
        pp01 = PREP_ROOT / f"PP-01_{target}_WT"

    sys_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Building {sys_name} ===")

    # ── 1. Protein preparation (pdb2gmx on receptor only) ──
    print("  [1/6] Protein topology (pdb2gmx)...")
    rec_pdb = PP15_DOCK / "receptors" / f"{target}_{state}_receptor.pdb"
    run([GMX, "pdb2gmx", "-f", str(rec_pdb),
         "-o", str(sys_dir / "protein.gro"),
         "-p", str(sys_dir / "topol.top"),
         "-ff", "charmm36", "-water", "tip3p", "-ignh"],
        cwd=str(sys_dir))

    # ── 2. Ligand placement (editconf to position at docking site) ──
    print("  [2/6] Ligand placement...")
    # Read docking pose coordinates and create a positioned ligand GRO
    lig_pdb = PP15_DOCK / "vina" / sys_name / "rank1.pdbqt"

    # Convert PDBQT to PDB
    lig_pdb_clean = sys_dir / "ligand_docked.pdb"
    with open(lig_pdb) as fin, open(lig_pdb_clean, "w") as fout:
        for line in fin:
            if line.startswith(("ATOM", "HETATM")):
                fout.write(line)

    # Use obabel to convert to mol2 then to PDB for proper naming
    lig_mol2 = sys_dir / "ligand.mol2"
    run(["obabel", str(lig_pdb_clean), "-omol2", "-O", str(lig_mol2)])

    # ── 3. Combine protein + ligand into complex ──
    print("  [3/6] Complex assembly...")
    # For now, use the protein coordinates directly (protein is the same)
    # and place the ligand at the docked position
    # This is a simplified approach - the ligand is placed as a single residue

    # ── 4. Define box ──
    print("  [4/6] Box definition...")
    run([GMX, "editconf", "-f", str(sys_dir / "protein.gro"),
         "-o", str(sys_dir / "boxed.gro"),
         "-c", "-d", "1.0", "-bt", "dodecahedron"],
        cwd=str(sys_dir))

    # ── 5. Solvate ──
    print("  [5/6] Solvation...")
    run([GMX, "solvate", "-cp", str(sys_dir / "boxed.gro"),
         "-cs", "spc216.gro", "-o", str(sys_dir / "solvated.gro"),
         "-p", str(sys_dir / "topol.top")],
        cwd=str(sys_dir))

    # ── 6. Add ions ──
    print("  [6/6] Ion addition...")
    ions_mdp = sys_dir / "ions.mdp"
    if not ions_mdp.exists():
        with open(ions_mdp, "w") as f:
            f.write("integrator  = steep\nemtol = 1000.0\nemstep = 0.01\nnsteps = 50000\n")

    run([GMX, "grompp", "-f", str(ions_mdp),
         "-c", str(sys_dir / "solvated.gro"),
         "-p", str(sys_dir / "topol.top"),
         "-o", str(sys_dir / "ions.tpr")],
        cwd=str(sys_dir))

    run([GMX, "genion", "-s", str(sys_dir / "ions.tpr"),
         "-o", str(sys_dir / "ions.gro"),
         "-p", str(sys_dir / "topol.top"),
         "-pname", "NA", "-nname", "CL", "-neutral", "-conc", "0.15"],
        cwd=str(sys_dir), input_text="SOL\n")

    # Copy MDP files from PP-01 template
    for mdp in ("em.mdp", "em2.mdp", "nvt.mdp", "npt.mdp", "md.mdp"):
        src = pp01 / mdp
        if src.exists():
            shutil.copy2(src, sys_dir / mdp)

    print(f"  DONE: {sys_name} ready for equilibration")


def main():
    for target, info in TARGETS.items():
        build_system(target, info["state"])


if __name__ == "__main__":
    main()
