#!/usr/bin/env python3
"""P4 — Pareto provenance lock (P0-1, submission blocking).

Verifies that every SMILES + score in the 4-point canonical merged Pareto front
(results/pareto/merged_pareto_front.csv) is traceable to the deposited per-seed
Pareto CSVs (results/pareto/p4_pareto_seed_*.csv) and that the post-hoc SYBA
recomputation is reproducible with the lich/conda classifier.

Checks:
  1. Each front SMILES exists in its per-seed CSV with identical
     MPO / SA / RRS / PNS (SYBA is expected to differ: the original run
     returned a constant zero fallback and SYBA was recomputed post-hoc).
  2. The 4 front points are mutually non-dominated and the hypervolume
     equals the deposited value (1.2366).
  3. Re-running the SYBA classifier reproduces syba_raw and normalised syba
     stored in merged_pareto_front.csv / merged_pareto_front_recompute.log.
  4. The manuscript's SA^-1 display values match (10 - SA)/9 for SA=3.0.

Usage:
    python scripts/p4_pareto_provenance_check.py

Exit code 0 if all checks pass, 1 otherwise.

NOTE: this script embeds the manuscript's displayed values (e.g. SYBA 1.000,
SA^-1 0.778). If the manuscript LaTeX tables change, update the embedded
values in lockstep.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
PARETO_DIR = PROJECT_DIR / "results" / "pareto"
MERGED_CSV = PARETO_DIR / "merged_pareto_front.csv"
RECOMPUTE_LOG = PARETO_DIR / "merged_pareto_front_recompute.log"

# v12: 6 objectives — the public-activity oracle is a Pareto objective.
# Historical v11 artifacts lack the activity column; scores.get(obj, 0.0)
# yields a constant 0 there, which _detect_active_objectives auto-excludes.
OBJECTIVES = ["mpo", "syba", "sa", "rrs", "pns", "activity"]
MAXIMIZE = [True, True, False, True, True, True]

# Manuscript Table 2 (tab:pareto) as rendered in P4_Pareto_MCTS_JoC_refined.tex
MANUSCRIPT_TABLE = {
    "P1": {"mpo": 0.910, "syba": 1.000, "sa_inv": 0.778, "rrs": 0.211, "pns": 1.0},
    "P2": {"mpo": 0.945, "syba": 1.000, "sa_inv": 0.778, "rrs": 0.196, "pns": 1.0},
    "P3": {"mpo": 0.946, "syba": 0.021, "sa_inv": 0.778, "rrs": 0.141, "pns": 0.0},
    "P4": {"mpo": 0.729, "syba": 0.994, "sa_inv": 0.778, "rrs": 0.223, "pns": 1.0},
}
MANUSCRIPT_HYPERVOLUME = 1.2366

FAILURES: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not cond:
        FAILURES.append(label)


def normalize_syba(raw: float) -> float:
    """Same sigmoid used in p4_mcts_oracles.py / p4_recompute_pareto_syba.py."""
    return 1.0 / (1.0 + math.exp(-raw / 5.0))


def load_per_seed_rows(seed: int) -> list[dict]:
    path = PARETO_DIR / f"p4_pareto_seed_{seed}.csv"
    if not path.exists():
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    print("=" * 72)
    print("P4 PARETO PROVENANCE LOCK")
    print("=" * 72)

    # ── 0. Load merged front ──────────────────────────────────────────────
    with open(MERGED_CSV, newline="") as fh:
        merged = list(csv.DictReader(fh))
    print(f"\n[0] Merged front: {len(merged)} rows from {MERGED_CSV.name}")
    check(len(merged) == 4, "merged front has exactly 4 points", f"got {len(merged)}")

    # ── 1. Per-seed provenance ────────────────────────────────────────────
    print("\n[1] Per-seed provenance (SMILES + MPO/SA/RRS/PNS must match; SYBA recomputed):")
    for row in merged:
        seed = int(row["seed"])
        smi = row["smiles"]
        per_seed = load_per_seed_rows(seed)
        match = next((r for r in per_seed if r["smiles"] == smi), None)
        if match is None:
            check(False, f"seed {seed}: SMILES not found in p4_pareto_seed_{seed}.csv",
                  smi[:50])
            continue
        same = all(
            abs(float(match[k]) - float(row[k])) < 1e-6
            for k in ["mpo", "sa", "rrs", "pns"]
        )
        check(same, f"seed {seed} P{seed}: MPO/SA/RRS/PNS identical to per-seed CSV",
              f"front_size={len(per_seed)}")
        # SYBA must differ: per-seed holds the original constant-0 fallback
        syba_differs = abs(float(match["syba"]) - float(row["syba"])) > 1e-6
        check(syba_differs,
              f"seed {seed}: SYBA differs from per-seed (documented post-hoc recompute)",
              f"per-seed={match['syba']} -> merged={row['syba']}")

    # ── 2. Non-dominance + hypervolume ────────────────────────────────────
    print("\n[2] Non-dominance + hypervolume (ParetoFront on MPO/SYBA/SA/RRS/PNS):")
    sys.path.insert(0, str(SCRIPT_DIR))
    from p4_mcts_pareto import ParetoFront  # type: ignore

    front = ParetoFront(objectives=OBJECTIVES, maximize=MAXIMIZE)
    for row in merged:
        front.update(row["smiles"], {k: float(row[k]) for k in OBJECTIVES},
                     {"seed": row["seed"]})
    sols = front.solutions
    check(len(sols) == 4, "all 4 merged points mutually non-dominated",
          f"front size={len(sols)}")
    hv = front.hypervolume()
    check(abs(hv - MANUSCRIPT_HYPERVOLUME) < 1e-3,
          "hypervolume matches manuscript 1.2366", f"recomputed={hv:.4f}")
    active = front._detect_active_objectives()
    inactive = [o for o, a in zip(OBJECTIVES, active) if not a]
    check("sa" in inactive,
          "SA excluded from HV as constant (sa=3.0 for all points)",
          f"inactive objectives={inactive}")
    print(f"    active objectives: "
          f"{[o for o, a in zip(OBJECTIVES, active) if a]}")

    # ── 3. SYBA recomputation reproducibility ─────────────────────────────
    print("\n[3] SYBA post-hoc recomputation (lich/conda classifier):")
    log = json.loads(RECOMPUTE_LOG.read_text())
    from syba.syba import SybaClassifier  # type: ignore

    syba = SybaClassifier()
    syba.fitDefaultScore()
    for row in merged:
        smi = row["smiles"]
        raw = float(syba.predict(smi))
        norm = normalize_syba(raw)
        raw_ok = abs(raw - float(row["syba_raw"])) < 1e-3
        norm_ok = abs(norm - float(row["syba"])) < 1e-3
        check(raw_ok and norm_ok,
              f"SYBA reproducible: {smi[:44]:44s}",
              f"raw={raw:9.3f} (CSV {row['syba_raw'][:9]})  "
              f"norm={norm:.4f} (CSV {row['syba']})")
    check(len(log["solutions"]) == 4, "recompute log records 4 non-dominated solutions")
    check(abs(log["hypervolume"] - MANUSCRIPT_HYPERVOLUME) < 1e-3,
          "recompute log hypervolume matches 1.2366",
          f"log hv={log['hypervolume']:.4f}")

    # ── 4. Manuscript display values ──────────────────────────────────────
    print("\n[4] Manuscript Table 2 display values vs merged CSV:")
    sa_inv_expected = (10.0 - 3.0) / 9.0
    # explicit mapping by MPO to keep this readable
    mpo_to_label = {"0.9103": "P1", "0.9447": "P2", "0.9463": "P3", "0.7285": "P4"}
    for row in merged:
        label = mpo_to_label.get(f"{float(row['mpo']):.4f}", "?")
        man = MANUSCRIPT_TABLE.get(label)
        if man is None:
            continue
        mpo_ok = abs(float(row["mpo"]) - man["mpo"]) < 1e-3
        syba_ok = abs(float(row["syba"]) - man["syba"]) < 1e-3
        sa_inv_ok = abs(sa_inv_expected - man["sa_inv"]) < 1e-3
        rrs_ok = abs(float(row["rrs"]) - man["rrs"]) < 1e-3
        pns_ok = abs(float(row["pns"]) - man["pns"]) < 1e-3
        check(mpo_ok and rrs_ok and pns_ok,
              f"{label}: MPO/RRS/PNS match manuscript",
              f"MPO {row['mpo']} RRS {row['rrs']} PNS {row['pns']}")
        check(syba_ok,
              f"{label}: SYBA matches manuscript",
              f"CSV {row['syba']} vs manuscript {man['syba']}")
        check(sa_inv_ok,
              f"{label}: SA^-1=(10-SA)/9 matches manuscript",
              f"(10-3)/9={sa_inv_expected:.3f} vs manuscript {man['sa_inv']}")

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    if FAILURES:
        print(f"PROVENANCE LOCK: {len(FAILURES)} FAILURE(S)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("PROVENANCE LOCK: ALL CHECKS PASSED")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
