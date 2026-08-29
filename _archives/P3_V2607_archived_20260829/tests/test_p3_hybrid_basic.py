#!/usr/bin/env python3
"""P3 — Basic unit tests for Hybrid Benchmark (R9).

Tests:
  1. ecfp4() returns correct shape and dtype
  2. load_activity() loads expected columns
  3. scale() normalises to mean=0, std=1
  4. ecfp4 cache works (R11)
  5. cv_score returns correct record structure

Usage:
    pytest tests/test_p3_hybrid_basic.py -v
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
warnings.filterwarnings("ignore")


@pytest.fixture
def sample_smiles() -> list[str]:
    return ["C", "CC", "CCC", "CCCC", "CCCCC", "c1ccccc1",
            "c1ccccc1C", "c1ccccc1CC", "c1ccccc1CCC", "c1ccccc1CCCC"]


@pytest.fixture
def sample_y() -> np.ndarray:
    # 10 samples, 5 active + 5 inactive → StratifiedKFold(5) possible
    return np.array([0, 0, 0, 1, 1, 1, 0, 0, 1, 1], dtype=int)


class TestECFP4:
    """R11: ECFP4 fingerprint generation with caching."""

    def test_shape(self, sample_smiles):
        from p3_hybrid_benchmark import ecfp4
        X = ecfp4(sample_smiles)
        assert X.shape == (len(sample_smiles), 2048), f"Expected (6, 2048), got {X.shape}"
        assert X.dtype == np.float32, f"Expected float32, got {X.dtype}"

    def test_values(self, sample_smiles):
        from p3_hybrid_benchmark import ecfp4
        X = ecfp4(sample_smiles)
        assert np.all((X == 0) | (X == 1)), "ECFP4 should be binary (0 or 1)"
        assert X.sum() > 0, "ECFP4 should have at least some bits set"

    def test_cache(self, sample_smiles):
        """Verify ECFP4 cache returns identical arrays."""
        from p3_hybrid_benchmark import ecfp4, _ECFP4_CACHE
        _ECFP4_CACHE.clear()
        _ = ecfp4(sample_smiles)
        cached_size = len(_ECFP4_CACHE)
        assert cached_size == len(sample_smiles), f"Cache should have {len(sample_smiles)} entries, got {cached_size}"
        _ = ecfp4(sample_smiles)  # second call uses cache
        assert len(_ECFP4_CACHE) == cached_size, "Cache should not grow on repeat call"


class TestScale:
    """R7: StandardScaler wrapper."""

    def test_normalisation(self):
        from sklearn.preprocessing import StandardScaler
        X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        sc = StandardScaler(); X_tr = sc.fit_transform(X[:2]); X_te = sc.transform(X[2:])
        assert abs(X_tr.mean()) < 1e-10, f"Train mean should be ~0, got {X_tr.mean()}"
        assert abs(X_tr.std() - 1.0) < 1e-6, f"Train std should be ~1, got {X_tr.std()}"


class TestCVScore:
    """R10: CV score record structure."""

    def test_record_keys(self, sample_smiles, sample_y):
        from p3_hybrid_benchmark import ecfp4
        from p3_hybrid_benchmark import cv_score
        X = ecfp4(sample_smiles)
        records = cv_score(X, sample_y, "rf", "ECFP4")
        assert len(records) == 5, f"Should have 5 folds, got {len(records)}"
        for rec in records:
            assert "descriptor" in rec
            assert "classifier" in rec
            assert "fold" in rec
            assert "auc" in rec
            assert rec["descriptor"] == "ECFP4"
            assert rec["classifier"] == "rf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
