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

# Dirichlet noise parameters (AlphaGo-style root exploration)
_DIRICHLET_ALPHA = 0.15        # concentration parameter (smaller = sparser noise)
_DIRICHLET_EPSILON = 0.20      # mixing proportion (P' = (1-ε)P + ε·Dir)


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

    Features (2026-07):
    - **Dynamic Progressive Widening**: branching factor grows with
      visit count (k * N^alpha) instead of a hard K cap, allowing deeper
      exploration in promising regions while restricting early branching.
    - **Virtual Loss**: penalises nodes being explored in the current
      iteration to encourage parallel exploration of diverse branches.
    - **Policy-biased rollouts**: informed rollouts via ScafVAE priors.

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
    pw_alpha : float
        Dynamic Progressive Widening exponent: max_actions = max(5, k * N^alpha).
        Default 0.5 (square-root growth). Set k=0 to disable.
    pw_k : float
        Base multiplier for Dynamic PW: max_actions = max(5, k * N^alpha).
        Default 1.0. Higher = more actions per node.
    virtual_loss : float
        Penalty applied to nodes currently being explored. Default 0.01.
        Higher = more exploration diversity.
    rollout_temperature : float
        Initial softmax temperature for policy-biased rollout. Higher = more
        uniform (exploration). Default 1.5.
    rollout_temp_min : float
        Minimum temperature after annealing. Default 0.3.
    rollout_epsilon : float
        Blending weight between policy and uniform distributions during rollout.
        Default 0.15. Higher = more diverse rollout actions.
    collision_threshold : int
        Number of consecutive identical best molecules before reset.
        Default 50. Detects rollout collapse.
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
        pw_alpha: float = 0.5,
        pw_k: float = 1.0,
        virtual_loss: float = 0.05,
        rollout_temperature: float = 1.5,
        rollout_temp_min: float = 0.3,
        rollout_epsilon: float = 0.15,
        collision_threshold: int = 50,
    ) -> None:
        self.env = env
        self.oracle = oracle
        self.n_iterations = n_iterations
        self.c_puct = c_puct
        self.policy_fn = policy_fn
        self.rollout_strategy = rollout_strategy
        self._rng = random.Random(seed)
        self.pw_alpha = pw_alpha
        self.pw_k = pw_k
        self.virtual_loss = virtual_loss
        self.rollout_temperature = rollout_temperature
        self.rollout_temp_min = rollout_temp_min
        self.rollout_epsilon = rollout_epsilon
        self.collision_threshold = collision_threshold
        # Track states visited this search to avoid revisiting (MCTS-Solver)
        self._visited_states: set[str] = set()
        self._priors_cache: dict[str, dict[str, float]] = {}

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

        Features:
        - Dynamic Progressive Widening (branching factor grows with visits)
        - Virtual Loss (diverse parallel exploration)
        - State caching (avoid revisiting same molecule)
        - Temperature annealing: rollout temperature decreases from
          rollout_temperature to rollout_temp_min over iterations
        - Epsilon-greedy: probability rollout_epsilon of random action
        - Adversarial collapse detection: if the same best molecule is
          found for collision_threshold consecutive iterations, the
          priors cache is cleared and temperature is reset to force
          re-exploration

        Returns
        -------
        str
            SMILES of the best molecule found.
        """
        root = MCTSNode(root_state)
        root.step_count = self.env.step_count

        # Reset per-search caches
        self._priors_cache = {}
        self._visited_states = {root_state}

        # Track best molecule seen during ANY part of the search
        # (including intermediate rollout states), not just root children.
        # This is critical: rollout from a good first-step (e.g. toluene)
        # often ADD fragments that LOWER the reward; without global tracking
        # the search returns the root child whose ROLLOUT was best, not the
        # child whose DIRECT molecule is best.
        best_global_smiles = root_state
        best_global_reward = self.oracle(root_state)

        # Collapse detection state
        last_best_state = root_state
        collision_count = 0
        # Start with max temperature; annealed at end of each iteration
        current_temp = self.rollout_temperature

        for iteration in range(self.n_iterations):
            node = self._select(root)
            reward, rollout_best_smiles, rollout_best_reward = self._rollout(
                node, temperature=current_temp)
            self._backpropagate(node, reward)

            # Track best molecule globally (max over all visited states)
            if rollout_best_reward > best_global_reward:
                best_global_reward = rollout_best_reward
                best_global_smiles = rollout_best_smiles

            # Adversarial collapse detection
            if root.children:
                best_child = max(root.children.values(),
                                 key=lambda c: c.value / max(c.visits, 1))
                current_best = best_child.state
            else:
                current_best = root_state

            if current_best == last_best_state:
                collision_count += 1
            else:
                collision_count = 0
                last_best_state = current_best

            # If collapse detected, force exploration via Dirichlet noise
            # on root priors (AlphaGo-style). Resets temperature to max
            # so the NEXT rollout explores more aggressively.
            if collision_count >= self.collision_threshold:
                self._priors_cache = {}
                current_temp = self.rollout_temperature  # Reset to max for next rollout
                # Dirichlet noise on root: get root priors and perturb them
                if self.policy_fn is not None and root.children:
                    root_priors = self._get_priors(root.state)
                    if root_priors:
                        from numpy.random import Generator, MT19937
                        _rg = Generator(MT19937(self._rng.randint(0, 2**31)))
                        dir_noise = _rg.dirichlet([_DIRICHLET_ALPHA] * len(root_priors))
                        # Perturb priors in the cache so PUCT uses noisy values
                        noisy_priors = {}
                        for idx, (act, prior) in enumerate(root_priors.items()):
                            # P' = (1 - ε) * P + ε * Dir(α)
                            noisy_priors[act] = (1.0 - _DIRICHLET_EPSILON) * prior + _DIRICHLET_EPSILON * float(dir_noise[idx])
                        self._priors_cache[root.state] = noisy_priors
                collision_count = 0
            else:
                # Annealed temperature for NEXT iteration
                # Use (iteration + 1) to avoid one-iteration delay:
                # iteration 0 computes temp for iteration 1's rollout, etc.
                frac = (iteration + 1) / max(self.n_iterations - 1, 1)
                frac = min(frac, 1.0)  # clamp to [0, 1]
                current_temp = self.rollout_temperature - frac * (self.rollout_temperature - self.rollout_temp_min)

        # Store root for downstream metrics (hparam search uses this)
        self._root = root

        if not root.children:
            # Cache oracle result to avoid double-call and stochastic inconsistency
            root_oracle_reward = self.oracle(root_state)
            return best_global_smiles if best_global_reward > root_oracle_reward else root_state

        # Best child by value/visits (MCTS standard)
        best_child = max(root.children.values(),
                         key=lambda child: child.value / max(child.visits, 1))
        best_child_reward = self.oracle(best_child.state)

        # Return the BEST molecule found during the entire search
        # (including intermediate rollout states). This is essential for
        # molecular MCTS: a good first step (e.g. toluene, reward=0.44) may
        # have a LOW rollout reward because subsequent fragment additions
        # degrade quality. The MCTS tree correctly uses terminal rewards
        # for backpropagation, but the BEST molecule is often an
        # intermediate along the rollout trajectory, not the terminal state.
        if best_global_reward > best_child_reward:
            return best_global_smiles
        return best_child.state

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
        """Select child with highest PUCT score = Q + U - VL.

        U = c_puct * P(s,a) * sqrt(N_parent) / (1 + N_child)
        where P(s,a) is the state-dependent policy prior for action a.

        **Virtual Loss (VL)**: a small penalty subtracted from the score
        to discourage repeated selection of the same branch within a
        single search iteration. This promotes exploration of diverse
        chemical regions.

        Uses a minimum prior of 1e-8 to avoid zero-prior actions being
        completely unexplored (fix: previous 0.0 caused `exp(0)=1` which
        over-favoured un-prioritised actions).
        """
        sqrt_n = math.sqrt(max(node.visits, 1))
        best_score = -float("inf")
        best_child = None

        # Get state-dependent priors for this node
        node_priors = self._get_priors(node.state) if self.policy_fn else {}

        # Apply virtual loss: penalise children that have been visited
        # many times already (encourages exploring less-visited branches)
        max_visits = max((c.visits for c in node.children.values()), default=1)

        for action, child in node.children.items():
            # Action value
            q = child.value / max(child.visits, 1)
            # State-dependent policy prior
            prior = node_priors.get(action, 0.0)
            # Convert log-prob back to prob for PUCT formula
            p = math.exp(prior) if prior < 0 else prior
            # Ensure p is at least a small positive value
            p = max(p, 1e-8)
            # PUCT exploration bonus
            u = self.c_puct * p * sqrt_n / (1.0 + child.visits)

            # Virtual Loss: penalise over-explored children
            # scale: fraction of max visits, multiplied by virtual_loss
            visit_ratio = child.visits / max_visits if max_visits > 0 else 0.0
            vl = self.virtual_loss * visit_ratio

            score = q + u - vl

            if score > best_score:
                best_score = score
                best_child = child

        return best_child or list(node.children.values())[0]

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand the node by adding one untried action as a child.

        Uses **Dynamic Progressive Widening**: the number of allowed actions
        grows with the node's visit count: max_actions = max(5, k * N^alpha)
        where N = node.visits, k = pw_k, alpha = pw_alpha.
        This replaces the old hard K=20 cap, allowing more actions in
        promising regions while keeping the branching factor manageable
        early on.
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

            # Dynamic Progressive Widening: actions = f(visit_count)
            if self.pw_k > 0:
                N = max(node.visits, 1)
                max_actions = max(5, int(self.pw_k * (N ** self.pw_alpha)))
                max_actions = min(max_actions, len(sorted_actions))
                node.untried_actions = sorted_actions[:max_actions]
            else:
                node.untried_actions = sorted_actions

        if not node.untried_actions:
            return node

        action = node.untried_actions.pop(0)

        # Use lightweight env copy instead of expensive deepcopy
        env_copy = self._make_env_copy(node.state, node.step_count)
        next_state, _reward, _done, _info = env_copy.step(action)

        # Skip states already visited (MCTS-Solver inspired)
        # Use a while loop instead of recursion to avoid Python stack overflow
        # when many states are already visited.
        while next_state in self._visited_states and next_state != node.state:
            if not node.untried_actions:
                return node
            action = node.untried_actions.pop(0)
            env_copy = self._make_env_copy(node.state, node.step_count)
            next_state, _reward, _done, _info = env_copy.step(action)
        self._visited_states.add(next_state)

        child = MCTSNode(state=next_state, parent=node, action=action)
        node.children[action] = child
        return child

    def _rollout(self, node: MCTSNode, temperature: float = 1.0) -> tuple[float, str, float]:
        """Simulate a rollout, tracking the best molecule along the trajectory.

        Returns (terminal_reward, best_smiles, best_reward) where best_smiles
        is the molecule with the highest oracle score encountered at any step
        along the rollout path (including the start state).

        This max-over-trajectory tracking is critical for molecular generation:
        the ROLLOUT from a good first-step molecule (e.g. toluene, reward=0.44)
        often ADDS fragments that LOWER the reward. Without tracking the best
        intermediate, the MCTS tree undervalues high-quality one-step molecules.

        Uses lightweight env reinit instead of expensive deepcopy.
        Policy-biased sampling with temperature annealing and epsilon-greedy:
        - 'policy_biased' (default): sample from ScafVAE with temperature
        - 'random': uniform random (original)

        Parameters
        ----------
        node : MCTSNode
            Node to rollout from.
        temperature : float
            Softmax temperature for action sampling. Higher = more uniform.

        Returns
        -------
        tuple[float, str, float]
            (terminal_reward, best_smiles_along_path, best_reward_along_path)
        """
        # Lightweight env copy instead of deepcopy
        env_copy = self._make_env_copy(node.state, node.step_count)

        # Track best molecule along the rollout trajectory
        best_smiles = env_copy.state
        best_reward = self.oracle(env_copy.state)

        done = env_copy.step_count >= env_copy.max_steps or env_copy._is_terminal(env_copy.state)

        while not done:
            if self.rollout_strategy == "policy_biased" and self.policy_fn is not None:
                # Soft exploration mix: P' = (1-ε)·P_policy + ε·P_uniform
                node_priors = self._get_priors(env_copy.state)
                if node_priors:
                    actions = list(node_priors.keys())
                    log_probs = np.array([node_priors[a] for a in actions])
                    # Temperature-scaled softmax
                    log_probs = log_probs / max(temperature, 1e-8)
                    # Numerically stable softmax
                    log_probs = log_probs - np.max(log_probs)
                    policy_probs = np.exp(log_probs)
                    policy_probs = policy_probs / policy_probs.sum()
                    # Blend: (1-ε)·policy + ε·uniform
                    uniform_probs = np.ones_like(policy_probs) / len(policy_probs)
                    blended = (1.0 - self.rollout_epsilon) * policy_probs + self.rollout_epsilon * uniform_probs
                    blended = blended / blended.sum()  # renormalise
                    action = self._rng.choices(actions, weights=blended, k=1)[0]
                else:
                    action = self._rng.choice(env_copy.fragment_vocab)
            else:
                # Uniform random (original)
                action = self._rng.choice(env_copy.fragment_vocab)

            _state, _reward, done, _info = env_copy.step(action)

            # Track best molecule encountered along rollout path
            rollout_reward = self.oracle(_state)
            if rollout_reward > best_reward:
                best_reward = rollout_reward
                best_smiles = _state

        terminal_reward = self.oracle(env_copy.state)
        return terminal_reward, best_smiles, best_reward

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
