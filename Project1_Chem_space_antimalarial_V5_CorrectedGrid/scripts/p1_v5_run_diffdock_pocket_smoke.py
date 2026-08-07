#!/usr/bin/env python3
"""Fail-closed fixed-center DiffDock smoke test for P1 V5.

Only PP-01/PfDHFR is permitted. The script creates a V5-local patched copy of
pinned DiffDock inference.py, adding a predeclared receptor/grid-center control
without modifying the external DiffDock checkout. Because the input is SMILES-only
and has no experimentally known bound pose, native ``pocket_knowledge`` is not
used. The script never launches a full 68-pair run, Vina, GROMACS, consensus, RRS,
or PNS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from rdkit import Chem

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
DIFFDOCK_HOME = Path("/home/nanaengo/software/DiffDock")
DIFFDOCK_PYTHON = Path("/home/nanaengo/miniforge3/envs/diffdock/bin/python")
SOURCE_ENTRYPOINT = DIFFDOCK_HOME / "inference.py"
SOURCE_CONFIG = V5 / "scripts/p1_v5_diffdock_inference_config.yaml"
MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
DEFAULT_OUT = V5 / "results/diffdock_pocket_smoke_PP01_PfDHFR"
CURRENT_PDB = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb"
CURRENT_RECEPTOR = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt"
CURRENT_CENTER = (1.33, -1.733, -23.842)
BOX = (25.0, 25.0, 25.0)
POCKET_CUTOFF_A = 5.0
POCKET_TR_MAX_A = 3.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"FAIL-CLOSED missing/empty {label}: {path}")


def pdbqt_coords(path: Path):
    coords = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith(("ATOM  ", "HETATM")):
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                pass
    return coords


def ca_frame_equivalence(pdb: Path, pdbqt: Path) -> dict:
    """Compare C-alpha identity/coordinates without modifying either receptor."""
    def read_ca(path: Path):
        result = {}
        for line in path.read_text(errors="replace").splitlines():
            if not line.startswith("ATOM  ") or line[12:16].strip() != "CA":
                continue
            try:
                key = (line[21:22].strip(), line[22:26].strip())
                result[key] = [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            except ValueError:
                continue
        return result

    import numpy as np
    a, b = read_ca(pdb), read_ca(pdbqt)
    common = sorted(set(a) & set(b))
    if set(a) != set(b) or not common:
        raise SystemExit("FAIL-CLOSED PDB/PDBQT C-alpha identity mismatch")
    delta = np.asarray([np.asarray(a[k]) - np.asarray(b[k]) for k in common], dtype=float)
    rmsd = float(np.sqrt(np.mean(delta ** 2)))
    max_norm = float(np.max(np.linalg.norm(delta, axis=1)))
    if rmsd > 1.0e-6 or max_norm > 1.0e-6:
        raise SystemExit(f"FAIL-CLOSED PDB/PDBQT C-alpha coordinate mismatch: rmsd={rmsd}, max={max_norm}")
    return {
        "method": "C-alpha keyed by chain+resseq",
        "pdb_ca_count": len(a),
        "pdbqt_ca_count": len(b),
        "common_ca_count": len(common),
        "rmsd_A": rmsd,
        "max_norm_A": max_norm,
        "status": "CA_FRAME_EQUIVALENT",
    }


def resolve_diffdock_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else DIFFDOCK_HOME / path


def sdf_valid_and_inside(path: Path) -> tuple[bool, float, int]:
    mol = next((m for m in Chem.SDMolSupplier(str(path), removeHs=False, sanitize=False) if m is not None), None)
    if mol is None or mol.GetNumConformers() == 0:
        return False, 0.0, 0
    coords = mol.GetConformer().GetPositions()
    import numpy as np
    coords = np.asarray(coords, dtype=float)
    if not np.isfinite(coords).all():
        return False, 0.0, mol.GetNumAtoms()
    center = np.asarray(CURRENT_CENTER, dtype=float)
    box = np.asarray(BOX, dtype=float)
    fraction = float(np.all((coords >= center - box / 2) & (coords <= center + box / 2), axis=1).mean())
    return True, fraction, mol.GetNumAtoms()


def patch_entrypoint(source: str) -> str:
    parser_anchor = "    parser.add_argument('--choose_residue', action='store_true', default=False, help='')\n"
    if parser_anchor not in source:
        raise SystemExit("FAIL-CLOSED pinned inference.py parser anchor not found")
    patched = source.replace(
        "from utils.sampling import randomize_position, sampling",
        "import random\n"
        "from utils.sampling import randomize_position as _native_randomize_position, sampling\n\n"
        "def randomize_position(data_list, no_torsion, no_random, tr_sigma_max, pocket_knowledge=False, pocket_cutoff=7,\n"
        "                       initial_noise_std_proportion=-1.0, choose_residue=False, fixed_center=None):\n"
        "    if fixed_center is None:\n"
        "        return _native_randomize_position(data_list, no_torsion, no_random, tr_sigma_max,\n"
        "                                         pocket_knowledge, pocket_cutoff,\n"
        "                                         initial_noise_std_proportion, choose_residue)\n"
        "    # Fixed-center initialization in the receptor-centered frame. This is\n"
        "    # not a post-hoc translation of an output pose.\n"
        "    _native_randomize_position(data_list, no_torsion, True, tr_sigma_max, False, pocket_cutoff,\n"
        "                               initial_noise_std_proportion, choose_residue)\n"
        "    receptor_mean = data_list[0]['receptor'].pos.mean(dim=0)\n"
        "    shift = fixed_center - receptor_mean\n"
        "    for graph in data_list:\n"
        "        graph['ligand'].pos = graph['ligand'].pos + shift\n",
        1,
    )
    seed_anchor = "def main(args):\n"
    if seed_anchor not in patched:
        raise SystemExit("FAIL-CLOSED pinned inference.py main anchor not found")
    patched = patched.replace(
        seed_anchor,
        "def main(args):\n"
        "    # V5 technical smoke reproducibility: seed all available RNGs.\n"
        "    random.seed(0)\n"
        "    np.random.seed(0)\n"
        "    torch.manual_seed(0)\n"
        "    if torch.cuda.is_available():\n"
        "        torch.cuda.manual_seed_all(0)\n"
        "        torch.backends.cudnn.deterministic = True\n"
        "        torch.backends.cudnn.benchmark = False\n",
        1,
    )
    patched = patched.replace(
        parser_anchor,
        parser_anchor
        + "    parser.add_argument('--pocket_knowledge', action='store_true', default=False, help='')\n"
        + "    parser.add_argument('--no_random_pocket', action='store_true', default=False, help='')\n"
        + "    parser.add_argument('--pocket_tr_max', type=float, default=3.0, help='')\n"
        + "    parser.add_argument('--pocket_cutoff', type=float, default=5.0, help='')\n"
        + "    parser.add_argument('--fixed_pocket_center', type=float, nargs=3, default=None, help='')\n",
        1,
    )
    old_call = "            randomize_position(data_list, score_model_args.no_torsion, False, score_model_args.tr_sigma_max,\n                               initial_noise_std_proportion=args.initial_noise_std_proportion,\n                               choose_residue=args.choose_residue)"
    new_call = "            fixed_center = None\n            if args.fixed_pocket_center is not None:\n"
    new_call += "                fixed_center = torch.tensor(args.fixed_pocket_center, dtype=orig_complex_graph['receptor'].pos.dtype, device=orig_complex_graph['receptor'].pos.device) - orig_complex_graph.original_center.squeeze(0)\n"
    new_call += "            randomize_position(data_list, score_model_args.no_torsion, args.no_random or args.no_random_pocket,\n"
    new_call += "                               score_model_args.tr_sigma_max if not args.fixed_pocket_center else args.pocket_tr_max,\n"
    new_call += "                               args.pocket_knowledge and fixed_center is None, args.pocket_cutoff,\n"
    new_call += "                               initial_noise_std_proportion=args.initial_noise_std_proportion,\n"
    new_call += "                               choose_residue=args.choose_residue, fixed_center=fixed_center)"
    if old_call not in patched:
        raise SystemExit("FAIL-CLOSED pinned inference.py randomization anchor not found")
    patched = patched.replace(old_call, new_call, 1)
    return patched


def parse_counts(text: str):
    match = re.search(r"Failed for (\d+) / \d+ complexes\.\s+Skipped (\d+) / \d+ complexes", text, re.S)
    if not match:
        raise SystemExit("FAIL-CLOSED smoke log lacks final failure/skip summary")
    return int(match.group(1)), int(match.group(2))


def write_failure_provenance(output: Path, base: dict, reason: str, **details) -> None:
    record = dict(base)
    record.update({
        "schema": "p1-v5-diffdock-fixed-center-smoke-failure/v1",
        "status": "TECHNICAL_SMOKE_FAILED_CLOSED",
        "reason": reason,
        "accepted_for_full_run": False,
        "biological_validation": False,
        "full_run_launched": False,
        "vina_launched": False,
        "consensus_scores_written": False,
        "rrs_pns_updated": False,
        **details,
    })
    (output / "failure_provenance.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    output = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"FAIL-CLOSED output directory exists and is non-empty: {output}")
    output.mkdir(parents=True, exist_ok=False)
    require_file(SOURCE_ENTRYPOINT, "pinned DiffDock inference.py")
    require_file(DIFFDOCK_PYTHON, "pinned DiffDock environment interpreter")
    require_file(SOURCE_CONFIG, "V5 DiffDock config")
    require_file(MANIFEST, "V5 DiffDock manifest")
    require_file(CURRENT_PDB, "exact DiffDock input receptor PDB")
    require_file(CURRENT_RECEPTOR, "current Vina receptor PDBQT")
    source = SOURCE_ENTRYPOINT.read_text(encoding="utf-8")
    patched = patch_entrypoint(source)
    patched_entrypoint = output / "inference_pocket_patched.py"
    patched_entrypoint.write_text(patched, encoding="utf-8")
    smoke_manifest = output / "smoke_input_manifest.csv"
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    rows = [r for r in rows if r["candidate_id"] == "PP-01" and r["target"] == "PfDHFR"]
    if len(rows) != 1:
        raise SystemExit("FAIL-CLOSED PP-01/PfDHFR row missing or duplicated")
    if Path(rows[0]["protein_path"]).resolve() != CURRENT_PDB.resolve():
        raise SystemExit("FAIL-CLOSED smoke manifest PDB is not the declared DiffDock receptor")
    frame_equivalence = ca_frame_equivalence(CURRENT_PDB, CURRENT_RECEPTOR)
    with smoke_manifest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    with SOURCE_CONFIG.open(encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise SystemExit("FAIL-CLOSED V5 DiffDock config is not a mapping")
    # inference.py applies YAML values after argparse parsing.  Therefore the
    # pocket controls must be recorded in an output-local config, not only on
    # the command line (otherwise the source config's false defaults win).
    config.update({
        "pocket_knowledge": False,
        "no_random_pocket": True,
        "pocket_cutoff": POCKET_CUTOFF_A,
        "pocket_tr_max": POCKET_TR_MAX_A,
    })
    smoke_config = output / "smoke_pocket_config.yaml"
    smoke_config.write_text(yaml.safe_dump(config, sort_keys=True), encoding="utf-8")
    expected_samples = int(config["samples_per_complex"])
    score_dir = resolve_diffdock_path(config["model_dir"])
    confidence_dir = resolve_diffdock_path(config["confidence_model_dir"])
    score_checkpoint = score_dir / config["ckpt"]
    confidence_checkpoint = confidence_dir / config["confidence_ckpt"]
    score_parameters = score_dir / "model_parameters.yml"
    confidence_parameters = confidence_dir / "model_parameters.yml"
    for path, label in (
        (score_checkpoint, "DiffDock score checkpoint"),
        (confidence_checkpoint, "DiffDock confidence checkpoint"),
        (score_parameters, "DiffDock score model parameters"),
        (confidence_parameters, "DiffDock confidence model parameters"),
    ):
        require_file(path, label)
    source_git_head = subprocess.run(
        ["git", "-C", str(DIFFDOCK_HOME), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    command = [
        str(DIFFDOCK_PYTHON), str(patched_entrypoint),
        "--config", str(smoke_config.resolve()),
        "--loglevel", "INFO",
        "--protein_ligand_csv", str(smoke_manifest.resolve()),
        "--out_dir", str(output.resolve()),
        "--no_random_pocket",
        "--pocket_cutoff", str(POCKET_CUTOFF_A),
        "--pocket_tr_max", str(POCKET_TR_MAX_A),
        "--fixed_pocket_center", *(str(value) for value in CURRENT_CENTER),
    ]
    started = datetime.now(timezone.utc).isoformat()
    log = output / "diffdock_execution.log"
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["DIFFDOCK_SEED"] = "0"
    env["PYTHONPATH"] = os.pathsep.join(
        [str(DIFFDOCK_HOME.resolve()), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    env["DIFFDOCK_RUN_MODE"] = "pocket_smoke"
    env["DIFFDOCK_POCKET_MODE"] = "fixed_receptor_grid_center_no_posthoc_translation"
    with log.open("w", encoding="utf-8") as handle:
        process = subprocess.run(command, cwd=DIFFDOCK_HOME, env=env, stdout=handle, stderr=subprocess.STDOUT, text=True)
    ended = datetime.now(timezone.utc).isoformat()
    text = log.read_text(encoding="utf-8", errors="replace")
    failure_base = {
        "mode": "fixed_center_smoke_only",
        "candidate_id": "PP-01",
        "target": "PfDHFR",
        "pdb_id": "7F3Y",
        "started_utc": started,
        "ended_utc": ended,
        "command": command,
        "cwd": str(DIFFDOCK_HOME),
        "python": str(DIFFDOCK_PYTHON.resolve()),
        "python_version": platform.python_version(),
        "diffdock_seed": 0,
        "source_entrypoint": str(SOURCE_ENTRYPOINT),
        "source_entrypoint_sha256": sha256(SOURCE_ENTRYPOINT),
        "patched_entrypoint_sha256": sha256(patched_entrypoint),
        "source_config_sha256": sha256(SOURCE_CONFIG),
        "smoke_config_sha256": sha256(smoke_config),
        "input_manifest_sha256": sha256(smoke_manifest),
        "diffdock_input_pdb": str(CURRENT_PDB),
        "diffdock_input_pdb_sha256": sha256(CURRENT_PDB),
        "receptor_pdbqt_sha256": sha256(CURRENT_RECEPTOR),
        "pdb_pdbqt_frame_equivalence": frame_equivalence,
        "log_sha256": sha256(log),
        "returncode": process.returncode,
        "pocket_parameters": {"mode": "predeclared_fixed_receptor_grid_center", "pocket_knowledge": False, "no_random_pocket": True, "fixed_center_pdb_coordinates": list(CURRENT_CENTER), "box_A": list(BOX)},
    }
    if process.returncode != 0:
        write_failure_provenance(output, failure_base, "DIFFDOCK_NONZERO_EXIT")
        raise SystemExit(f"FAIL-CLOSED pocket smoke returned exit code {process.returncode}; see {log}")
    failures, skipped = parse_counts(text)
    if failures != 0 or skipped != 0:
        write_failure_provenance(output, failure_base, "DIFFDOCK_FAILURE_OR_SKIP_COUNT", failures=failures, skipped=skipped)
        raise SystemExit(f"FAIL-CLOSED pocket smoke reports failures={failures}, skipped={skipped}")
    complex_dir = output / "PP-01_PfDHFR"
    rank1 = complex_dir / "rank1.sdf"
    confidence = sorted(complex_dir.glob("rank*_confidence*.sdf"))
    if len(confidence) != expected_samples:
        write_failure_provenance(output, failure_base, "CONFIDENCE_OUTPUT_COUNT_MISMATCH", expected=expected_samples, found=len(confidence))
        raise SystemExit(f"FAIL-CLOSED expected {expected_samples} confidence SDFs, found {len(confidence)}")
    valid, fraction, atoms = sdf_valid_and_inside(rank1)
    if not valid or fraction != 1.0:
        write_failure_provenance(output, failure_base, "RANK1_OUTSIDE_DECLARED_GRID", rank1_inside_fraction=fraction, rank1_atom_count=atoms)
        raise SystemExit(f"FAIL-CLOSED fixed-center smoke rank1 not fully IN_GRID: valid={valid}, fraction={fraction}")
    confidence_geometry = []
    for path in confidence:
        ok, conf_fraction, conf_atoms = sdf_valid_and_inside(path)
        if not ok:
            write_failure_provenance(output, failure_base, "CONFIDENCE_SDF_UNREADABLE", file=path.name)
            raise SystemExit(f"FAIL-CLOSED unreadable confidence SDF: {path}")
        confidence_geometry.append({
            "file": path.name,
            "sha256": sha256(path),
            "atom_count": conf_atoms,
            "inside_fraction": conf_fraction,
        })
    provenance = {
        "schema": "p1-v5-diffdock-fixed-center-smoke/v1",
        "status": "TECHNICAL_SMOKE_RANK1_VERIFIED_NO_BIOLOGICAL_VALIDATION",
        "mode": "fixed_center_smoke_only",
        "biological_validation": False,
        "status_scope": "rank1_only_technical_gate; not all confidence poses are required to be in-grid and this does not authorize the full run",
        "candidate_id": "PP-01",
        "target": "PfDHFR",
        "pdb_id": "7F3Y",
        "started_utc": started,
        "ended_utc": ended,
        "command": command,
        "cwd": str(DIFFDOCK_HOME),
        "pythonpath": env["PYTHONPATH"],
        "diffdock_seed": 0,
        "python": str(DIFFDOCK_PYTHON.resolve()),
        "python_version": platform.python_version(),
        "source_entrypoint": str(SOURCE_ENTRYPOINT),
        "source_entrypoint_sha256": sha256(SOURCE_ENTRYPOINT),
        "patched_entrypoint_sha256": sha256(patched_entrypoint),
        "source_config_sha256": sha256(SOURCE_CONFIG),
        "smoke_config_sha256": sha256(smoke_config),
        "input_manifest_sha256": sha256(smoke_manifest),
        "diffdock_source_git_head": source_git_head,
        "diffdock_score_checkpoint": str(score_checkpoint),
        "diffdock_score_checkpoint_sha256": sha256(score_checkpoint),
        "diffdock_score_parameters_sha256": sha256(score_parameters),
        "diffdock_confidence_checkpoint": str(confidence_checkpoint),
        "diffdock_confidence_checkpoint_sha256": sha256(confidence_checkpoint),
        "diffdock_confidence_parameters_sha256": sha256(confidence_parameters),
        "diffdock_input_pdb": str(CURRENT_PDB),
        "diffdock_input_pdb_sha256": sha256(CURRENT_PDB),
        "receptor_pdbqt_sha256": sha256(CURRENT_RECEPTOR),
        "pdb_pdbqt_frame_equivalence": frame_equivalence,
        "log_sha256": sha256(log),
        "returncode": process.returncode,
        "samples_per_complex": expected_samples,
        "rank1_sdf_sha256": sha256(rank1),
        "rank1_inside_fraction": fraction,
        "rank1_atom_count": atoms,
        "confidence_sdf_count": len(confidence),
        "confidence_geometry": confidence_geometry,
        "rank1_only_geometry_gate": True,
        "all_confidence_poses_in_grid": all(item["inside_fraction"] == 1.0 for item in confidence_geometry),
        "pocket_parameters": {"mode": "predeclared_fixed_receptor_grid_center", "pocket_knowledge": False, "no_random_pocket": True, "pocket_cutoff_A": POCKET_CUTOFF_A, "pocket_tr_max_A": "not_used_in_fixed_center_mode", "fixed_center_pdb_coordinates": list(CURRENT_CENTER), "box_A": list(BOX)},
        "full_run_launched": False,
        "vina_launched": False,
        "consensus_scores_written": False,
        "rrs_pns_updated": False,
        "accepted_for_full_run": False,
        "next_gate": "independent review of fixed-center smoke geometry and receptor/grid identity before any 68-pair run",
    }
    (output / "execution_provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(provenance, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
