#!/usr/bin/env python3
"""P1 V5 — target-normalised polypharmacology profile.

Raw Vina scores are not directly comparable across heterogeneous receptors.
This analysis therefore uses only within-target ranks and percentiles within
the locked 17-candidate cohort. It reports breadth of relative performance
across targets and a Pareto front; it does not create an absolute affinity or
cross-target potency score.

Outputs are quarantined under results/exploratory/polypharmacology/.
"""
from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
INPUT = V5 / "results/v5_four_target_vina_affinities.csv"
SCRIPT = Path(__file__).resolve()
OUT = V5 / "results/exploratory/polypharmacology"
OUT_CSV = OUT / "v5_within_target_polypharmacology.csv"
OUT_JSON = OUT / "v5_within_target_polypharmacology_provenance.json"
OUT_PNG = OUT / "v5_within_target_polypharmacology.png"
OUT_PDF = OUT / "v5_within_target_polypharmacology.pdf"
TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pareto_mask(values: np.ndarray) -> np.ndarray:
    """Return non-dominated rows when larger values are better."""
    mask = np.ones(len(values), dtype=bool)
    for i in range(len(values)):
        for j in range(len(values)):
            if i == j:
                continue
            if np.all(values[j] >= values[i]) and np.any(values[j] > values[i]):
                mask[i] = False
                break
    return mask


def make_figure(profile: pd.DataFrame) -> None:
    pct_cols = [f"pct_{t}" for t in TARGETS]
    ordered = profile.sort_values(["n_top_quartile", "mean_percentile", "min_percentile"], ascending=False)
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12.0, 6.0), gridspec_kw={"width_ratios": [1.7, 1.0]}
    )
    matrix = ordered[pct_cols].to_numpy()
    im = ax1.imshow(matrix, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax1.set_xticks(range(len(TARGETS)), TARGETS, rotation=35, ha="right")
    ax1.set_yticks(range(len(ordered)), ordered["candidate_id"])
    ax1.set_xlabel("Target-specific percentile (higher = better within cohort)")
    ax1.set_title("Relative multi-target profile")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax1.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=7,
                     color="white" if matrix[i, j] >= 0.55 else "black")
    fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04, label="Within-target percentile")

    colors = np.where(ordered["pareto_front"].to_numpy(), "#d95f02", "#4c78a8")
    ax2.barh(ordered["candidate_id"], ordered["mean_percentile"], color=colors, edgecolor="black", linewidth=0.3)
    ax2.axvline(0.75, color="#555555", linestyle="--", linewidth=1, label="Top-quartile threshold")
    ax2.set_xlim(0, 1)
    ax2.set_xlabel("Mean within-target percentile")
    ax2.set_title("Breadth of relative performance")
    ax2.invert_yaxis()
    ax2.legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("P1 V5: target-normalised polypharmacology", fontsize=14, fontweight="bold")
    fig.text(0.5, 0.01, "Scores are relative to the locked 17-candidate cohort; not experimental affinities.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    if not INPUT.is_file():
        raise SystemExit(f"Missing input: {INPUT}")
    df = pd.read_csv(INPUT)
    required = {"candidate_id", *(f"aff_{t}" for t in TARGETS)}
    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"Input schema missing: {missing}")
    if len(df) != 17 or df["candidate_id"].nunique() != 17:
        raise SystemExit("Expected exactly 17 unique candidates")
    if df["candidate_id"].duplicated().any():
        raise SystemExit("Duplicate candidate IDs")
    if not np.isfinite(df[[f"aff_{t}" for t in TARGETS]].to_numpy(dtype=float)).all():
        raise SystemExit("Non-finite target score")

    profile = df[["candidate_id"]].copy()
    for target in TARGETS:
        scores = df[f"aff_{target}"]
        rank = scores.rank(method="min", ascending=True).astype(int)
        profile[f"rank_{target}"] = rank
        profile[f"pct_{target}"] = (len(df) - rank) / (len(df) - 1)
    pct_cols = [f"pct_{t}" for t in TARGETS]
    pct = profile[pct_cols].to_numpy(dtype=float)
    profile["mean_percentile"] = pct.mean(axis=1)
    profile["min_percentile"] = pct.min(axis=1)
    profile["n_top_quartile"] = (pct >= 0.75).sum(axis=1)
    profile["pareto_front"] = pareto_mask(pct)
    profile = profile.sort_values(
        ["n_top_quartile", "pareto_front", "mean_percentile", "min_percentile"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    profile.insert(0, "profile_rank", np.arange(1, len(profile) + 1))

    OUT.mkdir(parents=True, exist_ok=True)
    profile.to_csv(OUT_CSV, index=False)
    make_figure(profile)
    pareto = profile.loc[profile["pareto_front"], "candidate_id"].tolist()
    summary = {
        "schema": "p1-v5-within-target-polypharmacology/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "PRE_SUBMISSION_DEVELOPMENT",
        "status": "EXPLORATORY_RELATIVE_POLYPHARMACOLOGY_NOT_SUBMISSION_READY",
        "input": str(INPUT.relative_to(ROOT)),
        "input_sha256": sha256(INPUT),
        "script": str(SCRIPT.relative_to(ROOT)),
        "script_sha256": sha256(SCRIPT),
        "candidate_count": int(len(profile)),
        "targets": TARGETS,
        "normalisation": "within-target rank; percentile=(17-rank)/16; rank 1 is most negative Vina score",
        "threshold": "top quartile = percentile >= 0.75",
        "results": {
            "pareto_front": pareto,
            "pareto_count": len(pareto),
            "n_at_least_3_top_quartile": int((profile["n_top_quartile"] >= 3).sum()),
            "n_at_least_4_top_quartile": int((profile["n_top_quartile"] >= 4).sum()),
            "top_quartile_candidates": profile.loc[profile["n_top_quartile"] >= 3, "candidate_id"].tolist(),
            "mean_percentile_min": float(profile["mean_percentile"].min()),
            "mean_percentile_max": float(profile["mean_percentile"].max()),
        },
        "interpretation": {
            "headline": "PP-06 is the only candidate in the top quartile on all four targets; PP-11 reaches three of four targets; the non-dominated front contains five candidates.",
            "scope": "relative multi-target breadth within the locked 17-candidate cohort",
            "not_claimed": [
                "absolute cross-target affinity",
                "experimental binding",
                "biological polypharmacology",
                "generalisation beyond this candidate cohort",
            ],
            "next_validation": "repeat target-normalised profiles on a common target-stratified decoy/background panel before making external enrichment claims",
        },
        "outputs": {
            "csv": str(OUT_CSV.relative_to(ROOT)),
            "csv_sha256": sha256(OUT_CSV),
            "figure_png": str(OUT_PNG.relative_to(ROOT)),
            "figure_pdf": str(OUT_PDF.relative_to(ROOT)),
        },
        "software": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "pareto_front": pareto,
                      "n_at_least_3_top_quartile": summary["results"]["n_at_least_3_top_quartile"],
                      "csv": str(OUT_CSV), "json": str(OUT_JSON)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
