#!/usr/bin/env python3
"""Aggregate the 16 Set-C MM-GBSA results into a summary + manifest.

For each system with a FINAL_RESULTS_MMPBSA.dat, parse the Delta-TOTAL line
(DeltaG_bind mean and propagated SD). Merge with the discriminative MD-RRS
metrics and the docking RRS from md_vs_docking_comparison_pilot.csv, and
compute MM-GBSA mutant/WT ratios (MMG_RRS) using the same convention as the
docking RRS (mutant/WT x 100; <100 = mutant binds weaker, i.e. looser).

Outputs:
  results/set_c_md/mmgbsa_summary_pilot.csv
  results/set_c_md/mmgbsa_manifest.json
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "results" / "set_c_md" / "mmgbsa_20260819"
COMPARISON = ROOT / "results" / "set_c_md" / "md_vs_docking_comparison_pilot.csv"
SUMMARY_CSV = ROOT / "results" / "set_c_md" / "mmgbsa_summary_pilot.csv"
MANIFEST = ROOT / "results" / "set_c_md" / "mmgbsa_manifest.json"


def parse_final(path: Path) -> dict | None:
    """Extract Delta-TOTAL (DeltaG_bind avg, SD) and frame count from a
    FINAL_RESULTS_MMPBSA.dat file."""
    text = path.read_text()
    m = re.search(r"Calculations performed using (\d+) complex frames", text)
    n_frames = int(m.group(1)) if m else None
    delta = None
    for line in text.splitlines():
        if re.match(r"^\s*(?:\u0394TOTAL|DELTA\s+TOTAL|Delta\s+TOTAL)\b", line):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    delta = {"mean_kcal_mol": float(parts[1]), "sd_kcal_mol": float(parts[2])}
                except ValueError:
                    continue
                break
    if delta is None:
        return None
    return {"n_frames": n_frames, **delta}


def main() -> int:
    results = {}
    for d in sorted(OUT_ROOT.iterdir()):
        if not d.is_dir():
            continue
        f = d / "FINAL_RESULTS_MMPBSA.dat"
        if not f.is_file():
            continue
        parsed = parse_final(f)
        if parsed is None:
            print(f"WARN: no Delta-TOTAL parsed for {d.name}", file=sys.stderr)
            continue
        results[d.name] = parsed

    if not results:
        print("No MM-GBSA results yet.", file=sys.stderr)
        return 1

    # docking comparison for dock_RRS + directions
    dock = {}
    if COMPARISON.is_file():
        for r in csv.DictReader(open(COMPARISON)):
            key = f"{r['set_c_id']}_{r['target']}_{r['mutation']}"
            dock[key] = {
                "dock_RRS": r.get("dock_RRS"),
                "MD_direction": r.get("MD_direction"),
                "dock_direction": r.get("dock_direction"),
            }

    rows = []
    for sys_name in sorted(results):
        parts = sys_name.split("_")  # PP-01_PfDHFR_WT
        set_c_id, target = parts[0], parts[1]
        mutation = "_".join(parts[2:])
        rows.append({
            "set_c_id": set_c_id,
            "target": target,
            "mutation": mutation,
            "system": sys_name,
            "mmgbsa_dg_kcal_mol": results[sys_name]["mean_kcal_mol"],
            "mmgbsa_sd_kcal_mol": results[sys_name]["sd_kcal_mol"],
            "n_frames": results[sys_name]["n_frames"],
            "dock_RRS": dock.get(sys_name, {}).get("dock_RRS", ""),
            "MD_direction": dock.get(sys_name, {}).get("MD_direction", ""),
            "dock_direction": dock.get(sys_name, {}).get("dock_direction", ""),
        })

    # MM-GBSA mutant/WT ratio per candidate+target (same convention as RRS)
    for r in rows:
        wt = next(
            (x for x in rows if x["set_c_id"] == r["set_c_id"]
             and x["target"] == r["target"] and x["mutation"] == "WT"), None)
        if wt is not None and wt["mmgbsa_dg_kcal_mol"] != 0:
            r["mmgbsa_rrs"] = (r["mmgbsa_dg_kcal_mol"] / wt["mmgbsa_dg_kcal_mol"]) * 100.0
        else:
            r["mmgbsa_rrs"] = ""

    fieldnames = ["set_c_id", "target", "mutation", "system",
                  "mmgbsa_dg_kcal_mol", "mmgbsa_sd_kcal_mol", "n_frames",
                  "mmgbsa_rrs", "dock_RRS", "MD_direction", "dock_direction"]
    with open(SUMMARY_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    manifest = {
        "schema_version": 1,
        "status": "MMGBSA_COMPUTED" if len(results) == 16 else f"PARTIAL_{len(results)}/16",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "gmx_MMPBSA v1.5.0.3, GB OBC2 (igb=5), salt 0.15 M, "
                    "dielectric 80/1, 100 ps snapshots (100 frames), CHARMM36-to-AMBER",
        "n_systems": len(results),
        "systems": {k: v for k, v in results.items()},
        "summary_csv": str(SUMMARY_CSV),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"status: {manifest['status']}")
    for r in rows:
        print(f"{r['system']:24s} dG={r['mmgbsa_dg_kcal_mol']:8.2f} +/- "
              f"{r['mmgbsa_sd_kcal_mol']:5.2f}  RRS={r['mmgbsa_rrs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
