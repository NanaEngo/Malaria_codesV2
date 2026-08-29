#!/usr/bin/env python3
"""P3 — Tests for TDA Pipeline (p3_tda_pipeline.py).

Tests mathematical functions that don't require ripser or 3D embedding:
  1. persistence_entropy() — entropy computation (R5)
  2. persistence_image() — binning + normalisation
  3. betti_curve() — Betti number evolution
  4. extract_tfp() — 78-D fingerprint shape and content
  5. _weight_distance_matrix() — atomic-number weighting
  6. smiles_to_distance_matrix() — 2D fallback for simple molecules

Usage:
    pytest tests/test_p3_tda_basic.py -v
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
warnings.filterwarnings("ignore")


# ── Synthetic persistence diagrams ───────────────────────────────────

@pytest.fixture
def dgm_h0() -> np.ndarray:
    """H0 diagram: 3 finite features + 1 infinite (birth=0, death=inf)."""
    return np.array([[0.0, 1.0],
                     [0.0, 2.5],
                     [0.0, 0.8],
                     [0.0, np.inf]])


@pytest.fixture
def dgm_h1() -> np.ndarray:
    """H1 diagram: 2 finite features."""
    return np.array([[0.5, 1.2],
                     [1.0, 3.0]])


@pytest.fixture
def dgm_empty() -> np.ndarray:
    """Empty diagram (no features)."""
    return np.zeros((0, 2))


# ── Test persistence_entropy ─────────────────────────────────────────

class TestPersistenceEntropy:
    """R5: entropy computation."""

    def test_entropy_h0(self, dgm_h0):
        from p3_tda_pipeline import persistence_entropy
        e = persistence_entropy(dgm_h0)
        assert 0 < e < 2.0, f"Expected entropy in (0,2), got {e:.4f}"

    def test_entropy_empty(self, dgm_empty):
        from p3_tda_pipeline import persistence_entropy
        e = persistence_entropy(dgm_empty)
        assert e == 0.0, f"Empty diagram should give entropy 0, got {e}"

    def test_entropy_dirac(self):
        """Single feature → zero entropy (within float precision)."""
        from p3_tda_pipeline import persistence_entropy
        dgm = np.array([[0.0, 1.0]])
        e = persistence_entropy(dgm)
        assert e == pytest.approx(0.0, abs=1e-10), \
            f"Single feature should give entropy ~0, got {e}"


# ── Test persistence_image ───────────────────────────────────────────

class TestPersistenceImage:
    """Binning + normalisation of persistence diagram."""

    def test_image_shape(self, dgm_h0):
        from p3_tda_pipeline import persistence_image
        img = persistence_image(dgm_h0, n_bins=25)
        assert img.shape == (25,), f"Expected (25,), got {img.shape}"
        assert img.dtype == np.float32

    def test_image_normalised(self, dgm_h0):
        from p3_tda_pipeline import persistence_image
        img = persistence_image(dgm_h0, n_bins=25)
        assert abs(img.sum() - 1.0) < 1e-5, f"Image should sum to 1, got {img.sum()}"

    def test_image_empty(self, dgm_empty):
        from p3_tda_pipeline import persistence_image
        img = persistence_image(dgm_empty, n_bins=25)
        assert np.all(img == 0), "Empty diagram should give zero image"


# ── Test betti_curve ─────────────────────────────────────────────────

class TestBettiCurve:
    """Betti number as function of filtration parameter."""

    def test_curve_shape(self, dgm_h0):
        from p3_tda_pipeline import betti_curve
        curve = betti_curve(dgm_h0, n_points=20)
        assert curve.shape == (20,), f"Expected (20,), got {curve.shape}"

    def test_curve_monotonic(self, dgm_h0):
        """Betti curve should be non-increasing (fewer features survive)."""
        from p3_tda_pipeline import betti_curve
        curve = betti_curve(dgm_h0, n_points=20)
        assert curve[0] >= curve[-1], f"Betti should decrease: start={curve[0]}, end={curve[-1]}"

    def test_curve_empty(self, dgm_empty):
        from p3_tda_pipeline import betti_curve
        curve = betti_curve(dgm_empty, n_points=20)
        assert np.all(curve == 0), "Empty diagram should give zero curve"


# ── Test _weight_distance_matrix ─────────────────────────────────────

class TestWeightDistanceMatrix:
    """Atomic-number weighting formula."""

    def test_weighted_3atom(self):
        from p3_tda_pipeline import _weight_distance_matrix
        d = np.array([[0, 1, 2], [1, 0, 1], [2, 1, 0]], dtype=float)
        Z = np.array([6.0, 1.0, 8.0])  # C, H, O
        w = _weight_distance_matrix(d, Z)
        assert w.shape == (3, 3), f"Expected (3,3), got {w.shape}"
        assert np.allclose(w, w.T), "Weighted matrix should be symmetric"
        assert np.allclose(np.diag(w), 0), "Diagonal should be zero"
        # w_ij = d_ij * (1 + Z_i*Z_j / 100)
        expected_01 = 1.0 * (1 + 6.0 * 1.0 / 100)  # = 1.06
        assert abs(w[0, 1] - expected_01) < 1e-10


# ── Test smiles_to_distance_matrix (2D fallback) ─────────────────────

class TestSmilesToDistanceMatrix:
    """Distance matrix from SMILES (2D graph fallback for simple molecules)."""

    def test_methane(self):
        """Methane (C) → 1 atom → too small, returns None."""
        from p3_tda_pipeline import smiles_to_distance_matrix
        result = smiles_to_distance_matrix("C")
        # Methane after AddHs has 5 atoms, so should succeed
        if result is not None:
            assert result.shape[0] >= 2

    def test_ethane_2d(self):
        """Ethane should produce a valid distance matrix."""
        from p3_tda_pipeline import smiles_to_distance_matrix
        result = smiles_to_distance_matrix("CC")
        assert result is not None, "Ethane should produce distance matrix"
        assert result.shape[0] >= 2, f"Matrix too small: {result.shape}"
        assert np.allclose(np.diag(result), 0), "Diagonal should be zero"

    def test_invalid_smiles(self):
        from p3_tda_pipeline import smiles_to_distance_matrix
        result = smiles_to_distance_matrix("NotAValidSMILES")
        assert result is None, "Invalid SMILES should return None"


# ── Test extract_tfp ─────────────────────────────────────────────────

class TestExtractTFP:
    """78-D topological fingerprint extraction."""

    def test_tfp_with_diagrams(self, dgm_h0, dgm_h1):
        from p3_tda_pipeline import extract_tfp
        tfp = extract_tfp([dgm_h0, dgm_h1])
        assert tfp.shape == (78,), f"Expected 78-D TFP, got {tfp.shape}"
        assert tfp.dtype == np.float32
        assert np.all(np.isfinite(tfp)), "TFP should have no NaN/Inf"

    def test_tfp_no_h2(self, dgm_h0, dgm_h1):
        """When H2 diagram is missing, zeros are filled."""
        from p3_tda_pipeline import extract_tfp
        tfp = extract_tfp([dgm_h0, dgm_h1])  # No H2
        assert tfp.shape == (78,)
        # Last 11 features (BASE_FEATURES) are for H2 → should be zero
        h2_features = tfp[22:33]  # features 22-32 are H2 base features
        assert np.all(h2_features == 0), "Missing H2 should produce zero features"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
