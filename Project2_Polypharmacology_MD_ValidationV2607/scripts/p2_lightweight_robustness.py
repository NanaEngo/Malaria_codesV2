#!/usr/bin/env python3
"""Run local robustness analyses for the canonical P2 Set-C cohort.

No docking, network retrieval, or MD is performed. Existing docking scores are
recomputed under declared RRS eligibility/retention rules and bounded score
perturbations. STRING threshold sensitivity is reported as NOT_COMPUTED unless
reviewed threshold-specific interaction matrices are supplied explicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

TARGET_MUTATIONS = {"PfDHFR": ("N51I", "C59R", "S108N", "I164L"), "PfCRT": ("K76T", "K76A")}
THRESHOLDS = (4.0, 5.0, 6.0, 7.0)
RETENTION_RULES = ((70.0, 80.0), (75.0, 85.0), (80.0, 90.0))
PERTURBATIONS = (-0.20, -0.10, 0.10, 0.20)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(values: list[float], anchor: float, retention=(70.0, 80.0)) -> str:
    if not values:
        return "D"
    low, high = retention
    if all(v >= high for v in values):
        return "A*" if anchor >= 7.0 else "A"
    if all(v >= low for v in values):
        return "B"
    if any(v >= high for v in values):
        return "C"
    return "D"


def candidate_records(docking: pd.DataFrame, wt_threshold: float, retention=(70.0, 80.0), leave_out=None, perturbation=0.0) -> list[dict]:
    records = []
    for smiles, group in docking.groupby("smiles", sort=True):
        values, targets, anchors = [], [], []
        for target, mutations in TARGET_MUTATIONS.items():
            wt_rows = group[(group.target == target) & (group.mutation == "WT")]
            if wt_rows.empty:
                continue
            wt = abs(float(wt_rows.vina_score.mean()))
            if wt < wt_threshold:
                continue
            targets.append(target)
            anchors.append(wt)
            for mutation in mutations:
                if leave_out == mutation:
                    continue
                rows = group[(group.target == target) & (group.mutation == mutation)]
                if not rows.empty:
                    values.append(abs(float(rows.vina_score.mean()) * (1 + perturbation)) / wt * 100)
        anchor = min(anchors) if anchors else np.nan
        records.append({
            "smiles": smiles,
            "wt_threshold_kcal_mol": wt_threshold,
            "retention_low_percent": retention[0],
            "retention_high_percent": retention[1],
            "leave_out_mutant": leave_out or "none",
            "score_perturbation_percent": int(round(perturbation * 100)),
            "eligible_target_count": len(targets),
            "eligible_targets": ";".join(targets),
            "mutant_count": len(values),
            "rrs_mean": float(np.mean(values)) if values else np.nan,
            "rrs_class": classify(values, anchor, retention) if values else "D",
            "wt_anchor_min_abs_kcal_mol": anchor,
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--string-matrix-dir", type=Path, default=None, help="Optional reviewed directory containing threshold-specific STRING matrices")
    args = parser.parse_args()
    project = args.project_dir.resolve()
    results = project / "results"
    docking_path = results / "docking_mutants.csv"
    docking = pd.read_csv(docking_path)
    required = {"smiles", "target", "mutation", "vina_score"}
    missing = sorted(required - set(docking.columns))
    if missing:
        raise SystemExit(f"Missing docking columns: {', '.join(missing)}")
    if docking.smiles.nunique() != 17:
        raise SystemExit("Expected exactly 17 canonical candidate SMILES")

    outdir = results / "lightweight_robustness"
    outdir.mkdir(parents=True, exist_ok=True)
    threshold_rows = []
    for threshold in THRESHOLDS:
        for retention in RETENTION_RULES:
            threshold_rows.extend(candidate_records(docking, threshold, retention))
    threshold_df = pd.DataFrame(threshold_rows)
    threshold_df.to_csv(outdir / "rrs_threshold_sensitivity.csv", index=False, float_format="%.8f")

    loo_rows = []
    mutations = [None, *[m for values in TARGET_MUTATIONS.values() for m in values]]
    for mutation in mutations:
        loo_rows.extend(candidate_records(docking, 5.0, leave_out=mutation))
    loo_df = pd.DataFrame(loo_rows)
    loo_df.to_csv(outdir / "rrs_leave_one_mutant_out.csv", index=False, float_format="%.8f")

    perturb_rows = []
    for perturbation in PERTURBATIONS:
        perturb_rows.extend(candidate_records(docking, 5.0, perturbation=perturbation))
    perturb_df = pd.DataFrame(perturb_rows)
    perturb_df.to_csv(outdir / "docking_score_perturbation.csv", index=False, float_format="%.8f")

    if args.string_matrix_dir is not None and args.string_matrix_dir.exists():
        string_status = "INPUTS_AVAILABLE_NOT_ANALYZED"
        string_files = sorted(str(p) for p in args.string_matrix_dir.glob("**/*") if p.is_file())
    else:
        string_status = "NOT_COMPUTED_MISSING_THRESHOLD_SPECIFIC_STRING_MATRICES"
        string_files = []
    manifest = {
        "schema_version": 2,
        "scope": "P2_SET_C_POLYPHARM_17",
        "script": "scripts/p2_lightweight_robustness.py",
        "input": "results/docking_mutants.csv",
        "input_sha256": sha256(docking_path),
        "wt_thresholds_kcal_mol": list(THRESHOLDS),
        "retention_rules_low_high_percent": [list(rule) for rule in RETENTION_RULES],
        "leave_one_mutant_out": ["none", *[m for values in TARGET_MUTATIONS.values() for m in values]],
        "score_perturbations_percent": [int(v * 100) for v in PERTURBATIONS],
        "string_thresholds_requested": [400, 700, 900],
        "string_threshold_sensitivity_status": string_status,
        "string_matrix_files": string_files,
        "outputs": [
            "results/lightweight_robustness/rrs_threshold_sensitivity.csv",
            "results/lightweight_robustness/rrs_leave_one_mutant_out.csv",
            "results/lightweight_robustness/docking_score_perturbation.csv",
        ],
        "interpretation": "Descriptive robustness of operational docking-RRS rules; not independent validation and not biochemical affinity.",
    }
    (outdir / "lightweight_analysis_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(threshold_df)} threshold rows, {len(loo_df)} leave-one-out rows, and {len(perturb_df)} perturbation rows")
    print(f"STRING threshold sensitivity: {string_status}")


if __name__ == "__main__":
    main()
