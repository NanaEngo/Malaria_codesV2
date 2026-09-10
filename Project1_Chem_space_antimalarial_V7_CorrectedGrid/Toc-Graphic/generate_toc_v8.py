#!/usr/bin/env python3
"""
Generate an improved ACS-compliant TOC graphic for P1 V8.

This script produces a publication-ready TOC graphic that includes:
  - Visual chemical structure of PP-15 (top candidate)
  - Schematic 4-target panel with protein type labels
  - Color-coded RRS classification output (A*/B/C)
  - Proper funnel narrative

ACS JCIM specifications:
  - 3.25 in × 1.75 in, landscape
  - ≥ 300 dpi (1200 dpi for the high-res version)
  - TIFF RGB LZW + PDF vector
  - White background, no alpha channel

Usage:
  conda run -n malaria_md python generate_toc_v8.py
  # or:
  python generate_toc_v8.py

Outputs (in this folder):
  p1_v8_toc_graphic.pdf
  p1_v8_toc_graphic_ACS.tiff         (300 dpi)
  p1_v8_toc_graphic_ACS_1200dpi.tiff (1200 dpi)
"""
from __future__ import annotations
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# RDKit for the PP-15 structure
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem.Draw import rdMolDraw2D
    import numpy as np
    RDKIT_OK = True
except ImportError:
    RDKIT_OK = False
    print("Warning: RDKit not available — structure panel will be text-only.")

# PIL for TIFF export
try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False
    print("Warning: PIL not available — TIFF export will use matplotlib directly.")

# --------------------------------------------------------------------------
# Output directory (same as this script)
# --------------------------------------------------------------------------
OUT_DIR = Path(__file__).parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# ACS dimensions
# --------------------------------------------------------------------------
W_IN, H_IN = 3.25, 1.75
DPI_LOW  = 300
DPI_HIGH = 1200

# --------------------------------------------------------------------------
# Color palette (scientifically conservative, accessible)
# --------------------------------------------------------------------------
C_BG        = "#FFFFFF"
C_FUNNEL1   = "#C1440E"   # terracotta (African NP warm)
C_FUNNEL2   = "#D4A017"   # ochre
C_TARGET    = "#0D9488"   # teal
C_TARGET_BG = "#F0FDFA"   # very light teal
C_ASTAR_BG  = "#DCFCE7"   # light green
C_ASTAR_FG  = "#15803D"   # forest green
C_B_BG      = "#FEF9C3"   # light amber
C_B_FG      = "#B45309"   # dark amber
C_C_BG      = "#F1F5F9"   # light slate
C_C_FG      = "#475569"   # slate
C_TEXT      = "#0F172A"   # near-black
C_TEXT2     = "#334155"   # dark slate
C_ARROW     = "#64748B"   # mid-slate
C_BORDER    = "#CBD5E1"   # light border

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size":    6.5,
    "axes.edgecolor": C_TEXT,
    "axes.linewidth": 0.6,
})

# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------

def rounded_box(ax, x, y, w, h, title, body,
                fc=C_BG, ec=C_BORDER, tc=C_TEXT, bc=C_TEXT2,
                title_size=6.5, body_size=5.5, lw=0.7):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2,
    ))
    ax.text(x + w / 2, y + h - 0.048, title,
            ha="center", va="top",
            fontsize=title_size, fontweight="bold", color=tc, zorder=3)
    if body:
        ax.text(x + w / 2, y + 0.042, body,
                ha="center", va="bottom",
                fontsize=body_size, color=bc, zorder=3,
                linespacing=1.3, multialignment="center")


def draw_arrow(ax, x1, y1, x2, y2, color=C_ARROW, lw=1.0, mut=8):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="-|>", color=color,
                    lw=lw, mutation_scale=mut,
                ), zorder=4)


def embed_structure(ax, smiles, x, y, w, h, label="PP-15"):
    """Render a 2D chemical structure into a matplotlib axes region."""
    if not RDKIT_OK:
        ax.text(x + w / 2, y + h / 2, f"[{label}]",
                ha="center", va="center", fontsize=7,
                color=C_TARGET, fontweight="bold", zorder=3)
        return
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)
    # Render to PNG bytes
    px_w = int(w * W_IN * DPI_LOW)
    px_h = int(h * H_IN * DPI_LOW)
    drawer = rdMolDraw2D.MolDraw2DCairo(px_w, px_h)
    drawer.drawOptions().addStereoAnnotation = False
    drawer.drawOptions().padding = 0.12
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    from PIL import Image as PILImage
    bio = io.BytesIO(drawer.GetDrawingText())
    img = PILImage.open(bio).convert("RGBA")
    # Paste onto white
    bg = PILImage.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    img_rgb = bg.convert("RGB")
    # Convert to numpy for imshow
    img_np = np.array(img_rgb) / 255.0
    ax.imshow(img_np, extent=[x, x + w, y, y + h],
              aspect="auto", zorder=3, interpolation="lanczos")
    ax.text(x + w / 2, y + 0.018, label,
            ha="center", va="bottom", fontsize=5.2,
            color=C_TEXT, style="italic", zorder=5)


# --------------------------------------------------------------------------
# Main drawing
# --------------------------------------------------------------------------

def make_toc(dpi: int = DPI_LOW) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=dpi)
    fig.patch.set_facecolor(C_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.axis("off")

    # ------------------------------------------------------------------ #
    # PANEL 1 — Left: chemical space funnel (0.00–0.28)
    # ------------------------------------------------------------------ #
    # Header box: library source
    rounded_box(ax, 0.010, 0.695, 0.260, 0.270,
                "African NP + Synthetics",
                "396 + 454 seed molecules\n→ 65,856 hybrid library",
                fc="#FFF7ED", ec=C_FUNNEL1, tc=C_FUNNEL1, bc=C_TEXT2,
                title_size=6.0, body_size=5.2)

    # Funnel arrow
    # Draw a trapezoid funnel shape
    funnel_x = [0.070, 0.200, 0.175, 0.095]
    funnel_y = [0.695, 0.695, 0.530, 0.530]
    ax.fill(funnel_x, funnel_y, color=C_FUNNEL2, alpha=0.25, zorder=1)
    ax.plot(funnel_x + [funnel_x[0]], funnel_y + [funnel_y[0]],
            color=C_FUNNEL2, lw=0.7, zorder=2)
    ax.text(0.135, 0.615, "MPO + SA\nfilter",
            ha="center", va="center", fontsize=4.8,
            color=C_FUNNEL1, fontstyle="italic", zorder=3)

    # Middle: prioritized leads
    rounded_box(ax, 0.010, 0.400, 0.260, 0.120,
                "19,913 leads",
                "Synthesizable, Lipinski-compliant",
                fc="#FEF3C7", ec=C_FUNNEL2, tc=C_B_FG, bc=C_TEXT2,
                title_size=6.2, body_size=5.0)

    # Small arrow
    draw_arrow(ax, 0.135, 0.400, 0.135, 0.340, lw=0.9)

    # Bottom: Set C cohort
    rounded_box(ax, 0.010, 0.215, 0.260, 0.120,
                "17-member cohort",
                "Polypharmacology-oriented Set C",
                fc="#FFEDD5", ec=C_FUNNEL1, tc=C_FUNNEL1, bc=C_TEXT2,
                title_size=6.2, body_size=5.0)

    # ------------------------------------------------------------------ #
    # PANEL 2 — Center: 4-target docking (0.30–0.66)
    # ------------------------------------------------------------------ #
    # PP-15 structure (top center of panel)
    if RDKIT_OK and PIL_OK:
        embed_structure(
            ax,
            smiles="COc1c(O)cc2c(c1O)C(=O)C([C@H](O)c1ccccc1)CO2",
            x=0.295, y=0.500, w=0.175, h=0.465,
            label="PP-15 (top candidate)"
        )
    else:
        rounded_box(ax, 0.295, 0.500, 0.175, 0.465,
                    "PP-15", "flavanone-type\nscaffold",
                    fc=C_TARGET_BG, ec=C_TARGET, tc=C_TARGET)

    # Four target boxes (2×2 grid, lower center)
    targets = [
        ("PfDHFR", "Folate\nmetabolism", 0.310, 0.190),
        ("PfCRT",  "Resistance\ntransporter", 0.475, 0.190),
        ("PfClpP", "Protease\n(proteostasis)", 0.310, 0.055),
        ("PfATP4", "Ion ATPase\n(homeostasis)", 0.475, 0.055),
    ]
    for t_name, t_body, tx, ty in targets:
        rounded_box(ax, tx, ty, 0.155, 0.125,
                    t_name, t_body,
                    fc=C_TARGET_BG, ec=C_TARGET,
                    tc=C_TARGET, bc=C_TEXT2,
                    title_size=5.8, body_size=4.8, lw=0.8)

    # Arrows from Set C → structure (left panel to center)
    draw_arrow(ax, 0.270, 0.270, 0.295, 0.560, lw=0.9)

    # Arrows from structure to each target
    for _, _, tx, ty in targets:
        draw_arrow(ax, 0.382, 0.500, tx + 0.077, ty + 0.125,
                   color=C_TARGET, lw=0.7, mut=6)

    # "AutoDock Vina" label on arrows
    ax.text(0.425, 0.390, "AutoDock Vina\ndocking",
            ha="center", va="center", fontsize=4.5,
            color=C_TARGET, fontstyle="italic", zorder=5)

    # ------------------------------------------------------------------ #
    # PANEL 3 — Right: RRS classification (0.67–1.00)
    # ------------------------------------------------------------------ #
    # Title bar
    ax.add_patch(FancyBboxPatch(
        (0.675, 0.780), 0.315, 0.185,
        boxstyle="round,pad=0.015,rounding_size=0.03",
        linewidth=0.8, edgecolor=C_ASTAR_FG, facecolor=C_ASTAR_BG, zorder=2,
    ))
    ax.text(0.832, 0.950, "Resistance-Resilience Score",
            ha="center", va="top", fontsize=6.0,
            fontweight="bold", color=C_TEXT, zorder=3)
    ax.text(0.832, 0.880, "5 candidates: 4/4 targets + A*",
            ha="center", va="top", fontsize=5.5,
            color=C_ASTAR_FG, fontweight="bold", zorder=3)
    # Star symbol
    ax.text(0.832, 0.810, "★  PP-15, PP-05, PP-06, PP-11, PP-13",
            ha="center", va="top", fontsize=4.8,
            color=C_ASTAR_FG, zorder=3)

    # Class legend boxes
    classes = [
        ("A*  7 candidates", C_ASTAR_BG, C_ASTAR_FG, 0.590),
        ("B    4 candidates", C_B_BG,    C_B_FG,    0.455),
        ("C    6 candidates", C_C_BG,    C_C_FG,    0.320),
    ]
    for c_label, c_bg, c_fg, c_y in classes:
        ax.add_patch(FancyBboxPatch(
            (0.675, c_y), 0.315, 0.115,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            linewidth=0.7, edgecolor=c_fg, facecolor=c_bg, zorder=2,
        ))
        ax.text(0.832, c_y + 0.057, c_label,
                ha="center", va="center", fontsize=6.2,
                fontweight="bold", color=c_fg, zorder=3)

    # Arrows from target panel to RRS panel
    draw_arrow(ax, 0.665, 0.600, 0.672, 0.680, lw=0.9)

    # ------------------------------------------------------------------ #
    # Evidence boundary footnote (very small)
    # ------------------------------------------------------------------ #
    ax.text(0.010, 0.020,
            "Computational hypotheses · docking scores, not experimental binding affinities · no biological activity claimed",
            ha="left", va="bottom", fontsize=4.2,
            color="#7C2D12", zorder=5, fontstyle="italic")

    fig.tight_layout(pad=0)
    return fig


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------

def export(fig: plt.Figure, dpi: int, prefix: str) -> None:
    pdf_path  = OUT_DIR / f"{prefix}.pdf"
    tiff_path = OUT_DIR / f"{prefix}_ACS.tiff"
    tiff_hi   = OUT_DIR / f"{prefix}_ACS_1200dpi.tiff"

    fig.savefig(pdf_path, bbox_inches=None, pad_inches=0, facecolor=C_BG)
    print(f"PDF : {pdf_path}")

    if PIL_OK:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi,
                    bbox_inches=None, pad_inches=0, facecolor=C_BG)
        buf.seek(0)
        rgba = Image.open(buf).convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[3])
        bg.save(tiff_path, dpi=(DPI_LOW, DPI_LOW), compression="tiff_lzw")
        print(f"TIFF 300 dpi  : {tiff_path}  "
              f"({tiff_path.stat().st_size / 1024:.0f} KB, "
              f"{bg.size[0]}×{bg.size[1]} px)")

        buf_hi = io.BytesIO()
        fig.savefig(buf_hi, format="png", dpi=DPI_HIGH,
                    bbox_inches=None, pad_inches=0, facecolor=C_BG)
        buf_hi.seek(0)
        rgba_hi = Image.open(buf_hi).convert("RGBA")
        bg_hi = Image.new("RGB", rgba_hi.size, (255, 255, 255))
        bg_hi.paste(rgba_hi, mask=rgba_hi.split()[3])
        bg_hi.save(tiff_hi, dpi=(DPI_HIGH, DPI_HIGH), compression="tiff_lzw")
        print(f"TIFF 1200 dpi : {tiff_hi}  "
              f"({tiff_hi.stat().st_size / 1024:.0f} KB, "
              f"{bg_hi.size[0]}×{bg_hi.size[1]} px)")
    else:
        fig.savefig(tiff_path, format="tiff", dpi=dpi,
                    bbox_inches=None, pad_inches=0, facecolor=C_BG)
        print(f"TIFF (no PIL) : {tiff_path}")


def main() -> None:
    print(f"Generating V8 TOC graphic ({W_IN}×{H_IN} in, {DPI_LOW} dpi)…")
    fig = make_toc(dpi=DPI_LOW)
    export(fig, DPI_LOW, "p1_v8_toc_graphic")
    plt.close(fig)
    print("Done. Files saved in:", OUT_DIR)
    print("\nNext steps:")
    print("  1. Open p1_v8_toc_graphic_ACS.tiff in an image viewer")
    print("  2. Verify dimensions: 3.25 × 1.75 in at 300 dpi (975 × 525 px)")
    print("  3. Verify RGB color mode (no alpha)")
    print("  4. If using AI-generated version, replace these files with the AI output")
    print("  5. Copy final TIFF to submission_ACS_P1V8/Graphics/")


if __name__ == "__main__":
    main()
