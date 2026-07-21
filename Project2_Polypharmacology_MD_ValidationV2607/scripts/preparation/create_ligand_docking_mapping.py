#!/usr/bin/env python3
"""
Create Ligand-Docking Mapping for MD Simulation Correction

Matches LIG# systems to their:
- Original SMILES
- Best target protein (based on MPO affinities)
- Docking pose files from Autodock VINA results

This mapping will be used to correct ligand placement in all MD systems.
"""

import pandas as pd
from pathlib import Path
import sys

# Paths
BASE_DIR = Path("/home/vital/Documents/GitHub/Malaria_codes")
MD_DIR = BASE_DIR / "Project2_Polypharmacology_MD_Validation" / "Tuto_MD_MC"
DOCKING_DIR = BASE_DIR / "Docking"

# Input files
MD_CANDIDATES = MD_DIR / "md_top20_candidates.csv"
MPO_RANKING = BASE_DIR / "results" / "ANP_MPO_Ranked_Final_refined.csv"

# Output
OUTPUT_FILE = MD_DIR / "LIGAND_DOCKING_MAPPING.csv"

def load_data():
    """Load all required data files"""
    print("="*80)
    print("CREATING LIGAND-DOCKING MAPPING")
    print("="*80)
    print()
    
    # Load MD candidates (rank → SMILES)
    print(f"📂 Loading MD candidates: {MD_CANDIDATES}")
    md_df = pd.read_csv(MD_CANDIDATES)
    print(f"   ✓ {len(md_df)} ligands")
    
    # Load MPO ranking (SMILES → affinities)
    print(f"📂 Loading MPO ranking: {MPO_RANKING}")
    mpo_df = pd.read_csv(MPO_RANKING)
    print(f"   ✓ {len(mpo_df)} ranked compounds")
    print()
    
    return md_df, mpo_df

def match_ligands(md_df, mpo_df):
    """Match LIG# to SMILES and find best targets"""
    print("🔗 Matching ligands to docking results...")
    print()
    
    mapping = []
    
    for idx, row in md_df.iterrows():
        rank = row['rank']
        smiles = row['smiles']
        
        # Create LIG ID
        lig_id = f"LIG{rank}"
        
        print(f"  Processing {lig_id}...")
        
        # Match to MPO data by SMILES
        mpo_match = mpo_df[mpo_df['SMILES'] == smiles]
        
        if len(mpo_match) == 0:
            # Try standardized SMILES
            mpo_match = mpo_df[mpo_df['standard_smiles'] == smiles]
        
        if len(mpo_match) == 0:
            print(f"    ⚠️  No MPO match found for {lig_id}")
            continue
        
        mpo_row = mpo_match.iloc[0]
        
        # Extract affinity data for all 4 targets
        affinities = {
            '4GM2': mpo_row.get('aff_4gm2', None),
            '6UKJ': mpo_row.get('aff_6ukj', None),
            '7F3Y': mpo_row.get('aff_7f3y', None),
            '9N10': mpo_row.get('aff_9n10', None)
        }
        
        confidences = {
            '4GM2': mpo_row.get('conf_4gm2', None),
            '6UKJ': mpo_row.get('conf_6ukj', None),
            '7F3Y': mpo_row.get('conf_7f3y', None),
            '9N10': mpo_row.get('conf_9n10', None)
        }
        
        # Find best target (most negative affinity)
        valid_affinities = {k: v for k, v in affinities.items() if v is not None and pd.notna(v)}
        
        if not valid_affinities:
            print(f"    ⚠️  No valid affinities for {lig_id}")
            continue
        
        best_target = min(valid_affinities, key=valid_affinities.get)
        best_affinity = valid_affinities[best_target]
        best_confidence = confidences[best_target]
        
        # Determine expected docking directory
        docking_dir = DOCKING_DIR / f"Docking_{best_target}"
        
        # Check if docking directory exists
        if not docking_dir.exists():
            docking_status = "Docking_Dir_Missing"
            pose_path = None
        else:
            # Look for docking results
            consensus_dir = docking_dir / "results_consensus"
            excellent_dir = consensus_dir / "EXCELLENT"
            good_dir = consensus_dir / "GOOD"
            
            # Check for pose files (we'll need to match by SMILES later)
            if excellent_dir.exists():
                docking_status = "Excellent_Available"
                pose_path = str(excellent_dir)
            elif good_dir.exists():
                docking_status = "Good_Available"
                pose_path = str(good_dir)
            else:
                docking_status = "No_Poses_Found"
                pose_path = None
        
        print(f"    ✓ Best target: {best_target} ({best_affinity:.2f} kcal/mol)")
        print(f"      Confidence: {best_confidence:.2f}")
        print(f"      Docking: {docking_status}")
        
        # Add to mapping
        mapping.append({
            'LIG_ID': lig_id,
            'Rank': rank,
            'SMILES': smiles,
            'Standard_SMILES': mpo_row.get('standard_smiles', smiles),
            'MPO_Score': mpo_row.get('MPO_multi', None),
            'Hit_Tier': mpo_row.get('Hit_Tier', None),
            'Best_Target': best_target,
            'Best_Affinity': best_affinity,
            'Best_Confidence': best_confidence,
            'Aff_4GM2': affinities['4GM2'],
            'Aff_6UKJ': affinities['6UKJ'],
            'Aff_7F3Y': affinities['7F3Y'],
            'Aff_9N10': affinities['9N10'],
            'Docking_Status': docking_status,
            'Docking_Pose_Dir': pose_path,
            'System_Status': 'Needs_Correction'
        })
    
    print()
    print(f"✓ Matched {len(mapping)} ligands")
    print()
    
    return pd.DataFrame(mapping)

def save_mapping(df):
    """Save mapping to CSV"""
    print(f"💾 Saving mapping to: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"   ✓ Saved {len(df)} entries")
    print()

def print_summary(df):
    """Print summary statistics"""
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    
    print("📊 Target Distribution:")
    target_counts = df['Best_Target'].value_counts()
    for target, count in target_counts.items():
        print(f"   {target}: {count} ligands")
    print()
    
    print("📊 Affinity Statistics (Best Targets):")
    print(f"   Mean: {df['Best_Affinity'].mean():.2f} kcal/mol")
    print(f"   Min: {df['Best_Affinity'].min():.2f} kcal/mol (strongest)")
    print(f"   Max: {df['Best_Affinity'].max():.2f} kcal/mol (weakest)")
    print()
    
    print("📊 Docking Status:")
    status_counts = df['Docking_Status'].value_counts()
    for status, count in status_counts.items():
        print(f"   {status}: {count} ligands")
    print()
    
    print("📊 Hit Tier Distribution:")
    tier_counts = df['Hit_Tier'].value_counts()
    for tier, count in tier_counts.items():
        print(f"   {tier}: {count} ligands")
    print()
    
    # Show top 5 by affinity
    print("🏆 Top 5 Ligands by Affinity:")
    top5 = df.nsmallest(5, 'Best_Affinity')[['LIG_ID', 'Best_Target', 'Best_Affinity', 'Hit_Tier']]
    for idx, row in top5.iterrows():
        print(f"   {row['LIG_ID']}: {row['Best_Target']} = {row['Best_Affinity']:.2f} kcal/mol ({row['Hit_Tier']})")
    print()
    
    # Check which systems are in Gromacs_inputs
    print("📁 MD System Status:")
    for lig_id in df['LIG_ID']:
        lig_dir = MD_DIR / "Gromacs_inputs" / lig_id
        if lig_dir.exists():
            print(f"   {lig_id}: ✓ Present in Gromacs_inputs/")
        else:
            print(f"   {lig_id}: ✗ Missing from Gromacs_inputs/")
    print()
    
    print("="*80)
    print("✅ MAPPING COMPLETE")
    print("="*80)
    print()
    print("Next steps:")
    print(f"1. Review mapping file: {OUTPUT_FILE}")
    print("2. Locate actual PDBQT pose files in docking directories")
    print("3. Extract ligand coordinates from docking poses")
    print("4. Re-merge with correct protein-ligand positioning")
    print()

def main():
    """Main function"""
    try:
        # Load data
        md_df, mpo_df = load_data()
        
        # Match ligands
        mapping_df = match_ligands(md_df, mpo_df)
        
        # Save mapping
        save_mapping(mapping_df)
        
        # Print summary
        print_summary(mapping_df)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
