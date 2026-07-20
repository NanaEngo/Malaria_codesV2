#!/usr/bin/env python3
"""P4 — CLI runner for MCTS+RL molecular generation.

Runs a single MCTS search from a given scaffold and writes the trajectory
(best state per iteration) to a CSV file. Designed to be called from the
SLURM array script `p4_mcts_array.sbatch`.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

from p4_mcts_agent import MCTSAgent
from p4_mcts_oracles import make_oracle
from p4_mcts_rl_env import MolecularEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MCTS molecular generation.")
    parser.add_argument("--initial-smiles", default="C", help="Starting scaffold SMILES")
    parser.add_argument("--max-steps", type=int, default=10, help="Maximum fragment additions")
    parser.add_argument("--n-iterations", type=int, default=100, help="MCTS iterations")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--output-csv", type=Path, default=Path("p4_mcts_result.csv"), help="Output CSV path")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    env = MolecularEnv(initial_smiles=args.initial_smiles, max_steps=args.max_steps)
    oracle = make_oracle()
    agent = MCTSAgent(env, oracle=oracle, n_iterations=args.n_iterations)

    best_state = agent.search(args.initial_smiles)
    best_reward = oracle(best_state)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["seed", "initial_smiles", "max_steps", "n_iterations", "best_state", "best_reward"])
        writer.writerow([
            args.seed,
            args.initial_smiles,
            args.max_steps,
            args.n_iterations,
            best_state,
            f"{best_reward:.6f}",
        ])

    print(f"Best state:  {best_state}")
    print(f"Best reward: {best_reward:.6f}")
    print(f"Output:      {args.output_csv}")


if __name__ == "__main__":
    main()
