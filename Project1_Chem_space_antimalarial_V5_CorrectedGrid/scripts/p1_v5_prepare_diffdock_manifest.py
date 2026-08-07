#!/usr/bin/env python3
"""Prepare the P1 V5 DiffDock input manifest without running DiffDock.

This script is intentionally side-effect bounded: it reads the canonical P2
Set-C cohort, target PDBs, and pinned local DiffDock artifacts; it writes only
an input CSV and a provenance JSON manifest. It never launches inference,
GROMACS, Vina, SLURM, or a network download.

The manifest is for P2 Set C (17 candidates x 4 targets = 68 pairs), which is
separate from P1 Set A and from the four parent-study MD systems.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch

from rdkit import Chem

PROJECT_ROOT = Path(__file__).resolve().parents[2]
P2_ROOT = PROJECT_ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
CANDIDATE_FILE = P2_ROOT / "results/candidate_selection/md_top20_candidates_polypharm.csv"
TARGETS = {
    "PfDHFR": P2_ROOT / "data/proteins/7F3Y.pdb",
    "PfCRT": P2_ROOT / "data/proteins/6UKJ.pdb",
    # 4GM2 is PfClpR, not PfClpP. Keep the intended cohort label explicit,
    # but fail closed before writing a new manifest until a genuine PfClpP PDB
    # is supplied and independently verified.
    "PfClpP": P2_ROOT / "data/proteins/4GM2.pdb",
    "PfATP4": P2_ROOT / "data/proteins/9N10.pdb",
}
BLOCKED_TARGET_IDENTITY = {"PfClpP": {"pdb_id": "4GM2", "actual_identity": "PfClpR", "reason": "4GM2 is not PfClpP"}}
DIFFDOCK_HOME = Path(os.environ.get("DIFFDOCK_HOME", "/home/nanaengo/software/DiffDock")).expanduser()
DIFFDOCK_ENTRYPOINT = Path(os.environ.get("DIFFDOCK_ENTRYPOINT", str(DIFFDOCK_HOME / "inference.py"))).expanduser()
SCORE_MODEL_DIR = Path(os.environ.get("DIFFDOCK_SCORE_MODEL_DIR", str(DIFFDOCK_HOME / "workdir/score_model"))).expanduser()
CONFIDENCE_MODEL_DIR = Path(os.environ.get("DIFFDOCK_CONFIDENCE_MODEL_DIR", str(DIFFDOCK_HOME / "workdir/confidence_model"))).expanduser()
SCORE_CHECKPOINT = SCORE_MODEL_DIR / os.environ.get("DIFFDOCK_SCORE_CKPT", "best_ema_inference_epoch_model.pt")
CONFIDENCE_CHECKPOINT = CONFIDENCE_MODEL_DIR / os.environ.get("DIFFDOCK_CONFIDENCE_CKPT", "best_model_epoch75.pt")
SCORE_PARAMS = SCORE_MODEL_DIR / "model_parameters.yml"
CONFIDENCE_PARAMS = CONFIDENCE_MODEL_DIR / "model_parameters.yml"
CONFIG_FILE = DIFFDOCK_HOME / "default_inference_args.yaml"
NORM_ARRAYS = {
    "score_norm": DIFFDOCK_HOME / ".score.npy",
    "so3_score_norms4": DIFFDOCK_HOME / ".so3_score_norms4.npy",
    "so3_exp_score_norms4": DIFFDOCK_HOME / ".so3_exp_score_norms4.npy",
}


def sha256(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Missing required file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_sha256(root: Path) -> str:
    """Hash a sorted list of file hashes for a reproducible source fingerprint."""
    if not root.is_dir():
        raise RuntimeError(f"Missing DiffDock source directory: {root}")
    lines: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        lines.append(f"{sha256(path)}  {relative}")
    return hashlib.sha256(("\\n".join(lines) + "\\n").encode()).hexdigest()


def git_revision(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def package_version(name: str) -> str | None:
    try:
        module = __import__(name)
        return str(getattr(module, "__version__", "unknown"))
    except Exception:
        return None


def canonical_smiles(value: str) -> str:
    molecule = Chem.MolFromSmiles(value.strip())
    if molecule is None:
        raise ValueError(f"Invalid SMILES: {value!r}")
    return Chem.MolToSmiles(molecule, canonical=True)


def require_file(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"{label} is missing or empty: {path}")
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256(path)}


def read_candidates() -> list[dict[str, Any]]:
    require_file(CANDIDATE_FILE, "canonical Set-C candidate file")
    with CANDIDATE_FILE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"rank", "smiles"}
    missing = sorted(required - set(rows[0] if rows else []))
    if missing:
        raise RuntimeError(f"Set-C candidate file missing columns: {missing}")
    if len(rows) != 17:
        raise RuntimeError(f"Expected exactly 17 Set-C rows, found {len(rows)}")

    candidates: list[dict[str, Any]] = []
    seen_smiles: set[str] = set()
    for row in sorted(rows, key=lambda item: int(item["rank"])):
        rank = int(row["rank"])
        if rank < 1 or rank > 17:
            raise RuntimeError(f"Unexpected Set-C rank: {rank}")
        smiles = canonical_smiles(row["smiles"])
        if smiles in seen_smiles:
            raise RuntimeError(f"Duplicate canonical Set-C SMILES at rank {rank}: {smiles}")
        seen_smiles.add(smiles)
        candidates.append({
            "candidate_id": f"PP-{rank:02d}",
            "rank": rank,
            "smiles": smiles,
            "source_smiles": row["smiles"],
        })
    if [item["rank"] for item in candidates] != list(range(1, 18)):
        raise RuntimeError("Set-C ranks are not exactly 1..17")
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/diffdock_polypharm",
    )
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_csv = output_dir / "diffdock_input_manifest.csv"
    manifest_json = output_dir / "diffdock_input_manifest.provenance.json"
    sentinel = output_dir / "NO_INFERENCE_SENTINEL"
    existing = list(output_dir.iterdir())
    if existing:
        raise RuntimeError(
            "Refusing to overwrite non-empty DiffDock manifest directory: "
            f"{output_dir}. Use a fresh --output-dir or remove it only after review."
        )

    candidates = read_candidates()
    for target, block in BLOCKED_TARGET_IDENTITY.items():
        if TARGETS[target].stem == block["pdb_id"]:
            raise RuntimeError(
                f"TARGET_IDENTITY_MISMATCH_BLOCKED: {block['pdb_id']} is {block['actual_identity']}, "
                f"not {target}; supply a verified PfClpP structure before preparing a manifest"
            )
    candidate_record = require_file(CANDIDATE_FILE, "canonical Set-C candidate file")
    target_records = {
        target: require_file(path, f"target receptor {target}")
        for target, path in TARGETS.items()
    }
    artifact_paths = {
        "diffdock_home": DIFFDOCK_HOME,
        "entrypoint": DIFFDOCK_ENTRYPOINT,
        "config": CONFIG_FILE,
        "score_model_parameters": SCORE_PARAMS,
        "score_checkpoint": SCORE_CHECKPOINT,
        "confidence_model_parameters": CONFIDENCE_PARAMS,
        "confidence_checkpoint": CONFIDENCE_CHECKPOINT,
        **NORM_ARRAYS,
    }
    artifact_records = {
        name: require_file(path, f"DiffDock artifact {name}")
        for name, path in artifact_paths.items()
        if name != "diffdock_home"
    }
    if not DIFFDOCK_HOME.is_dir():
        raise RuntimeError(f"DiffDock home is missing: {DIFFDOCK_HOME}")
    artifact_records["diffdock_home"] = {"path": str(DIFFDOCK_HOME.resolve())}

    rows: list[dict[str, str]] = []
    for candidate in candidates:
        for target, receptor in TARGETS.items():
            rows.append({
                "complex_name": f"{candidate['candidate_id']}_{target}",
                "candidate_id": candidate["candidate_id"],
                "candidate_rank": str(candidate["rank"]),
                "target": target,
                "pdb_id": receptor.stem,
                "protein_path": str(receptor.resolve()),
                "protein_sha256": target_records[target]["sha256"],
                "protein_sequence": "",
                "ligand_description": candidate["smiles"],
                "candidate_file_sha256": candidate_record["sha256"],
            })
    if len(rows) != 68 or len({row["complex_name"] for row in rows}) != 68:
        raise RuntimeError("Manifest does not contain exactly 68 unique pairs")

    with manifest_csv.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    provenance = {
        "schema": "p1-v5-diffdock-input-manifest/v2",
        "status": "INPUT_MANIFEST_ONLY_NO_INFERENCE",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "project": "P1 V5 migration",
        "cohort": "P2_SET_C_POLYPHARM_17",
        "cohort_boundary": {
            "p1_set_a": "separate",
            "p2_set_b_parent_md": "separate",
            "p2_set_c": "17 candidates used here",
            "parent_md_systems_not_reused": ["201-PfDHFR", "438-PfATP4", "164-PfClpP", "214-PfCRT"],
        },
        "pair_count": len(rows),
        "candidate_count": len(candidates),
        "target_count": len(TARGETS),
        "targets": list(TARGETS),
        "candidate_file": candidate_record,
        "targets_files": target_records,
        "generator": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256(Path(__file__).resolve()),
            "mode": "manifest_only_no_inference",
        },
        "runtime": {
            "python": sys.version,
            "torch": package_version("torch"),
            "rdkit": package_version("rdkit"),
            "cuda_available_observed": bool(torch.cuda.is_available()),
            "cuda_device_count_observed": int(torch.cuda.device_count()),
        },
        "diffdock_source": {
            "root": str(DIFFDOCK_HOME.resolve()),
            "git_revision": git_revision(DIFFDOCK_HOME),
            "tree_sha256": tree_sha256(DIFFDOCK_HOME),
        },
        "diffdock_artifacts": artifact_records,
        "diffdock_parameters": {
            "inference_steps": 20,
            "samples_per_complex": 10,
            "batch_size": 10,
            "confidence_checkpoint_explicit": CONFIDENCE_CHECKPOINT.name,
            "note": "Parameters are recorded for review; this script does not execute them.",
        },
        "manifest_csv": {
            "path": str(manifest_csv.resolve()),
            "bytes": manifest_csv.stat().st_size,
            "sha256": sha256(manifest_csv),
        },
        "execution": {
            "inference_launched": False,
            "slurm_submitted": False,
            "gromacs_launched": False,
            "scores_written": False,
            "rrs_pns_updated": False,
        },
        "required_raw_outputs_before_rescoring": [
            "68 non-empty complex directories",
            "rank1.sdf in every complex directory",
            "rank1_confidence*.sdf in every complex directory",
            "immutable execution log with command, environment, timestamps, and exit status",
            "output-to-manifest candidate/target identity match",
        ],
    }
    sentinel.write_text(
        "NO_INFERENCE\n"
        "This directory contains only a DiffDock input manifest and provenance.\n"
        "No DiffDock inference, scores, RRS, or PNS outputs are present or accepted.\n",
        encoding="utf-8",
    )
    provenance["sentinel"] = {
        "path": str(sentinel.resolve()),
        "sha256": sha256(sentinel),
        "meaning": "Input manifest only; no inference, scores, RRS, or PNS outputs accepted.",
    }
    manifest_json.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": provenance["status"],
        "pairs": len(rows),
        "manifest_csv": str(manifest_csv),
        "manifest_json": str(manifest_json),
        "inference_launched": False,
        "slurm_submitted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
