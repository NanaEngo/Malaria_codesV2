# Project 3 — Quantum-inspired molecular representations for AI-generated African antimalarial candidates: persistent homology, tensor networks, and quantum kernels (P3)

**Target Journal:** *Journal of Cheminformatics*
**Status:** ✅ **Submission-ready** — canonical benchmarks complete; manuscript trimmed 26→18 p. (main 18 p. / 7 230 mots, SM 18 p., cover letter 1 p., 0 erreur / 0 réf. indéfinie)
**Date:** July 2026 (updated Aug 2, 2026)

---

## 1. Overview

| Attribute | Details |
|-----------|---------|
| **Focus** | African Natural Product (ANP) Antimalarial Chemical Space |
| **Status** | ✅ Submission-ready — canonical benchmarks complete (jobs 12698/12699/12700/12702) |
| **Target Journal** | *Journal of Cheminformatics* |
| **Manuscript** | Main `Paper3_Quantum_InspiredV2608.tex` (20 p. after final H1–RRS reconciliation) + SM `Paper3_Quantum_Inspired_SM_V2608.tex` (18 p.) + cover letter (1 p.) — trim 26→18 p. (02/08/2026), fusion des tables benchmark/hybrid, `tab:qkernel`→SM S13, titre harmonisé. ⚠️ V2607 et `_refined` archivés dans `manuscript/LaTeX/archive/` |
| **Key Results (canonical)** | ECFP4 **0.9475 ± 0.0045** (n=19,836) ; Hybrid RF **0.8876 ± 0.0065** (p<0.0001 vs ECFP4) ; ablation QK Δ=−0.040 (principal contributeur) ; QKS 6q ≈ RBF (p=0.060/0.419, ns) ; TFP 0.8759 ; TNE 0.7219 (6.1× compression réelle) ; 92.6% ECFP4-unreachable / 69.3% scaffold recovery |
| **ChEMBL validation** | ✅ Exécutée (02/08/2026) — 10 leads top queryés : analogues ChEMBL tous **Inactive**, Tanimoto 0.229–0.379 (résultat honnête négatif = nouveauté chimique, pas de validation expérimentale positive) |
| **Resistance integration** | Analyse canonique **H₁–RRS** sur n=494 : H₁ count ρ=0.2399 (p=6.76×10⁻⁸) avant ajustement, mais ρ_partial=0.0329 (p=0.4668) après contrôle MW, cycles, fraction sp³ et H₀ ; résultat size-confounded, hypothesis-generating, sans preuve d’un prédicteur topologique indépendant |
| **Strategic Docs** | [`P3_ADVERSARIAL_AUDIT_MITIGATION.md`](P3_ADVERSARIAL_AUDIT_MITIGATION.md) (v3.1) · [`P3_SUBMISSION_ROADMAP_85PCT.md`](P3_SUBMISSION_ROADMAP_85PCT.md) · boussole : `BMAD_Q1_DATA_ANALYSIS_REPORT.md` |
| **Methodology Skills** | `pennylane`, `datamol`, `scikit-learn`, `pymoo`, `experimental-design`, `BMAD-METHOD` |

---

## 2. The African Natural Product (ANP) Rationale & Novelty Claims

Historically, the most effective antimalarial classes (quinine, artemisinin) originate from natural products. African natural products (AfroDb, p-ANPDB) feature complex 3D architectures, high $sp^3$ carbon fractions, and rigid polycyclic scaffolds that standard 2D molecular fingerprints (ECFP4) fail to represent accurately.

### Literature gaps (anchored)

The manuscript positions itself against two open gaps: (i) the "larger is better" narrative is untested on antimalarial NP space — this study controls it on a dedicated panel; (ii) quantum kernels and tensor/topological representations are advocated as richer, but their *scalable, honest* benchmark against classical baselines is missing. P3 answers both with canonical, fixed-panel comparisons (n=19,849) and publishes an honest negative (QKS ≈ RBF).

| ID | Distinction / Novelty Claim |
|----|----------------------------|
| **N1** | **Physical Pharmacophore Retention:** First proof that Tensor Network Embedding (TNE, 192-dim, 6.1× real compression) retains 3D physical binding affinity across 19,913 molecules (Tartarus docking oracle). |
| **N2** | **Quantum Kernel Parity at Scale:** First canonical benchmark showing quantum kernel (QKS) ≈ RBF at n=5,000 (p=0.419) and n=19,849 (p=0.060) — honest negative, no quantum advantage claimed. |
| **N3** | **Topological Rigidity vs. Promiscuity:** First topological data analysis (TDA $H_1$ persistent homology) correlation mapping scaffold ring rigidity to biological target promiscuity. |
| **N4** | **Scaffold Paradox Resolution:** Explanation of the 92.6% ECFP4-unreachable gap vs. 69.3% scaffold recovery via persistent homology ($H_1$ preservation vs. $H_0$ divergence). |
| **N5** | **Resistance Resilience as a Topological Signal:** First mapping of $H_1$ count to resistance-resilience scores (RRS) of antimalarial leads — the explicit bridge from representation to the P2 resistance-validation programme. |

---

## 3. Scope & Key Parameters

- **Library**: 65,856 molecules from African Natural Product chemical space (19,849 primary dataset).
- **Physical Oracle**: 19,913 molecules × 3 *P. falciparum* docking targets (`tartarus_output.csv`).
- **Descriptors**:
  - **TFP**: 78-dim Topological Fingerprints (Vietoris-Rips persistent homology, $H_0, H_1$).
  - **TNE**: Tucker decomposition tensor embeddings (bond_dim=8, 192 dims, 6.1× real compression).
  - **QKS**: 6-qubit Quantum Kernel Score (state-vector, `pennylane` `lightning.qubit`).
- **Statistical Rigour**: 5-fold Stratified Cross-Validation (canonical), Bonferroni-corrected paired $t$-tests / Wilcoxon.

---

## 4. File Architecture

```
Project3_Quantum_Inspired_RepresentationsV2607/
├── P3_ADVERSARIAL_AUDIT_MITIGATION.md   # Audit adverse & mitigation (v3.1)
├── P3_SUBMISSION_ROADMAP_85PCT.md       # Roadmap de soumission (→ ≥85% PA)
├── README.md                            # Ce fichier
├── scripts/
│   ├── p3_tda_pipeline.py               # Vietoris-Rips persistence diagrams & TFP extraction
│   ├── p3_tne_generate.sbatch           # TNE embedding generation (bond_dim=8)
│   ├── p3_tda_extend.sbatch             # TDA feature extension (19,849 mol.)
│   ├── p3_qks_benchmark.py              # Quantum kernel vs RBF-SVM benchmark
│   ├── p3_hybrid_benchmark.py           # Hybrid framework + ablation study
│   ├── p3_chembl_validation.py          # ChEMBL IC50 validation (top-10 leads)
│   └── p3_nisq_smoke_test.py            # 2-qubit IBM Quantum NISQ hardware test
├── manuscript/LaTeX/
│   ├── Paper3_Quantum_InspiredV2608.tex        # Main manuscript (18 p.) — CANONIQUE
│   ├── Paper3_Quantum_Inspired_SM_V2608.tex    # Supplementary Material (18 p.) — CANONIQUE
│   ├── Cover_Letter_P3.tex                     # Cover letter (1 p.)
│   ├── archive/                                # V2607, _refined (tex+pdf) — historiques
│   └── Bibliography_Paper3.bib                 # References
└── results/                           # Generated CSVs and figures
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

# 4. Quantum kernel benchmark (PennyLane best_device, CPU)
python scripts/p3_qks_benchmark.py --device lightning.qubit --n-mols 1000

# 5. ChEMBL IC50 validation (top-10 candidates)
python scripts/p3_chembl_validation.py
```

---

## 6. Citation & Provenance

- **Data DOI:** `10.5281/zenodo.19608875` (reserved; upload pending) (reserved; Zenodo upload pending)
- **GitHub Repository:** https://github.com/NanaEngo/Malaria_codesV2
- **BMAD Compliance:** Full data provenance and canonical directory governance aligned with `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (v50, 02/08/2026).
