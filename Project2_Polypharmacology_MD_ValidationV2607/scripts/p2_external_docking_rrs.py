#!/usr/bin/env python3
"""Post-process the external docking replication into RRS.

Reads the integrity-audited aggregate (external_docking_scores.csv) and
computes the frozen P2 RRS estimand per target:

    RRS = |S_mutant,t| / |S_WT,t| x 100,

with target-specific WT denominators below 5.0 kcal/mol excluded
(|S_WT,t| < 5.0 => target not a binder for that compound). Following the
canonical P2 pipeline, RRS is averaged per mutant across binding targets,
and the compound is classified on the per-mutant RRS profile.

This is a docking replication of the RRS pattern on a non-overlapping
external panel. It is NOT experimental validation and NOT an MD estimate;
all outputs carry that boundary.
"""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/results/robustness_transfer_20260827"
AGG = BASE / "external_docking_aggregate_20260827"
SCORES = AGG / "external_docking_scores.csv"
OUT_CSV = BASE / "external_docking_rrs_20260827.csv"
OUT_JSON = BASE / "external_docking_rrs_20260827.json"
WT_THRESHOLD = 5.0  # kcal/mol; WT below this => non-binder, target excluded

# Declared EMBED_FAILURE (frozen plan + repair ledger): no ligand PDBQT exists,
# so its states are absent from the aggregate. The RRS panel is therefore
# 39 ligands x 8 states = 312 records (was 320 before the declared exclusion).
DECLARED_EMBED_FAILURES = {"EXT-039"}

MUTATIONS = ["N51I", "C59R", "S108N", "I164L", "K76T", "K76A"]
TARGETS = ["PfDHFR", "PfCRT"]


def parse_state(state: str) -> tuple[str, str] | None:
    """Split 'PfDHFR_WT' -> ('PfDHFR', 'WT'); 'PfCRT_K76T' -> ('PfCRT', 'K76T')."""
    for target in TARGETS:
        if state == f"{target}_WT":
            return target, "WT"
        for mut in MUTATIONS:
            if state == f"{target}_{mut}":
                return target, mut
    return None


def classify_rrs(rrs_values: dict) -> str:
    """Dual-criterion classification identical to the canonical P2 estimand."""
    mutant_rrs = {k: v for k, v in rrs_values.items() if k != "WT"}
    if not mutant_rrs:
        return "D"
    vals = list(mutant_rrs.values())
    if all(v >= 80 for v in vals) and min(vals) >= 70:
        return "A"
    if all(v >= 70 for v in vals):
        return "B"
    if any(v >= 80 for v in vals):
        return "C"
    return "D"


def main() -> int:
    if not SCORES.is_file():
        print("ERROR: aggregate scores not found; run p2_external_docking_aggregate.py first")
        return 2

    rows = list(csv.DictReader(SCORES.open(newline="")))
    # 39 ligands x 8 states = 312 (EXT-) which is declared EMBED_FAILURE, so its
    #   states are intentionally absent from the aggregate.
    eligible_ids = {r["external_panel_id"]
                    for r in rows} | DECLARED_EMBED_FAILURES
    expected = (len({r["external_panel_id"] for r in rows}) * 8)
    if len(rows) != expected:
        print(f"ERROR: expected {expected} aggregate records, found {len(rows)}; aborting fail-closed")
        return 2

    # integrity re-check: every record must parse to a known (target, mutation)
    bad = [r["state"] for r in rows if parse_state(r["state"]) is None]
    if bad:
        print(f"ERROR: {len(bad)} unrecognized states: {sorted(set(bad))[:5]}... aborting fail-closed")
        return 2

    records = []
    for pid in sorted({r["external_panel_id"] for r in rows}):
        compound_rows = [r for r in rows if r["external_panel_id"] == pid]
        # WT scores per target (single record per state in the aggregate)
        wt_by_target = {}
        for target in TARGETS:
            wt = [r for r in compound_rows if parse_state(r["state"]) == (target, "WT")]
            if wt:
                wt_by_target[target] = float(wt[0]["vina_score_kcal_mol"])
        binding_targets = {t: d for t, d in wt_by_target.items() if abs(d) >= WT_THRESHOLD}

        # per-mutant RRS: mean over binding targets that have that mutant
        rrs_vals: dict[str, float] = {}
        for mut in MUTATIONS:
            ratios = []
            for target in binding_targets:
                m = [r for r in compound_rows if parse_state(r["state"]) == (target, mut)]
                if not m:
                    continue
                dg_mut = float(m[0]["vina_score_kcal_mol"])
                ratios.append(abs(dg_mut) / abs(binding_targets[target]) * 100.0)
            if ratios:
                rrs_vals[mut] = round(sum(ratios) / len(ratios), 1)

        row_out = {"external_panel_id": pid}
        for target in TARGETS:
            if target in binding_targets:
                row_out[f"S_WT_{target}"] = round(binding_targets[target], 2)
            else:
                row_out[f"S_WT_{target}"] = "excluded_nonbinder"
        for mut, v in rrs_vals.items():
            row_out[f"RRS_{mut}"] = v
        if rrs_vals:
            row_out["RRS_mean"] = round(sum(rrs_vals.values()) / len(rrs_vals), 1)
            row_out["RRS_class"] = classify_rrs(rrs_vals)
        else:
            row_out["RRS_mean"] = ""
            row_out["RRS_class"] = "D"
        row_out["binding_targets"] = len(binding_targets)
        records.append(row_out)

    records.sort(key=lambda r: (r.get("RRS_mean") is None, -(r.get("RRS_mean") or 0)))

    # summary
    classes: dict[str, int] = {}
    for r in records:
        classes[r["RRS_class"]] = classes.get(r["RRS_class"], 0) + 1
    n_binders = sum(1 for r in records if r.get("binding_targets", 0) > 0)

    fieldnames = (["external_panel_id", "S_WT_PfDHFR", "S_WT_PfCRT"] +
                  [f"RRS_{m}" for m in MUTATIONS] + ["RRS_mean", "RRS_class", "binding_targets"])
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    summary = {
        "schema_version": 1,
        "status": "COMPUTED_EXTERNAL_DOCKING_RRS_REPLICATION",
        "estimand": "RRS = |S_mutant,t| / |S_WT,t| x 100; WT non-binders (|S_WT| < 5.0 kcal/mol) excluded per target; RRS averaged per mutant across binding targets",
        "boundary": "Docking-derived replication on a non-overlapping external panel; NOT experimental validation, NOT an MD estimate",
        "n_compounds": len(records),
        "n_records": len(rows),
        "declared_embed_failures": sorted(DECLARED_EMBED_FAILURES),
        "panel_exclusion_note": "EXT-039 declared EMBED_FAILURE (no 3D coordinates under RDKit DG / random-coords / OBabel gen3d); its 8 states are intentionally absent, panel target = 39 ligands x 8 states = 312 records",
        "class_counts": classes,
        "n_with_binding_target": n_binders,
        "aggregate_sha256": hashlib.sha256(SCORES.read_bytes()).hexdigest(),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
