#!/usr/bin/env python3
"""P1 V5 — Fail-closed gate for consensus / RRS / PNS computation.

The V5 workflow requires an INDEPENDENTLY SIGNED structural review before any
scoring, consensus, RRS, or PNS may be computed from the four-target Vina
docking panel (jobs 12854/12855/12859/12864). This script is the enforcement
point: it checks `results/structural_pocket_independent_review.json` and
refuses to do anything unless `accepted_for_full_run` is true AND every target
decision is ACCEPTED.

Author decision 2026-08-08 (evening): the independent review is MANDATORY;
no internal-work bypass exists. An earlier session proposal to lift the
signature constraint for internal computation was rejected by the author and
is documented as such in the register (authorization_mode
INDEPENDENT_REVIEW_REQUIRED).

Usage:
    python scripts/p1_v5_consensus_rrs_gate.py            # check + refuse/allow
    python scripts/p1_v5_consensus_rrs_gate.py --status   # print register summary

The shared function `check_gate(register_path)` is imported by other V5
scripts (e.g. p1_v5_consensus_scoring.py) so authorization logic cannot drift.
This script intentionally performs NO scoring.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V5 = Path(__file__).resolve().parents[1]
REGISTER = V5 / "results/structural_pocket_independent_review.json"

REQUIRED_TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def check_gate(register_path: Path = REGISTER) -> tuple[bool, str]:
    """Return (allowed, message). Fail-closed: allowed only if the register is
    signed (accepted_for_full_run=true) and every required target decision is
    ACCEPTED."""
    if not register_path.exists():
        return False, f"FAIL-CLOSED: register missing: {register_path}"
    reg = json.loads(register_path.read_text())
    if not reg.get("accepted_for_full_run", False):
        return False, ("FAIL-CLOSED: independent structural review NOT signed — "
                       "no consensus/RRS/PNS computation permitted (V5 workflow).")
    for t in REQUIRED_TARGETS:
        d = reg.get("targets", {}).get(t, {})
        if d.get("decision") != "ACCEPTED":
            return False, (f"FAIL-CLOSED: target {t} decision="
                           f"{d.get('decision')} — not ACCEPTED")
    return True, ("GATE PASSED: independent review signed for all targets — "
                  "consensus/RRS/PNS computation is permitted.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", action="store_true",
                    help="print register summary and exit 0")
    args = ap.parse_args()

    if args.status:
        if not REGISTER.exists():
            print(f"FAIL-CLOSED: register missing: {REGISTER}")
            return 1
        reg = json.loads(REGISTER.read_text())
        print(f"status: {reg.get('status')}")
        print(f"reviewer: {reg.get('reviewer_identity')}  ({reg.get('review_date')})")
        print(f"accepted_for_full_run: {reg.get('accepted_for_full_run')}")
        auth = reg.get("authorization", {})
        print(f"authorization_mode: {auth.get('authorization_mode')} "
              f"(internal_work_authorized={auth.get('internal_work_authorized')})")
        for t in REQUIRED_TARGETS:
            d = reg.get("targets", {}).get(t, {})
            print(f"  {t}: {d.get('decision')}")
        return 0

    allowed, msg = check_gate(REGISTER)
    print(msg)
    return 0 if allowed else 1


if __name__ == "__main__":
    sys.exit(main())
