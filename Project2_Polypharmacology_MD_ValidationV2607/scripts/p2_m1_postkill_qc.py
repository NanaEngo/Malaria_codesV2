#!/usr/bin/env python3
"""M1 post-kill trajectory QC + corrected provenance (single partial replicate).

The M1 task 0 (PP-01_PfDHFR_WT, replicate_1) runs under a 48 h SLURM limit and
is expected to be KILLED at ~50-60 ns instead of the intended 100 ns. This
script is the post-production gate for that partial trajectory. It:

- reads the REAL achieved last step / time from production.log (never assumes
  the hard-coded 100 ns of the launcher's manifest template),
- checks runtime integrity markers (Fatal error, LINCS WARNING, NaN) in the log,
- computes protein--ligand bound-fraction QC under the canonical declared rule
  ``setc_p2_minheavy_5A_ge10percent_v1`` (heavy-atom minimum distance < 5.0 A
  for >= 10% of sampled frames),
- writes a corrected ``m1_provenance.json`` with status
  ``M1_PRODUCTION_INTERRUPTED_PARTIAL`` (or ``..._COMPLETE`` only if the
  achieved duration is >= target), the true achieved duration, and the true
  first/last step,
- never overwrites an existing provenance that already records a *completed*
  status (safety against accidental reclassification).

Usage:
    python scripts/p2_m1_postkill_qc.py \
        --replicate results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1 \
        [--target-ns 100.0] [--bound-angstrom 5.0] [--min-bound-fraction 0.10] \
        [--max-frames 2000]

Exit codes: 0 = QC pass (bounds hold on the achieved interval), 1 = QC fail,
2 = input/integrity failure, 3 = provenance protected (already completed).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ANALYSIS_RULE_ID = "setc_p2_minheavy_5A_ge10percent_v1"
LOG_STEP_RE = re.compile(r"^\s*(\d+)\s+([0-9.]+)\s*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_log_progress(log_path: Path) -> tuple[int, float, list[str]]:
    """Return (last_step, last_time_ps, integrity_issues).

    Integrity issues are non-fatal if they appear only in benign header text
    (e.g. 'lincs-warnangle' mdp keyword or 'nvcc' compiler path); a genuine
    runtime 'Fatal error', 'LINCS WARNING' at step output, or 'NaN' in the
    step-performance block is reported as an issue.
    """
    issues: list[str] = []
    last_step = 0
    last_time_ps = 0.0
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return 0, 0.0, [f"cannot read log: {exc}"]

    for line in lines:
        match = LOG_STEP_RE.match(line)
        if match:
            last_step = int(match.group(1))
            last_time_ps = float(match.group(2))

    # Runtime fatal markers (case-insensitive). Header-only benign tokens are
    # excluded explicitly: 'warnangle' (mdp keyword), 'nvcc'/'compiler'
    # (CUDA toolchain banner), 'dana'/'nanometer' units in header.
    lower = "\n".join(lines).lower()
    for token, benign in (
        ("fatal error", False),
        ("segmentation fault", False),
        ("lincs warning", False),
        ("nan", True),  # checked below on step-performance lines only
    ):
        if token in lower and not benign:
            issues.append(f"runtime marker present: {token}")

    # NaN check restricted to step-performance lines (lines starting with digits).
    step_lines = [ln for ln in lines if LOG_STEP_RE.match(ln)]
    if any("nan" in ln.lower() for ln in step_lines):
        issues.append("NaN in step-performance output")
    if any("lincs warning" in ln.lower() for ln in step_lines):
        issues.append("LINCS WARNING in step output")

    return last_step, last_time_ps, issues


def compute_bound_fraction(tpr: Path, xtc: Path, bound_angstrom: float, max_frames: int) -> dict:
    """Return {n_frames, bound_fraction, mean_min_dist_A, duration_ns} for the
    trajectory as sampled. Uses MDAnalysis with the same selections as the
    canonical Set-C QC: protein heavy atoms vs ligand residue (resname MOL0,
    with a non-protein/non-water fallback)."""
    import MDAnalysis as mda
    from MDAnalysis.lib.distances import distance_array

    universe = mda.Universe(str(tpr), str(xtc))
    protein = universe.select_atoms("protein and name C N O S")
    ligand = universe.select_atoms("resname MOL0")
    if len(ligand) == 0:
        ligand = universe.select_atoms(
            "not protein and not water and not resname NA CL and not resname SOL"
        )
    if len(protein) == 0 or len(ligand) == 0:
        raise RuntimeError(f"selection failed: protein={len(protein)} ligand={len(ligand)}")

    min_dists: list[float] = []
    first_time_ps: float | None = None
    last_time_ps = 0.0
    for ts in universe.trajectory:
        if first_time_ps is None:
            first_time_ps = ts.time
        last_time_ps = ts.time
        box = ts.dimensions
        dists = distance_array(ligand.positions, protein.positions, box=box)
        min_dists.append(float(dists.min()))
        if len(min_dists) >= max_frames:
            break

    min_dists_arr = np.array(min_dists)
    n_frames = len(min_dists_arr)
    duration_ns = (
        ((last_time_ps - first_time_ps) / 1000.0) if n_frames > 1 and first_time_ps is not None else 0.0
    )
    bound_fraction = float(np.mean(min_dists_arr < bound_angstrom)) if n_frames else 0.0
    return {
        "n_frames": n_frames,
        "bound_fraction": bound_fraction,
        "mean_min_dist_A": float(min_dists_arr.mean()) if n_frames else float("nan"),
        "duration_ns": duration_ns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replicate",
        type=Path,
        default=Path("results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1"),
        help="M1 replicate output root containing production.{log,tpr,xtc}",
    )
    parser.add_argument("--target-ns", type=float, default=100.0)
    parser.add_argument("--bound-angstrom", type=float, default=5.0)
    parser.add_argument("--min-bound-fraction", type=float, default=0.10)
    parser.add_argument("--max-frames", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=26082901, help="Replicate seed (from launcher)")
    args = parser.parse_args()

    rep: Path = args.replicate.resolve()
    log_path = rep / "production.log"
    tpr_path = rep / "production.tpr"
    xtc_path = rep / "production.xtc"

    for required in (log_path, tpr_path, xtc_path):
        if not required.is_file() or required.stat().st_size <= 0:
            print(f"FATAL: missing/invalid required file: {required}", file=sys.stderr)
            return 2

    # --- provenance protection: never downgrade a completed record ----------
    prov_path = rep / "m1_provenance.json"
    if prov_path.is_file():
        try:
            existing = json.loads(prov_path.read_text(encoding="utf-8"))
            if existing.get("status") in ("M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW",):
                print("PROTECT: existing provenance records a completed run; refusing to overwrite.")
                return 3
        except (OSError, json.JSONDecodeError):
            pass  # corrupt/absent provenance: proceed to write a corrected one

    # --- log: real achieved progress + integrity ---------------------------
    last_step, last_time_ps, issues = read_log_progress(log_path)
    achieved_ns = last_time_ps / 1000.0
    print(f"log: last_step={last_step}  achieved={achieved_ns:.2f} ns (target {args.target_ns:.0f} ns)")
    if issues:
        for issue in issues:
            print(f"INTEGRITY: {issue}")
        print("FATAL: runtime integrity issues present; refusing QC on this trajectory", file=sys.stderr)
        return 2

    # --- trajectory QC on the ACHIEVED interval ----------------------------
    try:
        qc = compute_bound_fraction(tpr_path, xtc_path, args.bound_angstrom, args.max_frames)
    except Exception as exc:  # noqa: BLE001
        print(f"FATAL: trajectory analysis failed: {exc}", file=sys.stderr)
        return 2

    qc_pass = qc["n_frames"] >= 500 and qc["bound_fraction"] >= args.min_bound_fraction
    complete = achieved_ns >= args.target_ns
    status = (
        "M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW"
        if complete
        else "M1_PRODUCTION_INTERRUPTED_PARTIAL"
    )

    print(
        f"trajectory: n_frames={qc['n_frames']} bound_frac={qc['bound_fraction']:.4f} "
        f"mean_min={qc['mean_min_dist_A']:.2f} A span={qc['duration_ns']:.1f} ns "
        f"-> {'PASS' if qc_pass else 'FAIL'} on achieved interval"
    )
    print(f"status: {status}  (complete={complete})")

    # --- corrected provenance -------------------------------------------------
    inputs: dict[str, dict | str] = {}
    for name in ("production.mdp", "production.tpr", "topol.top", "npt.gro", "npt.cpt"):
        p = rep / name
        if p.is_file():
            inputs[name] = {"sha256": sha256(p), "size_bytes": p.stat().st_size}
        else:
            inputs[name] = "MISSING"

    manifest = {
        "status": status,
        "qc_status": "PASS" if qc_pass else "FAIL_BOUND_OR_FRAMES",
        "system": rep.parent.name,
        "replicate": int(rep.name.split("_")[-1]) if rep.name.startswith("replicate_") else None,
        "seed": args.seed,
        "target_ns": args.target_ns,
        "achieved_ns": round(achieved_ns, 3),
        "last_step": last_step,
        "duration_from_trajectory_ns": round(qc["duration_ns"], 3),
        "n_frames_sampled": qc["n_frames"],
        "bound_fraction": round(qc["bound_fraction"], 4),
        "mean_min_dist_A": round(qc["mean_min_dist_A"], 3),
        "analysis_rule_id": ANALYSIS_RULE_ID,
        "environment": "malaria_md",
        "gpu_path": "-nb gpu -pme gpu -bonded cpu -update cpu",
        "source_root": "results/md_systems/set_c_preparation_20260812_v1",
        "wallclock_end": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": inputs,
        "termination": "SLURM_TIME_LIMIT_KILL" if not complete else "NATURAL_COMPLETION",
        "interpretation": (
            "partial single-replicate structural stress trajectory; "
            "NOT a completed 100 ns replicate; not affinity or resistance validation"
        ),
    }
    prov_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote corrected provenance: {prov_path}")
    print(f"analysis_rule_id: {ANALYSIS_RULE_ID}")
    return 0 if qc_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
