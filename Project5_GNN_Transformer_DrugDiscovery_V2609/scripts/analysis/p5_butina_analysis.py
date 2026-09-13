#!/usr/bin/env python3
"""P5 — Butina scaffold-cluster benchmark analysis.

Compares the three partition families for the 5 P5 arms:

    random  (canonical, Section 3 of the DAR)
    scaffold (canonical greedy Bemis-Murcko split)
    butina  (secondary: Murcko scaffolds Butina-clustered at cutoff 0.55)

Mean ROC-AUC is the mean of per-seed means (5 seeds x 5 folds = 25 records per
arm/partition), identical to how p5_butina_cluster.py aggregates.

Inputs (all tracked / canonical):
  - results/butina_cluster_20260829/training/<ARM>/pred_seed{S}_fold{K}.csv
      (per-fold prediction CSVs, the canonical Butina record)
  - results/p5_*_scaffold_results.csv and p5_*_random_results.csv
      (canonical GNN arms, 25 fold-seed records)
  - results/p5_ecfp4rf_scaffold_baseline.json / p5_ecfp4rf_random_baseline.json
      (canonical ECFP4-RF baselines)

Outputs:
  - results/butina_cluster_20260829/butina_partition_comparison.csv
  - results/butina_cluster_20260829/Table_Butina_Partition_Comparison.tex
  - results/butina_cluster_20260829/butina_partition_comparison.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
BUTINA = ROOT / "results" / "butina_cluster_20260829"
TRAIN_DIR = BUTINA / "training"

ARMS = ["ECFP4-RF", "GIN", "GIN-TFP", "GIN-TNE", "ChemBERTa"]
SEEDS = [0, 1, 2, 3, 4]
N_FOLDS = 5


def _load_butina_arm(arm: str) -> list[dict]:
    """Recompute per-fold metrics from the prediction CSVs (canonical record)."""
    rows = []
    for seed in SEEDS:
        fold_aucs = []
        for fk in range(N_FOLDS):
            p = TRAIN_DIR / arm / f"pred_seed{seed}_fold{fk}.csv"
            if not p.exists():
                return rows  # incomplete arm (e.g. ChemBERTa while running)
            df = pd.read_csv(p)
            y, pr = df["y"].to_numpy(), df["p"].to_numpy()
            auc = roc_auc_score(y, pr)
            ap = average_precision_score(y, pr)
            bal = balanced_accuracy_score(y, (pr > 0.5).astype(int))
            rows.append({"arm": arm, "partition": "butina", "seed": seed,
                         "fold": fk, "test_auc": auc, "test_ap": ap, "bal": bal})
            fold_aucs.append(auc)
    return rows


def _load_canonical(arm: str, partition: str) -> list[dict]:
    """Load canonical GNN fold-seed records from results CSVs."""
    if arm == "ECFP4-RF":
        j = ROOT / "results" / f"p5_ecfp4rf_{partition}_baseline.json"
        if not j.exists():
            return []
        d = json.load(open(j))
        return [{"arm": arm, "partition": partition, "seed": s, "fold": 0,
                 "test_auc": d.get("mean", np.nan), "test_ap": np.nan, "bal": np.nan}
                for s in SEEDS]
    # Canonical result files use mixed-case stems matching the arm label
    # (p5_GIN-TFP_*, p5_chemberta_*).
    stem = "chemberta" if arm == "ChemBERTa" else arm
    f = ROOT / "results" / f"p5_{stem}_{partition}_results.csv"
    if not f.exists():
        return []
    df = pd.read_csv(f)
    out = []
    for _, r in df.iterrows():
        out.append({"arm": arm, "partition": partition,
                    "seed": r.get("seed", np.nan), "fold": r.get("fold", np.nan),
                    "test_auc": r.get("test_auc", np.nan),
                    "test_ap": r.get("test_ap", np.nan),
                    "bal": r.get("test_bacc", np.nan)})
    return out


def mean_auc(rows: list[dict]) -> float | None:
    """Mean of per-seed means (same aggregation as the benchmark)."""
    if not rows:
        return None
    by_seed = {}
    for r in rows:
        if r["test_auc"] != r["test_auc"]:  # NaN
            continue
        by_seed.setdefault(r["seed"], []).append(r["test_auc"])
    if not by_seed:
        return None
    return float(np.mean([np.mean(v) for v in by_seed.values()]))


def main() -> None:
    arms = [a for a in ARMS]
    partitions = ["random", "scaffold", "butina"]
    table = []
    for arm in arms:
        row = {"arm": arm}
        for part in partitions:
            if part == "butina":
                rows = _load_butina_arm(arm)
                status = "RUNNING" if len(rows) < N_FOLDS * len(SEEDS) else "COMPUTED"
            else:
                rows = _load_canonical(arm, part)
                status = "COMPUTED" if rows else "MISSING"
            # Only report a mean when the partition is fully computed: a partial
            # (RUNNING) arm would otherwise silently present a misleading AUC.
            ma = mean_auc(rows) if status == "COMPUTED" else None
            row[part] = ma
            row[f"{part}_status"] = status
        table.append(row)

    df = pd.DataFrame(table)
    df.to_csv(BUTINA / "butina_partition_comparison.csv", index=False)

    # ---- LaTeX table ----
    lines = [
        "\\begin{table}[htbp]",
        "  \\centering",
        "  \\caption{Partition-family comparison (mean ROC-AUC, 5 seeds $\\times$ 5 folds).",
        "  Random and scaffold are the canonical splits (DAR \\S3); Butina is a stricter",
        "  cluster-disjoint split (Murcko scaffolds, Tanimoto cutoff 0.55; DAR \\S6, 29 Aug 2026).}",
        "  \\label{tab:butina-partition}",
        "  \\begin{tabular}{lccc}",
        "    \\toprule",
        "    Arm & Random & Scaffold & Butina \\\\",
        "    \\midrule",
    ]
    for _, r in df.iterrows():
        cells = [r["arm"]]
        for part in partitions:
            v = r[part]
            cells.append(f"{v:.4f}" if v is not None and v == v else "--")
        lines.append("    " + " & ".join(cells) + r" \\")
    lines += ["    \\bottomrule", "  \\end{tabular}", "\\end{table}"]
    (BUTINA / "Table_Butina_Partition_Comparison.tex").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    # ---- Figure ----
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib unavailable; figure skipped")
        return

    labels = [r["arm"] for r in table]
    x = np.arange(len(labels))
    w = 0.25
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, part in enumerate(partitions):
        vals = [r[part] if r[part] is not None and r[part] == r[part] else 0.0 for r in table]
        ax.bar(x + (i - 1) * w, vals, w, label=part.capitalize())
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Mean ROC-AUC (5 seeds × 5 folds)")
    ax.set_ylim(0.70, 0.98)
    ax.axhline(0.5, color="grey", lw=0.8, ls="--")
    ax.legend(title="Partition")
    ax.set_title("P5 arms across partition families (random / scaffold / Butina)")
    fig.tight_layout()
    fig.savefig(BUTINA / "butina_partition_comparison.png", dpi=200)
    print(f"\nFigure: {BUTINA / 'butina_partition_comparison.png'}")


if __name__ == "__main__":
    sys.exit(main())
