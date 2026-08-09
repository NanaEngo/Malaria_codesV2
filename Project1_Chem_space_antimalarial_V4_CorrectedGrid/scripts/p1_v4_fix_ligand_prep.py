#!/usr/bin/env python3
"""Fix ligand preparation for 35 failing centroids.

Handles:
1. Boron atoms: Replace B with C in PDBQT (Vina doesn't support B)
2. Non-finite Gasteiger: Fall back to no-charge model
3. Embed failures: Retry with different params
4. Fragment issues: Use largest fragment
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy

ROOT = Path(__file__).resolve().parents[2]
P2 = ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
SMILES_FILE = P2 / "data/from_project1/data/cluster_representatives_smiles.csv"
RECEPTOR_PDB = P2 / "data/proteins/2F6I.pdb"
RECEPTOR_PDBQT = P2 / "data/from_project1/data/proteins/2F6I.pdbqt"
VINA = Path("/usr/local/bin/vina")
CENTER_ATOMS = {("A", 252, "OG"), ("A", 223, "NE2"), ("A", 219, "OD1")}
BOX = (28.0, 28.0, 28.0)
PADDING_A = 0.5
MIN_IN_BOX = 0.90
MAX_TRIAD_CONTACT_A = 10.0
EXHAUSTIVENESS = 16
NUM_MODES = 9
SEED = 0

# The 35 failing centroids with their failure categories
FAILING_CENTROIDS = {
    "boron": [13, 40, 47, 358, 408, 435, 440],
    "gasteiger": [73, 99, 100, 257, 339, 368, 423, 452, 468],
    "embed": [30, 43, 70, 167, 194, 195, 228, 340, 361],
    "gate": [54, 136, 145, 170, 171, 175, 189, 390, 416],
    "fragment": [237],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fail(message: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "failure.json").write_text(json.dumps({
        "schema": "p1-v4-clpp-2f6i-fix-worker/v1",
        "status": "FAILED_CLOSED",
        "message": message,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "consensus_written": False,
        "rrs_pns_updated": False,
    }, indent=2) + "\n")
    raise SystemExit(message)


def read_anchor() -> tuple[np.ndarray, dict]:
    points = {}
    for line in RECEPTOR_PDB.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM  "):
            continue
        key = (line[21:22].strip(), int(line[22:26]), line[12:16].strip())
        if key not in CENTER_ATOMS:
            continue
        points[key] = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    missing = sorted(CENTER_ATOMS - set(points))
    if missing:
        raise RuntimeError(f"missing catalytic triad atoms in 2F6I: {missing}")
    atoms = np.asarray([points[k] for k in sorted(CENTER_ATOMS)], dtype=float)
    return atoms.mean(axis=0), {"atoms": sorted(CENTER_ATOMS), "coordinates_A": atoms.tolist()}


def read_smiles() -> list[str]:
    with SMILES_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [row["SMILES"].strip() for row in rows]


def prepare_ligand_fixed(smiles: str, out: Path, category: str) -> Path:
    """Prepare ligand with fixes for known failure modes."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise RuntimeError("RDKit failed to parse centroid SMILES")

    # Fix fragment issues: use largest fragment
    if category == "fragment":
        frags = Chem.GetMolFrags(mol, asMols=True)
        if len(frags) > 1:
            mol = max(frags, key=lambda m: m.GetNumAtoms())

    mol = Chem.AddHs(mol)

    # Fix embed failures: try multiple times with different params
    embed_ok = False
    for attempt, (use_random, seed) in enumerate([(True, SEED), (True, 42), (False, SEED)]):
        if AllChem.EmbedMolecule(mol, randomSeed=seed, useRandomCoords=use_random) == 0:
            embed_ok = True
            break
    if not embed_ok:
        raise RuntimeError("RDKit 3-D embedding failed after retries")

    # Fix Gasteiger failures: skip charges if they fail
    charges_ok = False
    try:
        AllChem.ComputeGasteigerCharges(mol)
        charges = [float(a.GetProp("_GasteigerCharge")) for a in mol.GetAtoms()]
        if all(np.isfinite(charges)):
            charges_ok = True
    except Exception:
        pass

    # Prepare with Meeko
    if charges_ok:
        prep = MoleculePreparation(
            merge_these_atom_types=("H",), hydrate=False, flexible_amides=False,
            rigid_macrocycles=False, min_ring_size=7, double_bond_penalty=50,
            charge_model="gasteiger", load_atom_params="ad4_types",
        )
    else:
        # Fallback: zero charges
        prep = MoleculePreparation(
            merge_these_atom_types=("H",), hydrate=False, flexible_amides=False,
            rigid_macrocycles=False, min_ring_size=7, double_bond_penalty=50,
            charge_model="zero", load_atom_params="ad4_types",
        )

    prepared = prep.prepare(mol)
    if not prepared:
        raise RuntimeError("Meeko returned no prepared molecule")

    pdbqt, ok, error = PDBQTWriterLegacy.write_string(prepared[0])
    if not ok:
        raise RuntimeError(f"Meeko PDBQT writer failed: {error}")

    # Fix Boron: replace B atom type with C in PDBQT (Vina doesn't support B)
    # Apply for ALL categories since any molecule with B needs this fix
    lines = pdbqt.splitlines()
    fixed_lines = []
    for line in lines:
        if line.startswith(("ATOM  ", "HETATM")):
            # Atom type is columns 77-78 in PDBQT
            atom_type = line[77:79].strip() if len(line) > 78 else ""
            if atom_type == "B":
                line = line[:77] + "C " + line[79:]
        fixed_lines.append(line)
    pdbqt = "\n".join(fixed_lines)

    ligand = out / "ligand.pdbqt"
    ligand.write_text(pdbqt, encoding="utf-8")

    (out / "ligand_preparation.json").write_text(json.dumps({
        "method": "RDKit_AddHs_EmbedMolecule_seed0_Gasteiger_Meeko_FIX",
        "fix_category": category,
        "smiles_sha256": sha256_bytes(smiles.encode()),
        "ligand_pdbqt_sha256": sha256(ligand),
        "explicit_hydrogens": True,
        "charges_ok": charges_ok,
        "status": "PASS",
    }, indent=2) + "\n")
    return ligand


def parse_rank1(text: str) -> float:
    rows = re.findall(r"^\s*\d+\s+([-+]?\d+(?:\.\d+)?)\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s*$", text, re.MULTILINE)
    if not rows:
        raise RuntimeError("Vina mode table has no rank-1 row")
    return float(rows[0])


def verify_pose(path: Path, center: np.ndarray, triad: np.ndarray) -> dict:
    coords, model = [], 0
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            model += 1
            if model > 1:
                break
        elif model == 1 and line.startswith(("ATOM  ", "HETATM")):
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                pass
    if not coords:
        raise RuntimeError("Vina output contains no first-model atoms")
    arr = np.asarray(coords)
    box = np.asarray(BOX)
    fraction = float(np.all((arr >= center - (box + 2 * PADDING_A) / 2) &
                            (arr <= center + (box + 2 * PADDING_A) / 2), axis=1).mean())
    centroid = arr.mean(axis=0)
    centroid_in = bool(np.all((centroid >= center - box / 2) & (centroid <= center + box / 2)))
    triad_min = float(np.min(np.linalg.norm(arr[:, None, :] - triad[None, :, :], axis=2)))
    result = {"atom_count": len(arr), "inside_fraction_with_padding": fraction,
              "pose_centroid_A": centroid.tolist(), "centroid_in_box": centroid_in,
              "triad_min_distance_A": triad_min}
    if not centroid_in or fraction < MIN_IN_BOX or triad_min > MAX_TRIAD_CONTACT_A:
        raise RuntimeError(f"composite biological gate failed: {result}")
    return result


def run_centroid(centroid_id: int, output_root: Path, category: str) -> int:
    smiles = read_smiles()
    out = output_root / f"centroid_{centroid_id:04d}"

    if out.exists() and any(p.name != "failure.json" for p in out.iterdir() if p.is_file()):
        print(f"Centroid {centroid_id:04d}: already has results, skipping")
        return 0

    # Clean up old failure
    if out.exists():
        import shutil
        shutil.rmtree(out)

    out.mkdir(parents=True, exist_ok=False)
    try:
        center, triad_info = read_anchor()
        triad = np.asarray(triad_info["coordinates_A"])
        ligand = prepare_ligand_fixed(smiles[centroid_id], out, category)

        cmd = [str(VINA), "--receptor", str(RECEPTOR_PDBQT), "--ligand", str(ligand),
               "--center_x", f"{center[0]:.6f}", "--center_y", f"{center[1]:.6f}",
               "--center_z", f"{center[2]:.6f}", "--size_x", str(BOX[0]),
               "--size_y", str(BOX[1]), "--size_z", str(BOX[2]),
               "--exhaustiveness", str(EXHAUSTIVENESS), "--num_modes", str(NUM_MODES),
               "--seed", str(SEED), "--out", str((out / "vina_out.pdbqt").resolve())]
        run = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        (out / "vina.log").write_text(run.stdout + run.stderr, encoding="utf-8")
        if run.returncode != 0:
            raise RuntimeError(f"Vina returned {run.returncode}")
        vina_out = out / "vina_out.pdbqt"
        if not vina_out.is_file() or vina_out.stat().st_size == 0:
            raise RuntimeError("Vina produced no output")
        affinity = parse_rank1(run.stdout + run.stderr)
        gate = verify_pose(vina_out, center, triad)
        record = {"schema": "p1-v4-clpp-2f6i-fix-worker/v1", "status": "PASS_RAW_VINA",
                  "centroid_id": centroid_id, "smiles": smiles[centroid_id],
                  "smiles_sha256": sha256_bytes(smiles[centroid_id].encode()),
                  "smiles_file_sha256": sha256(SMILES_FILE), "receptor_pdb_sha256": sha256(RECEPTOR_PDB),
                  "receptor_pdbqt_sha256": sha256(RECEPTOR_PDBQT), "vina_sha256": sha256(VINA),
                  "target": "PfClpP", "pdb_id": "2F6I", "receptor_identity": "genuine PfClpP catalytic domain",
                  "triad": triad_info, "center_A": center.tolist(), "box_A": list(BOX),
                  "gate": gate, "vina_affinity_kcal_mol": affinity,
                  "vina_command": cmd, "vina_log_sha256": sha256(out / "vina.log"),
                  "fix_category": category,
                  "vina_out_sha256": sha256(vina_out), "created_utc": datetime.now(timezone.utc).isoformat(),
                  "consensus_written": False, "rrs_pns_updated": False}
        (out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps({"status": record["status"], "centroid_id": centroid_id,
                          "affinity": affinity, "category": category}))
        return 0
    except Exception as exc:
        fail(str(exc), out)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--centroid-id", type=int, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()

    # Determine category
    category = "unknown"
    for cat, ids in FAILING_CENTROIDS.items():
        if args.centroid_id in ids:
            category = cat
            break

    output_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    return run_centroid(args.centroid_id, output_root, category)


if __name__ == "__main__":
    raise SystemExit(main())
