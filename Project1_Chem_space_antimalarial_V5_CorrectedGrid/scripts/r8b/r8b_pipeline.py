#!/usr/bin/env python3
"""
R8-B Implementation — Top-10 Binding Modes + Retrosynthesis
Project 1: JCIM Manuscript (V2607)

Generates:
1. SM Table S20: Top-10 candidates with SMILES, scores, retrosynthetic routes
2. SM Figure S15: Multi-panel 2D structure diagrams
3. ASKCOS retrosynthesis via public API (no token required)

Public ASKCOS API (MIT): https://askcos.mit.edu
Endpoints (no auth):
  - /api/tree-search/expand-one/call-sync-without-token
  - /api/tree-search/mcts/call-sync-without-token

Author: Myke Vital Sao Temgoua
Date: July 12, 2026
Version: 1.1
"""

import argparse
import json
import re
import time
import sys
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import Draw, rdDepictor
    HAS_RDKit = True
except ImportError:
    HAS_RDKit = False
    print("[WARN] RDKit not available – structure diagrams will be placeholders")

# Requests (for ASKCOS API)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[WARN] requests not available – ASKCOS API calls disabled")

# ── Paths ─────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # Malaria_codesV2
PROJECT1_DIR = REPO_ROOT / "Project1_Chem_space_antimalarial_V2_CorrectedGrid"
PROJECT2_DIR = REPO_ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
DEFAULT_INPUT = PROJECT2_DIR / "data" / "from_project1" / "results" / "md_top20_candidates.csv"
DEFAULT_TABLE = PROJECT1_DIR / "manuscript" / "SM_Table_S20_top10_retrosynthesis.tex"
DEFAULT_FIGURE = PROJECT1_DIR / "manuscript" / "SM_Figure_S15_top10_binding_modes.pdf"
CACHE_DIR = PROJECT1_DIR / "results" / "r8b"

# ASKCOS public endpoint (no auth)
ASKCOS_EXPAND_URL = "https://askcos.mit.edu/api/tree-search/expand-one/call-sync-without-token"
ASKCOS_MCTS_URL = "https://askcos.mit.edu/api/tree-search/mcts/call-sync-without-token"

# Reaction SMARTS → human-readable name mapping
REACTION_MAP = [
    (r"\[CH;D2;\+0:\d\]-\[c:\d\]\.\[C:\d\]-\[NH;D2;\+0:\d\]-\[C:\d\]", "Reductive amination (aldehyde + amine)"),
    (r"O=\[CH;D2;\+0:\d\]-\[c:\d\].*O=\[CH;D2;\+0:\d\]-\[c:\d\]", "Reductive amination (two aldehydes + amine)"),
    (r"Br-\[CH2;D2;\+0:\d\]-\[c:\d\]", "N-alkylation (alkyl bromide)"),
    (r"Cl-\[CH2;D2;\+0:\d\]-\[c:\d\]", "N-alkylation (alkyl chloride)"),
    (r"\[C:\d\]-\[NH;D2;\+0:\d\]-\[C:\d\]\.\[c:\d\]:\[cH;D2;\+0:\d\]:\[c:\d\]", "C-N cross-coupling"),
    (r"O-\[CH2;D2;\+0:\d\]-\[c:\d\]", "N-alkylation (alcohol)"),
    (r"\[C:\d\]-\[O;H0;D2;\+0:\d\]-\[c:\d\]", "O-alkylation"),
    (r"C-\[O;H0;D2;\+0:\d\]-\[c:\d\]", "O-alkylation / ether formation"),
    (r"\[CH2;D1;\+0:\d\]", "Formylation / multicomponent"),
    (r"\[c:\d\]:\[cH;D2;\+0:\d\]:\[c:\d\]", "C-H activation / coupling"),
]

def classify_reaction(smarts):
    """Convert SMARTS pattern to human-readable reaction name."""
    if not smarts or smarts == 'N/A':
        return 'N/A'
    for pattern, name in REACTION_MAP:
        if re.search(pattern, smarts):
            return name
    return smarts[:40] + '...' if len(smarts) > 40 else smarts

# ── Helpers ────────────────────────────────────────────────────────────────

def load_top20(path):
    df = pd.read_csv(path)
    print(f"[OK] Loaded {len(df)} candidates from {path}")
    return df


def select_top10(df):
    top = df.sort_values('weighted_mpo_score', ascending=False).head(10).copy()
    top['rank'] = range(1, 11)
    print(f"[OK] Top-10 by MPO score: {top['weighted_mpo_score'].min():.3f} – {top['weighted_mpo_score'].max():.3f}")
    return top


def canonical_smiles(smi):
    """Return canonical SMILES (RDKit) or original on failure."""
    if not smi:
        return smi
    try:
        mol = Chem.MolFromSmiles(smi)
        return Chem.MolToSmiles(mol) if mol else smi
    except Exception:
        return smi


# ── ASKCOS API ─────────────────────────────────────────────────────────────

def query_askcos_expand(smiles, timeout=30):
    """
    Call the public ASKCOS expand-one endpoint (no token needed).
    Returns parsed JSON response, or None on failure.
    """
    if not HAS_REQUESTS:
        return None

    payload = {
        "smiles": canonical_smiles(smiles),
        "retro_backend_options": [
            {
                "retro_backend": "template_relevance",
                "retro_model_name": "reaxys",
                "max_num_templates": 100,
                "max_cum_prob": 0.995,
                "threshold": 0.3,
                "top_k": 5,
            }
        ],
        "banned_chemicals": [],
        "use_fast_filter": True,
        "fast_filter_threshold": 0.75,
        "retro_rerank_backend": "relevance_heuristic",
        "extract_template": False,
        "selectivity_check": False,
    }

    try:
        resp = requests.post(ASKCOS_EXPAND_URL, json=payload, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"  [WARN] ASKCOS expand returned {resp.status_code} for {smiles[:50]}")
            return None
    except requests.exceptions.Timeout:
        print(f"  [WARN] ASKCOS timeout for {smiles[:50]}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  [WARN] ASKCOS connection error (offline?)")
        return None
    except Exception as e:
        print(f"  [WARN] ASKCOS error: {e}")
        return None


def parse_askcos_routes(response):
    """
    Parse ASKCOS expand-one response into human-readable synthetic routes.
    Returns list of (precursors, reaction_type, score) tuples.
    """
    routes = []
    if not response:
        return routes

    results = response.get('result', [])
    if not results and isinstance(response, list):
        results = response

    for result in results[:5]:
        try:
            # precursors (outcome) and reaction info
            precursors = result.get('outcome', 'N/A')
            # reaction SMARTS from template metadata
            meta = result.get('model_metadata', [])
            rxn_smarts = ''
            if meta:
                tmpl = meta[0].get('source', {}).get('template', {})
                rxn_smarts = tmpl.get('reaction_smarts', '')

            score = result.get('precursor_score', 0)
            rank = result.get('precursor_rank', 0)

            # Build a human-readable reaction description
            if rxn_smarts:
                # Extract reaction type from SMARTS
                rxn_type = rxn_smarts.split('>>')[-1][:60] if '>>' in rxn_smarts else 'N/A'
            else:
                rxn_type = 'N/A'

            routes.append((precursors, rxn_type, score, rank))

        except Exception:
            continue

    # Sort by rank
    routes.sort(key=lambda x: x[3])
    return routes


def askcos_batch(smiles_list, cache_dir=None, delay=2.0):
    """
    Query ASKCOS for a batch of SMILES with caching and rate limiting.
    Returns dict mapping SMILES -> list of (precursors, rxn_type, score, rank).
    """
    cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "askcos_cache.json"

    # Load existing cache
    cache = {}
    if cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text())
            print(f"[OK] Loaded {len(cache)} cached ASKCOS results")
        except Exception:
            cache = {}

    results = {}
    for i, smi in enumerate(smiles_list):
        key = canonical_smiles(smi)
        if key in cache and cache[key] is not None:
            results[smi] = cache[key]
            n = len(cache[key])
            print(f"  [{i+1}/{len(smiles_list)}] {smi[:40]}... ({n} routes, cached)")
            continue

        print(f"  [{i+1}/{len(smiles_list)}] Querying ASKCOS: {smi[:40]}...")
        resp = query_askcos_expand(smi)
        routes = parse_askcos_routes(resp)
        results[smi] = routes
        cache[key] = routes

        # Save cache after each query
        cache_file.write_text(json.dumps(cache, indent=2))

        # Rate limiting
        if i < len(smiles_list) - 1:
            time.sleep(delay)

    n_with = sum(1 for v in results.values() if v)
    print(f"[OK] ASKCOS: {n_with}/{len(results)} compounds have routes")
    return results


# ── Output generation ──────────────────────────────────────────────────────

def generate_sm_table_s20(df_top10, askcos_results, output_path):
    """Generate SM Table S20 with retrosynthetic analysis."""
    with open(output_path, 'w') as f:
        f.write("% SM Table S20: Top-10 Polypharmacological Candidates with Retrosynthetic Analysis\n")
        f.write("% Generated by r8b_pipeline.py (ASKCOS public API)\n\n")

        # ── Table 1: Candidate data ──
        f.write("\\begin{table}[htbp]\n\\centering\n")
        f.write("\\caption{Top-10 polypharmacological candidates from the generative library. "
                "MPO $\\geq$ 0.50 across multiple targets. "
                "\\label{tab:sm_s20_top10_retrosynthesis}}\n")
        f.write("\\small\n\\begin{tabular}{l l l l l l}\n\\toprule\n")
        f.write("Rank & SMILES & MPO Score & SYBA Score & QED & Targets \\\\\n\\midrule\n")

        for _, row in df_top10.iterrows():
            smi = row.get('smiles', 'N/A')
            f.write(f"{row['rank']} & {smi} & {row['weighted_mpo_score']:.3f} & "
                    f"{row['syba_score']:.1f} & {row['qed']:.3f} & PfDHFR, PfCRT, PfATP4 \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")

        # ── Table 2: Retrosynthetic routes ──
        f.write("\\begin{table}[htbp]\n\\centering\n")
        f.write("\\caption{Predicted retrosynthetic routes for top-10 candidates via ASKCOS "
                "(public API, MIT). Precursors and reaction types from template relevance "
                "model (Reaxys database).\n\\label{tab:sm_s20_retrosynthesis}}\n")
        f.write("\\small\n\\begin{tabular}{l l l}\n\\toprule\n")
        f.write("Compound & Proposed Precursors & Reaction Type \\\\\n\\midrule\n")

        has_routes = False
        for _, row in df_top10.iterrows():
            smi = row.get('smiles', '')
            routes = askcos_results.get(smi, [])
            if routes:
                has_routes = True
                for j, route in enumerate(routes[:3]):
                    if len(route) >= 2:
                        prec, rxn_type = route[0], route[1]
                        score = route[2] if len(route) > 2 else 0
                    else:
                        prec, rxn_type = 'N/A', 'N/A'
                        score = 0
                    compound = f"T{row['rank']} (route {j+1})"
                    prec_trim = prec[:80] + '...' if len(prec) > 80 else prec
                    rxn_name = classify_reaction(rxn_type)
                    rxn_trim = rxn_name[:80] + '...' if len(rxn_name) > 80 else rxn_name
                    f.write(f"{compound} & {prec_trim} & {rxn_trim} \\\\\n")
            else:
                f.write(f"T{row['rank']} & No route found & — \\\\\n")

        if not has_routes:
            f.write("% No ASKCOS routes found – API may be unavailable\n")

        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    print(f"[OK] Generated SM Table S20: {output_path}")


def generate_sm_figure_s15(df_top10, output_path):
    """Generate 2D structure diagram for top-10 candidates."""
    if not HAS_RDKit:
        print("[WARN] RDKit unavailable – generating placeholder figure")
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.text(0.5, 0.5,
                "SM Figure S15 Placeholder\nTop-10 Binding Mode Diagrams\n(RDKit needed)",
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        plt.savefig(output_path, format='pdf', bbox_inches='tight')
        plt.close()
        print(f"[WARN] Created placeholder: {output_path}")
        return

    fig, axes = plt.subplots(2, 5, figsize=(16, 8))
    axes = axes.flatten()

    for i, (_, row) in enumerate(df_top10.iterrows()):
        smi = row.get('smiles', '')
        try:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                axes[i].axis('off')
                continue
            rdDepictor.Compute2DCoords(mol)
            img = Draw.MolToImage(mol, size=(280, 280))
            axes[i].imshow(img)
            axes[i].axis('off')
            axes[i].set_title(f"T{i+1}", fontsize=10, fontweight='bold')
        except Exception:
            axes[i].axis('off')

    for j in range(len(df_top10), len(axes)):
        axes[j].axis('off')

    plt.suptitle("SM Figure S15: Top-10 Polypharmacological Candidates", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated SM Figure S15: {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="R8-B: Top-10 Binding Modes + Retrosynthesis")
    parser.add_argument('--input', default=str(DEFAULT_INPUT))
    parser.add_argument('--output-table', default=str(DEFAULT_TABLE))
    parser.add_argument('--output-figure', default=str(DEFAULT_FIGURE))
    parser.add_argument('--askcos', action='store_true',
                        help="Query ASKCOS public API for retrosynthesis routes")
    parser.add_argument('--cachedir', default=str(CACHE_DIR),
                        help="Cache directory for ASKCOS results")
    parser.add_argument('--delay', type=float, default=2.0,
                        help="Delay between ASKCOS API calls (default: 2s)")
    parser.add_argument('--no-cache', action='store_true',
                        help="Skip cache and re-query all compounds")

    args = parser.parse_args()

    print("=" * 60)
    print("R8-B Pipeline: Top-10 Binding Modes + Retrosynthesis")
    print("=" * 60)

    # Load & select
    df = load_top20(args.input)
    top10 = select_top10(df)

    # ASKCOS
    askcos_results = {}
    if args.askcos:
        if not HAS_REQUESTS:
            print("[ERR] requests library required for ASKCOS API. Install: pip install requests")
            sys.exit(1)

        smiles_list = [s for s in top10['smiles'].tolist() if s]
        print(f"\n[ASKCOS] Querying {len(smiles_list)} compounds via public API "
              f"(delay={args.delay}s, cache={not args.no_cache})...")

        if args.no_cache:
            # Clear cache file
            cache_file = Path(args.cachedir) / "askcos_cache.json"
            if cache_file.exists():
                cache_file.unlink()

        askcos_results = askcos_batch(
            smiles_list,
            cache_dir=args.cachedir if not args.no_cache else None,
            delay=args.delay,
        )

        # Summary
        found = sum(1 for v in askcos_results.values() if v)
        print(f"\n[ASKCOS] Routes found for {found}/{len(askcos_results)} compounds")
    else:
        print("\n[ASKCOS] Skipped (use --askcos to query API)")

    # Generate outputs
    generate_sm_table_s20(top10, askcos_results, args.output_table)
    generate_sm_figure_s15(top10, args.output_figure)

    print("\n" + "=" * 60)
    print("[OK] R8-B Pipeline completed")
    print(f"  Table : {args.output_table}")
    print(f"  Figure: {args.output_figure}")
    if args.askcos:
        print(f"  Cache : {Path(args.cachedir) / 'askcos_cache.json'}")
    print("=" * 60)


if __name__ == '__main__':
    main()
