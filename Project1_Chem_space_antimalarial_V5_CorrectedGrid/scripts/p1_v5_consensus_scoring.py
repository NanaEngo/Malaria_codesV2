#!/usr/bin/env python3
"""P1 V5 — four-target consensus scoring on the locked 17x4 Vina panel.

Input:   results/v5_four_target_vina_affinities.csv (17 candidates x 4 targets,
         machine-verified, jobs 12854/12855/12859/12864).
Gate:    technical input/QC checks remain active. During
         `PRE_SUBMISSION_DEVELOPMENT`, no editorial or independent-review
         restriction blocks scientific calculation; outputs retain their
         NOT_SUBMISSION_READY provenance label. A signed-review gate is dormant
         until the author explicitly requests reactivation after submission.
Output:  results/v5_consensus_four_target.csv + provenance JSON.

Consensus = per-candidate mean binding affinity over COMPLETED targets only
(no missing-target imputation). Ranks by strongest mean affinity (most
negative = best consensus binder).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

V5 = Path(__file__).resolve().parents[1]
REPO = V5.parent
sys.path.insert(0, str(V5 / "scripts"))
from p1_v5_consensus_rrs_gate import check_gate, REGISTER  # noqa: E402
from p1_development_policy import is_pre_submission, phase_name  # noqa: E402

INPUT_CSV = V5 / "results/v5_four_target_vina_affinities.csv"
OUT_CSV = V5 / "results/v5_consensus_four_target.csv"
OUT_PROV = V5 / "results/v5_consensus_four_target_provenance.json"
EXPLORATORY_DIR = V5 / "results/exploratory"

TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--internal-development",
        action="store_true",
        help=(
            "run an explicitly quarantined exploratory calculation when the "
            "submission gate is closed; never writes canonical outputs"
        ),
    )
    args = ap.parse_args()

    # The phase file is the authoritative workflow switch. The CLI flag remains
    # a backward-compatible explicit quarantine option, but is not required
    # during PRE_SUBMISSION_DEVELOPMENT.
    explicit_internal = args.internal_development or os.environ.get(
        "P1_V5_INTERNAL_DEVELOPMENT", ""
    ).lower() in {"1", "true", "yes"}
    try:
        pre_submission = is_pre_submission()
    except RuntimeError as exc:
        print(f"FAIL-CLOSED: {exc}")
        return 1
    internal_development = explicit_internal or pre_submission
    if explicit_internal and not pre_submission:
        print("SUBMISSION REVIEW GATE CLOSED: explicit exploratory mode requires author reactivation policy")
        return 1
    allowed, msg = check_gate(REGISTER)
    print(msg)
    if not allowed and not internal_development:
        return 1
    if not allowed:
        print(
            "INTERNAL_DEVELOPMENT: submission gate remains closed; "
            "writing quarantined exploratory outputs only."
        )

    # Explicit development intent always wins: even a later-signed register
    # cannot make a development invocation write submission-facing outputs.
    out_csv = OUT_CSV if (allowed and not internal_development) else EXPLORATORY_DIR / "v5_consensus_four_target_exploratory.csv"
    out_prov = OUT_PROV if (allowed and not internal_development) else EXPLORATORY_DIR / "v5_consensus_four_target_exploratory_provenance.json"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
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
    out.to_csv(out_csv, index=False)

    prov = {
        "schema": "p1-v5-consensus-four-target/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": ("CONSENSUS_SUBMISSION_READY" if (allowed and not internal_development)
                    else "PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY"),
        "gate": msg,
        "internal_development": bool(internal_development),
        "development_phase": phase_name() if internal_development else None,
        "accepted_for_full_run": bool(allowed and not internal_development),
        "submission_eligible": bool(allowed and not internal_development),
        "input": str(INPUT_CSV.relative_to(V5)),
        "n_candidates": len(out),
        "n_targets": 4,
        "aggregation": "mean over completed targets only, no imputation",
        "ranking": "strongest (most negative) consensus mean first",
        "note": (
            "Computed after the independent structural review register was signed."
            if allowed else
            "Development artifact only. The independent structural review "
            "register is unsigned; this output retains exploratory provenance. "
            "It may guide ongoing science and drafting, but must be re-audited "
            "if the author later requests submission-facing promotion."
        ),
        "output_csv": str(out_csv.relative_to(V5)),
        "phase": phase_name(),
    }
    out_prov.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

    print("\n=== Consensus 4-target (signed-review gate) ===")
    show = out[["consensus_rank", "candidate_id", "n_completed_targets",
                "consensus_mean_kcal_mol", "consensus_min_kcal_mol", "consensus_max_kcal_mol"]]
    print(show.to_string(index=False))
    print(f"\nOutput: {out_csv.relative_to(V5)}  |  provenance: {out_prov.relative_to(V5)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
