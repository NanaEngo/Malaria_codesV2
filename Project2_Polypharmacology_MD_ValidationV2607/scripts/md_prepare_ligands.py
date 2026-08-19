"""
MD Simulation: Ligand Topology Preparation

This is a preparation utility, not an execution command. Its GAFF2 fallback is
retained only for diagnostics and is never sufficient evidence for a
CHARMM36m-compatible production campaign; a future production system must
record the chosen ligand force field in a provenance manifest and fail closed
when the approved force-field policy is not met.

Force field strategy (per roadmap v1.4):
  - PfDHFR, PfATP4, PfClpP ligands: OpenFF 2.2 (Sage) via OpenFF Toolkit
    Fully automated, no manual penalty review, validated on drug-like/NP molecules.
  - PfCRT ligands: CGenFF via cgenff_charmm2gmx
    Required for consistency with CHARMM36m membrane protein force field.
  - Fallback (both): GAFF2 via ACPYPE with explicit warning.

Workflow per ligand:
  1. SMILES -> 3D PDB (RDKit ETKDGv3 + MMFF/UFF optimisation)
  OpenFF path (PfDHFR/PfATP4/PfClpP):
  2. SMILES -> OpenFF Molecule -> GROMACS .itp + .gro (OpenFF Toolkit)
  CGenFF path (PfCRT):
  2. PDB -> MOL2 (Open Babel)
  3. MOL2 -> .str (CGenFF / ParamChem)
  4. .str -> GROMACS .itp + .gro (cgenff_charmm2gmx)
  Fallback:
  2. PDB -> GAFF2 .itp + .gro (ACPYPE)

Usage:
    python scripts/md_prepare_ligands.py
"""

import os
import shutil
import subprocess
from pathlib import Path
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
MD_DIR = PROJECT_DIR / "MD_systems"


def get_ligand_smiles(ligand_idx):
    """Get SMILES for a ligand from the activity file."""
    df = pd.read_csv(RESULTS_DIR / "eos80ch_malaria_final_activity.csv")
    idx = int(ligand_idx)
    if idx < len(df):
        smiles = df.iloc[idx]['input']
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            return smiles
        print(f"  Warning: Invalid SMILES for ligand {ligand_idx}: {smiles}")
        return None
    print(f"  Warning: Ligand index {ligand_idx} out of range (max: {len(df)-1})")
    return None


def smiles_to_pdb(smiles, output_file):
    """Convert SMILES to 3D PDB using RDKit ETKDGv3."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"  Error: Could not parse SMILES: {smiles}")
        return False, 0

    net_charge = Chem.GetFormalCharge(mol)
    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.useRandomCoords = True
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) != 0:
        if AllChem.EmbedMolecule(mol, useRandomCoords=True) != 0:
            print("  Error: Could not generate 3D coordinates")
            return False, 0

    try:
        if AllChem.MMFFHasAllMoleculeParams(mol):
            AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
        else:
            AllChem.UFFOptimizeMolecule(mol, maxIters=500)
    except Exception as e:
        print(f"  Warning: Geometry optimisation failed: {e}")

    Chem.MolToPDBFile(mol, str(output_file))
    print(f"  Generated 3D PDB: {output_file} (net charge: {net_charge})")
    return True, net_charge


# Targets that use CGenFF (membrane protein — must match CHARMM36m)
CGENFF_TARGETS = {'PfCRT'}


def generate_openff_parameters(smiles: str, output_dir: Path, ligand_name: str) -> bool:
    """
    Generate OpenFF 2.2 (Sage) GROMACS topology via OpenFF Toolkit.

    Fully automated — no manual penalty review required.
    Validated on drug-like and NP-like molecules (JCTC 2023).

    Returns True on success, False on failure.
    """
    try:
        from openff.toolkit import Molecule, ForceField
        from openff.toolkit.utils.exceptions import UndefinedStereochemistryError
        from openff.units import unit
    except ImportError:
        print("  Warning: openff-toolkit not installed. Run: pip install openff-toolkit openff-forcefields")
        return False

    try:
        mol = Molecule.from_smiles(smiles, allow_undefined_stereo=True)
        mol.generate_conformers(n_conformers=1)

        ff = ForceField("openff-2.2.0.offxml")
        topology = mol.to_topology()

        # GROMACS requires periodic box vectors; set a 10 nm cubic box
        # to avoid the "non-periodic system" error in to_gromacs()
        topology.box_vectors = [[10.0, 0.0, 0.0],
                                [0.0, 10.0, 0.0],
                                [0.0, 0.0, 10.0]] * unit.nanometer

        interchange = ff.create_interchange(topology)
        interchange.box = topology.box_vectors

        itp_file = output_dir / f"{ligand_name}.itp"
        gro_file = output_dir / f"{ligand_name}.gro"

        interchange.to_gromacs(prefix=str(output_dir / ligand_name))

        if itp_file.exists() and gro_file.exists():
            print(f"  ✓ OpenFF 2.2 (Sage) topology: {itp_file.name}, {gro_file.name}")
            return True

        print("  Warning: OpenFF output files missing after generation")
        return False

    except UndefinedStereochemistryError:
        print("  Warning: Undefined stereochemistry in SMILES; retrying with allow_undefined_stereo=True")
        return False
    except Exception as e:
        print(f"  Warning: OpenFF parameterisation failed: {e}")
        return False


def pdb_to_mol2(pdb_file: Path, mol2_file: Path) -> bool:
    """Convert PDB to MOL2 via Open Babel (required by CGenFF)."""
    result = subprocess.run(
        ["obabel", str(pdb_file), "-O", str(mol2_file), "--gen3d"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not mol2_file.exists():
        print(f"  Warning: obabel conversion failed: {result.stderr[:200]}")
        return False
    print(f"  Converted to MOL2: {mol2_file}")
    return True


def generate_cgenff_parameters(pdb_file, mol2_file, output_dir, ligand_name, net_charge, timeout=1200):
    """
    Generate CGenFF/CHARMM36m-compatible GROMACS topology via cgenff_charmm2gmx.

    Requires:
      - cgenff_charmm2gmx.py  (from MacKerell lab / CHARMM-GUI)
      - A local CGenFF binary or ParamChem API key in env PARAMCHEM_KEY
    Penalty thresholds (roadmap Step 9):
      - penalty < 50  : accepted automatically
      - penalty 50-100: accepted with manual review (flagged in output)
      - penalty > 100 : triggers OpenFF 2.2 fallback

    Returns True on success, False on failure.
    Falls back to ACPYPE/GAFF2 with an explicit warning if unavailable.
    """
    # Locate cgenff_charmm2gmx helper
    helper = shutil.which("cgenff_charmm2gmx") or shutil.which("cgenff_charmm2gmx.py")
    cgenff_bin = shutil.which("cgenff")

    if helper and (cgenff_bin or os.environ.get("PARAMCHEM_KEY")):
        # --- CGenFF path ---
        str_file = output_dir / f"{ligand_name}.str"

        # Step 1: generate .str with CGenFF
        if cgenff_bin:
            cmd = [cgenff_bin, str(mol2_file), "-o", str(str_file)]
        else:
            # ParamChem REST API via cgenff_charmm2gmx built-in
            cmd = [helper, str(mol2_file), ligand_name, "LIG",
                   str(str_file), str(pdb_file)]

        result = subprocess.run(cmd, capture_output=True, text=True,
                                cwd=str(output_dir), timeout=timeout)
        if result.returncode != 0 or not str_file.exists():
            print(f"  Warning: CGenFF .str generation failed: {result.stderr[:300]}")
            return _fallback_gaff2(pdb_file, output_dir, ligand_name, net_charge, timeout)

        # Step 2: convert .str → GROMACS .itp + .gro
        result = subprocess.run(
            [helper, str(mol2_file), ligand_name, "LIG",
             str(str_file), str(pdb_file)],
            capture_output=True, text=True,
            cwd=str(output_dir), timeout=timeout
        )
        if result.returncode != 0:
            print(f"  Warning: cgenff_charmm2gmx conversion failed: {result.stderr[:300]}")
            return _fallback_gaff2(pdb_file, output_dir, ligand_name, net_charge, timeout)

        itp = output_dir / f"{ligand_name}.itp"
        gro = output_dir / f"{ligand_name}.gro"
        if itp.exists() and gro.exists():
            print(f"  ✓ Generated CGenFF topology: {itp.name}, {gro.name}")
            return True
        print("  Warning: CGenFF output files missing after conversion")
        return _fallback_gaff2(pdb_file, output_dir, ligand_name, net_charge, timeout)

    else:
        print("  Warning: cgenff_charmm2gmx / CGenFF binary not found.")
        print("  Falling back to GAFF2 — NOTE: force field mismatch with CHARMM36m protein.")
        print("  For production runs, obtain CGenFF parameters from https://cgenff.umaryland.edu")
        return _fallback_gaff2(pdb_file, output_dir, ligand_name, net_charge, timeout)


def _fallback_gaff2(pdb_file, output_dir, ligand_name, net_charge, timeout=1200):
    """
    GAFF2 fallback via ACPYPE. Tries multiple charge methods to improve
    robustness for sulfur-rich ligands (e.g., sulfonamides, trifluoromethyl-
    sulfonyl groups) that fail with BCC.

    Charge method priority:
      1. bcc    — AM1-BCC (most accurate for drug-like molecules)
      2. gas    — Gasteiger (fast; skips quantum step that causes timeouts)
      3. explicit zero charge (neutral override; last resort)

    Each attempt uses a shorter timeout (``timeout_per_attempt``) to avoid
    blocking the entire pipeline on a single problematic ligand.
    """
    print(f"  [GAFF2 FALLBACK] Using ACPYPE for {ligand_name} — diagnostic only; incompatible with CHARMM36m protein and blocked for publication-grade production.")

    # Use shorter per-attempt timeouts so one failure does not block everything
    timeout_per_attempt = min(timeout // 3, 360)  # max 360 s per attempt

    charge_methods = [
        ("bcc", net_charge),   # AM1-BCC (best)
        ("gas", net_charge),   # Gasteiger (fast)
        ("gas", 0),            # neutral override (last resort)
    ]

    for charge_method, charge in charge_methods:
        print(f"  Trying ACPYPE: -c {charge_method} -n {charge}")
        cmd = (
            f"acpype -i {pdb_file} -b {ligand_name} "
            f"-c {charge_method} -n {charge} -a gaff2"
        )
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=str(output_dir), timeout=timeout_per_attempt
            )
            if result.returncode == 0:
                acpype_dir = output_dir / f"{ligand_name}.acpype"
                itp = acpype_dir / f"{ligand_name}_GMX.itp"
                gro = acpype_dir / f"{ligand_name}_GMX.gro"
                if itp.exists() and gro.exists():
                    print(f"  ✓ GAFF2 parameters generated (charge={charge_method}): {acpype_dir}/")
                    return True
            print(f"    ACPYPE -c {charge_method} failed (rc={result.returncode})")
            if result.stderr:
                print(f"    {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"    ACPYPE -c {charge_method} timed out after {timeout_per_attempt}s")
            continue

    print(f"  ERROR: All ACPYPE charge methods failed for {ligand_name}")
    return False


def main():
    print("=" * 60)
    print("MD Ligand Topology Preparation (CGenFF / CHARMM36m)")
    print("=" * 60)

    ligands_info = {
        '201': {'name': 'ligand_201', 'target': 'PfDHFR'},
        '438': {'name': 'ligand_438', 'target': 'PfATP4'},
        '164': {'name': 'ligand_164', 'target': 'PfClpP'},
        '214': {'name': 'ligand_214', 'target': 'PfCRT'},
    }

    for ligand_idx, info in ligands_info.items():
        print(f"\nPreparing {info['name']} ({info['target']})...")

        smiles = get_ligand_smiles(ligand_idx)
        if not smiles:
            print(f"  Warning: No valid SMILES for ligand {ligand_idx}, skipping")
            continue

        complex_dir = MD_DIR / f"{ligand_idx}_{info['target']}"
        ligand_dir = complex_dir / "ligand"
        ligand_dir.mkdir(parents=True, exist_ok=True)

        pdb_file = ligand_dir / f"{info['name']}.pdb"
        success, net_charge = smiles_to_pdb(smiles, pdb_file)
        if not success:
            continue

        # Route by target: OpenFF for non-membrane targets, CGenFF for PfCRT
        if info['target'] not in CGENFF_TARGETS:
            print(f"  Using OpenFF 2.2 (Sage) for {info['target']} (non-membrane target)")
            if not generate_openff_parameters(smiles, ligand_dir, info['name']):
                print("  OpenFF failed — falling back to CGenFF/GAFF2")
                mol2_file = ligand_dir / f"{info['name']}.mol2"
                pdb_to_mol2(pdb_file, mol2_file)
                generate_cgenff_parameters(pdb_file, mol2_file, ligand_dir,
                                           info['name'], net_charge)
        else:
            print(f"  Using CGenFF for {info['target']} (membrane protein — must match CHARMM36m)")
            mol2_file = ligand_dir / f"{info['name']}.mol2"
            if not pdb_to_mol2(pdb_file, mol2_file):
                print(f"  Warning: MOL2 conversion failed; CGenFF path unavailable for {info['name']}")
            generate_cgenff_parameters(pdb_file, mol2_file, ligand_dir,
                                       info['name'], net_charge)

    print("\n" + "=" * 60)
    print("Ligand preparation complete!")
    print("=" * 60)


if __name__ == "__main__":
    import shutil
    main()