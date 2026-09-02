"""
P7 — Data Preparation Script

Extract and prepare datasets for P7 quantum molecular encoding project:
  - P1 Set A: 20 top candidates from P1 V7
  - P3 Benchmark: 19,849 molecules with activity labels
  - External validation: Sample from 122K asexual dataset

Outputs:
  - data/p1_set_a_20_candidates.csv
  - data/p3_benchmark_19849.csv
  - data/external_sample_10k.csv
  - data/provenance/data_manifest.json

Usage:
    python scripts/p7_data_preparation.py --all
    python scripts/p7_data_preparation.py --p1-only
    python scripts/p7_data_preparation.py --p3-only
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROVENANCE_DIR = DATA_DIR / "provenance"

# Source data paths (relative to workspace root)
WORKSPACE_ROOT = PROJECT_ROOT.parent
P1_V7_ROOT = WORKSPACE_ROOT / "Project1_Chem_space_antimalarial_V7_CorrectedGrid"
P3_ROOT = WORKSPACE_ROOT / "Project3_Quantum_Inspired_RepresentationsV2607"
QMSE_DATA = WORKSPACE_ROOT / "Quantum_malaria_codes " / "Dataset_paper"


def canonicalize_smiles(smiles: str) -> str:
    """Canonicalize SMILES string using RDKit."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def smiles_to_qmse_bond_order(smiles: str, add_hydrogens: bool = False) -> np.ndarray:
    """
    Convert SMILES to QMSE BondOrderMatrix.
    
    This is the quantum molecular encoding approach where molecular structure
    is directly encoded into a matrix suitable for quantum circuits.
    
    Args:
        smiles: SMILES string
        add_hydrogens: Whether to add explicit hydrogens (default: False)
    
    Returns:
        (n_atoms, n_atoms) BondOrderMatrix
        - Diagonal: atomic charges (Z values)
        - Off-diagonal: bond_order × (Z_i × Z_j)
    """
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from qmse_lib import BondOrderMatrix
    
    encoder = BondOrderMatrix()
    matrix = encoder.compute(smiles, add_hydrogens=add_hydrogens)
    return matrix


def smiles_to_qmse_coulomb(smiles: str, add_hydrogens: bool = False) -> np.ndarray:
    """
    Convert SMILES to QMSE CoulombMatrix.
    
    Requires 3D conformer generation.
    
    Args:
        smiles: SMILES string
        add_hydrogens: Whether to add explicit hydrogens (default: False)
    
    Returns:
        (n_atoms, n_atoms) CoulombMatrix
        - Diagonal: 0.5 × Z^2.4 (atomic self-energy)
        - Off-diagonal: (Z_i × Z_j) / distance
    """
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from qmse_lib import CoulombMatrix
    
    encoder = CoulombMatrix()
    matrix = encoder.compute(smiles, add_hydrogens=add_hydrogens)
    return matrix


def extract_p1_set_a() -> pd.DataFrame:
    """
    Extract P1 Set A: Candidates from P1 V7 (P2 Set C polypharmacology cohort).
    
    Source: Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/v7_candidate_manifest.csv
    Cohort: P2 Set C (17 molecules, polypharmacology candidates)
    Labels: Binary classification based on MD-RRS retention (PP-01/PP-02 as binders)
    
    Note: P1 V7 manuscript is computational; activity labels are synthetic for PoC
    
    Returns:
        DataFrame with columns: [molecule_id, smiles, canonical_smiles, activity, ...]
    """
    print("\n=== Extracting P1 Set A (20 candidates) ===")
    
    # Check for P1 V7 candidate manifest
    p1_manifest = P1_V7_ROOT / "results" / "v7_candidate_manifest.csv"
    
    if not p1_manifest.exists():
        print(f"ERROR: P1 V7 candidate manifest not found at {p1_manifest}")
        print(f"\nSearching for alternative P1 V7 result files...")
        
        # Search for any CSV in results directory
        results_dir = P1_V7_ROOT / "results"
        if results_dir.exists():
            csv_files = list(results_dir.glob("*.csv"))
            if csv_files:
                print(f"Found {len(csv_files)} CSV files in P1 results:")
                for f in csv_files[:10]:
                    print(f"  - {f.name}")
                print(f"\nPlease specify the correct file containing Set A candidates.")
        
        sys.exit(1)
    
    print(f"Reading: {p1_manifest}")
    df = pd.read_csv(p1_manifest)
    
    # Validate and extract all candidates (P1 V7 has 17 molecules in Set C)
    # Handle both 'smiles' and 'canonical_smiles' columns
    if 'canonical_smiles' in df.columns:
        smiles_col = 'canonical_smiles'
    elif 'smiles' in df.columns:
        smiles_col = 'smiles'
    else:
        print(f"ERROR: No SMILES column found in {p1_manifest}")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    print(f"Using SMILES column: {smiles_col}")
    print(f"Total candidates in manifest: {len(df)}")
    
    # P1 V7 manifest doesn't have MPO scores - it has validated candidates
    # Take all candidates (should be 17 from P2 Set C)
    # These are already validated as top candidates
    print(f"Note: Using all {len(df)} candidates from P1 V7 manifest (already filtered)")
    
    # Create synthetic activity labels based on P2 MD-RRS results if available
    # PP-01 and PP-02 are known binders; we'll use docking/MD evidence as proxy
    if 'candidate_id' in df.columns:
        # For proof-of-concept, create binary classification:
        # Binders (1): PP-01, PP-02 (these have strong MD-RRS retention)
        # Non-binders (0): Others (for conservative classification)
        # In reality, all Set C candidates are predicted actives, but we need
        # binary labels for supervised learning
        df['activity'] = df['candidate_id'].apply(
            lambda x: 1 if x in ['PP-01', 'PP-02'] else 0
        )
        print(f"Activity labels: {df['activity'].value_counts().to_dict()}")
        print(f"Note: Labels are based on MD-RRS retention (PP-01/PP-02=binders)")
    else:
        # If no candidate_id, assign random labels for PoC
        print(f"WARNING: No candidate_id column, assigning 50/50 random labels")
        np.random.seed(42)
        df['activity'] = np.random.choice([0, 1], size=len(df))
    
    # Canonicalize SMILES
    if smiles_col == 'canonical_smiles':
        # Already canonical, but re-canonicalize to ensure consistency
        df['canonical_smiles'] = df[smiles_col].apply(canonicalize_smiles)
    else:
        df['canonical_smiles'] = df[smiles_col].apply(canonicalize_smiles)
    
    # Also keep a 'smiles' column for compatibility
    if 'smiles' not in df.columns:
        df['smiles'] = df['canonical_smiles']
    
    # Remove failed canonicalizations
    failed = df['canonical_smiles'].isna().sum()
    if failed > 0:
        print(f"WARNING: {failed} molecules failed SMILES canonicalization")
        df = df.dropna(subset=['canonical_smiles'])
    
    # Add molecule IDs
    df.insert(0, 'molecule_id', [f"P1_A_{i:03d}" for i in range(len(df))])
    
    print(f"✓ Extracted {len(df)} candidates from P1 V7 (P2 Set C)")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Activity distribution: {df['activity'].value_counts().to_dict()}")
    
    return df


def extract_p3_benchmark() -> pd.DataFrame:
    """
    Extract P3 benchmark: 19,849 molecules with activity labels.
    
    Source: Project3_Quantum_Inspired_RepresentationsV2607/results/
    Must match exact cohort used in P3 canonical benchmarks
    
    Returns:
        DataFrame with columns: [molecule_id, smiles, canonical_smiles, activity, ...]
    """
    print("\n=== Extracting P3 Benchmark (19,849 molecules) ===")
    
    # Search for P3 canonical panel
    p3_results = P3_ROOT / "results"
    
    if not p3_results.exists():
        print(f"ERROR: P3 results directory not found at {p3_results}")
        sys.exit(1)
    
    # Look for canonical panel file
    possible_files = [
        "p3_canonical_panel.csv",
        "p3_benchmark_data.csv",
        "hybrid_benchmark_data.csv",
        "p3_activity_labels.csv"
    ]
    
    p3_data_file = None
    for filename in possible_files:
        candidate = p3_results / filename
        if candidate.exists():
            p3_data_file = candidate
            break
    
    if p3_data_file is None:
        print(f"ERROR: P3 benchmark data file not found in {p3_results}")
        print(f"\nSearched for: {possible_files}")
        print(f"\nAvailable files:")
        for f in p3_results.glob("*.csv"):
            print(f"  - {f.name}")
        print(f"\nPlease specify the correct file containing the 19,849-molecule cohort.")
        sys.exit(1)
    
    print(f"Reading: {p3_data_file}")
    df = pd.read_csv(p3_data_file)
    
    # Validate structure
    if 'smiles' not in df.columns:
        print(f"ERROR: 'smiles' column not found in {p3_data_file}")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    # Check for activity labels
    activity_cols = [c for c in df.columns if 'activity' in c.lower() or 'label' in c.lower()]
    if not activity_cols:
        print(f"WARNING: No activity column found. Available columns: {list(df.columns)}")
        df['activity'] = np.nan
    else:
        activity_col = activity_cols[0]
        print(f"Using activity column: {activity_col}")
        if activity_col != 'activity':
            df['activity'] = df[activity_col]
    
    # Canonicalize SMILES
    df['canonical_smiles'] = df['smiles'].apply(canonicalize_smiles)
    
    # Remove failed canonicalizations
    failed = df['canonical_smiles'].isna().sum()
    if failed > 0:
        print(f"WARNING: {failed} molecules failed SMILES canonicalization")
        df = df.dropna(subset=['canonical_smiles'])
    
    # Add molecule IDs if not present
    if 'molecule_id' not in df.columns:
        df.insert(0, 'molecule_id', [f"P3_B_{i:06d}" for i in range(len(df))])
    
    print(f"Extracted {len(df)} molecules from P3 benchmark")
    print(f"Expected: 19,849 | Actual: {len(df)}")
    
    if abs(len(df) - 19849) > 100:
        print(f"WARNING: Molecule count differs significantly from expected 19,849")
    
    print(f"Columns: {list(df.columns)}")
    
    return df


def extract_external_sample(n_sample=10000, seed=42) -> pd.DataFrame:
    """
    Extract external validation sample from QMSE asexual dataset.
    
    Source: Quantum_malaria_codes /Dataset_paper/Asexual_libraries_hits and nonhitsFinal.csv
    Total: 122,572 compounds (hits + non-hits)
    Sample: 10,000 for computational feasibility
    
    Returns:
        DataFrame with columns: [molecule_id, smiles, canonical_smiles, activity, ...]
    """
    print(f"\n=== Extracting External Sample ({n_sample} from 122K asexual dataset) ===")
    
    # Check for QMSE asexual dataset
    asexual_file = QMSE_DATA / "Asexual_libraries_hits and nonhitsFinal.csv"
    
    if not asexual_file.exists():
        print(f"ERROR: QMSE asexual dataset not found at {asexual_file}")
        print(f"\nSearching for alternative files in {QMSE_DATA}...")
        
        if QMSE_DATA.exists():
            csv_files = list(QMSE_DATA.glob("*.csv"))
            if csv_files:
                print(f"Found {len(csv_files)} CSV files:")
                for f in csv_files:
                    print(f"  - {f.name}")
        else:
            print(f"ERROR: QMSE Dataset_paper directory not found")
        
        sys.exit(1)
    
    print(f"Reading: {asexual_file}")
    df = pd.read_csv(asexual_file)
    
    print(f"Total molecules in asexual dataset: {len(df)}")
    
    # Sample stratified by activity if possible
    if 'activity' in df.columns or any('hit' in c.lower() for c in df.columns):
        activity_col = 'activity' if 'activity' in df.columns else [c for c in df.columns if 'hit' in c.lower()][0]
        print(f"Stratified sampling by: {activity_col}")
        df_sample = df.groupby(activity_col, group_keys=False).apply(
            lambda x: x.sample(min(len(x), n_sample // 2), random_state=seed)
        ).head(n_sample)
    else:
        print(f"Random sampling (no activity column found)")
        df_sample = df.sample(n=min(n_sample, len(df)), random_state=seed)
    
    # Canonicalize SMILES
    if 'SMILES' in df_sample.columns:
        df_sample['smiles'] = df_sample['SMILES']
    
    df_sample['canonical_smiles'] = df_sample['smiles'].apply(canonicalize_smiles)
    
    # Remove failed canonicalizations
    failed = df_sample['canonical_smiles'].isna().sum()
    if failed > 0:
        print(f"WARNING: {failed} molecules failed SMILES canonicalization")
        df_sample = df_sample.dropna(subset=['canonical_smiles'])
    
    # Add molecule IDs
    df_sample.insert(0, 'molecule_id', [f"EXT_A_{i:06d}" for i in range(len(df_sample))])
    
    print(f"Extracted {len(df_sample)} molecules from external dataset")
    print(f"Columns: {list(df_sample.columns)}")
    
    return df_sample


def save_datasets(p1_df=None, p3_df=None, ext_df=None):
    """Save datasets and generate provenance manifest."""
    print("\n=== Saving Datasets ===")
    
    # Create directories
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROVENANCE_DIR.mkdir(parents=True, exist_ok=True)
    
    provenance = {
        "timestamp": datetime.now().isoformat(),
        "script": "p7_data_preparation.py",
        "datasets": {}
    }
    
    if p1_df is not None:
        p1_file = DATA_DIR / "p1_set_a_20_candidates.csv"
        p1_df.to_csv(p1_file, index=False)
        print(f"Saved: {p1_file} ({len(p1_df)} molecules)")
        
        provenance["datasets"]["p1_set_a"] = {
            "file": "p1_set_a_20_candidates.csv",
            "n_molecules": len(p1_df),
            "source": str(P1_V7_ROOT.relative_to(WORKSPACE_ROOT)),
            "columns": list(p1_df.columns)
        }
    
    if p3_df is not None:
        p3_file = DATA_DIR / "p3_benchmark_19849.csv"
        p3_df.to_csv(p3_file, index=False)
        print(f"Saved: {p3_file} ({len(p3_df)} molecules)")
        
        provenance["datasets"]["p3_benchmark"] = {
            "file": "p3_benchmark_19849.csv",
            "n_molecules": len(p3_df),
            "source": str(P3_ROOT.relative_to(WORKSPACE_ROOT)),
            "columns": list(p3_df.columns)
        }
    
    if ext_df is not None:
        ext_file = DATA_DIR / "external_sample_10k.csv"
        ext_df.to_csv(ext_file, index=False)
        print(f"Saved: {ext_file} ({len(ext_df)} molecules)")
        
        provenance["datasets"]["external_sample"] = {
            "file": "external_sample_10k.csv",
            "n_molecules": len(ext_df),
            "source": str(QMSE_DATA.relative_to(WORKSPACE_ROOT)),
            "columns": list(ext_df.columns)
        }
    
    # Save provenance
    manifest_file = PROVENANCE_DIR / "data_manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(provenance, f, indent=2)
    print(f"\nProvenance saved: {manifest_file}")


def main():
    parser = argparse.ArgumentParser(description="Prepare P7 datasets")
    parser.add_argument('--all', action='store_true', help="Extract all datasets")
    parser.add_argument('--p1-only', action='store_true', help="Extract P1 Set A only")
    parser.add_argument('--p3-only', action='store_true', help="Extract P3 benchmark only")
    parser.add_argument('--external-only', action='store_true', help="Extract external sample only")
    parser.add_argument('--n-external', type=int, default=10000, help="Number of external samples")
    
    args = parser.parse_args()
    
    # Default to --all if no specific option
    if not any([args.all, args.p1_only, args.p3_only, args.external_only]):
        args.all = True
    
    print("=" * 60)
    print("P7 Data Preparation")
    print("=" * 60)
    
    p1_df, p3_df, ext_df = None, None, None
    
    try:
        if args.all or args.p1_only:
            p1_df = extract_p1_set_a()
        
        if args.all or args.p3_only:
            p3_df = extract_p3_benchmark()
        
        if args.all or args.external_only:
            ext_df = extract_external_sample(n_sample=args.n_external)
        
        save_datasets(p1_df, p3_df, ext_df)
        
        print("\n" + "=" * 60)
        print("✅ Data preparation complete")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Verify datasets in data/ directory")
        print("  2. Run baseline: python scripts/p7_baseline_classical.py")
        print("  3. Run quantum encoding: python scripts/p7_quantum_circuits.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
