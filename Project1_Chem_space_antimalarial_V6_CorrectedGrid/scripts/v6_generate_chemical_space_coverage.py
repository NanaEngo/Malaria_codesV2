#!/usr/bin/env python3
"""Generate the P1 V6 chemical-space coverage figure.

The figure is a descriptive paired comparison of maximum whole-molecule and
scaffold Morgan-fingerprint Tanimoto similarity in the locked 5,000-molecule
sample used by the P1 chemical-space analysis. It does not encode activity,
target preference, or a biological class.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
V6 = ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid"
SOURCE = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid" / "p1_scaffold_tanimoto.csv"
OUT = V6 / "results" / "figures"
GRAPHICS = V6 / "manuscript" / "Graphics"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    data = pd.read_csv(SOURCE)
    required = {"smiles", "max_tanimoto_whole", "max_tanimoto_scaffold"}
    if not required.issubset(data.columns):
        raise ValueError(f"Missing source columns: {sorted(required - set(data.columns))}")
    data = data.dropna(subset=["max_tanimoto_whole", "max_tanimoto_scaffold"]).copy()
    if len(data) != 5000:
        raise ValueError(f"Expected the locked 5,000-molecule sample, found {len(data)} rows")
    whole = data["max_tanimoto_whole"].to_numpy(float)
    scaffold = data["max_tanimoto_scaffold"].to_numpy(float)
    if ((whole < 0) | (whole > 1) | (scaffold < 0) | (scaffold > 1)).any():
        raise ValueError("Tanimoto values must lie in [0, 1]")

    OUT.mkdir(parents=True, exist_ok=True)
    GRAPHICS.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig = plt.figure(figsize=(10.0, 4.8), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0], wspace=0.28)
    ax = fig.add_subplot(gs[0, 0])
    ax.scatter(whole, scaffold, s=8, alpha=0.22, color="#2563eb", edgecolors="none", rasterized=True)
    ax.axvline(0.4, color="#dc2626", linestyle="--", linewidth=1.2)
    ax.axhline(0.4, color="#dc2626", linestyle="--", linewidth=1.2)
    ax.fill_between([0, 0.4], 0.4, 1.0, color="#047857", alpha=0.08, zorder=0)
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Maximum whole-molecule Tanimoto similarity")
    ax.set_ylabel("Maximum scaffold Tanimoto similarity")
    ax.set_title("Paired similarity profile", loc="left", fontweight="bold")
    ax.text(0.03, 0.96, "novel molecule /\nretained scaffold", transform=ax.transAxes,
            va="top", ha="left", fontsize=8, color="#047857",
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "none", "alpha": 0.85})
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color="#e5e7eb", linewidth=0.6, zorder=0)

    ax2 = fig.add_subplot(gs[0, 1])
    bins = np.linspace(0, 1, 26)
    ax2.hist(whole, bins=bins, density=True, alpha=0.60, color="#2563eb", label="Whole molecule")
    ax2.hist(scaffold, bins=bins, density=True, alpha=0.48, color="#047857", label="Scaffold")
    ax2.axvline(0.4, color="#dc2626", linestyle="--", linewidth=1.2, label="Novelty threshold")
    ax2.set_xlabel("Maximum Tanimoto similarity")
    ax2.set_ylabel("Density")
    ax2.set_title("Similarity distributions", loc="left", fontweight="bold")
    ax2.legend(frameon=False, fontsize=8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", color="#e5e7eb", linewidth=0.6)
    fig.suptitle("Chemical-space coverage: novelty at molecule level and scaffold retention",
                 fontsize=14, fontweight="bold", x=0.02, ha="left")
    fig.text(0.02, -0.02,
             "Locked sample n=5,000; dashed lines mark Tanimoto = 0.4. Similarity is structural, not biological activity.",
             ha="left", fontsize=8.5, color="#4b5563")

    outputs = []
    for ext in ("pdf", "png"):
        p = OUT / f"p1_v6_chemical_space_coverage.{ext}"
        fig.savefig(p, bbox_inches="tight", dpi=300, facecolor="white")
        g = GRAPHICS / p.name
        g.write_bytes(p.read_bytes())
        outputs.extend([str(p.relative_to(ROOT)), str(g.relative_to(ROOT))])
    plt.close(fig)

    provenance = {
        "schema": "p1-v6-chemical-space-coverage/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "n_molecules": int(len(data)),
        "metrics": {
            "whole_molecule_tanimoto_mean": float(whole.mean()),
            "whole_molecule_tanimoto_sd": float(whole.std(ddof=1)),
            "scaffold_tanimoto_mean": float(scaffold.mean()),
            "scaffold_tanimoto_sd": float(scaffold.std(ddof=1)),
            "whole_molecule_below_0_4": int((whole < 0.4).sum()),
            "whole_molecule_below_0_4_fraction": float((whole < 0.4).mean()),
            "scaffold_at_or_above_0_4": int((scaffold >= 0.4).sum()),
            "scaffold_at_or_above_0_4_fraction": float((scaffold >= 0.4).mean()),
            "both_whole_below_0_4_and_scaffold_at_or_above_0_4": int(((whole < 0.4) & (scaffold >= 0.4)).sum()),
        },
        "interpretation_boundary": [
            "Maximum Morgan-fingerprint similarities are descriptive structural metrics.",
            "The figure does not establish biological activity, target preference, or synthetic success.",
            "The 5,000-molecule sample is the declared novelty-analysis sample, not the full 65,856-molecule library.",
        ],
        "outputs": outputs,
        "output_sha256": {p: sha256(ROOT / p) for p in outputs},
    }
    prov = OUT / "p1_v6_chemical_space_coverage_provenance.json"
    prov.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "OK", "n": len(data), "outputs": outputs + [str(prov.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
