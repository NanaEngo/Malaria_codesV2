#!/usr/bin/env python3
"""
Generates RRS radar plots for the 17 Set-C candidates.
Saves to Project2_Polypharmacology_MD_ValidationV2607/manuscript/Graphics/rrs_radar_profiles.pdf
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Paths
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, '..', 'results', 'c_rrs_classification.csv')
OUT_PDF = os.path.join(BASE, '..', 'manuscript', 'Graphics', 'rrs_radar_profiles.pdf')
os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)

# Load data
df = pd.read_csv(CSV_PATH)
# The rigorous audit exposes the available-target estimand through the
# compatibility aliases RRS_mean/RRS_class. Missing mutation values indicate
# an ineligible target and are intentionally left as gaps in the radar.
df = df.dropna(subset=['RRS_class']).copy()

# Mutants to plot
mutants = ['RRS_N51I', 'RRS_C59R', 'RRS_S108N', 'RRS_I164L', 'RRS_K76T', 'RRS_K76A']
labels = ['N51I\n(DHFR)', 'C59R\n(DHFR)', 'S108N\n(DHFR)', 'I164L\n(DHFR)', 'K76T\n(CRT)', 'K76A\n(CRT)']

# Number of variables
num_vars = len(mutants)

# Compute angle for each axis
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
# Complete the loop
angles += angles[:1]

# Set up matplotlib figure
fig, axes = plt.subplots(4, 5, figsize=(15, 13), subplot_kw=dict(polar=True))
axes = axes.flatten()

# Colors for classes
class_colors = {
    'A*': '#2196F3', # Blue
    'A': '#00BCD4',  # Cyan
    'B': '#4CAF50',  # Green
    'C': '#FF9800',  # Orange
    'D': '#F44336'   # Red
}

# Plot each compound
for i, (idx, row) in enumerate(df.iterrows()):
    if i >= len(axes):
        raise RuntimeError(f"Radar layout has only {len(axes)} axes for {len(df)} candidates")
    ax = axes[i]
    
    # Get values and close the loop
    values = row[mutants].values.tolist()
    values += values[:1]
    
    # Plot data
    color = class_colors.get(row['RRS_class'], '#888888')
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.25)
    
    # Labels
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=7)
    
    # Y-axis
    ax.set_rlabel_position(0)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=6, color='grey')
    ax.set_ylim(0, 180)
    
    # Title
    ax.set_title(f"{row.get('candidate_id', f'PP-{i+1:02d}')} (Class {row['RRS_class']})\nRRS={row['RRS_mean']:.1f}%",
                 fontsize=9, fontweight='bold', pad=10)

# Hide unused axes
for i in range(len(df), len(axes)):
    axes[i].axis('off')

plt.tight_layout()
plt.savefig(OUT_PDF, dpi=300, bbox_inches='tight')
print(f"Generated radar profiles at: {OUT_PDF}")
