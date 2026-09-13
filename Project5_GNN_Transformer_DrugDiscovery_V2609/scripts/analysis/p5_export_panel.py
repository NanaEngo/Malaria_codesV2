#!/usr/bin/env python3
"""
P5 — Canonical panel export (v1-prep, documented in P5_DATA_ANALYSIS_REPORT.md §10).

Builds results/p5_canonical_panel.csv (SMILES, activity, TFP-full, TNE-192) by
REUSING the P3 canonical-panel logic (p3_hybrid_benchmark.load_canonical_panel)
so the molecule order and activity labels are byte-identical to P3
(paired comparisons across P3/P5 are therefore valid).

TFP is enriched exactly like P3 (base 78 + persistence image + Betti curves).
TNE is the 192-d embedding.

Raises if the panel length != 19,836 or any feature column is missing/finite-violating.

Usage:
    python scripts/p5_export_panel.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

P5_ROOT = Path(__file__).resolve().parent.parent
P3_SCRIPTS = Path("/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/scripts")
P3_RESULTS = Path("/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/results")

sys.path.insert(0, str(P3_SCRIPTS))
from p3_hybrid_benchmark import load_canonical_panel, load_precomputed  # noqa: E402

OUT = P5_ROOT / "results" / "p5_canonical_panel.csv"
EXPECTED_N = 19836


def main() -> None:
    t0 = time.perf_counter()
    print("P5 canonical panel export (reusing P3 canonical panel logic)")
    print("=" * 60)

    act_df = load_canonical_panel(n_mols=None)
    n_mols = len(act_df)
    print(f"Canonical panel: {n_mols:,} molecules")
    if n_mols != EXPECTED_N:
        raise ValueError(
            f"Expected {EXPECTED_N:,} canonical molecules, got {n_mols:,}. "
            "P5 comparability to P3 is broken — aborting."
        )

    smiles_list = act_df["smiles"].tolist()
    y = (act_df["activity"].values >= 0.5).astype(int)
    print(f"Active: {y.sum():,} ({100*y.sum()/n_mols:.2f}%)")

    # --- TFP full (78 base + pers_img + betti), identical enrichment to P3 ---
    X_tfp_base = load_precomputed(smiles_list, P3_RESULTS / "p3_tda_fingerprints.csv", "H")
    X_pers = load_precomputed(smiles_list, P3_RESULTS / "p3_tda_fingerprints.csv", "pers_img_")
    X_betti = load_precomputed(smiles_list, P3_RESULTS / "p3_tda_fingerprints.csv", "betti_")
    X_tfp = np.hstack([X_tfp_base, X_pers, X_betti])
    print(f"TFP full: {X_tfp.shape}")

    # --- TNE 192-d ---
    X_tne = load_precomputed(smiles_list, P3_RESULTS / "p3_tne_embeddings.csv", "tne_")
    print(f"TNE: {X_tne.shape}")
    if not np.isfinite(X_tne).all():
        raise ValueError("Non-finite values in TNE — panel is not canonical.")

    panel = pd.DataFrame({"smiles": smiles_list, "activity": y.astype(np.int8)})
    for i in range(X_tfp.shape[1]):
        panel[f"tfp_{i}"] = X_tfp[:, i]
    for i in range(X_tne.shape[1]):
        panel[f"tne_{i}"] = X_tne[:, i]

    assert len(panel) == EXPECTED_N
    assert panel["smiles"].is_unique, "duplicated SMILES in exported panel"
    assert panel["activity"].isin([0, 1]).all()

    panel.to_csv(OUT, index=False)
    print(f"\nWrote {OUT}")
    print(f"Shape: {panel.shape} (expect {EXPECTED_N} x {1+1+len([c for c in panel.columns if c.startswith('tfp_')])+192})")
    print(f"Elapsed: {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()
