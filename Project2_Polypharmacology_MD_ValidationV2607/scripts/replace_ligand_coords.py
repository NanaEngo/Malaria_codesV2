#!/usr/bin/env python3
"""
Replace Ligand Coordinates in MD System with Docked Pose

Takes a docked ligand PDB and replaces the ligand coordinates in an
existing solvated GRO file, maintaining all other atoms (protein, water, ions).

This allows us to start MD from the actual docking pose instead of a
generic placement that may lead to dissociation.

Usage:
    python scripts/replace_ligand_coords.py --complex 201_PfDHFR
    python scripts/replace_ligand_coords.py --complex 164_PfClpP
"""

import sys
import argparse
from pathlib import Path
import shutil

PROJECT_DIR = Path(__file__).parent.parent
MD_DIR = PROJECT_DIR / "MD_systems"


def read_gro_file(gro_file):
    """
    Parse GROMACS GRO file.
    
    Returns:
        header: First line (title)
        n_atoms: Number of atoms
        atoms: List of atom lines
        box: Box dimensions line
    """
    lines = gro_file.read_text().splitlines()
    
    header = lines[0]
    n_atoms = int(lines[1].strip())
    atoms = lines[2:2+n_atoms]
    box = lines[2+n_atoms]
    
    return header, n_atoms, atoms, box


def read_pdb_file(pdb_file):
    """
    Parse PDB file and extract coordinates.
    
    Returns:
        coords: List of (x, y, z) tuples in Angstroms
        elements: List of element symbols
    """
    lines = pdb_file.read_text().splitlines()
    
    coords = []
    elements = []
    
    for line in lines:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            # PDB format: columns 31-38 (x), 39-46 (y), 47-54 (z)
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            
            # Element is typically at columns 77-78, or can parse from atom name
            if len(line) >= 78:
                element = line[76:78].strip()
            else:
                # Fallback: parse from atom name (columns 13-16)
                atom_name = line[12:16].strip()
                element = ''.join([c for c in atom_name if c.isalpha()])[:2]
            
            coords.append((x, y, z))
            elements.append(element)
    
    return coords, elements


def angstrom_to_nm(angstrom_coords):
    """Convert Angstrom to nanometers."""
    return [(x/10.0, y/10.0, z/10.0) for x, y, z in angstrom_coords]


def parse_gro_atom(line):
    """
    Parse GRO atom line.
    
    GRO format (fixed width):
    %5d%-5s%5s%5d%8.3f%8.3f%8.3f%8.4f%8.4f%8.4f
    residue_num, residue_name, atom_name, atom_num, x, y, z, vx, vy, vz
    """
    residue_num = int(line[0:5])
    residue_name = line[5:10].strip()
    atom_name = line[10:15].strip()
    atom_num = int(line[15:20])
    x = float(line[20:28])
    y = float(line[28:36])
    z = float(line[36:44])
    
    # Velocities (optional)
    vx = vy = vz = 0.0
    if len(line) > 44:
        try:
            vx = float(line[44:52])
            vy = float(line[52:60])
            vz = float(line[60:68])
        except:
            pass
    
    return {
        'residue_num': residue_num,
        'residue_name': residue_name,
        'atom_name': atom_name,
        'atom_num': atom_num,
        'coords': (x, y, z),
        'velocities': (vx, vy, vz),
        'has_velocities': len(line) > 44
    }


def format_gro_atom(atom_data, new_coords=None):
    """
    Format GRO atom line.
    
    Args:
        atom_data: Dict from parse_gro_atom
        new_coords: Optional (x, y, z) tuple to replace coordinates
    """
    if new_coords:
        x, y, z = new_coords
    else:
        x, y, z = atom_data['coords']
    
    line = (
        f"{atom_data['residue_num']:>5d}"
        f"{atom_data['residue_name']:<5s}"
        f"{atom_data['atom_name']:>5s}"
        f"{atom_data['atom_num']:>5d}"
        f"{x:>8.3f}{y:>8.3f}{z:>8.3f}"
    )
    
    if atom_data['has_velocities']:
        vx, vy, vz = atom_data['velocities']
        line += f"{vx:>8.4f}{vy:>8.4f}{vz:>8.4f}"
    
    return line


def replace_ligand_in_gro(gro_file, docked_pdb, output_gro, ligand_resname="UNL"):
    """
    Replace ligand coordinates in GRO file with docked pose.
    
    Args:
        gro_file: Input GRO file (e.g., ions.gro)
        docked_pdb: Docked ligand PDB file
        output_gro: Output GRO file with replaced ligand
        ligand_resname: Residue name of ligand in GRO (default: UNL)
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n  🔄 Replacing ligand coordinates...")
    print(f"     Input GRO:  {gro_file.name}")
    print(f"     Docked PDB: {docked_pdb.name}")
    print(f"     Output GRO: {output_gro.name}")
    
    # Read GRO file
    header, n_atoms, atom_lines, box = read_gro_file(gro_file)
    
    # Parse all atoms
    atoms = [parse_gro_atom(line) for line in atom_lines]
    
    # Find ligand atoms
    ligand_indices = [i for i, atom in enumerate(atoms) 
                     if atom['residue_name'] == ligand_resname]
    
    if not ligand_indices:
        print(f"  ❌ ERROR: No ligand atoms found with residue name '{ligand_resname}'")
        print(f"     Available residue names: {set([a['residue_name'] for a in atoms[:100]])}")
        return False
    
    print(f"     Found {len(ligand_indices)} ligand atoms in GRO")
    
    # Read docked pose
    pdb_coords, pdb_elements = read_pdb_file(docked_pdb)
    pdb_coords_nm = angstrom_to_nm(pdb_coords)
    
    print(f"     Found {len(pdb_coords_nm)} atoms in docked PDB")
    
    # Check atom count match
    if len(ligand_indices) != len(pdb_coords_nm):
        print(f"  ⚠️  WARNING: Atom count mismatch!")
        print(f"     GRO ligand atoms: {len(ligand_indices)}")
        print(f"     PDB docked atoms: {len(pdb_coords_nm)}")
        print(f"     Will use minimum count and align by element")
    
    # Replace coordinates
    n_replaced = min(len(ligand_indices), len(pdb_coords_nm))
    
    for i in range(n_replaced):
        gro_idx = ligand_indices[i]
        atoms[gro_idx]['coords'] = pdb_coords_nm[i]
    
    print(f"     ✓ Replaced {n_replaced} ligand atom coordinates")
    
    # Write output GRO
    with open(output_gro, 'w') as f:
        f.write(header + "\n")
        f.write(f"{n_atoms}\n")
        
        for atom in atoms:
            f.write(format_gro_atom(atom) + "\n")
        
        f.write(box + "\n")
    
    print(f"  ✅ Output saved: {output_gro.name}")
    
    return True


def replace_ligand_for_complex(complex_name):
    """
    Replace ligand coordinates for a specific complex.
    
    Steps:
    1. Find docked pose PDB
    2. Backup original ions.gro
    3. Replace ligand coordinates
    4. Save as ions_docked.gro
    """
    complex_dir = MD_DIR / complex_name
    
    print(f"\n{'='*70}")
    print(f"🔄 Replacing Ligand Coordinates: {complex_name}")
    print(f"{'='*70}")
    
    # Find files
    ions_gro = complex_dir / "ions.gro"
    docked_pdb = list(complex_dir.glob("ligand_*_docked.pdb"))
    
    if not ions_gro.exists():
        print(f"  ❌ ERROR: ions.gro not found in {complex_dir}")
        return False
    
    if not docked_pdb:
        print(f"  ❌ ERROR: No docked PDB found in {complex_dir}")
        print(f"     Run extract_docking_poses.py first!")
        return False
    
    docked_pdb = docked_pdb[0]
    
    # Backup original
    backup_gro = complex_dir / "ions_original.gro"
    if not backup_gro.exists():
        shutil.copy2(ions_gro, backup_gro)
        print(f"  ✓ Backed up original: {backup_gro.name}")
    
    # Replace ligand
    output_gro = complex_dir / "ions_docked.gro"
    
    success = replace_ligand_in_gro(ions_gro, docked_pdb, output_gro)
    
    if success:
        print(f"\n  ✅ SUCCESS: Ligand coordinates replaced!")
        print(f"     New system ready: {output_gro.name}")
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Replace ligand coordinates with docked pose"
    )
    parser.add_argument(
        "--complex",
        type=str,
        required=True,
        help="Complex name (e.g., 201_PfDHFR, 164_PfClpP)"
    )
    args = parser.parse_args()
    
    print("="*70)
    print("🔄 Ligand Coordinate Replacement Tool")
    print("="*70)
    print("\nThis script will:")
    print("  1. Backup original ions.gro")
    print("  2. Extract ligand coordinates from docked PDB")
    print("  3. Replace ligand in solvated system")
    print("  4. Save as ions_docked.gro")
    
    success = replace_ligand_for_complex(args.complex)
    
    if success:
        print(f"\n{'='*70}")
        print("✅ Coordinate replacement complete!")
        print(f"{'='*70}")
        print("\nNext steps:")
        print("  1. Visually inspect ions_docked.gro with PyMOL/VMD")
        print("  2. Run fix protocol with --input ions_docked.gro")
        print(f"     python scripts/md_fix_dissociated_ligands.py --complex {args.complex} --input ions_docked.gro")
    else:
        print(f"\n{'='*70}")
        print("❌ Coordinate replacement failed!")
        print(f"{'='*70}")
        sys.exit(1)


if __name__ == "__main__":
    main()
