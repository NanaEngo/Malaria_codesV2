#!/usr/bin/env python3
"""Regenerate Figure 2 (exploratory cross-metric relationships) with
Spearman rho, p, and n annotated in each panel (reviewer R2m.6).

Source: results/derived/v7_integrated_candidate_metrics.csv (canonical)
        merged with the revised RRS (corrected PfCRT channel) from
        results/pfcrt_redock_v2grid_20260909/revised_rrs_and_nfav.csv.
Output: submission_ACS_P1V8/Graphics/p1_v7_exploratory_metric_relationships.pdf
        (and .png for reference).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results/derived/v7_integrated_candidate_metrics.csv"
OUT = ROOT / "submission_ACS_P1V8" / "Graphics"

CLASS_COLORS = {"A*": "#047857", "A": "#0f766e", "B": "#2563eb", "C": "#d97706", "D": "#dc2626"}


def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.7)
    ax.set_axisbelow(True)


REV = ROOT / "results/pfcrt_redock_v2grid_20260909/revised_rrs_and_nfav.csv"


def main() -> None:
    df = pd.read_csv(CSV)
    assert len(df) == 17, f"expected 17 candidates, got {len(df)}"
    rev = pd.read_csv(REV)[["candidate", "RRS_mean", "RRS_class"]]
    df = df.drop(columns=["RRS_mean", "RRS_class"]).merge(
        rev.rename(columns={"candidate": "candidate_id"}), on="candidate_id", validate="one_to_one")
    assert df["RRS_mean"].notna().all()
    n = len(df)

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.5))
    pairs = [("PNS", "PNS (network descriptor)", "PNS versus RRS"),
             ("ACSI", "ACSI (chemical-space descriptor)", "ACSI versus RRS")]
    for ax, (xcol, xlabel, title) in zip(axes, pairs):
        for klass, g in df.groupby("RRS_class", sort=False):
            ax.scatter(g[xcol], g["RRS_mean"], s=52, color=CLASS_COLORS.get(klass, "#6b7280"),
                       edgecolor="white", linewidth=0.7, label=klass, alpha=0.9)
        for _, r in df.iterrows():
            ax.annotate(r["candidate_id"], (r[xcol], r["RRS_mean"]), xytext=(3, 3),
                        textcoords="offset points", fontsize=6, color="#374151")
        rho, p = stats.spearmanr(df[xcol], df["RRS_mean"])
        ax.text(0.03, 0.97, f"$\\rho$ = {rho:.3f}\n$p$ = {p:.3f}\n$n$ = {n}",
                transform=ax.transAxes, va="top", ha="left", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cbd5e1", alpha=0.9))
        ax.set_xlabel(xlabel)
        ax.set_ylabel("RRS mean (% score magnitude)")
        ax.set_title(title, loc="left", fontweight="bold")
        clean_axes(ax)
    axes[1].legend(title="RRS class", frameon=False, ncol=2, fontsize=8)
    fig.suptitle("Exploratory cross-metric relationships", fontsize=15, fontweight="bold", y=1.02)
    fig.text(0.5, -0.01,
             "Associations are descriptive and do not establish biological activity, causality, or resistance protection.",
             ha="center", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"p1_v7_exploratory_metric_relationships.{ext}",
                    bbox_inches="tight", dpi=300, facecolor="white")
    print(f"Figure regenerated with rho/p/n -> {OUT}")
    print(f"  PNS-RRS: rho={stats.spearmanr(df['PNS'], df['RRS_mean'])[0]:.4f} "
          f"p={stats.spearmanr(df['PNS'], df['RRS_mean'])[1]:.4f}")
    print(f"  ACSI-RRS: rho={stats.spearmanr(df['ACSI'], df['RRS_mean'])[0]:.4f} "
          f"p={stats.spearmanr(df['ACSI'], df['RRS_mean'])[1]:.4f}")


if __name__ == "__main__":
    main()