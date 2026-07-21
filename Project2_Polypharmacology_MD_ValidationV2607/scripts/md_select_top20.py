"""
Paper 2 — Step 0: Select top 20 candidate molecules for MD validation.

Criteria (from roadmap):
  - MPO score >= 0.70  (primary leads)
  - SYBA score > 0     (synthesisable)
  - Selectivity Index > 10 (from c3 output)

Outputs:
  results/md_top20_candidates.csv   — ranked list with all scores
  results/md_top20_smiles.smi       — SMILES file for downstream use

Usage:
    python scripts/md_select_top20.py [--n 20]
"""

import argparse
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"


def load_and_merge() -> pd.DataFrame:
    mpo = pd.read_csv(RESULTS_DIR / "c6_primary_leads_synthesisable.csv")
    # c6 columns: input, weighted_mpo_score, syba_score, sa_score, qed
    mpo = mpo.rename(columns={"input": "smiles"})

    si = pd.read_csv(RESULTS_DIR / "c3_selectivity_index.csv")
    # c3 columns: SI, pf_nf54, hepg2  — index-aligned with mpo
    if len(si) == len(mpo):
        mpo["SI"] = si["SI"].values
    else:
        print(f"  Warning: SI row count ({len(si)}) != MPO row count ({len(mpo)}); SI filter skipped")
        mpo["SI"] = float("nan")

    return mpo


def select_top(df: pd.DataFrame, n: int) -> pd.DataFrame:
    mask = df["weighted_mpo_score"] >= 0.70
    mask &= df["syba_score"] > 0
    if df["SI"].notna().any():
        mask &= df["SI"] > 10

    filtered = df[mask].copy()
    filtered = filtered.sort_values("weighted_mpo_score", ascending=False)
    top = filtered.head(n).reset_index(drop=True)
    top.index = top.index + 1  # 1-based rank
    top.index.name = "rank"
    return top


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20, help="Number of candidates to select")
    args = parser.parse_args()

    print("=" * 60)
    print(f"Selecting top {args.n} MD candidates")
    print("=" * 60)

    df = load_and_merge()
    print(f"  Loaded {len(df)} molecules from c6_primary_leads_synthesisable.csv")

    top = select_top(df, args.n)
    print(f"  After filters (MPO>=0.70, SYBA>0, SI>10): {len(top)} selected")

    out_csv = RESULTS_DIR / "md_top20_candidates.csv"
    out_smi = RESULTS_DIR / "md_top20_smiles.smi"

    top.to_csv(out_csv)
    top["smiles"].to_csv(out_smi, index=False, header=False)

    print(f"\n  Saved: {out_csv}")
    print(f"  Saved: {out_smi}")
    print("\n  Top 5 preview:")
    print(top[["smiles", "weighted_mpo_score", "syba_score", "SI"]].head().to_string())


if __name__ == "__main__":
    main()
