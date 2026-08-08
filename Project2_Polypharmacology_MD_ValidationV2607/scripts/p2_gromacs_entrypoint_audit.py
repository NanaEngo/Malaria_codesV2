#!/usr/bin/env python3
"""Generate a provenance audit of P2 GROMACS entrypoints without execution."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "scripts"
OUTPUT = ROOT / "results" / "metrics" / "p2_gromacs_entrypoint_audit.json"

CANONICAL = [
    "scripts/md_full_pipeline.sh",
    "scripts/md_run_minimisation.sh",
    "scripts/md_run_nvt.sh",
    "scripts/md_run_npt.sh",
    "scripts/md_run_production.sh",
    "scripts/rebuild_438_complex_md.sh",
    "scripts/p2_setc_md_workflow.py",
]
LEGACY = {
    "scripts/md_build_complexes.py": "historical preparation utility; direct GROMACS calls; not publication-grade",
    "scripts/md_fix_dissociated_ligands.py": "historical rescue utility; direct GROMACS calls; not publication-grade",
    "scripts/prepare_pfdhfr_with_docked_pose.py": "historical one-off parent-lead preparation; not canonical",
    "scripts/auto_mmpbsa_438.sh": "historical monitor for excluded 438 conversion-artifact workflow",
    "scripts/preparation/": "historical preparation examples and generated command templates",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_record(relative: str) -> dict:
    path = ROOT / relative.rstrip("/")
    if path.is_dir():
        files = sorted(p for p in path.rglob("*") if p.is_file())
        return {"path": relative, "exists": True, "file_count": len(files), "sha256": None}
    return {"path": relative, "exists": path.is_file(), "sha256": sha256(path) if path.is_file() else None}


def main() -> int:
    record = {
        "schema": "p2-gromacs-entrypoint-audit/v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "audit_performed": True,
        "report_written": True,
        "execution_performed": False,
        "gromacs_launched_by_audit": False,
        "canonical_execution_policy": {
            "allowed_entrypoints": [source_record(p) for p in CANONICAL],
            "requirements": [
                "--execute where supported",
                "P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND",
                "exhaustive parent or set-C preflight",
                "canonical force-field manifest and hash validation",
                "no -maxwarn in publication-grade execution",
            ],
        },
        "legacy_noncanonical_entrypoints": [
            {**source_record(path), "reason": reason} for path, reason in LEGACY.items()
        ],
        "interpretation_rule": "Legacy scripts and outputs are historical/provenance context only; they cannot support new publication-grade trajectory, MD-RRS, or validated MM-GBSA claims.",
        "status": "AUDIT_COMPLETE_NO_EXECUTION",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
