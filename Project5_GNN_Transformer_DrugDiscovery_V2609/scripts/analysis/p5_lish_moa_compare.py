#!/usr/bin/env python3
"""Compare the two LISH-MoA phenotype benchmark conditions (with vs without controls).

Reproduces the audit table used in P5_DATA_ANALYSIS_REPORT.md and
results/lish_moa/README.md from the report JSONs and fold CSVs produced by
SLURM job 15273 (12 August 2026). Exits non-zero if any audit gate fails.

Audit gates:
  - exactly 25 folds per condition (5 seeds x 5 folds)
  - zero NaN/inf cells in every fold CSV
  - report JSON parseable and consistent with the fold CSV (mean over folds)
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results" / "lish_moa"

REPORTS = {
    "with_controls": RES / "p5_lish_moa_phenotype_drug_grouped_report.json",
    "no_controls": RES / "p5_lish_moa_phenotype_drug_grouped_no_controls_report.json",
}
FOLDS = {
    "with_controls": RES / "p5_lish_moa_phenotype_drug_grouped_folds.csv",
    "no_controls": RES / "p5_lish_moa_phenotype_drug_grouped_no_controls_folds.csv",
}
METRICS = ["mean_columnwise_log_loss", "macro_auprc", "macro_auroc", "mean_brier", "mean_ece"]
N_FOLDS = 25


def main() -> None:
    rows = []
    for cond in ("with_controls", "no_controls"):
        rep = json.loads(REPORTS[cond].read_text())
        df = pd.read_csv(FOLDS[cond])
        assert len(df) == N_FOLDS, f"{cond}: expected {N_FOLDS} folds, got {len(df)}"
        assert df.isna().sum().sum() == 0, f"{cond}: NaN cells present"
        assert (df == float("inf")).sum().sum() == 0, f"{cond}: inf cells present"
        # report mean must equal the fold mean for the primary metric
        fold_mean = df[METRICS[0]].mean()
        rep_mean = rep["mean_metrics"][METRICS[0]]
        assert abs(fold_mean - rep_mean) < 1e-9, f"{cond}: report/fold mismatch"
        row = {
            "condition": cond,
            "n_drugs": rep["n_drugs"],
            "n_labels": rep["n_labels"],
            "folds": len(df),
            "nan_cells": int(df.isna().sum().sum()),
        }
        for m in METRICS:
            row[m] = round(rep["mean_metrics"][m], 5)
            row[f"{m}_min"] = round(df[m].min(), 5)
            row[f"{m}_max"] = round(df[m].max(), 5)
        row["auroc_seed_range"] = (
            f"{df.groupby('seed')['macro_auroc'].mean().min():.4f}-"
            f"{df.groupby('seed')['macro_auroc'].mean().max():.4f}"
        )
        rows.append(row)

    delta = {"condition": "delta (no_controls - with_controls)", "n_drugs": rows[1]["n_drugs"] - rows[0]["n_drugs"]}
    for m in METRICS:
        delta[m] = round(rows[1][m] - rows[0][m], 5)
    rows.append(delta)

    out = RES / "p5_lish_moa_conditions_comparison.json"
    out.write_text(json.dumps({"rows": rows}, indent=2) + "\n")

    print(pd.DataFrame(rows).to_string(index=False))
    print("saved:", out)
    print("AUDIT_PASS")


if __name__ == "__main__":
    main()
