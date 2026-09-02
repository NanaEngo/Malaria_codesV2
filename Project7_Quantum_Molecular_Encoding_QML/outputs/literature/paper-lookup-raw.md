# P7 Literature Search — Raw Results

**Date:** 28 August 2026  
**Purpose:** Systematic literature search for P7 bibliography completion  
**Databases:** Web search (arXiv, Nature, PubMed, Google Scholar aggregated)

---

## Search 1: Quantum Molecular Encoding

**Query:** "quantum molecular encoding BondOrderMatrix molecular structure representation"  
**Date:** 28 August 2026  
**Results:** 10 papers

### Key Findings:

#### ⭐ PRIMARY: QMSE Paper (arXiv:2507.20422)
**Title:** Encoding molecular structures in quantum machine learning  
**URL:** https://arxiv.org/abs/2507.20422  
**Published:** 2025  
**Key Point:** Introduces quantum molecular structure encoding (QMSE) scheme using hybrid Coulomb-adjacency matrix (BondOrderMatrix) encoded directly as quantum circuit rotations

**Citation:**
```bibtex
@Article{Boy2025QMSE,
  author  = {Boy, Marvin and K\"{o}rner, Jonas and others},
  title   = {Encoding molecular structures in quantum machine learning},
  journal = {arXiv preprint arXiv:2507.20422},
  year    = {2025},
  url     = {https://arxiv.org/abs/2507.20422},
}
```

#### Other Relevant Papers:

1. **Quantum Autoencoder for Molecular Representation** (arXiv:2505.01875)
   - MolQAE: Maps SMILES to quantum states
   - Preserves structural information
   
2. **Quantum Molecular Structure Encoding Definition**
   - Family of quantum representations preserving molecular/geometric/symmetry info
   - Source: emergentmind.com, quantumzeitgeist

3. **Bond Order Decomposition** (Springer, 2013)
   - Theoretical foundations of bond multiplicities
   - Quantum-mechanical interpretation

---

## Search 2: Quantum Kernel Drug Discovery

**Query:** "quantum kernel machine learning molecular similarity drug discovery chemistry"  
**Date:** 28 August 2026  
**Results:** 10 papers

### Key Findings:

#### ⭐ HIGHLY RELEVANT:

1. **Q2SAR: Quantum Multiple Kernel Learning (arXiv:2506.14920, 2607.11701)**
   - QMKL framework for QSAR modeling
   - AUC 0.8750 vs classical 0.8037
   - Outperforms gradient boosting
   
**Citation:**
```bibtex
@Article{Q2SAR2025,
  author  = {[Authors TBD]},
  title   = {A Quantum Multiple Kernel Learning Approach for Drug Discovery},
  journal = {arXiv preprint arXiv:2506.14920},
  year    = {2025},
  url     = {https://arxiv.org/abs/2506.14920},
}
```

2. **Morgan-Anchored Quantum Kernel (arXiv:2606.21213)**
   - Quantum kernel adds similarity info to Morgan/Tanimoto
   - Small-data ligand classification
   
3. **QKDTI: Quantum Kernel Drug-Target Interaction (Nature Sci Rep 2025)**
   - 94.21% accuracy on DAVIS, 99.99% on KIBA
   - Significantly outperforms classical models
   
**Citation:**
```bibtex
@Article{QKDTI2025,
  author  = {[Authors TBD]},
  title   = {{QKDTI}: A quantum kernel based machine learning model for drug target interaction prediction},
  journal = {Scientific Reports},
  year    = {2025},
  doi     = {10.1038/s41598-025-07303-z},
  url     = {https://www.nature.com/articles/s41598-025-07303-z},
}
```

4. **Quantum Neural Networks for Drug Discovery (arXiv:2409.15645)**
   - Gate-based quantum computers
   - Review of potential in chemistry

5. **Robust Quantum Reservoir Computing (arXiv:2412.06758)**
   - Molecular property prediction
   - Quantum ML in biomedical research

---

## Search 3: Barren Plateaus & Gradient Vanishing

**Query:** "barren plateaus variational quantum algorithms gradient vanishing quantum neural networks"  
**Date:** 28 August 2026  
**Results:** 10 papers

### Key Findings:

#### ⭐ CRITICAL FOR DISCUSSION:

1. **Cost Function Dependent Barren Plateaus (arXiv:2001.00550)**
   - Global observables → exponentially vanishing gradients
   - Even with shallow circuits
   
2. **Survey of Barren Plateau Mitigation (arXiv:2406.14285)**
   - Comprehensive methods review
   - Flat plateaus in loss landscape
   - Challenge for hybrid quantum-classical algorithms

**Citation:**
```bibtex
@Article{BarrenPlateauSurvey2024,
  author  = {[Authors TBD]},
  title   = {A Survey of Methods for Mitigating Barren Plateaus for Parameterized Quantum Circuits},
  journal = {arXiv preprint arXiv:2406.14285},
  year    = {2024},
  url     = {https://arxiv.org/abs/2406.14285},
}
```

3. **Initialization Strategy (arXiv:1903.05076)**
   - Random initialization → barren plateaus
   - Exponential scaling with qubits
   
4. **Barren Plateaus Amplified by Qudit Dimension (arXiv:2405.08190)**
   - VQA obstacles
   - Vanishing gradient problem

5. **Equivalence: Kernel Concentration ↔ Barren Plateaus (arXiv:2501.07433)**
   - Exponential concentration in quantum kernels
   - Related to BP in variational algorithms
   
6. **Investigating & Mitigating BPs (arXiv:2407.17706)**
   - Gradient variance vanishes with qubits/layers
   - Hinders scaling on large datasets

7. **Higher Order Derivatives (arXiv:2008.07454)**
   - Can Hessian help escape BP?
   - Gradient vanishes exponentially

8. **PDE-Constrained Loss Functions (arXiv:2604.09957)**
   - Mitigation via physics-informed loss
   - Fundamental obstacle to VQC training

---

## Search 4: Quantum Advantage & NISQ Applications

**Query:** "quantum advantage quantum machine learning near-term NISQ devices chemistry applications"  
**Date:** 28 August 2026  
**Results:** 10 papers

### Key Findings:

#### ⭐ CONTEXT FOR INTRODUCTION/DISCUSSION:

1. **Quantum ML: Where Can Quantum Help? (arXiv:2507.08379)**
   - Significant potential for quantum chemistry, sensing
   - Real-world utility contingent on overcoming hurdles
   
2. **Towards Quantum Advantage in Chemistry (arXiv:2512.13657)**
   - Molecular simulations as leading candidates
   - Surpass classical in accuracy or scale
   
**Citation:**
```bibtex
@Article{QuantumAdvantageChemistry2025,
  author  = {[Authors TBD]},
  title   = {Towards Quantum Advantage in Chemistry},
  journal = {arXiv preprint arXiv:2512.13657},
  year    = {2025},
  url     = {https://arxiv.org/abs/2512.13657},
}
```

3. **Framework for Quantum Advantage (arXiv:2506.20658)**
   - Quantum + HPC platforms
   - Chemistry, materials, optimization

4. **Quantum Computing for Generative Chemistry (PubMed:37331692)**
   - Near-term applications in drug discovery
   - Practical early applications

5. **Utility-Scale Quantum Chemistry (arXiv:2603.19081)**
   - Beyond strongly correlated molecules
   - Broader perspective on utility

6. **Advances in NISQ Era (MDPI Entropy 2027)**
   - Hybrid quantum-classical computing
   - Diverse domains: chemistry, materials, ML

7. **Quantum Advantage in Computational Chemistry? (arXiv:2508.20972)**
   - Decades of promises
   - Critical assessment

8. **McKinsey Report on Quantum in Chemicals**
   - $200B-$500B potential value by 2035
   - Cost reductions, faster R&D, new products

---

## Search 5: Coulomb Matrix & Molecular Descriptors

**Query:** "Coulomb matrix molecular representation machine learning quantum chemistry descriptors"  
**Date:** 28 August 2026  
**Results:** 10 papers

### Key Findings:

#### ⭐ ESSENTIAL BACKGROUND:

1. **Quantum Chemical Roots of ML Descriptors (arXiv:2207.03599)**
   - Molecular descriptor = feature vector
   - Assessing similarity
   - Coulomb matrix foundations
   
**Citation:**
```bibtex
@Article{QuantumChemicalRoots2022,
  author  = {[Authors TBD]},
  title   = {Quantum chemical roots of machine-learning molecular similarity descriptors},
  journal = {arXiv preprint arXiv:2207.03599},
  year    = {2022},
  url     = {https://arxiv.org/abs/2207.03599},
}
```

2. **Molecular Reps of Quantum Circuits (arXiv:2503.05955)**
   - QSVMs characterized by fingerprints
   - Coulomb matrices, Gershgorin circles
   
3. **QMSE with Coulomb-Adjacency Matrix (arXiv:2507.20422)**
   - Same as Search 1 primary paper
   - Hybrid Coulomb-adjacency encoding

4. **Wasserstein Metric for QML (arXiv:2001.11005)**
   - Adjacency "Coulomb" matrix distances
   - Kernel ridge regression
   - Improved training efficiency

5. **Coulomb Matrices for Molecular ML (Tutorial)**
   - Introduced by Rupp et al. 2012
   - Excellent starting point for descriptors
   - Newer methods superseded it

6. **Atomization Energy Prediction (Springer 2019)**
   - Coulomb matrix + Bayesian neural networks
   - Fundamental for compound design

---

## Summary of Key Papers to Add

### Definitely Add (High Priority):

1. ✅ Boy et al. 2025 — QMSE (arXiv:2507.20422)
2. ✅ Q2SAR — Quantum kernel drug discovery (arXiv:2506.14920, 2607.11701)
3. ✅ QKDTI — Nature Sci Rep 2025 quantum kernel DTI
4. ✅ Barren plateaus survey (arXiv:2406.14285)
5. ✅ Towards quantum advantage in chemistry (arXiv:2512.13657)
6. ✅ Quantum chemical roots of descriptors (arXiv:2207.03599)
7. ✅ Initialization strategy for barren plateaus (arXiv:1903.05076)
8. ✅ Cost-function dependent BPs (arXiv:2001.00550) — this is Cerezo et al. 2021, already have it!

### Consider Adding (Medium Priority):

9. Morgan-anchored quantum kernel (arXiv:2606.21213)
10. Quantum neural networks for drug discovery review (arXiv:2409.15645)
11. Framework for quantum advantage (arXiv:2506.20658)
12. Wasserstein metric for QML (arXiv:2001.11005)
13. Higher-order derivatives & BP (arXiv:2008.07454)
14. PDE-constrained loss mitigation (arXiv:2604.09957)

### Optional (Context/Background):

15. Utility-scale quantum chemistry (arXiv:2603.19081)
16. Quantum advantage assessment (arXiv:2508.20972)
17. NISQ advances review (MDPI Entropy)
18. Molecular reps of quantum circuits (arXiv:2503.05955)

---

## Missing / To Search Further:

1. **Havlíček et al. 2019** — Already in bibliography ✅
2. **Schuld & Killoran 2019** — Already in bibliography ✅
3. **McClean et al. 2018** — Already in bibliography ✅
4. **Rupp et al. 2012 Coulomb Matrix** — Already in bibliography ✅
5. **Original BondOrderMatrix paper** — May be in Boy et al. GitHub repo
6. **Molecular fingerprints review** — Rogers 2010 already included ✅
7. **Antimalarial resistance papers** — Already covered by P1 citations

---

## Action Items:

1. ✅ Download full text PDFs for key papers (arXiv links above)
2. ⏳ Extract author names, exact titles, dates from PDFs
3. ⏳ Create complete BibTeX entries
4. ⏳ Verify DOIs for published versions (check if arXiv papers got published)
5. ⏳ Cross-reference with existing bibliography to avoid duplicates
6. ⏳ Organize by topic in bibliography file

---

**Status:** Raw search complete, ready for bibliography integration

