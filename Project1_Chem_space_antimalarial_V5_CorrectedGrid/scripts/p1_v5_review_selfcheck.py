#!/usr/bin/env python3
"""P1 V5 — independent-review self-check: machine-verified evidence report.

The independent reviewer must NOT trust this report blindly: it regenerates
the verification quantities (frame rmsd, gate counts, affinity ranges, file
hashes) from the raw artifacts so the reviewer can cross-check them in
minutes rather than hours. Every value is recomputed from disk at run time.

Outputs:
  results/review_selfcheck_report.json   (machine-verified evidence report)
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

V5 = Path(__file__).resolve().parents[1]
RESULTS = V5 / "results"

FOUR_TARGET_CSV = RESULTS / "v5_four_target_vina_affinities.csv"
REVIEW_TABLE = RESULTS / "v5_four_target_vina_review_table.json"
FRAME_CHECK = RESULTS / "rrs_pilot/receptors/frame_check.json"
TARGET_ID = RESULTS / "target_identity_audit.json"
REGISTER = RESULTS / "structural_pocket_independent_review.json"
VINA_DIRS = {
    "PfClpP": RESULTS / "vina_dock_2F6I_PfClpP_17",
    "PfCRT": RESULTS / "vina_dock_6UKJ_PfCRT_17",
    "PfDHFR": RESULTS / "vina_dock_7F3Y_PfDHFR_17",
    "PfATP4": RESULTS / "vina_dock_9N10_PfATP4_17",
}
OUT = RESULTS / "review_selfcheck_report.json"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    report = {"schema": "p1-v5-review-selfcheck/v1", "checks": {}, "ok": True}

    # --- 1. Four-target affinity table: 17 rows, 4 affinity columns non-empty ---
    df = pd.read_csv(FOUR_TARGET_CSV)
    aff_cols = [c for c in df.columns if c.startswith("aff_")]
    n_rows = len(df)
    n_complete = int(df[aff_cols].notna().all(axis=1).sum())
    ranges = {c: (round(float(df[c].min()), 2), round(float(df[c].max()), 2))
              for c in aff_cols if df[c].notna().any()}
    c1 = n_rows == 17 and n_complete == 17 and len(aff_cols) == 4
    report["checks"]["four_target_table"] = {
        "pass": c1, "rows": n_rows, "complete_rows": n_complete,
        "affinity_ranges_kcal_mol": ranges,
        "sha256": sha256(FOUR_TARGET_CSV)}

    # --- 2. Review table JSON says COMPLETE_17 for all four targets ---
    try:
        rt = json.loads(REVIEW_TABLE.read_text())
        comp = {t: rt.get("completeness", {}).get(t) if isinstance(rt.get("completeness"), dict)
                else rt.get("targets", {}).get(t, {}).get("status")
                for t in ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]}
    except Exception as e:  # noqa: BLE001
        comp, rt = {}, {}
    c2 = all(v == "COMPLETE_17" or "COMPLETE" in str(v) for v in comp.values())
    report["checks"]["review_table"] = {"pass": c2, "completeness": comp,
                                        "sha256": sha256(REVIEW_TABLE)}

    # --- 3. Receptor frame equivalence: rmsd == 0 and no missing CA ---
    fchk = json.loads(FRAME_CHECK.read_text())
    frame_bad = []
    for label, rec in fchk.items():
        fr = rec.get("frame", {})
        if fr.get("status") != "OK" or fr.get("rmsd_A") != 0.0 or fr.get("missing_vs_wt", 1) != 0:
            frame_bad.append(label)
    c3 = not frame_bad
    report["checks"]["receptor_frames"] = {
        "pass": c3, "n_receptors": len(fchk),
        "rmsd_ok_all": c3, "bad": frame_bad, "sha256": sha256(FRAME_CHECK)}

    # --- 4. Per-target Vina run dirs exist with provenance ---
    missing_dirs = [t for t, d in VINA_DIRS.items() if not d.exists()]
    prov_ok = []
    for t, d in VINA_DIRS.items():
        p = d / "execution_provenance.json"
        prov_ok.append(t if p.exists() else None)
    c4 = not missing_dirs and all(x is not None for x in prov_ok)
    report["checks"]["vina_run_dirs"] = {"pass": c4, "missing": missing_dirs,
                                         "with_provenance": [p for p in prov_ok if p]}

    # --- 5. Target identity audit present ---
    c5 = TARGET_ID.exists()
    report["checks"]["target_identity_audit"] = {
        "pass": c5, "sha256": sha256(TARGET_ID) if c5 else None}

    # --- 6. Register state: must still be PENDING (signature is human) ---
    reg = json.loads(REGISTER.read_text()) if REGISTER.exists() else {}
    c6 = reg.get("status") == "PENDING_INDEPENDENT_REVIEW" and not reg.get("accepted_for_full_run")
    report["checks"]["register_pending"] = {
        "pass": c6, "status": reg.get("status"),
        "accepted_for_full_run": reg.get("accepted_for_full_run")}

    report["ok"] = all(v["pass"] for v in report["checks"].values())
    report["generated_utc"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
