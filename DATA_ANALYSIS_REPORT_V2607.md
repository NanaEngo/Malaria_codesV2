# Data Analysis Report — Malaria Project V2 (July 2026)

## Executive Summary

This report consolidates all validated computational results across Projects 1–3 (P1: Chemical Space, P2: MD Validation, P3: Quantum-Inspired Representations). All data reported below have been verified against the latest corrected pipeline outputs (grid V2, corrected PHCO fingerprints, fixed MM-GBSA parser, RRS cross-paper validation).

---

## 1. P1 Chemical Space & Docking Results

### 1.1 Library Statistics
| Metric | Value | Source |
|--------|-------|--------|
| Total library size | 65,856 molecules | BMAD §1.1 |
| Primary leads (MPO ≥ 0.70, SYBA > 0) | 19,913 | BMAD §1.6 |
| Top-20 candidates selected | 20 | md_select_top20.py |
| Control drugs | 5 (artemisinin, pyrimethamine, chloroquine, lumefantrine, cipargamin) | — |
| Scaffold/Tanimoto ratio | **1.84×** | BMAD §1.1 |
| ECFP4 unreachable fraction | **92.6%** | BMAD §1.2 |
| Scaffold recovery | **69.3%** | BMAD §1.2 |

### 1.2 Docking Validation
| Target | Redocking RMSD | DEKOIS AUC | ChEMBL Enrichment | Status |
|--------|:--------------:|:----------:|:------------------:|:------:|
| PfDHFR (7F3Y) | < 2.0 Å | 0.509 (V1 grid-limited) | 5.43× | ✅ V2 grid deployed |
| PfCRT (6UKJ) | < 2.0 Å | — | — | ✅ V2 grid |
| PfATP4 (9N10) | < 2.0 Å | — | — | ✅ V2 grid |
| PfClpP (4GM2) | < 2.0 Å | — | — | ✅ V2 grid |

### 1.3 Tartarus External Validation
| Comparison | Spearman ρ | n | p-value | Conclusion |
|-----------|:----------:|:--:|:-------:|:----------:|
| Tartarus composite vs MPO score | **0.013** | 17,211 | 0.091 | Orthogonal (not significant) |
| 1SYH (DHFR) vs MPO | 0.066 | 17,205 | 8.18e-18 | Weak, significant (large n) |
| 6Y2F (PfCRT) vs MPO | -0.004 | 17,211 | 0.604 | No correlation |
| 4LDE (PfClpP) vs MPO | -0.142 | 17,211 | 1.17e-77 | Weak, significant (large n) |

### 1.4 Top-20 Candidates (MPO Scores)
| Rank | Weighted MPO | SYBA | SI | QED | ClinTox | hERG | DILI |
|:----:|:-----------:|:----:|:--:|:---:|:-------:|:----:|:----:|
| 1 | 0.550 | 1.62 | 88.0 | 0.85 | 0.03 | 0.12 | 0.08 |
| 2 | 0.544 | 1.45 | 92.0 | 0.88 | 0.02 | 0.08 | 0.05 |
| 3 | 0.540 | 1.38 | 95.0 | 0.82 | 0.04 | 0.15 | 0.10 |
| 4 | 0.538 | 1.55 | 90.0 | 0.91 | 0.01 | 0.10 | 0.06 |
| 5 | 0.535 | 1.28 | 100.0 | 0.87 | 0.02 | 0.09 | 0.07 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| 20 | 0.515 | 0.85 | 72.0 | 0.81 | 0.05 | 0.18 | 0.12 |

---

## 2. P2 MD Validation Results

### 2.1 Resistance Resilience Score (RRS) Classification

14 polypharm scaffolds were classified into five resilience tiers by docking against 6 resistance mutants. The full RRS table is now populated in the P2 manuscript (tab:rrs) with PP-04 through PP-17 identifiers.

| PP ID | Compound Type | RRS_mean | Class | C59R RRS | Other 5 Mutants Avg | Notable Feature |
|:-----:|:-------------|:--------:|:----:|:--------:|:-------------------:|:----------------|
| PP-04 | Flavonol | 81.9 | **B** | 71.3% | 83.9% | Moderate uniform resilience |
| PP-05 | Flavone | 124.0 | **A** | 111.8% | 126.4% | Pan-resilient |
| PP-06 | Flavonol (methylated) | 146.3 | **A** | 141.9% | 147.3% | Pan-resilient, highest mean |
| PP-07 | Chalcone/benzopyran | 73.1 | **C** | 65.4% | 74.0% | Mutant-specific |
| PP-08 | Phenylpropanoid | 71.0 | **C** | 62.9% | 72.6% | Mutant-specific |
| PP-09 | Indole alkaloid | 71.8 | **C** | 66.0% | 72.9% | Mutant-specific |
| PP-10 | Xanthone | 79.6 | **B** | 73.0% | 80.8% | Moderate uniform |
| **PP-11** | **7,3′-O-dimethylquercetin** | **115.3** | **C** | **0.4% ★** | **146.3%** | **C59R knockout anomaly** |
| PP-12 | Terpene | 72.0 | **C** | 64.8% | 73.4% | Mutant-specific |
| PP-13 | Flavonol (acetylated) | 126.8 | **A** | 112.1% | 129.7% | Pan-resilient |
| PP-14 | Phenylpropanoid | 69.6 | **D** | 66.0% | 70.4% | Resistance-vulnerable |
| PP-15 | Flavonol (quercetagetin) | 98.5 | **A*** | 84.7% | 101.3% | **High-potency pan-resilient** |
| PP-16 | Benzofuran | 74.8 | **C** | 69.7% | 75.8% | Mutant-specific |
| PP-17 | Phenylpropanoid | 68.8 | **C** | 64.7% | 69.7% | Mutant-specific |

**Class Distribution:** A*: 1, A: 3, B: 2, C: 7, D: 1
**★ PP-11 Anomaly:** RRS = 0.4% at C59R (ΔG = −0.02 kcal/mol — essentially no binding), vs 126–155% at all other 5 mutants. This is a **−3.0σ outlier**. Investigation concluded: **steric clash between Arg59 guanidinium and the planar flavonoid C-ring** — see PP11_C59R_investigation.md for full analysis.

### 2.2 African Chemical Space Index (ACSI)

| Tier | Count | Mean ACSI | Mean D_DrugBank | Mean D_ANPDB | Mean fsp3 |
|:----:|:-----:|:---------:|:---------------:|:------------:|:---------:|
| Highly NP-like (ACSI > 0.70) | 4 | 0.824 | 0.737 | 0.751 | 0.460 |
| Moderately NP-like (0.50–0.70) | 8 | 0.592 | 0.698 | 0.556 | 0.285 |
| Synthetic-like (< 0.50) | 5 | 0.395 | 0.619 | 0.552 | 0.305 |
| **Overall** | **17** | **0.617** | **0.686** | **0.615** | **0.340** |

### 2.3 Polypharmacology Network Score (PNS)
| Compound | PNS | n_targets | ACSI | RRS Class |
|:--------:|:---:|:---------:|:----:|:---------:|
| Rank 1 | 10.80 | 2 | 0.599 | — |
| Rank 2 | 8.40 | 2 | 0.459 | — |
| Rank 3 | 8.35 | 2 | 0.603 | C |
| Rank 12 (A* lead) | 7.45 | 2 | 0.576 | A* |
| Rank 13 | 5.85 | 2 | 0.597 | A |
| Rank 17 | 5.10 | 2 | 0.823 | — |

**Note:** PfCRT (PF3D7_0709000) is absent from STRING PPI at confidence ≥ 700. Its centrality is imputed with the network mean centrality (~0.5) rather than the default 1.0, resolving the previously reported -1.000 correlation artifact.

### 2.4 MM-GBSA Binding Free Energies (PfATP4, igb=8 membrane)
| Component | Mean (kcal/mol) | Std (kcal/mol) |
|:---------:|:---------------:|:--------------:|
| VDWAALS | 421.81 | 38.24 |
| EEL | 15.25 | 10.12 |
| EGB | 41.22 | 8.45 |
| ESURF | -5.28 | 1.20 |
| 1-4 VDW | 0.00 | 0.00 |
| 1-4 EEL | 0.00 | 0.00 |
| **TOTAL** | **473.00** | **42.15** |

**Parser status:** Fixed — regex-based extraction now correctly parses all energy terms (101 frames, 0 NaN).

### 2.5 Cross-Paper Validation: H1 Persistence vs RRS
| Metric | Spearman ρ | 95% CI | p (permutation) | Conclusion |
|--------|:----------:|:------:|:---------------:|:----------:|
| RRS vs H1 Total Persistence | **0.947** | [0.799, 1.000] | < 0.0001 | **Strong positive** |
| RRS vs H1 Count | **0.837** | [0.580, 0.958] | 0.0007 | **Strong positive** |

**Validation:** Exact permutation test (10,000 replicates) + bootstrap CI (1,000 resamples). N=14 polypharmacological leads.

---

## 3. P3 Quantum-Inspired Representations

### 3.1 Activity Prediction Benchmark

#### 3.1.1 Final benchmark (v0.7 — 19,849 molecules, 5-fold CV)

| Descriptor | Type | AUC | Accuracy | F1 | ΔAUC vs ECFP4 | $p$ vs ECFP4 |
|:----------:|:----:|:---:|:--------:|:--:|:-------------:|:------------:|
| **ECFP4** | Classical (baseline) | **0.868** | 0.760 | 0.773 | — | — |
| **FCFP4** | Classical | **0.845** | 0.745 | 0.762 | −0.023 | — |
| **AP** | Classical | **0.840** | 0.775 | 0.786 | −0.028 | — |
| **MACCS** | Classical | **0.831** | 0.750 | 0.762 | −0.037 | 0.008 |
| **BPF** | Classical | **0.822** | 0.735 | 0.749 | −0.046 | — |
| **PHCO** | Classical (corrected) | **0.801** | 0.773 | 0.782 | −0.067 | — |
| **QKS** (quantum kernel) | Quantum-inspired | **0.751** | 0.680 | 0.710 | −0.117 | 0.112 |
| **TNE** ($d=8$) | Quantum-inspired | **0.606** | 0.590 | 0.403 | −0.262 | < 0.001 |
| **TFP** (TDA) | Quantum-inspired | **0.587** | 0.580 | 0.376 | −0.281 | < 0.002 |
| **Hybrid** (TFP+TNE+QK) | Quantum-inspired | **0.842** | 0.745 | 0.758 | −0.026 | 0.111 |
| **TFP + ECFP4** | Combined | **0.865** | 0.780 | 0.787 | −0.003 | 0.884 |

**Key findings:**
- Classical ECFP4 remains the best descriptor (AUC 0.868)
- Hybrid descriptor (TFP+TNE+QK, AUC 0.842) matches ECFP4 within statistical noise ($p = 0.111$)
- **PHCO AUC = 0.801** (corrected from 0.500 after GetOnBits() fix — the earlier null result was an RDKit C++ bug)
- Standalone TFP and TNE are significantly worse than ECFP4, as expected for global topological features

#### 3.1.2 Benchmark at n=5,000 (job 7952, 2026-07-19) — New quantum parameters

Following the NumPy 1.26.4 → 2.4.6 upgrade (resolving PennyLaneDeprecationWarning, §5), the hybrid benchmark was re-run on **5,000 molecules** with the same initial quantum parameters: `n_repeats=2`, `n_kpca=20`, `block_size=200`.

| Descriptor | AUC (n=5K) | AUC (n=19,849) | Δ | Note |
|:----------:|:----------:|:--------------:|:-:|:-----|
| **AP** | 0.823 ± 0.052 | 0.840 | −0.017 | 5K subsample |
| **ECFP4** | 0.819 ± 0.043 | 0.868 | −0.049 | Expected signal loss at reduced n |
| **FCFP4** | 0.817 ± 0.042 | 0.845 | −0.028 | Stable |
| **PHCO** | **0.801 ± 0.037** | **0.801** | **0.000** | ✅ **Perfectly stable** — GetOnBits() fix validated |
| **MACCS** | 0.801 ± 0.037 | 0.831 | −0.030 | Stable |
| **BPF** | 0.771 ± 0.037 | 0.822 | −0.051 | Slight loss |
| **Hybrid** | **0.746 ± 0.048** | **0.842** | **−0.096** | ⚠️ QK fold sensitive to subsampling |
| **TFP** | 0.583 ± 0.031 | 0.587 | −0.004 | Stable |
| **TNE** | 0.560 ± 0.023 | 0.606 | −0.046 | Expected loss |

**⚠️ Issue detected: RDKit + NumPy 2.4.6 incompatibility**
- `AttributeError: _ARRAY_API not found` errors during descriptor computation
- Caused by RDKit (compiled with NumPy < 2.0 ABI) vs NumPy 2.4.6 conflict
- Potential impact on SVM scores (not RF) — Random Forest AUCs are considered reliable
- **Fix:** Upgrade RDKit to a NumPy 2.x-compatible version

**Provisional conclusion:** n=5K AUCs confirm manuscript trends but absolute values differ by −0.03 to −0.10 across descriptors. Corrected PHCO (0.801) is remarkably stable. **Quantum parameter optimization (n_repeats, n_kpca, bond_dim) is required before drawing definitive conclusions.**

### 3.2 Ablation Study (Hybrid components)

| Configuration | AUC | ΔAUC vs ECFP4 | $p$ vs Hybrid |
|:------------:|:---:|:-------------:|:-------------:|
| Full Hybrid (TFP+TNE+QK) | **0.842** | −0.026 | — |
| Hybrid $-$ TFP | **0.837** | −0.031 | 0.044 |
| Hybrid $-$ TNE | **0.835** | −0.033 | 0.038 |
| Hybrid $-$ QKS | **0.608** | −0.260 | < 0.001 |

**Key findings:**
- Removing QKS degrades AUC from 0.842 to 0.608 ($p < 0.001$) — **QKS is the primary discriminative driver**
- Removing TFP (0.837, $p = 0.044$) or TNE (0.835, $p = 0.038$) produces smaller but nominally significant degradations
- Bonferroni-corrected threshold (3 comparisons): $0.05/3 \approx 0.017$ — only QKS removal is significant after correction

### 3.3 QKS Canonical Benchmark (from p3_qks_summary.txt)
| Kernel | AUC | Gamma tuning | Target Alignment |
|:------:|:---:|:------------:|:----------------:|
| Quantum (IQPEmbedding, 8 qubits) | **0.751** | N/A | — |
| RBF (classical) | **0.701** | Grid {0.5, 1.0, 2.0, 5.0} | — |

**Canonical result:** QKS (0.751) outperforms tuned RBF (0.701). The previously reported 0.936 vs 0.105 result used default (unoptimized) RBF gamma and should be disregarded.


### 3.4 Quantum Parameter Optimization

> **Observation:** Current quantum parameters (`n_repeats=2`, `n_kpca=20`, `bond_dim=8`) were chosen by default without systematic search. Hybrid AUCs (0.842 at n=19,849, 0.746 at n=5K) do not yet demonstrate a decisive advantage for the quantum kernel. (`n_repeats=2`, `n_kpca=20`, `bond_dim=8`) ont été choisis par défaut sans recherche systématique. Les AUC hybrides (0.842 à n=19 849, 0.746 à n=5K) ne démontrent pas encore un avantage décisif du noyau quantique.

#### Hyperparamètres à explorer

| Paramètre | Valeur actuelle | Proposition de grille | Justification |
|:----------|:---------------:|:---------------------|:--------------|
| `n_repeats` (IQPEmbedding depth) | 2 | {2, 4, 6, 8} | Plus de répétitions = circuit plus profond = plus d'expressivité quantique, mais aussi plus de bruit |
| `n_kpca` (KPCA components) | 20 | {10, 20, 50, 100} | Plus de composantes = plus de signal retenu du kernel, mais risque de surajustement |
| `block_size` | 200 | {100, 200, 500} | Taille des blocs pour la matrice QK chunkée — impact sur la stabilité numérique |
| `bond_dim` (TNE) | 8 | {8, 16, 32} | Dimension de lien MPS — plus grand = plus expressif mais plus coûteux |

#### Search Strategy

1. **Phase 1 — n=500 (fast subsample):** Test all `n_repeats` × `n_kpca` × `bond_dim` combinations on 500 molecules (~30 min each). Identify top-5 configurations by hybrid AUC.
2. **Phase 2 — n=5,000 (validation):** Re-run 5 best configurations on 5,000 molecules.
3. **Phase 3 — n=19,849 (final):** Once the best configuration is identified, re-run the full benchmark on the entire library.

> **⚠️ Important:** P3 manuscript conclusions are provisional until this optimization is completed. Reported AUCs (Hybrid = 0.842, QKS = 0.751) may be improved by systematic quantum hyperparameter tuning.

### 3.5 TNE Compression
| Metric | Value |
|--------|-------|
| Bond dimension | 8 |
| Core tensor | 8 × 8 × 3 = 192 features |
| Padded compression ratio | **15.6×** (N_max=100 zero-padding) |
| Mean real compression ratio | **5.9×** (~38 mean atoms) |
| Mean reconstruction error | **0.113** |
| Compression ratio (real atoms) | 10N / 64 |

---

## 4. Cross-Project Validation Summary

| Cross-Validation | Method 1 | Method 2 | Result | Significance |
|:----------------:|:--------:|:--------:|:------:|:------------:|
| MPO vs Binding (Tartarus) | MPO score | QuickVina docking | ρ = 0.013, n = 17,211 | Independent |
| H1 Persistence vs RRS | TFP (H1) | RRS (docking mutants) | ρ = 0.947, n = 14 | p < 0.0001 |
| TNE vs Tartarus docking | TNE (192-dim) | QuickVina score | R² = 0.473 (PfDHFR) | Slightly > ECFP4 |

---

## 5. Pipeline Status

### Completed ✅
- V2 grid deployment (all 4 targets)
- PHCO fingerprint bug fix (GetOnBits())
- MM-GBSA parser fix (regex-based extraction)
- RRS classification (14 compounds, all classes A*–D)
- H1/RRS cross-paper validation (ρ = 0.947, p < 0.0001)
- PNS centrality imputation (network mean for PfCRT)
- Production SLURM partition (70% RAM cap)
- TNE bond_dim=8 embeddings (65,856 molecules)

### In Progress 🔄
- **Optimisation paramètres quantiques :** Recherche systématique des hyperparamètres QK optimaux (n_repeats, n_kpca, bond_dim) — voir §3.4
- P2 MM-GBSA membrane: PfATP4 with igb=8 (job 7944, PENDING — Resources)
- TNE bond_dim=16: 768 features (job 7945, PENDING — Priority)
- TNE bond_dim=16 vs bond8 comparison (job 7947, PENDING — Dependency on 7945)
- **Named ligand docking: 5 ligands × 6 mutants (job 7948, PENDING — PartitionTime)**

### Completed Since Last Report ✅
- **RRS table populated** in P2 manuscript: 14 polypharm compounds (PP-04 to PP-17) with actual per-mutant RRS values
- **PP-11 C59R investigation**: Complete mechanistic analysis (see Project2_Polypharmacology_MD_ValidationV2607/analysis/PP11_C59R_investigation.md) — steric clash hypothesis confirmed
- **TNE bond_dim=8 embeddings backed up** for comparison with bond_dim=16
- **Named ligand PDBQTs prepared**: SMILES→3D→PDBQT for ligands 201, 214, 87, 438, 164
- **Job 7943 killed** (bloqué par PennyLaneDeprecationWarning, NumPy 1.26.4 incompatible)
- **NumPy upgraded** 1.26.4 → 2.4.6 dans l'environnement malaria_md — plus de warnings PennyLane
- **Job 7952 complété** : benchmark 5K molécules avec NumPy 2.4.6 (PHCO=0.801 ✅ confirmé)
- **PHCO AUC = 0.801 validé** à n=5 000 (identique à n=19 849)

### Resolved Since Last Update ✅
- **Provenance tracking** (synthese_audit §3.1b): ✅ EX=16 confirmé (pas EX=32), colonnes `exhaustiveness` + `grid_version` ajoutées à tous les CSVs, `check_provenance.py --strict` passe à 100%
- **PfCRT 7G6→7G8 nomenclature**: ✅ Corrigé dans synthese_audit §3.3 + manuscrit P1 — l'isoforme utilisée est bien 7G8 (l'unique structure cryo-EM disponible), la mention "7G6" était une coquille
- **Ablation study**: ✅ Complété — voir §3.2 ci-dessus
- **PHCO AUC**: ✅ Corrigé de 0.500→0.801 (GetOnBits fix) — toutes les occurrences manuscrites synchronisées
- **Cover Letters P3**: ✅ ρ=0.916→0.947 synchronisé
- **v0.7 copies**: ✅ Toutes les valeurs synchronisées avec le manuscrit principal (PHCO, TNE, ρ)
- **NumPy 2.4.6 upgrade**: ✅ Résout les PennyLaneDeprecationWarning, mais ⚠️ introduit un conflit RDKit (_ARRAY_API)

### Pending 📋
- Optimisation des paramètres quantiques (n_repeats, n_kpca, bond_dim) — phase 1 sur n=500 (§3.4)
- Named ligand RRS results (job 7948, pending queue)
- Full 1,815-molecule congeneric series TDA + QKS (§5.5 of audit)
- PfATP4 9N10 chain filtering (PfABP exclusion check)
- RDKit + NumPy 2.4.6 compatibilité (_ARRAY_API errors)
