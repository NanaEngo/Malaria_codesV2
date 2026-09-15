# P5 Reproducibility Package — Pre-Submission Development

**DOI**: https://doi.org/10.5281/zenodo.[TBD] (to be reserved)  
**License**: CC BY 4.0  
**Manuscript**: "Graph neural networks and transformers for antimalarial activity prediction: honest-negative results under chemical distribution shift"  
**Journal**: *Journal of Computer-Aided Molecular Design* (JCAMD) [target]  
**Version**: V2609 (pre-submission development)  
**Authors**: Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; Nana Engo, S. G.

---

## Purpose

This deposit provides complete reproducibility records for Project 5 (P5), evaluating Graph Neural Networks (GNNs) and Transformer models against classical ECFP4-Random Forest on a curated panel of 19,836 African antimalarial candidates under chemical distribution shift.

**Key finding (honest-negative)**: ECFP4-RF outperforms all learned models under scaffold-based split (ECFP4-RF: 0.8300 vs best GNN: 0.8138), with the gap driven by novel test molecules (NN-Tanimoto decile analysis).

All files are sha256-verified. The checksum manifest is in `sha256sums.txt`.

---

## Contents

### 1. `data/` — Core panel and splits

| File | Description |
|------|-------------|
| `p5_panel_19836.csv` | Complete molecular panel with SMILES and activity labels |
| `p5_splits/` | Frozen train/test splits (random, scaffold, Butina) |
| `p5_graph_cache.pkl` | Pre-computed molecular graphs for GNN models |

### 2. `results/` — Benchmark and robustness analyses

#### Core benchmark (canonical)
- `p5_replication_stats.csv` — 5-fold × 5-seed statistics for all models
- `p5_ecfp4rf_random_baseline.json` — ECFP4-RF reference performance
- `p5_GIN_random_results.csv` — GIN per-fold results (25 records)
- `p5_GIN_scaffold_results.csv` — GIN scaffold split (25 records)
- Similar files for GIN-TFP, GIN-TNE, ChemBERTa

#### Extended robustness campaign
- `extended_campaign_20260825/` — Complete robustness analysis
  - 625 fold-seed records across 25 configurations
  - Novel scaffold partitions (novel_101, novel_202, novel_303)
  - Descriptor permutation tests
  - Salience stability analysis

#### External validation
- `p5_public_chembl_malaria_disjoint.csv` — 22,267 molecule-disjoint ChEMBL panel
- `p5_chembl_transfer_results.json` — Transfer learning results

#### Distribution-shift analyses
- `nn_tanimoto_deciles_20260829/` — Per-decile AUC stratification
- `butina_cluster_20260829/` — Stricter scaffold-cluster split
- `calibration_20260827/` — ECE/MCE/Brier under shift

### 3. `scripts/` — Analysis pipeline

| Script | Purpose |
|--------|---------|
| `p5_gnn_train.py` | GNN training (GIN, GIN-TFP, GIN-TNE) |
| `p5_chemberta_train.py` | ChemBERTa fine-tuning |
| `p5_ecfp4_baseline.py` | ECFP4-RF reference |
| `p5_extended_campaign.py` | Robustness campaign executor |
| `p5_nn_tanimoto_deciles.py` | NN-Tanimoto stratification |
| `p5_butina_cluster.py` | Butina scaffold-cluster split |
| `p5_calibration_posthoc.py` | Calibration analysis |
| `environment.yml` | Conda environment specification |

### 4. `documentation/` — Supporting documents

| File | Description |
|------|-------------|
| `P5_DATA_ANALYSIS_REPORT.md` | Complete data provenance and analysis record |
| `P5_METHODS_SUPPLEMENT.md` | Detailed computational methods |
| `P5_RESULTS_SUMMARY.md` | Executive summary of key findings |

---

## How to Use This Deposit

### Verify Integrity

```bash
cd zenodo_package_P5
sha256sum -c sha256sums.txt
```

### Reproduce Key Results

#### 1. Canonical benchmark (Table 1)

```bash
# Random split
python scripts/p5_ecfp4_baseline.py --split random --n-folds 5 --n-seeds 5
python scripts/p5_gnn_train.py --model GIN --split random --n-folds 5 --n-seeds 5

# Scaffold split
python scripts/p5_gnn_train.py --model GIN --split scaffold --n-folds 5 --n-seeds 5
```

**Expected (scaffold split, mean over 5 per-seed means)**:
- ECFP4-RF: 0.8300 ± 0.0023
- GIN-TFP: 0.8138 ± 0.0107
- GIN: 0.8047 ± 0.0141
- GIN-TNE: 0.8090 ± 0.0149
- ChemBERTa: 0.7867 ± 0.0054

#### 2. NN-Tanimoto decile stratification (Figure 3)

```bash
python scripts/p5_nn_tanimoto_deciles.py \
  --split scaffold \
  --output results/nn_tanimoto_deciles_reproduced/
```

**Expected** (scaffold, decile 1→10, NN-sim 0.31→0.63):
- ECFP4-RF: 0.779 → 0.890 (strong improvement)
- GIN-TFP: 0.752 → 0.883
- **Gap driven by novel molecules (deciles 1-9)**

#### 3. Butina cluster split (Table S4)

```bash
python scripts/p5_butina_cluster.py \
  --distance-cutoff 0.55 \
  --n-folds 5 \
  --n-seeds 5
```

**Expected**:
- ECFP4-RF: 0.8331
- GIN-TFP: 0.8232
- GIN: 0.8202
- ChemBERTa: 0.7776

#### 4. External ChEMBL validation

```bash
python scripts/p5_external_validation.py \
  --chembl-panel data/p5_public_chembl_malaria_disjoint.csv \
  --model-checkpoint results/gin_scaffold_final.pt
```

**Expected**:
- ECFP4-RF: 0.9190
- GIN: 0.8843 ± 0.0021
- Δ = 0.0346, p = 3.35×10⁻⁶

---

## File Formats

### CSV files
- Comma-separated, UTF-8 encoding
- SMILES strings are canonical (RDKit-generated)
- Activity labels: binary (0/1)

### Graph cache
- PyTorch Geometric Data objects
- Pre-computed edge indices and node features
- Cached to avoid repeated graph construction

### Splits
- JSON format with train/test indices per fold
- Deterministic given seed
- Scaffold split: greedy Murcko scaffold assignment
- Butina split: Tanimoto distance clustering (cutoff=0.55)

---

## Software Versions

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11.10 | Core environment |
| PyTorch | 2.13.0 | Deep learning framework |
| PyTorch Geometric | 2.8.0 | GNN library |
| Transformers | 5.14.1 | ChemBERTa |
| RDKit | 2025.03.6 | SMILES, ECFP4 |
| NumPy | 2.2.1 | Array operations |
| pandas | 2.2.3 | Tabular data |
| scikit-learn | 1.6.1 | RF, metrics, CV |

**Environment**: `malaria_md` conda environment.

---

## Evidence Boundaries

This deposit provides:
- ✅ 5-fold × 5-seed canonical benchmark
- ✅ Honest-negative scaffold-split result
- ✅ NN-Tanimoto decile stratification
- ✅ Butina cluster split (stricter extrapolation test)
- ✅ External ChEMBL validation (22,267 molecules)
- ✅ Calibration analysis under distribution shift
- ✅ Descriptor permutation and salience stability

This deposit **does NOT provide**:
- ❌ Claims of universal GNN/Transformer superiority
- ❌ Prospective experimental validation
- ❌ Temporal or clinical validation
- ❌ Complete mechanistic interpretability
- ❌ Guaranteed biological activity predictions

**The fingerprint advantage is driven by the novel half of the test set (NN-Tanimoto decile analysis).**

---

## Relation to Manuscript

This deposit corresponds to:
- **Main text**: Tables 1–2, Figures 1–4
- **Supporting Information**: Tables S1–S17, Figures S1–S6

**Manuscript sections**:
- §2 Methods (GNN, ChemBERTa, ECFP4-RF, splits)
- §3.1 Canonical benchmark
- §3.2 External validation
- §3.3 Distribution-shift analyses
- §3.4 Calibration and robustness

---

## Citation

**Dataset**:
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. (2026). P5 Reproducibility Package [Data set]. 
Zenodo. https://doi.org/10.5281/zenodo.[TBD]
```

**Manuscript** (when published):
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. Graph neural networks and transformers for antimalarial 
activity prediction: honest-negative results under chemical distribution shift. 
J. Comput. Aided Mol. Des. 2026, XX, XXXX–XXXX. DOI: [to be assigned]
```

---

## Contact

**Corresponding author**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**ORCID**: 0009-0004-5170-2309  
**Institution**: Department of Physics, Faculty of Science, University of Yaoundé I, Cameroon

**Code repository**: https://github.com/NanaEngo/Malaria_codesV2

---

## Acknowledgments

Computational resources from the University of Yaoundé I. GPU computing for ChemBERTa and GNN training.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V2609 | 2026-09-11 | Initial Zenodo package (pre-submission) |

---

**Last updated**: 2026-09-11  
**Package prepared by**: Kiro AI agent  
**Zenodo deposit ID**: [TBD] (to be reserved)
