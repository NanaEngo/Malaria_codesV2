# ─── CHANGE THIS ──────────────────────────────────────────────────────────────
SMILES = "PASTE_YOUR_SMILES_HERE"   # Your top candidate from Project 1
LIGAND_NAME = "LIG001"              # Short name, no spaces
OUTPUT_DIR = "ligand_prep"        # Where to save outputs
# ──────────────────────────────────────────────────────────────────────────────

import os
import sys
os.makedirs(OUTPUT_DIR, exist_ok=True) 

# ── PART 1: RDKit — 3D Conformer Generation ───────────────────────────────────
print("=" * 60)
print("PART 1: 3D Conformer Generation (RDKit ETKDGv3)")
print("=" * 60)

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors 

# 1a. Parse SMILES
mol = Chem.MolFromSmiles(SMILES)
if mol is None:
    sys.exit(f"ERROR: RDKit could not parse SMILES: {SMILES}\n"
             f"Check for typos. Use https://www.cheminfo.org to validate.")

print("✓ SMILES parsed successfully")
print(f"  Formula: {rdMolDescriptors.CalcMolFormula(mol)}")
print(f"  MW: {Descriptors.MolWt(mol):.2f} Da")
print(f"  Heavy atoms: {mol.GetNumHeavyAtoms()}")

# 1b. Add hydrogens — NEVER skip this
# GROMACS needs explicit H. Implicit H = wrong topology later.
mol = Chem.AddHs(mol)
print(f"  Total atoms (with H): {mol.GetNumAtoms()}")

# 1c. Generate 3D conformer with ETKDGv3
params = AllChem.ETKDGv3()
params.randomSeed = 42          # Reproducibility
params.numThreads = 0           # Use all available cores
params.enforceChirality = True  # Preserve stereocenters from your SMILES

result = AllChem.EmbedMolecule(mol, params)
if result == -1:
    sys.exit("ERROR: ETKDGv3 failed to embed molecule.\n"
             "Possible causes: very large ring system, invalid stereo, "
             "unusual valence.\nTry: AllChem.EmbedMolecule(mol, AllChem.ETKDG())")

print("✓ ETKDGv3 conformer generated (seed=42)")

# 1d. MMFF94 geometry optimization (removes bad contacts before OpenFF)
ff_result = AllChem.MMFFOptimizeMolecule(mol, maxIters=2000)
if ff_result == 0:
    print("✓ MMFF94 optimization converged")
elif ff_result == 1:
    print("⚠ MMFF94 did not converge (may still be usable)")
else:
    print("⚠ MMFF94 not available for this molecule (rare). Proceeding.")

# 1e. Save as SDF (primary format for OpenFF)
sdf_path = os.path.join(OUTPUT_DIR, f"{LIGAND_NAME}.sdf")
writer = Chem.SDWriter(sdf_path)
mol.SetProp("_Name", LIGAND_NAME)
writer.write(mol)
writer.close()
print(f"✓ Saved: {sdf_path}")

# 1f. Save as PDB (for visual inspection in PyMOL — always check this!)
pdb_path = os.path.join(OUTPUT_DIR, f"{LIGAND_NAME}.pdb")
Chem.MolToPDBFile(mol, pdb_path)
print(f"✓ Saved: {pdb_path}")
print(f"\n>>> OPEN {pdb_path} IN PyMOL NOW and check the 3D structure looks reasonable.")
print(">>> If it looks like a tangled mess, something is wrong with your SMILES.\n")


# ── PART 2: OpenFF Sage 2.2 — Force Field Parameterization ───────────────────
print("=" * 60)
print("PART 2: Force Field Parameterization (OpenFF 2.2 Sage)")
print("=" * 60)
print("This assigns:")
print("  - Bond/angle/torsion parameters (how atoms vibrate and rotate)")
print("  - AM1-BCC partial charges (how electrons are distributed)")
print("  These are ESSENTIAL for MD — without them GROMACS cannot compute forces.")
print()

try:
    from openff.toolkit import Molecule, ForceField
    from openff.toolkit.utils import RDKitToolkitWrapper

    # 2a. Load ligand into OpenFF from SDF
    off_mol = Molecule.from_file(sdf_path, file_format="sdf")
    off_mol.name = LIGAND_NAME
    print("✓ Molecule loaded into OpenFF toolkit")

    # 2b. Load force field
    ff = ForceField("openff-2.2.0.offxml")
    print("✓ OpenFF 2.2 Sage loaded")

    # 2c. Assign AM1-BCC charges
    # AM1-BCC = semi-empirical quantum chemistry + bond charge corrections
    # Standard for AMBER/GROMACS ligand simulations
    print("  Assigning AM1-BCC partial charges (this takes 1-5 min)...")
    off_mol.assign_partial_charges(partial_charge_method="am1bcc")
    print("✓ AM1-BCC charges assigned")

    # Charge sanity check: total charge should be ~0 for neutral, or integer for ions
    total_charge = sum(c.magnitude for c in off_mol.partial_charges)
    print(f"  Total charge: {total_charge:.4f} e  (should be ~0 or integer)")
    if abs(total_charge) > 0.01 and abs(round(total_charge) - total_charge) > 0.01:
        print("  ⚠ WARNING: Non-integer total charge. Check protonation state.")

    # 2d. Create OpenMM system and export to GROMACS format
    from openff.toolkit.topology import Topology
    topology = Topology.from_molecules([off_mol])
    system = ff.create_openmm_system(topology)
    print("✓ OpenMM system created")

    # 2e. Export GROMACS topology files
    from openmmforcefields.utils import system_to_parmed
    import parmed as pmd

    structure = system_to_parmed(system, topology)
    gro_path = os.path.join(OUTPUT_DIR, f"{LIGAND_NAME}.gro")
    top_path = os.path.join(OUTPUT_DIR, f"{LIGAND_NAME}.top")
    structure.save(gro_path, overwrite=True)
    structure.save(top_path, overwrite=True)
    print("✓ Saved GROMACS files:")
    print(f"    {gro_path}  (coordinates)")
    print(f"    {top_path}  (topology with force field parameters)")

except ImportError:
    print("OpenFF toolkit not installed yet.")
    print("Run this to install:")
    print("    conda install -c conda-forge openff-toolkit openff-forcefields")
    print()
    print("The SDF file from Part 1 is ready and waiting.")
    print("Come back to Part 2 after installation.")

except Exception as e:
    print(f"ERROR in OpenFF parameterization: {e}")
    print("Common causes:")
    print("  - Molecule has unusual valence or bond orders")
    print("  - Missing stereochemistry on a chiral center")
    print("  - OpenFF does not cover this chemistry (rare)")


# ── SUMMARY ──────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 1 COMPLETE — What you have now:")
print("=" * 60)
print(f"  {LIGAND_NAME}.sdf   → 3D geometry (input for OpenFF, docking tools)")
print(f"  {LIGAND_NAME}.pdb   → for PyMOL visualization (CHECK THIS)")
print(f"  {LIGAND_NAME}.gro   → GROMACS coordinates (if Part 2 ran)")
print(f"  {LIGAND_NAME}.top   → GROMACS topology (if Part 2 ran)")
print()
print("NEXT STEP: step2_protein_prep.py")
print("  → Clean PfDHFR crystal structure (1J3I)")
print("  → Run pdb2gmx with CHARMM36m")
print("  → Assign protonation states at pH 7.4")
