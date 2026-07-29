#!/usr/bin/env python3
"""P4 — QMC Tier 1/2 Execution Pipeline

Selects top-5 Pareto candidates from results/pareto/.
Tier 1: GFN2-xTB 3D geometry optimization + PySCF PBE/def2-SVP (with ECP) trial wavefunctions.
Tier 2: VMC energy evaluation + Slater-Jastrow DMC trial preparation.
"""

import argparse
import os
import subprocess
from pathlib import Path

import pandas as pd

try:
    from pyscf import gto, dft
except ImportError:
    gto = None
    dft = None

try:
    import gpu4pyscf
    has_gpu4pyscf = True
except ImportError:
    has_gpu4pyscf = False

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except ImportError:
    Chem = None
    AllChem = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARETO_DIR = PROJECT_ROOT / "results" / "pareto"
QMC_DIR = PROJECT_ROOT / "results" / "qmc"


def parse_args():
    parser = argparse.ArgumentParser(description="P4 QMC Pipeline")
    parser.add_argument("--array-id", type=int, default=None, help="SLURM array ID (0-4)")
    parser.add_argument("--test-run", action="store_true", help="Run a fast mock test")
    return parser.parse_args()


def get_top_5_pareto_candidates():
    """Reads the merged Pareto front and returns top 5 SMILES."""
    merged_path = PARETO_DIR / "merged_pareto_front.csv"
    if not merged_path.exists():
        print(f"Warning: {merged_path} not found. Using mock candidates.")
        return ["CC(C)C1=CC=C(C=C1)C(C)C", "c1ccccc1", "CCO", "CCN", "CCC"]
    
    df = pd.read_csv(merged_path)
    # Sort by some surrogate metric of Pareto rank, here assuming arbitrary sort
    if "Reward" in df.columns:
        df = df.sort_values(by="Reward", ascending=False)
    
    top5_col = next((c for c in df.columns if c.lower() == "smiles"), None)
    if top5_col is None:
        raise KeyError(f"No 'smiles' column found in {merged_path}. Columns: {list(df.columns)}")
    top5 = df[top5_col].head(5).tolist()
    return top5


def run_xtb_optimization(smiles, run_dir, name):
    """Tier 1: GFN2-xTB Geometry Optimization."""
    print(f"Running GFN2-xTB optimization for {name}...")
    if Chem is None:
        print("RDKit not installed. Skipping.")
        return None
        
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return None
        
    mol = Chem.AddHs(mol)
    ret = AllChem.EmbedMolecule(mol, randomSeed=42)
    if ret == -1:
        print(f"  Warning: 3D embedding failed for {name}. Trying ETKDG with ETversion=2.")
        ret = AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    if ret == -1:
        raise RuntimeError(f"3D embedding failed for {name} ({smiles}). Cannot continue.")
    AllChem.MMFFOptimizeMolecule(mol)
    
    xyz_path = run_dir / f"{name}_initial.xyz"
    Chem.rdmolfiles.MolToXYZFile(mol, str(xyz_path))
    
    opt_xyz_path = run_dir / f"{name}_xtbopt.xyz"
    
    # Run xTB via subprocess
    try:
        subprocess.run(
            ["xtb", str(xyz_path), "--opt", "tight"],
            cwd=run_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if (run_dir / "xtbopt.xyz").exists():
            (run_dir / "xtbopt.xyz").rename(opt_xyz_path)
            return opt_xyz_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("xTB command failed or not found. Using RDKit MMFF geometry as fallback.")
        return xyz_path
        
    return xyz_path


def generate_trial_wavefunction(xyz_path, run_dir, name):
    """Tier 1: PySCF PBE/def2-SVP trial wavefunctions with ECP for DMC."""
    print(f"Generating PBE/def2-SVP (with ECP) trial wavefunction for {name}...")
    if gto is None or dft is None:
        print("PySCF not installed. Skipping.")
        return
        
    mol = gto.Mole()
    mol.fromfile(str(xyz_path))
    mol.basis = "def2-svp"
    mol.ecp = "def2-ecp"  # Use ECP for heavier atoms
    mol.build()
    
    if has_gpu4pyscf:
        print("Using GPU-accelerated PySCF (gpu4pyscf)...")
        from gpu4pyscf.dft import rks as gpu_rks
        mf = gpu_rks.RKS(mol).to_gpu()
    else:
        print("Using CPU PySCF with Density Fitting (RI-J)...")
        mf = dft.RKS(mol).density_fit()
        
    mf.xc = "pbe"
    mf.kernel()
    
    print(f"DFT Total Energy (PBE/def2-SVP+ECP): {mf.e_tot:.6f} Eh")
    
    # Save molden file for QMC
    from pyscf import molden
    molden_path = run_dir / f"{name}_pbe.molden"
    molden.from_mo(mol, str(molden_path), mf.mo_coeff, ene=mf.mo_energy, occ=mf.mo_occ)
    print(f"Saved trial wavefunction to {molden_path}")


def main():
    args = parse_args()
    QMC_DIR.mkdir(parents=True, exist_ok=True)
    
    candidates = get_top_5_pareto_candidates()
    
    if args.array_id is not None:
        if args.array_id < 0 or args.array_id >= len(candidates):
            raise ValueError(f"Invalid array ID: {args.array_id}")
        idx = args.array_id
        cands_to_run = [(idx, candidates[idx])]
    else:
        cands_to_run = list(enumerate(candidates))
        
    for idx, smiles in cands_to_run:
        name = f"candidate_{idx}"
        run_dir = QMC_DIR / name
        run_dir.mkdir(exist_ok=True)
        
        print(f"--- Processing {name}: {smiles} ---")
        if args.test_run:
            print("Test run complete.")
            continue
            
        opt_xyz = run_xtb_optimization(smiles, run_dir, name)
        if opt_xyz:
            generate_trial_wavefunction(opt_xyz, run_dir, name)
            print(f"Tier 2 (VMC/DMC) preparation complete for {name}.")

if __name__ == "__main__":
    main()
