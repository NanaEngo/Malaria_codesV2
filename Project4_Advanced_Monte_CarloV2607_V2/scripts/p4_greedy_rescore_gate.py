#!/usr/bin/env python
"""Gate for the greedy rescore (CRITICAL-1): reproduce the published number first.

Finding (as it stood before the rescore). scripts/p4_mcts_benchmark.py scored greedy under
a different rule from every method it is tabulated against:

    :147  run_random  -> best_reward             (best reward seen on the trajectory)
    :215  run_ga      -> best_reward             (best-intermediate)
    :128  run_mcts    -> oracle(best), where MCTSAgent.search returns the better of
                         best_global_smiles (best seen anywhere in the search,
                         p4_mcts_agent.py:279) and best_child.state (:280)
                         -- so MCTS is best-intermediate too
    :179  run_greedy  -> oracle(state)           (TERMINAL state; best_reward was
                         computed and then discarded)

Greedy was the sole outlier, and P4_Pareto_MCTS_JoC_refined.tex:318 states the opposite
rule while :282 claims that correction as a contribution. Rescoring greedy as
best-intermediate makes the table internally consistent and makes the text true.

Status. run_greedy now returns best_smiles, best_reward (p4_mcts_benchmark.py:186), so the
outlier is gone. This gate was written and passed BEFORE that edit and still governs it.

What this file does. It re-runs greedy under the published configuration and reports both
conventions from the SAME trajectory, reading each one independently of the other:

    terminal          oracle(env.state) after run_greedy returns. MolecularEnv.step
                      assigns self.state (p4_mcts_rl_env.py:469) and run_greedy steps the
                      real env once per accepted action, so env.state is the last molecule
                      on the trajectory. This is what the v12 SLURM array reported.
    best-intermediate run_greedy's returned reward, cross-checked against
                      oracle(returned smiles) -- the oracle is deterministic, so the two
                      must agree exactly or the returned pair is internally inconsistent.

Reading the terminal from the env rather than from the return value is what lets one run
gate BOTH deposits after the fix: the pre-fix return carried the terminal and the post-fix
return carries the best-intermediate, but env.state carries the terminal either way.

Gate discipline (same as scripts/p4_hv_independent_recheck.py). Lifting 0.6672 out of a
CSV is not verification: the CSV was written by the same call that produced the number.
This script therefore refuses to report a best-intermediate value as verified unless the
same run first reproduces the published terminal value for that vocabulary:

    medium vocabulary   terminal 0.4277593921809697   (results/benchmark_molecules_opt_v12/
                                                       p4_benchmark_merged.csv)
                        best-int 0.6672118688382241   (..._molecules_seed_*.csv)
    full vocabulary     terminal 0.4593                (4 dp; manuscript/
                        best-int  NOT ON DISK          Graphical_Abstract_Brief/data/
                                                       benchmark_v12_allfrag.csv, whose
                                                       header records that per-seed files
                                                       were never deposited)

The full-vocabulary best-intermediate value is the one genuinely new number here; it
backs tab:allfrag in P4_Pareto_MCTS_JoC_refined.tex:260, which has no source artifact.

Mock fallbacks are refused. p4_mcts_benchmark falls back to a hash oracle and a string
concatenating environment when RDKit-backed modules are missing; either fallback would
make every comparison below meaningless, so their absence is a hard failure, not a skip.

Read-only: imports scripts/, reads no file, writes nothing.

Usage:
    /home/tchapet/VirtualEnv/bin/python3 scripts/p4_greedy_rescore_gate.py
Exit 0 only if every published value reproduces.
"""
from __future__ import annotations

import statistics
import sys
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import p4_mcts_benchmark as bench  # noqa: E402

# Published configuration: p4_mcts_benchmark.parse_args defaults, which is what the v12
# SLURM array ran.
INITIAL_SMILES = "C"
MAX_STEPS = 10
SEEDS = (0, 1, 2)

TOL_EXACT = 1e-12  # full-precision CSV values
TOL_4DP = 5e-5  # values quoted to 4 decimal places in the manuscript

PUBLISHED = {
    "medium": {
        "terminal": 0.4277593921809697,
        "terminal_tol": TOL_EXACT,
        "best_intermediate": 0.6672118688382241,
        "best_intermediate_tol": TOL_EXACT,
        "smiles": "CN(c1ccc2ccccc2n1)C(C(=O)O)C(C)(C)C",
        "source": "results/benchmark_molecules_opt_v12/p4_benchmark_merged.csv"
                  " + p4_benchmark_molecules_seed_*.csv",
    },
    "all": {
        "terminal": 0.4593,
        "terminal_tol": TOL_4DP,
        "best_intermediate": None,  # no artifact -- this run is its first derivation
        "best_intermediate_tol": None,
        "smiles": None,
        "source": "manuscript/Graphical_Abstract_Brief/data/benchmark_v12_allfrag.csv"
                  " (aggregate only; per-seed files not deposited)",
    },
}


def run_one(fragment_set: str, seed: int) -> tuple[str, float, float, float, float]:
    """Return (best_smiles, terminal_reward, returned_reward, recomputed_best, elapsed_s).

    All four numbers come from one trajectory, and the two conventions are read from
    different places so neither depends on the other:

      terminal_reward  oracle(env.state) -- env is the live environment run_greedy stepped,
                       so its state is the last molecule on the trajectory. Independent of
                       whatever run_greedy chooses to return.
      returned_reward  run_greedy's reward, whatever convention it currently implements.
      recomputed_best  oracle(returned smiles). Must equal returned_reward exactly once
                       run_greedy reports the best-intermediate; main() checks it.
    """
    oracle = bench.compute_mpo_reward
    env = bench.make_env(INITIAL_SMILES, MAX_STEPS, seed, fragment_set)
    args = Namespace(max_steps=MAX_STEPS, fragment_set=fragment_set, seed=seed)
    smiles, returned, elapsed = bench.run_greedy(env, oracle, args)
    return smiles, oracle(env.state), returned, oracle(smiles), elapsed


def main() -> int:
    failures: list[str] = []

    # Refuse the mock paths outright -- a hash oracle or a string-concatenating env would
    # produce numbers that look fine and mean nothing.
    for flag, what in (("HAS_BASELINES", "compute_mpo_reward (MPO oracle)"),
                       ("HAS_ENV", "MolecularEnv (fragment vocabulary)")):
        if not getattr(bench, flag):
            failures.append(f"{what} unavailable -- {flag} is False, mock fallback refused")
    if failures:
        print("GREEDY RESCORE GATE: cannot run")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"greedy rescore gate | initial={INITIAL_SMILES!r} max_steps={MAX_STEPS} "
          f"seeds={list(SEEDS)}")

    cleared: dict[str, tuple[float, float]] = {}

    for fragment_set, want in PUBLISHED.items():
        print(f"\n--- fragment_set={fragment_set} "
              f"(published terminal {want['terminal']}) ---")
        print(f"    source: {want['source']}")

        terminals: list[float] = []
        bests: list[float] = []
        smiles_seen: set[str] = set()
        for seed in SEEDS:
            smiles, terminal, returned, recomputed, elapsed = run_one(fragment_set, seed)
            terminals.append(terminal)
            bests.append(returned)
            smiles_seen.add(smiles)
            print(f"  seed {seed}: terminal {terminal:.16f}  "
                  f"returned {returned:.16f}  ({elapsed:.1f}s)")
            # The two CSVs p4_mcts_benchmark writes must agree: --output records the
            # returned reward, --molecules-out records oracle(best_smiles). Under the
            # best-intermediate rule these are the same molecule, so any gap means the
            # returned reward and the returned SMILES describe different states.
            if abs(returned - recomputed) >= TOL_EXACT:
                failures.append(
                    f"{fragment_set} seed {seed}: returned reward {returned:.16f} != "
                    f"oracle(returned smiles) {recomputed:.16f} -- reward and molecule "
                    f"disagree, so the two benchmark CSVs would disagree"
                )

        sd_t = statistics.stdev(terminals) if len(terminals) > 1 else 0.0
        sd_b = statistics.stdev(bests) if len(bests) > 1 else 0.0
        print(f"  across {len(SEEDS)} seeds: terminal SD {sd_t:.2e}, "
              f"best-intermediate SD {sd_b:.2e}, distinct molecules {len(smiles_seen)}")
        print(f"  best molecule(s): {sorted(smiles_seen)}")
        if len(smiles_seen) != 1:
            failures.append(f"{fragment_set}: greedy is deterministic in the manuscript "
                            f"(SD 0.0000) but produced {len(smiles_seen)} molecules")

        # Gate: does the published terminal value reproduce?
        got_t = terminals[0]
        ok_t = abs(got_t - want["terminal"]) < want["terminal_tol"]
        print(f"  [{'PASS' if ok_t else 'FAIL'}] terminal {got_t:.16f} vs published "
              f"{want['terminal']}")
        if not ok_t:
            failures.append(f"{fragment_set}: terminal {got_t:.16f} != published "
                            f"{want['terminal']}")

        got_b = bests[0]
        if want["best_intermediate"] is None:
            if ok_t:
                print(f"  [NEW ] best-intermediate {got_b:.16f} -- first derivation, "
                      f"no prior artifact")
                cleared[fragment_set] = (got_t, got_b)
            else:
                print("  [HOLD] best-intermediate NOT reported: this vocabulary's "
                      "published terminal value did not reproduce")
        else:
            ok_b = abs(got_b - want["best_intermediate"]) < want["best_intermediate_tol"]
            print(f"  [{'PASS' if ok_b else 'FAIL'}] best-intermediate {got_b:.16f} vs "
                  f"deposited {want['best_intermediate']}")
            if not ok_b:
                failures.append(f"{fragment_set}: best-intermediate {got_b:.16f} != "
                                f"deposited {want['best_intermediate']}")
            got_smiles = next(iter(smiles_seen))
            ok_s = got_smiles == want["smiles"]
            print(f"  [{'PASS' if ok_s else 'FAIL'}] best molecule {got_smiles}")
            if not ok_s:
                failures.append(f"{fragment_set}: best molecule {got_smiles} != deposited "
                                f"{want['smiles']}")
            if ok_t and ok_b:
                cleared[fragment_set] = (got_t, got_b)

        # p4_mcts_benchmark.py:269--275 used to assert the two conventions coincide "when
        # rewards are monotonically non-decreasing". They never did; report the gap that
        # falsified it.
        if got_b > got_t:
            print(f"  greedy walks downhill: best-intermediate exceeds terminal by "
                  f"{got_b - got_t:.4f} -- the two do NOT coincide")

    print()
    if failures:
        print(f"GREEDY RESCORE GATE: {len(failures)} FAILURE(S)")
        for f in failures:
            print(f"  - {f}")
        print("No value is cleared for the ledger.")
        return 1

    print("GREEDY RESCORE GATE: ALL CHECKS PASSED")
    print("cleared for the ledger (terminal -> best-intermediate):")
    for fragment_set, (t, b) in cleared.items():
        print(f"  {fragment_set:6s}: {t:.4f} -> {b:.4f}   (full precision {b!r})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
