#!/usr/bin/env python3
"""P1 V5 — docking-RRS pilot: per-target Resistance Resilience Score.

Input:  results/rrs_pilot/vina_scores/v5_mutant_vina_scores.csv
        (uniform protein-only receptor panel; jobs 12894 PfDHFR / 12895 PfCRT)
WT baselines: PfDHFR_WT (7F3Y frame), PfCRT_WT_K76 (T76K revertant, 6UKJ frame).

Protocol (mirrors P2 md_calculate_rrs_acsi_pns.py, per-target definition):
  RRS_{m,t} = |dG_mut,m,t| / |dG_WT,t| * 100
  averaged per compound over the mutants of each target for which the WT
  binding baseline is genuine (|dG_WT,t| >= 5.0 kcal/mol). Non-binding WT
  targets are excluded (no target mixing).

Classes (P2): A* (|dG_WT| >= 7.0 AND RRS >= 80% for every mutant), A (>=80%
every), B (>=70% every but not all >=80%), C (>=80% for a subset), D (<60%
for any mutant).

Status: PILOT — this artifact is NOT accepted for manuscript claims until the
independent structural review register is signed (accepted_for_full_run=true
AND all targets ACCEPTED; author decision 2026-08-08: independent review
MANDATORY, no internal-work bypass).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

V5 = Path(__file__).resolve().parents[1]
SCORES = V5 / "results/rrs_pilot/vina_scores/v5_mutant_vina_scores.csv"
REGISTER = V5 / "results/structural_pocket_independent_review.json"
OUT_CSV = V5 / "results/rrs_pilot/c_rrs_pilot_per_target_v5.csv"
# schema note: one row per (candidate, target) with that target's mutant RRS
# values — NOT the P2 c_rrs_classification.csv schema (one row per compound
# spanning both targets). P1.3's primary endpoint is target-specific retention.
OUT_PROV = V5 / "results/rrs_pilot/rrs_pilot_provenance.json"

WT_RECEPTORS = {"PfDHFR": "PfDHFR_WT", "PfCRT": "PfCRT_WT_K76"}
MUTANTS = {
    "PfDHFR": ["PfDHFR_N51I", "PfDHFR_C59R", "PfDHFR_S108N", "PfDHFR_I164L"],
    "PfCRT": ["PfCRT_K76T", "PfCRT_K76A"],
}
BINDING_THRESHOLD = 5.0  # |dG_WT,t| >= 5.0 kcal/mol = genuine binder


def classify(rrs: dict, dg_wt: float) -> str:
    """P2-exact classification (mirrors md_calculate_rrs_acsi_pns.classify_rrs).

    A*: all >=80 AND |dG_WT| >= 7.0 ; A: all >=80 ; B: all >=70 ;
    C: any >=80 ; D: otherwise.
    """
    vals = [v for k, v in rrs.items() if k != "WT" if v == v]
    if not vals:
        return "D"
    if all(v >= 80.0 for v in vals) and min(vals) >= 70.0:
        if dg_wt is not None and abs(dg_wt) >= 7.0:
            return "A*"
        return "A"
    if all(v >= 70.0 for v in vals):
        return "B"
    if any(v >= 80.0 for v in vals):
        return "C"
    return "D"


def main() -> int:
    if not SCORES.exists():
        print(f"FAIL-CLOSED missing scores: {SCORES} (jobs 12894/12895 not finished?)")
        return 1
    df = pd.read_csv(SCORES)
    reg = json.loads(REGISTER.read_text()) if REGISTER.exists() else {}
    accepted = bool(reg.get("accepted_for_full_run", False))

    rows = []
    for target, wt_label in WT_RECEPTORS.items():
        wt = df[(df["target"] == target) & (df["receptor"] == wt_label)]
        wt_map = {r["candidate_id"]: float(r["vina_affinity_kcal_mol"]) for _, r in wt.iterrows()}
        for cid, dg_wt in wt_map.items():
            if abs(dg_wt) < BINDING_THRESHOLD:
                continue  # non-binder: excluded per per-target protocol
            rrs_vals = {"WT": 100.0}
            for mlabel in MUTANTS[target]:
                m = df[(df["target"] == target) & (df["receptor"] == mlabel)
                       & (df["candidate_id"] == cid)]
                if m.empty:
                    rrs_vals[mlabel.split("_", 1)[1]] = float("nan")
                    continue
                dg_mut = float(m["vina_affinity_kcal_mol"].iloc[0])
                rrs_vals[mlabel.split("_", 1)[1]] = abs(dg_mut) / abs(dg_wt) * 100.0
            vals = [v for k, v in rrs_vals.items() if k != "WT" and v == v]
            rows.append({
                "candidate_id": cid, "target": target,
                "dG_WT_kcal_mol": round(dg_wt, 3),
                **{f"RRS_{k}": round(v, 1) for k, v in rrs_vals.items() if k != "WT"},
                "RRS_mean": round(float(np.mean(vals)), 1) if vals else None,
                "RRS_class": classify(rrs_vals, dg_wt),
            })

    out = pd.DataFrame(rows).sort_values(["target", "RRS_mean"], ascending=[True, False])
    out.to_csv(OUT_CSV, index=False)
    prov = {
        "schema": "p1-v5-rrs-pilot/v1",
        "status": "DOCKING_RRS_ACCEPTED" if accepted
                  else "DOCKING_RRS_PILOT_COMPUTED_PENDING_REVIEW",
        "accepted_for_full_run": accepted,
        "protocol": "per-target RRS = |dG_mut,t|/|dG_WT,t|*100, WT binding baseline "
                    "|dG_WT,t| >= 5.0 kcal/mol, no target mixing (P2 definition)",
        "wt_baselines": WT_RECEPTORS,
        "mutants": MUTANTS,
        "rows": len(out),
        "n_binders_dhfr": int((out["target"] == "PfDHFR").sum()),
        "n_binders_crt": int((out["target"] == "PfCRT").sum()),
        "note": "PILOT artifact; manuscript claims BLOCKED until the independent "
                "structural review register is signed (accepted_for_full_run=true "
                "AND all targets ACCEPTED).",
    }
    OUT_PROV.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")
    print(json.dumps(prov, indent=2, sort_keys=True))
    print("\n=== RRS classification (per target) ===")
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
