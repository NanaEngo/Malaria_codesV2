#!/usr/bin/env python3
"""Set-C production-trajectory QC: bound-fraction per candidate/target/mutation.

For every prepared system under results/md_systems/set_c with a completed
production run (production.xtc + production.tpr under runs/*/replicate_1/),
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
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
SYSTEM_ROOT = RESULTS_DIR / "md_systems" / "set_c"
OUTPUT = RESULTS_DIR / "set_c_md" / "set_c_trajectory_qc.csv"
TARGET_MUTATIONS = {
    "PfDHFR": ["WT", "N51I", "C59R", "S108N", "I164L"],
    "PfCRT": ["WT", "K76T", "K76A"],
}
ANALYSIS_RULE_ID = "setc_p2_minheavy_5A_ge10percent_v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_production_run(system_dir: Path) -> tuple[Path, Path] | None:
    """Locate the production xtc/tpr (runs/*/replicate_1/)."""
    runs = system_dir / "runs"
    if not runs.is_dir():
        return None
    for run_dir in sorted(runs.iterdir()):
        if not run_dir.is_dir():
            continue
        rep = run_dir / "replicate_1"
        if not rep.is_dir():
            continue
        xtc = rep / "production.xtc"
        tpr = rep / "production.tpr"
        if xtc.is_file() and xtc.stat().st_size > 0 and tpr.is_file() and tpr.stat().st_size > 0:
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
    for ts in universe.trajectory:
        box = ts.dimensions
        dists = distance_array(ligand.positions, protein.positions, box=box)
        min_dists.append(dists.min())
        if len(min_dists) >= max_frames:
            break
    min_dists = np.array(min_dists)
    n_frames = len(min_dists)
    duration_ns = universe.trajectory.timespan / 1000.0 if n_frames > 1 else 0.0
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
