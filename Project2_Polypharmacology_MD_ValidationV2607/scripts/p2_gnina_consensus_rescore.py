#!/usr/bin/env python3
"""
P2 — GNINA CNN consensus rescoring of external Vina poses (S5, 28 Aug 2026).

Post-processing only: rescore the *existing* Vina pose (MODEL 1) of each
external docking state with the local GNINA 1.3.2 CNN, without re-docking.

Canonical estimand unchanged: Vina-only scores remain the primary layer;
the GNINA CNN column is a consensus sensitivity. A class change between
scoring layers is reported as a discordance, never silently resolved.

Fail-closed rules (from the P2 DAR):
  * Non-empty output required; no empty manifest is reportable.
  * All expected states (40 ligands x 8 states = 320) must be present and
    produce a finite GNINA score; otherwise status = BLOCKED_INCOMPLETE.
  * No promotion of any CNN-based claim before this manifest is complete.

Usage:
  python p2_gnina_consensus_rescore.py \
      --poses results/robustness_transfer_20260827/external_docking_run_20260827 \
      --out results/robustness_transfer_20260827/gnina_consensus_20260828
"""

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

GNINA = Path("/home/nanaengo/gnina/gnina")
EXPECTED_STATES = 8
EXPECTED_LIGANDS = 40
EXPECTED_TOTAL = EXPECTED_STATES * EXPECTED_LIGANDS

VINA_RE = re.compile(r"REMARK VINA RESULT:\s+(-?[0-9.]+)")
GNINA_AFFINITY_RE = re.compile(r"affinity:\s+(-?[0-9.]+)")
GNINA_CNN_RE = re.compile(r"CNNaffinity:\s+(-?[0-9.]+)")


def parse_pose_metadata(path: Path):
    """Return (ligand_id, state) from a filename EXT-###_<State>.pdbqt."""
    name = path.stem  # e.g. EXT-003_PfCRT_K76T
    parts = name.split("_", 1)
    return parts[0], parts[1]


def read_vina_score(path: Path):
    """Extract the Vina score from the REMARK VINA RESULT line of MODEL 1."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = VINA_RE.search(line)
            if m:
                return float(m.group(1))
            if line.startswith("MODEL 2"):
                break
    return None


def extract_model1(path: Path, out_path: Path):
    """Extract MODEL 1 and strip MODEL/ENDMDL tags (GNINA score_only rejects them)."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        in_model1 = False
        lines = []
        for line in fh:
            if line.startswith("MODEL 1"):
                in_model1 = True
                continue
            if line.startswith("MODEL "):
                break
            if in_model1:
                if line.startswith("ENDMDL"):
                    break
                lines.append(line)
    if not lines:
        return False
    out_path.write_text("".join(lines), encoding="utf-8")
    return True


def run_gnina(pose: Path, receptor: Path, log_path: Path, work_dir: Path):
    """Run gnina --score_only on the existing pose; return (cnn_affinity) score."""
    clean_pose = work_dir / f"{pose.stem}.model1.pdbqt"
    if not extract_model1(pose, clean_pose):
        log_path.write_text("ERROR: no MODEL 1 found\n")
        return None
    cmd = [
        str(GNINA), "--score_only",
        "-r", str(receptor),
        "-l", str(clean_pose),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    log_path.write_text(proc.stdout + "\n---STDERR---\n" + proc.stderr)
    if proc.returncode != 0:
        return None
    cnn = None
    for line in proc.stdout.splitlines():
        m = re.search(r"CNNaffinity:\s+(-?[0-9.]+)", line)
        if m:
            cnn = float(m.group(1))
            break
    return cnn


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--poses", required=True, type=Path, help="Dir with EXT-*.pdbqt Vina poses")
    ap.add_argument("--out", required=True, type=Path, help="Output directory")
    ap.add_argument("--gnina", default=GNINA, type=Path)
    args = ap.parse_args()

    if not args.gnina.exists():
        print(f"FATAL: GNINA binary not found at {args.gnina}", file=sys.stderr)
        sys.exit(2)

    args.out.mkdir(parents=True, exist_ok=True)
    receptors = args.poses / "receptors"
    if not receptors.is_dir():
        print(f"FATAL: receptors dir not found under {args.poses}", file=sys.stderr)
        sys.exit(2)

    poses = sorted(args.poses.glob("EXT-*.pdbqt"))
    if len(poses) != EXPECTED_TOTAL:
        print(
            f"BLOCKED_INCOMPLETE: expected {EXPECTED_TOTAL} pose files, "
            f"found {len(poses)}", file=sys.stderr
        )
        sys.exit(3)

    rows = []
    failures = []
    work_dir = args.out / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    for pose in poses:
        ligand, state = parse_pose_metadata(pose)
        receptor = receptors / f"{state}.pdbqt"
        if not receptor.exists():
            failures.append((pose.name, f"missing receptor {receptor.name}"))
            continue
        vina = read_vina_score(pose)
        if vina is None:
            failures.append((pose.name, "no Vina REMARK score in MODEL 1"))
            continue
        log_path = args.out / f"{pose.stem}.log"
        cnn = run_gnina(pose, receptor, log_path, work_dir)
        if cnn is None:
            failures.append((pose.name, "GNINA returned no finite CNN score"))
            continue
        rows.append({
            "ligand": ligand,
            "state": state,
            "vina_score": round(vina, 3),
            "gnina_cnn_score": round(cnn, 3),
            "pose_file": pose.name,
        })

    if failures:
        print(f"BLOCKED_INCOMPLETE: {len(failures)} state(s) failed:", file=sys.stderr)
        for name, reason in failures[:20]:
            print(f"  {name}: {reason}", file=sys.stderr)
        (args.out / "failures.json").write_text(
            json.dumps([{"pose": n, "reason": r} for n, r in failures], indent=2)
        )
        sys.exit(4)

    if len(rows) != EXPECTED_TOTAL:
        print(f"BLOCKED_INCOMPLETE: expected {EXPECTED_TOTAL} scored rows, got {len(rows)}", file=sys.stderr)
        sys.exit(5)

    csv_path = args.out / "gnina_consensus_scores.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Per-state / per-ligand aggregates + class-change summary
    states = sorted({r["state"] for r in rows})
    summary = {"n_poses": len(rows), "n_states": len(states), "states": states}
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))

    # Hash provenance of inputs and outputs
    h = hashlib.sha256()
    for pose in poses:
        h.update(pose.read_bytes())
    manifest = {
        "status": "COMPUTED",
        "n_poses": len(rows),
        "n_failures": len(failures),
        "gnina_binary": str(args.gnina),
        "gnina_version": subprocess.run(
            [str(args.gnina), "--version"], capture_output=True, text=True
        ).stdout.strip().splitlines()[0] if args.gnina.exists() else "n/a",
        "input_poses_hash_sha256": h.hexdigest(),
        "expected_total": EXPECTED_TOTAL,
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"COMPUTED: {len(rows)} poses rescored -> {csv_path}")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
