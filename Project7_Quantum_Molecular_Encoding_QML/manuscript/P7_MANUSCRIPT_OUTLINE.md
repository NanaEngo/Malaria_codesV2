# P7 Manuscript — Full Outline

**Date:** 28 August 2026  
**Purpose:** Comprehensive section-by-section outline before drafting  
**Pattern:** Following P1-P6 JCIM structure

---

## Provisional Title Options

**Recommended:**  
"Quantum Molecular Encoding for Antimalarial Drug Discovery: Evaluating BondOrderMatrix-Based Kernel Learning Against Classical Fingerprints"

**Alternative 1:**  
"Direct Quantum Encoding of Molecular Structure: BondOrderMatrix and Variational Quantum Circuits for Antimalarial Activity Prediction"

**Alternative 2:**  
"From Quantum-Inspired to Quantum-Native: Molecular Encoding via BondOrderMatrix for Drug Discovery"

**Key elements:** Quantum molecular encoding, BondOrderMatrix, antimalarial, comparison with classical

---

## Abstract (≤250 words)

### Structure (following P1 pattern):

**Opening question (1 sent):**  
Can quantum molecular encoding — where molecular structure is directly embedded into quantum states — improve upon classical molecular fingerprints for antimalarial activity prediction?

**What we did (2-3 sent):**  
- Applied BondOrderMatrix (QMSE) encoding to P1 Set A (20 antimalarial candidates)
- Computed UnitaryOverlap quantum kernel via simulated quantum circuits
- Compared kernel-SVM performance against ECFP4 baseline
- [OPTIONAL: Evaluated trainable hybrid VQC architecture]

**Key results (2-3 sent, with numbers):**  
- QMSE quantum kernel achieved AUC = [X.XX] vs ECFP4 AUC = [Y.YY]
- [Quantum advantage of ±Z% | Comparable performance | Honest-negative result]
- BondOrderMatrix encoding cost: [N] seconds/molecule; [faster/slower] than conformer-based methods
- [OPTIONAL: Hybrid VQC achieved AUC = [W.WW] but encountered gradient vanishing]

**Interpretation (1-2 sent):**  
- These results [support | do not support] quantum advantage for molecular encoding in this antimalarial cohort
- Quantum encoding preserved molecular topology and stereochemistry, offering [complementary | redundant] information to classical fingerprints

**Scope statement (1 sent):**  
Findings represent computational benchmarks on a focused candidate set; experimental validation and larger-scale studies are required to establish generalizability.

**TOC Graphic:** Workflow schematic (SMILES → BondOrderMatrix → Quantum Circuit → Kernel → Classification)

---

## 1. Introduction

### 1.1 Opening — The Quantum Encoding Gap (2 paragraphs)

**¶1 — Problem setup:**  
- Antimalarial drug discovery faces resistance and limited chemical diversity
- Classical molecular representations (ECFP4, Morgan fingerprints) lose structural information during featurization
- Quantum molecular encoding promises structure-direct representation
- **Gap:** Prior work used quantum-*inspired* methods on classical features (cite P3); true quantum encoding remains unexplored for malaria

**¶2 — Quantum ML landscape:**  
- Quantum kernel methods (cite: quantum kernel papers)
- Variational quantum circuits (VQC) for supervised learning
- Molecular encoding via BondOrderMatrix, CoulombMatrix (cite: Boy et al. 2025, Rupp et al.)
- **Challenge:** Computational cost, barren plateaus, unclear advantage over classical methods

### 1.2 Prior Art — From Classical to Quantum-Inspired to Quantum-Native (2 paragraphs)

**¶3 — Classical baselines (P1, P5):**  
- P1 established chemical-space expansion + ECFP4 docking (cite self)
- P5 demonstrated GNN/Transformer performance on molecular graphs (cite self)
- Classical fingerprints: fast, interpretable, but lossy encoding

**¶4 — Quantum-inspired (P3):**  
- P3 introduced Quantum Kernel Similarity (QKS) on ECFP4 features (cite self)
- QKS ≈ classical RBF kernel performance
- **Limitation:** Still operates on classical pre-computed features, not molecular structure directly

### 1.3 This Work — True Quantum Encoding (2 paragraphs)

**¶5 — Our approach:**  
- **Quantum molecular encoding:** SMILES → BondOrderMatrix → quantum circuits (no classical fingerprint intermediate)
- **Two architectures:**  
  1. Quantum kernel (UnitaryOverlap + kernel-SVM) — fixed encoding, no training
  2. Hybrid VQC (trainable quantum + classical layers) — end-to-end gradient training [OPTIONAL if not run]
- **Test cohort:** P1 Set A (20 candidates) with known docking profiles
- **Baseline:** ECFP4 + classical kernel

**¶6 — Research questions:**  
1. Does QMSE quantum kernel outperform classical ECFP4 kernel for antimalarial activity prediction?
2. Is BondOrderMatrix encoding more effective than CoulombMatrix (geometry-based)?
3. Can hybrid VQC achieve competitive performance despite gradient vanishing risks?
4. What is the computational cost trade-off?

**Honest-negative framing:**  
"We designed this study to test quantum advantage claims rigorously, with the understanding that negative or neutral results constitute valid scientific contributions documenting when and why quantum encoding does not improve classical methods."

---

## 2. Materials and Methods

### 2.1 Dataset — P1 Set A Antimalarial Candidates

**Content:**
- 20 top-ranked candidates from P1 V7 chemical-space expansion
- Selection criteria: Multi-parameter optimization (MPO 0.515–0.550), target selectivity (SI > 10)
- Molecular diversity: 92.6% ECFP4-unreachable from African-NP seeds, 69.3% scaffold recovery
- Activity labels: [Describe if available; else: "Docking scores from P1 used as proxy"]
- Data provenance: Canonical SMILES from P1 V7 candidate manifest

**Justification:**  
- Small focused cohort enables quantum simulation on classical hardware
- Known chemical-space novelty from P1 analysis
- Direct comparison with P1 docking and P5 GNN baselines

**Cross-reference:** P1 paper (self-cite), P1 V7 data repository

### 2.2 Quantum Molecular Encoding (QMSE)

#### 2.2.1 BondOrderMatrix Construction

**Mathematical definition:**
```
M[i,j] = {
    Z_i                      if i == j  (diagonal: atomic number)
    b_ij × Z_i × Z_j         if i ≠ j  (off-diagonal: bond order × charges)
}

where:
  Z_i = atomic number of atom i
  b_ij = bond order between atoms i and j
         (1 = single, 2 = double, 3 = triple, 1.5 = aromatic)
```

**Stereochemistry encoding:**
- Z-conformers: negative bond orders
- S-stereoisomers: negative diagonal elements
- **Preservation:** Molecular topology embedded in matrix structure

**Example:** Ethane (C₂H₆) — show 2×2 matrix with explanation

**Implementation:**  
- Library: `qmse_lib` (Boy et al. 2025 implementation)
- Add hydrogens: No (kept implicit for speed)
- Padding: Zero-pad to max_atoms=30 for batch processing

#### 2.2.2 CoulombMatrix (Alternative, [OPTIONAL])

**Mathematical definition:**
```
M[i,j] = {
    0.5 × Z_i^2.4            if i == j  (atomic self-energy)
    (Z_i × Z_j) / r_ij       if i ≠ j  (electrostatic interaction)
}

where r_ij = 3D distance between atoms i and j
```

**3D conformer generation:**  
- RDKit ETKDGv3
- Energy minimization: UFF force field
- **Limitation:** Conformer-dependent; slower than BondOrderMatrix

**When used:** [Specify if ablation study conducted]

### 2.3 Quantum Circuit Construction — BondFeatureMap

**Architecture:**

```
1. Data encoding layer (non-trainable):
   - Map matrix elements M[i,j] → rotation angles θ_ij
   - Encoding: θ_ij = arctan(M[i,j]) for off-diagonal
   - Apply RZ(θ_ij) gates on qubits i and j

2. Entangling layer:
   - CNOT gates between adjacent qubits (linear connectivity)
   - [Alternative: RZZ gates for hardware compatibility]

3. Measurement:
   - Pauli Z expectation values on all qubits
   - Output: n_qubits-dimensional quantum feature vector
```

**Qubit mapping:**  
- 1 qubit per atom (up to max_atoms qubits)
- Molecules with < max_atoms: zero-padding in QMSE matrix

**Quantum simulator:**  
- PennyLane `default.qubit` device
- Statevector simulation (exact, no shot noise)
- **Limitation:** Classical simulation; true quantum hardware not used

**Circuit depth:**  
- 1 data-encoding layer + [n_layers] variational layers (for hybrid VQC)
- Kernel: n_layers = 0 (fixed encoding only)

### 2.4 Quantum Kernel Method

#### 2.4.1 UnitaryOverlap Kernel

**Definition:**
```
K(x_i, x_j) = |⟨ψ(x_i)|ψ(x_j)⟩|²

where:
  |ψ(x_i)⟩ = quantum state after encoding molecule x_i
  ⟨·|·⟩ = inner product in Hilbert space
```

**Interpretation:**  
- Measures similarity in quantum feature space
- Range: [0, 1] (0 = orthogonal states, 1 = identical states)
- **Advantage:** Captures non-linear relationships via quantum superposition

**Gram matrix construction:**  
- For n molecules: compute n×n kernel matrix K
- Element K[i,j] = UnitaryOverlap(molecule_i, molecule_j)
- Symmetric, positive semi-definite (valid kernel)

#### 2.4.2 Kernel-SVM Classification

**Algorithm:**  
- Support Vector Machine with pre-computed quantum kernel
- Hyperparameters: C = [1.0 | grid-searched], kernel = 'precomputed'
- Training: scikit-learn SVC

**Cross-validation:**  
- Leave-One-Out CV (LOO-CV) for P1 Set A (20 molecules)
- Each fold: train on 19, test on 1
- Rationale: Small cohort necessitates maximum data utilization

**Baseline comparison:**  
- ECFP4 (radius=2, 2048 bits) + Tanimoto kernel + SVM
- Same CV protocol

### 2.5 Hybrid Quantum-Classical Neural Network [OPTIONAL Section]

**[Include only if hybrid VQC experiments were run; otherwise move to SI or omit]**

#### 2.5.1 Architecture

```
Input: QMSE matrix (max_atoms × max_atoms)
  ↓
Quantum Layer (QMSEQuantumLayer):
  - BondFeatureMap encoding (fixed)
  - n_layers variational layers (trainable weights)
  - Measurement: Pauli Z expectations
  - Output: n_qubits-dimensional quantum features
  ↓
Classical MLP:
  - Dense(n_qubits → 32, ReLU)
  - Dropout(0.2)
  - Dense(32 → 16, ReLU)
  - Dense(16 → 1, Sigmoid)
  ↓
Output: Binary classification probability
```

**Trainable parameters:**  
- Quantum: n_layers × n_qubits × 3 rotation angles
- Classical: MLP weights
- Total: ~[N] parameters

#### 2.5.2 Training Protocol

**Optimizer:** Adam (lr=[0.01 | tuned])  
**Loss:** Binary cross-entropy  
**Epochs:** 50 with early stopping (patience=10)  
**Validation:** LOO-CV (same as kernel method)

**Gradient computation:**  
- Parameter-shift rule for quantum gradients (PennyLane automatic)
- Backpropagation for classical layers

**Gradient monitoring:**  
- Track gradient norms per epoch
- Flag barren plateaus: gradient norm < 10⁻⁶

### 2.6 Evaluation Metrics

**Primary:**
- **AUC-ROC:** Area under receiver operating characteristic curve
- **Rationale:** Handles class imbalance, rank-based metric

**Secondary:**
- Accuracy: Correct predictions / total
- F1-score: Harmonic mean of precision and recall
- Confusion matrix

**Statistical significance:**  
- Permutation test (n=1000) for AUC difference
- p < 0.05 considered significant

### 2.7 Computational Environment

**Hardware:**  
- CPU: [Specify]
- RAM: [Specify]
- GPU: [If used for VQC]
- No quantum hardware (classical simulation only)

**Software:**  
- Python 3.10
- PennyLane 0.34.0 (quantum circuits)
- PyTorch 2.1.0 (hybrid VQC training)
- Qiskit 1.0.0 (circuit visualization)
- RDKit 2023.3.1 (molecular processing)
- scikit-learn 1.3.0 (SVM, metrics)

**Reproducibility:**  
- Random seeds: 42 (all experiments)
- Code: GitHub repository [LINK]
- Environment: `environment.yml` (conda)
- Data: P1 Set A manifest (DOI or repository)

### 2.8 Computational Cost Measurement

**Metrics:**
- Wall-clock time per molecule (encoding + circuit simulation)
- Total time for full experiment (LOO-CV on 20 molecules)
- Memory usage (peak RAM)

**Comparison:**  
- QMSE BondOrderMatrix vs ECFP4 computation time
- Quantum kernel vs classical kernel (Tanimoto)
- [OPTIONAL: Hybrid VQC training time]

---

## 3. Results

### 3.1 QMSE Encoding Preserves Molecular Topology

**Key findings:**
- BondOrderMatrix successfully encoded all 20 P1 Set A molecules
- Matrix size range: [min_atoms × min_atoms] to [max_atoms × max_atoms]
- Zero-padding applied to [N] molecules with < max_atoms

**Figure 2 — BondOrderMatrix Examples:**  
Panel A: Small molecule (e.g., pyrimethamine analog) — show matrix, highlight bond orders  
Panel B: Large molecule — show matrix, demonstrate stereochemistry encoding  
Panel C: Matrix element distribution (histogram)

**Validation:**  
- Diagonal elements = atomic numbers (verified)
- Off-diagonal symmetry preserved
- Bond orders match RDKit molecular graph

**Text (~1-2 paragraphs):**  
"BondOrderMatrix encoding captured molecular topology for all 20 candidates... Diagonal elements ranged from [Z_min] to [Z_max], reflecting atomic diversity... Off-diagonal elements encoded single (b=1), double (b=2), and aromatic (b=1.5) bonds, with stereochemical information preserved via sign convention..."

### 3.2 Quantum Kernel Performance on P1 Set A

**Primary result:**

| Method | AUC | Accuracy | F1 | Time/mol |
|--------|-----|----------|----|---------| 
| QMSE Quantum Kernel | [X.XX ± std] | [X.XX] | [X.XX] | [N sec] |
| ECFP4 Tanimoto Kernel | [Y.YY ± std] | [Y.YY] | [Y.YY] | [M sec] |
| **Difference** | **[±Z%]** | — | — | — |

**Statistical test:**  
- Permutation test: p = [P-VALUE]
- Significance: [YES/NO at α=0.05]

**Figure 4 — ROC Curves:**  
- QMSE quantum kernel (blue line, AUC=[X.XX])
- ECFP4 classical baseline (red line, AUC=[Y.YY])
- Diagonal reference (random, AUC=0.50)
- Shaded confidence intervals (bootstrap)

**Interpretation (~2-3 paragraphs):**

**Scenario 1 (Quantum advantage):**  
"QMSE quantum kernel outperformed the ECFP4 baseline by [Z]% (p=[P]), achieving AUC=[X.XX] vs [Y.YY]. This advantage suggests that direct quantum encoding of molecular structure captures information lost in classical fingerprint generation. The UnitaryOverlap kernel's ability to measure similarity in quantum Hilbert space may provide finer-grained discrimination between structurally similar antimalarial candidates..."

**Scenario 2 (Neutral/comparable):**  
"QMSE quantum kernel achieved AUC=[X.XX], statistically indistinguishable from the ECFP4 baseline (AUC=[Y.YY], p=[P]). This parity indicates that quantum encoding preserved molecular information without substantial loss but did not uncover latent structure invisible to classical fingerprints. The computational cost ([N] vs [M] sec/molecule) suggests that quantum encoding trades speed for theoretical elegance without empirical advantage on this cohort..."

**Scenario 3 (Honest-negative):**  
"QMSE quantum kernel underperformed the ECFP4 baseline (AUC=[X.XX] vs [Y.YY], p=[P]), challenging the hypothesis that quantum molecular encoding universally improves classical representations. This result may reflect: (1) P1 Set A's chemical diversity exceeding quantum circuit expressivity, (2) ECFP4's pre-optimization for drug-likeness capturing relevant features more efficiently, or (3) quantum kernel's sensitivity to encoding hyperparameters (qubit count, circuit depth). These findings document important boundary conditions for quantum advantage..."

### 3.3 Gram Matrix Structure Reveals Quantum Similarity Patterns

**Figure S1 (SI) — Kernel Gram Matrix Heatmaps:**  
Panel A: QMSE quantum kernel (20×20)  
Panel B: ECFP4 Tanimoto kernel (20×20)  
Panel C: Difference matrix (A - B)

**Analysis:**
- QMSE kernel sparsity: [X]% entries < 0.1
- ECFP4 kernel sparsity: [Y]% entries < 0.1
- Correlation between kernels: Pearson r=[R], Spearman ρ=[Rho]

**Text (~1 paragraph):**  
"Gram matrix visualization revealed distinct similarity structures... QMSE kernel showed [higher/lower/similar] off-diagonal entries compared to ECFP4 (mean [X.XX] vs [Y.YY]), indicating [more/less] discriminative power. The [moderate/weak/strong] correlation (r=[R]) between quantum and classical kernels suggests [complementary/redundant] information..."

### 3.4 Hybrid VQC Results [OPTIONAL — Include if experiments run]

**Training dynamics:**

| Architecture | Final AUC | Train Loss | Gradient Status | Time (total) |
|-------------|-----------|------------|-----------------|--------------|
| Hybrid VQC (n_layers=2) | [W.WW] | [L.LL] | [Healthy/Vanishing] | [T hours] |
| Classical MLP baseline | [Z.ZZ] | [L2.LL] | Healthy | [T2 hours] |

**Figure 5 — Training Curves:**  
Panel A: Loss over epochs (train/val)  
Panel B: AUC over epochs  
Panel C: Gradient norm over epochs (detect barren plateaus)

**Gradient vanishing analysis:**
- Initial gradient norm: [G_init]
- Final gradient norm: [G_final]
- Barren plateau detected: [YES/NO]
- Mitigation: [e.g., reduced depth to n_layers=1, changed entangling gate]

**Interpretation (~2 paragraphs):**

**If successful:**  
"Hybrid VQC achieved competitive AUC=[W.WW], approaching quantum kernel performance ([X.XX]) while maintaining trainable capacity. Gradient norms remained stable above [threshold], indicating that the parameter-shift rule and shallow circuit depth (n_layers=2) successfully mitigated barren plateaus. End-to-end trainability offers potential for feature learning beyond fixed kernel methods..."

**If gradient issues:**  
"Hybrid VQC training encountered gradient vanishing after epoch [E], with gradient norms dropping below [10⁻⁶]. This barren plateau phenomenon — where gradients exponentially concentrate around zero as circuit depth increases — is a known limitation of variational quantum algorithms. Despite architectural tuning (reducing depth, changing entangling gates), stable training remained elusive. These results highlight the practical challenges of gradient-based quantum ML..."

### 3.5 Ablation: BondOrderMatrix vs CoulombMatrix [If conducted]

**Comparison:**

| QMSE Method | AUC | Encoding Time/mol | 3D Required |
|-------------|-----|-------------------|-------------|
| BondOrderMatrix | [X.XX] | [N sec] | No |
| CoulombMatrix | [Y.YY] | [M sec] | Yes (conformer gen) |

**Figure 6 — Ablation Comparison:**  
ROC curves for both methods

**Analysis (~1 paragraph):**  
"BondOrderMatrix outperformed/matched CoulombMatrix (AUC [X.XX] vs [Y.YY]) while being [N/M]× faster. The performance parity/gap suggests that bond topology information in BondOrderMatrix is sufficient/insufficient for this cohort, and the added 3D geometric information in CoulombMatrix does not justify the conformer-generation overhead. For rapid quantum encoding pipelines, BondOrderMatrix is the preferred choice..."

### 3.6 Computational Cost Analysis

**Table 2 — Runtime Comparison:**

| Operation | QMSE Quantum | ECFP4 Classical | Ratio |
|-----------|-------------|----------------|-------|
| Encoding (per molecule) | [N] ms | [M] ms | [N/M]× |
| Kernel matrix (20×20) | [T1] sec | [T2] sec | [T1/T2]× |
| SVM training (LOO-CV) | [T3] sec | [T4] sec | [T3/T4]× |
| **Total pipeline** | **[Ttot1] sec** | **[Ttot2] sec** | **[Ttot1/Ttot2]×** |

**Memory usage:**  
- Peak RAM: [X] GB (quantum simulation)
- ECFP4 baseline: [Y] GB

**Scalability analysis:**  
- Quantum: O(2^n_qubits) for statevector simulation → intractable beyond ~25 qubits
- Classical: O(n_molecules × n_bits) → scales linearly

**Text (~1-2 paragraphs):**  
"Quantum kernel computation required [T1] seconds for 20 molecules ([N] ms/molecule), [T1/T2]× [slower/faster] than ECFP4 Tanimoto ([T2] seconds, [M] ms/molecule). This overhead reflects statevector simulation cost, which grows exponentially with qubit count. On true quantum hardware, this cost would [decrease to near-constant / remain prohibitive depending on circuit depth]. The computational trade-off — [better/comparable/worse] performance at [higher/lower] cost — informs practical deployment decisions..."

---

## 4. Discussion

### 4.1 Summary of Findings (1 paragraph)

"We evaluated quantum molecular encoding (QMSE: BondOrderMatrix → quantum circuits) against classical fingerprints (ECFP4) for antimalarial activity prediction on P1 Set A. The QMSE quantum kernel achieved AUC=[X.XX], [outperforming/matching/underperforming] the ECFP4 baseline (AUC=[Y.YY], p=[P]). [If hybrid VQC run: Trainable hybrid VQC achieved AUC=[W.WW] but faced gradient vanishing challenges.] Computational cost increased by [N]×, reflecting statevector simulation overhead. These results [support/challenge/nuance] quantum advantage claims for molecular encoding..."

### 4.2 Quantum Encoding Captures Molecular Topology (2 paragraphs)

**¶1 — Information preservation:**  
- BondOrderMatrix retains bond orders, atomic types, stereochemistry
- Classical fingerprints (ECFP4) lose explicit bond information via hashing
- Quantum encoding is lossless (up to discretization)
- **Trade-off:** Lossless encoding does not guarantee improved prediction if lost information is noise

**¶2 — Quantum Hilbert space advantage:**  
- UnitaryOverlap kernel operates in quantum feature space (exponentially large)
- Classical kernels restricted to explicit feature space
- **However:** P1 Set A's small size may not leverage this expressivity
- Larger datasets and deeper circuits needed to fully test hypothesis

### 4.3 Comparison with P3 Quantum-Inspired Approach (1-2 paragraphs)

**P3 (quantum-inspired):**  
- Used Quantum Kernel Similarity (QKS) on ECFP4 features
- QKS ≈ classical RBF kernel (no significant advantage)
- **Limitation:** Still operates on classical pre-computed features

**P7 (quantum-native):**  
- Uses true quantum encoding (SMILES → QMSE → quantum circuits)
- No classical fingerprint intermediate
- **Progression:** P3 → P7 represents quantum-inspired → quantum-native transition

**Result interpretation:**  
- [If P7 > P3]: "Quantum-native encoding provides advantage over quantum-inspired on classical features"
- [If P7 ≈ P3]: "Quantum advantage may require both encoding and algorithmic innovation"
- [If P7 < P3]: "Classical features may already capture relevant information efficiently"

### 4.4 Practical Limitations and Honest-Negative Framing (2-3 paragraphs)

**¶1 — Computational cost:**  
- Statevector simulation: exponential scaling with qubits
- Current limit: ~25 qubits (classical simulation)
- True quantum hardware: limited qubit count, high error rates
- **Implication:** Quantum ML is not yet practical for large-scale drug discovery

**¶2 — Barren plateaus (if hybrid VQC run):**  
- Gradient vanishing prevented stable training
- Known problem in VQC literature (McClean et al.)
- Mitigation strategies (shallow circuits, layer-wise training) only partially effective
- **Implication:** Fixed quantum kernels currently more reliable than trainable VQCs

**¶3 — Generalizability:**  
- P1 Set A is small (20 molecules), computationally prioritized (not activity-validated)
- Results may not generalize to larger, more diverse datasets
- **Honest-negative value:** Documenting when quantum encoding does not help is scientifically valid

### 4.5 Relationship to P1-P6 Ecosystem (1 paragraph)

"This work completes a progression from classical (P1, P5) to quantum-inspired (P3) to quantum-native (P7) molecular encoding for antimalarial discovery. P1 established chemical-space expansion via ECFP4; P5 demonstrated GNN/Transformer graph learning; P3 introduced QKS on classical features; P7 now tests true quantum encoding. Collectively, these projects define testable boundaries for quantum advantage: P7's [success/failure] suggests that quantum ML [offers/does not offer] near-term practical value for malaria drug discovery, while contributing fundamental insights into quantum molecular representation..."

### 4.6 Future Directions (1-2 paragraphs)

**Near-term:**
1. Scale to larger datasets (P3 benchmark: 19,849 molecules) with sampling or tensor-network methods
2. Test on quantum hardware (IBM, Rigetti) once error rates improve
3. Hybrid classical-quantum pipelines: quantum encoding + classical ML

**Long-term:**
4. Quantum advantage for specific molecular classes (e.g., macrocycles, metal complexes)
5. Quantum generative models for de novo design
6. Integration with experimental validation (synthesis + assays)

---

## 5. Conclusion (≤200 words)

**Structure:**

**¶1 — Main finding:**  
"Quantum molecular encoding via BondOrderMatrix and UnitaryOverlap kernel achieved AUC=[X.XX] on P1 Set A antimalarial candidates, [demonstrating/failing to demonstrate] advantage over classical ECFP4 (AUC=[Y.YY]). This represents the first application of true quantum encoding — where molecular structure maps directly to quantum states — for antimalarial drug discovery."

**¶2 — Significance:**  
"[If positive:] These results support continued quantum ML research for molecular encoding, particularly for datasets where classical fingerprints lose critical structural information."  
"[If neutral/negative:] These results document important boundary conditions for quantum advantage, revealing that encoding alone does not guarantee improved prediction."

**¶3 — Broader impact:**  
"As part of a PhD dissertation on 'Quantum Machine Learning Approach for Malaria Drug Discovery,' this work advances from quantum-inspired (P3) to quantum-native methods (P7). Future integration with experimental validation and quantum hardware deployment will determine whether quantum encoding translates to actionable drug discovery pipelines for malaria and beyond."

---

## Supporting Information (SI)

### SI Structure:

**S1. Extended Methods**
- S1.1 Detailed QMSE matrix construction algorithms
- S1.2 Quantum circuit gate sequences (with code)
- S1.3 Hyperparameter tuning (grid search results)
- S1.4 Statistical test details (permutation test procedure)

**S2. Additional Results**
- S2.1 Full Gram matrices (Figure S1)
- S2.2 Per-molecule results (Table S1: all 20 candidates)
- S2.3 Sensitivity analysis (circuit depth, qubit count)
- S2.4 [OPTIONAL: Hybrid VQC ablations]

**S3. Comparison with P1/P3/P5 Baselines**
- S3.1 P1 docking scores for P1 Set A
- S3.2 P3 QKS results (reproduced)
- S3.3 P5 GNN baseline (if applicable)
- S3.4 Cross-project performance table

**S4. Computational Details**
- S4.1 Hardware specifications
- S4.2 Software versions and dependencies
- S4.3 Runtime profiling (detailed breakdown)
- S4.4 Memory usage plots

**S5. Code and Data Availability**
- S5.1 GitHub repository structure
- S5.2 Reproducibility instructions
- S5.3 Dataset access (P1 Set A SMILES)
- S5.4 Example notebooks (Jupyter)

---

## Figures Plan

| # | Title | Type | Purpose |
|---|-------|------|---------|
| **1** | P7 Workflow Schematic | Diagram | Overview: SMILES → QMSE → Quantum Circuit → Kernel → SVM |
| **2** | BondOrderMatrix Examples | Multi-panel | Show matrix construction, highlight topology encoding |
| **3** | Quantum Circuit Diagram | Circuit | Illustrate BondFeatureMap architecture (data encoding + entangling) |
| **4** | ROC Curves | Plot | Primary result: QMSE vs ECFP4 performance |
| **5** | [OPTIONAL] Hybrid VQC Training | Multi-panel | Loss, AUC, gradient norms over epochs |
| **6** | [OPTIONAL] Ablation Comparison | Plot | BondOrderMatrix vs CoulombMatrix ROC |
| **TOC** | Graphical Abstract | Schematic | Journal-required visual summary |

---

## Tables Plan

| # | Title | Content |
|---|-------|---------|
| **1** | Quantum Kernel vs Classical Baseline | AUC, Accuracy, F1, p-value, time |
| **2** | Computational Cost Breakdown | Encoding, kernel, training time; memory |
| **3** | [OPTIONAL] Hybrid VQC Results | Architecture variants, performance, gradient status |
| **S1** | Per-Molecule Results | All 20 P1 Set A candidates with individual metrics |
| **S2** | Hyperparameter Grid Search | Circuit depth, qubit count, learning rate effects |

---

## Bibliography Sections (Preliminary)

### Core Citations Needed:

**Quantum ML Foundations:**
- [ ] Boy et al. 2025 — quantum-molecular-encodings (BondOrderMatrix)
- [ ] Rupp et al. — Coulomb matrix for molecular representation
- [ ] Havlíček et al. 2019 — Quantum kernel estimation
- [ ] Schuld & Killoran 2019 — Quantum ML in feature spaces
- [ ] McClean et al. 2018 — Barren plateaus in quantum neural networks

**Quantum Frameworks:**
- [ ] Bergholm et al. 2018 — PennyLane quantum ML
- [ ] Qiskit documentation — Quantum circuit simulation

**Classical Baselines:**
- [ ] Rogers & Hahn 2010 — Extended-connectivity fingerprints (ECFP)
- [ ] RDKit documentation — Molecular fingerprints

**Malaria Drug Discovery:**
- [ ] WHO 2024 — World Malaria Report (context)
- [ ] [Resistance papers cited in P1]

**Self-Citations (P1-P6):**
- [ ] P1 V7 — Chemical-space expansion, Set A definition
- [ ] P3 — Quantum-inspired kernel (QKS) on ECFP4
- [ ] P5 — GNN/Transformer baselines (if used for comparison)

**Methods:**
- [ ] scikit-learn documentation — SVM, metrics
- [ ] PyTorch documentation — Neural network training

---

## Next Steps (After Outline Approval)

1. **Literature search** — `paper-lookup` + `literature-review` for quantum ML + molecular encoding
2. **Create analysis ledger** — Template ready for results
3. **Run experiments** — Execute `p7_phase1_poc.py` to generate data
4. **Draft Methods** — Most deterministic section (known algorithms)
5. **Generate figures** — As results become available
6. **Draft Results** — Populate with ledger entries
7. **Draft Introduction/Discussion** — Contextual framing
8. **Draft Abstract** — Summary of complete story
9. **Review loops** — Independent verification passes

---

**Status:** Outline complete, awaiting user approval to proceed to L1 (Evidence Generation) or begin drafting known sections (Methods).

**Estimated manuscript length:** 6000-8000 words (main text) + 3000-4000 words (SI), following P1 pattern.

