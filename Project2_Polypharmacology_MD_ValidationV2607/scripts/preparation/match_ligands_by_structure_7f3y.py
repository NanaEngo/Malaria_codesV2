#!/usr/bin/env python3
"""
Match LIG systems to 7F3Y docking poses by extracting SMILES from PDB files
and matching them with the MD candidates list.
"""

import pandas as pd
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path("/home/vital/Documents/GitHub/Malaria_codes")
TUTO_DIR = BASE_DIR / "Project2_Polypharmacology_MD_Validation/Tuto_MD_MC"

# Read MD candidates with SMILES
md_candidates = pd.read_csv(TUTO_DIR / "md_top20_candidates.csv")
md_candidates['LIG_ID'] = 'LIG' + md_candidates['rank'].astype(str)

# Systems that need correction
lig_systems_present = ['LIG1', 'LIG2', 'LIG3', 'LIG5', 'LIG7', 'LIG8', 'LIG9', 'LIG10', 
                       'LIG14', 'LIG15', 'LIG16', 'LIG17']

print("=" * 80)
print("MATCHING LIG SYSTEMS TO 7F3Y DOCKING POSES BY STRUCTURE")
print("=" * 80)

# Read the docking summary to know which ligands are in EXCELLENT category
docking_summary = pd.read_csv(BASE_DIR / "Docking/Docking_7F3Y/mmv_results_consensus/summary_consensus_7F3Y.csv")

# Get EXCELLENT ligands
excellent_ligands = docking_summary[docking_summary['Category'] == 'EXCELLENT']['Ligand'].tolist()
print(f"\n✓ Found {len(excellent_ligands)} EXCELLENT docking results:")
for lig in excellent_ligands:
    score = docking_summary[docking_summary['Ligand'] == lig]['Best_Score'].values[0]
    print(f"  {lig}: {score:.3f} kcal/mol")

# Function to extract SMILES from PDB file using RDKit
def pdb_to_smiles(pdb_file):
    """Convert PDB file to SMILES string"""
    try:
        mol = Chem.MolFromPDBFile(str(pdb_file), removeHs=False)
        if mol is None:
            return None
        smiles = Chem.MolToSmiles(mol)
        return smiles
    except Exception:
        return None

# Function to calculate Tanimoto similarity
def calculate_similarity(smiles1, smiles2):
    """Calculate Tanimoto similarity between two SMILES"""
    try:
        mol1 = Chem.MolFromSmiles(smiles1)
        mol2 = Chem.MolFromSmiles(smiles2)
        
        if mol1 is None or mol2 is None:
            return 0.0
        
        # Generate Morgan fingerprints
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, radius=2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, radius=2, nBits=2048)
        
        # Calculate Tanimoto similarity
        similarity = DataStructs.TanimotoSimilarity(fp1, fp2)
        return similarity
    except Exception:
        return 0.0

print("\n" + "=" * 80)
print("EXTRACTING SMILES FROM DOCKING PDB FILES")
print("=" * 80)

# Path to original PDB ligand library
pdb_ligands_dir = BASE_DIR / "Project2_Polypharmacology_MD_Validation/data/from_project1/data/pdb_ligands_mmv"

if not pdb_ligands_dir.exists():
    print(f"\n⚠ Directory not found: {pdb_ligands_dir}")
    print("Trying alternate path...")
    pdb_ligands_dir = Path("/home/vital/Documents/PhD_2021/Malaria_codes/data/pdb_ligands_mmv")

if pdb_ligands_dir.exists():
    print(f"\n✓ Found PDB ligands directory: {pdb_ligands_dir}")
    
    # Extract SMILES for all relevant ligands
    ligand_smiles_map = {}
    
    # Check all ligand IDs (0-399, the full screening library)
    print("\nExtracting SMILES from PDB files (this may take a minute)...")
    for i in range(400):
        pdb_file = pdb_ligands_dir / f"ligand_{i}.pdb"
        if pdb_file.exists():
            smiles = pdb_to_smiles(pdb_file)
            if smiles:
                ligand_smiles_map[f"ligand_{i}"] = smiles
    
    print(f"✓ Successfully extracted SMILES for {len(ligand_smiles_map)} ligands")
    
    # Now match each LIG system to the best matching docking pose
    print("\n" + "=" * 80)
    print("MATCHING LIG SYSTEMS TO DOCKING POSES")
    print("=" * 80)
    
    results = []
    
    for lig_id in lig_systems_present:
        # Get SMILES for this LIG system
        rank = int(lig_id.replace('LIG', ''))
        lig_smiles = md_candidates[md_candidates['rank'] == rank]['smiles'].values[0]
        lig_aff_7f3y = md_candidates[md_candidates['rank'] == rank]['MPO_7f3y'].values[0]
        
        print(f"\n{lig_id}:")
        print(f"  SMILES: {lig_smiles[:60]}...")
        print(f"  7F3Y Affinity: {lig_aff_7f3y:.3f}")
        
        # Calculate similarity with all ligands in the screening library
        best_match = None
        best_similarity = 0.0
        
        for ligand_id, docking_smiles in ligand_smiles_map.items():
            similarity = calculate_similarity(lig_smiles, docking_smiles)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = ligand_id
        
        if best_match and best_similarity > 0.95:
            print(f"  ✓ MATCH FOUND: {best_match} (similarity: {best_similarity:.4f})")
            
            # Check if this ligand has a docking result
            ligand_num = best_match.replace('ligand_', '')
            docking_entry = docking_summary[docking_summary['Ligand'] == f'ligand_{ligand_num}']
            
            if not docking_entry.empty:
                category = docking_entry['Category'].values[0]
                score = docking_entry['Best_Score'].values[0]
                print(f"    Docking: {category}, Score: {score:.3f} kcal/mol")
                
                # Check if PDBQT file exists
                if category == 'EXCELLENT':
                    pdbqt_path = BASE_DIR / f"Docking/Docking_7F3Y/mmv_results_consensus/EXCELLENT/ligand_{ligand_num}_out.pdbqt"
                elif category == 'GOOD':
                    pdbqt_path = BASE_DIR / f"Docking/Docking_7F3Y/mmv_results_consensus/GOOD/ligand_{ligand_num}_out.pdbqt"
                else:
                    pdbqt_path = BASE_DIR / f"Docking/Docking_7F3Y/mmv_results_consensus/OTHERS/ligand_{ligand_num}_out.pdbqt"
                
                pdbqt_exists = pdbqt_path.exists()
                print(f"    PDBQT file: {'✓ EXISTS' if pdbqt_exists else '✗ NOT FOUND'}")
                
                results.append({
                    'LIG_ID': lig_id,
                    'Rank': rank,
                    'LIG_SMILES': lig_smiles,
                    'Matched_Ligand': best_match,
                    'Similarity': best_similarity,
                    'Docking_Category': category,
                    'Docking_Score': score,
                    'PDBQT_File': f"ligand_{ligand_num}_out.pdbqt",
                    'PDBQT_Path': str(pdbqt_path),
                    'PDBQT_Exists': pdbqt_exists
                })
            else:
                print(f"    ⚠ No docking result found for {best_match}")
        else:
            print(f"  ✗ NO GOOD MATCH FOUND (best similarity: {best_similarity:.4f})")
    
    # Create DataFrame and save results
    if results:
        results_df = pd.DataFrame(results)
        output_file = TUTO_DIR / "7F3Y_LIGAND_MAPPING.csv"
        results_df.to_csv(output_file, index=False)
        print("\n" + "=" * 80)
        print("RESULTS SUMMARY")
        print("=" * 80)
        print(f"\n✓ Successfully matched {len(results)} LIG systems")
        print(f"✓ Results saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("MAPPING TABLE")
        print("=" * 80)
        print(results_df[['LIG_ID', 'Matched_Ligand', 'Similarity', 'Docking_Category', 'Docking_Score', 'PDBQT_Exists']].to_string(index=False))
        
        # Count by category
        print("\n" + "=" * 80)
        print("BY DOCKING CATEGORY")
        print("=" * 80)
        print(results_df.groupby('Docking_Category').size())
        
    else:
        print("\n⚠ No matches found!")
        
else:
    print(f"\n✗ PDB ligands directory not found: {pdb_ligands_dir}")
    print("\nPlease check the path to the original PDB ligand library.")

print("\n" + "=" * 80)
print("NEXT STEP: Extract docking poses from matched PDBQT files")
print("=" * 80)
