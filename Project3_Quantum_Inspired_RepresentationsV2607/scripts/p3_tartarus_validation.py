"""
p3_tartarus_validation.py
=========================
Cross-validation of P3 quantum-inspired descriptors (TNE, TDA, QKS) against
the full Tartarus docking oracle (19,913 × 3 targets).

Three analyses (BMAD_Q1_DATA_ANALYSIS_REPORT.md §3.8):
  §3.8.1 — TNE compression preserves pharmacophoric information
             RF regressor (TNE 192-dim) vs ECFP4 baseline → predict docking scores
  §3.8.2 — QKS on realistic polypharmacology classification task
             QK vs RBF-SVM: label=1 if ≥2 targets at ΔG ≤ −7.0 kcal/mol
  §3.8.3 — TDA topology predicts binding promiscuity (Spearman ρ)
             H0/H1/H2 features vs number of targets bound

Usage:
    # All three analyses (recommended)
    python p3_tartarus_validation.py

    # Single analysis
    python p3_tartarus_validation.py --analysis tne
    python p3_tartarus_validation.py --analysis poly
    python p3_tartarus_validation.py --analysis tda

Outputs (in results/):
    p3_tartarus_tne_regression.csv      — R², Spearman ρ per target per descriptor
    p3_tartarus_poly_classification.csv — AUC, precision, recall per method
    p3_tartarus_tda_spearman.csv        — TDA feature × Spearman ρ vs #targets
    p3_tartarus_summary.txt             — Human-readable summary
    p3_tartarus_tne_regression.png      — Figure for manuscript §3.8.1
    p3_tartarus_tda_promiscuity.png     — Figure for manuscript §3.8.3
"""

import argparse
import sys
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, r2_score
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]   # Malaria_codesV2/
P3_RESULTS = Path(__file__).resolve().parents[1] / "results"
TARTARUS_CSV = ROOT / "Project2_Polypharmacology_MD_ValidationV2607" / "results" / "tartarus_output.csv"
TNE_CSV      = P3_RESULTS / "p3_tne_embeddings.csv"
TDA_CSV      = P3_RESULTS / "p3_tda_fingerprints.csv"
OUTPUT_DIR   = P3_RESULTS

# Docking score columns
DOCKING_COLS  = ["score_1syh", "score_6y2f", "score_4lde"]
TARGET_NAMES  = {
    "score_1syh": "PfDHFR (1SYH)",
    "score_6y2f": "PfATP4 (6Y2F)",
    "score_4lde": "PfCRT (4LDE)",
}
POLYPHARM_THRESHOLD    = -7.0   # kcal/mol
POLYPHARM_MIN_TARGETS  = 2      # ≥2 targets must be bound

# Colour palette (colourblind-safe)
COLORS = {
    "tne":   "#1f77b4",
    "ecfp4": "#ff7f0e",
    "qks":   "#2ca02c",
    "rbf":   "#d62728",
    "tda":   "#9467bd",
}


# ─────────────────────────────────────────────
# Data loading helpers
# ─────────────────────────────────────────────

def load_tartarus() -> pd.DataFrame:
    print(f"[load] Tartarus: {TARTARUS_CSV}")
    df = pd.read_csv(TARTARUS_CSV)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=DOCKING_COLS, how="all")
    print(f"       {len(df):,} molecules with at least one valid docking score.")
    return df


def load_tne() -> pd.DataFrame:
    print(f"[load] TNE: {TNE_CSV}")
    raw = pd.read_csv(TNE_CSV, header=None)
    smiles_col  = raw.iloc[:, 0]
    embed_cols  = raw.iloc[:, 1:]
    embed_cols.columns = [f"tne_{i}" for i in range(embed_cols.shape[1])]
    df = pd.concat([smiles_col.rename("smiles"), embed_cols], axis=1)
    df = df.dropna()
    print(f"       {len(df):,} molecules, {embed_cols.shape[1]}-dim TNE.")
    return df


def load_tda() -> pd.DataFrame:
    print(f"[load] TDA: {TDA_CSV}")
    df = pd.read_csv(TDA_CSV)
    df = df.dropna()
    print(f"       {len(df):,} molecules, {len(df.columns)-1} TDA features.")
    return df


def merge_with_tartarus(descriptor_df: pd.DataFrame, tartarus_df: pd.DataFrame,
                        smiles_col_desc: str = "smiles",
                        smiles_col_tart: str = "smile") -> pd.DataFrame:
    merged = descriptor_df.merge(tartarus_df, left_on=smiles_col_desc,
                                 right_on=smiles_col_tart, how="inner")
    print(f"       Merged: {len(merged):,} molecules.")
    return merged


def ecfp4_features(smiles_series: pd.Series, n_bits: int = 2048):
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        fps = []
        for smi in smiles_series:
            mol = Chem.MolFromSmiles(str(smi))
            if mol is not None:
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=n_bits)
                fps.append(list(fp))
            else:
                fps.append([0] * n_bits)
        return np.array(fps, dtype=np.float32)
    except ImportError:
        print("[warn] RDKit not available — ECFP4 baseline skipped.")
        return None


# ─────────────────────────────────────────────
# §3.8.1 — TNE → RF regression on docking scores
# ─────────────────────────────────────────────

def analysis_tne_regression():
    print("\n" + "=" * 60)
    print("§3.8.1 — TNE Compression vs Docking Scores (RF Regression)")
    print("=" * 60)

    tartarus = load_tartarus()
    tne_df   = load_tne()
    merged   = merge_with_tartarus(tne_df, tartarus)

    tne_feat_cols = [c for c in merged.columns if c.startswith("tne_")]
    X_tne = merged[tne_feat_cols].values.astype(np.float32)
    X_ecfp4 = ecfp4_features(merged["smiles"])
    has_ecfp4 = X_ecfp4 is not None

    records = []
    fig, axes = plt.subplots(1, len(DOCKING_COLS), figsize=(15, 4))

    for ax, score_col in zip(axes, DOCKING_COLS):
        target_name = TARGET_NAMES[score_col]
        y_raw  = merged[score_col].values.astype(np.float64)
        valid  = np.isfinite(y_raw) & (y_raw < 0)
        y      = y_raw[valid]
        X_t    = X_tne[valid]

        print(f"\n  Target: {target_name} | N valid = {valid.sum():,}")

        rf_tne    = RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42)
        y_pred    = cross_val_predict(rf_tne, X_t, y, cv=5)
        r2_tne    = r2_score(y, y_pred)
        rho_tne, p_tne = stats.spearmanr(y, y_pred)
        print(f"    TNE RF:   R²={r2_tne:.3f}  ρ={rho_tne:.3f}  p={p_tne:.2e}")
        records.append({"target": target_name, "descriptor": "TNE (192-dim)",
                        "R2": r2_tne, "spearman_rho": rho_tne, "spearman_p": p_tne,
                        "N": valid.sum()})

        r2_ecfp4 = rho_ecfp4 = p_ecfp4 = np.nan
        if has_ecfp4:
            X_e = X_ecfp4[valid]
            rf_e = RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42)
            y_pred_e = cross_val_predict(rf_e, X_e, y, cv=5)
            r2_ecfp4 = r2_score(y, y_pred_e)
            rho_ecfp4, p_ecfp4 = stats.spearmanr(y, y_pred_e)
            print(f"    ECFP4 RF: R²={r2_ecfp4:.3f}  ρ={rho_ecfp4:.3f}  p={p_ecfp4:.2e}")
            records.append({"target": target_name, "descriptor": "ECFP4 (2048-bit)",
                            "R2": r2_ecfp4, "spearman_rho": rho_ecfp4,
                            "spearman_p": p_ecfp4, "N": valid.sum()})

        vals_plot  = [r2_tne, r2_ecfp4 if has_ecfp4 else 0.0]
        labels     = ["TNE\n(192-dim)", "ECFP4\n(2048-bit)"]
        clrs       = [COLORS["tne"], COLORS["ecfp4"]]
        bars       = ax.bar(labels, vals_plot, color=clrs, width=0.5, edgecolor="black")
        ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
        ax.set_title(target_name, fontsize=11, fontweight="bold")
        ax.set_ylabel("R² (5-fold CV)", fontsize=9)
        ax.set_ylim(-0.05, 1.0)
        for bar, val in zip(bars, vals_plot):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    max(0, val) + 0.01, f"{val:.3f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.suptitle("§3.8.1 — TNE (15.6× Compressed) vs ECFP4 for Docking Score Prediction",
                 fontsize=12, fontweight="bold", y=1.01)
    plt.tight_layout()
    out_fig = OUTPUT_DIR / "p3_tartarus_tne_regression.png"
    plt.savefig(out_fig, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Figure saved: {out_fig}")

    out_csv = OUTPUT_DIR / "p3_tartarus_tne_regression.csv"
    pd.DataFrame(records).to_csv(out_csv, index=False)
    print(f"  Results saved: {out_csv}")
    return pd.DataFrame(records)


# ─────────────────────────────────────────────
# §3.8.2 — QKS on polypharmacology classification
# ─────────────────────────────────────────────

def analysis_polypharmacology_classification():
    print("\n" + "=" * 60)
    print("§3.8.2 — QKS vs RBF-SVM: Polypharmacology Detection")
    print("=" * 60)

    tartarus = load_tartarus()
    tne_df   = load_tne()
    merged   = merge_with_tartarus(tne_df, tartarus)

    score_arr = merged[DOCKING_COLS].values.astype(np.float64)
    n_bound   = (score_arr <= POLYPHARM_THRESHOLD).sum(axis=1)
    y         = (n_bound >= POLYPHARM_MIN_TARGETS).astype(int)
    prevalence = y.mean() * 100
    print(f"  Class=1 prevalence: {y.sum():,}/{len(y):,} ({prevalence:.1f}%)")

    tne_feat_cols = [c for c in merged.columns if c.startswith("tne_")]
    X_tne = merged[tne_feat_cols].values.astype(np.float32)
    cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    records = []

    # RBF-SVM
    pipe_rbf = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", SVC(kernel="rbf", probability=True, random_state=42,
                    class_weight="balanced")),
    ])
    aucs_rbf = cross_val_score(pipe_rbf, X_tne, y, cv=cv, scoring="roc_auc")
    print(f"  RBF-SVM (5CV AUC): {aucs_rbf.mean():.3f} ± {aucs_rbf.std():.3f}")
    records.append({"method": "RBF-SVM", "mean_AUC": aucs_rbf.mean(),
                    "std_AUC": aucs_rbf.std(), "N": len(y),
                    "prevalence_pct": prevalence})

    # Quantum kernel approximation (polynomial on PCA-8D)
    X_pca = PCA(n_components=8, random_state=42).fit_transform(X_tne)
    pipe_qk = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", SVC(kernel="poly", degree=2, coef0=1, probability=True,
                    random_state=42, class_weight="balanced")),
    ])
    aucs_qk = cross_val_score(pipe_qk, X_pca, y, cv=cv, scoring="roc_auc")
    print(f"  Quantum Kernel approx (5CV AUC): {aucs_qk.mean():.3f} ± {aucs_qk.std():.3f}")
    records.append({"method": "Quantum Kernel (PCA-8D + poly)", "mean_AUC": aucs_qk.mean(),
                    "std_AUC": aucs_qk.std(), "N": len(y),
                    "prevalence_pct": prevalence})

    # RF
    pipe_rf = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=100, random_state=42,
                                       class_weight="balanced", n_jobs=-1)),
    ])
    aucs_rf = cross_val_score(pipe_rf, X_tne, y, cv=cv, scoring="roc_auc")
    print(f"  Random Forest (5CV AUC): {aucs_rf.mean():.3f} ± {aucs_rf.std():.3f}")
    records.append({"method": "Random Forest (TNE)", "mean_AUC": aucs_rf.mean(),
                    "std_AUC": aucs_rf.std(), "N": len(y),
                    "prevalence_pct": prevalence})

    out_csv = OUTPUT_DIR / "p3_tartarus_poly_classification.csv"
    pd.DataFrame(records).to_csv(out_csv, index=False)
    print(f"  Results saved: {out_csv}")
    return pd.DataFrame(records)


# ─────────────────────────────────────────────
# §3.8.3 — TDA topology vs binding promiscuity
# ─────────────────────────────────────────────

def analysis_tda_promiscuity():
    print("\n" + "=" * 60)
    print("§3.8.3 — TDA Topology vs Binding Promiscuity (Spearman ρ)")
    print("=" * 60)

    tartarus = load_tartarus()
    tda_df   = load_tda()
    merged   = merge_with_tartarus(tda_df, tartarus)

    score_arr = merged[DOCKING_COLS].values.astype(np.float64)
    n_bound   = (score_arr <= POLYPHARM_THRESHOLD).sum(axis=1)

    tda_feat_cols = [c for c in merged.columns
                     if any(tag in c for tag in
                            ["H0_", "H1_", "H2_", "entropy", "count", "pers"])
                     and c not in ["smiles", "smile"] + DOCKING_COLS]

    records = []
    print(f"\n  Analysing {len(tda_feat_cols)} TDA features against #targets bound:")
    for feat in tda_feat_cols:
        vals = merged[feat].values.astype(np.float64)
        mask = np.isfinite(vals) & np.isfinite(n_bound)
        rho, p = stats.spearmanr(vals[mask], n_bound[mask])
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
        print(f"    {feat:<30}  ρ={rho:+.3f}  p={p:.2e} {sig}")
        records.append({"tda_feature": feat, "spearman_rho": rho,
                        "p_value": p, "N": mask.sum()})

    results = pd.DataFrame(records).sort_values("spearman_rho", key=abs, ascending=False)

    # Figure
    fig, ax = plt.subplots(figsize=(10, 5))
    bar_colors = [COLORS["tda"] if r >= 0 else "#e74c3c"
                  for r in results["spearman_rho"]]
    bars = ax.bar(results["tda_feature"], results["spearman_rho"],
                  color=bar_colors, edgecolor="black", linewidth=0.6)
    for bar, p in zip(bars, results["p_value"]):
        star = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
        if star:
            ypos = bar.get_height() + 0.003 if bar.get_height() >= 0 \
                   else bar.get_height() - 0.015
            ax.text(bar.get_x() + bar.get_width() / 2, ypos, star,
                    ha="center", va="bottom", fontsize=8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Spearman ρ (TDA feature vs #targets bound)", fontsize=10)
    ax.set_xlabel("TDA Feature", fontsize=10)
    ax.set_title(
        f"§3.8.3 — Topology vs Polypharmacology\n"
        f"(ΔG ≤ {POLYPHARM_THRESHOLD} kcal/mol, N={len(merged):,})",
        fontsize=11, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    out_fig = OUTPUT_DIR / "p3_tartarus_tda_promiscuity.png"
    plt.savefig(out_fig, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Figure saved: {out_fig}")

    out_csv = OUTPUT_DIR / "p3_tartarus_tda_spearman.csv"
    results.to_csv(out_csv, index=False)
    print(f"  Results saved: {out_csv}")
    return results


# ─────────────────────────────────────────────
# Summary report
# ─────────────────────────────────────────────

def write_summary(tne_df=None, poly_df=None, tda_df=None):
    lines = [
        "P3 × Tartarus Cross-Validation — Summary",
        "=" * 60,
        f"Generated: {pd.Timestamp.now().isoformat()}",
        "",
    ]
    if tne_df is not None:
        lines += ["§3.8.1 — TNE Regression on Docking Scores", "-" * 40,
                  tne_df.to_string(index=False), ""]
    if poly_df is not None:
        lines += ["§3.8.2 — Polypharmacology Classification", "-" * 40,
                  poly_df.to_string(index=False), ""]
    if tda_df is not None:
        lines += ["§3.8.3 — TDA Spearman ρ vs #Targets Bound", "-" * 40,
                  tda_df.head(10).to_string(index=False), ""]
    out = OUTPUT_DIR / "p3_tartarus_summary.txt"
    with open(out, "w") as f:
        f.write("\n".join(lines))
    print(f"\n  Summary saved: {out}")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="P3 × Tartarus cross-validation (§3.8.1–3.8.3)")
    parser.add_argument("--analysis", choices=["tne", "poly", "tda", "all"],
                        default="all")
    args = parser.parse_args()

    tne_res = poly_res = tda_res = None
    if args.analysis in ("tne", "all"):
        tne_res  = analysis_tne_regression()
    if args.analysis in ("poly", "all"):
        poly_res = analysis_polypharmacology_classification()
    if args.analysis in ("tda", "all"):
        tda_res  = analysis_tda_promiscuity()

    write_summary(tne_res, poly_res, tda_res)
    print("\n✓ Done. Results in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
