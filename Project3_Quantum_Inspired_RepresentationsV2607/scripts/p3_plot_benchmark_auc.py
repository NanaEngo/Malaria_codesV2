#!/usr/bin/env python3
"""
P3 AUC Benchmark Bar Plot (canonical, BMAD v51)

Primary source: canonical classical benchmark (p3_classical_benchmark_19849.csv,
job 12698, n=19,836 panel — RF, 5-fold CV). Adds:
  - Hybrid descriptor row from the canonical hybrid re-run CSV
    (p3_hybrid_benchmark.csv) when present and canonical.
  - QKS comparison (quantum / RBF / linear) from the QKS benchmark CSV
    (p3_qks_benchmark_*.csv) when present.

Output: results/figures/p3_auc_benchmark_bar.png (300 DPI, colorblind-safe)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
OUT_DIR = RESULTS_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Load canonical classical data ────────────────────────────────────────────
CLASSICAL_CSV = RESULTS_DIR / "p3_classical_benchmark_19849.csv"
if not CLASSICAL_CSV.exists():
    raise SystemExit(f"Canonical classical CSV not found: {CLASSICAL_CSV}")
df = pd.read_csv(CLASSICAL_CSV)
rf = df[df['classifier'] == 'rf'].copy()

summary = []
for desc in rf['descriptor'].unique():
    aucs = rf[rf['descriptor'] == desc]['auc'].dropna().values
    if len(aucs) > 0:
        summary.append({
            'descriptor': desc,
            'mean_auc': aucs.mean(),
            'std_auc': aucs.std(),
            'fold_aucs': aucs,
            'group': 'classical',
        })

# ─── Hybrid row from canonical re-run (if present) ───────────────────────────
# Gate on the canonical checkpoint: the old hybrid CSV (job 12696) contains the
# transductive-leakage value 0.8968 and must NOT be shown. Only trust the
# hybrid row once the canonical re-run (p3_hybrid_canonical_checkpoint.json)
# has produced it (BMAD v51 / Appendix K).
HYBRID_CSV = RESULTS_DIR / "p3_hybrid_benchmark.csv"
CANON_CKPT = RESULTS_DIR / "p3_hybrid_canonical_checkpoint.json"
hybrid_present = False
if HYBRID_CSV.exists() and CANON_CKPT.exists():
    try:
        import json
        ckpt = json.loads(CANON_CKPT.read_text())
        ckpt_records = ckpt.get("records", [])
        hybrid_folds = {r.get("fold") for r in ckpt_records
                        if r.get("descriptor") == "Hybrid"}
        if len(hybrid_folds) == 5:
            h = pd.read_csv(HYBRID_CSV)
            hr = h[(h['classifier'] == 'rf') & (h['descriptor'] == 'Hybrid')]['auc'].dropna()
            if len(hr) == 5:
                summary.append({
                    'descriptor': 'Hybrid',
                    'mean_auc': hr.mean(),
                    'std_auc': hr.std(),
                    'fold_aucs': hr.values,
                    'group': 'hybrid',
                })
                hybrid_present = True
        elif ckpt.get("section") == "ablation_done":
            # canonical run finished through ablation; read hybrid from CSV
            h = pd.read_csv(HYBRID_CSV)
            hr = h[(h['classifier'] == 'rf') & (h['descriptor'] == 'Hybrid')]['auc'].dropna()
            if len(hr) == 5:
                summary.append({
                    'descriptor': 'Hybrid',
                    'mean_auc': hr.mean(),
                    'std_auc': hr.std(),
                    'fold_aucs': hr.values,
                    'group': 'hybrid',
                })
                hybrid_present = True
    except Exception as e:
        print(f"  [warn] could not read hybrid CSV for figure: {e}")

# ─── QKS models (quantum / RBF / linear) from QKS benchmark ──────────────────
QKS_CSV = RESULTS_DIR / "p3_qks_benchmark_n19849.csv"
if not QKS_CSV.exists():
    QKS_CSV = RESULTS_DIR / "p3_qks_benchmark_n5000.csv"
qks_present = False
if QKS_CSV.exists():
    try:
        q = pd.read_csv(QKS_CSV)
        for model in ['quantum', 'rbf', 'linear']:
            qa = q[q['model'] == model]['auc'].dropna()
            if len(qa) > 0:
                label = {'quantum': 'QK (quantum)', 'rbf': 'RBF', 'linear': 'Linear'}[model]
                summary.append({
                    'descriptor': label,
                    'mean_auc': qa.mean(),
                    'std_auc': qa.std(),
                    'fold_aucs': qa.values,
                    'group': 'qks',
                })
        qks_present = True
    except Exception as e:
        print(f"  [warn] could not read QKS CSV for figure: {e}")

summary.sort(key=lambda x: x['mean_auc'], reverse=True)

labels = [s['descriptor'] for s in summary]
means  = [s['mean_auc'] for s in summary]
stds   = [s['std_auc'] for s in summary]
groups = [s['group'] for s in summary]

# ─── Color palette (colorblind-safe, paper-matched) ─────────────────────────
# Classical fingerprints: blues/greens; hybrid: purple; QKS: greys/oranges
color_map = {
    'ECFP4':  '#2196F3', 'FCFP4': '#1E88E5', 'MACCS': '#1565C0', 'AP': '#0D47A1',
    'PHCO':   '#43A047', 'BPF':   '#2E7D32',
    'TFP':    '#FF8F00', 'TNE':   '#E65100',
    'Hybrid': '#6A1B9A',
    'QK (quantum)': '#9E9E9E', 'RBF': '#757575', 'Linear': '#BDBDBD',
}
colors = [color_map.get(l, '#888888') for l in labels]

# ─── Plot ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))

x = np.arange(len(labels))
width = 0.65

bars = ax.bar(x, means, width, yerr=stds, color=colors, edgecolor='black',
              linewidth=0.8, capsize=4, error_kw={'linewidth': 1.5})

for bar, mean, std in zip(bars, means, stds):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.008,
            f'{mean:.3f}±{std:.3f}', ha='center', va='bottom',
            fontsize=8, fontweight='bold')

ax.axhline(y=0.5, color='red', linestyle='--', linewidth=0.8, alpha=0.6,
           label='Random (AUC=0.5)')
ax.axhline(y=0.8, color='green', linestyle=':', linewidth=0.8, alpha=0.4,
           label='Threshold (AUC=0.8)')

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
ax.set_ylabel('Mean AUC (5-fold CV)', fontsize=12, fontweight='bold')
n_panel = "19,836"
title = ('P3 Activity Prediction Benchmark (canonical panel, '
         f'n={n_panel})\nClassical + Hybrid + Quantum Kernel Scores')
if not hybrid_present:
    title += '\n(Hybrid row appears once the canonical re-run completes)'
ax.set_title(title, fontsize=13, fontweight='bold', pad=12)
ax.set_ylim(0.35, 0.98)
ax.legend(fontsize=9, loc='lower left', framealpha=0.85)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Group separator lines (classical | hybrid | qks)
prev_group = groups[0]
for i in range(1, len(groups)):
    if groups[i] != prev_group:
        ax.axvline(x=i - 0.5, color='black', linestyle=':', linewidth=0.8, alpha=0.5)
    prev_group = groups[i]

plt.tight_layout()
out_path = OUT_DIR / 'p3_auc_benchmark_bar.png'
fig.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Saved: {out_path}")
plt.close()

# ─── Also regenerate summary.txt from canonical data ─────────────────────────
from scipy.stats import ttest_rel

lines = [
    "P3 Benchmark Summary (RF, 5-fold CV, canonical panel n=19,836)",
    "=" * 60,
    "",
]
for s in summary:
    lines.append(f"{s['descriptor']:<14s}  AUC = {s['mean_auc']:.4f} ± {s['std_auc']:.4f}")

ecfp4_rows = [s for s in summary if s['descriptor'] == 'ECFP4']
if ecfp4_rows:
    ecfp4_aucs = ecfp4_rows[0]['fold_aucs']
    lines.append("")
    lines.append("Paired t-tests (vs ECFP4):")
    for s in summary:
        if s['descriptor'] == 'ECFP4' or len(s['fold_aucs']) != len(ecfp4_aucs):
            continue
        t_stat, p_val = ttest_rel(ecfp4_aucs, s['fold_aucs'])
        sig = "SIGNIFICANT" if p_val < 0.05 else "not significant"
        mean_diff = ecfp4_aucs.mean() - s['fold_aucs'].mean()
        lines.append(f"  vs {s['descriptor']:<14s}: Δ={mean_diff:+.4f}, t={t_stat:.3f}, "
                     f"p={p_val:.5f} ({sig})")

if not hybrid_present:
    lines.append("")
    lines.append("Hybrid row pending canonical re-run (BMAD Appendix K).")

summary_text = "\n".join(lines)
summary_path = RESULTS_DIR / "p3_hybrid_summary.txt"
summary_path.write_text(summary_text)
print(f"Saved: {summary_path}")
print(summary_text)
