#!/usr/bin/env python3
"""
generate_toc_graphic.py — Generate a dedicated TOC (Table of Contents)
graphic for the P2 JCIM manuscript.

The graphic summarises the paper's pipeline:
    African NP compounds ──> MD validation (30,000 ns, 220 systems)
    ──> RRS / ACSI / PNS metrics ──> Resistance classification (A*–D)

Output: PDF (and PNG) saved to manuscript/LaTeX/Graphics/
"""

import os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# ── Colour palette (Wong 2011, Nature Methods – colorblind-safe) ────────────
BLUE   = '#0072B2'
ORANGE = '#D55E00'
GREEN  = '#009E73'
PINK   = '#CC79A7'
YELLOW = '#F0E442'
SKY    = '#56B4E9'
RED    = '#D55E00'
GREY   = '#999999'
WHITE  = '#FFFFFF'
OFF_WHITE = '#F2F2F2'
DARK   = '#333333'
LIGHT_BLUE = '#DAE8FC'
LIGHT_GREEN = '#D5E8D4'
LIGHT_ORANGE = '#FFE6CC'
LIGHT_PINK = '#F8CECC'

# ── Matplotlib configuration ───────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif'],
    'font.size': 9,
    'axes.unicode_minus': False,
})

# ── Output paths ────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "manuscript" / "LaTeX" / "Graphics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Figure setup ────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(10, 5.5))
ax.set_xlim(0, 14)
ax.set_ylim(0, 5)
ax.axis('off')
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# ── Helper functions ────────────────────────────────────────────────────────

def draw_box(ax, x, y, w, h, facecolor, edgecolor=DARK, linewidth=1.5,
             alpha=0.95, text='', fontsize=9, fontweight='bold',
             text_color=DARK, ha='center', va='center',
             corner_radius=0.15):
    """Draw a rounded rectangle with text."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={corner_radius}",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth,
        alpha=alpha, zorder=2
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, fontsize=fontsize, fontweight=fontweight,
            color=text_color, ha=ha, va=va, zorder=3)


def draw_arrow(ax, x1, y1, x2, y2, color=DARK, linewidth=2.0,
               arrowstyle='->', connectionstyle='arc3,rad=0.0'):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=arrowstyle, color=color,
                                linewidth=linewidth,
                                connectionstyle=connectionstyle),
                zorder=1)


def draw_symbol(ax, x, y, symbol, fontsize=22, color=DARK):
    """Draw a Unicode geometric symbol (reliable in PDF)."""
    ax.text(x, y, symbol, fontsize=fontsize, color=color,
            ha='center', va='center', zorder=3, fontweight='bold')


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 1: INPUT — Compound library  (left)
# ══════════════════════════════════════════════════════════════════════════════

# Background panel label
ax.text(0.5, 4.6, '① African NP Library', fontsize=11, fontweight='bold',
        color=DARK, ha='center', va='center')

# Box 1: 396 NPs
draw_box(ax, 0.2, 3.3, 2.6, 0.8, LIGHT_GREEN, text='396 African NPs\n+ 454 Drugs',
         fontsize=8, fontweight='normal')

# Arrow
draw_arrow(ax, 2.8, 3.7, 3.6, 3.7, color=BLUE, linewidth=2.5)

# Box 2: Generative expansion
draw_box(ax, 3.6, 3.3, 2.6, 0.8, LIGHT_BLUE, text='Generative Expansion\n65,856 compounds',
         fontsize=8, fontweight='normal')

# Arrow
draw_arrow(ax, 6.2, 3.7, 7.0, 3.7, color=BLUE, linewidth=2.5)

# Box 3: MPO scoring & selection
draw_box(ax, 7.0, 3.3, 2.6, 0.8, LIGHT_ORANGE, text='MPO Scoring\nTop 20 candidates',
         fontsize=8, fontweight='normal')

# Small icon for compounds
draw_symbol(ax, 1.5, 2.6, '◆', fontsize=18, color=GREEN)
draw_symbol(ax, 4.9, 2.6, '●', fontsize=18, color=BLUE)
draw_symbol(ax, 8.3, 2.6, '★', fontsize=18, color=ORANGE)

# ══════════════════════════════════════════════════════════════════════════════
# PANEL 2: MD VALIDATION (center)
# ══════════════════════════════════════════════════════════════════════════════

# Background panel label
ax.text(4.5, 1.9, '② MD Validation Pipeline', fontsize=11, fontweight='bold',
        color=DARK, ha='center', va='center')

# Main arrow from top section to bottom
draw_arrow(ax, 8.3, 3.3, 8.3, 2.5, color=DARK, linewidth=2.5,
           connectionstyle='arc3,rad=-0.2')

# Box: MD simulations
draw_box(ax, 2.5, 0.8, 3.0, 1.0, LIGHT_BLUE,
         text='MD Simulations\n30,000 ns • 220 systems\n4 targets × 6 mutants',
         fontsize=7.5, fontweight='normal', corner_radius=0.12)

# Box: MM-GBSA + MC
draw_box(ax, 6.0, 0.8, 2.8, 1.0, LIGHT_ORANGE,
         text='MM-GBSA\n+ MC Sampling\nBinding free energies',
         fontsize=7.5, fontweight='normal', corner_radius=0.12)

# Arrow between MD and MM-GBSA
draw_arrow(ax, 5.5, 1.3, 6.0, 1.3, color=BLUE, linewidth=2.0)

# Box: Trajectory analysis
draw_box(ax, 9.3, 0.8, 2.8, 1.0, LIGHT_PINK,
         text='Trajectory Analysis\nRMSD • RMSF • H-bonds\nStability metrics',
         fontsize=7.5, fontweight='normal', corner_radius=0.12)

# Arrow from MM-GBSA to Trajectory
draw_arrow(ax, 8.8, 1.3, 9.3, 1.3, color=BLUE, linewidth=2.0)

# Small icon for MD
draw_symbol(ax, 4.0, 0.4, '▶', fontsize=16, color=BLUE)
draw_symbol(ax, 7.4, 0.4, '◆', fontsize=16, color=ORANGE)
draw_symbol(ax, 10.7, 0.4, '▲', fontsize=16, color=PINK)

# ══════════════════════════════════════════════════════════════════════════════
# TIMELINE / METRICS (right)
# ══════════════════════════════════════════════════════════════════════════════

# Large arrow pointing right to the metrics
draw_arrow(ax, 12.0, 1.3, 12.8, 1.3, color=ORANGE, linewidth=3.0,
           arrowstyle='->')

# ── Metrics panel ──
metrics_x = 12.8

# RRS box
draw_box(ax, metrics_x, 3.0, 1.0, 0.6, ORANGE,
         text='RRS', fontsize=9, fontweight='bold', text_color=WHITE,
         corner_radius=0.08)
ax.text(metrics_x + 0.5, 2.5, 'Resistance\nResilience', fontsize=6,
        color=DARK, ha='center', va='center', fontweight='normal',
        style='italic')

# ACSI box
draw_box(ax, metrics_x, 2.0, 1.0, 0.6, GREEN,
         text='ACSI', fontsize=9, fontweight='bold', text_color=WHITE,
         corner_radius=0.08)
ax.text(metrics_x + 0.5, 1.5, 'African NP\nLikeness', fontsize=6,
        color=DARK, ha='center', va='center', fontweight='normal',
        style='italic')

# PNS box
draw_box(ax, metrics_x, 1.0, 1.0, 0.6, PINK,
         text='PNS', fontsize=9, fontweight='bold', text_color=WHITE,
         corner_radius=0.08)
ax.text(metrics_x + 0.5, 0.5, 'Polypharm.\nNetwork', fontsize=6,
        color=DARK, ha='center', va='center', fontweight='normal',
        style='italic')

# ══════════════════════════════════════════════════════════════════════════════
# RESULT: Classification (far right)
# ══════════════════════════════════════════════════════════════════════════════

# Big arrow from metrics to classification
draw_arrow(ax, metrics_x + 0.5, 2.0, metrics_x + 1.3, 2.0,
           color=ORANGE, linewidth=2.5, arrowstyle='->')

classif_x = metrics_x + 1.3

ax.text(classif_x + 0.5, 4.2, '③ Classification', fontsize=10,
        fontweight='bold', color=DARK, ha='center', va='center')

classes = [
    ('A*', 'Pan-resilient\nHigh potency', LIGHT_GREEN, GREEN),
    ('A',  'Pan-resilient',              LIGHT_GREEN, GREEN),
    ('B',  'Partially\nresilient',       LIGHT_BLUE,  BLUE),
    ('C',  'Mutant-\nspecific',          LIGHT_ORANGE, ORANGE),
    ('D',  'Resistance-\nvulnerable',    LIGHT_PINK,   RED),
]

for i, (label, desc, bg, fg) in enumerate(classes):
    y_pos = 3.4 - i * 0.55
    # Class letter badge
    badge = FancyBboxPatch(
        (classif_x - 0.05, y_pos), 0.45, 0.4,
        boxstyle=f"round,pad=0,rounding_size=0.08",
        facecolor=fg, edgecolor=fg, linewidth=1.5, zorder=2
    )
    ax.add_patch(badge)
    ax.text(classif_x + 0.175, y_pos + 0.2, label, fontsize=10,
            fontweight='bold', color=WHITE, ha='center', va='center', zorder=3)

    # Description
    ax.text(classif_x + 0.6, y_pos + 0.2, desc, fontsize=7,
            color=DARK, ha='left', va='center', fontweight='normal')

# ══════════════════════════════════════════════════════════════════════════════
# Title at top
# ══════════════════════════════════════════════════════════════════════════════

ax.text(0.5, 4.85, 'Resistance-Resilient Antimalarial Leads from African NP Space',
        fontsize=13, fontweight='bold', color=DARK, ha='left', va='center')
ax.text(0.5, 4.65, 'MD Validation Against Resistance Mutants',
        fontsize=10, fontweight='normal', color=GREY, ha='left', va='center',
        style='italic')

# ── Save ────────────────────────────────────────────────────────────────────
fig.savefig(OUTPUT_DIR / 'TOC_graphic.pdf', dpi=400,
            bbox_inches='tight', pad_inches=0.1, facecolor='white')
fig.savefig(OUTPUT_DIR / 'TOC_graphic.png', dpi=300,
            bbox_inches='tight', pad_inches=0.1, facecolor='white')

plt.close(fig)
print(f"✅ TOC graphic saved to {OUTPUT_DIR}")
print(f"   • {OUTPUT_DIR / 'TOC_graphic.pdf'}")
print(f"   • {OUTPUT_DIR / 'TOC_graphic.png'}")
