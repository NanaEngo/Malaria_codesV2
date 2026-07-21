#!/usr/bin/env python3
"""P4 — Monte Carlo Tree Search (MCTS) agent for molecular generation.

The agent explores a tree where each node is a partial molecule and edges are
fragment-attachment actions. Selection uses the UCT formula; expansion, rollout,
and backpropagation are standard MCTS steps.

The environment is deep-copied during expansion and rollout so that the shared
environment state is not mutated while exploring the tree.
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable, Optional

import numpy as np


class MCTSNode:
    """Node in the MCTS tree."""

    def __init__(self, state: str, parent: Optional["MCTSNode"] = None, action: str = "") -> None:
        self.state = state
        self.parent = parent
        self.action = action
        self.children: dict[str, "MCTSNode"] = {}
        self.visits = 0
        self.value = 0.0
        self.untried_actions: Optional[list[str]] = None
        self.step_count = parent.step_count + 1 if parent else 0

    def is_fully_expanded(self) -> bool:
        return self.untried_actions is not None and len(self.untried_actions) == 0

    def best_child(self, c: float = 1.414) -> "MCTSNode":
        """Select child with highest UCT score."""
        return max(
            self.children.values(),
            key=lambda child: child.value / max(child.visits, 1)
            + c * math.sqrt(math.log(self.visits) / max(child.visits, 1)),
        )

    def update(self, reward: float) -> None:
        self.visits += 1
        self.value += reward


class MCTSAgent:
    """MCTS agent for molecular optimization.

    Uses a PUCT variant of the standard MCTS algorithm with policy-guided
    selection. The policy provides action priors P(s,a) that bias the
    tree search toward chemically plausible fragment combinations.

    Parameters
    ----------
    env : MolecularEnv
        Molecular environment with reset(), step(), and fragment_vocab.
    oracle : callable
        Function that maps a SMILES string to a scalar reward.
    n_iterations : int
        Number of MCTS iterations per search.
    c_puct : float
        Exploration constant for PUCT (higher = more exploration).
    policy_fn : callable or None
        Function(state, available_actions) -> dict[str, float] of log-prob
        priors. If None, uses uniform priors (standard UCT).
    rollout_strategy : str
        Rollout strategy: 'policy_biased' (default) or 'random'.
    seed : int or None
        Random seed for reproducible MCTS runs.
    progressive_widening_k : int
        Base number of top-K actions to consider per node (Progressive
        Widening). Default 10. Set to 0 or >33 to disable.
    """

    def __init__(
        self,
        env: Any,
        oracle: Callable[[str], float],
        n_iterations: int = 100,
        c_puct: float = 1.414,
        policy_fn: Optional[Callable[[str, list[str]], dict[str, float]]] = None,
        rollout_strategy: str = "policy_biased",
        seed: Optional[int] = None,
        progressive_widening_k: int = 10,
    ) -> None:
        self.env = env
        self.oracle = oracle
        self.n_iterations = n_iterations
        self.c_puct = c_puct
        self.policy_fn = policy_fn
        self.rollout_strategy = rollout_strategy
        self._rng = random.Random(seed)
        self.progressive_widening_k = progressive_widening_k

    def _make_env_copy(self, state: str, step_count: int) -> Any:
        """Create a lightweight environment copy (avoids expensive deepcopy).

        The new env uses the agent's RNG to ensure reproducibility even
        when randomize_attachment=True (every expansion/rollout is seeded
        deterministically from the parent agent's RNG).
        """
        from p4_mcts_rl_env import MolecularEnv

        env_copy = MolecularEnv(
            initial_smiles=self.env.initial_smiles,
            max_steps=self.env.max_steps,
            fragment_set=getattr(self.env, '_fragment_set', 'all'),
            randomize_attachment=getattr(self.env, 'randomize_attachment', False),
            seed=self._rng.randint(0, 2**31 - 1),
        )
        env_copy.state = state
        env_copy.step_count = step_count
        return env_copy

    def search(self, root_state: str) -> str:
        """Run MCTS from root_state and return the best molecule found.

        Returns
        -------
        str
            SMILES of the best molecule found.
        """
        root = MCTSNode(root_state)
        root.step_count = self.env.step_count

        # Cache priors per node state for efficiency
        self._priors_cache: dict[str, dict[str, float]] = {}

        for iteration in range(self.n_iterations):
            node = self._select(root)
            reward = self._rollout(node)
            self._backpropagate(node, reward)

        if not root.children:
            return root_state
        best = max(root.children.values(), key=lambda child: child.visits)
        return best.state

    def _get_priors(self, state: str) -> dict[str, float]:
        """Get (or compute and cache) action priors for a given state."""
        if state in self._priors_cache:
            return self._priors_cache[state]
        if self.policy_fn is not None:
            vocab = list(getattr(self.env, "fragment_vocab", []))
            priors = self.policy_fn(state, vocab)
        else:
            priors = {}
        self._priors_cache[state] = priors
        return priors

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select a leaf node using PUCT, expanding if possible."""
        while node.children and node.is_fully_expanded():
            node = self._puct_best_child(node)
        if not node.is_fully_expanded():
            node = self._expand(node)
        return node

    def _puct_best_child(self, node: MCTSNode) -> MCTSNode:
        """Select child with highest PUCT score = Q + U.

        U = c_puct * P(s,a) * sqrt(N_parent) / (1 + N_child)
        where P(s,a) is the state-dependent policy prior for action a.

        Uses a minimum prior of 1e-8 to avoid zero-prior actions being
        completely unexplored (fix: previous 0.0 caused `exp(0)=1` which
        over-favoured un-prioritised actions).
        """
        sqrt_n = math.sqrt(max(node.visits, 1))
        best_score = -float("inf")
        best_child = None

        # Get state-dependent priors for this node
        node_priors = self._get_priors(node.state) if self.policy_fn else {}

        for action, child in node.children.items():
            # Action value
            q = child.value / max(child.visits, 1)
            # State-dependent policy prior
            prior = node_priors.get(action, 0.0)
            # Convert log-prob back to prob for PUCT formula
            p = math.exp(prior) if prior < 0 else prior
            # Ensure p is at least a small positive value to avoid actions
            # with zero prior being over-favoured by the PUCT formula
            # (previously exp(0)=1 gave them equal weight to high-prior actions)
            p = max(p, 1e-8)
            # PUCT exploration bonus
            u = self.c_puct * p * sqrt_n / (1.0 + child.visits)
            score = q + u

            if score > best_score:
                best_score = score
                best_child = child

        return best_child or list(node.children.values())[0]

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand the node by adding one untried action as a child.

        Uses **Progressive Widening**: limits untried actions to the top-K
        highest-priority fragments (based on ScafVAE policy priors).
        This reduces the branching factor from 33→10 (default K=10),
        giving ~3× more visits per action within the same budget.
        """
        if node.untried_actions is None:
            vocab = list(getattr(self.env, "fragment_vocab", []))
            # Get state-dependent priors for this node
            node_priors = self._get_priors(node.state)
            if node_priors:
                # Order by policy prior (highest first)
                sorted_actions = sorted(
                    vocab,
                    key=lambda a: node_priors.get(a, 0.0),
                    reverse=True,
                )
            else:
                sorted_actions = list(vocab)
                self._rng.shuffle(sorted_actions)

            # Progressive Widening: limit to top-K actions
            pw_k = self.progressive_widening_k
            if pw_k > 0 and len(sorted_actions) > pw_k:
                node.untried_actions = sorted_actions[:pw_k]
            else:
                node.untried_actions = sorted_actions

        if not node.untried_actions:
            return node

        action = node.untried_actions.pop(0)

        # Use lightweight env copy instead of expensive deepcopy
        env_copy = self._make_env_copy(node.state, node.step_count)
        next_state, _reward, _done, _info = env_copy.step(action)

        child = MCTSNode(state=next_state, parent=node, action=action)
        node.children[action] = child
        return child

    def _rollout(self, node: MCTSNode) -> float:
        """Simulate a rollout from the node and return the oracle reward.

        Uses lightweight env reinit instead of expensive deepcopy.
        Policy-biased sampling during rollout:
        - 'policy_biased' (default): sample fragments from ScafVAE policy distribution
        - 'random': uniform random (original, poor performance)
        """
        # Lightweight env copy instead of deepcopy
        env_copy = self._make_env_copy(node.state, node.step_count)

        done = env_copy.step_count >= env_copy.max_steps or env_copy._is_terminal(env_copy.state)

        while not done:
            if self.rollout_strategy == "policy_biased" and self.policy_fn is not None:
                # Sample fragment from policy distribution (not uniform random)
                node_priors = self._get_priors(env_copy.state)
                if node_priors:
                    actions = list(node_priors.keys())
                    log_probs = np.array([node_priors[a] for a in actions])
                    # Numerically stable softmax
                    log_probs = log_probs - np.max(log_probs)
                    probs = np.exp(log_probs)
                    probs = probs / probs.sum()
                    action = self._rng.choices(actions, weights=probs, k=1)[0]
                else:
                    action = self._rng.choice(env_copy.fragment_vocab)
            else:
                # Uniform random (original)
                action = self._rng.choice(env_copy.fragment_vocab)

            _state, _reward, done, _info = env_copy.step(action)

        return self.oracle(env_copy.state)

    def _backpropagate(self, node: MCTSNode, reward: float) -> None:
        """Propagate the reward up the tree."""
        while node is not None:
            node.update(reward)
            node = node.parent


def dummy_oracle(smiles: str) -> float:
    """Placeholder oracle returning a random reward."""
    return random.random()


if __name__ == "__main__":
    from p4_mcts_rl_env import MolecularEnv

    env = MolecularEnv(initial_smiles="C", max_steps=5)
    agent = MCTSAgent(env, oracle=dummy_oracle, n_iterations=10)
    best_state = agent.search("C")
    print("Best state found:", best_state)
