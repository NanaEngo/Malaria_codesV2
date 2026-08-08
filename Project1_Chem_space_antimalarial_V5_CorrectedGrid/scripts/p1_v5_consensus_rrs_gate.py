#!/usr/bin/env python3
"""
P1 V5 — Fail-closed gate for consensus / RRS / PNS computation.

The V5 workflow requires an INDEPENDENTLY SIGNED structural review before any
scoring, consensus, RRS, or PNS may be computed from the three-target Vina
docking panel (jobs 12854/12855/12859). This script is the enforcement point:
it checks `results/structural_pocket_independent_review.json` and refuses to
do anything unless `accepted_for_full_run` is true AND every target decision
is accepted.

Usage:
    python scripts/p1_v5_consensus_rrs_gate.py            # check + refuse/allow
    python scripts/p1_v5_consensus_rrs_gate.py --status   # print register summary

This script intentionally performs NO scoring. It exists so that no future
automation can compute consensus/RRS/PNS without an explicit signed register.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V5 = Path(__file__).resolve().parents[1]
REGISTER = V5 / "results/structural_pocket_independent_review.json"

REQUIRED_TARGETS = ["PfDHFR", "PfCRT", "PfClpP"]  # PfATP4 blocked (no anchor)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", action="store_true", help="print register summary and exit 0")
    args = ap.parse_args()

    if not REGISTER.exists():
        print(f"FAIL-CLOSED: register missing: {REGISTER}")
        return 1

    reg = json.loads(REGISTER.read_text())
    if args.status:
        print(f"status: {reg.get('status')}")
        print(f"reviewer: {reg.get('reviewer_identity')}  ({reg.get('review_date')})")
        print(f"accepted_for_full_run: {reg.get('accepted_for_full_run')}")
        for t in REQUIRED_TARGETS:
            d = reg.get("targets", {}).get(t, {})
            print(f"  {t}: {d.get('decision')}")
        print(f"  PfATP4: {reg.get('targets', {}).get('PfATP4', {}).get('decision')}")
        return 0

    accepted = reg.get("accepted_for_full_run", False)
    if not accepted:
        print("FAIL-CLOSED: independent structural review NOT signed — "
              "no consensus/RRS/PNS computation permitted (V5 workflow).")
        return 1
    for t in REQUIRED_TARGETS:
        d = reg.get("targets", {}).get(t, {})
        if d.get("decision") != "ACCEPTED":
            print(f"FAIL-CLOSED: target {t} decision={d.get('decision')} — not ACCEPTED")
            return 1
    print("GATE PASSED: independent review signed for all three targets — "
          "consensus/RRS/PNS computation is permitted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
