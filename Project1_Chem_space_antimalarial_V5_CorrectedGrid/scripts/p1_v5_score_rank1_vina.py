#!/usr/bin/env python3
"""Rescore verified DiffDock rank-1 poses with local AutoDock Vina.

This runner deliberately keeps DiffDock confidence and Vina affinity separate.
It only accepts the 68-row V5 input manifest and the corresponding verified raw
rank1.sdf files. It creates a new immutable output directory, records every
input/model/config/log hash, and never updates RRS/PNS or manuscript files.
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

from rdkit import Chem
from rdkit.Chem import AllChem
try:
    from meeko import MoleculePreparation, PDBQTWriterLegacy
except ImportError:  # pragma: no cover - the diffdock environment must provide Meeko
    MoleculePreparation = None
    PDBQTWriterLegacy = None

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
RAW = V5 / "results/diffdock_full_68_verified"
AUDIT_CSV = RAW / "independent_rank1_audit.csv"
AUDIT_JSON = RAW / "independent_rank1_audit.provenance.json"
DEFAULT_OUT = V5 / "results/vina_rank1_rescore_68"
VINA = shutil.which("vina") or "/usr/local/bin/vina"
MEEKO = shutil.which("mk_prepare_ligand.py") or "/home/nanaengo/miniforge3/envs/diffdock/bin/mk_prepare_ligand.py"

TARGETS = {
    "PfDHFR": {"pdb_id": "7F3Y", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt", "center": (1.33, -1.733, -23.842)},
    "PfCRT": {"pdb_id": "6UKJ", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/6UKJ.pdbqt", "center": (152.99, 151.042, 159.379)},
    "PfClpP": {"pdb_id": "2F6I", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/2F6I.pdbqt", "center": (-0.116, 40.446, 12.213)},
    "PfATP4": {"pdb_id": "9N10", "receptor": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/9N10.pdbqt", "center": (134.84, 133.10, 97.63)},
}
BOX = (25.0, 25.0, 25.0)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"FAIL-CLOSED missing/empty {label}: {path}")


def read_secondary_audit() -> tuple[dict, dict[str, dict]]:
    """Read and cryptographically bind the independent audit before scoring."""
    require_file(AUDIT_JSON, "independent DiffDock rank-1 audit provenance")
    require_file(AUDIT_CSV, "independent DiffDock rank-1 audit CSV")
    try:
        audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL-CLOSED invalid independent audit provenance: {AUDIT_JSON}") from exc
    if audit.get("expected_pairs") != 68 or audit.get("rank1_records") != 68:
        raise SystemExit("FAIL-CLOSED independent audit is not the expected 68-pair panel")
    if audit.get("rank1_valid") != 68 or audit.get("rank1_confidence_valid") != 68:
        raise SystemExit("FAIL-CLOSED independent audit does not validate all rank-1 pose/confidence SDFs")
    if audit.get("status") != "RANK1_VERIFIED_SECONDARIES_PARTIAL_VINA_GATE_BLOCKED":
        raise SystemExit("FAIL-CLOSED unexpected independent audit status")
    if audit.get("audit_csv_sha256") != sha256(AUDIT_CSV):
        raise SystemExit("FAIL-CLOSED independent audit CSV hash does not match its provenance")
    with AUDIT_CSV.open(encoding="utf-8", newline="") as f:
        records = list(csv.DictReader(f))
    if len(records) != 68 or len({r["complex_name"] for r in records}) != 68:
        raise SystemExit("FAIL-CLOSED independent audit CSV is not a unique 68-pair panel")
    by_name = {r["complex_name"]: r for r in records}
    if any(r.get("grid_status") != "IN_GRID" for r in records):
        raise SystemExit("FAIL-CLOSED Vina score-only gate: at least one audited rank-1 pose is not fully IN_GRID")
    return audit, by_name


def read_manifest() -> list[dict[str, str]]:
    require_file(MANIFEST, "V5 input manifest")
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 68:
        raise SystemExit(f"FAIL-CLOSED expected 68 manifest rows, found {len(rows)}")
    names = {r["complex_name"] for r in rows}
    if len(names) != 68:
        raise SystemExit("FAIL-CLOSED duplicate complex names in manifest")
    for r in rows:
        if r["target"] not in TARGETS:
            raise SystemExit(f"FAIL-CLOSED unexpected target: {r['target']}")
        if r["target"] == "PfClpP" and r["pdb_id"] == "4GM2":
            raise SystemExit("FAIL-CLOSED target identity mismatch: 4GM2 is PfClpR, not PfClpP")
        if r["target"] == "PfClpP" and r["pdb_id"] != "2F6I":
            raise SystemExit("FAIL-CLOSED PfClpP rows must reference the verified 2F6I receptor (EC 3.4.21.92)")
        if not r["candidate_id"] or not r["ligand_description"]:
            raise SystemExit(f"FAIL-CLOSED incomplete manifest row: {r['complex_name']}")
    return rows


def parse_vina_affinity(text: str) -> float:
    matches = re.findall(r"^\s*Affinity:\s*([-+]?\d+(?:\.\d+)?)\s*\(kcal/mol\)", text, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one Vina Affinity line, found {len(matches)}")
    return float(matches[0])


def run_one(row: dict[str, str], output: Path, vina_version: str) -> dict:
    target = TARGETS[row["target"]]
    raw_dir = RAW / row["complex_name"]
    sdf = raw_dir / "rank1.sdf"
    require_file(sdf, f"verified DiffDock rank1 SDF for {row['complex_name']}")
    receptor = target["receptor"]
    require_file(receptor, f"local receptor for {row['target']}")
    pair_dir = output / row["complex_name"]
    pair_dir.mkdir()
    ligand_pdbqt = pair_dir / "rank1.pdbqt"
    conversion_log = pair_dir / "meeko_conversion.log"
    if MEEKO is None or MoleculePreparation is None or PDBQTWriterLegacy is None:
        raise SystemExit("FAIL-CLOSED Meeko 0.7.1 CLI/API is unavailable")
    try:
        supplier = Chem.SDMolSupplier(str(sdf), removeHs=False, sanitize=False)
        mol = next((candidate for candidate in supplier if candidate is not None), None)
        if mol is None:
            raise ValueError("RDKit could not read rank1.sdf")
        Chem.SanitizeMol(mol)
        # DiffDock writes implicit hydrogens and no partial charges. Meeko 0.7.1
        # requires explicit Hs and finite Gasteiger charges for PDBQT writing.
        AllChem.ComputeGasteigerCharges(mol)
        charges = [float(atom.GetProp("_GasteigerCharge")) for atom in mol.GetAtoms()]
        if not all(value == value and abs(value) < 1e100 for value in charges):
            raise ValueError("RDKit Gasteiger charge calculation produced non-finite values")
        mol = Chem.AddHs(mol, addCoords=True)
        AllChem.ComputeGasteigerCharges(mol)
        preparator = MoleculePreparation(
            merge_these_atom_types=("H",),
            hydrate=False,
            flexible_amides=False,
            rigid_macrocycles=False,
            min_ring_size=7,
            double_bond_penalty=50,
            charge_model="gasteiger",
            load_atom_params="ad4_types",
        )
        prepared = preparator.prepare(mol)
        if not prepared:
            raise ValueError("Meeko returned no prepared molecule")
        pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(prepared[0])
        if not is_ok:
            raise ValueError(f"PDBQT writer failed: {error_msg}")
        ligand_pdbqt.write_text(pdbqt_string, encoding="utf-8")
        conversion_log.write_text(
            "conversion_method=Meeko_API_MoleculePreparation_PDBQTWriterLegacy\n"
            "explicit_hydrogens_added=true\n"
            "gasteiger_charges_recomputed=true\n"
            f"input_atoms={mol.GetNumAtoms()}\n"
            "status=PASS\n",
            encoding="utf-8",
        )
    except Exception as exc:
        conversion_log.write_text(f"conversion_method=Meeko_API\nstatus=FAIL\nerror={exc}\n", encoding="utf-8")
        raise SystemExit(f"FAIL-CLOSED Meeko conversion failed for {row['complex_name']}: {conversion_log}") from exc
    if not ligand_pdbqt.is_file() or ligand_pdbqt.stat().st_size == 0:
        raise SystemExit(f"FAIL-CLOSED Meeko wrote no PDBQT for {row['complex_name']}: {conversion_log}")
    vina_log = pair_dir / "vina_score_only.log"
    cx, cy, cz = target["center"]
    cmd = [
        VINA,
        "--receptor", str(receptor.resolve()),
        "--ligand", str(ligand_pdbqt.resolve()),
        "--score_only",
        "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
        "--size_x", str(BOX[0]), "--size_y", str(BOX[1]), "--size_z", str(BOX[2]),
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    vina_log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(f"FAIL-CLOSED Vina score_only failed for {row['complex_name']}: {vina_log}")
    try:
        affinity = parse_vina_affinity(result.stdout + result.stderr)
    except ValueError as exc:
        raise SystemExit(f"FAIL-CLOSED Vina output parse failed for {row['complex_name']}: {exc}") from exc
    return {
        "complex_name": row["complex_name"], "candidate_id": row["candidate_id"], "target": row["target"], "pdb_id": row["pdb_id"],
        "rank1_sdf": str(sdf.resolve()), "rank1_sdf_sha256": sha256(sdf),
        "rank1_pdbqt": str(ligand_pdbqt.resolve()), "rank1_pdbqt_sha256": sha256(ligand_pdbqt),
        "receptor": str(receptor.resolve()), "receptor_sha256": sha256(receptor),
        "vina_score_only_kcal_mol": affinity,
        "diffdock_confidence_is_not_affinity": True,
        "conversion_log_sha256": sha256(conversion_log), "vina_log_sha256": sha256(vina_log),
        "vina_command": cmd, "vina_version": vina_version,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--limit", type=int, default=None, help="Smoke limit; must be 1 or omitted, never used for a full result.")
    args = ap.parse_args()
    output = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"FAIL-CLOSED output directory exists and is non-empty: {output}")
    output.mkdir(parents=True, exist_ok=False)
    require_file(Path(VINA), "AutoDock Vina executable")
    if MEEKO is None:
        raise SystemExit("FAIL-CLOSED Meeko executable mk_prepare_ligand.py not found")
    version = subprocess.run([VINA, "--version"], text=True, capture_output=True).stdout.strip()
    rows = read_manifest()
    audit, audit_rows = read_secondary_audit()
    for row in rows:
        audited = audit_rows.get(row["complex_name"])
        if audited is None or audited.get("rank1_sdf_sha256") != sha256(RAW / row["complex_name"] / "rank1.sdf"):
            raise SystemExit(f"FAIL-CLOSED stale or mismatched rank-1 audit hash: {row['complex_name']}")
    if args.limit is not None:
        if args.limit != 1:
            raise SystemExit("FAIL-CLOSED --limit is only permitted as a one-pair smoke test")
        rows = rows[:1]
    run_start = datetime.now(timezone.utc).isoformat()
    output_rows = []
    manifest_copy = output / "input_manifest.csv"
    manifest_copy.write_bytes(MANIFEST.read_bytes())
    try:
        for row in rows:
            output_rows.append(run_one(row, output, version))
    except Exception:
        (output / "RUN_FAILED_NO_ACCEPTED_RESULT").write_text("This directory is incomplete and must not be used for scoring or manuscript claims.\n", encoding="utf-8")
        raise
    out_csv = output / "vina_rank1_rescore.csv"
    fields = list(output_rows[0])
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(output_rows)
    provenance = {
        "schema": "p1-v5-vina-rank1-score-only/v1", "status": "VINA_RANK1_RESCORED_RAW",
        "started_utc": run_start, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "pairs": len(output_rows), "expected_pairs": 68, "mode": "smoke" if args.limit else "full",
        "vina_executable": str(Path(VINA).resolve()), "vina_version": version, "meeko_executable": str(Path(MEEKO).resolve()), "meeko_conversion_method": "MoleculePreparation+PDBQTWriterLegacy_with_explicit_Hs",
        "manifest_sha256": sha256(MANIFEST), "raw_diffdock_directory": str(RAW.resolve()),
        "raw_diffdock_rank1_only": True,
        "independent_audit_provenance": str(AUDIT_JSON.resolve()),
        "independent_audit_provenance_sha256": sha256(AUDIT_JSON),
        "secondary_pose_total": audit.get("secondary_pose_total"),
        "secondary_pose_invalid": audit.get("secondary_pose_invalid"),
        "target_configs": {k: {"pdb_id": v["pdb_id"], "receptor": str(v["receptor"].resolve()), "receptor_sha256": sha256(v["receptor"]), "center": v["center"], "box": BOX} for k, v in TARGETS.items()},
        "output_csv_sha256": sha256(out_csv), "consensus_scores_written": False, "rrs_pns_updated": False,
    }
    (output / "execution_provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": provenance["status"], "pairs": len(output_rows), "output": str(output), "csv_sha256": provenance["output_csv_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
