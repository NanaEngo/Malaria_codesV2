#!/usr/bin/env python3
"""
P7 Manuscript Figures 3–5 — Publication-quality PDF generation.

Produces three figures from canonical DAR results (no HPO data required):

    Fig 3 — Phase 4 ROC curves (5-fold CV, ECFP4-RBF vs QFE 4q-d1-rzz)
    Fig 4 — Phase 4 ablation bar chart (4q / 6q / 8q AUC comparison)
    Fig 5 — Phase 5 scaffold-split panel: AUC comparison + gradient norm distribution

Output directory: manuscript/figures/
Each figure is saved as both PDF (vector, for LaTeX) and PNG (300 dpi, for review).

Provenance: all data read from canonical DAR result CSVs / JSONs.
No recomputation; this script is display-only.

Usage (from Project7_Quantum_Molecular_Encoding_QML/ root):
    conda run -n malaria_qml_hybrid python scripts/p7_generate_figures.py

Author: Myke Vital Sao Temgoua
Date:   2026-10-05
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # non-interactive, PDF-safe backend
import matplotlib.ticker
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import pandas as pd

# ── Path setup ─────────────────────────────────────────────────────────────────
PROJ    = Path(__file__).resolve().parent.parent   # Project7_Quantum_Molecular_Encoding_QML/
RESULTS = PROJ / "results"
FIGS    = PROJ / "manuscript" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

# ── Global style ───────────────────────────────────────────────────────────────
# ACS-compatible: sans-serif, 8 pt base, clean spines
plt.rcParams.update({
    "font.family":         "sans-serif",
    "font.sans-serif":     ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size":           8,
    "axes.labelsize":      8,
    "axes.titlesize":      8,
    "xtick.labelsize":     7,
    "ytick.labelsize":     7,
    "legend.fontsize":     7,
    "legend.framealpha":   0.88,
    "legend.edgecolor":    "0.75",
    "axes.linewidth":      0.8,
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "xtick.major.width":   0.8,
    "ytick.major.width":   0.8,
    "lines.linewidth":     1.0,
    "grid.linewidth":      0.5,
    "grid.alpha":          0.35,
    "savefig.dpi":         300,
    "savefig.bbox":        "tight",
    "savefig.pad_inches":  0.05,
})

# Colour palette (colour-blind safe; consistent with P2/P3 figures)
C_ECFP4  = "#2166AC"   # blue   — classical ECFP4
C_QFE    = "#D6604D"   # red    — QFE 4q canonical
C_QFE6   = "#F4A582"   # orange — 6-qubit
C_QFE8   = "#B2182B"   # dark-red — 8-qubit
C_REF    = "#636363"   # grey   — P3 canonical reference
C_CHANCE = "#BBBBBB"   # light grey — chance diagonal


def save_fig(fig: plt.Figure, stem: str) -> None:
    """Save figure as PDF + PNG into manuscript/figures/."""
    for ext in ("pdf", "png"):
        path = FIGS / f"{stem}.{ext}"
        fig.savefig(path)
        print(f"  Saved: {path}")


def load_summary(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_auc_from_summary(path: Path) -> tuple[float, float]:
    """Return (mean_auc, std_auc) from a canonical summary JSON."""
    d = load_summary(path)
    return d["results"]["mean_auc"], d["results"]["std_auc"]


# ══════════════════════════════════════════════════════════════════════════════
# Figure 3 — Phase 4 ROC curves (5-fold CV)
# ══════════════════════════════════════════════════════════════════════════════

def figure3_roc_curves() -> None:
    """
    Fig 3: Per-fold AUC strip plot for Phase 4 5-fold CV (P3 subsample n=1000).

    Left panel:  all 5 fold AUCs for ECFP4-RBF and QFE 4q, shown as individual
                 dots with mean ± SD bars. P3 canonical and QKS reference lines.
    Right panel: Phase 1 LOO-CV AUCs (per-molecule LOO predictions → ROC AUC)
                 for ECFP4-MLP, GIN, and QFE — from phase1 summary data.

    Note: Phase 4 benchmark CSVs store one aggregate row per fold (no per-sample
    scores), so per-fold AUCs from the summary JSONs are the finest granularity
    available.  This strip chart is the scientifically correct visualisation.
    """
    print("[Fig 3] Per-fold AUC strip chart — Phase 4 5-fold CV + Phase 1 LOO")

    # ── Phase 4 data ─────────────────────────────────────────────────────────
    ecfp4_sum = load_summary(
        RESULTS / "phase2_benchmark" / "ecfp4_rbf_p3sub1000_cv5_summary.json")
    qfe_sum   = load_summary(
        RESULTS / "phase2_benchmark" / "qfe_4q_d1_p3sub1000_cv5_summary.json")

    ecfp4_fold_aucs = np.array([r["auc"] for r in ecfp4_sum["results"]["per_fold"]])
    qfe_fold_aucs   = np.array([r["auc"] for r in qfe_sum["results"]["per_fold"]])
    ecfp4_mean, ecfp4_std = ecfp4_sum["results"]["mean_auc"], ecfp4_sum["results"]["std_auc"]
    qfe_mean,   qfe_std   = qfe_sum["results"]["mean_auc"],   qfe_sum["results"]["std_auc"]

    # P3 canonical references
    P3_ECFP4 = 0.9475
    P3_QKS   = 0.8385

    # ── Phase 1 data (LOO-CV per-sample scores → individual AUC per fold) ─────
    # Phase 1 LOO results: fold = molecule index, y_true, y_pred (probability)
    ecfp4_loo = pd.read_csv(
        RESULTS / "phase1_proof_of_concept" / "ecfp4_mlp_loo_results.csv")
    qfe_loo   = pd.read_csv(
        RESULTS / "phase1_proof_of_concept" / "qfe_4q_d1_loo_results.csv")

    # Phase 1 summary AUCs
    with open(RESULTS / "phase1_proof_of_concept" / "ecfp4_mlp_loo_summary.json") as f:
        ecfp4_loo_sum = json.load(f)
    with open(RESULTS / "phase1_proof_of_concept" / "qfe_4q_d1_loo_summary.json") as f:
        qfe_loo_sum = json.load(f)

    # GIN summary
    with open(RESULTS / "phase1_proof_of_concept" / "gnn_loo_summary.json") as f:
        gnn_loo_sum = json.load(f)

    ecfp4_loo_auc = ecfp4_loo_sum["metrics"]["auc"]
    qfe_loo_auc   = qfe_loo_sum["metrics"]["auc"]
    gnn_loo_auc   = gnn_loo_sum["metrics"]["auc"]

    # ── Plot layout: 1 × 2 ───────────────────────────────────────────────────
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(7.0, 3.2))
    fig.subplots_adjust(wspace=0.32)

    fold_colors = ["#4393C3", "#74ADD1", "#ABD9E9", "#FEE090", "#FDAE61"]
    jitter = 0.08   # horizontal jitter for dot visibility

    # ── LEFT: Phase 4 strip chart ──────────────────────────────────────────────
    for xi, (fold_aucs, mean_auc, std_auc, color, label) in enumerate([
        (ecfp4_fold_aucs, ecfp4_mean, ecfp4_std, C_ECFP4, "ECFP4-RBF"),
        (qfe_fold_aucs,   qfe_mean,   qfe_std,   C_QFE,   "QFE 4q"),
    ]):
        xs = xi + np.random.default_rng(seed=42).uniform(-jitter, jitter,
                                                          size=len(fold_aucs))
        # Individual fold dots
        ax_l.scatter(xs, fold_aucs, color=fold_colors[:len(fold_aucs)],
                     s=28, zorder=4, edgecolors=color, linewidths=0.5)

        # Mean ± SD error bar
        ax_l.errorbar(xi, mean_auc, yerr=std_auc,
                      fmt="D", color=color, ms=7, capsize=5, capthick=1.2,
                      elinewidth=1.2, zorder=5,
                      label=f"{label}\n{mean_auc:.4f} ± {std_auc:.4f}")

    # Reference lines
    ax_l.axhline(P3_ECFP4, color=C_ECFP4, ls="--", lw=0.9, alpha=0.55,
                 label=f"P3 canonical ECFP4 ({P3_ECFP4})")
    ax_l.axhline(P3_QKS,   color=C_REF,   ls=":",  lw=0.9, alpha=0.65,
                 label=f"P3 canonical QKS ({P3_QKS})")

    ax_l.set_xticks([0, 1])
    ax_l.set_xticklabels(["ECFP4-RBF", "QFE 4q-d1-RZZ"], fontsize=7.5)
    ax_l.set_ylabel("AUC-ROC")
    ax_l.set_ylim(0.76, 0.97)
    ax_l.set_xlim(-0.55, 1.55)
    ax_l.grid(True, axis="y", alpha=0.35)
    ax_l.legend(loc="lower right", fontsize=6.0,
                handlelength=1.3, handletextpad=0.4, labelspacing=0.4)
    ax_l.set_title("(A) Phase 4 — 5-fold CV ($n=1000$)", fontsize=8, pad=4)

    # Scenario B annotation
    ax_l.annotate("Scenario B", xy=(0.5, (ecfp4_mean + qfe_mean) / 2),
                  xytext=(0.5, 0.795), ha="center", fontsize=6.5,
                  color="#666666", style="italic",
                  arrowprops=dict(arrowstyle="->", color="#999999", lw=0.6))

    # ── RIGHT: Phase 1 LOO bar chart ──────────────────────────────────────────
    ph1_labels = ["ECFP4-MLP", "GIN\n(3-layer)", "QFE 4q\n(canonical)"]
    ph1_aucs   = [ecfp4_loo_auc, gnn_loo_auc, qfe_loo_auc]
    ph1_colors = [C_ECFP4, C_REF, C_QFE]
    ph1_hatches= ["", "///", ""]

    x = np.arange(len(ph1_labels))
    bars = ax_r.bar(x, ph1_aucs, 0.50, color=ph1_colors, hatch=ph1_hatches,
                    edgecolor="white", lw=0.5, zorder=3, alpha=0.85)

    for bar, a in zip(bars, ph1_aucs):
        ax_r.text(bar.get_x() + bar.get_width() / 2.0, a + 0.008,
                  f"{a:.3f}", ha="center", va="bottom", fontsize=7,
                  color="#222222")

    # GIN caution annotation
    ax_r.text(1, gnn_loo_auc - 0.03, "⚠ overfitting\n($n$=17)",
              ha="center", va="top", fontsize=5.5, color="#888888",
              style="italic")

    ax_r.set_xticks(x)
    ax_r.set_xticklabels(ph1_labels, fontsize=7)
    ax_r.set_ylabel("AUC-ROC (LOO-CV)")
    ax_r.set_ylim(0.75, 1.10)
    ax_r.axhline(1.0, color="#BBBBBB", ls="--", lw=0.7, alpha=0.6)
    ax_r.grid(True, axis="y", alpha=0.35)
    ax_r.set_title("(B) Phase 1 PoC — LOO-CV ($n=17$)", fontsize=8, pad=4)
    ax_r.text(0.97, 0.06, "n=17: underpowered;\nAUC only indicative",
              transform=ax_r.transAxes, ha="right", va="bottom",
              fontsize=6, color="#888888", style="italic",
              bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                        edgecolor="#BBBBBB", alpha=0.85, lw=0.6))

    fig.suptitle(
        "Figure 3.  Phase 4 five-fold CV AUC (left) and Phase 1 PoC LOO-CV (right)",
        fontsize=8, y=1.01)
    save_fig(fig, "fig3_roc_curves")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Figure 4 — Phase 4 ablation bar chart (4q / 6q / 8q)
# ══════════════════════════════════════════════════════════════════════════════

def figure4_ablation_bar() -> None:
    """
    Fig 4: Grouped bar chart comparing ECFP4-RBF and QFE 4q/6q/8q AUC
    on the P3 subsample (n=1000, 5-fold CV).
    Error bars = ±1 SD.  Horizontal reference lines for P3 canonical
    ECFP4 (0.9475) and P3 QKS (0.8385).
    Decision gate at 0.80 × 0.9475 = 0.758.
    """
    print("[Fig 4] Ablation bar chart")

    ecfp4_auc, ecfp4_std = load_auc_from_summary(
        RESULTS / "phase2_benchmark" / "ecfp4_rbf_p3sub1000_cv5_summary.json")
    qfe4_auc, qfe4_std   = load_auc_from_summary(
        RESULTS / "phase2_benchmark" / "qfe_4q_d1_p3sub1000_cv5_summary.json")
    qfe6_auc, qfe6_std   = load_auc_from_summary(
        RESULTS / "phase2_benchmark" / "qfe_6q_d1_p3sub1000_cv5_summary.json")
    qfe8_auc, qfe8_std   = load_auc_from_summary(
        RESULTS / "phase2_benchmark" / "qfe_8q_d1_p3sub1000_cv5_summary.json")

    P3_ECFP4 = 0.9475
    P3_QKS   = 0.8385
    GATE     = 0.80 * P3_ECFP4   # 0.758

    labels  = ["ECFP4-RBF\n(local, $n$=1000)", "QFE 4q\n(canonical)",
               "QFE 6q", "QFE 8q"]
    aucs    = [ecfp4_auc,  qfe4_auc,  qfe6_auc,  qfe8_auc]
    stds    = [ecfp4_std,  qfe4_std,  qfe6_std,  qfe8_std]
    colors  = [C_ECFP4,    C_QFE,     C_QFE6,    C_QFE8]
    hatches = ["",         "",        "///",      "xxx"]

    x = np.arange(len(labels))
    bar_w = 0.52

    fig, ax = plt.subplots(figsize=(4.8, 3.4))

    bars = ax.bar(x, aucs, bar_w, yerr=stds,
                  color=colors, hatch=hatches,
                  edgecolor="white", linewidth=0.6,
                  error_kw=dict(elinewidth=0.9, capsize=3.5,
                                capthick=0.9, ecolor="#444444"),
                  zorder=3)

    # AUC value labels above each bar
    for bar, a, s in zip(bars, aucs, stds):
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                a + s + 0.004,
                f"{a:.4f}", ha="center", va="bottom",
                fontsize=6.2, color="#222222")

    # Reference lines
    ax.axhline(P3_ECFP4, color=C_ECFP4, ls="--", lw=0.9, alpha=0.60, zorder=2,
               label=f"P3 canonical ECFP4-RBF ({P3_ECFP4})")
    ax.axhline(P3_QKS, color=C_REF, ls=":", lw=0.9, alpha=0.70, zorder=2,
               label=f"P3 canonical QKS ({P3_QKS})")
    ax.axhline(GATE, color="#B87333", ls="-.", lw=0.8, alpha=0.55, zorder=2,
               label=f"Decision gate (×0.80 = {GATE:.3f})")

    # Scenario B label
    ax.text(0.97, 0.55,
            "Scenario B:\ncompetitive, not superior",
            transform=ax.transAxes, ha="right", va="center",
            fontsize=6.5, color="#666666", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow",
                      edgecolor="#CCCC88", alpha=0.9, lw=0.6))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("AUC-ROC (mean ± SD, 5-fold CV)")
    ax.set_ylim(0.70, 0.98)
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.01))
    ax.grid(True, axis="y", which="major", zorder=0)
    ax.grid(True, axis="y", which="minor", alpha=0.15, zorder=0)
    ax.legend(loc="lower left", fontsize=6.2,
              handlelength=1.5, handletextpad=0.4, borderpad=0.5)
    ax.set_title("Figure 4.  Ablation: qubit count (P3 subsample, $n=1000$)",
                 fontsize=8, pad=4)

    save_fig(fig, "fig4_ablation_bar")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Figure 5 — Phase 5 scaffold-split AUC + gradient norms (2-panel)
# ══════════════════════════════════════════════════════════════════════════════

def figure5_scaffold_gradient() -> None:
    """
    Fig 5: Two-panel figure.
      Panel A (left):  Phase 4 vs Phase 5 AUC comparison per method.
                       Arrows show generalisation drop under scaffold novelty.
      Panel B (right): QFE gradient norm distribution (Phase 4 vs Phase 5)
                       as overlapping histograms; barren-plateau threshold marked.
    """
    print("[Fig 5] Scaffold-split AUC + gradient norms")

    # ── Panel A data ──────────────────────────────────────────────────────────
    ecfp4_cv_sum   = load_summary(
        RESULTS / "phase2_benchmark" / "ecfp4_rbf_p3sub1000_cv5_summary.json")
    qfe_cv_sum     = load_summary(
        RESULTS / "phase2_benchmark" / "qfe_4q_d1_p3sub1000_cv5_summary.json")
    ecfp4_scaf_sum = load_summary(
        RESULTS / "phase3_scaffold"  / "ecfp4_rbf_ext10k_scaffold_summary.json")
    qfe_scaf_sum   = load_summary(
        RESULTS / "phase3_scaffold"  / "qfe_4q_d1_ext10k_scaffold_summary.json")

    ecfp4_cv_auc   = ecfp4_cv_sum["results"]["mean_auc"]
    ecfp4_cv_std   = ecfp4_cv_sum["results"]["std_auc"]
    qfe_cv_auc     = qfe_cv_sum["results"]["mean_auc"]
    qfe_cv_std     = qfe_cv_sum["results"]["std_auc"]
    ecfp4_scaf_auc = ecfp4_scaf_sum["results"]["auc"]
    qfe_scaf_auc   = qfe_scaf_sum["results"]["auc"]
    P3_CANONICAL   = 0.9475

    # ── Panel B data ──────────────────────────────────────────────────────────
    gn4 = pd.read_csv(
        RESULTS / "phase2_benchmark" / "qfe_4q_d1_p3sub1000_cv5_gradient_norms.csv")
    gn5 = pd.read_csv(
        RESULTS / "phase3_scaffold"  / "qfe_4q_d1_ext10k_scaffold_gradient_norms.csv")

    # Phase 4: cols fold, epoch, grad_norm → all values across all folds
    g4_vals = gn4["grad_norm"].values
    # Phase 5: cols step, grad_norm
    g5_vals = gn5["grad_norm"].values

    BP_THRESH = 1e-6
    bp4 = 100.0 * (g4_vals < BP_THRESH).mean()
    bp5 = 100.0 * (g5_vals < BP_THRESH).mean()

    # ── Plot ─────────────────────────────────────────────────────────────────
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.2, 3.3))
    fig.subplots_adjust(wspace=0.30)

    # ── Panel A: AUC comparison across phases ─────────────────────────────────
    # x positions: ECFP4-P4, QFE-P4 in group 1; ECFP4-P5, QFE-P5 in group 2
    group_gap = 0.20   # gap between P4 and P5 groups
    bar_w = 0.32

    x_e4 = 0.0
    x_q4 = bar_w + 0.06
    x_e5 = x_q4 + bar_w + group_gap
    x_q5 = x_e5 + bar_w + 0.06

    ax_a.bar(x_e4, ecfp4_cv_auc, bar_w, yerr=ecfp4_cv_std,
             color=C_ECFP4, alpha=0.90, edgecolor="white", lw=0.5,
             error_kw=dict(elinewidth=0.9, capsize=3, capthick=0.9,
                           ecolor="#333333"), zorder=3,
             label="ECFP4-RBF SVM")
    ax_a.bar(x_q4, qfe_cv_auc, bar_w, yerr=qfe_cv_std,
             color=C_QFE, alpha=0.90, edgecolor="white", lw=0.5,
             error_kw=dict(elinewidth=0.9, capsize=3, capthick=0.9,
                           ecolor="#333333"), zorder=3,
             label="QFE 4q-d1-RZZ")
    ax_a.bar(x_e5, ecfp4_scaf_auc, bar_w,
             color=C_ECFP4, alpha=0.50, hatch="///", edgecolor="white",
             lw=0.5, zorder=3)
    ax_a.bar(x_q5, qfe_scaf_auc, bar_w,
             color=C_QFE, alpha=0.50, hatch="///", edgecolor="white",
             lw=0.5, zorder=3)

    # Δ arrows (Phase 4 → Phase 5) and labels
    for x4, x5, v4, v5, col in [
        (x_e4, x_e5, ecfp4_cv_auc, ecfp4_scaf_auc, C_ECFP4),
        (x_q4, x_q5, qfe_cv_auc,   qfe_scaf_auc,   C_QFE),
    ]:
        cx4 = x4 + bar_w / 2
        cx5 = x5 + bar_w / 2
        ax_a.annotate(
            "", xy=(cx5, v5 + 0.003), xytext=(cx4, v4 - 0.003),
            arrowprops=dict(arrowstyle="-|>", color=col,
                            lw=0.85, shrinkA=2, shrinkB=2))
        mid_x = (cx4 + cx5) / 2 + 0.03
        mid_y = (v4 + v5) / 2
        ax_a.text(mid_x, mid_y, f"Δ={v5-v4:+.3f}",
                  fontsize=6.2, color=col, ha="left", va="center",
                  rotation=90, rotation_mode="anchor")

    # P3 canonical reference line
    ax_a.axhline(P3_CANONICAL, color=C_ECFP4, ls="--", lw=0.8, alpha=0.50,
                 zorder=2, label=f"P3 canonical ECFP4 ({P3_CANONICAL})")

    # x-axis labels & group labels
    xticks = [x_e4 + bar_w/2, x_q4 + bar_w/2,
              x_e5 + bar_w/2, x_q5 + bar_w/2]
    ax_a.set_xticks(xticks)
    ax_a.set_xticklabels(["ECFP4", "QFE", "ECFP4", "QFE"], fontsize=6.5)

    # Group labels below
    mid_p4 = (x_e4 + x_q4 + bar_w) / 2
    mid_p5 = (x_e5 + x_q5 + bar_w) / 2
    y_label = ax_a.get_ylim()[0] - 0.028
    ax_a.text(mid_p4, y_label, "Phase 4\n(5-fold CV, $n$=1000)",
              ha="center", va="top", fontsize=6.2, color="#333333")
    ax_a.text(mid_p5, y_label, "Phase 5\n(scaffold split, $n$=10 000)",
              ha="center", va="top", fontsize=6.2, color="#333333")
    ax_a.axvline((x_q4 + bar_w + x_e5) / 2, color="#BBBBBB",
                 ls="--", lw=0.6, alpha=0.6, zorder=1)

    ax_a.set_ylabel("AUC-ROC")
    ax_a.set_ylim(0.70, 0.98)
    ax_a.margins(x=0.06)
    ax_a.grid(True, axis="y", zorder=0)
    ax_a.legend(loc="upper right", fontsize=6.2,
                handlelength=1.4, handletextpad=0.4)
    ax_a.set_title("(A) Phase 4 → Phase 5 generalisation", fontsize=8, pad=4)

    # ── Panel B: Gradient norm distributions ──────────────────────────────────
    # Clip display at 2.0 (long tail); show overflow note
    CLIP = 2.0
    bins = np.linspace(0, CLIP, 45)

    g4_clip = np.clip(g4_vals, 0, CLIP)
    g5_clip = np.clip(g5_vals, 0, CLIP)

    # Phase 4 stats
    p4_mean = g4_vals.mean()
    p5_mean = g5_vals.mean()

    ax_b.hist(g4_clip, bins=bins, density=True, alpha=0.55, color=C_ECFP4,
              zorder=3,
              label=(f"Phase 4  ($n_{{train}}$=800)\n"
                     f"mean={p4_mean:.3f},  bp={bp4:.1f}%"))
    ax_b.hist(g5_clip, bins=bins, density=True, alpha=0.45, color=C_QFE,
              zorder=3,
              label=(f"Phase 5  ($n_{{train}}$=8000)\n"
                     f"mean={p5_mean:.3f},  bp={bp5:.1f}%"))

    # Barren-plateau threshold line
    ax_b.axvline(BP_THRESH, color="#B87333", ls="-.", lw=0.9, alpha=0.75,
                 zorder=4,
                 label=f"bp threshold ($10^{{-6}}$)")

    # Clip overflow note
    ylim_top = ax_b.get_ylim()[1] if ax_b.get_ylim()[1] > 0 else 5
    ax_b.text(CLIP * 0.97, ylim_top * 0.97,
              f"→ tail clipped at {CLIP}",
              ha="right", va="top", fontsize=5.5,
              color="#666666", style="italic")

    ax_b.set_xlabel(r"Gradient norm $\|\nabla_\theta\mathcal{L}\|$")
    ax_b.set_ylabel("Density")
    ax_b.set_xlim(-0.01, CLIP + 0.01)
    ax_b.legend(loc="upper right", fontsize=6,
                handlelength=1.4, handletextpad=0.4, labelspacing=0.4)
    ax_b.grid(True, axis="y", zorder=0)
    ax_b.set_title("(B) QFE gradient norms — P4 vs P5", fontsize=8, pad=4)

    fig.suptitle(
        "Figure 5.  Phase 5 scaffold-split generalisation and gradient diagnostics",
        fontsize=8, y=1.01)
    save_fig(fig, "fig5_scaffold_gradient")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print(f"Output directory: {FIGS}\n")
    figure3_roc_curves();   print()
    figure4_ablation_bar(); print()
    figure5_scaffold_gradient(); print()
    print("All figures generated.\n")
    for f in sorted(FIGS.glob("fig[345]*")):
        print(f"  {f.name:50s}  {f.stat().st_size/1024:6.1f} KB")


if __name__ == "__main__":
    main()
