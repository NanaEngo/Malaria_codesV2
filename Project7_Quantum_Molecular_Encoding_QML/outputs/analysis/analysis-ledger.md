# P7 Analysis Ledger

**Purpose:** Record every calculation, measurement, and result before it enters the manuscript  
**Rule:** No number appears in the manuscript without a ledger entry  
**Date started:** 28 August 2026

---

## Ledger Entry Template

```
## [ENTRY-ID] — Short descriptor

**Date:** YYYY-MM-DD  
**Analyst:** Name  
**Method:** Algorithm/tool used  
**Input:** Data source, parameters  
**Output:** Numbers WITH UNITS AND UNCERTAINTY  
**Code:** Path to script / commit hash  
**Provenance:** How to reproduce

**Interpretation (written):**  
What this result means scientifically, with caveats.

**Links to claims:**  
- C1: [Claim from project-tracking.md]
- C2: [Another claim]

**Caveats:**
- Limitation 1
- Limitation 2

---
```

---

## QMSE-001 — BondOrderMatrix Encoding of P1 Set A

**Date:** [PENDING]  
**Analyst:** [User]  
**Method:** `qmse_lib.BondOrderMatrix.compute()` via `p7_data_preparation.py`  
**Input:**  
- P1 Set A canonical SMILES (n=20)
- Parameters: add_hydrogens=False, max_atoms=30
- Source: `data/p1_set_a_20_candidates.csv`

**Output:**  
- Successfully encoded: [N]/20 molecules  
- Failed encoding: [M] molecules [list IDs if any]  
- Matrix size range: [min_atoms×min_atoms] to [max_atoms×max_atoms]  
- Mean matrix size: [X.X ± std] atoms  
- Encoding time: [T ± std] ms per molecule  
- Peak memory: [M] MB

**Code:** `scripts/p7_data_preparation.py::smiles_to_qmse_bond_order()`  
**Provenance:** Run `python scripts/p7_data_preparation.py --p1-only`, then inspect output matrices

**Interpretation:**  
BondOrderMatrix successfully encoded [all/most] P1 Set A candidates, preserving bond topology and atomic information. Matrix elements ranged from [min] to [max], reflecting [description of chemical diversity]. [If failures: Failed encodings were due to [reason], and these molecules were [excluded/handled how].]

**Links to claims:**
- C1: QMSE encodes molecular structure directly
- C7: Quantum encoding preserves topology and stereochemistry

**Caveats:**
- Implicit hydrogens only (add_hydrogens=False for speed)
- Zero-padding to max_atoms may introduce artifact similarity for small molecules
- 2D topology only (no 3D geometry unless CoulombMatrix used)

---

## QMSE-002 — Quantum Circuit Generation from QMSE

**Date:** [PENDING]  
**Method:** `p7_quantum_circuits.py --p1-set-a --method bond_order`  
**Input:**  
- QMSE matrices from QMSE-001
- Circuit parameters: n_qubits=[N], n_layers=[L], entangling='cnot'

**Output:**  
- Circuits generated: [N]/20 molecules  
- Mean circuit depth: [D ± std] gates  
- Mean qubit count: [Q ± std] (molecule-dependent)  
- Circuit generation time: [T ± std] ms per molecule

**Code:** `scripts/p7_quantum_circuits.py`  
**Provenance:** `python scripts/p7_quantum_circuits.py --p1-set-a --method bond_order`

**Interpretation:**  
Quantum circuits were successfully constructed from QMSE matrices using BondFeatureMap encoding. Circuit depth scaled with [molecular size/constant], averaging [D] gates per molecule. The encoding layer faithfully mapped bond-order matrix elements to rotation angles via arctan transformation.

**Links to claims:**
- C1: QMSE → quantum circuit pipeline
- C2: Quantum encoding methodology

**Caveats:**
- Classical simulation only (no quantum hardware)
- Circuit depth limited to avoid exponential blowup
- Statevector simulation: no noise model (overly optimistic)

---

## KERNEL-001 — UnitaryOverlap Quantum Kernel Gram Matrix

**Date:** [PENDING]  
**Method:** `p7_quantum_kernel.py --p1-set-a --method bond_order`  
**Input:**  
- Quantum circuits from QMSE-002 (n=20)
- Kernel: UnitaryOverlap K(x_i, x_j) = |⟨ψ(x_i)|ψ(x_j)⟩|²

**Output:**  
- Gram matrix K: 20×20 symmetric, positive semi-definite  
- Diagonal: K[i,i] = [mean ± std] (should be ~1.0 for normalized states)  
- Off-diagonal mean: K[i,j] = [X.XX ± std]  
- Off-diagonal range: [min, max]  
- Kernel sparsity: [P]% entries < 0.1  
- Computation time: [T] seconds total ([T/n²] sec per pair)

**Code:** `scripts/p7_quantum_kernel.py`  
**Provenance:** `python scripts/p7_quantum_kernel.py --p1-set-a --method bond_order`, outputs `results/.../quantum_kernel_gram_matrix.npy`

**Interpretation:**  
The quantum kernel Gram matrix shows [high/moderate/low] off-diagonal similarity (mean=[X.XX]), indicating [discriminative/overlapping] quantum feature representations. [Sparsity analysis suggests most molecule pairs are dissimilar in quantum feature space | Dense matrix suggests high overlap]. This kernel structure will inform SVM decision boundaries.

**Links to claims:**
- C2: Quantum kernel computes similarity in quantum feature space

**Caveats:**
- Kernel quality depends on encoding hyperparameters (n_qubits, circuit depth)
- Classical simulation limits molecule size (max ~25 qubits)
- Kernel values are inner products of quantum states, not direct measures of chemical similarity

---

## KERNEL-002 — ECFP4 Tanimoto Kernel (Baseline)

**Date:** [PENDING]  
**Method:** ECFP4 (radius=2, 2048 bits) + Tanimoto similarity  
**Input:**  
- P1 Set A SMILES (n=20)
- RDKit Morgan fingerprints

**Output:**  
- Gram matrix K_ecfp: 20×20 symmetric  
- Off-diagonal mean: [Y.YY ± std]  
- Off-diagonal range: [min, max]  
- Kernel sparsity: [Q]% entries < 0.1  
- Computation time: [T] seconds total

**Code:** `scripts/p7_baseline_classical.py` (or equivalent)  
**Provenance:** Standard RDKit fingerprint + sklearn pairwise Tanimoto

**Interpretation:**  
Classical ECFP4 Tanimoto kernel produced [comparison to quantum kernel: more/less sparse, higher/lower mean similarity]. This establishes the baseline similarity structure that quantum encoding must improve upon.

**Links to claims:**
- C4: QMSE vs ECFP4 comparison

**Caveats:**
- ECFP4 is optimized for drug-like molecules (may have unfair advantage)
- Tanimoto is inherently sparse for dissimilar molecules
- No hyperparameter tuning (radius=2 is standard but not optimal)

---

## CV-001 — Quantum Kernel LOO-CV Performance

**Date:** [PENDING]  
**Method:** Kernel-SVM with pre-computed quantum kernel + LOO-CV  
**Input:**  
- Quantum kernel Gram matrix (KERNEL-001)
- Activity labels: [describe source: docking scores, assay data, proxy]
- SVM hyperparameters: C=[value], kernel='precomputed'

**Output:**  
**Primary metrics:**
- AUC-ROC: [X.XX ± CI]  
- Accuracy: [X.XX]  
- F1-score: [X.XX]  
- Precision: [X.XX]  
- Recall: [X.XX]

**Confusion matrix:**
```
            Predicted
            Pos   Neg
Actual Pos  [TP]  [FN]
       Neg  [FP]  [TN]
```

**Per-fold results:** [Optional: detailed fold-by-fold if informative]

**Code:** `scripts/p7_phase1_poc.py::run_quantum_kernel_svm()`  
**Provenance:** `python scripts/p7_phase1_poc.py --method bond_order`

**Interpretation:**  
QMSE quantum kernel achieved AUC=[X.XX], indicating [excellent/good/moderate/poor] discriminative ability on P1 Set A. [If AUC > 0.7: The model successfully separated active/inactive candidates, suggesting quantum encoding captured relevant structural features. | If AUC ~ 0.5: Performance approached random chance, questioning quantum advantage for this cohort.] Accuracy of [X.XX] with [class imbalance description] demonstrates [appropriate/limited] generalization.

**Links to claims:**
- C3: Quantum kernel performance
- C4: Comparison with classical baseline

**Caveats:**
- Small dataset (n=20) → high variance, limited generalizability
- LOO-CV is optimistic (each fold trains on 19, but molecular diversity may be low)
- Activity labels may be proxy scores (docking), not experimental IC50
- No hyperparameter tuning (C value arbitrary)

---

## CV-002 — ECFP4 Baseline LOO-CV Performance

**Date:** [PENDING]  
**Method:** Kernel-SVM with ECFP4 Tanimoto kernel + LOO-CV  
**Input:**  
- ECFP4 kernel Gram matrix (KERNEL-002)
- Same activity labels as CV-001
- Same SVM hyperparameters for fair comparison

**Output:**  
**Primary metrics:**
- AUC-ROC: [Y.YY ± CI]  
- Accuracy: [Y.YY]  
- F1-score: [Y.YY]

**Code:** `scripts/p7_phase1_poc.py::run_classical_baseline()`  
**Provenance:** `python scripts/p7_phase1_poc.py --method bond_order --baseline ecfp4`

**Interpretation:**  
ECFP4 baseline achieved AUC=[Y.YY], establishing the classical performance ceiling. [Comparison with CV-001: Quantum kernel was [better/worse/equivalent] by [|X-Y|] AUC points.] This baseline represents well-optimized classical molecular representation with decades of community refinement.

**Links to claims:**
- C4: QMSE vs ECFP4 head-to-head comparison

**Caveats:**
- Same as CV-001 (small n, LOO optimism, proxy labels)
- ECFP4 may be overfit to drug-like molecules from historical usage

---

## STAT-001 — Statistical Significance Test (Quantum vs Classical)

**Date:** [PENDING]  
**Method:** Permutation test for AUC difference  
**Input:**  
- AUC_quantum = [X.XX] (from CV-001)
- AUC_ecfp4 = [Y.YY] (from CV-002)
- Observed difference: Δ = [X.XX - Y.YY]
- Permutations: n=1000

**Output:**  
- Null distribution: Δ_null ~ N(μ=[mean], σ=[std])  
- p-value: [P] (two-tailed)  
- Significance: [YES/NO] at α=0.05  
- Effect size: Cohen's d = [D]

**Code:** `scripts/p7_statistical_tests.py::permutation_test()`  
**Provenance:** Bootstrap/permutation from stored predictions

**Interpretation:**  
[If p < 0.05:] The quantum kernel's AUC advantage of [Δ] is statistically significant (p=[P]), providing evidence that quantum encoding captures information beyond classical fingerprints for this cohort.  
[If p ≥ 0.05:] The AUC difference of [Δ] is not statistically significant (p=[P]), suggesting quantum and classical encodings perform equivalently. This null result is scientifically valuable as an honest-negative finding.

**Links to claims:**
- C4: Quantum vs classical comparison

**Caveats:**
- Permutation test assumes exchangeability (may not hold if molecules clustered)
- Small n (20) limits statistical power (wide confidence intervals)
- Multiple comparisons: if testing multiple methods, apply Bonferroni correction

---

## COST-001 — Computational Cost Breakdown

**Date:** [PENDING]  
**Method:** Wall-clock time measurement + memory profiling  
**Input:** Same experimental runs as above

**Output:**

| Operation | QMSE Quantum | ECFP4 Classical | Ratio |
|-----------|-------------|-----------------|-------|
| **Encoding** (per molecule) | [N ± std] ms | [M ± std] ms | [N/M]× |
| **Kernel matrix** (20×20, 190 pairs) | [T1] sec | [T2] sec | [T1/T2]× |
| **SVM training** (LOO-CV, 20 folds) | [T3] sec | [T4] sec | [T3/T4]× |
| **Total pipeline** | **[Ttot1]** sec | **[Ttot2]** sec | **[Ttot1/Ttot2]×** |

**Memory:**  
- Peak RAM (quantum): [X] GB  
- Peak RAM (classical): [Y] GB

**Code:** Python `time.time()`, `memory_profiler`  
**Provenance:** Logged during experimental runs

**Interpretation:**  
Quantum kernel pipeline required [Ttot1] seconds total, [Ttot1/Ttot2]× [slower/faster] than classical ECFP4 ([Ttot2] seconds). The overhead is dominated by [encoding/kernel computation/SVM training], reflecting [statevector simulation cost/circuit depth]. This [N/M]× encoding slowdown is [acceptable/prohibitive] for practical deployment, especially considering [performance gain/lack thereof].

**Links to claims:**
- C6: Computational cost comparison (if in claims matrix)

**Caveats:**
- CPU-only (no GPU acceleration for quantum simulation)
- Wall-clock time depends on hardware (report specs)
- Classical simulation overhead; true quantum hardware would have different cost profile
- Does not include conformer generation time (for CoulombMatrix, if applicable)

---

## [OPTIONAL] VQC-001 — Hybrid VQC Training Results

**Date:** [PENDING]  
**Method:** `p7_qmse_hybrid.py --p1-set-a --qubits 8 --depth 2 --epochs 50`  
**Input:**  
- QMSE matrices (QMSE-001)
- Architecture: QMSEQuantumLayer + MLP
- Training: Adam optimizer, lr=0.01, early stopping (patience=10)

**Output:**  
**Final performance:**
- AUC-ROC: [W.WW]  
- Accuracy: [W.WW]  
- F1-score: [W.WW]  
- Training epochs: [E] (stopped early? YES/NO)

**Training dynamics:**
- Initial loss: [L_init]  
- Final loss: [L_final]  
- Best validation AUC: [W_best] (at epoch [E_best])

**Gradient analysis:**
- Initial gradient norm: [G_init]  
- Final gradient norm: [G_final]  
- Barren plateau detected: [YES/NO]  
- Mitigation applied: [e.g., reduced depth to n_layers=1]

**Code:** `scripts/p7_qmse_hybrid.py`  
**Provenance:** `python scripts/p7_qmse_hybrid.py --p1-set-a`, outputs in `results/phase1_p1_set_a/qmse_bond_order/`

**Interpretation:**  
Hybrid VQC achieved AUC=[W.WW], [comparable to/better than/worse than] quantum kernel ([X.XX]) and classical baseline ([Y.YY]). [If successful: End-to-end trainability allowed quantum layer to learn optimal encoding, providing [marginal/substantial] improvement. | If gradient issues: Training was hampered by barren plateaus, with gradient norms dropping to [G_final] by epoch [E], preventing effective learning. This highlights practical challenges of variational quantum algorithms.]

**Links to claims:**
- C5: Hybrid VQC performance
- C8: Gradient stability

**Caveats:**
- Extremely small training set (n=19 per fold) → risk of overfitting
- Gradient-based optimization sensitive to initialization (ran with seed=42 only)
- Parameter-shift rule is exact but slow (2 circuit evaluations per parameter per gradient)
- No hyperparameter tuning (learning rate, architecture, circuit depth)

---

## [OPTIONAL] ABLATION-001 — BondOrderMatrix vs CoulombMatrix

**Date:** [PENDING]  
**Method:** Same pipeline (QMSE → Kernel → SVM) with CoulombMatrix encoding  
**Input:**  
- P1 Set A SMILES
- CoulombMatrix encoding (requires 3D conformer generation)

**Output:**

| QMSE Method | AUC | Encoding Time/mol | 3D Required |
|-------------|-----|-------------------|-------------|
| BondOrderMatrix | [X.XX] | [N] ms | No |
| CoulombMatrix | [Y.YY] | [M] ms | Yes |

**Code:** `scripts/p7_phase1_poc.py --method coulomb`  
**Provenance:** Run both methods back-to-back

**Interpretation:**  
[If BondOrderMatrix ≥ CoulombMatrix:] BondOrderMatrix matched/outperformed CoulombMatrix (AUC [X.XX] vs [Y.YY]) while being [N/M]× faster. The 2D bond topology information was sufficient for this cohort, and added 3D geometric information did not improve discrimination. BondOrderMatrix is the preferred choice for rapid quantum encoding pipelines.  
[If CoulombMatrix > BondOrderMatrix:] CoulombMatrix's inclusion of 3D geometry provided [significant/modest] advantage (AUC [Y.YY] vs [X.XX]), but at the cost of [M/N]× slower encoding due to conformer generation. The trade-off depends on dataset size and performance requirements.

**Links to claims:**
- C6: QMSE method comparison

**Caveats:**
- Conformer generation adds variability (different conformers → different matrices)
- CoulombMatrix sensitive to 3D coordinate system (may need alignment)
- Only one conformer per molecule tested (could average over ensemble)

---

## VALIDATION-001 — QMSE Matrix Sanity Checks

**Date:** [PENDING]  
**Method:** Programmatic validation of BondOrderMatrix construction  
**Input:** Example molecules from P1 Set A

**Output:**  
**Checks performed:**
1. Diagonal elements = atomic numbers ✓/✗  
2. Off-diagonal symmetry: M[i,j] = M[j,i] ✓/✗  
3. Bond orders match RDKit mol graph ✓/✗  
4. Non-bonded pairs have M[i,j] = 0 ✓/✗  
5. Aromatic bonds encoded as b=1.5 ✓/✗

**Example validation:**  
- Molecule: PP-01 (from P1 Set A)
- Atoms: [list]  
- Expected bond C1-C2: single (b=1)  
- QMSE matrix M[0,1]: [value]  
- Expected: Z_C × Z_C × 1 = 6 × 6 × 1 = 36  
- Match: ✓/✗

**Code:** `scripts/tests/test_qmse_validation.py`  
**Provenance:** Unit tests

**Interpretation:**  
All [N] validation checks passed, confirming BondOrderMatrix correctly encodes molecular topology. [If failures: Discrepancies in [which check] were traced to [cause] and [resolved/documented as known limitation].]

**Links to claims:**
- C7: Quantum encoding preserves topology

**Caveats:**
- Validation on small sample (not all 20 molecules tested)
- RDKit bond-order interpretation may differ from chemical intuition (e.g., aromatic systems)

---

## Ledger Status Summary

| Entry ID | Status | Linked Claims | Ready for Manuscript |
|----------|--------|---------------|----------------------|
| QMSE-001 | 🟡 PENDING | C1, C7 | ❌ Awaiting data |
| QMSE-002 | 🟡 PENDING | C1, C2 | ❌ Awaiting data |
| KERNEL-001 | 🟡 PENDING | C2 | ❌ Awaiting data |
| KERNEL-002 | 🟡 PENDING | C4 | ❌ Awaiting data |
| CV-001 | 🟡 PENDING | C3, C4 | ❌ Awaiting data |
| CV-002 | 🟡 PENDING | C4 | ❌ Awaiting data |
| STAT-001 | 🟡 PENDING | C4 | ❌ Awaiting data |
| COST-001 | 🟡 PENDING | (optional C6) | ❌ Awaiting data |
| VQC-001 | ⚪ OPTIONAL | C5, C8 | ❌ Awaiting decision |
| ABLATION-001 | ⚪ OPTIONAL | C6 | ❌ Awaiting decision |
| VALIDATION-001 | 🟡 PENDING | C7 | ❌ Awaiting data |

**Legend:**  
🟢 COMPLETE | 🟡 PENDING | 🔴 BLOCKED | ⚪ OPTIONAL

---

## Next Ledger Actions

1. **Run experiments:** Execute `p7_phase1_poc.py` to generate QMSE-001 through STAT-001
2. **Populate entries:** Fill in all [PENDING] placeholders with actual numbers
3. **Validate interpretations:** Check that written interpretations match data
4. **Link to manuscript:** Reference ledger entry IDs in LaTeX (e.g., "AUC=\num{0.XX} \cite{ledger:CV-001}")
5. **Update status:** Mark entries 🟢 COMPLETE as data arrives

---

**Last updated:** 28 August 2026  
**Entries:** 0 complete, 9 pending, 2 optional  
**Gate status:** ❌ BLOCKED on L1 → L2 (no complete entries yet)
