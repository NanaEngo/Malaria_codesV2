#!/usr/bin/env python3
"""Independent audit of the failed-centroid 2F6I rescue layer.

This script never merges seed-0/exhaustiveness-16 records with rescue
seed-20260809/exhaustiveness-32 records into a canonical panel. It validates
rescue poses and hashes using the same geometry and identity rules as the
original aggregator, then writes a sensitivity report only.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Resolve the repository root by a required sibling project rather than by a
# fixed parent index; this remains portable if the checkout is relocated.
ROOT_CANDIDATES = [p for p in HERE.parents if (p / "Project2_Polypharmacology_MD_ValidationV2607").is_dir()]
if not ROOT_CANDIDATES:
    raise RuntimeError("cannot locate repository root containing Project2_Polypharmacology_MD_ValidationV2607")
ROOT = ROOT_CANDIDATES[0]
ORIGINAL_SCRIPT = HERE / "p1_v4_revalidate_clpp_2f6i.py"
ORIGINAL_RAW = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid" / "results/pfclpp_2f6i_484_raw"
RESCUE = Path(os.environ.get(
    "P1_CLPP_RESCUE_DIR",
    str(ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid" / "results/pfclpp_2f6i_484_rescue_seed20260809_v2"),
))
OUT = Path(os.environ.get(
    "P1_CLPP_RESCUE_AUDIT_OUT",
    str(ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid" / "results/pfclpp_2f6i_484_rescue_aggregate"),
))
P2 = ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
SMILES = P2 / "data/from_project1/data/cluster_representatives_smiles.csv"

# The imported worker predates this portability fix. Override only its
# read-only reference paths; no raw result is rewritten and no new docking is
# launched by this audit script.
worker_reference_paths = {
    "RECEPTOR_PDB": P2 / "data/proteins/2F6I.pdb",
    "RECEPTOR_PDBQT": P2 / "data/from_project1/data/proteins/2F6I.pdbqt",
}

spec = importlib.util.spec_from_file_location("p1_v4_original_aggregate_helpers", ORIGINAL_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load original worker helpers")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
for _name, _path in worker_reference_paths.items():
    setattr(worker, _name, _path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_requested_ids() -> set[int]:
    """Load the complete rescue request, not only original failure files.

    The first implementation used ``ORIGINAL_RAW/centroid_*/failure.json``.
    That is insufficient when the original audit stores some worker failures
    in a summary rather than one failure file per centroid. Prefer the tracked
    rescue request manifest; otherwise use the rescue tree itself and fail
    closed if the requested 35-record scope cannot be recovered.
    """
    manifest_path = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid" / "results" / "pfclpp_2f6i_484_run_manifests.json"
    if manifest_path.is_file():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            requested = payload.get("rescue_v2", {}).get("requested_centroid_ids")
            if requested:
                ids = {int(value) for value in requested}
                if ids:
                    return ids
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass
    ids = set()
    for p in RESCUE.glob("centroid_*"):
        try:
            ids.add(int(p.name.split("_")[-1]))
        except ValueError:
            pass
    if not ids:
        for p in ORIGINAL_RAW.glob("centroid_*/failure.json"):
            try:
                ids.add(int(p.parent.name.split("_")[-1]))
            except ValueError:
                pass
    return ids


def audit_one(cid: int, expected_smiles: str) -> tuple[dict | None, str | None]:
    base = RESCUE / f"centroid_{cid:04d}"
    result = base / "result.json"
    failure = base / "failure.json"
    pose = base / "vina_out.pdbqt"
    log = base / "vina.log"
    ligand = base / "ligand.pdbqt"
    try:
        if not result.is_file():
            if failure.is_file():
                failure_data = json.loads(failure.read_text(encoding="utf-8"))
                reason = str(failure_data.get("error") or failure_data.get("message") or failure_data.get("reason") or "failure.json present")
                raise ValueError(f"worker failure: {reason}")
            raise FileNotFoundError(result)
        d = json.loads(result.read_text())
        if d.get("status") != "PASS_RAW_VINA":
            raise ValueError("status is not PASS_RAW_VINA")
        if d.get("centroid_id") != cid or d.get("target") != "PfClpP" or d.get("pdb_id") != "2F6I":
            raise ValueError("identity fields mismatch")
        if d.get("smiles") != expected_smiles:
            raise ValueError("canonical SMILES mismatch")
        if d.get("smiles_file_sha256") != sha256(SMILES):
            raise ValueError("SMILES source hash mismatch")
        if d.get("receptor_pdb_sha256") != sha256(worker.RECEPTOR_PDB):
            raise ValueError("receptor PDB hash mismatch")
        if d.get("receptor_pdbqt_sha256") != sha256(worker.RECEPTOR_PDBQT):
            raise ValueError("receptor PDBQT hash mismatch")
        if d.get("vina_sha256") != sha256(worker.VINA):
            raise ValueError("Vina executable hash mismatch")
        if not pose.is_file() or not log.is_file() or not ligand.is_file():
            raise ValueError("raw pose/log/ligand missing")
        if d.get("vina_out_sha256") != sha256(pose) or d.get("vina_log_sha256") != sha256(log):
            raise ValueError("raw pose/log hash mismatch")
        if d.get("rescue_protocol", {}).get("seed") != 20260809:
            raise ValueError("rescue seed provenance missing")
        if d.get("rescue_protocol", {}).get("exhaustiveness") != 32:
            raise ValueError("rescue exhaustiveness provenance missing")
        center, triad_info = worker.read_anchor()
        pose_gate = worker.verify_pose(pose, center, __import__("numpy").asarray(triad_info["coordinates_A"]))
        return {"centroid_id": cid, "affinity": d.get("vina_affinity_kcal_mol"), "pose_gate": pose_gate, "result_sha256": sha256(result)}, None
    except Exception as exc:
        return None, str(exc)


def main() -> int:
    with SMILES.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 484 or list(rows[0]) != ["SMILES"]:
        raise SystemExit("FAIL-CLOSED: canonical 484-row SMILES source is invalid")
    expected = [r["SMILES"].strip() for r in rows]
    requested_ids = load_requested_ids()
    if len(requested_ids) != 35:
        raise SystemExit(f"FAIL-CLOSED: expected 35 rescue IDs, recovered {len(requested_ids)}")
    results, failures = [], []
    for cid in sorted(requested_ids):
        ok, error = audit_one(cid, expected[cid])
        if ok is not None:
            results.append(ok)
        else:
            failures.append({"centroid_id": cid, "reason": error})
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "pfclpp_2f6i_rescue_sensitivity.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["centroid_id", "affinity", "pose_gate", "result_sha256"])
        writer.writeheader()
        for row in results:
            row = dict(row)
            row["pose_gate"] = json.dumps(row["pose_gate"], sort_keys=True)
            writer.writerow(row)
    summary = {
        "schema": "p1-v4-clpp-2f6i-rescue-audit/v2",
        "status": "RESCUE_SENSITIVITY_AUDITED_PENDING_INDEPENDENT_REVIEW" if not failures else "RESCUE_SENSITIVITY_INCOMPLETE",
        "requested_rescue_ids": sorted(requested_ids),
        "requested_records": len(requested_ids),
        "rescue_records_audited": len(results),
        "rescue_records_failed_or_missing": failures,
        "rescue_records_unaccounted": len(requested_ids) - len(results) - len(failures),
        "rescue_protocol": {"seed": 20260809, "exhaustiveness": 32, "fixed_box_unchanged": True, "biological_gate_unchanged": True, "canonical_panel_promotion": False},
        "csv_sha256": sha256(csv_path),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "consensus_written": False,
        "rrs_pns_updated": False,
        "scientific_promotion_note": "This heterogeneous rescue layer is sensitivity evidence only. Scientific reconciliation of the uniform 484-record panel remains in progress; no editorial restriction blocks further development before explicit author reactivation."
    }
    (OUT / "rescue_audit_provenance.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
