#!/usr/bin/env python3
"""
P4 — 2^5 factorial ablation runner (reconstructed generator).

Reproduces the component ablation reported in the manuscript:
    ScafVAE policy (+0.148), Pareto front (+0.108), Large vocabulary (+0.079).

Design (ConfigID 0..31, 5 binary factors, LSB first):
    bit 0  Vocab      0=Small(minimal)  1=Large(all)
    bit 1  Temperature 0=0.5             1=1.5
    bit 2  c_PUCT     0=1.0              1=2.0
    bit 3  Pareto     0=False            1=True
    bit 4  ScafVAE    0=False            1=True

Each ConfigID is run with `n_replicates` independent replicates (default 5,
matching the deposited `results/ablation/p4_ablation_config_*.csv`).

Usage (single config + replicate, for a SLURM array):
    python p4_mcts_factorial_run.py --array-id 0 --replicate 0 \
        --output results/ablation/p4_ablation_config_0.csv
    # appends one reward row to the config CSV (creates header if missing)
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))


def _mapping(cid: int) -> dict:
    """Decode a ConfigID into its five factor levels (binary, LSB first)."""
    b = int(cid)
    return {
        "Vocab": "Large" if (b >> 0) & 1 else "Small",
        "Temperature": 1.5 if (b >> 1) & 1 else 0.5,
        "c_PUCT": 2.0 if (b >> 2) & 1 else 1.0,
        "Pareto": bool((b >> 3) & 1),
        "ScafVAE": bool((b >> 4) & 1),
        "ConfigID": cid,
    }


def _fragment_set(vocab: str) -> str:
    return "all" if vocab == "Large" else "minimal"


def run_config(cfg: dict, seed: int, n_iterations: int, max_steps: int) -> float:
    """Run one MCTS episode under the factor levels in `cfg`; return best reward."""
    from p4_mcts_agent import MCTSAgent
    from p4_mcts_baselines import compute_mpo_reward
    from p4_mcts_rl_env import MolecularEnv

    vocab = _fragment_set(cfg["Vocab"])
    env = MolecularEnv(
        initial_smiles="C",
        max_steps=max_steps,
        fragment_set=vocab,
        randomize_attachment=True,
        seed=seed,
    )

    # Optional ScafVAE policy (bit 4).
    policy_fn = None
    if cfg["ScafVAE"]:
        from p4_mcts_policy import ScafVAEPolicy
        policy = ScafVAEPolicy(
            temperature=cfg["Temperature"],
            random_seed=seed,
        )
        policy_fn = policy.get_action_priors

    if cfg["Pareto"]:
        from p4_mcts_oracles import OracleAggregator
        from p4_mcts_pareto import ParetoMCTSAgent

        oracle_agg = OracleAggregator(
            weights={
                "mpo": 0.30,
                "docking": 0.25,
                "syba": 0.15,
                "sa": 0.05,
                "rrs": 0.15,
                "pns": 0.10,
                "drug_like": 0.0,
            },
            use_precomputed=True,
            use_rrs=True,
        )

        def _vec_reward(smiles: str) -> dict[str, float]:
            return oracle_agg.score(smiles)

        # ParetoMCTSAgent takes `env` as the first argument, `oracle_fn` second,
        # and has NO temperature parameter (no rollout_temperature).
        agent = ParetoMCTSAgent(
            env=env,
            oracle_fn=_vec_reward,
            objectives=["mpo", "syba", "sa", "rrs", "pns"],
            maximize=[True, True, False, True, True],
            n_iterations=n_iterations,
            c_puct=cfg["c_PUCT"],
            policy_fn=policy_fn,
            virtual_loss=0.01,
            pw_alpha=0.5,
            pw_k=1.0,
        )
        front = agent.search(env.state)
        # Scalarised reward of the best front member (comparable across configs).
        best_r = -1.0
        for smi, _vec, _meta in getattr(front, "solutions", []):
            r = compute_mpo_reward(smi)
            if r > best_r:
                best_r = r
        return best_r if best_r >= 0.0 else 0.0
    else:
        agent = MCTSAgent(
            env=env,
            oracle=compute_mpo_reward,
            n_iterations=n_iterations,
            c_puct=cfg["c_PUCT"],
            policy_fn=policy_fn,
            pw_alpha=0.5,
            pw_k=1.0,
            virtual_loss=0.01,
            rollout_temperature=cfg["Temperature"],
        )
        best_smi = agent.search(env.state)
        return float(compute_mpo_reward(best_smi))


def main() -> None:
    parser = argparse.ArgumentParser(description="P4 2^5 factorial ablation run")
    parser.add_argument("--array-id", type=int, default=0, help="ConfigID 0..31")
    parser.add_argument("--replicate", type=int, default=0, help="Replicate index")
    parser.add_argument("--n-iterations", type=int, default=200,
                        help="MCTS iterations per run (default 200)")
    parser.add_argument("--max-steps", type=int, default=8,
                        help="Max molecular construction steps")
    parser.add_argument("--output", type=Path, required=True,
                        help="Output config CSV path (appends reward row)")
    args = parser.parse_args()

    cfg = _mapping(args.array_id)
    seed = args.replicate  # deterministic per replicate

    random.seed(seed)
    np.random.seed(seed)

    reward = run_config(cfg, seed, args.n_iterations, args.max_steps)
    print(f"ConfigID {cfg['ConfigID']} rep {args.replicate}: "
          f"ScafVAE={cfg['ScafVAE']} Pareto={cfg['Pareto']} "
          f"cPUCT={cfg['c_PUCT']} T={cfg['Temperature']} Vocab={cfg['Vocab']} "
          f"-> reward={reward:.6f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    header = ["ScafVAE", "Pareto", "c_PUCT", "Temperature", "Vocab",
              "ConfigID", "Replicate", "Reward"]
    new = not args.output.exists()
    with open(args.output, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(header)
        w.writerow([
            str(cfg["ScafVAE"]), str(cfg["Pareto"]), str(cfg["c_PUCT"]),
            str(cfg["Temperature"]), cfg["Vocab"], cfg["ConfigID"],
            args.replicate, f"{reward:.12f}",
        ])


if __name__ == "__main__":
    main()