#!/usr/bin/env python3
"""Discriminative MD-RRS for the Set-C pilot: multi-threshold bound fractions.

The canonical pilot MD-RRS uses a single binary threshold (min heavy-atom
protein--ligand distance < 5.0 A), which saturates at bound_fraction = 1.000
for all 16 systems over 10 ns: the metric cannot resolve partial affinity loss.
This script re-analyzes the *existing* production trajectories (no new MD) and
reports a continuous, non-saturating family of metrics:

- bound_fraction at thresholds 2.0, 2.5, 3.0, 3.5, 4.0, 5.0 A;
- mean and 5th-percentile of the per-frame minimum heavy-atom distance;
- MD-RRS_d = 100 * mutant_metric / WT_metric for each continuous metric,
  per target and per candidate, with WT defined as the same-target WT system.

The output is a fail-closed manifest; no claim of affinity equality or of a
validated resistance phenotype is made. The result is a *ceiling-corrected*
descriptive diagnostic for PP-01/PP-02 only (same scope boundary as the pilot).

Usage:
    P2_SETC_ROOT=... python scripts/p2_setc_md_rrs_discriminative.py
        [--qc-csv results/set_c_md/set_c_trajectory_qc_pilot.csv]
        [--output-dir results/set_c_md]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
DEFAULT_QC_CSV = RESULTS_DIR / "set_c_md" / "set_c_trajectory_qc_pilot.csv"
THRESHOLDS_A = [2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
MIN_FRAMES = 500


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def per_frame_min_distances(tpr: Path, xtc: Path, max_frames: int = 2000) -> np.ndarray:
    """Return the per-frame protein--ligand minimum heavy-atom distance array."""
    import MDAnalysis as mda
    from MDAnalysis.lib.distances import distance_array

    universe = mda.Universe(str(tpr), str(xtc))
    protein = universe.select_atoms("protein and name C N O S")
    ligand = universe.select_atoms(
        "not protein and not water and not resname NA CL and not resname SOL"
    )
    if len(protein) == 0 or len(ligand) == 0:
        raise RuntimeError(f"selection failed: protein={len(protein)} ligand={len(ligand)}")
    min_dists = []
    for ts in universe.trajectory:
        dists = distance_array(ligand.positions, protein.positions, box=ts.dimensions)
        min_dists.append(dists.min())
        if len(min_dists) >= max_frames:
            break
    return np.asarray(min_dists, dtype=float)


def metrics_from_distances(min_dists: np.ndarray) -> dict:
    """Continuous metrics from a per-frame min-distance array."""
    n = len(min_dists)
    out = {"n_frames": n}
    if n == 0:
        return out
    for thr in THRESHOLDS_A:
        out[f"bound_frac_{thr:g}A"] = float(np.mean(min_dists < thr))
    out["mean_min_dist_A"] = float(min_dists.mean())
    out["p5_min_dist_A"] = float(np.percentile(min_dists, 5))
    out["median_min_dist_A"] = float(np.median(min_dists))
    return out


def md_rrs_ratio(mutant: dict, wt: dict, field: str) -> float | None:
    """MD-RRS_d = 100 * mutant / WT for a continuous metric (mutant larger => weaker binding)."""
    m, w = mutant.get(field), wt.get(field)
    if m is None or w is None or not np.isfinite(m) or not np.isfinite(w) or w == 0:
        return None
    return float(100.0 * m / w)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--qc-csv", type=Path, default=DEFAULT_QC_CSV)
    ap.add_argument("--output-dir", type=Path, default=RESULTS_DIR / "set_c_md")
    ap.add_argument("--max-frames", type=int, default=2000)
    args = ap.parse_args()
    qc_csv = args.qc_csv.resolve()
    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    qc = pd.read_csv(qc_csv)
    qc = qc[qc["qc_status"] == "PASS"].copy()
    if len(qc) != 16:
        raise SystemExit(f"FAIL-CLOSED: expected 16 PASS rows, found {len(qc)}")

    records = []
    for row in qc.itertuples(index=False):
        tpr = Path(row.tpr_path)
        xtc = Path(row.trajectory_path)
        if not tpr.is_file() or not xtc.is_file():
            raise SystemExit(f"FAIL-CLOSED: missing trajectory inputs for {row.set_c_id}_{row.target}_{row.mutation}")
        dists = per_frame_min_distances(tpr, xtc, max_frames=args.max_frames)
        if len(dists) < MIN_FRAMES:
            raise SystemExit(f"FAIL-CLOSED: {row.set_c_id}_{row.target}_{row.mutation} frames={len(dists)}")
        m = metrics_from_distances(dists)
        m.update(
            {
                "set_c_id": row.set_c_id,
                "target": row.target,
                "mutation": row.mutation,
                "trajectory_sha256": row.trajectory_sha256,
            }
        )
        records.append(m)
        print(
            f"{row.set_c_id}_{row.target}_{row.mutation}: "
            f"mean_min={m['mean_min_dist_A']:.2f} A p5={m['p5_min_dist_A']:.2f} "
            f"bf2A={m['bound_frac_2A']:.3f} bf3A={m['bound_frac_3A']:.3f} bf5A={m['bound_frac_5A']:.3f}"
        )

    df = pd.DataFrame(records)
    df.to_csv(out_dir / "set_c_trajectory_metrics_pilot.csv", index=False)

    # MD-RRS ratios per target per candidate (mutant / same-target WT)
    ratio_fields = ["mean_min_dist_A", "p5_min_dist_A", "median_min_dist_A"] + [
        f"bound_frac_{thr:g}A" for thr in THRESHOLDS_A
    ]
    rrs_rows = []
    for set_c_id in sorted(df["set_c_id"].unique()):
        sub = df[df["set_c_id"] == set_c_id]
        for target in sorted(sub["target"].unique()):
            tgt = sub[sub["target"] == target]
            wt = tgt[tgt["mutation"] == "WT"]
            if len(wt) != 1:
                print(f"SKIP ratio: {set_c_id}/{target} has {len(wt)} WT rows")
                continue
            wt_m = wt.iloc[0].to_dict()
            for mut in tgt[tgt["mutation"] != "WT"].itertuples(index=False):
                mut_m = mut._asdict()
                row = {"set_c_id": set_c_id, "target": target, "mutation": mut.mutation}
                for field in ratio_fields:
                    row[f"MD_RRS_{field}"] = md_rrs_ratio(mut_m, wt_m, field)
                rrs_rows.append(row)
    rrs = pd.DataFrame(rrs_rows)
    rrs.to_csv(out_dir / "md_rrs_discriminative_pilot.csv", index=False)
    print("\n=== MD-RRS discriminative (mutant/WT x 100) ===")
    print(rrs[["set_c_id", "target", "mutation", "MD_RRS_mean_min_dist_A", "MD_RRS_bound_frac_3A"]].to_string(index=False))

    # Fail-closed manifest
    manifest = {
        "schema_version": 1,
        "status": "MD_RRS_DISCRIMINATIVE_COMPUTED",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_rule_id": "setc_p2_multithreshold_continuous_v1",
        "input_qc_csv": str(qc_csv),
        "qc_csv_sha256": sha256(qc_csv),
        "thresholds_A": THRESHOLDS_A,
        "metric_definition": "per-frame protein--ligand min heavy-atom distance; "
        "bound_frac_T = fraction of frames with min distance < T; "
        "MD_RRS_d = 100 * mutant_metric / WT_metric",
        "scope": "PP-01/PP-02 pilot only; descriptive diagnostic, not affinity proof",
        "saturation_note": "bound_frac at 5 A saturates near 1.0 over 10 ns; "
        "stricter thresholds and continuous distances are the discriminative layer",
        "records": len(records),
        "rows": records,
        "ratios": rrs_rows,
    }
    manifest_path = out_dir / "md_rrs_discriminative_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nManifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
