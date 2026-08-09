#!/usr/bin/env python3
"""Reconcile the P1 V5 mutant Vina panel against the P2 raw-score panel.

This script is deliberately read-only with respect to canonical P2 outputs.  It
compares the two raw score layers on the exact 17-candidate cohort after
normalising the V5 PfCRT WT label (WT_K76 -> WT).  It does not decide which
panel is biologically correct and does not promote V5 values into a manuscript
or canonical P2 table.

Outputs (all quarantined under V5/results/exploratory/reconciliation/):
  v5_p2_raw_score_reconciliation.csv   one row per shared candidate/target/state
  v5_p2_raw_score_reconciliation.json  statistics, hashes, and decision record
"""
from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
V5_PANEL = V5 / "results/rrs_pilot/vina_scores/v5_mutant_vina_scores.csv"
P2_PANEL = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/results/docking_mutants.csv"
MANIFEST = ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/v6_candidate_manifest.csv"
OUT_DIR = V5 / "results/exploratory/reconciliation"
OUT_CSV = OUT_DIR / "v5_p2_raw_score_reconciliation.csv"
OUT_JSON = OUT_DIR / "v5_p2_raw_score_reconciliation.json"
SCRIPT_PATH = Path(__file__).resolve()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def stat_pair(frame: pd.DataFrame) -> dict:
    x = frame["score_v5"].to_numpy(dtype=float)
    y = frame["score_p2"].to_numpy(dtype=float)
    if len(frame) < 3:
        pearson = spearman = None
        pearson_p = spearman_p = None
    else:
        pr = pearsonr(x, y)
        sr = spearmanr(x, y)
        pearson, pearson_p = float(pr.statistic), float(pr.pvalue)
        spearman, spearman_p = float(sr.statistic), float(sr.pvalue)
    diff = frame["diff_v5_minus_p2"].to_numpy(dtype=float)
    return {
        "n": int(len(frame)),
        "pearson_r": pearson,
        "pearson_p": pearson_p,
        "spearman_rho": spearman,
        "spearman_p": spearman_p,
        "mean_diff_kcal_mol": float(np.mean(diff)) if len(diff) else None,
        "mae_kcal_mol": float(np.mean(np.abs(diff))) if len(diff) else None,
        "rmse_kcal_mol": float(np.sqrt(np.mean(diff**2))) if len(diff) else None,
    }


def panel_rrs(frame: pd.DataFrame, score_col: str) -> dict:
    """Summarise target-specific RRS from a raw panel, without class promotion."""
    rows: list[dict] = []
    for (candidate, target), group in frame.groupby(["candidate_id", "target"]):
        wt_rows = group.loc[group["state"] == "WT", score_col]
        mutant = group.loc[group["state"] != "WT", score_col]
        if wt_rows.empty or mutant.empty:
            continue
        wt = float(wt_rows.iloc[0])
        if abs(wt) < 5.0:
            continue
        ratios = mutant.abs().to_numpy(dtype=float) / abs(wt) * 100.0
        rows.append({
            "candidate_id": candidate,
            "target": target,
            "wt_abs_kcal_mol": abs(wt),
            "rrs_mean_percent": float(np.mean(ratios)),
            "rrs_min_percent": float(np.min(ratios)),
            "rrs_max_percent": float(np.max(ratios)),
        })
    target_frame = pd.DataFrame(rows)
    if target_frame.empty:
        return {"target_rows": 0, "targets": {}, "candidate_summary": {}}
    candidate = target_frame.groupby("candidate_id")["rrs_mean_percent"].mean()
    return {
        "target_rows": int(len(target_frame)),
        "targets": {
            target: {
                "n": int(len(group)),
                "mean": float(group.rrs_mean_percent.mean()),
                "sd": float(group.rrs_mean_percent.std(ddof=1)) if len(group) > 1 else 0.0,
                "min": float(group.rrs_mean_percent.min()),
                "max": float(group.rrs_mean_percent.max()),
            }
            for target, group in target_frame.groupby("target")
        },
        "candidate_summary": {
            "n": int(len(candidate)),
            "mean": float(candidate.mean()),
            "sd": float(candidate.std(ddof=1)) if len(candidate) > 1 else 0.0,
            "min": float(candidate.min()),
            "max": float(candidate.max()),
            "n_ge_80_percent": int((candidate >= 80.0).sum()),
            "n_lt_80_percent": int((candidate < 80.0).sum()),
        },
    }


def main() -> int:
    for path in (V5_PANEL, P2_PANEL, MANIFEST):
        if not path.is_file():
            raise SystemExit(f"Missing required input: {path}")

    v5 = pd.read_csv(V5_PANEL).rename(columns={"vina_affinity_kcal_mol": "score_v5"})
    p2 = pd.read_csv(P2_PANEL).rename(columns={"vina_score": "score_p2"})
    manifest = pd.read_csv(MANIFEST)
    required_v5 = {"candidate_id", "target", "receptor", "mutation", "score_v5"}
    required_p2 = {"smiles", "target", "mutation", "score_p2"}
    if not required_v5.issubset(v5.columns):
        raise SystemExit(f"V5 schema missing: {sorted(required_v5 - set(v5.columns))}")
    if not required_p2.issubset(p2.columns):
        raise SystemExit(f"P2 schema missing: {sorted(required_p2 - set(p2.columns))}")
    if not {"candidate_id", "canonical_smiles"}.issubset(manifest.columns):
        raise SystemExit("V6 manifest must contain candidate_id and canonical_smiles")

    if manifest["canonical_smiles"].duplicated().any():
        raise SystemExit("V6 manifest contains duplicate canonical_smiles; refusing ambiguous mapping")
    if manifest["candidate_id"].duplicated().any():
        raise SystemExit("V6 manifest contains duplicate candidate_id values")
    expected_candidates = set(manifest["candidate_id"].astype(str))
    if len(expected_candidates) != 17:
        raise SystemExit(f"Expected 17 V6 candidates, found {len(expected_candidates)}")
    smiles_to_candidate = dict(zip(manifest["canonical_smiles"], manifest["candidate_id"]))
    v5["state"] = v5["mutation"].astype(str)
    v5.loc[v5["receptor"].astype(str).str.contains("WT"), "state"] = "WT"
    v5.loc[v5["state"] == "WT_K76", "state"] = "WT"
    v5["candidate_id_norm"] = v5["candidate_id"]
    p2["candidate_id_norm"] = p2["smiles"].map(smiles_to_candidate)
    p2["state"] = p2["mutation"].astype(str)

    if p2["candidate_id_norm"].isna().any():
        missing = int(p2["candidate_id_norm"].isna().sum())
        raise SystemExit(f"Unable to map {missing} P2 rows to V6 candidate IDs")

    keys = ["candidate_id_norm", "target", "state"]
    expected_states = {
        (target, state)
        for target, states in {
            "PfDHFR": {"WT", "N51I", "C59R", "S108N", "I164L"},
            "PfCRT": {"WT", "K76T", "K76A"},
        }.items()
        for state in states
    }

    def validate_panel(frame: pd.DataFrame, label: str) -> None:
        if len(frame) != 136:
            raise SystemExit(f"{label} panel must contain exactly 136 rows, found {len(frame)}")
        if frame[keys].duplicated().any():
            dup = frame.loc[frame[keys].duplicated(keep=False), keys].head(4).to_dict(orient="records")
            raise SystemExit(f"{label} panel contains duplicate candidate/target/state rows: {dup}")
        observed_candidates = set(frame["candidate_id_norm"].astype(str))
        if observed_candidates != expected_candidates:
            raise SystemExit(f"{label} panel candidate set mismatch")
        observed_states = set(zip(frame["target"], frame["state"]))
        if observed_states != expected_states:
            raise SystemExit(f"{label} panel target/state set mismatch")
        counts = frame.groupby(["target", "state"])["candidate_id_norm"].nunique()
        if (counts != 17).any():
            raise SystemExit(f"{label} panel does not contain exactly 17 candidates per state")

    validate_panel(v5, "V5")
    validate_panel(p2, "P2")
    left = v5[keys + ["score_v5"]].rename(columns={"candidate_id_norm": "candidate_id"})
    right = p2[keys + ["score_p2"]].rename(columns={"candidate_id_norm": "candidate_id"})
    joined = left.merge(right, on=["candidate_id", "target", "state"], how="inner", validate="one_to_one")
    joined["diff_v5_minus_p2"] = joined["score_v5"] - joined["score_p2"]
    joined = joined.sort_values(["target", "state", "candidate_id"]).reset_index(drop=True)

    expected = 17 * 8
    if len(joined) != expected:
        raise SystemExit(f"Expected {expected} shared states, found {len(joined)}")
    if not np.isfinite(joined[["score_v5", "score_p2"]].to_numpy()).all():
        raise SystemExit("Non-finite raw score detected")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    joined.to_csv(OUT_CSV, index=False)
    summary = {
        "schema": "p1-v5-p2-raw-score-reconciliation/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "PRE_SUBMISSION_DEVELOPMENT",
        "status": "EXPLORATORY_RECONCILIATION_NOT_SUBMISSION_READY",
        "inputs": {
            "reconciliation_script": str(SCRIPT_PATH.relative_to(ROOT)),
            "reconciliation_script_sha256": sha256(SCRIPT_PATH),
            "v5_panel": str(V5_PANEL.relative_to(ROOT)),
            "v5_panel_sha256": sha256(V5_PANEL),
            "p2_panel": str(P2_PANEL.relative_to(ROOT)),
            "p2_panel_sha256": sha256(P2_PANEL),
            "v6_manifest": str(MANIFEST.relative_to(ROOT)),
            "v6_manifest_sha256": sha256(MANIFEST),
        },
        "normalisation": {
            "v5_pfcrt_wt_k76_to": "WT",
            "candidate_mapping": "exact canonical_smiles -> candidate_id via V6 manifest",
            "join_keys": ["candidate_id", "target", "state"],
        },
        "coverage": {
            "v5_rows_after_deduplication": int(len(v5)),
            "p2_rows_after_deduplication": int(len(p2)),
            "shared_rows": int(len(joined)),
            "shared_candidates": int(joined.candidate_id.nunique()),
            "states": {
                f"{target}|{state}": int(size)
                for (target, state), size in joined.groupby(["target", "state"]).size().items()
            },
        },
        "overall": stat_pair(joined),
        "by_target": {target: stat_pair(group) for target, group in joined.groupby("target")},
        "by_state": {state: stat_pair(group) for state, group in joined.groupby("state")},
        "largest_absolute_differences": joined.loc[
            joined["diff_v5_minus_p2"].abs().nlargest(12).index,
            ["candidate_id", "target", "state", "score_v5", "score_p2", "diff_v5_minus_p2"],
        ].to_dict(orient="records"),
        "raw_panel_rrs_without_class_promotion": {
            "v5": panel_rrs(
                v5.drop(columns=["candidate_id"], errors="ignore").rename(
                    columns={"candidate_id_norm": "candidate_id"}
                ),
                "score_v5",
            ),
            "p2": panel_rrs(
                p2.rename(columns={"candidate_id_norm": "candidate_id"}),
                "score_p2",
            ),
        },
        "scientific_decision": {
            "v5_status": "new exploratory docking-RRS execution layer",
            "p2_status": "canonical corrected P2 RRS evidence layer",
            "promotion": "none; do not overwrite canonical P2/V6 tables",
            "interpretation": "The panels are not directly interchangeable. The observed discrepancy is a protocol/data-layer sensitivity result, not proof that either panel is biologically correct.",
            "minimum_next_run": "freeze identical receptor/mutation/grid/ligand/Vina inputs, rerun the shared 136 states, then recompute both RRS summaries from the same raw table",
        },
        "software": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "output_csv": str(OUT_CSV.relative_to(ROOT)),
    }
    summary["output_csv_sha256"] = sha256(OUT_CSV)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "shared_rows": len(joined), "csv": str(OUT_CSV), "json": str(OUT_JSON)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
