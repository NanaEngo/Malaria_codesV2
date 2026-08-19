#!/usr/bin/env python
"""Independent re-derivation of the P4 Pareto hypervolume, written from the spec.

Purpose. scripts/p4_pareto_provenance_check.py verifies 1.2366 by calling the same
ParetoArchive.hypervolume() that produced it, so it cannot detect an error in that
method. This file re-implements the documented algorithm from scratch and computes the
hypervolume by exact inclusion--exclusion over the dominated boxes -- no pymoo in the
primary path, no import from p4_mcts_pareto -- so a disagreement localises to the
algorithm rather than to the data.

Algorithm re-implemented, per scripts/p4_mcts_pareto.py:168--198:
  1. drop objectives that are constant across the front (here: sa = 3.0 everywhere);
  2. multiply maximised objectives by -1 (pymoo minimisation convention);
  3. min-max normalise each surviving column to [0, 1];
  4. reference point 1.1 in every active dimension;
  5. hypervolume = volume of the union of the boxes [point, ref].

Step 5 is where this file is genuinely independent. For n points the union volume is
exact by inclusion--exclusion,

    HV = sum over nonempty S of (-1)^(|S|+1) * prod_d max(0, ref_d - max_{p in S} p_d)

which is tractable here because the merged front holds 4 points (2^4 - 1 = 15 terms) and
needs no dimension-sweep algorithm at all.

Gate. The three-objective figure 1.1244 quoted in
outputs/critical-reviews/review-claim-ledger-20260817.md is checker-reported and was
never re-derived. It is only trustworthy if the same implementation first reproduces the
published four-objective 1.2366, so this script refuses to report the three-objective
values as verified unless the four-objective check passes.

Reads results/pareto/merged_pareto_front.csv (read-only). Writes nothing.

Usage:
    /home/tchapet/VirtualEnv/bin/python3 scripts/p4_hv_independent_recheck.py
Exit 0 if the four-objective value reproduces 1.2366; nonzero otherwise.
"""
from __future__ import annotations

import csv
import itertools
import os
import sys

OBJECTIVES = ["mpo", "syba", "sa", "rrs", "pns"]
# scripts/p4_mcts_pareto.py:599 -- maximize=[True, True, False, True, True]
MAXIMIZE = {"mpo": True, "syba": True, "sa": False, "rrs": True, "pns": True}

MANUSCRIPT_HV = 1.2366
MANUSCRIPT_ACTIVE = ["mpo", "syba", "rrs", "pns"]
CHECKER_THREE_OBJ_HV = 1.124376  # review-claim-ledger-20260817.md, quoted there as 1.1244
REF = 1.1
TOL = 5e-5  # the manuscript prints 4 decimal places

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONT = os.path.join(ROOT, "results", "pareto", "merged_pareto_front.csv")


def load_front(path: str) -> tuple[list[str], list[list[float]]]:
    """Return (smiles, rows) with one row of len(OBJECTIVES) floats per front point."""
    smiles: list[str] = []
    rows: list[list[float]] = []
    with open(path) as fh:
        for rec in csv.DictReader(fh):
            missing = [k for k in OBJECTIVES if k not in rec]
            if missing:
                raise SystemExit(f"{path}: missing objective columns {missing}")
            smiles.append(rec["smiles"])
            rows.append([float(rec[k]) for k in OBJECTIVES])
    if not rows:
        raise SystemExit(f"{path}: no rows")
    return smiles, rows


def active_objectives(rows: list[list[float]]) -> list[str]:
    """Objectives that vary across the front, in OBJECTIVES order."""
    active = []
    for j, name in enumerate(OBJECTIVES):
        col = [r[j] for r in rows]
        if max(col) - min(col) > 1e-10:
            active.append(name)
    return active


def normalise(rows: list[list[float]], names: list[str]) -> list[list[float]]:
    """Sign-flip maximised columns, then min-max each to [0, 1]."""
    idx = [OBJECTIVES.index(n) for n in names]
    signed = [[(-1.0 if MAXIMIZE[n] else 1.0) * r[j] for n, j in zip(names, idx)]
              for r in rows]
    lo = [min(p[c] for p in signed) for c in range(len(names))]
    hi = [max(p[c] for p in signed) for c in range(len(names))]
    out = []
    for p in signed:
        row = []
        for c in range(len(names)):
            span = hi[c] - lo[c]
            row.append((p[c] - lo[c]) / (span if span > 1e-10 else 1.0))
        out.append(row)
    return out


def hypervolume_exact(points: list[list[float]], ref: float = REF) -> float:
    """Union volume of the boxes [p, ref], by inclusion--exclusion. Exact, no library."""
    k = len(points[0])
    total = 0.0
    for size in range(1, len(points) + 1):
        for subset in itertools.combinations(points, size):
            vol = 1.0
            for c in range(k):
                edge = ref - max(p[c] for p in subset)
                if edge <= 0.0:
                    vol = 0.0
                    break
                vol *= edge
            if vol:
                total += vol if size % 2 else -vol
    return total


def main() -> int:
    rows = load_front(FRONT)[1]
    active = active_objectives(rows)
    print(f"front: {len(rows)} points from {os.path.relpath(FRONT, ROOT)}")
    print(f"active objectives: {active}   (constant, dropped: "
          f"{[o for o in OBJECTIVES if o not in active]})")

    failures: list[str] = []
    if active != MANUSCRIPT_ACTIVE:
        failures.append(f"active set {active} != manuscript {MANUSCRIPT_ACTIVE}")

    hv4 = hypervolume_exact(normalise(rows, active))
    bound4 = REF ** len(active)
    ok4 = abs(hv4 - MANUSCRIPT_HV) < TOL
    print(f"\n[{'PASS' if ok4 else 'FAIL'}] {len(active)}-objective HV = {hv4:.6f} "
          f"vs manuscript {MANUSCRIPT_HV}  (bound {REF}^{len(active)} = {bound4:.4f})")
    if not ok4:
        failures.append(f"4-objective HV {hv4:.6f} != {MANUSCRIPT_HV}")

    # Cross-check the exact routine against pymoo, if pymoo is importable. This checks
    # the inclusion--exclusion code, not the manuscript. pymoo's Hypervolume.do is
    # typed Optional, so a None is treated as a skipped cross-check rather than
    # crashing or silently comparing against nothing.
    pm: float | None = None
    try:
        import numpy as np
        from pymoo.indicators.hv import Hypervolume

        raw = Hypervolume(ref_point=np.ones(len(active)) * REF).do(
            np.array(normalise(rows, active)))
        pm = None if raw is None else float(raw)
    except ImportError:
        pm = None

    if pm is None:
        print("[SKIP] pymoo unavailable -- exact routine not cross-checked")
    else:
        agree = abs(pm - hv4) < 1e-9
        print(f"[{'PASS' if agree else 'FAIL'}] inclusion--exclusion agrees with pymoo "
              f"({pm:.6f})")
        if not agree:
            failures.append(f"inclusion--exclusion {hv4:.6f} != pymoo {pm:.6f}")

    # Three-objective variants: which 3-subset, if any, gives the checker's 1.124376?
    # Two of the four subsets agree with it to 4 decimal places while differing at the
    # 5th, so the 4-dp form "1.1244" does not identify the subset -- flag the two cases
    # separately rather than reporting a match twice.
    print("\nthree-objective recomputes (each drops one active objective):")
    for drop in active:
        sub = [o for o in active if o != drop]
        hv3 = hypervolume_exact(normalise(rows, sub))
        delta = abs(hv3 - CHECKER_THREE_OBJ_HV)
        if delta < 1e-6:
            hit = f"  <-- IS the checker figure {CHECKER_THREE_OBJ_HV}"
        elif delta < 5e-4:
            hit = "  (4-dp collision with it, differs at the 5th -- not the same value)"
        else:
            hit = ""
        print(f"  drop {drop:5s} -> {sub} HV = {hv3:.6f}"
              f"  (bound {REF ** len(sub):.4f}){hit}")

    if not ok4:
        print("\nFour-objective check FAILED, so the three-objective values above are "
              "NOT verified -- fix the four-objective disagreement first.")

    print()
    if failures:
        print(f"HV RECHECK: {len(failures)} FAILURE(S)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("HV RECHECK: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
