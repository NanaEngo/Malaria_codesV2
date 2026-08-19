#!/usr/bin/env python3
"""Regenerate rigorous, auditable secondary metrics for the canonical Set-C cohort.

This script does not perform docking or molecular dynamics. It re-analyses the
committed docking, ACSI, and PNS source tables with explicit candidate IDs,
target coverage, mutually exclusive RRS classes, deterministic permutation
p-values, bootstrap confidence intervals, PNS imputation sensitivity, and
explicit raw/normalised ACSI components.

All scores originating from AutoDock Vina are labelled as docking scores rather
than binding free energies. The resulting files are descriptive computational
records; they do not establish biochemical affinity, resistance, or target
engagement.

Outputs:
    results/c_rrs_classification.csv
    results/c_rrs_sensitivity.csv
    results/cross_metric_statistical_audit.csv
    results/cross_metric_statistical_audit.json
    results/pns_imputation_sensitivity.csv
    results/pns_imputation_sensitivity.json
    results/c_acsi_scores.csv
    results/p2_rigorous_audit_manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

SEED = 42
N_PERMUTATIONS = 100_000
N_BOOTSTRAP = 10_000
BASE_WEIGHTS = {
    "D_DrugBank": 0.40,
    "D_ANPDB": 0.25,
    "fsp3": 0.20,
    "NPL": 0.15,
}
TARGETS = ("PfDHFR", "PfCRT")
MUTATIONS = {
    "PfDHFR": ("N51I", "C59R", "S108N", "I164L"),
    "PfCRT": ("K76T", "K76A"),
}


def minmax(values: pd.Series) -> pd.Series:
    """Scale a raw unitless descriptor to [0, 1] over the canonical cohort.

    Args:
        values: Raw descriptor values for the 17-candidate cohort.

    Returns:
        Min--max normalised descriptor values.
    """
    lo = float(values.min())
    hi = float(values.max())
    if hi <= lo:
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return (values - lo) / (hi - lo)


def classify_rrs(values: list[float], wt_anchor: float) -> str:
    """Assign the mutually exclusive class implemented by the canonical rule.

    Args:
        values: Available mutant RRS percentages for one candidate.
        wt_anchor: Weakest eligible wild-type docking score magnitude in
            kcal/mol, used only for the A* potency discriminator.

    Returns:
        One of A*, A, B, C, or D. D means that no available mutant reaches
        80%; it is not defined as an arbitrary <60% cutoff.
    """
    if not values:
        return "D"
    all_ge_80 = all(value >= 80.0 for value in values)
    all_ge_70 = all(value >= 70.0 for value in values)
    any_ge_80 = any(value >= 80.0 for value in values)
    if all_ge_80:
        return "A*" if wt_anchor >= 7.0 else "A"
    if all_ge_70:
        return "B"
    if any_ge_80:
        return "C"
    return "D"


def candidate_ids(candidate_df: pd.DataFrame) -> dict[str, str]:
    """Map canonical candidate SMILES to stable PP identifiers.

    Args:
        candidate_df: Candidate-selection table in canonical rank order.

    Returns:
        Mapping from canonical SMILES to PP-01 through PP-17.
    """
    if "smiles" not in candidate_df or len(candidate_df) != 17:
        raise ValueError("Canonical Set-C candidate table must contain 17 SMILES")
    if candidate_df["smiles"].duplicated().any():
        raise ValueError("Canonical candidate table contains duplicate SMILES")
    return {smiles: f"PP-{index:02d}" for index, smiles in enumerate(candidate_df["smiles"], 1)}


def build_rrs(docking: pd.DataFrame, ids: dict[str, str]) -> pd.DataFrame:
    """Build target-specific RRS, coverage, and reproducible class records.

    Args:
        docking: WT and mutant Vina score table.
        ids: Stable candidate-ID mapping.

    Returns:
        One row per candidate with target-specific docking scores, coverage,
        available-target RRS values, and complete-two-target classifications.
    """
    records: list[dict[str, object]] = []
    for smiles, candidate in docking.groupby("smiles", sort=False):
        if smiles not in ids:
            continue
        record: dict[str, object] = {"candidate_id": ids[smiles], "smiles": smiles}
        target_rrs: list[float] = []
        target_values: dict[str, list[float]] = {target: [] for target in TARGETS}
        eligible_targets: list[str] = []
        all_mutant_values: list[float] = []
        target_wt: dict[str, float] = {}
        for target in TARGETS:
            wt_rows = candidate[(candidate["target"] == target) & (candidate["mutation"] == "WT")]
            wt = float(wt_rows["vina_score"].mean()) if not wt_rows.empty else np.nan
            target_wt[target] = wt
            record[f"s_Vina_WT_{target}"] = wt
            eligible = bool(np.isfinite(wt) and abs(wt) >= 5.0)
            record[f"RRS_target_eligible_{target}"] = eligible
            if eligible:
                eligible_targets.append(target)
            for mutation in MUTATIONS[target]:
                rows = candidate[(candidate["target"] == target) & (candidate["mutation"] == mutation)]
                score = float(rows["vina_score"].mean()) if not rows.empty else np.nan
                record[f"s_Vina_{target}_{mutation}"] = score
                rrs = abs(score) / abs(wt) * 100.0 if eligible and np.isfinite(score) else np.nan
                record[f"RRS_{target}_{mutation}"] = rrs
                if np.isfinite(rrs):
                    target_rrs.append(rrs)
                    target_values[target].append(rrs)
                    all_mutant_values.append(rrs)
        for target in TARGETS:
            values = target_values[target]
            record[f"RRS_mean_{target}"] = float(np.mean(values)) if values else np.nan
            record[f"RRS_class_{target}"] = (
                classify_rrs(values, abs(target_wt[target]))
                if values and np.isfinite(target_wt[target])
                else "N/A"
            )
        anchor = max((abs(target_wt[t]) for t in eligible_targets), default=np.nan)
        min_wt = min((abs(target_wt[t]) for t in eligible_targets), default=np.nan)
        record["eligible_target_count"] = len(eligible_targets)
        record["eligible_targets"] = ";".join(eligible_targets)
        record["available_mutant_count"] = len(all_mutant_values)
        record["WT_anchor_max_abs_kcal_mol"] = anchor
        record["WT_anchor_min_abs_kcal_mol"] = min_wt
        record["RRS_mean_available"] = float(np.mean(all_mutant_values)) if all_mutant_values else np.nan
        record["RRS_class_available"] = classify_rrs(all_mutant_values, min_wt) if np.isfinite(min_wt) else "N/A"

        complete_values: list[float] = []
        for target in TARGETS:
            if not record[f"RRS_target_eligible_{target}"]:
                continue
            complete_values.extend(
                float(record[f"RRS_{target}_{mutation}"])
                for mutation in MUTATIONS[target]
                if np.isfinite(record[f"RRS_{target}_{mutation}"])
            )
        complete = len(eligible_targets) == len(TARGETS) and len(complete_values) == 6
        record["complete_two_target_panel"] = complete
        record["RRS_class_complete_two_target"] = (
            classify_rrs(complete_values, min_wt) if complete else "N/A"
        )
        record["RRS_mean_complete_two_target"] = (
            float(np.mean(complete_values)) if complete else np.nan
        )
        # Stable compatibility aliases are intentionally the available-target
        # estimand. The available-target class uses the weakest eligible WT
        # score, so a strong second target cannot promote an imbalanced
        # candidate. The target-specific columns above remain authoritative for
        # target-balanced reporting and figure generation.
        record["RRS_WT"] = 100.0
        for target, mutations in MUTATIONS.items():
            for mutation in mutations:
                if mutation == "WT":
                    continue
                record[f"RRS_{mutation}"] = record[f"RRS_{target}_{mutation}"]
        record["RRS_mean"] = record["RRS_mean_available"]
        record["RRS_class"] = record["RRS_class_available"]
        records.append(record)
    return pd.DataFrame(records).sort_values("candidate_id").reset_index(drop=True)


def permutation_spearman(
    x: np.ndarray,
    y: np.ndarray,
    rng: np.random.Generator,
    n_permutations: int = N_PERMUTATIONS,
) -> tuple[float, float]:
    """Estimate a two-sided permutation p-value for Spearman correlation.

    Args:
        x: First finite-valued vector.
        y: Second finite-valued vector.
        rng: Seeded NumPy random generator.
        n_permutations: Number of random permutations.

    Returns:
        Observed Spearman rho and +1 corrected two-sided permutation p-value.
    """
    observed = float(spearmanr(x, y).statistic)
    xr = rankdata(x).astype(float)
    yr = rankdata(y).astype(float)
    xr = (xr - xr.mean()) / xr.std(ddof=0)
    yr = (yr - yr.mean()) / yr.std(ddof=0)
    exceed = 0
    for _ in range(n_permutations):
        perm = rng.permutation(yr)
        value = float(np.mean(xr * perm))
        exceed += abs(value) >= abs(observed) - 1e-12
    return observed, float((exceed + 1) / (n_permutations + 1))


def bootstrap_spearman_ci(
    x: np.ndarray,
    y: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int = N_BOOTSTRAP,
) -> tuple[float, float]:
    """Compute a percentile bootstrap interval for Spearman rho.

    Args:
        x: First finite-valued vector.
        y: Second finite-valued vector.
        rng: Seeded NumPy random generator.
        n_bootstrap: Number of resamples.

    Returns:
        Lower and upper 95% percentile interval bounds.
    """
    values = np.empty(n_bootstrap, dtype=float)
    n = len(x)
    for index in range(n_bootstrap):
        sample = rng.integers(0, n, n)
        values[index] = float(spearmanr(x[sample], y[sample]).statistic)
    finite = values[np.isfinite(values)]
    if len(finite) < 0.95 * n_bootstrap:
        return np.nan, np.nan
    return tuple(float(value) for value in np.percentile(finite, [2.5, 97.5]))


def infer_pf_dhfr_centrality(
    docking: pd.DataFrame,
    pns_table: pd.DataFrame,
    pfcrt_weight: float,
) -> float:
    """Infer the canonical PfDHFR weight from the committed PNS output.

    The qom environment intentionally does not require NetworkX. The
    committed PNS table and WT docking scores are sufficient to reconstruct
    the PfDHFR weight used in the two-target mean, while the manuscript
    records the PfCRT imputation as 0.151.

    Args:
        docking: WT docking score table.
        pns_table: Committed PNS output with one row per candidate.
        pfcrt_weight: Canonical PfCRT centrality imputation.

    Returns:
        Median inferred PfDHFR centrality across candidates, dimensionless.
    """
    wt = docking[docking["mutation"] == "WT"].pivot_table(
        index="smiles", columns="target", values="vina_score", aggfunc="mean"
    )
    merged = pns_table.merge(wt, on="smiles", validate="one_to_one")
    required = {"PNS", "PfDHFR", "PfCRT"}
    if not required.issubset(merged.columns):
        raise ValueError("Cannot reconstruct PNS weights from the WT docking table")
    inferred = (2.0 * merged["PNS"] - pfcrt_weight * merged["PfCRT"].abs()) / merged["PfDHFR"].abs()
    inferred = inferred.replace([np.inf, -np.inf], np.nan).dropna()
    if inferred.empty:
        raise ValueError("No finite PfDHFR centrality values could be inferred")
    return float(inferred.median())


def pns_scores(docking: pd.DataFrame, pfcrt_weight: float, observed: dict[str, float]) -> pd.Series:
    """Compute two-target PNS under a specified PfCRT centrality imputation.

    Args:
        docking: WT docking score table.
        pfcrt_weight: Imputed PfCRT centrality.
        observed: STRING centrality map keyed by target IDs.

    Returns:
        PNS values indexed by candidate SMILES.
    """
    target_ids = {"PfDHFR": "PF3D7_0417200", "PfCRT": "PF3D7_0709000"}
    scores: dict[str, float] = {}
    for smiles, group in docking[docking["mutation"] == "WT"].groupby("smiles"):
        terms = []
        for target in TARGETS:
            rows = group[group["target"] == target]
            if rows.empty:
                continue
            weight = pfcrt_weight if target == "PfCRT" else observed.get(target_ids[target], 0.0)
            terms.append(weight * abs(float(rows["vina_score"].mean())))
        if terms:
            scores[smiles] = float(np.mean(terms))
    return pd.Series(scores, dtype=float)


def main() -> None:
    """Regenerate all rigorous computational audit outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    project = args.project_dir.resolve()
    results = project / "results"
    candidate_path = results / "candidate_selection" / "md_top20_candidates_polypharm.csv"
    docking_path = results / "docking_mutants.csv"
    candidate_df = pd.read_csv(candidate_path)
    docking = pd.read_csv(docking_path)
    ids = candidate_ids(candidate_df)
    if set(ids) != set(docking["smiles"]):
        raise ValueError("Docking and candidate cohorts do not contain identical SMILES sets")

    rrs = build_rrs(docking, ids)
    rrs.insert(0, "cohort_id", "P2_SET_C_POLYPHARM_17")
    rrs.insert(2, "candidate_file", str(candidate_path.relative_to(project)))
    rrs["candidate_sha256"] = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    rrs.to_csv(results / "c_rrs_classification.csv", index=False, float_format="%.8f")

    sensitivity = rrs[
        [
            "candidate_id",
            "eligible_target_count",
            "eligible_targets",
            "available_mutant_count",
            "RRS_mean_available",
            "RRS_class_available",
            "complete_two_target_panel",
            "RRS_mean_complete_two_target",
            "RRS_class_complete_two_target",
            "WT_anchor_max_abs_kcal_mol",
            "WT_anchor_min_abs_kcal_mol",
        ]
    ].copy()
    sensitivity.to_csv(results / "c_rrs_sensitivity.csv", index=False, float_format="%.8f")

    acsi = pd.read_csv(results / "c_acsi_scores.csv")
    if set(BASE_WEIGHTS) - set(acsi.columns):
        raise ValueError("ACSI source table lacks raw component columns")
    normalised = {f"{key}_normalized": minmax(acsi[key]) for key in BASE_WEIGHTS}
    for key, values in normalised.items():
        acsi[key] = values
    reconstructed = sum(acsi[f"{key}_normalized"] * weight for key, weight in BASE_WEIGHTS.items())
    max_error = float((reconstructed - acsi["ACSI"]).abs().max())
    if max_error > 1e-9:
        raise ValueError(f"ACSI reconstruction mismatch: {max_error:.3e}")
    acsi["ACSI_reconstruction_abs_error"] = (reconstructed - acsi["ACSI"]).abs()
    acsi.to_csv(results / "c_acsi_scores.csv", index=False, float_format="%.10f")

    merged = rrs[
        [
            "candidate_id",
            "smiles",
            "RRS_mean_available",
            "RRS_mean_complete_two_target",
            "WT_anchor_max_abs_kcal_mol",
            "WT_anchor_min_abs_kcal_mol",
            "complete_two_target_panel",
        ]
    ].merge(acsi[["smiles", "ACSI"]], on="smiles", validate="one_to_one")
    pns = pd.read_csv(results / "c_pns_ranking.csv")[["smiles", "PNS"]]
    merged = merged.merge(pns, on="smiles", validate="one_to_one")
    rng = np.random.default_rng(SEED)
    available = merged.dropna(subset=["RRS_mean_available", "PNS", "ACSI"]).copy()
    complete = merged[merged["complete_two_target_panel"]].dropna(
        subset=["RRS_mean_complete_two_target", "PNS", "ACSI"]
    ).copy()
    pair_specs = [
        (
            "available_17",
            {
                "PNS_vs_RRS": (available["PNS"].to_numpy(), available["RRS_mean_available"].to_numpy()),
                "ACSI_vs_PNS": (available["ACSI"].to_numpy(), available["PNS"].to_numpy()),
                "ACSI_vs_RRS": (available["ACSI"].to_numpy(), available["RRS_mean_available"].to_numpy()),
                "RRS_vs_WT_anchor_min": (available["RRS_mean_available"].to_numpy(), available["WT_anchor_min_abs_kcal_mol"].to_numpy()),
            },
        ),
        (
            "complete_two_target_12",
            {
                "PNS_vs_RRS": (complete["PNS"].to_numpy(), complete["RRS_mean_complete_two_target"].to_numpy()),
                "ACSI_vs_PNS": (complete["ACSI"].to_numpy(), complete["PNS"].to_numpy()),
                "ACSI_vs_RRS": (complete["ACSI"].to_numpy(), complete["RRS_mean_complete_two_target"].to_numpy()),
                "RRS_vs_WT_anchor_min": (complete["RRS_mean_complete_two_target"].to_numpy(), complete["WT_anchor_min_abs_kcal_mol"].to_numpy()),
            },
        ),
    ]
    stats = []
    for analysis_set, pairs in pair_specs:
        for name, (x, y) in pairs.items():
            rho, p_perm = permutation_spearman(x, y, rng)
            low, high = bootstrap_spearman_ci(x, y, rng)
            stats.append(
                {
                    "analysis_set": analysis_set,
                    "comparison": name,
                    "n": len(x),
                    "spearman_rho": rho,
                    "permutation_p_two_sided": p_perm,
                    "bonferroni_p_three_hypotheses": min(1.0, 3.0 * p_perm),
                    "bootstrap_ci95_low": low,
                    "bootstrap_ci95_high": high,
                    "inference_scope": "exploratory_selected_cohort; not independent validation",
                }
            )
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv(results / "cross_metric_statistical_audit.csv", index=False, float_format="%.8f")
    (results / "cross_metric_statistical_audit.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "n_permutations": N_PERMUTATIONS,
                "n_bootstrap": N_BOOTSTRAP,
                "multiplicity_note": "Permutation p-values are two-sided and +1 corrected; the reported Bonferroni value multiplies each p-value by three for the prespecified H1-H3 family and is capped at 1. Bootstrap intervals are descriptive and should not be interpreted as independent validation after candidate selection; complete_two_target_12 is the target-balanced sensitivity set.",
                "records": stats,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    pns_table = pd.read_csv(results / "c_pns_ranking.csv")
    canonical_pfcrt = 0.151
    inferred_pf_dhfr = infer_pf_dhfr_centrality(docking, pns_table, canonical_pfcrt)
    centrality = {"PF3D7_0417200": inferred_pf_dhfr}
    alternatives = {
        "zero": 0.0,
        "half_canonical": canonical_pfcrt * 0.5,
        "canonical_mean": canonical_pfcrt,
        "one_and_half_canonical": canonical_pfcrt * 1.5,
        "double_canonical": canonical_pfcrt * 2.0,
    }
    baseline = pns_scores(docking, canonical_pfcrt, centrality)
    pns_records = []
    for label, weight in alternatives.items():
        values = pns_scores(docking, weight, centrality)
        aligned = pd.concat([baseline.rename("baseline"), values.rename("alternative")], axis=1).dropna()
        rho = float(spearmanr(aligned["baseline"], aligned["alternative"]).statistic)
        pns_records.append(
            {
                "imputation": label,
                "pfcrt_centrality": weight,
                "spearman_rank_vs_canonical": rho,
                "pns_range_min": float(values.min()),
                "pns_range_max": float(values.max()),
                "n_candidates": len(values),
            }
        )
    pns_df = pd.DataFrame(pns_records)
    pns_df.to_csv(results / "pns_imputation_sensitivity.csv", index=False, float_format="%.8f")
    (results / "pns_imputation_sensitivity.json").write_text(
        json.dumps(
            {
                "canonical_imputation": "canonical_mean",
                "canonical_pfcrt_centrality": canonical_pfcrt,
                "inferred_pf_dhfr_centrality": inferred_pf_dhfr,
                "records": pns_records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema_version": 1,
        "script": "scripts/p2_rigorous_audit.py",
        "seed": SEED,
        "candidate_count": len(candidate_df),
        "docking_rows": len(docking),
        "eligible_target_counts": {str(k): int(v) for k, v in rrs["eligible_target_count"].value_counts().to_dict().items()},
        "available_mutant_counts": {str(k): int(v) for k, v in rrs["available_mutant_count"].value_counts().to_dict().items()},
        "complete_two_target_count": int(rrs["complete_two_target_panel"].sum()),
        "available_class_counts": {str(k): int(v) for k, v in rrs["RRS_class_available"].value_counts().to_dict().items()},
        "complete_class_counts": {str(k): int(v) for k, v in rrs.loc[rrs["complete_two_target_panel"], "RRS_class_complete_two_target"].value_counts().to_dict().items()},
        "class_definition": "A*/A/B/C/D mutually exclusive; D means no available mutant RRS reaches 80%; A* and A use the minimum eligible WT score magnitude; complete-two-target status reported separately.",
        "acsi_normalization": "cohort min-max over the raw component columns in c_acsi_scores.csv",
        "permutation_count": N_PERMUTATIONS,
        "bootstrap_count": N_BOOTSTRAP,
        "outputs": [
            "results/c_rrs_classification.csv",
            "results/c_rrs_sensitivity.csv",
            "results/cross_metric_statistical_audit.csv",
            "results/cross_metric_statistical_audit.json",
            "results/pns_imputation_sensitivity.csv",
            "results/pns_imputation_sensitivity.json",
            "results/c_acsi_scores.csv",
        ],
    }
    (results / "p2_rigorous_audit_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Rigorous audit outputs regenerated.")
    print(f"RRS classes (available targets): {rrs['RRS_class_available'].value_counts().to_dict()}")
    print(f"Complete two-target candidates: {int(rrs['complete_two_target_panel'].sum())}/{len(rrs)}")
    print(f"ACSI maximum reconstruction error: {max_error:.3e}")
    print(f"PNS imputation sensitivity minimum rank rho: {pns_df['spearman_rank_vs_canonical'].min():.6f}")


if __name__ == "__main__":
    main()
