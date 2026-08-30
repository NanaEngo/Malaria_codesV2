#!/usr/bin/env python3
"""Audit and aggregate the completed P5 extended campaign.

This is a post-processing script only. It does not retrain models, alter
canonical results, or infer statistics from incomplete matrices. It validates
all 25 seed-fold records per configuration, summarizes ROC-AUC/AUPRC, computes
paired native-versus-permuted descriptor contrasts on five per-seed means, and
quantifies salience stability from the archived per-run vectors.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN = ROOT / "results" / "extended_campaign_20260825"
TRAINING = CAMPAIGN / "training"
OUT = CAMPAIGN / "robustness"
PARTITIONS = ["canonical_random", "canonical_scaffold", "novel_101", "novel_202", "novel_303"]
CONFIGS = [
    ("GIN", "native"),
    ("GIN-TFP", "native"),
    ("GIN-TFP", "permuted"),
    ("GIN-TNE", "native"),
    ("GIN-TNE", "permuted"),
]
SEEDS = list(range(5))
FOLDS = list(range(5))
EXPECTED = {(s, f) for s in SEEDS for f in FOLDS}


def exact_sign_flip_p(deltas: np.ndarray) -> float:
    """Exact two-sided sign-flip p-value for five paired differences."""
    observed = abs(float(np.mean(deltas)))
    means = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(deltas)):
        means.append(abs(float(np.mean(deltas * np.asarray(signs)))))
    return float(np.mean(np.asarray(means) >= observed - 1e-15))


def read_results(partition: str, model: str, mode: str) -> pd.DataFrame:
    path = TRAINING / partition / f"{model}_{mode}" / "fold_results.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    required = {"seed", "fold", "test_auc", "test_ap", "n_test"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    keys = {(int(s), int(f)) for s, f in zip(df.seed, df.fold)}
    if len(df) != 25 or keys != EXPECTED:
        raise ValueError(f"{path}: expected exactly 25 unique seed-fold records, got {len(df)}")
    for col in ("test_auc", "test_ap"):
        values = df[col].to_numpy(float)
        if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
            raise ValueError(f"{path}: invalid {col}")
    return df.sort_values(["seed", "fold"]).reset_index(drop=True)


def summarize(df: pd.DataFrame, partition: str, model: str, mode: str) -> dict:
    seed_auc = df.groupby("seed")["test_auc"].mean().reindex(SEEDS).to_numpy(float)
    seed_ap = df.groupby("seed")["test_ap"].mean().reindex(SEEDS).to_numpy(float)
    return {
        "partition": partition,
        "model": model,
        "descriptor_mode": mode,
        "status": "COMPUTED",
        "n_records": int(len(df)),
        "auc_mean_fold_seed": float(df.test_auc.mean()),
        "auc_sd_fold_seed": float(df.test_auc.std(ddof=1)),
        "auc_mean_seed": float(seed_auc.mean()),
        "auc_sd_seed": float(seed_auc.std(ddof=1)),
        "ap_mean_fold_seed": float(df.test_ap.mean()),
        "ap_sd_fold_seed": float(df.test_ap.std(ddof=1)),
        "ap_mean_seed": float(seed_ap.mean()),
        "ap_sd_seed": float(seed_ap.std(ddof=1)),
        "seed_means_auc": [float(x) for x in seed_auc],
        "seed_means_ap": [float(x) for x in seed_ap],
    }


def paired_contrast(partition: str, model: str, native: pd.DataFrame, permuted: pd.DataFrame) -> dict:
    a = native.groupby("seed")["test_auc"].mean().reindex(SEEDS).to_numpy(float)
    b = permuted.groupby("seed")["test_auc"].mean().reindex(SEEDS).to_numpy(float)
    d = a - b
    t, p = stats.ttest_rel(a, b)
    return {
        "partition": partition,
        "contrast": f"{model}_native_minus_permuted",
        "unit": "five per-seed means, each averaging five folds",
        "status": "COMPUTED",
        "native_mean_auc": float(a.mean()),
        "permuted_mean_auc": float(b.mean()),
        "mean_delta_auc": float(d.mean()),
        "delta_by_seed": [float(x) for x in d],
        "paired_t_df4": float(t),
        "paired_t_p": float(p),
        "exact_sign_flip_p": exact_sign_flip_p(d),
    }


def spearman_pairwise(values: np.ndarray) -> list[float]:
    out = []
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            out.append(float(stats.spearmanr(values[i], values[j]).statistic))
    return out


def salience_stability(partition: str, model: str, mode: str) -> dict:
    path = TRAINING / partition / f"{model}_{mode}" / "salience_individual.npz"
    if not path.exists():
        return {"partition": partition, "model": model, "descriptor_mode": mode, "status": "NOT_COMPUTED_INPUT_MISSING"}
    z = np.load(path, allow_pickle=False)
    sal = np.asarray(z["salience"], dtype=float)
    seeds = np.asarray(z["seed"], dtype=int)
    folds = np.asarray(z["fold"], dtype=int)
    if sal.shape[0] != 25 or {(int(s), int(f)) for s, f in zip(seeds, folds)} != EXPECTED:
        raise ValueError(f"{path}: salience records are incomplete")
    if not np.isfinite(sal).all() or (sal < 0).any():
        raise ValueError(f"{path}: invalid salience values")
    k = max(1, int(math.ceil(sal.shape[1] * 0.10)))
    top_sets = [set(np.argsort(row)[-k:]) for row in sal]
    jaccard = []
    for i in range(25):
        for j in range(i + 1, 25):
            jaccard.append(len(top_sets[i] & top_sets[j]) / len(top_sets[i] | top_sets[j]))
    rho = spearman_pairwise(sal)
    top_frequency = np.mean(np.asarray([[int(d in s) for d in range(sal.shape[1])] for s in top_sets]), axis=0)
    order = np.argsort(-sal.mean(axis=0))
    result = {
        "partition": partition,
        "model": model,
        "descriptor_mode": mode,
        "status": "COMPUTED",
        "n_runs": 25,
        "n_dimensions": int(sal.shape[1]),
        "top_k": k,
        "top_k_fraction": 0.10,
        "top_k_jaccard_mean": float(np.mean(jaccard)),
        "top_k_jaccard_median": float(np.median(jaccard)),
        "top_k_jaccard_min": float(np.min(jaccard)),
        "top_k_jaccard_max": float(np.max(jaccard)),
        "pairwise_spearman_mean": float(np.mean(rho)),
        "pairwise_spearman_median": float(np.median(rho)),
        "pairwise_spearman_min": float(np.min(rho)),
        "pairwise_spearman_max": float(np.max(rho)),
        "dimension_top_k_frequency_mean": float(np.mean(top_frequency)),
        "dimension_top_k_frequency_max": float(np.max(top_frequency)),
        "top_dimensions_by_mean_salience": [int(x) for x in order[:min(10, len(order))]],
        "mean_salience_sum": float(sal.mean(axis=0).sum()),
    }
    if model == "GIN-TFP":
        blocks = {"homology_0": (0, 33), "persistent_image": (33, 58), "betti": (58, 78)}
    else:
        blocks = {"all_TNE": (0, sal.shape[1])}
    block_mean = sal.mean(axis=0)
    result["block_mean_salience"] = {name: float(block_mean[a:b].mean()) for name, (a, b) in blocks.items() if b <= len(block_mean)}
    return result


def main() -> None:
    global CAMPAIGN, TRAINING, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", type=Path, default=CAMPAIGN)
    args = ap.parse_args()
    CAMPAIGN = args.campaign.resolve()
    TRAINING = CAMPAIGN / "training"
    OUT = CAMPAIGN / "robustness"
    OUT.mkdir(parents=True, exist_ok=True)

    summaries = []
    tables = {}
    for partition in PARTITIONS:
        for model, mode in CONFIGS:
            df = read_results(partition, model, mode)
            summaries.append(summarize(df, partition, model, mode))
            tables[(partition, model, mode)] = df
    pd.DataFrame(summaries).to_csv(OUT / "extended_model_aggregates.csv", index=False)

    contrasts = []
    for partition in PARTITIONS:
        for model in ("GIN-TFP", "GIN-TNE"):
            contrasts.append(paired_contrast(partition, model, tables[(partition, model, "native")], tables[(partition, model, "permuted")]))
    salience = [salience_stability(partition, model, mode) for partition in PARTITIONS for model, mode in CONFIGS if model != "GIN"]
    payload = {
        "status": "COMPUTED",
        "campaign": str(CAMPAIGN),
        "expected_configurations": 25,
        "completed_configurations": len(summaries),
        "expected_records_per_configuration": 25,
        "total_fold_seed_records": int(sum(x["n_records"] for x in summaries)),
        "model_aggregates_csv": str(OUT / "extended_model_aggregates.csv"),
        "paired_ablation_contrasts": contrasts,
        "salience_stability": salience,
        "boundary": "Extended reruns are versioned robustness analyses; canonical manuscript estimates are not silently replaced.",
    }
    (OUT / "extended_analysis_summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
    pd.DataFrame(contrasts).to_csv(OUT / "paired_ablation_contrasts.csv", index=False)
    pd.DataFrame(salience).to_csv(OUT / "salience_stability.csv", index=False)
    print(json.dumps({"status": payload["status"], "configurations": payload["completed_configurations"], "records": payload["total_fold_seed_records"], "contrasts": len(contrasts), "salience_rows": len(salience)}, indent=2))
    for row in contrasts:
        print(f"{row['partition']} {row['contrast']}: delta={row['mean_delta_auc']:.4f}, exact_sign_flip_p={row['exact_sign_flip_p']:.4f}")


if __name__ == "__main__":
    main()
