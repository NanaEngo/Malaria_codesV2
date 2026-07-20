#!/usr/bin/env python3
"""P4 — Molecular RL environment for MCTS-guided generator.

This module defines a Gym-compatible environment where:
- state  : a partial molecular graph / scaffold (SMILES string)
- action : attachment of a molecular fragment
- reward : composite pharmacological score (MPO, docking, SYBA, SA)

The environment uses RDKit to validate fragment attachments and to combine
molecules into chemically valid structures.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import ValenceType


class MolecularEnv:
    """Simple molecular construction environment.

    Parameters
    ----------
    initial_smiles : str
        Starting scaffold SMILES.
    max_steps : int
        Maximum number of fragment additions before termination.
    """

    def __init__(self, initial_smiles: str = "C", max_steps: int = 10) -> None:
        self.initial_smiles = initial_smiles
        self.max_steps = max_steps
        self.state: str = initial_smiles
        self.step_count: int = 0
        self._fragment_vocab: list[str] = [
            "c1ccccc1",  # phenyl
            "C",         # methyl
            "N",         # amine
            "O",         # hydroxyl
            "Cl",        # chloride
        ]

    @property
    def fragment_vocab(self) -> list[str]:
        """Return the list of available fragment actions."""
        return self._fragment_vocab

    def reset(self, initial_smiles: Optional[str] = None) -> str:
        """Reset the environment to the initial scaffold."""
        self.state = initial_smiles or self.initial_smiles
        self.step_count = 0
        return self.state

    def step(self, action: str) -> Tuple[str, float, bool, dict[str, Any]]:
        """Apply one fragment attachment and return (next_state, reward, done, info).

        Parameters
        ----------
        action : str
            SMILES fragment to attach.

        Returns
        -------
        tuple
            (next_state_smiles, reward, done, info)
        """
        self.state = self._attach_fragment(self.state, action)
        self.step_count += 1

        reward = self._dummy_reward(self.state)
        done = self.step_count >= self.max_steps or self._is_terminal(self.state)
        info = {"step": self.step_count, "smiles": self.state}
        return self.state, reward, done, info

    def _attach_fragment(self, state: str, fragment: str) -> str:
        """Attach a fragment to the current molecule using RDKit.

        The attachment selects atoms with available implicit valence on both
        the current molecule and the fragment, adds a single bond between
        them, and sanitizes the result. If the operation fails, the original
        state is returned unchanged.
        """
        mol1 = Chem.MolFromSmiles(state)
        mol2 = Chem.MolFromSmiles(fragment)
        if mol1 is None or mol2 is None:
            return state

        combined = Chem.CombineMols(mol1, mol2)
        rw_mol = Chem.RWMol(combined)

        num_mol1_atoms = mol1.GetNumAtoms()
        mol1_atoms = [
            a.GetIdx()
            for a in rw_mol.GetAtoms()
            if a.GetIdx() < num_mol1_atoms and a.GetValence(ValenceType.IMPLICIT) > 0
        ]
        mol2_atoms = [
            a.GetIdx()
            for a in rw_mol.GetAtoms()
            if a.GetIdx() >= num_mol1_atoms and a.GetValence(ValenceType.IMPLICIT) > 0
        ]

        if not mol1_atoms or not mol2_atoms:
            return state

        # Deterministic attachment: always pick the first available atom on the
        # scaffold and on the fragment. This keeps the MCTS tree consistent.
        idx1 = mol1_atoms[0]
        idx2 = mol2_atoms[0]
        rw_mol.AddBond(idx1, idx2, Chem.BondType.SINGLE)

        try:
            Chem.SanitizeMol(rw_mol)
            return Chem.MolToSmiles(rw_mol)
        except Exception:
            return state

    def _dummy_reward(self, state: str) -> float:
        """Placeholder reward; integrate with p4_mcts_oracles."""
        return 0.0

    def _is_terminal(self, state: str) -> bool:
        """Placeholder terminal condition."""
        return False


if __name__ == "__main__":
    env = MolecularEnv(initial_smiles="C", max_steps=5)
    state = env.reset()
    print("Initial state:", state)
    for fragment in env.fragment_vocab[:3]:
        state, reward, done, info = env.step(fragment)
        print(f"Action: {fragment:10s} -> State: {state:20s} Reward: {reward:.3f} Done: {done}")
