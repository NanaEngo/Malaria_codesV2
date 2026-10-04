#!/usr/bin/env python3
"""
P7 Data Extraction - P1 Set A (20 candidates)

Searches for P1 Set A data in multiple possible locations and extracts it.
Fallback: Can use P2 Set C (17 candidates) if Set A not found.

Usage:
    python scripts/p7_extract_p1_set_a.py [--use-set-c]
"""
import os
import sys
import json
import argparse
from pathlib import Path
import pandas as pd

def find_p1_data(project_root):
    """Search for P1 Set A data in multiple locations"""
    
    # Possible P1 project directories
    p1_candidates = [
        "Project1_Chem_space_antimalarial_V7_CorrectedGrid",
        "Project1_Chem_space_antimalarial_V8",
        "Project1_Chem_space_antimalarial_V2607_CorrectedGrid"
    ]
    
    # Possible file patterns for Set A
    set_a_patterns = [
        "results/set_a*.csv",
        "results/*top_20*.csv",
        "results/*candidates*.csv",
        "data/set_a*.csv",
        "data/*top_20*.csv"
    ]
    
    found_files = []
    
    for p1_name in p1_candidates:
        p1_path = project_root / p1_name
        if not p1_path.exists():
            continue
        
        print(f"Searching in {p1_name}...")
        
        for pattern in set_a_patterns:
            for file_path in p1_path.glob(pattern):
                if file_path.is_file():
                    found_files.append(file_path)
                    print(f"  Found: {file_path.relative_to(project_root)}")
    
    return found_files

def find_set_c_data(project_root):
    """Fallback: Find P2 Set C (17 polypharmacology candidates)"""
    
    p2_candidates = [
        "Project2_Polypharmacology_MD_ValidationV2607",
        "Project2_Polypharmacology_MD_Validation"
    ]
    
    set_c_patterns = [
        "results/*set_c*.csv",
        "results/*c_candidates*.csv",
        "results/*pp-*.csv",
        "data/*set_c*.csv"
    ]
    
    found_files = []
    
    for p2_name in p2_candidates:
        p2_path = project_root / p2_name
        if not p2_path.exists():
            continue
        
        print(f"Searching Set C in {p2_name}...")
        
        for pattern in set_c_patterns:
            for file_path in p2_path.glob(pattern):
                if file_path.is_file():
                    found_files.append(file_path)
                    print(f"  Found: {file_path.relative_to(project_root)}")
    
    return found_files

def standardize_data(df, source_name):
    """Standardize data format to required schema"""
    
    required_cols = {'mol_id', 'SMILES', 'activity_label'}
    
    # Map common column name variations
    col_map = {
        'smiles': 'SMILES',
        'canonical_smiles': 'SMILES',
        'Canonical_SMILES': 'SMILES',
        'molecule_id': 'mol_id',
        'compound_id': 'mol_id',
        'id': 'mol_id',
        'label': 'activity_label',
        'active': 'activity_label',
        'is_active': 'activity_label'
    }
    
    # Rename columns
    df = df.rename(columns=col_map)
    
    # Check for SMILES column
    if 'SMILES' not in df.columns:
        smiles_candidates = [c for c in df.columns if 'smiles' in c.lower()]
        if smiles_candidates:
            df = df.rename(columns={smiles_candidates[0]: 'SMILES'})
        else:
            raise ValueError(f"No SMILES column found in {source_name}")
    
    # Check for mol_id
    if 'mol_id' not in df.columns:
        # Try to find ID column
        id_candidates = [c for c in df.columns if c.lower() in ['id', 'molecule_id', 'compound_id', 'name']]
        if id_candidates:
            df = df.rename(columns={id_candidates[0]: 'mol_id'})
        elif 'PP-' in str(df.iloc[0, 0]):  # Set C naming convention
            df['mol_id'] = df.iloc[:, 0]
        else:
            # Generate IDs
            df['mol_id'] = [f"MOL_{i:03d}" for i in range(len(df))]
            print("  Generated mol_id column")
    
    # Check for activity_label
    if 'activity_label' not in df.columns:
        # Try to derive from MPO or docking scores
        if 'MPO' in df.columns:
            # Use MPO threshold (e.g., > 0.5 = active)
            threshold = df['MPO'].median()
            df['activity_label'] = (df['MPO'] > threshold).astype(int)
            print(f"  Derived activity_label from MPO (threshold={threshold:.3f})")
        elif 'docking_score' in df.columns or 'binding_affinity' in df.columns:
            score_col = 'docking_score' if 'docking_score' in df.columns else 'binding_affinity'
            threshold = df[score_col].median()
            df['activity_label'] = (df[score_col] < threshold).astype(int)  # Lower = better
            print(f"  Derived activity_label from {score_col} (threshold={threshold:.3f})")
        else:
            # Default: all active (for initial testing)
            df['activity_label'] = 1
            print("  ⚠️  No activity labels found - setting all to 1 (active)")
    
    # Ensure binary labels
    if df['activity_label'].dtype != int:
        df['activity_label'] = df['activity_label'].astype(int)
    
    # Select required columns + keep extras
    keep_cols = ['mol_id', 'SMILES', 'activity_label']
    extra_cols = [c for c in df.columns if c not in keep_cols and c not in ['Unnamed: 0', 'index']]
    final_cols = keep_cols + extra_cols
    
    df = df[final_cols]
    
    return df

def extract_data(use_set_c=False):
    """Main extraction logic"""
    
    script_dir = Path(__file__).parent.parent
    project_root = script_dir.parent
    output_dir = script_dir / "data" / "p1_set_a"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("P7 Data Extraction - P1 Set A (or Set C)")
    print("=" * 60)
    print()
    
    # Search for data
    if use_set_c:
        print("Using Set C (17 polypharmacology candidates) as requested...")
        found_files = find_set_c_data(project_root)
        target_name = "Set C"
    else:
        print("Searching for P1 Set A (20 top candidates)...")
        found_files = find_p1_data(project_root)
        target_name = "Set A"
        
        if not found_files:
            print("\n⚠️  Set A not found. Trying Set C as fallback...")
            found_files = find_set_c_data(project_root)
            target_name = "Set C (fallback)"
    
    if not found_files:
        print("\n❌ No candidate data found!")
        print("\nPlease manually specify the data file:")
        print("  python scripts/p7_extract_p1_set_a.py --input path/to/data.csv")
        sys.exit(1)
    
    print(f"\nFound {len(found_files)} candidate file(s)")
    
    # Try to load each file
    for file_path in found_files:
        try:
            print(f"\nTrying to load: {file_path.name}")
            
            # Try different separators
            for sep in [',', '\t', ';']:
                try:
                    df = pd.read_csv(file_path, sep=sep, nrows=5)
                    if len(df.columns) > 1:
                        # Found correct separator
                        df = pd.read_csv(file_path, sep=sep)
                        break
                except:
                    continue
            
            print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
            print(f"  Columns: {', '.join(df.columns[:10])}")
            
            # Standardize format
            df = standardize_data(df, file_path.name)
            
            # Quality checks
            assert 'SMILES' in df.columns, "Missing SMILES column"
            assert 'mol_id' in df.columns, "Missing mol_id column"
            assert 'activity_label' in df.columns, "Missing activity_label column"
            
            # Check SMILES validity (RDKit)
            try:
                from rdkit import Chem
                valid_smiles = df['SMILES'].apply(lambda s: Chem.MolFromSmiles(str(s)) is not None)
                n_valid = valid_smiles.sum()
                print(f"  Valid SMILES: {n_valid}/{len(df)}")
                
                if n_valid < len(df):
                    print(f"  ⚠️  {len(df) - n_valid} invalid SMILES found - removing")
                    df = df[valid_smiles].reset_index(drop=True)
            except ImportError:
                print("  ⚠️  RDKit not available - skipping SMILES validation")
            
            # Check size
            if len(df) < 10:
                print(f"  ⚠️  Only {len(df)} molecules - might be too small")
            
            # Save
            output_file = output_dir / f"p1_set_a_{len(df)}_candidates.csv"
            df.to_csv(output_file, index=False)
            print(f"\n✓ Saved to: {output_file}")
            
            # Save metadata
            metadata = {
                'source': str(file_path.relative_to(project_root)),
                'source_type': target_name,
                'n_molecules': len(df),
                'n_active': int(df['activity_label'].sum()),
                'n_inactive': int((df['activity_label'] == 0).sum()),
                'columns': list(df.columns),
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            metadata_file = output_dir / "extraction_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"✓ Metadata saved to: {metadata_file}")
            
            # Summary
            print(f"\n" + "=" * 60)
            print(f"Extraction Summary:")
            print(f"=" * 60)
            print(f"Source: {target_name}")
            print(f"Molecules: {len(df)}")
            print(f"Active: {metadata['n_active']}")
            print(f"Inactive: {metadata['n_inactive']}")
            print(f"Output: {output_file}")
            print("=" * 60)
            
            return
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue
    
    print("\n❌ Could not load any candidate file")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract P1 Set A data for P7")
    parser.add_argument('--use-set-c', action='store_true', 
                       help='Use P2 Set C (17 candidates) instead of Set A')
    parser.add_argument('--input', type=str, 
                       help='Manually specify input file path')
    
    args = parser.parse_args()
    
    if args.input:
        # Manual input file specified
        input_file = Path(args.input)
        if not input_file.exists():
            print(f"❌ File not found: {input_file}")
            sys.exit(1)
        
        # Load and process
        print(f"Loading manual input: {input_file}")
        # TODO: Add manual file processing
        
    else:
        # Auto-search
        extract_data(use_set_c=args.use_set_c)
