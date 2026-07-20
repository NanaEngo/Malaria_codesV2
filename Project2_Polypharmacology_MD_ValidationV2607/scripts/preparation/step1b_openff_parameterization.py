# ─── CHANGE THESE IF NEEDED ───────────────────────────────────────────────────
SDF_PATH    = "ligand_prep/LIG001.sdf"
LIGAND_NAME = "LIG001"
OUTPUT_DIR  = "ligand_prep"
# ──────────────────────────────────────────────────────────────────────────────

import os
import sys
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Step 1: Verify the SDF exists from Part 1 ─────────────────────────────────
if not os.path.exists(SDF_PATH):
    sys.exit(f"ERROR: {SDF_PATH} not found.\nRun step1_ligand_prep.py first.")
print(f"✓ Found: {SDF_PATH}")

# ── Step 2: Import with informative error messages ────────────────────────────
try:
    from openff.toolkit import Molecule, ForceField, Topology
    print("✓ openff-toolkit imported")
except ImportError:
    sys.exit("ERROR: openff-toolkit missing.\n"
             "Fix: mamba install -c conda-forge openff-toolkit openff-forcefields")

try: 
    from openff.interchange import Interchange
    print("✓ openff-interchange imported")
except ImportError:
    sys.exit("ERROR: openff-interchange missing.\n"
             "Fix: mamba install -c conda-forge openff-interchange\n\n"
             "This is the correct modern tool for OpenFF → GROMACS export.\n"
             "Do NOT use parmed or openmmforcefields for this step.")

# ── Step 3: Load molecule ─────────────────────────────────────────────────────
print("\n── Loading molecule ──")
mol = Molecule.from_file(SDF_PATH)
mol.name = LIGAND_NAME

# Check for undefined stereocenters — critical for your NP hybrids
stereo_centers = [
    atom for atom in mol.atoms
    if atom.stereochemistry is not None
]
print(f"✓ Molecule loaded: {mol.n_atoms} atoms")
print(f"  Defined stereocenters: {len(stereo_centers)}")
if len(stereo_centers) == 0:
    print("  ⚠ No stereocenters detected. If your compound has chiral centers,")
    print("    check your SMILES includes @/@@. Wrong stereochemistry = wrong binding.")

# ── Step 4: Assign AM1-BCC partial charges ────────────────────────────────────
print("\n── Assigning AM1-BCC partial charges ──")
print("  (This uses a semi-empirical QM method — takes 1-5 minutes)")
print("  AM1-BCC is the AMBER/GROMACS community standard for ligand charges.")

mol.assign_partial_charges("am1bcc")

total_q = sum(c.magnitude for c in mol.partial_charges)
print("✓ Charges assigned")
print(f"  Total charge: {total_q:.4f} e")

# Validate charge
expected_charge = mol.total_charge.magnitude
if abs(total_q - expected_charge) > 0.05:
    print(f"  ⚠ WARNING: Total charge ({total_q:.3f}) differs from formal charge "
          f"({expected_charge}). Re-examine protonation state.")
else:
    print(f"  ✓ Charge is consistent with formal charge ({expected_charge})")

# Print per-atom charges for your records
print("\n  Per-atom partial charges (for verification):")
for i, (atom, charge) in enumerate(zip(mol.atoms, mol.partial_charges)):
    print(f"    {i:3d}  {atom.symbol:2s}  {charge.magnitude:+.4f} e")

# ── Step 5: Apply OpenFF 2.2 Sage force field ─────────────────────────────────
print("\n── Applying OpenFF 2.2 Sage force field ──")
ff = ForceField("openff-2.2.0.offxml")
topology = mol.to_topology()

# Create Interchange object — this holds ALL parameters
interchange = Interchange.from_smirnoff(force_field=ff, topology=topology)
print("✓ Interchange created (bond, angle, torsion, vdW parameters assigned)")

# ── Step 6: Export to GROMACS ─────────────────────────────────────────────────
print("\n── Exporting to GROMACS format ──")

# Define a 2.0nm x 2.0nm x 2.0nm box 
from openff.units import unit
interchange.box = [2.0, 2.0, 2.0] * unit.nanometer 

gro_path = os.path.join(OUTPUT_DIR, f"{LIGAND_NAME}.gro")
top_path = os.path.join(OUTPUT_DIR, f"{LIGAND_NAME}.top")

# This creates both .gro and .top
interchange.to_gromacs(prefix=os.path.join(OUTPUT_DIR, LIGAND_NAME))

# ── Step 7: Print what's inside .top so you understand it ────────────────────
print("\n── Preview of GROMACS topology (.top) ──")
print("  (This is what GROMACS reads to understand your molecule)")
with open(top_path) as f:
    lines = f.readlines()
print(f"  Total lines: {len(lines)}")
print("  First 30 lines:")
for line in lines[:30]:
    print("    " + line.rstrip())

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 1b COMPLETE")
print("=" * 60)
print(f"  {gro_path}  → GROMACS coordinates for your ligand")
print(f"  {top_path}  → GROMACS topology (FF params + charges)")
print()
print("WHAT THESE FILES CONTAIN:")
print("  .gro : atom names, x/y/z positions in nanometers, box vectors")
print("  .top : [ atoms ] [ bonds ] [ pairs ] [ angles ] [ dihedrals ]")
print("         Each section tells GROMACS how atoms interact.")
print()
print("NEXT STEP: step2_protein_prep.py")
print("  We will clean 1J3I (PfDHFR), run pdb2gmx, and combine")
print("  the protein topology with this ligand topology.")
print()
print("IMPORTANT: Keep these files — they are the foundation of all")
print("  220 protein-ligand systems in your project.")
