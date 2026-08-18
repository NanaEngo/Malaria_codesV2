#!/usr/bin/env python3
"""Unit tests for the PfCRT junction-repair and MD-RRS discriminative scripts.

These tests exercise pure logic and manifest integrity without launching
OpenMM/GROMACS/MDAnalysis heavy runs (the expensive stages are validated by the
provenance manifests themselves). Fast, deterministic, no GPU/CPU MD required.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_DIR / "results" / "md_systems"
SET_C_MD = PROJECT_DIR / "results" / "set_c_md"


# ---------------------------------------------------------------------------
# Discriminative MD-RRS manifest integrity
# ---------------------------------------------------------------------------

def test_discriminative_manifest_exists_and_computed():
    path = SET_C_MD / "md_rrs_discriminative_manifest.json"
    assert path.is_file(), "discriminative MD-RRS manifest missing"
    manifest = json.loads(path.read_text())
    assert manifest["status"] == "MD_RRS_DISCRIMINATIVE_COMPUTED"
    assert manifest["analysis_rule_id"] == "setc_p2_multithreshold_continuous_v1"


def test_discriminative_manifest_has_16_records_and_12_ratios():
    path = SET_C_MD / "md_rrs_discriminative_manifest.json"
    manifest = json.loads(path.read_text())
    records = manifest["rows"]
    ratios = manifest["ratios"]
    # 16 systems = 2 candidates x (5 PfDHFR + 3 PfCRT)
    assert len(records) == 16
    # 12 ratios = 2 candidates x (4 PfDHFR mutants + 2 PfCRT mutants)
    assert len(ratios) == 12
    targets = {r["target"] for r in records}
    assert targets == {"PfDHFR", "PfCRT"}


def test_discriminative_manifest_metrics_are_continuous():
    path = SET_C_MD / "md_rrs_discriminative_manifest.json"
    manifest = json.loads(path.read_text())
    for row in manifest["rows"]:
        assert 0.0 <= row["mean_min_dist_A"] <= 20.0
        assert 0.0 <= row["bound_frac_5A"] <= 1.0
        assert row["n_frames"] >= 500
        # stricter thresholds must be <= looser ones
        assert row["bound_frac_2A"] <= row["bound_frac_3A"] <= row["bound_frac_5A"] + 1e-9


def test_discriminative_matches_qc_log():
    """mean_min_dist_A must match the independent QC job-15386 log values."""
    import re

    log_vals = {}
    log_path = PROJECT_DIR / "logs" / "p2_setc_qc_rrs_15386.log"
    if not log_path.is_file():
        pytest.skip("QC 15386 log not present")
    for line in log_path.read_text().splitlines():
        m = re.match(r"(\S+): n_frames=(\d+) bound_frac=([\d.]+) mean_min=([\d.]+) A", line)
        if m:
            log_vals[m.group(1)] = float(m.group(4))
    path = SET_C_MD / "set_c_trajectory_metrics_pilot.csv"
    import csv

    rows = list(csv.DictReader(path.open()))
    assert len(rows) == 16
    for row in rows:
        key = f"{row['set_c_id']}_{row['target']}_{row['mutation']}"
        assert key in log_vals, f"missing QC log value for {key}"
        assert abs(float(row["mean_min_dist_A"]) - log_vals[key]) < 0.01


# ---------------------------------------------------------------------------
# Junction repair ensemble manifest integrity
# ---------------------------------------------------------------------------

def test_junction_repair_ensemble_manifest_completed():
    path = RESULTS / "pfcrt_junction_repair_ensemble_20260818" / "junction_repair_ensemble_manifest.json"
    assert path.is_file(), "junction repair ensemble manifest missing"
    manifest = json.loads(path.read_text())
    assert manifest["status"] == "JUNCTION_REPAIR_ENSEMBLE_COMPLETED"
    assert manifest["counts"]["passing"] >= 1
    assert manifest["selected_candidate"] is not None


def test_junction_repair_selected_candidate_passes_gate():
    path = RESULTS / "pfcrt_junction_repair_ensemble_20260818" / "junction_repair_ensemble_manifest.json"
    manifest = json.loads(path.read_text())
    selected = manifest["selected_candidate"]
    cand_dir = RESULTS / "pfcrt_junction_repair_ensemble_20260818" / selected
    audit = json.loads((cand_dir / "junction_repair_audit.json").read_text())
    assert audit["status"] == "PASS_GEOMETRY"
    a = audit["audit"]
    assert a["sequence_114_122"] == "NKKGNSKER"
    assert a["core_clash_screen_pass"] is True
    bonds = a["peptide_bond_distances_A"]
    assert len(bonds) == 10
    assert all(1.0 <= v <= 1.8 for v in bonds.values()), "peptide bonds out of range"
    # repaired.pdb sha matches manifest
    import hashlib

    repaired = cand_dir / "repaired.pdb"
    assert repaired.is_file()
    digest = hashlib.sha256(repaired.read_bytes()).hexdigest()
    assert digest == manifest["selected_output_sha256"]


# ---------------------------------------------------------------------------
# MD-RRS vs docking cross-comparison
# ---------------------------------------------------------------------------

def test_md_vs_docking_comparison_file_exists():
    path = SET_C_MD / "md_vs_docking_comparison_pilot.csv"
    assert path.is_file(), "MD vs docking comparison CSV missing"
    import csv

    rows = list(csv.DictReader(path.open()))
    assert len(rows) == 12  # 2 candidates x 6 mutants
    assert {"MD_RRS_mean_min_dist_A", "dock_RRS", "MD_direction", "dock_direction"} <= set(rows[0].keys())


def test_md_vs_docking_directions_are_consistent_fields():
    import csv

    path = SET_C_MD / "md_vs_docking_comparison_pilot.csv"
    rows = list(csv.DictReader(path.open()))
    for row in rows:
        assert row["MD_direction"] in {"tighter", "looser", "equal"}
        assert row["dock_direction"] in {"tighter", "looser", "equal", "n/a"}
        md_val = float(row["MD_RRS_mean_min_dist_A"])
        # MD direction must match the numeric value
        if md_val < 100:
            assert row["MD_direction"] == "tighter"
        elif md_val > 100:
            assert row["MD_direction"] == "looser"


# ---------------------------------------------------------------------------
# GROMACS canonical check + MD witness manifests
# ---------------------------------------------------------------------------

def test_gromacs_check_manifest_pass():
    path = RESULTS / "pfcrt_gromacs_check_20260818" / "gromacs_check_manifest.json"
    assert path.is_file()
    manifest = json.loads(path.read_text())
    assert manifest["status"] == "GROMACS_CANONICAL_POLICY_CHECK_PASS"
    assert manifest["pdb2gmx"]["chains"] == 1
    assert manifest["pdb2gmx"]["internal_split"] is False
    assert manifest["pdb2gmx"]["residues"] == 359


def test_md_witness_manifest_pass():
    path = RESULTS / "pfcrt_md_witness_20260818" / "md_witness_manifest.json"
    assert path.is_file()
    manifest = json.loads(path.read_text())
    assert manifest["status"] == "CANONICAL_MD_WITNESS_PASS"
    assert manifest["nvt"]["steps"] == 50000
    assert manifest["npt"]["steps"] == 50000
    # temperature must be near the 310.15 K target
    assert abs(manifest["npt"]["temperature_k"]["mean"] - 310.15) < 5.0
    # density TIP3P-typical at 310 K
    assert 950.0 <= manifest["npt"]["density_kg_m3"]["mean"] <= 1050.0
    assert manifest["npt"]["error_markers"] == 0
