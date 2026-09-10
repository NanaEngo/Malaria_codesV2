#!/usr/bin/env python3
"""P1 V8 revision — R2.3/R2.5/R2.2 recomputation from the corrected PfCRT re-dock.

Inputs:
  results/derived/v7_integrated_candidate_metrics.csv  (canonical 17x4 + RRS panel)
  results/pfcrt_redock_v2grid_20260909/scores.csv       (68 corrected-protocol runs)

Computes (and writes results/pfcrt_redock_v2grid_20260909/revised_rrs_and_nfav.csv):
  - corrected PfCRT WT scores (new SM S3 PfCRT column)
  - corrected PfCRT RRS (K76T, K76A vs corrected WT)
  - R2.5 pipeline-null RRS distribution (K76K stripped WT vs full WT)
  - revised RRS_mean and RRS classes (declared P2 rules)
  - Table 2 per-target-median N_fav on the corrected matrix
  - N_fav-RRS Spearman rho/p + 100000-permutation p
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
CSV = RES / "derived/v7_integrated_candidate_metrics.csv"
SCORES = RES / "pfcrt_redock_v2grid_20260909/scores.csv"
OUT = RES / "pfcrt_redock_v2grid_20260909/revised_rrs_and_nfav.csv"

TARGETS = ["aff_PfDHFR", "aff_PfCRT", "aff_PfClpP", "aff_PfATP4"]
PFCRT_MUTANTS = ["K76T", "K76A"]


def main() -> None:
    df = pd.read_csv(CSV)
    s = pd.read_csv(SCORES, keep_default_na=False)
    piv = s.pivot(index="candidate", columns="receptor", values="affinity").astype(float)

    rrs = {m: 100 * piv[m].abs() / piv["WT"].abs() for m in PFCRT_MUTANTS}
    rrs_null = 100 * piv["NULL"].abs() / piv["WT"].abs()

    rows = []
    for _, r in df.iterrows():
        cid = r["candidate_id"]
        pfdhfr = [r[f"RRS_{m}"] for m in ["N51I", "C59R", "S108N", "I164L"]]
        pfcrt = [rrs[m][cid] for m in PFCRT_MUTANTS]
        vals = [v for v in pfdhfr + pfcrt if pd.notna(v)]
        wt_mag = abs(piv.loc[cid, "WT"])
        all80 = all(v >= 80 for v in vals)
        all70 = all(v >= 70 for v in vals)
        any80 = any(v >= 80 for v in vals)
        if all80 and wt_mag >= 7:
            klass = "A*"
        elif all80:
            klass = "A"
        elif all70:
            klass = "B"
        elif any80:
            klass = "C"
        else:
            klass = "D"
        rows.append({
            "candidate": cid,
            "RRS_mean": round(float(np.mean(vals)), 1),
            "RRS_class": klass,
            "RRS_K76T": round(float(rrs["K76T"][cid]), 1),
            "RRS_K76A": round(float(rrs["K76A"][cid]), 1),
            "RRS_null": round(float(rrs_null[cid]), 1),
            "PfCRT_WT_corr": round(float(piv.loc[cid, "WT"]), 3),
            "PfCRT_K76T_corr": round(float(piv.loc[cid, "K76T"]), 3),
            "PfCRT_K76A_corr": round(float(piv.loc[cid, "K76A"]), 3),
        })

    rev = pd.DataFrame(rows)
    # per-target median N_fav on the corrected matrix
    m_new = df.copy()
    m_new["aff_PfCRT"] = piv["WT"].values
    med = m_new[TARGETS].median()
    nfav = (m_new[TARGETS] <= med).sum(axis=1)
    rev["N_fav_perTargetMedian"] = nfav.values

    rho, p = stats.spearmanr(nfav, rev["RRS_mean"])
    rng = np.random.default_rng(42)
    obs, _ = stats.spearmanr(nfav, rev["RRS_mean"])
    perm = sum(abs(stats.spearmanr(nfav, rng.permutation(rev["RRS_mean"].values))[0]) >= abs(obs)
               for _ in range(100000))

    summary = {
        "corrected_pfcrt_wt_mean": float(piv["WT"].mean().round(3)),
        "rrs_null_pfcrt": {"mean": float(rrs_null.mean().round(1)),
                           "min": float(rrs_null.min().round(1)),
                           "max": float(rrs_null.max().round(1)),
                           "frac_above_80": float((rrs_null > 80).mean().round(3)),
                           "frac_above_70": float((rrs_null > 70).mean().round(3))},
        "rrs_k76t_range": [float(rrs["K76T"].min().round(1)), float(rrs["K76T"].max().round(1))],
        "rrs_k76a_range": [float(rrs["K76A"].min().round(1)), float(rrs["K76A"].max().round(1))],
        "max_abs_deviation_mutant_vs_null": {
            "K76T": float((rrs["K76T"] - rrs_null).abs().max().round(2)),
            "K76A": float((rrs["K76A"] - rrs_null).abs().max().round(2))},
        "class_counts_new": rev["RRS_class"].value_counts().to_dict(),
        "class_counts_old": df["RRS_class"].value_counts().to_dict(),
        "rrs_mean_range_new": [float(rev["RRS_mean"].min()), float(rev["RRS_mean"].max())],
        "rrs_mean_range_old": [float(df["RRS_mean"].min()), float(df["RRS_mean"].max())],
        "nfav_per_target_medians": {t: float(med[t].round(3)) for t in TARGETS},
        "nfav_rrs_spearman": {"rho": float(rho.round(4)), "p": float(p.round(4)),
                              "permutation_p_100k": float(perm / 100000)},
    }
    rev.to_csv(OUT, index=False)
    (RES / "pfcrt_redock_v2grid_20260909/revision_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()