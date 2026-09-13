#!/usr/bin/env python3
"""Prepare the LISH-MoA Kaggle package for leak-audited external benchmarks.

This script deliberately does not download Kaggle data.  Supply a directory
containing train_features.csv, train_targets_scored.csv, and train_drug.csv.
Repeated assay observations are aggregated at drug_id before any split.

Optional structures.csv must contain exactly: drug_id, smiles.  Duplicate
mapping rows or invalid SMILES are rejected; repeated canonical SMILES across
different drug IDs are collapsed explicitly before structure-only analyses.
Unmapped compounds remain in the phenotype artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results" / "lish_moa"
REQUIRED = ("train_features.csv", "train_targets_scored.csv", "train_drug.csv")


def canonical_smiles(value: object) -> str | None:
    if pd.isna(value):
        return None
    mol = Chem.MolFromSmiles(str(value))
    return Chem.MolToSmiles(mol, canonical=True) if mol is not None else None



def load_and_validate(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    missing = [name for name in REQUIRED if not (raw_dir / name).exists()]
    if missing:
        raise FileNotFoundError("Missing required LISH-MoA file(s): " + ", ".join(missing))
    features = pd.read_csv(raw_dir / "train_features.csv")
    targets = pd.read_csv(raw_dir / "train_targets_scored.csv")
    drug = pd.read_csv(raw_dir / "train_drug.csv")
    for frame, name in ((features, "features"), (targets, "targets"), (drug, "drug")):
        if "sig_id" not in frame.columns:
            raise ValueError(f"{name} is missing sig_id")
        if frame["sig_id"].duplicated().any():
            raise ValueError(f"{name} contains duplicated sig_id")
    if "drug_id" not in drug.columns:
        raise ValueError("train_drug.csv is missing drug_id")
    if set(features.sig_id) != set(drug.sig_id) or set(targets.sig_id) != set(features.sig_id):
        raise ValueError("sig_id sets do not match across the three required files")
    return features, targets, drug


def build_drug_level(features: pd.DataFrame, targets: pd.DataFrame,
                     drug: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    joined = features.merge(drug[["sig_id", "drug_id"]], on="sig_id", validate="one_to_one")
    joined = joined.merge(targets, on="sig_id", validate="one_to_one", suffixes=("", "_target"))
    target_cols = [c for c in targets.columns if c != "sig_id"]
    numeric_cols = [c for c in features.columns if c.startswith(("g-", "c-"))]
    rows = []
    for drug_id, group in joined.groupby("drug_id", sort=True):
        row: dict[str, object] = {"drug_id": drug_id, "n_observations": int(len(group))}
        for col in numeric_cols:
            row[col] = float(pd.to_numeric(group[col], errors="coerce").mean())
        # Encode assay metadata as aggregate numeric covariates.
        row["cp_time_hours"] = float(pd.to_numeric(group.get("cp_time"), errors="coerce").mean()) if "cp_time" in group else np.nan
        dose = group.get("cp_dose")
        row["cp_dose_high_fraction"] = float(dose.astype(str).str.lower().eq("high").mean()) if dose is not None else np.nan
        cptype = group.get("cp_type")
        row["cp_type_trt_fraction"] = float(cptype.astype(str).eq("trt_cp").mean()) if cptype is not None else np.nan
        for col in target_cols:
            values = pd.to_numeric(group[col], errors="coerce").fillna(0)
            row[f"moa_{col}"] = int(values.max() > 0)
        rows.append(row)
    out = pd.DataFrame(rows)
    report = {
        "n_observations": int(len(joined)),
        "n_drugs": int(len(out)),
        "n_scored_targets": len(target_cols),
        "target_columns": target_cols,
        "n_control_observations": int((features.get("cp_type", pd.Series(dtype=str)) == "ctl_vehicle").sum()),
        "duplicate_observation_distribution": joined.groupby("drug_id").size().value_counts().sort_index().astype(int).to_dict(),
        "label_prevalence": {f"moa_{c}": int(out[f"moa_{c}"].sum()) for c in target_cols},
        "label_aggregation": "max across assay conditions per drug_id (ever_observed_MoA)",
    }
    return out, report


def add_structure_mapping(drug_level: pd.DataFrame, mapping_path: Path) -> tuple[pd.DataFrame, dict]:
    mapping = pd.read_csv(mapping_path)
    if not {"drug_id", "smiles"}.issubset(mapping.columns):
        raise ValueError("Structure mapping must contain drug_id and smiles columns")
    mapping = mapping[["drug_id", "smiles"]].copy()
    if mapping.drug_id.duplicated().any():
        raise ValueError("Structure mapping contains duplicate drug_id; refusing ambiguous mapping")
    mapping["smiles"] = mapping["smiles"].map(canonical_smiles)
    if mapping["smiles"].isna().any():
        raise ValueError("Structure mapping contains invalid or unparsable SMILES")
    mapped = drug_level.merge(mapping, on="drug_id", how="left", validate="one_to_one")
    structure = mapped.dropna(subset=["smiles"]).copy()
    collision_counts = structure.groupby("smiles")["drug_id"].nunique()
    n_colliding_smiles = int((collision_counts > 1).sum())
    # Multiple assay-level drug identifiers can legitimately resolve to the
    # same canonical structure. Collapse those identifiers explicitly rather
    # than allowing structure leakage across folds. Labels use OR/max and
    # phenotype covariates use means; provenance retains all contributing IDs.
    if n_colliding_smiles:
        label_cols = [c for c in structure.columns if c.startswith("moa_")]
        mean_cols = [c for c in structure.columns if c.startswith(("g-", "c-", "cp_")) or c in ("n_observations",)]
        rows = []
        for smi, group in structure.groupby("smiles", sort=True):
            row = {"smiles": smi,
                   "drug_id": ";".join(sorted(map(str, group["drug_id"]))),
                   "n_drug_ids": int(group["drug_id"].nunique())}
            for col in mean_cols:
                row[col] = float(pd.to_numeric(group[col], errors="coerce").mean())
            for col in label_cols:
                row[col] = int(pd.to_numeric(group[col], errors="coerce").fillna(0).max() > 0)
            rows.append(row)
        structure = pd.DataFrame(rows)
    else:
        structure["n_drug_ids"] = 1
    return structure, {
        "mapping_file": str(mapping_path),
        "n_mapping_rows": int(len(mapping)),
        "n_mapped_drug_ids": int(mapped["smiles"].notna().sum()),
        "n_structure_rows_after_collision_collapse": int(len(structure)),
        "mapping_coverage": float(mapped["smiles"].notna().sum() / len(drug_level)),
        "n_colliding_canonical_smiles": n_colliding_smiles,
        "canonical_collision_policy": "collapse_by_smiles; labels=max; covariates=mean; IDs retained",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True, type=Path)
    ap.add_argument("--mapping-csv", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    features, targets, drug = load_and_validate(args.raw_dir)
    drug_level, report = build_drug_level(features, targets, drug)
    drug_level.to_csv(args.out_dir / "lish_moa_drug_level.csv", index=False)
    report.update({"raw_dir": str(args.raw_dir), "mapping_status": "NOT_PROVIDED"})
    if args.mapping_csv is not None:
        structure, mapping_report = add_structure_mapping(drug_level, args.mapping_csv)
        structure.to_csv(args.out_dir / "lish_moa_structure_mapped.csv", index=False)
        report.update(mapping_report)
        report["mapping_status"] = "PASS"
    (args.out_dir / "lish_moa_prepare_report.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.out_dir / "lish_moa_data_contract.md").write_text(
        "# LISH-MoA prepared data contract\n\n"
        f"- Drug-level rows: {len(drug_level):,}\n"
        f"- Scored MoA labels: {report['n_scored_targets']}\n"
        f"- Mapping status: {report['mapping_status']}\n\n"
        "Rows are aggregated by `drug_id`; labels are max/ever-observed across assay conditions; no assay replicate may cross a split. "
        "MoA predictions are phenotype-associated labels, not causal target engagement.\n"
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
