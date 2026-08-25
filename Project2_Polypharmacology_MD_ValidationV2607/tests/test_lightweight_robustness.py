from pathlib import Path

import pandas as pd

from scripts.p2_lightweight_robustness import classify


PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "results" / "lightweight_robustness"


def test_classification_boundaries_are_mutually_exclusive():
    assert classify([80.0, 80.0], 7.0) == "A*"
    assert classify([80.0, 80.0], 6.9) == "A"
    assert classify([70.0, 70.0], 6.9) == "B"
    assert classify([80.0, 69.9], 6.9) == "C"
    assert classify([69.9, 69.9], 6.9) == "D"
    assert classify([], 7.0) == "D"


def test_generated_robustness_tables_have_expected_shapes():
    threshold = pd.read_csv(OUT / "rrs_threshold_sensitivity.csv")
    loo = pd.read_csv(OUT / "rrs_leave_one_mutant_out.csv")
    perturb = pd.read_csv(OUT / "docking_score_perturbation.csv")
    assert len(threshold) == 17 * 4 * 3
    assert len(loo) == 17 * 7
    assert len(perturb) == 17 * 4
    assert set(threshold["wt_threshold_kcal_mol"]) == {4.0, 5.0, 6.0, 7.0}
    assert set(zip(threshold["retention_low_percent"], threshold["retention_high_percent"])) == {(70.0, 80.0), (75.0, 85.0), (80.0, 90.0)}
    assert set(perturb["score_perturbation_percent"]) == {-20, -10, 10, 20}
    assert threshold["smiles"].nunique() == 17
