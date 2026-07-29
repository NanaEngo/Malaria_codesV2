# Results Directory

**⚠️ Generated Outputs - Do Not Commit**

This directory contains script outputs, screening results, and generated data (~430 MB).

## Directory Structure

```
results/
├── eos*/                # Screening campaign results (Ersilia models)
├── clustering/          # Cluster labels, latent vectors, and summaries
├── figures/             # Publication-quality figures and plots
├── ligands/             # Unified ligand structures archive
│   ├── pdb/             # Full 3D ligand structures (65,856+ files)
│   └── pdbqt/           # Docking-ready ligands for AutoDock Vina
├── c*.csv/txt           # Manuscript calculation outputs (C1-C14)
└── *.csv                # Global screening and MPO summaries
```

## Key Statistics (Verified April 2026)

| Metric | Value | Description |
|--------|-------|-------------|
| **Final hybrid library** | **65,856** | From 396 African NPs + 454 SDs |
| **Unique scaffolds** | **20,702** | Bemis-Murcko scaffolds (31.4% diversity) |
| **Primary leads (MPO ≥ 0.70)** | **20,466** | 31.1% of library |
| **Secondary hits (0.50 ≤ MPO < 0.70)** | **37,138** | 56.4% of library |
| **Synthesisable leads** | **19,913** | MPO ≥ 0.70 AND SYBA > 0 |
| **Polypharmacological candidates** | **>70** | Engaging ≥2 targets simultaneously |
| **Tanimoto novelty rate** | **92.6%** | 4,630/5,000 vs. seed NPs |
| **Lipinski Ro5 compliance** | **94.1%** | 61,975 / 65,856 |

## Contents by Category

### Screening Results

| Pattern | Description | Size | Records |
|---------|-------------|------|---------|
| `eos80ch_malaria_final_activity.csv` | Final hybrid library | ~25 MB | **65,856** |
| `eos7yti_all_mol_activity.csv` | Seed molecules screened | ~10 MB | **850** |
| `eos7kpb_all_mol_screening.csv` | Multi-strain + ADMET | ~25 MB | **850** |
| `eos2db3_malaria_final_chemdiv_mpo.csv` | MPO scores, drug-likeness | ~30 MB | 65,856 |
| `eos9gg2_malaria_final_drugbank_mpo.csv` | PCA/UMAP/t-SNE coordinates | ~20 MB | 65,856 |
| `eos57bx_generated_mol2molscaf.csv` | Generative expansion arms | ~50 MB | 65,856 |

### MPO Tier Distribution

| Tier | Threshold | Count | % |
|------|-----------|-------|---|
| **Primary leads** | MPO ≥ 0.70 | **20,466** | **31.1%** |
| **Secondary hits** | 0.50 ≤ MPO < 0.70 | 37,138 | 56.4% |
| **Borderline** | 0.35 ≤ MPO < 0.50 | 7,776 | 11.8% |
| **Deprioritised** | MPO < 0.35 | 476 | 0.7% |

> 87.5% of the library achieved MPO ≥ 0.50, confirming generative expansion preserved drug-like characteristics.

### Docking Outputs

| Directory | Format | Purpose |
|-----------|--------|---------|
| `ligands/pdb/` | PDB | 3D ligand structures (65,856+) |
| `ligands/pdbqt/` | PDBQT | AutoDock-ready ligands |

### Manuscript Calculations (C1-C14)

| File | Calculation | Purpose | Status |
|------|-------------|---------|--------|
| `c1_library_size.csv` | C1: Library size verification | Confirm N = 65,856 | ✅ |
| `c2_generative_arms.csv` | C2: Per-source breakdown | Quantify Cheese vs. STONED | ✅ |
| `c3_selectivity_index.csv` | C3: Selectivity index (SI > 10) | Flag selective compounds | ✅ |
| `c4_cyp450_inhibition.csv` | C4: CYP450 inhibition profile | Safety annotation | ✅ |
| `c5_aqueous_solubility.csv` | C5: Aqueous solubility | Co-formulation needs | ✅ |
| `c6_syba_shortlist.csv` | C6: SYBA-filtered shortlist | Synthesis candidates | ✅ |
| `c7_stage_activity.csv` | C7: Stage-specific activity | Per-source medians | ✅ |
| `c8_pca_variance.csv` | C8: PCA explained variance | "PC1-3 explain X%" | ✅ |
| `c9_scaffold_analysis.csv` | C9: Bemis-Murcko scaffold analysis | Top scaffolds | ✅ |
| `c10_scaffold_recovery.csv` | C10: Scaffold recovery rate | "% NP scaffolds recovered" | ✅ |
| `c11_fsp3_analysis.csv` | C11: fsp³ per source group | 3D complexity | ✅ |
| `c12_tanimoto_novelty.csv` | C12: Tanimoto novelty | 92.6% novelty rate | ✅ |
| `c13_diffdock_vina_corr.csv` | C13: DiffDock-Vina correlation | Pooled r = -0.049 | ✅ |
| `c14_2d_diagrams/` | C14: 2D interaction diagrams | Key residue contacts | ✅ |


### Paper 2 & 3 Outputs (pending computation)

| File | Description | Status |
|------|-------------|--------|
| `md_top20_candidates.csv` | Top 20 MD candidates (MPO/SYBA/SI filtered) | ⏳ Pending |
| `c_rrs_classification.csv` | RRS Classes A–D for 20 candidates × 6 mutants | ⏳ Pending |
| `c_acsi_scores.csv` | ACSI scores for 65,856-molecule library | ⏳ Pending |
| `c_pns_ranking.csv` | PNS ranking for 20 candidates | ⏳ Pending |
| `md_mpo_sensitivity.csv` | MPO weight sensitivity (Jaccard heatmap) | ⏳ Pending |
| `p3_tda_fingerprints.csv` | TFP matrix (65,856 × 12) | ⏳ Pending |
| `p3_tne_embeddings.csv` | TNE embeddings (65,856 × core_dim, d=8) | ⏳ Pending |
| `p3_qks_benchmark.csv` | Quantum kernel vs RBF-SVM (5-fold CV) | ⏳ Pending |
| `p3_hybrid_benchmark.csv` | Hybrid TFP+TNE+QK benchmark + ablation | ⏳ Pending |

## Regenerating Results

Results are **regenerable** and should not be committed to Git. To regenerate:

```bash
# Run pipeline notebooks
jupyter notebook pipelines/06_stoned-selfies.ipynb
jupyter notebook pipelines/07_consensus_filtering.ipynb

# Or run Python scripts
python Python_scripts/03_clustering.py
python Python_scripts/06_stoned_selfies.py
```

## Git Configuration

This directory is **ignored** in `.gitignore` to prevent committing large generated files.

```gitignore
# .gitignore
results/
```

## File Naming Convention

Results follow the pattern: `eos{campaign_id}_{analysis_type}.{ext}`

- `eos{campaign_id}`: Experiment campaign identifier
- `{analysis_type}`: Type of analysis (all_mol, malaria_final, generated, etc.)
- `{ext}`: File extension (csv, png, pdf, etc.)

## Accessing Results

```python
from malaria_explorer.utils.config import RESULTS_DIR
import pandas as pd

# Access results directory
results_path = RESULTS_DIR / "eos7kpb_malaria_final_screening.csv"

# Load results
df = pd.read_csv(results_path)
print(f"Loaded {len(df)} molecules")
```

## Storage Management

| Action | Command |
|--------|---------|
| Check size | `du -sh results/` |
| List largest files | `du -sh results/* | sort -hr \| head -20` |
| Clean old results | `rm results/eos*_old_*.csv` |

---

**Location:** `results/`
**Size:** ~430 MB (regenerable)
**Git Status:** Ignored (do not commit)
**Last Updated:** April 8, 2026
**Status:** ✅ Verified (65,856 molecules, 92% acceptance probability)
