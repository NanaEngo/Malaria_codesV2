#!/usr/bin/env python3
"""P4 — Scoring oracles for MCTS molecular optimization.

This module provides a unified interface to combine multiple pharmacological
scores (MPO, docking, SYBA, synthetic accessibility) into a single scalar
reward. It reuses pre-computed Project 1 / Project 2 score libraries whenever
possible and falls back to fast on-the-fly calculations for novel molecules.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from rdkit.DataStructs import TanimotoSimilarity


# ── Optional third-party scorers ─────────────────────────────────────
try:
    from syba.syba import SybaClassifier

    _HAS_SYBA = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_SYBA = False

try:
    import sascorer

    _HAS_SASCORER = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_SASCORER = False


# ── Paths to P1/P2 score libraries ───────────────────────────────────
def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


C6_CSV = (
    _repo_root()
    / "Project2_Polypharmacology_MD_ValidationV2607"
    / "data"
    / "from_project1"
    / "results"
    / "c6_primary_leads_synthesisable.csv"
)

TARTARUS_CSV = (
    _repo_root()
    / "Project2_Polypharmacology_MD_ValidationV2607"
    / "results"
    / "tartarus_output.csv"
)


class OracleAggregator:
    """Aggregate multiple oracle scores into a scalar reward.

    Parameters
    ----------
    weights : dict[str, float]
        Weight for each oracle component. Keys: mpo, docking, syba, sa.
    use_precomputed : bool
        If True, load P1/P2 score libraries and use them for lookups.
    docking_fallback : str
        How to score novel molecules when no precomputed docking value exists.
        Options: "similarity" (Tanimoto nearest-neighbour proxy), "default".
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        use_precomputed: bool = True,
        docking_fallback: str = "similarity",
    ) -> None:
        self.weights = weights or {
            "mpo": 0.4,
            "docking": 0.3,
            "syba": 0.2,
            "sa": 0.1,
        }
        self.docking_fallback = docking_fallback
        self._runtime_cache: Dict[str, Dict[str, float]] = {}
        self._canonical_cache: Dict[str, str] = {}

        # Precomputed P1/P2 libraries
        self._c6: Dict[str, Dict[str, float]] = {}
        self._tartarus: Dict[str, Dict[str, float]] = {}
        self._tartarus_smiles: list[str] = []
        self._tartarus_fingerprints: list = []

        if use_precomputed:
            self._load_precomputed_libraries()

        # Optional on-the-fly scorers
        self._syba: Optional[object] = None
        if _HAS_SYBA:
            try:
                self._syba = SybaClassifier()
                self._syba.fitDefaultScore()
            except Exception as exc:  # pragma: no cover
                warnings.warn(f"SYBA initialisation failed: {exc}")
                self._syba = None

    # ── Public API ───────────────────────────────────────────────────
    def score(self, smiles: str) -> Dict[str, float]:
        """Return a dictionary of individual oracle scores."""
        return {
            "mpo": self._mpo_score(smiles),
            "docking": self._docking_score(smiles),
            "syba": self._syba_score(smiles),
            "sa": self._sa_score(smiles),
        }

    def reward(self, smiles: str) -> float:
        """Compute weighted scalar reward.

        Docking scores are negative (kcal/mol); we negate them so that more
        negative (better) binding increases the reward.
        """
        scores = self.score(smiles)
        # Negate docking so that more negative (stronger binding) is better.
        # Invert SAscore (lower is better) onto a [0,1]-like reward scale.
        docking = -scores["docking"]
        sa_reward = max(0.0, 10.0 - scores["sa"]) / 9.0
        return (
            self.weights["mpo"] * scores["mpo"]
            + self.weights["docking"] * docking
            + self.weights["syba"] * scores["syba"]
            + self.weights["sa"] * sa_reward
        )

    # ── Library loading ────────────────────────────────────────────────
    def _load_precomputed_libraries(self) -> None:
        """Load P1/P2 score CSVs into memory as lookup tables."""
        if C6_CSV.exists():
            try:
                df = pd.read_csv(C6_CSV)
                if "input" in df.columns:
                    df = df.rename(columns={"input": "smiles"})
                df = df.drop_duplicates(subset=["smiles"])
                self._c6 = (
                    df.set_index("smiles")
                    .replace([np.inf, -np.inf], np.nan)
                    .to_dict(orient="index")
                )
            except Exception as exc:  # pragma: no cover
                warnings.warn(f"Failed to load C6 library: {exc}")
                self._c6 = {}

        if TARTARUS_CSV.exists():
            try:
                df = pd.read_csv(TARTARUS_CSV)
                if "smile" in df.columns:
                    df = df.rename(columns={"smile": "smiles"})
                # Average the three target scores for a single docking value
                target_cols = [c for c in df.columns if c.startswith("score_")]
                if target_cols:
                    df["docking"] = df[target_cols].mean(axis=1)
                else:
                    df["docking"] = 0.0
                df = df.drop_duplicates(subset=["smiles"])
                self._tartarus = (
                    df.set_index("smiles")
                    .replace([np.inf, -np.inf], np.nan)
                    .to_dict(orient="index")
                )
                self._tartarus_smiles = list(self._tartarus.keys())
                self._tartarus_fingerprints = self._compute_fingerprints(
                    self._tartarus_smiles
                )
            except Exception as exc:  # pragma: no cover
                warnings.warn(f"Failed to load Tartarus library: {exc}")
                self._tartarus = {}
                self._tartarus_smiles = []
                self._tartarus_fps = None

    # ── Scoring helpers ────────────────────────────────────────────────
    def _canonical_smiles(self, smiles: str) -> str:
        """Return canonical SMILES; fall back to input on failure."""
        if smiles in self._canonical_cache:
            return self._canonical_cache[smiles]
        try:
            mol = Chem.MolFromSmiles(smiles)
            canon = Chem.MolToSmiles(mol) if mol is not None else smiles
        except Exception:
            canon = smiles
        self._canonical_cache[smiles] = canon
        return canon

    def _cache_get(self, smiles: str, key: str) -> Optional[float]:
        canon = self._canonical_smiles(smiles)
        return self._runtime_cache.get(canon, {}).get(key)

    def _cache_set(self, smiles: str, key: str, value: float) -> None:
        canon = self._canonical_smiles(smiles)
        self._runtime_cache.setdefault(canon, {})[key] = value

    def _compute_fingerprints(self, smiles_list: list[str]) -> list:
        """Compute Morgan bit-vector fingerprints for a list of SMILES."""
        if not smiles_list:
            return []
        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        fps = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                fps.append(None)
            else:
                fps.append(gen.GetFingerprint(mol))
        return fps

    def _tanimoto_nearest_docking(self, smiles: str) -> float:
        """Return the docking score of the nearest neighbour by Tanimoto similarity."""
        if not self._tartarus_fingerprints or not self._tartarus_smiles:
            return -7.0

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return -7.0

        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        query_fp = gen.GetFingerprint(mol)

        # Compute true Tanimoto similarity against precomputed bit fingerprints
        best_sim = -1.0
        best_idx = 0
        for idx, lib_fp in enumerate(self._tartarus_fingerprints):
            if lib_fp is None:
                continue
            sim = TanimotoSimilarity(query_fp, lib_fp)
            if sim > best_sim:
                best_sim = sim
                best_idx = idx

        best_smi = self._tartarus_smiles[best_idx]
        return float(self._tartarus[best_smi].get("docking", -7.0))

    # ── Individual oracles ───────────────────────────────────────────
    def _mpo_score(self, smiles: str) -> float:
        """MPO score: use precomputed P1 value or fall back to a QED proxy."""
        cached = self._cache_get(smiles, "mpo")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._c6:
            score = float(self._c6[canon].get("weighted_mpo_score", 0.5))
        else:
            # Fallback: QED is a good proxy for the drug-likeness part of MPO
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                score = 0.0
            else:
                score = Descriptors.qed(mol)

        self._cache_set(smiles, "mpo", score)
        return score

    def _docking_score(self, smiles: str) -> float:
        """Docking score (kcal/mol): use precomputed Tartarus or nearest-neighbour proxy."""
        cached = self._cache_get(smiles, "docking")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._tartarus:
            score = float(self._tartarus[canon].get("docking", -7.0))
        elif self.docking_fallback == "similarity":
            score = self._tanimoto_nearest_docking(canon)
        else:
            score = -7.0

        self._cache_set(smiles, "docking", score)
        return score

    def _syba_score(self, smiles: str) -> float:
        """SYBA synthetic accessibility score: precomputed or on-the-fly."""
        cached = self._cache_get(smiles, "syba")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._c6:
            score = float(self._c6[canon].get("syba_score", 0.0))
        elif self._syba is not None:
            try:
                score = float(self._syba.predict(canon))
            except Exception:
                score = 0.0
        else:
            score = 0.0

        self._cache_set(smiles, "syba", score)
        return score

    def _sa_score(self, smiles: str) -> float:
        """Synthetic accessibility penalty (lower is better): precomputed or RDKit SAscore."""
        cached = self._cache_get(smiles, "sa")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._c6:
            score = float(self._c6[canon].get("sa_score", 3.0))
        elif _HAS_SASCORER:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                score = 3.0
            else:
                try:
                    score = float(sascorer.calculateScore(mol))
                except Exception:
                    score = 3.0
        else:
            score = 3.0

        self._cache_set(smiles, "sa", score)
        return score


def make_oracle(
    weights: Optional[Dict[str, float]] = None,
    use_precomputed: bool = True,
    docking_fallback: str = "similarity",
) -> Callable[[str], float]:
    """Factory returning a callable reward function."""
    aggregator = OracleAggregator(
        weights,
        use_precomputed=use_precomputed,
        docking_fallback=docking_fallback,
    )
    return aggregator.reward


if __name__ == "__main__":
    oracle = OracleAggregator()
    scores = oracle.score("CCO")
    print("Scores:", scores)
    print("Reward:", oracle.reward("CCO"))
