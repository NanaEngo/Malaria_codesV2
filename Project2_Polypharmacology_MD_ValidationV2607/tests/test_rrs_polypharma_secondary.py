"""Guard tests for the 28 Aug secondary bootstrap / MD-filter gate artifacts.

The DAR entry (P2_DATA_ANALYSIS_REPORT.md, section "RRS/polypharma secondary
bootstrap and MD-filter gate (28 August 2026; documented 28-09-2026)") must
stay consistent with the committed artifacts under
`results/rrs_polypharma_secondary_20260828/`. These tests fail if the
artifacts are regenerated with a different scope or values without a
corresponding DAR update. Everything here is `COMPUTED_SECONDARY`: no
canonical value and no manuscript claim depends on these outputs.
"""

import json
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "results" / "rrs_polypharma_secondary_20260828"


def _summary() -> dict:
    return json.loads((OUT / "secondary_summary.json").read_text(encoding="utf-8"))


def test_status_bootstrap_params_and_boundary_are_secondary():
    s = _summary()
    assert s["status"] == "COMPUTED_SECONDARY"
    assert s["bootstrap"] == {"B": 10000, "seed": 42, "ci": "95%"}
    assert "no canonical value replaced" in s["boundary"]
    assert "pilot-scope only" in s["boundary"]


def test_run1_class_fractions_match_dar_entry():
    run1 = _summary()["run1_setc_bootstrap"]
    assert run1["n_candidates"] == 17
    # Pooled available-target estimand (RRS_class); consistent with the 25 Aug
    # RUN3 cohort bootstrap, including the class-A interval [0, 0.176].
    assert run1["class_A*_fraction"]["ci95"] == [0.1176, 0.5294]
    assert run1["class_A_fraction"]["ci95"] == [0.0, 0.1765]
    assert run1["class_D_fraction"]["ci95"] == [0.0, 0.1765]
    assert run1["retention_N51I"]["point"] == 74.71
    assert run1["retention_N51I"]["ci95"] == [67.22, 85.16]
    assert run1["retention_N51I"]["n"] == 12
    assert run1["retention_K76T"]["n"] == 17
    assert run1["mean_RRS_PfDHFR"]["n"] == 12
    assert run1["mean_RRS_PfCRT"]["n"] == 17


def test_run1b_external_panel_matches_dar_entry():
    run1b = _summary()["run1b_external_bootstrap"]
    assert run1b["n_ligands"] == 39
    assert run1b["mean_RRS"]["point"] == 100.45
    assert run1b["class_A_fraction"]["point"] == 0.9744


def test_run2_md_filter_gate_is_pilot_scope_only():
    gate = _summary()["run2_md_filter_gate"]
    assert gate["scope"].startswith("PP-01/PP-02 pilot only")
    assert gate["n_gate_rows"] == 12
    assert gate["n_passes_both"] == 7
    # Only PP-01 passes on >= 2 targets at pilot scope; exploratory label only.
    assert gate["polypharma_promoted_pilot"] == {"PP-01": ["PfCRT", "PfDHFR"]}


def test_md_filter_gate_csv_rows_are_consistent_with_summary():
    rows = pd.read_csv(OUT / "md_filter_gate.csv")
    assert len(rows) == 12
    assert set(rows["candidate"]) == {"PP-01", "PP-02"}
    assert int(rows["passes_both"].sum()) == 7
    # Fail-closed: rows without a WT-eligible docking reference cannot pass.
    assert rows.loc[rows["docking_rrs"].isna(), "docking_gate_ge80"].eq(False).all()
