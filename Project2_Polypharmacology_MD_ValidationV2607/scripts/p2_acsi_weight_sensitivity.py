#!/usr/bin/env python3
"""Compute the candidate-cohort ACSI weight-sensitivity analysis.

The canonical ACSI output stores the four unweighted components for the
17-member Set-C cohort. This script reconstructs the same min--max
normalisation used by ``md_calculate_rrs_acsi_pns.py`` and perturbs one weight
by +/-20 percent while rescaling the other weights proportionally so that the
weights still sum to one.

The full 65,856-molecule component matrix is not part of the committed source
record. Therefore this analysis is explicitly limited to the 17-candidate
cohort; it does not claim robustness of a full-library top-20 ranking. The
reported stability measures are Spearman rank correlation over all 17
candidates and Jaccard overlap of the top five candidates.

Outputs:
    results/c_acsi_weight_sensitivity.csv
    results/c_acsi_weight_sensitivity.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

BASE_WEIGHTS = {
    "D_DrugBank": 0.40,
    "D_ANPDB": 0.25,
    "fsp3": 0.20,
    "NPL": 0.15,
}


def minmax(values: pd.Series) -> pd.Series:
    """Min--max normalise one ACSI component over the candidate cohort.

    Args:
        values: Unitless raw descriptor values for the candidate cohort.

    Returns:
        Unitless descriptor values scaled to the interval [0, 1].
    """
    lo = float(values.min())
    hi = float(values.max())
    if hi <= lo:
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return (values - lo) / (hi - lo)


PROJECT_DIR = Path(__file__).resolve().parents[1]


def perturbed_weights(component: str, variation: float) -> dict[str, float]:
    """Perturb one ACSI weight and rescale the remaining weights.

    Args:
        component: Component name whose baseline weight is perturbed.
        variation: Fractional change, for example ``-0.20`` or ``0.20``.

    Returns:
        A unit-sum mapping of component names to perturbed, unitless weights.
    """
    weights = dict(BASE_WEIGHTS)
    old = weights[component]
    new = old * (1.0 + variation)
    scale = (1.0 - new) / (1.0 - old)
    for key in weights:
        weights[key] = new if key == component else weights[key] * scale
    return weights


def main() -> None:
    """Generate the deterministic ACSI sensitivity records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results" / "c_acsi_scores.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results" / "c_acsi_weight_sensitivity.csv",
    )
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    required = {"smiles", "ACSI", *BASE_WEIGHTS}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise SystemExit(f"Input is missing required columns: {', '.join(missing)}")
    if len(frame) != 17 or frame["smiles"].duplicated().any():
        raise SystemExit("Canonical ACSI sensitivity requires 17 unique candidate rows")

    components = pd.DataFrame({key: minmax(frame[key]) for key in BASE_WEIGHTS})
    baseline = components.mul(pd.Series(BASE_WEIGHTS)).sum(axis=1)
    baseline_error = float((baseline - frame["ACSI"]).abs().max())
    if baseline_error > 1e-9:
        raise SystemExit(
            "Reconstructed baseline ACSI does not match the committed scores "
            f"(maximum absolute difference {baseline_error:.3e})"
        )
    baseline_order = baseline.sort_values(ascending=False).index.tolist()
    baseline_top5 = set(baseline_order[:5])

    records: list[dict[str, object]] = []
    for component in BASE_WEIGHTS:
        for variation in (-0.20, 0.20):
            weights = perturbed_weights(component, variation)
            score = components.mul(pd.Series(weights)).sum(axis=1)
            order = score.sort_values(ascending=False).index.tolist()
            rho = float(spearmanr(baseline, score).statistic)
            top5 = set(order[:5])
            jaccard = len(top5 & baseline_top5) / len(top5 | baseline_top5)
            records.append(
                {
                    "weight_varied": component,
                    "variation_percent": int(variation * 100),
                    "new_weight": weights[component],
                    "remaining_weight_scale": (1.0 - weights[component]) / (1.0 - BASE_WEIGHTS[component]),
                    "mean_acsi": float(score.mean()),
                    "sd_acsi": float(score.std(ddof=1)),
                    "spearman_vs_baseline": rho,
                    "top5_jaccard_vs_baseline": jaccard,
                    "n_candidates": len(frame),
                    "scope": "canonical_17_candidate_cohort",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output = pd.DataFrame(records)
    output.to_csv(args.output, index=False, float_format="%.6f")
    summary = {
        "schema_version": 1,
        "scope": "canonical_17_candidate_cohort",
        "input": str(args.input.relative_to(PROJECT_DIR)) if args.input.is_relative_to(PROJECT_DIR) else str(args.input),
        "n_candidates": len(frame),
        "baseline_weights": BASE_WEIGHTS,
        "perturbations": len(output),
        "minimum_spearman": float(output["spearman_vs_baseline"].min()),
        "minimum_top5_jaccard": float(output["top5_jaccard_vs_baseline"].min()),
        "all_top5_jaccard_ge_0_60": bool((output["top5_jaccard_vs_baseline"] >= 0.60).all()),
        "records": records,
    }
    args.output.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(output)} sensitivity rows to {args.output}")
    print(f"Minimum Spearman rho: {summary['minimum_spearman']:.4f}")
    print(f"Minimum top-five Jaccard: {summary['minimum_top5_jaccard']:.4f}")


if __name__ == "__main__":
    main()
