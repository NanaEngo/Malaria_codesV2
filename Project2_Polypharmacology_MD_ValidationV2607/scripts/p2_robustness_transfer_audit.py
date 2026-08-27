#!/usr/bin/env python3
"""Bounded robustness and transfer audit for P2.

This script performs only lightweight post-processing on committed P2 tables.
It does not run docking, molecular dynamics, MM-GBSA, or network extraction.
All perturbations are deterministic and are explicitly secondary.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = RES / "robustness_transfer_20260827"
SEED = 20260827


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rho(x, y):
    return float(spearmanr(x, y).statistic)


def classify(values, wt_anchor, retention=80.0, broad=70.0):
    if not values:
        return "D"
    if all(v >= retention for v in values):
        return "A*" if wt_anchor >= 7.0 else "A"
    if all(v >= broad for v in values):
        return "B"
    if any(v >= retention for v in values):
        return "C"
    return "D"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rrs_path = RES / "c_rrs_classification.csv"
    pns_path = RES / "c_pns_ranking.csv"
    acsi_path = RES / "c_acsi_scores.csv"
    rrs = pd.read_csv(rrs_path)
    pns = pd.read_csv(pns_path)[["smiles", "PNS"]]
    acsi = pd.read_csv(acsi_path)[["smiles", "ACSI"]]
    data = rrs.merge(pns, on="smiles", validate="one_to_one").merge(acsi, on="smiles", validate="one_to_one")
    complete = data[data["complete_two_target_panel"]].copy()
    complete = complete.dropna(subset=["RRS_mean_complete_two_target", "PNS", "ACSI"])

    loo = []
    for removed in complete["candidate_id"]:
        d = complete[complete["candidate_id"] != removed]
        loo.append({
            "removed_candidate": removed,
            "n": len(d),
            "pns_rrs_rho": rho(d.PNS, d.RRS_mean_complete_two_target),
            "acsi_rrs_rho": rho(d.ACSI, d.RRS_mean_complete_two_target),
            "rrs_wt_anchor_rho": rho(d.RRS_mean_complete_two_target, d.WT_anchor_min_abs_kcal_mol),
        })
    pd.DataFrame(loo).to_csv(OUT / "leave_one_candidate_out.csv", index=False)

    perturb = []
    for delta in (-1.0, 1.0):
        for score_col in [c for c in rrs.columns if c.startswith("s_Vina_")]:
            d = rrs.copy()
            d[score_col] = d[score_col].where(d[score_col].notna(), np.nan) + delta
            for _, row in d.iterrows():
                candidate = rrs[rrs.candidate_id == row.candidate_id].iloc[0]
                vals = []
                for target, muts in {"PfDHFR": ("N51I", "C59R", "S108N", "I164L"), "PfCRT": ("K76T", "K76A")}.items():
                    wt_col = f"s_Vina_WT_{target}"
                    wt = row[wt_col]
                    if not np.isfinite(wt) or abs(wt) < 5:
                        continue
                    for mut in muts:
                        col = f"s_Vina_{target}_{mut}"
                        score = row[col]
                        if np.isfinite(score):
                            vals.append(abs(score) / abs(wt) * 100)
                if vals:
                    perturb.append({
                        "candidate_id": row.candidate_id,
                        "perturbed_column": score_col,
                        "delta_kcal_mol": delta,
                        "class_perturbed": classify(vals, float(row["WT_anchor_min_abs_kcal_mol"])),
                        "class_baseline": candidate["RRS_class_available"],
                    })
    pd.DataFrame(perturb).to_csv(OUT / "docking_score_perturbation_classes.csv", index=False)

    target_rows = []
    for target in ("PfDHFR", "PfCRT"):
        col = f"RRS_mean_{target}"
        d = data.dropna(subset=[col, "PNS", "ACSI"])
        target_rows.append({
            "target": target,
            "n": len(d),
            "pns_rrs_rho": rho(d.PNS, d[col]),
            "acsi_rrs_rho": rho(d.ACSI, d[col]),
        })
    pd.DataFrame(target_rows).to_csv(OUT / "target_stratified_correlations.csv", index=False)

    threshold_path = RES / "lightweight_robustness" / "rrs_threshold_sensitivity.csv"
    threshold_status = "COMPUTED_EXISTING_ARTIFACT" if threshold_path.exists() else "NOT_AVAILABLE"
    if threshold_path.exists():
        pd.read_csv(threshold_path).to_csv(OUT / "rrs_threshold_sensitivity.csv", index=False)

    external_candidates = sorted(RES.glob("*chembl*.csv")) + sorted(RES.glob("*public*chembl*.csv"))
    external_records = []
    for path in external_candidates:
        external_records.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path), "status": "LOCAL_ARTIFACT_AUDITED", "independent_replication": False})
    p5_root = ROOT.parent / "Project5_GNN_Transformer_DrugDiscovery"
    p5_candidates = [p5_root / "results" / "p5_public_chembl_malaria.csv", p5_root / "results" / "p5_public_chembl_malaria_disjoint.csv", p5_root / "results" / "p5_public_malaria_report.json"]
    for path in p5_candidates:
        if path.is_file():
            external_records.append({"path": str(path.relative_to(ROOT.parent.parent)), "sha256": sha(path), "status": "RELATED_PROJECT_EXTERNAL_ARTIFACT", "independent_replication": False, "boundary": "P5 transfer artifact; not a P2 replication"})
    external = {
        "status": "COMPUTED_EXTERNAL_TRANSFER_AUDIT" if external_records else "NOT_AVAILABLE",
        "interpretation": "Existing ChEMBL transfer outputs are provenance-audited only; they are not treated as an independent biological replication or experimental validation of P2.",
        "artifacts": external_records,
    }
    (OUT / "external_transfer_audit.json").write_text(json.dumps(external, indent=2) + "\n")

    summary = {
        "schema_version": 1,
        "status": "COMPUTED_SECONDARY_ROBUSTNESS",
        "seed": SEED,
        "inputs": {p.name: {"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in (rrs_path, pns_path, acsi_path)},
        "analyses": {
            "leave_one_candidate_out": {"n_candidates": len(complete), "records": len(loo)},
            "score_perturbation": {"deltas_kcal_mol": [-1.0, 1.0], "records": len(perturb)},
            "target_stratified": {"targets": ["PfDHFR", "PfCRT"]},
            "rrs_threshold_sensitivity": threshold_status,
            "external_transfer": external["status"],
        },
        "boundary": "All outputs are secondary, post-selection diagnostics. No output establishes biochemical affinity, biological resistance, target engagement, or mechanism of action.",
    }
    (OUT / "robustness_transfer_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
