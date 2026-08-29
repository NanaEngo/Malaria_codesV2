"""
p3_physical_validation.py
=========================
P3 Strategic Roadmap (85% PA) — Physical validation of quantum-inspired
descriptors against the Tartarus docking oracle.

Implements P3_Strategic_85PA.md Steps 1–4:

  Step 1 — Merge tartarus_output.csv + p3_tne_embeddings.csv +
           p3_tda_fingerprints.csv by SMILES.
  Step 2 — TNE regression: RandomForestRegressor (192-dim TNE) predicts each
           Tartarus docking score (1SYH, 6Y2F, 4LDE); ECFP4 baseline.
           Generates **parity plots** (predicted vs true ΔG).
  Step 3 — REAL quantum kernel (PennyLane IQPEmbedding, 8 qubits) vs tuned
           RBF-SVM on the polypharmacology classification task
           (label = 1 if >= 2 targets bound at ΔG <= -7.0 kcal/mol).
           n = 1000 stratified subsample, 10-fold stratified CV.
           Statistical rigor: Wilcoxon signed-rank + Bonferroni-Holm
           correction, Cliff's delta effect size, 95% bootstrap CIs.
  Step 4 — TDA topology vs binding promiscuity: Spearman ρ + Pearson r +
           bootstrap 95% CI (10,000 resamples) for each H0/H1/H2 feature.

This script REPLACES the classical polynomial surrogate used in the earlier
p3_tartarus_validation.py §3.8.2 with a genuine PennyLane quantum kernel,
fulfilling the strategic plan's `pennylane (QKS)` requirement.

Usage
-----
    # All analyses (recommended)
    python scripts/p3_physical_validation.py

    # Single analysis
    python scripts/p3_physical_validation.py --analysis tne
    python scripts/p3_physical_validation.py --analysis poly
    python scripts/p3_physical_validation.py --analysis tda

    # Adjust QKS polypharm subsample / folds
    python scripts/p3_physical_validation.py --analysis poly --n-poly 1000 --n-folds 10

Outputs (in results/p3_physical_validation/)
    p3_merged_dataset.csv            — merged SMILES + TNE + TDA + docking
    p3_tne_regression.csv            — R², Spearman ρ, Pearson r per target
    p3_tne_parity.png                — parity plot figure (3 targets × 2 desc)
    p3_polypharm_qks.csv             — per-fold AUC for QKS, RBF, Linear
    p3_polypharm_summary.txt         — Wilcoxon + Bonferroni + Cliff's δ
    p3_tda_promiscuity.csv           — Spearman ρ + Pearson r + 95% CI per feature
    p3_tda_promiscuity.png           — bar chart of Spearman ρ
    p3_physical_validation_summary.txt — consolidated summary
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, r2_score
from sklearn.decomposition import PCA

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]                          # Malaria_codesV2/
P3_DIR = Path(__file__).resolve().parents[1]                        # Project3_.../
P3_RESULTS = P3_DIR / "results"
TARTARUS_CSV = ROOT / "Project2_Polypharmacology_MD_ValidationV2607" / "results" / "tartarus_output.csv"
TNE_CSV = P3_RESULTS / "p3_tne_embeddings.csv"
TDA_CSV = P3_RESULTS / "p3_tda_fingerprints.csv"
OUT_DIR = P3_RESULTS / "p3_physical_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Docking score columns (Tartarus: smile, score_1syh, score_6y2f, score_4lde)
DOCKING_COLS = ["score_1syh", "score_6y2f", "score_4lde"]
TARGET_NAMES = {
    "score_1syh": "PfDHFR (1SYH)",
    "score_6y2f": "PfATP4 (6Y2F)",
    "score_4lde": "PfCRT (4LDE)",
}
POLYPHARM_THRESHOLD = -7.0       # kcal/mol — bind threshold
POLYPHARM_MIN_TARGETS = 2        # >= 2 targets bound => promiscuous

N_QUBITS = 8
COLOURS = {
    "tne":   "#1f77b4",
    "ecfp4": "#ff7f0e",
    "qks":   "#2ca02c",
    "rbf":   "#d62728",
    "linear":"#9467bd",
    "tda":   "#8c564b",
}


# ===========================================================================
# Step 1 — Data loading & merge
# ===========================================================================

def load_tartarus() -> pd.DataFrame:
    """Load Tartarus docking scores (19,913 molecules × 3 targets)."""
    print(f"[load] Tartarus: {TARTARUS_CSV}")
    df = pd.read_csv(TARTARUS_CSV)
    df.columns = df.columns.str.strip()
    # The Tartarus CSV uses 'smile' (singular); rename for consistency
    if "smile" in df.columns and "smiles" not in df.columns:
        df = df.rename(columns={"smile": "smiles"})
    df = df.dropna(subset=DOCKING_COLS, how="all")
    # Filter out the 2,836 corrupted entries (docking = 10,000.00)
    for col in DOCKING_COLS:
        df.loc[df[col] > 0, col] = np.nan
    df = df.dropna(subset=DOCKING_COLS, how="all")
    print(f"       {len(df):,} molecules with >=1 valid (negative) docking score.")
    return df


def load_tne() -> pd.DataFrame:
    """Load TNE embeddings (19,836 × 192 dims)."""
    print(f"[load] TNE: {TNE_CSV}")
    # Read once with default header inference, then decide if a header exists.
    peek = pd.read_csv(TNE_CSV)
    first_col = str(peek.columns[0]).lower().strip()
    if len(peek.columns) >= 2 and first_col in ("smiles", "smiles_canon"):
        df = peek.copy()
        # Rename smiles column if it differs in case
        if first_col != "smiles":
            df = df.rename(columns={peek.columns[0]: "smiles"})
    else:
        raw = pd.read_csv(TNE_CSV, header=None)
        smiles_col = raw.iloc[:, 0]
        embed_cols = raw.iloc[:, 1:]
        embed_cols.columns = [f"tne_{i}" for i in range(embed_cols.shape[1])]
        df = pd.concat([smiles_col.rename("smiles"), embed_cols], axis=1)
    df = df.dropna()
    print(f"       {len(df):,} molecules, {len(df.columns) - 1}-dim TNE.")
    return df


def load_tda() -> pd.DataFrame:
    """Load TDA fingerprints (19,849 × 78 features, with header)."""
    print(f"[load] TDA: {TDA_CSV}")
    df = pd.read_csv(TDA_CSV)
    df = df.dropna()
    print(f"       {len(df):,} molecules, {len(df.columns) - 1} TDA features.")
    return df


def merge_datasets(tartarus: pd.DataFrame, tne: pd.DataFrame, tda: pd.DataFrame | None = None) -> pd.DataFrame:
    """Inner-join Tartarus + TNE (+ optional TDA) on canonical SMILES."""
    # Canonicalise SMILES to improve merge hit-rate
    from rdkit import Chem
    def canon(s):
        m = Chem.MolFromSmiles(str(s))
        return Chem.MolToSmiles(m) if m is not None else str(s)
    for d in [tartarus, tne] + ([tda] if tda is not None else []):
        d["smiles_canon"] = d["smiles"].apply(canon)
        # Deduplicate on canonical SMILES to avoid inflated row counts
        d.drop_duplicates(subset="smiles_canon", inplace=True)
    merged = tartarus.merge(tne, on="smiles_canon", how="inner", suffixes=("", "_tne"))
    if tda is not None:
        merged = merged.merge(tda, on="smiles_canon", how="inner", suffixes=("", "_tda"))
    # Drop duplicate SMILES columns (tne's 'smiles' → 'smiles_tne', tda's 'smiles' → 'smiles_tda')
    drop_cols = [c for c in merged.columns if c in ("smiles_tne", "smiles_tda")]
    if drop_cols:
        merged = merged.drop(columns=drop_cols)
    print(f"[merge] {len(merged):,} molecules in merged dataset.")
    out = OUT_DIR / "p3_merged_dataset.csv"
    # Save only key columns to keep file size manageable
    save_cols = ["smiles", "smiles_canon"] + DOCKING_COLS
    merged[save_cols].to_csv(out, index=False)
    print(f"       Saved merged index: {out}")
    return merged


def ecfp4_features(smiles_series: pd.Series, n_bits: int = 2048) -> np.ndarray:
    """Compute ECFP4 (Morgan radius 2) bit vectors."""
    from rdkit import Chem
    from rdkit.Chem import rdFingerprintGenerator
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=n_bits)
    fps = []
    for smi in smiles_series:
        mol = Chem.MolFromSmiles(str(smi))
        if mol is not None:
            arr = np.zeros(n_bits, dtype=np.float32)
            from rdkit.DataStructs import ConvertToNumpyArray
            ConvertToNumpyArray(gen.GetFingerprint(mol), arr)
            fps.append(arr)
        else:
            fps.append(np.zeros(n_bits, dtype=np.float32))
    return np.array(fps, dtype=np.float32)


# ===========================================================================
# Step 2 — TNE regression with parity plots
# ===========================================================================

def analysis_tne_regression(merged: pd.DataFrame) -> pd.DataFrame:
    """TNE (192-dim) RandomForest regression → predict docking ΔG per target.

    Generates parity plots (predicted vs true) for each target × descriptor.
    """
    print("\n" + "=" * 70)
    print("Step 2 — TNE Regression on Docking Scores (with parity plots)")
    print("=" * 70)

    tne_feat_cols = [c for c in merged.columns if c.startswith("tne_")]
    X_tne = merged[tne_feat_cols].values.astype(np.float32)
    X_ecfp4 = ecfp4_features(merged["smiles"])
    smiles = merged["smiles"].values

    records = []
    # Parity plot: 3 targets × 2 descriptors
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))

    for j, score_col in enumerate(DOCKING_COLS):
        target_name = TARGET_NAMES[score_col]
        y_raw = merged[score_col].values.astype(np.float64)
        valid = np.isfinite(y_raw) & (y_raw < 0)
        y = y_raw[valid]
        X_t = X_tne[valid]
        X_e = X_ecfp4[valid]

        print(f"\n  Target: {target_name} | N valid = {valid.sum():,}")

        # TNE regression
        rf_tne = RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42)
        y_pred_tne = cross_val_predict(rf_tne, X_t, y, cv=5)
        r2_tne = r2_score(y, y_pred_tne)
        rho_tne, p_tne = stats.spearmanr(y, y_pred_tne)
        r_tne, _ = stats.pearsonr(y, y_pred_tne)
        print(f"    TNE RF:   R²={r2_tne:.3f}  ρ={rho_tne:.3f}  r={r_tne:.3f}  p={p_tne:.2e}")
        records.append({
            "target": target_name, "descriptor": "TNE (192-dim)",
            "R2": r2_tne, "spearman_rho": rho_tne, "spearman_p": p_tne,
            "pearson_r": r_tne, "N": int(valid.sum()),
        })

        # ECFP4 baseline regression
        rf_e = RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42)
        y_pred_e = cross_val_predict(rf_e, X_e, y, cv=5)
        r2_e = r2_score(y, y_pred_e)
        rho_e, p_e = stats.spearmanr(y, y_pred_e)
        r_e, _ = stats.pearsonr(y, y_pred_e)
        print(f"    ECFP4 RF: R²={r2_e:.3f}  ρ={rho_e:.3f}  r={r_e:.3f}  p={p_e:.2e}")
        records.append({
            "target": target_name, "descriptor": "ECFP4 (2048-bit)",
            "R2": r2_e, "spearman_rho": rho_e, "spearman_p": p_e,
            "pearson_r": r_e, "N": int(valid.sum()),
        })

        # Parity plot — TNE (top row)
        ax = axes[0, j]
        _parity(ax, y, y_pred_tne, "TNE (192-dim)", COLOURS["tne"], target_name, r2_tne, rho_tne)
        # Parity plot — ECFP4 (bottom row)
        ax = axes[1, j]
        _parity(ax, y, y_pred_e, "ECFP4 (2048-bit)", COLOURS["ecfp4"], target_name, r2_e, rho_e)

    fig.suptitle(
        "Step 2 — TNE (15.6× compressed) vs ECFP4: Docking Score Prediction Parity Plots\n"
        "RandomForest 5-fold CV; diagonal = perfect prediction",
        fontsize=13, fontweight="bold", y=1.01,
    )
    plt.tight_layout()
    out_fig = OUT_DIR / "p3_tne_parity.png"
    plt.savefig(out_fig, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"\n  Parity figure saved: {out_fig}")

    out_csv = OUT_DIR / "p3_tne_regression.csv"
    pd.DataFrame(records).to_csv(out_csv, index=False)
    print(f"  Results saved: {out_csv}")
    return pd.DataFrame(records)


def _parity(ax, y_true, y_pred, label, color, title, r2, rho):
    """Draw a parity (predicted vs true) scatter on the given axis."""
    ax.scatter(y_true, y_pred, s=3, alpha=0.25, color=color, edgecolors="none")
    lo = min(y_true.min(), y_pred.min())
    hi = max(y_true.max(), y_pred.max())
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1.0, label="y = x")
    ax.set_xlabel("True docking ΔG (kcal/mol)", fontsize=9)
    ax.set_ylabel("Predicted ΔG (kcal/mol)", fontsize=9)
    ax.set_title(f"{title}\n{label}  |  R²={r2:.3f}, ρ={rho:.3f}", fontsize=10, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3)


# ===========================================================================
# Step 3 — REAL QKS polypharmacology classification
# ===========================================================================

def analysis_polypharm_qks(merged: pd.DataFrame, n_poly: int = 1000, n_folds: int = 10,
                           n_repeats: int = 1, compute_target_alignment: bool = False) -> pd.DataFrame:
    """Real PennyLane IQPEmbedding quantum kernel vs tuned RBF-SVM on the
    polypharmacology binary task (>=2 targets bound at ΔG <= -7.0 kcal/mol).

    Statistical rigor:
      - 10-fold stratified CV (n=1000 stratified subsample preserving natural prevalence)
      - UMAP fitted per-fold on TRAIN ONLY (no data leakage)
      - Wilcoxon signed-rank test (non-parametric)
      - Bonferroni-Holm multiple-comparison correction (3 pairwise)
      - Cliff's delta effect size
      - 95% bootstrap confidence intervals (10,000 resamples)
    """
    print("\n" + "=" * 70)
    print(f"Step 3 — REAL Quantum Kernel (IQPEmbedding) Polypharmacology Benchmark")
    print(f"         n={n_poly}, {n_folds}-fold stratified CV, n_repeats={n_repeats}")
    print("=" * 70)

    # Build label
    score_arr = merged[DOCKING_COLS].values.astype(np.float64)
    # A target is "bound" if score <= -7.0 (NaN → not bound)
    bound = (score_arr <= POLYPHARM_THRESHOLD).astype(int)
    bound[np.isnan(score_arr)] = 0
    n_bound = bound.sum(axis=1)
    y_all = (n_bound >= POLYPHARM_MIN_TARGETS).astype(int)
    prevalence = y_all.mean() * 100
    print(f"  Class=1 prevalence (>=2 targets bound): {y_all.sum():,}/{len(y_all):,} "
          f"({prevalence:.1f}%)")

    # Stratified subsample preserving NATURAL prevalence (not 50/50 balanced)
    # — the SVM already uses class_weight='balanced' to handle imbalance.
    rng = np.random.RandomState(42)
    idx_pos = np.where(y_all == 1)[0]
    idx_neg = np.where(y_all == 0)[0]
    rng.shuffle(idx_pos)
    rng.shuffle(idx_neg)
    # Preserve natural prevalence ratio
    natural_prev = y_all.mean()
    n_pos = min(len(idx_pos), int(round(n_poly * natural_prev)))
    n_neg = min(len(idx_neg), n_poly - n_pos)
    sel = np.concatenate([idx_pos[:n_pos], idx_neg[:n_neg]])
    rng.shuffle(sel)
    y = y_all[sel]
    smiles_sel = merged["smiles"].values[sel]
    print(f"  Stratified subsample (natural prevalence): n={len(y)}, active={y.sum()} "
          f"({100*y.mean():.1f}%) — preserves the ~{prevalence:.1f}% population rate")

    # ECFP4 features computed on the full subsample (no leakage: ECFP4 is
    # deterministic per molecule, not fit on labels)
    X_ecfp = ecfp4_features(pd.Series(smiles_sel))
    print(f"  ECFP4 features: {X_ecfp.shape}")
    # UMAP reduction is done PER-FOLD inside the CV loop (train-only fit) to
    # avoid data leakage — see below.

    # PennyLane quantum kernel machinery (reused from p3_qks_benchmark.py)
    import pennylane as qml
    from pennylane.kernels import kernel_matrix, closest_psd_matrix, target_alignment

    def make_kernel_fn(n_qubits: int, n_repeats: int):
        dev = qml.device("lightning.qubit", wires=n_qubits)

        @qml.qnode(dev)
        def _kernel(x1, x2):
            qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
            qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
            return qml.probs(wires=range(n_qubits))

        def kernel(a, b):
            return float(_kernel(a, b)[0])
        return kernel

    def rbf_matrix(A, B, gamma):
        sq = np.sum((A[:, None] - B[None]) ** 2, axis=-1)
        return np.exp(-gamma * sq)

    def tune_rbf_gamma(X_tr, y_tr, gammas=None, n_inner=3):
        if gammas is None:
            gammas = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 0.1, 0.5, 1.0, 2.0, 5.0]
        best_g, best_auc = gammas[0], -1.0
        skf = StratifiedKFold(n_splits=n_inner, shuffle=True, random_state=42)
        for g in gammas:
            aucs = []
            for itr, ite in skf.split(X_tr, y_tr):
                Ktr = rbf_matrix(X_tr[itr], X_tr[itr], g)
                Kte = rbf_matrix(X_tr[ite], X_tr[itr], g)
                clf = SVC(kernel="precomputed", C=1.0, probability=True)
                clf.fit(Ktr, y_tr[itr])
                proba = clf.predict_proba(Kte)[:, 1]
                if len(np.unique(y_tr[ite])) > 1:
                    aucs.append(roc_auc_score(y_tr[ite], proba))
            mean_auc = np.mean(aucs) if aucs else 0.5
            if mean_auc > best_auc:
                best_auc, best_g = mean_auc, g
        return best_g

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    # Checkpoint file to allow resuming the expensive QKS run
    checkpoint_path = OUT_DIR / f"p3_polypharm_checkpoint_n{n_poly}_f{n_folds}_r{n_repeats}.csv"
    records = []
    if checkpoint_path.exists():
        try:
            records = pd.read_csv(checkpoint_path).to_dict("records")
            print(f"  [checkpoint] Resumed {len(records)} prior fold-records from {checkpoint_path}")
        except Exception:
            records = []
    completed_folds = {r["fold"] for r in records}

    t0 = time.perf_counter()

    for fold, (tr_idx, te_idx) in enumerate(skf.split(X_ecfp, y), start=1):
        if fold in completed_folds:
            print(f"  Fold {fold}/{n_folds} already completed — skipping")
            continue
        t_fold = time.perf_counter()
        X_tr_raw, X_te_raw = X_ecfp[tr_idx], X_ecfp[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]
        print(f"\n  Fold {fold}/{n_folds}  (train={len(y_tr)}, test={len(y_te)}, "
              f"test_pos={y_te.sum()})")

        # --- Per-fold UMAP (fit on TRAIN ONLY — no data leakage) ---
        try:
            from umap import UMAP
            reducer = UMAP(n_components=N_QUBITS, metric="jaccard",
                           random_state=42, n_neighbors=15, min_dist=0.1)
            X_tr_umap = reducer.fit_transform(X_tr_raw)
            X_te_umap = reducer.transform(X_te_raw)
        except ImportError:
            print("    [warn] umap-learn not installed; using PCA fallback")
            _pca = PCA(n_components=N_QUBITS, random_state=42)
            _sc = StandardScaler()
            X_tr_umap = _pca.fit_transform(_sc.fit_transform(X_tr_raw))
            X_te_umap = _pca.transform(_sc.transform(X_te_raw))
        # Scale to [-1, 1] for IQPEmbedding (fit on train, apply to both)
        lo, hi = X_tr_umap.min(axis=0), X_tr_umap.max(axis=0)
        rng_scale = np.where(hi - lo > 0, hi - lo, 1.0)
        X_tr = np.clip(2.0 * (X_tr_umap - lo) / rng_scale - 1.0, -1.0, 1.0).astype(np.float32)
        X_te = np.clip(2.0 * (X_te_umap - lo) / rng_scale - 1.0, -1.0, 1.0).astype(np.float32)

        # --- Quantum kernel ---
        print(f"    [QKS] Building kernel matrix ({len(X_tr)}x{len(X_tr)})...")
        kfn = make_kernel_fn(N_QUBITS, n_repeats)
        t_qk = time.perf_counter()
        K_tr_q = kernel_matrix(X_tr, X_tr, kfn)
        K_tr_q = closest_psd_matrix(K_tr_q)
        K_te_q = kernel_matrix(X_te, X_tr, kfn)
        ta_q = np.nan
        if compute_target_alignment:
            ta_q = float(target_alignment(X_tr, y_tr, kfn))
        clf_q = SVC(kernel="precomputed", C=1.0, probability=True, class_weight="balanced")
        clf_q.fit(K_tr_q, y_tr)
        proba_q = clf_q.predict_proba(K_te_q)[:, 1]
        auc_q = roc_auc_score(y_te, proba_q) if len(np.unique(y_te)) > 1 else np.nan
        qk_time = time.perf_counter() - t_qk
        print(f"    [QKS] AUC={auc_q:.4f}  target_alignment={ta_q:.4f}  ({qk_time:.1f}s)")
        records.append({"fold": fold, "model": "QKS", "auc": auc_q,
                        "target_alignment": ta_q, "time_s": round(qk_time, 1)})

        # --- RBF (gamma-tuned on same [-1,1] features) ---
        best_gamma = tune_rbf_gamma(X_tr, y_tr)
        K_tr_r = rbf_matrix(X_tr, X_tr, best_gamma)
        K_te_r = rbf_matrix(X_te, X_tr, best_gamma)
        def _rbf_fn(a, b, _g=best_gamma):
            return float(rbf_matrix(a.reshape(1, -1), b.reshape(1, -1), _g)[0, 0])
        ta_r = float(target_alignment(X_tr, y_tr, _rbf_fn))
        clf_r = SVC(kernel="precomputed", C=1.0, probability=True, class_weight="balanced")
        clf_r.fit(K_tr_r, y_tr)
        proba_r = clf_r.predict_proba(K_te_r)[:, 1]
        auc_r = roc_auc_score(y_te, proba_r) if len(np.unique(y_te)) > 1 else np.nan
        print(f"    [RBF] AUC={auc_r:.4f}  gamma={best_gamma:.4g}  ta={ta_r:.4f}")
        records.append({"fold": fold, "model": "RBF", "auc": auc_r,
                        "target_alignment": ta_r, "gamma": best_gamma})

        # --- Linear baseline ---
        clf_l = SVC(kernel="linear", C=1.0, probability=True, class_weight="balanced")
        clf_l.fit(X_tr, y_tr)
        proba_l = clf_l.predict_proba(X_te)[:, 1]
        auc_l = roc_auc_score(y_te, proba_l) if len(np.unique(y_te)) > 1 else np.nan
        print(f"    [LIN] AUC={auc_l:.4f}")
        records.append({"fold": fold, "model": "Linear", "auc": auc_l})

        elapsed = time.perf_counter() - t0
        done = fold
        eta = (elapsed / done) * (n_folds - fold) if done > 0 else 0
        print(f"  Fold {fold} done in {time.perf_counter()-t_fold:.1f}s | "
              f"ETA {eta/60:.1f} min")

        del K_tr_q, K_te_q, K_tr_r, K_te_r
        gc.collect()

        # Save checkpoint after each completed fold
        pd.DataFrame(records).to_csv(checkpoint_path, index=False)

    results = pd.DataFrame(records)
    out_csv = OUT_DIR / "p3_polypharm_qks.csv"
    results.to_csv(out_csv, index=False)
    print(f"\n  Per-fold results saved: {out_csv}")

    # Statistical analysis
    _write_polypharm_stats(results, prevalence, n_poly, n_folds, n_repeats, checkpoint_path)
    return results


def _cliffs_delta(x, y):
    """Cliff's delta non-parametric effect size."""
    n = 0
    d = 0
    for xi in x:
        for yi in y:
            n += 1
            if xi > yi:
                d += 1
            elif xi < yi:
                d -= 1
    return d / n if n > 0 else 0.0


def _bootstrap_ci(data, n_boot=10000, ci=0.95, statistic=np.mean, seed=42):
    """Bootstrap confidence interval for a statistic."""
    rng = np.random.RandomState(seed)
    data = np.asarray(data)
    n = len(data)
    boots = [statistic(rng.choice(data, size=n, replace=True)) for _ in range(n_boot)]
    lo = np.percentile(boots, (1 - ci) / 2 * 100)
    hi = np.percentile(boots, (1 + ci) / 2 * 100)
    return lo, hi


def _write_polypharm_stats(results: pd.DataFrame, prevalence: float, n: int,
                           n_folds: int, n_repeats: int, checkpoint_path: Path | None = None):
    """Wilcoxon signed-rank + Bonferroni-Holm + Cliff's delta + bootstrap CI."""
    lines = [
        "P3 Physical Validation — Quantum Kernel Polypharmacology Benchmark",
        "=" * 70,
        f"Generated: {pd.Timestamp.now().isoformat()}",
        f"Task: classify molecules binding >= {POLYPHARM_MIN_TARGETS} targets "
        f"at ΔG <= {POLYPHARM_THRESHOLD} kcal/mol",
        f"Subsample: n={n} (stratified), prevalence={prevalence:.1f}%",
        f"CV: {n_folds}-fold stratified, IQPEmbedding n_repeats={n_repeats}",
        f"Circuit: 8-qubit IQPEmbedding on lightning.qubit",
        "",
    ]
    # Per-model summaries
    for model in ["QKS", "RBF", "Linear"]:
        sub = results[results["model"] == model]["auc"].dropna().values
        if len(sub) == 0:
            continue
        mean = sub.mean()
        std = sub.std(ddof=1) if len(sub) > 1 else 0.0
        lo, hi = _bootstrap_ci(sub)
        lines.append(f"{model:>8s}:  AUC = {mean:.4f} ± {std:.4f}  "
                      f"(95% bootstrap CI [{lo:.4f}, {hi:.4f}], n={len(sub)} folds)")
        if "target_alignment" in results.columns:
            ta = results[results["model"] == model]["target_alignment"].dropna().values
            if len(ta) > 0:
                lines.append(f"          target alignment = {ta.mean():.4f} ± {ta.std():.4f}")
    lines.append("")

    # Pairwise Wilcoxon signed-rank tests — align by fold to keep pairing correct
    pairs = [("QKS", "RBF"), ("QKS", "Linear"), ("RBF", "Linear")]
    raw_pvals = []
    test_desc = []
    pivot = results.pivot_table(index="fold", columns="model", values="auc", aggfunc="first")
    for m1, m2 in pairs:
        pair_df = pivot[[m1, m2]].dropna()
        a1, a2 = pair_df[m1].values, pair_df[m2].values
        n_pair = len(a1)
        if n_pair < 5:
            test_desc.append(f"  {m1} vs {m2}: insufficient paired data (n={n_pair})")
            raw_pvals.append(np.nan)
            continue
        try:
            stat_w, p_raw = stats.wilcoxon(a1, a2)
        except ValueError:
            # All differences zero
            stat_w, p_raw = 0.0, 1.0
        delta = _cliffs_delta(a1, a2)
        diff = a1 - a2
        test_desc.append(
            f"  {m1} vs {m2}: Wilcoxon W={stat_w:.1f}, p_raw={p_raw:.4f}, "
            f"Cliff's δ={delta:+.3f}, mean ΔAUC={diff.mean():+.4f} (n={n_pair})"
        )
        raw_pvals.append(p_raw)

    # Bonferroni-Holm correction (with running max for monotonicity)
    valid = [(p, i) for i, p in enumerate(raw_pvals) if not np.isnan(p)]
    valid.sort()
    m = len(valid)
    corrected = {}
    prev_adj = 0.0
    for rank, (p, idx) in enumerate(valid):
        holm_p = min(p * (m - rank), 1.0)
        holm_p = max(holm_p, prev_adj)  # enforce non-decreasing adjusted p-values
        corrected[idx] = holm_p
        prev_adj = holm_p
    lines.append("Pairwise Wilcoxon signed-rank tests (Bonferroni-Holm corrected):")
    for i, desc in enumerate(test_desc):
        if i in corrected:
            sig = "***" if corrected[i] < 0.001 else "**" if corrected[i] < 0.01 else "*" if corrected[i] < 0.05 else "n.s."
            lines.append(f"{desc}  |  p_Holm={corrected[i]:.4f} ({sig})")
        else:
            lines.append(desc)
    lines.append("")
    lines.append("Significance: * p<0.05, ** p<0.01, *** p<0.001 (Bonferroni-Holm corrected)")

    summary = "\n".join(lines)
    print("\n" + summary)
    out = OUT_DIR / f"p3_polypharm_summary_n{n}_f{n_folds}_r{n_repeats}.txt"
    out.write_text(summary)
    print(f"\n  Summary saved: {out}")
    if checkpoint_path is not None:
        print(f"  Checkpoint file: {checkpoint_path}")


# ===========================================================================
# Step 4 — TDA topology vs binding promiscuity
# ===========================================================================

def analysis_tda_promiscuity(merged: pd.DataFrame) -> pd.DataFrame:
    """Spearman ρ + Pearson r + bootstrap 95% CI for each TDA feature vs
    number of targets bound."""
    print("\n" + "=" * 70)
    print("Step 4 — TDA Topology vs Binding Promiscuity (Spearman ρ + 95% CI)")
    print("=" * 70)

    score_arr = merged[DOCKING_COLS].values.astype(np.float64)
    bound = (score_arr <= POLYPHARM_THRESHOLD).astype(int)
    bound[np.isnan(score_arr)] = 0
    n_bound = bound.sum(axis=1)

    tda_feat_cols = [c for c in merged.columns
                     if any(tag in c for tag in
                            ["H0_", "H1_", "H2_", "entropy", "count", "pers", "betti"])
                     and c not in ["smiles", "smiles_canon"] + DOCKING_COLS]
    print(f"\n  Analysing {len(tda_feat_cols)} TDA features vs #targets bound (N={len(merged):,}):")

    records = []
    for feat in tda_feat_cols:
        vals = merged[feat].values.astype(np.float64)
        mask = np.isfinite(vals) & np.isfinite(n_bound)
        v, nb = vals[mask], n_bound[mask]
        if len(v) < 10 or np.std(v) == 0:
            continue
        rho, p_rho = stats.spearmanr(v, nb)
        r, p_r = stats.pearsonr(v, nb)
        # Bootstrap CI on Spearman rho
        try:
            lo, hi = _bootstrap_ci(list(zip(v, nb)), n_boot=10000,
                                   statistic=lambda d: stats.spearmanr(
                                       np.array([x[0] for x in d]),
                                       np.array([x[1] for x in d]))[0])
        except Exception:
            lo, hi = np.nan, np.nan
        sig = "***" if p_rho < 0.001 else "**" if p_rho < 0.01 else "*" if p_rho < 0.05 else ""
        print(f"    {feat:<25}  ρ={rho:+.4f}  [{lo:+.3f}, {hi:+.3f}]  p={p_rho:.2e} {sig}")
        records.append({
            "tda_feature": feat, "spearman_rho": rho, "spearman_p": p_rho,
            "pearson_r": r, "pearson_p": p_r,
            "ci95_lo": lo, "ci95_hi": hi, "N": int(mask.sum()),
        })

    results = pd.DataFrame(records).sort_values("spearman_rho", key=abs, ascending=False)

    # Bar chart
    fig, ax = plt.subplots(figsize=(11, 5.5))
    bar_colors = [COLOURS["tda"] if r >= 0 else "#e74c3c" for r in results["spearman_rho"]]
    xerr = [results["spearman_rho"] - results["ci95_lo"],
            results["ci95_hi"] - results["spearman_rho"]]
    bars = ax.bar(results["tda_feature"], results["spearman_rho"],
                  yerr=xerr, color=bar_colors, edgecolor="black", linewidth=0.6,
                  capsize=3, error_kw={"linewidth": 0.8, "alpha": 0.7})
    for bar, p in zip(bars, results["spearman_p"]):
        star = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        if star:
            ypos = bar.get_height() + 0.008 if bar.get_height() >= 0 else bar.get_height() - 0.02
            ax.text(bar.get_x() + bar.get_width() / 2, ypos, star,
                    ha="center", va="bottom", fontsize=8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Spearman ρ (TDA feature vs #targets bound)", fontsize=10)
    ax.set_xlabel("TDA Feature", fontsize=10)
    ax.set_title(
        f"Step 4 — Topology vs Polypharmacology\n"
        f"(ΔG ≤ {POLYPHARM_THRESHOLD} kcal/mol, N={len(merged):,}; error bars = 95% bootstrap CI)",
        fontsize=11, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    out_fig = OUT_DIR / "p3_tda_promiscuity.png"
    plt.savefig(out_fig, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"\n  Figure saved: {out_fig}")

    out_csv = OUT_DIR / "p3_tda_promiscuity.csv"
    results.to_csv(out_csv, index=False)
    print(f"  Results saved: {out_csv}")
    return results


# ===========================================================================
# Consolidated summary
# ===========================================================================

def write_consolidated_summary(tne_df=None, poly_df=None, tda_df=None, n_poly=1000):
    lines = [
        "P3 Physical Validation — Consolidated Summary",
        "=" * 70,
        f"Generated: {pd.Timestamp.now().isoformat()}",
        f"Implements: P3_Strategic_85PA.md Steps 1–4",
        "",
    ]
    if tne_df is not None:
        lines += ["Step 2 — TNE Regression on Docking Scores", "-" * 40,
                  tne_df.to_string(index=False), ""]
    if poly_df is not None:
        lines += ["Step 3 — Quantum Kernel Polypharmacology (per-fold AUCs)", "-" * 40,
                  poly_df.to_string(index=False), ""]
        summary_paths = list(OUT_DIR.glob("p3_polypharm_summary_n*.txt"))
        if summary_paths:
            summary_path = max(summary_paths, key=lambda p: p.stat().st_mtime)
            lines += ["", "Statistical analysis:", summary_path.read_text(), ""]
        else:
            lines += ["", "[No polypharm summary found]", ""]
    if tda_df is not None:
        lines += ["Step 4 — TDA Spearman ρ vs #Targets Bound (top 12)", "-" * 40,
                  tda_df.head(12).to_string(index=False), ""]
    out = OUT_DIR / "p3_physical_validation_summary.txt"
    out.write_text("\n".join(lines))
    print(f"\n  Consolidated summary saved: {out}")


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="P3 Physical Validation (P3_Strategic_85PA.md Steps 1–4)")
    parser.add_argument("--analysis", choices=["tne", "poly", "tda", "all"],
                        default="all")
    parser.add_argument("--n-poly", type=int, default=1000,
                        help="Subsample size for QKS polypharm benchmark (default 1000)")
    parser.add_argument("--n-folds", type=int, default=10,
                        help="CV folds for QKS polypharm (default 10)")
    parser.add_argument("--n-repeats", type=int, default=1,
                        help="IQPEmbedding repeats (default 1)")
    args = parser.parse_args()

    print("=" * 70)
    print("P3 Physical Validation — P3_Strategic_85PA.md Implementation")
    print("=" * 70)

    # Step 1 — Load & merge
    tartarus = load_tartarus()
    tne = load_tne()
    tda = load_tda() if args.analysis in ("tda", "all") else None
    merged = merge_datasets(tartarus, tne, tda)

    tne_res = poly_res = tda_res = None
    if args.analysis in ("tne", "all"):
        tne_res = analysis_tne_regression(merged)
    if args.analysis in ("poly", "all"):
        poly_res = analysis_polypharm_qks(
            merged, n_poly=args.n_poly, n_folds=args.n_folds,
            n_repeats=args.n_repeats)
    if args.analysis in ("tda", "all"):
        tda_res = analysis_tda_promiscuity(merged)

    write_consolidated_summary(tne_res, poly_res, tda_res, args.n_poly)
    print("\n✓ Done. Results in:", OUT_DIR)


if __name__ == "__main__":
    main()
