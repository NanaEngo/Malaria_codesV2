#!/usr/bin/env python3
"""
P7 ANP Metadata Computation

Computes African Natural Product metadata:
- ACSI (African-Chemotype Structural Index)
- Fsp³ (Fraction sp³ carbons)
- Stereocenter count
- Ring count
- ANP class assignment

Usage:
    python scripts/p7_compute_anp_metadata.py --dataset p1_set_a
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np

def compute_fsp3(mol):
    """Compute fraction of sp³ carbons"""
    from rdkit import Chem
    
    if mol is None:
        return np.nan
    
    n_carbons = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() == 'C')
    if n_carbons == 0:
        return 0.0
    
    n_sp3 = sum(1 for atom in mol.GetAtoms() 
                if atom.GetSymbol() == 'C' and atom.GetHybridization() == Chem.HybridizationType.SP3)
    
    return n_sp3 / n_carbons

def count_stereocenters(mol):
    """Count chiral centers (R/S)"""
    from rdkit import Chem
    
    if mol is None:
        return 0
    
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    stereocenters = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    
    return len(stereocenters)

def count_rings(mol):
    """Count number of rings"""
    from rdkit import Chem
    
    if mol is None:
        return 0
    
    return Chem.GetSSSR(mol)

def has_macrocycle(mol):
    """Detect macrocycles (rings ≥ 12 atoms)"""
    from rdkit import Chem
    
    if mol is None:
        return False
    
    ri = mol.GetRingInfo()
    for ring in ri.AtomRings():
        if len(ring) >= 12:
            return True
    return False

def compute_acsi(mol, anp_reference_fp):
    """
    Compute African-Chemotype Structural Index
    
    ACSI = mean Tanimoto similarity to top-5 nearest ANP references
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem, DataStructs
    
    if mol is None:
        return np.nan
    
    # Generate fingerprint
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
    
    # Compute similarities to all ANP references
    similarities = []
    for ref_fp in anp_reference_fp:
        sim = DataStructs.TanimotoSimilarity(fp, ref_fp)
        similarities.append(sim)
    
    # Mean of top-5
    similarities.sort(reverse=True)
    acsi = np.mean(similarities[:5])
    
    return acsi

def classify_anp(mol, acsi, fsp3, n_stereocenters):
    """
    Classify molecule into ANP structural classes:
    - Indole alkaloids
    - Prenylated flavonoids
    - Quassinoids
    - Simple phenolics
    - Synthetic
    """
    from rdkit import Chem
    
    if mol is None:
        return "Unknown"
    
    # Synthetic (low ANP similarity)
    if acsi < 0.3:
        return "Synthetic"
    
    # SMARTS patterns for structural classes
    patterns = {
        'Indole alkaloids': Chem.MolFromSmarts('c1ccc2c(c1)[nH]cc2'),  # Indole core
        'Prenylated flavonoids': Chem.MolFromSmarts('c1cc(O)c(c(O)c1)C(=O)c2ccccc2'),  # Flavonoid skeleton
        'Simple phenolics': Chem.MolFromSmarts('c1ccccc1O'),  # Phenol
    }
    
    # Check patterns
    for class_name, pattern in patterns.items():
        if pattern and mol.HasSubstructMatch(pattern):
            # Additional checks
            if class_name == 'Indole alkaloids' and n_stereocenters >= 1:
                return class_name
            elif class_name == 'Prenylated flavonoids' and fsp3 > 0.3:
                return class_name
            elif class_name == 'Simple phenolics' and fsp3 < 0.3:
                return class_name
    
    # Quassinoids (high Fsp³, many stereocenters, complex)
    if fsp3 > 0.6 and n_stereocenters >= 4:
        return "Quassinoids"
    
    # Default: ANP (high similarity but no specific class)
    if acsi > 0.5:
        return "ANP (unclassified)"
    
    return "Other"

def load_anp_reference_set():
    """
    Load 396 ANP reference structures for ACSI computation
    
    Returns:
        List of RDKit fingerprints
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem
    
    print("Loading ANP reference set...")
    
    # Try to find ANP reference file
    script_dir = Path(__file__).parent.parent
    project_root = script_dir.parent
    
    anp_ref_candidates = [
        script_dir / "data" / "anp_reference_396.csv",
        project_root / "data" / "anp_reference_396.csv",
        project_root / "Project1_Chem_space_antimalarial_V7_CorrectedGrid" / "data" / "anp_seeds.csv"
    ]
    
    for ref_file in anp_ref_candidates:
        if ref_file.exists():
            print(f"  Found: {ref_file}")
            df_ref = pd.read_csv(ref_file)
            
            # Find SMILES column
            smiles_col = None
            for col in df_ref.columns:
                if 'smiles' in col.lower():
                    smiles_col = col
                    break
            
            if smiles_col is None:
                continue
            
            # Generate fingerprints
            fps = []
            for smiles in df_ref[smiles_col]:
                mol = Chem.MolFromSmiles(str(smiles))
                if mol:
                    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
                    fps.append(fp)
            
            print(f"  Loaded {len(fps)} ANP reference fingerprints")
            return fps
    
    # Fallback: Generate synthetic ANP-like structures
    print("  ⚠️  ANP reference file not found - using synthetic references")
    print("  Note: ACSI values will be approximate")
    
    # Generic ANP SMILES (examples)
    anp_smiles = [
        "CC1=C(C(=O)C2=C(C1=O)C(=CC=C2O)O)CC=C(C)C",  # Naphthoquinone
        "CC1=CC(=O)C2=C(O1)C=C(C(=C2O)CC=C(C)C)O",  # Prenylated chromone
        "C1CN2CC3=CC=CC=C3C2=CC4=C1C=C(C=C4)O",  # Isoquinoline alkaloid
    ]
    
    fps = []
    for smiles in anp_smiles * 50:  # Repeat to get ~150 references
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
            fps.append(fp)
    
    return fps

def compute_metadata(dataset_name):
    """Main computation logic"""
    
    from rdkit import Chem
    
    script_dir = Path(__file__).parent.parent
    input_dir = script_dir / "data" / dataset_name
    
    # Find input file
    input_files = list(input_dir.glob("*_candidates.csv"))
    if not input_files:
        print(f"❌ No candidate file found in {input_dir}")
        sys.exit(1)
    
    input_file = input_files[0]
    print(f"Loading: {input_file}")
    
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} molecules")
    
    # Load ANP reference set
    anp_reference_fp = load_anp_reference_set()
    
    # Compute RDKit mols
    print("\nComputing molecular descriptors...")
    df['mol'] = df['SMILES'].apply(Chem.MolFromSmiles)
    
    # Compute descriptors
    print("  - Fsp³...")
    df['Fsp3'] = df['mol'].apply(compute_fsp3)
    
    print("  - Stereocenter count...")
    df['stereocenter_count'] = df['mol'].apply(count_stereocenters)
    
    print("  - Ring count...")
    df['ring_count'] = df['mol'].apply(count_rings)
    
    print("  - Macrocycle detection...")
    df['has_macrocycle'] = df['mol'].apply(has_macrocycle)
    
    print("  - ACSI (ANP similarity)...")
    df['ACSI'] = df['mol'].apply(lambda m: compute_acsi(m, anp_reference_fp))
    
    print("  - ANP class assignment...")
    df['ANP_class'] = df.apply(
        lambda row: classify_anp(row['mol'], row['ACSI'], row['Fsp3'], row['stereocenter_count']),
        axis=1
    )
    
    # Drop mol column (not serializable)
    df = df.drop(columns=['mol'])
    
    # Save
    output_file = input_dir / input_file.name.replace('.csv', '_anp_metadata.csv')
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    # Summary statistics
    print(f"\n" + "=" * 60)
    print("ANP Metadata Summary")
    print("=" * 60)
    print(f"Molecules: {len(df)}")
    print(f"\nFsp³ distribution:")
    print(f"  Mean: {df['Fsp3'].mean():.3f}")
    print(f"  Median: {df['Fsp3'].median():.3f}")
    print(f"  Range: [{df['Fsp3'].min():.3f}, {df['Fsp3'].max():.3f}]")
    print(f"\nACSI distribution:")
    print(f"  Mean: {df['ACSI'].mean():.3f}")
    print(f"  Median: {df['ACSI'].median():.3f}")
    print(f"  Range: [{df['ACSI'].min():.3f}, {df['ACSI'].max():.3f}]")
    print(f"\nANP class distribution:")
    print(df['ANP_class'].value_counts().to_string())
    print(f"\nStereocenters: {df['stereocenter_count'].sum()} total")
    print(f"Macrocycles: {df['has_macrocycle'].sum()} molecules")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute ANP metadata for P7")
    parser.add_argument('--dataset', type=str, required=True,
                       choices=['p1_set_a', 'p3_benchmark', 'external'],
                       help='Dataset to annotate')
    
    args = parser.parse_args()
    
    try:
        compute_metadata(args.dataset)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
