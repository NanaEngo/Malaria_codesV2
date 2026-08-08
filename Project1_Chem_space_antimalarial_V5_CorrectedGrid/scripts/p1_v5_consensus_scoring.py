#!/usr/bin/env python3
"""P1 V5 — four-target consensus scoring on the locked 17x4 Vina panel.

Input:   results/v5_four_target_vina_affinities.csv (17 candidates x 4 targets,
         machine-verified, jobs 12854/12855/12859/12864).
Gate:    strict fail-closed via `p1_v5_consensus_rrs_gate.check_gate` — refuses
         unless the independent structural review register is signed
         (accepted_for_full_run=true AND all four targets ACCEPTED).
         Author decision 2026-08-08 (evening): the independent review is
         MANDATORY; no internal-work bypass exists.
Output:  results/v5_consensus_four_target.csv + provenance JSON.

Consensus = per-candidate mean binding affinity over COMPLETED targets only
(no missing-target imputation). Ranks by strongest mean affinity (most
negative = best consensus binder).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

V5 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V5 / "scripts"))
from p1_v5_consensus_rrs_gate import check_gate, REGISTER  # noqa: E402

INPUT_CSV = V5 / "results/v5_four_target_vina_affinities.csv"
OUT_CSV = V5 / "results/v5_consensus_four_target.csv"
OUT_PROV = V5 / "results/v5_consensus_four_target_provenance.json"

TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()

    allowed, msg = check_gate(REGISTER)
    print(msg)
    if not allowed:
        return 1
    if not INPUT_CSV.exists():
        print(f"FAIL-CLOSED missing input: {INPUT_CSV}")
        return 1

    df = pd.read_csv(INPUT_CSV)
    rows = []
    for _, r in df.iterrows():
        vals = {t: float(r[f"aff_{t}"]) for t in TARGETS if pd.notna(r.get(f"aff_{t}"))}
        completed = len(vals)
        mean = sum(vals.values()) / completed if completed else float("nan")
        rows.append({
            "candidate_id": r["candidate_id"],
            **{f"aff_{t}": vals.get(t) for t in TARGETS},
            "n_completed_targets": completed,
            "consensus_mean_kcal_mol": round(mean, 3) if completed else None,
            "consensus_min_kcal_mol": round(min(vals.values()), 3) if completed else None,
            "consensus_max_kcal_mol": round(max(vals.values()), 3) if completed else None,
        })
    out = pd.DataFrame(rows)
    out = out.sort_values("consensus_mean_kcal_mol", ascending=True, na_position="last")
    out.insert(0, "consensus_rank", range(1, len(out) + 1))
    out.to_csv(OUT_CSV, index=False)

    prov = {
        "schema": "p1-v5-consensus-four-target/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONSENSUS_SUBMISSION_READY",
        "gate": msg,
        "input": str(INPUT_CSV.relative_to(V5)),
        "n_candidates": len(out),
        "n_targets": 4,
        "aggregation": "mean over completed targets only, no imputation",
        "ranking": "strongest (most negative) consensus mean first",
        "note": "Computed only after the independent structural review register "
                "is signed (accepted_for_full_run=true, all targets ACCEPTED).",
    }
    OUT_PROV.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

    print("\n=== Consensus 4-target (signed-review gate) ===")
    show = out[["consensus_rank", "candidate_id", "n_completed_targets",
                "consensus_mean_kcal_mol", "consensus_min_kcal_mol", "consensus_max_kcal_mol"]]
    print(show.to_string(index=False))
    print(f"\nOutput: {OUT_CSV.relative_to(V5)}  |  provenance: {OUT_PROV.relative_to(V5)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
