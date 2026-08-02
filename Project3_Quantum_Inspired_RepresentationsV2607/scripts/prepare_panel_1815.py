#!/usr/bin/env python3
"""
prepare_panel_1815.py — Prepare the 1,815-molecule panel for §5.5 TDA/QKS relance.

Reconstructs SMILES for each molecule in the full-cluster rescoring panel
by re-running the Tanimoto nearest-neighbor search from r8b_fullcluster_rescoring.py,
then merges with Vina scores and saves a clean input CSV for the TDA pipeline.

Pipeline:
  1. Load cluster centroids SMILES (cluster_representatives_smiles.csv)
  2. Load full library SMILES (eos9gg2_malaria_final_drugbank_mpo.csv)
  3. Load docking_results_clean.csv (cluster_id, member_idx, vina_score)
  4. For each unique cluster_id:
     a. Get centroid SMILES
     b. Compute ECFP4 fingerprint
     c. Find Tanimoto nearest neighbors in library (threshold=0.55)
  5. Merge member SMILES with Vina scores by cluster_id + member_idx
  6. Save panel_1815_smiles.csv for TDA pipeline
  7. Save panel_1815_metadata.csv with full info

Usage:
    python scripts/prepare_panel_1815.py
    python scripts/prepare_panel_1815.py --n-jobs 8
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors
from rdkit.DataStructs import TanimotoSimilarity

RDLogger.logger().setLevel(RDLogger.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # .../Project3
MALARIA_ROOT = PROJECT_ROOT.parent  # .../Malaria_codesV2
ARCHIVE = MALARIA_ROOT / ".archive_P1_V2607_20260717"
P2_DATA = MALARIA_ROOT / "Project2_Polypharmacology_MD_ValidationV2607" / "data" / "from_project1"
P1_RESULTS = MALARIA_ROOT / "Project1_Chem_space_antimalarial_V2_CorrectedGrid" / "results"

TANIMOTO_THRESHOLD = 0.50   # original was 0.55, but 694 molecules fall in [0.50, 0.55)
MAX_MEMBERS_PER_CLUSTER = 250  # largest cluster has 233 members


# ═══════════════════════════════════════════════════════════════════════════════
#  SMILE canonicalization + fingerprinting
# ═══════════════════════════════════════════════════════════════════════════════

def canonicalize(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def ecfp4(smiles: str):
    """Compute ECFP4 (Morgan, radius=2, 2048 bits) fingerprint."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)


# ═══════════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Prepare 1,815-molecule panel for §5.5 TDA/QKS relance"
    )
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel workers for fingerprinting")
    args = parser.parse_args()

    t0 = time.perf_counter()
    log.info("═" * 60)
    log.info("Preparing 1,815-molecule Panel — §5.5")
    log.info("═" * 60)

    # ── Step 1: Load docking results clean ────────────────────────────────
    log.info("\n[Step 1] Loading docking results...")
    dock = pd.read_csv(P1_RESULTS / "docking_results_clean.csv")
    log.info(f"  Loaded {len(dock)} rows from docking_results_clean.csv")
    log.info(f"  Unique cluster_ids: {sorted(dock['cluster_id'].unique())}")
    log.info(f"  Targets: {dock['target'].value_counts().to_dict()}")

    unique_clusters = sorted(dock['cluster_id'].unique())
    log.info(f"  {len(unique_clusters)} unique clusters in panel")

    # ── Step 2: Load cluster centroid representatives ──────────────────────
    log.info("\n[Step 2] Loading cluster centroid SMILES...")
    centroids = pd.read_csv(P2_DATA / "data/cluster_representatives_smiles.csv")
    centroids.columns = [c.strip().upper() for c in centroids.columns]

    # The cluster_id in docking_results.csv = row index in centroids CSV
    centroids['canon'] = centroids['SMILES'].apply(canonicalize)
    log.info(f"  Loaded {len(centroids)} centroids total")
    log.info(f"  Panel uses {len(unique_clusters)} of them")

    # ── Step 3: Load full library SMILES ──────────────────────────────────
    log.info("\n[Step 3] Loading full library SMILES from MPO file...")
    mpo = pd.read_csv(P2_DATA / "results/eos9gg2_malaria_final_drugbank_mpo.csv")
    lib_smiles = mpo['input'].dropna().tolist()
    log.info(f"  Library size: {len(lib_smiles)} molecules")

    # ── Step 4: Compute all library fingerprints ──────────────────────────
    log.info("\n[Step 4] Computing ECFP4 fingerprints...")
    log.info("  Computing library fingerprints (65k molecules)...")
    t1 = time.perf_counter()

    lib_fps = []
    for i, smi in enumerate(lib_smiles):
        if i % 10000 == 0:
            log.info(f"    {i}/{len(lib_smiles)}... ({time.perf_counter()-t1:.0f}s)")
        fp = ecfp4(smi)
        lib_fps.append(fp)

    n_valid = sum(1 for fp in lib_fps if fp is not None)
    log.info(f"  Library fingerprints: {n_valid}/{len(lib_fps)} valid in {time.perf_counter()-t1:.0f}s")

    # ── Step 5: For each panel cluster, find member SMILES ────────────────
    log.info("\n[Step 5] Finding nearest neighbors for each panel cluster...")

    # Build mapping: (cluster_id, member_idx) → row in dock
    dock_index = {(row['cluster_id'], row['member_idx']): idx
                  for idx, row in dock.iterrows()}

    member_records = []  # will hold {smiles, vina_score, cluster_id, member_idx, tanimoto, target}
    matched = 0
    unmatched_entries = []

    for cluster_id in unique_clusters:
        if cluster_id >= len(centroids):
            log.warning(f"  Cluster {cluster_id}: exceeds centroids file ({len(centroids)} rows)")
            continue

        centroid_smi = centroids.iloc[cluster_id]['canon']
        if centroid_smi is None or pd.isna(centroid_smi):
            log.warning(f"  Cluster {cluster_id}: centroid SMILES is None")
            continue

        centroid_fp = ecfp4(centroid_smi)
        if centroid_fp is None:
            log.warning(f"  Cluster {cluster_id}: cannot compute fingerprint for centroid")
            continue

        # Compute Tanimoto similarities to all library molecules
        similarities = []
        for lib_idx, fp in enumerate(lib_fps):
            if fp is None:
                continue
            sim = TanimotoSimilarity(centroid_fp, fp)
            if sim >= TANIMOTO_THRESHOLD:
                similarities.append((lib_idx, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: -x[1])

        # Exclude centroid itself
        similarities = [(idx, sim) for idx, sim in similarities
                        if lib_smiles[idx] != centroid_smi]

        # Cap to MAX_MEMBERS_PER_CLUSTER
        similarities = similarities[:MAX_MEMBERS_PER_CLUSTER]

        log.info(f"  Cluster {cluster_id}: {len(similarities)} members found (threshold={TANIMOTO_THRESHOLD})")

        # Match members to docking results
        for member_idx, (lib_idx, sim) in enumerate(similarities):
            key = (cluster_id, member_idx)
            if key in dock_index:
                row = dock.iloc[dock_index[key]]
                member_records.append({
                    'smiles': lib_smiles[lib_idx],
                    'cluster_id': cluster_id,
                    'member_idx': member_idx,
                    'tanimoto_to_centroid': sim,
                    'vina_score': row['vina_score'],
                    'target': row['target'],
                })
                matched += 1
            else:
                unmatched_entries.append((cluster_id, member_idx))

    log.info(f"  Matched: {matched} molecules")
    if unmatched_entries:
        log.warning(f"  Unmatched (in dock but NN search didn't find): {len(unmatched_entries)}")
        log.info(f"  First 5 unmatched: {unmatched_entries[:5]}")

    # ── Step 6: Also check for unmatched docking entries ──────────────────
    matched_keys = set((r['cluster_id'], r['member_idx']) for r in member_records)
    for _, row in dock.iterrows():
        key = (row['cluster_id'], row['member_idx'])
        if key not in matched_keys:
            unmatched_entries.append(key)

    log.info(f"\n  Total matched: {matched} / {len(dock)}")

    # ── Step 7: Save outputs ──────────────────────────────────────────────
    log.info("\n[Step 6] Saving output files...")

    panel_dir = PROJECT_ROOT / "results"
    panel_dir.mkdir(parents=True, exist_ok=True)

    # Save SMILES-only file for TDA pipeline
    smiles_df = pd.DataFrame([{'smiles': r['smiles']} for r in member_records])
    smiles_path = panel_dir / "panel_1815_smiles.csv"
    smiles_df.to_csv(smiles_path, index=False)
    log.info(f"  TDA input (SMILES only): {smiles_path} ({len(smiles_df)} molecules)")

    # Save full metadata for TFP-Vina correlation analysis
    meta_df = pd.DataFrame(member_records)
    meta_path = panel_dir / "panel_1815_metadata.csv"
    meta_df.to_csv(meta_path, index=False)
    log.info(f"  Full metadata: {meta_path} ({len(meta_df)} rows)")
    log.info(f"    Columns: {list(meta_df.columns)}")
    log.info(f"    Target distribution: {meta_df['target'].value_counts().to_dict()}")
    log.info(f"    Mean Vina: {meta_df['vina_score'].mean():.3f} ± {meta_df['vina_score'].std():.3f}")

    # Summary
    log.info(f"\n{'='*60}")
    log.info(f"Panel preparation complete in {time.perf_counter()-t0:.0f}s")
    log.info(f"  Molecules for TDA: {len(smiles_df)}")
    log.info(f"  With Vina scores:  {len(meta_df)}")
    log.info(f"{'='*60}")

    if len(meta_df) < len(dock):
        log.warning(f"  Warning: only matched {len(meta_df)}/{len(dock)} docking results")
        log.warning(f"  The TDA analysis will use {len(smiles_df)} molecules with SMILES")


if __name__ == "__main__":
    main()
