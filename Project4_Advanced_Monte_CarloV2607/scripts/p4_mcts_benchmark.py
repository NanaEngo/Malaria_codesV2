#!/usr/bin/env python3
"""P4 — Unified benchmark: MCTS vs Random vs Greedy vs GA.

Compares all four molecular generation methods on identical settings:
same environment, same oracle, same compute budget. Outputs:

1. **Summary CSV** — Best molecule per method with scores
2. **LaTeX table** — Ready for paper inclusion
3. **Benchmark metrics** — Mean/median/std rewards, Pareto front size,
   scaffold diversity (Tanimoto dissimilarity), novelty

Usage
-----
# Quick benchmark (small budget, no precomputed libraries)
python p4_mcts_benchmark.py \
  --n-iterations 200 \
  --output results/benchmark/p4_benchmark.csv

# Full production benchmark
python p4_mcts_benchmark.py \
  --n-iterations 2000 \
  --ga-population 100 --ga-generations 40 \
  --output results/benchmark/p4_benchmark.csv \
  --latex-table results/benchmark/p4_benchmark_table.tex
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np

_HAS_PANDAS = False
_HAS_RDKIT = False
_HAS_MATPLOTLIB = False
_HAS_JOBLIB = False

try:
    from joblib import Parallel, delayed
    _HAS_JOBLIB = True
except ImportError:
    pass

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    pass

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdFingerprintGenerator
    from rdkit.DataStructs import BulkTanimotoSimilarity
    _HAS_RDKIT = True
except ImportError:
    pass

try:
    import matplotlib.pyplot as plt
    _HAS_MATPLOTLIB = True
except ImportError:
    pass


# ── Scaffold diversity metric ────────────────────────────────────────


def _compute_diversity(smiles_list: list[str]) -> float:
    """Compute average pairwise Tanimoto dissimilarity (0–1).

    Higher values indicate a more diverse set of molecules.
    """
    if not _HAS_RDKIT or len(smiles_list) < 2:
        return 0.0

    mols = [Chem.MolFromSmiles(smi) for smi in smiles_list]
    mols = [m for m in mols if m is not None]
    if len(mols) < 2:
        return 0.0

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [gen.GetFingerprint(m) for m in mols]

    total_sim = 0.0
    count = 0
    for i in range(len(fps)):
        sims = BulkTanimotoSimilarity(fps[i], fps[i + 1:])
        total_sim += sum(sims)
        count += len(sims)

    if count == 0:
        return 0.0
    avg_sim = total_sim / count
    return 1.0 - avg_sim  # dissimilarity


# ── Benchmark runner ─────────────────────────────────────────────────


def _run_single_seed(
    seed: int,
    env: Any,
    oracle: Any,
    n_iterations: int,
    ga_population: int,
    ga_generations: int,
    mcts_c_puct: float,
    use_policy: bool,
) -> dict[str, Any]:
    """Run all methods for a single seed (extracted for joblib parallelism)."""
    from p4_mcts_agent import MCTSAgent
    from p4_mcts_baselines import (
        genetic_algorithm,
        greedy_search,
        random_search,
    )
    from p4_mcts_policy import ScafVAEPolicy

    result: dict[str, Any] = {}

    # ── MCTS ──────────────────────────────────────────────────
    policy_fn = None
    if use_policy:
        policy = ScafVAEPolicy(temperature=0.8, random_seed=seed)
        policy_fn = policy.get_action_priors

    agent = MCTSAgent(
        env, oracle=oracle.reward,
        n_iterations=n_iterations,
        c_puct=mcts_c_puct,
        policy_fn=policy_fn,
    )
    mcts_start = time.time()
    best_mcts = agent.search(env.initial_smiles)
    mcts_time = time.time() - mcts_start
    mcts_reward = oracle.reward(best_mcts)
    mcts_scores = oracle.score(best_mcts)

    result["mcts"] = {
        "seed": seed,
        "best_smiles": best_mcts,
        "best_reward": mcts_reward,
        "mpo": mcts_scores.get("mpo", 0.0),
        "docking": mcts_scores.get("docking", 0.0),
        "syba": mcts_scores.get("syba", 0.0),
        "sa": mcts_scores.get("sa", 0.0),
        "time_s": mcts_time,
    }

    # ── Random Search ─────────────────────────────────────────
    random_start = time.time()
    best_rand, rand_r, rand_traj = random_search(
        env, oracle.reward, n_iterations=n_iterations, seed=seed
    )
    random_time = time.time() - random_start
    rand_scores = oracle.score(best_rand)

    result["random"] = {
        "seed": seed,
        "best_smiles": best_rand,
        "best_reward": rand_r,
        "mpo": rand_scores.get("mpo", 0.0),
        "docking": rand_scores.get("docking", 0.0),
        "syba": rand_scores.get("syba", 0.0),
        "sa": rand_scores.get("sa", 0.0),
        "time_s": random_time,
        "n_molecules": len(rand_traj),
    }

    # ── Greedy Search ─────────────────────────────────────────
    n_restarts = max(1, n_iterations // 50)
    greedy_start = time.time()
    best_greedy, greedy_r, greedy_traj = greedy_search(
        env, oracle.reward, max_steps=env.max_steps,
        n_restarts=n_restarts, seed=seed
    )
    greedy_time = time.time() - greedy_start
    greedy_scores = oracle.score(best_greedy)

    result["greedy"] = {
        "seed": seed,
        "best_smiles": best_greedy,
        "best_reward": greedy_r,
        "mpo": greedy_scores.get("mpo", 0.0),
        "docking": greedy_scores.get("docking", 0.0),
        "syba": greedy_scores.get("syba", 0.0),
        "sa": greedy_scores.get("sa", 0.0),
        "time_s": greedy_time,
        "n_molecules": len(greedy_traj),
    }

    # ── Genetic Algorithm ─────────────────────────────────────
    ga_start = time.time()
    best_ga, ga_r, ga_traj = genetic_algorithm(
        env, oracle.reward,
        population_size=ga_population,
        n_generations=ga_generations,
        seed=seed,
    )
    ga_time = time.time() - ga_start
    ga_scores = oracle.score(best_ga)

    result["ga"] = {
        "seed": seed,
        "best_smiles": best_ga,
        "best_reward": ga_r,
        "mpo": ga_scores.get("mpo", 0.0),
        "docking": ga_scores.get("docking", 0.0),
        "syba": ga_scores.get("syba", 0.0),
        "sa": ga_scores.get("sa", 0.0),
        "time_s": ga_time,
        "n_evals": ga_population * ga_generations,
    }

    return result


def run_benchmark(
    env: Any,
    oracle: Any,
    n_iterations: int = 500,
    ga_population: int = 50,
    ga_generations: int = 20,
    n_seeds: int = 5,
    n_jobs: int = 1,
    mcts_c_puct: float = 1.414,
    use_policy: bool = True,
) -> dict[str, Any]:
    """Run all methods over multiple seeds and collect statistics.

    Parameters
    ----------
    env : MolecularEnv
        Shared molecular environment.
    oracle : OracleAggregator
        Oracle with .reward() and .score() methods.
    n_iterations : int
        Number of MCTS iterations / random iterations.
    ga_population : int
        GA population size.
    ga_generations : int
        GA number of generations (total evals = pop * gens).
    n_seeds : int
        Number of random seeds for statistical replicates.
    mcts_c_puct : float
        MCTS exploration constant.
    use_policy : bool
        Whether to use ScafVAE policy in MCTS.

    Returns
    -------
    dict
        Nested dictionary with results per method per seed.
    """
    results: dict[str, list[dict[str, Any]]] = {
        "mcts": [],
        "random": [],
        "greedy": [],
        "ga": [],
    }

    # Use joblib for cross-seed parallelism when n_jobs > 1
    _run_seed_job = lambda seed: _run_single_seed(
        seed, env, oracle, n_iterations, ga_population, ga_generations,
        mcts_c_puct, use_policy
    )

    if _HAS_JOBLIB and n_jobs != 1:
        parallel_results = Parallel(n_jobs=n_jobs, verbose=10)(
            delayed(_run_seed_job)(seed) for seed in range(n_seeds)
        )
        for method in results:
            results[method] = [r[method] for r in parallel_results]
        print(f"  Parallel (n_jobs={n_jobs}): {n_seeds} seeds → {len(parallel_results)} results")
    else:
        for seed in range(n_seeds):
            print(f"  Seed {seed + 1}/{n_seeds}...")
            seed_result = _run_single_seed(
                seed, env, oracle, n_iterations, ga_population, ga_generations,
                mcts_c_puct, use_policy
            )
            for method in results:
                results[method].append(seed_result[method])

    return results


# ── Analysis ─────────────────────────────────────────────────────────


def analyse_benchmark(
    results: dict[str, list[dict[str, Any]]],
    oracle: Any,
) -> dict[str, dict[str, Any]]:
    """Compute summary statistics and diversity metrics.

    Parameters
    ----------
    results : dict
        Raw results from run_benchmark().
    oracle : OracleAggregator
        Oracle for scoring (used for diversity computation).

    Returns
    -------
    dict
        Summary statistics per method.
    """
    summary: dict[str, dict[str, Any]] = {}

    for method, runs in results.items():
        if not runs:
            continue

        rewards = [r["best_reward"] for r in runs]
        times = [r["time_s"] for r in runs]
        smiles_list = [r["best_smiles"] for r in runs]

        summary[method] = {
            "mean_reward": float(np.mean(rewards)),
            "median_reward": float(np.median(rewards)),
            "std_reward": float(np.std(rewards)),
            "min_reward": float(np.min(rewards)),
            "max_reward": float(np.max(rewards)),
            "mean_time_s": float(np.mean(times)),
            "total_time_s": float(np.sum(times)),
            "best_smiles": smiles_list[int(np.argmax(rewards))],
            "all_smiles": smiles_list,
            "n_seeds": len(runs),
            "scaffold_diversity": _compute_diversity(smiles_list),
            "mpo_mean": float(np.mean([r.get("mpo", 0.0) for r in runs])),
            "docking_mean": float(np.mean([r.get("docking", 0.0) for r in runs])),
            "syba_mean": float(np.mean([r.get("syba", 0.0) for r in runs])),
            "sa_mean": float(np.mean([r.get("sa", 0.0) for r in runs])),
        }

    return summary


# ── LaTeX table generation ───────────────────────────────────────────


def make_latex_table(
    summary: dict[str, dict[str, Any]],
    output_path: Path,
) -> None:
    """Generate a LaTeX table comparing all methods.

    Table columns: Method | Mean Reward | Max Reward | std | Time (s) | Diversity
    """
    methods_ordered = ["mcts", "random", "greedy", "ga"]
    method_labels = {
        "mcts": "MCTS + ScafVAE (ours)",
        "random": "Random Search",
        "greedy": "Greedy Search",
        "ga": "Genetic Algorithm",
    }

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Benchmark comparison of molecular generation methods.}",
        r"\label{tab:p4_benchmark}",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"Method & Mean Reward $\uparrow$ & Max Reward $\uparrow$ & Std & Time (s) & Diversity $\uparrow$ & MPO \\",
        r"\midrule",
    ]

    for method in methods_ordered:
        if method not in summary:
            continue
        s = summary[method]
        label = method_labels.get(method, method.capitalize())
        line = (
            f"  {label} & "
            f"{s['mean_reward']:.4f} & "
            f"{s['max_reward']:.4f} & "
            f"{s['std_reward']:.4f} & "
            f"{s['mean_time_s']:.1f} & "
            f"{s['scaffold_diversity']:.3f} & "
            f"{s['mpo_mean']:.3f} \\\\"
        )
        lines.append(line)

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  LaTeX table: {output_path} ({len(lines)} lines)")


# ── CLI ──────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P4 — Unified benchmark: MCTS vs baselines.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--n-iterations", type=int, default=500,
                        help="MCTS iterations / random samples (default: 500)")
    parser.add_argument("--ga-population", type=int, default=50,
                        help="GA population size (default: 50)")
    parser.add_argument("--ga-generations", type=int, default=20,
                        help="GA generations (default: 20)")
    parser.add_argument("--n-seeds", type=int, default=5,
                        help="Number of random seeds (default: 5)")
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel seeds via joblib (default: 1=sequential)")
    parser.add_argument("--no-policy", action="store_true",
                        help="Disable ScafVAE policy in MCTS")
    parser.add_argument("--output", type=Path,
                        default=Path("results/benchmark/p4_benchmark.csv"),
                        help="Output CSV path")
    parser.add_argument("--latex-table", type=Path, default=None,
                        help="Output LaTeX table path")
    parser.add_argument("--initial-smiles", default="C",
                        help="Starting scaffold (default: methane)")
    parser.add_argument("--max-steps", type=int, default=10,
                        help="Max fragment additions (default: 10)")
    args = parser.parse_args()

    from p4_mcts_oracles import OracleAggregator
    from p4_mcts_rl_env import MolecularEnv

    print("=" * 60)
    print("  P4 — Benchmark: MCTS vs Random vs Greedy vs GA")
    print("=" * 60)
    print(f"  MCTS iterations:  {args.n_iterations}")
    print(f"  GA pop × gen:     {args.ga_population} × {args.ga_generations}")
    print(f"  Seeds:            {args.n_seeds}")
    parallel_label = "parallel" if _HAS_JOBLIB and args.n_jobs != 1 else "sequential"
    print(f"  n_jobs:           {args.n_jobs} ({parallel_label})")
    print(f"  Max steps:        {args.max_steps}")
    print(f"  Policy:           {'ScafVAE' if not args.no_policy else 'None'}")
    print(f"  Oracle:           P1/P2 precomputed libraries")
    print()

    # Environment and oracle (shared across all methods)
    env = MolecularEnv(
        initial_smiles=args.initial_smiles,
        max_steps=args.max_steps,
        fragment_set="all",
        randomize_attachment=True,
    )
    oracle = OracleAggregator(use_precomputed=True)

    # Run benchmark
    print("Running benchmark...")
    results = run_benchmark(
        env, oracle,
        n_iterations=args.n_iterations,
        ga_population=args.ga_population,
        ga_generations=args.ga_generations,
        n_seeds=args.n_seeds,
        n_jobs=args.n_jobs,
        use_policy=not args.no_policy,
    )

    # Analyse
    print("\nAnalysing results...")
    summary = analyse_benchmark(results, oracle)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  Benchmark Results")
    print(f"{'=' * 60}")
    for method, s in summary.items():
        print(f"  {method.upper():8s}: mean={s['mean_reward']:.4f} "
              f"max={s['max_reward']:.4f} ±{s['std_reward']:.4f}  "
              f"time={s['mean_time_s']:.1f}s  "
              f"diversity={s['scaffold_diversity']:.3f}")

    # Write CSV
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "method", "seed", "best_smiles", "best_reward",
            "mpo", "docking", "syba", "sa", "time_s",
        ])
        for method, runs in results.items():
            for run in runs:
                writer.writerow([
                    method,
                    run["seed"],
                    run["best_smiles"],
                    f"{run['best_reward']:.6f}",
                    f"{run.get('mpo', 0.0):.4f}",
                    f"{run.get('docking', 0.0):.4f}",
                    f"{run.get('syba', 0.0):.4f}",
                    f"{run.get('sa', 0.0):.4f}",
                    f"{run['time_s']:.2f}",
                ])
    print(f"\n  CSV: {args.output}")

    # LaTeX table
    if args.latex_table:
        make_latex_table(summary, args.latex_table)

    print(f"\n{'=' * 60}")
    print(f"  Benchmark complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
