#!/usr/bin/env python3
"""P2 — STRING threshold sensitivity for PNS (open item #2, DAR §9).

The canonical PNS (md_calculate_rrs_acsi_pns.py) uses the STRING PPI network
filtered at score >= 700. This script answers the reviewer question R5
("STRING 700 threshold not justified") by recomputing the composite centrality
and the imputed PfCRT PNS at the neighbouring STRING confidence thresholds
400 (medium) and 900 (highest), using the exact same centrality formula as the
canonical pipeline (composite of degree/betweenness/closeness/eigenvector,
each min-max normalised, 0.25 weight each), and comparing the resulting PNS
rankings to the canonical 700 baseline.

Status target: NOT_COMPUTED_MISSING_THRESHOLD_SPECIFIC_STRING_MATRICES -> COMPUTED.

Outputs (results/string_threshold_sensitivity_20260829/):
  - string_threshold_sensitivity.csv       (PNS per threshold, joined)
  - string_threshold_sensitivity_summary.json
  - STRING_Threshold_Sensitivity.tex       (table for the SI)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PPI = DATA_DIR / "external" / "ppi_network.tsv"
OUT_DIR = ROOT / "results" / "string_threshold_sensitivity_20260829"

THRESHOLDS = [400, 700, 900]
CANONICAL_THRESHOLD = 700

# STRING IDs for the P. falciparum 3D7 docking targets (same as canonical).
TARGETS = {
    "PfDHFR": "PF3D7_0417200",
    "PfCRT": "PF3D7_0709000",
}


def composite_centrality(df: pd.DataFrame, threshold: int) -> dict[str, float]:
    """Composite centrality C_j = 0.25*(C_D + C_B + C_C + C_E), normalised to
    [0,1] each — identical to the canonical load_ppi_centrality()."""
    import networkx as nx

    sub = df[df["score"] >= threshold]
    G = nx.Graph()
    for _, row in sub.iterrows():
        G.add_edge(row["protein_a"], row["protein_b"], weight=row["score"])

    def norm(d: dict) -> dict:
        mx = max(d.values()) if d else 1
        return {k: v / mx for k, v in d.items()} if mx > 0 else d

    if len(G.nodes()) == 0:
        return {}
    c_d = norm(dict(nx.degree_centrality(G)))
    c_b = norm(dict(nx.betweenness_centrality(G, normalized=True)))
    c_c = norm(dict(nx.closeness_centrality(G)))
    c_e = norm(dict(nx.eigenvector_centrality(G, max_iter=1000, tol=1e-6)))
    nodes = set(G.nodes())
    return {n: 0.25 * (c_d.get(n, 0) + c_b.get(n, 0) + c_c.get(n, 0) + c_e.get(n, 0))
            for n in nodes}


def main() -> None:
    if not PPI.exists():
        print(f"FAIL-CLOSED: {PPI} missing"); sys.exit(1)
    df = pd.read_csv(PPI, sep="\t")
    df["score"] = df["score"].astype(float)
    df["protein_a"] = df["protein_a"].astype(str)
    df["protein_b"] = df["protein_b"].astype(str)

    # Canonical docking panel (136 = 17 candidates x 8 states; WT rows only
    # enter the PNS, exactly as in the canonical calculate_pns()).
    dock = ROOT / "results" / "docking_mutants.csv"
    if not dock.exists():
        print(f"FAIL-CLOSED: {dock} missing"); sys.exit(1)
    dock_df = pd.read_csv(dock)
    wt_df = dock_df[dock_df["mutation"] == "WT"]

    def pns_ranking(cent: dict[str, float]) -> pd.DataFrame:
        mean_c = float(np.mean(list(cent.values()))) if cent else 1.0
        records = []
        for smiles, grp in wt_df.groupby("smiles"):
            scores = []
            for target, string_id in TARGETS.items():
                trows = grp[grp["target"] == target]
                if trows.empty:
                    continue
                dg = abs(trows["vina_score"].mean())
                cd = cent.get(string_id, mean_c)  # PfCRT imputed when absent
                scores.append(cd * dg)
            if scores:
                records.append({"smiles": smiles, "PNS": float(np.mean(scores))})
        return pd.DataFrame(records).sort_values("PNS", ascending=False).reset_index(drop=True)

    cents = {th: composite_centrality(df, th) for th in THRESHOLDS}
    pns_by_th = {th: pns_ranking(c) for th, c in cents.items()}

    out = []
    for th in THRESHOLDS:
        cent = cents[th]
        mean_c = float(np.mean(list(cent.values()))) if cent else 1.0
        n_edges = int((df["score"] >= th).sum())
        out.append({
            "threshold": th,
            "n_edges": n_edges,
            "n_nodes": len(cent),
            "centrality_PfDHFR": cent.get(TARGETS["PfDHFR"]),
            "centrality_PfCRT_imputed": mean_c if TARGETS["PfCRT"] not in cent
            else cent[TARGETS["PfCRT"]],
            "mean_centrality": mean_c,
        })
    summary_df = pd.DataFrame(out)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(OUT_DIR / "string_threshold_sensitivity.csv", index=False)

    # Per-threshold PNS, joined for direct comparison.
    pns_wide = pns_by_th[CANONICAL_THRESHOLD][["smiles", "PNS"]].rename(
        columns={"PNS": f"PNS_{CANONICAL_THRESHOLD}"})
    for th in THRESHOLDS:
        if th == CANONICAL_THRESHOLD:
            continue
        pns_wide = pns_wide.merge(
            pns_by_th[th][["smiles", "PNS"]].rename(columns={"PNS": f"PNS_{th}"}),
            on="smiles", how="outer")
    pns_wide.to_csv(OUT_DIR / "string_threshold_pns_ranking.csv", index=False)

    # Rank correlations + top-5 Jaccard between thresholds.
    pns_corr = {}
    for a in THRESHOLDS:
        for b in THRESHOLDS:
            if a >= b:
                continue
            m = pns_wide[[f"PNS_{a}", f"PNS_{b}"]].dropna()
            rho, p = spearmanr(m[f"PNS_{a}"], m[f"PNS_{b}"])
            ta = set(pns_by_th[a]["smiles"].head(5))
            tb = set(pns_by_th[b]["smiles"].head(5))
            pns_corr[f"{a}_vs_{b}"] = {
                "pns_rho": round(float(rho), 4),
                "pns_p": round(float(p), 6),
                "n_candidates": int(len(m)),
                "top5_jaccard": round(len(ta & tb) / len(ta | tb), 4),
            }

    # Spearman correlations between the threshold-specific centrality vectors.
    nodes = sorted(set().union(*[set(c) for c in cents.values()]))
    corr = {}
    for a in THRESHOLDS:
        for b in THRESHOLDS:
            if a >= b:
                continue
            va = np.array([cents[a].get(n, np.nan) for n in nodes])
            vb = np.array([cents[b].get(n, np.nan) for n in nodes])
            mask = ~(np.isnan(va) | np.isnan(vb))
            if mask.sum() >= 3:
                rho, p = spearmanr(va[mask], vb[mask])
                corr[f"{a}_vs_{b}"] = {"rho": round(float(rho), 4),
                                       "p": round(float(p), 6),
                                       "n_shared_nodes": int(mask.sum())}

    report = {
        "status": "COMPUTED",
        "date": "2026-08-29",
        "ppi_file": str(PPI),
        "docking_panel": str(dock),
        "canonical_threshold": CANONICAL_THRESHOLD,
        "thresholds": THRESHOLDS,
        "centrality_spearman": corr,
        "pns_spearman": pns_corr,
        "notes": (
            "Composite centrality (degree/betweenness/closeness/eigenvector, "
            "0.25 each) identical to the canonical load_ppi_centrality(); "
            "threshold changes only the edge filter. PfCRT centrality is "
            "imputed with the interactome mean at each threshold. PNS uses the "
            "canonical WT docking panel (docking_mutants.csv) and the formula "
            "Σ_j C_j × |ΔG_j| / n_j, identical to calculate_pns()."
        ),
    }
    with open(OUT_DIR / "string_threshold_sensitivity_summary.json", "w") as f:
        json.dump(report, f, indent=2)

    # LaTeX table for the SI.
    lines = [
        "\\begin{table}[htbp]",
        "  \\centering",
        "  \\caption{STRING confidence-threshold sensitivity of the composite",
        "  interactome centrality used in PNS (edges filtered at score $\\geq$ threshold).",
        "  Canonical threshold 700; 400 and 900 are the STRING medium/highest",
        "  confidence bands. Centrality formula identical to the canonical pipeline.}",
        "  \\label{tab:string-threshold}",
        "  \\begin{tabular}{lccc}",
        "    \\toprule",
        "    STRING threshold & \\num{400} & \\num{700} & \\num{900} \\\\",
        "    \\midrule",
    ]
    def fmt(x): return "---" if x is None else f"{x:.4f}"
    lines.append("    Edges & " + " & ".join(str(r) for r in summary_df["n_edges"]) + r" \\")
    lines.append("    Nodes & " + " & ".join(str(r) for r in summary_df["n_nodes"]) + r" \\")
    lines.append("    PfDHFR centrality & " + " & ".join(fmt(r) for r in summary_df["centrality_PfDHFR"]) + r" \\")
    lines.append("    PfCRT (imputed) & " + " & ".join(fmt(r) for r in summary_df["centrality_PfCRT_imputed"]) + r" \\")
    lines += ["    \\bottomrule", "  \\end{tabular}", "\\end{table}"]
    (OUT_DIR / "STRING_Threshold_Sensitivity.tex").write_text("\n".join(lines) + "\n")

    print(summary_df.to_string(index=False))
    print("\nCentrality Spearman:", json.dumps(corr, indent=2))
    print("\nPNS ranking Spearman (candidate level):", json.dumps(pns_corr, indent=2))
    print("\nPNS ranking (canonical 700):")
    print(pns_by_th[CANONICAL_THRESHOLD].to_string(index=False))
    print(f"\nOutputs in {OUT_DIR}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
