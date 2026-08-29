"""Aggregate P6 calibration tertile results across all 7 arms and produce a single
status JSON. RRS-class-style stratification: data-driven per-MoA pos_rate tertiles
(no external ontology required)."""
import json
import glob
from pathlib import Path
from datetime import datetime, timezone

OUTD = Path("results/p6_phase2")
files = sorted(OUTD.glob("calibration/*_scaffold_tertile.json"))

arms_summary = {}
for f in files:
    d = json.loads(f.read_text())
    arm = f.stem.replace("_scaffold_tertile", "")
    pooled = d.get("calibration", {}).get("pooled", {})
    strata = d.get("calibration", {}).get("stratification", {}).get("strata", [])
    by_stratum = {s["stratum"]: {
        "n_labels": s["n_labels"],
        "pos_rate_pooled": round(s["pos_rate_pooled"], 6),
        "mean_pred_pooled": round(s["mean_pred_pooled"], 6),
        "brier_pooled": round(s["brier_pooled"], 6),
    } for s in strata}
    arms_summary[arm] = {
        "features": d.get("features"),
        "n_pooled": pooled.get("n", 0),
        "ece_pooled": round(pooled.get("ece", 0), 6),
        "mce_pooled": round(pooled.get("mce", 0), 6),
        "brier_pooled": round(pooled.get("brier", 0), 6),
        "strata": by_stratum,
    }

status = {
    "status": "COMPUTED_RRS_CLASS_PROXY_29AUG2026",
    "scheme": "pos_rate_tertile",
    "scheme_rationale": (
        "No canonical per-MoA RRS-class ontology exists for the LISH-MoA 206-label set. "
        "Stratification uses a data-driven per-MoA pos_rate tertile partition (low/mid/high) "
        "computed from observed positive-rates across the 25 scaffold-disjoint folds. "
        "Cut-points are derived from per-MoA pos_rate quantiles, not external labels."
    ),
    "n_labels": 206,
    "n_folds_per_arm": 25,
    "arms": arms_summary,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
}

out = OUTD / "p6_rrs_class_proxy_status.json"
out.write_text(json.dumps(status, indent=2, ensure_ascii=False))
print(f"Wrote {out}: status={status['status']}, arms={list(arms_summary)}")
print()
print(f"{'arm':10s}  {'ECE':>7s}  {'MCE':>7s}  {'Brier':>7s}  {'n':>10s}  brier_low    brier_mid    brier_high")
for arm, s in arms_summary.items():
    bl = s['strata'].get('low', {}).get('brier_pooled', 0)
    bm = s['strata'].get('mid', {}).get('brier_pooled', 0)
    bh = s['strata'].get('high', {}).get('brier_pooled', 0)
    print(f"  {arm:10s} {s['ece_pooled']:.4f}   {s['mce_pooled']:.4f}   {s['brier_pooled']:.4f}   {s['n_pooled']:>10d}   {bl:.4f}      {bm:.4f}      {bh:.4f}")
