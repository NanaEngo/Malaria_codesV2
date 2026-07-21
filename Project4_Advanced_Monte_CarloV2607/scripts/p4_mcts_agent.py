#!/usr/bin/env python3
"""P4 — Monte Carlo Tree Search (MCTS) agent for molecular generation.

The agent explores a tree where each node is a partial molecule and edges are
fragment-attachment actions. Selection uses the UCT formula; expansion, rollout,
and backpropagation are standard MCTS steps.

The environment is deep-copied during expansion and rollout so that the shared
environment state is not mutated while exploring the tree.
"""

from __future__ import annotations

import copy
import math
import random
from typing import Any, Callable, Optional


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
    """

    def __init__(
        self,
        env: Any,
        oracle: Callable[[str], float],
        n_iterations: int = 100,
        c_puct: float = 1.414,
        policy_fn: Optional[Callable[[str, list[str]], dict[str, float]]] = None,
    ) -> None:
        self.env = env
        self.oracle = oracle
        self.n_iterations = n_iterations
        self.c_puct = c_puct
        self.policy_fn = policy_fn

    def search(self, root_state: str) -> str:
        """Run MCTS from root_state and return the best molecule found.

        Returns
        -------
        str
            SMILES of the best molecule found.
        """
        root = MCTSNode(root_state)
        root.step_count = self.env.step_count

        # Pre-compute action priors if a policy is available
        if self.policy_fn is not None:
            vocab = list(getattr(self.env, "fragment_vocab", []))
            self._action_priors = self.policy_fn(root_state, vocab)
        else:
            self._action_priors = {}

        for iteration in range(self.n_iterations):
            node = self._select(root)
            reward = self._rollout(node)
            self._backpropagate(node, reward)

        if not root.children:
            return root_state
        best = max(root.children.values(), key=lambda child: child.visits)
        return best.state

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
        where P(s,a) is the policy prior for taking action a from state s.
        """
        sqrt_n = math.sqrt(max(node.visits, 1))
        best_score = -float("inf")
        best_child = None

        for action, child in node.children.items():
            # Action value
            q = child.value / max(child.visits, 1)
            # Policy prior
            prior = self._action_priors.get(action, 0.0)
            # Convert log-prob back to prob for PUCT formula
            p = math.exp(prior) if prior < 0 else prior
            # PUCT exploration bonus
            u = self.c_puct * p * sqrt_n / (1.0 + child.visits)
            score = q + u

            if score > best_score:
                best_score = score
                best_child = child

        return best_child or list(node.children.values())[0]

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand the node by adding one untried action as a child."""
        if node.untried_actions is None:
            vocab = list(getattr(self.env, "fragment_vocab", []))
            if self.policy_fn is not None and self._action_priors:
                # Order by policy prior (highest first) for efficient exploration
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

        # Advance an isolated cloned environment so the shared env is untouched.
        env_copy = copy.deepcopy(self.env)
        env_copy.state = node.state
        env_copy.step_count = node.step_count
        next_state, _reward, _done, _info = env_copy.step(action)

        child = MCTSNode(state=next_state, parent=node, action=action)
        node.children[action] = child
        return child

    def _rollout(self, node: MCTSNode) -> float:
        """Simulate a random rollout from the node and return the oracle reward."""
        env_copy = copy.deepcopy(self.env)
        env_copy.state = node.state
        env_copy.step_count = node.step_count

        done = env_copy.step_count >= env_copy.max_steps or env_copy._is_terminal(env_copy.state)
        while not done:
            action = random.choice(env_copy.fragment_vocab)
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
