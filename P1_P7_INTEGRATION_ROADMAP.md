# P1–P7 Integration Roadmap: Antimalarial Drug Discovery Pipeline

**Created:** 28 August 2026  
**Status:** P1–P6 operational; P7 initialized  
**Thesis integration:** My_PhD_Thesis/PhD_SAO_V250404.tex

## Overview

This document maps the complete antimalarial drug discovery pipeline across seven projects (P1–P7), showing how each contributes unique methodologies and how they integrate into the thesis structure.

## Project Summary Table

| Project | Method | Key Result | Thesis Chapter | Status |
|---|---|---|---|---|
| **P1** | Chemical space exploration, docking, RRS | 65,856 molecules, 20 top candidates (Set A), 4 targets | Ch 4.1–4.2 | V7 submission-ready |
| **P2** | Molecular dynamics, polypharmacology, RRS | 17 candidates (Set C), 16-system MD pilot complete | Ch 4.3–4.4 | Pilot complete |
| **P3** | Quantum-inspired representations (TFP, TNE, QKS) | Honest-negative: quantum ≈ classical (AUC 0.8876 vs 0.9475) | Ch 4.5 | Benchmarks complete |
| **P4** | Advanced Monte Carlo (MCTS) | Pareto front exploration, v12 benchmark | Ch 4.6 | Benchmark complete |
| **P5** | GNN + Transformer | ECFP4-RF dominates scaffold split; topological fusion modest | Ch 4.7 | Benchmark complete |
| **P6** | LISH-MoA structure-phenotype integration | Phenotype baseline 0.636 AUROC; structure arms pending | Ch 4.8 | Phase 2 running |
| **P7** | **Quantum machine learning (true QML via QMSE)** | **NOT_COMPUTED** | **Ch 4.9** | **Initialized** |

## P7: True Quantum Machine Learning

### Scientific Innovation

**P7 is the only project using true quantum machine learning**—encoding molecular structure directly into quantum circuits via the Boy et al. (2025) framework, not just quantum-inspired classical algorithms.

**Key distinction from P3:**
- **P3 (Quantum-Inspired):** Classical fingerprints (ECFP4) → UMAP → IQPEmbedding quantum circuit → PennyLane simulator
- **P7 (True QML):** Molecular structure → BondOrderMatrix → BondFeatureMap quantum circuit → IBM Quantum hardware

### Integration with Existing Projects

#### Data Flow

```
P1 (Chemical Space)
├── 65,856-molecule library
├── Set A: 20 top candidates (MPO 0.515–0.550)
│   └── P7 Tier 1: Proof-of-concept (20 candidates, LOO-CV)
└── 4 targets: PfDHFR, PfCRT, PfATP4, PfClpP

P3 (Quantum-Inspired Benchmark)
├── 19,849 molecules (activity-labeled)
├── Canonical baselines: ECFP4 (0.9475), Hybrid (0.8876), QKS (0.8385)
└── P7 Tier 2: Direct comparison (same 5-fold splits)

Quantum_malaria_codes/Dataset_paper/
├── 122,572 asexual hits/non-hits
├── 83,775 sexual hits/non-hits
└── P7 Tier 3: External validation (scaffold split, 10K sample)

P2 Set C (17 candidates)
└── Explicitly disjoint from P7 (independent test set, no overlap)
```

#### Methodological Relationships

**Encoding Comparison:**

| Project | Encoding Method | Type | Quantum Hardware |
|---|---|---|---|
| P3 | ECFP4 → UMAP → IQPEmbedding | Quantum-inspired (classical features) | Simulator only |
| P7 | Structure → BondOrderMatrix → BondFeatureMap | True QML (structure-direct) | IBM Quantum |

**Kernel Comparison:**

| Kernel | Computation | Space |
|---|---|---|
| ECFP4 Tanimoto (P1, P3, P5) | Classical, O(n²) bitwise | Jaccard similarity |
| RBF (P3 baseline) | Classical, O(n²) | Euclidean distance |
| QKS IQPEmbedding (P3) | Quantum circuit, O(n²) kernel entries | Hilbert space (classical features) |
| **QMSE UnitaryOverlap (P7)** | **Quantum circuit, O(n²) kernel entries** | **Hilbert space (molecular structure)** |

**Honest-Negative Precedent (P3 → P7):**

P3 established the honest-negative reporting standard:
- QKS ≈ RBF (p=0.374), no quantum advantage claimed
- Manuscript transparently reports: "quantum-inspired descriptors are complementary, not superior"

**P7 commits to the same rigor:**
- If P7 ≈ ECFP4 or P7 < ECFP4, report transparently
- All three scenarios (advantage / equivalence / underperformance) are valid scientific outcomes
- Statistical evidence required for any quantum advantage claim (paired t-test, p < 0.05)

### Thesis Integration

#### Chapter 3: Tools and Methods

**New Section 3.5: Quantum Machine Learning Methods**

```
3.5.1 Quantum Molecular Encoding
  - BondOrderMatrix: bond orders (1/2/3/1.5), stereochemistry (Z/E, R/S)
  - CoulombMatrix: atomic charges (0.5 × Z^2.4), average bond lengths
  - Comparison to classical fingerprints (ECFP4, Morgan)

3.5.2 Quantum Circuits for Molecular Representation
  - BondFeatureMap: parameterized quantum circuits
  - Initial layer: RX/RY/RZ rotations (diagonal matrix elements)
  - Entangling layer: RXX/RYY/RZZ two-qubit gates (off-diagonal)
  - Circuit depth and qubit requirements

3.5.3 Quantum Kernels and SVM Classification
  - UnitaryOverlap circuit: K(A,B) = |⟨0|U_B† U_A|0⟩|²
  - Kernel target alignment (label correlation)
  - SVM classifier on quantum kernel matrix

3.5.4 IBM Quantum Hardware and Qiskit Framework
  - Backend specifications (ibm_fez, ibm_pittsburgh)
  - Gate fidelity, noise models, shot budgets
  - Circuit transpilation and optimization
  - Comparison: statevector simulator vs. real hardware
```

#### Chapter 4: Results and Discussion

**New Section 4.9: Quantum Molecular Encoding (P7)**

```
4.9.1 Proof-of-Concept: P1 Set A (20 candidates)
  - LOO-CV results: QML vs. ECFP4 baseline
  - Circuit parameters: matrix type, entangling layer, depth
  - Kernel analysis: target alignment, eigenvalue spectrum

4.9.2 Benchmark Comparison with P3 Classical/Quantum-Inspired Methods
  - Direct comparison: same P3 cohort (19,849), same 5-fold splits
  - Baselines: ECFP4 (0.9475), Hybrid RF (0.8876), QKS (0.8385)
  - Statistical tests: paired t-tests across folds
  - Interpretation: quantum advantage / equivalence / underperformance

4.9.3 Ablation Studies and Hyperparameter Optimization
  - Matrix type: BondOrderMatrix vs. CoulombMatrix
  - Entangling layer: RXX vs. RYY vs. RZZ
  - Circuit depth: 1 vs. 2 vs. 3 layers
  - n_atom_to_qubit: 1 vs. 2 qubits per atom
  - ANOVA: effect sizes, significance

4.9.4 External Validation and Scaffold Generalization
  - 10K sample from asexual dataset (122K total)
  - Scaffold-based train/test split (80/20)
  - Activity cliff detection
  - Generalization vs. memorization

4.9.5 Hardware Noise Analysis and Mitigation
  - IBM Quantum backend characteristics
  - Gate fidelity impact on kernel accuracy
  - Noise mitigation strategies (error mitigation, post-selection)
  - Statevector (exact) vs. hardware (noisy) comparison

4.9.6 Honest Assessment: Quantum Advantage, Equivalence, or Limitation
  - Summary of findings in context of P3 honest-negative precedent
  - Mechanistic interpretation: what structural features are (or aren't) captured?
  - Hardware readiness: current NISQ limitations vs. future fault-tolerant requirements
  - Recommendations: when to use QML vs. classical methods in drug discovery
```

#### Chapter 5: General Conclusion

**Updated to include P7:**

```
5.1 Multi-Method Antimalarial Pipeline (P1–P7)
  - P1: Chemical space exploration → prioritization
  - P2: Polypharmacology and resistance circumvention
  - P3: Quantum-inspired representations (honest-negative)
  - P4: Monte Carlo optimization
  - P5: Deep learning (GNN + Transformer)
  - P6: Structure-phenotype integration
  - P7: True quantum machine learning

5.2 Position of Quantum Computing in Computational Drug Discovery
  - Current state: NISQ hardware limitations
  - P3 result: Quantum-inspired ≈ classical
  - P7 result: Structure-direct quantum encoding (TBD: advantage / equivalence / limitation)
  - Future potential: Fault-tolerant quantum computing, larger training sets
  - Realistic assessment: When will quantum advantage emerge?

5.3 Methodological Contributions
  - Honest-negative reporting standard (P3, P7)
  - Rigorous provenance tracking across P1–P7
  - Disjoint dataset management (Set A / Set B / Set C)
  - Statistical rigor: paired tests, effect sizes, ablation studies

5.4 Recommendations for Future Work
  - Experimental validation: IC₅₀/EC₅₀ for top candidates
  - Quantum hardware: track improvements in gate fidelity, qubit count
  - Hybrid workflows: quantum encoding + classical ML
  - Multi-target optimization: integrate P2 polypharmacology with P7 QML
```

## Dataset Provenance and Disjoint Sets

**Critical rule:** P1 Set A, P2 Set B (MD), and P2 Set C (polypharm) remain disjoint across all projects.

| Set | Size | Projects | Purpose | Status |
|---|---|---|---|---|
| **P1 Set A** | 20 | P1, P7 | Top candidates, QML proof-of-concept | Disjoint from P2 |
| **P2 Set B** | Historical | P2 | Parent-lead MD (superseded) | Disjoint from P1/P7 |
| **P2 Set C** | 17 | P2 | Polypharmacology, RRS, MD pilot | Disjoint from P1/P7 |
| **P3 Benchmark** | 19,849 | P3, P7 | Activity prediction, QML validation | Overlaps P1 library (post-QC) |
| **External (QMSE)** | 122K + 83K | P7 | Large-scale validation | Independent bioactivity data |

**Provenance tracking:**
- All datasets: canonical SMILES, hashes, sources, dates
- P7: Hardware job IDs, circuit transpilation logs, qubit maps, noise models
- Never merge exploratory outputs without explicit labels (CANONICAL, PILOT, NOT_COMPUTED)

## Timeline and Dependencies

### Immediate (Weeks 1-2): P7 Setup
- ✅ Create P7 directory structure, README, DAR
- ⏳ Environment setup: `conda env create -f environment.yml`
- ⏳ Install quantum-molecular-encodings library locally
- ⏳ Extract P1 Set A (20), P3 benchmark (19,849) to P7 data/
- ⏳ Verify P3 splits and baselines
- ⏳ Unit tests: encoding, circuits, kernel

### Short-term (Weeks 3-4): Phase 1 Proof-of-Concept
- ⏳ Implement ECFP4-RBF baseline on P1 Set A (LOO-CV)
- ⏳ Implement P7 QML: BondOrderMatrix + RZZ + SVM (LOO-CV)
- ⏳ Statistical test: paired t-test QML vs. baseline
- ⏳ Decision: If Phase 1 promising, proceed to Phase 2; otherwise ablate/debug

### Medium-term (Weeks 5-8): Phase 2 Benchmark
- ⏳ P3 cohort (19,849) with P7 QML
- ⏳ Compare to P3 canonical baselines (ECFP4, Hybrid, QKS)
- ⏳ Ablation study: matrix type, entangling layer, depth
- ⏳ Update P7 DAR with canonical results (CANONICAL or HONEST_NEGATIVE)

### Long-term (Weeks 9-11): Phase 3 + Manuscript
- ⏳ External validation (10K from asexual dataset)
- ⏳ IBM Quantum hardware runs (if Phase 2 shows promise)
- ⏳ Manuscript drafting: JCIM format, follow P1–P3 structure
- ⏳ Thesis integration: Chapter 3.5, Chapter 4.9, Chapter 5 updates

### Critical Path
1. **P7 Phase 1 gates P7 Phase 2** — If P1 Set A shows no signal, debug before scaling
2. **P7 Phase 2 gates hardware runs** — Only run expensive IBM Quantum if statevector shows promise
3. **P3 baselines are canonical** — P7 cannot change P3 results retroactively
4. **Thesis deadline drives manuscript priority** — Phase 3 optional if time-constrained

## Success Criteria

**Minimum viable P7:**
1. ✅ Phase 1 complete: P1 Set A LOO-CV, QML vs. ECFP4
2. ✅ Phase 2 complete: P3 benchmark, comparison to P3 baselines
3. ✅ Statistical tests: Paired t-tests, significance determination
4. ✅ Honest reporting: Advantage / equivalence / limitation clearly stated
5. ✅ Provenance: Job IDs, circuit parameters, hardware specs documented
6. ✅ Thesis integration: Chapter 3.5, Chapter 4.9 drafted

**Stretch goals:**
- Phase 3 external validation (10K+ molecules)
- IBM hardware results with noise mitigation
- Kernel approximation (Nyström) for scalability
- P6 integration: LISH-MoA multi-label QML

## References and Citations

**Core methodology:**
1. Boy, C., Altamura, E., Manawadu, D., Tavernelli, I., Mensa, S., & Wales, D. J. (2025). Encoding molecular structures in quantum machine learning. *arXiv preprint* arXiv:2507.20422.

**P1–P6 for comparison:**
2. P1 V7 manuscript: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`
3. P3 canonical results: `Project3_Quantum_Inspired_RepresentationsV2607/manuscript/LaTeX/Paper3_Quantum_InspiredV2608.tex`
4. BMAD Q1 DAR: Provenance rules and dataset documentation

**Quantum computing frameworks:**
5. Qiskit: IBM Quantum framework (https://qiskit.org/)
6. PennyLane: Hardware-agnostic quantum ML (https://pennylane.ai/)

## Contact and Maintenance

**Primary contact:** Vital (thesis author)

**Maintenance:**
- This roadmap updated at major P7 milestones
- P7 DAR (`P7_DATA_ANALYSIS_REPORT.md`) is the canonical results record
- Long narratives go to `Project7_Quantum_Molecular_Encoding_QML/docs/archive/`
- Keep AGENTS.md, DARs, and roadmaps operational and short

**Git provenance:**
- All P7 code, data, and results under version control
- Commit messages reference phases and provenance
- No silent upgrades to P1–P6 results

---

**Last updated:** 28 August 2026  
**Next update:** After P7 Phase 1 completion or first canonical result
