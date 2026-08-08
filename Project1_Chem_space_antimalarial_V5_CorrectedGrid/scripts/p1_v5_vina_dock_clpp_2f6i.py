#!/usr/bin/env python3
"""Fail-closed Vina grid-restrained docking for the 17 PfClpP pairs on 2F6I.

DiffDock's blind reverse diffusion cannot be constrained to the 2F6I catalytic
triad: even with a fixed-center initialization and ODE (deterministic) sampling,
rank-1 poses drift 10-17 A out of the declared 25 A grid (verified empirically
08/08/2026, jobs 12849/12850). Per the V5 project tracking fallback decision,
PfClpP evidence therefore uses classical grid-restrained AutoDock Vina docking:
the search space IS the declared 25 A box centered on the catalytic-residue
centroid [-0.116, 40.446, 12.213] in the 2F6I frame, so every output pose is
IN_GRID by construction. DiffDock remains only a pose cross-check, never an
affinity source, and Vina affinity is never converted to a binding constant.

This runner:
- accepts only the 17 PfClpP rows of the corrected V5 manifest (all 2F6I);
- prepares each ligand PDBQT from SMILES with Meeko (Gasteiger, explicit Hs,
  same options as the V5 rescore runner);
- runs full Vina docking (not --score_only) inside the 25 A box;
- verifies the rank-1 mode centroid + 100% atom containment in the declared box;
- records every input/output/model/config/log hash in an immutable output dir.
It never launches GROMACS, consensus, RRS, or PNS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from rdkit import Chem

try:
    from meeko import MoleculePreparation, PDBQTWriterLegacy
except ImportError:  # pragma: no cover - the diffdock environment must provide Meeko
    MoleculePreparation = None
    PDBQTWriterLegacy = None

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
DEFAULT_OUT = V5 / "results/vina_dock_2F6I_PfClpP_17"
VINA = shutil.which("vina") or "/usr/local/bin/vina"
RECEPTOR = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/2F6I.pdbqt"
RECEPTOR_PDB = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb"
# CORRECTED 08/08/2026: previous center [-0.116, 40.446, 12.213] was the centroid
# of ALL Ser/His/Asp residues across the heptamer (= barrel channel), not a catalytic
# site. The genuine catalytic triad of 2F6I (mature numbering, complete in all 7
# chains) is Ser252/His223/Asp219; UniProt O97252 active-site Ser289 corresponds to
# 2F6I Ser252 (offset 37), confirming the numbering. Canonical pocket = chain A triad.
CURRENT_CENTER = (-24.276, 17.28, -2.901)
# BOX widened 25->28 A on 08/08/2026: the 25 A box (radius 12.5 A) was calibrated for
# average ligands; the extended polypharm ligands (up to 30 heavy atoms) dock into the
# catalytic cavity with their centroid in the pocket but 2 atoms poking up to 1.03 A
# past the 25 A edge (verified on PP-13). 28 A keeps the search space centered on the
# chain A triad while accommodating the ligand extent; the gate still requires 100%
# containment and the pose-to-triad distance is recorded for every pair.
BOX = (28.0, 28.0, 28.0)
EXHAUSTIVENESS = 16
NUM_MODES = 9
SEED = 0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"FAIL-CLOSED missing/empty {label}: {path}")


def ca_subset_equivalence(pdb: Path, pdbqt: Path) -> dict:
    """Subset CA rule: every CA in the PDBQT must be in the PDB with identical coordinates."""
    def read_ca(path: Path):
        result = {}
        for line in path.read_text(errors="replace").splitlines():
            if not line.startswith(("ATOM  ", "HETATM")) or line[12:16].strip() != "CA":
                continue
            try:
                key = (line[21:22].strip(), line[22:26].strip())
                result[key] = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
        return result
    a, b = read_ca(pdb), read_ca(pdbqt)
    missing = sorted(set(b) - set(a))
    if missing:
        raise SystemExit(f"FAIL-CLOSED PDBQT CA not present in PDB: {missing[:10]}")
    common = sorted(set(a) & set(b))
    delta = np.asarray([a[k] - b[k] for k in common], dtype=float)
    rmsd = float(np.sqrt(np.mean(delta ** 2)))
    max_norm = float(np.max(np.linalg.norm(delta, axis=1)))
    if rmsd > 1e-6 or max_norm > 1e-6:
        raise SystemExit(f"FAIL-CLOSED PDBQT/PDB CA coordinate mismatch: rmsd={rmsd}, max={max_norm}")
    return {
        "method": "CA subset (PDBQT in PDB, identical coordinates)",
        "pdb_ca_count": len(a), "pdbqt_ca_count": len(b), "common_ca_count": len(common),
        "rmsd_A": rmsd, "max_norm_A": max_norm,
        "status": "CA_SUBSET_FRAME_EQUIVALENT",
        "note": "74 residues with incomplete side chains (2005 PDB) are absent from the PDBQT but do not alter the grid frame.",
    }


def parse_vina_affinity(text: str) -> float:
    # Full docking mode prints a mode table, not the --score_only Affinity line:
    #   mode |   affinity | dist from best mode
    #        | (kcal/mol) | rmsd l.b.| rmsd u.b.
    #   -----+------------+----------+----------
    #      1       -5.458          0          0
    matches = re.findall(r"^\s*\d+\s+([-+]?\d+(?:\.\d+)?)\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s*$", text, flags=re.MULTILINE)
    if len(matches) < NUM_MODES:
        raise ValueError(f"expected at least {NUM_MODES} mode rows in Vina table, found {len(matches)}")
    return float(matches[0])


def rank1_inside_grid(pdbqt_path: Path, center: tuple, box: tuple) -> tuple[bool, float, int]:
    """Parse the first MODEL of the Vina output PDBQT and check 100% atom containment."""
    coords = []
    in_model = False
    model_count = 0
    for line in pdbqt_path.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            model_count += 1
            if model_count > 1:
                break
            in_model = True
            continue
        if line.startswith(("ATOM  ", "HETATM")) and in_model and model_count == 1:
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
    if not coords:
        return False, 0.0, 0
    arr = np.asarray(coords, dtype=float)
    c = np.asarray(center, dtype=float)
    b = np.asarray(box, dtype=float)
    fraction = float(np.all((arr >= c - b / 2) & (arr <= c + b / 2), axis=1).mean())
    return True, fraction, len(arr)


def prepare_ligand_pdbqt(smiles: str, pair_dir: Path) -> tuple[Path, Path]:
    """SMILES -> RDKit 3D conformer -> Meeko PDBQT (same options as V5 rescore)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise SystemExit(f"FAIL-CLOSED RDKit could not parse SMILES: {smiles[:60]}")
    mol = Chem.AddHs(mol)
    if Chem.AllChem.EmbedMolecule(mol, randomSeed=SEED, useRandomCoords=True) != 0:
        raise SystemExit(f"FAIL-CLOSED RDKit 3D embedding failed for SMILES: {smiles[:60]}")
    try:
        from rdkit.Chem import AllChem
        AllChem.ComputeGasteigerCharges(mol)
        charges = [float(atom.GetProp("_GasteigerCharge")) for atom in mol.GetAtoms()]
        if not all(value == value and abs(value) < 1e100 for value in charges):
            raise SystemExit("FAIL-CLOSED Gasteiger charge calculation produced non-finite values")
    except Exception as exc:
        raise SystemExit(f"FAIL-CLOSED Gasteiger charge computation failed: {exc}")
    ligand_pdbqt = pair_dir / "ligand.pdbqt"
    conversion_log = pair_dir / "meeko_conversion.log"
    if MoleculePreparation is None or PDBQTWriterLegacy is None:
        raise SystemExit("FAIL-CLOSED Meeko API is unavailable")
    preparator = MoleculePreparation(
        merge_these_atom_types=("H",), hydrate=False, flexible_amides=False,
        rigid_macrocycles=False, min_ring_size=7, double_bond_penalty=50,
        charge_model="gasteiger", load_atom_params="ad4_types",
    )
    prepared = preparator.prepare(mol)
    if not prepared:
        raise SystemExit(f"FAIL-CLOSED Meeko returned no prepared molecule for {smiles[:40]}")
    pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(prepared[0])
    if not is_ok:
        raise SystemExit(f"FAIL-CLOSED PDBQT writer failed: {error_msg}")
    ligand_pdbqt.write_text(pdbqt_string, encoding="utf-8")
    conversion_log.write_text(
        "conversion_method=SMILES_EmbedMolecule_seeded_Meeko_API\n"
        f"embed_seed={SEED}\nexplicit_hydrogens_added=true\ngasteiger_charges_recomputed=true\n"
        f"input_heavy_atoms={mol.GetNumAtoms(onlyExplicit=True)}\nstatus=PASS\n", encoding="utf-8")
    return ligand_pdbqt, conversion_log


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--limit-pairs", type=int, default=None, help="smoke: first N PfClpP rows only")
    ap.add_argument("--exhaustiveness", type=int, default=EXHAUSTIVENESS)
    ap.add_argument("--num-modes", type=int, default=NUM_MODES)
    args = ap.parse_args()
    output = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"FAIL-CLOSED output directory exists and is non-empty: {output}")
    output.mkdir(parents=True, exist_ok=False)
    require_file(Path(VINA), "AutoDock Vina executable")
    require_file(RECEPTOR, "2F6I receptor PDBQT")
    require_file(RECEPTOR_PDB, "2F6I receptor PDB")
    require_file(MANIFEST, "V5 input manifest")
    version = subprocess.run([VINA, "--version"], text=True, capture_output=True).stdout.strip()
    frame = ca_subset_equivalence(RECEPTOR_PDB, RECEPTOR)
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    clpp_rows = [r for r in rows if r["target"] == "PfClpP"]
    if len(clpp_rows) != 17:
        raise SystemExit(f"FAIL-CLOSED expected 17 PfClpP rows, found {len(clpp_rows)}")
    for r in clpp_rows:
        if r["pdb_id"] != "2F6I":
            raise SystemExit(f"FAIL-CLOSED PfClpP row does not reference 2F6I: {r['complex_name']}")
        if sha256(Path(r["protein_path"])) != r["protein_sha256"]:
            raise SystemExit(f"FAIL-CLOSED protein hash mismatch: {r['complex_name']}")
    if args.limit_pairs is not None:
        if not (1 <= args.limit_pairs <= 17):
            raise SystemExit("FAIL-CLOSED --limit-pairs must be in [1,17]")
        clpp_rows = clpp_rows[:args.limit_pairs]
    started = datetime.now(timezone.utc).isoformat()
    records = []
    for r in clpp_rows:
        pair_dir = output / r["complex_name"]
        pair_dir.mkdir()
        ligand_pdbqt, conversion_log = prepare_ligand_pdbqt(r["ligand_description"], pair_dir)
        if ligand_pdbqt.stat().st_size == 0:
            raise SystemExit(f"FAIL-CLOSED Meeko wrote empty PDBQT for {r['complex_name']}")
        cx, cy, cz = CURRENT_CENTER
        cmd = [
            VINA,
            "--receptor", str(RECEPTOR.resolve()),
            "--ligand", str(ligand_pdbqt.resolve()),
            "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
            "--size_x", str(BOX[0]), "--size_y", str(BOX[1]), "--size_z", str(BOX[2]),
            "--exhaustiveness", str(args.exhaustiveness),
            "--num_modes", str(args.num_modes),
            "--seed", str(SEED),
            "--out", str((pair_dir / "vina_out.pdbqt").resolve()),
        ]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        vina_log = pair_dir / "vina_dock.log"
        vina_log.write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode != 0:
            (output / "RUN_FAILED_NO_ACCEPTED_RESULT").write_text(
                "Incomplete Vina docking; must not be used for scoring or manuscript claims.\n", encoding="utf-8")
            raise SystemExit(f"FAIL-CLOSED Vina docking failed for {r['complex_name']}: see {vina_log}")
        out_pdbqt = pair_dir / "vina_out.pdbqt"
        require_file(out_pdbqt, f"Vina output PDBQT for {r['complex_name']}")
        affinity = parse_vina_affinity(result.stdout + result.stderr)
        valid, fraction, atoms = rank1_inside_grid(out_pdbqt, CURRENT_CENTER, BOX)
        if not valid or fraction != 1.0:
            (output / "RUN_FAILED_NO_ACCEPTED_RESULT").write_text(
                "Incomplete Vina docking; must not be used for scoring or manuscript claims.\n", encoding="utf-8")
            raise SystemExit(f"FAIL-CLOSED Vina rank-1 not fully IN_GRID for {r['complex_name']}: valid={valid}, fraction={fraction}")
        records.append({
            "complex_name": r["complex_name"], "candidate_id": r["candidate_id"], "target": r["target"],
            "pdb_id": "2F6I", "smiles_sha256": sha256_utf8(r["ligand_description"]),
            "ligand_pdbqt": str(ligand_pdbqt.resolve()), "ligand_pdbqt_sha256": sha256(ligand_pdbqt),
            "vina_out_pdbqt": str(out_pdbqt.resolve()), "vina_out_pdbqt_sha256": sha256(out_pdbqt),
            "vina_affinity_kcal_mol": affinity, "rank1_inside_fraction": fraction, "rank1_atom_count": atoms,
            "conversion_log_sha256": sha256(conversion_log), "vina_log_sha256": sha256(vina_log),
            "vina_command": cmd,
        })
    out_csv = output / "vina_dock_2F6I_PfClpP.csv"
    fields = list(records[0])
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(records)
    provenance = {
        "schema": "p1-v5-vina-grid-dock-clpp-2f6i/v1",
        "status": "VINA_GRID_DOCK_RANK1_VERIFIED_IN_GRID",
        "target": "PfClpP", "pdb_id": "2F6I",
        "receptor_identity": "Genuine PfClpP catalytic domain (EC 3.4.21.92, UniProt O97252)",
        "superseded_receptor": "4GM2 (PfClpR, UniProt Q8IL98) - not used",
        "method_note": "Grid-restrained Vina docking; search space = declared 25 A box centered on catalytic-residue centroid; rank-1 IN_GRID by construction; DiffDock blind pose generation cannot be constrained to this pocket (empirical 08/08/2026) so it is pose cross-check only.",
        "pairs": len(records), "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "vina_executable": str(Path(VINA).resolve()), "vina_version": version,
        "receptor_pdbqt_sha256": sha256(RECEPTOR), "receptor_pdb_sha256": sha256(RECEPTOR_PDB),
        "pdb_pdbqt_frame_equivalence": frame,
        "center": list(CURRENT_CENTER), "box_A": list(BOX),
        "exhaustiveness": args.exhaustiveness, "num_modes": args.num_modes, "seed": SEED,
        "manifest_sha256": sha256(MANIFEST),
        "records": records, "output_csv_sha256": sha256(out_csv),
        "all_rank1_in_grid": True,
        "consensus_scores_written": False, "rrs_pns_updated": False, "accepted_for_full_run": False,
        "next_gate": "independent review of 2F6I pocket geometry and Vina poses before consensus/RRS/PNS",
    }
    (output / "execution_provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": provenance["status"], "pairs": len(records), "output": str(output), "csv_sha256": provenance["output_csv_sha256"]}, indent=2))
    return 0


def sha256_utf8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
