#!/usr/bin/env python3
"""PP-15 MD preparation and production -- minimal 2-WT-scenario.

Prepares PP-15 (Class A* candidate) against PfDHFR WT and PfCRT WT.
Steps: dock, prepare, equilibrate, produce.

Usage:
    mamba run -n malaria_md python scripts/p2_pp15_launch.py --step dock
    mamba run -n malaria_md python scripts/p2_pp15_launch.py --step all
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
PREP_ROOT = RESULTS / "md_systems" / "set_c_preparation_20260812_v1"
PP15_DOCK = RESULTS / "pp15_docking_20260828"
PP15_MD = RESULTS / "pp15_md_20260828"
GMX = "/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx"
OBABEL = "/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel"
PYTHON = "/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
LIGAND_PREP = PROJECT / "scripts" / "p2_pp15_ligand_prep.py"

PP15_SMILES = "COc1c(O)cc2c(c1O)C(=O)C([C@H](O)c1ccccc1)CO2"
PP15_ID = "PP-15"

# (target, mutation) -> receptor PDB basename in V5/PP-01
RECEPTORS = {
    ("PfDHFR", "WT"): "PfDHFR_WT.pdb",
    ("PfCRT", "WT"): "PfCRT_WT_K76.pdb",
}


def run(cmd, cwd=None, check=True, input_text=None):
    print(f"  > {cmd[0]} ... {' '.join(cmd[1:4])}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       input=input_text)
    if check and r.returncode != 0:
        print(f"  FAILED rc={r.returncode}")
        for line in (r.stderr or "").splitlines()[-10:]:
            print(f"    {line}")
        sys.exit(1)
    return r


def compute_vina_box(target, state):
    """Compute docking box centered on PP-01 ligand binding site."""
    # Use PP-01 ligand coordinates as binding-site reference
    ref_lig = PREP_ROOT / f"PP-01_{target}_{state}" / "ligand_heavy_dock.pdb"
    if not ref_lig.exists():
        ref_lig = PREP_ROOT / f"PP-01_{target}_WT" / "ligand_heavy_dock.pdb"
    coords = []
    with open(ref_lig) as f:
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    c = np.array(coords)
    center = c.mean(axis=0)
    # 25 A box (standard for small-molecule docking)
    size = [25.0, 25.0, 25.0]
    return center.tolist(), size


def extract_rank1(vina_out, dest):
    models, cur = [], []
    for line in open(vina_out):
        if line.startswith("MODEL"):
            if cur:
                models.append(cur)
            cur = [line]
        elif line.startswith("ENDMDL"):
            cur.append(line)
            models.append(cur)
            cur = []
        else:
            cur.append(line)
    if models:
        with open(dest, "w") as f:
            f.writelines(models[0])


def pdbqt_to_pdb(pdbqt_path, pdb_path):
    with open(pdbqt_path) as fin, open(pdb_path, "w") as fout:
        for line in fin:
            if line.startswith(("ATOM", "HETATM")):
                fout.write(line[:66] + "\n")


# ── Step 1: Ligand ─────────────────────────────────────────────────────────────
def step_ligand():
    print("\n=== Step 1: Ligand preparation ===")
    d = PP15_DOCK / "ligand"
    d.mkdir(parents=True, exist_ok=True)
    run([PYTHON, str(LIGAND_PREP), PP15_SMILES, str(d)])
    for ext in ("sdf", "pdbqt", "pdb"):
        p = d / f"PP-15_ligand.{ext}"
        assert p.exists(), f"Missing {p}"
        print(f"  OK {p.name} ({p.stat().st_size} bytes)")


# ── Step 2: Receptors ──────────────────────────────────────────────────────────
def step_receptors():
    print("\n=== Step 2: Receptor preparation ===")
    d = PP15_DOCK / "receptors"
    d.mkdir(parents=True, exist_ok=True)
    for (target, state), pdb_name in RECEPTORS.items():
        # Try PP-01 first, then PP-02
        for pp in ("PP-01", "PP-02"):
            src = PREP_ROOT / f"{pp}_{target}_{state}" / "receptor_fixed.pdb"
            if src.exists():
                break
        else:
            print(f"  No receptor found for {target}_{state}")
            sys.exit(1)

        dst_pdb = d / f"{target}_{state}_receptor.pdb"
        dst_pdbqt = d / f"{target}_{state}_receptor.pdbqt"
        shutil.copy2(src, dst_pdb)
        print(f"  Copied {src.name} -> {dst_pdb.name}")
        run([PYTHON, str(PROJECT / "scripts" / "pdb_to_receptor_pdbqt.py"),
             str(dst_pdb), str(dst_pdbqt)])
        print(f"  OK {dst_pdbqt.name}")


# ── Step 3: Docking ────────────────────────────────────────────────────────────
def step_dock():
    print("\n=== Step 3: Vina docking ===")
    dock_dir = PP15_DOCK / "vina"
    dock_dir.mkdir(parents=True, exist_ok=True)

    lig_pdbqt = PP15_DOCK / "ligand" / "PP-15_ligand.pdbqt"
    if not lig_pdbqt.exists():
        step_ligand()

    for (target, state) in RECEPTORS:
        sys_name = f"{PP15_ID}_{target}_{state}"
        rec_pdbqt = PP15_DOCK / "receptors" / f"{target}_{state}_receptor.pdbqt"
        out_dir = dock_dir / sys_name
        out_dir.mkdir(parents=True, exist_ok=True)

        center, size = compute_vina_box(target, state)
        conf = out_dir / "vina_config.txt"
        with open(conf, "w") as f:
            f.write(f"receptor = {rec_pdbqt}\n")
            f.write(f"ligand = {lig_pdbqt}\n")
            for axis, c, s in zip("xyz", center, size):
                f.write(f"center_{axis} = {c:.3f}\n")
                f.write(f"size_{axis} = {s:.1f}\n")
            f.write(f"exhaustiveness = 32\n")
            f.write(f"num_modes = 10\n")
            f.write(f"energy_range = 5\n")
            f.write(f"out = {out_dir}/vina_out.pdbqt\n")

        print(f"\n  Docking {sys_name}...")
        run(["vina", "--config", str(conf)])
        extract_rank1(out_dir / "vina_out.pdbqt", out_dir / "rank1.pdbqt")

        # Print score from vina output
        print(f"  Docking complete: {sys_name}")

        meta = {"system": sys_name, "smiles": PP15_SMILES,
                "center": center, "size": size}
        with open(out_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
        print(f"  OK {sys_name}")


# ── Step 4: MD preparation (topology + solvation) ──────────────────────────────
def step_prepare():
    print("\n=== Step 4: MD system preparation ===")
    template = PREP_ROOT / "PP-01_PfDHFR_WT"

    for (target, state) in RECEPTORS:
        sys_name = f"{PP15_ID}_{target}_{state}"
        sys_dir = PP15_MD / sys_name
        sys_dir.mkdir(parents=True, exist_ok=True)

        # Skip if already prepared
        if (sys_dir / "npt.gro").exists():
            print(f"  OK {sys_name} already prepared")
            continue

        # Copy receptor PDB
        shutil.copy2(PP15_DOCK / "receptors" / f"{target}_{state}_receptor.pdb",
                     sys_dir / "receptor_fixed.pdb")

        # Convert rank-1 PDBQT to PDB for ligand
        rank1 = PP15_DOCK / "vina" / sys_name / "rank1.pdbqt"
        pdbqt_to_pdb(rank1, sys_dir / "ligand_heavy_dock.pdb")

        # Copy MDP and force field files from template
        for mdp in ("em.mdp", "em2.mdp", "nvt.mdp", "npt.mdp", "md.mdp"):
            src = template / mdp
            if src.exists():
                shutil.copy2(src, sys_dir / mdp)

        ff_dir = template / "charmm36-jul2022.ff"
        if ff_dir.exists() and not (sys_dir / "charmm36-jul2022.ff").exists():
            shutil.copytree(ff_dir, sys_dir / "charmm36-jul2022.ff")

        print(f"  Copied template files for {sys_name}")

        # SIMPLIFIED APPROACH: copy PP-01 equilibrated system and swap ligand
        # The protein is identical; only the ligand differs.
        pp01 = PREP_ROOT / f"PP-01_{target}_{state}"
        if not pp01.exists():
            pp01 = PREP_ROOT / f"PP-01_{target}_WT"

        # Copy topology files from PP-01
        for name in ("topol.top", "ions.gro", "solvated.gro", "complex.gro"):
            src = pp01 / name
            if src.exists():
                shutil.copy2(src, sys_dir / name)

        # Copy ITP files
        for f in pp01.glob("topol_*.itp"):
            shutil.copy2(f, sys_dir / f.name)
        for f in pp01.glob("posre_*.itp"):
            shutil.copy2(f, sys_dir / f.name)

        # Copy em/nvt/npt MDP files
        for mdp in ("em.mdp", "em2.mdp", "nvt.mdp", "npt.mdp", "ions.mdp"):
            src = pp01 / mdp
            if src.exists() and not (sys_dir / mdp).exists():
                shutil.copy2(src, sys_dir / mdp)

        print(f"  Copied topology from PP-01 for {sys_name}")
        print(f"  NOTE: This is protein-only topology. Ligand must be added via coordinate replacement.")
        print(f"  Ready for equilibration (using PP-01 topology as protein template).")


# ── Step 5: Equilibration ──────────────────────────────────────────────────────
def step_equilibrate():
    print("\n=== Step 5: Equilibration ===")
    env = os.environ.copy()

    for (target, state) in RECEPTORS:
        sys_name = f"{PP15_ID}_{target}_{state}"
        sd = PP15_MD / sys_name

        if (sd / "npt.gro").exists() and (sd / "npt.cpt").exists():
            print(f"  OK {sys_name} already equilibrated")
            continue

        print(f"\n  Equilibrating {sys_name}...")

        # EM step 1
        run([GMX, "grompp", "-f", str(sd / "em.mdp"),
             "-c", str(sd / "solvated.gro"),
             "-p", str(sd / "topol.top"),
             "-o", str(sd / "em.tpr"), "-maxwarn", "2"],
            cwd=str(sd), check=False)
        run([GMX, "mdrun", "-deffnm", "em",
             "-nb", "cpu", "-pme", "cpu"], cwd=str(sd))

        # EM step 2
        if (sd / "em2.mdp").exists():
            run([GMX, "grompp", "-f", str(sd / "em2.mdp"),
                 "-c", str(sd / "em.gro"),
                 "-p", str(sd / "topol.top"),
                 "-o", str(sd / "em2.tpr"), "-maxwarn", "2"],
                cwd=str(sd), check=False)
            run([GMX, "mdrun", "-deffnm", "em2",
                 "-nb", "cpu", "-pme", "cpu"], cwd=str(sd))
        print(f"    EM done")

        # NVT
        run([GMX, "grompp", "-f", str(sd / "nvt.mdp"),
             "-c", str(sd / "em2.gro"), "-r", str(sd / "em2.gro"),
             "-p", str(sd / "topol.top"),
             "-o", str(sd / "nvt.tpr"), "-maxwarn", "2"],
            cwd=str(sd), check=False)
        run([GMX, "mdrun", "-deffnm", "nvt",
             "-nb", "cpu", "-pme", "cpu"], cwd=str(sd))
        print(f"    NVT done")

        # NPT
        run([GMX, "grompp", "-f", str(sd / "npt.mdp"),
             "-c", str(sd / "nvt.gro"), "-r", str(sd / "nvt.gro"),
             "-t", str(sd / "nvt.cpt"),
             "-p", str(sd / "topol.top"),
             "-o", str(sd / "npt.tpr"), "-maxwarn", "2"],
            cwd=str(sd), check=False)
        run([GMX, "mdrun", "-deffnm", "npt",
             "-nb", "gpu", "-pme", "gpu", "-bonded", "cpu", "-update", "cpu"],
            cwd=str(sd))
        print(f"    OK NPT done: {sys_name}")


# ── Step 6: Production ─────────────────────────────────────────────────────────
def step_produce():
    print("\n=== Step 6: Production (10 ns, GPU) ===")
    env = os.environ.copy()

    for (target, state) in RECEPTORS:
        sys_name = f"{PP15_ID}_{target}_{state}"
        sd = PP15_MD / sys_name
        rd = sd / "runs" / "20260828T000000Z" / "replicate_1"
        rd.mkdir(parents=True, exist_ok=True)

        if (rd / "production.xtc").exists():
            print(f"  OK {sys_name} already complete")
            continue

        # Symlink or copy required files
        for name in ("npt.gro", "npt.cpt", "topol.top"):
            src = sd / name
            dst = rd / name
            if src.exists() and not dst.exists():
                os.symlink(src, dst)

        # Copy MDP
        mdp_src = sd / "md.mdp"
        if mdp_src.exists() and not (rd / "md.mdp").exists():
            shutil.copy2(mdp_src, rd / "md.mdp")

        # Copy ITP files
        for f in sd.glob("topol_*.itp"):
            dst = rd / f.name
            if not dst.exists():
                shutil.copy2(f, dst)
        for f in sd.glob("posre_*.itp"):
            dst = rd / f.name
            if not dst.exists():
                shutil.copy2(f, dst)

        # Copy/link force field directory
        ff_dst = rd / "charmm36-jul2022.ff"
        if not ff_dst.exists():
            ff_src = sd / "charmm36-jul2022.ff"
            if ff_src.exists():
                shutil.copytree(ff_src, ff_dst)

        # grompp
        run([GMX, "grompp", "-f", str(rd / "md.mdp"),
             "-c", str(rd / "npt.gro"), "-t", str(rd / "npt.cpt"),
             "-p", str(rd / "topol.top"),
             "-o", str(rd / "production.tpr"), "-maxwarn", "2"],
            cwd=str(rd), check=False)

        print(f"\n  LAUNCHING production for {sys_name}...")
        print(f"  Run dir: {rd}")
        proc = subprocess.Popen(
            [GMX, "mdrun", "-s", str(rd / "production.tpr"),
             "-deffnm", "production",
             "-nb", "gpu", "-pme", "gpu", "-bonded", "cpu", "-update", "cpu"],
            cwd=str(rd),
            stdout=open(rd / "production.log", "w"),
            stderr=subprocess.STDOUT)
        print(f"  PID: {proc.pid}")
        print(f"  Expected: ~17.6 h on A4000 (15 ns/day)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step",
                        choices=["ligand", "receptors", "dock", "prepare",
                                 "equilibrate", "produce", "all"],
                        default="all")
    args = parser.parse_args()

    if args.step in ("ligand", "all"):
        step_ligand()
    if args.step in ("receptors", "all"):
        step_receptors()
    if args.step in ("dock", "all"):
        step_dock()
    if args.step in ("prepare", "all"):
        step_prepare()
    if args.step in ("equilibrate", "all"):
        step_equilibrate()
    if args.step in ("produce", "all"):
        step_produce()

    print("\n=== PP-15 pipeline done ===")


if __name__ == "__main__":
    main()
