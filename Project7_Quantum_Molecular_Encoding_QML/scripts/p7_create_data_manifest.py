#!/usr/bin/env python3
"""
P7 Phase 1.4 — Freeze data provenance manifest.

Computes SHA-256 hashes for all data files and writes
data/provenance/data_manifest.json

Usage:
    python scripts/p7_create_data_manifest.py
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

P7_ROOT = Path(__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def file_entry(path: Path, label: str) -> dict:
    if not path.exists():
        return {"label": label, "path": str(path.relative_to(P7_ROOT)), "status": "MISSING"}
    return {
        "label":    label,
        "path":     str(path.relative_to(P7_ROOT)),
        "size_kb":  round(path.stat().st_size / 1024, 2),
        "sha256":   sha256(path),
        "status":   "PRESENT",
    }


def load_meta(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def main():
    prov_dir = P7_ROOT / "data" / "provenance"
    prov_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("P7 Phase 1.4 — Data Manifest")
    print("=" * 60)

    # ── Collect entries ───────────────────────────────────────────────────
    entries = {}

    # --- P1 Set A ---
    p1_csv  = P7_ROOT / "data" / "p1_set_a" / "p1_set_a_17_candidates.csv"
    p1_anp  = P7_ROOT / "data" / "p1_set_a" / "p1_set_a_17_candidates_anp_metadata.csv"
    p1_meta = load_meta(P7_ROOT / "data" / "p1_set_a" / "extraction_metadata.json")

    p1_entry = file_entry(p1_csv, "P1 Set A — 17 candidates (P2 Set C)")
    if p1_meta:
        p1_entry.update({
            "n_molecules":  p1_meta.get("n_molecules"),
            "n_active":     p1_meta.get("n_active"),
            "n_inactive":   p1_meta.get("n_inactive"),
            "source":       p1_meta.get("source"),
        })
    entries["p1_set_a"] = p1_entry
    entries["p1_set_a_anp"] = file_entry(p1_anp, "P1 Set A — ANP metadata")

    # --- P3 Benchmark ---
    p3_csv  = P7_ROOT / "data" / "p3_benchmark" / "p3_benchmark_19849.csv"
    p3_meta = load_meta(P7_ROOT / "data" / "p3_benchmark" / "extraction_metadata.json")

    p3_entry = file_entry(p3_csv, "P3 benchmark — 19,849 molecules")
    if p3_meta:
        p3_entry.update({
            "n_molecules": p3_meta.get("n_molecules"),
            "n_active":    p3_meta.get("n_active"),
            "n_inactive":  p3_meta.get("n_inactive"),
            "source":      p3_meta.get("source"),
        })
    entries["p3_benchmark"] = p3_entry

    # --- Splits ---
    splits_file = P7_ROOT / "data" / "splits" / "p3_5fold_splits.json"
    entries["p3_splits"] = file_entry(splits_file, "P3 5-fold stratified CV splits (seed=42)")

    # ── Assemble manifest ─────────────────────────────────────────────────
    manifest = {
        "created":    datetime.now(timezone.utc).isoformat(),
        "p7_root":    str(P7_ROOT),
        "entries":    entries,
        "provenance_rules": [
            "Inputs frozen before execution",
            "SHA-256 hashes computed at extraction time",
            "P1 Set A = P2 Set C (17 molecules, 2 active / 15 inactive)",
            "P3 benchmark = p3_labels_production.csv (19,849 molecules)",
            "P3 splits: StratifiedKFold(n_splits=5, seed=42) — NOT scaffold-split",
            "P1 Set A / P2 MD Set B / P2 Set C remain disjoint",
        ],
    }

    out = prov_dir / "data_manifest.json"
    out.write_text(json.dumps(manifest, indent=2))

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\nEntries:")
    for key, entry in entries.items():
        status = entry.get("status", "?")
        n      = entry.get("n_molecules", "")
        sha    = entry.get("sha256", "")[:16] + "..." if entry.get("sha256") else "—"
        print(f"  [{status:7s}] {key:25s}  n={n!s:6s}  sha256={sha}")

    print(f"\n✓ Manifest: {out}")
    print("\nPhase 1.4 COMPLETE")


if __name__ == "__main__":
    main()
