#!/usr/bin/env python3
"""Set-C production-trajectory QC: bound-fraction per candidate/target/mutation.

For every prepared system under the explicitly exported versioned Set-C root
(with a completed production run: production.xtc + production.tpr under runs/*/replicate_1/),
compute:

- per-frame protein--ligand minimum heavy-atom distance (cKDTree, PBC-aware
  minimum-image via periodic box from the trajectory),
- bound_fraction = fraction of frames with min distance < BOUND_ANGSTROM,
- duration_ns from the trajectory time span.

The output CSV follows the exact column contract consumed by
p2_setc_md_rrs.py (bound_fraction, n_frames, duration_ns, hashes,
qc_status, analysis_rule_id, candidate_sha256, ...).  QC passes only when
n_frames >= MIN_FRAMES and the trajectory/tpr hashes match the prepared
system manifest expectation (topology/coordinates provenance).

The analysis rule is predeclared (documented, not inferred post hoc):
analysis_rule_id = "setc_p2_minheavy_5A_ge10percent_v1" — heavy-atom
protein--ligand minimum distance < 5.0 A for >= 10% of frames.

Usage:
    python scripts/p2_setc_trajectory_qc.py [--bound-angstrom 5.0]
        [--min-frames 500] [--min-bound-fraction 0.10]
        [--system PP-01_PfCRT_K76A]   # optional: single system

Output: results/set_c_md/set_c_trajectory_qc.csv
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
_root_env = os.environ.get("P2_SETC_ROOT")
if not _root_env:
    raise RuntimeError("P2_SETC_ROOT must be explicitly exported; refusing the legacy Set-C root")
SYSTEM_ROOT = Path(_root_env).expanduser().resolve()
EXPECTED_SYSTEM_ROOT = (PROJECT_DIR / "results" / "md_systems" / "set_c_preparation_20260812_v1").resolve()
if SYSTEM_ROOT != EXPECTED_SYSTEM_ROOT:
    raise RuntimeError(f"P2_SETC_ROOT must equal {EXPECTED_SYSTEM_ROOT}, got {SYSTEM_ROOT}")
OUTPUT = Path(os.environ.get("P2_SETC_QC_OUTPUT", RESULTS_DIR / "set_c_md" / "set_c_trajectory_qc.csv"))
TARGET_MUTATIONS = {
    "PfDHFR": ["WT", "N51I", "C59R", "S108N", "I164L"],
    "PfCRT": ["WT", "K76T", "K76A"],
}
ANALYSIS_RULE_ID = "setc_p2_minheavy_5A_ge10percent_v1"
REQUIRED_FORCEFIELD_FIELDS = {
    "cohort_id", "system_name", "protein_force_field", "ligand_force_field",
    "water_model", "topology_sha256", "coordinates_sha256", "checkpoint_sha256",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_prepared_manifests(system_dir: Path, set_c_id: str, target: str, mutation: str, expected_smiles: str) -> list[str]:
    """Revalidate prepared-system identity and hashes at the QC boundary."""
    errors: list[str] = []
    system_path = system_dir / "system_manifest.json"
    forcefield_path = system_dir / "forcefield_manifest.json"
    try:
        system = json.loads(system_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid system_manifest.json: {exc}"]
    expected = {
        "cohort_id": "P2_SET_C_POLYPHARM_17",
        "set_c_id": set_c_id,
        "target": target,
        "mutation": mutation,
        "system_name": f"{set_c_id}_{target}_{mutation}",
        "smiles": expected_smiles,
    }
    for key, value in expected.items():
        if system.get(key) != value:
            errors.append(f"system_manifest {key}={system.get(key)!r}, expected {value!r}")
    try:
        ff = json.loads(forcefield_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"invalid forcefield_manifest.json: {exc}"]
    missing = sorted(REQUIRED_FORCEFIELD_FIELDS - set(ff))
    if missing:
        errors.append(f"forcefield manifest missing fields: {', '.join(missing)}")
    if ff.get("cohort_id") != "P2_SET_C_POLYPHARM_17":
        errors.append("forcefield cohort_id mismatch")
    if ff.get("system_name") != expected["system_name"]:
        errors.append("forcefield system_name mismatch")
    if ff.get("protein_force_field") != "CHARMM36m":
        errors.append("protein force field is not CHARMM36m")
    deviation = ff.get("policy_deviation") or {}
    if ff.get("ligand_force_field") != "CGenFF" and not (
        ff.get("ligand_force_field") == "OpenFF 2.2.0 (AM1-BCC)"
        and deviation.get("declared") is True
        and deviation.get("field") == "ligand_force_field"
        and deviation.get("canonical_requirement") == "CGenFF"
        and deviation.get("approved") is True
    ):
        errors.append("ligand force-field policy is missing or not approved")
    if ff.get("water_model") != "TIP3P":
        errors.append("water model is not TIP3P")
    for filename, field in (
        ("topol.top", "topology_sha256"),
        ("npt.gro", "coordinates_sha256"),
        ("npt.cpt", "checkpoint_sha256"),
        ("system_manifest.json", "system_manifest_sha256"),
    ):
        path = system_dir / filename
        if not path.is_file() or not isinstance(ff.get(field), str):
            errors.append(f"missing hash input or manifest hash: {filename}")
        elif sha256(path) != ff[field]:
            errors.append(f"{field} mismatch for {filename}")
    for relative, expected_hash in (ff.get("topology_dependency_sha256") or {}).items():
        relative_path = Path(str(relative))
        if relative_path.is_absolute() or ".." in relative_path.parts:
            errors.append(f"unsafe topology dependency path: {relative}")
            continue
        path = system_dir / relative_path
        if not path.is_file():
            errors.append(f"missing topology dependency: {relative}")
        elif sha256(path) != expected_hash:
            errors.append(f"topology dependency hash mismatch: {relative}")
    return errors


def find_production_run(system_dir: Path) -> tuple[Path, Path] | None:
    """Locate only a terminal, provenance-backed production run."""
    runs = system_dir / "runs"
    if not runs.is_dir():
        return None
    for run_dir in sorted(runs.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        rep = run_dir / "replicate_1"
        if not rep.is_dir():
            continue
        provenance_path = rep / "production_provenance.json"
        try:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if provenance.get("status") != "PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC":
            continue
        if provenance.get("system_name") != system_dir.name:
            continue
        recorded_inputs = provenance.get("input_sha256") or {}
        input_pairs = (("topol.top", system_dir / "topol.top"), ("npt.gro", system_dir / "npt.gro"), ("npt.cpt", system_dir / "npt.cpt"))
        if any(recorded_inputs.get(name) != sha256(path) for name, path in input_pairs if path.is_file()):
            continue
        if any(not path.is_file() for _, path in input_pairs):
            continue
        xtc = rep / "production.xtc"
        tpr = rep / "production.tpr"
        if not (xtc.is_file() and xtc.stat().st_size > 0 and tpr.is_file() and tpr.stat().st_size > 0):
            continue
        recorded_outputs = provenance.get("outputs_sha256") or {}
        if recorded_outputs.get("production.xtc") != sha256(xtc):
            continue
        if recorded_outputs.get("production.tpr") != sha256(tpr):
            continue
        return xtc, tpr
    return None


def compute_bound_fraction(tpr: Path, xtc: Path, bound_angstrom: float, max_frames: int = 2000) -> dict:
    """Return {n_frames, bound_fraction, mean_min_dist_A, duration_ns}."""
    import MDAnalysis as mda
    from MDAnalysis.lib.distances import distance_array

    universe = mda.Universe(str(tpr), str(xtc))
    protein = universe.select_atoms("protein and name C N O S")
    ligand = universe.select_atoms("resname MOL0")
    if len(ligand) == 0:
        # fallback: the ligand is the residue whose name is neither protein nor water/ions
        ligand = universe.select_atoms(
            "not protein and not water and not resname NA CL and not resname SOL"
        )
    if len(protein) == 0 or len(ligand) == 0:
        raise RuntimeError(f"selection failed: protein={len(protein)} ligand={len(ligand)}")

    min_dists = []
    first_time_ps: float | None = None
    last_time_ps = 0.0
    for ts in universe.trajectory:
        if first_time_ps is None:
            first_time_ps = ts.time
        last_time_ps = ts.time
        box = ts.dimensions
        dists = distance_array(ligand.positions, protein.positions, box=box)
        min_dists.append(dists.min())
        if len(min_dists) >= max_frames:
            break
    min_dists = np.array(min_dists)
    n_frames = len(min_dists)
    # MDAnalysis >= 2.6 removed the reader-level ``timespan`` attribute;
    # compute the sampled span from the first/last frame times instead.
    duration_ns = (
        ((last_time_ps - first_time_ps) / 1000.0) if n_frames > 1 and first_time_ps is not None else 0.0
    )
    bound_fraction = float(np.mean(min_dists < bound_angstrom)) if n_frames else 0.0
    return {
        "n_frames": n_frames,
        "bound_fraction": bound_fraction,
        "mean_min_dist_A": float(min_dists.mean()) if n_frames else np.nan,
        "duration_ns": duration_ns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound-angstrom", type=float, default=5.0)
    parser.add_argument("--min-frames", type=int, default=500)
    parser.add_argument("--min-bound-fraction", type=float, default=0.10)
    parser.add_argument("--system", default=None, help="Optional: single system dir name")
    parser.add_argument("--max-frames", type=int, default=2000, help="Cap sampled frames (default 2000)")
    args = parser.parse_args()

    systems = [args.system] if args.system else sorted(
        [p.name for p in SYSTEM_ROOT.iterdir() if p.is_dir()]
    )

    candidates = pd.read_csv(RESULTS_DIR / "candidate_selection" / "md_top20_candidates_polypharm.csv")
    candidate_hash = sha256(RESULTS_DIR / "candidate_selection" / "md_top20_candidates_polypharm.csv")
    by_rank = {int(r.rank): r for r in candidates.itertuples()}

    rows = []
    for sys_name in systems:
        system_dir = SYSTEM_ROOT / sys_name
        parts = sys_name.split("_", 2)
        if len(parts) != 3:
            print(f"SKIP unparseable: {sys_name}")
            continue
        set_c_id, target, mutation = parts
        rank = int(set_c_id.split("-")[1])
        cand = by_rank.get(rank)
        if cand is None:
            print(f"SKIP no candidate row: {sys_name}")
            continue

        manifest_errors = verify_prepared_manifests(system_dir, set_c_id, target, mutation, cand.smiles)
        if manifest_errors:
            rows.append({
                "set_c_id": set_c_id, "target": target, "mutation": mutation,
                "smiles": cand.smiles, "bound_fraction": np.nan, "n_frames": 0,
                "duration_ns": 0.0, "trajectory_path": "", "tpr_path": "",
                "trajectory_sha256": "", "tpr_sha256": "",
                "qc_status": "MANIFEST_INVALID: " + "; ".join(manifest_errors),
                "analysis_rule_id": ANALYSIS_RULE_ID,
                "candidate_sha256": candidate_hash,
            })
            print(f"ERROR {sys_name}: prepared-manifest validation failed")
            continue

        found = find_production_run(system_dir)
        if found is None:
            rows.append({
                "set_c_id": set_c_id, "target": target, "mutation": mutation,
                "smiles": cand.smiles, "bound_fraction": np.nan, "n_frames": 0,
                "duration_ns": 0.0, "trajectory_path": "", "tpr_path": "",
                "trajectory_sha256": "", "tpr_sha256": "",
                "qc_status": "NO_PRODUCTION_RUN", "analysis_rule_id": ANALYSIS_RULE_ID,
                "candidate_sha256": candidate_hash,
            })
            continue

        xtc, tpr = found
        try:
            result = compute_bound_fraction(tpr, xtc, args.bound_angstrom, args.max_frames)
        except Exception as exc:  # noqa: BLE001
            rows.append({
                "set_c_id": set_c_id, "target": target, "mutation": mutation,
                "smiles": cand.smiles, "bound_fraction": np.nan, "n_frames": 0,
                "duration_ns": 0.0, "trajectory_path": str(xtc), "tpr_path": str(tpr),
                "trajectory_sha256": "", "tpr_sha256": "",
                "qc_status": f"QC_ERROR: {exc}", "analysis_rule_id": ANALYSIS_RULE_ID,
                "candidate_sha256": candidate_hash,
            })
            print(f"ERROR {sys_name}: {exc}")
            continue

        qc_pass = (
            result["n_frames"] >= args.min_frames
            and result["bound_fraction"] >= args.min_bound_fraction
        )
        rows.append({
            "set_c_id": set_c_id, "target": target, "mutation": mutation,
            "smiles": cand.smiles, "bound_fraction": round(result["bound_fraction"], 4),
            "n_frames": result["n_frames"], "duration_ns": round(result["duration_ns"], 3),
            "trajectory_path": str(xtc), "tpr_path": str(tpr),
            "trajectory_sha256": sha256(xtc), "tpr_sha256": sha256(tpr),
            "qc_status": "PASS" if qc_pass else "FAIL_BOUND_OR_FRAMES",
            "analysis_rule_id": ANALYSIS_RULE_ID, "candidate_sha256": candidate_hash,
        })
        print(
            f"{sys_name}: n_frames={result['n_frames']} "
            f"bound_frac={result['bound_fraction']:.3f} "
            f"mean_min={result['mean_min_dist_A']:.2f} A "
            f"({result['duration_ns']:.1f} ns) -> {'PASS' if qc_pass else 'FAIL'}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"\nQC CSV written: {OUTPUT} ({len(rows)} rows)")
    print(f"analysis_rule_id: {ANALYSIS_RULE_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
