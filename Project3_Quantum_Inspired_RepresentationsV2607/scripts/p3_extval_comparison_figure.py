#!/usr/bin/env python3
"""Generate internal vs external validation comparison bar chart for P3."""
import json
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "Project3_Quantum_Inspired_RepresentationsV2607/results"
FIG = RES / "figures"

# --- Internal canonical values (from tab:benchmark, RF for descriptors, SVM for QKS) ---
internal = {
    "ECFP4":   0.948,
    "TFP":     0.876,
    "TNE":     0.722,
    "Hybrid":  0.888,
    "QKS\n(quantum)": 0.823,
    "QKS\n(RBF)":     0.829,
}

# --- External descriptor values (RF, from report JSON) ---
with open(RES / "p3_external_validation_report.json") as f:
    desc_ext = json.load(f)

# --- External QKS values (SVM, from QKS report JSON) ---
with open(RES / "p3_external_validation_qks_report.json") as f:
    qks_ext = json.load(f)

external = {
    "ECFP4":   desc_ext["descriptor_mean_auc"]["ECFP4"],
    "TFP":     desc_ext["descriptor_mean_auc"]["TFP"],
    "TNE":     desc_ext["descriptor_mean_auc"]["TNE"],
    "Hybrid":  desc_ext["descriptor_mean_auc"]["Hybrid"],
    "QKS\n(quantum)": qks_ext["kernel_mean_auc"]["quantum"],
    "QKS\n(RBF)":     qks_ext["kernel_mean_auc"]["rbf"],
}

methods = list(internal.keys())
int_vals = [internal[m] for m in methods]
ext_vals = [external[m] for m in methods]

# External std errors for error bars
ext_std = {
    "ECFP4":   0.0035,
    "TFP":     0.0064,
    "TNE":     0.0102,
    "Hybrid":  0.0063,
    "QKS\n(quantum)": qks_ext["kernel_std_auc"]["quantum"],
    "QKS\n(RBF)":     qks_ext["kernel_std_auc"]["rbf"],
}
ext_err = [ext_std[m] for m in methods]

# Colors
colors_int = ["#2166ac", "#4393c3", "#92c5de", "#d1e5f0", "#1b7837", "#5aae61"]
colors_ext = ["#b2182b", "#d6604d", "#f4a582", "#fddbc7", "#762a83", "#9970ab"]

x = np.arange(len(methods))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
bars_int = ax.bar(x - width/2, int_vals, width, label="Internal (n = 19,836/19,849)",
                  color=colors_int, edgecolor="black", linewidth=0.5)
bars_ext = ax.bar(x + width/2, ext_vals, width, label="External (n = 22,447)",
                  color=colors_ext, edgecolor="black", linewidth=0.5, yerr=ext_err,
                  capsize=3)

ax.set_ylabel("AUC-ROC", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=10)
ax.set_ylim(0.55, 1.02)
ax.legend(fontsize=10, loc="lower left")
ax.axhline(y=0.5, color="gray", linestyle="--", linewidth=0.5, alpha=0.5)
ax.set_title("Internal vs External Validation: Descriptor and Kernel Performance",
             fontsize=12, fontweight="bold")

# Add value labels on bars
for bar in bars_int:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.005, f"{h:.3f}",
            ha="center", va="bottom", fontsize=7, fontweight="bold")
for bar in bars_ext:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.005, f"{h:.3f}",
            ha="center", va="bottom", fontsize=7, fontweight="bold")

plt.tight_layout()
out = FIG / "p3_extval_internal_vs_external.png"
FIG.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=300, bbox_inches="tight")
print(f"Saved: {out}")
