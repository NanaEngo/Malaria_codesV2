#!/usr/bin/env python3
"""Paired uncertainty summaries for the P6 scaffold benchmark.

The unit of resampling is the seed--fold replicate. This script reports
paired mean differences and percentile bootstrap intervals. A sign-flip
reference statistic is retained for transparency, but no confirmatory inference
is assigned and the 25 replicates are not treated as independent chemical
observations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "p6_phase2"


def paired_summary(a: np.ndarray, b: np.ndarray, *, seed: int = 20260830, n_boot: int = 20000) -> dict:
    """Summarize paired differences as a-b."""
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    boot = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(axis=1)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_boot, len(d)))
    null = (d * signs).mean(axis=1)
    observed = float(d.mean())
    p = float(np.mean(np.abs(null) >= abs(observed)))
    return {
        "n_seed_fold_pairs": int(len(d)),
        "difference_definition": "arm_a minus arm_b",
        "mean_difference": observed,
        "bootstrap_ci_95": [float(x) for x in np.quantile(boot, [0.025, 0.975])],
        "sign_flip_reference_probability": p,
    }


def load(stem: str) -> pd.DataFrame:
    path = RESULTS / f"{stem}_folds.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    required = {"seed", "fold", "mean_columnwise_log_loss", "macro_auroc", "macro_auprc"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing {sorted(missing)}")
    return df.sort_values(["seed", "fold"]).reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="scaffold", choices=["scaffold", "collision_group"])
    ap.add_argument("--arms", nargs="+", default=["phenotype", "structure", "both"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    frames = {arm: load(f"p6_lish_moa_{arm}_{args.split}") for arm in args.arms}
    keys = [frames[args.arms[0]][["seed", "fold"]]]
    for arm in args.arms[1:]:
        keys.append(frames[arm][["seed", "fold"]])
    for k in keys[1:]:
        if not k.equals(keys[0]):
            raise ValueError("seed/fold identities are not identical across arms")

    comparisons = {}
    for i, a in enumerate(args.arms):
        for b in args.arms[i + 1 :]:
            comparisons[f"{a}_minus_{b}"] = {
                metric: paired_summary(frames[a][metric].to_numpy(), frames[b][metric].to_numpy())
                for metric in ["mean_columnwise_log_loss", "macro_auroc", "macro_auprc"]
            }
    out = {
        "status": "AVAILABLE_PAIRED_SEED_FOLD_VARIABILITY_SUMMARY",
        "split": args.split,
        "arms": args.arms,
        "multiplicity": {"families": 3, "inferential_role": "not assigned", "adjustment": "No confirmatory multiplicity procedure was applied; sign-flip reference statistics are retained for transparency only"},
        "method": "20,000 paired bootstrap resamples over seed-fold differences; seed-fold, not molecule, is the resampling unit. Sign-flip reference statistics are not used for confirmatory inference",
        "comparisons": comparisons,
    }
    path = Path(args.out) if args.out else RESULTS / f"p6_paired_uncertainty_{args.split}.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
