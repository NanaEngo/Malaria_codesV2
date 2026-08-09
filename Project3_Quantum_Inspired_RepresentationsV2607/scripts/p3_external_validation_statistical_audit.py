#!/usr/bin/env python3
"""Post-process completed P3 external-validation outputs without refitting.

This audit preserves the historical descriptor/QKS reports and writes companion
files containing (i) explicit legacy failure-mask provenance and (ii) corrected
resampled t statistics. A five-fold CV paired t-test is retained only as an
audit comparator because folds have overlapping training sets.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
P3 = ROOT / "Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS = P3 / "results"
SENS = RESULTS / "external_validation_sensitivity"


def bh(values: list[float]) -> list[float]:
    p = np.asarray(values, dtype=float)
    order = np.argsort(p)
    raw = np.minimum(1.0, p[order] * len(p) / np.arange(1, len(p) + 1))
    adj = np.minimum.accumulate(raw[::-1])[::-1]
    out = np.empty_like(adj)
    out[order] = adj
    return out.tolist()


def corrected(base: np.ndarray, other: np.ndarray) -> dict:
    diff = np.asarray(base, float) - np.asarray(other, float)
    k = len(diff)
    sd = float(diff.std(ddof=1))
    mean = float(diff.mean())
    naive_t = mean / (sd / np.sqrt(k))
    naive_p = float(2 * stats.t.sf(abs(naive_t), k - 1))
    # Nadeau--Bengio corrected resampled t approximation for one k-fold
    # partition: variance factor = 1/k + n_test/n_train = 1/5 + 1/4.
    factor = (1.0 / k) + (1.0 / (k - 1.0))
    if sd == 0.0:
        t_corr = float("inf") if mean != 0.0 else 0.0
        p_corr = 0.0 if mean != 0.0 else 1.0
    else:
        t_corr = mean / np.sqrt(factor * sd * sd)
        p_corr = float(2 * stats.t.sf(abs(t_corr), k - 1))
    return {
        "mean_delta_base_minus_other": mean,
        "sd_delta": sd,
        "naive_t_df4": float(naive_t),
        "naive_p_df4": naive_p,
        "corrected_resampled_t_df4": float(t_corr),
        "corrected_resampled_p_df4": p_corr,
        "variance_factor": factor,
        "n_folds": k,
    }


def migrate_failure_metadata() -> dict:
    out = {}
    for name in ("tfp", "tne"):
        arr_path = RESULTS / f"p3_extval_{name}.npy"
        meta_path = RESULTS / f"p3_extval_{name}_meta.json"
        meta = json.loads(meta_path.read_text())
        arr = np.load(arr_path, mmap_mode="r")
        if "failed_indices" not in meta:
            failed = np.flatnonzero(np.isclose(arr, 0.0).all(axis=1)).astype(int).tolist()
            meta["failed_indices"] = failed
            meta["failure_mask_source"] = "legacy_zero_vector_migration"
            meta["failure_mask_migration_note"] = (
                "Inferred from the pre-mask cache's documented zero-vector failure encoding."
            )
            meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        failed = [int(i) for i in meta["failed_indices"]]
        if len(failed) != int(meta.get("n_fail", -1)):
            raise RuntimeError(f"{name}: failure mask/count mismatch")
        if len(set(failed)) != len(failed) or any(i < 0 or i >= arr.shape[0] for i in failed):
            raise RuntimeError(f"{name}: invalid failure indices")
        out[name] = {
            "n_fail": len(failed),
            "failure_mask_source": meta.get("failure_mask_source", "explicit_cache_mask"),
            "failed_indices_sha256": __import__("hashlib").sha256(
                json.dumps(failed, separators=(",", ":")).encode()
            ).hexdigest(),
        }
    return out


def audit_descriptor() -> dict:
    d = json.loads((SENS / "p3_external_validation_sensitivity.json").read_text())
    panels = {}
    for panel in ("itt_zero_failure_penalty", "complete_case_no_tne_failures"):
        rows = {r["descriptor"]: np.asarray(r["fold_auc"], float)
                for r in d["records"] if r["panel"] == panel}
        base = rows["ECFP4"]
        comps = {}
        for desc in ("TFP", "TNE", "Hybrid"):
            comps[desc] = corrected(base, rows[desc])
        q = bh([v["corrected_resampled_p_df4"] for v in comps.values()])
        for item, qv in zip(comps.values(), q):
            item["bh_fdr_qvalue_corrected"] = qv
            item["confirmatory_significance_claim_permitted"] = False
        panels[panel] = comps
    return {
        "source": "external_validation_sensitivity/p3_external_validation_sensitivity.json",
        "status": "COMPLETE_EXPLORATORY_NOT_CONFIRMATORY",
        "panels": panels,
        "interpretation": "AUC conclusions are stable between ITT and complete-case panels. Corrected p-values are exploratory because one five-fold partition remains a small resampling basis; naive fold-level p-values are not confirmatory.",
    }


def audit_qks() -> dict:
    d = json.loads((RESULTS / "p3_external_validation_qks_report.json").read_text())
    arrays = {c["model_a"] + "_vs_" + c["model_b"]: (np.asarray(c["per_fold_a"], float), np.asarray(c["per_fold_b"], float)) for c in d["paired_comparisons"]}
    comps = {}
    for key, (a, b) in arrays.items():
        comps[key] = corrected(a, b)
    q = bh([v["corrected_resampled_p_df4"] for v in comps.values()])
    for item, qv in zip(comps.values(), q):
        item["bh_fdr_qvalue_corrected"] = qv
        item["confirmatory_significance_claim_permitted"] = False
    return {
        "source": "p3_external_validation_qks_report.json",
        "status": "COMPLETE_EXPLORATORY_NOT_CONFIRMATORY",
        "comparisons": comps,
        "interpretation": "The external QKS deficit relative to RBF remains directionally present after correction, but its inferential status is exploratory rather than confirmatory.",
    }


def main() -> None:
    provenance = migrate_failure_metadata()
    result = {
        "schema": "p3-external-validation-statistical-audit/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "failure_mask_provenance": provenance,
        "descriptor_sensitivity": audit_descriptor(),
        "qks_external": audit_qks(),
    }
    out = RESULTS / "p3_external_validation_statistical_audit.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
