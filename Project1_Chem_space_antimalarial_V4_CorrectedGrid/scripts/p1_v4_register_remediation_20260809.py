#!/usr/bin/env python3
"""Append the completed 2026-08-09 remediation evidence to the V4 2F6I
independent-review register without changing any review/signature state."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REGISTER = PROJECT / "results" / "pfclpp_2f6i_484_independent_review.json"
REMEDIATION_ROOT = PROJECT / "results" / "pfclpp_2f6i_484_remediation_20260809"
PROVENANCE = REMEDIATION_ROOT / "c_v4_2f6i_remediation_provenance.json"


def main() -> int:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    evidence = register.setdefault("evidence", {})
    evidence["remediation_20260809"] = {
        "array_job": "15016",
        "aggregate_job": "15044",
        "output_root": "results/pfclpp_2f6i_484_remediation_20260809",
        "relative_to": "Project1_Chem_space_antimalarial_V4_CorrectedGrid",
        "requested_centroids": prov["requested_centroids"],
        "records_found": prov["n_records_found"],
        "missing_records": prov["n_missing"],
        "status_counts": prov["status_counts"],
        "provenance_json": str(PROVENANCE.relative_to(PROJECT)),
        "summary_csv": str((REMEDIATION_ROOT / "c_v4_2f6i_remediation_summary.csv").relative_to(PROJECT)),
        "canonical_outputs_modified": False,
        "promotion": "EXPLORATORY_REMEDIATION_NOT_SUBMISSION_READY",
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    }
    REGISTER.write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence["remediation_20260809"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
