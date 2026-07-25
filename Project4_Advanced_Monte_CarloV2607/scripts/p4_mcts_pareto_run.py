#!/usr/bin/env python3
"""P4 — CLI runner for Pareto MCTS multi-objective molecular generation.

Runs a single Pareto MCTS search from a given scaffold and writes the full
Pareto front (all non-dominated solutions) to a CSV file. Designed to be
called from the SLURM array script `p4_pareto_array.sbatch`.

Uses ParetoMCTSAgent which maintains a global Pareto front across 5 objectives:
MPO (maximise), SYBA (maximise), SA (minimise), RRS (maximise), PNS (maximise).

Output CSV contains one row per non-dominated solution with full score vector.
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import sys
from pathlib import Path

import numpy as np

from p4_mcts_oracles import OracleAggregator
from p4_mcts_pareto import ParetoMCTSAgent
from p4_mcts_policy import ScafVAEPolicy
from p4_mcts_rl_env import MolecularEnv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Pareto MCTS multi-objective molecular generation."
    )
    parser.add_argument(
        "--initial-smiles", default="c1ccccc1",
        help="Starting scaffold SMILES (default: benzene)"
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
        help="Fragment vocabulary (default: all ~99 fragments)"
    )
    parser.add_argument(
        "--c-puct", type=float, default=5.0,
        help="PUCT exploration constant (default: 5.0, tuned for large action space)"
    )
    parser.add_argument(
        "--policy-temperature", type=float, default=0.8,
        help="ScafVAE policy temperature (default: 0.8; lower = more greedy)"
    )
    parser.add_argument(
        "--output-csv", type=Path, default=None,
        help="Output CSV path (default: results/pareto/p4_pareto_seed_{seed}.csv)"
    )
    args = parser.parse_args()

    # Seed: use SLURM_ARRAY_TASK_ID if available, else argparse seed
    if args.seed is None:
        args.seed = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))

    random.seed(args.seed)
    np.random.seed(args.seed)

    # Default output path
    if args.output_csv is None:
        script_dir = Path(__file__).resolve().parent
        project_dir = script_dir.parent
        args.output_csv = (
            project_dir / "results" / "pareto"
            / f"p4_pareto_seed_{args.seed}.csv"
        )

    # ── Environment ──────────────────────────────────────────────────
    env = MolecularEnv(
        initial_smiles=args.initial_smiles,
        max_steps=args.max_steps,
        fragment_set=args.fragment_set,
        randomize_attachment=True,
    )

    # ── Oracle (returns dict of scores, for multi-objective Pareto) ──
    oracle_agg = OracleAggregator(use_precomputed=True)

    # The Pareto MCTS agent expects oracle_fn(state) -> dict[str, float]
    # OracleAggregator.score() returns exactly this.
    oracle_fn = oracle_agg.score

    # ── Policy ───────────────────────────────────────────────────────
    policy = ScafVAEPolicy(
        temperature=args.policy_temperature,
        random_seed=args.seed,
    )
    policy_fn = policy.get_action_priors

    # ── Pareto MCTS Agent ────────────────────────────────────────────
    objectives = ["mpo", "syba", "sa", "rrs", "pns"]
    # Maximise MPO, SYBA, RRS, PNS; minimise SA
    maximize = [True, True, False, True, True]

    agent = ParetoMCTSAgent(
        env,
        oracle_fn=oracle_fn,
        objectives=objectives,
        maximize=maximize,
        n_iterations=args.n_iterations,
        c_puct=args.c_puct,
        policy_fn=policy_fn,
    )

    print(f"═══ P4 Pareto MCTS — seed={args.seed} ═══")
    print(f"  Initial SMILES:  {args.initial_smiles}")
    print(f"  Max steps:       {args.max_steps}")
    print(f"  Iterations:      {args.n_iterations}")
    print(f"  Fragment set:    {args.fragment_set} ({len(env.fragment_vocab)} fragments)")
    print(f"  PUCT c:          {args.c_puct}")
    print(f"  Objectives:      {objectives}")
    print(f"  Maximize:        {maximize}")
    print(f"  Host:            {__import__('socket').gethostname()}")

    # ── Run Pareto MCTS search ───────────────────────────────────────
    front = agent.search(args.initial_smiles)
    solutions = front.solutions
    hv = front.hypervolume()

    print(f"\n═══ Pareto Front Results ═══")
    print(f"  Front size:      {len(solutions)}")
    print(f"  Hypervolume:     {hv:.4f}")

    # ── Output: one row per Pareto-optimal solution ──────────────────
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "seed", "hypervolume", "front_size",
            "smiles", "mpo", "syba", "sa", "rrs", "pns",
        ])
        for smi, vec, meta in solutions:
            writer.writerow([
                args.seed,
                f"{hv:.4f}",
                len(solutions),
                smi,
                f"{vec[0]:.4f}",  # MPO
                f"{vec[1]:.4f}",  # SYBA
                f"{vec[2]:.4f}",  # SA
                f"{vec[3]:.4f}",  # RRS
                f"{vec[4]:.4f}",  # PNS
            ])

    print(f"  Output CSV:      {args.output_csv}")
    print(f"  Front molecules:")
    for smi, vec, _ in solutions[:10]:
        print(f"    {smi:40s} MPO={vec[0]:.3f} SYBA={vec[1]:.3f} "
              f"SA={vec[2]:.3f} RRS={vec[3]:.3f} PNS={vec[4]:.3f}")
    if len(solutions) > 10:
        print(f"    ... and {len(solutions) - 10} more non-dominated solutions")
    print(f"\n═══ Task {args.seed} complete ═══")


if __name__ == "__main__":
    main()
