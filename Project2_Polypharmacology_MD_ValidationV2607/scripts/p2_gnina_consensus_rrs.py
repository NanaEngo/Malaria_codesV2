#!/usr/bin/env python3
"""Consensus RRS comparison: GNINA CNN vs Vina scoring on the external panel.

Reads the GNINA consensus scores (312 records, 39 ligands x 8 states) and
recomputes the frozen P2 RRS estimand under each scoring layer:

    RRS_mut = |S_mut,t| / |S_WT,t| x 100      (WT non-binder |S_WT,t| < 5.0
                                              kcal/mol excluded per target)

with the same per-mutant averaging across binding targets and the same
dual-criterion class assignment as the canonical P2 pipeline. The Vina column
comes from the pose REMARK (identical to the canonical external RRS); the CNN
column is the GNINA 1.3.2 CNN affinity of the same pose.

Outputs (fail-closed):
  - gnina_consensus_rrs.csv        per-ligand RRS profile under both layers
  - gnina_consensus_rrs.json       summary: class concordance/discordance,
                                   Spearman Vina-CNN, per-class counts
  - consensus_discordances.csv     ligands whose RRS class differs by layer

Boundary: this is a consensus sensitivity on a non-overlapping external panel;
it is NOT experimental validation and NOT an MD estimate. Vina-only remains
the canonical estimand.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Project2_Polypharmacology_MD_ValidationV2607/results/robustness_transfer_20260827"
SCORES = BASE / "gnina_consensus_20260828" / "gnina_consensus_scores.csv"
OUT_CSV = BASE / "gnina_consensus_rrs.csv"
OUT_JSON = BASE / "gnina_consensus_rrs.json"
OUT_DISC = BASE / "consensus_discordances.csv"
WT_THRESHOLD = 5.0  # kcal/mol
EXPECTED_ROWS = 312  # 39 ligands x 8 states; EXT-039 declared EMBED_FAILURE

MUTATIONS = ["N51I", "C59R", "S108N", "I164L", "K76T", "K76A"]
TARGETS = ["PfDHFR", "PfCRT"]


def parse_state(state: str) -> tuple[str, str] | None:
    for target in TARGETS:
        if state == f"{target}_WT":
            return target, "WT"
        for mut in MUTATIONS:
            if state == f"{target}_{mut}":
                return target, mut
    return None


def classify_rrs(rrs_values: dict) -> str:
    mutant_rrs = {k: v for k, v in rrs_values.items() if k != "WT"}
    if not mutant_rrs:
        return "D"
    vals = list(mutant_rrs.values())
    if all(v >= 80 for v in vals) and min(vals) >= 70:
        return "A"
    if all(v >= 70 for v in vals):
        return "B"
    if any(v >= 80 for v in vals):
        return "C"
    return "D"


def rrs_profile(rows: list[dict], layer: str, eligible_targets: set[str] | None = None) -> dict:
    """Compute {mutant: RRS} for one ligand under one scoring layer.

    Target eligibility is decided once, on the canonical Vina scale
    (|S_WT,t| >= WT_THRESHOLD). The CNN layer is scored on the SAME eligible
    targets so the two layers share an identical estimand; the 5.0 kcal/mol
    threshold is Vina-calibrated and is not re-applied to the CNN scale.
    """
    wt_by_target = {}
    mut_scores = {}
    for r in rows:
        parsed = parse_state(r["state"])
        if parsed is None:
            continue
        target, state = parsed
        val = float(r[layer])
        if state == "WT":
            wt_by_target[target] = val
        else:
            mut_scores.setdefault(target, {})[state] = val
    profile = {}
    for target, wt in wt_by_target.items():
        if eligible_targets is not None:
            if target not in eligible_targets:
                continue
        else:
            if abs(wt) < WT_THRESHOLD:
                continue
        for mut in MUTATIONS:
            if mut in mut_scores.get(target, {}):
                profile[mut] = abs(mut_scores[target][mut]) / abs(wt) * 100.0
    return profile


def spearman(xs: list[float], ys: list[float]) -> float:
    def rank(vals):
        idx = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(idx):
            j = i
            while j + 1 < len(idx) and vals[idx[j + 1]] == vals[idx[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[idx[k]] = avg
            i = j + 1
        return ranks

    if len(xs) < 3:
        return float("nan")
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def main() -> int:
    if not SCORES.is_file():
        print(f"ERROR: {SCORES} not found; run p2_gnina_consensus_rescore.py first")
        return 2
    rows = list(csv.DictReader(SCORES.open(newline="")))
    if len(rows) != EXPECTED_ROWS:
        print(f"ERROR: expected {EXPECTED_ROWS} scored rows, found {len(rows)}; aborting fail-closed")
        return 2
    bad = [r["state"] for r in rows if parse_state(r["state"]) is None]
    if bad:
        print(f"ERROR: {len(bad)} unrecognized states; aborting fail-closed")
        return 2

    ligands = sorted({r["ligand"] for r in rows})
    out_rows = []
    vina_rrs = {}
    cnn_rrs = {}
    for lig in ligands:
        sub = [r for r in rows if r["ligand"] == lig]
        # Decide eligibility once on the canonical Vina scale; CNN uses the
        # same eligible targets (identical estimand, no Vina-calibrated
        # threshold transposed to the CNN scale).
        vina_wt = {}
        for r in sub:
            parsed = parse_state(r["state"])
            if parsed and parsed[1] == "WT":
                vina_wt[parsed[0]] = abs(float(r["vina_score"])) >= WT_THRESHOLD
        eligible = {t for t, ok in vina_wt.items() if ok}
        pv = rrs_profile(sub, "vina_score", eligible)
        pc = rrs_profile(sub, "gnina_cnn_score", eligible)
        vina_rrs[lig] = pv
        cnn_rrs[lig] = pc
        if not pv:
            cls_v = ""
            mean_v = ""
        else:
            cls_v = classify_rrs(pv)
            mean_v = round(sum(pv.values()) / len(pv), 1)
        if not pc:
            cls_c = ""
            mean_c = ""
        else:
            cls_c = classify_rrs(pc)
            mean_c = round(sum(pc.values()) / len(pc), 1)
        out_rows.append({
            "ligand": lig,
            "RRS_mean_Vina": mean_v,
            "RRS_class_Vina": cls_v,
            "RRS_mean_CNN": mean_c,
            "RRS_class_CNN": cls_c,
            "discordant": "YES" if (cls_v and cls_c and cls_v != cls_c) else "NO",
        })

    # class counts per layer (only ligands with a non-empty profile)
    counts_vina = {k: 0 for k in ["A", "B", "C", "D"]}
    counts_cnn = {k: 0 for k in ["A", "B", "C", "D"]}
    for r in out_rows:
        if r["RRS_class_Vina"] in counts_vina:
            counts_vina[r["RRS_class_Vina"]] += 1
        if r["RRS_class_CNN"] in counts_cnn:
            counts_cnn[r["RRS_class_CNN"]] += 1

    # Spearman on ligand-level mean RRS (only ligands with both layers finite)
    pairs = [(r["RRS_mean_Vina"], r["RRS_mean_CNN"])
             for r in out_rows if r["RRS_mean_Vina"] != "" and r["RRS_mean_CNN"] != ""]
    rho = spearman([p[0] for p in pairs], [p[1] for p in pairs]) if pairs else float("nan")

    # per-mutant RRS correlation across ligands
    mut_rhos = {}
    for mut in MUTATIONS:
        xs, ys = [], []
        for lig in ligands:
            if mut in vina_rrs[lig] and mut in cnn_rrs[lig]:
                xs.append(vina_rrs[lig][mut])
                ys.append(cnn_rrs[lig][mut])
        if len(xs) >= 3:
            mut_rhos[mut] = round(spearman(xs, ys), 3)
        else:
            mut_rhos[mut] = None

    n_disc = sum(1 for r in out_rows if r["discordant"] == "YES")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    disc_rows = [r for r in out_rows if r["discordant"] == "YES"]
    with open(OUT_DISC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(disc_rows)

    summary = {
        "status": "COMPUTED_CONSENSUS_RRS_SENSITIVITY",
        "estimand": "RRS = |S_mut,t|/|S_WT,t| x 100 per target; WT non-binder < 5.0 kcal/mol excluded",
        "estimand_note": "Target eligibility decided once on the canonical Vina scale; the CNN layer is scored on the same eligible targets (5.0 kcal/mol is Vina-calibrated and not re-applied to the CNN scale)",
        "boundary": "Consensus sensitivity on the non-overlapping external panel; Vina-only remains canonical; not experimental validation",
        "n_ligands": len(ligands),
        "n_rows": len(rows),
        "n_discordant_classes": n_disc,
        "class_counts_Vina": counts_vina,
        "class_counts_CNN": counts_cnn,
        "spearman_meanRRS_Vina_vs_CNN": round(rho, 4) if not math.isnan(rho) else None,
        "per_mutant_spearman_Vina_vs_CNN": mut_rhos,
    }
    (BASE / "gnina_consensus_rrs.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
