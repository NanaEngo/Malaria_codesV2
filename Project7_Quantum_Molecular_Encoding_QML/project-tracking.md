# P7 Manuscript — Project Tracking

**Date:** 28 August 2026  
**Model:** Claude Sonnet 4.5  
**Active loop:** L1 EVIDENCE (Literature complete, awaiting experimental data)  
**Beat:** 2  

---

## Journal Target

**Journal:** Journal of Chemical Information and Modeling (JCIM)  
**Template:** ACS achemso  
**Format:** Original research article  
**Word limit:** ~6000-8000 words (estimated, following P1 pattern)  
**Submission status:** Pre-draft

---

## Working Title (Provisional)

**Option 1:** "Quantum Molecular Encoding for Antimalarial Drug Discovery: BondOrderMatrix-Based Kernel Learning and Hybrid Quantum-Classical Neural Networks"

**Option 2:** "From Molecular Structure to Quantum States: Direct Encoding of Antimalarial Candidates via BondOrderMatrix and Variational Quantum Circuits"

**Option 3:** "Quantum Advantage in Molecular Encoding: Comparing Quantum Kernel and Hybrid VQC Approaches for Antimalarial Activity Prediction"

**To decide:** Which emphasizes the main contribution best?

---

## Central Question

**Primary:** Can quantum molecular encoding (QMSE: BondOrderMatrix/CoulombMatrix → quantum circuits) improve upon classical molecular fingerprints (ECFP4) for antimalarial activity prediction?

**Secondary:**
1. Does quantum kernel learning (UnitaryOverlap) offer advantages over classical kernels?
2. Can trainable hybrid quantum-classical networks (QMSE → VQC → MLP) achieve competitive performance?
3. Which QMSE method (BondOrderMatrix vs CoulombMatrix) is more effective?

---

## Relationship to P1-P6

| Project | Relationship |
|---------|-------------|
| **P1** | Uses P1 Set A (20 top candidates) as test cohort; compares QMSE quantum encoding vs P1's ECFP4 docking approach |
| **P2** | Independent — P2 uses MD simulation; P7 uses quantum circuits; no overlap |
| **P3** | **Direct extension** — P3 used quantum-*inspired* kernels (QKS) on classical features; P7 uses true quantum encoding + quantum circuits |
| **P4** | Independent — P4 is Monte Carlo optimization; P7 is supervised learning |
| **P5** | **Comparison baseline** — P5 established GNN/Transformer performance; P7 tests if quantum encoding adds value |
| **P6** | Independent — P6 is LISH-MoA phenotype; P7 is structure-based |

**Key narrative:** P7 moves from quantum-*inspired* (P3: QKS on ECFP4) to **true quantum encoding** (QMSE → quantum circuits).

---

## Claims–Evidence Matrix

| Claim ID | Claim | Evidence Source | Ledger Entry | Status |
|----------|-------|----------------|--------------|--------|
| C1 | QMSE encodes molecular structure directly into quantum states | QMSE matrix construction, BondFeatureMap circuit | [PENDING] | 🟡 TO GENERATE |
| C2 | Quantum kernel (UnitaryOverlap) computes similarity in quantum feature space | Kernel Gram matrix, mathematical definition | [PENDING] | 🟡 TO GENERATE |
| C3 | QMSE + quantum kernel achieves AUC ≥ X on P1 Set A | LOO-CV results, ROC curve | [PENDING] | 🟡 AWAITS DATA |
| C4 | QMSE outperforms/equals/underperforms ECFP4 baseline | Head-to-head comparison | [PENDING] | 🟡 AWAITS DATA |
| C5 | Hybrid VQC (trainable) achieves AUC ≥ Y | Training curves, test metrics | [PENDING] | 🟡 AWAITS DATA |
| C6 | BondOrderMatrix is faster/better than CoulombMatrix | Computational cost, performance comparison | [PENDING] | 🟡 AWAITS DATA |
| C7 | Quantum encoding preserves molecular topology and stereochemistry | Matrix element analysis, examples | [PENDING] | 🟡 TO GENERATE |
| C8 | Gradient flow is stable in hybrid VQC (or: gradients vanish — honest-negative) | Gradient norm tracking | [PENDING] | 🟡 AWAITS DATA |

**Status codes:** 🟢 COMPLETE | 🟡 PENDING | 🔴 BLOCKED | ⚪ OPTIONAL

---

## Sprint Plan

### Phase 1: Setup & Outline ✅ COMPLETE
- [x] Create manuscript scaffold
- [x] Create project tracking
- [x] Create analysis ledger
- [x] Complete full outline (sections, figures, tables)
- [x] **Literature search (65+ papers, mapped to claims)**
- [x] **Bibliography file with all core citations**
- [ ] Extract authors from [TBD] placeholders (~20 arXiv papers)

### Phase 2: Evidence Generation
- [ ] Run QMSE kernel experiments (p7_phase1_poc.py)
- [ ] Run hybrid VQC experiments (p7_qmse_hybrid.py) [OPTIONAL]
- [ ] Generate all figures
- [ ] Populate analysis ledger with results
- [ ] Extract P1/P3/P5 baseline numbers for comparison

### Phase 3: Drafting
- [ ] Methods section (QMSE encoding, quantum circuits, kernel, hybrid architecture)
- [ ] Results section (kernel performance, hybrid performance, ablations)
- [ ] Introduction (gap: quantum-inspired → true quantum)
- [ ] Discussion (quantum advantage, limitations, future)
- [ ] Abstract
- [ ] SI (extended methods, additional figures)

### Phase 4: Review & Finalize
- [ ] Independent review passes
- [ ] Anti-AI scan
- [ ] Audit checklist
- [ ] Cover letter

---

## Missing Inputs

### Literature
- [x] Quantum molecular encoding foundations (Boy et al. 2025 quantum-molecular-encodings) ✅
- [x] BondOrderMatrix in QMSE paper (arXiv:2507.20422) ✅
- [x] CoulombMatrix original paper (Rupp et al. 2012) ✅
- [x] Quantum kernel methods in chemistry (Havlíček, Schuld, Q2SAR, QKDTI) ✅
- [x] PennyLane quantum ML framework (Bergholm et al. 2018) ✅
- [x] Barren plateau problem (McClean, Cerezo, survey) ✅
- [x] Quantum ML for drug discovery (Q2SAR, QKDTI, reviews) ✅
- [ ] **ACTION:** Extract author names from ~20 arXiv papers with [TBD] placeholders
- [x] P1-P6 self-citations (placeholder DOIs for unpublished) ✅

### Data
- [ ] P1 Set A molecular structures (SMILES)
- [ ] Activity labels (if available; else use proxy/dummy)
- [ ] QMSE kernel results (to be generated)
- [ ] Hybrid VQC results (to be generated or marked OPTIONAL)
- [ ] ECFP4 baseline results for comparison
- [ ] Computational cost measurements

### Code & Reproducibility
- [ ] QMSE encoding scripts (p7_molecular_encoding.py)
- [ ] Quantum circuit generation (p7_quantum_circuits.py)
- [ ] Kernel computation (p7_quantum_kernel.py)
- [ ] Phase 1 PoC (p7_phase1_poc.py)
- [ ] Hybrid model (p7_qmse_hybrid.py)
- [ ] Environment specification (environment.yml)

---

## File Map

```
manuscript/
├── P7_Quantum_Molecular_Encoding.tex          (main manuscript)
├── P7_Quantum_Molecular_Encoding_SM.tex       (supporting information)
├── P7_QME_references.bib                      (bibliography)
├── sections/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── methods.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
├── Graphics/
│   ├── qmse_workflow_schematic.pdf            (Figure 1: workflow)
│   ├── bond_order_matrix_example.pdf          (Figure 2: QMSE construction)
│   ├── quantum_circuit_diagram.pdf            (Figure 3: BondFeatureMap)
│   ├── kernel_performance_roc.pdf             (Figure 4: ROC curves)
│   ├── hybrid_training_curves.pdf             (Figure 5: loss/metrics)
│   └── ablation_comparison.pdf                (Figure 6: QMSE methods)
└── tables/
    ├── qmse_vs_ecfp4_comparison.tex           (Table 1: performance)
    ├── computational_cost.tex                 (Table 2: runtime)
    └── p1_set_a_results.tex                   (Table 3: per-molecule)

outputs/
├── analysis/
│   └── analysis-ledger.md                     (all calculations)
├── literature/
│   ├── paper-lookup-raw.md
│   └── literature-map.md
└── critical-reviews/
    └── (review outputs)

scripts/
├── qmse_lib/                                  (QMSE core)
├── p7_quantum_circuits.py
├── p7_quantum_kernel.py
├── p7_phase1_poc.py
├── p7_qmse_hybrid.py
└── p7_data_preparation.py
```

---

## Review Log

_Empty — no reviews yet_

---

## Notes

- **Honest-negative policy:** If QMSE underperforms ECFP4, this is a valid dissertation contribution documenting when quantum encoding does not help.
- **Computational budget:** Quantum simulations are expensive; prioritize kernel approach (faster) over hybrid VQC (slower) if compute-limited.
- **Dissertation alignment:** This is one chapter/paper in "Quantum Machine Learning Approach for Malaria Drug Discovery" thesis.
- **P3 connection:** P3 used QKS (quantum-inspired kernel on classical ECFP4); P7 uses true quantum encoding — this progression is the key narrative.

---

**Last updated:** 28 August 2026, Beat 1
