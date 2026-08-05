#!/usr/bin/env python3
"""
P5 — Benchmark figure: bipanel random vs scaffold (publication-grade).

Reads p5_*_results.csv (model,fold,seed,test_auc,split) plus the ECFP4-RF
baseline JSONs, and plots mean ± CI bar per split. ECFP4-RF is the bar; P3
hybrid noted. Honest-negative framing: on scaffold, no GNN/fusion clears the
ECFP4 line.

Usage:
    python scripts/p5_figure.py [--output results/figures/p5_auc_benchmark.png]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st

P5_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = P5_ROOT / "results"


def load_model_results() -> dict[str, pd.DataFrame]:
    results = {}
    for csv in OUT_DIR.glob("p5_*_results.csv"):
        name = csv.stem.removeprefix("p5_").removesuffix("_results").removesuffix("_random").removesuffix("_scaffold")
        results[name] = pd.read_csv(csv)
    return results


def baseline(split: str) -> list[float] | None:
    """Return per-seed mean AUCs (n=5) for the ECFP4-RF baseline."""
    p = OUT_DIR / f"p5_ecfp4rf_{split}_baseline.json"
    if p.exists():
        return json.load(open(p))["seed_means"]
    return None


def model_mean(results: dict, model: str, split: str) -> tuple[float, float] | None:
    """Return (mean, 95% CI half-width) across all seeds for model+split."""
    if model not in results:
        return None
    df = results[model]
    if "split" in df.columns:
        df = df[df["split"] == split]
    auc = df["test_auc"].values.astype(float)
    if len(auc) == 0:
        return None
    m = np.mean(auc)
    se = np.std(auc, ddof=1) / np.sqrt(len(auc))
    ci = st.t.interval(0.95, len(auc) - 1, loc=m, scale=se) if len(auc) > 1 else (m, m)
    return m, (ci[1] - m)


def plot_panel(ax, split: str, results: dict, order: list[str], baselines: dict):
    rows = []
    for m in order:
        mm = model_mean(results, m, split)
        if mm:
            rows.append({"model": m, "mean": mm[0], "err": mm[1]})
    # always append ECFP4 baseline first (bar), CI from its seed means
    seeds = np.asarray(baselines[split], dtype=float)
    bm = seeds.mean()
    se = seeds.std(ddof=1) / np.sqrt(len(seeds))
    lo, hi = st.t.interval(0.95, len(seeds) - 1, loc=bm, scale=se)
    rows.append({"model": "ECFP4-RF", "mean": bm, "err": hi - bm})

    df = pd.DataFrame(rows).sort_values("mean", ascending=True)
    y = np.arange(len(df))
    bars = ax.barh(y, df["mean"], xerr=df["err"], height=0.55, capsize=3,
                   color=["#d62728" if m == "ECFP4-RF" else "#1f77b4" for m in df["model"]],
                   alpha=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(df["model"])
    ax.set_xlabel("ROC AUC")
    ax.set_title(f"{split.title()} split (5-fold × 5 seeds)", fontsize=12)
    ax.axvline(df.loc[df.model == "ECFP4-RF", "mean"].iloc[0], color="#d62728", ls="--", lw=1.2, alpha=0.6)
    ax.set_xlim(0.5, 1.0)
    for i, row in df.iterrows():
        ax.text(min(row["mean"] + row["err"] + 0.01, 0.98), row.name,
                f"{row['mean']:.3f}±{row['err']:.3f}", va="center", fontsize=8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    out = Path(args.output) if args.output else OUT_DIR / "figures" / "p5_auc_benchmark.png"

    results = load_model_results()
    order = ["GIN", "GCN", "GAT", "GIN-FP", "GIN-TFP", "GIN-TNE", "Hybrid-All", "ChemBERTa"]
    order = [m for m in order if model_mean(results, m, "scaffold") or model_mean(results, m, "random")]

    baselines = {"random": baseline("random"), "scaffold": baseline("scaffold")}

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    plot_panel(axes[0], "random", results, order, baselines)
    plot_panel(axes[1], "scaffold", results, order, baselines)
    fig.suptitle("P5 antimalarial NP panel (n=19,836) — GNN/Transformer vs ECFP4-RF", fontsize=14)
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    main()