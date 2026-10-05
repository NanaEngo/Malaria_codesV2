# P7 Analysis Ledger

**Project:** Quantum Molecular Encoding for African Natural Products  
**Created:** 2026-09-24  
**Purpose:** Every number in the manuscript must trace to an entry here

---

## LED-001: ECFP4 Baseline Performance (P1 Set A, LOO-CV)

**Date:** 2026-08-31  
**Method:** ECFP4 (2048-bit, radius=2) + RBF-SVM, Leave-One-Out Cross-Validation  
**Dataset:** P1 Set A, n=17 molecules (15 inactive, 2 active)  
**Source:** `results/phase1_p1_set_a/baseline_ecfp4_loo.csv`

### Raw Numbers

| Metric | Value | Unit |
|--------|-------|------|
| **AUC-ROC** | 0.467 | dimensionless |
| **Accuracy** | 0.882 | fraction (15/17 correct) |
| **Precision** | 0.0 | (no positive predictions) |
| **Recall** | 0.0 | (no true positives detected) |
| **F1** | 0.0 | (no positive predictions) |
| **True Negatives** | 15 | molecules |
| **False Positives** | 0 | molecules |
| **False Negatives** | 2 | molecules (P1_A_000, P1_A_001) |
| **True Positives** | 0 | molecules |

### Prediction Scores (y_score)

**Active molecules (y_true=1):**
- P1_A_000: 0.138 (predicted inactive)
- P1_A_001: 0.099 (predicted inactive)

**Inactive molecules (y_true=0):**
- Range: 0.0006 to 0.272
- Mean: 0.134 ± 0.073 (SD)

### Written Interpretation

The ECFP4-RBF-SVM baseline achieved AUC = 0.467 (95% CI: not computed), which is **below random chance** (0.5). The classifier failed to identify either of the two active molecules (P1_A_000, P1_A_001), instead predicting all 17 molecules as inactive. Accuracy of 88.2% is misleading due to severe class imbalance (88.2% = 15/17 inactive baseline).

**Critical findings:**

1. **Class imbalance:** 15:2 inactive:active ratio creates a trivial majority-class baseline of 88.2% accuracy
2. **Low AUC:** Below 0.5 indicates the model performs worse than random guessing
3. **Score separation failure:** Active molecules scored 0.099–0.138, overlapping heavily with inactive range (0.0006–0.272)
4. **Small sample size:** n=17 is insufficient for reliable AUC estimation; confidence intervals would be very wide

**Possible causes:**
- **Hypothesis A:** Labels derived from docking/MPO scores may not reflect true binary activity
- **Hypothesis B:** P1 Set A molecules are structurally similar (all ANP-derived), making ECFP4 unable to discriminate
- **Hypothesis C:** SVM hyperparameters not optimized for this small, imbalanced dataset
- **Hypothesis D:** Active molecules (n=2) may be outliers, not a generalizable active class

### Caveats

1. **LOO-CV on n=17:** Each fold trains on 16 molecules, which is extremely small for SVM
2. **No confidence intervals:** With n=17 and AUC near 0.5, bootstrap CI would likely span [0.2, 0.7]
3. **Threshold issue:** Default SVM decision threshold (0.5) may be inappropriate for 15:2 imbalance
4. **No hyperparameter tuning reported:** C and gamma values unknown

### Links to Claims

- **Claim:** "ECFP4 baseline struggles on small, imbalanced ANP datasets"
- **Not suitable for:** "ECFP4 achieves X% accuracy" (misleading due to class imbalance)

---

## LED-002: Quantum Kernel Technical Demonstration (3 Molecules)

**Date:** 2026-09-02  
**Method:** BondOrderMatrix encoding + PennyLane quantum kernel  
**Dataset:** P1 Set A subset, n=3 molecules (P1_A_000, P1_A_001, P1_A_002)  
**Source:** `results/phase1_p1_set_a/quantum_kernel/quantum_kernel_bond_order_test3_metadata.json`

### Raw Numbers

| Parameter | Value | Unit |
|-----------|-------|------|
| **n_molecules** | 3 | molecules |
| **n_qubits** | 28 | qubits |
| **Kernel shape** | 3×3 | matrix |
| **Computation time** | 307.6 | seconds per quantum state |
| **Total time** | ~15 minutes | for 3×3 kernel |

### Kernel Matrix

```
K = | 1.000  1.000  1.000 |
    | 1.000  1.000  1.000 |
    | 1.000  1.000  1.000 |
```

**Note:** All kernel entries ≈ 1.0 (within numerical precision: max deviation 4×10⁻¹⁵)

### Molecular Labels

- P1_A_000: active (y=1)
- P1_A_001: active (y=1)
- P1_A_002: inactive (y=0)

### Written Interpretation

The BondOrderMatrix quantum kernel was successfully computed for a 3-molecule test subset, demonstrating **technical feasibility** of the quantum encoding pipeline. The computation required 28 qubits and ~5 minutes per kernel entry (307.6 seconds per quantum state × 3 molecules).

**Critical issue:** All kernel entries equal 1.0 within numerical precision (10⁻¹⁵), indicating the quantum states for all three molecules are **identical** or **maximally similar**. This suggests:

**Hypothesis A: Quantum circuit design problem**
- The BondFeatureMap circuit may collapse to identity for these molecules
- Entangling layers not effectively encoding molecular differences
- Circuit depth insufficient

**Hypothesis B: Molecular similarity**
- The 3 test molecules may be extremely structurally similar
- BondOrderMatrix representation maps them to nearly identical quantum states

**Hypothesis C: Numerical precision artifact**
- Kernel values so close to 1.0 may indicate a bug in kernel computation
- Expected: K(A,B) < 1.0 for distinct molecules

### Implications for Classification

A kernel matrix where K(i,j) ≈ 1.0 ∀ i,j provides **no discriminative information** for SVM:
- SVM cannot separate classes if all molecules appear identical
- Equivalent to training on constant features
- Expected classification: majority class (all predicted inactive)

### Computational Scalability

**Extrapolation to 17 molecules:**
- Kernel entries needed: 17×17 = 289 (using symmetry: 153 unique)
- Estimated time: 153 × 307.6 s ≈ **13 hours** (single-threaded)
- With parallelization (8 cores): ~1.6 hours

**Extrapolation to P3 benchmark (19,849 molecules):**
- Kernel entries: ~197 million
- Estimated time: ~**1,900 CPU-years**
- **Not feasible** without kernel approximation (Nyström, random features)

### Caveats

1. **Test subset only:** Results are not representative of full P1 Set A behavior
2. **No validation:** Kernel computation needs verification (e.g., test on known-different molecules)
3. **Circuit parameters unknown:** Depth, entangling gates, encoding scheme not documented here
4. **No comparison to classical kernel:** Need ECFP4 Tanimoto kernel on same 3 molecules

### Links to Claims

- **Claim:** "BondOrderMatrix quantum kernel is computationally feasible for small cohorts (n<50)"
- **Claim:** "Quantum encoding requires circuit optimization to capture molecular diversity"
- **Not suitable for:** "Quantum kernel outperforms classical" (insufficient evidence)

---

## LED-PENDING-001: Full Quantum Kernel (17 Molecules)

**Status:** NOT_COMPUTED  
**Required for:** Manuscript Results section, quantum vs. classical comparison

**What is needed:**

1. **17×17 quantum kernel matrix**
   - BondOrderMatrix encoding
   - Optimized quantum circuit (verify K(i,j) ≠ 1.0 for diverse molecules)
   - Computation time logged

2. **SVM classification with quantum kernel**
   - LOO-CV to match ECFP4 baseline
   - Metrics: AUC, accuracy, confusion matrix
   - Prediction scores for each molecule

3. **Statistical comparison**
   - Paired t-test: quantum AUC vs. ECFP4 AUC across 17 LOO folds
   - Effect size (Cohen's d)
   - Interpretation: advantage (p<0.05, Δ>0.01) / equivalence / underperformance

4. **Kernel target alignment**
   - Correlation between K and label similarity
   - Eigenvalue spectrum of kernel matrix
   - Effective dimensionality

**Estimated timeline:** TBD (depends on computation resources)

**Blocker:** Cannot write Results/Discussion without this data

---

## LED-PENDING-002: ANP Metadata Analysis

**Status:** PARTIAL — metadata exists in `data/p1_set_a/*_anp_metadata.csv` but not analyzed

**Required for:** ANP-centered narrative, stratified analysis

**What is needed:**

1. **ACSI distribution**
   - Mean, median, range for 17 molecules
   - Correlation with quantum kernel performance (pending LED-PENDING-001)

2. **Fsp³ distribution**
   - Mean, median, range
   - Comparison to typical drugs (Fsp³ ~ 0.3-0.4)
   - ANP classification (high Fsp³ > 0.5)

3. **Stereocenter count**
   - Total across 17 molecules
   - Correlation with kernel K(i,j) ≠ 1.0

4. **ANP class distribution**
   - How many indole alkaloids, flavonoids, quassinoids, synthetic?

**Timeline:** Can compute now (30 minutes) if metadata CSV exists

---

## LED-PENDING-003: Kernel Comparison (ECFP4 Tanimoto vs. Quantum)

**Status:** NOT_COMPUTED

**Required for:** Demonstrating quantum encoding captures different structural features

**What is needed:**

1. **ECFP4 Tanimoto kernel** on same 17 molecules
   - 17×17 kernel matrix
   - Compare to quantum kernel

2. **Kernel distance**
   - Frobenius norm: ||K_quantum - K_classical||_F
   - Correlation: Pearson r between kernel entries

3. **Visualization**
   - Heatmaps: K_quantum vs. K_classical
   - MDS/t-SNE: Quantum space vs. ECFP4 space

**Timeline:** 1 hour (if quantum kernel available)

---

## Summary: What We Have vs. What We Need

### ✅ Available Now (Can Enter Manuscript)

1. **ECFP4 baseline:** AUC = 0.467, n=17, LOO-CV
   - Honest interpretation: worse than random, class imbalance issue
   
2. **Quantum technical demo:** 3 molecules, 28 qubits, 15 min
   - Proof of feasibility, but kernel K ≈ I (all 1.0)

### ⏳ Critical Missing (Blocks Manuscript)

3. **Full 17-molecule quantum kernel + classification**
   - Need for quantum vs. classical comparison
   - Central finding depends on this

4. **Statistical comparison**
   - Paired test, effect size
   - Interpretation: advantage/equivalence/underperformance

### 📊 Important Missing (Strengthens Manuscript)

5. **ANP metadata analysis**
   - ACSI, Fsp³, stereocenters
   - ANP-stratified performance

6. **Kernel comparison**
   - Quantum vs. ECFP4 Tanimoto
   - Demonstrates encoding differences

### 🔮 Future Phases (Not Blocking)

7. P3 benchmark (19,849 molecules)
8. Ablation studies
9. IBM Quantum hardware

---

## Interpretation Rules

### Honest-Negative Precedent (P3)

Following P3's transparent reporting:
- If quantum ≈ ECFP4 (|ΔAUC| < 0.01 or p > 0.05) → report as **equivalence**
- If quantum < ECFP4 (p < 0.05) → report as **underperformance** with mechanistic analysis
- If quantum > ECFP4 (p < 0.05, Δ > 0.01) → report as **advantage** with effect size

### Class Imbalance Caveat

For 15:2 imbalance:
- Accuracy is misleading (majority baseline = 88.2%)
- AUC is appropriate metric (but n=17 gives wide CI)
- Balanced accuracy: (sensitivity + specificity) / 2
- Consider reporting: "Model achieves 88% accuracy by predicting all molecules as inactive"

---

**Last Updated:** 2026-09-24  
**Next Action:** Wait for LED-PENDING-001 (17-molecule quantum results) before drafting Results
