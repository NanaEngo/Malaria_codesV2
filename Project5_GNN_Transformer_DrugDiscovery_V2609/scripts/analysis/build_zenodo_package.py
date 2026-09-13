#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20260827"
OUT = ROOT / f"zenodo_package_{STAMP}"

# Files that must be present for the package to be submission-ready.
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

# Levier-3 light GNN sensitivity outputs (job 15617). A normal-mode run of
# p5_benchmark.py on the BASE GIN model emits exactly two files per config:
#   - *_results_*_sens_<cfg>.csv  (25 fold x seed records with finite AUC)
#   - *_ckpt_*_sens_<cfg>.json     (carries the per-fold `curve` key inline)
# A separate *_curves_*.json is only written in `--curves-only` runs, and a
# *_salience_*.json only for fusion models (GIN-TFP/TNE/FP): base GIN has no
# descriptor projection, hence no salience. Both are therefore NOT expected
# here and must not gate the package. Included automatically once the fold-
# level gates produce them; the package stays buildable (status
# PENDING_SENSITIVITY) while job 15617 is still queued/running.
SENSITIVITY_FILES = [
    "results/p5_GIN_scaffold_results_sens_h64_d02.csv",
    "results/p5_GIN_scaffold_ckpt_sens_h64_d02.json",
    "results/p5_GIN_scaffold_results_sens_h256_d01.csv",
    "results/p5_GIN_scaffold_ckpt_sens_h256_d01.json",
]

# p5_benchmark.py itself is part of the code deposit (canonical + sensitivity CLI).
CODE_FILES = [
    "scripts/p5_benchmark.py",
    "scripts/p5_sensitivity_gnn.sbatch",
]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def stage(records: list, missing: list, rel: str) -> None:
    src = ROOT / rel
    if not src.is_file():
        missing.append(rel)
        return
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    records.append({"path": rel, "bytes": dst.stat().st_size, "sha256": sha256(dst)})

def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    records: list = []
    missing: list = []
    for rel in FILES + CODE_FILES:
        stage(records, missing, rel)
    # Sensitivity files: staged only if present; otherwise recorded as pending.
    sensitivity_present: list = []
    sensitivity_pending: list = []
    for rel in SENSITIVITY_FILES:
        if (ROOT / rel).is_file():
            stage(records, sensitivity_present, rel)
        else:
            sensitivity_pending.append(rel)
    status = (
        "READY_FOR_UPLOAD_NOT_UPLOADED"
        if not sensitivity_pending
        else "PENDING_SENSITIVITY_15617_NOT_UPLOADED"
    )
    manifest = {
        "schema_version": 2,
        "created_utc": "2026-08-27",
        "status": status,
        "project": "P5_GNN_Transformer_DrugDiscovery_V2",
        "reserved_doi": "10.5281/zenodo.19608875",
        "files_expected": len(FILES) + len(CODE_FILES) + len(SENSITIVITY_FILES),
        "files_staged": len(records),
        "missing": missing,
        "sensitivity_files_present": sensitivity_present,
        "sensitivity_files_pending": sensitivity_pending,
        "sensitivity_output_contract": "Base-GIN normal-mode sensitivity runs (job 15617) emit two files per config (results CSV + ckpt JSON; curves embedded in ckpt, salience n/a for base GIN); no separate curves/salience JSON is expected",
        "files": records,
        "exclusions": ["Slurm logs", "LaTeX auxiliary files", "Python caches", "model caches", "temporary files", "credentials"],
        "boundary": "Local staging only. No Zenodo upload or DOI publication was performed.",
    }
    (OUT / "ZENODO_PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("status", "files_expected", "files_staged", "missing", "sensitivity_files_pending")}, indent=2))

if __name__ == "__main__":
    main()
