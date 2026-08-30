#!/usr/bin/env python3
"""Compute bounded RRS threshold margins for the V2609 release.

This is a descriptive sensitivity analysis. It does not alter the canonical
RRS classes or claim biological calibration. For each candidate and mutant
state it reports the distance to the 70% and 80% RRS thresholds, the minimum
margin per candidate, and a near-threshold flag. The input is the canonical
Set-C RRS table; output is versioned under results/v2609_rrs_margin_20260830/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

THRESHOLDS = (70.0, 80.0)
DEFAULT_INPUT = Path("results/c_rrs_classification.csv")
DEFAULT_OUTPUT = Path("results/v2609_rrs_margin_20260830")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_rrs_columns(df: pd.DataFrame) -> list[str]:
    cols = []
    for col in df.columns:
        low = col.lower()
        if "rrs" in low and any(token in low for token in ("n51", "c59", "s108", "i164", "k76")) and "mean" not in low and "class" not in low:
            cols.append(col)
    if not cols:
        # Fallback for explicit numeric RRS columns in alternate canonical exports.
        cols = [c for c in df.columns if "rrs" in c.lower() and pd.api.types.is_numeric_dtype(df[c])]
    return cols


def candidate_column(df: pd.DataFrame) -> str:
    for c in ("set_c_id", "candidate_id", "candidate", "ligand", "compound", "id"):
        if c in df.columns:
            return c
    raise ValueError("No candidate identifier column found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--near-threshold", type=float, default=5.0)
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"ERROR: input not found: {args.input}")
    df = pd.read_csv(args.input)
    id_col = candidate_column(df)
    rrs_cols = find_rrs_columns(df)
    if not rrs_cols:
        raise SystemExit("ERROR: no RRS columns found in canonical classification table")

    long_rows = []
    for _, row in df.iterrows():
        for col in rrs_cols:
            value = pd.to_numeric(row[col], errors="coerce")
            if pd.isna(value):
                continue
            long_rows.append({
                "candidate": row[id_col],
                "source_column": col,
                "rrs_percent": float(value),
                "margin_to_70_percent": float(value - 70.0),
                "margin_to_80_percent": float(value - 80.0),
                "near_70_or_80_threshold": bool(min(abs(value - 70.0), abs(value - 80.0)) <= args.near_threshold),
            })

    if not long_rows:
        raise SystemExit("ERROR: no finite RRS observations found")
    long_df = pd.DataFrame(long_rows)
    long_df["classification_sensitivity_note"] = "descriptive margin; canonical class unchanged"

    summary_rows = []
    for candidate, group in long_df.groupby("candidate", sort=True):
        distances = [abs(v - t) for v in group["rrs_percent"] for t in THRESHOLDS]
        summary_rows.append({
            "candidate": candidate,
            "n_finite_rrs": int(len(group)),
            "min_abs_margin_to_70_or_80_percent": float(min(distances)),
            "min_signed_margin_to_70_percent": float(group["margin_to_70_percent"].min()),
            "max_signed_margin_to_70_percent": float(group["margin_to_70_percent"].max()),
            "min_signed_margin_to_80_percent": float(group["margin_to_80_percent"].min()),
            "max_signed_margin_to_80_percent": float(group["margin_to_80_percent"].max()),
            "n_near_threshold_observations": int(group["near_70_or_80_threshold"].sum()),
            "near_threshold_candidate": bool(group["near_70_or_80_threshold"].any()),
        })
    summary_df = pd.DataFrame(summary_rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    long_path = args.output_dir / "rrs_threshold_margins_long.csv"
    summary_path = args.output_dir / "rrs_threshold_margins_by_candidate.csv"
    manifest_path = args.output_dir / "margin_analysis_manifest.json"
    long_df.to_csv(long_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    manifest = {
        "analysis": "V2609_RRS_THRESHOLD_MARGIN_ANALYSIS",
        "status": "COMPUTED_SECONDARY_SENSITIVITY",
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "thresholds_percent": list(THRESHOLDS),
        "near_threshold_half_width_percent": args.near_threshold,
        "candidate_count": int(summary_df["candidate"].nunique()),
        "finite_observation_count": int(len(long_df)),
        "canonical_classes_modified": False,
        "biological_calibration_claim": False,
        "outputs": [str(long_path), str(summary_path)],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
