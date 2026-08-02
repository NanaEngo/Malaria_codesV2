#!/usr/bin/env python3
"""P4 — MCTS Hyperparameter Search.

Grid search over MCTS hyperparameters to find optimal settings.
Evaluates each configuration on a small benchmark (50 iterations, 3 seeds)
and reports mean reward, diversity, and exploration metrics.

Usage
-----
# Quick local search (small grid, 1 seed)
python p4_mcts_hparam_search.py --quick

# Full grid search (SLURM)
python p4_mcts_hparam_search.py \
  --n-seeds 3 --n-iterations 50 \
  --output results/hparam_search.csv

# Individual task for SLURM array
python p4_mcts_hparam_search.py --task-id $SLURM_ARRAY_TASK_ID
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np


# ── Default search grid ──────────────────────────────────────────────
# Each key is a parameter name, each value is a list of candidate values.
DEFAULT_GRID: dict[str, list[float]] = {
    "pw_alpha":       [0.3, 0.5, 0.7],
    "pw_k":           [0.5, 1.0, 2.0],
    "virtual_loss":   [0.01, 0.05, 0.1, 0.2],
    "c_puct":         [0.5, 1.414, 3.0, 5.0],
    "temperature":    [0.5, 0.8, 1.0],
}

# Quick grid for testing (covers extreme values only)
QUICK_GRID: dict[str, list[float]] = {
    "pw_alpha":       [0.3, 0.7],
    "pw_k":           [0.5, 2.0],
    "virtual_loss":   [0.01, 0.2],
    "c_puct":         [0.5, 5.0],
    "temperature":    [0.5, 1.0],
}


def _parse_grid(grid_dict: dict[str, list[float]]) -> list[dict[str, float]]:
    """Convert parameter grid dict into a list of all combinations."""
    keys = list(grid_dict.keys())
    values = list(grid_dict.values())
    combinations = list(itertools.product(*values))
    return [dict(zip(keys, combo)) for combo in combinations]


def _evaluate_config(
    params: dict[str, float],
    seed: int,
    n_iterations: int = 50,
    max_steps: int = 5,
) -> dict[str, Any]:
    """Run MCTS with given hyperparameters and return metrics.

    Parameters
    ----------
    params : dict
        Hyperparameter values (pw_alpha, pw_k, virtual_loss, c_puct, temperature).
    seed : int
        Random seed for reproducibility.
    n_iterations : int
        Number of MCTS iterations.
    max_steps : int
        Maximum fragment additions.

    Returns
    -------
    dict
        Evaluation metrics: reward, diversity, exploration depth, visited states.
    """
    from p4_mcts_agent import MCTSAgent
    from p4_mcts_oracles import OracleAggregator
    from p4_mcts_policy import ScafVAEPolicy
    from p4_mcts_rl_env import MolecularEnv

    # ── Environment ──────────────────────────────────────────────
    env = MolecularEnv(
        initial_smiles="C",
        max_steps=max_steps,
        fragment_set="all",
        randomize_attachment=True,
        seed=seed,
    )

    # ── Oracle (no precomputed libraries for speed) ──────────────
    oracle = OracleAggregator(
        use_precomputed=False,
        use_rrs=False,
        use_pns=False,
    )

    # ── Policy ──────────────────────────────────────────────────
    policy = ScafVAEPolicy(
        temperature=params.get("temperature", 0.8),
        random_seed=seed,
    )

    # ── MCTS Agent ──────────────────────────────────────────────
    agent = MCTSAgent(
        env,
        oracle=oracle.reward,
        n_iterations=n_iterations,
        c_puct=params.get("c_puct", 1.414),
        policy_fn=policy.get_action_priors,
        seed=seed,
        pw_alpha=params.get("pw_alpha", 0.5),
        pw_k=params.get("pw_k", 1.0),
        virtual_loss=params.get("virtual_loss", 0.05),
    )

    # ── Run search ──────────────────────────────────────────────
    start_time = time.time()
    best_state = agent.search("C")
    elapsed = time.time() - start_time

    best_reward = oracle.reward(best_state)

    # ── Metrics ─────────────────────────────────────────────────
    # Exploration: number of unique states visited
    n_visited = len(agent._visited_states)

    # Diversity: number of distinct child SMILES
    root = getattr(agent, '_root', None)
    # Depth: max step count reached via most-visited path
    depth = 0
    if root and root.children:
        node = root
        while node and node.children:
            best = max(node.children.values(), key=lambda c: c.visits)
            depth += 1
            node = best

    return {
        "pw_alpha": params["pw_alpha"],
        "pw_k": params["pw_k"],
        "virtual_loss": params["virtual_loss"],
        "c_puct": params["c_puct"],
        "temperature": params["temperature"],
        "seed": seed,
        "best_reward": best_reward,
        "n_visited": n_visited,
        "depth": depth,
        "time_s": round(elapsed, 2),
        "best_smiles": best_state,
    }


def run_grid_search(
    grid: list[dict[str, float]],
    n_seeds: int = 3,
    n_iterations: int = 50,
    max_steps: int = 5,
    n_jobs: int = 1,
) -> list[dict[str, Any]]:
    """Run grid search over all parameter combinations.

    Parameters
    ----------
    grid : list[dict]
        List of hyperparameter configurations to evaluate.
    n_seeds : int
        Number of random seeds per configuration.
    n_iterations : int
        Number of MCTS iterations per evaluation.
    n_jobs : int
        Number of parallel tasks (1 = sequential).

    Returns
    -------
    list[dict]
        List of evaluation results, one per (config, seed) combination.
    """
    all_results: list[dict[str, Any]] = []

    total_tasks = len(grid) * n_seeds
    task_idx = 0

    for params in grid:
        for seed in range(n_seeds):
            task_idx += 1
            print(f"  [{task_idx}/{total_tasks}] pw_a={params['pw_alpha']} "
                  f"pw_k={params['pw_k']} vl={params['virtual_loss']} "
                  f"cp={params['c_puct']} T={params['temperature']} "
                  f"seed={seed}...", end=" ")

            result = _evaluate_config(params, seed, n_iterations, max_steps)
            all_results.append(result)

            print(f"reward={result['best_reward']:.4f} "
                  f"visited={result['n_visited']} depth={result['depth']}")

    return all_results


def print_summary(results: list[dict[str, Any]]) -> None:
    """Print a summary table grouped by hyperparameter configuration.

    Groups results by (pw_alpha, pw_k, virtual_loss, c_puct, temperature)
    and reports mean reward, std, visited states, and depth across seeds.
    """
    from collections import defaultdict

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in results:
        key = (r["pw_alpha"], r["pw_k"], r["virtual_loss"],
               r["c_puct"], r["temperature"])
        grouped[str(key)].append(r)

    # Sort by mean reward (descending)
    scored: list[tuple[float, str, list[dict]]] = []
    for key_str, runs in grouped.items():
        rewards = [r["best_reward"] for r in runs]
        mean_r = float(np.mean(rewards))
        scored.append((mean_r, key_str, runs))
    scored.sort(reverse=True)

    # Print header
    print(f"\n{'=' * 100}")
    print(f"  MCTS Hyperparameter Search Results (sorted by mean reward)")
    print(f"{'=' * 100}")
    print(f"  {'Rank':<5} {'pw_a':<6} {'pw_k':<6} {'VL':<6} {'c_puct':<8} "
          f"{'Temp':<6} {'Mean Rew':<9} {'Std':<6} {'Visited':<8} {'Depth':<6} {'Time':<7}")
    print(f"  {'-' * 55}")

    for rank, (mean_r, key_str, runs) in enumerate(scored, 1):
        rewards = [r["best_reward"] for r in runs]
        visited = [r["n_visited"] for r in runs]
        depths = [r["depth"] for r in runs]
        times = [r["time_s"] for r in runs]
        std_r = float(np.std(rewards))

        # Extract params from first run
        r0 = runs[0]
        print(f"  {rank:<5} {r0['pw_alpha']:<6.1f} {r0['pw_k']:<6.1f} "
              f"{r0['virtual_loss']:<6.2f} {r0['c_puct']:<8.1f} "
              f"{r0['temperature']:<6.1f} {mean_r:<9.4f} {std_r:<6.4f} "
              f"{np.mean(visited):<8.1f} {np.mean(depths):<6.1f} {np.mean(times):<7.1f}")

    # Best config
    best = scored[0]
    r0 = best[2][0]
    print(f"\n  ** Best config: pw_alpha={r0['pw_alpha']}, pw_k={r0['pw_k']}, "
          f"virtual_loss={r0['virtual_loss']}, c_puct={r0['c_puct']}, "
          f"temperature={r0['temperature']} **")
    print(f"     Mean reward: {best[0]:.4f} over {len(best[2])} seeds")
    print(f"{'=' * 100}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P4 — MCTS Hyperparameter Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--quick", action="store_true",
                        help="Use small grid for testing")
    parser.add_argument("--n-seeds", type=int, default=3,
                        help="Number of seeds per config (default: 3)")
    parser.add_argument("--n-iterations", type=int, default=50,
                        help="MCTS iterations per config (default: 50)")
    parser.add_argument("--max-steps", type=int, default=5,
                        help="Max fragment additions (default: 5)")
    parser.add_argument("--output", type=Path,
                        default=Path("results/hparam_search.csv"),
                        help="Output CSV path")
    parser.add_argument("--task-id", type=int, default=None,
                        help="Single task ID (for SLURM array)")
    args = parser.parse_args()

    # Build grid
    grid_dict = QUICK_GRID if args.quick else DEFAULT_GRID
    grid = _parse_grid(grid_dict)

    print(f"{'=' * 60}")
    print(f"  P4 — MCTS Hyperparameter Search")
    print(f"{'=' * 60}")
    total_evals = len(grid) * args.n_seeds
    est_time = total_evals * args.n_iterations * 0.6  # ~0.6s per iteration per eval
    print(f"  Grid size:      {len(grid)} configurations")
    print(f"  Seeds/config:   {args.n_seeds}")
    print(f"  Total evals:    {total_evals}")
    print(f"  Est. time:      ~{est_time:.0f}s ({est_time/60:.1f} min)")
    print(f"  Iterations:     {args.n_iterations}")
    print(f"  Max steps:      {args.max_steps}")
    print(f"  Parameters:     {list(grid_dict.keys())}")
    if total_evals > 100:
        print(f"  ** WARNING: Large grid ({total_evals} evals). "
              f"Consider --n-seeds 1 or --quick first. **")
    print()

    if args.task_id is not None:
        # Single task mode (SLURM array)
        # task_id indexes into (config_index, seed) pairs
        total_tasks = len(grid) * args.n_seeds
        if args.task_id >= total_tasks:
            print(f"Error: task_id {args.task_id} >= total tasks {total_tasks}")
            sys.exit(1)
        task_config = args.task_id // args.n_seeds
        task_seed = args.task_id % args.n_seeds
        params = grid[task_config]
        result = _evaluate_config(params, task_seed, args.n_iterations, args.max_steps)
        print(f"  Config {task_config}, seed {task_seed}: reward={result['best_reward']:.4f} "
              f"visited={result['n_visited']} depth={result['depth']}")
        # Save single result
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(result.keys()))
            w.writeheader()
            w.writerow(result)
    else:
        # Full grid search (sequential)
        results = run_grid_search(
            grid, n_seeds=args.n_seeds,
            n_iterations=args.n_iterations,
            max_steps=args.max_steps,
        )

        # Print summary
        print_summary(results)

        # Save CSV
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            if results:
                w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
                w.writeheader()
                w.writerows(results)
        print(f"  Results saved: {args.output}")


if __name__ == "__main__":
    main()
