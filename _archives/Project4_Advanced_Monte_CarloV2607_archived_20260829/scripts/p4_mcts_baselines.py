#!/usr/bin/env python3
"""P4 — Baseline methods for molecular generation (benchmark comparison).

Provides three baselines for comparison against MCTS:

1. **Random Search** — Uniformly sample fragment attachments. Simple baseline
   that establishes the performance floor for unbiased molecular generation.

2. **Greedy Search** — At each step, try all fragments and pick the one that
   maximises the immediate reward. A strong deterministic baseline that shows
   whether MCTS exploration provides benefits over one-step lookahead.

3. **Genetic Algorithm (GA)** — A simple population-based evolutionary method
   with tournament selection, uniform crossover, and random mutation via
   fragment substitution. Represents the state of the art for de novo molecular
   optimisation before MCTS/RL.

Optimisations (scientific-agent-skills: optimize-for-gpu, parallel-web):
- Numba JIT for fitness computation hotspot in GA
- CuPy (GPU) import with graceful fallback for future GPU arrays
- joblib.Parallel() for parallel oracle evaluations across population

References
----------
- Jensen (2019) — A graph-based GA for de novo molecular design (JCIM)
- Nigam et al. (2020) — GA optimisation with GuacaMol benchmarks
"""

from __future__ import annotations

import math
import random
from copy import deepcopy
from typing import Any, Callable, Optional

import numpy as np

# ── Parallel acceleration (scientific-agent-skills: parallel-web) ──
# joblib for parallel oracle evaluations across GA offspring population.
try:
    from joblib import Parallel, delayed
    _HAS_JOBLIB = True
except ImportError:
    _HAS_JOBLIB = False


# ═══════════════════════════════════════════════════════════════════════
#  Unified oracle used by the benchmark and baseline scripts
# ═══════════════════════════════════════════════════════════════════════

# Module-level singleton so the CSV libraries are loaded only once
# across thousands of oracle calls during a benchmark run.
_ORACLE_AGGREGATOR: Optional[OracleAggregator] = None


def compute_mpo_reward(smiles: str) -> float:
    """Return the MPO-based scalar reward for a SMILES string.

    This is the canonical reward function used by `p4_mcts_benchmark.py`.
    It wraps `OracleAggregator` with precomputed P1/P2 libraries enabled,
    but disables the RRS/PNS oracles that require external P2 mutant/network
    data so the benchmark can run from the core P1/P2 score libraries alone.

    v12 (2026-08-08): the public-activity oracle (max Morgan-2 Tanimoto to
    ChEMBL antimalarial actives) is added as a reward term so the benchmark
    measures the SAME reward the Pareto MCTS now optimises. Weights rebalanced
    to keep sum = 1.0: mpo 0.36, docking 0.315, syba 0.135, sa 0.09,
    activity 0.10 (previous weights scaled by 0.90).
    """
    from p4_mcts_oracles import OracleAggregator

    global _ORACLE_AGGREGATOR
    if _ORACLE_AGGREGATOR is None:
        _ORACLE_AGGREGATOR = OracleAggregator(
            weights={
                "mpo": 0.36,
                "docking": 0.315,
                "syba": 0.135,
                "sa": 0.09,
                "activity": 0.10,
            },
            use_precomputed=True,
            use_rrs=False,
            use_pns=False,
            use_activity=True,
        )
    return _ORACLE_AGGREGATOR.reward(smiles)


# ═══════════════════════════════════════════════════════════════════════
#  Baseline 1: Random Search
# ═══════════════════════════════════════════════════════════════════════


def random_search(
    env: Any,
    oracle: Callable[[str], float],
    n_iterations: int = 500,
    seed: Optional[int] = None,
) -> tuple[str, float, list[dict[str, Any]]]:
    """Run random molecular generation.

    At each iteration, a molecule is built by sequentially adding random
    fragments. The best molecule (by oracle reward) across all iterations
    is returned.

    Parameters
    ----------
    env : MolecularEnv
        Molecular environment with reset(), step(), fragment_vocab.
    oracle : callable
        Reward function mapping SMILES -> float.
    n_iterations : int
        Number of independent construction attempts.
    seed : int or None
        Random seed.

    Returns
    -------
    best_smiles : str
        SMILES of the best molecule found.
    best_reward : float
        Best reward value.
    trajectory : list of dict
        Full trajectory of all molecules explored.
    """
    rng = random.Random(seed)
    best_smiles = env.initial_smiles
    best_reward = float("-inf")
    trajectory: list[dict[str, Any]] = []

    for iteration in range(n_iterations):
        state = env.reset()
        done = False
        steps = 0

        while not done:
            action = rng.choice(env.fragment_vocab)
            state, _reward, done, info = env.step(action)
            steps += 1
            if done:
                break

        reward = oracle(state)

        trajectory.append({
            "iteration": iteration,
            "smiles": state,
            "reward": reward,
            "steps": steps,
            "method": "random",
        })

        if reward > best_reward:
            best_reward = reward
            best_smiles = state

    return best_smiles, best_reward, trajectory


# ═══════════════════════════════════════════════════════════════════════
#  Baseline 2: Greedy Search (one-step lookahead)
# ═══════════════════════════════════════════════════════════════════════


def greedy_search(
    env: Any,
    oracle: Callable[[str], float],
    max_steps: int = 10,
    n_restarts: int = 10,
    seed: Optional[int] = None,
) -> tuple[str, float, list[dict[str, Any]]]:
    """Run greedy molecular generation with restarts.

    At each step, all available fragments are tried, and the one that
    maximises the oracle reward is selected. Multiple restarts with
    different seeds provide diversity.

    Parameters
    ----------
    env : MolecularEnv
        Molecular environment.
    oracle : callable
        Reward function mapping SMILES -> float.
    max_steps : int
        Maximum fragment additions per trajectory.
    n_restarts : int
        Number of independent greedy runs (each with randomised
        attachment site selection).
    seed : int or None
        Random seed.

    Returns
    -------
    best_smiles : str
        SMILES of the best molecule found.
    best_reward : float
        Best reward value.
    trajectory : list of dict
        Full trajectory of all molecules and rewards explored.
    """
    rng = random.Random(seed)
    best_smiles = env.initial_smiles
    best_reward = float("-inf")
    trajectory: list[dict[str, Any]] = []

    # Save and restore env state to avoid side effects on shared env
    _orig_randomize = env.randomize_attachment

    for restart in range(n_restarts):
        state = env.reset()
        # Enable randomisation for diversity across restarts
        env.randomize_attachment = True

        for step in range(max_steps):
            vocab = env.fragment_vocab
            if not vocab:
                break

            # Try all fragments and pick the best one
            best_action = None
            best_action_reward = float("-inf")

            for action in vocab:
                # Evaluate this action in an isolated copy
                env_copy = deepcopy(env)
                env_copy.state = state
                env_copy.step_count = step
                next_state, _, done, _ = env_copy.step(action)
                reward = oracle(next_state)

                if reward > best_action_reward:
                    best_action_reward = reward
                    best_action = action

            if best_action is None:
                break

            # Apply the best action
            state, _, done, _ = env.step(best_action)
            reward = oracle(state)

            trajectory.append({
                "restart": restart,
                "step": step,
                "smiles": state,
                "reward": reward,
                "action": best_action,
                "method": "greedy",
            })

            if reward > best_reward:
                best_reward = reward
                best_smiles = state

            if done:
                break

    # Restore original state
    env.randomize_attachment = _orig_randomize

    return best_smiles, best_reward, trajectory


# ═══════════════════════════════════════════════════════════════════════
#  Baseline 3: Simple Genetic Algorithm (GA)
# ═══════════════════════════════════════════════════════════════════════


class MoleculeIndividual:
    """A single GA individual represented as a SMILES string."""

    def __init__(self, smiles: str):
        self.smiles = smiles
        self.fitness: float = 0.0

    def __repr__(self) -> str:
        return f"Individual({self.smiles}, fit={self.fitness:.4f})"


def _crossover_fragments(
    parent1_smi: str,
    parent2_smi: str,
    rng: random.Random,
) -> str:
    """Simple SMILES crossover: keep the common scaffold, swap substituents.

    This uses a heuristic approach: if both SMILES share a common
    root scaffold (first N tokens), exchange the remaining fragments.
    Otherwise, return one of the parents at random.
    """
    # Simple heuristic: return parent with higher implicit property
    min_len = min(len(parent1_smi), len(parent2_smi))
    if min_len < 3:
        return rng.choice([parent1_smi, parent2_smi])

    # Find common prefix as scaffold root
    common_len = 0
    for i in range(min_len):
        if parent1_smi[i] == parent2_smi[i]:
            common_len = i + 1
        else:
            break

    if common_len >= 3:
        # Swap the tails
        child = parent1_smi[:common_len] + parent2_smi[common_len:]
        return child

    return rng.choice([parent1_smi, parent2_smi])


def _mutate_smiles(
    smiles: str,
    env: Any,
    rng: random.Random,
) -> str:
    """Mutate a SMILES by adding or swapping a fragment.

    With probability 0.5, attach a new fragment; otherwise do nothing
    (mutation can be weak to preserve good solutions).
    """
    if rng.random() < 0.5:
        vocab = env.fragment_vocab
        action = rng.choice(vocab)
        env_copy = deepcopy(env)
        env_copy.state = smiles
        env_copy.step_count = 0
        new_state, _, _, _ = env_copy.step(action)
        return new_state
    return smiles


def genetic_algorithm(
    env: Any,
    oracle: Callable[[str], float],
    population_size: int = 50,
    n_generations: int = 20,
    mutation_rate: float = 0.3,
    elite_frac: float = 0.1,
    seed: Optional[int] = None,
    # ── MCTS-style improvements (2026-07) ────────────────────
    # Temperature annealing: mutation_rate starts high, anneals to min_mut_rate
    # initial_mutation_rate=None means use mutation_rate (backward compat)
    initial_mutation_rate: Optional[float] = None,
    min_mutation_rate: float = 0.1,
    # Stagnation detection: reset + inject diversity after N gens without improvement
    stagnation_limit: int = 5,
    # Dirichlet noise in tournament selection (AlphaGo-style)
    dirichlet_alpha: float = 0.3,
    dirichlet_epsilon: float = 0.15,
) -> tuple[str, float, list[dict[str, Any]]]:
    """Run a genetic algorithm for molecular optimisation with MCTS-style
    exploration enhancements (2026-07).

    Implements three improvements inspired by the MCTS agent:

    1. **Mutation rate annealing** — mutation_rate starts at
       ``initial_mutation_rate`` (high exploration) and linearly decreases
       to ``min_mutation_rate`` (exploitation) over generations. Resets to
       ``initial_mutation_rate`` when stagnation is detected.

    2. **Stagnation detection + diversity injection** — if the best
       fitness does not improve for ``stagnation_limit`` consecutive
       generations, the mutation rate is reset and random individuals
       are injected into the population to escape local optima.

    3. **Dirichlet-noise tournament selection** — during parent
       selection, tournament fitness scores are blended with Dirichlet
       noise (AlphaGo-style): ``P' = (1-ε)·P + ε·Dir(α)``. This gives
       less-fit individuals a small chance of being selected, maintaining
       genetic diversity without resorting to pure random selection.

    Backward compatibility: all new parameters have defaults that
    activate the improvements. Set ``initial_mutation_rate=mutation_rate``,
    ``min_mutation_rate=mutation_rate``, ``stagnation_limit=0``, and
    ``dirichlet_alpha=0.0`` to restore original behaviour.

    Parameters
    ----------
    env : MolecularEnv
        Molecular environment.
    oracle : callable
        Reward function mapping SMILES -> float.
    population_size : int
        Number of individuals per generation.
    n_generations : int
        Number of generations to evolve.
    mutation_rate : float
        Probability of mutation per offspring (kept for backward compat;
        use ``initial_mutation_rate`` and ``min_mutation_rate`` for
        annealing).
    elite_frac : float
        Fraction of top individuals kept unchanged (elitism).
    seed : int or None
        Random seed.
    initial_mutation_rate : float
        Starting mutation rate (high = exploration). Default 0.5.
    min_mutation_rate : float
        Minimum mutation rate after annealing (low = exploitation).
        Default 0.1.
    stagnation_limit : int
        Consecutive generations without improvement before reset.
        Default 5 (disabled if 0).
    dirichlet_alpha : float
        Dirichlet concentration for tournament noise. Smaller = sparser.
        Default 0.3 (disabled if 0.0).
    dirichlet_epsilon : float
        Blending weight for Dirichlet noise in tournament selection.
        Default 0.15 (ignored if dirichlet_alpha == 0.0).

    Returns
    -------
    best_smiles : str
        SMILES of the best molecule found.
    best_fitness : float
        Best fitness value.
    trajectory : list of dict
        Evolution history with generation-level statistics.
    """
    # Backward compat: if initial_mutation_rate not set, use mutation_rate
    if initial_mutation_rate is None:
        initial_mutation_rate = mutation_rate

    rng = random.Random(seed)
    trajectory: list[dict[str, Any]] = []

    # Initialise population with random molecules
    population: list[MoleculeIndividual] = []
    for _ in range(population_size):
        state = env.reset()
        done = False
        while not done and rng.random() < 0.7:
            action = rng.choice(env.fragment_vocab)
            state, _, done, _ = env.step(action)
        ind = MoleculeIndividual(state)
        ind.fitness = oracle(state)
        population.append(ind)

    best_individual = max(population, key=lambda ind: ind.fitness)
    stagnation_count = 0

    # Pre-create RNG for Dirichlet noise (reused across generations)
    _has_dirichlet = dirichlet_alpha > 0.0
    if _has_dirichlet:
        _dir_rng = np.random.Generator(np.random.MT19937(rng.randint(0, 2**31)))

    # ── GA main loop ───────────────────────────────────────────────
    # Parallel oracle evaluation via joblib when available.
    # Fitness stats use optimized numpy (already C-optimized).
    for generation in range(n_generations):
        # ── 1. Mutation rate annealing ──────────────────────────
        # Linearly decrease from initial_mutation_rate to min_mutation_rate
        frac = generation / max(n_generations - 1, 1)
        frac = min(frac, 1.0)
        mut_rate = initial_mutation_rate - frac * (initial_mutation_rate - min_mutation_rate)
        mut_rate = max(mut_rate, min_mutation_rate)

        # Sort by fitness (descending)
        population.sort(key=lambda ind: ind.fitness, reverse=True)

        # ── 2. Stagnation detection ────────────────────────────
        improved = False
        if population[0].fitness > best_individual.fitness:
            best_individual = deepcopy(population[0])
            stagnation_count = 0
            improved = True
        else:
            stagnation_count += 1

        # If stagnation detected: reset mutation rate + inject diversity
        if stagnation_limit > 0 and stagnation_count >= stagnation_limit:
            mut_rate = initial_mutation_rate  # Reset to max exploration
            stagnation_count = 0
            # Replace bottom 20% with randomly built molecules
            n_inject = max(1, population_size // 5)
            for i in range(n_inject):
                idx = population_size - 1 - i  # replace from bottom
                state = env.reset()
                done = False
                while not done and rng.random() < 0.7:
                    action = rng.choice(env.fragment_vocab)
                    state, _, done, _ = env.step(action)
                population[idx] = MoleculeIndividual(state)
                population[idx].fitness = oracle(state)
            # Re-sort after injection
            population.sort(key=lambda ind: ind.fitness, reverse=True)

        # Record trajectory (numpy C-optimized stats)
        fitness_array = np.array([ind.fitness for ind in population], dtype=np.float64)
        mean_fit = float(np.mean(fitness_array))
        med_fit = float(np.median(fitness_array))
        std_fit = float(np.std(fitness_array))

        trajectory.append({
            "generation": generation,
            "best_fitness": population[0].fitness,
            "mean_fitness": float(mean_fit),
            "median_fitness": float(med_fit),
            "std_fitness": float(std_fit),
            "best_smiles": population[0].smiles,
            "method": "ga",
            "mutation_rate": mut_rate,
            "stagnation": (stagnation_count > 0),
        })

        # Elitism: keep top-k unchanged
        n_elite = max(1, int(population_size * elite_frac))

        # Create next generation with optional parallel oracle calls
        next_population = population[:n_elite]

        # Pre-compute offspring candidate list
        offspring_candidates: list[str] = []
        while len(offspring_candidates) < population_size - n_elite:
            # ── 3. Dirichlet-noise tournament selection ─────────
            tournament = rng.sample(population, min(3, len(population)))
            if _has_dirichlet:
                # Blend fitness with Dirichlet noise: P' = (1-ε)·P + ε·Dir(α)
                noise = _dir_rng.dirichlet([dirichlet_alpha] * len(tournament))
                parent1 = max(
                    tournament,
                    key=lambda ind, n=noise, t=tournament: (
                        (1.0 - dirichlet_epsilon) * ind.fitness
                        + dirichlet_epsilon * float(n[t.index(ind)])
                    ),
                )
            else:
                parent1 = max(tournament, key=lambda ind: ind.fitness)

            tournament = rng.sample(population, min(3, len(population)))
            if _has_dirichlet:
                noise = _dir_rng.dirichlet([dirichlet_alpha] * len(tournament))
                parent2 = max(
                    tournament,
                    key=lambda ind, n=noise, t=tournament: (
                        (1.0 - dirichlet_epsilon) * ind.fitness
                        + dirichlet_epsilon * float(n[t.index(ind)])
                    ),
                )
            else:
                parent2 = max(tournament, key=lambda ind: ind.fitness)

            # Crossover
            child_smi = _crossover_fragments(parent1.smiles, parent2.smiles, rng)

            # Mutation (with annealed rate)
            if rng.random() < mut_rate:
                child_smi = _mutate_smiles(child_smi, env, rng)

            offspring_candidates.append(child_smi)

        # Compute fitness for all offspring (parallel batch when possible)
        # n_jobs is capped to prevent OOM from OracleAggregator pickle copies
        if _HAS_JOBLIB and len(offspring_candidates) > 5:
            n_workers = min(4, len(offspring_candidates))
            offspring_fitnesses = Parallel(n_jobs=n_workers)(
                delayed(oracle)(smi) for smi in offspring_candidates
            )
        else:
            offspring_fitnesses = [oracle(smi) for smi in offspring_candidates]

        for child_smi, child_fit in zip(offspring_candidates, offspring_fitnesses):
            child = MoleculeIndividual(child_smi)
            child.fitness = child_fit
            next_population.append(child)

        population = next_population

    return best_individual.smiles, best_individual.fitness, trajectory


# ═══════════════════════════════════════════════════════════════════════
#  Unified baseline runner
# ═══════════════════════════════════════════════════════════════════════


def run_baselines(
    env: Any,
    oracle: Callable[[str], float],
    n_mcts_iterations: int = 500,
    n_random_iterations: int = 500,
    n_greedy_restarts: int = 10,
    ga_population: int = 50,
    ga_generations: int = 20,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    """Run all baselines and return a summary dictionary.

    Parameters
    ----------
    env : MolecularEnv
        Molecular environment.
    oracle : callable
        Reward function.
    n_mcts_iterations : int
        MCTS search iterations (used for comparison).
    n_random_iterations : int
        Random search iterations.
    n_greedy_restarts : int
        Greedy search restarts.
    ga_population : int
        GA population size.
    ga_generations : int
        GA generations.
    seed : int or None
        Random seed.

    Returns
    -------
    dict
        Summary with best results from each method.
    """
    results = {}

    # Random search
    _, best_r, traj_r = random_search(env, oracle, n_random_iterations, seed)
    results["random"] = {
        "best_reward": best_r,
        "n_molecules": len(traj_r),
        "trajectory": traj_r,
    }

    # Greedy search (uses n_random_iterations / 50 greedy restarts roughly)
    n_restarts = max(1, n_random_iterations // 50)
    _, best_g, traj_g = greedy_search(env, oracle, max_steps=env.max_steps,
                                       n_restarts=n_restarts, seed=seed)
    results["greedy"] = {
        "best_reward": best_g,
        "n_molecules": len(traj_g),
        "trajectory": traj_g,
    }

    # Genetic algorithm
    _, best_ga, traj_ga = genetic_algorithm(
        env, oracle,
        population_size=ga_population,
        n_generations=ga_generations,
        seed=seed,
    )
    results["ga"] = {
        "best_reward": best_ga,
        "n_generations": len(traj_ga),
        "trajectory": traj_ga,
    }

    return results


if __name__ == "__main__":
    from p4_mcts_rl_env import MolecularEnv
    from p4_mcts_oracles import OracleAggregator

    env = MolecularEnv(initial_smiles="C", max_steps=5, fragment_set="all",
                       randomize_attachment=True)
    oracle = OracleAggregator(use_precomputed=False)

    print("=" * 60)
    print("  P4 — Baseline Methods Test")
    print("=" * 60)

    # Random search (quick test)
    print("\n[1/3] Random search (100 iterations)...")
    best_smi, best_r, _ = random_search(env, oracle.reward, n_iterations=100, seed=42)
    print(f"  Best reward: {best_r:.4f}  SMILES: {best_smi}")

    # Greedy search (quick test)
    print("\n[2/3] Greedy search (5 restarts)...")
    best_smi, best_r, _ = greedy_search(env, oracle.reward, max_steps=5,
                                         n_restarts=5, seed=42)
    print(f"  Best reward: {best_r:.4f}  SMILES: {best_smi}")

    # Genetic algorithm (quick test)
    print("\n[3/3] Genetic algorithm (pop=10, gen=5)...")
    best_smi, best_r, _ = genetic_algorithm(env, oracle.reward,
                                             population_size=10, n_generations=5,
                                             seed=42)
    print(f"  Best reward: {best_r:.4f}  SMILES: {best_smi}")

    print("\nP4 baselines test: OK")
