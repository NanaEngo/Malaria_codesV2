#!/usr/bin/env python3
"""Targeted remediation worker for the V4 PfClpP 2F6I 484-centroid panel.

Handles the 35 centroids that failed the original uniform run (job 13451) or
the rescue runs. For each requested centroid it:

  1. parses the canonical centroid SMILES;
  2. removes salt/buffer counter-ions (largest fragment) when multi-fragment;
  3. embeds with multiple random seeds (0, 1, 42, 2026) and an ETKDGv3
     fallback before giving up;
  4. assigns Gasteiger charges with a documented fallback to Meeko
     ``charge_model="zero"`` when Gasteiger is non-finite (recorded in
     provenance);
  5. pre-checks for elements that AutoDock Vina AD4 atom types do not support
     (e.g. boron) and records an explicit ``UNSUPPORTED_ELEMENT_FOR_AD4``
     classification instead of an unexplained Vina runtime failure;
  6. runs Vina with the identical receptor/box/anchor protocol as the
     canonical worker and applies the identical composite biological gate.

Every record carries full provenance (SMILES hash, preparation method, Vina
version, command, hashes). Canonical files are never modified: all outputs are
written under the isolated output root passed via ``--output-root``.
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
EXHAUSTIVENESS = 32
NUM_MODES = 9
SEEDS = (0, 1, 42, 2026)
# Elements with no AD4 atom type in AutoDock Vina 1.2.x default force field.
UNSUPPORTED_AD4_ELEMENTS = {"B", "Si", "Se", "Te", "As", "Sb", "Bi", "Ge", "Sn", "Pb", "Li", "Na", "K", "Mg", "Ca", "Zn", "Fe", "Cu", "Co", "Ni", "Mn", "Mo", "Cd", "Hg", "Al", "Ga", "In", "Tl", "Ti", "V", "Cr", "Zr", "Ag", "Au", "Pt", "Pd", "Ir", "Os", "Ru", "Rh", "W", "Re", "Hf", "Ta", "La", "Ce", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Sc", "Y", "Sr", "Ba", "Cs", "Rb", "Fr", "Ra", "U", "Th"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def classify(outcome: str, out: Path, **extra) -> None:
    record = {
        "schema": "p1-v4-clpp-2f6i-remediation-worker/v1",
        "status": outcome,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "consensus_written": False,
        "rrs_pns_updated": False,
    }
    record.update(extra)
    write_json(out / "remediation_result.json", record)


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


def largest_fragment(mol: Chem.Mol) -> tuple[Chem.Mol, int]:
    frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True)
    if len(frags) <= 1:
        return mol, 1
    big = max(frags, key=lambda m: m.GetNumHeavyAtoms())
    return big, len(frags)


def embed(mol: Chem.Mol) -> tuple[bool, str]:
    for seed in SEEDS:
        try:
            if AllChem.EmbedMolecule(mol, randomSeed=seed, useRandomCoords=True) == 0:
                return True, f"random_coords_seed_{seed}"
        except Exception:
            continue
    try:
        params = AllChem.ETKDGv3()
        params.randomSeed = 2026
        params.useRandomCoords = True
        if AllChem.EmbedMolecule(mol, params) == 0:
            return True, "etkdgv3_seed_2026"
    except Exception:
        pass
    return False, "embed_failed_all_strategies"


def prepare_ligand(smiles: str, out: Path) -> tuple[Path | None, dict]:
    """Return (ligand_pdbqt, provenance_meta). Raises on unrecoverable prep."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise RuntimeError("RDKit failed to parse centroid SMILES")
    mol, n_frags = largest_fragment(mol)
    elements = sorted({a.GetSymbol() for a in mol.GetAtoms()})
    unsupported = sorted(set(elements) & UNSUPPORTED_AD4_ELEMENTS)
    if unsupported:
        raise UnsupportedElement(unsupported)
    mol = Chem.AddHs(mol)
    ok, embed_method = embed(mol)
    if not ok:
        raise EmbeddingFailure()
    charge_method = "gasteiger"
    try:
        AllChem.ComputeGasteigerCharges(mol)
        charges = [float(a.GetProp("_GasteigerCharge")) for a in mol.GetAtoms()]
        if not all(np.isfinite(charges)):
            raise RuntimeError("non-finite Gasteiger charge")
    except Exception:
        # Meeko recomputes Gasteiger internally; zeroing the RDKit property alone
        # is NOT sufficient. Use Meeko's own zero charge model so the recorded
        # charge_method provenance matches the charges actually written.
        charge_method = "zero"
        for a in mol.GetAtoms():
            a.SetProp("_GasteigerCharge", "0.0")
    prep = MoleculePreparation(
        merge_these_atom_types=("H",), hydrate=False, flexible_amides=False,
        rigid_macrocycles=False, min_ring_size=7, double_bond_penalty=50,
        charge_model=charge_method, load_atom_params="ad4_types",
    )
    prepared = prep.prepare(mol)
    if not prepared:
        raise RuntimeError("Meeko returned no prepared molecule")
    pdbqt, ok, error = PDBQTWriterLegacy.write_string(prepared[0])
    if not ok:
        raise RuntimeError(f"Meeko PDBQT writer failed: {error}")
    ligand = out / "ligand.pdbqt"
    ligand.write_text(pdbqt, encoding="utf-8")
    meta = {
        "preparation_method": "RDKit_fragments_embed_gasteiger_or_zero_Meeko",
        "n_fragments_after_cleanup": n_frags,
        "charge_method": charge_method,
        "embed_method": embed_method,
        "ligand_pdbqt_sha256": sha256(ligand),
        "elements": elements,
    }
    write_json(out / "ligand_preparation.json", meta | {"status": "PASS"})
    return ligand, meta


class UnsupportedElement(Exception):
    def __init__(self, elements: list[str]):
        self.elements = elements
        super().__init__(f"unsupported AD4 element(s): {elements}")


class EmbeddingFailure(Exception):
    def __init__(self):
        super().__init__("RDKit 3-D embedding failed on all strategies")


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
    return result, centroid_in and fraction >= MIN_IN_BOX and triad_min <= MAX_TRIAD_CONTACT_A


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--centroid-id", type=int, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()
    output_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    out = output_root / f"centroid_{args.centroid_id:04d}"
    if not (0 <= args.centroid_id < 484):
        raise SystemExit(f"centroid-id must be 0..483, got {args.centroid_id}")
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"non-empty output exists: {out}")
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
        common = {"centroid_id": args.centroid_id, "smiles": smiles[args.centroid_id],
                  "smiles_sha256": sha256_bytes(smiles[args.centroid_id].encode()),
                  "smiles_file_sha256": sha256(SMILES_FILE),
                  "receptor_pdb_sha256": sha256(RECEPTOR_PDB),
                  "receptor_pdbqt_sha256": sha256(RECEPTOR_PDBQT),
                  "vina_sha256": sha256(VINA),
                  "target": "PfClpP", "pdb_id": "2F6I",
                  "receptor_identity": "genuine PfClpP catalytic domain",
                  "triad": triad_info, "center_A": center.tolist(), "box_A": list(BOX),
                  "frame_check": frame, "vina_version_cmd": str(VINA)}
        ligand, meta = prepare_ligand(smiles[args.centroid_id], out)
        cmd = [str(VINA), "--receptor", str(RECEPTOR_PDBQT), "--ligand", str(ligand),
               "--center_x", f"{center[0]:.6f}", "--center_y", f"{center[1]:.6f}",
               "--center_z", f"{center[2]:.6f}", "--size_x", str(BOX[0]),
               "--size_y", str(BOX[1]), "--size_z", str(BOX[2]),
               "--exhaustiveness", str(EXHAUSTIVENESS), "--num_modes", str(NUM_MODES),
               "--seed", str(0), "--out", str((out / "vina_out.pdbqt").resolve())]
        run = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        (out / "vina.log").write_text(run.stdout + run.stderr, encoding="utf-8")
        if run.returncode != 0:
            classify("VINA_RUNTIME_FAILURE", out, error=run.stdout[-500:] + run.stderr[-500:], **common, **meta)
            return 0
        vina_out = out / "vina_out.pdbqt"
        if not vina_out.is_file() or vina_out.stat().st_size == 0:
            classify("VINA_NO_OUTPUT", out, error="empty vina_out.pdbqt", **common, **meta)
            return 0
        affinity = parse_rank1(run.stdout + run.stderr)
        gate, gate_pass = verify_pose(vina_out, center, triad)
        if gate_pass:
            classify("PASS_RAW_VINA", out, vina_affinity_kcal_mol=affinity, gate=gate,
                     vina_out_sha256=sha256(vina_out), vina_log_sha256=sha256(out / "vina.log"),
                     **common, **meta)
        else:
            classify("DOCKED_GATE_FAILED", out, vina_affinity_kcal_mol=affinity, gate=gate,
                     vina_out_sha256=sha256(vina_out), vina_log_sha256=sha256(out / "vina.log"),
                     **common, **meta)
        return 0
    except UnsupportedElement as exc:
        classify("UNSUPPORTED_ELEMENT_FOR_AD4", out, unsupported_elements=exc.elements, **common)
        return 0
    except EmbeddingFailure:
        classify("EMBED_FAILURE_ALL_STRATEGIES", out, **common)
        return 0
    except Exception as exc:
        classify("PREPARATION_FAILURE", out, error=str(exc)[:400], **common)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
