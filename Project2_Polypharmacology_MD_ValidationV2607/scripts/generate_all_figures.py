#!/usr/bin/env python3
"""
generate_all_figures.py — Generate all 7 main text figures for Paper 2
Run after MD simulations and analysis are complete.

Figures:
  F1: ACSI distribution for 65,856-molecule library
  F2: P. falciparum PPI network with target highlighting
  F3: Representative RMSD trajectories (stable vs unstable)
  F4: H-bond occupancy heatmap for key residues
  F5: MC binding free energy landscapes
  F6: MC pose clustering
  F7: Cross-metric correlation matrix (RRS, ACSI, PNS, MM-GBSA)

Usage:
  python scripts/generate_all_figures.py [--data-dir results/] [--output-dir results/figures/]
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401 — registers styles
from matplotlib.patches import Patch
import pandas as pd

# SciencePlots context: 'science' base + 'no-latex' for systems without TeX
# 'grid' adds light gridlines; 'high-vis' boosts contrast for PDF output
SCIENCE_STYLE = ['science', 'no-latex', 'grid', 'high-vis']

# Colorblind-safe palette (Wong 2011, Nature Methods)
COLORS_CB = ['#0072B2', '#D55E00', '#009E73', '#CC79A7',
             '#F0E442', '#56B4E9', '#E69F00', '#999999']


def figure1_acsi_distribution(data_dir: Path, output_dir: Path):
    """F1: ACSI distribution for 65,856-molecule library."""
    csv_path = data_dir / "metrics" / "acsi_scores.csv"
    if not csv_path.exists():
        print(f"  [SKIP] F1: {csv_path} not found")
        return

    df = pd.read_csv(csv_path)
    acsi = df["acsi"]

    with plt.style.context(SCIENCE_STYLE):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(acsi, bins=50, color=COLORS_CB[0], edgecolor='white',
                linewidth=0.5, alpha=0.85)
        mean_val = acsi.mean()
        ax.axvline(x=mean_val, color=COLORS_CB[1], linestyle='--',
                   linewidth=1.5, label=f'Mean = {mean_val:.3f}')
        ax.set_xlabel('ACSI Score')
        ax.set_ylabel('Count')
        ax.set_title('African Chemical Space Index Distribution ($n$ = 65,856)')
        ax.legend(frameon=True, fancybox=False)
        fig.savefig(output_dir / 'figure1_acsi_distribution.pdf',
                    dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / 'figure1_acsi_distribution.png',
                    dpi=300, bbox_inches='tight')
        plt.close(fig)
    print("  [OK] F1: ACSI distribution")


def figure2_ppi_network(data_dir: Path, output_dir: Path):
    """F2: P. falciparum PPI network with target highlighting."""
    try:
        import networkx as nx
    except ImportError:
        print("  [SKIP] F2: networkx not installed")
        return

    ppi_path = data_dir / "metrics" / "ppi_network.csv"
    if not ppi_path.exists():
        print(f"  [SKIP] F2: {ppi_path} not found")
        return

    df = pd.read_csv(ppi_path)
    G = nx.from_pandas_edgelist(df, "node1", "node2", edge_attr="confidence")

    targets = ["PfDHFR", "PfCRT", "PfATP4", "PfClpP"]
    node_colors = [COLORS_CB[1] if n in targets else COLORS_CB[5] for n in G.nodes()]
    node_sizes = [400 if n in targets else 40 for n in G.nodes()]

    with plt.style.context(SCIENCE_STYLE):
        fig, ax = plt.subplots(figsize=(12, 10))
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
        nx.draw_networkx_edges(G, pos, alpha=0.15, width=0.5, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                               edgecolors='white', linewidths=0.5, ax=ax)
        nx.draw_networkx_labels(G, pos, labels={n: n for n in targets},
                                font_size=10, font_weight='bold', ax=ax)
        ax.set_title('P. falciparum PPI Network (STRING, confidence \u2265 0.7)')
        ax.axis('off')
        legend_elements = [
            Patch(facecolor=COLORS_CB[1], label='Drug target'),
            Patch(facecolor=COLORS_CB[5], label='Other protein'),
        ]
        ax.legend(handles=legend_elements, loc='lower left', frameon=True,
                  fancybox=False)
        fig.savefig(output_dir / 'figure2_ppi_network.pdf',
                    dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / 'figure2_ppi_network.png',
                    dpi=300, bbox_inches='tight')
        plt.close(fig)
    print("  [OK] F2: PPI network")


def figure3_rmsd_stability(data_dir: Path, output_dir: Path):
    """F3: Representative RMSD trajectories (stable vs unstable)."""
    rmsd_dir = data_dir / "analysis" / "rmsd"
    if not rmsd_dir.exists():
        print(f"  [SKIP] F3: {rmsd_dir} not found")
        return

    with plt.style.context(SCIENCE_STYLE):
        fig, ax = plt.subplots(figsize=(10, 6))
        plotted = 0

        for i, rmsd_file in enumerate(sorted(rmsd_dir.glob("*.csv"))[:10]):
            df = pd.read_csv(rmsd_file)
            if "time_ns" in df.columns and "backbone_rmsd_nm" in df.columns:
                ax.plot(df["time_ns"], df["backbone_rmsd_nm"],
                        color=COLORS_CB[i % len(COLORS_CB)], linewidth=1.2,
                        label=rmsd_file.stem.replace("_rmsd", ""))
                plotted += 1

        if plotted == 0:
            plt.close(fig)
            print("  [SKIP] F3: no RMSD CSV files with expected columns")
            return

        ax.axhline(y=0.30, color=COLORS_CB[1], linestyle='--',
                   linewidth=1.5, alpha=0.7, label='Stability threshold (0.30 nm)')
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('Backbone RMSD (nm)')
        ax.set_title('Representative RMSD Trajectories')
        ax.legend(fontsize=8, ncol=2, frameon=True, fancybox=False)
        ax.set_ylim(bottom=0)
        fig.savefig(output_dir / 'figure3_rmsd_stability.pdf',
                    dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / 'figure3_rmsd_stability.png',
                    dpi=300, bbox_inches='tight')
        plt.close(fig)
    print("  [OK] F3: RMSD stability")


def figure4_hbond_heatmap(data_dir: Path, output_dir: Path):
    """F4: H-bond occupancy heatmap for key residues."""
    hbond_path = data_dir / "analysis" / "hbond_occupancy.csv"
    if not hbond_path.exists():
        print(f"  [SKIP] F4: {hbond_path} not found")
        return

    df = pd.read_csv(hbond_path, index_col=0)
    if df.empty:
        print("  [SKIP] F4: hbond_occupancy.csv is empty")
        return

    with plt.style.context(SCIENCE_STYLE):
        fig, ax = plt.subplots(figsize=(14, 8))
        im = ax.imshow(df.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(df.columns, rotation=45, ha='right', fontsize=9)
        ax.set_yticks(range(len(df.index)))
        ax.set_yticklabels(df.index, fontsize=9)
        ax.set_title('H-bond Occupancy (%) for Key Binding Site Residues')
        cbar = fig.colorbar(im, ax=ax, label='Occupancy (%)')
        cbar.ax.tick_params(labelsize=9)
        fig.savefig(output_dir / 'figure4_hbond_heatmap.pdf',
                    dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / 'figure4_hbond_heatmap.png',
                    dpi=300, bbox_inches='tight')
        plt.close(fig)
    print("  [OK] F4: H-bond heatmap")


def figure5_mc_landscapes(data_dir: Path, output_dir: Path):
    """F5: MC binding free energy landscapes."""
    mc_path = data_dir / "metrics" / "mc_energies.csv"
    if not mc_path.exists():
        print(f"  [SKIP] F5: {mc_path} not found")
        return

    df = pd.read_csv(mc_path)
    if df.empty:
        print("  [SKIP] F5: mc_energies.csv is empty")
        return

    with plt.style.context(SCIENCE_STYLE):
        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        ligands = df["ligand"].unique()[:6]

        for idx, ligand in enumerate(ligands):
            ax = axes[idx // 3, idx % 3]
            lig_data = df[df["ligand"] == ligand]
            ax.hist(lig_data["energy_kcal"], bins=30, color=COLORS_CB[0],
                    edgecolor='white', linewidth=0.5, alpha=0.85)
            ax.set_title(f'Ligand {ligand}')
            ax.set_xlabel(r'$\Delta G$ (kcal/mol)')
            ax.set_ylabel('Count')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        fig.suptitle('MC Binding Free Energy Landscapes', fontsize=14, y=1.02)
        fig.tight_layout()
        fig.savefig(output_dir / 'figure5_mc_landscapes.pdf',
                    dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / 'figure5_mc_landscapes.png',
                    dpi=300, bbox_inches='tight')
        plt.close(fig)
    print("  [OK] F5: MC landscapes")


def figure6_mc_poses(data_dir: Path, output_dir: Path):
    """F6: MC pose clustering."""
    cluster_path = data_dir / "metrics" / "mc_pose_clusters.csv"
    if not cluster_path.exists():
        print(f"  [SKIP] F6: {cluster_path} not found")
        return

    df = pd.read_csv(cluster_path)
    if df.empty:
        print("  [SKIP] F6: mc_pose_clusters.csv is empty")
        return

    with plt.style.context(SCIENCE_STYLE):
        fig, ax = plt.subplots(figsize=(8, 6))
        clusters = sorted(df["cluster"].unique())
        for ci, cluster in enumerate(clusters):
            cdata = df[df["cluster"] == cluster]
            label = f'Cluster {cluster}' if cluster >= 0 else 'Noise'
            marker = 'o' if cluster >= 0 else 'x'
            ax.scatter(cdata["rmsd_x"], cdata["rmsd_y"], label=label,
                       color=COLORS_CB[ci % len(COLORS_CB)], marker=marker,
                       s=35, edgecolors='white', linewidths=0.3)

        ax.set_xlabel('RMSD PC1 (\u00C5)')
        ax.set_ylabel('RMSD PC2 (\u00C5)')
        ax.set_title('MC Pose Clustering (DBSCAN, \u03b5 = 2.0 \u00C5)')
        ax.legend(frameon=True, fancybox=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig(output_dir / 'figure6_mc_poses.pdf',
                    dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / 'figure6_mc_poses.png',
                    dpi=300, bbox_inches='tight')
        plt.close(fig)
    print("  [OK] F6: MC pose clusters")


def figure7_crossmetric(data_dir: Path, output_dir: Path):
    """F7: Cross-metric correlation matrix (RRS, ACSI, PNS, MM-GBSA)."""
    metrics_path = data_dir / "metrics" / "cross_metric_matrix.csv"
    if not metrics_path.exists():
        print(f"  [SKIP] F7: {metrics_path} not found")
        return

    df = pd.read_csv(metrics_path, index_col=0)
    if df.empty:
        print("  [SKIP] F7: cross_metric_matrix.csv is empty")
        return

    with plt.style.context(SCIENCE_STYLE):
        fig, ax = plt.subplots(figsize=(8, 7))
        im = ax.imshow(df.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(df.columns, rotation=45, ha='right')
        ax.set_yticks(range(len(df.index)))
        ax.set_yticklabels(df.index)

        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                val = df.values[i, j]
                ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                        fontsize=10, color='white' if abs(val) > 0.5 else 'black')

        ax.set_title('Cross-Metric Spearman Correlations')
        cbar = fig.colorbar(im, ax=ax, label=r'Spearman $\rho$')
        cbar.ax.tick_params(labelsize=9)
        fig.savefig(output_dir / 'figure7_crossmetric.pdf',
                    dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / 'figure7_crossmetric.png',
                    dpi=300, bbox_inches='tight')
        plt.close(fig)
    print("  [OK] F7: Cross-metric correlation")


def main():
    parser = argparse.ArgumentParser(description="Generate all 7 main text figures")
    parser.add_argument("--data-dir", type=Path, default=Path("results"),
                        help="Directory containing analysis results")
    parser.add_argument("--output-dir", type=Path, default=Path("results/figures"),
                        help="Directory to save figures")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating Paper 2 figures (SciencePlots styling)...")
    print(f"  Data dir: {args.data_dir}")
    print(f"  Output dir: {args.output_dir}")
    print()

    figure1_acsi_distribution(args.data_dir, args.output_dir)
    figure2_ppi_network(args.data_dir, args.output_dir)
    figure3_rmsd_stability(args.data_dir, args.output_dir)
    figure4_hbond_heatmap(args.data_dir, args.output_dir)
    figure5_mc_landscapes(args.data_dir, args.output_dir)
    figure6_mc_poses(args.data_dir, args.output_dir)
    figure7_crossmetric(args.data_dir, args.output_dir)

    print()
    print("Done. Figures saved to", args.output_dir)


if __name__ == "__main__":
    main()
