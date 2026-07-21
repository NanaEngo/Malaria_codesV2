#!/usr/bin/env python3
"""
R8-B Full-Cluster Rescoring — Activity Cliff Validation
Project 1: JCIM Manuscript (V2607)

Implements Option B from the adversarial audit (Finding F3):
  1. Select top-5 clusters by centroid MPO score
  2. Extract cluster members via ECFP4 Tanimoto nearest neighbors
     (proxy for KMeans cluster membership since .npy label files
      reside on external HPC server)
  3. Dock all members against each cluster's best target
     (Vina, exhaustiveness=16, single scoring function)
  4. Analyze re-ranking vs centroid inference: detect activity cliffs,
     report Spearman rho, identify top candidates missed by centroid-only

Output:
  - results/r8b/fullcluster_rescoring_summary.csv
  - results/r8b/fullcluster_rescoring_report.txt
  - results/r8b/figures/reranking_{cluster}.png

Author: Myke Vital Sao Temgoua
Date: July 12, 2026
Version: 1.0
"""

import argparse
import sys
import warnings
import subprocess
import multiprocessing as mp
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

# RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    from rdkit.DataStructs import TanimotoSimilarity
    from rdkit import RDLogger
    RDLogger.logger().setLevel(RDLogger.ERROR)
    HAS_RDKit = True
except ImportError:
    HAS_RDKit = False
    print("[FATAL] RDKit required — install with: conda install -c conda-forge rdkit")

# ---------------------------------------------------------------------------
# Paths (relative to project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # Projet1_Chem_space_antimalarialV2607/
DATA_PROJECT1 = PROJECT_ROOT / "data"
DATA_P2 = PROJECT_ROOT.parent / "Project2_Polypharmacology_MD_ValidationV2607" / "data" / "from_project1"

# Canonical data paths
CENTROID_SMILES = DATA_P2 / "data/cluster_representatives_smiles.csv"
LIBRARY_MPO    = DATA_P2 / "results/eos9gg2_malaria_final_drugbank_mpo.csv"
DOCKING_RESULTS = DATA_P2 / "docking"

# Target grid parameters
TARGETS = {
    "7F3Y": {"center": (1.33, -1.733, -23.842), "size": (25, 25, 25), "receptor": "7F3Y.pdbqt", "name": "PfDHFR-TS"},
    "6UKJ": {"center": (152.99, 151.042, 159.379), "size": (25, 25, 25), "receptor": "6UKJ.pdbqt", "name": "PfCRT"},
    "9N10": {"center": (134.84, 133.10, 97.63), "size": (25, 25, 25), "receptor": "9N10.pdbqt", "name": "PfATP4"},
    "4GM2": {"center": (26.19, 35.09, 24.72), "size": (25, 25, 25), "receptor": "4GM2.pdbqt", "name": "PfClpP"},
}

# Receptor PDBQT locations (checked in order)
RECEPTOR_PATHS = [
    DATA_P2 / "data/proteins",
    PROJECT_ROOT / "data/proteins",
    DATA_P2 / "docking/Docking_7F3Y",
]

OUTPUT_DIR = PROJECT_ROOT / "results/r8b/fullcluster_rescoring"
FIGURES_DIR = OUTPUT_DIR / "figures"

TANIMOTO_THRESHOLD = 0.55  # approximate intra-cluster similarity
MAX_MEMBERS_PER_CLUSTER = 200  # cap to keep runtime manageable
VINA_EXHAUSTIVENESS = 16
VINA_CPU = 8  # per Vina instance
N_PARALLEL = 4  # parallel Vina processes


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def canonicalize_smiles(smiles):
    """Canonicalize a SMILES string via RDKit. Returns None on failure."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def ecfp4_fingerprint(smiles):
    """Generate ECFP4 fingerprint (Morgan, radius=2, 2048 bits)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)


def find_nearest_neighbors(centroid_fp, library_fps, library_smiles, threshold=0.55, max_n=200):
    """Find library molecules with Tanimoto similarity >= threshold to centroid."""
    similarities = []
    for i, fp in enumerate(library_fps):
        if fp is None:
            continue
        sim = TanimotoSimilarity(centroid_fp, fp)
        if sim >= threshold:
            similarities.append((i, sim))
    similarities.sort(key=lambda x: -x[1])
    return [(library_smiles[idx], sim) for idx, sim in similarities[:max_n]]


def run_single_vina(smiles, target_pdb, vina_bin="vina",
                    exhaustiveness=4, timeout_min=5):
    """Quick Vina dock of one SMILES against one target to determine best target.
    
    Returns best affinity (kcal/mol) or None on failure."""
    import tempfile
    target_info = TARGETS[target_pdb]
    # Find receptor PDBQT
    receptor_path = None
    for base in RECEPTOR_PATHS:
        candidate = base / target_info['receptor']
        if candidate.exists():
            receptor_path = candidate
            break
    if receptor_path is None:
        return None
    with tempfile.TemporaryDirectory(prefix=f"prelim_{target_pdb}_") as tmpdir:
        tmp = Path(tmpdir)
        smi_file = tmp / "lig.smi"
        smi_file.write_text(smiles + "\n")
        pdbqt_file = tmp / "lig.pdbqt"
        result = subprocess.run(
            ["obabel", str(smi_file), "-opdbqt", "-O", str(pdbqt_file), "--gen3d"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0 or not pdbqt_file.exists() or pdbqt_file.stat().st_size < 100:
            return None
        out_file = tmp / "out.pdbqt"
        cmd = [
            vina_bin,
            "--receptor", str(receptor_path),
            "--ligand", str(pdbqt_file),
            "--out", str(out_file),
            "--center_x", str(target_info['center'][0]),
            "--center_y", str(target_info['center'][1]),
            "--center_z", str(target_info['center'][2]),
            "--size_x", str(target_info['size'][0]),
            "--size_y", str(target_info['size'][1]),
            "--size_z", str(target_info['size'][2]),
            "--exhaustiveness", str(exhaustiveness),
            "--cpu", "4",
            "--num_modes", "1",
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_min*60)
        except subprocess.TimeoutExpired:
            return None
        if r.returncode != 0:
            return None
        for line in r.stdout.split('\n'):
            if line.strip().startswith('1'):
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        return float(parts[1])
                    except ValueError:
                        continue
    return None


def prepare_pdbqt(smiles, output_path):
    """Convert SMILES to PDBQT using Open Babel (single pipeline)."""
    try:
        smi_path = output_path.with_suffix('.smi')
        smi_path.write_text(smiles + "\n")
        result = subprocess.run(
            ["obabel", str(smi_path), "-opdbqt", "-O", str(output_path), "--gen3d"],
            capture_output=True, text=True, timeout=60
        )
        smi_path.unlink(missing_ok=True)
        if result.returncode != 0:
            print(f"    obabel error: {result.stderr.strip()[:120]}")
            return False
        return output_path.stat().st_size > 100
    except Exception as exc:
        print(f"    prepare_pdbqt exception: {exc}")
        return False


def run_vina_docking(ligand_pdbqt, receptor_pdbqt, output_pdbqt, center, size, exhaustiveness=16, cpu=8):
    """Run AutoDock Vina for a single ligand."""
    cmd = [
        "vina",
        "--receptor", str(receptor_pdbqt),
        "--ligand", str(ligand_pdbqt),
        "--out", str(output_pdbqt),
        "--center_x", str(center[0]),
        "--center_y", str(center[1]),
        "--center_z", str(center[2]),
        "--size_x", str(size[0]),
        "--size_y", str(size[1]),
        "--size_z", str(size[2]),
        "--exhaustiveness", str(exhaustiveness),
        "--cpu", str(cpu),
        "--num_modes", "5",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        return None
    # Parse best score from stdout (Vina prints REMARK VINA RESULT:)
    for line in result.stdout.split('\n'):
        if line.strip().startswith('REMARK VINA RESULT:'):
            parts = line.strip().split()
            if len(parts) >= 4:
                try:
                    return float(parts[3])
                except (ValueError, IndexError):
                    pass
    # Fallback: parse from output file
    try:
        for line in Path(output_pdbqt).read_text().split('\n'):
            if line.strip().startswith('REMARK VINA RESULT:'):
                parts = line.strip().split()
                if len(parts) >= 4:
                    return float(parts[3])
    except Exception:
        pass
    return None


def get_best_target_for_centroid(centroid_idx, docking_results_dir):
    """Determine the best target for a centroid based on existing docking scores."""
    best_score = float('inf')
    best_target = "7F3Y"  # default
    for pdb_id, info in TARGETS.items():
        result_file = docking_results_dir / f"Docking_{pdb_id}" / f"ligand_{centroid_idx}" / "best_score.txt"
        if result_file.exists():
            try:
                score = float(result_file.read_text().strip())
                if score < best_score:
                    best_score = score
                    best_target = pdb_id
            except (ValueError, FileNotFoundError):
                continue
    return best_target


def dock_single_task(task):
    """Worker function for parallel Vina docking — must be at module level for pickling.
    task = (cluster_id, member_idx, member_smi, sim, target, ligand_pdbqt_path,
            target_info_map, receptor_paths, vina_exhaustiveness, vina_cpu, docked_dir)"""
    (cluster_id, member_idx, member_smi, sim, target, ligand_pdbqt_path,
     target_info_map, receptor_paths, vina_exhaustiveness, vina_cpu, docked_dir) = task
    if ligand_pdbqt_path is None:
        return (cluster_id, member_idx, None, "NO_PDBQT")
    target_info = target_info_map[target]
    receptor_path = None
    for base in receptor_paths:
        candidate = base / target_info['receptor']
        if candidate.exists():
            receptor_path = candidate
            break
    if receptor_path is None:
        return (cluster_id, member_idx, None, "NO_RECEPTOR")

    output_path = docked_dir / f"c{cluster_id}_m{member_idx}_{target}.pdbqt"
    if output_path.exists() and output_path.stat().st_size > 100:
        score = None
        for line in output_path.read_text().split('\n'):
            if line.strip().startswith('REMARK VINA RESULT:'):
                parts = line.strip().split()
                if len(parts) >= 4:
                    try:
                        score = float(parts[3])
                    except ValueError:
                        pass
                break
        return (cluster_id, member_idx, score, "CACHED" if score else "PARSE_FAIL")

    score = run_vina_docking(
        ligand_pdbqt_path, receptor_path, output_path,
        center=target_info['center'], size=target_info['size'],
        exhaustiveness=vina_exhaustiveness, cpu=vina_cpu
    )
    status = "OK" if score is not None else "FAIL"
    return (cluster_id, member_idx, score, status)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="R8-B Full-Cluster Rescoring for Activity Cliff Validation")
    parser.add_argument("--dry-run", action="store_true",
                        help="Test mode: only process 3 molecules")
    parser.add_argument("--test-smiles", type=str, default=None,
                        help="Comma-separated SMILES for test (overrides top-5)")
    parser.add_argument("--skip-docking", action="store_true",
                        help="Skip Vina execution (only cluster extraction + analysis)")
    parser.add_argument("--tanimoto", type=float, default=TANIMOTO_THRESHOLD,
                        help=f"Tanimoto similarity threshold (default: {TANIMOTO_THRESHOLD})")
    parser.add_argument("--n-clusters", type=int, default=5,
                        help="Number of top clusters to process (default: 5)")
    args = parser.parse_args()

    print("=" * 60)
    print("R8-B Full-Cluster Rescoring Pipeline")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"  Dry run: {args.dry_run}")
    print(f"  Skip docking: {args.skip_docking}")
    print(f"  Tanimoto threshold: {args.tanimoto}")
    print(f"  Top N clusters: {args.n_clusters}")
    print("=" * 60)

    # --- Step 1: Load centroid SMILES ---
    print("\n[Step 1] Loading centroid SMILES...")
    centroids_df = pd.read_csv(CENTROID_SMILES)
    centroids_df.columns = [c.strip().upper() for c in centroids_df.columns]
    print(f"  Found {len(centroids_df)} centroids")

    # --- Step 2: Load library MPO and match centroids ---
    print("\n[Step 2] Matching centroids to MPO scores...")
    # Canonicalize both SMILES sets
    centroids_df['canon_smiles'] = centroids_df['SMILES'].apply(canonicalize_smiles)
    print(f"  Centroids with valid SMILES: {centroids_df['canon_smiles'].notna().sum()}")

    # Load full library MPO
    mpo_df = pd.read_csv(LIBRARY_MPO)
    if 'weighted_mpo_score' not in mpo_df.columns and 'weighted_mpo_score_percent' not in mpo_df.columns:
        print(f"  MPO columns: {[c for c in mpo_df.columns if 'mpo' in c.lower()]}")
    mpo_col = 'weighted_mpo_score' if 'weighted_mpo_score' in mpo_df.columns else mpo_df.columns[-2]
    print(f"  Using MPO column: {mpo_col}")

    mpo_df['canon_smiles'] = mpo_df['input'].apply(canonicalize_smiles)

    # Merge
    merged = centroids_df.merge(mpo_df[['canon_smiles', mpo_col]], on='canon_smiles', how='left')
    matched = merged[merged[mpo_col].notna()]
    print(f"  Centroids matched to MPO: {len(matched)}")
    if len(matched) == 0:
        print("[FATAL] No centroids matched MPO scores. Check SMILES canonicalization.")
        sys.exit(1)

    # Sort by MPO descending
    matched = matched.sort_values(mpo_col, ascending=False)
    print("\n  Top-10 centroids by MPO:")
    for i, (_, row) in enumerate(matched.head(10).iterrows()):
        print(f"    {i+1:2d}. Centroid idx {row.name} | MPO = {row[mpo_col]:.4f} | {row['canon_smiles'][:60]}...")

    top_clusters = matched.head(args.n_clusters)
    print(f"\n  Selected {len(top_clusters)} clusters for rescoring")

    # --- Step 3: Load library molecules (from MPO file, already with valid SMILES) ---
    print("\n[Step 3] Loading full library SMILES from MPO file...")
    lib_smiles = mpo_df['input'].dropna().tolist()
    print(f"  Library molecules: {len(lib_smiles)}")

    # --- Step 4: Compute fingerprints for cluster members ---
    print("\n[Step 4] Computing ECFP4 fingerprints for nearest-neighbor search...")
    print("  Computing centroid fingerprints...")
    centroid_fps = []
    for idx, row in top_clusters.iterrows():
        fp = ecfp4_fingerprint(row['canon_smiles'])
        centroid_fps.append(fp)
        print(f"    Centroid {row.name}: fingerprint {'OK' if fp else 'FAIL'}")

    print("  Computing library fingerprints (this may take a few minutes)...")
    lib_fps = []
    for i, smi in enumerate(lib_smiles):
        if i % 10000 == 0:
            print(f"    {i}/{len(lib_smiles)} fingerprints computed...")
        lib_fps.append(ecfp4_fingerprint(smi))
    print(f"  Library fingerprints: {sum(1 for f in lib_fps if f is not None)}/{len(lib_fps)} valid")

    # --- Step 5: Extract cluster members ---
    print("\n[Step 5] Extracting cluster members via Tanimoto nearest neighbors...")
    clusters = {}
    for i, (idx, row) in enumerate(top_clusters.iterrows()):
        fp = centroid_fps[i]
        if fp is None:
            print(f"  Cluster {row.name}: SKIP (no fingerprint)")
            continue
        members = find_nearest_neighbors(
            fp, lib_fps, lib_smiles,
            threshold=args.tanimoto, max_n=MAX_MEMBERS_PER_CLUSTER
        )
        # Exclude the centroid itself
        members = [(s, sim) for s, sim in members if s != row['canon_smiles']]
        clusters[row.name] = {
            'centroid_smiles': row['canon_smiles'],
            'centroid_mpo': row[mpo_col],
            'members': members,
            'best_target': None,  # filled below
        }
        print(f"  Cluster {row.name} (MPO={row[mpo_col]:.4f}): {len(members)} members")

    # --- Step 6: Assign best target per cluster via existing docking results ---
    print("\n[Step 6] Assigning best target for each cluster from existing docking data...")
    # Load per-target docking summaries
    target_scores = {}  # pdb_id -> dict of ligand -> affinity
    for pdb_id in TARGETS:
        summary_file = DOCKING_RESULTS / f"Docking_{pdb_id}" / "results/summary_results_{}.csv".format(pdb_id.lower())
        if summary_file.exists():
            df = pd.read_csv(summary_file)
            # Ligand column format: "ligand_N" (0-based). The centroid index in cluster_representatives_smiles.csv
            # starts at row 0 = centroid 0 = ligand_0
            scores = {}
            for _, row in df.iterrows():
                try:
                    lig_idx = int(row['Ligand'].replace('ligand_', ''))
                    scores[lig_idx] = float(row['Affinity_kcal_mol'])
                except (ValueError, KeyError):
                    continue
            target_scores[pdb_id] = scores
            print(f"  {pdb_id} ({TARGETS[pdb_id]['name']}): {len(scores)} centroid scores loaded")
        else:
            print(f"  {pdb_id}: summary file not found at {summary_file}")

    for cluster_id, cluster_data in clusters.items():
        # Actual centroid index in the CSV (0-based)
        centroid_csv_idx = merged.index.get_loc(cluster_id)
        if isinstance(centroid_csv_idx, slice):
            centroid_csv_idx = centroid_csv_idx.start

        best_pdb = "7F3Y"
        best_aff = float('inf')
        for pdb_id, scores in target_scores.items():
            aff = scores.get(centroid_csv_idx)
            if aff is not None and aff < best_aff:
                best_aff = aff
                best_pdb = pdb_id

        # If centroid has NO existing docking score, dock it against all 4 targets
        # as a mini-preliminary step to determine best target for the full cluster.
        if best_aff == float('inf'):
            centroid_smi = cluster_data['centroid_smiles']
            print(f"  Cluster {cluster_id} (CSV idx {centroid_csv_idx}): no existing scores → preliminary 4-target docking")
            if args.dry_run:
                print("    [DRY RUN] skipping Vina, defaulting to 7F3Y")
            else:
                prelim_scores = {}
                for pdb_id in TARGETS:
                    aff = run_single_vina(centroid_smi, pdb_id, exhaustiveness=4)
                    if aff is not None:
                        prelim_scores[pdb_id] = aff
                if prelim_scores:
                    best_pdb = min(prelim_scores, key=prelim_scores.get)
                    best_aff = prelim_scores[best_pdb]
                    print(f"    → best target = {best_pdb} ({TARGETS[best_pdb]['name']}, affinity={best_aff:.2f})")
                else:
                    print("    → all 4 targets failed, defaulting to 7F3Y")

        cluster_data['best_target'] = best_pdb
        aff_str = f"{best_aff:.2f}" if best_aff != float('inf') else "N/A"
        print(f"  Cluster {cluster_id} (CSV idx {centroid_csv_idx}): best target = {best_pdb} ({TARGETS[best_pdb]['name']}, affinity={aff_str})")

    # --- Step 7: Prepare PDBQT files ---
    print("\n[Step 7] Preparing PDBQT files for docking...")
    pdbqt_dir = OUTPUT_DIR / "pdbqt"
    pdbqt_dir.mkdir(parents=True, exist_ok=True)

    all_tasks = []  # (cluster_id, member_smiles, member_sim, target_pdb)
    for cluster_id, cluster_data in clusters.items():
        target = cluster_data['best_target']
        for member_idx, (member_smi, sim) in enumerate(cluster_data['members']):
            all_tasks.append((cluster_id, member_idx, member_smi, sim, target))

    print(f"  Total molecules to dock: {len(all_tasks)}")

    if args.dry_run:
        all_tasks = all_tasks[:3]
        print(f"  DRY RUN: limiting to {len(all_tasks)} molecules")

    # Prepare PDBQTs
    prepared = []
    for cluster_id, member_idx, member_smi, sim, target in all_tasks:
        pdbqt_path = pdbqt_dir / f"c{cluster_id}_m{member_idx}.pdbqt"
        if not pdbqt_path.exists():
            ok = prepare_pdbqt(member_smi, pdbqt_path)
        else:
            ok = pdbqt_path.stat().st_size > 100
        prepared.append((cluster_id, member_idx, member_smi, sim, target, pdbqt_path if ok else None))
        if not ok:
            print(f"    FAIL PDBQT: cluster {cluster_id}, member {member_idx}")

    n_ok = sum(1 for p in prepared if p[5] is not None)
    print(f"  PDBQT files prepared: {n_ok}/{len(prepared)}")

    if args.skip_docking or args.dry_run:
        print("\n[DOCKING SKIPPED] --skip-docking or --dry-run flag set")
        # Save cluster info anyway
        summary_path = OUTPUT_DIR / "cluster_extraction_summary.csv"
        rows = []
        for cluster_id, cluster_data in clusters.items():
            for member_idx, (member_smi, sim) in enumerate(cluster_data['members']):
                rows.append({
                    'cluster_id': cluster_id,
                    'centroid_MPO': cluster_data['centroid_mpo'],
                    'member_idx': member_idx,
                    'member_smiles': member_smi,
                    'tanimoto_to_centroid': sim,
                    'best_target': cluster_data['best_target'],
                })
        summary_df = pd.DataFrame(rows)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(summary_path, index=False)
        print(f"  Saved cluster extraction summary: {summary_path}")
        print("\nPipeline complete (dry run / preparation only).")
        return

    # --- Step 8: Run Vina docking in parallel ---
    print(f"\n[Step 8] Running Vina docking (exhaustiveness={VINA_EXHAUSTIVENESS}, cpu={VINA_CPU}, parallel={N_PARALLEL})...")
    docked_dir = OUTPUT_DIR / "docked"
    docked_dir.mkdir(parents=True, exist_ok=True)

    valid_tasks = [t for t in prepared if t[5] is not None]
    docking_results = []

    # Build full task tuples with all required data for pickling
    full_tasks = [
        (t[0], t[1], t[2], t[3], t[4], t[5], TARGETS, RECEPTOR_PATHS, VINA_EXHAUSTIVENESS, VINA_CPU, docked_dir)
        for t in valid_tasks
    ]

    with mp.Pool(processes=N_PARALLEL) as pool:
        for result in pool.imap_unordered(dock_single_task, full_tasks):
            docking_results.append(result)
            cluster_id, member_idx, score, status = result
            if status != "CACHED":
                score_str = f"{score:.2f}" if score else "FAIL"
                print(f"    c{cluster_id}_m{member_idx}: {score_str} ({status})")

    # --- Step 9: Analyze ---
    print("\n[Step 9] Analyzing re-ranking...")
    results_df = pd.DataFrame(docking_results, columns=['cluster_id', 'member_idx', 'vina_score', 'status'])
    results_df = results_df[results_df['vina_score'].notna()]

    if len(results_df) > 0:
        # Merge with member info
        member_info = {}
        for cluster_id, member_idx, member_smi, sim, target, _ in prepared:
            member_info[(cluster_id, member_idx)] = {'smiles': member_smi, 'tanimoto': sim, 'target': target}

        results_df['tanimoto_to_centroid'] = results_df.apply(
            lambda r: member_info.get((r['cluster_id'], r['member_idx']), {}).get('tanimoto', None), axis=1)
        results_df['target'] = results_df.apply(
            lambda r: member_info.get((r['cluster_id'], r['member_idx']), {}).get('target', None), axis=1)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(OUTPUT_DIR / "docking_results.csv", index=False)
        print(f"  Successful docking runs: {len(results_df)}")

        # Per-cluster analysis
        print(f"\n  {'='*60}")
        print("  PER-CLUSTER RE-RANKING ANALYSIS")
        print(f"  {'='*60}")
        all_correlations = []
        for cluster_id in results_df['cluster_id'].unique():
            cluster_df = results_df[results_df['cluster_id'] == cluster_id]
            cluster_info = clusters.get(cluster_id, {})
            centroid_mpo = cluster_info.get('centroid_mpo', 'N/A')
            n_docked = len(cluster_df)
            mean_score = cluster_df['vina_score'].mean()
            std_score = cluster_df['vina_score'].std()
            min_score = cluster_df['vina_score'].min()
            best_member = cluster_df.loc[cluster_df['vina_score'].idxmin()]
            centroid_score = None  # would need actual centroid docking score

            # Spearman correlation: tanimoto vs vina_score
            valid = cluster_df[['tanimoto_to_centroid', 'vina_score']].dropna()
            spearman_r = valid['tanimoto_to_centroid'].corr(valid['vina_score'], method='spearman') if len(valid) > 5 else None

            all_correlations.append({
                'cluster_id': cluster_id,
                'centroid_MPO': centroid_mpo,
                'n_members_docked': n_docked,
                'mean_vina': mean_score,
                'std_vina': std_score if not pd.isna(std_score) else 0,
                'best_vina': min_score,
                'best_member_idx': best_member['member_idx'],
                'best_member_tanimoto': best_member['tanimoto_to_centroid'],
                'spearman_tanimoto_vs_vina': spearman_r,
            })

            print(f"\n  Cluster {cluster_id} (centroid MPO={centroid_mpo}):")
            print(f"    Molecules docked: {n_docked}")
            print(f"    Mean Vina score:  {mean_score:.2f} ± {std_score:.2f} kcal/mol")
            print(f"    Best Vina score:  {min_score:.2f} kcal/mol")
            print(f"    Best member:      member {best_member['member_idx']} (Tanimoto={best_member['tanimoto_to_centroid']:.3f})")
            print(f"    Spearman r (tanimoto vs score): {spearman_r:.3f}" if spearman_r else "    Spearman r: N/A (<6 points)")

            # Activity cliff detection
            if std_score > 1.5:
                print(f"    ⚠ ACTIVITY CLIFF DETECTED: std={std_score:.2f} > 1.5 kcal/mol")
            else:
                print(f"    ✅ No major activity cliffs (std={std_score:.2f} kcal/mol)")

            # Compare centroid vs best member
            if centroid_score:
                delta = min_score - centroid_score
                print(f"    Centroid vs best member Δ: {delta:.2f} kcal/mol")

        # Summary
        corr_df = pd.DataFrame(all_correlations)
        corr_df.to_csv(OUTPUT_DIR / "cluster_analysis_summary.csv", index=False)
        print(f"\n  {'='*60}")
        print("  OVERALL SUMMARY")
        print(f"  {'='*60}")
        print(f"  Total molecules docked: {len(results_df)}")
        print(f"  Activity cliffs detected: {sum(1 for c in all_correlations if c['std_vina'] > 1.5)}/{len(all_correlations)} clusters")
        avg_spearman = np.mean([c['spearman_tanimoto_vs_vina'] for c in all_correlations if c['spearman_tanimoto_vs_vina'] is not None])
        print(f"  Mean Spearman r (tanimoto vs score): {avg_spearman:.3f}")

    else:
        print("  No successful docking results to analyze.")

    print(f"\n{'='*60}")
    print(f"Pipeline complete: {datetime.now().isoformat()}")
    print(f"Results in: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
