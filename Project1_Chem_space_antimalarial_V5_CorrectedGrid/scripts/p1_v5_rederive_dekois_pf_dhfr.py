#!/usr/bin/env python3
"""Independent redérivation of the archived PfDHFR DEKOIS docking benchmark.

Inputs are the archived molecule-level Vina scores: 40 experimentally labelled
DEKOIS actives and 1,200 property-matched decoys.  More-negative Vina scores
are converted to higher ranking scores by negation.  This script never edits
canonical P1/P2 result files; it writes only quarantined V5 exploratory outputs.
"""
from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
ACTIVE = ROOT / ".archive_P1_V2607_20260717/results/r1a_dekois/dekois_dhfr_actives_scores.csv"
DECOY = ROOT / ".archive_P1_V2607_20260717/results/r1a_dekois/dekois_dhfr_vina_scores.csv"
OUT = V5 / "results/exploratory/external_validation/dekois_pf_dhfr"
OUT_METRICS = OUT / "p1_v5_dekois_pf_dhfr_metrics.csv"
OUT_JSON = OUT / "p1_v5_dekois_pf_dhfr_provenance.json"
OUT_SCORES = OUT / "p1_v5_dekois_pf_dhfr_scores.csv"
OUT_PNG = OUT / "p1_v5_dekois_pf_dhfr_roc_distribution.png"
OUT_PDF = OUT / "p1_v5_dekois_pf_dhfr_roc_distribution.pdf"
SCRIPT = Path(__file__).resolve()
SEED = 20260809
N_BOOT = 10000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def ef(labels: np.ndarray, fraction: float) -> float:
    k = max(1, int(np.floor(len(labels) * fraction)))
    observed = labels[:k].sum() / k
    prevalence = labels.mean()
    return float(observed / prevalence) if prevalence > 0 else float("nan")


def bootstrap_ci(active: np.ndarray, decoy: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.empty(N_BOOT, dtype=float)
    for i in range(N_BOOT):
        a = rng.choice(active, size=len(active), replace=True)
        d = rng.choice(decoy, size=len(decoy), replace=True)
        values[i] = roc_auc_score(
            np.r_[np.ones(len(a), dtype=int), np.zeros(len(d), dtype=int)],
            np.r_[a, d],
        )
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def main() -> int:
    for path in (ACTIVE, DECOY):
        if not path.is_file():
            raise SystemExit(f"Missing input: {path}")
    act = pd.read_csv(ACTIVE)
    dec = pd.read_csv(DECOY)
    for name, frame in (("active", act), ("decoy", dec)):
        if not {"ligand_id", "vina_score"}.issubset(frame.columns):
            raise SystemExit(f"{name} schema must contain ligand_id,vina_score")
        if frame["ligand_id"].duplicated().any():
            raise SystemExit(f"Duplicate {name} ligand IDs")
        if not np.isfinite(frame["vina_score"].to_numpy(dtype=float)).all():
            raise SystemExit(f"Non-finite {name} score")
    if len(act) != 40 or len(dec) != 1200:
        raise SystemExit(f"Expected 40 actives and 1200 decoys; found {len(act)} and {len(dec)}")

    # Negation is the only ranking transformation: more negative Vina = higher score.
    scores = np.r_[-act["vina_score"].to_numpy(float), -dec["vina_score"].to_numpy(float)]
    labels = np.r_[np.ones(len(act), dtype=int), np.zeros(len(dec), dtype=int)]
    order = np.argsort(-scores, kind="mergesort")
    sorted_labels = labels[order]
    auc = float(roc_auc_score(labels, scores))
    pr_auc = float(average_precision_score(labels, scores))
    rng = np.random.default_rng(SEED)
    ci_low, ci_high = bootstrap_ci(-act["vina_score"].to_numpy(float), -dec["vina_score"].to_numpy(float), rng)
    metrics = {
        "roc_auc": auc,
        "roc_auc_bootstrap_ci_low": ci_low,
        "roc_auc_bootstrap_ci_high": ci_high,
        "pr_auc": pr_auc,
        "ef_1pct": ef(sorted_labels, 0.01),
        "ef_5pct": ef(sorted_labels, 0.05),
        "ef_10pct": ef(sorted_labels, 0.10),
        "ef_20pct": ef(sorted_labels, 0.20),
        "n_actives": int(len(act)),
        "n_decoys": int(len(dec)),
        "active_mean_vina": float(act.vina_score.mean()),
        "active_sd_vina": float(act.vina_score.std(ddof=1)),
        "decoy_mean_vina": float(dec.vina_score.mean()),
        "decoy_sd_vina": float(dec.vina_score.std(ddof=1)),
        "mean_vina_difference_active_minus_decoy": float(act.vina_score.mean() - dec.vina_score.mean()),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    scores_out = pd.concat([
        act.assign(class_label="active", ranking_score=-act.vina_score),
        dec.assign(class_label="decoy", ranking_score=-dec.vina_score),
    ], ignore_index=True)
    scores_out.to_csv(OUT_SCORES, index=False)
    pd.DataFrame([metrics]).to_csv(OUT_METRICS, index=False)

    fpr, tpr, _ = roc_curve(labels, scores)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].plot(fpr, tpr, color="#2166ac", linewidth=2,
                 label=f"ROC-AUC = {auc:.3f} [{ci_low:.3f}, {ci_high:.3f}]")
    axes[0].plot([0, 1], [0, 1], "--", color="#777777", linewidth=1)
    axes[0].set(xlabel="False-positive rate", ylabel="True-positive rate", title="DEKOIS PfDHFR enrichment")
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    axes[1].hist(act.vina_score, bins=18, alpha=0.75, label="Active", color="#1b9e77", density=True)
    axes[1].hist(dec.vina_score, bins=30, alpha=0.55, label="Decoy", color="#d95f02", density=True)
    axes[1].set(xlabel="Vina score (kcal mol$^{-1}$; lower is better)", ylabel="Density", title="Score distributions")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("Independent redérivation: archived DEKOIS PfDHFR panel", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    plt.close(fig)

    provenance = {
        "schema": "p1-v5-independent-dekois-pfdhfr/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "PRE_SUBMISSION_DEVELOPMENT",
        "status": "EXPLORATORY_EXTERNAL_ENRICHMENT_NOT_SUBMISSION_READY",
        "target": "PfDHFR",
        "pdb": "7F3Y",
        "inputs": {
            "active_csv": str(ACTIVE.relative_to(ROOT)),
            "active_sha256": sha256(ACTIVE),
            "decoy_csv": str(DECOY.relative_to(ROOT)),
            "decoy_sha256": sha256(DECOY),
        },
        "protocol": {
            "ranking": "score = -vina_score; more-negative Vina ranks higher",
            "bootstrap_replicates": N_BOOT,
            "bootstrap_seed": SEED,
            "ef_definition": "top fraction enrichment relative to active prevalence",
        },
        "metrics": metrics,
        "comparison_to_archived_summary": {
            "archived_true_roc_auc": 0.49640625,
            "archived_v2_roc_auc": 0.450104,
            "note": "Different archived score panels/protocols; neither summary is overwritten by this redérivation.",
        },
        "interpretation": {
            "headline": "The archived DEKOIS PfDHFR panel shows weak discrimination of the 40 actives from 1200 decoys under this Vina protocol.",
            "meaning": "This is a valid negative external enrichment result and cautions against interpreting Vina ranking as validated activity prediction.",
            "not_claimed": ["experimental affinity", "generalisation to PfCRT/PfClpP/PfATP4", "failure of the molecules themselves"],
        },
        "outputs": {
            "scores_csv": str(OUT_SCORES.relative_to(ROOT)),
            "metrics_csv": str(OUT_METRICS.relative_to(ROOT)),
            "figure_png": str(OUT_PNG.relative_to(ROOT)),
            "figure_pdf": str(OUT_PDF.relative_to(ROOT)),
        },
        "software": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
    }
    provenance["script"] = str(SCRIPT.relative_to(ROOT))
    provenance["script_sha256"] = sha256(SCRIPT)
    provenance["output_sha256"] = {str(p.name): sha256(p) for p in (OUT_SCORES, OUT_METRICS, OUT_PNG, OUT_PDF)}
    OUT_JSON.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": provenance["status"], "metrics": metrics,
                      "outputs": provenance["outputs"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
