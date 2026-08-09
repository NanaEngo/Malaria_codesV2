#!/usr/bin/env python3
"""
P4 — Recompute SYBA for the canonical merged Pareto front and recalculate
the Pareto front / hypervolume across the active objectives.

Usage:
    python scripts/p4_recompute_pareto_syba.py

Output:
    results/pareto/merged_pareto_front.csv  (updated)
    results/pareto/merged_pareto_front_recompute.log
"""

import csv
import json
import math
from pathlib import Path

import numpy as np
from p4_mcts_pareto import ParetoFront

# ── Paths ───────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
CSV_PATH = PROJECT_DIR / "results" / "pareto" / "merged_pareto_front.csv"
LOG_PATH = PROJECT_DIR / "results" / "pareto" / "merged_pareto_front_recompute.log"


def normalize_syba(raw: float) -> float:
    """Same sigmoid used in p4_mcts_oracles.py."""
    return 1.0 / (1.0 + math.exp(-raw / 5.0))


def main() -> None:
    from syba.syba import SybaClassifier

    syba = SybaClassifier()
    syba.fitDefaultScore()

    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)

    # Read the existing merged front. This utility is intentionally scoped to
    # the deposited pre-activity Pareto front; never silently drop a v12
    # activity column if someone points it at a different artifact.
    rows = []
    with open(CSV_PATH) as fh:
        reader = csv.DictReader(fh)
        fields = set(reader.fieldnames or [])
        if "activity" in fields:
            raise ValueError(
                "Refusing to rewrite a v12 activity-bearing CSV: "
                "p4_recompute_pareto_syba.py only handles the pre-activity "
                "canonical Pareto front."
            )
        for row in reader:
            rows.append(row)

    print(f"Read {len(rows)} pre-activity rows from {CSV_PATH}")

    # Recompute SYBA for each molecule
    updated = []
    for row in rows:
        smi = row["smiles"]
        raw = float(syba.predict(smi))
        norm = normalize_syba(raw)
        row = dict(row)  # copy
        row["syba_raw"] = f"{raw:.6f}"
        row["syba"] = f"{norm:.4f}"
        updated.append((smi, row))
        print(f"  {smi[:40]:40s}  raw={raw:8.2f}  norm={norm:.4f}")

    # Recompute the deposited canonical Pareto front. The public-activity
    # term belongs to the v12 scalar benchmark; it was not part of the
    # historical Pareto-MCTS run and must not be added retroactively here.
    objectives = ["mpo", "syba", "sa", "rrs", "pns"]
    maximize = [True, True, False, True, True]
    front = ParetoFront(objectives=objectives, maximize=maximize)

    for smi, row in updated:
        scores = {k: float(row[k]) for k in objectives}
        front.update(smi, scores)

    sols = front.solutions
    hv = front.hypervolume()
    active = front._detect_active_objectives()

    print(f"Varying objectives after SYBA re-derivation: {[o for a, o in zip(active, objectives) if a]}")
    print(f"Front size after SYBA recompute: {len(sols)}")
    print(f"Hypervolume after SYBA recompute: {hv:.4f}")

    # Map back to rows, preserving only non-dominated solutions
    non_dominated_smiles = {sol[0] for sol in sols}
    final_rows = [row for smi, row in updated if smi in non_dominated_smiles]

    # Write updated merged CSV
    with open(CSV_PATH, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "smiles", "mpo", "syba", "sa", "rrs", "pns",
            "syba_raw", "hypervolume", "seed",
        ])
        for row in final_rows:
            writer.writerow([
                row["smiles"],
                row["mpo"],
                row["syba"],
                row["sa"],
                row["rrs"],
                row["pns"],
                row["syba_raw"],
                f"{hv:.4f}",
                row["seed"],
            ])

    # Log
    log = {
        "input_csv": str(CSV_PATH.relative_to(PROJECT_DIR)),
        "n_input": len(rows),
        "n_non_dominated": len(final_rows),
        "hypervolume": hv,
        "active_objectives": [o for a, o in zip(active, objectives) if a],
        "solutions": [
            {
                "smiles": row["smiles"],
                "mpo": row["mpo"],
                "syba": row["syba"],
                "syba_raw": row["syba_raw"],
                "sa": row["sa"],
                "rrs": row["rrs"],
                "pns": row["pns"],
                "seed": row["seed"],
            }
            for row in final_rows
        ],
    }
    LOG_PATH.write_text(json.dumps(log, indent=2))
    print(f"Updated {CSV_PATH}")
    print(f"Log written to {LOG_PATH}")


if __name__ == "__main__":
    main()
