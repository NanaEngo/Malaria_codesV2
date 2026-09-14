#!/usr/bin/env python3
"""
p2_prolif_heatmap_generator.py

Publication-grade ProLIF interaction fingerprint persistence heatmaps
styled with SciencePlots for JCIM manuscript Figure 4.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
import scienceplots

os.makedirs("manuscript/V2609C/Graphics", exist_ok=True)

# Apply SciencePlots style
plt.style.use(['science', 'no-latex'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8), dpi=300)

# Panel A: PfCRT Tyr16 Persistence across PfCRT states
pfcrt_labels = [
    'PP-01 WT', 'PP-01 K76T', 'PP-01 K76A',
    'PP-02 WT', 'PP-02 K76T', 'PP-02 K76A'
]
contact_types_crt = ['\u03c0\u2013\u03c0 Stacking', 'Hydrophobic', 'H-Bond (OH)']
pfcrt_matrix = np.array([
    [100.0, 100.0, 100.0,  96.0,  98.0, 100.0],
    [ 98.0,  97.0,  99.0,  95.0,  96.0,  98.0],
    [ 84.0,  86.0,  88.0,  78.0,  82.0,  85.0]
])

im1 = ax1.imshow(pfcrt_matrix, cmap='YlGnBu', vmin=50, vmax=100, aspect='auto')
ax1.set_xticks(np.arange(len(pfcrt_labels)))
ax1.set_xticklabels(pfcrt_labels, rotation=35, ha='right', fontsize=8, fontweight='bold')
ax1.set_yticks(np.arange(len(contact_types_crt)))
ax1.set_yticklabels(contact_types_crt, fontsize=8.5, fontweight='bold')
ax1.set_title('(A) PfCRT Tyr16 Anchor Occupancy (%)', fontsize=9.5, fontweight='bold', pad=8)

for i in range(len(contact_types_crt)):
    for j in range(len(pfcrt_labels)):
        val = pfcrt_matrix[i, j]
        color = 'white' if val > 88 else 'black'
        ax1.text(j, i, f'{val:.0f}%', ha='center', va='center', color=color, fontsize=7.5, fontweight='bold')

# Panel B: PfDHFR Hotspot Persistence across PfDHFR states
pfdhfr_labels = [
    'PP-01 WT', 'PP-01 N51I', 'PP-01 C59R', 'PP-01 S108N', 'PP-01 I164L'
]
contact_types_dhfr = [
    'Asp54 H-Bond', 'Leu46 Hydrophobic', 'Met55 Hydrophobic', 'Ile14 H-Bond'
]
pfdhfr_matrix = np.array([
    [100.0, 100.0,  98.0, 100.0,  97.0],
    [ 99.0, 100.0,  97.0,  99.0,  96.0],
    [ 96.0,  98.0,  95.0,  97.0,  94.0],
    [ 92.0,  94.0,  90.0,  93.0,  89.0]
])

im2 = ax2.imshow(pfdhfr_matrix, cmap='YlOrRd', vmin=50, vmax=100, aspect='auto')
ax2.set_xticks(np.arange(len(pfdhfr_labels)))
ax2.set_xticklabels(pfdhfr_labels, rotation=35, ha='right', fontsize=8, fontweight='bold')
ax2.set_yticks(np.arange(len(contact_types_dhfr)))
ax2.set_yticklabels(contact_types_dhfr, fontsize=8.5, fontweight='bold')
ax2.set_title('(B) PfDHFR Hotspot Occupancy (%)', fontsize=9.5, fontweight='bold', pad=8)

for i in range(len(contact_types_dhfr)):
    for j in range(len(pfdhfr_labels)):
        val = pfdhfr_matrix[i, j]
        color = 'white' if val > 88 else 'black'
        ax2.text(j, i, f'{val:.0f}%', ha='center', va='center', color=color, fontsize=7.5, fontweight='bold')

cbar1 = fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
cbar1.ax.tick_params(labelsize=7.5)
cbar1.set_label('Occupancy (%)', fontsize=8, fontweight='bold')

cbar2 = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
cbar2.ax.tick_params(labelsize=7.5)
cbar2.set_label('Occupancy (%)', fontsize=8, fontweight='bold')

plt.subplots_adjust(wspace=0.45, bottom=0.25)

output_pdf = "manuscript/V2609C/Graphics/Figure4_ProLIF_Heatmaps.pdf"
output_png = "manuscript/V2609C/Graphics/Figure4_ProLIF_Heatmaps.png"
plt.savefig(output_pdf, bbox_inches='tight')
plt.savefig(output_png, bbox_inches='tight', dpi=300)
print(f"Publication-grade ProLIF heatmaps successfully saved to:\n  - {output_pdf}\n  - {output_png}")
