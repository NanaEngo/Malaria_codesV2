#!/usr/bin/env python3
"""
P7 Phase 1.1 — Normalize P1 Set A data to required schema.

Reads data/p1_set_a_20_candidates.csv  (P2 Set C, 17 molecules)
Writes data/p1_set_a/p1_set_a_17_candidates.csv with columns:
    mol_id, SMILES, activity_label  (+ all original columns preserved)

Usage:
    python scripts/p7_normalize_p1_set_a.py
"""
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from rdkit import Chem


def main():
    p7_root = Path(__file__).resolve().parent.parent
    src     = p7_root / "data" / "p1_set_a_20_candidates.csv"
    out_dir = p7_root / "data" / "p1_set_a"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("P7 Phase 1.1 — Normalize P1 Set A")
    print("=" * 60)

    if not src.exists():
        print(f"ERROR: Source file not found: {src}")
        sys.exit(1)

    df = pd.read_csv(src)
    print(f"Source  : {src}")
    print(f"Shape   : {df.shape}")
    print(f"Columns : {list(df.columns)}")

    # ── Rename to required schema ─────────────────────────────────────────
    # Handle preferred SMILES column: canonical_smiles beats smiles
    if "canonical_smiles" in df.columns:
        df = df.rename(columns={"canonical_smiles": "SMILES"})
        # Drop duplicate 'smiles' column if both exist
        if "smiles" in df.columns:
            df = df.drop(columns=["smiles"])
    elif "smiles" in df.columns:
        df = df.rename(columns={"smiles": "SMILES"})

    if "activity" in df.columns:
        df = df.rename(columns={"activity": "activity_label"})
    if "molecule_id" in df.columns:
        df = df.rename(columns={"molecule_id": "mol_id"})

    # If no mol_id yet, use the first column
    if "mol_id" not in df.columns:
        df = df.rename(columns={df.columns[0]: "mol_id"})

    print(f"Columns after rename: {list(df.columns)}")

    # ── Validate SMILES ───────────────────────────────────────────────────
    valid_mask = df["SMILES"].apply(
        lambda s: Chem.MolFromSmiles(str(s)) is not None
    ).reset_index(drop=True)
    df = df.reset_index(drop=True)
    n_invalid  = (~valid_mask).sum()
    if n_invalid:
        print(f"WARNING : {n_invalid} invalid SMILES removed")
    df = df[valid_mask].reset_index(drop=True)

    df["activity_label"] = df["activity_label"].astype(int)
    n = len(df)
    n_active   = int(df["activity_label"].sum())
    n_inactive = n - n_active

    print(f"Valid molecules  : {n}")
    print(f"Active (label=1) : {n_active}")
    print(f"Inactive(label=0): {n_inactive}")

    # ── Save ──────────────────────────────────────────────────────────────
    out_file = out_dir / f"p1_set_a_{n}_candidates.csv"
    df.to_csv(out_file, index=False)

    sha256 = hashlib.sha256(out_file.read_bytes()).hexdigest()

    meta = {
        "source":       str(src.relative_to(p7_root)),
        "source_type":  "P2_SET_C_POLYPHARM_17 (used as P7 Phase-1 proof-of-concept cohort)",
        "n_molecules":  n,
        "n_active":     n_active,
        "n_inactive":   n_inactive,
        "columns":      list(df.columns),
        "sha256":       sha256,
        "timestamp":    pd.Timestamp.now().isoformat(),
    }
    meta_file = out_dir / "extraction_metadata.json"
    meta_file.write_text(json.dumps(meta, indent=2))

    print()
    print(f"✓ Saved : {out_file}")
    print(f"✓ SHA256: {sha256[:32]}...")
    print(f"✓ Meta  : {meta_file}")
    print()
    print("Phase 1.1 COMPLETE")


if __name__ == "__main__":
    main()
