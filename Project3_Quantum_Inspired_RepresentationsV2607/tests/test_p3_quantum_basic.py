#!/usr/bin/env python3
"""P3 — Tests for Quantum Parameter Search (p3_quantum_param_search.py).

Tests functions that don't require PennyLane or SLURM:
  1. ecfp4() — fingerprint shape and values
  2. _ECFP4_CACHE — cache hit detection
  3. load_activity() — data loading structure
  4. load_precomputed() — CSV loading logic
  5. _get_kernel_fn() — cache key mechanism (device detection only)

Usage:
    pytest tests/test_p3_quantum_basic.py -v
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
warnings.filterwarnings("ignore")


# ── Sample SMILES ────────────────────────────────────────────────────

SIMPLE_SMILES = ["C", "CC", "CCC", "c1ccccc1", "CC(=O)O", "CCO"]
COMBINED_SMILES = ["C", "CC", "CCC", "c1ccccc1", "CC(=O)O", "CCO"]


# ── Test ecfp4 ───────────────────────────────────────────────────────

class TestECFP4:
    """Morgan fingerprint (radius=2, 2048 bits) computation."""

    def test_shape(self):
        from p3_quantum_param_search import ecfp4
        fps = ecfp4(SIMPLE_SMILES)
        assert fps.shape == (len(SIMPLE_SMILES), 2048), \
            f"Expected ({len(SIMPLE_SMILES)}, 2048), got {fps.shape}"

    def test_binary_values(self):
        """ECFP4 bits should be 0 or 1 (binary fingerprint)."""
        from p3_quantum_param_search import ecfp4
        fps = ecfp4(SIMPLE_SMILES)
        assert set(np.unique(fps)).issubset({0, 1}), \
            f"Unexpected values: {np.unique(fps)}"

    def test_different_molecules(self):
        """Different SMILES should produce non-identical fingerprints."""
        from p3_quantum_param_search import ecfp4
        fps = ecfp4(["C", "c1ccccc1"])
        assert not np.array_equal(fps[0], fps[1]), \
            "Methane and benzene should have different fingerprints"

    def test_same_molecule(self):
        """Same SMILES should produce identical fingerprints."""
        from p3_quantum_param_search import ecfp4
        fps = ecfp4(["CCO", "CCO"])
        assert np.array_equal(fps[0], fps[1]), \
            "Same SMILES should give identical fingerprints"

    def test_invalid_smiles(self):
        """Invalid SMILES → zero vector (not crash)."""
        from p3_quantum_param_search import ecfp4
        fps = ecfp4(["NotAValidSMILES"])
        assert fps.shape == (1, 2048)
        assert np.all(fps == 0), "Invalid SMILES should give zero fingerprint"


# ── Test ECFP4 Cache ─────────────────────────────────────────────────

class TestECFP4Cache:
    """Module-level _ECFP4_CACHE dict (R11)."""

    def test_cache_hit_after_first_call(self):
        """Second call with same SMILES reuses cached result."""
        from p3_quantum_param_search import ecfp4, _ECFP4_CACHE
        _ECFP4_CACHE.clear()
        # First call: compute and cache
        fps1 = ecfp4(["CCO"])
        n_cached = len(_ECFP4_CACHE)
        # Second call: should use cache
        fps2 = ecfp4(["CCO"])
        assert len(_ECFP4_CACHE) == n_cached, \
            "Cache should not grow for repeated SMILES"
        assert np.array_equal(fps1, fps2), \
            "Cached result should match computed result"

    def test_cache_cleared(self):
        """Cache is cleared, fresh computation matches direct compute."""
        from p3_quantum_param_search import ecfp4, _ECFP4_CACHE
        from rdkit import Chem
        from rdkit.Chem import rdFingerprintGenerator
        morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        from rdkit.DataStructs import ConvertToNumpyArray

        _ECFP4_CACHE.clear()
        # Compute via ecfp4 (will cache)
        fps = ecfp4(["c1ccccc1"])
        # Direct computation
        mol = Chem.MolFromSmiles("c1ccccc1")
        arr = np.zeros(2048, dtype=np.float32)
        ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        assert np.array_equal(fps[0], arr), \
            "Cached fingerprint should match direct RDKit computation"

    def test_multiple_smiles(self):
        from p3_quantum_param_search import ecfp4, _ECFP4_CACHE
        _ECFP4_CACHE.clear()
        fps = ecfp4(["C", "CC", "CCC", "CCO", "c1ccccc1"])
        assert len(_ECFP4_CACHE) == 5, \
            f"Expected 5 cached entries, got {len(_ECFP4_CACHE)}"
        assert fps.shape == (5, 2048)


# ── Test load_activity ───────────────────────────────────────────────

class TestLoadActivity:
    """Data loading from eos80ch_malaria_final_activity.csv."""

    def test_dataframe_structure(self):
        from p3_quantum_param_search import load_activity, RESULTS_DIR
        csv_path = RESULTS_DIR / "eos80ch_malaria_final_activity.csv"
        if not csv_path.exists():
            pytest.skip(f"Activity CSV not found: {csv_path}")
        df = load_activity()
        assert "smiles" in df.columns, "Missing 'smiles' column"
        assert "activity" in df.columns, "Missing 'activity' column"
        assert len(df) > 0, "Empty dataframe"
        assert df["activity"].between(0, 1).all(), \
            "Activities should be in [0, 1]"

    def test_no_nan_smiles(self):
        from p3_quantum_param_search import load_activity, RESULTS_DIR
        csv_path = RESULTS_DIR / "eos80ch_malaria_final_activity.csv"
        if not csv_path.exists():
            pytest.skip(f"Activity CSV not found: {csv_path}")
        df = load_activity()
        assert df["smiles"].isna().sum() == 0, \
            "SMILES column should have no NaN"


# ── Test load_precomputed ────────────────────────────────────────────

class TestLoadPrecomputed:
    """Load precomputed embeddings from CSV."""

    def test_nonexistent_file(self, tmp_path):
        from p3_quantum_param_search import load_precomputed
        result = load_precomputed(["C", "CC"],
                                  tmp_path / "nonexistent.csv", "H")
        assert result is None, "Non-existent file should return None"

    def test_feature_columns(self, tmp_path):
        """CSV with 'H_1', 'H_2' features loads correctly."""
        from p3_quantum_param_search import load_precomputed
        import pandas as pd
        # Create test CSV
        df = pd.DataFrame({
            "smiles": ["C", "CC"],
            "H_1": [0.1, 0.2],
            "H_2": [0.3, 0.4],
        })
        csv_path = tmp_path / "test_features.csv"
        df.to_csv(csv_path, index=False)

        result = load_precomputed(["C", "CC"], csv_path, "H")
        assert result is not None
        assert result.shape == (2, 2), f"Expected (2,2), got {result.shape}"

    def test_missing_smiles_in_csv(self, tmp_path):
        """When requested SMILES not in CSV → NaN filled with column mean."""
        from p3_quantum_param_search import load_precomputed
        import pandas as pd
        df = pd.DataFrame({
            "smiles": ["CC"],
            "H_1": [0.5],
        })
        csv_path = tmp_path / "test_missing.csv"
        df.to_csv(csv_path, index=False)

        result = load_precomputed(["C", "CC"], csv_path, "H")
        assert result is not None
        assert result.shape == (2, 1)
        # "C" is missing → filled with column mean (0.5)
        assert abs(result[0, 0] - 0.5) < 1e-6, \
            f"Missing SMILES should get column mean, got {result[0, 0]}"


# ── Test best_device ─────────────────────────────────────────────────

class TestBestDevice:
    """Device selection logic (no actual PennyLane calls)."""

    def test_returns_string(self):
        from p3_quantum_param_search import best_device
        device = best_device(n_qubits=4, prefer_cpu=True)
        assert isinstance(device, str)
        assert len(device) > 0

    def test_nonzero_qubits(self):
        from p3_quantum_param_search import best_device
        device = best_device(n_qubits=2, prefer_cpu=True)
        assert isinstance(device, str)
        assert len(device) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
