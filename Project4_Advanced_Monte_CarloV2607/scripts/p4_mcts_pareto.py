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
        self._dominated: set[int] = set()

    def _dominates(self, a: np.ndarray, b: np.ndarray) -> bool:
        """Check if vector a dominates vector b."""
        at_least_one = False
        for i in range(self.n_obj):
            ai = a[i] if self.maximize[i] else -a[i]
            bi = b[i] if self.maximize[i] else -b[i]
            if ai < bi:
                return False
            if ai > bi:
                at_least_one = True
        return at_least_one

    def update(self, smiles: str, scores: dict[str, float], metadata: Optional[dict] = None) -> bool:
        """Try to add a new solution. Returns True if Pareto front was updated."""
        vec = np.array([scores.get(obj, 0.0) for obj in self.objectives], dtype=float)
        meta = metadata or {}

        # Check if new solution is dominated by any existing solution
        for i, (existing_smi, existing_vec, _) in enumerate(self._solutions):
            if i in self._dominated:
                continue
            if self._dominates(existing_vec, vec):
                return False  # dominated — not Pareto-optimal

        # New solution is Pareto-optimal: remove dominated solutions
        newly_dominated = []
        for i, (_, existing_vec, _) in enumerate(self._solutions):
            if i in self._dominated:
                continue
            if self._dominates(vec, existing_vec):
                newly_dominated.append(i)

        for i in newly_dominated:
            self._dominated.add(i)

        self._solutions.append((smiles, vec, meta))
        return True

    @property
    def solutions(self) -> list[tuple[str, np.ndarray, dict]]:
        """Return the list of (smiles, score_vector, metadata) for non-dominated solutions."""
        return [
            (smi, vec, meta)
            for i, (smi, vec, meta) in enumerate(self._solutions)
            if i not in self._dominated
        ]

    @property
    def hypervolume(self, reference: Optional[np.ndarray] = None) -> float:
        """Approximate hypervolume indicator (sum of volumes of dominated hyper-rectangles).

        Higher is better. Uses a simple Monte Carlo estimate for >2 objectives.
        """
        sols = self.solutions
        if not sols:
            return 0.0

        if reference is None:
            reference = np.zeros(self.n_obj)

        if self.n_obj <= 2:
            # Exact hypervolume for 2D
            vecs = np.array([v for _, v, _ in sols])
            # Sort by first objective (descending)
            idx = np.argsort([-v[0] if self.maximize[0] else v[0] for v in vecs])
            sorted_vecs = vecs[idx]
            hv = 0.0
            prev_second = reference[1]
            for v in sorted_vecs:
                if self.maximize[1]:
                    width = max(0.0, v[1] - reference[1])
                    height = max(0.0, prev_second - reference[1])
                    hv += width * height
                else:
                    width = max(0.0, reference[1] - v[1])
                    height = max(0.0, reference[1] - prev_second)
                    hv += width * height
                prev_second = v[1] if self.maximize[1] else -v[1]
            return hv
        else:
            # Monte Carlo estimate for >2 objectives
            bounds = np.array([
                [v[i] for _, v, _ in sols] for i in range(self.n_obj)
            ])
            n_samples = max(10000, 100 * len(sols))
            count = 0
            rng = np.random.default_rng(42)
            for _ in range(n_samples):
                point = rng.uniform(
                    [b.min() for b in bounds],
                    [b.max() for b in bounds],
                )
                # Check if point is dominated by any solution
                dominated = False
                for _, v, _ in sols:
                    if all(
                        (v[i] >= point[i]) if self.maximize[i] else (v[i] <= point[i])
                        for i in range(self.n_obj)
                    ):
                        dominated = True
                        break
                if dominated:
                    count += 1
            return count / n_samples * np.prod([b.max() - b.min() for b in bounds])


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
        self.objectives = objectives or ["mpo", "docking", "syba"]
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
        objectives=["mpo", "syba", "sa"],
        maximize=[True, True, False],  # minimise SA (lower is better)
        n_iterations=50,
        policy_fn=policy.get_action_priors,
    )

    front = agent.search("c1ccccc1")
    print(f"Pareto front size: {len(front.solutions)}")
    print(f"Hypervolume: {front.hypervolume():.4f}")
    for smi, vec, meta in front.solutions[:5]:
        print(f"  {smi:35s} MPO={vec[0]:.3f} SYBA={vec[1]:.3f} SA={vec[2]:.3f}")
