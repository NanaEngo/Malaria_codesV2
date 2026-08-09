#!/usr/bin/env python3
"""Generate V6 integrated candidate data and exploratory figures.

The join is performed through the locked V6 canonical-SMILES manifest. No
cross-target Vina mean is read or generated. RRS/ACSI/PNS are displayed as
exploratory source-panel descriptors; the independent-review gate remains
closed and no acceptance or biological validation is inferred.
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
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
V6 = ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid"
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from v6_review_gate import check_gate as check_v6_review_gate  # noqa: E402
V5_SCRIPT_DIR = V5 / "scripts"
sys.path.insert(0, str(V5_SCRIPT_DIR))
from p1_v5_consensus_rrs_gate import check_gate as check_v5_review_gate  # noqa: E402
from p1_development_policy import is_pre_submission, phase_name  # noqa: E402
P2 = ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
OUT = V6 / "results" / "derived"
FIG = V6 / "results" / "figures"
MANIFEST = V6 / "results" / "v6_candidate_manifest.csv"
VINA = V5 / "results" / "v5_four_target_vina_affinities.csv"
RRS = P2 / "results" / "c_rrs_classification.csv"
ACSI = P2 / "results" / "c_acsi_scores.csv"
PNS = P2 / "results" / "c_pns_ranking.csv"
V6_REGISTER = V6 / "results" / "v6_review_register.json"
V5_REGISTER = V5 / "results" / "structural_pocket_independent_review.json"

TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]
MUTANTS = ["RRS_N51I", "RRS_C59R", "RRS_S108N", "RRS_I164L", "RRS_K76T", "RRS_K76A"]
CLASS_COLORS = {"A*": "#047857", "A": "#0f766e", "B": "#2563eb", "C": "#d97706", "D": "#dc2626"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_one(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if "smiles" not in df.columns:
        raise ValueError(f"{label} has no smiles column")
    df["smiles"] = df["smiles"].astype(str)
    if df["smiles"].duplicated().any():
        raise ValueError(f"{label} contains duplicate SMILES")
    return df


def load(internal_development: bool = False) -> tuple[pd.DataFrame, dict]:
    manifest = pd.read_csv(MANIFEST)
    required = {"candidate_id", "canonical_smiles", "v5_source_smiles", "cohort_id", "p2_source_sha256"}
    if not required.issubset(manifest.columns):
        raise ValueError("V6 manifest lacks required columns")
    if set(manifest["cohort_id"].dropna().unique()) != {"P2_SET_C_POLYPHARM_17"}:
        raise ValueError("V6 manifest contains an unexpected cohort")
    if len(manifest) != 17 or manifest["candidate_id"].nunique() != 17:
        raise ValueError("Expected 17 unique candidates in V6 manifest")
    if (manifest["canonical_smiles"] != manifest["v5_source_smiles"]).any():
        raise ValueError("V6 manifest canonical and V5 source SMILES differ")

    vina = pd.read_csv(VINA)
    if len(vina) != 17 or not set(["candidate_id", *[f"aff_{t}" for t in TARGETS]]).issubset(vina.columns):
        raise ValueError("V5 raw table is not the expected 17 x 4 panel")
    vina = vina.drop(columns=["mean_completed_targets"], errors="ignore")

    rrs = read_one(RRS, "RRS")
    acsi = read_one(ACSI, "ACSI")
    pns = read_one(PNS, "PNS")
    for name, df in [("RRS", rrs), ("ACSI", acsi), ("PNS", pns)]:
        if len(df) != 17:
            raise ValueError(f"{name} does not have 17 rows")

    # P2 files have the same candidate-set source hash. Join only on the
    # locked manifest's exact SMILES values, never by row order.
    base = manifest[["candidate_id", "canonical_smiles", "p2_source_rank", "cohort_id"]].copy()
    base = base.rename(columns={"canonical_smiles": "smiles"})
    expected_cohort = "P2_SET_C_POLYPHARM_17"
    expected_source_hash = str(manifest["p2_source_sha256"].iloc[0])
    if manifest["p2_source_sha256"].nunique() != 1:
        raise ValueError("V6 manifest has inconsistent P2 source hashes")
    expected_source = "results/candidate_selection/md_top20_candidates_polypharm.csv"
    for name, df, required_metric in [
        ("RRS", rrs, "RRS_mean"),
        ("ACSI", acsi, "ACSI"),
        ("PNS", pns, "PNS"),
    ]:
        if set(df["cohort_id"].dropna().unique()) != {expected_cohort}:
            raise ValueError(f"{name} contains an unexpected cohort")
        if "candidate_sha256" not in df.columns or df["candidate_sha256"].nunique() != 1:
            raise ValueError(f"{name} lacks a single source hash")
        if str(df["candidate_sha256"].iloc[0]) != expected_source_hash:
            raise ValueError(f"{name} hash does not match the locked V6 manifest hash")
        if set(df["candidate_file"].dropna().unique()) != {expected_source}:
            raise ValueError(f"{name} contains an unexpected candidate source")
        metric = df[["smiles", required_metric] + (["RRS_class"] if name == "RRS" else []) +
                   (["RRS_N51I", "RRS_C59R", "RRS_S108N", "RRS_I164L", "RRS_K76T", "RRS_K76A"] if name == "RRS" else []) +
                   (["D_DrugBank", "D_ANPDB", "fsp3", "NPL"] if name == "ACSI" else []) +
                   (["n_targets"] if name == "PNS" else [])]
        base = base.merge(metric, on="smiles", how="left", validate="one_to_one")
        if base[required_metric].isna().any():
            raise ValueError(f"{name} join incomplete")

    merged = base.merge(vina, on="candidate_id", validate="one_to_one")
    merged = merged.rename(columns={"smiles": "canonical_smiles"})
    # Keep only declared V6 analysis fields and explicit raw target-wise scores.
    keep = ["candidate_id", "canonical_smiles", "p2_source_rank", "cohort_id", "RRS_mean", "RRS_class",
            *MUTANTS, "ACSI", "D_DrugBank", "D_ANPDB", "fsp3", "NPL", "PNS", "n_targets",
            *[f"aff_{t}" for t in TARGETS]]
    merged = merged[keep].sort_values("p2_source_rank").reset_index(drop=True)
    if len(merged) != 17 or merged["candidate_id"].nunique() != 17:
        raise ValueError("Merged V6 data is not 17 unique candidates")
    register = json.loads(V6_REGISTER.read_text(encoding="utf-8"))
    v5register = json.loads(V5_REGISTER.read_text(encoding="utf-8"))
    v6_pending = register.get("status") == "PENDING_INDEPENDENT_REVIEW" and register.get("accepted_for_full_run") is False
    v5_pending = v5register.get("status") == "PENDING_INDEPENDENT_REVIEW" and v5register.get("accepted_for_full_run") is False
    # Authorization-mode fields remain bound to the future cryptographic
    # review protocol. They do not block pre-submission science; pending status
    # is the required truth condition for development.
    pre_submission = is_pre_submission()
    if internal_development:
        if not pre_submission:
            raise ValueError("explicit exploratory mode requires author reactivation policy after submission")
        if not (v6_pending and v5_pending):
            raise ValueError("internal development requires both V5 and V6 registers to remain truthfully pending")
    elif pre_submission:
        # During manuscript development, signatures do not block calculation.
        # However, malformed/tampered registers are still rejected so that an
        # exploratory artifact can never inherit an acceptance-like state.
        if not (v6_pending and v5_pending):
            raise ValueError("pre-submission registers must remain truthfully pending")
    else:
        v6_gate_ok, v6_gate_message = check_v6_review_gate(V6_REGISTER)
        if not v6_gate_ok:
            raise ValueError(f"V6 submission gate is not cryptographically accepted: {v6_gate_message}")
        v5_gate_ok, v5_gate_message = check_v5_review_gate(V5_REGISTER)
        if not v5_gate_ok:
            raise ValueError(f"V5 submission gate is not cryptographically accepted: {v5_gate_message}")
    return merged, {"v6": register, "v5": v5register}


def review_gate_provenance(gates: dict, exploratory: bool) -> dict:
    """Return non-promoting provenance for exploratory V6 outputs."""
    return {
        "v5_status": "PENDING_INDEPENDENT_REVIEW" if exploratory else gates["v5"]["status"],
        "v6_status": "PENDING_INDEPENDENT_REVIEW" if exploratory else gates["v6"]["status"],
        "internal_development": bool(exploratory),
        "submission_eligible": False if exploratory else True,
        "v5_accepted_for_full_run": False if exploratory else gates["v5"]["accepted_for_full_run"],
        "v6_accepted_for_full_run": False if exploratory else gates["v6"]["accepted_for_full_run"],
    }


def save_fig(fig: plt.Figure, stem: str) -> list[str]:
    outputs = []
    for ext in ("pdf", "png"):
        p = FIG / f"{stem}.{ext}"
        fig.savefig(p, bbox_inches="tight", dpi=300, facecolor="white")
        outputs.append(str(p.relative_to(ROOT)))
    plt.close(fig)
    return outputs


def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.7)
    ax.set_axisbelow(True)


def fig_rrs_heatmap(df: pd.DataFrame) -> list[str]:
    order = df.sort_values("RRS_mean", ascending=False)["candidate_id"].tolist()
    x = df.set_index("candidate_id").loc[order, MUTANTS]
    fig, ax = plt.subplots(figsize=(10.2, 7.0))
    image = ax.imshow(x.values, cmap="RdYlGn", vmin=50, vmax=135, aspect="auto")
    ax.set_xticks(np.arange(len(MUTANTS)), [m.replace("RRS_", "") for m in MUTANTS], rotation=30, ha="right")
    ax.set_yticks(np.arange(len(x.index)), [f"{c} ({df.set_index('candidate_id').loc[c, 'RRS_class']})" for c in x.index])
    ax.set_xlabel("Declared mutation panel")
    ax.set_ylabel("Candidate (exploratory class)")
    ax.set_title("Per-target RRS mutation profile", loc="left", fontweight="bold")
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            value = x.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{value:.0f}", ha="center", va="center", fontsize=7,
                        color="black" if 65 < value < 105 else "white")
    cbar = fig.colorbar(image, ax=ax, pad=0.02, fraction=0.04)
    cbar.set_label("RRS (% of wild-type Vina-score magnitude)")
    fig.text(0.5, 0.01, "Exploratory source-panel ratios; blank cells denote excluded non-binding wild-type targets.", ha="center", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    return save_fig(fig, "p1_v6_rrs_mutation_profiles")


def fig_metric_scatter(df: pd.DataFrame) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.5))
    for ax, xcol, xlabel, title in [
        (axes[0], "PNS", "PNS (network descriptor)", "PNS versus RRS"),
        (axes[1], "ACSI", "ACSI (chemical-space descriptor)", "ACSI versus RRS"),
    ]:
        for klass, g in df.groupby("RRS_class", sort=False):
            ax.scatter(g[xcol], g["RRS_mean"], s=52, color=CLASS_COLORS.get(klass, "#6b7280"),
                       edgecolor="white", linewidth=0.7, label=klass, alpha=0.9)
        for _, r in df.iterrows():
            ax.annotate(r["candidate_id"], (r[xcol], r["RRS_mean"]), xytext=(3, 3),
                        textcoords="offset points", fontsize=6, color="#374151")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("RRS mean (% score magnitude)")
        ax.set_title(title, loc="left", fontweight="bold")
        clean_axes(ax)
    axes[1].legend(title="RRS class", frameon=False, ncol=2, fontsize=8)
    fig.suptitle("Exploratory cross-metric relationships", fontsize=15, fontweight="bold", y=1.02)
    fig.text(0.5, -0.01, "Associations are descriptive and do not establish biological activity, causality, or resistance protection.", ha="center", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    return save_fig(fig, "p1_v6_exploratory_metric_relationships")


def fig_profile(df: pd.DataFrame) -> list[str]:
    means = df[[f"aff_{t}" for t in TARGETS]].mean().sort_values()
    fig, ax = plt.subplots(figsize=(9.3, 4.9))
    x = np.arange(len(means))
    bars = ax.bar(x, means.values, color=["#2563eb", "#0f766e", "#b45309", "#7c3aed"], width=0.62)
    ax.set_xticks(x, [c.replace("aff_", "") for c in means.index])
    ax.set_ylabel("Mean Vina score estimate (kcal mol$^{-1}$)")
    ax.set_title("Target-wise V5 score distributions: descriptive means", loc="left", fontweight="bold")
    for bar, val in zip(bars, means.values):
        ax.text(bar.get_x() + bar.get_width()/2, val - 0.12, f"{val:.3f}", ha="center", va="top", color="white", fontsize=9, fontweight="bold")
    clean_axes(ax)
    fig.text(0.5, 0.01, "Means are shown for within-target description only; no cross-target mean or consensus was used.", ha="center", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    return save_fig(fig, "p1_v6_targetwise_profile_summary")


def main() -> None:
    global OUT, FIG
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--internal-development",
        action="store_true",
        help="write exploratory V6 data/figures to results/exploratory while review is pending",
    )
    args = ap.parse_args()
    pre_submission = is_pre_submission()
    exploratory = bool(args.internal_development or pre_submission)
    if exploratory:
        OUT = V6 / "results" / "exploratory" / "derived"
        FIG = V6 / "results" / "exploratory" / "figures"
    else:
        # Outside the active development phase, `load()` must pass both
        # cryptographic gates before canonical outputs are created. This branch
        # is dormant until the author explicitly reactivates restrictions.
        OUT = V6 / "results" / "derived"
        FIG = V6 / "results" / "figures"
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    df, gates = load(internal_development=bool(args.internal_development))
    out_csv = OUT / "v6_integrated_candidate_metrics.csv"
    df.to_csv(out_csv, index=False, float_format="%.6f")
    outputs = [str(out_csv.relative_to(ROOT))]
    outputs += fig_rrs_heatmap(df)
    outputs += fig_metric_scatter(df)
    outputs += fig_profile(df)
    provenance = {
        "schema": "p1-v6-integrated-data-figures/v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": ("EXPLORATORY_UNVERIFIED_VOID_FOR_SUBMISSION" if exploratory
                    else "INDEPENDENT_REVIEW_ACCEPTED_SOURCE_PANEL"),
        "join_rule": "V6 candidate manifest canonical_smiles -> P2 source tables smiles; never row-order join",
        "scientific_boundary": [
            "Vina scores retained target-wise; mean_completed_targets excluded",
            "RRS/ACSI/PNS are descriptive source-panel metrics already present in P2 artifacts",
            "no new consensus, biological validation, or acceptance claim was generated",
            "RRS missing cells remain missing where non-binding wild-type targets were excluded",
        ],
        "n_candidates": int(len(df)),
        "sources": {str(p.relative_to(ROOT)): sha256(p) for p in [MANIFEST, VINA, V5 / "results" / "v5_four_target_vina_review_table.json", RRS, ACSI, PNS, V6_REGISTER, V5_REGISTER]},
        "generator": {
            "version": "1.0.0",
            "script": str(Path(__file__).relative_to(ROOT)),
            "configuration": {"targets": TARGETS, "figure_dpi": 300, "join": "exact_manifest_smiles"},
            "script_sha256": sha256(Path(__file__)),
            "python": sys.version,
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "pandas", "matplotlib")
            },
        },
        "outputs": outputs,
        "output_sha256": {path: sha256(ROOT / path) for path in outputs},
        "review_gates": {
            **review_gate_provenance(gates, exploratory),
            "phase": phase_name(),
        },
    }
    prov = OUT / "v6_integrated_data_figures_provenance.json"
    prov.write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": provenance["status"], "rows": len(df), "outputs": outputs + [str(prov.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
