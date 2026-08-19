#!/usr/bin/env python
"""RETIRED 2026-08-17 — v11-era verifier. Do not run against the v12 manuscript.

Original purpose: verify the P4 v11 canonical checks (diversity CSV == SM table,
benchmark CSV stats == SM/abstract, provenance re-pass).

Why it is retired rather than ported. Every check group in this file asserts a v11
value, and the manuscript, the benchmark directory and one of the two input CSVs have
all since been regenerated for v12:

  * the diversity expectations (mcts 0.8023, random 0.7806, ga 0.8332/17/0.85) no
    longer match results/diversity/p4_diversity_metrics.csv itself, which now holds the
    v12 values 0.7732, 0.8046 and 0.7761/12/0.600 -- so these checks fail against the
    live artifact, not merely against the manuscript;
  * the benchmark block reads results/benchmark_molecules_opt/, superseded by
    results/benchmark_molecules_opt_v12/;
  * the canonical rewards 0.7335/0.7276/0.7027/0.6147 are v12's 0.6724/0.6649/
    0.6453/0.4278; the paired statistics t=-2.41 (p=0.026) and t_ga=5.55 are v12's
    t=-4.97 (p=0.000085) and 6.95; the seed-win count 5/20 is 1/20; and the mean
    wall-clock times 82.2 s / 42.4 s are 92.1 s / 50.4 s, both outside the +/-5 s
    tolerance coded below;
  * the string checks against the two .tex files look for v11 reward literals and the
    phrase "\\num{5} of \\num{20} seeds", none of which appear in the v12 sources.

Porting would therefore mean replacing roughly thirty expected constants and the input
directory -- that is, writing a new verifier -- and the v12 equivalents already exist:

  * scripts/p4_pareto_provenance_check.py   Pareto front, active objectives, HV 1.2366
  * scripts/p4_n2_power_test.py             selection-ablation dHV statistics
  * the 2026-08-17 from-primary-source recomputation recorded in
    manuscript/LaTeX/SUBMISSION_MANIFEST.md (factorial and vocabulary ablations,
    diversity, reward weight vectors, RF activity-oracle panel)

The v11 expectations below are kept verbatim as the historical v11 record. Execution is
gated so that a future reader cannot run this file, see a wall of FAIL lines, and
conclude the v12 manuscript is wrong. To run it for v11 archaeology against a v11
checkout, set P4_RUN_RETIRED_V11_CHECKS=1.

Tracked as O10 in project-tracking.md.
"""
import csv
import os
import sys

_RETIRED_NOTICE = """\
p4_verify_v11_checks.py is RETIRED (2026-08-17) and did not run.

It asserts v11 values and reads the superseded results/benchmark_molecules_opt/
directory; every check group in it fails against the v12 manuscript, and the diversity
block fails against the current results/diversity/p4_diversity_metrics.csv as well. It
is kept only as the historical v11 record -- see the module docstring.

For v12 provenance use instead:
  python scripts/p4_pareto_provenance_check.py
  python scripts/p4_n2_power_test.py
plus the 2026-08-17 recomputation notes in manuscript/LaTeX/SUBMISSION_MANIFEST.md.

Set P4_RUN_RETIRED_V11_CHECKS=1 to run it anyway against a v11 checkout.
"""

if os.environ.get("P4_RUN_RETIRED_V11_CHECKS") != "1":
    # Exit 0: "retired, deliberately not run" is not a verification failure, so a
    # harness that sweeps scripts/p4_verify_*.py must not go red on this file.
    print(_RETIRED_NOTICE)
    sys.exit(0)

ROOT = os.path.dirname(os.path.abspath(__file__))
P4 = os.path.join(os.path.dirname(ROOT))  # Project4 dir
ok = True

def check(name, cond, detail=""):
    global ok
    status = "OK " if cond else "FAIL"
    if not cond:
        ok = False
    print(f"  [{status}] {name} {detail}")

print("=== 1. Diversity metrics CSV == SM values ===")
div_path = os.path.join(P4, "results/diversity/p4_diversity_metrics.csv")
rows = {}
with open(div_path) as f:
    for r in csv.DictReader(f):
        rows[r["method"]] = r

expect = {
    "mcts":   ("0.8023", "19", "0.95"),
    "random": ("0.7806", "20", "1.0"),
    "greedy": ("0.0",    "1",  "0.05"),
    "ga":     ("0.8332", "17", "0.85"),
}
for m, (diss, nsc, frac) in expect.items():
    got = (rows[m]["mean_pairwise_tanimoto_dissimilarity"],
           rows[m]["n_unique_bm_scaffolds"],
           rows[m]["unique_scaffold_fraction"])
    check(f"diversity[{m}]", got == (diss, nsc, frac), f"CSV {got} vs expected {(diss, nsc, frac)}")

sm_path = os.path.join(P4, "manuscript/LaTeX/P4_Pareto_MCTS_JoC_SM.tex")
with open(sm_path) as f:
    sm = f.read()
for val in ["0.8023", "0.7806", "0.8332", "0.0000", "0.95", "1.0", "0.85", "0.05"]:
    check(f"SM contains {val}", val in sm)

print("=== 2. Benchmark v11 merged CSV stats ===")
merged = os.path.join(P4, "results/benchmark_molecules_opt/p4_benchmark_merged.csv")
data = {}
with open(merged) as f:
    for r in csv.DictReader(f):
        m = r["method"]
        if m not in data:
            data[m] = {"reward": [], "time": []}
        data[m]["reward"].append(float(r["reward"]))
        data[m]["time"].append(float(r["elapsed_s"]))

import statistics
canon = {"random": (0.7335, 0.0063), "mcts": (0.7276, 0.0090),
         "ga": (0.7027, 0.0152), "greedy": (0.6147, 0.0)}
for m, (mean, sd) in canon.items():
    r = data[m]["reward"]
    m_mean, m_sd = statistics.mean(r), statistics.stdev(r) if len(r) > 1 else 0.0
    check(f"benchmark[{m}] mean", abs(m_mean - mean) < 5e-4,
          f"computed {m_mean:.4f} vs canonical {mean}")
    check(f"benchmark[{m}] sd", abs(m_sd - sd) < 5e-4,
          f"computed {m_sd:.4f} vs canonical {sd}")
    check(f"benchmark[{m}] n=20", len(r) == 20, f"n={len(r)}")

# paired MCTS vs Random
import itertools
rm = data["random"]["reward"]
mm = data["mcts"]["reward"]
diffs = [mm[i] - rm[i] for i in range(20)]
dbar = statistics.mean(diffs)
sd = statistics.stdev(diffs)
t = dbar / (sd / (20 ** 0.5))
from math import erf, sqrt

def ttest_p(t, df):
    # two-sided p via regularized incomplete beta (student-t survival)
    x = df / (df + t * t)
    # use scipy if available
    try:
        from scipy import stats as st
        return st.t.sf(abs(t), df) * 2
    except ImportError:
        return float("nan")

p = ttest_p(t, 19)
check("MCTS vs Random t=-2.41 p=0.026", abs(t - (-2.41)) < 0.05 and abs(p - 0.026) < 0.005,
      f"t={t:.3f} p={p:.4f}")

ga = data["ga"]["reward"]
diffs_ga = [mm[i] - ga[i] for i in range(20)]  # MCTS - GA (manuscript convention)
dbar_ga = statistics.mean(diffs_ga)
sd_ga = statistics.stdev(diffs_ga)
t_ga = dbar_ga / (sd_ga / (20 ** 0.5))
p_ga = ttest_p(t_ga, 19)
check("MCTS vs GA t=5.55 p<0.0001", abs(t_ga - 5.55) < 0.1 and p_ga < 0.0001,
      f"t={t_ga:.3f} p={p_ga:.4f}")

# wins: MCTS best seed beats Random best seed count
wins = sum(1 for i in range(20) if mm[i] > rm[i])
check("MCTS wins 5/20 seeds", wins == 5, f"wins={wins}")

# timing
check("MCTS time ~82.2s", abs(statistics.mean(data["mcts"]["time"]) - 82.2) < 5,
      f"mean={statistics.mean(data['mcts']['time']):.1f}s")
check("Random time ~42.4s", abs(statistics.mean(data["random"]["time"]) - 42.4) < 5,
      f"mean={statistics.mean(data['random']['time']):.1f}s")

print("=== 3. SM/abstract contains v11 narrative ===")
main_path = os.path.join(P4, "manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex")
with open(main_path) as f:
    main = f.read()
for phrase in ["0.7276", "0.0090", "0.7335", "0.0063", "0.7027", "0.0152",
               "0.6147", "ScafVAE"]:
    check(f"main contains {phrase}", phrase in main)
check("main: MCTS wins 5 of 20 seeds", "\\num{5} of \\num{20} seeds" in main)

print()
print("=== RESULT ===")
print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
