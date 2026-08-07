#!/usr/bin/env python3
"""
Re-generate ALL DEKOIS PDBQT files using Meeko for consistent atom typing.
- 40 actives from DHFR_ligands.smi → actives/active_XXXX.pdbqt
- 1200 decoys from DHFR_decoys.smi → decoys/decoy_X.pdbqt

Fix: eliminates AUC bias caused by different preparation pipelines.

Usage:
    python scripts/prepare_all_dekois_meeko.py [--force]
"""
import os, sys, logging, time
from rdkit import Chem
from rdkit.Chem import AllChem, rdDistGeom
from meeko import MoleculePreparation, PDBQTWriterLegacy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

V2DIR = "/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
SMILES_DIR = "/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/external/dekois"
ACTIVES_SMILES = os.path.join(SMILES_DIR, "DHFR_ligands.smi")
DECOYS_SMILES = os.path.join(SMILES_DIR, "DHFR_decoys.smi")
OUTDIR_ACTIVES = os.path.join(V2DIR, "results", "v2_dekois", "actives")
OUTDIR_DECOYS = os.path.join(V2DIR, "results", "v2_dekois", "decoys")
os.makedirs(OUTDIR_ACTIVES, exist_ok=True)
os.makedirs(OUTDIR_DECOYS, exist_ok=True)

FORCE = "--force" in sys.argv


def generate_conformer(mol, seed=42):
    """Generate 3D conformer using ETKDG with fallback."""
    mol = Chem.AddHs(mol)
    params = rdDistGeom.ETKDGv3()
    params.randomSeed = seed
    params.useRandomCoords = True
    params.numThreads = 1
    status = rdDistGeom.EmbedMolecule(mol, params)
    if status != 0:
        params.useRandomCoords = True
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
    """Prepare PDBQT string via Meeko."""
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


def process_smiles_list(smiles_list, output_dir, name_prefix, name_format, start_idx=1):
    """Process a list of SMILES and write PDBQT files."""
    success = 0
    errors = 0
    skipped = 0
    
    for idx, smi in enumerate(smiles_list):
        outname = name_format.format(idx + start_idx)
        outpath = os.path.join(output_dir, outname)

        if not FORCE and os.path.exists(outpath):
            # Quick check: is it a valid PDBQT with TORSDOF?
            with open(outpath) as f:
                content = f.read()
            if 'TORSDOF' in content and 'ROOT' in content:
                skipped += 1
                continue
            else:
                log.warning(f"{outname} exists but invalid, regenerating")

        # Parse SMILES
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            log.error(f"[{idx+1:04d}] Cannot parse SMILES: {smi[:50]}...")
            errors += 1
            continue

        # Generate 3D
        mol_3d = generate_conformer(mol, seed=idx + 1)
        if mol_3d is None:
            log.error(f"[{idx+1:04d}] Cannot generate 3D: {smi[:50]}...")
            errors += 1
            continue

        # PDBQT via Meeko
        pdbqt_string, error = prepare_pdbqt(mol_3d)
        if error:
            log.error(f"[{idx+1:04d}] {error}")
            errors += 1
            continue

        # Write
        with open(outpath, "w") as f:
            f.write(pdbqt_string)

        # Verify TORSDOF
        torsdof = 0
        for line in pdbqt_string.split("\n"):
            if line.startswith("TORSDOF"):
                torsdof = int(line.split()[1])
                break

        log.info(f"[{idx+1:04d}] {outname} (TORSDOF={torsdof})")
        success += 1

    return success, errors, skipped


def main():
    total_start = time.time()

    # --- Actives (40) ---
    log.info("=" * 60)
    log.info("ACTIVES: reading SMILES from DHFR_ligands.smi")
    with open(ACTIVES_SMILES) as f:
        active_smiles = [line.strip() for line in f if line.strip()]
    log.info(f"Found {len(active_smiles)} active SMILES")

    s, e, sk = process_smiles_list(
        active_smiles, OUTDIR_ACTIVES,
        name_prefix="active", name_format="active_{:04d}.pdbqt",
        start_idx=1
    )
    log.info(f"Actives: {s} generated, {sk} skipped, {e} errors")

    # --- Decoys (1200) ---
    log.info("=" * 60)
    log.info("DECOYS: reading SMILES from DHFR_decoys.smi")
    with open(DECOYS_SMILES) as f:
        decoy_smiles = [line.strip() for line in f if line.strip()]
    log.info(f"Found {len(decoy_smiles)} decoy SMILES")

    s2, e2, sk2 = process_smiles_list(
        decoy_smiles, OUTDIR_DECOYS,
        name_prefix="decoy", name_format="decoy_{}.pdbqt",
        start_idx=1
    )
    log.info(f"Decoys: {s2} generated, {sk2} skipped, {e2} errors")

    # --- Summary ---
    total_time = time.time() - total_start
    log.info("=" * 60)
    total_ok = s + s2
    total_err = e + e2
    log.info(f"TOTAL: {total_ok} OK, {total_err} errors in {total_time:.0f}s")
    log.info(f"  Actives: {OUTDIR_ACTIVES}/")
    log.info(f"  Decoys:  {OUTDIR_DECOYS}/")

    if total_err > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
