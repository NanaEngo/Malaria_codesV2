#!/usr/bin/env python3
"""P4 — Benchmark: MCTS vs Random vs Greedy vs GA

Runs all 4 methods with a single seed and writes per-seed CSV + LaTeX table.
Designed for SLURM array: each task runs one seed, results aggregated post-hoc.

Usage:
    python p4_mcts_benchmark.py --seed 0 --output results/benchmark/p4_benchmark_seed_0.csv \
        --latex-table results/benchmark/p4_benchmark_table_seed_0.tex
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))

try:
    from p4_mcts_agent import MCTSAgent
    HAS_MCTS = True
except ImportError:
    HAS_MCTS = False

try:
    from p4_mcts_rl_env import MolecularEnv
    HAS_ENV = True
except ImportError:
    HAS_ENV = False

try:
    from p4_mcts_baselines import compute_mpo_reward
    HAS_BASELINES = True
except ImportError:
    HAS_BASELINES = False
    print("WARNING: p4_mcts_baselines not found. Using mock baselines.", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P4 MCTS Benchmark (single seed)")
    parser.add_argument("--n-iterations", type=int, default=1000)
    parser.add_argument("--ga-population", type=int, default=50)
    parser.add_argument("--ga-generations", type=int, default=20)
    parser.add_argument("--n-seeds", type=int, default=1,
                        help="Always 1 per SLURM task; kept for CLI compatibility")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--initial-smiles", default="C")
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument(
        "--fragment-set",
        type=str,
        default="medium",
        choices=["all", "medium", "aromatic_only", "minimal"],
        help="Fragment vocabulary subset; 'medium' reduces valence/kekulization errors.",
    )
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--latex-table", type=str, required=True)
    return parser.parse_args()


def _mock_oracle(smiles: str) -> float:
    h = int(hashlib.md5(smiles.encode()).hexdigest(), 16)
    return 0.3 + 0.4 * (h % 1000) / 1000.0


def make_env(initial_smiles, max_steps, seed, fragment_set="medium"):
    if HAS_ENV:
        return MolecularEnv(
            initial_smiles=initial_smiles,
            max_steps=max_steps,
            seed=seed,
            fragment_set=fragment_set,
        )

    class _MockEnv:
        def __init__(self):
            self.state = initial_smiles
            self.step_count = 0
            self.max_steps = max_steps
            self.fragment_vocab = ["c1ccccc1", "CC", "C=O", "CN", "CF",
                                   "CCO", "CCC", "CCCC", "c1ccncc1", "C1CCCC1"]
            self._fragment_set = "all"

        def reset(self):
            self.state = initial_smiles
            self.step_count = 0
            return self.state

        def step(self, action):
            self.state = self.state + "." + action
            self.step_count += 1
            return self.state, 0.0, self.step_count >= self.max_steps, {}

    return _MockEnv()


def run_mcts(env, oracle, args):
    agent = MCTSAgent(env=env, oracle=oracle, n_iterations=args.n_iterations,
                      c_puct=1.414, seed=args.seed)
    t0 = time.perf_counter()
    best = agent.search(env.state)
    return oracle(best), time.perf_counter() - t0


def run_random(env, oracle, args):
    import numpy as np
    rng = np.random.default_rng(args.seed)
    vocab = list(env.fragment_vocab)
    best_reward, best_smiles = 0.0, env.state
    t0 = time.perf_counter()
    for _ in range(args.n_iterations):
        env.reset()
        for _ in range(args.max_steps):
            action = vocab[rng.integers(len(vocab))]
            state, _, done, _ = env.step(action)
            r = oracle(state)
            if r > best_reward:
                best_reward, best_smiles = r, state
            if done:
                break
    return best_reward, time.perf_counter() - t0


def run_greedy(env, oracle, args):
    vocab = list(env.fragment_vocab)
    state = env.state
    t0 = time.perf_counter()
    for _ in range(args.max_steps):
        best_r, best_a = -1.0, None
        for a in vocab:
            env.reset()
            # Temporarily step to evaluate
            next_s, _, _, _ = env.step(a)
            r = oracle(next_s)
            if r > best_r:
                best_r, best_a = r, a
        if best_a:
            env.reset()
            state, _, done, _ = env.step(best_a)
            if done:
                break
    return oracle(state), time.perf_counter() - t0


def run_ga(env, oracle, args):
    import numpy as np
    rng = np.random.default_rng(args.seed)
    vocab = list(env.fragment_vocab)
    pop_size = args.ga_population
    n_gen = args.ga_generations
    population = [rng.choice(vocab, size=rng.integers(1, args.max_steps + 1)).tolist()
                  for _ in range(pop_size)]
    best_reward = 0.0
    t0 = time.perf_counter()
    for _ in range(n_gen):
        fitnesses = []
        for ind in population:
            env.reset()
            for a in ind:
                state, _, done, _ = env.step(a)
                if done:
                    break
            r = oracle(state)
            fitnesses.append(r)
            if r > best_reward:
                best_reward = r
        # Tournament selection + crossover (simplified)
        new_pop = []
        for _ in range(pop_size):
            i, j = rng.integers(pop_size, size=2)
            parent = population[i] if fitnesses[i] > fitnesses[j] else population[j]
            cut = rng.integers(1, max(2, len(parent)))
            child = parent[:cut] + [rng.choice(vocab)]
            new_pop.append(child[:args.max_steps])
        population = new_pop
    return best_reward, time.perf_counter() - t0


def main() -> None:
    args = parse_args()
    out_path = Path(args.output)
    tex_path = Path(args.latex_table)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.parent.mkdir(parents=True, exist_ok=True)

    oracle = compute_mpo_reward if HAS_BASELINES else _mock_oracle
    env = make_env(args.initial_smiles, args.max_steps, args.seed, args.fragment_set)

    results = {}
    print(f"=== P4 Benchmark | seed={args.seed} | fragment_set={args.fragment_set} ===")

    if HAS_MCTS:
        r, t = run_mcts(make_env(args.initial_smiles, args.max_steps, args.seed, args.fragment_set), oracle, args)
        results["mcts"] = {"reward": r, "elapsed_s": t}
        print(f"  MCTS:   {r:.4f} ({t:.1f}s)")

    r, t = run_random(make_env(args.initial_smiles, args.max_steps, args.seed, args.fragment_set), oracle, args)
    results["random"] = {"reward": r, "elapsed_s": t}
    print(f"  Random: {r:.4f} ({t:.1f}s)")

    r, t = run_greedy(make_env(args.initial_smiles, args.max_steps, args.seed, args.fragment_set), oracle, args)
    results["greedy"] = {"reward": r, "elapsed_s": t}
    print(f"  Greedy: {r:.4f} ({t:.1f}s)")

    r, t = run_ga(make_env(args.initial_smiles, args.max_steps, args.seed, args.fragment_set), oracle, args)
    results["ga"] = {"reward": r, "elapsed_s": t}
    print(f"  GA:     {r:.4f} ({t:.1f}s)")

    # Write CSV
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "seed", "reward", "elapsed_s"])
        writer.writeheader()
        for method, v in results.items():
            writer.writerow({"method": method, "seed": args.seed,
                             "reward": v["reward"], "elapsed_s": f"{v['elapsed_s']:.2f}"})
    print(f"  CSV saved to {out_path}")

    # Write per-seed LaTeX snippet
    with open(tex_path, "w") as f:
        f.write(f"% Benchmark results — seed {args.seed}\n")
        f.write("\\begin{tabular}{ll}\n\\hline\nMethod & Reward \\\\\n\\hline\n")
        for method, v in results.items():
            f.write(f"  {method.upper()} & {v['reward']:.4f} \\\\\n")
        f.write("\\hline\n\\end{tabular}\n")
    print(f"  LaTeX saved to {tex_path}")


if __name__ == "__main__":
    main()
