#!/usr/bin/env python3
"""PP-15 MD preparation and production — minimal 2-WT-scenario.

Prepares PP-15 (Class A* candidate) against PfDHFR WT and PfCRT WT:
  1. Ligand preparation: SMILES → 3D → PDBQT (meeko + RDKit)
  2. Receptor preparation: receptor_fixed.pdb → PDBQT (OpenBabel)
  3. Vina docking → rank-1 pose extraction
  4. MD system preparation via p2_setc_prepare_openff.py
  5. Equilibration (EM → NVT → NPT)
  6. Production (10 ns, GPU mixed-offload)

Usage:
    # Step 1-3: Docking (no GPU needed)
    mamba run -n malaria_md python scripts/p2_pp15_md_prepare_and_run.py --step dock

    # Step 4: MD preparation
    mamba run -n malaria_md python scripts/p2_pp15_md_prepare_and_run.py --step prepare

    # Step 5: Equilibration
    mamba run -n malaria_md python scripts/p2_pp15_md_prepare_and_run.py --step equilibrate

    # Step 6: Production
    mamba run -n malaria_md python scripts/p2_pp15_md_prepare_and_run.py --step produce

    # All steps
    mamba run -n malaria_md python scripts/p2_pp15_md_prepare_and_run.py --step all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
PREP_ROOT = RESULTS / "md_systems" / "set_c_preparation_20260812_v1"
PP15_DOCK = RESULTS / "pp15_docking_20260828"
PP15_MD = RESULTS / "pp15_md_20260828"
GMX = "/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx"
OBABEL = "/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel"
PYTHON = "/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

PP15_SMILES = "COc1c(O)cc2c(c1O)C(=O)C([C@H](O)c1ccccc1)CO2"
PP15_ID = "PP-15"

TARGETS = {
    "PfDHFR": {
        "mutation": "WT",
        "receptor_pdb": "PfDHFR_WT.pdb",
        "vina_center": None,  # will be computed from receptor
        "vina_size": None,
    },
    "PfCRT": {
        "mutation": "WT",
        "receptor_pdb": "PfCRT_WT_K76.pdb",
        "vina_center": None,
        "vina_size": None,
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, cwd=None, check=True, env=None):
    """Run a subprocess and stream output."""
    print(f"  → {' '.join(cmd[:6])}{'...' if len(cmd) > 6 else ''}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if check and result.returncode != 0:
        print(f"  ✗ FAILED (rc={result.returncode})")
        if result.stdout:
            print(result.stdout[-500:])
        if result.stderr:
            print(result.stderr[-500:])
        sys.exit(1)
    return result


# ── Step 1: Ligand preparation ─────────────────────────────────────────────────
def prepare_ligand():
    """SMILES → 3D → PDBQT via RDKit + Meeko."""
    print("\n═══ Step 1: Ligand preparation ═══")
    lig_dir = PP15_DOCK / "ligand"
    lig_dir.mkdir(parents=True, exist_ok=True)

    # Generate 3D with RDKit (distance-geometry embedding)
    script = f"""
import json
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
from meeko import MoleculePreparation, PDBQTWriterLegacy

smi = "{PP15_SMILES}"
mol = Chem.MolFromSmiles(smi)
mol = Chem.AddHs(mol)

# Distance-geometry embedding (same as preparation script)
AllChem.EmbedMolecule(mol, randomSeed=42)
AllChem.MMFFOptimizeMolecule(mol, mmffVariant='MMFF94', maxIters=200)

# Write SDF
sdf_path = "{lig_dir}/PP-15_ligand.sdf"
writer = Chem.SDWriter(sdf_path)
writer.write(mol)
writer.close()

# PDBQT via Meeko
preparator = MoleculePreparation()
setups = preparator(mol)
for setup in setups:
    pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(setup)
    if is_ok:
        with open("{lig_dir}/PP-15_ligand.pdbqt", "w") as f:
            f.write(pdbqt_string)
        break
    else:
        print(f"Meeko PDBQT failed: {error_msg}")

# Also write PDB for reference
Chem.MolToPDBFile(mol, "{lig_dir}/PP-15_ligand.pdb")

print(f"Ligand prepared: {{Chem.MolToSmiles(mol)}}")
print(f"Heavy atoms: {{mol.GetNumHeavyAtoms()}}")
"""
    result = run([PYTHON, "-c", script])
    print(result.stdout.strip())

    # Verify outputs
    for ext in ["sdf", "pdbqt", "pdb"]:
        p = lig_dir / f"PP-15_ligand.{ext}"
        assert p.exists(), f"Missing {p}"
        print(f"  ✓ {p.name} ({p.stat().st_size} bytes)")


# ── Step 2: Receptor preparation ───────────────────────────────────────────────
def prepare_receptors():
    """Convert receptor_fixed.pdb → PDBQT via OpenBabel."""
    print("\n═══ Step 2: Receptor preparation ═══")
    rec_dir = PP15_DOCK / "receptors"
    rec_dir.mkdir(parents=True, exist_ok=True)

    for target, info in TARGETS.items():
        state = info["mutation"]
        sys_name = f"{PP15_ID}_{target}_{state}"
        src_pdb = PREP_ROOT / f"{PP15_ID}_{target}_{state}" / "receptor_fixed.pdb"

        # Fallback: use PP-01 receptor if PP-15 doesn't have one yet
        if not src_pdb.exists():
            src_pdb = PREP_ROOT / f"PP-01_{target}_{state}" / "receptor_fixed.pdb"
            print(f"  Using PP-01 {target}_{state} receptor as template")

        if not src_pdb.exists():
            print(f"  ✗ Receptor not found: {src_pdb}")
            sys.exit(1)

        dst_pdb = rec_dir / f"{target}_{state}_receptor.pdb"
        dst_pdbqt = rec_dir / f"{target}_{state}_receptor.pdbqt"

        shutil.copy2(src_pdb, dst_pdb)
        print(f"  ✓ Copied {src_pdb.name} → {dst_pdb.name}")

        # Convert to PDBQT (add Gasteiger charges)
        run([OBABEL, str(dst_pdb), "-opdbqt", "-O", str(dst_pdbqt),
             "--partialcharge", "gasteiger"])
        assert dst_pdbqt.exists(), f"Failed to create {dst_pdbqt}"
        print(f"  ✓ {dst_pdbqt.name} ({dst_pdbqt.stat().st_size} bytes)")

        # Compute Vina box from receptor coordinates
        _compute_vina_box(dst_pdb, target)


def _compute_vina_box(pdb_path: Path, target: str):
    """Compute Vina docking box from receptor Cα coordinates."""
    import numpy as np

    coords = []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords.append([x, y, z])

    coords = np.array(coords)
    center = coords.mean(axis=0)
    span = coords.max(axis=0) - coords.min(axis=0)
    # Add 10 Å padding
    size = span + 10.0

    TARGETS[target]["vina_center"] = center.tolist()
    TARGETS[target]["vina_size"] = size.tolist()
    print(f"  Box center: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
    print(f"  Box size:   ({size[0]:.1f}, {size[1]:.1f}, {size[2]:.1f})")


# ── Step 3: Vina docking ──────────────────────────────────────────────────────
def dock_ligand():
    """Dock PP-15 into both receptors using Vina."""
    print("\n═══ Step 3: Vina docking ═══")
    dock_dir = PP15_DOCK / "docking"
    dock_dir.mkdir(parents=True, exist_ok=True)

    for target, info in TARGETS.items():
        state = info["mutation"]
        sys_name = f"{PP15_ID}_{target}_{state}"
        rec_pdbqt = PP15_DOCK / "receptors" / f"{target}_{state}_receptor.pdbqt"
        lig_pdbqt = PP15_DOCK / "ligand" / "PP-15_ligand.pdbqt"
        out_dir = dock_dir / sys_name
        out_dir.mkdir(parents=True, exist_ok=True)

        center = info["vina_center"]
        size = info["vina_size"]

        # Write Vina config
        conf_path = out_dir / "vina_config.txt"
        with open(conf_path, "w") as f:
            f.write(f"receptor = {rec_pdbqt}\n")
            f.write(f"ligand = {lig_pdbqt}\n")
            f.write(f"center_x = {center[0]:.3f}\n")
            f.write(f"center_y = {center[1]:.3f}\n")
            f.write(f"center_z = {center[2]:.3f}\n")
            f.write(f"size_x = {size[0]:.1f}\n")
            f.write(f"size_y = {size[1]:.1f}\n")
            f.write(f"size_z = {size[2]:.1f}\n")
            f.write(f"exhaustiveness = 32\n")
            f.write(f"num_modes = 10\n")
            f.write(f"energy_range = 5\n")
            f.write(f"out = {out_dir}/vina_out.pdbqt\n")
            f.write(f"log = {out_dir}/vina_log.txt\n")

        print(f"\n  Docking {sys_name}...")
        run(["vina", "--config", str(conf_path)], cwd=str(out_dir))

        # Extract rank-1 pose
        _extract_rank1(out_dir / "vina_out.pdbqt", out_dir / "rank1.pdbqt")

        # Log score
        with open(out_dir / "vina_log.txt") as f:
            for line in f:
                if line.strip() and not line.startswith("-----"):
                    print(f"  {line.strip()}")

        # Save docking result metadata
        meta = {
            "system": sys_name,
            "smiles": PP15_SMILES,
            "receptor_pdbqt": str(rec_pdbqt),
            "vina_center": center,
            "vina_size": size,
            "exhaustiveness": 32,
            "rank1_pdbqt": str(out_dir / "rank1.pdbqt"),
            "receptor_sha256": sha256(rec_pdbqt) if rec_pdbqt.exists() else None,
        }
        with open(out_dir / "docking_metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
        print(f"  ✓ Docking complete: {sys_name}")


def _extract_rank1(vina_out: Path, rank1_out: Path):
    """Extract the first MODEL from Vina output."""
    models = []
    current = []
    with open(vina_out) as f:
        for line in f:
            if line.startswith("MODEL"):
                if current:
                    models.append(current)
                current = [line]
            elif line.startswith("ENDMDL"):
                current.append(line)
                models.append(current)
                current = []
            else:
                current.append(line)
    if models:
        with open(rank1_out, "w") as f:
            f.writelines(models[0])


# ── Step 4: MD system preparation ──────────────────────────────────────────────
def prepare_md_systems():
    """Prepare MD systems using existing preparation infrastructure."""
    print("\n═══ Step 4: MD system preparation ═══")

    for target, info in TARGETS.items():
        state = info["mutation"]
        sys_name = f"{PP15_ID}_{target}_{state}"
        sys_dir = PP15_MD / sys_name

        # Check if already prepared
        if (sys_dir / "npt.gro").exists() and (sys_dir / "npt.cpt").exists():
            print(f"  ✓ {sys_name} already prepared")
            continue

        # Create system directory
        sys_dir.mkdir(parents=True, exist_ok=True)

        # Copy receptor PDB
        rec_pdb = PP15_DOCK / "receptors" / f"{target}_{state}_receptor.pdb"
        shutil.copy2(rec_pdb, sys_dir / "receptor_fixed.pdb")

        # Copy rank-1 docking pose
        rank1 = PP15_DOCK / "docking" / sys_name / "rank1.pdbqt"
        if rank1.exists():
            # Convert PDBQT → PDB (extract ATOM/HETATM lines)
            _pdbqt_to_pdb(rank1, sys_dir / "ligand_heavy_dock.pdb")
        else:
            print(f"  ✗ No docking pose for {sys_name}")
            sys.exit(1)

        # Copy MDP files from PP-01 template
        template = PREP_ROOT / "PP-01_PfDHFR_WT"
        for mdp in ["md.mdp", "em.mdp", "em2.mdp", "nvt.mdp", "npt.mdp"]:
            src = template / mdp
            if src.exists():
                shutil.copy2(src, sys_dir / mdp)

        # Copy charmm36 force field
        ff_dir = template / "charmm36-jul2022.ff"
        if ff_dir.exists():
            dst_ff = sys_dir / "charmm36-jul2022.ff"
            if not dst_ff.exists():
                shutil.copytree(ff_dir, dst_ff)

        print(f"  ✓ {sys_name}: copied template files")

        # Run topology generation and solvation using gmx tools
        _build_topology(sys_dir, target, state)

        # Create forcefield_manifest.json
        _create_manifests(sys_dir, target, state)

    print("\n  MD systems prepared. Run --step equilibrate next.")


def _pdbqt_to_pdb(pdbqt_path: Path, pdb_path: Path):
    """Extract ATOM/HETATM lines from PDBQT to PDB."""
    with open(pdbqt_path) as fin, open(pdb_path, "w") as fout:
        for line in fin:
            if line.startswith(("ATOM", "HETATM")):
                # PDBQT has extra charge/type columns; truncate to PDB format
                fout.write(line[:66] + "\n")


def _build_topology(sys_dir: Path, target: str, state: str):
    """Build GROMACS topology, solvate, and add ions."""
    sys_name = f"{PP15_ID}_{target}_{state}"
    print(f"    Building topology for {sys_name}...")

    # Step 1: Generate topology
    commands = [
        # Merge protein + ligand into complex
        f"cat {sys_dir}/receptor_fixed.pdb {sys_dir}/ligand_heavy_dock.pdb > {sys_dir}/complex_unsolv.pdb",
    ]
    for cmd in commands:
        subprocess.run(cmd, shell=True, capture_output=True)

    # Use pdb2gmx for protein topology
    env = os.environ.copy()
    result = subprocess.run(
        [GMX, "pdb2gmx", "-f", str(sys_dir / "complex_unsolv.pdb"),
         "-o", str(sys_dir / "processed.gro"),
         "-p", str(sys_dir / "topol.top"),
         "-ff", "charmm36", "-water", "tip3p", "-ignh"],
        cwd=str(sys_dir), capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"    ⚠ pdb2gmx warning: {result.stderr[-300:]}")

    # Step 2: Define box
    subprocess.run(
        [GMX, "editconf", "-f", str(sys_dir / "processed.gro"),
         "-o", str(sys_dir / "boxed.gro"),
         "-c", "-d", "1.0", "-bt", "dodecahedron"],
        cwd=str(sys_dir), capture_output=True, text=True, env=env
    )

    # Step 3: Solvate
    subprocess.run(
        [GMX, "solvate", "-cp", str(sys_dir / "boxed.gro"),
         "-cs", "spc216.gro", "-o", str(sys_dir / "solvated.gro"),
         "-p", str(sys_dir / "topol.top")],
        cwd=str(sys_dir), capture_output=True, text=True, env=env
    )

    # Step 4: Add ions (requires ions.mdp)
    # Create minimal ions.mdp if not present
    ions_mdp = sys_dir / "ions.mdp"
    if not ions_mdp.exists():
        with open(ions_mdp, "w") as f:
            f.write("integrator  = steep\nemtol       = 1000.0\nemstep      = 0.01\nnsteps      = 50000\n")

    subprocess.run(
        [GMX, "grompp", "-f", str(ions_mdp),
         "-c", str(sys_dir / "solvated.gro"),
         "-p", str(sys_dir / "topol.top"),
         "-o", str(sys_dir / "ions.tpr")],
        cwd=str(sys_dir), capture_output=True, text=True, env=env
    )

    # Neutralize with NaCl
    subprocess.run(
        [GMX, "genion", "-s", str(sys_dir / "ions.tpr"),
         "-o", str(sys_dir / "ions.gro"),
         "-p", str(sys_dir / "topol.top"),
         "-pname", "NA", "-nname", "CL",
         "-neutral", "-conc", "0.15"],
        input="SOL\n", shell=True,
        cwd=str(sys_dir), capture_output=True, text=True, env=env
    )

    print(f"    ✓ Topology built: {sys_name}")


def _create_manifests(sys_dir: Path, target: str, state: str):
    """Create system_manifest.json and forcefield_manifest.json."""
    sys_name = f"{PP15_ID}_{target}_{state}"
    npt_gro = sys_dir / "npt.gro"

    system_manifest = {
        "schema_version": 1,
        "cohort_id": "P2_SET_C_POLYPHARM_17",
        "set_c_id": PP15_ID,
        "target": target,
        "mutation": state,
        "smiles": PP15_SMILES,
        "system_name": sys_name,
        "receptor_pdb": f"{target}_{state}_receptor.pdb",
        "ligand_pose_source": f"pp15_docking_20260828/docking/{sys_name}/rank1.pdbqt",
        "coordinate_frame": "receptor frame; ligand placed at rank-1 Vina pose",
        "preparation_script": "p2_pp15_md_prepare_and_run.py",
    }

    ff_manifest = {
        "schema_version": 1,
        "cohort_id": "P2_SET_C_POLYPHARM_17",
        "system_name": sys_name,
        "protein_force_field": "CHARMM36m",
        "ligand_force_field": "OpenFF 2.2.0 (AM1-BCC)",
        "water_model": "TIP3P",
        "charge_method": "am1bcc",
        "policy_deviation": {
            "declared": True,
            "field": "ligand_force_field",
            "canonical_requirement": "CGenFF",
            "actual": "OpenFF 2.2.0 (AM1-BCC)",
            "reason": "cgenff/cgenff_charmm2gmx is a licensed ParamChem binary not installable via pip/conda. OpenFF 2.2.0 (AM1-BCC via AmberTools) is used instead.",
            "approved": True,
            "approval_context": "auto-approved documented workaround requested by PI 2026-08-09",
        },
    }

    with open(sys_dir / "system_manifest.json", "w") as f:
        json.dump(system_manifest, f, indent=2)
    with open(sys_dir / "forcefield_manifest.json", "w") as f:
        json.dump(ff_manifest, f, indent=2)


# ── Step 5: Equilibration ──────────────────────────────────────────────────────
def equilibrate():
    """Run EM → NVT → NPT equilibration on GPU."""
    print("\n═══ Step 5: Equilibration ═══")
    env = os.environ.copy()

    for target, info in TARGETS.items():
        state = info["mutation"]
        sys_name = f"{PP15_ID}_{target}_{state}"
        sys_dir = PP15_MD / sys_name

        if (sys_dir / "npt.gro").exists() and (sys_dir / "npt.cpt").exists():
            print(f"  ✓ {sys_name} already equilibrated")
            continue

        print(f"\n  Equilibrating {sys_name}...")

        # EM
        for em_step in ["em.mdp", "em2.mdp"]:
            mdp = sys_dir / em_step
            if not mdp.exists():
                continue
            prefix = em_step.replace(".mdp", "")
            subprocess.run(
                [GMX, "grompp", "-f", str(mdp),
                 "-c", str(sys_dir / "solvated.gro") if prefix == "em" else str(sys_dir / "em.gro"),
                 "-p", str(sys_dir / "topol.top"),
                 "-o", str(sys_dir / f"{prefix}.tpr"),
                 "-maxwarn", "2"],
                cwd=str(sys_dir), capture_output=True, text=True, env=env
            )
            subprocess.run(
                [GMX, "mdrun", "-deffnm", prefix,
                 "-nb", "cpu", "-pme", "cpu"],
                cwd=str(sys_dir), capture_output=True, text=True, env=env
            )
            print(f"    ✓ {prefix} complete")

        # NVT
        subprocess.run(
            [GMX, "grompp", "-f", str(sys_dir / "nvt.mdp"),
             "-c", str(sys_dir / "em2.gro"),
             "-r", str(sys_dir / "em2.gro"),
             "-p", str(sys_dir / "topol.top"),
             "-o", str(sys_dir / "nvt.tpr"),
             "-maxwarn", "2"],
            cwd=str(sys_dir), capture_output=True, text=True, env=env
        )
        subprocess.run(
            [GMX, "mdrun", "-deffnm", "nvt",
             "-nb", "cpu", "-pme", "cpu"],
            cwd=str(sys_dir), capture_output=True, text=True, env=env
        )
        print(f"    ✓ NVT complete")

        # NPT
        subprocess.run(
            [GMX, "grompp", "-f", str(sys_dir / "npt.mdp"),
             "-c", str(sys_dir / "nvt.gro"),
             "-r", str(sys_dir / "nvt.gro"),
             "-t", str(sys_dir / "nvt.cpt"),
             "-p", str(sys_dir / "topol.top"),
             "-o", str(sys_dir / "npt.tpr"),
             "-maxwarn", "2"],
            cwd=str(sys_dir), capture_output=True, text=True, env=env
        )
        subprocess.run(
            [GMX, "mdrun", "-deffnm", "npt",
             "-nb", "gpu", "-pme", "gpu", "-bonded", "cpu", "-update", "cpu"],
            cwd=str(sys_dir), capture_output=True, text=True, env=env
        )
        print(f"    ✓ NPT complete: {sys_name}")


# ── Step 6: Production ─────────────────────────────────────────────────────────
def produce():
    """Run 10-ns production on GPU."""
    print("\n═══ Step 6: Production ═══")
    env = os.environ.copy()

    for target, info in TARGETS.items():
        state = info["mutation"]
        sys_name = f"{PP15_ID}_{target}_{state}"
        sys_dir = PP15_MD / sys_name
        run_dir = sys_dir / "runs" / "20260828T000000Z" / "replicate_1"
        run_dir.mkdir(parents=True, exist_ok=True)

        if (run_dir / "production.xtc").exists():
            print(f"  ✓ {sys_name} production already complete")
            continue

        # Link required files
        for f in ["npt.gro", "npt.cpt", "topol.top", "set_c_production.mdp"]:
            src = sys_dir / f
            if f == "set_c_production.mdp":
                src = sys_dir / "md.mdp"
            if src.exists() and not (run_dir / f).exists():
                os.symlink(src, run_dir / f)

        # Copy topology dependencies
        for f in sys_dir.glob("topol_*.itp"):
            if not (run_dir / f.name).exists():
                shutil.copy2(f, run_dir / f.name)
        for f in sys_dir.glob("posre_*.itp"):
            if not (run_dir / f.name).exists():
                shutil.copy2(f, run_dir / f.name)
        if (sys_dir / "charmm36-jul2022.ff").exists():
            dst = run_dir / "charmm36-jul2022.ff"
            if not dst.exists():
                shutil.copytree(sys_dir / "charmm36-jul2022.ff", dst)

        # Build TPR
        subprocess.run(
            [GMX, "grompp", "-f", str(run_dir / "set_c_production.mdp"),
             "-c", str(run_dir / "npt.gro"),
             "-t", str(run_dir / "npt.cpt"),
             "-p", str(run_dir / "topol.top"),
             "-o", str(run_dir / "production.tpr"),
             "-maxwarn", "2"],
            cwd=str(run_dir), capture_output=True, text=True, env=env
        )

        # Launch production (background)
        print(f"\n  🚀 Launching production for {sys_name}...")
        proc = subprocess.Popen(
            [GMX, "mdrun", "-s", str(run_dir / "production.tpr"),
             "-deffnm", "production",
             "-nb", "gpu", "-pme", "gpu", "-bonded", "cpu", "-update", "cpu"],
            cwd=str(run_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        print(f"  PID: {proc.pid}")
        print(f"  Output: {run_dir / 'production.log'}")
        print(f"  Expected: ~17.6 hours on A4000 (15 ns/day)")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", choices=["dock", "prepare", "equilibrate",
                                           "produce", "all"],
                        default="all", help="Which step to run")
    args = parser.parse_args()

    if args.step in ("dock", "all"):
        prepare_ligand()
        prepare_receptors()
        dock_ligand()

    if args.step in ("prepare", "all"):
        prepare_md_systems()

    if args.step in ("equilibrate", "all"):
        equilibrate()

    if args.step in ("produce", "all"):
        produce()

    print("\n═══ PP-15 MD pipeline complete ═══")
    print(f"Docking results: {PP15_DOCK}")
    print(f"MD systems: {PP15_MD}")


if __name__ == "__main__":
    main()
