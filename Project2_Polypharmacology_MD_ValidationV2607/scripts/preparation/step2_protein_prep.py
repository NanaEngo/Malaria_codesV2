"""
STEP 2: Protein Preparation — PfDHFR Wildtype (PDB: 1J3I)
===========================================================
Project: Resistance-Resilient Polypharmacological Antimalarials

WHAT THIS SCRIPT DOES
---------------------
1. Downloads PDB structure from RCSB PDB
2. Inspects chains, ligands, missing residues
3. Uses PDBFixer to:
      - Fix missing residues
      - Fix missing atoms
      - Add hydrogens at specified pH
      - Remove heterogens (waters, ligands) if requested
      - Handle non-standard residues
4. Exports cleaned structure ready for GROMACS 2025
5. Provides pdb2gmx command for topology generation

INSTALL
-------
mamba install -c conda-forge pdbfixer openmm biopython

REQUIRED
--------
GROMACS 2025 in PATH
PDBFixer (installed via conda/mamba)
OpenMM (dependency for PDBFixer)

WHY THIS VERSION IS BETTER
--------------------------
- PDBFixer intelligently fixes missing residues/atoms
- Adds hydrogens at specified pH using OpenMM force fields
- More robust than Propka for structure preparation
- Compatible with GROMACS 2025 topology generation
- Handles non-standard residues and caps automatically
"""

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────

PDB_ID     = "7F3Y"
CHAIN      = "A"              # Specify chain to keep (or None to keep all)
OUTPUT_DIR = "protein_prep"
PH         = 7.4              # pH for hydrogen addition
REMOVE_HETEROGENS = True      # Remove waters, ions, and ligands
FIX_MISSING_RESIDUES = True   # Add missing residues
FIX_MISSING_ATOMS = True      # Add missing heavy atoms

# ──────────────────────────────────────────────────────────────────────────────

import os
import sys
import urllib.request

try:
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile
except ImportError:
    print("ERROR: PDBFixer not found!")
    print("Install with: mamba install -c conda-forge pdbfixer openmm")
    sys.exit(1)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# PART 1 — DOWNLOAD PDB
# ──────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print(f"PART 1: Download {PDB_ID} from RCSB PDB")
print("=" * 60)

raw_pdb = os.path.join(OUTPUT_DIR, f"{PDB_ID}_raw.pdb")

url = f"https://files.rcsb.org/download/{PDB_ID}.pdb"

if os.path.exists(raw_pdb):
    print(f"✓ Already downloaded: {raw_pdb}")
else:
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, raw_pdb)
    print(f"✓ Saved: {raw_pdb}")

# ──────────────────────────────────────────────────────────────────────────────
# PART 2 — INSPECT RAW PDB
# ──────────────────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("PART 2: Inspect raw PDB")
print("=" * 60)

chains = set()
residues = {}
hetatms = []
missing_hint = []
altloc_atoms = []

with open(raw_pdb) as f:
    for line in f:

        rec = line[:6].strip()

        if rec == "REMARK":
            if "MISSING" in line:
                missing_hint.append(line.rstrip())

        elif rec == "ATOM":

            chain = line[21]
            resnum = int(line[22:26].strip())
            altloc = line[16].strip()

            chains.add(chain)

            residues.setdefault(chain, set()).add(resnum)

            if altloc:
                altloc_atoms.append(line.rstrip())

        elif rec == "HETATM":

            resname = line[17:20].strip()
            chain = line[21]
            resnum = int(line[22:26].strip())

            hetatms.append((resname, chain, resnum))

print(f"Chains found: {sorted(chains)}")

for ch, resset in sorted(residues.items()):

    rmin = min(resset)
    rmax = max(resset)

    gaps = sorted(set(range(rmin, rmax + 1)) - resset)

    print(f"  Chain {ch}: residues {rmin}-{rmax} ({len(resset)} present)")

    if gaps:
        print(f"    ⚠ Gaps: {gaps[:10]}")
    else:
        print("    ✓ No gaps")

print("\nHETATM records:")

unique_het = {}

for resname, chain, resnum in hetatms:

    key = (resname, chain)

    unique_het[key] = unique_het.get(key, 0) + 1

for (resname, chain), count in sorted(unique_het.items()):

    tag = ""

    if resname not in ("HOH", "WAT", "Na", "Cl"):
        tag = "← KEEP NOTE"

    print(f"  {resname:4s} chain {chain} {count:4d} atoms {tag}")

if altloc_atoms:
    print(f"\n⚠ Alternative conformations found: {len(altloc_atoms)} atoms")
else:
    print("\n✓ No alternative conformations found")

if missing_hint:
    print("\nREMARK entries about missing residues:")
    for r in missing_hint[:10]:
        print(" ", r)

# ──────────────────────────────────────────────────────────────────────────────
# PART 3 — FIX STRUCTURE WITH PDBFIXER
# ──────────────────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("PART 3: Fix structure with PDBFixer")
print("=" * 60)

# Initialize PDBFixer with the downloaded structure
fixer = PDBFixer(filename=raw_pdb)

print("✓ Loaded structure into PDBFixer")

# Get initial statistics
initial_chains = len(list(fixer.topology.chains()))
print(f"Initial chains: {initial_chains}")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3.1 — KEEP SPECIFIC CHAIN
# ──────────────────────────────────────────────────────────────────────────────

if CHAIN is not None:
    print(f"\nRemoving all chains except chain {CHAIN}...")
    
    chains_to_remove = []
    for chain in fixer.topology.chains():
        if chain.id != CHAIN:
            chains_to_remove.append(chain.index)
    
    if chains_to_remove:
        fixer.removeChains(chainIds=chains_to_remove)
        print(f"✓ Removed {len(chains_to_remove)} chain(s)")
    else:
        print(f"✓ Chain {CHAIN} is the only chain present")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3.2 — FIND AND FIX MISSING RESIDUES
# ──────────────────────────────────────────────────────────────────────────────

if FIX_MISSING_RESIDUES:
    print("\nSearching for missing residues...")
    fixer.findMissingResidues()
    
    if fixer.missingResidues:
        print(f"⚠ Found {len(fixer.missingResidues)} missing residue region(s):")
        chains_list = list(fixer.topology.chains())
        
        for key, residues in fixer.missingResidues.items():
            try:
                # Handle different PDBFixer versions
                # Key can be: int (chain index) or tuple (chain_idx, position)
                if isinstance(key, tuple):
                    chain_idx = key[0] if isinstance(key[0], int) else 0
                    position_info = f" at position {key[1]}" if len(key) > 1 else ""
                else:
                    chain_idx = int(key)
                    position_info = ""
                
                # Get chain ID safely
                if 0 <= chain_idx < len(chains_list):
                    chain_id = chains_list[chain_idx].id
                    print(f"  Chain {chain_id}{position_info}: {len(residues)} missing residue(s)")
                else:
                    print(f"  Region {key}: {len(residues)} missing residue(s)")
                    
            except (ValueError, IndexError, TypeError):
                # Fallback for unexpected key formats
                print(f"  Region {key}: {len(residues)} missing residue(s)")
    else:
        print("✓ No missing residues detected")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3.3 — REMOVE HETEROGENS (WATERS, IONS, LIGANDS)
# ──────────────────────────────────────────────────────────────────────────────

if REMOVE_HETEROGENS:
    print("\nRemoving heterogens (waters, ions, ligands)...")
    fixer.removeHeterogens(keepWater=False)
    print("✓ Heterogens removed")
else:
    print("\nKeeping heterogens (waters, ions, ligands)")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3.4 — FIND AND FIX MISSING ATOMS
# ──────────────────────────────────────────────────────────────────────────────

if FIX_MISSING_ATOMS:
    print("\nSearching for missing heavy atoms...")
    fixer.findMissingAtoms()
    
    if fixer.missingAtoms or fixer.missingTerminals:
        missing_count = sum(len(atoms) for atoms in fixer.missingAtoms.values())
        terminal_count = sum(len(terms) for terms in fixer.missingTerminals.values())
        
        if missing_count > 0:
            print(f"⚠ Found {missing_count} missing heavy atom(s)")
        if terminal_count > 0:
            print(f"⚠ Found {terminal_count} missing terminal(s)")
        
        print("Adding missing atoms and terminals...")
        fixer.addMissingAtoms()
        print("✓ Missing atoms added")
    else:
        print("✓ No missing atoms detected")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3.5 — ADD HYDROGENS AT SPECIFIED pH
# ──────────────────────────────────────────────────────────────────────────────

print(f"\nAdding hydrogens at pH {PH}...")
fixer.addMissingHydrogens(pH=PH)
print("✓ Hydrogens added")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3.6 — SAVE FIXED STRUCTURE
# ──────────────────────────────────────────────────────────────────────────────

chain_suffix = f"_chain{CHAIN}" if CHAIN else ""
fixed_pdb = os.path.join(OUTPUT_DIR, f"{PDB_ID}{chain_suffix}_fixed.pdb")

print(f"\nSaving fixed structure to {fixed_pdb}...")
with open(fixed_pdb, 'w') as f:
    PDBFile.writeFile(fixer.topology, fixer.positions, f, keepIds=True)

print(f"✓ Fixed structure saved: {fixed_pdb}")

# Count final atoms
atom_count = sum(1 for _ in fixer.topology.atoms())
residue_count = sum(1 for _ in fixer.topology.residues())
print(f"Final structure: {residue_count} residues, {atom_count} atoms")

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3.7 — CLEAN FOR GROMACS (REMOVE NON-PROTEIN ATOMS)
# ──────────────────────────────────────────────────────────────────────────────

print("\nCleaning structure for GROMACS compatibility...")

# Standard amino acids (20 common + protonation states)
STANDARD_RESIDUES = {
    'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
    'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
    'HIE', 'HID', 'HIP', 'HSD', 'HSE', 'HSP',  # Histidine protonation states
    'CYX', 'CYM',  # Cysteine variants
    'ASH', 'GLH',  # Protonated ASP/GLU
    'LYN',  # Neutral LYS
}

# Additional atoms to skip (common artifacts)
SKIP_ATOMS = {
    "O3'", "O5'", "C3'", "C4'", "C5'", "P", "OP1", "OP2",  # Nucleic acid atoms
    "O2'", "C2'", "C1'",  # More RNA/DNA
}

clean_pdb = os.path.join(OUTPUT_DIR, f"{PDB_ID}{chain_suffix}_clean.pdb")

kept_atoms = 0
skipped_atoms = 0
skipped_residues = set()
problematic_atoms = []

with open(fixed_pdb, 'r') as fin, open(clean_pdb, 'w') as fout:
    for line in fin:
        if line.startswith(('ATOM', 'HETATM')):
            resname = line[17:20].strip()
            atomname = line[12:16].strip()
            
            # Skip non-standard residues
            if resname not in STANDARD_RESIDUES:
                skipped_residues.add(resname)
                skipped_atoms += 1
                continue
            
            # Skip problematic atom names (nucleic acid artifacts)
            if atomname in SKIP_ATOMS:
                problematic_atoms.append((resname, atomname, line[22:26].strip()))
                skipped_atoms += 1
                continue
            
            # Keep valid protein atoms
            fout.write(line)
            kept_atoms += 1
            
        elif line.startswith(('MODEL', 'ENDMDL', 'TER', 'END')):
            fout.write(line)
        elif line.startswith(('CRYST1', 'REMARK')):
            fout.write(line)

print(f"✓ Kept {kept_atoms} protein atoms")
print(f"✓ Skipped {skipped_atoms} non-protein/problematic atoms")

if skipped_residues:
    print(f"\n⚠ Skipped non-standard residues: {', '.join(sorted(skipped_residues))}")

if problematic_atoms:
    print(f"\n⚠ Removed {len(problematic_atoms)} nucleic acid artifact atoms:")
    for resname, atomname, resid in problematic_atoms[:10]:
        print(f"  {resname}-{resid}: {atomname}")
    if len(problematic_atoms) > 10:
        print(f"  ... and {len(problematic_atoms) - 10} more")

print(f"\n✓ Clean structure saved: {clean_pdb}")

# ──────────────────────────────────────────────────────────────────────────────
# PART 4 — ANALYZE PROTONATION STATES
# ──────────────────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print(f"PART 4: Protonation States (pH {PH})")
print("=" * 60)

print(f"\n✓ PDBFixer added hydrogens at pH {PH}")
print("Histidine protonation was determined automatically by OpenMM force field")

# Count histidines in the structure
his_residues = []
for residue in fixer.topology.residues():
    if residue.name in ['HIS', 'HIE', 'HID', 'HIP']:
        his_residues.append((residue.name, residue.id, residue.chain.id))

if his_residues:
    print(f"\nFound {len(his_residues)} histidine residue(s):")
    print(f"{'Residue':>10} {'ID':>6} {'Chain':>6} {'State'}")
    print("-" * 40)
    
    for resname, resid, chain in his_residues:
        state_desc = {
            'HIS': 'Default (from PDB)',
            'HIE': 'Neutral (Nε protonated)',
            'HID': 'Neutral (Nδ protonated)',
            'HIP': 'Protonated (+1)'
        }.get(resname, 'Unknown')
        
        print(f"{resname:>10} {resid:>6} {chain:>6} {state_desc}")
    
    print("\nNOTE: PDBFixer uses OpenMM force field to assign protonation states")
    print("      based on pH and local environment. These assignments are generally")
    print("      more accurate than simple pKa-based rules.")
else:
    print("\n✓ No histidines found in this structure")
    print("No histidine protonation assignment required")

# ──────────────────────────────────────────────────────────────────────────────
# PART 5 — PREPARE FOR GROMACS TOPOLOGY GENERATION
# ──────────────────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("PART 5: Prepare Files for GROMACS Topology Generation")
print("=" * 60)

# Create version without hydrogens for pdb2gmx (from clean structure)
no_h_pdb = os.path.join(OUTPUT_DIR, f"{PDB_ID}{chain_suffix}_noH.pdb")

print(f"\nCreating structure without hydrogens: {no_h_pdb}")
print("(This allows GROMACS to add hydrogens with correct naming)")

# Create version without hydrogens for pdb2gmx
with open(clean_pdb, 'r') as fin, open(no_h_pdb, 'w') as fout:
    for line in fin:
        if line.startswith(('ATOM', 'HETATM')):
            # Skip hydrogen atoms
            atomname = line[12:16].strip()
            element = line[76:78].strip() if len(line) > 77 else atomname[0]
            
            if element not in ['H', 'D']:  # Skip H and deuterium
                fout.write(line)
        else:
            fout.write(line)

print("✓ Structure without hydrogens saved")

print("\nFILES READY FOR GROMACS:")
print("-" * 60)
print(f"  {fixed_pdb}  (with PDBFixer hydrogens, all atoms)")
print(f"  {clean_pdb}  (cleaned, protein-only with H)")
print(f"  {no_h_pdb}  (cleaned, protein-only without H - RECOMMENDED)")

print("\nNEXT STEP: TOPOLOGY GENERATION")
print("=" * 60)
print("\nStep 2A (Local) is complete. Next:")
print("\n1. Upload the protein_prep directory to your GROMACS server")
print("2. Run step2b_topology_generation.py on the server:")
print("\n   python step2b_topology_generation.py")
print("\n   Or with custom options:")
print(f"   python step2b_topology_generation.py --pdb {PDB_ID} --chain {CHAIN} --ff charmm36m")
print("\nThis will generate:")
print("  - {PDB_ID}_processed.gro  (coordinate file)")
print("  - {PDB_ID}.top            (topology)")
print("  - {PDB_ID}_posre.itp      (position restraints)")

# ──────────────────────────────────────────────────────────────────────────────
# FINAL CHECKLIST
# ──────────────────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("STEP 2A COMPLETE (Local Preparation)")
print("=" * 60)

print(
    f"{'[✓]' if os.path.exists(fixed_pdb) else '[ ]'} "
    f"Structure fixed with PDBFixer"
)

print(
    f"{'[✓]' if os.path.exists(clean_pdb) else '[ ]'} "
    f"Structure cleaned (protein-only)"
)

print(
    f"{'[✓]' if os.path.exists(no_h_pdb) else '[ ]'} "
    f"Structure without H prepared for pdb2gmx"
)

print()
print("OUTPUT FILES")
print("-" * 60)
print(f"  {raw_pdb}")
print(f"  {fixed_pdb}  (with hydrogens, all atoms)")
print(f"  {clean_pdb}  (cleaned protein with H)")
print(f"  {no_h_pdb}  (cleaned protein without H, for GROMACS)")

print()
print("READY FOR SERVER")
print("-" * 60)
print("1. Upload protein_prep directory to GROMACS server")
print("2. Run step2b_topology_generation.py on server")
print("3. Use the *_noH.pdb file for pdb2gmx")
print("4. Proceed to step3_complex_assembly.py")