#!/usr/bin/env python3
"""Aggregate the external docking replication only when all 320 states are valid."""
from __future__ import annotations
import csv, hashlib, json, math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/results/robustness_transfer_20260827"
RUN = BASE / "external_docking_run_20260827"
PANEL = BASE / "external_docking_panel_candidate_40.csv"
OUT = BASE / "external_docking_aggregate_20260827"
STATES = ["PfDHFR_WT", "PfDHFR_N51I", "PfDHFR_C59R", "PfDHFR_S108N", "PfDHFR_I164L", "PfCRT_WT", "PfCRT_K76T", "PfCRT_K76A"]

# Declared EMBED_FAILURE (see frozen replication plan + repair ledger); its
# states are NOT part of the expected-valid aggregate.
DECLARED_EMBED_FAILURES = {"EXT-039"}


def score(path: Path) -> float | None:
    text = path.read_text(errors="replace")
    m = re.search(r"REMARK VINA RESULT:\s*([-+]?\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None


def main() -> int:
    rows = list(csv.DictReader(PANEL.open(newline="")))
    eligible = [r for r in rows if r["external_panel_id"] not in DECLARED_EMBED_FAILURES]
    expected = [(r["external_panel_id"], s) for r in eligible for s in STATES]
    records, missing, invalid = [], [], []
    for ligand, state in expected:
        p = RUN / f"{ligand}_{state}.pdbqt"
        if not p.exists():
            missing.append(str(p.relative_to(ROOT)))
            continue
        value = score(p)
        if value is None or not math.isfinite(value):
            invalid.append({"path": str(p.relative_to(ROOT)), "score": value})
            continue
        records.append({"external_panel_id": ligand, "state": state, "vina_score_kcal_mol": value, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    status = "READY_FOR_RRS_POSTPROCESSING" if not missing and not invalid and len(records) == len(expected) else "BLOCKED_INCOMPLETE_OR_INVALID_DOCKING"
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "status": status, "expected_records": len(expected), "valid_records": len(records), "missing_records": missing, "invalid_records": invalid, "states": STATES, "panel_sha256": hashlib.sha256(PANEL.read_bytes()).hexdigest(), "declared_embed_failures": sorted(DECLARED_EMBED_FAILURES)}
    (OUT / "aggregate_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if status != "READY_FOR_RRS_POSTPROCESSING":
        print(json.dumps(manifest, indent=2))
        return 2
    with (OUT / "external_docking_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=records[0].keys()); w.writeheader(); w.writerows(records)
    print(json.dumps(manifest, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
