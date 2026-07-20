#!/usr/bin/env python3
"""P4 — Scoring oracles for MCTS molecular optimization.

This module provides a unified interface to combine multiple pharmacological
scores (MPO, docking, SYBA, synthetic accessibility) into a single scalar
reward. All oracles are placeholders/skeletons for future integration with P1
and P2 pipelines.
"""

from __future__ import annotations

from typing import Callable, Dict


class OracleAggregator:
    """Aggregate multiple oracle scores into a scalar reward.

    Parameters
    ----------
    weights : dict[str, float]
        Weight for each oracle component. Keys: mpo, docking, syba, sa.
    """

    def __init__(self, weights: Dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "mpo": 0.4,
            "docking": 0.3,
            "syba": 0.2,
            "sa": 0.1,
        }

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
        # Use a local variable to avoid mutating the dict returned by score().
        docking = -scores["docking"]
        return (
            self.weights["mpo"] * scores["mpo"]
            + self.weights["docking"] * docking
            + self.weights["syba"] * scores["syba"]
            + self.weights["sa"] * scores["sa"]
        )

    def _mpo_score(self, smiles: str) -> float:
        """Placeholder for Multi-Parameter Optimization score."""
        # TODO: integrate with P1 MPO pipeline
        return 0.5

    def _docking_score(self, smiles: str) -> float:
        """Placeholder for Tartarus/Vina docking score.

        Note
        ----
        Docking scores are typically negative (kcal/mol), with more negative
        values indicating stronger binding. The aggregator treats this as a
        reward component, so the sign is preserved here.
        """
        # TODO: integrate with P1/P2 docking pipeline
        return -7.0

    def _syba_score(self, smiles: str) -> float:
        """Placeholder for SYBA synthetic accessibility score."""
        # TODO: integrate with P1 SYBA scorer
        return 0.0

    def _sa_score(self, smiles: str) -> float:
        """Placeholder for synthetic accessibility penalty (lower is better)."""
        # TODO: integrate with RDKit SAscore
        return 3.0


def make_oracle(weights: Dict[str, float] | None = None) -> Callable[[str], float]:
    """Factory returning a callable reward function."""
    aggregator = OracleAggregator(weights)
    return aggregator.reward


if __name__ == "__main__":
    oracle = OracleAggregator()
    scores = oracle.score("CCO")
    print("Scores:", scores)
    print("Reward:", oracle.reward("CCO"))
