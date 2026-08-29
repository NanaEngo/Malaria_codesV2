#!/usr/bin/env python3
"""P4 — Canonical benchmark statistics for the re-benchmarked 20-seed run.

Computes, from results/benchmark_molecules/p4_benchmark_merged.csv (new
canonical) and results/benchmark/p4_benchmark_merged.csv (old deposit):
  * best/worst seed per method
  * paired t-tests (MCTS vs Random, GA vs Random, GA vs MCTS)
  * seed-level Spearman stability new vs old
  * timing profiles (new vs old)
"""
from __future__ import annotations

import pandas as pd
from scipy import stats

PROJECT = "Project4_Advanced_Monte_CarloV2607"
NEW = f"{PROJECT}/results/benchmark_molecules/p4_benchmark_merged.csv"
OLD = f"{PROJECT}/results/benchmark/p4_benchmark_merged.csv"


def main() -> None:
    df = pd.read_csv(NEW)
    old = pd.read_csv(OLD)

    print("=== best/worst seed per method (new canonical) ===")
    for m in ["random", "mcts", "ga", "greedy"]:
        sub = df[df.method == m].sort_values("reward")
        best = sub.iloc[-1]
        worst = sub.iloc[0]
        print(f"{m:8s} best={best['reward']:.4f} (seed {int(best['seed'])}), "
              f"worst={worst['reward']:.4f} (seed {int(worst['seed'])})")

    rd = df[df.method == "random"].sort_values("seed").reward.values
    mc = df[df.method == "mcts"].sort_values("seed").reward.values
    ga = df[df.method == "ga"].sort_values("seed").reward.values

    print("\n=== paired t-tests (new canonical) ===")
    for name, a, b in [("MCTS vs Random", mc, rd),
                       ("GA vs Random", ga, rd),
                       ("GA vs MCTS", ga, mc)]:
        t, p = stats.ttest_rel(a, b)
        print(f"{name:16s} t={t:.3f}, p={p:.4f}")
    print(f"mean(MCTS-Random) = {(mc - rd).mean():+.5f}")

    print("\n=== seed-level stability new vs old ===")
    for m in ["random", "mcts", "ga"]:
        new_v = df[df.method == m].sort_values("seed").reward.values
        old_v = old[old.method == m].sort_values("seed").reward.values
        rho = stats.spearmanr(new_v, old_v).statistic
        print(f"{m:8s} spearman rho={rho:.3f}  mean_delta={new_v.mean() - old_v.mean():+.4f}")

    print("\n=== timing profile (new) ===")
    print(df.groupby("method")["elapsed_s"].agg(["mean", "std"]).round(1))
    print("\n=== timing profile (old deposited) ===")
    print(old.groupby("method")["elapsed_s"].agg(["mean", "std"]).round(1))

    print("\n=== greedy identical across seeds? ===")
    g = df[df.method == "greedy"].reward.unique()
    print("unique greedy rewards:", g)


if __name__ == "__main__":
    main()
