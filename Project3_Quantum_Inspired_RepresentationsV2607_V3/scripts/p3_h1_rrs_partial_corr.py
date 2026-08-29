#!/usr/bin/env python
"""Partial Spearman correlation of H1_count vs RRS controlling for confounders.

Follow-up E-2 (project-tracking.md): test whether the H1_count-RRS association
(whole-sample Spearman rho=0.312, n=77) survives control for molecular size
(MW, ring count, H0_count) and sp3 fraction (Fsp3).

Partial Spearman = Spearman on ranks of all variables, then partial Pearson
on the rank-transformed data (semi-partial / standard partial via precision
matrix of the correlation matrix).

Output: results/p3_h1_rrs_partial_corr.txt + .csv
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors
from scipy import stats
from scipy.stats import rankdata


def partial_pearson(x: np.ndarray, y: np.ndarray, covars: np.ndarray) -> tuple[float, float]:
    """Partial Pearson correlation of x vs y controlling for covars.

    Uses the inverse of the correlation matrix (Gaussian graphical model
    precision matrix) restricted to x,y.
    """
    Z = np.column_stack([x, y] + [covars[:, i] for i in range(covars.shape[1])])
    R = np.corrcoef(Z.T)
    # guard against singular covariance
    R = R + np.eye(R.shape[0]) * 1e-10
    P = np.linalg.inv(R)
    p_val = -P[0, 1] / np.sqrt(P[0, 0] * P[1, 1])
    # t-statistic & p-value
    n = Z.shape[0]
    k = covars.shape[1] + 2
    dof = n - k
    t = p_val * np.sqrt(dof / (1.0 - p_val**2))
    p = 2 * stats.t.sf(abs(t), dof)
    return float(p_val), float(p)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rrs-csv", type=str,
                    default="results/p3_rrs_tfp_final.csv")
    ap.add_argument("--tda-csv", type=str,
                    default="results/p3_tda_fingerprints.csv")
    ap.add_argument("--out-txt", type=str,
                    default="results/p3_h1_rrs_partial_corr.txt")
    ap.add_argument("--out-csv", type=str,
                    default="results/p3_h1_rrs_partial_corr.csv")
    args = ap.parse_args()

    rrs = pd.read_csv(args.rrs_csv)
    tda = pd.read_csv(args.tda_csv, usecols=lambda c: c in {
        "smiles", "H0_count", "H0_entropy", "H0_max_pers"})

    valid = rrs[rrs["rrs_class"].isin(["A", "B", "C", "D"])].copy()
    if "rrs_score" not in valid.columns:
        raise SystemExit("rrs_score column missing")

    df = valid.merge(tda, on="smiles", how="left")
    df["H1_total_pers_prod"] = df["H1_count"] * df["H1_mean_pers"]
    df["H1_total_pers_sum"] = (df["H1_max_pers"] + df["H1_mean_pers"]
                               + df["H1_entropy"] + df["H1_count"])

    # RDKit descriptors
    mw, rings, fsp3 = [], [], []
    for s in df["smiles"]:
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            mw.append(np.nan); rings.append(np.nan); fsp3.append(np.nan)
            continue
        mw.append(Descriptors.MolWt(mol))
        rings.append(rdMolDescriptors.CalcNumRings(mol))
        fsp3.append(rdMolDescriptors.CalcFractionCSP3(mol))
    df["MW"] = mw
    df["n_rings"] = rings
    df["Fsp3"] = fsp3

    outcome = "rrs_score"
    predictors = ["H1_count", "H1_entropy", "H1_total_pers_prod",
                  "H1_total_pers_sum", "H1_max_pers"]
    confounders = ["MW", "n_rings", "Fsp3", "H0_count"]

    results = []
    lines = [
        "=" * 78,
        "P3 H1-RRS PARTIAL CORRELATION (follow-up E-2)",
        "=" * 78,
        f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"Valid compounds (RRS class A/B/C/D): {len(df)}",
        f"Missing confounders dropped: {df[confounders].isna().any(axis=1).sum()}",
        f"Final n (listwise): {df[confounders + [outcome]].dropna().shape[0]}",
        "",
        "Partial Spearman = Spearman on ranks, then partial Pearson on ranks,",
        "controlling for MW, n_rings, Fsp3, H0_count.",
        "",
        f"{'predictor':<24s}{'rho_total':>10s}{'p_total':>10s}{'rho_partial':>12s}{'p_partial':>11s}{'n':>5s}",
        "-" * 78,
    ]

    clean = df.dropna(subset=confounders + [outcome]).copy()
    covs = clean[confounders].to_numpy(dtype=float)
    y = rankdata(clean[outcome].to_numpy(dtype=float))

    for feat in predictors:
        x_raw = clean[feat].to_numpy(dtype=float)
        rho_total, p_total = stats.spearmanr(x_raw, clean[outcome])
        # rank everything for partial Spearman
        xr = rankdata(x_raw)
        yr = y
        cr = np.column_stack([rankdata(covs[:, i]) for i in range(covs.shape[1])])
        rho_part, p_part = partial_pearson(xr, yr, cr)
        results.append({
            "predictor": feat,
            "rho_total": round(rho_total, 4),
            "p_total": float(p_total),
            "rho_partial": round(rho_part, 4),
            "p_partial": float(p_part),
            "n": int(len(clean)),
        })
        lines.append(f"{feat:<24s}{rho_total:>10.4f}{p_total:>10.4f}"
                     f"{rho_part:>12.4f}{p_part:>11.4f}{len(clean):>5d}")

    lines.append("-" * 78)
    for r in results:
        if r["predictor"] == "H1_count":
            survived = r["p_partial"] < 0.05
            lines.append("")
            lines.append("VERDICT H1_count:")
            lines.append(f"  whole-sample Spearman rho = {r['rho_total']:.3f} (p={r['p_total']:.4f})")
            lines.append(f"  partial (MW, n_rings, Fsp3, H0_count) = {r['rho_partial']:.3f} (p={r['p_partial']:.4f})")
            lines.append("  -> association SURVIVES confounding control" if survived
                         else "  -> association NOT robust to confounding (p>=0.05)")

    Path(args.out_txt).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_txt).write_text("\n".join(lines) + "\n")
    pd.DataFrame(results).to_csv(args.out_csv, index=False)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
