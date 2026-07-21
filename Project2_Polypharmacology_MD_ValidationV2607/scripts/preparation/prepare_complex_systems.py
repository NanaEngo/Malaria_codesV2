#!/usr/bin/env python
"""
Prepare Complex Systems for GROMACS MD Simulations

This script integrates ligand topologies from CHARMM-GUI into prepared
protein-solvent systems to create complete protein-ligand complexes ready
for GROMACS MD simulations.

Input:
    - Gromacs_inputs/LIG*/charmm-gui-*/: Ligand topologies from CHARMM-GUI
    - Gromacs_inputs/LIG*/Complex_*/: Protein-solvent systems (without ligand)

Output:
    - Updated topology files (topol.top) with ligand included
    - Updated index files (index.ndx) with ligand groups
    - Merged coordinate files (step3_input.gro) with ligand

Requirements:
    - Each LIG*/charmm-gui-* folder must contain:
        * gromacs/LIG*.itp (ligand topology)
        * ligandrm.pdb (ligand structure)
        * toppar/*.prm and *.rtf files (CGenFF parameters)
    - Each Complex_* folder must contain:
        * topol.top (protein-solvent topology)
        * step3_input.gro (starting structure)
        * step3_input.pdb (starting structure in PDB)
        * index.ndx (index groups)

Author: Generated for Malaria MD Project
Date: June 2026
"""

import os
import sys
import shutil
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path("/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/Gromacs_inputs")
TEST_COMPLEX = Path("/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/Test/Complex_test")

# List of LIG folders to process
LIG_FOLDERS = [f"LIG{i}" for i in [1, 2, 3, 5, 7, 8, 9, 10, 14, 15, 16, 17]]

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def find_charmm_gui_folder(lig_folder):
    """Find the charmm-gui-* folder in a LIG directory"""
    charmm_dirs = list(lig_folder.glob("charmm-gui-*"))
    if not charmm_dirs:
        return None
    return charmm_dirs[0]

def find_complex_folder(lig_folder):
    """Find the Complex_* folder in a LIG directory"""
    complex_dirs = list(lig_folder.glob("Complex_*"))
    if not complex_dirs:
        return None
    return complex_dirs[0]

def extract_lig_name_from_itp(itp_file):
    """Extract ligand residue name from .itp file"""
    try:
        with open(itp_file, 'r') as f:
            for line in f:
                if line.strip().startswith('[') and 'moleculetype' in line:
                    # Read next non-comment line
                    for next_line in f:
                        if not next_line.strip().startswith(';') and next_line.strip():
                            parts = next_line.strip().split()
                            if parts:
                                return parts[0]
                    break
        return None
    except Exception as e:
        print(f"    ✗ Error reading {itp_file.name}: {e}")
        return None

# ──────────────────────────────────────────────────────────────────────────────
# TOPOLOGY MODIFICATION
# ──────────────────────────────────────────────────────────────────────────────

def update_topology_file(complex_dir, charmm_dir, lig_name):
    """
    Update topol.top to include ligand topology
    
    Adds:
    1. CGenFF parameters include
    2. Ligand .itp file include
    3. Ligand entry in [molecules] section
    """
    topol_file = complex_dir / "topol.top"
    topol_backup = complex_dir / "topol.top.backup"
    
    print(f"    Updating {topol_file.name}...")
    
    # Backup original
    if not topol_backup.exists():
        shutil.copy(topol_file, topol_backup)
    
    # Find ligand .itp file
    lig_itp_files = list((charmm_dir / "gromacs").glob(f"{lig_name}*.itp"))
    if not lig_itp_files:
        lig_itp_files = list((charmm_dir / "gromacs").glob("LIG*.itp"))
    
    if not lig_itp_files:
        print("    ✗ No .itp file found for ligand")
        return False
    
    lig_itp = lig_itp_files[0]
    lig_resname = extract_lig_name_from_itp(lig_itp)
    
    if not lig_resname:
        print(f"    ✗ Could not extract ligand residue name from {lig_itp.name}")
        return False
    
    print(f"      Ligand residue name: {lig_resname}")
    
    # Read current topology
    with open(topol_file, 'r') as f:
        lines = f.readlines()
    
    # Find where to insert includes
    forcefield_idx = None
    molecules_idx = None
    
    for i, line in enumerate(lines):
        if '#include "toppar/forcefield.itp"' in line:
            forcefield_idx = i
        if '[ molecules ]' in line:
            molecules_idx = i
    
    if forcefield_idx is None or molecules_idx is None:
        print("    ✗ Could not find insertion points in topology")
        return False
    
    # Check if ligand already added
    if any(lig_resname in line for line in lines):
        print(f"      ⚠ Ligand {lig_resname} already in topology, skipping...")
        return True
    
    # Build new content
    new_lines = lines[:forcefield_idx + 1]
    
    # Add CGenFF parameters (if exists in toppar directory)
    cgenff_file = complex_dir / "toppar" / "cgenff_params.itp"
    if cgenff_file.exists():
        new_lines.append("\n; --- CGenFF additional parameters ---\n")
        new_lines.append('#include "toppar/cgenff_params.itp"\n')
    
    # Add ligand topology
    new_lines.append("\n; --- Ligand topology ---\n")
    rel_path = os.path.relpath(lig_itp, complex_dir)
    new_lines.append(f'#include "{rel_path}"\n')
    new_lines.append("\n")
    
    # Add rest of original content until molecules section
    new_lines.extend(lines[forcefield_idx + 1:])
    
    # Add ligand to [molecules] section
    # Find the end of molecules list
    in_molecules = False
    final_lines = []
    
    for line in new_lines:
        final_lines.append(line)
        
        if '[ molecules ]' in line:
            in_molecules = True
        elif in_molecules and line.strip() and not line.strip().startswith(';'):
            # This is a molecule entry, check if it's the last one
            if not any(mol in line for mol in ['PROA', 'NDP', 'POT', 'CLA', 'TIP3']):
                continue
            
            # If this is TIP3 (usually last), add ligand after
            if 'TIP3' in line:
                final_lines.append(f"{lig_resname:6s}             1\n")
                in_molecules = False
    
    # Write updated topology
    with open(topol_file, 'w') as f:
        f.writelines(final_lines)
    
    print(f"      ✓ Topology updated with {lig_resname}")
    return True

# ──────────────────────────────────────────────────────────────────────────────
# COORDINATE FILE MERGING
# ──────────────────────────────────────────────────────────────────────────────

def merge_coordinates(complex_dir, charmm_dir):
    """
    Merge protein system with ligand coordinates
    
    Reads:
        - complex_dir/step3_input.gro (protein+solvent)
        - charmm_dir/ligandrm.pdb (ligand)
    
    Outputs:
        - complex_dir/step3_input_with_ligand.gro
    """
    print("    Merging coordinate files...")
    
    complex_gro = complex_dir / "step3_input.gro"
    ligand_pdb = charmm_dir / "ligandrm.pdb"
    output_gro = complex_dir / "step3_input_with_ligand.gro"
    
    if not complex_gro.exists():
        print(f"    ✗ {complex_gro.name} not found")
        return False
    
    if not ligand_pdb.exists():
        print(f"    ✗ {ligand_pdb.name} not found")
        return False
    
    # This is a placeholder - actual merging should be done with GROMACS gmx editconf
    print("      ⚠ Coordinate merging requires GROMACS gmx editconf")
    print("      Manual step required:")
    print(f"        cd {complex_dir}")
    print("        gmx editconf -f step3_input.gro -o protein.gro")
    print(f"        gmx editconf -f {ligand_pdb} -o ligand.gro")
    print("        gmx insert-molecules -f protein.gro -ci ligand.gro -o step3_input_merged.gro")
    
    return None  # Indicates manual step needed

# ──────────────────────────────────────────────────────────────────────────────
# INDEX FILE UPDATE
# ──────────────────────────────────────────────────────────────────────────────

def update_index_file(complex_dir, lig_resname):
    """
    Update index.ndx to include ligand atom groups
    
    This is a placeholder - actual index updating should be done with gmx make_ndx
    """
    print("    Updating index file...")
    
    index_file = complex_dir / "index.ndx"
    
    if not index_file.exists():
        print(f"      ⚠ {index_file.name} not found, will be generated by GROMACS")
        return None
    
    print("      ⚠ Index file update requires GROMACS gmx make_ndx")
    print("      Manual step required:")
    print(f"        cd {complex_dir}")
    print("        gmx make_ndx -f step3_input_merged.gro -o index.ndx")
    print("        # In gmx make_ndx, add ligand group:")
    print(f"        > r {lig_resname}")
    print("        > q")
    
    return None

# ──────────────────────────────────────────────────────────────────────────────
# MAIN PROCESSING
# ──────────────────────────────────────────────────────────────────────────────

def process_lig_folder(lig_name):
    """Process a single LIG folder"""
    print(f"\n{'='*70}")
    print(f"Processing {lig_name}")
    print(f"{'='*70}")
    
    lig_folder = BASE_DIR / lig_name
    
    if not lig_folder.exists():
        print(f"  ✗ Folder not found: {lig_folder}")
        return False
    
    # Find charmm-gui folder
    charmm_dir = find_charmm_gui_folder(lig_folder)
    if not charmm_dir:
        print("  ✗ No charmm-gui-* folder found")
        return False
    
    print(f"  ✓ CHARMM-GUI: {charmm_dir.name}")
    
    # Find Complex folder
    complex_dir = find_complex_folder(lig_folder)
    if not complex_dir:
        print("  ✗ No Complex_* folder found")
        return False
    
    print(f"  ✓ Complex: {complex_dir.name}")
    
    # Check required files
    required_charmm_files = [
        charmm_dir / "gromacs",
        charmm_dir / "ligandrm.pdb"
    ]
    
    required_complex_files = [
        complex_dir / "topol.top",
        complex_dir / "step3_input.gro"
    ]
    
    missing_files = []
    for f in required_charmm_files + required_complex_files:
        if not f.exists():
            missing_files.append(str(f.name))
    
    if missing_files:
        print(f"  ✗ Missing files: {', '.join(missing_files)}")
        return False
    
    print("  ✓ All required files present")
    
    # Update topology
    success = update_topology_file(complex_dir, charmm_dir, lig_name)
    
    if not success:
        print("  ✗ Failed to update topology")
        return False
    
    # Note: Coordinate merging and index update require GROMACS
    merge_coordinates(complex_dir, charmm_dir)
    
    # Extract ligand residue name for index update
    lig_itp_files = list((charmm_dir / "gromacs").glob("LIG*.itp"))
    if lig_itp_files:
        lig_resname = extract_lig_name_from_itp(lig_itp_files[0])
        if lig_resname:
            update_index_file(complex_dir, lig_resname)
    
    print(f"\n  ✓ {lig_name} processing complete (topology updated)")
    print("    ⚠ Manual GROMACS steps still required for coordinates & index")
    
    return True

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PREPARE COMPLEX SYSTEMS" + " " * 29 + "║")
    print("║" + " " * 12 + "Integrate Ligands into MD Systems" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    print(f"Base directory: {BASE_DIR}")
    print(f"Processing {len(LIG_FOLDERS)} LIG folders")
    print()
    
    # Check base directory exists
    if not BASE_DIR.exists():
        print(f"✗ Error: Base directory not found: {BASE_DIR}")
        return 1
    
    # Process each LIG folder
    success_count = 0
    fail_count = 0
    failed_ligs = []
    
    for lig_name in LIG_FOLDERS:
        try:
            if process_lig_folder(lig_name):
                success_count += 1
            else:
                fail_count += 1
                failed_ligs.append(lig_name)
        except Exception as e:
            print(f"\n  ✗ Exception processing {lig_name}: {e}")
            fail_count += 1
            failed_ligs.append(lig_name)
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total:      {len(LIG_FOLDERS)}")
    print(f"Success:    {success_count} ✓")
    print(f"Failed:     {fail_count} ✗")
    
    if failed_ligs:
        print("\nFailed LIG folders:")
        for lig in failed_ligs:
            print(f"  - {lig}")
    
    print(f"\n{'='*70}")
    print("NEXT STEPS")
    print(f"{'='*70}")
    print("1. For each Complex_* folder, run coordinate merging:")
    print("   cd Gromacs_inputs/LIG1/Complex_1/")
    print("   gmx editconf -f step3_input.gro -o complex_merged.gro")
    print()
    print("2. Generate index files:")
    print("   gmx make_ndx -f complex_merged.gro -o index.ndx")
    print()
    print("3. Run energy minimization:")
    print("   gmx grompp -f step4.0_minimization.mdp -o mini.tpr -c complex_merged.gro -p topol.top -n index.ndx")
    print("   gmx mdrun -v -deffnm mini")
    print()
    print("4. Continue with equilibration and production")
    print()
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
