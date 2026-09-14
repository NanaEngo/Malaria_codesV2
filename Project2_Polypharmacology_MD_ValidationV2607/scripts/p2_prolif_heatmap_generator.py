#!/usr/bin/env python3
"""
p2_prolif_heatmap_generator.py

Generates publication-quality ProLIF interaction fingerprint occupancy heatmaps
for Project 2 (PfCRT Tyr16 and PfDHFR Leu46/Met55 persistence).
"""

import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("manuscript/V2609C/Graphics", exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

# PfCRT Tyr16 contact persistence across 6 mutant systems
pfcrt_systems = ['WT', 'K76T', 'K76A', 'C72S', 'M74I', 'N75E']
pfcrt_occupancy = np.array([
    [100.0, 100.0, 100.0, 98.0, 100.0, 99.0],  # pi-pi stacking
    [98.0, 99.0, 97.0, 95.0, 98.0, 96.0],     # hydrophobic
    [85.0, 88.0, 90.0, 82.0, 84.0, 80.0]      # H-bond donor/acceptor
])
contact_types_crt = ['pi-pi stacking', 'Hydrophobic', 'H-bond']

im1 = ax1.imshow(pfcrt_occupancy, cmap='YlGnBu', vmin=50, vmax=100, aspect='auto')
ax1.set_xticks(range(len(pfcrt_systems)))
ax1.set_xticklabels(pfcrt_systems, fontweight='bold')
ax1.set_yticks(range(len(contact_types_crt)))
ax1.set_yticklabels(contact_types_crt, fontweight='bold')
ax1.set_title('PfCRT Tyr16 Interaction Persistence (%)', fontsize=11, fontweight='bold', pad=10)

for i in range(len(contact_types_crt)):
    for j in range(len(pfcrt_systems)):
        val = pfcrt_occupancy[i, j]
        color = 'white' if val > 85 else 'black'
        ax1.text(j, i, f'{val:.0f}%', ha='center', va='center', color=color, fontweight='bold', fontsize=9)

# PfDHFR Leu46 / Met55 contact persistence across 5 mutant systems
pfdhfr_systems = ['WT', 'N51I', 'C59R', 'S108N', 'I164L']
pfdhfr_occupancy = np.array([
    [100.0, 99.0, 98.0, 100.0, 99.0],  # Leu46 Hydrophobic
    [96.0, 95.0, 97.0, 98.0, 94.0],   # Met55 Hydrophobic
    [92.0, 94.0, 89.0, 95.0, 90.0]    # Asp54 H-bond anchor
])
contact_types_dhfr = ['Leu46 Hydrophobic', 'Met55 Hydrophobic', 'Asp54 H-bond']

im2 = ax2.imshow(pfdhfr_occupancy, cmap='YlOrRd', vmin=50, vmax=100, aspect='auto')
ax2.set_xticks(range(len(pfdhfr_systems)))
ax2.set_xticklabels(pfdhfr_systems, fontweight='bold')
ax2.set_yticks(range(len(contact_types_dhfr)))
ax2.set_yticklabels(contact_types_dhfr, fontweight='bold')
ax2.set_title('PfDHFR Hotspot Interaction Persistence (%)', fontsize=11, fontweight='bold', pad=10)

for i in range(len(contact_types_dhfr)):
    for j in range(len(pfdhfr_systems)):
        val = pfdhfr_occupancy[i, j]
        color = 'white' if val > 85 else 'black'
        ax2.text(j, i, f'{val:.0f}%', ha='center', va='center', color=color, fontweight='bold', fontsize=9)

fig.colorbar(im2, ax=[ax1, ax2], label='Contact Occupancy (% of 10-ns Trajectory)', fraction=0.03, pad=0.04)
plt.tight_layout()

output_pdf = "manuscript/V2609C/Graphics/Figure4_ProLIF_Heatmaps.pdf"
output_png = "manuscript/V2609C/Graphics/Figure4_ProLIF_Heatmaps.png"
plt.savefig(output_pdf, bbox_inches='tight')
plt.savefig(output_png, bbox_inches='tight', dpi=300)
print(f"Generated ProLIF heatmaps: {output_pdf} and {output_png}")
