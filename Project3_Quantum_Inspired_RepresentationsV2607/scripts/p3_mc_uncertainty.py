"""
Paper 3 — Quick Win: Monte Carlo Dropout for Prediction Uncertainty.

Implements MC Dropout-style uncertainty quantification for the Random Forest
classifier used in the P3 hybrid benchmark (p3_hybrid_benchmark.py).

For Random Forests, we simulate MC Dropout by:
  1. Training the full RF on training data
  2. At inference, randomly sub-sampling trees (dropout_rate fraction) N times
  3. Computing mean prediction + 95% CI across the N MC samples

This provides pixel-level uncertainty maps for classification:
  - High-confidence predictions: narrow CI near 0 or 1
  - Low-confidence predictions: wide CI straddling 0.5

Outputs:
    results/p3_mc_uncertainty.csv     — per-molecule uncertainty metrics
    results/p3_mc_uncertainty_summary.txt — calibration + coverage summary
    results/p3_mc_uncertainty.png      — calibration curve plot

Usage:
    python scripts/p3_mc_uncertainty.py
    python scripts/p3_mc_uncertainty.py --n-mols 1000 --n-mc-samples 200 --dropout-rate 0.3

Requires:
    pandas, numpy, scikit-learn, rdkit, matplotlib
"""

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import binom
from rdkit import Chem

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
ACT_THRESHOLD = 0.5
N_QUBITS = 8
RF_TREES = 200


# ---------------------------------------------------------------------------
# Data loading — reuse p3_hybrid_benchmark logic
# ---------------------------------------------------------------------------

def load_activity(n_mols: int = 0) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Load activity labels + SMILES."""
    df = pd.read_csv(RESULTS_DIR / "eos80ch_malaria_final_activity.csv")
    df = df[["input", "asexual_blood_stage"]].dropna().rename(
        columns={"input": "smiles", "asexual_blood_stage": "activity"}
    )
    if n_mols:
        df = df.head(n_mols)
    y = (df["activity"].values >= ACT_THRESHOLD).astype(int)
    return df, df["smiles"].tolist(), y


def ecfp4_bulk(smiles_list: list[str]) -> np.ndarray:
    """Compute ECFP4 fingerprints for a list of SMILES.

    Falls back to zero vector on failure (robust for large-scale).
    """
    from rdkit.Chem import rdFingerprintGenerator
    from rdkit.DataStructs import ConvertToNumpyArray
    morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


def load_tfpn_features(smiles_list: list[str]) -> np.ndarray | None:
    """Load precomputed TFP + TNE features, fallback to ECFP4."""
    tfp = None
    tne = None
    tfp_path = RESULTS_DIR / "p3_tda_fingerprints.csv"
    tne_path = RESULTS_DIR / "p3_tne_embeddings.csv"

    if tfp_path.exists():
        df = pd.read_csv(tfp_path)
        feat_cols = [c for c in df.columns if c.startswith("H")]
        df = df.set_index("smiles")
        rows = []
        for smi in smiles_list:
            if smi in df.index:
                rows.append(df.loc[smi, feat_cols].values.astype(np.float32))
            else:
                rows.append(np.zeros(len(feat_cols), dtype=np.float32))
        tfp = np.array(rows)
        col_means = np.nanmean(tfp, axis=0)
        col_means = np.where(np.isfinite(col_means), col_means, 0.0)
        inds = np.where(~np.isfinite(tfp))
        tfp[inds] = np.take(col_means, inds[1])
        print(f"    TFP loaded: {tfp.shape}")

    if tne_path.exists():
        df = pd.read_csv(tne_path)
        feat_cols = [c for c in df.columns if c.startswith("tne_")]
        df = df.set_index("smiles")
        rows = []
        for smi in smiles_list:
            if smi in df.index:
                rows.append(df.loc[smi, feat_cols].values.astype(np.float32))
            else:
                rows.append(np.zeros(len(feat_cols), dtype=np.float32))
        tne = np.array(rows)
        col_means = np.nanmean(tne, axis=0)
        col_means = np.where(np.isfinite(col_means), col_means, 0.0)
        inds = np.where(~np.isfinite(tne))
        tne[inds] = np.take(col_means, inds[1])
        print(f"    TNE loaded: {tne.shape}")

    if tfp is not None and tne is not None:
        return np.hstack([tfp, tne])
    elif tfp is not None:
        return tfp
    elif tne is not None:
        return tne
    return None


# ---------------------------------------------------------------------------
# Bootstrap MC for Random Forest (proper uncertainty)
# ---------------------------------------------------------------------------

def mc_bootstrap_predict(X_tr: np.ndarray, y_tr: np.ndarray,
                         X_te: np.ndarray,
                         n_mc: int = 100,
                         subsample_frac: float = 0.7,
                         n_trees: int = 30,
                         random_state: int = 42) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Bootstrap-based Monte Carlo uncertainty for Random Forest.

    Unlike simple tree sub-sampling (which under-estimates variance), this
    method bootstraps the *training data* for each MC iteration and trains
    a small RF on each bootstrap sample. This yields:
      - Wider, more realistic prediction intervals
      - Proper coverage when used with conformal prediction

    Args:
        X_tr: (n_train, n_features) training data
        y_tr: (n_train,) training labels
        X_te: (n_test, n_features) test data
        n_mc: number of MC bootstrap iterations
        subsample_frac: fraction of training data to sample per MC iteration
        n_trees: trees per bootstrap RF (smaller = faster, more variance)
        random_state: RNG seed

    Returns:
        y_mean: (n_test,) mean predicted probability across MC samples
        y_std:  (n_test,) std of predicted probabilities
        mc_probs: (n_mc, n_test) full MC sample matrix
    """
    from sklearn.ensemble import RandomForestClassifier
    rng = np.random.default_rng(random_state)
    n_train = len(y_tr)
    n_sample = max(10, int(n_train * subsample_frac))

    mc_probs = np.zeros((n_mc, len(X_te)))

    for mc_i in range(n_mc):
        # Bootstrap: sample with replacement from training data
        idx = rng.choice(n_train, size=n_sample, replace=True)
        X_boot, y_boot = X_tr[idx], y_tr[idx]

        # Train small RF on bootstrap sample
        boot_rf = RandomForestClassifier(
            n_estimators=n_trees, n_jobs=1,
            random_state=random_state + mc_i,
            max_depth=10,  # shallow trees = more variance
        )
        boot_rf.fit(X_boot, y_boot)
        mc_probs[mc_i] = boot_rf.predict_proba(X_te)[:, 1]

        if (mc_i + 1) % 25 == 0:
            print(f"    MC sample {mc_i + 1}/{n_mc}")

    y_mean = mc_probs.mean(axis=0)
    y_std = mc_probs.std(axis=0)
    return y_mean, y_std, mc_probs


def conformal_prediction_sets(mc_probs: np.ndarray,
                              y_cal: np.ndarray,
                              y_te: np.ndarray,
                              alpha: float = 0.05,
                              random_state: int = 42) -> dict:
    """Compute conformal prediction coverage for binary classification.

    Uses the MC bootstrap samples to construct conformal prediction sets
    with (1-alpha) marginal coverage guarantee.

    Nonconformity score for binary classification:
        s_i = 1 - predicted_prob_i[true_class]
        = { 1 - p_i  if y_i == 1
          { p_i      if y_i == 0

    Then for a test point with predicted probability p_new:
        Class 0 is included if p_new <= q_hat (the (1-alpha) quantile of scores)
        Class 1 is included if 1-p_new <= q_hat

    Args:
        mc_probs: (n_mc, n_samples) MC probability samples
        y_cal: (n_cal,) calibration set labels
        y_te: (n_test,) test set labels
        alpha: desired miscoverage rate (default 0.05 → 95% coverage)
        random_state: RNG seed

    Returns:
        dict with:
            conformal_coverage: fraction of test points where true label in set
            avg_set_size: average number of classes in prediction set (1-2)
            q_hat: the conformal quantile threshold
            cal_scores: nonconformity scores on calibration set
    """
    rng = np.random.default_rng(random_state)

    # Mean probabilities (across MC samples) for calibration set
    # mc_probs_cal: we need predictions for calibration set too
    # But we only have MC probs for test set...
    # We need to run MC bootstrap on both cal and test
    # This is handled in main() — see below

    # Compute nonconformity scores
    # s_i = 1 - p(y_i | x_i) where p(y_i|x_i) = p_i if y_i=1 else 1-p_i
    n_cal = len(y_cal)
    # cal_probs_from_mc: passed in via mc_probs_cal
    # For now, assume mc_probs contains both cal and test predictions
    # Dimension: (n_mc, n_cal + n_test)
    n_mc = mc_probs.shape[0]
    n_total = mc_probs.shape[1]
    n_test = len(y_te)
    n_cal_actual = n_total - n_test

    cal_probs = mc_probs[:, :n_cal_actual].mean(axis=0)  # mean across MC
    test_probs = mc_probs[:, n_cal_actual:].mean(axis=0)

    # Nonconformity scores on calibration set
    cal_scores = np.where(y_cal == 1, 1.0 - cal_probs, cal_probs)

    # Conformal quantile with finite-sample correction
    n_cal_actual_adj = max(1, n_cal_actual)
    q_level = (1.0 - alpha) * (1.0 + 1.0 / n_cal_actual_adj)
    q_level = min(q_level, 1.0)  # cap at 1.0
    q_hat = np.quantile(cal_scores, q_level, method='higher')

    # Prediction sets on test set
    # Nonconformity score for class 0: s(x,0) = p_new  → include class 0 if p_new <= q_hat
    # Nonconformity score for class 1: s(x,1) = 1-p_new → include class 1 if p_new >= 1 - q_hat
    includes_class0 = test_probs <= q_hat
    includes_class1 = test_probs >= (1.0 - q_hat)

    set_sizes = includes_class0.astype(int) + includes_class1.astype(int)

    # Coverage: fraction where true label is in prediction set
    # True label 0 is covered if includes_class0 is True (p_new <= q_hat)
    # True label 1 is covered if includes_class1 is True (p_new >= 1 - q_hat)
    true_in_set = np.where(y_te == 1, includes_class1, includes_class0)
    conformal_coverage = true_in_set.mean()

    return {
        "conformal_coverage": conformal_coverage,
        "avg_set_size": set_sizes.mean(),
        "q_hat": q_hat,
        "cal_scores": cal_scores,
    }


def calibration_curve(y_true: np.ndarray, y_prob: np.ndarray,
                      n_bins: int = 10) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute calibration curve (reliability diagram).

    Returns:
        bin_centers, bin_accuracies, bin_counts
    """
    bins = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_accuracies = np.zeros(n_bins)
    bin_counts = np.zeros(n_bins, dtype=int)

    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        bin_counts[i] = mask.sum()
        if bin_counts[i] > 0:
            bin_accuracies[i] = y_true[mask].mean()

    return bin_centers, bin_accuracies, bin_counts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MC Dropout Uncertainty for P3 Hybrid Benchmark"
    )
    parser.add_argument("--n-mols", type=int, default=500,
                        help="Number of molecules (default: 500)")
    parser.add_argument("--n-mc-samples", type=int, default=100,
                        help="MC Dropout iterations (default: 100)")
    parser.add_argument("--dropout-rate", type=float, default=0.3,
                        help="Tree dropout fraction (default: 0.3 = keep 70%)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("=" * 60)
    print("P3 — MC Dropout Uncertainty Quantification")
    print(f"  Molecules:      {args.n_mols}")
    print(f"  MC samples:     {args.n_mc_samples}")
    print(f"  Dropout rate:   {args.dropout_rate}")
    print("=" * 60)

    t0 = time.perf_counter()

    # Load data
    print("\n  Loading data...")
    df, smiles, y = load_activity(args.n_mols)
    print(f"  {len(y)} molecules (active={y.sum()}, inactive={(y == 0).sum()})")

    # Load features: try TFP+TNE first, fallback to ECFP4
    print("  Loading features...")
    X_tfpn = load_tfpn_features(smiles)
    if X_tfpn is not None:
        X = X_tfpn
        desc_name = "TFP+TNE"
    else:
        print("  TFP/TNE not found; using ECFP4 fingerprints")
        X = ecfp4_bulk(smiles)
        desc_name = "ECFP4"
    print(f"  Feature matrix: {X.shape}")

    # Train/Cal/Test split (60/20/20) — Calibration set for conformal prediction
    from sklearn.model_selection import train_test_split
    X_tr, X_tmp, y_tr, y_tmp, _, smiles_tmp = train_test_split(
        X, y, smiles, test_size=0.4, random_state=args.seed, stratify=y
    )
    X_cal, X_te, y_cal, y_te, smiles_cal, smiles_te = train_test_split(
        X_tmp, y_tmp, smiles_tmp, test_size=0.5, random_state=args.seed, stratify=y_tmp
    )
    print(f"  Train: {len(y_tr)}  Calibration: {len(y_cal)}  Test: {len(y_te)}")

    # Train full Random Forest on Train+Cal (max data for standard model)
    X_tc = np.vstack([X_tr, X_cal])
    y_tc = np.concatenate([y_tr, y_cal])
    print(f"\n  Training Standard RF (n_estimators={RF_TREES}) on Train+Cal...")
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                 random_state=args.seed)
    clf.fit(X_tc, y_tc)

    # Standard prediction on test set
    y_prob_std = clf.predict_proba(X_te)[:, 1]
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
    auc_std = roc_auc_score(y_te, y_prob_std) if len(np.unique(y_te)) > 1 else np.nan
    print(f"  Standard RF AUC: {auc_std:.4f}")

    # Bootstrap MC — predict on Cal + Test combined (for conformal)
    print(f"\n  Bootstrap MC ({args.n_mc_samples} samples, "
          f"subsample_frac=0.7, n_trees=30)...")
    X_mc = np.vstack([X_cal, X_te])
    t_mc = time.perf_counter()
    y_mean_all, y_std_all, mc_probs = mc_bootstrap_predict(
        X_tr, y_tr, X_mc,
        n_mc=args.n_mc_samples,
        subsample_frac=0.7,
        n_trees=30,
        random_state=args.seed
    )
    mc_time = time.perf_counter() - t_mc
    print(f"  MC done in {mc_time:.1f}s")

    # Split back into Cal and Test
    n_cal = len(y_cal)
    y_mean_cal = y_mean_all[:n_cal]
    y_mean = y_mean_all[n_cal:]
    y_std = y_std_all[n_cal:]
    mc_probs_te = mc_probs[:, n_cal:]

    # Metrics with uncertainty (on Test set)
    auc_mc = roc_auc_score(y_te, y_mean) if len(np.unique(y_te)) > 1 else np.nan
    y_pred = (y_mean >= 0.5).astype(int)
    acc_mc = accuracy_score(y_te, y_pred)
    f1_mc = f1_score(y_te, y_pred, zero_division=0)

    # Conformal Prediction coverage (proper metric for classification)
    cp = conformal_prediction_sets(
        mc_probs, y_cal, y_te,
        alpha=0.05, random_state=args.seed
    )
    conformal_coverage = cp["conformal_coverage"]
    avg_set_size = cp["avg_set_size"]
    q_hat = cp["q_hat"]

    # Quantile-based 95% CI (more robust than 1.96 × std)
    ci_lower = np.percentile(mc_probs_te, 2.5, axis=0)
    ci_upper = np.percentile(mc_probs_te, 97.5, axis=0)

    # Brier score components
    brier = np.mean((y_mean - y_te) ** 2)

    # Average uncertainty
    mean_uncertainty = y_std.mean()
    # Uncertainty-performance correlation
    from scipy.stats import spearmanr
    errors = np.abs(y_mean - y_te)
    rho_uncert, p_uncert = spearmanr(y_std, errors)

    print(f"\n  Bootstrap MC AUC:  {auc_mc:.4f}")
    print(f"  Accuracy:          {acc_mc:.4f}")
    print(f"  F1:                {f1_mc:.4f}")
    print(f"  Mean uncertainty:  {mean_uncertainty:.4f}")
    print(f"  Conformal coverage: {conformal_coverage:.3f} (target 0.95)")
    print(f"  Avg prediction set size: {avg_set_size:.3f}")
    print(f"  Brier score:       {brier:.4f}")
    print(f"  Uncertainty-error ρ: {rho_uncert:.3f} (p={p_uncert:.4f})")

    # Save per-molecule results
    records = []
    for i in range(len(smiles_te)):
        records.append({
            "smiles":        smiles_te[i],
            "true_label":    int(y_te[i]),
            "prob_mean":     round(float(y_mean[i]), 4),
            "prob_std":      round(float(y_std[i]), 4),
            "ci_lower_95":   round(float(max(0, ci_lower[i])), 4),
            "ci_upper_95":   round(float(min(1, ci_upper[i])), 4),
            "predicted":     int(y_pred[i]),
            "correct":       int(y_pred[i] == y_te[i]),
        })

    out_csv = RESULTS_DIR / "p3_mc_uncertainty.csv"
    pd.DataFrame(records).to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # Calibration curve
    print("  Computing calibration curve...")
    bin_centers, bin_accs, bin_counts = calibration_curve(y_te, y_mean, n_bins=10)

    # Plot: calibration curve + uncertainty histogram
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left: Reliability diagram
    ax = axes[0]
    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Perfect calibration")
    ax.plot(bin_centers, bin_accs, "o-", color="#2c7bb6", lw=2, markersize=6,
            label="RF Bootstrap MC")
    # Add bin count annotations
    for c, a, n in zip(bin_centers, bin_accs, bin_counts):
        if n > 0:
            ax.annotate(str(n), (c, a), textcoords="offset points",
                        xytext=(0, 8), fontsize=7, ha="center")
    ax.set_xlabel("Predicted probability", fontsize=11)
    ax.set_ylabel("Observed frequency", fontsize=11)
    ax.set_title("Calibration Curve (Reliability Diagram)", fontsize=11)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(alpha=0.3)

    # Right: Uncertainty distribution
    ax = axes[1]
    ax.hist(y_std, bins=30, color="#d7191c", alpha=0.7, edgecolor="white")
    ax.axvline(mean_uncertainty, color="black", ls="--", lw=1,
               label=f"Mean = {mean_uncertainty:.3f}")
    # Separate correct/incorrect
    records_df = pd.DataFrame(records)
    correct_mask = records_df["correct"].values.astype(bool)
    if correct_mask.sum() > 0 and (~correct_mask).sum() > 0:
        ax.hist(y_std[correct_mask], bins=20, color="#2ca02c", alpha=0.4,
                label="Correct", edgecolor="white")
        ax.hist(y_std[~correct_mask], bins=20, color="#d62728", alpha=0.4,
                label="Incorrect", edgecolor="white")
    ax.set_xlabel("Prediction uncertainty (std)", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Uncertainty Distribution", fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    out_png = RESULTS_DIR / "p3_mc_uncertainty.png"
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"  Saved: {out_png}")
    plt.close()

    # Summary text
    ece = np.mean(np.abs(bin_accs - bin_centers) * (bin_counts / bin_counts.sum()))

    lines = [
        "Bootstrap MC Uncertainty Quantification",
        "=" * 50,
        f"Descriptor:           {desc_name}",
        f"Test molecules:       {len(y_te)}",
        f"MC bootstrap samples: {args.n_mc_samples}",
        f"Subsample fraction:   0.7",
        f"Trees per bootstrap:  30",
        "",
        "Standard RF (Train+Cal):",
        f"  AUC:                {auc_std:.4f}",
        "",
        "Bootstrap MC:",
        f"  AUC:                {auc_mc:.4f}",
        f"  Accuracy:           {acc_mc:.4f}",
        f"  F1:                 {f1_mc:.4f}",
        f"  Brier score:        {brier:.4f}",
        f"  Mean uncertainty:   {mean_uncertainty:.4f}",
        f"  Expected Calibration Error (ECE): {ece:.4f}",
        "",
        "Conformal Prediction (α=0.05):",
        f"  Coverage:           {conformal_coverage:.3f} (target: 0.950)",
        f"  Avg set size:       {avg_set_size:.3f} (1.0 = always singleton, 2.0 = always both)",
        f"  Quantile threshold: {q_hat:.4f}",
        "",
        f"  Uncertainty-error Spearman ρ: {rho_uncert:.3f} (p={p_uncert:.4f})",
        "",
        "Interpretation:",
    ]

    if ece < 0.05:
        lines.append("  ✓ ECE < 0.05 — probabilities are well-calibrated.")
    else:
        lines.append("  △ ECE ≥ 0.05 — consider probability calibration.")

    if conformal_coverage >= 0.90:
        lines.append(f"  ✓ Conformal coverage {conformal_coverage:.1%} ≥ 90% — "
                     f"prediction intervals are reliable.")
    else:
        lines.append(f"  △ Conformal coverage {conformal_coverage:.1%} < 90% — "
                     f"consider more MC samples or larger bootstrap.")

    if avg_set_size < 1.3:
        lines.append("  ✓ Avg set size < 1.3 — predictions are confident "
                      "(most molecules get single-class sets).")
    else:
        lines.append("  △ Avg set size ≥ 1.3 — many predictions are ambiguous "
                      "(both classes plausible).")

    if rho_uncert > 0.2 and p_uncert < 0.05:
        lines.append("  ✓ Significant positive correlation between uncertainty and error "
                      "— uncertainty is informative.")
    else:
        lines.append("  △ Weak or non-significant uncertainty-error correlation.")

    summary = "\n".join(lines)
    print("\n" + summary)
    out_txt = RESULTS_DIR / "p3_mc_uncertainty_summary.txt"
    out_txt.write_text(summary)
    print(f"  Saved: {out_txt}")
    print(f"\n  Total wall time: {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
