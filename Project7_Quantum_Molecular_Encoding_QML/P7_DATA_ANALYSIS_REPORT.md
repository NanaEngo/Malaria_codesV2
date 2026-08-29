# P7 Data Analysis Report — Quantum Molecular Encoding

> **Règle de workflow (permanente) : DAR avant manuscrit.** Toute modification de données, de résultats, de paramètres ou de protocole est tracée dans ce rapport AVANT toute édition du manuscrit ou du SM. Le manuscrit ne cite que des valeurs/statuts déjà reportés ici (source de vérité). En cas de divergence, le DAR fait foi et le manuscrit est corrigé ensuite. Cette règle s'applique à tous les projets (P1–P7) via leurs DAR respectifs et AGENTS.md.

**Scope:** Project 7 only — true quantum machine learning via molecular structure encoding  
**Created:** 28 August 2026  
**Status:** Project initialization; no canonical results yet

## 1. Executive Status

| Phase | Status | Key Result |
|---|---|---|
| **P7.1 Setup** | IN_PROGRESS | Environment configuration, data preparation, baseline validation |
| **P7.2 Phase 1 (P1 Set A)** | PENDING_INPUTS | Proof-of-concept: 20 candidates, LOO-CV, QML vs. ECFP4 |
| **P7.3 Phase 2 (P3 Benchmark)** | PENDING_INPUTS | 19,849 molecules, 5-fold CV, comparison to P3 canonical baselines |
| **P7.4 Phase 3 (External)** | PENDING_INPUTS | 122K asexual dataset (sampled), scaffold generalization |
| **P7.5 Hardware Validation** | PENDING_INPUTS | IBM Quantum execution, noise mitigation |
| **P7.6 Manuscript** | NOT_COMPUTED | JCIM-format article, Supporting Information |

## 2. Scientific Question and Hypothesis

**Question:** Can quantum molecular structure encoding (QMSE) improve antimalarial activity prediction compared to classical fingerprints and quantum-inspired methods?

**Hypothesis:** Direct encoding of molecular graph topology (bond orders, atomic charges, stereochemistry) into parameterized quantum circuits will capture structural features that classical fingerprints miss.

**Critical distinction from P3:**
- **P3:** Classical features (ECFP4) → UMAP → IQPEmbedding → PennyLane simulator
- **P7:** Molecular structure → BondOrderMatrix → BondFeatureMap → IBM Quantum hardware

P3 encodes *classical fingerprints* into quantum states; P7 encodes *molecular structure directly* into quantum states.

## 3. Methodology Summary

### Molecular Encoding (Boy et al. 2025)

**BondOrderMatrix:**
- Single bond = 1, Double = 2, Triple = 3, Aromatic = 1.5
- Z-conformers: negative bond orders
- S-stereoisomers: negative diagonal elements
- Off-diagonal: Z_i × Z_j / bond_order

**CoulombMatrix:**
- Diagonal: 0.5 × Z^2.4 (atomic charge)
- Off-diagonal: Z_i × Z_j / distance (average bond lengths)

**Quantum Circuit (BondFeatureMap):**
- **Initial layer:** RX/RY/RZ rotations (angles = diagonal matrix elements)
- **Entangling layer:** RXX/RYY/RZZ two-qubit gates (angles = off-diagonal elements)
- **Parameters:** n_layers (1–3), n_atom_to_qubit (1–2), interleaving gates (CNOT/CZ/None)

**Quantum Kernel:**
K(A, B) = |⟨0|U_B† U_A|0⟩|²  
- Computed via UnitaryOverlap circuit
- SVM classifier on kernel matrix

### Datasets and Splits

| Tier | Dataset | Size | Split | Purpose |
|------|---------|------|-------|---------|
| **1** | P1 Set A | 20 | LOO-CV | Proof-of-concept, integration with P1 pipeline |
| **2** | P3 Benchmark | 19,849 | 5-fold (P3 splits) | Direct comparison to P3 baselines (ECFP4, Hybrid, QKS) |
| **3** | External Asexual | 122,572 (sampled 10K) | Scaffold 80/20 | Generalization, activity cliff analysis |

**Provenance rule:** All splits frozen before execution; hashes recorded in `data/provenance/data_manifest.json`.

### Baselines

| Baseline | Source | Metric | Status |
|---|---|---|---|
| ECFP4-RBF SVM | P3 canonical | AUC 0.9475 ± 0.0045 | CANONICAL |
| Hybrid RF (ECFP4+TFP+TNE+QKS) | P3 canonical | AUC 0.8876 ± 0.0065 | CANONICAL |
| QKS (PennyLane IQPEmbedding) | P3 external pilot | AUC 0.8385 | CANONICAL |
| ECFP4-RBF (P1 Set A) | To compute | TBD | PENDING |

### Statistical Analysis

- **Paired t-test:** QML vs. baselines across CV folds (α = 0.05)
- **Kernel target alignment:** Kernel–label correlation independent of SVM
- **ANOVA:** Ablation study (matrix type, entangling layer, depth)
- **Effect sizes:** Cohen's d for AUC differences

## 4. Provenance Rules (Aligned with P1–P6)

1. **Disjoint sets:** P1 Set A (P7), P2 Set B (MD), P2 Set C (polypharm) remain separate
2. **Freeze inputs:** SMILES, activity labels, circuit parameters, random seeds before execution
3. **Hardware provenance:** Backend name, qubit count, gate fidelity, noise model, shot count, job IDs
4. **Never fabricate:** Quantum results require IBM Quantum job IDs, circuit transpilation logs, qubit connectivity maps
5. **Explicit labels:** EXPLORATORY, PILOT, CANONICAL, NOT_COMPUTED, COMPUTED_WITH_COHORT_CONTRACT, PENDING_INPUTS
6. **Analysis ledger:** Every AUC, kernel entry, circuit fidelity → ledger entry with uncertainty and provenance
7. **No silent upgrades:** P3 results are canonical; P7 cannot retroactively improve P3 claims
8. **Honest-negative reporting:** If P7 ≈ P3 or P7 < P3, report transparently (following P3 precedent)

## 5. Expected Outcomes and Manuscript Implications

### Scenario A: Quantum advantage detected (P7 > ECFP4)
- **Evidence:** AUC improvement ≥ 0.01, p < 0.05 across CV folds
- **Mechanism hypothesis:** Structure-preserving encoding captures stereochemistry, ring strain, or 3D conformational features
- **Manuscript claim:** "Quantum molecular encoding improves antimalarial activity prediction"
- **Position:** Novel contribution beyond P3; quantum circuits provide advantage when encoding structure directly

### Scenario B: Equivalence (P7 ≈ ECFP4, honest-negative)
- **Evidence:** AUC difference < 0.01, p > 0.05
- **Mechanism hypothesis:** Classical fingerprints already capture relevant structural features for antimalarial activity
- **Manuscript claim:** "Structure-direct quantum encoding is competitive but not superior; classical methods remain effective"
- **Position:** Transparent null result; consistent with P3 honest-negative precedent

### Scenario C: Quantum underperformance (P7 < ECFP4)
- **Evidence:** AUC significantly lower, p < 0.05
- **Possible causes:** Insufficient circuit depth, NISQ hardware noise, kernel concentration, small training sets, inadequate parameter optimization
- **Manuscript claim:** "Current quantum hardware and algorithms not yet advantageous for this task; identify requirements for future advantage"
- **Position:** Methodological transparency; ablation studies identify bottlenecks; honest assessment of quantum computing readiness

**All three scenarios are scientifically valid outcomes.** The project commits to honest reporting regardless of result.

## 6. Results Summary

**Status:** Project initialized 28 August 2026. No canonical results yet.

### Phase 1: P1 Set A Proof-of-Concept (20 candidates)

| Metric | QML (BondOrderMatrix + RZZ) | ECFP4-RBF | Status |
|---|---|---|---|
| AUC (LOO-CV) | NOT_COMPUTED | NOT_COMPUTED | PENDING_INPUTS |
| Accuracy | NOT_COMPUTED | NOT_COMPUTED | PENDING_INPUTS |
| F1 | NOT_COMPUTED | NOT_COMPUTED | PENDING_INPUTS |
| Kernel target alignment | NOT_COMPUTED | N/A | PENDING_INPUTS |

**Circuit parameters:** NOT_COMPUTED  
**Provenance:** NOT_COMPUTED

### Phase 2: P3 Benchmark (19,849 molecules)

| Method | AUC (5-fold CV) | Status | Source |
|---|---|---|---|
| **Baselines (P3 canonical)** | | | |
| ECFP4-RBF | 0.9475 ± 0.0045 | CANONICAL | P3 DAR |
| Hybrid RF | 0.8876 ± 0.0065 | CANONICAL | P3 DAR |
| QKS (PennyLane) | 0.8385 | CANONICAL | P3 external pilot |
| **P7 Methods** | | | |
| QML (BondOrderMatrix + RZZ, depth 1) | NOT_COMPUTED | PENDING_INPUTS | — |
| QML (CoulombMatrix + RXX, depth 2) | NOT_COMPUTED | PENDING_INPUTS | — |
| QML (Optimized, ablation) | NOT_COMPUTED | PENDING_INPUTS | — |

**Ablation study:** NOT_COMPUTED  
**Statistical tests:** NOT_COMPUTED  
**Provenance:** NOT_COMPUTED

### Phase 3: External Validation (10K sampled from 122K asexual)

| Metric | QML | ECFP4 | Status |
|---|---|---|---|
| AUC (scaffold test split) | NOT_COMPUTED | NOT_COMPUTED | PENDING_INPUTS |
| Scaffold generalization | NOT_COMPUTED | NOT_COMPUTED | PENDING_INPUTS |
| Activity cliff detection | NOT_COMPUTED | NOT_COMPUTED | PENDING_INPUTS |

**Provenance:** NOT_COMPUTED

### Hardware Validation (IBM Quantum)

| Backend | Qubits | Gate fidelity | Shots | Job ID | Status |
|---|---|---|---|---|---|
| Aer statevector | — | Exact | — | — | PENDING |
| ibm_fez | TBD | TBD | 10,000 | NOT_COMPUTED | PENDING |
| ibm_pittsburgh | TBD | TBD | 10,000 | NOT_COMPUTED | PENDING |

**Noise mitigation:** NOT_COMPUTED  
**Fidelity analysis:** NOT_COMPUTED

## 7. Evidence Boundaries and Limitations

**Current (August 2026):**
- **No canonical results yet** — project is in setup phase
- All outcome scenarios (advantage / equivalence / underperformance) remain possible
- P7 will not claim quantum advantage without statistical evidence (paired t-test, p < 0.05, effect size)

**Anticipated limitations:**
1. **Sample size:** P1 Set A (n=20) is small; LOO-CV has high variance
2. **Computational cost:** Kernel matrices are O(n²); large cohorts require Nyström approximation or subset selection
3. **Hardware access:** IBM Quantum free tier limits runtime; statevector simulation is exact but classical
4. **Circuit depth:** NISQ hardware restricts depth; deeper circuits may improve accuracy but increase noise
5. **Activity labels:** Binary thresholding of docking scores is a proxy for bioactivity, not experimental IC₅₀/EC₅₀
6. **Generalization:** P3 benchmark is a single dataset; external validation tests scaffold generalization only

## 8. Integration with P1–P6 and Thesis

### Cross-Project Dependencies

| Project | Provides to P7 | Status |
|---|---|---|
| **P1** | Set A (20 candidates), SMILES, docking scores, target structures | CANONICAL |
| **P3** | Benchmark cohort (19,849), activity labels, baseline AUCs, splits | CANONICAL |
| **P2** | Set C (17 candidates) — must remain disjoint from P7 | CANONICAL |
| **Quantum_malaria_codes/** | QMSE library (BondOrderMatrix, BondFeatureMap, UnitaryOverlap) | AVAILABLE |

### Thesis Integration (My_PhD_Thesis/)

**Chapter 3 (Tools and Methods):**
- Section 3.5: Quantum Machine Learning Methods (new section)
  - 3.5.1: Quantum molecular encoding (BondOrderMatrix, CoulombMatrix)
  - 3.5.2: Quantum circuits for molecular representation
  - 3.5.3: Quantum kernels and SVM classification
  - 3.5.4: IBM Quantum hardware and Qiskit framework

**Chapter 4 (Results and Discussion):**
- Section 4.7: Quantum Molecular Encoding (P7) (new section)
  - 4.7.1: Proof-of-concept on P1 Set A
  - 4.7.2: Benchmark comparison with P3 baselines
  - 4.7.3: Ablation studies and hyperparameter optimization
  - 4.7.4: External validation and scaffold generalization
  - 4.7.5: Hardware noise analysis
  - 4.7.6: Honest assessment: advantage / equivalence / limitation

**Chapter 5 (General Conclusion):**
- P7 contribution to multi-method pipeline (P1–P7)
- Position of QML in computational drug discovery: current state vs. future potential
- Comparison with P3: classical-feature vs. structure-direct quantum encoding

## 9. Next Actions

**Immediate (Week 1-2):**
1. ✅ Create P7 directory structure and README
2. ✅ Create P7 DAR template (this file)
3. ⏳ Set up Python environment (`environment.yml`, install dependencies)
4. ⏳ Clone and install `quantum-molecular-encodings` library locally
5. ⏳ Extract P1 Set A (20 candidates) to `data/p1_set_a_20_candidates.csv`
6. ⏳ Extract P3 benchmark (19,849) to `data/p3_benchmark_19849.csv` with activity labels
7. ⏳ Verify P3 5-fold splits and save to `data/splits/p3_5fold_splits.json`
8. ⏳ Implement baseline: ECFP4-RBF SVM on P1 Set A (LOO-CV)
9. ⏳ Unit tests: `test_p7_encoding.py`, `test_p7_circuits.py`

**Short-term (Week 3-4):**
10. ⏳ Implement P7 Phase 1: QML on P1 Set A (BondOrderMatrix, RZZ, depth 1)
11. ⏳ Compare to ECFP4 baseline, compute paired t-test
12. ⏳ If Phase 1 successful, proceed to Phase 2 ablation study
13. ⏳ Document all results in this DAR with provenance

**Medium-term (Week 5-8):**
14. ⏳ Phase 2: P3 benchmark cohort, compare to P3 canonical baselines
15. ⏳ Ablation study: matrix type, entangling layer, circuit depth
16. ⏳ Statistical tests: paired t-tests, ANOVA, kernel target alignment
17. ⏳ Update DAR with canonical results (CANONICAL or HONEST_NEGATIVE)

**Long-term (Week 9-11):**
18. ⏳ Phase 3: External validation (scaffold split, 10K sample)
19. ⏳ IBM Quantum hardware runs (if Phase 2 shows promise)
20. ⏳ Manuscript drafting (JCIM format, follow P1–P3 structure)
21. ⏳ Thesis integration (Chapter 3.5, Chapter 4.7)

## 10. Maintenance Rule

Keep this DAR operational and short. Long narratives, superseded plans, and detailed job logs go to `docs/archive/` or `results/*/provenance_manifest.json`. Add a dated checkpoint when a validated result changes the scientific status.

**Status checkpoints will be added here as work progresses.**

---

**Last updated:** 28 August 2026  
**Next update:** After Phase 1 (P1 Set A) completion or when first canonical result is computed
