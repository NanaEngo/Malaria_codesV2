#!/usr/bin/env python3
"""P4 — CLI runner for MCTS+RL molecular generation (production).

Runs a single MCTS search from a given scaffold with:
- ScafVAE-guided policy for fragment selection (PUCT priors)
- Expanded 33-fragment medicinal chemistry vocabulary
- Real oracles (MPO + docking + SYBA + SA from P1/P2)
- Random seed per task for independent exploration

Designed to be called from the SLURM array script `p4_mcts_array.sbatch`.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

from p4_mcts_agent import MCTSAgent
from p4_mcts_oracles import make_oracle
from p4_mcts_policy import ScafVAEPolicy
from p4_mcts_rl_env import MolecularEnv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run MCTS molecular generation (production)."
    )
    parser.add_argument(
        "--initial-smiles", default="C",
        help="Starting scaffold SMILES (default: methane)"
    )
    parser.add_argument(
        "--max-steps", type=int, default=10,
        help="Maximum fragment additions (default: 10)"
    )
    parser.add_argument(
        "--n-iterations", type=int, default=500,
        help="MCTS iterations (default: 500)"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed (default: SLURM_ARRAY_TASK_ID)"
    )
    parser.add_argument(
        "--fragment-set", choices=["all", "medium", "aromatic_only", "minimal"],
        default="all",
        help="Fragment vocabulary (default: all 108 fragments)"
    )
    parser.add_argument(
        "--c-puct", type=float, default=1.414,
        help="PUCT exploration constant (default: 1.414)"
    )
    parser.add_argument(
        "--policy-temperature", type=float, default=0.8,
        help="ScafVAE policy temperature (default: 0.8; lower = more greedy)"
    )
    parser.add_argument(
        "--oracle-weights", type=str, default=None,
        help="JSON string of oracle weights, e.g. '{\"mpo\":0.4,\"docking\":0.3}'"
    )
    parser.add_argument(
        "--no-policy", action="store_true",
        help="Disable ScafVAE policy (use flat UCT instead)"
    )
    parser.add_argument(
        "--output-csv", type=Path, default=Path("p4_mcts_result.csv"),
        help="Output CSV path"
    )
    args = parser.parse_args()

    # Seed: use SLURM_ARRAY_TASK_ID if available, else argparse seed
    if args.seed is None:
        import os
        args.seed = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))

    random.seed(args.seed)

    # ── Environment (expanded 33-fragment vocabulary) ──────────────
    env = MolecularEnv(
        initial_smiles=args.initial_smiles,
        max_steps=args.max_steps,
        fragment_set=args.fragment_set,
        randomize_attachment=True,  # stochasticity for diversity
    )

    # ── Oracle (use P1/P2 precomputed libraries when possible) ─────
    weights = None
    if args.oracle_weights:
        try:
            weights = json.loads(args.oracle_weights)
        except json.JSONDecodeError:
            print(f"Warning: invalid oracle weights JSON: {args.oracle_weights}",
                  file=sys.stderr)

    oracle = make_oracle(weights=weights)

    # ── Policy (ScafVAE-guided fragment selection) ────────────────
    policy_fn = None
    if not args.no_policy:
        policy = ScafVAEPolicy(
            temperature=args.policy_temperature,
            random_seed=args.seed,
        )
        policy_fn = policy.get_action_priors

    # ── MCTS Agent ────────────────────────────────────────────────
    agent = MCTSAgent(
        env,
        oracle=oracle,
        n_iterations=args.n_iterations,
        c_puct=args.c_puct,
        policy_fn=policy_fn,
        seed=args.seed,
    )

    print(f"═══ P4 MCTS+RL — seed={args.seed} ═══")
    print(f"  Initial SMILES:  {args.initial_smiles}")
    print(f"  Max steps:       {args.max_steps}")
    print(f"  Iterations:      {args.n_iterations}")
    print(f"  Fragment set:    {args.fragment_set} ({len(env.fragment_vocab)} fragments)")
    print(f"  Policy:          {'ScafVAE' if policy_fn else 'None (flat UCT)'}")
    print(f"  PUCT c:          {args.c_puct}")
    print(f"  Host:            {__import__('socket').gethostname()}")

    # ── Run MCTS search ───────────────────────────────────────────
    best_state = agent.search(args.initial_smiles)
    best_reward = oracle(best_state)

    # ── Output ────────────────────────────────────────────────────
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "seed", "initial_smiles", "max_steps", "n_iterations",
            "fragment_set", "policy", "best_state", "best_reward",
        ])
        writer.writerow([
            args.seed,
            args.initial_smiles,
            args.max_steps,
            args.n_iterations,
            args.fragment_set,
            "scafvae" if policy_fn else "flat_uct",
            best_state,
            f"{best_reward:.6f}",
        ])

    print(f"\\n═══ Results ═══")
    print(f"  Best state:      {best_state}")
    print(f"  Best reward:     {best_reward:.6f}")
    print(f"  Output CSV:      {args.output_csv}")


if __name__ == "__main__":
    main()
