#!/usr/bin/env python3
"""P4 — Comprehensive results visualization for MCTS+RL and QMC analyses.

Generates publication-quality figures for the P4 project:

1. **MCTS search trajectory** — best reward over iterations, tree depth
2. **Fragment usage distribution** — which fragments are used most
3. **Score component heatmap** — MPO vs Docking vs SYBA vs SA across molecules
4. **Molecular property analysis** — MW, LogP, HBA, HBD, RotBonds
5. **QMC energy landscape** — if QMC results are available
6. **Combined dashboards** — multi-panel summary figures

Usage
-----
# Visualize merged MCTS results
python p4_visualize.py --mcts-csv results/mcts/p4_mcts_merged_ranked.csv

# Include QMC data
python p4_visualize.py --mcts-csv results/mcts/p4_mcts_merged_ranked.csv --qmc-dir qmc_inputs/

# Full dashboard
python p4_visualize.py --mcts-csv ... --output-dir figures/ --dashboard
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger("p4_visualize")

# ── Optional dependencies ────────────────────────────────────────────
_HAS_PANDAS = False
_HAS_MATPLOTLIB = False
_HAS_SEABORN = False
_HAS_RDKIT = False

try:
    import pandas as pd

    _HAS_PANDAS = True
except ImportError:
    pass

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    matplotlib.use("Agg")
    _HAS_MATPLOTLIB = True
except ImportError:
    pass

try:
    import seaborn as sns

    _HAS_SEABORN = True
except ImportError:
    pass

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors

    _HAS_RDKIT = True
except ImportError:
    pass

# ── Colour palette ───────────────────────────────────────────────────
PALETTE = {
    "primary": "#4575b4",
    "secondary": "#fc8d59",
    "tertiary": "#313695",
    "accent": "#d73027",
    "bg": "#f5f5f5",
    "grid": "#dddddd",
    "positive": "#4575b4",
    "negative": "#d73027",
    "neutral": "#cccccc",
}

# Fragment categories with colours
FRAGMENT_COLORS = {
    "aromatic": "#4575b4",
    "saturated_heterocycle": "#91cf60",
    "alkyl": "#fee08b",
    "functional_group": "#fc8d59",
    "halogen_cn": "#d73027",
}


def _setup_style() -> None:
    """Set consistent matplotlib style."""
    if not _HAS_MATPLOTLIB:
        return

    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": PALETTE["bg"],
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.color": PALETTE["grid"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.2,
    })

    if _HAS_SEABORN:
        sns.set_style("whitegrid")
        sns.set_palette("colorblind")


# ═══════════════════════════════════════════════════════════════════════
#  1. MCTS Trajectory Plots
# ═══════════════════════════════════════════════════════════════════════


def plot_mcts_trajectory(
    results_df: "pd.DataFrame",
    output_path: Path,
    max_molecules: int = 50,
) -> Optional[Path]:
    """Plot the MCTS search trajectory showing reward progression.

    Parameters
    ----------
    results_df : pd.DataFrame
        Merged MCTS results with 'rank' and 'best_reward' columns.
    output_path : Path
        Output PNG path.
    max_molecules : int
        Maximum number of top molecules to show.

    Returns
    -------
    Path or None
    """
    if not _HAS_MATPLOTLIB or not _HAS_PANDAS:
        return None

    df = results_df.head(max_molecules).copy()
    if df.empty:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Reward vs Rank
    x = range(1, len(df) + 1)
    ax1.scatter(x, df["best_reward"], c=PALETTE["primary"],
                s=40, alpha=0.7, edgecolor="white", linewidth=0.5, zorder=3)
    ax1.plot(x, df["best_reward"], color=PALETTE["secondary"],
             alpha=0.4, linewidth=1, zorder=1)

    # Rolling mean
    if len(df) >= 10:
        rolling = df["best_reward"].rolling(window=10, center=True).mean()
        ax1.plot(x, rolling, color=PALETTE["accent"],
                 linewidth=2, label="10-molecule rolling mean", zorder=2)
        ax1.legend(fontsize=9)

    ax1.set_xlabel("Rank")
    ax1.set_ylabel("Best Reward")
    ax1.set_title("MCTS Search Trajectory — Reward by Rank")

    # Right: Reward distribution histogram
    ax2.hist(df["best_reward"], bins=min(25, len(df) // 2),
             color=PALETTE["primary"], edgecolor="white",
             alpha=0.8, density=True)
    median_r = df["best_reward"].median()
    ax2.axvline(median_r, color=PALETTE["accent"], linestyle="--",
                linewidth=2, label=f"Median: {median_r:.4f}")
    ax2.set_xlabel("Reward")
    ax2.set_ylabel("Density")
    ax2.set_title("Reward Distribution")
    ax2.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info("MCTS trajectory plot: %s", output_path)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
#  2. Fragment Usage Distribution
# ═══════════════════════════════════════════════════════════════════════


def plot_fragment_usage(
    usage_data: dict[str, int],
    output_path: Path,
    top_n: int = 20,
) -> Optional[Path]:
    """Plot fragment usage counts as a horizontal bar chart.

    Parameters
    ----------
    usage_data : dict
        Mapping from fragment name to count.
    output_path : Path
        Output PNG path.
    top_n : int
        Show only top-N fragments.

    Returns
    -------
    Path or None
    """
    if not _HAS_MATPLOTLIB:
        return None

    if not usage_data:
        return None

    # Sort and take top N
    sorted_items = sorted(usage_data.items(), key=lambda x: x[1], reverse=True)
    names, counts = zip(*sorted_items[:top_n])

    fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.35)))

    # Assign colors by category (heuristic: infer from fragment name)
    colors = []
    for name in names:
        name_lower = name.lower()
        if any(arom in name_lower for arom in ["phenyl", "pyridyl", "pyrimidin", "furan", "thiophen", "pyrrol", "imidazol", "thiazol"]):
            colors.append(FRAGMENT_COLORS["aromatic"])
        elif any(het in name_lower for het in ["piperidin", "morpholin", "piperazin", "pyrrolidin"]):
            colors.append(FRAGMENT_COLORS["saturated_heterocycle"])
        elif any(alk in name_lower for alk in ["methyl", "ethyl", "isopropyl", "butyl", "cyclopropyl", "trifluoroethyl"]):
            colors.append(FRAGMENT_COLORS["alkyl"])
        elif any(fg in name_lower for fg in ["hydroxyl", "methoxy", "ethoxy", "amine", "amino", "carboxyl", "amide", "ester", "sulfonamide"]):
            colors.append(FRAGMENT_COLORS["functional_group"])
        else:
            colors.append(FRAGMENT_COLORS["halogen_cn"])

    bars = ax.barh(range(len(names)), counts, color=colors, edgecolor="white", height=0.7)

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("Usage count")
    ax.set_title(f"Fragment Usage Distribution (Top {top_n})")
    ax.invert_yaxis()

    # Add count labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(count + 0.3, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", fontsize=8, color="gray")

    # Legend
    legend_elements = [
        Line2D([0], [0], color=FRAGMENT_COLORS["aromatic"], lw=4, label="Aromatic"),
        Line2D([0], [0], color=FRAGMENT_COLORS["saturated_heterocycle"], lw=4, label="Saturated heterocycle"),
        Line2D([0], [0], color=FRAGMENT_COLORS["alkyl"], lw=4, label="Alkyl"),
        Line2D([0], [0], color=FRAGMENT_COLORS["functional_group"], lw=4, label="Functional group"),
        Line2D([0], [0], color=FRAGMENT_COLORS["halogen_cn"], lw=4, label="Halogen / CN"),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc="lower right")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info("Fragment usage plot: %s", output_path)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
#  3. Score Component Heatmap
# ═══════════════════════════════════════════════════════════════════════


def plot_score_heatmap(
    results_df: "pd.DataFrame",
    output_path: Path,
    top_n: int = 30,
) -> Optional[Path]:
    """Plot a heatmap of score components (MPO, docking, SYBA, SA).

    Parameters
    ----------
    results_df : pd.DataFrame
        Merged MCTS results with component score columns.
    output_path : Path
        Output PNG path.
    top_n : int
        Number of top molecules to include.

    Returns
    -------
    Path or None
    """
    if not _HAS_MATPLOTLIB or not _HAS_PANDAS or not _HAS_SEABORN:
        return None

    # Check required columns
    score_cols = [c for c in ["mpo", "docking", "syba", "sa"] if c in results_df.columns]
    if len(score_cols) < 2:
        logger.warning("Not enough score columns for heatmap (need mpo, docking, syba, sa)")
        return None

    df = results_df.head(top_n).copy()
    if df.empty:
        return None

    # Prepare heatmap data (normalise each column to [0, 1])
    heat_data = df[score_cols].copy()
    for col in score_cols:
        col_min, col_max = heat_data[col].min(), heat_data[col].max()
        if col_max > col_min:
            heat_data[col] = (heat_data[col] - col_min) / (col_max - col_min)

    # Short molecule labels
    if "best_state" in df.columns:
        labels = [s[:15] + "..." if len(str(s)) > 15 else str(s) for s in df["best_state"]]
    else:
        labels = [f"M{i+1}" for i in range(len(df))]

    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.35)))
    sns.heatmap(
        heat_data,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Normalised Score", "shrink": 0.6},
        yticklabels=labels,
        xticklabels=[c.upper() for c in score_cols],
    )
    ax.set_title("Score Component Heatmap — Top Molecules")
    ax.set_ylabel("Molecule")
    ax.set_xlabel("Score Component")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info("Score heatmap: %s", output_path)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
#  4. Molecular Property Analysis
# ═══════════════════════════════════════════════════════════════════════


def compute_molecular_properties(smiles_list: list[str]) -> "pd.DataFrame":
    """Compute RDKit molecular properties for a list of SMILES.

    Parameters
    ----------
    smiles_list : list of str
        List of SMILES strings.

    Returns
    -------
    pd.DataFrame
        DataFrame with computed properties.
    """
    if not _HAS_RDKIT or not _HAS_PANDAS:
        return pd.DataFrame()

    properties = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            properties.append({
                "SMILES": smi,
                "MW": 0, "LogP": 0, "HBA": 0, "HBD": 0,
                "RotBonds": 0, "TPSA": 0, "RingCount": 0,
                "Validity": False,
            })
            continue
        try:
            properties.append({
                "SMILES": smi,
                "MW": Descriptors.MolWt(mol),
                "LogP": Descriptors.MolLogP(mol),
                "HBA": Descriptors.NumHAcceptors(mol),
                "HBD": Descriptors.NumHDonors(mol),
                "RotBonds": Descriptors.NumRotatableBonds(mol),
                "TPSA": Descriptors.TPSA(mol),
                "RingCount": rdMolDescriptors.CalcNumRings(mol),
                "Validity": True,
            })
        except Exception as exc:
            logger.debug("Property computation failed for %s: %s", smi, exc)
            properties.append({
                "SMILES": smi, "MW": 0, "LogP": 0, "HBA": 0,
                "HBD": 0, "RotBonds": 0, "TPSA": 0, "RingCount": 0,
                "Validity": False,
            })

    return pd.DataFrame(properties)


def plot_property_radar(
    properties_df: "pd.DataFrame",
    output_path: Path,
    top_n: int = 5,
) -> Optional[Path]:
    """Plot a radar chart of molecular properties for the top N molecules.

    Parameters
    ----------
    properties_df : pd.DataFrame
        DataFrame with molecular properties.
    output_path : Path
        Output PNG path.
    top_n : int
        Number of top molecules to show.

    Returns
    -------
    Path or None
    """
    if not _HAS_MATPLOTLIB or not _HAS_PANDAS:
        return None

    prop_cols = ["MW", "LogP", "HBA", "HBD", "RotBonds", "TPSA"]
    available = [c for c in prop_cols if c in properties_df.columns]
    if len(available) < 3:
        return None

    df = properties_df.head(top_n).copy()
    if df.empty:
        return None

    # Normalise properties to [0, 1] for radar chart
    norm_df = pd.DataFrame()
    for col in available:
        col_min, col_max = df[col].min(), df[col].max()
        if col_max > col_min:
            norm_df[col] = (df[col] - col_min) / (col_max - col_min)
        else:
            norm_df[col] = 0.5

    n_props = len(available)
    angles = np.linspace(0, 2 * np.pi, n_props, endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})

    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(df)))
    for idx, (_, row) in enumerate(norm_df.iterrows()):
        values = row[available].tolist() + [row[available].iloc[0]]
        ax.plot(angles, values, "o-", color=colors[idx], linewidth=2,
                label=f"M{idx+1}" if idx < 10 else f"M{idx+1}", alpha=0.8)
        ax.fill(angles, values, alpha=0.1, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(available, fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.set_title("Molecular Property Comparison (Top Molecules)", pad=25)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0), fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info("Property radar chart: %s", output_path)
    return output_path


def plot_property_correlation(
    properties_df: "pd.DataFrame",
    output_path: Path,
) -> Optional[Path]:
    """Plot a correlation matrix of molecular properties.

    Parameters
    ----------
    properties_df : pd.DataFrame
        DataFrame with molecular properties.
    output_path : Path
        Output PNG path.

    Returns
    -------
    Path or None
    """
    if not _HAS_MATPLOTLIB or not _HAS_PANDAS or not _HAS_SEABORN:
        return None

    prop_cols = ["MW", "LogP", "HBA", "HBD", "RotBonds", "TPSA", "RingCount"]
    available = [c for c in prop_cols if c in properties_df.columns]
    if len(available) < 3:
        return None

    corr = properties_df[available].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Pearson r", "shrink": 0.7},
    )
    ax.set_title("Molecular Property Correlation Matrix")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info("Property correlation plot: %s", output_path)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
#  5. Combined Dashboard
# ═══════════════════════════════════════════════════════════════════════


def plot_dashboard(
    mcts_df: "pd.DataFrame",
    properties_df: "pd.DataFrame",
    fragment_data: dict[str, int],
    qmc_data: Optional[dict[str, Any]] = None,
    output_path: Optional[Path] = None,
) -> Optional[Path]:
    """Generate a comprehensive multi-panel dashboard figure.

    Parameters
    ----------
    mcts_df : pd.DataFrame
        Merged MCTS results.
    properties_df : pd.DataFrame
        Molecular properties.
    fragment_data : dict
        Fragment usage counts.
    qmc_data : dict or None
        QMC analysis results (optional).
    output_path : Path or None
        Output PNG path.

    Returns
    -------
    Path or None
    """
    if not _HAS_MATPLOTLIB or not _HAS_PANDAS:
        return None

    n_panels = 4 if qmc_data else 3
    fig = plt.figure(figsize=(16, n_panels * 4.5))

    gs = fig.add_gridspec(n_panels, 2, hspace=0.3, wspace=0.25)

    # Panel 1: MCTS Trajectory (top left)
    ax1 = fig.add_subplot(gs[0, :])
    x = range(1, min(len(mcts_df), 50) + 1)
    rewards = mcts_df["best_reward"].head(50).values
    ax1.scatter(x, rewards, c=PALETTE["primary"], s=30, alpha=0.6, edgecolor="white")
    ax1.plot(x, rewards, color=PALETTE["secondary"], alpha=0.4)
    if len(rewards) >= 10:
        rolling = pd.Series(rewards).rolling(10, center=True).mean()
        ax1.plot(x, rolling, color=PALETTE["accent"], linewidth=2,
                 label="10-molecule rolling mean")
        ax1.legend(fontsize=8)
    ax1.set_xlabel("Rank")
    ax1.set_ylabel("Reward")
    ax1.set_title("MCTS Search Trajectory")

    # Panel 2: Fragment usage (top right)
    ax2 = fig.add_subplot(gs[1, 0])
    if fragment_data:
        sorted_items = sorted(fragment_data.items(), key=lambda x: x[1], reverse=True)[:15]
        names, counts = zip(*sorted_items)
        ax2.barh(range(len(names)), counts, color=PALETTE["primary"], edgecolor="white")
        ax2.set_yticks(range(len(names)))
        ax2.set_yticklabels([n[:12] + ".." if len(n) > 12 else n for n in names], fontsize=7)
        ax2.invert_yaxis()
        ax2.set_xlabel("Count")
        ax2.set_title(f"Top Fragments (n={sum(counts)})")

    # Panel 3: Properties (bottom left)
    ax3 = fig.add_subplot(gs[1, 1])
    prop_cols = ["MW", "LogP", "HBA", "HBD", "RotBonds", "TPSA"]
    available = [c for c in prop_cols if c in properties_df.columns]
    if available and not properties_df.empty:
        props_mean = properties_df[available].mean()
        props_std = properties_df[available].std()
        x_pos = range(len(available))
        ax3.bar(x_pos, props_mean, yerr=props_std, color=PALETTE["primary"],
                edgecolor="white", capsize=3, alpha=0.8)
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(available, fontsize=9)
        ax3.set_ylabel("Mean Value")
        ax3.set_title("Average Molecular Properties")

    # Panel 4: Score components (bottom full width)
    ax4 = fig.add_subplot(gs[2, :])
    score_cols = [c for c in ["mpo", "docking", "syba", "sa"] if c in mcts_df.columns]
    if score_cols:
        n_mols = min(10, len(mcts_df))
        top_n = mcts_df[score_cols].head(n_mols).reset_index(drop=True)
        top_n.plot(kind="bar", ax=ax4, colormap="viridis", alpha=0.8, edgecolor="white")
        ax4.set_xlabel("Molecule Rank")
        ax4.set_ylabel("Score")
        ax4.set_title(f"Score Components — Top {n_mols} Molecules")
        ax4.legend(fontsize=8)
        ax4.set_xticklabels(range(1, n_mols + 1))

    # Panel 5: QMC (if available)
    if qmc_data and n_panels > 3:
        ax5 = fig.add_subplot(gs[3, :])
        correlations = qmc_data.get("correlations", [])
        if correlations:
            names = [c["descriptor"][:15] for c in correlations]
            pearson = [c["pearson_r"] for c in correlations]
            colors = [PALETTE["negative"] if v < 0 else PALETTE["positive"] for v in pearson]
            ax5.barh(names, pearson, color=colors, edgecolor="white", alpha=0.8)
            ax5.axvline(0, color="black", linewidth=0.5)
            ax5.set_xlabel("Pearson r")
            ax5.set_title("QMC Energy — Descriptor Correlations")
            ax5.invert_yaxis()

    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
        logger.info("Dashboard saved: %s", output_path)
        return output_path

    return None


# ═══════════════════════════════════════════════════════════════════════
#  6. Main entry point
# ═══════════════════════════════════════════════════════════════════════


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P4 — Results visualization dashboard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mcts-csv", type=Path,
                        default=Path("results/mcts/p4_mcts_merged_ranked.csv"),
                        help="Merged MCTS results CSV")
    parser.add_argument("--qmc-dir", type=Path, default=None,
                        help="QMC input directory (optional, for QMC plots)")
    parser.add_argument("--qmc-results", type=Path, default=None,
                        help="QMC analysis results JSON (optional)")
    parser.add_argument("--output-dir", type=Path, default=Path("figures"),
                        help="Output directory for figures")
    parser.add_argument("--dashboard", action="store_true",
                        help="Generate comprehensive dashboard figure")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    _setup_style()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load MCTS results
    mcts_df = None
    fragment_data: dict[str, int] = {}
    properties_df = pd.DataFrame()

    if args.mcts_csv and args.mcts_csv.exists() and _HAS_PANDAS:
        mcts_df = pd.read_csv(args.mcts_csv)
        logger.info("Loaded MCTS results: %d molecules", len(mcts_df))

        # Extract fragment usage from SMILES
        if _HAS_RDKIT and "best_state" in mcts_df.columns:
            properties_df = compute_molecular_properties(mcts_df["best_state"].tolist())
            logger.info("Computed properties for %d molecules", len(properties_df))

            # Estimate fragment usage from SMILES features (heuristic)
            for smi in mcts_df["best_state"]:
                mol = Chem.MolFromSmiles(smi)
                if mol:
                    for atom in mol.GetAtoms():
                        if atom.GetSymbol() == "O" and not atom.IsInRing():
                            fragment_data["Hydroxyl/Methoxy"] = fragment_data.get("Hydroxyl/Methoxy", 0) + 1
                        elif atom.GetSymbol() == "N" and not atom.IsInRing():
                            fragment_data["Amine/Amide"] = fragment_data.get("Amine/Amide", 0) + 1
                        elif atom.GetSymbol() == "F":
                            fragment_data["Fluorine"] = fragment_data.get("Fluorine", 0) + 1
                        elif atom.GetSymbol() == "Cl":
                            fragment_data["Chlorine"] = fragment_data.get("Chlorine", 0) + 1
            # Ring counts
            n_ring_mols = sum(1 for smi in mcts_df["best_state"]
                              if Chem.MolFromSmiles(smi)
                              and Chem.MolFromSmiles(smi).GetRingInfo().NumRings() > 0)
            fragment_data["Ring-containing"] = n_ring_mols

        logger.info("Fragment usage: %d categories", len(fragment_data))
    else:
        logger.warning("MCTS CSV not found: %s", args.mcts_csv)

    # Load QMC results
    qmc_data = None
    if args.qmc_results and args.qmc_results.exists():
        try:
            qmc_data = json.loads(args.qmc_results.read_text(encoding="utf-8"))
            logger.info("Loaded QMC results: %d molecules", qmc_data.get("n_molecules", 0))
        except Exception as exc:
            logger.warning("Failed to load QMC results: %s", exc)

    # Generate individual plots
    generated = []

    if mcts_df is not None:
        traj_path = args.output_dir / "mcts_trajectory.png"
        if plot_mcts_trajectory(mcts_df, traj_path):
            generated.append(traj_path)

        heat_path = args.output_dir / "score_heatmap.png"
        if plot_score_heatmap(mcts_df, heat_path):
            generated.append(heat_path)

    if fragment_data:
        frag_path = args.output_dir / "fragment_usage.png"
        if plot_fragment_usage(fragment_data, frag_path):
            generated.append(frag_path)

    if not properties_df.empty:
        radar_path = args.output_dir / "property_radar.png"
        if plot_property_radar(properties_df, radar_path, top_n=5):
            generated.append(radar_path)

        corr_path = args.output_dir / "property_correlation.png"
        if plot_property_correlation(properties_df, corr_path):
            generated.append(corr_path)

    # Dashboard
    if args.dashboard and mcts_df is not None:
        dash_path = args.output_dir / "p4_dashboard.png"
        if plot_dashboard(mcts_df if mcts_df is not None else pd.DataFrame(),
                          properties_df, fragment_data, qmc_data, dash_path):
            generated.append(dash_path)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  P4 Visualization Complete")
    print(f"  {'=' * 60}")
    if generated:
        for p in generated:
            size = p.stat().st_size / 1024 if p.exists() else 0
            print(f"  ✅ {p.name} ({size:.0f} KB)")
    else:
        print(f"  ❌ No plots generated — check input files")
    print(f"  Output directory: {args.output_dir.resolve()}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
