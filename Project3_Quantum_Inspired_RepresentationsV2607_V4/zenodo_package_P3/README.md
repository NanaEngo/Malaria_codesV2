# P3 Reproducibility Package — JCAMD Submission

**DOI**: https://doi.org/10.5281/zenodo.19608875 (reserved)  
**License**: CC BY 4.0  
**Manuscript**: "Quantum-inspired molecular representations for African antimalarial candidates: topological fingerprints, tensor network embeddings, and kernel methods"  
**Journal**: *Journal of Computer-Aided Molecular Design* (JCAMD)  
**Version**: V4 (submitted 2026-08-30)  
**Authors**: Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; Nana Engo, S. G.

---

## Purpose

This deposit provides complete reproducibility records for Project 3 (P3), evaluating three quantum-inspired molecular representations against classical ECFP4 fingerprints on a curated panel of 19,836 African antimalarial candidates.

**Key finding**: None of the three non-classical representations (TFP, TNE, QKS) improves predictive performance beyond ECFP4 under the tested protocols, though they add diagnostic and interpretive value.

All files are sha256-verified. The checksum manifest is in `sha256sums.txt`.

---

## Contents

### 1. `data/` — Core datasets

| File | Description |
|------|-------------|
| `p3_labels_production.csv` | 19,849 molecules with activity labels (computational predictions) |
| `p3_panel_smiles.csv` | Canonical SMILES for the full panel |
| `p3_tda_fingerprints.csv` | Topological fingerprints (TFP) — 84 features per molecule |
| `p3_tne_embeddings.csv` | Tensor Network Embeddings (TNE) — 192-dim, 13 failures |

### 2. `results/` — Benchmark results

#### Core benchmarks
- `p3_hybrid_benchmark.csv` — 5-fold CV RF AUC for 9 representations
- `p3_qks_benchmark_v1.csv` — Quantum Kernel Score internal benchmark
- `p3_sota_benchmark.csv` — SOTA comparison (PersStats, TFP-enriched)
- `p3_chembl_external_validation.csv` — External ChEMBL label-shift validation

#### Regression analyses
- `p3_tne_regression_summary.csv` — TNE vs ECFP4 on docking scores (PfDHFR, PfATP4, PfCRT)
- `p3_tartarus_polypharma.csv` — Polypharmacology proxy analysis

#### TDA analyses
- `p3_tda_promiscuity_correlation.csv` — H0/H1 persistence vs target count

### 3. `scripts/` — Analysis code

| Script | Purpose |
|--------|---------|
| `p3_tda_pipeline.py` | Topological fingerprint generation (persistent homology) |
| `p3_tne_pipeline.py` | Tensor Network Embedding (Tucker decomposition) |
| `p3_qks_kernel.py` | Quantum Kernel Score computation (IQPEmbedding, 8 qubits) |
| `p3_hybrid_benchmark.py` | 5-fold CV benchmark for all representations |
| `p3_external_validation.py` | ChEMBL external validation pipeline |
| `p3_regression_analysis.py` | Docking score regression (TNE vs ECFP4) |
| `environment.yml` | Conda environment specification |

### 4. `documentation/` — Supporting documents

| File | Description |
|------|-------------|
| `P3_DATA_ANALYSIS_REPORT.md` | Complete data provenance and analysis record |
| `P3_METHODS_SUPPLEMENT.md` | Detailed computational methods |
| `P3_RESULTS_SUMMARY.md` | Executive summary of key findings |

---

## How to Use This Deposit

### Verify Integrity

Before using any data, verify the checksums:

```bash
cd zenodo_package_P3
sha256sum -c sha256sums.txt
```

**Expected output**: All files OK (no mismatches).

### Reproduce Key Results

#### 1. Verify hybrid benchmark (Table 2 in manuscript)

```bash
python scripts/p3_hybrid_benchmark.py \
  --input data/p3_labels_production.csv \
  --tda data/p3_tda_fingerprints.csv \
  --tne data/p3_tne_embeddings.csv \
  --output results/p3_hybrid_benchmark_reproduced.csv
```

**Expected**:
- ECFP4-RF: AUC 0.9475 ± 0.0043
- Hybrid (TFP+TNE+QK): AUC 0.8876 ± 0.0072
- TFP-RF: AUC 0.6300 ± 0.1121
- TNE-RF: AUC 0.6300 ± 0.1121

#### 2. Reproduce quantum kernel benchmark (Table 3)

```bash
python scripts/p3_qks_kernel.py \
  --input data/p3_labels_production.csv \
  --n-samples 5000 \
  --n-folds 5 \
  --output results/p3_qks_reproduced.csv
```

**Expected**:
- Quantum kernel: AUC 0.7512 ± 0.0334
- RBF-SVM: AUC 0.7007 ± 0.0672
- Paired t-test: p = 0.0878 (not significant)

#### 3. Reproduce external validation (ChEMBL)

```bash
python scripts/p3_external_validation.py \
  --chembl-data data/p3_chembl_expanded.csv \
  --output results/p3_chembl_validation_reproduced.csv
```

**Expected**:
- Internal quantum: AUC 0.7512
- External quantum: AUC 0.817
- External RBF: AUC 0.847 (quantum performs *worse*, p=0.021)

#### 4. Reproduce TNE regression analysis (Figure 4)

```bash
python scripts/p3_regression_analysis.py \
  --input data/p3_tne_embeddings.csv \
  --docking-scores data/p3_docking_scores.csv \
  --output results/p3_regression_reproduced.csv
```

**Expected R²**:
- PfDHFR: TNE 0.473 vs ECFP4 0.461 (competitive)
- PfATP4: TNE 0.464 vs ECFP4 0.578 (ECFP4 better)
- PfCRT: TNE 0.334 vs ECFP4 0.517 (ECFP4 better)

---

## File Formats

### CSV files
- Comma-separated
- UTF-8 encoding
- First row = column headers
- SMILES strings are canonical (RDKit-generated)

### Tensor Network Embeddings (TNE)
- Tucker decomposition: bond_dim=8, ranks=(8,8,3)
- Output dimension: 192
- Reconstruction error: mean 0.113, max 0.220
- 13 failures out of 19,849 molecules (flagged in data)

### Topological Fingerprints (TFP)
- Persistent homology features: 84 dimensions
- H0 (connected components) and H1 (loops/cycles)
- Vietoris-Rips filtration
- 0 failures (all molecules successfully processed)

### Quantum Kernel Scores (QKS)
- 8-qubit IQPEmbedding circuit
- Simulated on classical hardware (no quantum device access)
- Kernel matrix computed via overlap of quantum states

---

## Software Versions

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11.10 | Analysis environment |
| RDKit | 2025.03.6 | SMILES, descriptors, ECFP4 |
| NumPy | 2.2.1 | Array operations |
| pandas | 2.2.3 | Tabular data |
| SciPy | 1.15.1 | Statistics |
| scikit-learn | 1.6.1 | ML models, CV |
| PennyLane | 0.45.1 | Quantum kernels |
| Gudhi | 3.10.1 | Persistent homology (TDA) |
| tensorly | 0.8.1 | Tucker decomposition (TNE) |
| matplotlib | 3.10.1 | Figures |

**Environment**: `malaria_md` conda environment (see `scripts/environment.yml` for complete package list).

---

## Evidence Boundaries

This deposit provides:
- ✅ Benchmark results on 19,836 curated molecules
- ✅ Five-fold cross-validation with multiple random seeds
- ✅ External validation on ChEMBL dataset
- ✅ Honest-negative results (quantum-inspired methods do not outperform ECFP4)
- ✅ Diagnostic value demonstrations (TDA promiscuity correlations)

This deposit **does NOT provide**:
- ❌ Claims of quantum advantage (QKS is simulated, not run on quantum hardware)
- ❌ Prospective experimental validation
- ❌ Guaranteed biological activity predictions
- ❌ Hardware quantum computer results
- ❌ Complete scaffold-based split analysis (reported separately in P5)

**The quantum-inspired representations provide complementary chemical insights but not superior predictive performance under the tested protocols.**

---

## Relation to Manuscript

This deposit corresponds to:
- **Main text**: Tables 1–4, Figures 1–5
- **Supporting Information**: Tables S1–S6, Figures S1–S4

**Manuscript sections directly supported**:
- §2 Methods (TFP, TNE, QKS protocols)
- §3.1 Benchmark design and panel curation
- §3.2 Hybrid representation performance
- §3.3 Quantum kernel evaluation
- §3.4 External validation
- §3.5 Regression and promiscuity analyses

---

## Citation

**Dataset**:
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. (2026). P3 Reproducibility Package — JCAMD Submission [Data set]. 
Zenodo. https://doi.org/10.5281/zenodo.19608875
```

**Manuscript** (when published):
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. Quantum-inspired molecular representations for African antimalarial 
candidates: topological fingerprints, tensor network embedings, and kernel methods. 
J. Comput. Aided Mol. Des. 2026, XX, XXXX–XXXX. DOI: [to be assigned]
```

---

## Contact

**Corresponding author**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**ORCID**: 0009-0004-5170-2309  
**Institution**: Department of Physics, Faculty of Science, University of Yaoundé I, Cameroon

**Code repository** (to be made public upon publication): https://github.com/NanaEngo/Malaria_codesV2

---

## Acknowledgments

This work was supported by computational resources from the University of Yaoundé I. Quantum kernel simulations were performed using PennyLane's classical simulator.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V4 | 2026-08-30 | Initial Zenodo deposit for JCAMD submission |

---

**Last updated**: 2026-09-11  
**Package prepared by**: Kiro AI agent  
**Zenodo deposit ID**: 19608875 (reserved, pending upload)
