#!/usr/bin/env python3
"""8quater secondary analyses — per-target bootstrap RRS CI95 + MD-filter gate.

RUN1 — Per-target bootstrap RRS CI95 (B=10k, seed 42).
  Bootstrap CI95 on the canonical Set-C cohort (c_rrs_classification.csv):
  class fractions (A*/A/B/C/D) and per-target retention fractions, plus the
  external panel (external_docking_rrs_20260827.csv).

RUN2 — MD-filter retention gate (pilot scope PP-01/PP-02 only).
  Docking RRS >= 80 (class A*) AND pilot MD-RRS retention (< 100, tighter-or-
  equal parity) per candidate/target from md_rrs_discriminative_pilot.csv;
  candidates passing on >= 2 targets are polypharma-promoted at pilot scope.
  Uses mmgbsa_ddeltaG_pilot.csv only for context in the output.

All outputs are SECONDARY; no canonical value is replaced.
"""
from __future__ import annotations
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/results"
OUT_DIR = BASE / "rrs_polypharma_secondary_20260828"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RNG = random.Random(42)
B = 10_000
CI = (0.025, 0.975)

MUTATIONS = ["N51I", "C59R", "S108N", "I164L", "K76T", "K76A"]


def boot_ci(values: list[float]) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    means = []
    n = len(values)
    for _ in range(B):
        sample = [RNG.choice(values) for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    return (means[int(CI[0] * B)], means[int(CI[1] * B) - 1])


def boot_frac_ci(flags: list[bool]) -> tuple[float, float]:
    if not flags:
        return (float("nan"), float("nan"))
    fracs = []
    n = len(flags)
    for _ in range(B):
        s = [RNG.choice(flags) for _ in range(n)]
        fracs.append(sum(s) / n)
    fracs.sort()
    return (fracs[int(CI[0] * B)], fracs[int(CI[1] * B) - 1])


def fnum(v) -> float | None:
    if v in (None, "", "nan", "n/a", "NaN"):
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------
# RUN1 — bootstrap RRS CI95 on the Set-C cohort
# --------------------------------------------------------------------------
def run1() -> dict:
    rows = list(csv.DictReader((BASE / "c_rrs_classification.csv").open(newline="")))
    out = {"n_candidates": len(rows)}
    # class fractions (canonical RRS_class)
    classes = [r.get("RRS_class", "") for r in rows if r.get("RRS_class")]
    for cls in ["A*", "A", "B", "C", "D"]:
        flags = [c == cls for c in classes]
        out[f"class_{cls}_fraction"] = {
            "point": round(sum(flags) / len(flags), 4) if flags else None,
            "ci95": [round(v, 4) for v in boot_frac_ci(flags)],
        }
    # per-target retention fractions (RRS_<mutant> columns, pooled across
    # eligible candidates; WT = 100 by construction)
    for mut in MUTATIONS:
        col = f"RRS_{mut}"
        vals = [fnum(r.get(col)) for r in rows]
        vals = [v for v in vals if v is not None]
        if vals:
            out[f"retention_{mut}"] = {
                "point": round(sum(vals) / len(vals), 2),
                "ci95": [round(v, 2) for v in boot_ci(vals)],
                "n": len(vals),
            }
    # per-target mean RRS (PfDHFR / PfCRT)
    for tgt in ["PfDHFR", "PfCRT"]:
        vals = [fnum(r.get(f"RRS_mean_{tgt}")) for r in rows]
        vals = [v for v in vals if v is not None]
        if vals:
            out[f"mean_RRS_{tgt}"] = {
                "point": round(sum(vals) / len(vals), 2),
                "ci95": [round(v, 2) for v in boot_ci(vals)],
                "n": len(vals),
            }
    return out


# --------------------------------------------------------------------------
# RUN1b — bootstrap on the external panel
# --------------------------------------------------------------------------
def run1b() -> dict:
    rows = list(csv.DictReader(
        (BASE / "robustness_transfer_20260827/external_docking_rrs_20260827.csv").open(newline="")))
    rrs_means = [fnum(r.get("RRS_mean")) for r in rows]
    rrs_means = [v for v in rrs_means if v is not None]
    cls_a = [r.get("RRS_class") == "A" for r in rows if r.get("RRS_class")]
    return {
        "n_ligands": len(rows),
        "mean_RRS": {
            "point": round(sum(rrs_means) / len(rrs_means), 2) if rrs_means else None,
            "ci95": [round(v, 2) for v in boot_ci(rrs_means)],
        },
        "class_A_fraction": {
            "point": round(sum(cls_a) / len(cls_a), 4) if cls_a else None,
            "ci95": [round(v, 4) for v in boot_frac_ci(cls_a)],
        },
    }


# --------------------------------------------------------------------------
# RUN2 — MD-filter retention gate (pilot scope only)
# --------------------------------------------------------------------------
def run2() -> dict:
    md = list(csv.DictReader((BASE / "set_c_md/md_rrs_discriminative_pilot.csv").open(newline="")))
    dock = list(csv.DictReader((BASE / "c_rrs_classification.csv").open(newline="")))
    # docking RRS per (candidate, target) from the canonical table
    dock_rrs = {}
    for r in dock:
        cand = r.get("candidate_id")
        for tgt in ["PfDHFR", "PfCRT"]:
            mean_col = f"RRS_mean_{tgt}"
            v = fnum(r.get(mean_col))
            if cand and v is not None:
                dock_rrs.setdefault(cand, {})[tgt] = v
    gate_rows = []
    for r in md:
        cand = r.get("set_c_id")
        tgt = r.get("target")
        md_rrs = fnum(r.get("MD_RRS_mean_min_dist_A"))
        if not cand or not tgt or md_rrs is None:
            continue
        dock_val = dock_rrs.get(cand, {}).get(tgt)
        passes_dock = dock_val is not None and dock_val >= 80.0
        passes_md = md_rrs < 100.0
        gate_rows.append({
            "candidate": cand,
            "target": tgt,
            "docking_rrs": round(dock_val, 1) if dock_val is not None else None,
            "md_rrs": round(md_rrs, 1),
            "docking_gate_ge80": passes_dock,
            "md_gate_lt100": passes_md,
            "passes_both": passes_dock and passes_md,
        })
    by_cand = {}
    for g in gate_rows:
        if g["passes_both"]:
            by_cand.setdefault(g["candidate"], set()).add(g["target"])
    promoted = {c: sorted(t) for c, t in by_cand.items() if len(t) >= 2}
    return {
        "scope": "PP-01/PP-02 pilot only; full-panel (17x8) MD-RRS remains NOT_COMPUTED",
        "n_gate_rows": len(gate_rows),
        "n_passes_both": sum(1 for g in gate_rows if g["passes_both"]),
        "polypharma_promoted_pilot": promoted,
        "gate_rows": gate_rows,
    }


def main() -> int:
    r2 = run2()
    summary = {
        "status": "COMPUTED_SECONDARY",
        "bootstrap": {"B": B, "seed": 42, "ci": "95%"},
        "run1_setc_bootstrap": run1(),
        "run1b_external_bootstrap": run1b(),
        "run2_md_filter_gate": {k: v for k, v in r2.items() if k != "gate_rows"},
        "boundary": "Secondary post-processing (28 Aug 2026); no canonical value replaced; MD gate is pilot-scope only.",
    }
    (OUT_DIR / "secondary_summary.json").write_text(json.dumps(summary, indent=2))
    cols = ["candidate", "target", "docking_rrs", "md_rrs",
            "docking_gate_ge80", "md_gate_lt100", "passes_both"]
    with open(OUT_DIR / "md_filter_gate.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(r2["gate_rows"])
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
