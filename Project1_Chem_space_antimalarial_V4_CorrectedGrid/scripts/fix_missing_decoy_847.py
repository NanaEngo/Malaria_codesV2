#!/usr/bin/env python3
"""Regenerate a single missing DEKOIS decoy PDBQT using Meeko."""
import os, sys
from rdkit import Chem
from rdkit.Chem import AllChem, rdDistGeom
from meeko import MoleculePreparation, PDBQTWriterLegacy

V2DIR = "/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
SMILES_FILE = "/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/external/dekois/DHFR_decoys.smi"
OUTDIR = os.path.join(V2DIR, "results", "v2_dekois", "decoys")
TARGET_IDX = 847  # 1-indexed line in the SMILES file
OUTPATH = os.path.join(OUTDIR, f"decoy_{TARGET_IDX}.pdbqt")


def generate_conformer(mol, seed=42):
    mol = Chem.AddHs(mol)
    params = rdDistGeom.ETKDGv3()
    params.randomSeed = seed
    params.useRandomCoords = True
    params.numThreads = 1
    status = rdDistGeom.EmbedMolecule(mol, params)
    if status != 0:
        params.randomSeed = seed + 1000
        status = rdDistGeom.EmbedMolecule(mol, params)
        if status != 0:
            return None
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    except Exception:
        try:
            AllChem.UFFOptimizeMolecule(mol, maxIters=200)
        except Exception:
            pass
    return mol


def prepare_pdbqt(mol):
    preparator = MoleculePreparation(
        merge_these_atom_types=('H',),
        hydrate=False,
        flexible_amides=False,
        rigid_macrocycles=False,
        min_ring_size=7,
        double_bond_penalty=50,
        charge_model='gasteiger',
        load_atom_params='ad4_types',
    )
    prep_container = preparator.prepare(mol)
    if prep_container is None or len(prep_container) == 0:
        return None, "Meeko preparation failed"
    prep = prep_container[0]
    pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(prep)
    if not is_ok:
        return None, f"PDBQT write failed: {error_msg}"
    return pdbqt_string, None


def main():
    with open(SMILES_FILE) as f:
        lines = [line.strip() for line in f if line.strip()]
    smi = lines[TARGET_IDX - 1]
    print(f"Decoy {TARGET_IDX}: {smi}")

    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        print(f"ERROR: Cannot parse SMILES for decoy {TARGET_IDX}")
        sys.exit(1)

    mol_3d = generate_conformer(mol, seed=TARGET_IDX)
    if mol_3d is None:
        print(f"ERROR: Cannot generate conformer for decoy {TARGET_IDX}")
        sys.exit(1)

    pdbqt_string, error = prepare_pdbqt(mol_3d)
    if error:
        print(f"ERROR: {error}")
        sys.exit(1)

    with open(OUTPATH, "w") as f:
        f.write(pdbqt_string)
    print(f"Wrote {OUTPATH}")


if __name__ == "__main__":
    main()
