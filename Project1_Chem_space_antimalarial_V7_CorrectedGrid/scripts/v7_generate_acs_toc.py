#!/usr/bin/env python3
"""Generate the ACS-compliant Table of Contents graphic for P1 V7.

Specifications (ACS Journal of Chemical Information and Modeling):
  - Size: 3.25 in wide x 1.75 in tall (8.25 cm x 4.45 cm), landscape rectangle.
  - Resolution: 300 dpi minimum (1200 dpi for line art); TIFF preferred, PDF/JPEG accepted.
  - Mandatory for all ACS research articles.

Outputs (in manuscript/Graphics/):
  - p1_v7_toc_graphic.pdf  (vector, canonical for the .tex)
  - p1_v7_toc_graphic_ACS.tiff  (300 dpi RGB, for the ACS submission portal)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
V7 = ROOT / "Project1_Chem_space_antimalarial_V7_CorrectedGrid"
FIG_DIR = V7 / "manuscript" / "Graphics"

# ACS TOC geometry
W_IN, H_IN = 3.25, 1.75
DPI = 300
ASPECT = W_IN / H_IN  # 1.857

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7.5,
    "axes.edgecolor": "#1f2937",
    "axes.linewidth": 0.8,
})


def box(ax, x, y, w, h, title, body, color="#ffffff", edge="#1f2937", tcol="#0f172a", bcol="#334155"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.045",
        linewidth=0.9, edgecolor=edge, facecolor=color, zorder=2,
    ))
    ax.text(x + w / 2, y + h - 0.055, title, ha="center", va="top",
            fontsize=7.6, fontweight="bold", color=tcol, zorder=3)
    ax.text(x + w / 2, y + 0.045, body, ha="center", va="bottom",
            fontsize=6.4, color=bcol, zorder=3, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#475569",
                                lw=1.1, mutation_scale=9), zorder=4)


def main() -> None:
    fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ---- left: pipeline funnel ----
    box(ax, 0.015, 0.60, 0.24, 0.33, "Hybrid library",
        "65,856 molecules\n396 ANP + 454 synth.")
    box(ax, 0.015, 0.33, 0.24, 0.20, "Prioritised leads",
        "19,913 synthesizable\n(SYBA > 0)")
    box(ax, 0.015, 0.05, 0.24, 0.21, "Set-C cohort",
        "17 polypharm\ncandidates")

    # ---- centre: 4 targets ----
    targets = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]
    subs = ["7F3Y", "6UKJ", "2F6I", "9N10"]
    for i, (t, s) in enumerate(zip(targets, subs)):
        x = 0.32 + i * 0.16
        box(ax, x, 0.42, 0.135, 0.42, t,
            f"anchor {s}\n68/68 gate-pass\nVina grid",
            color="#f0fdfa", edge="#0d9488")

    # ---- right: RRS readout ----
    box(ax, 0.955 - 0.225, 0.42, 0.225, 0.52,
        "Resistance Resilience",
        "A*: 6  ·  B: 5  ·  C: 5  ·  D: 1\nRRS range 68.2–111.7%\nρ(PNS–RRS) = −0.559",
        color="#fefce8", edge="#ca8a04")

    # ---- bottom strip: honest evidence boundary ----
    ax.text(0.015, 0.155, "Evidence boundary: docking-derived hypotheses — no cross-target mean, "
                          "no biological validation claimed.",
            fontsize=5.6, color="#7c2d12", ha="left", va="center", zorder=5)

    # arrows
    arrow(ax, 0.255, 0.76, 0.315, 0.66)
    arrow(ax, 0.255, 0.44, 0.315, 0.52)
    arrow(ax, 0.255, 0.15, 0.315, 0.28)
    arrow(ax, 0.865, 0.63, 0.930, 0.70)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIG_DIR / "p1_v7_toc_graphic.pdf"
    tiff_path = FIG_DIR / "p1_v7_toc_graphic_ACS.tiff"
    fig.savefig(pdf_path, bbox_inches=None, pad_inches=0, facecolor="white")
    # Save a temporary RGBA PNG buffer, then flatten onto white and write RGB TIFF.
    # ACS requires RGB (no alpha); keeping the flatten inside the script makes
    # the RGB output reproducible from a single command.
    import io
    from PIL import Image
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches=None, pad_inches=0,
                facecolor="white")
    buf.seek(0)
    rgba = Image.open(buf).convert("RGBA")
    bg = Image.new("RGB", rgba.size, (255, 255, 255))
    bg.paste(rgba, mask=rgba.split()[3])
    bg.save(tiff_path, dpi=(DPI, DPI), compression="tiff_lzw")
    # High-resolution TIFF (1200 dpi) for text-bearing line art per ACS guidance.
    tiff_hi = FIG_DIR / "p1_v7_toc_graphic_ACS_1200dpi.tiff"
    buf.seek(0)
    rgba_hi = Image.open(buf).convert("RGBA")
    bg_hi = Image.new("RGB", rgba_hi.size, (255, 255, 255))
    bg_hi.paste(rgba_hi, mask=rgba_hi.split()[3])
    bg_hi.save(tiff_hi, dpi=(1200, 1200), compression="tiff_lzw")
    plt.close(fig)

    print(f"PDF   : {pdf_path}  ({pdf_path.stat().st_size/1024:.0f} KB)")
    print(f"TIFF  : {tiff_path}  ({tiff_path.stat().st_size/1024:.0f} KB, {DPI} dpi RGB, {W_IN}x{H_IN} in)")
    print(f"TIFF12: {tiff_hi}  ({tiff_hi.stat().st_size/1024:.0f} KB, 1200 dpi RGB)")


if __name__ == "__main__":
    main()
