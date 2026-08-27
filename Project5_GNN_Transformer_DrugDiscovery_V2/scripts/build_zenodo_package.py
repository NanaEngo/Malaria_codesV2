#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20260827"
OUT = ROOT / f"zenodo_package_{STAMP}"

FILES = [
    "manuscript/P5_manuscript_V2608.tex",
    "manuscript/P5_manuscript_V2608.pdf",
    "manuscript/Cover_Letter_P5_JCAMD.tex",
    "manuscript/Cover_Letter_P5_JCAMD.pdf",
    "manuscript/Bibliography_P5.bib",
    "manuscript/P5_SI_V2608.tex",
    "manuscript/P5_SI_V2608.pdf",
    "manuscript/Table_P5_Study_Design.tex",
    "manuscript/Table_P5_Effect_Summary.tex",
    "manuscript/SUBMISSION_MANIFEST.md",
    "docs/P5V2_SUGGESTIONS_IMPLEMENTATION_MATRIX_20260827.md",
    "results/scientific_audit_20260825.json",
    "results/extended_campaign_20260825/README.md",
    "results/extended_campaign_20260825/campaign_config.json",
    "results/extended_campaign_20260825/robustness/extended_analysis_summary.json",
    "results/extended_campaign_20260825/robustness/extended_model_aggregates.csv",
    "results/extended_campaign_20260825/robustness/paired_ablation_contrasts.csv",
    "results/extended_campaign_20260825/robustness/split_audit.json",
    "results/extended_campaign_20260825/robustness/chemical_standardization_audit.json",
    "results/extended_campaign_20260825/robustness/chembl_threshold_sensitivity.json",
    "results/extended_campaign_20260825/robustness/salience_stability.csv",
    "results/extended_campaign_20260825/chemberta/chemberta_completion_audit_20260827.json",
    "results/calibration_20260827/calibration_summary.csv",
    "results/calibration_20260827/summary.json",
    "scripts/p5_calibration_posthoc.py",
]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    records = []
    missing = []
    for rel in FILES:
        src = ROOT / rel
        if not src.is_file():
            missing.append(rel)
            continue
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        records.append({"path": rel, "bytes": dst.stat().st_size, "sha256": sha256(dst)})
    manifest = {
        "schema_version": 1,
        "created_utc": "2026-08-27",
        "status": "READY_FOR_AUTHOR_REVIEW_NOT_UPLOADED",
        "project": "P5_GNN_Transformer_DrugDiscovery_V2",
        "reserved_doi": "10.5281/zenodo.19608875",
        "files_expected": len(FILES),
        "files_staged": len(records),
        "missing": missing,
        "files": records,
        "exclusions": ["Slurm logs", "LaTeX auxiliary files", "Python caches", "model caches", "temporary files", "credentials"],
        "boundary": "Local staging only. No Zenodo upload or DOI publication was performed.",
    }
    (OUT / "ZENODO_PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("status", "files_expected", "files_staged", "missing")}, indent=2))

if __name__ == "__main__":
    main()
