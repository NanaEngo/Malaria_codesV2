#!/usr/bin/env python3
"""
P3 — Classical-only 19,849 molecule benchmark (no QK/hybrid/ablation).

Reuses the descriptor and CV helpers from p3_hybrid_benchmark.py, but only
computes classical/topological descriptors on the full 19,849 molecule panel
covered by p3_tda_fingerprints.csv.

Outputs:
    results/p3_classical_benchmark_19849.csv
    results/p3_classical_benchmark_19849_summary.txt

Usage:
    python scripts/p3_classical_benchmark_19849.py
"""

from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Reuse descriptor definitions and CV helper from the main hybrid benchmark.
# Importing pulls in PennyLane too, but no QK code is executed here.
sys.path.insert(0, str(Path(__file__).parent))
from p3_hybrid_benchmark import (
    ACT_THRESHOLD,
    N_FOLDS,
    ap,
    bpf_hashed,
    cv_score,
    ecfp4,
    fcfp4,
    load_activity,
    load_precomputed,
    maccs,
    phco,
    RESULTS_DIR,
)


def main() -> None:
    print("=" * 60)
    print("P3 Classical-only benchmark — 19,849 molecules")
    print("=" * 60)

    t0 = time.perf_counter()

    # Use the exact 19,849-molecule panel for which TFP/TNE are available.
    tfp_df = pd.read_csv(RESULTS_DIR / "p3_tda_fingerprints.csv")
    if "smiles" not in tfp_df.columns:
        raise ValueError("p3_tda_fingerprints.csv must contain a 'smiles' column")
    smiles_list = tfp_df["smiles"].tolist()
    n_mols = len(smiles_list)
    print(f"Loaded {n_mols:,} molecules from p3_tda_fingerprints.csv")

    act_df = (
        load_activity()
        .drop_duplicates("smiles")  # avoid duplicate rows inflating the length
        .merge(pd.DataFrame({"smiles": smiles_list}), on="smiles", how="inner")
    )
    if len(act_df) != n_mols:
        missing = n_mols - len(act_df)
        print(f"  WARNING: {missing:,} SMILES from TFP panel are missing from activity file — excluding them")
    smiles_list = act_df["smiles"].tolist()
    y = (act_df["activity"].values >= ACT_THRESHOLD).astype(int)
    print(f"Active: {y.sum():,}, Inactive: {(y == 0).sum():,}")

    # Load / compute descriptors.
    print("\nComputing descriptors...")
    descriptors = {
        "ECFP4": ecfp4(smiles_list),
        "FCFP4": fcfp4(smiles_list),
        "MACCS": maccs(smiles_list),
        "AP": ap(smiles_list),
        "PHCO": phco(smiles_list),
        "BPF": bpf_hashed(smiles_list),
        "TFP": load_precomputed(smiles_list, RESULTS_DIR / "p3_tda_fingerprints.csv", "H"),
        "TNE": load_precomputed(smiles_list, RESULTS_DIR / "p3_tne_embeddings.csv", "tne_"),
    }

    # Optionally enrich TFP with persistence image + Betti curves to match the
    # default behaviour in the main script.
    X_tfp_base = descriptors["TFP"]
    if X_tfp_base is not None:
        X_pers = load_precomputed(smiles_list, RESULTS_DIR / "p3_tda_fingerprints.csv", "pers_img_")
        X_betti = load_precomputed(smiles_list, RESULTS_DIR / "p3_tda_fingerprints.csv", "betti_")
        if X_pers is not None and X_betti is not None:
            descriptors["TFP"] = np.hstack([X_tfp_base, X_pers, X_betti])
            print(f"TFP enriched: {descriptors['TFP'].shape[1]} features")
        else:
            print(f"TFP base only: {X_tfp_base.shape[1]} features")

    # Run RF-only 5-fold CV for each descriptor (SVM on PHCO/19k features is slow
    # and is not needed to obtain the canonical AUC values used in the manuscript).
    all_records = []
    for desc_name, X in descriptors.items():
        if X is None:
            print(f"  {desc_name}: descriptor not available — skipping")
            continue
        print(f"  {desc_name}: shape {X.shape}")
        all_records.extend(cv_score(X, y, "rf", desc_name))

    results_df = pd.DataFrame(all_records)
    out_csv = RESULTS_DIR / "p3_classical_benchmark_19849.csv"
    results_df.to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}")

    # Summary.
    summary_lines = [f"P3 Classical-only benchmark ({n_mols:,} molecules)", ""]
    summary_lines.append(f"{'Descriptor':<12s} {'AUC':>8s} {'±':>6s} {'Acc':>8s} {'F1':>8s}")
    for desc in results_df["descriptor"].unique():
        sub = results_df[(results_df["descriptor"] == desc) & (results_df["classifier"] == "rf")]
        auc = sub["auc"].dropna()
        acc = sub["accuracy"].mean()
        f1 = sub["f1"].mean()
        summary_lines.append(
            f"{desc:<12s} {auc.mean():>8.4f} {auc.std():>6.4f} {acc:>8.4f} {f1:>8.4f}"
        )

    summary = "\n".join(summary_lines)
    print("\n" + summary)

    out_summary = RESULTS_DIR / "p3_classical_benchmark_19849_summary.txt"
    out_summary.write_text(summary)
    print(f"\nSaved: {out_summary}")

    elapsed = time.perf_counter() - t0
    print(f"Wall time: {elapsed:.1f} s ({elapsed / 60:.1f} min)")


if __name__ == "__main__":
    main()
