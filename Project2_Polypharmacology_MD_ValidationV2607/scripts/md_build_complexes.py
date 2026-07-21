"""
MD Simulation: Complex Building

Builds protein-ligand complexes and prepares solvated systems:
- Reads prepared protein and ligand structures
- Creates complex by placing ligand in binding site
- Generates topology with GROMACS pdb2gmx
- Solvates system with water box
- Adds ions for neutralization and 0.15 M NaCl

Usage:
    python scripts/md_build_complexes.py [--ligand-dir LIGAND_DIR]
"""

import sys
import subprocess
import shutil
from pathlib import Path
import argparse
import numpy as np

PROJECT_DIR = Path(__file__).parent.parent
MD_DIR = PROJECT_DIR / "MD_systems"

# Complex definitions with binding site info
COMPLEXES = {
    "201_PfDHFR": {
        "pdb": "7F3Y",
        "chain": "A",
        "ligand_name": "ligand_201",
        "ligand_resname": "LIG",
        "reference_ligand": "NAD",
        "binding_site_center": [1.33, -1.733, -23.842],
    },
    "438_PfATP4": {
        "pdb": "9N10",
        "chain": "A",
        "ligand_name": "ligand_438",
        "ligand_resname": "LIG",
        "reference_ligand": "ATP",
        "binding_site_center": [134.84, 133.10, 97.63],
    },
    "164_PfClpP": {
        "pdb": "4GM2",
        "chain": "A",
        "ligand_name": "ligand_164",
        "ligand_resname": "LIG",
        "reference_ligand": "COF",
        "binding_site_center": [26.19, 35.09, 24.72],
    },
    "214_PfCRT": {
        "pdb": "6UKJ",
        "chain": "A",
        "ligand_name": "ligand_214",
        "ligand_resname": "LIG",
        "reference_ligand": "CQ2",
        "binding_site_center": [152.99, 151.042, 159.379],
    },
}


def extract_binding_site_center_from_pdb(pdb_file, reference_ligand='NAD'):
    """
    Extract binding site center from reference ligand in prepared PDB.
    
    The binding site center is calculated as the geometric center
    of all heavy atoms in the reference ligand.
    
    Args:
        pdb_file: Path to prepared protein PDB
        reference_ligand: Residue name of reference ligand (NAD, ATP, COF, etc.)
        
    Returns:
        [x, y, z] center coordinates as list, or None if not found
    """
    pdb_file = Path(pdb_file)
    
    if not pdb_file.exists():
        print(f"  Warning: PDB file not found: {pdb_file}")
        return None
    
    try:
        from Bio.PDB import PDBParser, is_aa
    except ImportError:
        print("  Warning: BioPython not available for binding site extraction")
        print("  Please install: pip install biopython")
        return None
    
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', str(pdb_file))
        
        # Find all atoms in the reference ligand
        ligand_atoms = []
        found_ligand = False
        
        for residue in structure.get_residues():
            residue_name = residue.resname.strip()
            
            # Match residue name (case-insensitive)
            if residue_name.upper() == reference_ligand.upper():
                found_ligand = True
                
                # Get all heavy atoms (exclude hydrogens)
                for atom in residue:
                    # Skip hydrogen atoms
                    if atom.element.upper() != 'H':
                        ligand_atoms.append(atom.coord)
        
        if not found_ligand:
            # Get list of available residues for debugging
            available_residues = set(
                r.resname.strip() for r in structure.get_residues()
                if not is_aa(r)
            )
            print(f"  Warning: Reference ligand '{reference_ligand}' not found in PDB")
            if available_residues:
                print(f"  Available non-protein residues: {', '.join(sorted(available_residues))}")
            return None
        
        if not ligand_atoms:
            print(f"  Warning: No heavy atoms found in residue '{reference_ligand}'")
            return None
        
        # Calculate geometric center
        center = np.mean(ligand_atoms, axis=0).tolist()
        
        print(f"  ✓ Extracted binding site center from {reference_ligand}")
        print(f"    Center coordinates: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
        
        return center
        
    except Exception as e:
        print(f"  Warning: Error extracting binding site center: {e}")
        return None


def gro_to_pdb_atoms(gro_file, ligand_resname, binding_center):
    """
    Convert a GROMACS .gro file to PDB HETATM lines, translating the ligand
    centroid to the binding site centre.

    GROMACS .gro coordinates are in nm; PDB uses Angstroms.
    """
    lines = Path(gro_file).read_text().splitlines()
    # .gro format: line 0 = title, line 1 = atom count, lines 2..N-1 = atoms, last = box
    try:
        n_atoms = int(lines[1].strip())
    except (IndexError, ValueError):
        return []

    atom_lines = lines[2: 2 + n_atoms]
    coords = []
    parsed = []
    for line in atom_lines:
        # columns: resnum(5) resname(5) atomname(5) atomnum(5) x(8.3f) y(8.3f) z(8.3f)
        try:
            resname = line[5:10].strip()
            atomname = line[10:15].strip()
            atomnum = int(line[15:20].strip())
            x = float(line[20:28]) * 10.0  # nm -> Å
            y = float(line[28:36]) * 10.0
            z = float(line[36:44]) * 10.0
            coords.append([x, y, z])
            parsed.append((resname, atomname, atomnum, x, y, z))
        except (ValueError, IndexError):
            continue

    if not parsed:
        return []

    # Translate centroid to binding site centre
    centroid = np.mean(coords, axis=0)
    shift = np.array(binding_center) - centroid

    pdb_lines = []
    for i, (resname, atomname, atomnum, x, y, z) in enumerate(parsed, start=1):
        tx, ty, tz = x + shift[0], y + shift[1], z + shift[2]
        element = atomname[0] if atomname else 'C'
        pdb_lines.append(
            f"HETATM{i:5d}  {atomname:<4s}{ligand_resname:3s}  {1:4d}    "
            f"{tx:8.3f}{ty:8.3f}{tz:8.3f}  1.00  0.00          {element:>2s}\n"
        )
    return pdb_lines


def run_command(cmd: str, cwd: str = None, check: bool = True):
    """Run a shell command with proper error handling."""
    print(f"  Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ERROR: Command failed with return code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        if check:
            raise RuntimeError(f"Command failed: {cmd}")
    return result


def build_complex(complex_name, ligand_dir=None):
    """
    Build a single protein-ligand complex with solvation and ions.
    
    Auto-detects binding site center from reference ligand if not already set.
    """
    info = COMPLEXES[complex_name].copy()
    complex_dir = MD_DIR / complex_name

    print(f"\n{'=' * 60}")
    print(f"Building complex: {complex_name}")
    print(f"{'=' * 60}")

    # Check prepared protein exists
    protein_file = complex_dir / f"{info['pdb']}_prepared.pdb"
    if not protein_file.exists():
        print(f"  ERROR: Prepared protein not found: {protein_file}")
        print("  Run md_prepare_proteins.py first")
        return False

    # Auto-detect binding site center if not set
    if info.get('binding_site_center') is None:
        reference_ligand = info.get('reference_ligand', 'NAD')
        center = extract_binding_site_center_from_pdb(protein_file, reference_ligand)
        
        if center:
            info['binding_site_center'] = center
            print("  Updated binding site center from reference ligand")
        else:
            print("  ERROR: Could not auto-detect binding site center")
            print(f"  Please manually set binding_site_center for {complex_name}")
            return False

    # Find ligand files
    ligand_name = info["ligand_name"]
    ligand_resname = info["ligand_resname"]

    # Look for ligand topology files from ACPYPE
    acpype_dir = None
    ligand_itp = None
    ligand_gro = None

    # Check multiple possible locations
    possible_locations = [
        ligand_dir / ligand_name if ligand_dir else None,
        complex_dir / "ligand" / ligand_name,
        complex_dir / "ligand" / f"{ligand_name}.acpype",
    ]

    for loc in possible_locations:
        if loc and loc.exists():
            if loc.is_dir():
                # Find the correct ligand ITP (GMX, not posre, not OPLS) and GRO
                for f in loc.rglob("*.itp"):
                    fname = f.name
                    if ligand_name in fname and fname.endswith("_GMX.itp") and "posre" not in fname:
                        ligand_itp = f
                        acpype_dir = f.parent
                for f in loc.rglob("*.gro"):
                    fname = f.name
                    if ligand_name in fname and fname.endswith("_GMX.gro"):
                        ligand_gro = f
            if ligand_itp and ligand_gro:
                break

    if not ligand_itp or not ligand_gro:
        print(f"  WARNING: Ligand topology files not found for {ligand_name}")
        print("  Expected: .itp and .gro files from ACPYPE")
        print("  Run md_prepare_ligands.py first, or provide --ligand-dir")
        return False

    print("  Found ligand files:")
    print(f"    ITP: {ligand_itp}")
    print(f"    GRO: {ligand_gro}")

    # Copy ligand files to complex directory
    dest_itp = complex_dir / f"{ligand_name}.itp"
    dest_gro = complex_dir / f"{ligand_name}.gro"
    shutil.copy2(ligand_itp, dest_itp)
    shutil.copy2(ligand_gro, dest_gro)

    # Step 1a: Fix missing atoms with pdbfixer
    print("\n  Step 1a: Fixing missing atoms with pdbfixer...")
    fixed_pdb = complex_dir / "protein_fixed.pdb"

    try:
        from pdbfixer import PDBFixer
        from openmm.app import PDBFile

        fixer = PDBFixer(filename=str(protein_file))
        fixer.findMissingResidues()
        fixer.findNonstandardResidues()
        fixer.replaceNonstandardResidues()
        fixer.findMissingAtoms()
        fixer.addMissingAtoms()
        fixer.addMissingHydrogens(7.0)

        with open(fixed_pdb, 'w') as f:
            PDBFile.writeFile(fixer.topology, fixer.positions, f)

        print(f"  Fixed PDB saved: {fixed_pdb}")
        protein_file_for_pdb2gmx = fixed_pdb
    except Exception as e:
        print(f"  WARNING: pdbfixer failed ({e}), trying original PDB")
        protein_file_for_pdb2gmx = protein_file

    # Step 1b: Generate protein topology with pdb2gmx
    print("\n  Step 1b: Generating protein topology with pdb2gmx...")
    protein_gro = complex_dir / "protein_processed.gro"
    protein_topol = complex_dir / "protein_topol.top"

    run_command(
        f'printf "1\\n1\\n1\\n1\\n" | gmx pdb2gmx -f {protein_file_for_pdb2gmx} -o {protein_gro} -p {protein_topol} -water tip3p -ff charmm36-jul2022 -ignh -ter',
        cwd=str(complex_dir),
    )

    if not protein_gro.exists():
        print(f"  ERROR: pdb2gmx failed for {complex_name}")
        return False

    # Extract the protein molecule name from pdb2gmx output
    protein_molname = None
    with open(protein_topol) as f:
        for line in f:
            line = line.strip()
            if line.startswith("[ molecules ]"):
                # Next non-empty, non-comment line is the molecule definition
                for next_line in f:
                    next_line = next_line.strip()
                    if next_line and not next_line.startswith(";"):
                        protein_molname = next_line.split()[0]
                        break
                break

    if not protein_molname:
        protein_molname = "Protein_chain_A"
        print(f"  WARNING: Could not parse protein molecule name, using: {protein_molname}")
    else:
        print(f"  Protein molecule name: {protein_molname}")

    # Step 2: Create combined complex PDB from protein_processed.gro (matches topology)
    print("\n  Step 2: Creating combined complex...")
    complex_pdb = complex_dir / "complex.pdb"

    # Convert protein_processed.gro to PDB format
    protein_gro_pdb = complex_dir / "protein_processed.pdb"
    run_command(
        f"gmx editconf -f {protein_gro} -o {protein_gro_pdb}",
        cwd=str(complex_dir),
    )

    protein_lines = [l for l in Path(protein_gro_pdb).read_text().splitlines(keepends=True)
                     if l.startswith(("ATOM", "HETATM", "TER"))]
    ligand_pdb_lines = gro_to_pdb_atoms(dest_gro, ligand_resname,
                                         info['binding_site_center'])
    if not ligand_pdb_lines:
        print(f"  ERROR: Could not convert ligand GRO to PDB atoms for {ligand_name}")
        return False

    with open(complex_pdb, "w") as f:
        f.writelines(protein_lines)
        f.write("TER\n")
        f.writelines(ligand_pdb_lines)
        f.write("END\n")

    print(f"  Created complex ({len(ligand_pdb_lines)} ligand atoms): {complex_pdb}")

    # Step 3: Create full topology (forcefield + water + protein + ligand + ions)
    print("\n  Step 3: Generating topology...")
    topol_top = complex_dir / "topol.top"

    # Build topology with correct GROMACS directive ordering:
    # 1. [ defaults ] (from forcefield)
    # 2. [ atomtypes ] (from forcefield + ligand)
    # 3. [ moleculetype ] (protein, then ligand)
    # Split protein_topol.top at [ moleculetype ] to insert ligand atomtypes before it
    # Also strip [ system ] and [ molecules ] sections (we define them ourselves)
    protein_lines = Path(protein_topol).read_text().splitlines()
    header_lines = []  # everything before [ moleculetype ]
    body_lines = []    # [ moleculetype ] and everything after, excluding [ system ] and [ molecules ]
    in_body = False
    skip_section = False
    for line in protein_lines:
        stripped = line.strip()
        if stripped.startswith("[ moleculetype ]"):
            in_body = True
        if stripped.startswith("[ system ]") or stripped.startswith("[ molecules ]"):
            skip_section = True
            continue
        if skip_section:
            if stripped.startswith("[") and not stripped.startswith(";"):
                skip_section = False
            else:
                continue
        if in_body:
            body_lines.append(line)
        else:
            header_lines.append(line)

    # Read ligand ITP and split into atomtypes section and the rest
    ligand_itp_lines = Path(dest_itp).read_text().splitlines()
    ligand_atomtypes = []
    ligand_rest = []
    in_atomtypes = False
    in_moleculetype = False
    for line in ligand_itp_lines:
        stripped = line.strip()
        if stripped.startswith("[ atomtypes ]"):
            in_atomtypes = True
            in_moleculetype = False
        elif stripped.startswith("[ moleculetype ]"):
            in_atomtypes = False
            in_moleculetype = True
        elif stripped.startswith("[") and not stripped.startswith(";"):
            in_atomtypes = False

        if in_atomtypes:
            ligand_atomtypes.append(line)
        elif in_moleculetype:
            ligand_rest.append(line)
        elif not in_atomtypes:
            # Lines before atomtypes or between atomtypes and moleculetype (e.g. comments)
            if not in_moleculetype:
                ligand_atomtypes.append(line)
            else:
                ligand_rest.append(line)

    # Extract ligand moleculetype name from the ITP
    ligand_molname = ligand_name  # fallback
    for i, line in enumerate(ligand_itp_lines):
        if line.strip().startswith("[ moleculetype ]"):
            # Next non-empty, non-comment line has the name
            for j in range(i + 1, min(i + 3, len(ligand_itp_lines))):
                l = ligand_itp_lines[j].strip()
                if l and not l.startswith(";"):
                    ligand_molname = l.split()[0]
                    break
            break
    print(f"  Ligand moleculetype name: {ligand_molname}")

    # Write topol.top with correct ordering
    with open(topol_top, "w") as f:
        # Header: forcefield, water, ions (from protein_topol.top)
        f.write("\n".join(header_lines) + "\n")
        # Ligand atomtypes (must be before any [ moleculetype ])
        if ligand_atomtypes:
            f.write("\n".join(ligand_atomtypes) + "\n")
        # Protein moleculetype
        f.write("\n".join(body_lines) + "\n")
        # Ligand moleculetype (without its atomtypes section)
        if ligand_rest:
            f.write("\n".join(ligand_rest) + "\n")
        # System and molecules
        f.write("\n[ system ]\n")
        f.write(f"; Name\n")
        f.write(f"{complex_name} in water\n")
        f.write("\n[ molecules ]\n")
        f.write("; Compound        #mols\n")
        f.write(f"{protein_molname}     1\n")
        f.write(f"{ligand_molname}           1\n")

    print(f"  Created topology: {topol_top}")

    # Step 4: Define box and solvate
    print("\n  Step 4: Defining simulation box...")
    boxed_gro = complex_dir / "complex_boxed.gro"

    run_command(
        f"gmx editconf -f {complex_pdb} -o {boxed_gro} -c -d 1.2 -bt dodecahedron",
        cwd=str(complex_dir),
    )

    print("\n  Step 5: Solvating system...")
    solvated_gro = complex_dir / "solvated.gro"

    run_command(
        f"gmx solvate -cp {boxed_gro} -cs spc216.gro -o {solvated_gro} -p {topol_top}",
        cwd=str(complex_dir),
    )

    if not solvated_gro.exists():
        print("  ERROR: Solvation failed")
        return False

    print(f"  Created solvated system: {solvated_gro}")

    # Step 6: Add ions
    print("\n  Step 6: Adding ions...")
    ions_gro = complex_dir / "ions.gro"
    ions_tpr = complex_dir / "ions.tpr"

    # Create ions.mdp
    ions_mdp = complex_dir / "ions.mdp"
    with open(ions_mdp, "w") as f:
        f.write("""
; Ions mdp file
integrator  = steep
emtol       = 1000.0
emstep      = 0.01
nsteps      = 50000
""")

    # Generate tpr for ion addition
    run_command(
        f"gmx grompp -f {ions_mdp} -c {solvated_gro} -p {topol_top} -o {ions_tpr} -maxwarn 5",
        cwd=str(complex_dir),
    )

    # Add ions (neutralize + 0.15 M NaCl) automatically
    run_command(
        f'echo "SOL" | gmx genion -s {ions_tpr} -o {ions_gro} -p {topol_top} -pname NA -nname CL -conc 0.15 -neutral',
        cwd=str(complex_dir),
    )

    if ions_gro.exists():
        print(f"  Successfully added ions: {ions_gro}")
    else:
        print("  ERROR: Ion addition failed")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Build MD simulation complexes")
    parser.add_argument(
        "--ligand-dir",
        type=str,
        default=None,
        help="Directory containing ligand topology files",
    )
    parser.add_argument(
        "--complex", type=str, default="all", help='Complex to build (or "all" for all)'
    )
    args = parser.parse_args()

    ligand_dir = Path(args.ligand_dir) if args.ligand_dir else None

    print("=" * 60)
    print("MD Complex Building")
    print("=" * 60)

    if args.complex == "all":
        for complex_name in COMPLEXES:
            try:
                build_complex(complex_name, ligand_dir)
            except Exception as e:
                print(f"  ERROR building {complex_name}: {e}")
    else:
        if args.complex in COMPLEXES:
            build_complex(args.complex, ligand_dir)
        else:
            print(f"ERROR: Unknown complex '{args.complex}'")
            print(f"Available: {', '.join(COMPLEXES.keys())}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Complex building complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run add_ions.sh for each complex to add ions")
    print("  2. Verify solvated.gro and topol.top exist for each complex")
    print("  3. Proceed with energy minimisation")


if __name__ == "__main__":
    main()
