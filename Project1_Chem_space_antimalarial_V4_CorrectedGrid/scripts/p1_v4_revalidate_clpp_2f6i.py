#!/usr/bin/env python3
"""One-task V4 PfClpP revalidation against genuine PfClpP structure 2F6I.

This worker intentionally produces only raw, independently auditable Vina
records. It never computes consensus, MPO, RRS, PNS, or manuscript values.
The canonical V4 centroid mapping is the 484-row
cluster_representatives_smiles.csv file; centroid_id is zero-based.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
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
CENTER_ATOMS = {
    ("A", 252, "OG"),
    ("A", 223, "NE2"),
    ("A", 219, "OD1"),
}
BOX = (28.0, 28.0, 28.0)
PADDING_A = 0.5
MIN_IN_BOX = 0.90
MAX_TRIAD_CONTACT_A = 10.0
EXHAUSTIVENESS = 16
NUM_MODES = 9
SEED = 0


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fail(message: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "failure.json").write_text(json.dumps({
        "schema": "p1-v4-clpp-2f6i-worker/v1",
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


def frame_check() -> dict:
    def ca(path: Path) -> dict:
        out = {}
        for line in path.read_text(errors="replace").splitlines():
            if line.startswith(("ATOM  ", "HETATM")) and line[12:16].strip() == "CA":
                try:
                    out[(line[21:22].strip(), line[22:26].strip())] = np.asarray(
                        [float(line[30:38]), float(line[38:46]), float(line[46:54])]
                    )
                except ValueError:
                    pass
        return out
    a, b = ca(RECEPTOR_PDB), ca(RECEPTOR_PDBQT)
    if not set(b).issubset(a):
        raise RuntimeError("2F6I PDBQT CA atoms are not a coordinate-identical subset of the PDB")
    common = sorted(set(b))
    delta = np.asarray([a[k] - b[k] for k in common])
    rmsd = float(np.sqrt(np.mean(delta ** 2)))
    max_delta = float(np.max(np.linalg.norm(delta, axis=1)))
    if rmsd > 1e-6 or max_delta > 1e-6:
        raise RuntimeError(f"2F6I PDB/PDBQT frame mismatch rmsd={rmsd} max={max_delta}")
    return {"status": "CA_SUBSET_FRAME_EQUIVALENT", "pdb_ca": len(a), "pdbqt_ca": len(b),
            "common_ca": len(common), "rmsd_A": rmsd, "max_delta_A": max_delta}


def read_smiles() -> list[str]:
    with SMILES_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 484 or list(rows[0]) != ["SMILES"]:
        raise RuntimeError(f"expected exactly 484 one-column centroid SMILES rows, got {len(rows)}")
    smiles = [row["SMILES"].strip() for row in rows]
    if any(not s for s in smiles) or len(set(smiles)) != 484:
        raise RuntimeError("centroid SMILES are empty or non-unique")
    return smiles


def prepare_ligand(smiles: str, out: Path) -> Path:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise RuntimeError("RDKit failed to parse centroid SMILES")
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, randomSeed=SEED, useRandomCoords=True) != 0:
        raise RuntimeError("RDKit deterministic 3-D embedding failed")
    AllChem.ComputeGasteigerCharges(mol)
    charges = [float(a.GetProp("_GasteigerCharge")) for a in mol.GetAtoms()]
    if not all(np.isfinite(charges)):
        raise RuntimeError("non-finite Gasteiger charge")
    prep = MoleculePreparation(
        merge_these_atom_types=("H",), hydrate=False, flexible_amides=False,
        rigid_macrocycles=False, min_ring_size=7, double_bond_penalty=50,
        charge_model="gasteiger", load_atom_params="ad4_types",
    )
    prepared = prep.prepare(mol)
    if not prepared:
        raise RuntimeError("Meeko returned no prepared molecule")
    pdbqt, ok, error = PDBQTWriterLegacy.write_string(prepared[0])
    if not ok:
        raise RuntimeError(f"Meeko PDBQT writer failed: {error}")
    ligand = out / "ligand.pdbqt"
    ligand.write_text(pdbqt, encoding="utf-8")
    (out / "ligand_preparation.json").write_text(json.dumps({
        "method": "RDKit_AddHs_EmbedMolecule_seed0_Gasteiger_Meeko",
        "smiles_sha256": sha256_bytes(smiles.encode()),
        "ligand_pdbqt_sha256": sha256(ligand),
        "explicit_hydrogens": True,
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--centroid-id", type=int, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()
    output_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    out = output_root / f"centroid_{args.centroid_id:04d}"
    if not (0 <= args.centroid_id < 484):
        fail("centroid-id must be 0..483", out)
    if out.exists() and any(out.iterdir()):
        fail(f"non-empty output exists: {out}", out)
    out.mkdir(parents=True, exist_ok=False)
    try:
        for p, label in [(SMILES_FILE, "SMILES file"), (RECEPTOR_PDB, "receptor PDB"),
                         (RECEPTOR_PDBQT, "receptor PDBQT"), (VINA, "Vina")]:
            if not p.is_file() or p.stat().st_size == 0:
                raise RuntimeError(f"missing/empty {label}: {p}")
        smiles = read_smiles()
        center, triad_info = read_anchor()
        triad = np.asarray(triad_info["coordinates_A"])
        frame = frame_check()
        ligand = prepare_ligand(smiles[args.centroid_id], out)
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
        record = {"schema": "p1-v4-clpp-2f6i-worker/v1", "status": "PASS_RAW_VINA",
                  "centroid_id": args.centroid_id, "smiles": smiles[args.centroid_id],
                  "smiles_sha256": sha256_bytes(smiles[args.centroid_id].encode()),
                  "smiles_file_sha256": sha256(SMILES_FILE), "receptor_pdb_sha256": sha256(RECEPTOR_PDB),
                  "receptor_pdbqt_sha256": sha256(RECEPTOR_PDBQT), "vina_sha256": sha256(VINA),
                  "target": "PfClpP", "pdb_id": "2F6I", "receptor_identity": "genuine PfClpP catalytic domain",
                  "triad": triad_info, "center_A": center.tolist(), "box_A": list(BOX),
                  "frame_check": frame, "gate": gate, "vina_affinity_kcal_mol": affinity,
                  "vina_command": cmd, "vina_log_sha256": sha256(out / "vina.log"),
                  "rescue_protocol": globals().get("RESCUE_PROTOCOL"),
                  "vina_out_sha256": sha256(vina_out), "created_utc": datetime.now(timezone.utc).isoformat(),
                  "consensus_written": False, "rrs_pns_updated": False}
        (out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps({"status": record["status"], "centroid_id": args.centroid_id,
                          "affinity": affinity, "output": str(out)}))
        return 0
    except Exception as exc:
        fail(str(exc), out)


if __name__ == "__main__":
    raise SystemExit(main())
