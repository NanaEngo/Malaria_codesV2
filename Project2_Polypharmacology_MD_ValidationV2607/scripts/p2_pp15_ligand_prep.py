#!/usr/bin/env python3
"""Prepare PP-15 ligand: SMILES to 3D to PDBQT."""
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy
import sys

smi = sys.argv[1]
out_dir = sys.argv[2]

mol = Chem.MolFromSmiles(smi)
if mol is None:
    print(f"ERROR: invalid SMILES {smi}")
    sys.exit(1)
mol = Chem.AddHs(mol)
AllChem.EmbedMolecule(mol, randomSeed=42)
AllChem.MMFFOptimizeMolecule(mol, mmffVariant='MMFF94', maxIters=200)

# Write SDF
writer = Chem.SDWriter(f"{out_dir}/PP-15_ligand.sdf")
writer.write(mol)
writer.close()

# PDBQT via Meeko
preparator = MoleculePreparation()
setups = preparator(mol)
for setup in setups:
    result = PDBQTWriterLegacy.write_string(setup)
    pdbqt_string, is_ok = result[0], result[1]
    if is_ok:
        with open(f"{out_dir}/PP-15_ligand.pdbqt", "w") as fh:
            fh.write(pdbqt_string)
        break
    else:
        err = result[2] if len(result) > 2 else "unknown"
        print(f"Meeko PDBQT failed: {err}")
        sys.exit(1)

# Write PDB for reference
Chem.MolToPDBFile(mol, f"{out_dir}/PP-15_ligand.pdb")
print(f"Ligand prepared: {Chem.MolToSmiles(mol)}")
print(f"Heavy atoms: {mol.GetNumHeavyAtoms()}")
