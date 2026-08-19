#!/usr/bin/env python3
"""Compute MD-derived set-C RRS from trajectory-QC measurements.

This script intentionally does not infer binding from docking scores, filenames,
or missing trajectories.  A separate, reproducible trajectory-QC step must
write a CSV containing one validated bound-fraction measurement per
candidate/target/mutation.  The required ``analysis_rule_id`` records the
pre-specified trajectory rule (for example, a minimum protein--ligand distance
threshold and frame fraction) and is carried into the output.

Required input columns (``--qc-file``):
    set_c_id, target, mutation, smiles, bound_fraction, n_frames,
    duration_ns, trajectory_sha256, qc_status, analysis_rule_id,
    candidate_sha256

Only ``qc_status == PASS`` rows with 0 <= bound_fraction <= 1 and a 64-character
trajectory hash are accepted.  MD-RRS is defined per target as
100 * bound_fraction_mut / bound_fraction_WT, averaged only over targets whose
WT bound fraction is >= ``--min-wt-bound-fraction``.  This is explicitly an
MD-derived resilience proxy, not the docking-RRS definition.

Two explicit contracts are supported:
- ``--cohort-mode full``: all 17 canonical candidates and 136 QC rows;
- ``--cohort-mode pilot``: the predeclared PP-01/PP-02 pilot and 16 QC rows.
Pilot mode writes ``md_rrs_pilot_PP01_PP02.csv`` and refuses to overwrite the
full-cohort output. It must not be used to make a claim about all 17 candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
CANDIDATE_FILE = RESULTS_DIR / "candidate_selection" / "md_top20_candidates_polypharm.csv"
TARGET_MUTATIONS = {
    "PfDHFR": ["WT", "N51I", "C59R", "S108N", "I164L"],
    "PfCRT": ["WT", "K76T", "K76A"],
}
PILOT_CANDIDATE_IDS = {"PP-01", "PP-02"}
FULL_COHORT_ID = "P2_SET_C_POLYPHARM_17"
PILOT_COHORT_ID = "P2_SET_C_MD_RRS_PILOT_PP01_PP02"
FULL_OUTPUT = RESULTS_DIR / "set_c_md" / "md_rrs_classification.csv"
PILOT_OUTPUT = RESULTS_DIR / "set_c_md" / "md_rrs_pilot_PP01_PP02.csv"
REQUIRED = {
    "set_c_id", "target", "mutation", "smiles", "bound_fraction", "n_frames",
    "duration_ns", "trajectory_path", "tpr_path", "trajectory_sha256", "tpr_sha256", "qc_status", "analysis_rule_id", "candidate_sha256",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qc-file", type=Path, required=True, help="Trajectory-QC bound-fraction CSV")
    parser.add_argument(
        "--cohort-mode",
        choices=("full", "pilot"),
        default="full",
        help="Use the complete 17-candidate contract or the predeclared PP-01/PP-02 pilot contract.",
    )
    parser.add_argument("--min-wt-bound-fraction", type=float, default=0.10)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def classify(values: list[float]) -> str:
    if not values:
        return "D"
    if all(value >= 80.0 for value in values):
        return "A"
    if all(value >= 70.0 for value in values):
        return "B"
    if any(value >= 80.0 for value in values):
        return "C"
    return "D"


def main() -> int:
    args = parse_args()
    if not 0 < args.min_wt_bound_fraction <= 1:
        raise SystemExit("--min-wt-bound-fraction must be in (0, 1]")
    if not args.qc_file.exists():
        raise SystemExit(f"QC file not found: {args.qc_file}")
    expected_ids = set(PILOT_CANDIDATE_IDS) if args.cohort_mode == "pilot" else None
    cohort_id = PILOT_COHORT_ID if args.cohort_mode == "pilot" else FULL_COHORT_ID
    output = args.output or (PILOT_OUTPUT if args.cohort_mode == "pilot" else FULL_OUTPUT)
    if args.cohort_mode == "pilot" and output.resolve() == FULL_OUTPUT.resolve():
        raise SystemExit("Pilot mode refuses to overwrite the canonical full-cohort MD-RRS output")
    frame = pd.read_csv(args.qc_file)
    missing = sorted(REQUIRED - set(frame.columns))
    if missing:
        raise SystemExit(f"QC file missing required columns: {', '.join(missing)}")
    candidate_hash = sha256(CANDIDATE_FILE)
    if set(frame["candidate_sha256"]) != {candidate_hash}:
        raise SystemExit("QC candidate_sha256 does not match canonical set-C file")
    if not (frame["qc_status"] == "PASS").all():
        raise SystemExit("QC file contains non-PASS rows; refusing partial or failed trajectory analysis")
    if frame["analysis_rule_id"].nunique() != 1:
        raise SystemExit("QC panel must use exactly one analysis_rule_id")
    if pd.to_numeric(frame["duration_ns"], errors="coerce").nunique() != 1:
        raise SystemExit("QC panel must use one consistent trajectory duration")
    if pd.to_numeric(frame["n_frames"], errors="coerce").nunique() != 1:
        raise SystemExit("QC panel must use one consistent frame-count protocol")
    fractions = pd.to_numeric(frame["bound_fraction"], errors="coerce")
    if fractions.isna().any() or ((fractions < 0) | (fractions > 1)).any():
        raise SystemExit("bound_fraction must be finite and within [0, 1]")
    for field in ("n_frames", "duration_ns"):
        if not np.isfinite(pd.to_numeric(frame[field], errors="coerce")).all():
            raise SystemExit(f"{field} contains non-finite values")
    if frame["trajectory_sha256"].astype(str).str.fullmatch(r"[0-9a-fA-F]{64}").eq(False).any():
        raise SystemExit("trajectory_sha256 must contain 64-character SHA-256 hashes")
    for _, qc_row in frame.iterrows():
        trajectory = Path(str(qc_row["trajectory_path"]))
        tpr = Path(str(qc_row["tpr_path"]))
        if not trajectory.is_file() or trajectory.stat().st_size == 0:
            raise SystemExit(f"Trajectory missing/empty: {trajectory}")
        if not tpr.is_file() or tpr.stat().st_size == 0:
            raise SystemExit(f"TPR missing/empty: {tpr}")
        if sha256(trajectory) != str(qc_row["trajectory_sha256"]):
            raise SystemExit(f"Trajectory hash mismatch: {trajectory}")
        if sha256(tpr) != str(qc_row["tpr_sha256"]):
            raise SystemExit(f"TPR hash mismatch: {tpr}")
        if float(qc_row["duration_ns"]) <= 0 or int(qc_row["n_frames"]) < 2:
            raise SystemExit(f"Invalid duration/frame count for trajectory: {trajectory}")
    if frame.duplicated(["set_c_id", "target", "mutation"]).any():
        raise SystemExit("QC file contains duplicate candidate/target/mutation rows")
    candidates = pd.read_csv(CANDIDATE_FILE)
    candidate_map = dict(zip(candidates["smiles"], candidates["rank"]))
    all_candidate_ids = {f"PP-{int(rank):02d}" for rank in candidates["rank"]}
    if args.cohort_mode == "pilot":
        if not PILOT_CANDIDATE_IDS.issubset(all_candidate_ids):
            raise SystemExit("Pilot candidate IDs are not present in the canonical set-C file")
    else:
        expected_ids = all_candidate_ids
    expected_rows = len(expected_ids) * sum(len(mutations) for mutations in TARGET_MUTATIONS.values())
    if len(frame) != expected_rows or set(frame["target"]) != set(TARGET_MUTATIONS):
        raise SystemExit(
            f"{args.cohort_mode} QC panel must contain exactly {expected_rows} rows across PfDHFR/PfCRT"
        )
    expected_id_to_smiles = {f"PP-{int(row.rank):02d}": row.smiles for row in candidates.itertuples()}
    if set(frame["set_c_id"]) != expected_ids:
        raise SystemExit(
            f"QC panel must contain all {len(expected_ids)} {args.cohort_mode} set-C IDs; "
            f"found {sorted(set(frame['set_c_id']))}"
        )
    records = []
    for set_c_id, group in frame.groupby("set_c_id"):
        if set_c_id not in expected_ids:
            raise SystemExit(f"Unknown set-C ID in QC file: {set_c_id}")
        smiles = set(group["smiles"])
        if len(smiles) != 1 or next(iter(smiles)) not in candidate_map or next(iter(smiles)) != expected_id_to_smiles[set_c_id]:
            raise SystemExit(f"QC SMILES mismatch for {set_c_id}")
        target_values: dict[str, dict[str, float]] = {}
        for target in TARGET_MUTATIONS:
            target_rows = group[group["target"] == target]
            expected = set(TARGET_MUTATIONS[target])
            if set(target_rows["mutation"]) != expected:
                raise SystemExit(f"Incomplete MD-QC panel for {set_c_id}/{target}")
            target_values[target] = dict(zip(target_rows["mutation"], target_rows["bound_fraction"]))

        ratios = []
        per_target = {}
        for target, values in target_values.items():
            wt = float(values["WT"])
            if wt < args.min_wt_bound_fraction:
                continue
            target_ratios = {mutation: 100.0 * float(value) / wt for mutation, value in values.items() if mutation != "WT"}
            ratios.extend(target_ratios.values())
            per_target[target] = target_ratios
        if not ratios:
            raise SystemExit(f"No target with sufficient WT bound fraction for {set_c_id}")
        first = group.iloc[0]
        records.append({
            "cohort_id": cohort_id,
            "set_c_id": set_c_id,
            "rank": int(candidate_map[next(iter(smiles))]),
            "smiles": next(iter(smiles)),
            "MD_RRS_mean": float(np.mean(ratios)),
            "MD_RRS_class": classify(ratios),
            "MD_RRS_targets_used": ";".join(sorted(per_target)),
            "MD_RRS_rule": str(first["analysis_rule_id"]),
            "trajectory_count": int(group["trajectory_sha256"].nunique()),
            "candidate_sha256": candidate_hash,
            "qc_file_sha256": sha256(args.qc_file),
            "min_wt_bound_fraction": args.min_wt_bound_fraction,
        })

    result = pd.DataFrame(records).sort_values("MD_RRS_mean", ascending=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    provenance = {
        "schema_version": 1,
        "cohort_id": cohort_id,
        "cohort_mode": args.cohort_mode,
        "candidate_ids": sorted(expected_ids),
        "expected_rows": expected_rows,
        "candidate_sha256": candidate_hash,
        "qc_file": str(args.qc_file),
        "qc_file_sha256": sha256(args.qc_file),
        "analysis_rule_ids": sorted(frame["analysis_rule_id"].unique()),
        "min_wt_bound_fraction": args.min_wt_bound_fraction,
        "metric": "MD_RRS = 100 * mutant bound_fraction / WT bound_fraction, averaged over targets with WT >= threshold",
        "docking_rrs_not_replaced": True,
        "full_cohort_output": str(FULL_OUTPUT),
        "output": str(output),
    }
    provenance_path = output.with_name(f"{output.stem}_provenance.json")
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"MD-RRS rows: {len(result)}")
    print(f"Cohort mode: {args.cohort_mode} ({cohort_id})")
    print(f"Output: {output}")
    print("Trajectory QC status: PASS for all accepted rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
