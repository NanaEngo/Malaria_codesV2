#!/usr/bin/env python3
"""
Extract Best Docking Poses for MD Complex Building

Extracts the top-ranked docking poses from DiffDock results and converts
them to PDB format for use in MD simulations.

Strategy:
- For each target-ligand pair, use DiffDock rank1 pose (lowest confidence score)
- Convert SDF to PDB format
- Align to MD-ready protein structure
- Output ready-to-use ligand coordinates

Usage:
    python scripts/extract_docking_poses.py --complex 201_PfDHFR
    python scripts/extract_docking_poses.py --complex 164_PfClpP
    python scripts/extract_docking_poses.py --all
"""

import sys
import argparse
from pathlib import Path
import subprocess

PROJECT_DIR = Path(__file__).parent.parent
DIFFDOCK_DIR = PROJECT_DIR / "data" / "from_project1" / "docking" / "results_inference"
MD_DIR = PROJECT_DIR / "MD_systems"

# Mapping between complex names and docking targets
COMPLEX_MAPPING = {
    "201_PfDHFR": {
        "pdb": "7F3Y",
        "ligand": "201",
        "diffdock_dir": "7F3Y_mol_201",
        "target_name": "PfDHFR",
    },
    "164_PfClpP": {
        "pdb": "4GM2",
        "ligand": "164",
        "diffdock_dir": "4GM2_mol_164",
        "target_name": "PfClpP",
    },
    "214_PfCRT": {
        "pdb": "6UKJ",
        "ligand": "214",
        "diffdock_dir": "6UKJ_mol_214",
        "target_name": "PfCRT",
    },
    "438_PfATP4": {
        "pdb": "9N10",
        "ligand": "438",
        "diffdock_dir": "9N10_mol_438",
        "target_name": "PfATP4",
    },
}


def run_command(cmd, check=True):
    """Run shell command and return output."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout


def extract_pose_for_complex(complex_name):
    """
    Extract best docking pose for a complex.
    
    Steps:
    1. Find DiffDock results directory
    2. Extract rank1 pose (best confidence)
    3. Convert SDF to PDB
    4. Save to MD system directory
    """
    info = COMPLEX_MAPPING[complex_name]
    complex_dir = MD_DIR / complex_name
    
    print(f"\n{'='*70}")
    print(f"📥 Extracting Docking Pose: {complex_name}")
    print(f"{'='*70}")
    print(f"  Target: {info['target_name']} ({info['pdb']})")
    print(f"  Ligand: {info['ligand']}")
    
    # Find DiffDock results
    diffdock_path = DIFFDOCK_DIR / info['diffdock_dir']
    
    if not diffdock_path.exists():
        print(f"  ❌ ERROR: DiffDock results not found at {diffdock_path}")
        return False
    
    # Find rank1 pose
    rank1_files = list(diffdock_path.glob("rank1_confidence*.sdf"))
    if not rank1_files:
        rank1_files = list(diffdock_path.glob("rank1.sdf"))
    
    if not rank1_files:
        print(f"  ❌ ERROR: No rank1 pose found in {diffdock_path}")
        return False
    
    rank1_sdf = rank1_files[0]
    print(f"  ✓ Found rank1 pose: {rank1_sdf.name}")
    
    # Extract confidence score from filename
    if "confidence" in rank1_sdf.name:
        confidence = rank1_sdf.stem.split("confidence-")[1]
        print(f"    Confidence score: {confidence}")
    
    # Convert SDF to PDB using Open Babel or RDKit
    output_pdb = complex_dir / f"ligand_{info['ligand']}_docked.pdb"
    
    print(f"\n  🔄 Converting SDF to PDB...")
    
    try:
        # Try with obabel first
        run_command(
            f"obabel {rank1_sdf} -O {output_pdb} -h",
            check=True
        )
        print(f"  ✓ Converted with Open Babel")
    except:
        try:
            # Fallback to RDKit
            from rdkit import Chem
            from rdkit.Chem import AllChem
            
            mol = Chem.SDMolSupplier(str(rank1_sdf), removeHs=False)[0]
            if mol is None:
                raise ValueError("Could not read SDF")
            
            writer = Chem.PDBWriter(str(output_pdb))
            writer.write(mol)
            writer.close()
            print(f"  ✓ Converted with RDKit")
        except Exception as e:
            print(f"  ❌ ERROR: Could not convert SDF to PDB: {e}")
            print(f"  Trying manual Python conversion...")
            
            # Manual conversion as fallback
            convert_sdf_to_pdb_manual(rank1_sdf, output_pdb)
    
    if output_pdb.exists():
        print(f"  ✅ Docked pose saved: {output_pdb.name}")
        
        # Validate PDB
        n_atoms = len([l for l in output_pdb.read_text().splitlines() 
                      if l.startswith("ATOM") or l.startswith("HETATM")])
        print(f"     Atoms: {n_atoms}")
        
        return True
    else:
        print(f"  ❌ ERROR: Failed to create PDB file")
        return False


def convert_sdf_to_pdb_manual(sdf_file, pdb_file):
    """Manual SDF to PDB conversion."""
    lines = sdf_file.read_text().splitlines()
    
    # Parse SDF coordinate block
    # Line 4 contains counts: aaabbblllfffcccsssxxxrrrpppiiimmmvvvvvv
    # aaa = number of atoms
    count_line = lines[3]
    n_atoms = int(count_line[:3])
    
    # Atoms start at line 4 (0-indexed line 4 = 5th line)
    atom_lines = lines[4:4+n_atoms]
    
    # Write PDB
    with open(pdb_file, 'w') as f:
        f.write("REMARK   Extracted from DiffDock pose\n")
        
        for i, line in enumerate(atom_lines, start=1):
            parts = line.split()
            if len(parts) >= 4:
                x, y, z, element = parts[0], parts[1], parts[2], parts[3]
                
                # PDB format
                pdb_line = (
                    f"HETATM{i:5d}  {element:3s} UNL     1    "
                    f"{float(x):8.3f}{float(y):8.3f}{float(z):8.3f}"
                    f"  1.00  0.00          {element:>2s}\n"
                )
                f.write(pdb_line)
        
        f.write("END\n")
    
    print(f"  ✓ Manual conversion successful")


def main():
    parser = argparse.ArgumentParser(
        description="Extract docking poses for MD simulations"
    )
    parser.add_argument(
        "--complex",
        type=str,
        default="all",
        choices=list(COMPLEX_MAPPING.keys()) + ["all"],
        help="Complex to extract pose for"
    )
    args = parser.parse_args()
    
    print("="*70)
    print("📥 Docking Pose Extraction Tool")
    print("="*70)
    print("\nThis script will:")
    print("  1. Find DiffDock rank1 poses")
    print("  2. Convert SDF to PDB format")
    print("  3. Save to MD system directories")
    
    if args.complex == "all":
        complexes = list(COMPLEX_MAPPING.keys())
    else:
        complexes = [args.complex]
    
    success_count = 0
    for complex_name in complexes:
        try:
            if extract_pose_for_complex(complex_name):
                success_count += 1
        except Exception as e:
            print(f"\n  ❌ ERROR extracting {complex_name}: {e}")
    
    print(f"\n{'='*70}")
    print(f"Summary: {success_count}/{len(complexes)} poses extracted")
    print(f"{'='*70}")
    
    print("\n✅ Pose extraction complete!")
    print("\nNext steps:")
    print("  1. Visually inspect extracted poses with PyMOL")
    print("  2. Run replace_ligand_coords.py to update MD systems")
    print("  3. Re-run fix protocol with docked poses")


if __name__ == "__main__":
    main()
