#!/usr/bin/env python
"""MW-only partial Spearman correlation of H1 features vs RRS.

Companion to p3_h1_rrs_partial_corr.py, which controls for four confounders
(MW, ring count, Fsp3, H0_count) in a single hard-coded model. The manuscript
additionally reports an adjustment controlling for *molecular weight alone*;
no script produced that model and no deposited file contained its value. This
script computes it, using the same loading path, the same rank-based partial
correlation, and the same inputs as the four-confounder run, so the two are
directly comparable.

It also reports the plain Spearman correlation between H1_count and molecular
weight, which the manuscript quotes and which was likewise not deposited.

Output: results/p3_h1_rrs_mw_only.txt + .csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from scipy import stats
from scipy.stats import rankdata


def partial_pearson(x: np.ndarray, y: np.ndarray, covars: np.ndarray) -> tuple[float, float]:
    """Partial Pearson correlation of x vs y controlling for covars.

    Identical to the implementation in p3_h1_rrs_partial_corr.py so that the
    MW-only and four-confounder results differ only in the covariate set.
    """
    Z = np.column_stack([x, y] + [covars[:, i] for i in range(covars.shape[1])])
    R = np.corrcoef(Z.T)
    R = R + np.eye(R.shape[0]) * 1e-10
    P = np.linalg.inv(R)
    r = -P[0, 1] / np.sqrt(P[0, 0] * P[1, 1])
    n = Z.shape[0]
    k = covars.shape[1] + 2
    dof = n - k
    t = r * np.sqrt(dof / (1.0 - r**2))
    p = 2 * stats.t.sf(abs(t), dof)
    return float(r), float(p)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rrs-csv", type=str, default="results/p3_rrs_tfp_final.csv")
    ap.add_argument("--tda-csv", type=str, default="results/p3_tda_fingerprints.csv")
    ap.add_argument("--out-txt", type=str, default="results/p3_h1_rrs_mw_only.txt")
    ap.add_argument("--out-csv", type=str, default="results/p3_h1_rrs_mw_only.csv")
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

    mw = []
    for s in df["smiles"]:
        mol = Chem.MolFromSmiles(s)
        mw.append(np.nan if mol is None else Descriptors.MolWt(mol))
    df["MW"] = mw

    outcome = "rrs_score"
    predictors = ["H1_count", "H1_entropy", "H1_total_pers_prod",
                  "H1_total_pers_sum", "H1_max_pers"]
    confounders = ["MW"]

    clean = df.dropna(subset=confounders + [outcome]).copy()
    covs = clean[confounders].to_numpy(dtype=float)
    y = rankdata(clean[outcome].to_numpy(dtype=float))
    cov_r = np.column_stack([rankdata(covs[:, i]) for i in range(covs.shape[1])])

    rows = []
    for feat in predictors:
        x_raw = clean[feat].to_numpy(dtype=float)
        rho_t, p_t = stats.spearmanr(x_raw, clean[outcome].to_numpy(dtype=float))
        rho_p, p_p = partial_pearson(rankdata(x_raw), y, cov_r)
        rows.append({"predictor": feat, "rho_total": rho_t, "p_total": p_t,
                     "rho_partial_mw": rho_p, "p_partial_mw": p_p, "n": len(clean)})

    pd.DataFrame(rows).to_csv(args.out_csv, index=False)

    rho_h1_mw, p_h1_mw = stats.spearmanr(clean["H1_count"].to_numpy(dtype=float),
                                         clean["MW"].to_numpy(dtype=float))

    lines = [
        "=" * 78,
        "P3 H1-RRS PARTIAL CORRELATION -- MW-ONLY MODEL",
        "=" * 78,
        f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"Final n (listwise): {len(clean)}",
        "",
        "Partial Spearman = Spearman on ranks, then partial Pearson on ranks,",
        "controlling for MW only. Companion to the four-confounder model in",
        "p3_h1_rrs_partial_corr.py (MW, n_rings, Fsp3, H0_count).",
        "",
        f"{'predictor':<24s}{'rho_total':>10s}{'p_total':>10s}{'rho_part_MW':>13s}{'p_part_MW':>11s}{'n':>5s}",
        "-" * 78,
    ]
    for r in rows:
        lines.append(f"{r['predictor']:<24s}{r['rho_total']:>10.4f}{r['p_total']:>10.4f}"
                     f"{r['rho_partial_mw']:>13.4f}{r['p_partial_mw']:>11.4f}{r['n']:>5d}")
    lines += [
        "-" * 78,
        "",
        "Ancillary: Spearman H1_count vs molecular weight",
        f"  rho = {rho_h1_mw:.4f}  p = {p_h1_mw:.3e}  n = {len(clean)}",
        "",
    ]
    txt = "\n".join(lines)
    with open(args.out_txt, "w") as fh:
        fh.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
