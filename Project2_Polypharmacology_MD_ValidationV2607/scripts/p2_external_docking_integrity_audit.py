#!/usr/bin/env python3
"""Audit isolated external docking outputs without producing RRS claims."""
from __future__ import annotations
import csv, hashlib, json, math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/results/robustness_transfer_20260827"
RUN = BASE / "external_docking_run_20260827"
PANEL = BASE / "external_docking_panel_candidate_40.csv"
OUT = BASE / "external_docking_integrity_audit_20260827.json"
STATES = ["PfDHFR_WT", "PfDHFR_N51I", "PfDHFR_C59R", "PfDHFR_S108N", "PfDHFR_I164L", "PfCRT_WT", "PfCRT_K76T", "PfCRT_K76A"]

def main() -> int:
    rows = list(csv.DictReader(PANEL.open(newline="")))
    expected = [(r["external_panel_id"], s) for r in rows for s in STATES]
    valid = []; missing = []; invalid = []
    for ligand, state in expected:
        path = RUN / f"{ligand}_{state}.pdbqt"
        if not path.is_file():
            missing.append({"ligand": ligand, "state": state}); continue
        text = path.read_text(errors="replace")
        match = re.search(r"REMARK VINA RESULT:\s*([-+]?\d+(?:\.\d+)?)", text)
        value = float(match.group(1)) if match else None
        if value is None or not math.isfinite(value):
            invalid.append({"ligand": ligand, "state": state, "reason": "missing_or_nonfinite_vina_score"}); continue
        valid.append({"ligand": ligand, "state": state, "score": value, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    status = "PASS_READY_FOR_AGGREGATION" if len(valid) == len(expected) else "BLOCKED_INCOMPLETE_OR_INVALID"
    report = {"schema_version": 1, "status": status, "expected": len(expected), "valid": len(valid), "missing": missing, "invalid": invalid, "records": valid}
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "expected", "valid")}, indent=2))
    return 0 if status.startswith("PASS") else 2

if __name__ == "__main__":
    raise SystemExit(main())
