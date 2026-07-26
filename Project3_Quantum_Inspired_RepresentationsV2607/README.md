# Project 3 — Topological and Tensor-Network Representations Resolve Chemical Space Paradoxes in African Antimalarial Natural Products (P3)

**Target Journal:** *Journal of Cheminformatics* / *Nature Computational Science*
**Status:** Strategic Roadmap defined — 85% Probability of Acceptance Target (`P3_Stategic_85PA.md`)
**Date:** July 2026

---

## 1. Overview

| Attribute | Details |
|-----------|---------|
| **Focus** | African Natural Product (ANP) Antimalarial Chemical Space |
| **Status** | Advanced benchmarks complete + Physical Validation Plan ready |
| **Target Journal** | *Journal of Cheminformatics* / *Nature Computational Science* |
| **Target Acceptance** | **≥ 85%** (achieved via Tartarus physical validation + polypharmacology benchmark) |
| **Strategic Document** | [`P3_Stategic_85PA.md`](P3_Stategic_85PA.md) |
| **Methodology Skills** | `pennylane`, `datamol`, `scikit-learn`, `pymoo`, `experimental-design`, `BMAD-METHOD` |

---

## 2. The African Natural Product (ANP) Rationale & Novelty Claims

Historically, the most effective antimalarial classes (quinine, artemisinin) originate from natural products. African natural products (AfroDb, p-ANPDB) feature complex 3D architectures, high $sp^3$ carbon fractions, and rigid polycyclic scaffolds that standard 2D molecular fingerprints (ECFP4) fail to represent accurately.

| ID | Distinction / Novelty Claim |
|----|----------------------------|
| **N1** | **Physical Pharmacophore Retention:** First proof that Tensor Network Embedding (TNE, 192-dim, 15.6× compression) retains 3D physical binding affinity across 19,913 molecules (Tartarus docking oracle). |
| **N2** | **Quantum Advantage on Polypharmacology:** First quantum kernel (QKS) vs. SVM RBF benchmark on a hard multi-target antimalarial polypharmacology task ($\ge 2$ *P. falciparum* targets bound). |
| **N3** | **Topological Rigidity vs. Promiscuity:** First topological data analysis (TDA $H_1$ persistent homology) correlation mapping scaffold ring rigidity to biological target promiscuity. |
| **N4** | **Scaffold Paradox Resolution:** Explanation of the 92.6% ECFP4-unreachable gap vs. 69.3% scaffold recovery via persistent homology ($H_1$ preservation vs. $H_0$ divergence). |

---

## 3. Scope & Key Parameters

- **Library**: 65,856 molecules from African Natural Product chemical space (19,849 primary dataset).
- **Physical Oracle**: 19,913 molecules $\times$ 3 *P. falciparum* docking targets (`tartarus_output.csv`).
- **Descriptors**:
  - **TFP**: 12-dim / 78-dim Topological Fingerprints (Vietoris-Rips persistent homology, $H_0, H_1$).
  - **TNE**: Tucker decomposition tensor embeddings (bond_dim=8, 192 dims, 15.6× compression).
  - **QKS**: 8-qubit Quantum Kernel (`pennylane` with `lightning.qubit`/`lightning.gpu` auto-selection via `best_device()`).
- **Statistical Rigour**: 10-fold Stratified Cross-Validation, Bonferroni-corrected Wilcoxon signed-rank tests ($p < 0.01$).

---

## 4. File Architecture

```
Project3_Quantum_Inspired_RepresentationsV2607/
├── AGENTS.md                          # Methodology summary & skill mappings
├── README.md                          # This file — project overview & quick start
├── P3_Stategic_85PA.md                # 85% PA strategic roadmap & physical validation plan
├── scripts/
│   ├── p3_tda_pipeline.py             # Vietoris-Rips persistence diagrams & TFP extraction
│   ├── p3_tne_generate.sbatch         # TNE embedding generation (bond_dim=8)
│   ├── p3_tda_extend.sbatch           # TDA feature extension (19,849 mol.)
│   ├── p3_qks_benchmark.py            # 8-qubit quantum kernel vs RBF-SVM benchmark
│   ├── p3_hybrid_benchmark.py         # Hybrid framework + ablation study
│   └── p3_nisq_smoke_test.py          # 2-qubit IBM Quantum NISQ hardware test
├── manuscript/LaTeX/
│   ├── Paper3_Quantum_Inspired_v0.7_V2607.tex  # Main manuscript
│   └── Bibliography_Paper3.bib        # References
└── results/                           # Generated CSVs and figures (gitignored)
```

---

## 5. Quick Start

```bash
# 1. Environment activation
conda activate malaria_md

# 2. Run TDA persistence pipeline
python scripts/p3_tda_pipeline.py --n-jobs 4

# 3. Generate TNE embeddings (bond_dim=8)
python scripts/p3_tne_pipeline.py --bond-dim 8

# 4. Quantum kernel benchmark (PennyLane best_device)
python scripts/p3_qks_benchmark.py --device lightning.qubit --n-mols 1000

# 5. Execute 85% PA physical validation (TNE vs Tartarus docking scores)
python scripts/p3_physical_validation.py --oracle-csv ../results/tartarus_output.csv
```

---

## 6. Citation & Provenance

- **Data DOI:** `10.5281/zenodo.19608875`
- **GitHub Repository:** https://github.com/NanaEngo/Malaria_codesV2
- **BMAD Compliance:** Full data provenance and canonical directory governance aligned with `BMAD_Q1_DATA_ANALYSIS_REPORT.md`.
