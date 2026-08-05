#!/usr/bin/env python3
"""
P5 — Learning curves: mean val AUC per epoch (from ckpt `curve` key).

Only models trained AFTER the curve-capture change (Aug 4, 2026, v3-c) carry
the `curve` key; older runs are simply absent. Curves are early-stopped at
different epochs, so x-axes are aligned to the longest run and missing epochs
filled with NaN (mean skips NaN).

Usage:
    python scripts/p5_learning_curves.py [--output results/figures/p5_learning_curves.png]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

P5_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = P5_ROOT / "results"


def load_curves() -> dict[str, dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, int]]]:
    """{model: {split: (epochs, mean, std, n_curves)}} across all runs that have curves."""
    out: dict[str, dict[str, list]] = {}
    for ckpt in OUT_DIR.glob("p5_*_ckpt.json"):
        try:
            data = json.load(open(ckpt))
        except Exception:
            continue
        for r in data.get("results", []):
            curve = r.get("curve") or []
            if not curve:
                continue
            key = out.setdefault(r["model"], {}).setdefault(r["split"], [])
            key.append(curve)
    result: dict[str, dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, int]]] = {}
    for model, splits in out.items():
        result[model] = {}
        for split, curves in splits.items():
            curves = np.array([np.asarray(c, dtype=float) for c in curves])
            max_len = max(len(c) for c in curves)
            padded = np.full((len(curves), max_len), np.nan)
            for i, c in enumerate(curves):
                padded[i, : len(c)] = c
            mean = np.nanmean(padded, axis=0)
            std = np.nanstd(padded, axis=0, ddof=1)
            result[model][split] = (np.arange(1, max_len + 1), mean, std, len(curves))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    out = Path(args.output) if args.output else OUT_DIR / "figures" / "p5_learning_curves.png"

    curves = load_curves()
    if not curves:
        print("No curve data yet (only runs after v3-c capture change) — exiting without figure.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, split in zip(axes, ["random", "scaffold"]):
        for model, splits in curves.items():
            if split not in splits:
                continue
            x, mean, std, n = splits[split]
            ax.plot(x, mean, marker=".", label=f"{model} (n={n})")
            ax.fill_between(x, mean - std, mean + std, alpha=0.15)
        ax.set_title(f"{split.title()} split — val AUC per epoch (mean ± 1σ)")
        ax.set_xlabel("epoch")
        ax.set_ylabel("val ROC AUC")
        ax.legend()
        ax.set_ylim(0.4, 1.0)
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {out} ({len(curves)} models with curves)")


if __name__ == "__main__":
    main()