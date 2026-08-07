#!/usr/bin/env python3
"""
Regenerate DEKOIS active PDBQT files from SMILES using RDKit + Meeko.
Fixes the tree.h(101) Vina bug by generating properly structured PDBQT 
files with correct rotatable bond trees (TORSDOF > 0).

Usage:
    python scripts/regen_dekois_pdbqt.py [--force]

Output:
    results/v2_dekois/actives/active_XXXX.pdbqt (overwrites buggy files)
"""
import os, sys, logging
from rdkit import Chem
from rdkit.Chem import AllChem, rdDistGeom
from meeko import MoleculePreparation, PDBQTWriterLegacy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

V2DIR = "/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
SMILES_FILE = "DHFR_ligands.smi"
SMILES_PATH = "/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/external/dekois/DHFR_ligands.smi"
OUTDIR = os.path.join(V2DIR, "results", "v2_dekois", "actives")
os.makedirs(OUTDIR, exist_ok=True)


def generate_conformer(mol, seed=42):
    """Generate 3D conformer using ETKDG with fallback."""
    mol = Chem.AddHs(mol)
    params = rdDistGeom.ETKDGv3()
    params.randomSeed = seed
    params.useRandomCoords = True
    params.numThreads = 1
    status = rdDistGeom.EmbedMolecule(mol, params)
    if status != 0:
        log.warning(f"ETKDG failed (seed={seed}), trying random coords")
        params.useRandomCoords = True
        params.randomSeed = seed + 1000
        status = rdDistGeom.EmbedMolecule(mol, params)
        if status != 0:
            return None
    # MMFF optimization
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    except Exception:
        try:
            AllChem.UFFOptimizeMolecule(mol, maxIters=200)
        except Exception:
            pass
    return mol


def prepare_pdbqt_via_meeko(mol):
    """Use Meeko to generate a proper Vina PDBQT with torsion tree."""
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
    
    # Take the first (best) prepared form
    prep = prep_container[0]
    pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(prep)
    if not is_ok:
        return None, f"PDBQT write failed: {error_msg}"
    return pdbqt_string, None


def main():
    force = "--force" in sys.argv

    # Read SMILES
    if not os.path.exists(SMILES_PATH):
        log.error(f"SMILES file not found: {SMILES_PATH}")
        sys.exit(1)

    with open(SMILES_PATH) as f:
        smiles_list = [line.strip() for line in f if line.strip()]

    log.info(f"Found {len(smiles_list)} active SMILES in {SMILES_PATH}")

    success = 0
    errors = 0

    for idx, smi in enumerate(smiles_list):
        outfile = os.path.join(OUTDIR, f"active_{idx + 1:04d}.pdbqt")

        if not force and os.path.exists(outfile):
            log.info(f"[{idx+1:04d}] Skipping (exists): {os.path.basename(outfile)}")
            continue

        # Parse SMILES
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            log.error(f"[{idx+1:04d}] Cannot parse SMILES: {smi}")
            errors += 1
            continue

        # Generate 3D conformer
        mol_3d = generate_conformer(mol, seed=idx + 1)
        if mol_3d is None:
            log.error(f"[{idx+1:04d}] Cannot generate 3D: {smi}")
            errors += 1
            continue

        # Prepare PDBQT via Meeko
        pdbqt_string, error = prepare_pdbqt_via_meeko(mol_3d)
        if error:
            log.error(f"[{idx+1:04d}] {error}")
            errors += 1
            continue

        # Write PDBQT file
        with open(outfile, "w") as f:
            f.write(pdbqt_string)

        # Verify TORSDOF > 0
        torsdof = 0
        for line in pdbqt_string.split("\n"):
            if line.startswith("TORSDOF"):
                torsdof = int(line.split()[1])
                break

        log.info(f"[{idx+1:04d}] Wrote: {os.path.basename(outfile)} (TORSDOF={torsdof})")
        success += 1

    log.info(f"Done: {success} regenerated, {errors} errors out of {len(smiles_list)}")


if __name__ == "__main__":
    main()
