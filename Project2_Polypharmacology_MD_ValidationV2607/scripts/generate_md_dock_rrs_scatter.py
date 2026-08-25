#!/usr/bin/env python3
"""generate_md_dock_rrs_scatter.py — Set-C pilot RRS comparison figure.

Plots the trajectory-derived RRS estimates (MD-RRS from mean-minimum-distance
geometry and MM-GBSA RRS from binding free energies) against the
docking-derived RRS for the 16-system Set-C MD pilot (PP-01 and PP-02 against
the six-mutant panel). Both panels use the same mutant/WT ratio convention
(WT = 100; <100 = predicted looser/weaker mutant binding).

Panel (a): MD-RRS vs docking RRS (8 systems with both values).
Panel (b): MM-GBSA RRS vs docking RRS (8 systems; PP-02 PfDHFR has no docking
           WT reference and is shown on the MM-GBSA axis only).

Points are coloured by target (PfCRT / PfDHFR) and shaped by candidate
(PP-01 / PP-02). The dashed diagonal is y = x (perfect agreement) and the
solid vertical/horizontal reference marks WT = 100.

Outputs:
  manuscript/LaTeX/Graphics/p2_setc_rrs_scatter.pdf   (main-manuscript copy)
  manuscript/LaTeX/Graphics/p2_setc_rrs_scatter.pdf   (SI copy; same canonical graphics directory)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

try:
    import scienceplots  # noqa: F401 — registers 'science' style
    SCIENCE_STYLE = ['science', 'no-latex', 'grid', 'high-vis']
except ImportError:
    SCIENCE_STYLE = ['seaborn-v0_8-whitegrid']

# Colorblind-safe palette (Wong 2011, Nature Methods)
COLOR_PFCRT = '#0072B2'   # blue
COLOR_PFDHFR = '#D55E00'  # vermillion
MARKER_PP01 = 'o'
MARKER_PP02 = 's'

BASE = Path(__file__).resolve().parent.parent
MD_DOCK_CSV = BASE / 'results' / 'set_c_md' / 'md_vs_docking_comparison_pilot.csv'
MMGBSA_CSV = BASE / 'results' / 'set_c_md' / 'mmgbsa_summary_pilot.csv'
OUT_MAIN = BASE / 'manuscript' / 'LaTeX' / 'Graphics' / 'p2_setc_rrs_scatter.pdf'
OUT_SI = BASE / 'manuscript' / 'LaTeX' / 'Graphics' / 'p2_setc_rrs_scatter.pdf'


def load_md_dock() -> pd.DataFrame:
    """Load MD-RRS vs docking RRS comparison (12 mutant rows)."""
    df = pd.read_csv(MD_DOCK_CSV)
    df['label'] = df['target'] + ' ' + df['mutation']
    return df


def load_mmgbsa() -> pd.DataFrame:
    """Load MM-GBSA summary and merge docking RRS; keep mutant rows."""
    df = pd.read_csv(MMGBSA_CSV)
    df = df[df['mutation'] != 'WT'].copy()
    df['label'] = df['target'] + ' ' + df['mutation']
    # dock_RRS lives in md_vs_docking_comparison_pilot.csv
    dock = pd.read_csv(MD_DOCK_CSV)[['set_c_id', 'target', 'mutation', 'dock_RRS']]
    df = df.merge(dock, on=['set_c_id', 'target', 'mutation'], how='left',
                  suffixes=('', '_dock'))
    df['dock_RRS'] = df['dock_RRS_dock'].fillna(df['dock_RRS'])
    return df


def _scatter(ax, x, y, df, xlabel: str, ylabel: str, title: str,
             show_x_only: bool = False) -> None:
    """Shared scatter styling: y=x line, WT=100 guides, per-target colours."""
    ax.axhline(100.0, color='0.75', linewidth=0.8, zorder=1)
    ax.axvline(100.0, color='0.75', linewidth=0.8, zorder=1)
    lims = [min(ax.get_xlim()[0], ax.get_ylim()[0]),
            max(ax.get_xlim()[1], ax.get_ylim()[1])]
    ax.plot(lims, lims, '--', color='0.35', linewidth=0.9, zorder=1,
            label='y = x')

    for _, row in df.iterrows():
        color = COLOR_PFCRT if row['target'] == 'PfCRT' else COLOR_PFDHFR
        marker = MARKER_PP01 if row['set_c_id'] == 'PP-01' else MARKER_PP02
        if pd.notna(row[x]):
            ax.scatter(row[x], row[y], s=70, color=color, marker=marker,
                       edgecolor='black', linewidth=0.5, zorder=3)
        elif show_x_only and pd.notna(row[y]):
            # No docking WT reference (PP-02 PfDHFR): place on axis edge only
            ax.scatter(84.0, row[y], s=70, color=color, marker=marker,
                       edgecolor='black', linewidth=0.5, zorder=3, alpha=0.55)
            ax.annotate(row['label'], xy=(84.0, row[y]),
                        xytext=(84.0, row[y] + 2.5), fontsize=6,
                        ha='center', color=color)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=9)
    ax.set_xlim(80, 128)
    ax.set_ylim(70, 130)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-main', type=Path, default=OUT_MAIN)
    ap.add_argument('--output-si', type=Path, default=OUT_SI)
    args = ap.parse_args()

    if not MD_DOCK_CSV.is_file():
        print(f'ERROR: {MD_DOCK_CSV} not found', file=sys.stderr)
        return 1
    if not MMGBSA_CSV.is_file():
        print(f'ERROR: {MMGBSA_CSV} not found', file=sys.stderr)
        return 1

    md_df = load_md_dock()
    mm_df = load_mmgbsa()

    with plt.style.context(SCIENCE_STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))

        _scatter(axes[0], 'dock_RRS', 'MD_RRS_mean_min_dist_A', md_df,
                 xlabel='Docking RRS', ylabel='MD-RRS',
                 title='(a) Trajectory MD-RRS vs docking RRS',
                 show_x_only=False)
        _scatter(axes[1], 'dock_RRS', 'mmgbsa_rrs', mm_df,
                 xlabel='Docking RRS', ylabel='MM-GBSA RRS',
                 title='(b) MM-GBSA RRS vs docking RRS',
                 show_x_only=True)

        handles = [
            plt.Line2D([], [], marker='o', color='none', markerfacecolor=COLOR_PFCRT,
                       markeredgecolor='black', label='PfCRT (6UKJ)'),
            plt.Line2D([], [], marker='o', color='none', markerfacecolor=COLOR_PFDHFR,
                       markeredgecolor='black', label='PfDHFR (7F3Y)'),
            plt.Line2D([], [], marker='o', color='none', markerfacecolor='0.55',
                       markeredgecolor='black', label='PP-01'),
            plt.Line2D([], [], marker='s', color='none', markerfacecolor='0.55',
                       markeredgecolor='black', label='PP-02'),
            plt.Line2D([], [], linestyle='--', color='0.35', label='y = x'),
        ]
        fig.legend(handles=handles, loc='upper center', ncol=5,
                   frameon=False, fontsize=7, bbox_to_anchor=(0.5, 1.02))

        fig.tight_layout(rect=(0, 0, 1, 0.94))
        for out in (args.output_main, args.output_si):
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out, dpi=300, bbox_inches='tight')
            print(f'Generated: {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
