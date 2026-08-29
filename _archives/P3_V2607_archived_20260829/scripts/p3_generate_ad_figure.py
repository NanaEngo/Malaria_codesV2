#!/usr/bin/env python3
"""
Generate applicability-domain figure from canonical QKS benchmark data.

Panel A: AUC per fold (quantum ≈ RBF, honest negative)
Panel B: Target alignment per fold (quantum >> RBF, doesn't translate to AUC)
"""
import pathlib, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

RESULTS = pathlib.Path(__file__).resolve().parents[1] / "results"
OUT = pathlib.Path(__file__).resolve().parents[1] / "manuscript" / "LaTeX" / "Graphics"

# --- Load canonical data ---
df19 = pd.read_csv(RESULTS / "p3_qks_benchmark_n19849.csv")
df5k = pd.read_csv(RESULTS / "p3_qks_benchmark_n5000.csv")

def summary(df, label):
    q = df[df.model == "quantum"]
    r = df[df.model == "rbf"]
    # paired t-test across folds
    t, p = stats.ttest_rel(q.auc.values, r.auc.values)
    return {
        "label": label,
        "q_auc": q.auc.mean(),
        "q_std": q.auc.std(),
        "r_auc": r.auc.mean(),
        "r_std": r.auc.std(),
        "q_ta": q.target_alignment.mean(),
        "r_ta": r.target_alignment.mean(),
        "t": t, "p": p,
    }

s19 = summary(df19, "n = 19,849")
s5k = summary(df5k, "n = 5,000")

# --- Figure ---
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))

# Panel A: AUC per fold
ax = axes[0]
folds = np.arange(1, 6)
q19 = df19[df19.model == "quantum"].sort_values("fold").auc.values
r19 = df19[df19.model == "rbf"].sort_values("fold").auc.values
q5k = df5k[df5k.model == "quantum"].sort_values("fold").auc.values
r5k = df5k[df5k.model == "rbf"].sort_values("fold").auc.values

ax.plot(folds, q19, "o-", color="#1f77b4", markersize=5, label="Quantum (n=19,849)")
ax.plot(folds, r19, "s--", color="#ff7f0e", markersize=5, label="RBF (n=19,849)")
ax.plot(folds, q5k, "^", color="#2ca02c", markersize=5, alpha=0.7, label="Quantum (n=5,000)")
ax.plot(folds, r5k, "v", color="#d62728", markersize=5, alpha=0.7, label="RBF (n=5,000)")
ax.set_xlabel("Fold")
ax.set_ylabel("AUC-ROC")
ax.set_xticks(folds)
ax.set_ylim(0.79, 0.86)
ax.set_title("A: Classification performance", fontsize=9, loc="left")
ax.legend(fontsize=6, loc="lower left")
ax.axhline(0.5, color="gray", ls=":", lw=0.5)

# Panel B: Target alignment per fold
ax = axes[1]
ta_q19 = df19[df19.model == "quantum"].sort_values("fold").target_alignment.values
ta_r19 = df19[df19.model == "rbf"].sort_values("fold").target_alignment.values
ta_q5k = df5k[df5k.model == "quantum"].sort_values("fold").target_alignment.values
ta_r5k = df5k[df5k.model == "rbf"].sort_values("fold").target_alignment.values

ax.plot(folds, ta_q19, "o-", color="#1f77b4", markersize=5, label="Quantum (n=19,849)")
ax.plot(folds, ta_r19, "s--", color="#ff7f0e", markersize=5, label="RBF (n=19,849)")
ax.plot(folds, ta_q5k, "^", color="#2ca02c", markersize=5, alpha=0.7, label="Quantum (n=5,000)")
ax.plot(folds, ta_r5k, "v", color="#d62728", markersize=5, alpha=0.7, label="RBF (n=5,000)")
ax.set_xlabel("Fold")
ax.set_ylabel("Target alignment")
ax.set_xticks(folds)
ax.set_ylim(0.0, 0.75)
ax.set_title("B: Kernel-target alignment", fontsize=9, loc="left")
ax.legend(fontsize=6, loc="lower left")
ax.axhline(0.0, color="gray", ls=":", lw=0.5)

fig.tight_layout()
outpath = OUT / "applicability_domain.pdf"
fig.savefig(outpath, dpi=300, bbox_inches="tight")
print(f"Saved: {outpath}")

# --- Stats summary ---
for s in [s19, s5k]:
    sig = "*" if s["p"] < 0.05 else "ns"
    print(f"{s['label']}: Q={s['q_auc']:.4f}±{s['q_std']:.4f}  R={s['r_auc']:.4f}±{s['r_std']:.4f}  "
          f"ΔAUC={s['q_auc']-s['r_auc']:+.4f}  t={s['t']:.3f}  p={s['p']:.4f} ({sig})")
    print(f"  Target alignment: Q={s['q_ta']:.4f}  R={s['r_ta']:.4f}")
