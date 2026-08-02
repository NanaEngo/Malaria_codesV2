#!/usr/bin/env python3
"""P3 — Tests for QKS Benchmark (p3_qks_benchmark.py).

Tests functions that don't require PennyLane or SLURM submission:
  1. _rbf_matrix() — RBF kernel computation
  2. _tune_rbf_gamma() — gamma grid search logic
  3. rbf_kernel() — full kernel pipeline (default gamma fallback)
  4. reduce_to_qubits() — UMAP/PCA fallback scaling
  5. evaluate_fold() — metric dictionary structure

Usage:
    pytest tests/test_p3_qks_basic.py -v
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
warnings.filterwarnings("ignore")


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def sample_Xy():
    """Small synthetic dataset for kernel tests."""
    rng = np.random.RandomState(42)
    X = rng.randn(20, 8).astype(np.float32)  # 20 samples, 8 features
    y = np.array([1] * 10 + [0] * 10, dtype=int)  # balanced
    return X, y


@pytest.fixture
def sample_X_2d():
    """8-D samples in [-1, 1] (as after UMAP scaling)."""
    rng = np.random.RandomState(42)
    return 2.0 * rng.rand(10, 8).astype(np.float32) - 1.0


# ── Test _rbf_matrix ─────────────────────────────────────────────────

class TestRBFMatrix:
    """RBF kernel K(A, B) = exp(-gamma * ||A - B||^2)."""

    def test_shape(self, sample_X_2d):
        from p3_qks_benchmark import _rbf_matrix
        K = _rbf_matrix(sample_X_2d, sample_X_2d, gamma=0.5)
        assert K.shape == (10, 10), f"Expected (10,10), got {K.shape}"

    def test_identity(self, sample_X_2d):
        """K(x, x) = 1 for any gamma (diagonal = 1)."""
        from p3_qks_benchmark import _rbf_matrix
        for gamma in [0.01, 0.1, 1.0, 10.0]:
            K = _rbf_matrix(sample_X_2d, sample_X_2d, gamma=gamma)
            assert np.allclose(np.diag(K), 1.0), \
                f"Diagonal should be 1 for gamma={gamma}"

    def test_symmetric(self, sample_X_2d):
        from p3_qks_benchmark import _rbf_matrix
        K = _rbf_matrix(sample_X_2d, sample_X_2d, gamma=0.5)
        assert np.allclose(K, K.T), "RBF matrix should be symmetric"

    def test_positive(self, sample_X_2d):
        from p3_qks_benchmark import _rbf_matrix
        K = _rbf_matrix(sample_X_2d, sample_X_2d, gamma=0.5)
        assert np.all(K > 0), "RBF entries should be positive (exp > 0)"

    def test_gamma_effect(self, sample_X_2d):
        """Larger gamma → smaller off-diagonal values (more local kernel)."""
        from p3_qks_benchmark import _rbf_matrix
        K_small = _rbf_matrix(sample_X_2d, sample_X_2d, gamma=0.01)
        K_large = _rbf_matrix(sample_X_2d, sample_X_2d, gamma=5.0)
        off_small = K_small[np.triu_indices(10, k=1)].mean()
        off_large = K_large[np.triu_indices(10, k=1)].mean()
        assert off_large < off_small, \
            "Larger gamma should produce smaller off-diagonal values"


# ── Test _tune_rbf_gamma ─────────────────────────────────────────────

class TestTuneRBFGamma:
    """Grid search for optimal RBF gamma via inner CV."""

    def test_returns_float(self, sample_Xy):
        from p3_qks_benchmark import _tune_rbf_gamma
        X, y = sample_Xy
        gamma = _tune_rbf_gamma(X, y, n_inner_folds=2)
        assert isinstance(gamma, float)
        assert gamma > 0

    def test_custom_grid(self, sample_Xy):
        from p3_qks_benchmark import _tune_rbf_gamma
        X, y = sample_Xy
        gammas = [0.001, 0.01, 0.1, 1.0]
        gamma = _tune_rbf_gamma(X, y, gammas=gammas, n_inner_folds=2)
        assert gamma in gammas, f"Best gamma {gamma} not in grid {gammas}"

    def test_small_dataset(self):
        """Edge case: very small dataset with 2 inner folds."""
        from p3_qks_benchmark import _tune_rbf_gamma
        rng = np.random.RandomState(42)
        X = rng.randn(8, 4).astype(np.float32)
        y = np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=int)
        gamma = _tune_rbf_gamma(X, y, n_inner_folds=2)
        assert gamma > 0, "Should return a positive gamma"


# ── Test rbf_kernel ──────────────────────────────────────────────────

class TestRBFKernel:
    """Full RBF kernel pipeline with automatic gamma tuning."""

    def test_kernel_shapes(self, sample_Xy):
        from p3_qks_benchmark import rbf_kernel
        X, y = sample_Xy
        X_tr, X_te = X[:15], X[15:]
        y_tr = y[:15]
        K_tr, K_te, gamma = rbf_kernel(X_tr, X_te, y_train=y_tr)
        assert K_tr.shape == (15, 15), f"Train kernel: {K_tr.shape}"
        assert K_te.shape == (5, 15), f"Test kernel: {K_te.shape}"
        assert gamma > 0

    def test_default_gamma(self, sample_Xy):
        """When y_train is None and gamma is None, falls back to 0.01."""
        from p3_qks_benchmark import rbf_kernel
        X, _ = sample_Xy
        X_tr, X_te = X[:15], X[15:]
        K_tr, K_te, gamma = rbf_kernel(X_tr, X_te, gamma=None, y_train=None)
        assert gamma == 0.01, f"Expected default gamma 0.01, got {gamma}"
        assert K_tr.shape == (15, 15)

    def test_explicit_gamma(self, sample_Xy):
        """User-specified gamma bypasses tuning."""
        from p3_qks_benchmark import rbf_kernel
        X, y = sample_Xy
        X_tr, X_te = X[:15], X[15:]
        K_tr, K_te, gamma = rbf_kernel(X_tr, X_te, gamma=0.5, y_train=None)
        assert gamma == 0.5, f"Expected gamma 0.5, got {gamma}"


# ── Test reduce_to_qubits ────────────────────────────────────────────

class TestReduceToQubits:
    """UMAP/PCA fallback + [-1, 1] scaling."""

    def test_shape(self):
        from p3_qks_benchmark import reduce_to_qubits
        rng = np.random.RandomState(42)
        X_tr = rng.randn(30, 2048).astype(np.float32)
        X_te = rng.randn(10, 2048).astype(np.float32)
        tr_q, te_q = reduce_to_qubits(X_tr, X_te, n_components=8)
        assert tr_q.shape == (30, 8), f"Train reduced: {tr_q.shape}"
        assert te_q.shape == (10, 8), f"Test reduced: {te_q.shape}"

    def test_scaled_range(self):
        """Features should be in [-1, 1]."""
        from p3_qks_benchmark import reduce_to_qubits
        rng = np.random.RandomState(42)
        X_tr = rng.randn(50, 2048).astype(np.float32)
        X_te = rng.randn(10, 2048).astype(np.float32)
        tr_q, te_q = reduce_to_qubits(X_tr, X_te, n_components=8)
        assert tr_q.min() >= -1.0 - 1e-6, f"Min: {tr_q.min()}"
        assert tr_q.max() <= 1.0 + 1e-6, f"Max: {tr_q.max()}"
        assert te_q.min() >= -1.0 - 1e-6, f"Test min: {te_q.min()}"
        assert te_q.max() <= 1.0 + 1e-6, f"Test max: {te_q.max()}"

    def test_small_dataset(self):
        """Edge case: fewer samples than features."""
        from p3_qks_benchmark import reduce_to_qubits
        rng = np.random.RandomState(42)
        X_tr = rng.randn(20, 2048).astype(np.float32)  # 20 samples (n_neighbors=15 min)
        X_te = rng.randn(5, 2048).astype(np.float32)
        tr_q, te_q = reduce_to_qubits(X_tr, X_te, n_components=4)
        assert tr_q.shape == (20, 4), f"Train: {tr_q.shape}"
        assert te_q.shape == (5, 4), f"Test: {te_q.shape}"


# ── Test evaluate_fold ───────────────────────────────────────────────

class TestEvaluateFold:
    """Metric dictionary from SVM evaluation."""

    def test_record_keys(self):
        """Verify all expected metric keys are present."""
        from p3_qks_benchmark import evaluate_fold
        rng = np.random.RandomState(42)
        n = 10
        K_tr = _rbf_matrix_synthetic(rng.randn(n, 4))
        K_te = _rbf_matrix_synthetic(rng.randn(4, 4), rng.randn(n, 4))
        y_tr = np.array([1] * 5 + [0] * 5, dtype=int)
        y_te = np.array([1, 1, 0, 0], dtype=int)
        rec = evaluate_fold(K_tr, K_te, y_tr, y_te, "test_model", ta_val=0.5)
        for key in ["model", "auc", "accuracy", "f1"]:
            assert key in rec, f"Missing key: {key}"
        assert "target_alignment" in rec, "Missing target_alignment"
        assert rec["model"] == "test_model"

    def test_single_class_edge(self):
        """Edge case: y_test has only one class (AUC = nan)."""
        from p3_qks_benchmark import evaluate_fold
        n = 8
        K_tr = _rbf_matrix_synthetic(np.random.RandomState(0).randn(n, 4))
        K_te = _rbf_matrix_synthetic(np.random.RandomState(1).randn(4, 4),
                                      np.random.RandomState(1).randn(n, 4))
        y_tr = np.array([1] * 4 + [0] * 4, dtype=int)
        y_te = np.array([1, 1, 1, 1], dtype=int)  # all active
        rec = evaluate_fold(K_tr, K_te, y_tr, y_te, "test")
        assert np.isnan(rec["auc"]), "AUC should be nan for single-class test"


# ── Helpers ──────────────────────────────────────────────────────────

def _rbf_matrix_synthetic(A, B=None, gamma=1.0):
    """Simple RBF matrix for test setup (no import needed)."""
    if B is None:
        B = A
    sq = np.sum((A[:, None] - B[None]) ** 2, axis=-1)
    return np.exp(-gamma * sq)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
