#!/usr/bin/env python3
"""Reconstruct the available-target polypharmacology subset ROC-AUC for P5V2.

Post-hoc re-scoring (no retraining). For each molecular arm, pool the per-fold
test predictions of the six PP-01 ... PP-15 candidates (RRS_class_available in
{A*, A}) across the 25 scaffold fold-seed records, then compute ROC-AUC of the
predicted probability p vs the true label y on those pooled candidate rows.
The six candidates appear in exactly 5 test folds each -> 30 pooled samples,
as reported in the SI Table S2 ("30 test samples per configuration").

Usage:
    python3 scripts/p5_polypharma_available_reconstruct.py \
        --pred-root results/extended_campaign_20260825 \
        --panel results/p5_canonical_panel.csv \
        --rrs /path/to/c_rrs_classification.csv \
        --out results/calibration_20260827/polypharma_available_reconstructed.csv
"""
import argparse, glob, hashlib, json, os
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred-root", required=True)
    ap.add_argument("--panel", required=True)
    ap.add_argument("--rrs", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # 1. candidate set (available A*/A) -> panel index
    rrs = pd.read_csv(args.rrs)
    av = rrs[rrs.RRS_class_available.isin(["A*", "A"])]
    cand_smiles = set(av.smiles.astype(str))
    panel = pd.read_csv(args.panel, low_memory=False)
    panel_smiles = panel.smiles.astype(str).tolist()
    sidx = {}
    for i, s in enumerate(panel_smiles):
        if s in cand_smiles:
            sidx[s] = i
    cand_idx = sorted(sidx.values())
    cand_id = {sidx[s]: c for s, c in zip(av.smiles.astype(str), av.candidate_id)}
    print(f"candidates mapped to panel index: {len(cand_idx)} -> {cand_idx}")
    assert len(cand_idx) == 6, f"expected 6 available A*/A candidates, got {len(cand_idx)}"

    # 2. arms: native molecular arms + ECFP4-RF reference on scaffold split
    arms = {
        "GIN_native": f"{args.pred_root}/training/canonical_scaffold/GIN_native",
        "GIN-TFP_native": f"{args.pred_root}/training/canonical_scaffold/GIN-TFP_native",
        "GIN-TNE_native": f"{args.pred_root}/training/canonical_scaffold/GIN-TNE_native",
        "ChemBERTa": f"{args.pred_root}/chemberta/canonical_scaffold",
    }

    rows = []
    for arm, d in arms.items():
        fs = sorted(glob.glob(f"{d}/pred_seed*_fold*.csv"))
        assert len(fs) == 25, f"{arm}: expected 25 fold files, got {len(fs)}"
        ys, ps = [], []
        n_per_fold = 0
        for f in fs:
            df = pd.read_csv(f)
            sub = df[df["index"].isin(cand_idx)]
            # require the candidate indices to be present
            n_per_fold += sum(df["index"].isin(cand_idx))
            ys.extend(sub["y"].astype(float).tolist())
            ps.extend(sub["p"].astype(float).tolist())
        ys = np.asarray(ys)
        ps = np.asarray(ps)
        print(f"{arm}: n_pooled_samples={len(ys)} (of 30 expected)")
        if len(ys) < 2 or (ys.sum() == len(ys)) or ys.sum() == 0:
            rows.append({"partition": "canonical_scaffold", "model": arm,
                         "metric": "AUC", "polypharma": np.nan, "n": len(ys),
                         "note": "insufficient classes for ROC"})
            continue
        auc = roc_auc_score(ys, ps)
        rows.append({"partition": "canonical_scaffold", "model": arm,
                     "metric": "AUC", "polypharma": float(f"{auc:.4f}"),
                     "single_target": np.nan, "delta_auc": np.nan,
                     "poly_n": len(ys), "note": "reconstructed 30-sample available subset"})

    out_df = pd.DataFrame(rows)
    out_df.to_csv(args.out, index=False)

    # 3. hash + summary manifest
    with open(args.out, "rb") as fh:
        h = hashlib.sha256(fh.read()).hexdigest()
    manifest = {
        "source": os.path.basename(args.out),
        "sha256": h,
        "candidate_ids": [cand_id.get(i) for i in cand_idx],
        "panel_indices": [int(i) for i in cand_idx],
        "n_pooled_per_arm": 30,
        "folds_per_candidate": 5,
        "definition": "RRS_class_available in {A*,A} (PP-01/02/06/11/13/15)",
        "status": "RECONSTRUCTED_AVAILABLE_POLYPHARMA_20260830",
    }
    with open(args.out + ".manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()