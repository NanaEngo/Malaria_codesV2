#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMILES → 3D structure → SDF → MOL2 (CGenFF-ready)

Fix important:
- élimine UNL1
- impose un nom de résidu propre
"""

import os
import subprocess
import pandas as pd

from rdkit import Chem
from rdkit.Chem import AllChem

# ==========================
# PARAMÈTRES
# ==========================

CSV_FILE = "/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/results/candidate_selection/md_top20_candidates.csv"

ID_COLUMN = "rank"
SMILES_COLUMN = "smiles"

OBABEL = "/usr/bin/obabel"

SDF_DIR = "/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/results/sdf_files"
MOL2_DIR = "/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/results/mol2_files"

# Nom standard des ligands (IMPORTANT pour MD/CGenFF)
LIG_PREFIX = "LIG"

os.makedirs(SDF_DIR, exist_ok=True)
os.makedirs(MOL2_DIR, exist_ok=True)

# ==========================
# CHECK OPENBABEL
# ==========================

print("\nChecking Open Babel...")

subprocess.run([OBABEL, "-V"], check=True)

print("✓ Open Babel OK")

# ==========================
# READ CSV
# ==========================

df = pd.read_csv(CSV_FILE)

print(f"\n✓ {len(df)} molecules loaded")

success = 0
failed = 0

# ==========================
# PIPELINE
# ==========================

for i, row in df.iterrows():

    mol_id = str(row[ID_COLUMN]).strip()
    smiles = str(row[SMILES_COLUMN]).strip()

    ligand_name = f"{LIG_PREFIX}_{mol_id}"

    print(f"\n[{i+1}/{len(df)}] {ligand_name}")

    try:

        # ----------------------------------
        # SMILES → MOL
        # ----------------------------------

        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            raise ValueError("Invalid SMILES")

        # IMPORTANT : nom propre du ligand
        mol.SetProp("_Name", ligand_name)

        # Ajout hydrogènes
        mol = Chem.AddHs(mol)

        # ----------------------------------
        # 3D embedding
        # ----------------------------------

        params = AllChem.ETKDGv3()
        params.randomSeed = 42

        status = AllChem.EmbedMolecule(mol, params)

        if status != 0:
            raise RuntimeError("3D embedding failed")

        # ----------------------------------
        # Optimisation
        # ----------------------------------

        if AllChem.MMFFHasAllMoleculeParams(mol):

            AllChem.MMFFOptimizeMolecule(mol, maxIters=5000)

        else:

            AllChem.UFFOptimizeMolecule(mol, maxIters=5000)

        # ----------------------------------
        # Write SDF
        # ----------------------------------

        sdf_file = os.path.join(SDF_DIR, f"{ligand_name}.sdf")

        writer = Chem.SDWriter(sdf_file)
        writer.write(mol)
        writer.close()

        # ----------------------------------
        # Convert SDF → MOL2
        # IMPORTANT FIX UNL1
        # ----------------------------------

        mol2_file = os.path.join(MOL2_DIR, f"{ligand_name}.mol2")

        subprocess.run(
            [
                OBABEL,
                sdf_file,
                "-O", mol2_file,

                # FIX IMPORTANT
                "-h",        # add hydrogens cleanly
                "-xr", ligand_name,   # force residue name
            ],
            check=True,
            capture_output=True,
            text=True
        )

        print("✓ MOL2 generated (no UNL1)")

        success += 1

    except Exception as e:

        failed += 1

        print(f"✗ ERROR {ligand_name}: {e}")

# ==========================
# SUMMARY
# ==========================

print("\n==============================")
print("SUMMARY")
print("==============================")

print(f"Total   : {len(df)}")
print(f"Success : {success}")
print(f"Failed  : {failed}")

print(f"\nSDF  → {SDF_DIR}")
print(f"MOL2 → {MOL2_DIR}")

print("\nDone.")