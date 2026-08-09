#!/usr/bin/env python3
"""Generate descriptive P1 V5 data and figures from the locked raw Vina panel.

This script deliberately excludes ``mean_completed_targets``. Vina scores from
unlike receptor pockets are not calibrated for cross-target arithmetic. Outputs
are descriptive/raw evidence only and retain the independent-review gate status.

Outputs
-------
results/derived/ (post-submission accepted phase)
results/figures/ (post-submission accepted phase)
results/exploratory/derived/ and results/exploratory/figures/ (pre-submission)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
RESULTS = V5 / "results"
DERIVED = RESULTS / "derived"
FIGURES = RESULTS / "figures"
AFFINITIES = RESULTS / "v5_four_target_vina_affinities.csv"
REVIEW_TABLE = RESULTS / "v5_four_target_vina_review_table.json"
REGISTER = RESULTS / "structural_pocket_independent_review.json"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from p1_v5_consensus_rrs_gate import check_gate  # noqa: E402

TARGETS = ("PfDHFR", "PfCRT", "PfClpP", "PfATP4")
SCORE_COLUMNS = {target: f"aff_{target}" for target in TARGETS}
TARGET_COLORS = {
    "PfDHFR": "#2563eb",
    "PfCRT": "#0f766e",
    "PfClpP": "#b45309",
    "PfATP4": "#7c3aed",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_and_validate() -> tuple[pd.DataFrame, dict, dict, bool]:
    scores = pd.read_csv(AFFINITIES)
    review = json.loads(REVIEW_TABLE.read_text(encoding="utf-8"))
    register = json.loads(REGISTER.read_text(encoding="utf-8"))

    expected = {"candidate_id", *SCORE_COLUMNS.values()}
    missing = expected - set(scores.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(scores) != 17 or scores["candidate_id"].nunique() != 17:
        raise ValueError("Expected 17 unique candidates in the locked V5 panel")
    if any(scores[col].isna().any() for col in SCORE_COLUMNS.values()):
        raise ValueError("Missing target score in the locked 17 x 4 panel")
    if set(review.get("completeness", {}).values()) != {"COMPLETE_17"}:
        raise ValueError("Review table is not complete for all four targets")
    review_rows = review.get("rows", [])
    review_ids = [row.get("candidate_id") for row in review_rows]
    if len(review_rows) != 17 or len(set(review_ids)) != 17 or set(review_ids) != set(scores["candidate_id"]):
        raise ValueError("Review table must contain exactly one gate row for every candidate")
    required_gate_keys = {
        f"gate_{target}_anchor_min_A" for target in TARGETS
    } | {f"gate_{target}_frac" for target in TARGETS}
    if any(not required_gate_keys.issubset(row) for row in review_rows):
        raise ValueError("Review table contains incomplete geometric-gate records")
    for row in review_rows:
        for target in TARGETS:
            distance = float(row[f"gate_{target}_anchor_min_A"])
            fraction = float(row[f"gate_{target}_frac"])
            if not np.isfinite(distance) or distance < 0:
                raise ValueError(f"Invalid anchor distance for {row['candidate_id']} / {target}")
            if not np.isfinite(fraction) or not 0 <= fraction <= 1:
                raise ValueError(f"Invalid in-box fraction for {row['candidate_id']} / {target}")
    if set(review.get("targets", {})) != set(TARGETS):
        raise ValueError("Review table target keys do not match the canonical four-target panel")
    # During author-controlled pre-submission development, the register may
    # remain pending while descriptive tables/figures are generated. The
    # structural table, hashes, row counts, and geometric QC above remain
    # mandatory. Submission-facing generation is dormant until the author
    # explicitly requests restriction reactivation.
    phase_file = ROOT / "P1_DEVELOPMENT_PHASE.json"
    phase = json.loads(phase_file.read_text(encoding="utf-8"))
    pre_submission = phase.get("phase") == "PRE_SUBMISSION_DEVELOPMENT" and phase.get("exploratory_internal_work_enabled") is True
    if not pre_submission and register.get("status") != "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED":
        raise ValueError("Submission-facing figure generation requires explicit author reactivation")
    if not pre_submission and register.get("accepted_for_full_run") is not True:
        raise ValueError("Submission-facing figure generation is closed until explicit author reactivation")
    if not pre_submission:
        gate_ok, gate_message = check_gate(REGISTER)
        if not gate_ok:
            raise ValueError(f"Submission-facing review gate failed after explicit reactivation: {gate_message}")
    # The legacy aggregate is retained in the raw artifact for provenance, but
    # this script must never read it or use it in any derived output.
    return scores, review, register, pre_submission


def review_gate_provenance(register: dict, pre_submission: bool) -> dict:
    """Expose acceptance only after a cryptographically gated phase.

    Exploratory artifacts must not mirror mutable register acceptance fields.
    """
    return {
        "status": "PENDING_INDEPENDENT_REVIEW" if pre_submission else register["status"],
        "accepted_for_full_run": False if pre_submission else register["accepted_for_full_run"],
        "authorization_mode": register["authorization"]["authorization_mode"],
        "consensus_artifact_status": "VOID",
    }


def build_long(scores: pd.DataFrame, review: dict) -> pd.DataFrame:
    rows = []
    for target in TARGETS:
        tmeta = review["targets"][target]
        gate_rows = {row["candidate_id"]: row for row in review["rows"]}
        for _, record in scores.iterrows():
            cid = record["candidate_id"]
            gate = gate_rows[cid]
            score = float(record[SCORE_COLUMNS[target]])
            rows.append({
                "candidate_id": cid,
                "target": target,
                "pdb_id": tmeta["pdb"],
                "anchor": tmeta["anchor"],
                "vina_score_kcal_mol": score,
                "within_target_rank": None,
                "anchor_min_A": float(gate[f"gate_{target}_anchor_min_A"]),
                "in_box_fraction": float(gate[f"gate_{target}_frac"]),
                "geometric_gate_pass": bool(
                    float(gate[f"gate_{target}_anchor_min_A"]) <= 10.0
                    and float(gate[f"gate_{target}_frac"]) >= 0.90
                ),
            })
    long = pd.DataFrame(rows)
    # More negative Vina scores receive the better within-target rank. This is
    # an ordinal descriptor, not a cross-target potency ranking.
    long["within_target_rank"] = (
        long.groupby("target")["vina_score_kcal_mol"]
        .rank(method="min", ascending=True)
        .astype(int)
    )
    return long.sort_values(["target", "within_target_rank", "candidate_id"]).reset_index(drop=True)


def build_summary(long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target, group in long.groupby("target", sort=False):
        rows.append({
            "target": target,
            "pdb_id": group["pdb_id"].iloc[0],
            "n_pairs": len(group),
            "score_min_kcal_mol": group["vina_score_kcal_mol"].min(),
            "score_max_kcal_mol": group["vina_score_kcal_mol"].max(),
            "score_mean_kcal_mol": group["vina_score_kcal_mol"].mean(),
            "score_median_kcal_mol": group["vina_score_kcal_mol"].median(),
            "score_sd_kcal_mol": group["vina_score_kcal_mol"].std(ddof=1),
            "anchor_min_A": group["anchor_min_A"].min(),
            "anchor_max_A": group["anchor_min_A"].max(),
            "in_box_fraction_min": group["in_box_fraction"].min(),
            "in_box_fraction_max": group["in_box_fraction"].max(),
            "n_gate_pass": int(group["geometric_gate_pass"].sum()),
        })
    return pd.DataFrame(rows)


def save_table(df: pd.DataFrame, name: str) -> str:
    path = DERIVED / name
    df.to_csv(path, index=False, float_format="%.6f")
    return str(path.relative_to(ROOT))


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)


def save_figure(fig: plt.Figure, stem: str) -> list[str]:
    outputs = []
    for ext in ("pdf", "png"):
        path = FIGURES / f"{stem}.{ext}"
        fig.savefig(path, bbox_inches="tight", dpi=300, facecolor="white")
        outputs.append(str(path.relative_to(ROOT)))
    plt.close(fig)
    return outputs


def figure_scores(long: pd.DataFrame) -> list[str]:
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 8.0), sharex=False)
    for ax, target in zip(axes.flat, TARGETS):
        g = long[long["target"] == target].sort_values("vina_score_kcal_mol")
        y = np.arange(len(g))
        ax.hlines(y, g["vina_score_kcal_mol"].min(), g["vina_score_kcal_mol"],
                  color="#d1d5db", linewidth=1.0, zorder=1)
        ax.scatter(g["vina_score_kcal_mol"], y, s=42, color=TARGET_COLORS[target],
                   edgecolor="white", linewidth=0.7, zorder=2)
        ax.set_yticks(y)
        ax.set_yticklabels(g["candidate_id"], fontsize=8)
        ax.set_xlabel("Vina score estimate (kcal mol$^{-1}$)")
        ax.set_title(f"{target} ({g['pdb_id'].iloc[0]})", loc="left", fontweight="bold")
        ax.invert_yaxis()
        style_axes(ax)
    fig.suptitle("P1 V5 target-wise Vina score estimates", fontsize=15, fontweight="bold", y=0.99)
    fig.text(0.5, 0.01,
             "Each panel is an independent receptor-specific view; scores are not calibrated for cross-target comparison.",
             ha="center", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.035, 1, 0.96))
    return save_figure(fig, "p1_v5_targetwise_vina_scores")


def figure_ranks(long: pd.DataFrame) -> list[str]:
    pivot = long.pivot(index="candidate_id", columns="target", values="within_target_rank")[list(TARGETS)]
    fig, ax = plt.subplots(figsize=(9.0, 7.1))
    image = ax.imshow(pivot.values, cmap="viridis_r", vmin=1, vmax=17, aspect="auto")
    ax.set_xticks(np.arange(len(TARGETS)), TARGETS)
    ax.set_yticks(np.arange(len(pivot.index)), pivot.index)
    ax.set_xlabel("Target-specific receptor panel")
    ax.set_ylabel("Candidate")
    ax.set_title("Within-target rank map (rank 1 = most negative Vina score)",
                 loc="left", fontweight="bold")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, int(pivot.iloc[i, j]), ha="center", va="center",
                    color="white" if pivot.iloc[i, j] > 9 else "black", fontsize=8)
    cbar = fig.colorbar(image, ax=ax, pad=0.02, fraction=0.045)
    cbar.set_label("Within-target rank")
    fig.text(0.5, 0.01,
             "Ranks are computed separately within each target and must not be read as a four-target potency ranking.",
             ha="center", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    return save_figure(fig, "p1_v5_intratarget_rank_heatmap")


def figure_qc(long: pd.DataFrame) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8), sharey=True)
    for target in TARGETS:
        g = long[long["target"] == target].sort_values("anchor_min_A")
        axes[0].scatter(g["anchor_min_A"], g["candidate_id"], s=35,
                        label=target, color=TARGET_COLORS[target], alpha=0.9)
        axes[1].scatter(g["in_box_fraction"] * 100.0, g["candidate_id"], s=35,
                        label=target, color=TARGET_COLORS[target], alpha=0.9)
    axes[0].axvline(10.0, color="#dc2626", linestyle="--", linewidth=1.2, label="gate ≤ 10 Å")
    axes[1].axvline(90.0, color="#dc2626", linestyle="--", linewidth=1.2, label="gate ≥ 90%")
    axes[0].set_xlabel("Minimum anchor distance (Å)")
    axes[1].set_xlabel("Ligand atoms inside box (%)")
    axes[0].set_title("Anchor contact gate", loc="left", fontweight="bold")
    axes[1].set_title("Box-containment gate", loc="left", fontweight="bold")
    for ax in axes:
        style_axes(ax)
        ax.legend(frameon=False, fontsize=8, loc="best")
    fig.suptitle("P1 V5 geometric quality-control metrics", fontsize=15, fontweight="bold", y=1.02)
    fig.text(0.5, -0.01,
             "These are pose/provenance checks, not evidence of binding or biological activity.",
             ha="center", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    return save_figure(fig, "p1_v5_geometric_gate_qc")


def main() -> None:
    global DERIVED, FIGURES
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="remove only this script's prior derived outputs")
    args = parser.parse_args()
    # Resolve the phase before creating or cleaning any output directory. This
    # prevents a pre-submission run (including --clean) from touching canonical
    # submission-facing artifacts.
    phase_file = ROOT / "P1_DEVELOPMENT_PHASE.json"
    phase = json.loads(phase_file.read_text(encoding="utf-8"))
    pre_submission = phase.get("phase") == "PRE_SUBMISSION_DEVELOPMENT" and phase.get("exploratory_internal_work_enabled") is True
    if pre_submission:
        DERIVED = RESULTS / "exploratory" / "derived"
        FIGURES = RESULTS / "exploratory" / "figures"

    # Validate the register and all scientific inputs before creating or
    # cleaning any output. Canonical submission-facing outputs remain dormant
    # until explicit author reactivation; development outputs are isolated.
    scores, review, register, validated_pre_submission = load_and_validate()
    if validated_pre_submission != pre_submission:
        raise RuntimeError("development phase changed during figure generation")
    DERIVED.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for path in DERIVED.glob("v5_vina_*"):
            path.unlink()
        for stem in ("p1_v5_targetwise_vina_scores", "p1_v5_intratarget_rank_heatmap", "p1_v5_geometric_gate_qc"):
            for ext in ("pdf", "png"):
                (FIGURES / f"{stem}.{ext}").unlink(missing_ok=True)
    long = build_long(scores, review)
    summary = build_summary(long)
    gate = long[["candidate_id", "target", "pdb_id", "anchor_min_A", "in_box_fraction", "geometric_gate_pass"]]
    ranks = long[["candidate_id", "target", "within_target_rank", "vina_score_kcal_mol"]]

    output_files = [
        save_table(long, "v5_vina_long.csv"),
        save_table(summary, "v5_vina_target_summary.csv"),
        save_table(gate, "v5_vina_gate_metrics.csv"),
        save_table(ranks, "v5_vina_intratarget_ranks.csv"),
    ]
    output_files += figure_scores(long)
    output_files += figure_ranks(long)
    output_files += figure_qc(long)

    output_paths = output_files
    provenance = {
        "schema": "p1-v5-derived-data-figures/v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY" if pre_submission else "DESCRIPTIVE_RAW_EVIDENCE_REVIEWED",
        "submission_eligible": False if pre_submission else True,
        "scientific_boundary": [
            "mean_completed_targets was excluded from every derived table and figure",
            "Vina scores are reported target-wise and are not cross-target comparable",
            "within-target ranks are ordinal and are not a potency consensus",
            "geometric gates are pose/provenance QC, not biological validation",
            "no consensus, RRS, PNS, or manuscript claim was computed or promoted",
        ],
        "panel": {"n_candidates": int(len(scores)), "n_targets": len(TARGETS), "n_pairs": int(len(long))},
        "review_gate": review_gate_provenance(register, pre_submission),
        "sources": {
            str(p.relative_to(ROOT)): sha256(p)
            for p in (AFFINITIES, REVIEW_TABLE, REGISTER)
        },
        "generator": {
            "version": "1.0.0",
            "script": str(Path(__file__).relative_to(ROOT)),
            "configuration": {"targets": list(TARGETS), "rank_direction": "ascending_vina_score", "figure_dpi": 300},
            "script_sha256": sha256(Path(__file__)),
            "python": sys.version,
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "pandas", "matplotlib")
            },
        },
        "outputs": output_paths,
        "output_sha256": {
            path: sha256(ROOT / path) for path in output_paths
        },
        "source_columns_used": ["candidate_id", *SCORE_COLUMNS.values()],
        "source_columns_excluded": ["mean_completed_targets"],
    }
    (DERIVED / "v5_vina_derivation_provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": provenance["status"],
        "n_rows_long": len(long),
        "n_gate_pass": int(long["geometric_gate_pass"].sum()),
        "outputs": output_files + [str((DERIVED / "v5_vina_derivation_provenance.json").relative_to(ROOT))],
    }, indent=2))


if __name__ == "__main__":
    main()
