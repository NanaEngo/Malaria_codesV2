"""
Paper 2 — Steps 3–5: Calculate RRS, ACSI, and PNS metrics.

Resistance Resilience Score (RRS)
    RRS_m = (|ΔG_mutant_m| / |ΔG_WT|) × 100
    RRS   = mean(RRS_m) over all mutants
    Classes: A (≥80% all), B (≥70% for 4-5), C (mutant-specific), D (<60% any)

African Chemical Space Index (ACSI)
    ACSI = 0.40×D_DrugBank + 0.25×D_ANPDB + 0.20×fsp3 + 0.15×NPL
    All components min-max normalised to [0,1].

Polypharmacology Network Score (PNS)
    PNS_i = Σ_j (C_j × |ΔG_i,j|) / n_i
    where C_j = 0.25*(C_D,j + C_B,j + C_C,j + C_E,j) = composite centrality of target j.

Inputs expected:
    results/md_top20_candidates.csv          — from md_select_top20.py
    results/docking_mutants.csv              — Vina scores vs WT + 6 mutants
                                               columns: smiles, target, mutation, vina_score
    data/external/anpdb_smiles.csv           — ANPDB reference (smiles column)
    data/external/drugbank_smiles.csv        — DrugBank reference (smiles column)
    data/external/ppi_network.tsv            — STRING PPI (protein_a, protein_b, score)

Outputs:
    results/c_rrs_classification.csv
    results/c_acsi_scores.csv
    results/c_pns_ranking.csv

Usage:
    python scripts/md_calculate_rrs_acsi_pns.py [--skip-rrs] [--skip-acsi] [--skip-pns]
"""

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import DataStructs
from rdkit.Chem import rdFingerprintGenerator

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

warnings.filterwarnings("ignore", category=UserWarning)

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
DATA_DIR = PROJECT_DIR / "data"

# Docking targets and their STRING protein IDs (P. falciparum 3D7, taxid 36329)
TARGETS = {
    "PfDHFR": "PF3D7_0417200",
    "PfCRT":  "PF3D7_0709000",
    "PfATP4": "PF3D7_1211900",
    "PfClpP": "PF3D7_0311400",
}

MUTATIONS = ["WT", "N51I", "C59R", "S108N", "I164L", "K76T", "K76A"]


# ---------------------------------------------------------------------------
# RRS
# ---------------------------------------------------------------------------

def classify_rrs(rrs_values: dict, dg_wt: float = None) -> str:
    """Classify a compound by its RRS profile across mutants.

    Dual-criterion classification (per roadmap v1.4):
      Class A*: |ΔG_WT| >= 7.0 kcal/mol  AND  RRS >= 80% all mutants
      Class A:  RRS >= 80% all mutants  (|ΔG_WT| >= 5.0 by pre-filter)
      Class B:  RRS >= 70% all mutants but not all >= 80%
      Class C:  RRS >= 80% for 1-2 mutants only
      Class D:  RRS < 60% for any mutant
    """
    mutant_rrs = {k: v for k, v in rrs_values.items() if k != "WT"}
    if not mutant_rrs:
        return "D"
    vals = list(mutant_rrs.values())
    if all(v >= 80 for v in vals) and min(vals) >= 70:
        if dg_wt is not None and abs(dg_wt) >= 7.0:
            return "A*"
        return "A"
    if all(v >= 70 for v in vals):
        return "B"
    if any(v >= 80 for v in vals):
        return "C"
    return "D"


def calculate_rrs(docking_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute RRS for each compound from docking scores vs WT and mutants.

    docking_df columns: smiles, target, mutation, vina_score
    """
    records = []
    for smiles, grp in docking_df.groupby("smiles"):
        wt_rows = grp[grp["mutation"] == "WT"]
        if wt_rows.empty:
            continue
        dg_wt = wt_rows["vina_score"].mean()
        if dg_wt == 0:
            continue
        # Pre-filter: weak binders excluded from RRS (roadmap §Step 6)
        if abs(dg_wt) < 5.0:
            continue

        rrs_vals = {"WT": 100.0}
        for mut in [m for m in MUTATIONS if m != "WT"]:
            mut_rows = grp[grp["mutation"] == mut]
            if mut_rows.empty:
                continue
            dg_mut = mut_rows["vina_score"].mean()
            # Use absolute values: ΔG is negative; |ΔG_mut|/|ΔG_WT| × 100
            rrs_vals[mut] = (abs(dg_mut) / abs(dg_wt)) * 100.0

        rrs_mean = np.mean([v for k, v in rrs_vals.items() if k != "WT"])
        rrs_class = classify_rrs(rrs_vals, dg_wt)

        row = {"smiles": smiles, "RRS_mean": rrs_mean, "RRS_class": rrs_class}
        row.update({f"RRS_{k}": v for k, v in rrs_vals.items()})
        records.append(row)

    return pd.DataFrame(records).sort_values("RRS_mean", ascending=False)


# ---------------------------------------------------------------------------
# ACSI
# ---------------------------------------------------------------------------

def tanimoto_min_distance(smiles_list: list[str], ref_fps: list) -> np.ndarray:
    """Return minimum Tanimoto distance (1 - max_similarity) to reference set."""
    distances = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            distances.append(1.0)
            continue
        fp = morgan_gen.GetFingerprint(mol)
        sims = DataStructs.BulkTanimotoSimilarity(fp, ref_fps)
        distances.append(1.0 - max(sims) if sims else 1.0)
    return np.array(distances)


def compute_fsp3(smiles_list: list[str]) -> np.ndarray:
    vals = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        vals.append(rdMolDescriptors.CalcFractionCSP3(mol) if mol else 0.0)
    return np.array(vals)


def compute_npl(smiles_list: list[str]) -> np.ndarray:
    """Natural product-likeness score via RDKit (Ertl & Schuffenhauer)."""
    try:
        from rdkit.Chem.rdMolDescriptors import CalcNPLikeliness
        vals = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            vals.append(CalcNPLikeliness(mol) if mol else 0.0)
        return np.array(vals)
    except ImportError:
        # Fallback: use fraction of ring atoms as a proxy
        vals = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                vals.append(0.0)
                continue
            ring_atoms = sum(1 for a in mol.GetAtoms() if a.IsInRing())
            vals.append(ring_atoms / mol.GetNumAtoms() if mol.GetNumAtoms() > 0 else 0.0)
        return np.array(vals)


def minmax(arr: np.ndarray) -> np.ndarray:
    lo, hi = arr.min(), arr.max()
    return (arr - lo) / (hi - lo) if hi > lo else np.zeros_like(arr)


def calculate_acsi(smiles_list: list[str]) -> pd.DataFrame:
    """Compute ACSI for each SMILES."""
    def load_fps(csv_path: Path) -> list:
        if not csv_path.exists():
            print(f"  Warning: {csv_path.name} not found; component set to 0")
            return []
        df = pd.read_csv(csv_path)
        fps = []
        for smi in df["smiles"].dropna():
            mol = Chem.MolFromSmiles(smi)
            if mol:
                fps.append(morgan_gen.GetFingerprint(mol))
        return fps

    print("  Loading reference fingerprints...")
    drugbank_fps = load_fps(DATA_DIR / "external" / "drugbank_smiles.csv")
    anpdb_fps    = load_fps(DATA_DIR / "external" / "anpdb_smiles.csv")

    print("  Computing distance components...")
    d_drugbank = tanimoto_min_distance(smiles_list, drugbank_fps) if drugbank_fps else np.ones(len(smiles_list))
    d_anpdb    = tanimoto_min_distance(smiles_list, anpdb_fps)    if anpdb_fps    else np.ones(len(smiles_list))
    fsp3       = compute_fsp3(smiles_list)
    npl        = compute_npl(smiles_list)

    # Normalise each component to [0,1]
    d_db_n  = minmax(d_drugbank)
    d_an_n  = minmax(d_anpdb)
    fsp3_n  = minmax(fsp3)
    npl_n   = minmax(npl)

    acsi = 0.40 * d_db_n + 0.25 * d_an_n + 0.20 * fsp3_n + 0.15 * npl_n

    return pd.DataFrame({
        "smiles":       smiles_list,
        "ACSI":         acsi,
        "D_DrugBank":   d_drugbank,
        "D_ANPDB":      d_anpdb,
        "fsp3":         fsp3,
        "NPL":          npl,
    }).sort_values("ACSI", ascending=False)


# ---------------------------------------------------------------------------
# PNS
# ---------------------------------------------------------------------------

def load_ppi_centrality() -> dict[str, float]:
    """
    Load STRING PPI network and compute composite centrality for each target.
    Composite: C_j = 0.25*(C_D + C_B + C_C + C_E), each normalised to [0,1].
    Falls back to equal weights if network file or networkx is missing.
    """
    ppi_file = DATA_DIR / "external" / "ppi_network.tsv"
    if not ppi_file.exists():
        print(f"  Warning: {ppi_file.name} not found; using equal centrality weights")
        return {t: 1.0 for t in TARGETS.values()}

    try:
        import networkx as nx
    except ImportError:
        print("  Warning: networkx not installed; falling back to degree centrality only")
        # Degree-only fallback
        df = pd.read_csv(ppi_file, sep="\t")
        df = df[df["score"] >= 700]
        degree: dict[str, int] = {}
        for _, row in df.iterrows():
            for col in ["protein_a", "protein_b"]:
                degree[row[col]] = degree.get(row[col], 0) + 1
        max_deg = max(degree.values()) if degree else 1
        return {p: d / max_deg for p, d in degree.items()}

    df = pd.read_csv(ppi_file, sep="\t")
    df = df[df["score"] >= 700]

    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["protein_a"], row["protein_b"], weight=row["score"])

    def norm(d: dict) -> dict:
        mx = max(d.values()) if d else 1
        return {k: v / mx for k, v in d.items()} if mx > 0 else d

    c_d = norm(dict(nx.degree_centrality(G)))
    c_b = norm(dict(nx.betweenness_centrality(G, normalized=True)))
    c_c = norm(dict(nx.closeness_centrality(G)))
    c_e = norm(dict(nx.eigenvector_centrality(G, max_iter=1000, tol=1e-6)))

    nodes = set(G.nodes())
    composite = {
        n: 0.25 * (c_d.get(n, 0) + c_b.get(n, 0) + c_c.get(n, 0) + c_e.get(n, 0))
        for n in nodes
    }
    return composite


def calculate_pns(docking_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute PNS_i = Σ_j (C_D,j × |ΔG_i,j|) / n_i
    using WT docking scores only.
    """
    centrality = load_ppi_centrality()
    
    # Impute missing centralities (e.g., PfCRT) with the interactome mean
    mean_centrality = np.mean(list(centrality.values())) if centrality else 1.0

    records = []
    wt_df = docking_df[docking_df["mutation"] == "WT"]

    for smiles, grp in wt_df.groupby("smiles"):
        scores = []
        for target, string_id in TARGETS.items():
            target_rows = grp[grp["target"] == target]
            if target_rows.empty:
                continue
            dg = abs(target_rows["vina_score"].mean())
            cd = centrality.get(string_id, mean_centrality)
            scores.append(cd * dg)

        if scores:
            pns = np.mean(scores)
            records.append({"smiles": smiles, "PNS": pns, "n_targets": len(scores)})

    return pd.DataFrame(records).sort_values("PNS", ascending=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-rrs",  action="store_true")
    parser.add_argument("--skip-acsi", action="store_true")
    parser.add_argument("--skip-pns",  action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("Paper 2 metrics: RRS / ACSI / PNS")
    print("=" * 60)

    candidates = pd.read_csv(RESULTS_DIR / "md_top20_candidates.csv")
    smiles_list = candidates["smiles"].tolist()

    # --- RRS ---
    if not args.skip_rrs:
        docking_file = RESULTS_DIR / "docking_mutants.csv"
        if docking_file.exists():
            print("\nCalculating RRS...")
            docking_df = pd.read_csv(docking_file)
            rrs_df = calculate_rrs(docking_df)
            out = RESULTS_DIR / "c_rrs_classification.csv"
            rrs_df.to_csv(out, index=False)
            print(f"  Saved: {out}")
            print(f"  Class A (pan-resilient): {(rrs_df['RRS_class']=='A').sum()}")
            print(f"  Class B (partially):     {(rrs_df['RRS_class']=='B').sum()}")
            print(f"  Class C (specific):      {(rrs_df['RRS_class']=='C').sum()}")
            print(f"  Class D (vulnerable):    {(rrs_df['RRS_class']=='D').sum()}")
        else:
            print(f"\n  Skipping RRS: {docking_file.name} not found")
            print("  Run mutant docking first (AutoDock Vina vs 6 mutants + WT)")

    # --- ACSI ---
    if not args.skip_acsi:
        print("\nCalculating ACSI...")
        acsi_df = calculate_acsi(smiles_list)
        out = RESULTS_DIR / "c_acsi_scores.csv"
        acsi_df.to_csv(out, index=False)
        print(f"  Saved: {out}")
        print(f"  ACSI > 0.7 (highly African NP-like): {(acsi_df['ACSI'] > 0.7).sum()}")
        print(f"  ACSI 0.5–0.7 (moderately):           {((acsi_df['ACSI'] >= 0.5) & (acsi_df['ACSI'] <= 0.7)).sum()}")
        print(f"  ACSI < 0.5 (synthetic-like):         {(acsi_df['ACSI'] < 0.5).sum()}")

    # --- PNS ---
    if not args.skip_pns:
        docking_file = RESULTS_DIR / "docking_mutants.csv"
        if docking_file.exists():
            print("\nCalculating PNS...")
            docking_df = pd.read_csv(docking_file)
            pns_df = calculate_pns(docking_df)
            out = RESULTS_DIR / "c_pns_ranking.csv"
            pns_df.to_csv(out, index=False)
            print(f"  Saved: {out}")
            if not pns_df.empty:
                print(f"  Top PNS: {pns_df.iloc[0]['PNS']:.3f} ({pns_df.iloc[0]['smiles'][:40]}...)")
        else:
            print(f"\n  Skipping PNS: {docking_file.name} not found")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
