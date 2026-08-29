#!/usr/bin/env python3
"""P6 bounded QKS protocol — quantile kernel similarity between phenotype and structure arms.

Computes a bounded QKS separability diagnostic over the scaffold-split
fold-level predictions emitted by `p6_phase2_benchmark.py --dump-predictions`.
The protocol is bounded to a frozen cohort (max_compounds) and a single
per-pair arm comparison. No result is inferred from the GIN/GIN-TFP/GIN-TNE/
ChemBERTa outputs; QKS is computed strictly from the saved prediction CSVs.

QKS definition used here (bounded, single-fingerprint proxy):

    QKS(p, y; tau) = abs(F_p(tau) - F_y(tau))

where F_p and F_y are the empirical CDFs of the per-drug maximum predicted
probability and the per-drug positive-label count. tau is the median by
default; the script reports QKS at tau=0.5 (median) and tau=0.25 / 0.75
(robustness) plus the Spearman rank correlation between predicted-prob and
positive-count. This is a proxy, not a full QKS reference implementation.

The protocol is fail-closed: any fold-level schema failure or missing arm
yields NOT_COMPUTED with a stated reason; no value is fabricated.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from pathlib import Path

META_RE = re.compile(r"^seed(\d+)_fold(\d+)\.csv$")


def load_arm(pred_dir: Path) -> dict | None:
    """Load per-drug max-pred-prob and per-drug positive-label count from a prediction dir."""
    files = sorted(pred_dir.glob("seed*_fold*.csv"))
    if not files:
        return None
    per_drug_max_prob: dict[str, float] = {}
    per_drug_pos: dict[str, int] = {}
    per_drug_n_labels: dict[str, int] = {}
    fold_keys: set[tuple[int, int]] = set()
    bad: list[str] = []
    for f in files:
        m = META_RE.match(f.name)
        if not m:
            bad.append(str(f))
            continue
        fold_keys.add((int(m.group(1)), int(m.group(2))))
        with f.open(newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            if not header or header[0] != "drug_id":
                bad.append(f"bad-header:{f}")
                continue
            moa_cols = header[1:]
            if len(moa_cols) % 2 != 0:
                bad.append(f"bad-cols:{f}")
                continue
            for row in reader:
                if not row or row[0] == "":
                    continue
                drug_id = row[0]
                max_p = 0.0
                n_pos = 0
                n_lab = 0
                for i in range(0, len(moa_cols), 2):
                    base = 1 + 2 * i
                    if base + 1 >= len(row):
                        continue
                    try:
                        y = float(row[base])
                        p = float(row[base + 1])
                    except ValueError:
                        continue
                    n_lab += 1
                    if y == 1.0:
                        n_pos += 1
                    if p > max_p:
                        max_p = p
                if n_lab > 0:
                    per_drug_max_prob[drug_id] = max(per_drug_max_prob.get(drug_id, 0.0), max_p)
                    per_drug_pos[drug_id] = per_drug_pos.get(drug_id, 0) + n_pos
                    per_drug_n_labels[drug_id] = per_drug_n_labels.get(drug_id, 0) + n_lab
    if bad:
        return {"error": "schema_or_io_failures", "bad": bad[:5], "files_total": len(files), "folds": sorted(fold_keys)}
    return {
        "max_prob": per_drug_max_prob,
        "pos_count": per_drug_pos,
        "n_labels_total": per_drug_n_labels,
        "folds": sorted(fold_keys),
        "n_drugs": len(per_drug_max_prob),
    }


def quantile(values: list[float], tau: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = tau * (len(s) - 1)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    frac = k - lo
    return s[lo] * (1 - frac) + s[hi] * frac


def spearman(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return float("nan")
    rx = {v: i for i, v in enumerate(sorted(range(n), key=lambda i: x[i]))}
    ry = {v: i for i, v in enumerate(sorted(range(n), key=lambda i: y[i]))}
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


def qks_proxy(arm_a: dict, arm_b: dict, max_compounds: int, taus: list[float]) -> dict:
    drugs = sorted(set(arm_a["max_prob"].keys()) & set(arm_b["max_prob"].keys()))
    if max_compounds > 0 and len(drugs) > max_compounds:
        drugs = drugs[:max_compounds]
    pa = [arm_a["max_prob"][d] for d in drugs]
    pb = [arm_b["max_prob"][d] for d in drugs]
    ya = [arm_a["pos_count"][d] for d in drugs]
    yb = [arm_b["pos_count"][d] for d in drugs]
    out = {"n_drugs": len(drugs), "taus": {}}
    for tau in taus:
        qa = quantile(pa, tau)
        qb = quantile(pb, tau)
        out["taus"][str(tau)] = {
            "quantile_arm_a": qa,
            "quantile_arm_b": qb,
            "abs_diff": abs(qa - qb),
        }
    out["spearman_max_prob"] = spearman(pa, pb)
    out["spearman_pos_count"] = spearman(ya, yb)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm-a", type=Path, required=True)
    ap.add_argument("--arm-b", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--max-compounds", type=int, default=5000)
    ap.add_argument("--label-a", type=str, default="arm_a")
    ap.add_argument("--label-b", type=str, default="arm_b")
    ap.add_argument("--split", type=str, default="unknown")
    args = ap.parse_args()
    taus = [0.25, 0.5, 0.75]
    arm_a = load_arm(args.arm_a)
    arm_b = load_arm(args.arm_b)
    if not arm_a or "error" in arm_a:
        result = {
            "status": "NOT_COMPUTED_ARM_A_SCHEMA_FAILED",
            "arm_a_path": str(args.arm_a),
            "split": args.split,
            "details": arm_a,
        }
    elif not arm_b or "error" in arm_b:
        result = {
            "status": "NOT_COMPUTED_ARM_B_SCHEMA_FAILED",
            "arm_b_path": str(args.arm_b),
            "split": args.split,
            "details": arm_b,
        }
    else:
        qks = qks_proxy(arm_a, arm_b, args.max_compounds, taus)
        result = {
            "status": "COMPUTED",
            "split": args.split,
            "label_a": args.label_a,
            "label_b": args.label_b,
            "max_compounds": args.max_compounds,
            "arm_a_path": str(args.arm_a),
            "arm_b_path": str(args.arm_b),
            "arm_a_n_drugs": arm_a["n_drugs"],
            "arm_b_n_drugs": arm_b["n_drugs"],
            "arm_a_folds": arm_a["folds"],
            "arm_b_folds": arm_b["folds"],
            "qks_proxy": qks,
            "interpretation": "QKS at median (tau=0.5) is the headline separability; tau=0.25/0.75 are robustness. Spearman on max-prob cross-arm and on positive-count cross-arm. The lower the abs_diff, the more the two arms agree on the predicted-prob and positive-label distributions.",
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
