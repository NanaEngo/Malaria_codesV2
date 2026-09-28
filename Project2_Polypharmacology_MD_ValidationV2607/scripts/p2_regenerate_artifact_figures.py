#!/usr/bin/env python3
"""Regenerate the remaining V2609C manuscript figures from canonical artifacts.

Provenance (all values read from committed artifacts, no hardcoded data):
  fig_crossmetric  <- results/cross_metric_statistical_audit.json
                      (analysis_set=complete_two_target_12; n=12 primary estimand)
  fig_rmsd_main    <- results/figures/rmsd_real/*.xvg (gmx rms on the
                      canonical 10 ns R1 trajectories, groups Backbone/MOL0,
                      fit=Backbone -- same protocol as DAR §9)
  fig_violin       <- results/c_rrs_classification.csv (RRS_mean per candidate)
  fig_radar        <- results/c_rrs_classification.csv (per-mutant RRS columns;
                      two panels = PfDHFR and PfCRT estimands, no PfATP4/PfClpP
                      axis -- those targets have no mutant RRS in Set C)
  fig_rmsf_214     <- results/md_results/214_PfCRT_{rmsf,gyrate}.xvg (real
                      parent-study GROMACS outputs)
  fig_rmsd_214_438 <- results/md_results/{214_PfCRT,438_PfATP4}_backbone_rmsd.xvg

Outputs are written to manuscript/V2609C/Graphics/ (+ .png) and a manifest is
recorded under results/figures/figure_provenance_20260928.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
GRAPH = ROOT / "manuscript" / "V2609C" / "Graphics"
GRAPH.mkdir(parents=True, exist_ok=True)
manifest: dict = {"generated": "2026-09-28", "figures": {}}

plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
                     "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9})


def _save(fig, name: str, source: str) -> None:
    fig.savefig(GRAPH / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(GRAPH / f"{name}.png", bbox_inches="tight", dpi=300)
    plt.close(fig)
    manifest["figures"][name] = source
    print(f"  [OK] {name}")


# ---------------------------------------------------------------- fig: crossmetric
def fig_crossmetric() -> None:
    data = json.loads((RES / "cross_metric_statistical_audit.json").read_text())
    prim = [r for r in data["records"] if r["analysis_set"] == "complete_two_target_12"]
    comparisons = ["PNS_vs_RRS", "ACSI_vs_RRS", "ACSI_vs_PNS", "RRS_vs_WT_anchor_min"]
    rho = {r["comparison"]: r["spearman_rho"] for r in prim}
    bonf = {r["comparison"]: r["bonferroni_p_three_hypotheses"] for r in prim}
    labels = {"PNS_vs_RRS": "PNS–RRS", "ACSI_vs_RRS": "ACSI–RRS",
              "ACSI_vs_PNS": "ACSI–PNS", "RRS_vs_WT_anchor_min": "RRS–WT anchor"}
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    keys = [c for c in comparisons if c in rho]
    vals = [rho[k] for k in keys]
    colors = ["#1f77b4" if bonf[k] < 0.05 else "#7f7f7f" for k in keys]
    ax.barh(range(len(keys)), vals, color=colors, edgecolor="black", linewidth=0.6)
    ax.set_yticks(range(len(keys)), [labels[k] for k in keys])
    for i, (k, v) in enumerate(zip(keys, vals)):
        star = " *" if bonf[k] < 0.05 else ""
        ax.text(v - 0.03, i, f"{v:.3f}{star}", va="center",
                ha="right" if v < 0 else "left", fontsize=8)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlim(-0.75, 0.35)
    ax.set_xlabel("Spearman ρ (complete two-target panel, n = 12; * p_adj < 0.05)")
    fig.tight_layout()
    _save(fig, "cross_metric_correlation",
          "results/cross_metric_statistical_audit.json (complete_two_target_12)")


# ---------------------------------------------------------------- fig: RMSD main
def _read_xvg(path: Path) -> tuple[np.ndarray, np.ndarray]:
    t, y = [], []
    for line in path.read_text().splitlines():
        if line.startswith(("#", "@")):
            continue
        parts = line.split()
        if len(parts) >= 2:
            t.append(float(parts[0])); y.append(float(parts[1]))
    return np.asarray(t), np.asarray(y)


def fig_rmsd_main() -> None:
    sysmap = [("PP-01_PfDHFR_WT", "PfDHFR-WT"), ("PP-01_PfDHFR_N51I", "PfDHFR-N51I"),
              ("PP-01_PfCRT_WT", "PfCRT-WT"), ("PP-01_PfCRT_K76T", "PfCRT-K76T")]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=False)
    panels = [("(A) PfDHFR complexes (PP-01)", ["PP-01_PfDHFR_WT", "PP-01_PfDHFR_N51I"],
               ["PfDHFR-WT", "PfDHFR-N51I"]),
              ("(B) PfCRT complexes (PP-01)", ["PP-01_PfCRT_WT", "PP-01_PfCRT_K76T"],
               ["PfCRT-WT", "PfCRT-K76T"])]
    for ax, (title, syss, lbls) in zip(axes, panels):
        for k, (s, lbl) in enumerate(zip(syss, lbls)):
            tb, yb = _read_xvg(RES / "figures/rmsd_real" / f"{s}_backbone.xvg")
            tl, yl = _read_xvg(RES / "figures/rmsd_real" / f"{s}_ligand.xvg")
            solid = k == 0
            ax.plot(tb / 1000.0, yb, color=["#1f77b4", "#ff7f0e"][k], lw=1.1,
                    ls="-" if solid else "--", label=f"{lbl} backbone")
            ax.plot(tl / 1000.0, yl, color=["#2ca02c", "#d62728"][k], lw=0.9,
                    ls="-" if solid else ":", label=f"{lbl} ligand")
        ax.set_title(title, fontweight="bold", fontsize=9)
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("RMSD (nm)")
        ax.legend(fontsize=6.5, frameon=True)
    fig.tight_layout()
    _save(fig, "Figure3_RMSD_Stability", "results/figures/rmsd_real/*.xvg (gmx rms, R1 trajectories)")


# ---------------------------------------------------------------- fig: violin
def fig_violin() -> None:
    df = pd.read_csv(RES / "c_rrs_classification.csv")
    col = "RRS_mean"  # pooled available-target estimand (matches Table S15 bootstrap)
    df = df.dropna(subset=[col])
    groups = {c: df.loc[df["RRS_class"] == c, col].values for c in ["A*", "A", "B", "C", "D"]}
    groups = {k: v for k, v in groups.items() if len(v) > 0}
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    parts = ax.violinplot(list(groups.values()), showmedians=True)
    for body in parts["bodies"]:
        body.set_alpha(0.6)
    ax.set_xticks(range(1, len(groups) + 1), list(groups.keys()))
    for i, (cls, vals) in enumerate(groups.items(), start=1):
        ax.scatter(np.full(len(vals), i), vals, s=14, color="black", zorder=3)
    ax.set_ylabel("RRS (%)")
    ax.set_xlabel("Triage class (pooled available-target estimand)")
    fig.tight_layout()
    _save(fig, "h1_rrs_class_violin", "results/c_rrs_classification.csv (RRS_mean)")


# ---------------------------------------------------------------- fig: radar
def fig_radar() -> None:
    df = pd.read_csv(RES / "c_rrs_classification.csv")
    cols = ["RRS_PfDHFR_N51I", "RRS_PfDHFR_C59R", "RRS_PfDHFR_S108N", "RRS_PfDHFR_I164L"]
    labels = ["N51I", "C59R", "S108N", "I164L"]
    show = ["PP-01", "PP-15", "PP-07", "PP-14"]  # A*, A, B, D of the two-target set
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), subplot_kw=dict(polar=True))
    for ax, (tgt, ccols, clabels) in zip(
            axes,
            [("PfDHFR", cols, labels),
             ("PfCRT", ["RRS_PfCRT_K76T", "RRS_PfCRT_K76A"], ["K76T", "K76A"])]):
        angles = np.linspace(0, 2 * np.pi, len(ccols), endpoint=False).tolist()
        angles += angles[:1]
        for cand in show:
            row = df[df["candidate_id"] == cand].iloc[0]
            vals = [row[c] for c in ccols]
            if any(pd.isna(v) for v in vals):
                continue
            vals += vals[:1]
            ax.plot(angles, vals, lw=1.4, label=cand)
            ax.fill(angles, vals, alpha=0.08)
        ax.set_xticks(angles[:-1], clabels)
        ax.set_title(f"{tgt} mutants", fontsize=9, fontweight="bold", pad=12)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=7)
    fig.suptitle("Per-mutant RRS profiles (docking estimand)", fontsize=10)
    fig.tight_layout()
    _save(fig, "rrs_radar_profiles", "results/c_rrs_classification.csv (per-mutant RRS)")


# ---------------------------------------------------------------- fig: RMSF 214
def fig_rmsf_214() -> None:
    t, rmsf = _read_xvg(RES / "md_results/214_PfCRT_rmsf.xvg")
    ty, gy = _read_xvg(RES / "md_results/214_PfCRT_gyrate.xvg")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    axes[0].plot(t, rmsf, lw=0.8, color="#1f77b4")
    axes[0].axvspan(14, 18, color="yellow", alpha=0.3, label="Tyr16 region")
    axes[0].legend(fontsize=7)
    axes[0].set_xlabel("Residue")
    axes[0].set_ylabel("RMSF (nm)")
    axes[0].set_title("(A) PfCRT-WT backbone RMSF (ligand 214)", fontweight="bold", fontsize=9)
    axes[1].plot(ty / 1000.0, gy[:, 0] if gy.ndim > 1 else gy, lw=0.9, color="#9467bd")
    axes[1].set_xlabel("Time (ns)")
    axes[1].set_ylabel("R_g (nm)")
    axes[1].set_title("(B) Radius of gyration", fontweight="bold", fontsize=9)
    fig.tight_layout()
    _save(fig, "214_PfCRT_rmsf_contacts", "results/md_results/214_PfCRT_{rmsf,gyrate}.xvg")


# ------------------------------------------------- fig: RMSD panels 214 / 438
def fig_rmsd_214_438() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, (pdb, tgt, col) in zip(axes, [("214", "PfCRT", "#9467bd"),
                                          ("438", "PfATP4", "#8c564b")]):
        t, y = _read_xvg(RES / "md_results" / f"{pdb}_{tgt}_backbone_rmsd.xvg")
        ax.plot(t / 1000.0, y, lw=0.9, color=col)
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("Backbone RMSD (nm)")
        ax.set_title(f"{tgt}-WT (ligand {pdb})", fontweight="bold", fontsize=9)
    fig.tight_layout()
    _save(fig, "214_PfCRT_rmsd_panel", "results/md_results/214_PfCRT_backbone_rmsd.xvg")
    _save(fig, "438_PfATP4_mdanalysis_rmsd_panel",
          "results/md_results/438_PfATP4_backbone_rmsd.xvg")


def main() -> None:
    fig_crossmetric()
    fig_rmsd_main()
    fig_violin()
    fig_radar()
    fig_rmsf_214()
    fig_rmsd_214_438()
    out = RES / "figures" / "figure_provenance_20260928.json"
    out.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest: {out}")


if __name__ == "__main__":
    main()
