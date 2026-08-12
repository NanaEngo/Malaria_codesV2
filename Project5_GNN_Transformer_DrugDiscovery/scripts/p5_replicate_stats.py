#!/usr/bin/env python3
"""
P5 — Independent statistical re-derivation (Action 3, replication evidence).

Recomputes, from the published per-fold/per-seed result CSVs ONLY, the exact
statistics reported in the manuscript:

  1. per-seed means  (mean over the 5 folds for each of the 5 seeds)
  2. paired t-test on the 5 per-seed means vs ECFP4-RF baseline seed means (df=4)
  3. Benjamini-Hochberg FDR across the 4 comparisons, applied separately per split
  4. mean +/- SD over the 5 per-seed means (the manuscript dispersion), while also retaining the raw 25 fold-seed SD as `std25`

This is a from-data re-derivation: it reads no manuscript text and writes a
machine-readable appendix table (CSV + JSON) that reviewers can check line by line.

Usage:
    python scripts/p5_replicate_stats.py [--out results/p5_replication_stats.csv]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

P5_ROOT = Path(__file__).resolve().parent.parent
SEEDS = [0, 1, 2, 3, 4]
ARMS = ["GIN", "GIN-TFP", "GIN-TNE", "chemberta"]
DISPLAY = {"chemberta": "ChemBERTa"}


def bh_fdr(pvals: list[float]) -> list[float]:
    """Benjamini-Hochberg FDR adjustment (monotone).

    p_sorted ascending; iterate from the LARGEST p downward, so the rank of
    p[order[i]] is (i + 1): q_(k) = min_{j>=k} p_(j) * m / j.
    """
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    adj = np.ones(n)
    running = 1.0
    for i in range(n - 1, -1, -1):
        rank = i + 1  # rank of p[order[i]] among ascending p-values
        running = min(running, p[order[i]] * n / rank)
        adj[order[i]] = running
    return list(adj)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out_csv = Path(args.out) if args.out else P5_ROOT / "results" / "p5_replication_stats.csv"

    rows = []
    summary = {"generated": "2026-08-08", "method": "paired t on 5 per-seed means, df=4, BH-FDR per split", "arms": {}}
    for split in ["random", "scaffold"]:
        base = json.load(open(P5_ROOT / "results" / f"p5_ecfp4rf_{split}_baseline.json"))
        bsm = np.asarray(base["seed_means"], dtype=float)
        pvals = []
        split_rows = []
        for arm in ARMS:
            df = pd.read_csv(P5_ROOT / "results" / f"p5_{arm}_{split}_results.csv")
            sm = df.groupby("seed")["test_auc"].mean().reindex(SEEDS).values.astype(float)
            allv = df["test_auc"].values.astype(float)
            t, p = stats.ttest_rel(sm, bsm)
            delta = float(np.mean(allv) - np.mean(bsm))
            pvals.append(float(p))
            split_rows.append({
                "split": split, "arm": DISPLAY.get(arm, arm),
                "mean25": round(float(np.mean(allv)), 4),
                "std_seed": round(float(np.std(sm)), 4),
                "std25": round(float(np.std(allv)), 4),
                "seed_means": [round(float(x), 4) for x in sm],
                "delta_vs_ecfp4": round(delta, 4),
                "t_df4": round(float(t), 3),
                "raw_p": float(p),
            })
        adj = bh_fdr(pvals)
        for r, a in zip(split_rows, adj):
            r["bh_adjusted_p"] = float(a)
            rows.append(r)
            summary["arms"][f"{r['arm']}|{split}"] = {
                "mean25": r["mean25"], "std_seed": r["std_seed"], "std25": r["std25"], "delta": r["delta_vs_ecfp4"],
                "t_df4": r["t_df4"], "raw_p": r["raw_p"], "bh_adjusted_p": r["bh_adjusted_p"],
            }

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    out_json = out_csv.with_suffix(".json")
    json.dump(summary, open(out_json, "w"), indent=2)

    print(f"Re-derivation complete: {out_csv} and {out_json}")
    print(f"{'split':8s} {'arm':10s} {'mean25':>8s} {'delta':>7s} {'t(4)':>8s} {'raw_p':>10s} {'BH_p':>8s}")
    for r in rows:
        print(f"{r['split']:8s} {r['arm']:10s} {r['mean25']:8.4f} {r['delta_vs_ecfp4']:7.4f} "
              f"{r['t_df4']:8.3f} {r['raw_p']:10.6f} {r['bh_adjusted_p']:8.4f}")


if __name__ == "__main__":
    main()
