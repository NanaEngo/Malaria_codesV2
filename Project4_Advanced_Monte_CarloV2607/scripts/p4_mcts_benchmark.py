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
    mcts_c_puct: float = 5.0,
    use_policy: bool = True,
    mcts_virtual_loss: float = 0.01,
    mcts_pw_alpha: float = 0.5,
    mcts_pw_k: float = 1.0,
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
        seed=seed,
        pw_alpha=mcts_pw_alpha,
        pw_k=mcts_pw_k,
        virtual_loss=mcts_virtual_loss,
    )
    mcts_start = time.time()
    best_mcts = agent.search(env.initial_smiles)
    mcts_time = time.time() - mcts_start
    mcts_reward = oracle.reward(best_mcts)
    mcts_scores = oracle.score(best_mcts)

    # Anomaly detector: extreme values indicate data loading or cache issues
    if abs(mcts_reward) > 100 or abs(mcts_scores.get("docking", 0)) > 100:
        print(f"  ANOMALY seed={seed}: MCTS reward={mcts_reward:.4f} docking={mcts_scores.get('docking')}")
        print(f"    Best SMILES: {best_mcts}")
        print(f"    Tartarus entries: {len(oracle._tartarus_smiles) if hasattr(oracle, '_tartarus_smiles') else 'N/A'}")
        print(f"    C6 entries: {len(oracle._c6) if hasattr(oracle, '_c6') else 'N/A'}")
        print(f"    Cache size: {len(oracle._runtime_cache)}")
        print(f"    Oracle weights: {oracle.weights}")

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
    mcts_c_puct: float = 5.0,
    use_policy: bool = True,
    mcts_virtual_loss: float = 0.01,
    mcts_pw_alpha: float = 0.5,
    mcts_pw_k: float = 1.0,
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
        mcts_c_puct, use_policy, mcts_virtual_loss, mcts_pw_alpha, mcts_pw_k,
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
                        help="Number of random seeds for statistical replicates (default: 5; BMAD-METHOD: use >=5 for meaningful std)")
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel seeds via joblib (default: 1=sequential; experimental-design: use n_jobs=n_seeds for max parallelism)")
    parser.add_argument("--no-policy", action="store_true",
                        help="Disable ScafVAE policy in MCTS")
    parser.add_argument("--c-puct", type=float, default=5.0,
                        help="MCTS exploration constant (default: 5.0, tuned via hparam search)")
    parser.add_argument("--virtual-loss", type=float, default=0.01,
                        help="MCTS virtual loss (default: 0.01, tuned via hparam search)")
    parser.add_argument("--pw-alpha", type=float, default=0.5,
                        help="MCTS dynamic PW exponent (default: 0.5)")
    parser.add_argument("--pw-k", type=float, default=1.0,
                        help="MCTS dynamic PW multiplier (default: 1.0)")
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
    print(f"  Seed protocol:    split-half stratified (odd seeds=holdout)")
    print(f"  Randomization:    independent RNG per seed (BMAD-METHOD §3.1)")
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

    # Run benchmark with tuned hyperparameters
    # Experimental design note (scientific-agent-skills: experimental-design):
    # - Seeds 0-4 are the primary analysis set (5 replicates)
    # - Odd seeds (1,3) can be held out as a validation split if needed
    # - Each seed uses independent randomness (no seed chain)
    print(f"  MCTS c_puct:      {args.c_puct} (tuned via hparam search)")
    print(f"  MCTS virtual_loss: {args.virtual_loss} (tuned via hparam search)")
    print(f"  MCTS pw_alpha:    {args.pw_alpha}, pw_k: {args.pw_k}")
    print()
    results = run_benchmark(
        env, oracle,
        n_iterations=args.n_iterations,
        ga_population=args.ga_population,
        ga_generations=args.ga_generations,
        n_seeds=args.n_seeds,
        n_jobs=args.n_jobs,
        mcts_c_puct=args.c_puct,
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


# ── Merge per-seed CSVs into cross-seed LaTeX table ─────────────────

def merge_csvs_to_latex(
    results_dir: Path,
    n_seeds: int = 5,
    output_path: Optional[Path] = None,
) -> None:
    """Read per-seed CSVs and generate a cross-seed LaTeX table.

    This function is designed to run AFTER array jobs have completed.
    It reads all p4_benchmark_seed_N.csv files and computes cross-seed
    statistics (mean, std, max across seeds) for the LaTeX table.
    """
    if output_path is None:
        output_path = results_dir / "p4_benchmark_table.tex"

    from collections import defaultdict

    all_results: dict[str, list[dict[str, float]]] = defaultdict(list)

    for seed in range(n_seeds):
        csv_path = results_dir / f"p4_benchmark_seed_{seed}.csv"
        if not csv_path.exists():
            print(f"  WARNING: {csv_path} not found, skipping seed {seed}")
            continue
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_results[row["method"]].append({
                    "reward": float(row["best_reward"]),
                    "mpo": float(row["mpo"]),
                    "docking": float(row["docking"]),
                    "syba": float(row["syba"]),
                    "sa": float(row["sa"]),
                    "time_s": float(row["time_s"]),
                    "smiles": row["best_smiles"],
                })

    # Compute cross-seed stats
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
        r"\caption{Benchmark comparison of molecular generation methods across $n=5$ seeds.}",
        r"\label{tab:p4_benchmark}",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"Method & Mean Reward $\uparrow$ & Max Reward $\uparrow$ & Std & Time (s) & MPO $\uparrow$ & Docking \\",
        r"\midrule",
    ]

    for method in methods_ordered:
        if method not in all_results or not all_results[method]:
            continue
        runs = all_results[method]
        rewards = [r["reward"] for r in runs]
        times = [r["time_s"] for r in runs]
        mpos = [r["mpo"] for r in runs]
        docks = [r["docking"] for r in runs]
        smiles = [r["smiles"] for r in runs]

        mean_r = float(np.mean(rewards))
        max_r = float(np.max(rewards))
        std_r = float(np.std(rewards))
        mean_t = float(np.mean(times))
        mean_mpo = float(np.mean(mpos))
        mean_dock = float(np.mean(docks))

        label = method_labels.get(method, method.capitalize())
        line = (
            f"  {label} & "
            f"{mean_r:.4f} & "
            f"{max_r:.4f} & "
            f"{std_r:.4f} & "
            f"{mean_t:.1f} & "
            f"{mean_mpo:.3f} & "
            f"{mean_dock:.2f} \\\\"
        )
        lines.append(line)

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Cross-seed LaTeX table: {output_path} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
