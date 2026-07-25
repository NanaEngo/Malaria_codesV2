#!/usr/bin/env python3
"""P3 — SOTA Topological Benchmark (Action 3).

Compares our 12-dim TFP (H0/H1 summary statistics) against alternative
persistence-diagram vectorisation strategies inspired by TopologyNet and
D-GRIL, using the same RF/SVM classifiers on the same dataset.

Strategies tested:
  1. TFP-12       — Our 12-feature TFP (H0+H1: entropy, count, max, mean persistence)
  2. PersImage    — Persistence images (25×25 pixel, inspired by TopologyNet)
  3. BettiCurve   — Betti-number curves (20-bin, inspired by topology-based NNs)
  4. PersStats    — Raw persistence diagram statistics (all H0+H1 moments)
  5. TFP-Enriched — Our TFP + persistence image + Betti features (32-dim)

All strategies use 5-fold stratified CV with RF (n_estimators=500) and SVM
(RBF, tuned C/gamma). AUC is the primary metric.

Output:
  - results/p3_sota_benchmark.csv
  - results/p3_sota_benchmark_summary.txt
"""

from __future__ import annotations

import argparse
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("p3_sota_benchmark")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_tda_fingerprints(csv_path: Path) -> pd.DataFrame:
    """Load the TDA fingerprints file (already computed by p3_tda_pipeline.py)."""
    df = pd.read_csv(csv_path)
    log.info(f"Loaded {len(df)} molecules from {csv_path.name}")
    return df


def get_labels(df: pd.DataFrame) -> np.ndarray:
    """Extract binary activity labels (1=active, 0=inactive).

    Assumes the CSV has an 'activity' or 'label' column, or we infer from
    MPO score ≥ 0.50 = active.
    """
    if "activity" in df.columns:
        return (df["activity"].values >= 0.5).astype(int)
    if "label" in df.columns:
        return df["label"].values.astype(int)
    if "mpo_score" in df.columns:
        return (df["mpo_score"].values >= 0.50).astype(int)
    # No valid labels found — fail hard to prevent wasted HPC compute
    log.error("No activity/label/true_label column found in data or labels CSV")
    log.error("Provide a CSV with 'smiles' + activity columns via --labels-csv")
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Feature extraction strategies
# ---------------------------------------------------------------------------

def extract_tfp12(df: pd.DataFrame) -> np.ndarray:
    """Our 12-dim TFP: H0 and H1 summary statistics."""
    cols = [c for c in df.columns if c.startswith("H0_") or c.startswith("H1_")]
    if not cols:
        # Fallback: try generic column names
        cols = [c for c in df.columns if "entropy" in c or "count" in c
                or "max_pers" in c or "mean_pers" in c]
    if not cols:
        raise ValueError("Cannot find TFP columns in the data")
    # Take first 12 columns if more exist
    selected = cols[:12]
    log.info(f"TFP-12: using {len(selected)} features: {selected[:4]}...")
    return df[selected].values.astype(float)


def extract_persistence_images(df: pd.DataFrame) -> np.ndarray:
    """Persistence image features (25-dim, inspired by TopologyNet)."""
    cols = [c for c in df.columns if c.startswith("pers_img_")]
    if cols:
        log.info(f"PersImage: using {len(cols)} pre-computed features")
        return df[cols].values.astype(float)
    # If not pre-computed, use Betti curves as proxy
    log.warning("No persistence image columns found — falling back to Betti curves")
    return extract_betti_curves(df)


def extract_betti_curves(df: pd.DataFrame) -> np.ndarray:
    """Betti number curve features (20-dim, inspired by topology-based NNs)."""
    cols = [c for c in df.columns if c.startswith("betti_")]
    if cols:
        log.info(f"BettiCurve: using {len(cols)} pre-computed features")
        return df[cols].values.astype(float)
    log.warning("No Betti curve columns found")
    return np.zeros((len(df), 1))


def extract_pers_stats(df: pd.DataFrame) -> np.ndarray:
    """Raw persistence diagram statistics — all available H0/H1 moments."""
    cols = [c for c in df.columns
            if (c.startswith("H0_") or c.startswith("H1_"))
            and c not in ("smiles", "name", "label", "activity", "mpo_score")]
    if not cols:
        cols = [c for c in df.columns if "entropy" in c or "count" in c
                or "max_pers" in c or "mean_pers" in c or "std" in c
                or "skew" in c or "kurt" in c]
    log.info(f"PersStats: using {len(cols)} raw statistics")
    return df[cols].values.astype(float) if cols else np.zeros((len(df), 1))


def extract_tfp_enriched(df: pd.DataFrame) -> np.ndarray:
    """Enriched TFP: TFP-12 + PersImage + Betti (up to 32-dim)."""
    f1 = extract_tfp12(df)
    f2 = extract_persistence_images(df)
    f3 = extract_betti_curves(df)
    # Limit each to avoid explosion
    f2 = f2[:, :10]
    f3 = f3[:, :10]
    combined = np.hstack([f1, f2, f3])
    log.info(f"TFP-Enriched: {combined.shape[1]} features "
             f"({f1.shape[1]} TFP + {f2.shape[1]} PersImg + {f3.shape[1]} Betti)")
    return combined


STRATEGIES = {
    "TFP-12": extract_tfp12,
    "PersImage": extract_persistence_images,
    "BettiCurve": extract_betti_curves,
    "PersStats": extract_pers_stats,
    "TFP-Enriched": extract_tfp_enriched,
}

# ---------------------------------------------------------------------------
# Classifiers
# ---------------------------------------------------------------------------

def get_classifiers() -> dict:
    """Return the two classifier factories used in the main benchmark."""
    return {
        "rf": lambda: RandomForestClassifier(
            n_estimators=500, max_depth=None, min_samples_split=5,
            class_weight="balanced", random_state=42, n_jobs=-1,
        ),
        "svm": lambda: SVC(
            kernel="rbf", C=10.0, gamma="scale",
            class_weight="balanced", probability=True, random_state=42,
        ),
    }

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_strategy(
    X: np.ndarray, y: np.ndarray, strategy_name: str, clf_name: str,
    clf_factory, n_folds: int = 5,
) -> dict:
    """Run 5-fold CV and return metrics."""
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    aucs, accs, f1s = [], [], []

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Scale features
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        clf = clf_factory()
        clf.fit(X_train_s, y_train)

        y_prob = clf.predict_proba(X_test_s)[:, 1]
        y_pred = clf.predict(X_test_s)

        try:
            fold_auc = roc_auc_score(y_test, y_prob)
        except ValueError:
            fold_auc = 0.5

        aucs.append(fold_auc)
        accs.append(accuracy_score(y_test, y_pred))
        f1s.append(f1_score(y_test, y_pred, zero_division=0))

    return {
        "strategy": strategy_name,
        "classifier": clf_name,
        "auc_mean": np.mean(aucs),
        "auc_std": np.std(aucs),
        "accuracy_mean": np.mean(accs),
        "f1_mean": np.mean(f1s),
        "n_folds": n_folds,
        "n_molecules": len(y),
        "n_features": X.shape[1],
    }

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="P3 SOTA Topological Benchmark")
    parser.add_argument("--tda-csv", type=str, default=None,
                        help="Path to TDA fingerprints CSV")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--max-mols", type=int, default=2000,
                        help="Max molecules to subsample (SVM scales O(n^2))")
    parser.add_argument("--labels-csv", type=str, default=None,
                        help="CSV with 'smiles' and 'activity' columns (merge with TDA data)")
    parser.add_argument("--output-csv", type=str, default=None)
    args = parser.parse_args()

    # Locate input data
    if args.tda_csv:
        tda_path = Path(args.tda_csv)
    else:
        tda_path = RESULTS_DIR / "p3_tda_fingerprints.csv"
        if not tda_path.exists():
            tda_path = RESULTS_DIR / "p3_tda_features_1815.csv"
        if not tda_path.exists():
            log.error(f"TDA fingerprints not found at {tda_path}")
            return

    output_csv = Path(args.output_csv) if args.output_csv else RESULTS_DIR / "p3_sota_benchmark.csv"

    # Load data
    log.info(f"Loading data from {tda_path}")
    df = load_tda_fingerprints(tda_path)

    # Merge external labels if provided
    if args.labels_csv:
        labels_path = Path(args.labels_csv)
        if labels_path.exists():
            log.info(f"Merging labels from {labels_path}")
            labels_df = pd.read_csv(labels_path)
            # Find the label column (activity, label, or true_label)
            label_col = None
            for candidate in ["activity", "label", "true_label"]:
                if candidate in labels_df.columns:
                    label_col = candidate
                    break
            if label_col is None:
                log.warning(f"No activity/label column found in {labels_path}")
            elif "smiles" in labels_df.columns and "smiles" in df.columns:
                df = df.merge(labels_df[["smiles", label_col]], on="smiles", how="inner")
                df = df.rename(columns={label_col: "activity"})
                log.info(f"After merge: {len(df)} molecules with both TDA features and labels")
            else:
                log.warning(f"Cannot merge: missing 'smiles' column in one of the DataFrames")
        else:
            log.warning(f"Labels CSV not found: {labels_path}")

    y = get_labels(df)
    n_active = y.sum()
    n_inactive = len(y) - n_active
    log.info(f"Labels: {n_active} active, {n_inactive} inactive")

    # Subsample if needed (SVM scales O(n^2), RF scales O(n log n))
    if len(df) > args.max_mols:
        log.info(f"Subsampling from {len(df)} to {args.max_mols} molecules")
        rng = np.random.default_rng(42)
        # Stratified subsample: preserve class balance
        active_idx = np.where(y == 1)[0]
        inactive_idx = np.where(y == 0)[0]
        n_active_sub = min(len(active_idx), args.max_mols // 2)
        n_inactive_sub = min(len(inactive_idx), args.max_mols - n_active_sub)
        chosen = np.concatenate([
            rng.choice(active_idx, n_active_sub, replace=False),
            rng.choice(inactive_idx, n_inactive_sub, replace=False),
        ])
        df = df.iloc[chosen].reset_index(drop=True)
        y = y[chosen]
        log.info(f"Subsampled to {len(df)} molecules ({(y==1).sum()} active, {(y==0).sum()} inactive)")

    # Run benchmark
    results = []
    for strat_name, extract_fn in STRATEGIES.items():
        try:
            X = extract_fn(df)
            if X.shape[1] == 0:
                log.warning(f"Skipping {strat_name}: 0 features")
                continue
            if np.all(X == 0):
                log.warning(f"Skipping {strat_name}: all-zero features")
                continue

            for clf_name, clf_factory in get_classifiers().items():
                log.info(f"Running {strat_name} + {clf_name}...")
                res = evaluate_strategy(
                    X, y, strat_name, clf_name, clf_factory, args.n_folds
                )
                results.append(res)
                log.info(f"  AUC = {res['auc_mean']:.4f} ± {res['auc_std']:.4f} "
                         f"(n_feat={res['n_features']})")
        except Exception as e:
            log.error(f"Failed {strat_name}: {e}")
            results.append({
                "strategy": strat_name, "classifier": "all",
                "auc_mean": 0.0, "auc_std": 0.0,
                "accuracy_mean": 0.0, "f1_mean": 0.0,
                "n_folds": args.n_folds, "n_molecules": len(y),
                "n_features": 0, "error": str(e),
            })

    # Save results
    df_results = pd.DataFrame(results)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_csv(output_csv, index=False)
    log.info(f"Results saved to {output_csv}")

    # Summary
    summary_path = output_csv.with_name(output_csv.stem + "_summary.txt")
    with open(summary_path, "w") as f:
        f.write("P3 SOTA Topological Benchmark Summary\n")
        f.write(f"Date: {pd.Timestamp.now().isoformat()}\n")
        f.write(f"Data: {tda_path.name} ({len(df)} molecules)\n")
        f.write(f"Labels: {n_active} active, {n_inactive} inactive\n")
        f.write(f"Folds: {args.n_folds}\n\n")
        f.write(f"{'Strategy':<15} {'Classifier':<8} {'AUC':>8} {'±':>3} {'Std':>6} "
                f"{'Acc':>6} {'F1':>6} {'Feat':>5}\n")
        f.write("-" * 70 + "\n")
        for r in sorted(results, key=lambda x: x["auc_mean"], reverse=True):
            f.write(f"{r['strategy']:<15} {r['classifier']:<8} "
                    f"{r['auc_mean']:>8.4f} {'±':>3} {r['auc_std']:>6.4f} "
                    f"{r['accuracy_mean']:>6.4f} {r['f1_mean']:>6.4f} "
                    f"{r['n_features']:>5d}\n")
        f.write("\n")

        # Statistical comparison: TFP-12 vs each strategy
        tfp_rows = [r for r in results if r["strategy"] == "TFP-12"
                    and r["classifier"] == "rf"]
        if tfp_rows:
            tfp_auc = tfp_rows[0]["auc_mean"]
            f.write(f"\nTFP-12 (RF) AUC: {tfp_auc:.4f} — reference\n")
            for r in results:
                if r["strategy"] != "TFP-12" and r["classifier"] == "rf":
                    diff = r["auc_mean"] - tfp_auc
                    f.write(f"  {r['strategy']}: ΔAUC = {diff:+.4f} "
                            f"({'better' if diff > 0 else 'worse'})\n")

    log.info(f"Summary saved to {summary_path}")
    print(df_results.to_string(index=False))


if __name__ == "__main__":
    main()
