#!/usr/bin/env python3
"""
P4 — Plot the canonical merged Pareto front.

Reads Project4_Advanced_Monte_CarloV2607/results/pareto/merged_pareto_front.csv
and writes a publication-quality MPO-vs-SYBA scatter to
Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/Graphics/pareto_front.png.

The merged front contains the non-dominated solutions across all 20 independent
Pareto-MCTS seeds (4 molecules after cross-seed deduplication).
"""

from pathlib import Path

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

try:
    from matplotlib import colormaps as _colormaps
    _get_cmap = lambda name: _colormaps[name]  # type: ignore
except (ImportError, AttributeError):  # matplotlib < 3.6
    _get_cmap = lambda name: matplotlib.cm.get_cmap(name)

# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_DIR / "results" / "pareto" / "merged_pareto_front.csv"
OUT_PATH = PROJECT_DIR / "manuscript" / "LaTeX" / "Graphics" / "pareto_front.png"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "lines.linewidth": 1.2,
})


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Canonical Pareto CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    required = {"mpo", "syba", "sa", "rrs", "pns", "hypervolume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{CSV_PATH} is missing required columns: {missing}")

    fig, ax = plt.subplots(figsize=(5.0, 4.0))

    # Single colour normalisation across all points so the RRS scale is
    # comparable. Compute face colours from the viridis_r colormap.
    norm = plt.Normalize(df["rrs"].min(), df["rrs"].max())
    cmap = _get_cmap("viridis_r")
    df["rrs_colour"] = df["rrs"].apply(lambda x: cmap(norm(x)))

    # Encode RRS by colour and PNS by marker shape (SA is constant across the
    # four non-dominated solutions, so it is not used for visual encoding).
    marker_map = {0: "v", 1: "o"}
    pns_labels = {0: "PNS = 0", 1: "PNS = 1"}
    unknown_pns = set(df["pns"].unique()) - set(marker_map)
    if unknown_pns:
        raise ValueError(f"Unexpected PNS values in CSV: {unknown_pns}")
    for pns_val, sub in df.groupby("pns"):
        ax.scatter(
            sub["mpo"],
            sub["syba"],
            c=sub["rrs_colour"],
            s=120,
            marker=marker_map[int(pns_val)],
            edgecolors="black",
            linewidth=0.6,
            alpha=0.9,
            zorder=3,
            label=pns_labels[int(pns_val)],
        )

    # Invisible mappable for the colourbar (same data, single normalisation).
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array(df["rrs"])

    # Label each point P1–P4.
    for i, row in df.iterrows():
        ax.annotate(
            f"P{i + 1}",
            (row["mpo"], row["syba"]),
            fontsize=8,
            fontweight="bold",
            ha="center",
            va="center",
            color="white",
            zorder=4,
        )

    # Connect the points to emphasise the trade-off front.
    sorted_df = df.sort_values("mpo")
    ax.plot(
        sorted_df["mpo"],
        sorted_df["syba"],
        "k--",
        linewidth=0.8,
        alpha=0.5,
        label="Pareto frontier",
        zorder=1,
    )

    ax.set_xlabel("MPO score (maximise)", fontsize=10)
    ax.set_ylabel("SYBA score (maximise)", fontsize=10)
    hv = df["hypervolume"].iloc[0]
    assert df["hypervolume"].nunique() == 1, "Hypervolume values are not constant across rows"
    ax.set_title(
        f"Merged Pareto front ($n={len(df)}$ non-dominated solutions, HV={hv:.4f})",
        fontsize=11,
        fontweight="bold",
    )

    cbar = fig.colorbar(sm, ax=ax, shrink=0.75, pad=0.02)
    cbar.set_label("RRS (resistance resilience)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    ax.set_xlim(0.65, 1.00)
    ax.set_ylim(-0.05, 1.05)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.20))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.05))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=True, fancybox=False, edgecolor="grey", fontsize=8)

    fig.savefig(OUT_PATH)
    plt.close(fig)

    # Reproducibility sidecar
    from datetime import datetime, timezone

    sidecar = OUT_PATH.with_suffix(".sidecar.json")
    syba_recomputed = "syba_raw" in df.columns
    sidecar.write_text(
        json.dumps(
            {
                "script": Path(__file__).name,
                "generated_utc": datetime.now(timezone.utc).isoformat(),
                "input_csv": str(CSV_PATH.relative_to(PROJECT_DIR)),
                "output_png": str(OUT_PATH.relative_to(PROJECT_DIR)),
                "n_points": len(df),
                "hypervolume": float(hv),
                "columns": list(df.columns),
                "syba_recomputed": syba_recomputed,
                "syba_raw": df["syba_raw"].tolist() if syba_recomputed else None,
                "notes": (
                    "SYBA values were recomputed post-hoc with the lich/conda SYBA "
                    "classifier; the original Pareto run returned a constant fallback "
                    "of 0 because the SYBA classifier was not loaded."
                ),
            },
            indent=2,
        )
    )

    print(f"✅ Wrote {OUT_PATH}")
    print(f"✅ Wrote {sidecar}")


if __name__ == "__main__":
    main()
