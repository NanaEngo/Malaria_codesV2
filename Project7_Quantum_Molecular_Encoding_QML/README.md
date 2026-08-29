# Project 7 — Hybrid Quantum-Classical Deep Learning for Antimalarial Drug Discovery

**Status:** Scope defined, implementation phase (28 August 2026)  
**DAR:** `P7_DATA_ANALYSIS_REPORT.md`  
**Framework:** PennyLane + PyTorch + Qiskit  
**Integration:** Addresses P1–P6 limitations through quantum enhancement

---

## Overview

**Objective:** Develop hybrid quantum-classical deep learning models that integrate variational quantum circuits (VQC) into neural network architectures for antimalarial activity prediction.

**Key Innovation:** Quantum layers embedded in deep learning pipelines, trained end-to-end via gradient descent through quantum circuits (parameter-shift rule).

**Distinction from P3:** P3 used quantum-inspired methods (classical features → quantum encoding). P7 uses true hybrid QML (quantum circuits as trainable neural network layers).

---

## Scientific Question

Can hybrid quantum-classical neural networks improve antimalarial activity prediction compared to pure classical methods (P1–P6) and quantum-inspired approaches (P3)?

### Hypothesis

Variational quantum circuits, when integrated as trainable layers in deep learning models, can learn molecular representations that:
1. Capture features orthogonal to classical fingerprints (ECFP4)
2. Enhance graph neural network embeddings (addresses P5 limitation)
3. Enable effective phenotype-structure fusion (addresses P6 limitation)

---

## How This Addresses P1–P6 Limitations

| Project | Limitation | P7 Hybrid Solution |
|---------|-----------|-------------------|
| **P1** | Static docking scores | Hybrid model learns optimal representation via gradient descent |
| **P3** | Quantum-inspired ≠ true QML | True VQC with trainable parameters (parameter-shift rule) |
| **P5** | GNN underperformed on scaffold split (0.649 AUC) | Quantum enhancement of GNN graph-level embeddings |
| **P6** | Phenotype-structure fusion failed (0.583 < 0.636) | Quantum layer as high-dimensional fusion mechanism |
| **P2** | MD-RRS computational cost | Learn from static features without expensive MD simulations |

---

## Proposed Architectures

### Architecture 1: Quantum Feature Extractor (Phase 1 Focus)

```
Input (SMILES)
    ↓
Classical Featurizer (ECFP4 / QMSE Matrix)
    ↓
Dimension Reduction (Linear: 2048 → 4-8 features)
    ↓
Variational Quantum Circuit (VQC)
    ├─ Data encoding: RY rotations
    ├─ Trainable layers: RX/RY + CNOT entangling
    └─ Measurement: Pauli Z expectations → quantum features
    ↓
Classical MLP (64 → 32 → 1)
    ↓
Binary Classification (active / inactive)
```

**Use case:** Proof-of-concept, ablation studies, fastest iteration

---

### Architecture 2: Quantum-Enhanced GNN (Phase 2)

```
Input (SMILES)
    ↓
Molecular Graph Construction
    ↓
GNN Encoder (GIN / GAT)
    ├─ Node embeddings: atoms → 64-dim vectors
    └─ Graph pooling: global mean/max → 64-dim graph embedding
    ↓
Variational Quantum Circuit (VQC on embeddings)
    ├─ Encode 64-dim → 8-16 qubits
    ├─ Trainable VQC (depth 2-3)
    └─ Measure → quantum-enhanced embedding
    ↓
Fusion Layer [GNN features | Quantum features]
    ↓
Classical MLP (128 → 64 → 32 → 1)
    ↓
Binary Classification
```

**Use case:** Addresses P5 limitation (scaffold generalization)

---

### Architecture 3: Quantum Kernel Transfer (Baseline Comparison)

```
Stage 1: Quantum Kernel Pre-Training (n=20)
    SMILES → QMSE (BondOrderMatrix) → BondFeatureMap → UnitaryOverlap Kernel → SVM

Stage 2: Neural Network Fine-Tuning (n=19,849)
    SMILES → Classical Features → NN (initialized with kernel weights) → Fine-Tuned NN
```

**Use case:** Leverages quantum molecular encoding without quantum training; computational efficiency

---

## Experimental Design

### Phase 1: Proof-of-Concept (Week 1-2)

**Dataset:** P1 Set A (20 top candidates)  
**Architecture:** Quantum Feature Extractor (A1)  
**Baseline:** Classical MLP (same architecture, no quantum layer)  
**Validation:** Leave-one-out cross-validation  
**Metrics:** AUC-ROC, accuracy, F1, gradient norms (vanishing check)  

**Success criteria:**
- ✅ Quantum gradients do not vanish (norm > 10⁻⁴)
- ✅ Hybrid model ≥ 80% of classical MLP performance
- ✅ Ablation shows quantum layer contributes non-trivially

---

### Phase 2: Ablation Study + GNN Integration (Week 3-4)

**Dataset:** P3 benchmark (19,849 molecules, 5-fold CV)

**Ablation dimensions:**
1. Circuit depth: 1, 2, 3 layers
2. Qubit count: 4, 8, 16
3. Entangling gates: RXX, RYY, RZZ, CZ
4. Classical features: ECFP4 vs QMSE matrices
5. GNN encoder: GIN, GAT, GCN

**Comparison baselines:**
- P3 ECFP4-RBF: AUC 0.9475 ± 0.0045 (CANONICAL)
- P3 Hybrid RF: AUC 0.8876 ± 0.0065 (CANONICAL)
- P3 QKS: AUC 0.8385 (CANONICAL)

**Success criteria:**
- ✅ At least one architecture: AUC ≥ 0.85
- ✅ Quantum enhancement statistically significant (p < 0.05)
- ✅ Training time feasible (< 24 hours on GPU)

---

### Phase 3: External Validation + Scaffold Generalization (Week 5+)

**Dataset:** External asexual (122K, sampled 10K), scaffold split 80/20  
**Architecture:** Best-performing from Phase 2  
**Comparison:** P5 GNN baseline (0.649 AUC on scaffold split)  

**Success criteria:**
- ✅ AUC > 0.70 on scaffold test split
- ✅ Outperforms P5 GNN baseline
- ✅ Honest-negative reporting if no advantage

---

## Technical Stack

### Core Frameworks
- **PennyLane:** Quantum circuits with autodiff (parameter-shift rule)
- **PyTorch:** Neural networks, gradient descent, GPU acceleration
- **Qiskit:** IBM Quantum hardware backend
- **RDKit:** Molecular informatics (SMILES, fingerprints)
- **PyTorch Geometric:** Graph neural networks

### Quantum Backends
1. **Development:** `default.qubit` (PennyLane statevector simulator)
2. **Validation:** `qiskit.aer` (Qiskit Aer simulator)
3. **Hardware:** IBM Quantum (ibm_fez, ibm_pittsburgh) — if Phase 2 warrants

---

## Directory Structure

```
Project7_Quantum_Molecular_Encoding_QML/
├── README.md                           (this file)
├── P7_DATA_ANALYSIS_REPORT.md          (canonical results tracker)
├── requirements.txt                    (Python dependencies)
├── environment.yml                     (Conda environment)
│
├── scripts/                            (implementation scripts)
│   ├── p7_data_preparation.py          (extract P1/P3/External datasets)
│   ├── p7_baseline_classical.py        (MLP baseline, no quantum)
│   ├── p7_hybrid_vqc.py                [TODO] Architecture 1
│   ├── p7_hybrid_gnn_quantum.py        [TODO] Architecture 2
│   ├── p7_quantum_kernel_transfer.py   [TODO] Architecture 3
│   ├── p7_training_utils.py            [TODO] Training loops, metrics
│   ├── p7_quantum_layers.py            [TODO] PennyLane VQC definitions
│   ├── qmse_lib/                       (Boy et al. 2025 QMSE library)
│   └── EXECUTE_PHASE1.sh               (automated Phase 1 execution)
│
├── results/                            (experimental outputs)
│   ├── phase1_p1_set_a/
│   ├── phase2_p3_benchmark/
│   └── phase3_external_validation/
│
├── manuscript/                         (LaTeX source + figures)
│   └── [TBD after Phase 2 results]
│
├── tests/                              (unit tests)
│   └── [TBD]
│
└── docs/                               (documentation + archives)
    ├── P7_HYBRID_QML_SCOPE.md          (detailed scope definition)
    ├── P7_ARCHITECTURE_COMPARISON.md   (architecture trade-offs)
    ├── GETTING_STARTED.md              (installation + setup)
    ├── IMPLEMENTATION_READY.md         (execution guide)
    ├── PHASE1_COMPLETE.md              (Phase 1 summary)
    └── archive/                        (superseded documents)
```

---

## Installation

### 1. Clone Repository
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
```

### 2. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate malaria_qml_hybrid
```

### 3. Install Additional Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import pennylane as qml; import torch; print(f'PennyLane {qml.__version__}, PyTorch {torch.__version__}')"
```

---

## Quick Start (Phase 1)

### Step-by-Step Execution

```bash
# 1. Data preparation (~1 min)
python scripts/p7_data_preparation.py --p1-only

# 2. Classical baseline (~5 min)
python scripts/p7_baseline_classical.py --p1-set-a

# 3. Hybrid quantum model [TODO]
python scripts/p7_hybrid_vqc.py --p1-set-a --depth 2 --qubits 4

# Expected total: ~15 minutes on CPU
```

### Automated Execution

```bash
bash scripts/EXECUTE_PHASE1.sh
```

---

## Datasets

### Tier 1: P1 Integration (20 candidates)
- **Source:** P1 V7 Set A (top-20 MPO candidates)
- **Targets:** PfDHFR, PfCRT, PfATP4, PfClpP
- **Split:** Leave-one-out CV
- **Purpose:** Proof-of-concept, gradient vanishing check

### Tier 2: P3 Benchmark (19,849 molecules)
- **Source:** P3 canonical panel (eos80ch asexual_blood_stage)
- **Split:** Stratified 5-fold CV (same as P3)
- **Purpose:** Direct comparison to P3 baselines, ablation study

### Tier 3: External Validation (10K sample from 122K)
- **Source:** QMSE asexual hits/non-hits dataset
- **Split:** Scaffold-based 80/20
- **Purpose:** Generalization, comparison to P5 GNN baseline

---

## Provenance & Honest-Negative Commitment

Following P1–P6 standards:

1. **Disjoint sets:** P1 Set A, P2 Set B, P2 Set C remain separate
2. **Freeze inputs:** SMILES, labels, splits, random seeds before execution
3. **Never fabricate:** All results require job IDs, code hashes, timestamps
4. **Explicit labels:** CANONICAL, EXPLORATORY, PENDING, NOT_COMPUTED
5. **Honest reporting:** Report all outcomes (advantage, equivalence, underperformance)
6. **P3 baselines immutable:** P7 cannot retroactively improve P3 claims

If hybrid QML underperforms classical baselines, this will be reported transparently in DAR and manuscript.

---

## Expected Outcomes

### Scenario A: Quantum Enhancement (Target)
- Hybrid model > classical baseline (ΔAUC ≥ 0.02, p < 0.05)
- Quantum layer contributes non-trivially (ablation study)
- **Manuscript:** "Hybrid QML improves antimalarial drug discovery"

### Scenario B: Equivalence (Honest Negative)
- Hybrid model ≈ classical baseline (|ΔAUC| < 0.02)
- Quantum layer adds cost without benefit
- **Manuscript:** "Current quantum hardware not yet advantageous"

### Scenario C: Quantum Degradation (Failure Analysis)
- Hybrid model < classical baseline (gradient vanishing, noise)
- Document failure modes, identify requirements
- **Manuscript:** "Challenges in training hybrid QML models"

All outcomes are scientifically valid and will be reported transparently.

---

## Integration with Dissertation

**Thesis:** "Quantum Machine Learning Approach for Malaria Drug Discovery"

### Chapter 3 (Tools and Methods)
**New Section 3.5:** Hybrid Quantum-Classical Deep Learning
- Variational quantum circuits (VQC)
- Parameter-shift rule for quantum gradients
- Hybrid model architectures
- Training procedures (backpropagation through quantum layers)

### Chapter 4 (Results and Discussion)
**New Section 4.7:** Hybrid Quantum-Classical Models (P7)
- Proof-of-concept on P1 Set A
- Comparison with P1–P6 baselines
- Ablation study results
- Honest assessment of quantum advantage

### Chapter 5 (General Conclusion)
- P7 contribution to multi-method pipeline (P1–P7)
- Position of hybrid QML in drug discovery
- Limitations and future directions

---

## References

1. **Boy et al. (2025).** Quantum molecular structure encoding (QMSE). *Repository:* quantum-molecular-encodings
2. **Schuld et al. (2019).** Quantum machine learning with differential programming. *Phys. Rev. A*
3. **Mitarai et al. (2018).** Quantum circuit learning. *Phys. Rev. A*
4. **PennyLane Documentation.** Quantum gradients and hybrid quantum-classical models

---

## Status

- ✅ Scope defined (aligned with dissertation)
- ✅ Three architectures proposed
- ✅ Data preparation script ready
- ✅ Classical baseline script ready
- ⏳ **Next:** Implement Architecture 1 (Quantum Feature Extractor)
- ⏳ Phase 1 execution
- ⏳ Phase 2 ablation study
- ⏳ Phase 3 external validation

---

**Last updated:** 28 August 2026  
**Status:** Implementation phase — awaiting Architecture 1 implementation
