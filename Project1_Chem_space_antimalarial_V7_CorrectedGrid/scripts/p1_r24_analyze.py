#!/usr/bin/env python3
"""P1 V8 revision — R2.4 DEKOIS analysis: compare the two arms.

Reads results/dekois_mtxstripped_20260909/metrics.csv (one row per arm) and
scores_<arm>.csv, prints a combined comparison table (machine + human readable)
used to populate the DAR checkpoint and the manuscript (SM S12.2, enrichment
table, main text, response R2.4).

Workflow: data -> DAR -> manuscript. Run this first, then update the DAR,
then the manuscript.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/dekois_mtxstripped_20260909"
ARMS = ["retained", "stripped"]


def main() -> None:
    rows = []
    mdf = pd.read_csv(OUT / "metrics.csv")
    for arm in ARMS:
        m = mdf[mdf["arm"] == arm].iloc[0].to_dict()
        s = pd.read_csv(OUT / f"scores_{arm}.csv")
        rows.append(
            {
                "arm": arm,
                "n_actives_docked": int(m["n_actives_docked"]),
                "n_decoys_docked": int(m["n_decoys_docked"]),
                "n_prep_failed": int(m["n_prep_failed"]),
                "ROC_AUC": float(m["ROC_AUC"]),
                "AUC_lo": float(m["ROC_AUC_95CI_lo"]),
                "AUC_hi": float(m["ROC_AUC_95CI_hi"]),
                "EF1pct": float(m["EF1pct"]),
                "EF5pct": float(m["EF5pct"]),
                "EF10pct": float(m["EF10pct"]),
                "BEDROC": float(m["BEDROC"]),
                "PR_AUC": float(m["PR_AUC"]),
                "wall_min": float(m["wall_min"]),
            }
        )
    df = pd.DataFrame(rows).set_index("arm")
    print(df.to_string(float_format=lambda x: f"{x:.4f}"))

    # Delta stripped - retained
    r, s = df.loc["retained"], df.loc["stripped"]
    print("\nDelta (stripped - retained):")
    for k in ["ROC_AUC", "EF1pct", "EF5pct", "EF10pct", "BEDROC", "PR_AUC"]:
        print(f"  {k:8s}: {s[k] - r[k]:+.4f}")

    # Overlap of CIs -> statistically distinguishable?
    overlap = not (r["AUC_hi"] < s["AUC_lo"] or s["AUC_hi"] < r["AUC_lo"])
    print(f"\nAUC CIs overlap (no significant difference): {overlap}")
    print(f"  retained: {r['ROC_AUC']:.4f} [{r['AUC_lo']:.4f}, {r['AUC_hi']:.4f}]")
    print(f"  stripped: {s['ROC_AUC']:.4f} [{s['AUC_lo']:.4f}, {s['AUC_hi']:.4f}]")

    # Original published baseline (V4 validation, exhaustiveness 64)
    base = {"ROC_AUC": 0.450, "AUC_lo": 0.367, "AUC_hi": 0.531,
            "EF1pct": 0.0, "EF5pct": 0.0, "EF10pct": 1.0,
            "BEDROC": 0.021, "PR_AUC": 0.034}
    print("\nPublished baseline (exh 64):")
    print(f"  {base['ROC_AUC']:.3f} [{base['AUC_lo']:.3f}, {base['AUC_hi']:.3f}] "
          f"EF@1 {base['EF1pct']:.2f} EF@5 {base['EF5pct']:.2f} "
          f"BEDROC {base['BEDROC']:.3f} PR-AUC {base['PR_AUC']:.3f}")

    summary = {
        "arms": {
            arm: rows[i] for i, arm in enumerate(ARMS)
        },
        "published_baseline": base,
        "ci_overlap": overlap,
        "interpretation": (
            "stripped_improved" if s["ROC_AUC"] > r["ROC_AUC"] else
            "retained_improved" if r["ROC_AUC"] > s["ROC_AUC"] else "equal"),
    }
    (OUT / "comparison_summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n")
    print(f"\nWrote {OUT / 'comparison_summary.json'}")


if __name__ == "__main__":
    main()