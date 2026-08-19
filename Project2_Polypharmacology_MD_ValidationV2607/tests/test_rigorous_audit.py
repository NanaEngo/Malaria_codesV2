"""Integrity tests for the rigorous Set-C audit outputs.

These tests validate estimand definitions and committed data artifacts without
running docking, molecular dynamics, or network reconstruction.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_DIR / "results"


def test_rrs_class_definition_is_mutually_exclusive():
    from p2_rigorous_audit import classify_rrs

    assert classify_rrs([80.0, 90.0], 7.0) == "A*"
    assert classify_rrs([80.0, 90.0], 6.9) == "A"
    assert classify_rrs([70.0, 79.9], 8.0) == "B"
    assert classify_rrs([69.9, 80.0], 8.0) == "C"
    assert classify_rrs([69.9, 79.9], 8.0) == "D"


def test_rrs_coverage_and_primary_class_counts():
    data = pd.read_csv(RESULTS / "c_rrs_classification.csv")
    assert len(data) == 17
    assert data["eligible_target_count"].value_counts().to_dict() == {2: 12, 1: 5}
    assert data["available_mutant_count"].value_counts().to_dict() == {6: 12, 2: 5}
    assert data["RRS_class_available"].value_counts().to_dict() == {
        "A*": 5,
        "A": 1,
        "B": 5,
        "C": 5,
        "D": 1,
    }
    complete = data[data["complete_two_target_panel"]]
    assert len(complete) == 12
    assert complete["RRS_class_complete_two_target"].value_counts().to_dict() == {
        "A*": 1,
        "A": 1,
        "B": 4,
        "C": 5,
        "D": 1,
    }
    assert data.loc[data["candidate_id"] == "PP-15", "RRS_class_available"].item() == "A"


def test_statistical_audit_contains_primary_and_sensitivity_sets():
    stats = pd.read_csv(RESULTS / "cross_metric_statistical_audit.csv")
    assert set(stats["analysis_set"]) == {"available_17", "complete_two_target_12"}
    assert "bonferroni_p_three_hypotheses" in stats.columns
    primary = stats[stats["analysis_set"] == "complete_two_target_12"]
    assert set(primary["comparison"]) == {
        "PNS_vs_RRS",
        "ACSI_vs_PNS",
        "ACSI_vs_RRS",
        "RRS_vs_WT_anchor_min",
    }
    h1 = primary[primary["comparison"] == "PNS_vs_RRS"].iloc[0]
    assert abs(h1["spearman_rho"] + 0.20979021) < 1e-6
    assert h1["bonferroni_p_three_hypotheses"] == 1.0


def test_pns_imputation_sensitivity_is_ranked_and_complete():
    sensitivity = pd.read_csv(RESULTS / "pns_imputation_sensitivity.csv")
    assert len(sensitivity) == 5
    assert set(sensitivity["n_candidates"]) == {17}
    assert sensitivity["spearman_rank_vs_canonical"].min() >= 0.95
    manifest = json.loads((RESULTS / "p2_rigorous_audit_manifest.json").read_text())
    assert manifest["candidate_count"] == 17
    assert manifest["docking_rows"] == 136
    assert "minimum eligible WT score" in manifest["class_definition"]
