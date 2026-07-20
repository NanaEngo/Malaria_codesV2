#!/usr/bin/env python
"""
Convert PDB ligands to MOL2 format using OpenBabel
Adds Gasteiger charges and proper bond orders for CHARMM-GUI/GROMACS

Input:  ligand_prep/*.pdb
Output: ligand_mol2/*.mol2

Dependencies:
    OpenBabel (system installation): /usr/bin/obabel
"""

import os
import sys
import subprocess
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

OBABEL_PATH = "/usr/bin/obabel"
INPUT_DIR = "/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/ligand_prep"
OUTPUT_DIR = "/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/ligand_mol2"

# OpenBabel options
ADD_HYDROGENS = True        # Add hydrogens if missing
CALCULATE_CHARGES = True    # Calculate Gasteiger charges
PH = 7.4                    # pH for protonation

# ──────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def check_obabel():
    """Verify OpenBabel is installed"""
    if not os.path.exists(OBABEL_PATH):
        print(f"✗ Error: OpenBabel not found at {OBABEL_PATH}")
        print("\nInstall with:")
        print("  sudo apt-get install openbabel")
        print("  # or")
        print("  conda install -c conda-forge openbabel")
        return False
    
    try:
        # OpenBabel --version returns exit code 1, so check stderr for version
        result = subprocess.run(
            [OBABEL_PATH, "--version"],
            capture_output=True,
            text=True
        )
        # Version info is in stderr
        version_text = (result.stdout + result.stderr).strip()
        version_line = [l for l in version_text.split('\n') if 'Open Babel' in l]
        if version_line:
            print(f"✓ OpenBabel found: {version_line[0]}")
            return True
        else:
            print(f"✓ OpenBabel executable found at {OBABEL_PATH}")
            return True
    except Exception as e:
        print(f"✗ Error checking OpenBabel: {e}")
        return False

def convert_pdb_to_mol2(pdb_file, mol2_file):
    """
    Convert PDB to MOL2 using OpenBabel
    
    Args:
        pdb_file: Path to input PDB
        mol2_file: Path to output MOL2
        
    Returns:
        bool: True if successful
    """
    try:
        # Build obabel command
        cmd = [OBABEL_PATH, str(pdb_file), "-O", str(mol2_file)]
        
        # Add options
        options = []
        
        if ADD_HYDROGENS:
            options.append(f"-p {PH}")  # Add hydrogens at pH
        
        if CALCULATE_CHARGES:
            options.append("--partialcharge gasteiger")  # Gasteiger charges
        
        # Add bond order perception (important for MOL2)
        options.extend([
            "-h",              # Add hydrogens explicitly
            "--gen3d",         # Generate 3D coordinates if missing
        ])
        
        if options:
            cmd.extend(options)
        
        # Run conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"  ✗ OpenBabel error: {result.stderr}")
            return False
        
        # Check output file exists and has content
        if not os.path.exists(mol2_file):
            print("  ✗ Output file not created")
            return False
        
        if os.path.getsize(mol2_file) < 100:
            print("  ✗ Output file too small (likely empty)")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("  ✗ Conversion timeout (>30s)")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def get_mol2_info(mol2_file):
    """Extract basic info from MOL2 file"""
    try:
        with open(mol2_file, 'r') as f:
            content = f.read()
        
        # Count atoms
        if "@<TRIPOS>ATOM" in content:
            atom_section = content.split("@<TRIPOS>ATOM")[1].split("@<TRIPOS>")[0]
            n_atoms = len([l for l in atom_section.strip().split('\n') if l.strip()])
        else:
            n_atoms = 0
        
        # Count bonds
        if "@<TRIPOS>BOND" in content:
            bond_section = content.split("@<TRIPOS>BOND")[1].split("@<TRIPOS>")[0]
            n_bonds = len([l for l in bond_section.strip().split('\n') if l.strip()])
        else:
            n_bonds = 0
        
        # Get molecule name
        if "@<TRIPOS>MOLECULE" in content:
            mol_section = content.split("@<TRIPOS>MOLECULE")[1].split("@<TRIPOS>")[0]
            lines = mol_section.strip().split('\n')
            mol_name = lines[0].strip() if lines else "unknown"
        else:
            mol_name = "unknown"
        
        return {
            'name': mol_name,
            'atoms': n_atoms,
            'bonds': n_bonds,
            'size_kb': os.path.getsize(mol2_file) / 1024
        }
        
    except Exception:
        return {
            'name': 'error',
            'atoms': 0,
            'bonds': 0,
            'size_kb': 0
        }

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 17 + "CONVERSION PDB → MOL2" + " " * 29 + "║")
    print("║" + " " * 19 + "OpenBabel Pipeline" + " " * 30 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Check OpenBabel
    if not check_obabel():
        return 1
    print()
    
    # Check input directory
    input_path = Path(INPUT_DIR)
    if not input_path.exists():
        print(f"✗ Error: Input directory not found: {INPUT_DIR}")
        return 1
    
    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Input:  {INPUT_DIR}")
    print(f"✓ Output: {OUTPUT_DIR}")
    print()
    
    # Find PDB files
    pdb_files = sorted(input_path.glob("*.pdb"))
    
    if not pdb_files:
        print(f"✗ No PDB files found in {INPUT_DIR}")
        return 1
    
    print(f"Found {len(pdb_files)} PDB file(s)")
    print()
    
    print("=" * 70)
    print("CONVERSION")
    print("=" * 70)
    print()
    
    # Convert each file
    success_count = 0
    fail_count = 0
    failed_files = []
    
    for pdb_file in pdb_files:
        # Output filename
        mol2_file = output_path / f"{pdb_file.stem}.mol2"
        
        print(f"[{pdb_files.index(pdb_file) + 1}/{len(pdb_files)}] {pdb_file.name}")
        print(f"  → {mol2_file.name}")
        
        # Convert
        if convert_pdb_to_mol2(pdb_file, mol2_file):
            # Get info
            info = get_mol2_info(mol2_file)
            print("  ✓ Success")
            print(f"    Atoms: {info['atoms']}, Bonds: {info['bonds']}")
            print(f"    Size: {info['size_kb']:.1f} KB")
            success_count += 1
        else:
            print("  ✗ Failed")
            fail_count += 1
            failed_files.append(pdb_file.name)
        
        print()
    
    # Summary
    print("=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)
    print(f"Total:      {len(pdb_files)}")
    print(f"Succès:     {success_count} ✓")
    print(f"Échecs:     {fail_count} ✗")
    
    if failed_files:
        print("\nFichiers échoués:")
        for fname in failed_files:
            print(f"  - {fname}")
    
    print(f"\nFichiers MOL2 dans: {OUTPUT_DIR}")
    
    # List generated files
    mol2_files = sorted(output_path.glob("*.mol2"))
    if mol2_files:
        print(f"\nFichiers générés ({len(mol2_files)}):")
        for mol2_file in mol2_files:
            size_kb = mol2_file.stat().st_size / 1024
            print(f"  {mol2_file.name} ({size_kb:.1f} KB)")
    
    print()
    print("=" * 70)
    print("PROCHAINES ÉTAPES")
    print("=" * 70)
    print("1. Valider les fichiers MOL2:")
    print("   python validate_mol2_files.py")
    print()
    print("2. Upload vers CHARMM-GUI:")
    print("   https://charmm-gui.org/?doc=input/ligandrm")
    print()
    print("3. Ou utiliser pour GROMACS topologie:")
    print("   - CGenFF via CHARMM-GUI")
    print("   - ACPYPE pour AMBER/GAFF")
    print()
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
