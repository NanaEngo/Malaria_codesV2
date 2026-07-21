"""
p1_enrichment_validation.py (FIXED - Server Version)
=====================================================

REVISION-ROADMAP R1 — Replace circular enrichment validation.

Part A: External enrichment using DEKOIS 2.0 decoy sets + actives
Part B: ChEMBL-confirmed antimalarial benchmark

CRITICAL FIX: Original script only loaded DEKOIS decoys.
This version loads BOTH actives (DHFR_ligands.smi) AND decoys (DHFR_decoys.smi).

Outputs (results/):
  p1_enrichment_external.csv     — ROC-AUC, EF1%, EF5%, EF10%, BEDROC per target
  p1_enrichment_chembl_benchmark.csv — ChEMBL hit rate actives vs. inactives
  p1_enrichment_summary.txt      — human-readable summary for SM Table S14 / S14b

Usage:
  python scripts/p1_enrichment_validation.py --part A   # DEKOIS only
  python scripts/p1_enrichment_validation.py --part B   # ChEMBL only
  python scripts/p1_enrichment_validation.py            # both

Requirements:
  conda activate malaria_md
  pip install chembl-webresource-client rdkit scipy scikit-learn requests
"""

import argparse
import re
import subprocess
import tempfile
import time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.metrics import roc_auc_score, average_precision_score

PROJECT = Path(__file__).parent.parent

# ============================================================================
# PATH CONFIGURATION (Server paths - DO NOT CHANGE)
# ============================================================================

RESULTS = Path("/home/myke_vital/Docking/Malaria_codes/results")
DATA    = Path("/home/myke_vital/Docking/Malaria_codes/data/")
DOCKING = Path("/home/myke_vital/Docking/Malaria_codes/Docking")

TARGETS = {
    "PfDHFR_7F3Y": {
        "pdb":    "7F3Y",
        "pdbqt":  DATA / "proteins" / "7F3Y.pdbqt",
        "config": DOCKING / "Docking_7F3Y" / "config.txt",
        "chembl_target": "CHEMBL1939",  # PfDHFR
    },
    "PfATP4_9N10": {
        "pdb":    "9N10",
        "pdbqt":  DATA / "proteins" / "9N10.pdbqt",
        "config": DOCKING / "Docking_9N10" / "config.txt",
        "chembl_target": "CHEMBL364",  # PfATP4
    },
    "PfCRT_6UKJ": {
        "pdb":    "6UKJ",
        "pdbqt":  DATA / "proteins" / "6UKJ.pdbqt",
        "config": DOCKING / "Docking_6UKJ" / "config.txt",
        "chembl_target": "CHEMBL1795182",  # PfCRT
    },
    "PfClpP_4GM2": {
        "pdb":    "4GM2",
        "pdbqt":  DATA / "proteins" / "4GM2.pdbqt",
        "config": DOCKING / "Docking_4GM2" / "config.txt",
        "chembl_target": "CHEMBL4179069",  # PfClpP
    },
}

VINA_BIN = (Path("/home/myke_vital/usr/bin/vina")
            if Path("/home/myke_vital/usr/bin/vina").exists()
            else "vina")

# Mapping from PDB code to DEKOIS 2.0 target name
DEKOIS_NAME = {
    "7F3Y": "DHFR",       # human DHFR (closest proxy for PfDHFR)
    "6UKJ": None,          # not in DEKOIS
    "9N10": None,          # not in DEKOIS
    "4GM2": None,          # not in DEKOIS
}

# ============================================================================
# UTILITY: Parse Vina score from output
# ============================================================================

def parse_vina_score(pdbqt_path: Path) -> "float | None":
    """Return best (most negative) Vina score from a pdbqt output file."""
    try:
        text = pdbqt_path.read_text(encoding="utf-8", errors="ignore")
        scores = re.findall(r"REMARK VINA RESULT:\s+([-\d.]+)", text)
        if scores:
            return min(float(s) for s in scores)
    except (OSError, ValueError) as exc:
        print(f"  Warning: could not parse {pdbqt_path.name}: {exc}")
    return None

# ============================================================================
# UTILITY: Dock SMILES list against target (using config files)
# ============================================================================

def dock_smiles_list(
    smiles_list: list,
    target_name: str,
    exhaustiveness: int = 64
) -> dict:
    """
    Dock each SMILES against target using AutoDock Vina.
    Returns {smiles: best_vina_score}.
    Skips molecules that fail 3D embedding or Vina.
    """
    cfg = TARGETS[target_name]
    config_path = cfg["config"]
    receptor = cfg["pdbqt"]
    
    if not receptor.exists():
        raise FileNotFoundError(f"Receptor not found: {receptor}")
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    scores = {}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        
        for i, smi in enumerate(smiles_list):
            # Convert SMILES to 3D
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue
            
            mol = Chem.AddHs(mol)
            if AllChem.EmbedMolecule(mol, AllChem.ETKDGv3()) != 0:
                continue
            
            AllChem.MMFFOptimizeMolecule(mol)
            
            # Save as PDB
            lig_pdb = tmp / f"lig_{i}.pdb"
            lig_pdbqt = tmp / f"lig_{i}.pdbqt"
            out_pdbqt = tmp / f"out_{i}.pdbqt"
            
            Chem.MolToPDBFile(mol, str(lig_pdb))
            
            # Convert PDB to PDBQT using obabel
            ret = subprocess.run(
                ["obabel", str(lig_pdb), "-O", str(lig_pdbqt)],
                capture_output=True
            )
            if ret.returncode != 0 or not lig_pdbqt.exists():
                continue
            
            # Read grid from config
            cfg_text = config_path.read_text(encoding="utf-8")
            
            def _val(key: str) -> str:
                m = re.search(rf"{re.escape(key)}\s*=\s*([-\d.]+)", cfg_text)
                return m.group(1) if m else "0"
            
            # Dock with Vina
            vina_bin = Path(VINA_BIN).resolve() if Path(VINA_BIN).is_absolute() else VINA_BIN
            vina_cmd = [
                str(vina_bin),
                "--receptor", str(receptor),
                "--ligand", str(lig_pdbqt),
                "--out", str(out_pdbqt),
                "--center_x", _val("center_x"),
                "--center_y", _val("center_y"),
                "--center_z", _val("center_z"),
                "--size_x", _val("size_x"),
                "--size_y", _val("size_y"),
                "--size_z", _val("size_z"),
                "--exhaustiveness", str(exhaustiveness),
                "--num_modes", "20",
                "--cpu", "16",
            ]
            
            ret = subprocess.run(vina_cmd, capture_output=True)
            if ret.returncode == 0 and out_pdbqt.exists():
                score = parse_vina_score(out_pdbqt)
                if score is not None:
                    scores[smi] = score
    
    return scores

# ============================================================================
# ENRICHMENT METRICS
# ============================================================================

def bedroc(y_true: np.ndarray, scores: np.ndarray, alpha: float = 20.0) -> float:
    """
    Boltzmann-Enhanced Discrimination of ROC (Truchon & Bayly, 2007).
    Higher alpha = more weight on early recognition.
    """
    n = len(y_true)
    n_actives = y_true.sum()
    
    if n_actives == 0 or n_actives == n:
        return float("nan")
    
    # Sort by scores (higher is better)
    order = np.argsort(-scores)
    y_sorted = y_true[order]
    
    # Calculate BEDROC
    ra = n_actives / n
    sum_exp = 0.0
    
    for i, label in enumerate(y_sorted):
        if label == 1:  # Active
            sum_exp += np.exp(-alpha * i / n)
    
    # Normalization
    bedroc_max = (ra * np.sinh(alpha / 2) / (np.cosh(alpha / 2) - 1)) + \
                 ((1 - ra) / (1 - np.exp(-alpha)))
    
    bedroc_val = (sum_exp / n_actives) / bedroc_max
    
    return float(bedroc_val)

def enrichment_factor(y_true: np.ndarray, scores: np.ndarray, fraction: float) -> float:
    """EF at given fraction of ranked list."""
    n = len(y_true)
    n_actives = y_true.sum()
    
    if n_actives == 0:
        return 0.0
    
    cutoff = max(1, int(np.ceil(fraction * n)))
    order = np.argsort(-scores)
    top_actives = y_true[order[:cutoff]].sum()
    
    ef = (top_actives / cutoff) / (n_actives / n)
    return float(ef)

def compute_enrichment_metrics(y_true: np.ndarray, scores: np.ndarray) -> dict:
    """Compute all enrichment metrics for one target."""
    roc = roc_auc_score(y_true, scores) if len(np.unique(y_true)) > 1 else float("nan")
    pr = average_precision_score(y_true, scores) if len(np.unique(y_true)) > 1 else float("nan")
    
    return {
        "ROC_AUC": round(roc, 4),
        "EF1pct": round(enrichment_factor(y_true, scores, 0.01), 3),
        "EF5pct": round(enrichment_factor(y_true, scores, 0.05), 3),
        "EF10pct": round(enrichment_factor(y_true, scores, 0.10), 3),
        "BEDROC": round(bedroc(y_true, scores), 4),
        "PR_AUC": round(pr, 4),
        "n_actives": int(y_true.sum()),
        "n_decoys": int((1 - y_true).sum()),
    }

# ============================================================================
# PART A: DEKOIS 2.0 Enrichment Validation (FIXED - Loads Actives!)
# ============================================================================

def fetch_chembl_actives(
    chembl_target_id: str,
    ic50_uM_cutoff: float = 1.0,
    max_compounds: int = 200
) -> list:
    """Fetch SMILES of actives (IC50 < cutoff µM) from ChEMBL REST API.
    Returns list of canonical SMILES."""
    # Validate target ID format to prevent injection via URL construction
    if not re.fullmatch(r"CHEMBL\d+", chembl_target_id):
        raise ValueError(f"Invalid ChEMBL target ID format: {chembl_target_id}")
    
    base = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
    params = {
        "target_chembl_id": chembl_target_id,
        "standard_type": "IC50",
        "standard_relation": "=",
        "standard_units": "nM",
        "standard_value__lte": int(ic50_uM_cutoff * 1000),
        "assay_type": "B",
        "limit": max_compounds,
        "offset": 0,
    }
    
    try:
        resp = requests.get(base, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        smiles = []
        for act in data.get("activities", []):
            smi = act.get("canonical_smiles") or act.get("molecule_structures", {}).get("canonical_smiles")
            if smi:
                mol = Chem.MolFromSmiles(smi)
                if mol:
                    smiles.append(Chem.MolToSmiles(mol))
        return list(set(smiles))
    except (requests.RequestException, ValueError, KeyError) as exc:
        print(f"  ChEMBL fetch failed for {chembl_target_id}: {exc}")
        return []

def load_dekois_actives_and_decoys(target_pdb: str) -> tuple:
    """
    Load DEKOIS actives and decoys for a target.
    Returns (actives_smiles, decoys_smiles).
    
    CRITICAL FIX: Original script only loaded decoys!
    This function loads BOTH DHFR_ligands.smi AND DHFR_decoys.smi.
    """
    dekois_name = DEKOIS_NAME.get(target_pdb)
    
    if dekois_name is None:
        print(f"  {target_pdb} not available in DEKOIS 2.0.")
        return [], []
    
    # Try to find DEKOIS files in multiple locations
    actives = []
    decoys = []
    
    for base_dir in [DATA / "dekois", DATA / "external" / "dekois", DATA / "external"]:
        actives_file = base_dir / f"{dekois_name}_ligands.smi"
        decoys_file = base_dir / f"{dekois_name}_decoys.smi"
        
        # Load actives (CRITICAL - was missing in original!)
        if actives_file.exists() and not actives:
            for line in actives_file.read_text().splitlines():
                smi = line.strip().split()[0] if line.strip() else ""
                if smi:
                    mol = Chem.MolFromSmiles(smi)
                    if mol:
                        actives.append(Chem.MolToSmiles(mol))
            print(f"  Loaded {len(actives)} DEKOIS actives from {actives_file}")
        
        # Load decoys
        if decoys_file.exists() and not decoys:
            for line in decoys_file.read_text().splitlines():
                smi = line.strip().split()[0] if line.strip() else ""
                if smi:
                    mol = Chem.MolFromSmiles(smi)
                    if mol:
                        decoys.append(Chem.MolToSmiles(mol))
            print(f"  Loaded {len(decoys)} DEKOIS decoys from {decoys_file}")
    
    if not actives:
        print(f"  WARNING: No DEKOIS actives found for {dekois_name}")
    if not decoys:
        print(f"  WARNING: No DEKOIS decoys found for {dekois_name}")
    
    return actives, decoys

def run_part_a() -> pd.DataFrame:
    """
    Part A: Dock DEKOIS actives + decoys OR ChEMBL actives + fallback decoys;
    compute enrichment metrics.
    """
    print("\n" + "=" * 60)
    print("Part A: External Enrichment Validation (DEKOIS 2.0 + ChEMBL)")
    print("=" * 60)
    
    records = []
    
    for target_name, cfg in TARGETS.items():
        print(f"\n  Target: {target_name} ({cfg['pdb']})")
        
        # Try to load DEKOIS actives + decoys first (preferred)
        dekois_actives, dekois_decoys = load_dekois_actives_and_decoys(cfg["pdb"])
        
        if dekois_actives and dekois_decoys:
            # Use DEKOIS data (preferred for PfDHFR)
            print(f"  Using DEKOIS data: {len(dekois_actives)} actives, {len(dekois_decoys)} decoys")
            actives = dekois_actives
            decoys = dekois_decoys
        else:
            # Fallback to ChEMBL actives + generated decoys
            print("  DEKOIS not available, using ChEMBL actives + fallback decoys")
            actives = fetch_chembl_actives(cfg["chembl_target"])
            print(f"  ChEMBL actives fetched: {len(actives)}")
            
            if len(actives) < 10:
                print(f"  WARNING: < 10 actives for {target_name}. Skipping target.")
                continue
            
            # Generate fallback decoys (property-matched or random)
            decoys = _generate_property_matched_decoys(cfg["pdb"])
        
        if len(decoys) < 10:
            print(f"  WARNING: < 10 decoys for {target_name}. Skipping target.")
            continue
        
        # Limit to balanced set
        n = min(len(actives), len(decoys), 100)
        actives = actives[:n]
        decoys = decoys[:n]
        
        all_smi = actives + decoys
        y_true = np.array([1] * len(actives) + [0] * len(decoys))
        
        print(f"  Docking {len(all_smi)} compounds (exhaustiveness=64)...")
        scores_dict = dock_smiles_list(all_smi, target_name, exhaustiveness=64)
        
        docked_smi = [s for s in all_smi if s in scores_dict]
        docked_labels = np.array([y_true[all_smi.index(s)] for s in docked_smi])
        docked_scores = np.array([scores_dict[s] for s in docked_smi])
        
        # Vina scores are negative; negate so higher = better for sklearn
        docked_scores_neg = -docked_scores
        
        if len(docked_smi) < 10:
            print(f"  WARNING: Only {len(docked_smi)} compounds docked. Skipping.")
            continue
        
        metrics = compute_enrichment_metrics(docked_labels, docked_scores_neg)
        metrics["target"] = target_name
        metrics["pdb"] = cfg["pdb"]
        records.append(metrics)
        
        print(f"  ROC-AUC={metrics['ROC_AUC']:.3f}  "
              f"EF5%={metrics['EF5pct']:.2f}  "
              f"EF10%={metrics['EF10pct']:.2f}  "
              f"BEDROC={metrics['BEDROC']:.3f}")
    
    df = pd.DataFrame(records)
    if not df.empty:
        cols = ["target", "pdb", "ROC_AUC", "EF1pct", "EF5pct",
                "EF10pct", "BEDROC", "PR_AUC", "n_actives", "n_decoys"]
        df = df[cols]
        out = RESULTS / "p1_enrichment_external.csv"
        df.to_csv(out, index=False)
        print(f"\n  Saved: {out}")
    
    return df

def _generate_property_matched_decoys(target_pdb: str, n_decoys: int = 200) -> list:
    """Fallback: sample property-matched decoys from the 484 K-Means cluster
    representatives. Decoys are molecules with existing Vina docking scores
    > -5.0 kcal/mol (low affinity) in the OTHERS/ directory."""
    others_dir = DOCKING / f"Docking_{target_pdb}" / "results_consensus" / "OTHERS"
    if not others_dir.exists():
        print(f"  No OTHERS directory found for {target_pdb}; "
              f"falling back to random cluster representatives.")
        return _random_cluster_representatives(n_decoys)
    
    # Parse Vina scores from existing OTHERS/ pdbqt files to find weak binders
    weak_binders = []
    pdbqt_files = list(others_dir.glob("ligand_*_out.pdbqt"))
    for pdbqt in pdbqt_files:
        score = parse_vina_score(pdbqt)
        if score is not None and score > -5.0:
            weak_binders.append(pdbqt)
    
    if len(weak_binders) < 10:
        print(f"  Only {len(weak_binders)} weak binders found for {target_pdb}; "
              f"falling back to random cluster representatives.")
        return _random_cluster_representatives(n_decoys)
    
    # Sample from weak binders
    np.random.seed(42)
    sample = np.random.choice(weak_binders, min(n_decoys, len(weak_binders)), replace=False)
    
    # Extract SMILES from the cluster representatives file by matching ligand IDs
    smiles_file = DATA / "cluster_representatives_smiles.smi"
    if not smiles_file.exists():
        return _random_cluster_representatives(n_decoys)
    
    all_smiles = [line.strip() for line in smiles_file.read_text().splitlines() if line.strip()]
    
    # Extract ligand indices from pdbqt filenames (ligand_N_out.pdbqt → N)
    indices = []
    for pdbqt in sample:
        m = re.search(r"ligand_(\d+)_out\.pdbqt", pdbqt.name)
        if m:
            idx = int(m.group(1))
            if idx < len(all_smiles):
                indices.append(idx)
    
    decoys = []
    for idx in indices:
        smi = all_smiles[idx]
        mol = Chem.MolFromSmiles(smi)
        if mol:
            decoys.append(Chem.MolToSmiles(mol))
    
    print(f"  Generated {len(decoys)} property-matched fallback decoys "
          f"(Vina > -5.0 kcal/mol) from {len(weak_binders)} weak binders.")
    return decoys

def _random_cluster_representatives(n_decoys: int = 200) -> list:
    """Last-resort fallback: random sample from the 484 K-Means cluster
    representatives (centroid SMILES)."""
    smiles_file = DATA / "cluster_representatives_smiles.smi"
    if not smiles_file.exists():
        print(f"  Cluster representatives file not found: {smiles_file}")
        return []
    
    all_smiles = [line.strip() for line in smiles_file.read_text().splitlines() if line.strip()]
    np.random.seed(42)
    sample = np.random.choice(all_smiles, min(n_decoys, len(all_smiles)), replace=False)
    
    decoys = []
    for smi in sample:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            decoys.append(Chem.MolToSmiles(mol))
    
    print(f"  Generated {len(decoys)} random cluster representative decoys.")
    return decoys

# ============================================================================
# PART B: ChEMBL-Confirmed Antimalarial Benchmark
# ============================================================================

CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"

def fetch_chembl_activities_for_target(
    chembl_target_id: str,
    max_records: int = 3000
) -> pd.DataFrame:
    """
    Fetch all standardised bioactivities for a ChEMBL target.
    Returns DataFrame with: molecule_chembl_id, canonical_smiles, standard_type,
    standard_value (nM), standard_relation.
    """
    all_activities = []
    offset = 0
    page_size = 1000
    
    while offset < max_records:
        try:
            url = (f"{CHEMBL_BASE}/activity.json?"
                   f"target_chembl_id={chembl_target_id}&"
                   f"limit={page_size}&offset={offset}")
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            acts = data.get("activities", [])
            
            if not acts:
                break
            
            all_activities.extend(acts)
            offset += page_size
            time.sleep(0.5)
            
            # Stop if we got fewer than page_size (last page)
            if len(acts) < page_size:
                break
                
        except (requests.RequestException, OSError) as exc:
            print(f"  ChEMBL activities fetch failed at offset {offset}: {exc}")
            break
    
    if not all_activities:
        print(f"  No activities fetched for {chembl_target_id}.")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_activities)
    
    # Filter: IC50, standard values only
    df = df[df["standard_type"] == "IC50"]
    df = df[df["standard_relation"] == "="]
    df = df[df["standard_flag"] == 1]
    df = df.dropna(subset=["standard_value", "canonical_smiles"])
    df["standard_value"] = pd.to_numeric(df["standard_value"], errors="coerce")
    df = df.dropna(subset=["standard_value"])
    
    print(f"  {chembl_target_id}: {len(df)} standardised IC50 records "
          f"(from {len(all_activities)} total activities).")
    
    return df[["molecule_chembl_id", "canonical_smiles",
               "standard_value", "standard_type"]]

def fetch_chembl_malaria_controls(target_chembl_id: str) -> tuple:
    """
    Fetch P. falciparum compounds from ChEMBL with:
    - Actives:   IC₅₀ < 1 µM  (< 1000 nM, potent antimalarials)
    - Inactives: IC₅₀ > 10 µM (> 10000 nM, weak/non-active)
    
    Returns (actives_smiles, inactives_smiles).
    """
    print(f"  Fetching ChEMBL bioactivities for {target_chembl_id}...")
    df = fetch_chembl_activities_for_target(target_chembl_id)
    
    if df.empty:
        return [], []
    
    # Classify
    actives_df = df[df["standard_value"] < 1000]
    inactives_df = df[df["standard_value"] > 10000]
    
    # Canonicalise SMILES
    def canon(smi):
        mol = Chem.MolFromSmiles(smi)
        return Chem.MolToSmiles(mol) if mol else None
    
    actives = actives_df["canonical_smiles"].apply(canon).dropna().unique().tolist()
    inactives = inactives_df["canonical_smiles"].apply(canon).dropna().unique().tolist()
    
    # Deduplicate: remove molecules that appear in both sets
    active_set = set(actives)
    inactive_set = set(inactives)
    actives = list(active_set - inactive_set)
    inactives = list(inactive_set - active_set)
    
    print(f"  Actives (IC₅₀ < 1 µM):   {len(actives)} unique compounds")
    print(f"  Inactives (IC₅₀ > 10 µM): {len(inactives)} unique compounds")
    
    return actives, inactives

def run_part_b() -> pd.DataFrame:
    """
    Part B: ChEMBL-confirmed antimalarial positive control benchmark.
    Dock actives (IC₅₀ < 1 µM) and inactives (IC₅₀ > 10 µM) against all 4 targets.
    Compare hit rate: target is active hit rate ≥ 2× inactive hit rate.
    """
    print("\n" + "=" * 60)
    print("Part B: ChEMBL-Confirmed Antimalarial Benchmark")
    print("=" * 60)
    
    records = []
    
    for target_name, cfg in TARGETS.items():
        chembl_id = cfg.get("chembl_target")
        if not chembl_id:
            print(f"\n  Skipping {target_name}: no ChEMBL target ID.")
            continue
        
        print(f"\n  Target: {target_name} ({cfg['pdb']}, {chembl_id})")
        
        actives, inactives = fetch_chembl_malaria_controls(chembl_id)
        
        if len(actives) < 10 or len(inactives) < 10:
            print(f"  WARNING: Insufficient controls "
                  f"(actives={len(actives)}, inactives={len(inactives)}). Skipping.")
            continue
        
        # Limit to manageable size
        max_compounds = 100
        actives = actives[:max_compounds]
        inactives = inactives[:max_compounds]
        
        all_smi = actives + inactives
        y_true = np.array([1] * len(actives) + [0] * len(inactives))
        
        print(f"  Docking {len(all_smi)} compounds against {target_name}...")
        scores_dict = dock_smiles_list(all_smi, target_name, exhaustiveness=64)
        
        docked_smi = [s for s in all_smi if s in scores_dict]
        
        if len(docked_smi) < 10:
            print(f"  WARNING: Only {len(docked_smi)} docked. Skipping.")
            continue
        
        docked_labels = np.array([y_true[all_smi.index(s)] for s in docked_smi])
        docked_scores = np.array([scores_dict[s] for s in docked_smi])
        
        # Hit rate analysis
        act_mask = docked_labels == 1
        ina_mask = docked_labels == 0
        act_scores = docked_scores[act_mask]
        ina_scores = docked_scores[ina_mask]
        
        # GOOD threshold: Vina ≤ -5.0 kcal/mol
        act_hit_good = (act_scores <= -5.0).mean() * 100
        ina_hit_good = (ina_scores <= -5.0).mean() * 100
        fold_good = act_hit_good / ina_hit_good if ina_hit_good > 0 else float("inf")
        
        # EXCELLENT threshold: Vina ≤ -7.0 kcal/mol
        act_hit_exc = (act_scores <= -7.0).mean() * 100
        ina_hit_exc = (ina_scores <= -7.0).mean() * 100
        fold_exc = act_hit_exc / ina_hit_exc if ina_hit_exc > 0 else float("inf")
        
        row = {
            "target": target_name,
            "pdb": cfg["pdb"],
            "n_actives": int(act_mask.sum()),
            "n_inactives": int(ina_mask.sum()),
            "n_docked": len(docked_smi),
            "active_hit_rate_GOOD_pct": round(act_hit_good, 1),
            "inactive_hit_rate_GOOD_pct": round(ina_hit_good, 1),
            "fold_enrichment_GOOD": round(fold_good, 2),
            "active_hit_rate_EXCELLENT_pct": round(act_hit_exc, 1),
            "inactive_hit_rate_EXCELLENT_pct": round(ina_hit_exc, 1),
            "fold_enrichment_EXCELLENT": round(fold_exc, 2),
            "pass_2x_criterion_GOOD": fold_good >= 2.0,
            "pass_2x_criterion_EXCELLENT": fold_exc >= 2.0,
        }
        records.append(row)
        
        print(f"  GOOD hit rate — Actives: {act_hit_good:.1f}% | "
              f"Inactives: {ina_hit_good:.1f}% | Fold: {fold_good:.2f}x")
        print(f"  EXCELLENT hit rate — Actives: {act_hit_exc:.1f}% | "
              f"Inactives: {ina_hit_exc:.1f}% | Fold: {fold_exc:.2f}x")
    
    # Save results
    df = pd.DataFrame(records)
    if not df.empty:
        out = RESULTS / "p1_enrichment_chembl_benchmark.csv"
        df.to_csv(out, index=False)
        print(f"\n  Saved: {out}")
    
    return df

# ============================================================================
# SUMMARY WRITER
# ============================================================================

def write_summary(df_a: pd.DataFrame, df_b: pd.DataFrame) -> None:
    """Write human-readable summary."""
    lines = [
        "Enrichment Validation Summary",
        "=" * 50,
        "",
        "Part A: External Enrichment (DEKOIS 2.0)",
        "-" * 50,
    ]
    
    if not df_a.empty:
        lines.append(df_a.to_string(index=False))
    else:
        lines.append("  No results (DEKOIS files missing or docking failed).")
    
    lines += [
        "",
        "Part B: ChEMBL-Confirmed Antimalarial Benchmark",
        "-" * 50
    ]
    
    if not df_b.empty:
        lines.append(df_b.to_string(index=False))
    else:
        lines.append("  No results (ChEMBL query failed or docking failed).")
    
    out = RESULTS / "p1_enrichment_summary.txt"
    out.write_text("\n".join(lines))
    print(f"\n  Summary saved: {out}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="R1: External enrichment validation + ChEMBL antimalarial benchmark"
    )
    parser.add_argument(
        "--part",
        choices=["A", "B", "both"],
        default="both",
        help="Which part to run (default: both)"
    )
    args = parser.parse_args()
    
    # Create output directories
    RESULTS.mkdir(parents=True, exist_ok=True)
    
    df_a = pd.DataFrame()
    df_b = pd.DataFrame()
    
    if args.part in ("A", "both"):
        df_a = run_part_a()
    
    if args.part in ("B", "both"):
        df_b = run_part_b()
    
    write_summary(df_a, df_b)
    
    print("\n" + "=" * 60)
    print("✅ Enrichment validation complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
