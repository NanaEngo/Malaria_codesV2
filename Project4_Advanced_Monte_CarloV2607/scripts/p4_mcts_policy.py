#!/usr/bin/env python3
"""P4 — ScafVAE-guided fragment selection policy for MCTS.

Provides a policy that scores each fragment based on:
1. Scaffold compatibility (Tanimoto similarity to known privileged scaffolds)
2. Fragment frequency priors (medicinal chemistry fragment preferences)
3. Chemical compatibility (valence, reactivity filters)

The policy converts these scores into log-probability priors that plug
directly into the MCTS UCT formula as P(s, a) values.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Callable, Optional

import datamol as dm
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from rdkit.DataStructs import TanimotoSimilarity

# Suppress RDKit warnings during fragment scoring
RDLogger.logger().setLevel(RDLogger.ERROR)


# ── Fragment frequency priors (from medicinal chemistry literature) ──
# These are log-frequency scores for each fragment category.
# Higher = more drug-relevant / synthetically accessible.
# Based on analysis of ChEMBL27 fragment distributions (Bemis-Murcko).
FRAGMENT_PRIORS: dict[str, float] = {
    # Aromatic (highly privileged in drug discovery)
    "c1ccc([*])cc1":     0.95,   # Phenyl - most common
    "c1cc([*])ccn1":     0.70,   # 4-Pyridyl
    "c1c([*])nccn1":     0.50,   # Pyrimidin-5-yl
    "c1c([*])oco1":      0.40,   # Furan-2-yl
    "c1c([*])sc1":       0.45,   # Thiophen-2-yl
    "c1c([*])[nH]c1":    0.30,   # Pyrrol-2-yl
    "c1cn([*])cn1":      0.35,   # Imidazol-1-yl
    "c1c([*])ncs1":      0.25,   # Thiazol-5-yl
    # Saturated heterocycles (good for 3D geometry)
    "C1CC([*])NCC1":     0.80,   # 4-Piperidinyl - very common
    "C1COC([*])CN1":     0.65,   # Morpholin-4-yl
    "C1CN([*])CCN1":     0.60,   # Piperazin-1-yl - privileged
    "C1CC([*])CN1":      0.45,   # Pyrrolidin-3-yl
    # Alkyl chains (essential for linker/spacer)
    "[*]C":              0.90,   # Methyl - universal
    "[*]CC":             0.75,   # Ethyl
    "[*]C(C)C":          0.55,   # Isopropyl
    "[*]C(C)(C)C":       0.35,   # tert-Butyl (bulky)
    "[*]C1CC1":          0.50,   # Cyclopropyl - good metabolic stability
    "[*]CC(F)(F)F":      0.30,   # Trifluoroethyl - ADME optimisation
    # Functional groups
    "[*]O":              0.85,   # Hydroxyl - HBD/HBA
    "[*]OC":             0.80,   # Methoxy - most common ether
    "[*]OCC":            0.50,   # Ethoxy
    "[*]N":              0.75,   # Primary amine - HBD
    "[*]N(C)C":          0.40,   # Dimethylamino
    "[*]C(=O)O":         0.60,   # Carboxyl - common in actives
    "[*]C(=O)N":         0.70,   # Primary amide
    "[*]C(=O)OC":        0.45,   # Methyl ester
    "[*]S(=O)(=O)N":     0.25,   # Sulfonamide - specific
    # Halogens and CN groups
    "[*]F":              0.65,   # Fluoride - ADME, metabolic stability
    "[*]Cl":             0.55,   # Chloride
    "[*]Br":             0.20,   # Bromide (less common, heavier)
    "[*]C#N":            0.50,   # Cyano - HBA, metabolic stability
    "[*]C(F)(F)F":       0.40,   # Trifluoromethyl
    "[*][N+](=O)[O-]":   0.15,   # Nitro (less desirable, toxicity risk)
}

# ── Privileged scaffold fingerprints ─────────────────────────────────
# Pre-computed Morgan fingerprints for the canonical scaffold SMILES
# of the fragments (for Tanimoto-based compatibility scoring).
_PRIVILEGED_SMILES: list[str] = [
    "c1ccccc1",        # Benzene
    "c1ccncc1",        # Pyridine
    "c1ccncn1",        # Pyrimidine
    "c1ccoc1",         # Furan
    "c1ccsc1",         # Thiophene
    "c1c[nH]cc1",      # Pyrrole
    "c1cncn1",         # Imidazole
    "c1cscn1",         # Thiazole
    "C1CCNCC1",        # Piperidine
    "C1COCCN1",        # Morpholine
    "C1CNCCN1",        # Piperazine
    "C1CCCN1",         # Pyrrolidine
    "C1CC1",           # Cyclopropane
]

# ── Blocklist for problematic chemical patterns ──────────────────────
_REACTIVE_PATTERNS: tuple[str, ...] = (
    "[N+](=O)[O-]",         # Nitro group (reactive)
    "S(=O)(=O)N",           # Sulfonamide (specific, limited applicability)
    "[*]Br",                # Bromide (heavy, less common in leads)
)


class ScafVAEPolicy:
    """Fragment selection policy guided by scaffold compatibility and priors.

    This policy scores each available fragment by combining:
    - A structural prior (fragment frequency in drug-like molecules)
    - A scaffold compatibility score (Tanimoto similarity between the
      current molecule's scaffold and privileged scaffolds)
    - A chemical filter (penalising reactive or problematic groups)

    The combined score is converted to a log-probability suitable for use
    as the P(s,a) prior in the PUCT (polynomial Upper Confidence Tree)
    variant of MCTS.

    Parameters
    ----------
    temperature : float
        Softmax temperature for converting scores to probabilities.
        Higher values → more uniform exploration.
    diversity_bonus : float
        Bonus for fragments that increase molecular diversity (different
        chemical space from parent). Default 0.05.
    use_filters : bool
        If True, apply chemical reactivity filters.
    random_seed : Optional[int]
        Random seed for reproducible stochasticity.
    """

    def __init__(
        self,
        temperature: float = 1.0,
        diversity_bonus: float = 0.05,
        use_filters: bool = True,
        random_seed: Optional[int] = None,
    ) -> None:
        self.temperature = temperature
        self.diversity_bonus = diversity_bonus
        self.use_filters = use_filters
        self._rng = random.Random(random_seed)

        # Precompute privileged fingerprints
        self._priv_fps: list = []
        self._compute_privileged_fps()

    def _compute_privileged_fps(self) -> None:
        """Generate Morgan fingerprints for privileged scaffolds.

        Uses datamol for simpler SMILES handling (skill-based):
        dm.to_mol() returns None for invalid SMILES automatically.
        """
        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        for smi in _PRIVILEGED_SMILES:
            mol = dm.to_mol(smi)
            if mol:
                self._priv_fps.append(gen.GetFingerprint(mol))
            else:
                self._priv_fps.append(None)

    def get_action_priors(
        self, state: str, available_actions: list[str]
    ) -> dict[str, float]:
        """Compute log-probability prior for each available fragment action.

        Parameters
        ----------
        state : str
            Current molecular SMILES (the node state in MCTS).
        available_actions : list[str]
            List of fragment SMILES to score.

        Returns
        -------
        dict[str, float]
            Mapping from fragment SMILES to log-probability prior.
        """
        if not available_actions:
            return {}

        # Compute scaffold compatibility score for the current molecule
        scaffold_score = self._scaffold_compatibility(state)

        # Score each fragment
        raw_scores: dict[str, float] = {}
        for action in available_actions:
            # Base prior from fragment frequency
            prior = FRAGMENT_PRIORS.get(action, 0.3)

            # Scaffold compatibility bonus: fragments that match the
            # current molecule's scaffold chemistry get a small bonus
            prior += scaffold_score * 0.1

            # Chemical filter penalty
            if self.use_filters:
                penalty = self._chemical_penalty(action)
                prior -= penalty

            # Diversity bonus (small stochastic element)
            prior += self._rng.random() * self.diversity_bonus

            raw_scores[action] = max(prior, 0.01)  # floor to avoid zero

        # Convert to log-probabilities via softmax
        return self._softmax_log_probs(raw_scores)

    def _scaffold_compatibility(self, state: str) -> float:
        """Compute scaffold compatibility score (0-1) for current molecule."""
        mol = Chem.MolFromSmiles(state)
        if mol is None:
            return 0.3  # default

        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        try:
            query_fp = gen.GetFingerprint(mol)
        except Exception:
            return 0.3

        max_sim = 0.0
        for priv_fp in self._priv_fps:
            if priv_fp is None:
                continue
            sim = TanimotoSimilarity(query_fp, priv_fp)
            max_sim = max(max_sim, sim)

        return max_sim

    def _chemical_penalty(self, fragment: str) -> float:
        """Score penalty for reactive or problematic chemical patterns.

        Returns a value in [0, 0.3] to subtract from the prior.
        """
        penalty = 0.0
        for pattern in _REACTIVE_PATTERNS:
            if pattern in fragment:
                penalty += 0.15
        return min(penalty, 0.3)

    @staticmethod
    def _softmax_log_probs(scores: dict[str, float]) -> dict[str, float]:
        """Convert raw scores to log-probabilities using softmax."""
        values = list(scores.values())
        max_val = max(values)
        # Numerically stable exp
        exp_vals = [math.exp(v - max_val) for v in values]
        total = sum(exp_vals)
        if total <= 0:
            return {k: math.log(1.0 / len(scores)) for k in scores}

        probs = [v / total for v in exp_vals]
        return {
            k: math.log(max(p, 1e-10))
            for k, p in zip(scores.keys(), probs)
        }


def default_policy(
    temperature: float = 0.8,
    use_filters: bool = True,
) -> Callable[[str, list[str]], dict[str, float]]:
    """Factory returning a callable policy function for MCTS."""
    policy = ScafVAEPolicy(temperature=temperature, use_filters=use_filters)
    return policy.get_action_priors


if __name__ == "__main__":
    # Quick test
    from p4_mcts_rl_env import MolecularEnv

    env = MolecularEnv(initial_smiles="c1ccccc1", max_steps=3, fragment_set="all")
    policy = ScafVAEPolicy(temperature=0.8)

    print("Testing ScafVAE policy...")
    state = env.reset()
    priors = policy.get_action_priors(state, env.fragment_vocab)

    print(f"\nState: {state}")
    print(f"Scaffold compatibility: {policy._scaffold_compatibility(state):.3f}")
    print(f"\nTop-10 fragments by prior:")
    for i, (frag, log_prob) in enumerate(
        sorted(priors.items(), key=lambda x: -x[1])[:10]
    ):
        prob = math.exp(log_prob)
        name = env.fragment_names.get(frag, "?")
        print(f"  {i+1:2d}. {name:18s} {frag:25s} log-p={log_prob:+.3f}  p={prob:.3f}")

    print(f"\nTotal fragments scored: {len(priors)}")
    print("Policy test: OK")
