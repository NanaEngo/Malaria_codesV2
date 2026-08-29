#!/usr/bin/env python3
"""P4 — Generate TOC Graphical Abstract for JCIM

Generates a publication-ready 300 DPI TOC Graphical Abstract summarizing:
MCTS + ScafVAE + Pareto Front + QMC validation.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRAPHICS_DIR = PROJECT_ROOT / "manuscript" / "LaTeX" / "Graphics"
GRAPHICS_DIR.mkdir(parents=True, exist_ok=True)


def generate_toc_graphic():
    fig, ax = plt.subplots(figsize=(8.25, 4.45), dpi=300) # ACS Standard TOC size approx
    ax.axis("off")
    
    # Background
    rect = patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="#f8f9fa", zorder=0)
    ax.add_patch(rect)
    
    # Title
    ax.text(0.5, 0.9, "Advanced Monte Carlo Strategies for\nAntimalarial Discovery", 
            ha='center', va='center', fontsize=18, fontweight='bold', color="#1a365d")
            
    # MCTS Tree visualization
    ax.text(0.2, 0.7, "1. ScafVAE-guided MCTS", ha='center', fontsize=12, fontweight='bold')
    
    # Nodes
    ax.plot([0.2, 0.15], [0.65, 0.55], 'k-', lw=2)
    ax.plot([0.2, 0.25], [0.65, 0.55], 'k-', lw=2)
    ax.plot([0.25, 0.22], [0.55, 0.45], 'k-', lw=2)
    ax.plot([0.25, 0.28], [0.55, 0.45], 'k-', lw=2)
    
    circles = [(0.2, 0.65), (0.15, 0.55), (0.25, 0.55), (0.22, 0.45), (0.28, 0.45)]
    for x, y in circles:
        circle = patches.Circle((x, y), 0.03, facecolor="#4299e1", edgecolor="black", zorder=3)
        ax.add_patch(circle)
        
    # Pareto Front visualization
    ax.text(0.5, 0.7, "2. Pareto Multi-Objective", ha='center', fontsize=12, fontweight='bold')
    
    # Axes
    ax.plot([0.35, 0.65], [0.45, 0.45], 'k-', lw=1.5)
    ax.plot([0.35, 0.35], [0.45, 0.65], 'k-', lw=1.5)
    
    # Points
    np.random.seed(42)
    px = np.random.uniform(0.38, 0.62, 30)
    py = np.random.uniform(0.48, 0.62, 30)
    ax.scatter(px, py, color="#cbd5e0", s=20)
    
    # Pareto frontier points
    fx = np.array([0.4, 0.45, 0.55, 0.62])
    fy = np.array([0.62, 0.58, 0.52, 0.48])
    ax.plot(fx, fy, 'r--', lw=2)
    ax.scatter(fx, fy, color="#e53e3e", s=40, zorder=4)
    
    # QMC Validation visualization
    ax.text(0.8, 0.7, "3. QMC Validation", ha='center', fontsize=12, fontweight='bold')
    
    # Simple quantum well / orbital representation
    x = np.linspace(0.7, 0.9, 100)
    y = 0.55 + 0.08 * np.sin(10 * np.pi * x) * np.exp(-100 * (x - 0.8)**2)
    ax.plot(x, y, color="#805ad5", lw=2.5)
    ax.plot([0.7, 0.9], [0.55, 0.55], 'k--', lw=1)
    
    # Bottom text
    ax.text(0.5, 0.2, "Ab Initio Fidelity \u2192 Synthesisable Candidates", 
            ha='center', fontsize=14, fontstyle='italic', color="#2d3748")

    out_path = GRAPHICS_DIR / "toc_graphical_abstract.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated TOC Graphic at {out_path}")


if __name__ == "__main__":
    generate_toc_graphic()
