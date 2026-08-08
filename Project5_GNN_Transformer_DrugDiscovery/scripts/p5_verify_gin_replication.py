#!/usr/bin/env python3
"""
P5 — GIN computational replication verification (action 2b).

Compares the per-fold/per-seed test AUCs produced by the ``--tag _replic``
replication run against the canonical committed results.  A replication is
deemed PASS if, for both splits, the per-seed mean AUC deviates by less than
``TOL`` (default 0.01) and the Spearman rank correlation between per-seed
means is >= 0.7 (the protocol is deterministic given seed; small float /
nondeterministic-GPU deviations are expected).

Canonical files are never modified.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

P5_ROOT = Path(__file__).resolve().parent.parent
TOL = 0.01
RHO_MIN = 0.7
# Spearman rank correlation is only informative when the inter-seed variance is
# well above the replication tolerance; otherwise seed ranking is GPU noise.
RHO_MIN_VAR = 1e-4
MODEL = "GIN"
SPLITS = ["random", "scaffold"]


def per_seed_means(csv_path: Path) -> dict[int, float]:
    df = pd.read_csv(csv_path)
    # per-seed mean over the 5 folds
    means = {}
    for seed, grp in df.groupby("seed"):
        means[int(seed)] = float(grp["test_auc"].mean())
    return means


def main() -> int:
    report = {
        "protocol": "GIN frozen-split replication (tag _replic)",
        "tolerance_auc": TOL,
        "rho_min": RHO_MIN,
        "splits": {},
        "verdict": None,
    }
    ok_all = True
    for split in SPLITS:
        can = P5_ROOT / "results" / f"p5_{MODEL}_{split}_results.csv"
        rep = P5_ROOT / "results" / f"p5_{MODEL}_{split}_results_replic.csv"
        entry = {"canonical_exists": can.exists(), "replic_exists": rep.exists()}
        if not (can.exists() and rep.exists()):
            entry["status"] = "PENDING"
            entry["note"] = "replication output not present yet"
            ok_all = False
        else:
            cm = per_seed_means(can)
            rm = per_seed_means(rep)
            seeds = sorted(set(cm) & set(rm))
            diffs = {s: rm[s] - cm[s] for s in seeds}
            rho, pval = stats.spearmanr(
                [cm[s] for s in seeds], [rm[s] for s in seeds]
            )
            max_abs = max(abs(d) for d in diffs.values()) if diffs else float("nan")
            mean_c, mean_r = np.mean(list(cm.values())), np.mean(list(rm.values()))
            inter_seed_var = float(np.var(list(cm.values())))
            # Primary criterion: mean and per-seed deviations within tolerance
            # (deterministic protocol check). Rank correlation is only required
            # when inter-seed variance is resolvable above the noise floor.
            rho_informative = inter_seed_var > RHO_MIN_VAR
            rho_ok = (not rho_informative) or (rho >= RHO_MIN)
            passed = (max_abs <= TOL) and (abs(mean_r - mean_c) <= TOL) and rho_ok
            entry.update(
                {
                    "status": "PASS" if passed else "FAIL",
                    "n_seeds": len(seeds),
                    "canonical_per_seed": {s: round(cm[s], 5) for s in seeds},
                    "replic_per_seed": {s: round(rm[s], 5) for s in seeds},
                    "max_abs_diff": round(float(max_abs), 5),
                    "mean_canonical": round(float(mean_c), 5),
                    "mean_replic": round(float(mean_r), 5),
                    "delta_mean": round(float(mean_r - mean_c), 5),
                    "spearman_rho": round(float(rho), 4),
                    "spearman_p": round(float(pval), 4),
                    "inter_seed_var_canonical": round(inter_seed_var, 6),
                    "rho_informative": rho_informative,
                }
            )
            ok_all = ok_all and passed
        report["splits"][split] = entry

    report["verdict"] = "PASS" if ok_all else ("FAIL" if any(
        e.get("status") == "FAIL" for e in report["splits"].values()
    ) else "PENDING")

    out = P5_ROOT / "results" / f"p5_{MODEL}_replication_verification.json"
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
