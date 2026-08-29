#!/usr/bin/env python3
"""P6 calibration audit + per-label calibration metrics from fold-level predictions.

Replaces the fail-closed PENDING_IMPLEMENTATION stub with an explicit schema
audit followed by ECE/Brier computation when the schema matches. The schema
expected here is the alternating true/pred column pattern emitted by
`p6_phase2_benchmark.py --dump-predictions`:

    drug_id, <moa_a>_true, <moa_a>_pred, <moa_b>_true, <moa_b>_pred, ...

The audit reports row count, column count, fold identity, drug-set size, and
label-set size before any calibration metric is computed. If the schema does
not match, the output records the failure mode and no metric is reported.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

N_BINS = 10
THRESHOLD = 100_000.0
META_RE = re.compile(r"^seed(\d+)_fold(\d+)\.csv$")


def audit_files(files: list[Path]) -> dict:
    """Schema audit across prediction files; returns the audit report."""
    fold_keys: set[tuple[int, int]] = set()
    drug_ids_per_fold: dict[tuple[int, int], set[str]] = {}
    moa_names: set[str] | None = None
    n_moa_per_fold: dict[tuple[int, int], int] = {}
    bad: list[dict] = []

    for f in files:
        m = META_RE.match(f.name)
        if not m:
            bad.append({"file": str(f), "issue": "filename does not match seedX_foldY.csv"})
            continue
        seed, fold = int(m.group(1)), int(m.group(2))
        key = (seed, fold)
        if key in fold_keys:
            bad.append({"file": str(f), "issue": f"duplicate fold identity {key}"})
            continue
        fold_keys.add(key)
        with f.open(newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                bad.append({"file": str(f), "issue": "empty file"})
                continue
            if not header or header[0] != "drug_id":
                bad.append({"file": str(f), "issue": f"header[0] != 'drug_id' (got {header[0]!r})"})
                continue
            moa_cols = header[1:]
            if len(moa_cols) % 2 != 0:
                bad.append({"file": str(f), "issue": f"odd number of MoA columns ({len(moa_cols)})"})
                continue
            local_moa = []
            for i in range(0, len(moa_cols), 2):
                t, p = moa_cols[i], moa_cols[i + 1]
                if not t.endswith("_true") or not p.endswith("_pred"):
                    bad.append({"file": str(f), "issue": f"col {i} not *_true/*_pred (got {t!r},{p!r})"})
                    break
                base_t = t[: -len("_true")]
                base_p = p[: -len("_pred")]
                if base_t != base_p:
                    bad.append({"file": str(f), "issue": f"true/pred base mismatch at col {i}"})
                    break
                local_moa.append(base_t)
            else:
                if moa_names is None:
                    moa_names = set(local_moa)
                elif moa_names != set(local_moa):
                    bad.append({"file": str(f), "issue": "MoA set differs from first file"})
                    continue
                n_moa_per_fold[key] = len(local_moa)
                drug_ids_per_fold[key] = set()
                for row in reader:
                    if not row or row[0] == "":
                        continue
                    drug_ids_per_fold[key].add(row[0])
    return {
        "files_audited": len(files),
        "files_ok": len(fold_keys),
        "files_bad": len(bad),
        "bad_details": bad,
        "fold_identities": sorted(fold_keys),
        "n_moa": (len(next(iter(moa_names))) if False else (len(moa_names) if moa_names else 0)),
        "moa_set": sorted(moa_names) if moa_names else [],
        "n_drugs_per_fold": {f"{s}_{f}": len(d) for (s, f), d in sorted(drug_ids_per_fold.items())},
        "n_moa_per_fold": {f"{s}_{f}": n_moa_per_fold.get((s, f), 0) for (s, f) in sorted(fold_keys)},
    }


def compute_calibration(files: list[Path]) -> dict:
    """Compute per-label ECE/Brier and pooled metrics from the prediction files."""
    per_label: dict[str, dict] = {}
    pooled: list[tuple[float, int]] = []
    for f in files:
        m = META_RE.match(f.name)
        if not m:
            continue
        with f.open(newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            moa_cols = header[1:]
            moa_names_local = []
            for i in range(0, len(moa_cols), 2):
                moa_names_local.append(moa_cols[i][: -len("_true")])
            for row in reader:
                if not row or row[0] == "":
                    continue
                for i, moa in enumerate(moa_names_local):
                    base = 1 + 2 * i
                    if base + 1 >= len(row):
                        continue
                    try:
                        y = float(row[base])
                        p = float(row[base + 1])
                    except ValueError:
                        continue
                    if not math.isfinite(y) or not math.isfinite(p):
                        continue
                    if y not in (0.0, 1.0):
                        continue
                    if p < 0.0 or p > 1.0:
                        continue
                    pooled.append((p, int(y)))
                    slot = per_label.setdefault(moa, {"n": 0, "sum_y": 0.0, "sum_p": 0.0, "sum_y2": 0.0, "sq_err": 0.0})
                    slot["n"] += 1
                    slot["sum_y"] += y
                    slot["sum_p"] += p
                    slot["sum_y2"] += y * y
                    slot["sq_err"] += (p - y) ** 2
    if not pooled:
        return {"per_label": [], "pooled": None}
    edges = [i / N_BINS for i in range(N_BINS + 1)]
    binned_p = [0.0] * (N_BINS + 1)
    binned_y = [0.0] * (N_BINS + 1)
    binned_n = [0] * (N_BINS + 1)
    for p, y in pooled:
        b = min(int(p * N_BINS), N_BINS - 1) if p < 1.0 else N_BINS - 1
        binned_p[b] += p
        binned_y[b] += y
        binned_n[b] += 1
    ece = 0.0
    mce = 0.0
    n = len(pooled)
    bins = []
    for b in range(N_BINS):
        if binned_n[b] == 0:
            bins.append({"bin": b, "n": 0, "frac": 0.0, "mean_pred": None, "pos_frac": None})
            continue
        conf = binned_p[b] / binned_n[b]
        acc = binned_y[b] / binned_n[b]
        frac = binned_n[b] / n
        ece += frac * abs(acc - conf)
        mce = max(mce, abs(acc - conf))
        bins.append({"bin": b, "n": binned_n[b], "frac": frac, "mean_pred": conf, "pos_frac": acc})
    brier = sum((p - y) ** 2 for p, y in pooled) / n
    out = []
    for moa, slot in sorted(per_label.items()):
        n_m = slot["n"]
        if n_m == 0:
            continue
        out.append({
            "moa": moa,
            "n": n_m,
            "pos_rate": slot["sum_y"] / n_m,
            "mean_pred": slot["sum_p"] / n_m,
            "brier": slot["sq_err"] / n_m,
        })
    return {
        "per_label": out,
        "pooled": {
            "n": n,
            "ece": ece,
            "mce": mce,
            "brier": brier,
            "threshold_kcal_mol_note": "threshold=100000.0 reserved for kcal/mol convention; ECE/MCE/Brier are unitless probabilities.",
            "bins": bins,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prediction-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--features", type=str, default="unknown")
    ap.add_argument("--split", type=str, default="unknown")
    args = ap.parse_args()
    if not args.prediction_dir.exists():
        result = {
            "status": "NOT_COMPUTED_PREDICTION_DIR_MISSING",
            "prediction_dir": str(args.prediction_dir),
            "features": args.features,
            "split": args.split,
            "audit": {},
            "calibration": {"per_label": [], "pooled": None},
        }
    else:
        files = sorted(args.prediction_dir.glob("seed*_fold*.csv"))
        audit = audit_files(files)
        if audit["files_bad"] > 0 or audit["n_moa"] == 0:
            result = {
                "status": "SCHEMA_AUDIT_FAILED",
                "prediction_dir": str(args.prediction_dir),
                "features": args.features,
                "split": args.split,
                "audit": audit,
                "calibration": {"per_label": [], "pooled": None},
            }
        else:
            cal = compute_calibration(files)
            result = {
                "status": "COMPUTED",
                "prediction_dir": str(args.prediction_dir),
                "features": args.features,
                "split": args.split,
                "audit": audit,
                "calibration": cal,
            }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
