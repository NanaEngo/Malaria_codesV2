#!/usr/bin/env python3
"""
P3 AUC Benchmark Bar Plot

Reads p3_hybrid_benchmark.csv and generates a bar plot of mean AUC ± std
for all descriptors (RF classifier), ordered by descending AUC.
Output: results/figures/p3_auc_benchmark_bar.png (300 DPI)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
CSV_PATH = RESULTS_DIR / "p3_hybrid_benchmark.csv"
OUT_DIR = RESULTS_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Load data ───────────────────────────────────────────────────────────────
df = pd.read_csv(CSV_PATH)
rf = df[df['classifier'] == 'rf'].copy()

# ─── Aggregate ────────────────────────────────────────────────────────────────
summary = []
for desc in rf['descriptor'].unique():
    aucs = rf[rf['descriptor'] == desc]['auc'].dropna().values
    if len(aucs) > 0:
        summary.append({
            'descriptor': desc,
            'mean_auc': aucs.mean(),
            'std_auc': aucs.std(),
            'fold_aucs': aucs,
        })

summary.sort(key=lambda x: x['mean_auc'], reverse=True)

labels = [s['descriptor'] for s in summary]
means  = [s['mean_auc'] for s in summary]
stds   = [s['std_auc'] for s in summary]

# ─── Color palette (colorblind-safe, paper-matched) ─────────────────────────
# Classical fingerprints: blues/greens; quantum-inspired: oranges/reds
color_map = {
    'ECFP4':  '#2196F3',
    'FCFP4':  '#1E88E5',
    'MACCS':  '#1565C0',
    'AP':     '#0D47A1',
    'PHCO':   '#43A047',
    'BPF':    '#2E7D32',
    'TFP':    '#FF8F00',
    'TNE':    '#E65100',
    'Hybrid': '#6A1B9A',
}
colors = [color_map.get(l, '#888888') for l in labels]

# ─── Plot ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(labels))
width = 0.65

bars = ax.bar(x, means, width, yerr=stds, color=colors, edgecolor='black',
              linewidth=0.8, capsize=4, error_kw={'linewidth': 1.5})

# Value labels on bars
for bar, mean, std in zip(bars, means, stds):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.008,
            f'{mean:.3f}±{std:.3f}', ha='center', va='bottom',
            fontsize=8, fontweight='bold')

# Reference line at AUC=0.5 (random classifier)
ax.axhline(y=0.5, color='red', linestyle='--', linewidth=0.8, alpha=0.6,
           label='Random (AUC=0.5)')
ax.axhline(y=0.8, color='green', linestyle=':', linewidth=0.8, alpha=0.4,
           label='Threshold (AUC=0.8)')

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
ax.set_ylabel('Mean AUC (5-fold CV)', fontsize=12, fontweight='bold')
ax.set_title('P3 Activity Prediction Benchmark\n'
             'Hybrid Quantum-Inspired vs Classical Fingerprints',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylim(0.35, 0.95)
ax.legend(fontsize=9, loc='lower left', framealpha=0.85)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
out_path = OUT_DIR / 'p3_auc_benchmark_bar.png'
fig.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Saved: {out_path}")
plt.close()

# ─── Also regenerate summary.txt from CSV ────────────────────────────────────
from scipy.stats import ttest_rel

lines = [
    "P3 Hybrid Benchmark Summary (RF classifier, 5-fold CV)",
    "=" * 50,
    "",
]
for desc, mean, std in zip(labels, means, stds):
    lines.append(f"{desc:<12s}  AUC = {mean:.4f} ± {std:.4f}")

lines.append("")
lines.append("Paired t-tests (vs ECFP4):")
ecfp4_aucs = rf[rf['descriptor'] == 'ECFP4']['auc'].values
for desc in sorted(rf['descriptor'].unique()):
    if desc == 'ECFP4':
        continue
    other = rf[rf['descriptor'] == desc]['auc'].values
    if len(other) == 5:
        t_stat, p_val = ttest_rel(ecfp4_aucs, other)
        sig = "SIGNIFICANT" if p_val < 0.05 else "not significant"
        mean_diff = ecfp4_aucs.mean() - other.mean()
        lines.append(f"  vs {desc:<12s}: Δ={mean_diff:+.4f}, t={t_stat:.3f}, p={p_val:.5f} ({sig})")

summary_text = "\n".join(lines)
summary_path = RESULTS_DIR / "p3_hybrid_summary.txt"
summary_path.write_text(summary_text)
print(f"Saved: {summary_path}")
print(summary_text)
