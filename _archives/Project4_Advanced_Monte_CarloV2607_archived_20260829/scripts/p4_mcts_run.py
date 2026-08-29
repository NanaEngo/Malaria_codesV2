#!/usr/bin/env python3
"""P4 — MCTS Run Entry Point

CLI wrapper for MCTSAgent. Instantiates the molecular environment,
runs a single MCTS search, and writes results to CSV.

Usage:
    python p4_mcts_run.py --seed 0 --output-csv results/mcts/p4_mcts_seed_0.csv
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
except ImportError as e:
    print(f"ERROR: Cannot import MCTSAgent: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from p4_mcts_rl_env import MolecularEnv
    HAS_ENV = True
except ImportError:
    HAS_ENV = False
    print("WARNING: p4_mcts_rl_env not found. Using mock environment.", file=sys.stderr)

try:
    from p4_mcts_baselines import compute_mpo_reward
    HAS_MPO = True
except ImportError:
    HAS_MPO = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P4 MCTS Molecular Generation Run")
    parser.add_argument("--initial-smiles", default="C")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--n-iterations", type=int, default=1000)
    parser.add_argument("--fragment-set", default="medium",
                        choices=["all", "medium", "aromatic_only", "minimal"],
                        help="Fragment vocabulary (default: medium, valence-filtered)")
    parser.add_argument("--c-puct", type=float, default=1.414)
    parser.add_argument("--policy-temperature", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-csv", type=str, required=True)
    return parser.parse_args()


def make_oracle(has_mpo: bool):
    if has_mpo:
        print("Using MPO oracle (P1/P2 integration).")
        return compute_mpo_reward
    def _mock_oracle(smiles: str) -> float:
        h = int(hashlib.md5(smiles.encode()).hexdigest(), 16)
        return 0.3 + 0.4 * (h % 1000) / 1000.0
    print("WARNING: Using deterministic mock oracle (MPO not available).", file=sys.stderr)
    return _mock_oracle


def make_env(initial_smiles, max_steps, fragment_set, seed):
    if HAS_ENV:
        return MolecularEnv(initial_smiles=initial_smiles, max_steps=max_steps,
                            fragment_set=fragment_set, seed=seed)

    class _MockEnv:
        def __init__(self):
            self.state = initial_smiles
            self.step_count = 0
            self.max_steps = max_steps
            self.fragment_vocab = ["c1ccccc1", "CC", "C=O", "CN", "CF",
                                   "CCO", "CCC", "CCCC", "c1ccncc1", "C1CCCC1"]
            self._fragment_set = fragment_set

        def reset(self):
            self.state = initial_smiles
            self.step_count = 0
            return self.state

        def step(self, action: str):
            self.state = self.state + "." + action
            self.step_count += 1
            done = self.step_count >= self.max_steps
            return self.state, 0.0, done, {}

    return _MockEnv()


def main() -> None:
    args = parse_args()
    out_path = Path(args.output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    oracle = make_oracle(HAS_MPO)
    env = make_env(args.initial_smiles, args.max_steps, args.fragment_set, args.seed)

    print(f"=== P4 MCTS Run | seed={args.seed} | fragment_set={args.fragment_set} ===")

    agent = MCTSAgent(
        env=env,
        oracle=oracle,
        n_iterations=args.n_iterations,
        c_puct=args.c_puct,
        seed=args.seed,
        rollout_temperature=args.policy_temperature,
    )

    t0 = time.perf_counter()
    best_smiles = agent.search(env.state)
    elapsed = time.perf_counter() - t0
    best_reward = oracle(best_smiles)

    print(f"  Best SMILES: {best_smiles}")
    print(f"  Best reward: {best_reward:.4f}")
    print(f"  Elapsed:     {elapsed:.1f}s")

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "seed", "fragment_set", "c_puct", "policy_temperature",
            "n_iterations", "max_steps", "best_smiles", "best_reward", "elapsed_s",
        ])
        writer.writeheader()
        writer.writerow({
            "seed": args.seed, "fragment_set": args.fragment_set,
            "c_puct": args.c_puct, "policy_temperature": args.policy_temperature,
            "n_iterations": args.n_iterations, "max_steps": args.max_steps,
            "best_smiles": best_smiles, "best_reward": best_reward,
            "elapsed_s": f"{elapsed:.2f}",
        })
    print(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
