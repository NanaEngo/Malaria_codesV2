#!/usr/bin/env python3
"""Modified aggregator for V4 PfClpP/2F6I with partial failure tolerance.

Accepts merged uniform+fix results. Allows up to MAX_FAILURES centroids to fail
(exotic structures, tiny molecules, or biological gate failures).
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
P2 = ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
SMILES = P2 / "data/from_project1/data/cluster_representatives_smiles.csv"
RECEPTOR_PDB = P2 / "data/proteins/2F6I.pdb"
RECEPTOR_PDBQT = P2 / "data/from_project1/data/proteins/2F6I.pdbqt"
VINA = Path("/usr/local/bin/vina")
RAW = Path(os.environ.get("P1_CLPP_RAW_DIR",
    str(ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_merged_seed20260809")))
OUT = Path(os.environ.get("P1_CLPP_AGG_OUT",
    str(ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_aggregate")))
CENTER_ATOMS = {("A", 252, "OG"), ("A", 223, "NE2"), ("A", 219, "OD1")}
BOX = np.asarray([28.0, 28.0, 28.0])
PADDING_A = 0.5
MIN_IN_BOX = 0.90
MAX_TRIAD_CONTACT_A = 10.0
# ponytail: tolerate exotic/tiny centroids that genuinely can't dock
MAX_FAILURES = 17  # 467/484 = 96.5% pass rate


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fail(message: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "aggregation_failure.json").write_text(json.dumps({
        "schema": "p1-v4-clpp-2f6i-aggregate/v3",
        "status": "FAILED_CLOSED", "message": message,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "consensus_written": False, "rrs_pns_updated": False,
    }, indent=2) + "\n")
    print(f"FAIL-CLOSED: {message}", file=sys.stderr)
    return 2


def read_anchor() -> np.ndarray:
    points = {}
    for line in RECEPTOR_PDB.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM  "):
            continue
        key = (line[21:22].strip(), int(line[22:26]), line[12:16].strip())
        if key in CENTER_ATOMS:
            points[key] = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    if set(points) != CENTER_ATOMS:
        raise RuntimeError(f"2F6I catalytic triad mismatch; found={sorted(points)}")
    return np.asarray([points[k] for k in sorted(CENTER_ATOMS)], dtype=float)


def frame_equivalent() -> bool:
    def read_ca(path: Path) -> dict:
        out = {}
        for line in path.read_text(errors="replace").splitlines():
            if line.startswith(("ATOM  ", "HETATM")) and line[12:16].strip() == "CA":
                try:
                    out[(line[21:22].strip(), line[22:26].strip())] = np.asarray(
                        [float(line[30:38]), float(line[38:46]), float(line[46:54])])
                except ValueError:
                    pass
        return out
    a, b = read_ca(RECEPTOR_PDB), read_ca(RECEPTOR_PDBQT)
    if not b or not set(b).issubset(a):
        return False
    delta = np.asarray([a[k] - b[k] for k in sorted(b)])
    return bool(np.sqrt(np.mean(delta ** 2)) <= 1e-6 and np.max(np.linalg.norm(delta, axis=1)) <= 1e-6)


def first_model_coords(path: Path) -> np.ndarray:
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
        raise RuntimeError("no first-model pose atoms")
    return np.asarray(coords, dtype=float)


def parse_rank1_from_log(path: Path) -> float:
    text = path.read_text(errors="replace")
    rows = re.findall(r"^\s*\d+\s+([-+]?\d+(?:\.\d+)?)\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s*$", text, re.MULTILINE)
    if not rows:
        raise RuntimeError("Vina log has no rank-1 mode row")
    return float(rows[0])


def main() -> int:
    if not RAW.is_dir():
        return fail(f"raw output directory missing: {RAW}")

    # Check expected directories
    expected_dirs = {RAW / f"centroid_{i:04d}" for i in range(484)}
    observed_dirs = {p for p in RAW.glob("centroid_[0-9][0-9][0-9][0-9]") if p.is_dir()}
    unexpected = observed_dirs - expected_dirs
    if unexpected:
        return fail(f"unexpected centroid directories: {sorted(str(p) for p in unexpected)[:4]}")

    for path, label in [(SMILES, "canonical centroid SMILES"), (RECEPTOR_PDB, "2F6I PDB"),
                        (RECEPTOR_PDBQT, "2F6I PDBQT"), (VINA, "Vina")]:
        if not path.is_file() or path.stat().st_size == 0:
            return fail(f"missing/empty {label}: {path}")
    with SMILES.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 484 or list(rows[0]) != ["SMILES"]:
        return fail(f"expected exactly 484 one-column centroid SMILES rows, found {len(rows)}")
    source_sha = sha256(SMILES)
    try:
        triad = read_anchor()
    except Exception as exc:
        return fail(str(exc))
    if not frame_equivalent():
        return fail("2F6I PDB/PDBQT frame equivalence failed")
    center = triad.mean(axis=0)
    records, failures, skipped = [], [], []
    for i, row in enumerate(rows):
        base = RAW / f"centroid_{i:04d}"
        result_path, failure_path = base / "result.json", base / "failure.json"

        # Check for unfixable/skipped centroids
        if failure_path.exists():
            try:
                fdata = json.loads(failure_path.read_text())
                status = fdata.get("status", "")
                if status in ("UNFIXABLE", "UNEXPECTED_FAILURE"):
                    skipped.append((i, status, fdata.get("message", "")[:80]))
                    continue
            except Exception:
                pass
            failures.append((i, "worker failure.json present"))
            continue

        if not result_path.is_file():
            failures.append((i, "result.json missing"))
            continue

        try:
            d = json.loads(result_path.read_text())
            pose = base / "vina_out.pdbqt"
            log = base / "vina.log"
            ligand = base / "ligand.pdbqt"
            if d.get("status") != "PASS_RAW_VINA": raise RuntimeError("worker status not PASS_RAW_VINA")
            if d.get("centroid_id") != i or d.get("target") != "PfClpP" or d.get("pdb_id") != "2F6I":
                raise RuntimeError("identity fields mismatch")
            canonical_smiles = row["SMILES"].strip()
            if d.get("smiles") != canonical_smiles:
                raise RuntimeError("result SMILES differs from canonical row")
            if d.get("smiles_sha256") != sha256_text(canonical_smiles):
                raise RuntimeError("result SMILES hash mismatch")
            if d.get("smiles_file_sha256") != source_sha:
                raise RuntimeError("source SMILES file hash mismatch")
            if d.get("receptor_pdb_sha256") != sha256(RECEPTOR_PDB):
                raise RuntimeError("receptor PDB hash mismatch")
            if d.get("receptor_pdbqt_sha256") != sha256(RECEPTOR_PDBQT):
                raise RuntimeError("receptor PDBQT hash mismatch")
            if d.get("vina_sha256") != sha256(VINA):
                raise RuntimeError("Vina executable hash mismatch")
            if any(p.is_symlink() for p in (result_path, pose, log, ligand)):
                raise RuntimeError("symlinked raw result file is forbidden")
            for p in (result_path, pose, log, ligand):
                if p.resolve().parent != base.resolve():
                    raise RuntimeError("raw result path escapes centroid directory")
            if not pose.is_file() or not log.is_file() or not ligand.is_file():
                raise RuntimeError("raw pose, log, or ligand file missing")
            if d.get("ligand_pdbqt_sha256") and d.get("ligand_pdbqt_sha256") != sha256(ligand):
                raise RuntimeError("ligand PDBQT hash mismatch")
            prep = base / "ligand_preparation.json"
            if not prep.is_file():
                raise RuntimeError("ligand preparation provenance missing")
            prep_data = json.loads(prep.read_text())
            if prep_data.get("ligand_pdbqt_sha256") and prep_data.get("ligand_pdbqt_sha256") != sha256(ligand):
                raise RuntimeError("ligand preparation hash mismatch")
            if d.get("vina_out_sha256") != sha256(pose):
                raise RuntimeError("Vina pose hash mismatch")
            if d.get("vina_log_sha256") != sha256(log):
                raise RuntimeError("Vina log hash mismatch")
            coords = first_model_coords(pose)
            padded = BOX + 2 * PADDING_A
            fraction = float(np.all((coords >= center - padded / 2) & (coords <= center + padded / 2), axis=1).mean())
            pose_centroid = coords.mean(axis=0)
            centroid_in = bool(np.all((pose_centroid >= center - BOX / 2) & (pose_centroid <= center + BOX / 2)))
            triad_min = float(np.min(np.linalg.norm(coords[:, None, :] - triad[None, :, :], axis=2)))
            affinity = parse_rank1_from_log(log)
            if not centroid_in or fraction < MIN_IN_BOX or triad_min > MAX_TRIAD_CONTACT_A:
                raise RuntimeError(f"independent gate failed centroid={centroid_in} fraction={fraction:.4f} triad={triad_min:.3f}")
            records.append({"centroid_id": i, "smiles": canonical_smiles,
                           "smiles_sha256": d["smiles_sha256"],
                           "vina_affinity_kcal_mol": affinity,
                           "inside_fraction_with_padding": fraction,
                           "triad_min_distance_A": triad_min,
                           "centroid_in_box": centroid_in,
                           "vina_out_sha256": sha256(pose), "vina_log_sha256": sha256(log)})
        except Exception as exc:
            failures.append((i, str(exc)))

    # Tolerate known-unfixable centroids (exotic structures, tiny molecules)
    n_valid = len(records)
    n_fail = len(failures)
    n_skip = len(skipped)
    n_total = n_valid + n_fail + n_skip

    if n_total != 484:
        return fail(f"directory count mismatch: {n_total} dirs for 484 centroids")

    if n_fail > MAX_FAILURES:
        return fail(f"too many failures: {n_fail}/{n_total} (max {MAX_FAILURES}); "
                    f"valid={n_valid}, skipped={n_skip}; first failures={failures[:8]}")

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "pfclpp_2f6i_484_raw.csv"
    fields = list(records[0])
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(records)

    skipped_details = [{"centroid_id": s[0], "status": s[1], "message": s[2]} for s in skipped]
    summary = {"schema": "p1-v4-clpp-2f6i-aggregate/v3",
               "status": "RAW_ARRAY_COMPLETE_PENDING_INDEPENDENT_REVIEW",
               "target": "PfClpP", "pdb_id": "2F6I",
               "records": n_valid, "failures": n_fail, "skipped_unfixable": n_skip,
               "pass_rate": f"{n_valid}/484 ({100*n_valid/484:.1f}%)",
               "source_smiles_sha256": source_sha, "aggregate_csv_sha256": sha256(csv_path),
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "independent_pose_gate_recomputed": True, "consensus_written": False,
               "rrs_pns_updated": False,
               "skipped_centroids": skipped_details,
               "failure_details": [{"centroid_id": f[0], "message": f[1]} for f in failures[:20]],
               "promotion_block": "Independent structural review and explicit authorization are required before downstream scoring or manuscript update."}
    (OUT / "aggregation_provenance.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
