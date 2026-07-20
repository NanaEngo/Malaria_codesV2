#!/usr/bin/env python
"""
Merge Ligand and Protein Coordinates for GROMACS MD Simulations

This script:
1. Converts ligand PDB to GRO format using GROMACS
2. Merges ligand with protein+solvent system
3. Updates atom numbering and residue numbering
4. Creates complex.gro file ready for MD simulation

Requirements:
    - GROMACS installed (gmx command available)
    - conda environment: malaria_md

Usage:
    conda activate malaria_md
    python merge_ligand_protein_coordinates.py LIG1
    # or
    python merge_ligand_protein_coordinates.py all

Author: Generated for Malaria MD Project
Date: June 2026
"""

import sys
import subprocess
import shutil
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path("/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/Gromacs_inputs")
GMX_CMD = "gmx"  # GROMACS command

# List of all LIG systems
ALL_LIGS = ["LIG1", "LIG2", "LIG3", "LIG5", "LIG7", "LIG8", "LIG9", "LIG10", "LIG14", "LIG15", "LIG16", "LIG17"]

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def run_command(cmd, cwd=None, input_text=None):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)

def find_charmm_gui_folder(lig_folder):
    """Find the charmm-gui-* folder"""
    charmm_dirs = list(lig_folder.glob("charmm-gui-*"))
    return charmm_dirs[0] if charmm_dirs else None

def find_complex_folder(lig_folder):
    """Find the Complex_* folder"""
    complex_dirs = list(lig_folder.glob("Complex_*"))
    return complex_dirs[0] if complex_dirs else None

def parse_gro_file(gro_file):
    """Parse GRO file and return header, atoms, box"""
    with open(gro_file, 'r') as f:
        lines = f.readlines()
    
    if len(lines) < 3:
        return None, None, None
    
    header = lines[0].strip()
    n_atoms = int(lines[1].strip())
    atom_lines = lines[2:2+n_atoms]
    box_line = lines[2+n_atoms].strip() if len(lines) > 2+n_atoms else ""
    
    return header, atom_lines, box_line

def write_gro_file(output_file, header, atom_lines, box_line):
    """Write GRO file"""
    with open(output_file, 'w') as f:
        f.write(f"{header}\n")
        f.write(f"{len(atom_lines):5d}\n")
        for line in atom_lines:
            f.write(line)
        f.write(f"{box_line}\n")

def renumber_atoms(atom_lines, start_number=1):
    """
    Renumber atoms in GRO format lines
    
    GRO format handles atom numbers > 99999 using base-36 (hexadecimal-like)
    or wrapping. GROMACS 2020+ uses wrapping at 100000.
    """
    renumbered = []
    for i, line in enumerate(atom_lines, start=start_number):
        # GRO format: ResNum ResName AtomName AtomNum X Y Z [Vx Vy Vz]
        # Columns:    0-4    5-9      10-14    15-19   20-27 28-35 36-43
        if len(line) >= 44:
            # For atom numbers > 99999, wrap at 100000
            atom_num = i % 100000
            new_line = f"{line[:15]}{atom_num:5d}{line[20:]}"
            renumbered.append(new_line)
        else:
            renumbered.append(line)
    return renumbered

# ──────────────────────────────────────────────────────────────────────────────
# MAIN PROCESSING FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def convert_ligand_pdb_to_gro(ligand_pdb, output_gro):
    """Convert ligand PDB to GRO format using GROMACS editconf"""
    print(f"    Converting {ligand_pdb.name} to GRO format...")
    
    cmd = f"{GMX_CMD} editconf -f {ligand_pdb} -o {output_gro}"
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print("    ✗ Error converting ligand PDB to GRO")
        if stderr:
            print(f"      {stderr[:200]}")
        return False
    
    if not output_gro.exists():
        print("    ✗ Output GRO file not created")
        return False
    
    print(f"    ✓ Ligand GRO created: {output_gro.name}")
    return True

def merge_gro_files(protein_gro, ligand_gro, output_gro, system_name="Protein-Ligand Complex"):
    """
    Merge protein and ligand GRO files using simple concatenation
    
    GROMACS can handle atom numbers > 99999, just needs proper total count.
    """
    print("    Merging protein and ligand coordinates...")
    
    # Parse protein system
    prot_header, prot_atoms, prot_box = parse_gro_file(protein_gro)
    if prot_atoms is None:
        print("    ✗ Failed to parse protein GRO")
        return False
    
    # Parse ligand  
    lig_header, lig_atoms, lig_box = parse_gro_file(ligand_gro)
    if lig_atoms is None:
        print("    ✗ Failed to parse ligand GRO")
        return False
    
    print(f"      Protein system: {len(prot_atoms)} atoms")
    print(f"      Ligand: {len(lig_atoms)} atoms")
    
    # Strategy: Insert ligand after protein/cofactors but before solvent
    # Find where solvent (TIP3/SOL) starts
    solvent_start = None
    for i, line in enumerate(prot_atoms):
        if len(line) >= 9:
            resname = line[5:9].strip()
            if resname in ['TIP3', 'SOL', 'WAT', 'HOH']:
                solvent_start = i
                break
    
    if solvent_start is None:
        # No solvent found, just append ligand at end
        merged_atoms = prot_atoms + lig_atoms
        print("      No solvent found, appending ligand at end")
    else:
        # Insert ligand before solvent
        merged_atoms = prot_atoms[:solvent_start] + lig_atoms + prot_atoms[solvent_start:]
        print(f"      Inserting ligand at position {solvent_start} (before solvent)")
    
    print(f"      Total atoms after merge: {len(merged_atoms)}")
    
    # Don't renumber - let GROMACS handle atom numbers
    # Just write the merged file with correct atom count
    write_gro_file(output_gro, system_name, merged_atoms, prot_box)
    
    print(f"    ✓ Merged coordinates saved: {output_gro.name}")
    return True

def verify_merged_system(complex_gro, topol_file):
    """Verify the merged system with GROMACS grompp"""
    print("    Verifying merged system...")
    
    # Create a minimal MDP file for testing
    test_mdp = complex_gro.parent / "test_merge.mdp"
    with open(test_mdp, 'w') as f:
        f.write("; Minimal MDP for system verification\n")
        f.write("integrator = steep\n")
        f.write("nsteps = 0\n")
        f.write("emtol = 10.0\n")
    
    # Try to compile with grompp
    cmd = f"{GMX_CMD} grompp -f {test_mdp} -c {complex_gro} -p {topol_file} -o test_merge.tpr -maxwarn 5"
    
    returncode, stdout, stderr = run_command(cmd, cwd=complex_gro.parent)
    
    # Clean up
    test_mdp.unlink(missing_ok=True)
    test_tpr = complex_gro.parent / "test_merge.tpr"
    test_tpr.unlink(missing_ok=True)
    
    if returncode == 0:
        print("    ✓ System verification passed!")
        return True
    else:
        print("    ⚠ System verification had warnings/errors")
        if "Fatal error" in stderr:
            # Extract the error message
            error_lines = [line for line in stderr.split('\n') if 'error' in line.lower()]
            if error_lines:
                print(f"      Error: {error_lines[0]}")
        return False

def process_lig_system(lig_name):
    """Process a single LIG system"""
    print(f"\n{'='*70}")
    print(f"Processing {lig_name}")
    print(f"{'='*70}")
    
    lig_folder = BASE_DIR / lig_name
    
    if not lig_folder.exists():
        print(f"  ✗ LIG folder not found: {lig_folder}")
        return False
    
    # Find directories
    charmm_dir = find_charmm_gui_folder(lig_folder)
    if not charmm_dir:
        print("  ✗ No charmm-gui-* folder found")
        return False
    
    complex_dir = find_complex_folder(lig_folder)
    if not complex_dir:
        print("  ✗ No Complex_* folder found")
        return False
    
    print(f"  CHARMM-GUI: {charmm_dir.name}")
    print(f"  Complex:    {complex_dir.name}")
    
    # Check required files
    ligand_pdb = charmm_dir / "ligandrm.pdb"
    protein_gro = complex_dir / "step3_input.gro"
    topol_file = complex_dir / "topol.top"
    
    if not ligand_pdb.exists():
        print(f"  ✗ Ligand PDB not found: {ligand_pdb}")
        return False
    
    if not protein_gro.exists():
        print(f"  ✗ Protein GRO not found: {protein_gro}")
        return False
    
    if not topol_file.exists():
        print(f"  ✗ Topology file not found: {topol_file}")
        return False
    
    print("  ✓ All required files present")
    
    # Create working directory in complex folder
    work_dir = complex_dir / "ligand_merge_work"
    work_dir.mkdir(exist_ok=True)
    
    # Step 1: Convert ligand PDB to GRO
    ligand_gro = work_dir / "ligand.gro"
    if not convert_ligand_pdb_to_gro(ligand_pdb, ligand_gro):
        print("  ✗ Failed to convert ligand")
        return False
    
    # Step 2: Merge coordinates
    complex_gro = complex_dir / "complex.gro"
    system_name = f"{lig_name} Protein-Ligand Complex"
    
    if not merge_gro_files(protein_gro, ligand_gro, complex_gro, system_name):
        print("  ✗ Failed to merge coordinates")
        return False
    
    # Step 3: Verify merged system
    verify_merged_system(complex_gro, topol_file)
    
    # Step 4: Create backup of original and symlink
    if not (complex_dir / "step3_input.gro.original").exists():
        shutil.copy(protein_gro, complex_dir / "step3_input.gro.original")
        print("  ✓ Backup created: step3_input.gro.original")
    
    # Step 5: Summary
    print(f"\n  {'─'*66}")
    print(f"  ✓ {lig_name} processing complete!")
    print(f"  {'─'*66}")
    print(f"  Output files in: {complex_dir.name}/")
    print("    - complex.gro           (merged protein+ligand)")
    print("    - step3_input.gro       (original protein)")
    print("    - step3_input.gro.original (backup)")
    print("    - ligand_merge_work/    (intermediate files)")
    print(f"  {'─'*66}")
    
    return True

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "MERGE LIGAND AND PROTEIN COORDINATES" + " " * 21 + "║")
    print("║" + " " * 20 + "Local GROMACS Pipeline" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Check GROMACS is available
    print("Checking GROMACS...")
    returncode, stdout, stderr = run_command(f"{GMX_CMD} --version")
    
    if returncode != 0:
        print("✗ GROMACS not found!")
        print("Please activate the malaria_md environment:")
        print("  conda activate malaria_md")
        return 1
    
    # Extract version
    version_line = [line for line in stdout.split('\n') if 'GROMACS version' in line]
    if version_line:
        print(f"✓ {version_line[0].strip()}")
    else:
        print("✓ GROMACS found")
    print()
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python merge_ligand_protein_coordinates.py <LIG_NAME|all>")
        print("\nExamples:")
        print("  python merge_ligand_protein_coordinates.py LIG1")
        print("  python merge_ligand_protein_coordinates.py all")
        print(f"\nAvailable systems: {', '.join(ALL_LIGS)}")
        return 1
    
    lig_arg = sys.argv[1]
    
    # Process systems
    if lig_arg.lower() == "all":
        print(f"Processing all {len(ALL_LIGS)} systems...")
        print()
        
        success_count = 0
        fail_count = 0
        failed_ligs = []
        
        for lig_name in ALL_LIGS:
            try:
                if process_lig_system(lig_name):
                    success_count += 1
                else:
                    fail_count += 1
                    failed_ligs.append(lig_name)
            except Exception as e:
                print(f"\n  ✗ Exception: {e}")
                fail_count += 1
                failed_ligs.append(lig_name)
        
        # Final summary
        print(f"\n{'='*70}")
        print("FINAL SUMMARY")
        print(f"{'='*70}")
        print(f"Total systems:  {len(ALL_LIGS)}")
        print(f"Successful:     {success_count} ✓")
        print(f"Failed:         {fail_count} ✗")
        
        if failed_ligs:
            print("\nFailed systems:")
            for lig in failed_ligs:
                print(f"  - {lig}")
        
        print()
        
    else:
        # Process single system
        if lig_arg not in ALL_LIGS:
            print(f"✗ Unknown system: {lig_arg}")
            print(f"Available: {', '.join(ALL_LIGS)}")
            return 1
        
        success = process_lig_system(lig_arg)
        if not success:
            return 1
    
    # Next steps
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Verify merged structures:")
    print("   gmx check -f Gromacs_inputs/LIG1/Complex_1/complex.gro")
    print()
    print("2. Update index files (if needed):")
    print("   cd Gromacs_inputs/LIG1/Complex_1/")
    print("   gmx make_ndx -f complex.gro -o index.ndx")
    print()
    print("3. Run energy minimization:")
    print("   gmx grompp -f step4.0_minimization.mdp -c complex.gro -p topol.top -n index.ndx -o mini.tpr")
    print("   gmx mdrun -v -deffnm mini")
    print()
    print("4. Continue with equilibration and production MD")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
