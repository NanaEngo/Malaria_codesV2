#!/usr/bin/env python3
"""P3 public ChEMBL validation: explicit ITT versus complete-case sensitivity.

The historical external-validation run used zero vectors for descriptor
failures.  This script makes that choice explicit rather than silently relying
on ``isfinite``: (1) ITT retains all 22,447 molecules and treats an embedding
failure as a zero-feature failure penalty; (2) complete-case excludes the 351
molecules with failed TNE embeddings and evaluates all descriptors on the same
22,096-molecule subset.  Existing canonical external-validation outputs are
not overwritten.
"""
from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import p3_external_validation as ext

ROOT = Path(__file__).resolve().parents[2]
P3 = ROOT / "Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS = P3 / "results"
OUT = RESULTS / "external_validation_sensitivity"
SEED = 42
N_FOLDS = 5
RF_TREES = 200


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def aucs(X: np.ndarray, y: np.ndarray, name: str) -> np.ndarray:
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    out = []
    for tr, te in skf.split(X, y):
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=RF_TREES,
                                             n_jobs=-1, random_state=SEED)),
        ])
        pipe.fit(X[tr], y[tr])
        out.append(roc_auc_score(y[te], pipe.predict_proba(X[te])[:, 1]))
    return np.asarray(out, dtype=float)


def bh(pvals: list[float]) -> list[float]:
    """Benjamini--Hochberg adjusted p-values in the original order."""
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    q = np.empty_like(p)
    m = len(p)
    for rank, idx in enumerate(order, 1):
        q[idx] = min(1.0, p[idx] * m / rank)
    for i in range(m - 2, -1, -1):
        q[order[i]] = min(q[order[i]], q[order[i + 1]])
    return q.tolist()


def corrected_resampled_t(base: np.ndarray, descriptor: np.ndarray) -> tuple[float, float, float]:
    """Nadeau--Bengio corrected resampled t approximation for k folds.

    The five fold scores are paired, but their training sets overlap. For equal
    k-fold splits, use Var(diff) * (1/k + n_test/n_train), here 1/5 + 1/4,
    with df=k-1. This is reported as exploratory because one CV partition is
    still a small resampling basis; it replaces the over-optimistic naive
    fold-level t-test for inferential wording.
    """
    diff = np.asarray(base, dtype=float) - np.asarray(descriptor, dtype=float)
    k = len(diff)
    if k < 2:
        return float("nan"), float("nan"), float("nan")
    sd = float(diff.std(ddof=1))
    mean = float(diff.mean())
    variance_factor = (1.0 / k) + (1.0 / (k - 1.0))
    t_stat = mean / np.sqrt(variance_factor * sd * sd) if sd else float("inf")
    p_value = float(2.0 * stats.t.sf(abs(t_stat), df=k - 1)) if np.isfinite(t_stat) else 0.0
    return mean, float(t_stat), p_value


def main() -> int:
    public = ROOT / "Project5_GNN_Transformer_DrugDiscovery/results/p5_public_chembl_malaria.csv"
    df = pd.read_csv(public).dropna(subset=["smiles", "activity"]).drop_duplicates("smiles").reset_index(drop=True)
    smiles = df["smiles"].astype(str).tolist()
    y_all = (df["activity"].to_numpy() >= ext.ACT_THRESHOLD).astype(int)

    tfp = np.load(RESULTS / "p3_extval_tfp.npy")
    tne = np.load(RESULTS / "p3_extval_tne.npy")
    tfp_meta = json.loads((RESULTS / "p3_extval_tfp_meta.json").read_text())
    tne_meta = json.loads((RESULTS / "p3_extval_tne_meta.json").read_text())
    if tfp.shape[0] != len(df) or tne.shape[0] != len(df):
        raise SystemExit("Cache panel does not match the public dataset")
    # Legacy caches predate explicit masks; migrate their documented
    # zero-vector failure representation once and persist the provenance.
    def load_failures(arr: np.ndarray, meta: dict, path: Path, name: str) -> np.ndarray:
        if "failed_indices" not in meta:
            failed = np.flatnonzero(np.isclose(arr, 0.0).all(axis=1)).astype(int)
            meta["failed_indices"] = failed.tolist()
            meta["failure_mask_source"] = "legacy_zero_vector_migration"
            meta["failure_mask_migration_note"] = (
                "Inferred from the pre-mask cache's documented zero-vector failure encoding."
            )
            path.write_text(json.dumps(meta, indent=2) + "\n")
        failed = np.asarray(meta["failed_indices"], dtype=int)
        if len(np.unique(failed)) != len(failed):
            raise SystemExit(f"{name} failure indices are not unique")
        if ((failed < 0) | (failed >= len(df))).any():
            raise SystemExit(f"{name} failure indices are out of bounds")
        if len(failed) != int(meta.get("n_fail", -1)):
            raise SystemExit(f"{name} failure-index count does not match metadata")
        return failed

    tfp_failed = load_failures(tfp, tfp_meta, RESULTS / "p3_extval_tfp_meta.json", "TFP")
    tne_failed = load_failures(tne, tne_meta, RESULTS / "p3_extval_tne_meta.json", "TNE")
    if len(tfp_failed):
        raise SystemExit("Unexpected TFP failures in the current cache")
    failed_union = np.unique(np.r_[tfp_failed, tne_failed])
    complete_idx = np.setdiff1d(np.arange(len(df), dtype=int), failed_union)
    expected_complete = len(df) - len(failed_union)
    if len(complete_idx) != expected_complete:
        raise SystemExit("Complete-case index count mismatch")

    # Restrict the sensitivity run to the descriptors directly relevant to
    # the external topological/generalisation claim. This avoids re-running
    # the very expensive 39,972-dimensional PHCO arm while preserving the
    # canonical RF protocol for ECFP4, TFP, TNE, and Hybrid.
    desc_all = {
        "ECFP4": ext.ecfp4(smiles),
        "TFP": tfp.astype(np.float32),
        "TNE": tne.astype(np.float32),
        "Hybrid": np.hstack([tfp, tne]).astype(np.float32),
    }
    panels = {
        "itt_zero_failure_penalty": np.arange(len(df), dtype=int),
        "complete_case_no_tne_failures": complete_idx,
    }
    records = []
    fold_arrays = {}
    for panel_name, idx in panels.items():
        y = y_all[idx]
        for descriptor, X_all in desc_all.items():
            values = aucs(X_all[idx], y, descriptor)
            fold_arrays[(panel_name, descriptor)] = values
            records.append({
                "panel": panel_name,
                "descriptor": descriptor,
                "n_molecules": int(len(idx)),
                "n_active": int(y.sum()),
                "n_inactive": int((y == 0).sum()),
                "mean_auc": float(values.mean()),
                "sd_auc": float(values.std()),
                "fold_auc": [round(float(v), 8) for v in values],
            })

    comparisons = []
    for panel_name in panels:
        base = fold_arrays[(panel_name, "ECFP4")]
        rows = []
        for descriptor in desc_all:
            if descriptor == "ECFP4":
                continue
            vals = fold_arrays[(panel_name, descriptor)]
            t, p = stats.ttest_rel(base, vals)
            corrected_delta, corrected_t, corrected_p = corrected_resampled_t(base, vals)
            rows.append({
                "panel": panel_name,
                "descriptor": descriptor,
                "delta_ecfp_minus_descriptor": float(base.mean() - vals.mean()),
                "naive_paired_t_pvalue_df4": float(p),
                "corrected_delta_ecfp_minus_descriptor": corrected_delta,
                "corrected_resampled_t_statistic_df4": corrected_t,
                "corrected_resampled_pvalue_df4": corrected_p,
                "fold_ecfp4": [round(float(v), 8) for v in base],
                "fold_descriptor": [round(float(v), 8) for v in vals],
            })
        q_naive = bh([r["naive_paired_t_pvalue_df4"] for r in rows])
        q_corrected = bh([r["corrected_resampled_pvalue_df4"] for r in rows])
        for row, qn, qc in zip(rows, q_naive, q_corrected):
            row["bh_fdr_qvalue_naive"] = float(qn)
            row["bh_fdr_qvalue_corrected"] = float(qc)
            row["significant_after_corrected_fdr"] = bool(qc < 0.05)
        comparisons.extend(rows)

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_json(OUT / "p3_external_validation_sensitivity_records.json", orient="records", indent=2)
    pd.DataFrame(comparisons).to_csv(OUT / "p3_external_validation_sensitivity_comparisons.csv", index=False)
    summary = {
        "schema": "p3-public-chembl-validation-sensitivity/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "EXPLORATORY_SENSITIVITY_COMPLETE_NOT_CONFIRMATORY",
        "dataset": str(public.relative_to(ROOT)),
        "n_raw": int(len(df)),
        "n_active_raw": int(y_all.sum()),
        "n_inactive_raw": int((y_all == 0).sum()),
        "failure_counts": {
            "tfp_failed_indices": int(len(tfp_failed)),
            "tne_failed_indices": int(len(tne_failed)),
            "complete_case_rows": int(len(complete_idx)),
        },
        "protocol": {
            "folds": 5,
            "random_state": SEED,
            "rf_trees": RF_TREES,
            "itt": "retain all molecules; zero-vector embedding failures are an explicit failure penalty",
            "complete_case": "exclude rows indexed by the explicit TNE/TFP failure masks; all descriptors use the same subset",
            "inference": "Nadeau-Bengio corrected resampled t approximation (df=4) is exploratory; naive fold-level t-tests are retained only for audit comparison",
        },
        "records": records,
        "comparisons": comparisons,
        "interpretation": {
            "headline": "External descriptor conclusions are reported with explicit sensitivity to embedding-failure handling.",
            "caveat": "The historical external-validation report corresponds to the ITT zero-failure-penalty panel; the complete-case panel is a sensitivity analysis and does not overwrite it. Fold-level p-values are not confirmatory because CV training sets overlap.",
            "qks": "QKS is not recomputed here; its separate report uses a full parseable panel and an SVM classifier, unlike this RF descriptor analysis.",
        },
        "inputs": {
            "public_sha256": sha256(public),
            "tfp_cache_sha256": sha256(RESULTS / "p3_extval_tfp.npy"),
            "tne_cache_sha256": sha256(RESULTS / "p3_extval_tne.npy"),
            "script_sha256": sha256(Path(__file__).resolve()),
        },
    }
    (OUT / "p3_external_validation_sensitivity.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"status": summary["status"], "failure_counts": summary["failure_counts"], "means": {r["panel"] + "/" + r["descriptor"]: round(r["mean_auc"], 6) for r in records}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
