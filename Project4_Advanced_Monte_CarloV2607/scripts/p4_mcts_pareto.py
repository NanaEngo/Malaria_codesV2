#!/usr/bin/env python3
"""P4 — Pareto Monte Carlo Tree Search (PMCTS) for multi-objective molecular optimization.

Standard MCTS aggregates multiple objectives (MPO, docking, SYBA, SA) into a
scalar reward via weighted sum, which forces the user to choose weights a priori
and can miss optimal trade-offs. Pareto MCTS tracks the full Pareto front of
non-dominated solutions across all objectives, providing the decision-maker with
a set of optimal trade-offs.

A solution A dominates solution B iff:
    A_i >= B_i for all objectives i AND A_i > B_i for at least one objective i

The Pareto front is the set of all non-dominated solutions found during search.

Reference: Mothra (JCIM 2024), CombiMOTS (arXiv 2026)
"""

from __future__ import annotations

import copy
import math
import random
from typing import Any, Callable, Optional

import numpy as np


class ParetoFront:
    """Maintain a set of non-dominated (Pareto-optimal) solutions.

    Uses pymoo's non-dominated sorting and hypervolume computation for
    efficient and exact multi-objective optimization metrics.

    Parameters
    ----------
    objectives : list[str]
        Names of the objectives (e.g., ['mpo', 'docking', 'syba']).
    maximize : list[bool]
        Whether each objective is to be maximized (True) or minimized (False).
    """

    def __init__(self, objectives: list[str], maximize: Optional[list[bool]] = None):
        self.objectives = objectives
        self.n_obj = len(objectives)
        self.maximize = (
            maximize if maximize is not None else [True] * self.n_obj
        )
        # Store (solution_smiles, vector_of_scores, metadata)
        self._solutions: list[tuple[str, np.ndarray, dict]] = []

    def update(self, smiles: str, scores: dict[str, float], metadata: Optional[dict] = None) -> bool:
        """Try to add a new solution using pymoo's non-dominated check.
        Returns True if Pareto front was updated.
        """
        from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

        vec = np.array([scores.get(obj, 0.0) for obj in self.objectives], dtype=float)
        if len(self._solutions) == 0:
            self._solutions.append((smiles, vec, metadata or {}))
            return True

        # Check dominance using pymoo's efficient algorithm
        all_vecs = np.array([v for _, v, _ in self._solutions] + [vec])
        # pymoo minimises by default; negate maximised objectives
        sign = np.array([-1.0 if m else 1.0 for m in self.maximize])
        all_vecs_signed = all_vecs * sign[np.newaxis, :]

        # NonDominatedSorting.do() returns a numpy array (not a list)
        front_indices = NonDominatedSorting().do(all_vecs_signed, only_non_dominated_front=True)
        non_dominated_mask = np.zeros(len(all_vecs_signed), dtype=bool)
        non_dominated_mask[front_indices] = True

        # Check if new solution (last row) is non-dominated
        if not non_dominated_mask[-1]:
            return False  # new solution is dominated

        # Rebuild non-dominated solutions (keep only old non-dominated + new)
        kept = [
            (smi, vec, meta)
            for i, (smi, vec, meta) in enumerate(self._solutions)
            if non_dominated_mask[i]
        ]
        self._solutions = kept + [(smiles, vec, metadata or {})]
        return True

    @property
    def solutions(self) -> list[tuple[str, np.ndarray, dict]]:
        """Return the list of (smiles, score_vector, metadata) for non-dominated solutions."""
        if not self._solutions:
            return []
        from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

        vecs = np.array([v for _, v, _ in self._solutions])
        sign = np.array([-1.0 if m else 1.0 for m in self.maximize])
        # NonDominatedSorting.do() returns a numpy array directly
        front_indices = NonDominatedSorting().do(vecs * sign[np.newaxis, :], only_non_dominated_front=True)
        return [self._solutions[i] for i in front_indices]

    def hypervolume(self, reference: Optional[np.ndarray] = None) -> float:
        """Exact hypervolume indicator using pymoo's algorithm.

        Higher is better. Works for any number of objectives.
        """
        sols = self.solutions
        if not sols:
            return 0.0

        try:
            from pymoo.indicators.hv import Hypervolume

            vecs = np.array([v for _, v, _ in sols])
            # Negate maximised objectives for pymoo (minimisation convention)
            sign = np.array([-1.0 if m else 1.0 for m in self.maximize])
            signed_vecs = vecs * sign[np.newaxis, :]

            if reference is None:
                # Reference point must be WORSE than all solutions (pymoo minimisation convention):
                # use max + 10% margin instead of min - 10% margin
                vmin = signed_vecs.min(axis=0)
                vmax = signed_vecs.max(axis=0)
                margin = 0.1 * (vmax - vmin)
                ref_point = vmax + np.where(margin > 0, margin, 0.1)
                ref_point = np.where(np.isinf(ref_point), 0.0, ref_point)
            else:
                ref_point = reference.copy()
                for i, m in enumerate(self.maximize):
                    if m:
                        ref_point[i] = -ref_point[i]

            hv = Hypervolume(ref_point=ref_point)
            return hv.do(signed_vecs)
        except ImportError:
            return 0.0


class PMCTSNode:
    """Node in the Pareto MCTS tree, tracking multi-objective value."""

    def __init__(self, state: str, parent: Optional["PMCTSNode"] = None, action: str = ""):
        self.state = state
        self.parent = parent
        self.action = action
        self.children: dict[str, "PMCTSNode"] = {}
        self.visits = 0
        # Multi-objective: list of score vectors
        self.value_vectors: list[np.ndarray] = []
        self.untried_actions: Optional[list[str]] = None
        self.step_count = parent.step_count + 1 if parent else 0

    def is_fully_expanded(self) -> bool:
        return self.untried_actions is not None and len(self.untried_actions) == 0

    def best_child(self, c: float = 1.414) -> "PMCTSNode":
        """Select child with best multi-objective UCT score."""
        # Use scalarized proxy for selection (weighted sum across objectives)
        return max(
            self.children.values(),
            key=lambda child: (
                np.mean(child.value_vectors) if child.value_vectors else 0.0
            ) / max(child.visits, 1)
            + c * math.sqrt(math.log(self.visits) / max(child.visits, 1)),
        )

    def update(self, score_vector: np.ndarray) -> None:
        self.visits += 1
        self.value_vectors.append(score_vector)


class ParetoMCTSAgent:
    """Pareto MCTS agent for multi-objective molecular optimization.

    Maintains a global Pareto front of non-dominated solutions discovered
    during search. Uses PUCT for tree selection, with the UCB term computed
    from the mean of stored score vectors.

    Parameters
    ----------
    env : MolecularEnv
        Molecular environment.
    oracle_fn : callable
        Function returning a dict of {objective_name: score} for a SMILES.
    objectives : list[str]
        Names of objectives to optimise.
    maximize : list[bool] or None
        Whether each objective is to be maximised.
    n_iterations : int
        Number of MCTS iterations per search.
    c_puct : float
        Exploration constant.
    policy_fn : callable or None
        Optional policy for PUCT priors.
    """

    def __init__(
        self,
        env: Any,
        oracle_fn: Callable[[str], dict[str, float]],
        objectives: Optional[list[str]] = None,
        maximize: Optional[list[bool]] = None,
        n_iterations: int = 100,
        c_puct: float = 1.414,
        policy_fn: Optional[Callable] = None,
    ):
        self.env = env
        self.oracle_fn = oracle_fn
        self.objectives = objectives or ["mpo", "syba", "sa", "rrs", "pns"]
        self.maximize = maximize
        self.n_iterations = n_iterations
        self.c_puct = c_puct
        self.policy_fn = policy_fn

        self.pareto_front = ParetoFront(self.objectives, self.maximize)
        self._action_priors: dict[str, float] = {}

    def search(self, root_state: str) -> ParetoFront:
        """Run Pareto MCTS from root_state, return the Pareto front."""
        root = PMCTSNode(root_state)
        root.step_count = self.env.step_count

        if self.policy_fn is not None:
            vocab = list(getattr(self.env, "fragment_vocab", []))
            self._action_priors = self.policy_fn(root_state, vocab) or {}

        for _ in range(self.n_iterations):
            node = self._select(root)
            score_vector = self._rollout(node)
            self._backpropagate(node, score_vector)

            # Update global Pareto front
            scores_dict = {
                obj: float(score_vector[i])
                for i, obj in enumerate(self.objectives)
            }
            self.pareto_front.update(node.state, scores_dict)

        return self.pareto_front

    def _select(self, node: PMCTSNode) -> PMCTSNode:
        while node.children and node.is_fully_expanded():
            node = node.best_child(self.c_puct)
        if not node.is_fully_expanded():
            node = self._expand(node)
        return node

    def _expand(self, node: PMCTSNode) -> PMCTSNode:
        if node.untried_actions is None:
            vocab = list(getattr(self.env, "fragment_vocab", []))
            if self._action_priors:
                node.untried_actions = sorted(
                    vocab,
                    key=lambda a: self._action_priors.get(a, 0.0),
                    reverse=True,
                )
            else:
                node.untried_actions = list(vocab)
                random.shuffle(node.untried_actions)

        if not node.untried_actions:
            return node

        action = node.untried_actions.pop()
        env_copy = copy.deepcopy(self.env)
        env_copy.state = node.state
        env_copy.step_count = node.step_count
        next_state, _, _, _ = env_copy.step(action)

        child = PMCTSNode(state=next_state, parent=node, action=action)
        node.children[action] = child
        return child

    def _rollout(self, node: PMCTSNode) -> np.ndarray:
        env_copy = copy.deepcopy(self.env)
        env_copy.state = node.state
        env_copy.step_count = node.step_count

        done = env_copy.step_count >= env_copy.max_steps or env_copy._is_terminal(env_copy.state)
        while not done:
            action = random.choice(env_copy.fragment_vocab)
            _, _, done, _ = env_copy.step(action)

        scores = self.oracle_fn(env_copy.state)
        return np.array([scores.get(obj, 0.0) for obj in self.objectives], dtype=float)

    def _backpropagate(self, node: PMCTSNode, score_vector: np.ndarray) -> None:
        while node is not None:
            node.update(score_vector)
            node = node.parent


if __name__ == "__main__":
    from p4_mcts_rl_env import MolecularEnv
    from p4_mcts_oracles import OracleAggregator
    from p4_mcts_policy import ScafVAEPolicy

    env = MolecularEnv(initial_smiles="c1ccccc1", max_steps=5, fragment_set="all",
                       randomize_attachment=True)
    oracle = OracleAggregator(use_precomputed=False)
    policy = ScafVAEPolicy(temperature=0.8)

    agent = ParetoMCTSAgent(
        env,
        oracle_fn=oracle.score,
        objectives=["mpo", "syba", "sa", "rrs", "pns"],
        maximize=[True, True, False, True, True],  # minimise SA, maximise RRS+PNS
        n_iterations=50,
        policy_fn=policy.get_action_priors,
    )

    front = agent.search("c1ccccc1")
    print(f"Pareto front size: {len(front.solutions)}")
    print(f"Hypervolume: {front.hypervolume():.4f}")
    for smi, vec, meta in front.solutions[:5]:
        print(f"  {smi:35s} MPO={vec[0]:.3f} SYBA={vec[1]:.3f} SA={vec[2]:.3f} "
              f"RRS={vec[3]:.3f} PNS={vec[4]:.3f}")
