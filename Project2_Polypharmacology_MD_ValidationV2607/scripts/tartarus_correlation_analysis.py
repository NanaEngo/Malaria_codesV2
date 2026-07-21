#!/usr/bin/env python3
"""
Tartarus Multi-Level Correlation Analysis
=========================================
Correlates Tartarus benchmark docking scores (19,913 mol × 3 targets)
against our project's Vina, DiffDock, MPO, and ACSI metrics.

Data sources:
  results/tartarus_output.csv           — Tartarus scores (19,913 mol)
  data/from_project1/docking/ANP_MPO_Ranked_Final.csv  — Vina + DiffDock (94 mol)
  results/c_merged_metrics.csv          — MPO/ACSI/PNS for top 18 candidates
  results/docking_mutants.csv           — Vina per target/mutation

Outputs:
  results/analysis/
    tartarus_vina_correlation.csv       — Tartarus vs Vina per-target
    tartarus_diffdock_correlation.csv   — Tartarus vs DiffDock per-target
    tartarus_mpo_correlation.csv        — Tartarus vs MPO/ACSI (full scale)
    tartarus_all_correlations.csv       — Consolidated correlation table
    figure_tartarus_vs_vina.png         — Scatter: Tartarus composite vs Vina
    figure_tartarus_vs_diffdock.png     — Scatter: Tartarus vs DiffDock
    figure_tartarus_target_heatmap.png  — Per-target correlation heatmap
    figure_tartarus_distributions.png   — Score distribution comparison
"""

import argparse
from pathlib import Path
import warnings
import logging

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from scipy.stats import norm as normal_dist
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Optional RDKit for SMILES canonicalisation (increases merge overlap)
try:
    from rdkit import Chem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False
    print("  [WARN] RDKit not available. SMILES canonicalization disabled. "
          "Install RDKit for better SMILES matching.")

warnings.filterwarnings("ignore", category=FutureWarning)
logger = logging.getLogger("tartarus_correlation")

# ---- Paths ----
PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
DATA_DIR    = PROJECT_DIR / "data" / "from_project1" / "docking"
ANALYSIS_DIR = RESULTS_DIR / "analysis"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# Style
plt.rcParams.update({
    "figure.dpi": 150,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
})

# ---- Column mappings ----
# Tartarus targets (from the benchmark) vs our project targets
TARTARUS_TARGETS = {
    "score_1syh": "1SYH (DHFR benchmark)",
    "score_6y2f": "6Y2F (protease benchmark)",
    "score_4lde": "4LDE (A2a benchmark)",
}

OUR_TARGETS = {
    "aff_4gm2": "4GM2 (PfClpP)",
    "aff_6ukj": "6UKJ (PfCRT)",
    "aff_7f3y": "7F3Y (PfDHFR)",
    "aff_9n10": "9N10 (PfATP4)",
}

# ===================================================================
# 1. Data Loading
# ===================================================================

def load_tartarus(path: Path) -> pd.DataFrame:
    """Load Tartarus full-run docking scores (19,913 molecules)."""
    df = pd.read_csv(path)
    if "smile" in df.columns:
        df = df.rename(columns={"smile": "smiles"})
    df["smiles"] = df["smiles"].str.strip()
    # Flag failed dockings (score == 10000)
    for col in TARTARUS_TARGETS:
        if col in df.columns:
            df.loc[df[col] >= 9999, col] = np.nan
    # Composite = mean of available targets (more negative = stronger)
    tar_cols = [c for c in TARTARUS_TARGETS if c in df.columns]
    df["tar_composite"] = df[tar_cols].mean(axis=1)
    # Also compute per-target z-scores for normalized comparison
    for col in tar_cols:
        mu, sigma = df[col].mean(), df[col].std()
        df[f"{col}_z"] = (df[col] - mu) / sigma
    return df


def load_project_vina_diffdock(path: Path) -> pd.DataFrame:
    """Load our project's Vina + DiffDock scores from ANP_MPO_Ranked_Final."""
    df = pd.read_csv(path)
    df["SMILES"] = df["SMILES"].str.strip()
    df = df.rename(columns={"SMILES": "smiles"})

    # Normalised scores: S_vina, S_diff (0-1 range, higher = better)
    # Raw affinities: aff_4gm2, aff_6ukj, aff_7f3y, aff_9n10 (kcal/mol, more negative = better)
    # Confidence scores: conf_4gm2, conf_6ukj, conf_7f3y, conf_9n10

    # For the raw affinities, more negative = better binding
    # We invert them for correlation with Tartarus (where more negative also = better)
    # so that positive rho means agreement
    for col in OUR_TARGETS:
        if col in df.columns:
            pass  # keep as-is (negative = strong binding)

    return df


def load_merged_metrics(path: Path) -> pd.DataFrame:
    """Load P2 merged metrics (MPO, ACSI, PNS for top candidates)."""
    df = pd.read_csv(path)
    df["smiles"] = df["smiles"].str.strip()
    return df


def canonicalize_smiles(smiles_series: pd.Series) -> pd.Series:
    """Canonicalize SMILES with RDKit to maximise merge overlap.
    Falls back to stripped original if RDKit unavailable or parse fails.
    """
    if not HAS_RDKIT:
        return smiles_series.str.strip()

    def _canon(s):
        try:
            mol = Chem.MolFromSmiles(s)
            if mol is None:
                return s.strip()
            return Chem.MolToSmiles(mol, canonical=True)
        except Exception:
            return s.strip()

    return smiles_series.apply(_canon)


# ===================================================================
# 2. Correlation Analysis
# ===================================================================

def safe_spearmanr(x, y, min_n=5):
    """Spearman correlation with NaN handling and minimum n check."""
    mask = x.notna() & y.notna()
    n = mask.sum()
    if n < min_n:
        return {"n": int(n), "rho": np.nan, "p": np.nan, "significant": False}
    rho, p = spearmanr(x[mask], y[mask])
    return {"n": int(n), "rho": rho, "p": p, "significant": bool(p < 0.05)}


def safe_pearsonr(x, y, min_n=5):
    """Pearson correlation with NaN handling and minimum n check."""
    mask = x.notna() & y.notna()
    n = mask.sum()
    if n < min_n:
        return {"n": int(n), "r": np.nan, "p": np.nan, "significant": False}
    r, p = pearsonr(x[mask], y[mask])
    return {"n": int(n), "r": r, "p": p, "significant": bool(p < 0.05)}


def compute_target_correlations(merged_df):
    """
    Correlation between Tartarus targets and our project's Vina/DiffDock targets.
    Accepts a SINGLE merged dataframe with all columns.
    Returns DataFrame with Spearman ρ, Pearson r, p-values, and n.
    """
    rows = []

    # --- Tartarus composite vs each Vina target ---
    for proj_col, proj_label in OUR_TARGETS.items():
        if proj_col not in merged_df.columns:
            continue
        s = safe_spearmanr(merged_df["tar_composite"], merged_df[proj_col], min_n=5)
        p = safe_pearsonr(merged_df["tar_composite"], merged_df[proj_col], min_n=5)
        rows.append({
            "tartarus_metric": "Composite",
            "project_metric": proj_label,
            "project_column": proj_col,
            "spearman_rho": s["rho"],
            "spearman_p": s["p"],
            "spearman_sig": s["significant"],
            "pearson_r": p["r"],
            "pearson_p": p["p"],
            "n": s["n"],
        })

    # --- Per-target: 1SYH (DHFR benchmark) vs 7F3Y (PfDHFR) ---
    if "score_1syh" in merged_df.columns and "aff_7f3y" in merged_df.columns:
        sub = merged_df[["score_1syh", "aff_7f3y"]].dropna()
        if len(sub) >= 5:
            s = safe_spearmanr(sub["score_1syh"], sub["aff_7f3y"], min_n=5)
            p = safe_pearsonr(sub["score_1syh"], sub["aff_7f3y"], min_n=5)
            rows.append({
                "tartarus_metric": "score_1syh (DHFR)",
                "project_metric": "7F3Y (PfDHFR)",
                "project_column": "aff_7f3y",
                "spearman_rho": s["rho"],
                "spearman_p": s["p"],
                "spearman_sig": s["significant"],
                "pearson_r": p["r"],
                "pearson_p": p["p"],
                "n": s["n"],
            })

    # --- Tartarus composite vs S_vina (normalised Vina) ---
    if "S_vina" in merged_df.columns:
        s = safe_spearmanr(merged_df["tar_composite"], merged_df["S_vina"], min_n=5)
        p = safe_pearsonr(merged_df["tar_composite"], merged_df["S_vina"], min_n=5)
        rows.append({
            "tartarus_metric": "Composite",
            "project_metric": "S_vina (normalised)",
            "project_column": "S_vina",
            "spearman_rho": s["rho"],
            "spearman_p": s["p"],
            "spearman_sig": s["significant"],
            "pearson_r": p["r"],
            "pearson_p": p["p"],
            "n": s["n"],
        })

    # --- Tartarus composite vs S_diff (normalised DiffDock) ---
    if "S_diff" in merged_df.columns:
        s = safe_spearmanr(merged_df["tar_composite"], merged_df["S_diff"], min_n=5)
        p = safe_pearsonr(merged_df["tar_composite"], merged_df["S_diff"], min_n=5)
        rows.append({
            "tartarus_metric": "Composite",
            "project_metric": "S_diff (normalised)",
            "project_column": "S_diff",
            "spearman_rho": s["rho"],
            "spearman_p": s["p"],
            "spearman_sig": s["significant"],
            "pearson_r": p["r"],
            "pearson_p": p["p"],
            "n": s["n"],
        })

    return pd.DataFrame(rows)


def compute_mpo_correlations(tar_df, merged_metrics_df):
    """
    Correlations between Tartarus scores and MPO-derived metrics (ACSI, PNS, MPO score).
    Even with the full 19,913-mol Tartarus file, the overlap may be small
    if MPO only exists for top candidates.
    """
    rows = []

    # Merge Tartarus with merged metrics on SMILES
    merged = tar_df.merge(merged_metrics_df, on="smiles", how="inner", suffixes=("", "_m"))

    if len(merged) < 5:
        print(f"  [INFO] Only {len(merged)} overlapping molecules for MPO correlation (top candidates only)")
        return pd.DataFrame(rows), merged

    # Tartarus composite vs ACSI
    if "ACSI" in merged.columns:
        s = safe_spearmanr(merged["tar_composite"], merged["ACSI"], min_n=5)
        rows.append({
            "tartarus_metric": "Composite",
            "project_metric": "ACSI",
            "spearman_rho": s["rho"],
            "spearman_p": s["p"],
            "spearman_sig": s["significant"],
            "n": s["n"],
        })

    # Tartarus composite vs PNS
    if "PNS" in merged.columns:
        s = safe_spearmanr(merged["tar_composite"], merged["PNS"], min_n=5)
        rows.append({
            "tartarus_metric": "Composite",
            "project_metric": "PNS",
            "spearman_rho": s["rho"],
            "spearman_p": s["p"],
            "spearman_sig": s["significant"],
            "n": s["n"],
        })

    # Tartarus per-target vs ACSI
    for col in TARTARUS_TARGETS:
        if col in merged.columns:
            s = safe_spearmanr(merged[col], merged["ACSI"], min_n=5)
            rows.append({
                "tartarus_metric": col,
                "project_metric": "ACSI",
                "spearman_rho": s["rho"],
                "spearman_p": s["p"],
                "spearman_sig": s["significant"],
                "n": s["n"],
            })

    return pd.DataFrame(rows), merged


# ===================================================================
# 3. Visualisations
# ===================================================================

def plot_tartarus_vs_vina(merged_df, save_path: Path):
    """Scatter plot: Tartarus composite vs normalised Vina/DiffDock scores with CI bands."""
    if len(merged_df) < 5:
        print(f"  [WARN] Too few points ({len(merged_df)}) for Tartarus vs Vina scatter")
        return

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Tartarus Docking Scores vs. Project Docking Metrics", fontsize=14, y=1.02)

    # Panel A: Tartarus composite vs S_vina
    ax = axes[0]
    sub = merged_df[["tar_composite", "S_vina"]].dropna()
    if len(sub) >= 5:
        rho, p = spearmanr(sub["tar_composite"], sub["S_vina"])
        sns.regplot(data=sub, x="tar_composite", y="S_vina", ax=ax,
                    scatter_kws={"alpha": 0.6, "s": 30, "color": "#2196F3",
                                "edgecolors": "white"},
                    line_kws={"color": "#E91E63", "linestyle": "--"},
                    ci=95, truncate=False)
        sig = "*" if p < 0.05 else ""
        ax.set_title(f"A: Tartarus vs Vina (n={len(sub)}, ρ={rho:.3f}{sig}, p={p:.2e})")
    ax.set_xlabel("Tartarus Composite Score (kcal/mol)")
    ax.set_ylabel("S_vina (normalised)")

    # Panel B: Tartarus composite vs best per-target affinity
    ax2 = axes[1]
    df_local = merged_df.copy()
    df_local["best_aff"] = df_local[[c for c in OUR_TARGETS if c in df_local.columns]].min(axis=1)
    sub2 = df_local[["tar_composite", "best_aff"]].dropna()
    if len(sub2) >= 5:
        rho2, p2 = spearmanr(sub2["tar_composite"], sub2["best_aff"])
        sns.regplot(data=sub2, x="tar_composite", y="best_aff", ax=ax2,
                    scatter_kws={"alpha": 0.6, "s": 30, "color": "#4CAF50",
                                "edgecolors": "white"},
                    line_kws={"color": "#E91E63", "linestyle": "--"},
                    ci=95, truncate=False)
        sig = "*" if p2 < 0.05 else ""
        ax2.set_title(f"B: Tartarus vs Best Affinity (n={len(sub2)}, ρ={rho2:.3f}{sig})")
    ax2.set_xlabel("Tartarus Composite Score (kcal/mol)")
    ax2.set_ylabel("Best per-target affinity (kcal/mol)")

    # Panel C: Tartarus composite vs DiffDock
    ax3 = axes[2]
    sub3 = merged_df[["tar_composite", "S_diff"]].dropna()
    if len(sub3) >= 5:
        rho3, p3 = spearmanr(sub3["tar_composite"], sub3["S_diff"])
        sns.regplot(data=sub3, x="tar_composite", y="S_diff", ax=ax3,
                    scatter_kws={"alpha": 0.6, "s": 30, "color": "#FF9800",
                                "edgecolors": "white"},
                    line_kws={"color": "#E91E63", "linestyle": "--"},
                    ci=95, truncate=False)
        sig = "*" if p3 < 0.05 else ""
        ax3.set_title(f"C: Tartarus vs DiffDock (n={len(sub3)}, ρ={rho3:.3f}{sig})")
    ax3.set_xlabel("Tartarus Composite Score (kcal/mol)")
    ax3.set_ylabel("S_diff (normalised)")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] {save_path}")


def plot_correlation_heatmap(corr_df, save_path: Path):
    """Heatmap of all Spearman correlations."""
    if corr_df.empty:
        print("  [WARN] Empty correlation data for heatmap")
        return

    # Pivot: rows = Tartarus metrics, cols = project metrics
    pivot = corr_df.pivot_table(
        index="tartarus_metric", columns="project_metric",
        values="spearman_rho", aggfunc="first"
    )
    # Also create significance mask
    sig_pivot = corr_df.pivot_table(
        index="tartarus_metric", columns="project_metric",
        values="spearman_sig", aggfunc="first"
    )

    fig, ax = plt.subplots(figsize=(10, max(4, len(pivot) * 0.8 + 2)))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="RdBu_r", center=0,
                vmin=-1, vmax=1, linewidths=1, cbar_kws={"label": "Spearman ρ"},
                ax=ax, mask=pivot.isna())
    
    # Star significant correlations
    for i in range(len(pivot)):
        for j in range(len(pivot.columns)):
            if not pivot.isna().iloc[i, j] and sig_pivot.iloc[i, j]:
                ax.text(j + 0.5, i + 0.3, "*", ha="center", va="center",
                        fontsize=18, color="black", fontweight="bold")

    ax.set_title("Tartarus vs Project Docking: Spearman Correlations\n(* p < 0.05)", fontsize=13)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] {save_path}")


def plot_distributions(tar_df, proj_df, save_path: Path):
    """Side-by-side distribution comparison of Tartarus and project scores."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    fig.suptitle("Score Distributions: Tartarus vs Project Docking", fontsize=14)

    # Row 1: Tartarus targets
    for i, (col, label) in enumerate(TARTARUS_TARGETS.items()):
        if col in tar_df.columns:
            vals = tar_df[col].dropna()
            ax = axes[0, i]
            ax.hist(vals, bins=50, alpha=0.7, color="#2196F3", edgecolor="white", linewidth=0.3)
            ax.axvline(vals.mean(), color="#E91E63", linestyle="--", label=f"μ={vals.mean():.2f}")
            ax.set_xlabel(f"{label} (kcal/mol)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"{label}\n(n={len(vals):,})")
            ax.legend(fontsize=8)

    # Row 2: Project targets (affinities)
    proj_cols = [("aff_4gm2", "4GM2 (PfClpP)"), ("aff_6ukj", "6UKJ (PfCRT)"),
                 ("aff_7f3y", "7F3Y (PfDHFR)")]
    for i, (col, label) in enumerate(proj_cols):
        if col in proj_df.columns:
            vals = proj_df[col].dropna()
            ax = axes[1, i]
            ax.hist(vals, bins=30, alpha=0.7, color="#4CAF50", edgecolor="white", linewidth=0.3)
            ax.axvline(vals.mean(), color="#E91E63", linestyle="--", label=f"μ={vals.mean():.2f}")
            ax.set_xlabel(f"{label} (kcal/mol)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"{label}\n(n={len(vals):,})")
            ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] {save_path}")


def plot_per_target_scatter(merged_df, save_path: Path):
    """Per-target scatter plots with confidence bands."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Per-Target Comparison: Tartarus vs Project Docking", fontsize=14)

    comparisons = [
        ("score_1syh", "aff_7f3y", "Tartarus 1SYH (DHFR)", "Project 7F3Y (PfDHFR)"),
        ("score_6y2f", "aff_6ukj", "Tartarus 6Y2F (protease)", "Project 6UKJ (PfCRT)"),
        ("score_4lde", "aff_4gm2", "Tartarus 4LDE (A2a)", "Project 4GM2 (PfClpP)"),
        ("score_1syh", "aff_9n10", "Tartarus 1SYH (DHFR)", "Project 9N10 (PfATP4)"),
    ]

    for idx, (tar_col, proj_col, tar_lbl, proj_lbl) in enumerate(comparisons):
        ax = axes[idx // 2, idx % 2]
        sub = merged_df[[tar_col, proj_col]].dropna()
        if len(sub) < 5:
            ax.text(0.5, 0.5, f"Insufficient data (n={len(sub)})",
                    ha="center", va="center", transform=ax.transAxes, fontsize=12)
            ax.set_title(f"{tar_lbl} vs {proj_lbl}")
            continue

        rho, p = spearmanr(sub[tar_col], sub[proj_col])
        sns.regplot(data=sub, x=tar_col, y=proj_col, ax=ax,
                    scatter_kws={"alpha": 0.6, "s": 25, "color": "#9C27B0",
                                "edgecolors": "white"},
                    line_kws={"color": "#E91E63", "linestyle": "--"},
                    ci=95, truncate=False)
        sig = "*" if p < 0.05 else ""
        ax.set_xlabel(f"{tar_lbl} (kcal/mol)")
        ax.set_ylabel(f"{proj_lbl} (kcal/mol)")
        ax.set_title(f"{tar_lbl} vs {proj_lbl}\nn={len(sub)}, ρ={rho:.3f}{sig}")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] {save_path}")


# ===================================================================
# 4. Manuscript Helper: LaTeX Table
# ===================================================================

def generate_latex_table(corr_df, save_path: Path):
    """Generate a LaTeX table of correlations suitable for manuscript."""
    if corr_df.empty:
        save_path.write_text("% No significant correlations found")
        return

    # Compute power for the largest n
    max_n = int(corr_df["n"].max()) if "n" in corr_df.columns else 0
    # Power analysis for Spearman ρ = 0.6 at α = 0.05 (two-sided)
    # Using normal approximation: z = arctanh(ρ) * sqrt(n-3)
    power_note = (f"% Power analysis: With n={max_n}, achieving ρ=0.6 at α=0.05 "
                  f"gives ~{min(100, int(100 * (1 - normal_dist.cdf(1.96 - 0.6 * (max_n - 3)**0.5)))):.0f}% power. "
                  f"Results with n<20 should be interpreted cautiously.")

    lines = [
        power_note,
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Tartarus External Validation: Spearman Correlations with Project Docking Scores}",
        r"\label{tab:tartarus_correlation}",
        r"\small",
        r"\begin{tabular}{lcrrr}",
        r"\toprule",
        r"Tartarus Metric & Project Metric & $n$ & $\rho$ & $p$-value \\",
        r"\midrule",
    ]

    for _, row in corr_df.iterrows():
        if np.isnan(row["spearman_rho"]):
            continue
        sig_marker = "$^*$" if row["spearman_sig"] else ""
        lines.append(
            f"  {row['tartarus_metric']} & "
            f"{row['project_metric']} & "
            f"{int(row['n'])} & "
            f"${row['spearman_rho']:.3f}{sig_marker}$ & "
            f"${row['spearman_p']:.2e}$ \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    save_path.write_text("\n".join(lines))
    print(f"  [SAVED] {save_path}")


# ===================================================================
# Main
# ===================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Tartarus Multi-Level Correlation Analysis"
    )
    parser.add_argument("--tartarus-csv", type=Path,
                        default=RESULTS_DIR / "tartarus_output.csv",
                        help="Full Tartarus output CSV (19,913 mols)")
    parser.add_argument("--project-csv", type=Path,
                        default=DATA_DIR / "ANP_MPO_Ranked_Final.csv",
                        help="Project Vina/DiffDock scores CSV")
    parser.add_argument("--metrics-csv", type=Path,
                        default=RESULTS_DIR / "c_merged_metrics.csv",
                        help="Merged MPO/ACSI metrics CSV")
    parser.add_argument("--canonicalize", action="store_true", default=True,
                        help="Canonicalize SMILES with RDKit to increase merge overlap")
    parser.add_argument("--no-canonicalize", action="store_false", dest="canonicalize",
                        help="Skip SMILES canonicalization")
    args = parser.parse_args()

    print("=" * 65)
    print("Tartarus Multi-Level Correlation Analysis")
    print("=" * 65)

    # 1. Load data
    print("\n[1] Loading data...")
    tar_df = load_tartarus(args.tartarus_csv)
    print(f"    Tartarus: {len(tar_df)} molecules, "
          f"{sum(tar_df[c].notna().sum() for c in TARTARUS_TARGETS if c in tar_df.columns)} valid scores")

    proj_df = load_project_vina_diffdock(args.project_csv)
    print(f"    Project Vina/DiffDock: {len(proj_df)} molecules")

    metrics_df = load_merged_metrics(args.metrics_csv)
    print(f"    Merged metrics: {len(metrics_df)} molecules")

    # Canonicalise SMILES if requested (increases merge overlap)
    if args.canonicalize and HAS_RDKIT:
        print("\n    Canonicalizing SMILES with RDKit...")
        n_before = len(tar_df) + len(proj_df)
        tar_df["smiles"] = canonicalize_smiles(tar_df["smiles"])
        proj_df["smiles"] = canonicalize_smiles(proj_df["smiles"])
        metrics_df["smiles"] = canonicalize_smiles(metrics_df["smiles"])
        # Drop rows where SMILES became NaN after canonicalization
        tar_df = tar_df.dropna(subset=["smiles"])
        proj_df = proj_df.dropna(subset=["smiles"])
        print(f"    After canonicalization: {len(tar_df)} Tartarus + {len(proj_df)} project molecules")

    # 2. Merge Tartarus with project Vina/DiffDock
    print("\n[2] Computing Tartarus vs Vina/DiffDock correlations...")
    merged_tar_proj = tar_df.merge(proj_df, on="smiles", how="inner", suffixes=("", "_proj"))
    print(f"    Overlap: {len(merged_tar_proj)} molecules with both Tartarus and project scores")

    # Single merged dataframe passed to correlation function
    tar_vina_corr = compute_target_correlations(merged_tar_proj)
    if not tar_vina_corr.empty:
        tar_vina_corr.to_csv(ANALYSIS_DIR / "tartarus_vina_correlation.csv", index=False)
        print(f"    Saved: {ANALYSIS_DIR / 'tartarus_vina_correlation.csv'}")
        print(f"    Results ({len(tar_vina_corr)} comparisons):")
        for _, row in tar_vina_corr.iterrows():
            sig = " *" if row["spearman_sig"] else ""
            print(f"      {row['tartarus_metric']:25s} vs {row['project_metric']:30s}  "
                  f"ρ={row['spearman_rho']:.3f}{sig}  (n={int(row['n'])})")

    # 3. Tartarus vs MPO/ACSI
    print("\n[3] Computing Tartarus vs MPO/ACSI correlations...")
    mpo_corr_df, mpo_merged = compute_mpo_correlations(merged_tar_proj, metrics_df)
    if not mpo_corr_df.empty:
        mpo_corr_df.to_csv(ANALYSIS_DIR / "tartarus_mpo_correlation.csv", index=False)
        print(f"    Saved: {ANALYSIS_DIR / 'tartarus_mpo_correlation.csv'}")
        for _, row in mpo_corr_df.iterrows():
            sig = " *" if row.get("spearman_sig", False) else ""
            print(f"      {row['tartarus_metric']:25s} vs {row['project_metric']:10s}  "
                  f"ρ={row['spearman_rho']:.3f}{sig}  (n={int(row['n'])})")

    # 4. Consolidated correlation table
    all_corr = pd.concat([tar_vina_corr, mpo_corr_df], ignore_index=True)
    # Print power warning
    max_n = int(all_corr["n"].max()) if not all_corr.empty else 0
    if max_n < 20:
        print(f"\n    [CAVEAT] Maximum n = {max_n}. With n<20, Spearman correlations")
        print(f"             have <80% power to detect ρ < 0.65 at α = 0.05.")
        print(f"             Results should be interpreted as exploratory.")
    all_corr.to_csv(ANALYSIS_DIR / "tartarus_all_correlations.csv", index=False)
    print(f"\n    Consolidated: {ANALYSIS_DIR / 'tartarus_all_correlations.csv'} ({len(all_corr)} comparisons)")

    # 5. Generate LaTeX table
    generate_latex_table(all_corr, ANALYSIS_DIR / "table_tartarus_correlation.tex")
    print(f"    LaTeX table: {ANALYSIS_DIR / 'table_tartarus_correlation.tex'}")

    # 6. Generate figures
    print("\n[4] Generating visualizations...")
    plot_tartarus_vs_vina(merged_tar_proj,
                          ANALYSIS_DIR / "figure_tartarus_vs_vina.png")
    plot_correlation_heatmap(tar_vina_corr,
                             ANALYSIS_DIR / "figure_tartarus_target_heatmap.png")
    plot_distributions(merged_tar_proj, merged_tar_proj,
                       ANALYSIS_DIR / "figure_tartarus_distributions.png")
    plot_per_target_scatter(merged_tar_proj,
                            ANALYSIS_DIR / "figure_tartarus_per_target.png")

    # 7. Statistical summary
    print("\n[5] Summary statistics...")
    n_valid = merged_tar_proj["tar_composite"].notna().sum()
    print(f"    Tartarus valid composite scores: {n_valid:,} / {len(merged_tar_proj):,}")
    print(f"    Mean composite: {merged_tar_proj['tar_composite'].mean():.2f} ± {merged_tar_proj['tar_composite'].std():.2f} kcal/mol")
    
    print("\n" + "=" * 65)
    print("Analysis complete!")
    print(f"Outputs saved to: {ANALYSIS_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
