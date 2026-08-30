#!/usr/bin/env python3
"""
P5 — Post-hoc calibration metrics on the archived fold-level predictions.

Post-processing only: reads the 625 pred_*.csv files produced by the extended
campaign (results/extended_campaign_20260825/training/**/pred_seed*_fold*.csv,
schema: index,y,p) plus the 125 ChemBERTa files, and computes per-configuration:

  - Expected Calibration Error (ECE, 10 equal-width bins)
  - Maximum Calibration Error (MCE)
  - Brier score
  - reliability-diagram JSON (bin mean predicted vs bin positive fraction)

Predictions of every test molecule are pooled across the 5 seeds x 5 folds of
each configuration (pooled-calibration estimand, reported as such). No model is
retrained; canonical results are never overwritten.

Outputs: results/calibration_20260827/{calibration_summary.csv, summary.json,
reliability_<config>.json}

Usage (conda env malaria_md):
    python scripts/p5_calibration_posthoc.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

P5_ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN = P5_ROOT / "results" / "extended_campaign_20260825"
OUT = P5_ROOT / "results" / "calibration_20260827"
N_BINS = 10


def ece_mce_brier(p: np.ndarray, y: np.ndarray) -> dict:
    """ECE/MCE with N_BINS equal-width bins; Brier = mean((p-y)^2)."""
    p = np.asarray(p, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    brier = float(np.mean((p - y) ** 2))

    edges = np.linspace(0.0, 1.0, N_BINS + 1)
    bin_ids = np.clip(np.digitize(p, edges[1:-1]), 0, N_BINS - 1)
    ece, mce, rel_rows = 0.0, 0.0, []
    for b in range(N_BINS):
        mask = bin_ids == b
        n = int(mask.sum())
        if n == 0:
            continue
        conf = float(p[mask].mean())
        acc = float(y[mask].mean())
        frac = n / len(p)
        ece += frac * abs(acc - conf)
        mce = max(mce, abs(acc - conf))
        rel_rows.append({"bin": b, "n": n, "frac": frac,
                         "mean_pred": conf, "pos_frac": acc})
    return {"ece": ece, "mce": mce, "brier": brier, "bins": rel_rows,
            "n": int(len(p))}


def collect_config(dirpath: Path) -> tuple[np.ndarray, np.ndarray]:
    """Pool (y, p) over all pred_*.csv in a configuration directory."""
    files = sorted(dirpath.glob("pred_*.csv"))
    ys, ps = [], []
    for f in files:
        df = pd.read_csv(f)
        ys.append(df["y"].to_numpy(dtype=np.float64))
        ps.append(df["p"].to_numpy(dtype=np.float64))
    if not ys:
        return np.array([]), np.array([])
    return np.concatenate(ys), np.concatenate(ps)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, summaries = [], []

    # 1) GNN-family configurations under training/ (25 x 25 records)
    for cfg_dir in sorted(p for p in CAMPAIGN.glob("training/*/*") if p.is_dir()):
        parts = cfg_dir.relative_to(CAMPAIGN / "training").parts
        partition, model = parts[0], parts[1]
        if not list(cfg_dir.glob("pred_*.csv")):
            continue
        y, p = collect_config(cfg_dir)
        if len(y) == 0:
            continue
        metrics = ece_mce_brier(p, y)
        metrics.update({"partition": partition, "model": model,
                        "source": "training"})
        rows.append(metrics)
        with open(OUT / f"reliability_{partition}_{model}.json", "w") as f:
            json.dump({k: v for k, v in metrics.items() if k != "bins"},
                      f, indent=2)
        print(f"[OK] {partition}/{model}: ECE={metrics['ece']:.4f} "
              f"MCE={metrics['mce']:.4f} Brier={metrics['brier']:.5f} "
              f"n={metrics['n']}")

    # 2) ChemBERTa configurations (5 partitions)
    for part_dir in sorted(p for p in (CAMPAIGN / "chemberta").iterdir() if p.is_dir()):
        partition = part_dir.name
        y, p = collect_config(part_dir)
        if len(y) == 0:
            continue
        metrics = ece_mce_brier(p, y)
        metrics.update({"partition": partition, "model": "ChemBERTa",
                        "source": "chemberta"})
        rows.append(metrics)
        with open(OUT / f"reliability_{partition}_ChemBERTa.json", "w") as f:
            json.dump({k: v for k, v in metrics.items() if k != "bins"},
                      f, indent=2)
        print(f"[OK] chemberta/{partition}: ECE={metrics['ece']:.4f} "
              f"MCE={metrics['mce']:.4f} Brier={metrics['brier']:.5f} "
              f"n={metrics['n']}")

    if not rows:
        print("No prediction files found; nothing computed.", file=sys.stderr)
        return 1

    df = pd.DataFrame(rows)
    # drop the per-bin tables from the CSV; keep a compact summary
    df_out = df.drop(columns=["bins"], errors="ignore")
    df_out.to_csv(OUT / "calibration_summary.csv", index=False)
    with open(OUT / "summary.json", "w") as f:
        json.dump({"n_configs": len(df_out), "n_bins": N_BINS,
                   "pooled_estimand": "test predictions pooled over 5 seeds x 5 folds "
                                     "per configuration",
                   "configs": df_out.to_dict(orient="records")}, f, indent=2)

    print(f"\nDONE: {len(df_out)} configurations; summary -> "
          f"{OUT / 'calibration_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
