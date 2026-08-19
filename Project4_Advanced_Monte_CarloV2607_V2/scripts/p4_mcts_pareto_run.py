#!/usr/bin/env python3
"""P4 — CLI runner for Pareto MCTS multi-objective molecular generation.

Runs a single Pareto MCTS search from a given scaffold and writes the full
Pareto front (all non-dominated solutions) to a CSV file. Designed to be
called from the SLURM array script `p4_pareto_array.sbatch`.

Uses ParetoMCTSAgent with either the five-objective historical pre-activity
schema (MPO, SYBA, SA, RRS, PNS) or the six-objective v12 schema, which adds
ACTIVITY (proximity to public ChEMBL antimalarial actives).

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
        default="medium",
        help="Fragment vocabulary (default: medium, valence-filtered)"
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
        "--selection-mode", choices=["proxy", "pareto"], default="proxy",
        help="Child selection for tree: proxy = scalar per-objective PUCT; "
             "pareto = ParetoPUCT ablation (restrict to non-dominated children)"
    )
    parser.add_argument(
        "--pre-activity", action="store_true",
        help="Run the pre-activity vector protocol (exclude the public-activity objective)"
    )
    parser.add_argument(
        "--output-csv", type=Path, default=None,
        help="Explicit output CSV path (required; prevents accidental overwrite of locked artefacts)"
    )
    args = parser.parse_args()

    # Seed: use SLURM_ARRAY_TASK_ID if available, else argparse seed
    if args.seed is None:
        args.seed = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))

    random.seed(args.seed)
    np.random.seed(args.seed)

    if args.output_csv is None:
        raise SystemExit(
            "--output-csv is required; refusing an implicit write path. "
            "Use a separate directory for new runs and preserve locked artefacts."
        )
    output_path = args.output_csv.expanduser().resolve()
    locked_pareto_dir = (
        Path(__file__).resolve().parents[1] / "results" / "pareto"
    ).resolve()
    try:
        output_path.relative_to(locked_pareto_dir)
    except ValueError:
        pass
    else:
        raise SystemExit(
            "Refusing to write directly to the locked results/pareto directory; "
            "use a separate output directory."
        )
    args.output_csv = output_path

    # ── Environment ──────────────────────────────────────────────────
    env = MolecularEnv(
        initial_smiles=args.initial_smiles,
        max_steps=args.max_steps,
        fragment_set=args.fragment_set,
        randomize_attachment=True,
    )

    # ── Oracle (returns dict of scores, for multi-objective Pareto) ──
    # Publication reruns fail closed if SYBA is unavailable. Legacy artefact
    # re-scoring is performed by dedicated post-processing scripts, not this
    # search runner.
    oracle_agg = OracleAggregator(
        use_precomputed=True,
        use_activity=not args.pre_activity,
        require_syba=True,
    )

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
    if args.pre_activity:
        objectives = ["mpo", "syba", "sa", "rrs", "pns"]
        maximize = [True, True, False, True, True]
    else:
        objectives = ["mpo", "syba", "sa", "rrs", "pns", "activity"]
        maximize = [True, True, False, True, True, True]
    # Maximise MPO, SYBA, RRS, PNS (and ACTIVITY in v12); minimise SA.

    agent = ParetoMCTSAgent(
        env,
        oracle_fn=oracle_fn,
        objectives=objectives,
        maximize=maximize,
        n_iterations=args.n_iterations,
        c_puct=args.c_puct,
        policy_fn=policy_fn,
        selection_mode=args.selection_mode,
    )

    print(f"═══ P4 Pareto MCTS — seed={args.seed} ═══")
    print(f"  Initial SMILES:  {args.initial_smiles}")
    print(f"  Max steps:       {args.max_steps}")
    print(f"  Iterations:      {args.n_iterations}")
    print(f"  Fragment set:    {args.fragment_set} ({len(env.fragment_vocab)} fragments)")
    print(f"  PUCT c:          {args.c_puct}")
    print(f"  Selection mode:  {args.selection_mode}")
    print(f"  Objectives:      {objectives}")
    print(f"  Maximize:        {maximize}")
    print(f"  Host:            {__import__('socket').gethostname()}")

    # ── Run Pareto MCTS search ───────────────────────────────────────
    front = agent.search(args.initial_smiles)
    solutions = front.solutions
    hv = front.hypervolume()

    diagnostics = oracle_agg.syba_diagnostics()
    if diagnostics["n_evaluated"] < 2 or diagnostics["n_unique"] < 2:
        raise RuntimeError(
            "SYBA remained constant or unavailable during the Pareto run; "
            "refusing to write a non-informative publication artifact: "
            f"{diagnostics}"
        )

    print(f"\n═══ Pareto Front Results ═══")
    print(f"  Front size:      {len(solutions)}")
    print(f"  Hypervolume:     {hv:.4f}")

    # ── Output: one row per Pareto-optimal solution ──────────────────
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "seed", "hypervolume", "front_size",
            "smiles", *objectives,
        ])
        for smi, vec, meta in solutions:
            writer.writerow([
                args.seed,
                f"{hv:.4f}",
                len(solutions),
                smi,
                *(f"{value:.4f}" for value in vec),
            ])

    print(f"  Output CSV:      {args.output_csv}")
    print(f"  Front molecules:")
    for smi, vec, _ in solutions[:10]:
        values = " ".join(
            f"{name.upper()}={value:.3f}" for name, value in zip(objectives, vec)
        )
        print(f"    {smi:40s} {values}")
    if len(solutions) > 10:
        print(f"    ... and {len(solutions) - 10} more non-dominated solutions")
    print(f"\n═══ Task {args.seed} complete ═══")


if __name__ == "__main__":
    main()
