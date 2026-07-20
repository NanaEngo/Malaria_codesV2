"""
STEP 2B: GROMACS Topology Generation — Server-Side
===================================================
Project: Resistance-Resilient Polypharmacological Antimalarials

WHAT THIS SCRIPT DOES
---------------------
1. Validates that required PDB files exist from step2_protein_prep.py
2. Runs GROMACS pdb2gmx on the server
3. Generates topology files (.top, .gro, .itp)
4. Validates output files
5. Provides summary for next steps

PREREQUISITES
-------------
- Run step2_protein_prep.py locally first
- Upload protein_prep directory to server
- GROMACS 2025 installed on server
- Access to server via SSH

REQUIRED FILES
--------------
protein_prep/{PDB_ID}_chainX_noH.pdb  (or _fixed.pdb)

OUTPUT FILES
------------
protein_prep/{PDB_ID}_processed.gro   (coordinate file)
protein_prep/{PDB_ID}.top             (topology)
protein_prep/{PDB_ID}_posre.itp       (position restraints)

USAGE
-----
Server:
  python step2b_topology_generation.py

Or with custom parameters:
  python step2b_topology_generation.py --pdb 7YF3 --chain A --ff charmm36m
"""

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────

PDB_ID         = "7F3Y"
CHAIN          = "A"
OUTPUT_DIR     = "protein_prep"
FORCE_FIELD    = "charmm36m"      # Options: charmm36m, amber99sb-ildn, oplsaa
WATER_MODEL    = "tip3p"          # Options: tip3p, tip4p, tip5p, spc, spce
USE_PDBFIXER_H = False            # True: keep PDBFixer H, False: let GROMACS add H
INTERACTIVE    = True             # Set to False for fully automated runs

# ──────────────────────────────────────────────────────────────────────────────

import sys
import subprocess
import argparse
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# PARSE COMMAND LINE ARGUMENTS
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate GROMACS topology for prepared protein structure"
    )
    
    parser.add_argument(
        '--pdb',
        default=PDB_ID,
        help=f'PDB ID (default: {PDB_ID})'
    )
    
    parser.add_argument(
        '--chain',
        default=CHAIN,
        help=f'Chain ID (default: {CHAIN})'
    )
    
    parser.add_argument(
        '--ff',
        default=FORCE_FIELD,
        choices=['charmm36m', 'amber99sb-ildn', 'oplsaa', 'amber03', 'gromos54a7'],
        help=f'Force field (default: {FORCE_FIELD})'
    )
    
    parser.add_argument(
        '--water',
        default=WATER_MODEL,
        choices=['tip3p', 'tip4p', 'tip5p', 'spc', 'spce'],
        help=f'Water model (default: {WATER_MODEL})'
    )
    
    parser.add_argument(
        '--use-pdbfixer-h',
        action='store_true',
        help='Use hydrogens from PDBFixer instead of letting GROMACS add them'
    )
    
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run in non-interactive mode (auto-select defaults for his/ter)'
    )
    
    parser.add_argument(
        '--output-dir',
        default=OUTPUT_DIR,
        help=f'Output directory (default: {OUTPUT_DIR})'
    )
    
    return parser.parse_args()

# ──────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ──────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    
    print("=" * 70)
    print("STEP 2B: GROMACS TOPOLOGY GENERATION")
    print("=" * 70)
    print(f"PDB ID:      {args.pdb}")
    print(f"Chain:       {args.chain}")
    print(f"Force Field: {args.ff}")
    print(f"Water Model: {args.water}")
    print(f"Output Dir:  {args.output_dir}")
    print()
    
    # ──────────────────────────────────────────────────────────────────────────
    # STEP 1 — VALIDATE ENVIRONMENT
    # ──────────────────────────────────────────────────────────────────────────
    
    print("=" * 70)
    print("STEP 1: Validate Environment")
    print("=" * 70)
    
    # Check if GROMACS is installed
    try:
        result = subprocess.run(
            ['gmx', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Extract version info
            for line in result.stdout.split('\n'):
                if 'GROMACS version' in line:
                    print(f"✓ {line.strip()}")
                    break
        else:
            print("✗ GROMACS not found or not working properly")
            print("Install GROMACS 2025 or ensure it's in PATH")
            sys.exit(1)
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ GROMACS (gmx) not found in PATH")
        print("Please install GROMACS 2025 or add it to PATH")
        sys.exit(1)
    
    # Check if output directory exists
    output_path = Path(args.output_dir)
    if not output_path.exists():
        print(f"✗ Output directory not found: {args.output_dir}")
        print("Run step2_protein_prep.py first and upload the protein_prep directory")
        sys.exit(1)
    else:
        print(f"✓ Output directory exists: {args.output_dir}")
    
    # ──────────────────────────────────────────────────────────────────────────
    # STEP 2 — FIND INPUT PDB FILE
    # ──────────────────────────────────────────────────────────────────────────
    
    print()
    print("=" * 70)
    print("STEP 2: Locate Input PDB File")
    print("=" * 70)
    
    chain_suffix = f"_chain{args.chain}" if args.chain else ""
    
    # Determine which input file to use
    if args.use_pdbfixer_h:
        input_pdb = output_path / f"{args.pdb}{chain_suffix}_fixed.pdb"
        h_mode = "using PDBFixer hydrogens"
    else:
        input_pdb = output_path / f"{args.pdb}{chain_suffix}_noH.pdb"
        h_mode = "GROMACS will add hydrogens"
    
    if not input_pdb.exists():
        print(f"✗ Input file not found: {input_pdb}")
        print("\nAvailable PDB files in protein_prep directory:")
        
        for pdb_file in output_path.glob("*.pdb"):
            print(f"  - {pdb_file.name}")
        
        print("\nRun step2_protein_prep.py first to generate input files")
        sys.exit(1)
    
    print(f"✓ Input file found: {input_pdb.name}")
    print(f"✓ Hydrogen mode: {h_mode}")
    
    # ──────────────────────────────────────────────────────────────────────────
    # STEP 3 — RUN GROMACS pdb2gmx
    # ──────────────────────────────────────────────────────────────────────────
    
    print()
    print("=" * 70)
    print("STEP 3: Generate Topology with pdb2gmx")
    print("=" * 70)
    
    # Define output files
    output_gro = output_path / f"{args.pdb}_processed.gro"
    output_top = output_path / f"{args.pdb}.top"
    output_itp = output_path / f"{args.pdb}_posre.itp"
    
    # Build pdb2gmx command
    cmd = [
        'gmx', 'pdb2gmx',
        '-f', str(input_pdb),
        '-o', str(output_gro),
        '-p', str(output_top),
        '-i', str(output_itp),
        '-water', args.water,
        '-ff', args.ff
    ]
    
    # Add -ignh flag if not using PDBFixer hydrogens
    if not args.use_pdbfixer_h:
        cmd.append('-ignh')
    
    print("\nCommand:")
    print(' '.join(cmd))
    print()
    
    # Prepare stdin input for non-interactive mode
    stdin_input = None
    if args.non_interactive:
        print("Running in non-interactive mode...")
        print("Using default selections for histidine and terminal groups")
        # For most proteins: 0 = neutral histidine, 0 = default terminals
        stdin_input = "0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n"
    else:
        print("Running in interactive mode...")
        print("\nNOTES:")
        print("- GROMACS will ask about histidine protonation states")
        print("- Refer to step2_protein_prep.py output for pH-based recommendations")
        print("- Common choices:")
        print("    0: Neutral (HIE - epsilon protonated)")
        print("    1: Neutral (HID - delta protonated)")
        print("    2: Protonated (HIP - doubly protonated, +1 charge)")
        print("- GROMACS will also ask about N-terminus and C-terminus")
        print()
    
    try:
        # Run pdb2gmx
        if stdin_input:
            result = subprocess.run(
                cmd,
                input=stdin_input,
                text=True,
                capture_output=True,
                timeout=120
            )
        else:
            result = subprocess.run(
                cmd,
                text=True,
                timeout=120
            )
        
        # Check result
        if result.returncode == 0:
            print("\n✓ pdb2gmx completed successfully")
        else:
            print("\n✗ pdb2gmx failed")
            if hasattr(result, 'stderr') and result.stderr:
                print("\nError output:")
                print(result.stderr)
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("\n✗ pdb2gmx timed out")
        print("Try running with --non-interactive flag")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error running pdb2gmx: {e}")
        sys.exit(1)
    
    # ──────────────────────────────────────────────────────────────────────────
    # STEP 4 — VALIDATE OUTPUT FILES
    # ──────────────────────────────────────────────────────────────────────────
    
    print()
    print("=" * 70)
    print("STEP 4: Validate Output Files")
    print("=" * 70)
    
    all_good = True
    
    # Check GRO file
    if output_gro.exists():
        size = output_gro.stat().st_size
        print(f"✓ Coordinate file created: {output_gro.name} ({size:,} bytes)")
        
        # Count atoms in GRO file
        with open(output_gro) as f:
            lines = f.readlines()
            if len(lines) > 2:
                try:
                    n_atoms = int(lines[1].strip())
                    print(f"  Contains {n_atoms:,} atoms")
                except ValueError:
                    pass
    else:
        print(f"✗ Coordinate file missing: {output_gro.name}")
        all_good = False
    
    # Check TOP file
    if output_top.exists():
        size = output_top.stat().st_size
        print(f"✓ Topology file created: {output_top.name} ({size:,} bytes)")
        
        # Parse topology info
        with open(output_top) as f:
            for line in f:
                if 'Protein_chain_' in line or 'Protein' in line:
                    print(f"  {line.strip()}")
                    break
    else:
        print(f"✗ Topology file missing: {output_top.name}")
        all_good = False
    
    # Check ITP file
    if output_itp.exists():
        size = output_itp.stat().st_size
        print(f"✓ Position restraint file created: {output_itp.name} ({size:,} bytes)")
    else:
        print(f"✗ Position restraint file missing: {output_itp.name}")
        all_good = False
    
    # ──────────────────────────────────────────────────────────────────────────
    # FINAL SUMMARY
    # ──────────────────────────────────────────────────────────────────────────
    
    print()
    print("=" * 70)
    print("STEP 2B COMPLETE" if all_good else "STEP 2B INCOMPLETE")
    print("=" * 70)
    
    if all_good:
        print("\n✓ All topology files generated successfully")
        print("\nOUTPUT FILES:")
        print(f"  {output_gro}")
        print(f"  {output_top}")
        print(f"  {output_itp}")
        
        print("\nNEXT STEPS:")
        print("-" * 70)
        print("1. Download topology files to local machine (optional)")
        print("2. Proceed to step3_complex_assembly.py:")
        print("   - Build simulation box")
        print("   - Solvate with water")
        print("   - Add ions (neutralize)")
        print("   - Energy minimization")
        print("   - Equilibration (NVT, NPT)")
        print("   - Production MD")
        
        print("\nQUICK CHECK:")
        print("-" * 70)
        print(f"  gmx check -f {output_gro}")
        print(f"  gmx editconf -f {output_gro} -o {args.pdb}_visual.pdb")
        
    else:
        print("\n✗ Some output files are missing")
        print("Check error messages above and retry")
        sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
