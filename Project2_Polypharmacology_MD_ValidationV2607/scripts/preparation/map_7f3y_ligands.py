#!/usr/bin/env python3
"""
Map LIG systems to 7F3Y docking pose files by matching SMILES strings.
This script identifies which ligand_###_out.pdbqt files correspond to each LIG system.
"""

import pandas as pd
from pathlib import Path

# Base directory
BASE_DIR = Path("/home/vital/Documents/GitHub/Malaria_codes")
TUTO_DIR = BASE_DIR / "Project2_Polypharmacology_MD_Validation/Tuto_MD_MC"

# Read the MD candidates file with SMILES
md_candidates = pd.read_csv(TUTO_DIR / "md_top20_candidates.csv")

# Create LIG_ID mapping (rank 1 = LIG1, rank 2 = LIG2, etc.)
md_candidates['LIG_ID'] = 'LIG' + md_candidates['rank'].astype(str)

# Read 7F3Y docking summary
docking_summary = pd.read_csv(BASE_DIR / "Docking/Docking_7F3Y/mmv_results_consensus/summary_consensus_7F3Y.csv")

print("=" * 80)
print("7F3Y LIGAND MAPPING - Finding docking poses for LIG systems")
print("=" * 80)

# Systems present in Gromacs_inputs
lig_systems_present = ['LIG1', 'LIG2', 'LIG3', 'LIG5', 'LIG7', 'LIG8', 'LIG9', 'LIG10', 
                       'LIG14', 'LIG15', 'LIG16', 'LIG17']

print(f"\n✓ Found {len(md_candidates)} ligands in md_top20_candidates.csv")
print(f"✓ Found {len(docking_summary)} docking results in 7F3Y summary")
print(f"✓ Working with {len(lig_systems_present)} MD systems that need correction\n")

# The docking was done on ligands from the original screening library
# The ligand IDs in docking (ligand_0, ligand_1, etc.) correspond to row indices
# in the original screening library

# Let's check if there's a mapping file in the docking directory
docking_dir = BASE_DIR / "Docking/Docking_7F3Y/mmv_results_consensus"
print(f"Checking for mapping files in: {docking_dir}")

# Look for any CSV or text files that might contain SMILES
for file in docking_dir.glob("*.csv"):
    if file.name != "summary_consensus_7F3Y.csv":
        print(f"  Found: {file.name}")

for file in docking_dir.glob("*.txt"):
    if file.name != "progress_report_7F3Y.txt":
        print(f"  Found: {file.name}")

print("\n" + "=" * 80)
print("STRATEGY:")
print("=" * 80)
print("""
The docking results use numeric IDs (ligand_0, ligand_1, ..., ligand_395).
To map these to our LIG systems, we need to:

1. Find the original screening library file that was used as docking input
2. This file should contain SMILES strings for each ligand_### ID
3. Match the SMILES from md_top20_candidates.csv to the screening library

Let's search for the screening library file...
""")

# Search for potential screening library files
print("\nSearching for screening library files...")
search_paths = [
    BASE_DIR / "Docking",
    BASE_DIR / "data",
    BASE_DIR,
]

library_files = []
for search_path in search_paths:
    if search_path.exists():
        for pattern in ["*.csv", "*.smi", "*.txt"]:
            for file in search_path.rglob(pattern):
                name = file.name.lower()
                if any(keyword in name for keyword in ['library', 'ligand', 'smiles', 'compound', 'mmv', 'screening']):
                    if file.stat().st_size < 50 * 1024 * 1024:  # Less than 50 MB
                        library_files.append(file)

if library_files:
    print(f"\n✓ Found {len(library_files)} potential library files:")
    for f in library_files[:10]:  # Show first 10
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.relative_to(BASE_DIR)} ({size_mb:.2f} MB)")
    if len(library_files) > 10:
        print(f"  ... and {len(library_files) - 10} more files")
else:
    print("\n⚠ No obvious library files found")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("""
To complete the mapping, we need to either:

A. Locate the original screening library CSV/SMI file that was used as input to docking
   - Look for files with columns: [ID, SMILES] or similar
   - The ID should match the numeric IDs in the docking results (0-395)

B. Extract SMILES from the PDBQT files themselves
   - PDBQT files may contain SMILES in REMARK lines
   - We can parse all PDBQT files and extract their SMILES

C. Match by molecular structure
   - Convert PDBQT → MOL2
   - Calculate Tanimoto similarity between LIG systems and all docking poses
   - Find best matches

Let's start with option B (check PDBQT headers)...
""")

# Check PDBQT file headers for SMILES
print("\nChecking PDBQT file headers for SMILES information:")
pdbqt_dir = BASE_DIR / "Docking/Docking_7F3Y/mmv_results_consensus/EXCELLENT"
if pdbqt_dir.exists():
    pdbqt_files = list(pdbqt_dir.glob("ligand_*_out.pdbqt"))
    print(f"\n✓ Found {len(pdbqt_files)} PDBQT files in EXCELLENT category\n")
    
    # Check first few files for SMILES
    for pdbqt_file in pdbqt_files[:4]:
        print(f"\n{'=' * 60}")
        print(f"File: {pdbqt_file.name}")
        print('=' * 60)
        with open(pdbqt_file, 'r') as f:
            lines = f.readlines()[:30]  # First 30 lines
            for line in lines:
                if line.strip():
                    print(line.rstrip())
        print()

print("\n" + "=" * 80)
print("OUTPUT SUMMARY:")
print("=" * 80)
print(f"""
MD Systems to correct: {len(lig_systems_present)}
  {', '.join(lig_systems_present)}

7F3Y Affinities (kcal/mol):
""")

for lig_id in lig_systems_present:
    rank = int(lig_id.replace('LIG', ''))
    row = md_candidates[md_candidates['rank'] == rank].iloc[0]
    aff = row['MPO_7f3y']
    print(f"  {lig_id}: {aff:.3f} kcal/mol")

print("\n" + "=" * 80)
