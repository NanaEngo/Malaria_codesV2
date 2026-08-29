#!/usr/bin/env python3
"""P4 — Canonical statistics for the optimal-config MCTS benchmark (v11).

Reads results/benchmark_molecules_opt/p4_benchmark_merged.csv and reports:
  * best/worst seed per method
  * paired t-tests (MCTS vs Random, GA vs Random, GA vs MCTS)
  * timing profiles
"""
from __future__ import annotations

import pandas as pd
from scipy import stats

NEW = "Project4_Advanced_Monte_CarloV2607/results/benchmark_molecules_opt/p4_benchmark_merged.csv"


def main() -> None:
    df = pd.read_csv(NEW)

    print("=== best/worst seed per method (optimal-config, v11) ===")
    for m in ["random", "mcts", "ga", "greedy"]:
        sub = df[df.method == m].sort_values("reward")
        best = sub.iloc[-1]
        worst = sub.iloc[0]
        print(f"{m:8s} best={best['reward']:.4f} (seed {int(best['seed'])}), "
              f"worst={worst['reward']:.4f} (seed {int(worst['seed'])})")

    rd = df[df.method == "random"].sort_values("seed").reward.values
    mc = df[df.method == "mcts"].sort_values("seed").reward.values
    ga = df[df.method == "ga"].sort_values("seed").reward.values

    print("\n=== paired t-tests ===")
    for name, a, b in [("MCTS vs Random", mc, rd),
                       ("GA vs Random", ga, rd),
                       ("GA vs MCTS", ga, mc)]:
        t, p = stats.ttest_rel(a, b)
        print(f"{name:16s} t={t:.3f}, p={p:.4f}")
    print(f"mean(MCTS-Random) = {(mc - rd).mean():+.5f}")

    # Cohen's d (paired)
    d = (mc - rd).mean() / (mc - rd).std(ddof=1)
    print(f"Cohen d (MCTS-Random paired) = {d:.3f}")

    print("\n=== timing ===")
    print(df.groupby("method")["elapsed_s"].agg(["mean", "std"]).round(1))

    # Wins per seed
    print("\n=== wins per seed ===")
    for i in range(20):
        row = df[df.seed == i].set_index("method")["reward"]
        winner = row.idxmax()
        if winner == "mcts":
            print(f"  seed {i}: MCTS wins ({row['mcts']:.4f} vs random {row['random']:.4f})")


if __name__ == "__main__":
    main()
