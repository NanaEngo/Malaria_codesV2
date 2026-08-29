# P7 Quickstart — Quantum Molecular Encoding for Drug Discovery

**Date:** 28 August 2026  
**Purpose:** Run quantum molecular encoding (QMSE) experiments for antimalarial activity prediction  
**Key Point:** Uses **QMSE** (BondOrderMatrix/CoulombMatrix) as molecular features, NOT classical fingerprints

---

## 🎯 What Makes This Different

**Traditional approach (P1-P5):**
```
SMILES → ECFP4 fingerprint → ML model
```

**P7 approach (Quantum molecular encoding):**
```
SMILES → QMSE Matrix → Quantum Circuit → Quantum Features → ML model
```

**Key difference:** Molecular structure is **directly encoded** into quantum states, not preprocessed into classical features.

---

## 🔬 Two Implementation Approaches

### Approach 1: QMSE + Quantum Kernel (Recommended First) ✅

Uses quantum kernel with QMSE encoding (no gradient training):

```bash
# 1. Activate environment
conda activate malaria_qml_hybrid

# 2. Prepare data
python scripts/p7_data_preparation.py --p1-only

# 3. Generate quantum circuits from QMSE
python scripts/p7_quantum_circuits.py --p1-set-a --method bond_order

# 4. Compute quantum kernel
python scripts/p7_quantum_kernel.py --p1-set-a --method bond_order

# 5. Run full comparison (QMSE kernel vs ECFP4 baseline)
python scripts/p7_phase1_poc.py --method bond_order

# Expected time: ~15-30 minutes (CPU)
```

**Pros:**
- ✅ True quantum molecular encoding (as requested)
- ✅ No gradient issues (no barren plateaus)
- ✅ Uses existing verified QMSE infrastructure
- ✅ Direct kernel comparison

**Outputs:**
- Quantum kernel Gram matrix
- UnitaryOverlap similarities
- SVM classification results
- Comparison with ECFP4 baseline

---

### Approach 2: QMSE + Hybrid VQC (Trainable Quantum Layer)

Uses QMSE as input to trainable quantum circuits:

```bash
# 1. Activate environment
conda activate malaria_qml_hybrid

# 2. Prepare data
python scripts/p7_data_preparation.py --p1-only

# 3. Run QMSE hybrid model (trainable quantum layer)
python scripts/p7_qmse_hybrid.py \
    --p1-set-a \
    --qmse-method bond_order \
    --max-atoms 30 \
    --qubits 8 \
    --depth 2 \
    --epochs 50

# Expected time: ~30-60 minutes (CPU)
```

**Pros:**
- ✅ End-to-end trainable
- ✅ Quantum layer learns optimal encoding
- ✅ More expressive than fixed kernel

**Cons:**
- ⚠️ May encounter gradient vanishing
- ⚠️ Longer training time

**Outputs:**
- Trained hybrid model
- LOO-CV predictions
- AUC/Accuracy/F1 metrics

---

## 🚀 Recommended Execution Path

### Step 1: Environment Setup (One-time)

```bash
# Create conda environment
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
conda env create -f environment.yml

# Activate
conda activate malaria_qml_hybrid

# Verify setup
bash scripts/verify_setup.sh
```

**Expected:** All ✅ (environment, packages, imports)

---

### Step 2: Prepare Data (~1 minute)

```bash
# Extract P1 Set A (20 top candidates from P1 V7)
python scripts/p7_data_preparation.py --p1-only
```

**Output:** `data/p1_set_a_20_candidates.csv`

---

### Step 3A: Run QMSE Kernel (Recommended First) (~15-30 min)

```bash
# Full QMSE kernel comparison
python scripts/p7_phase1_poc.py --method bond_order
```

**This will:**
1. Encode SMILES → BondOrderMatrix (QMSE)
2. Generate quantum circuits from QMSE
3. Compute UnitaryOverlap quantum kernel
4. Train kernel-SVM
5. Compare with ECFP4 baseline

**Expected output:**
```
=== QMSE Kernel Results ===
AUC: 0.XX
Accuracy: 0.XX
F1: 0.XX

=== ECFP4 Baseline ===
AUC: 0.XX
Accuracy: 0.XX
F1: 0.XX

Quantum advantage: ±X%
```

---

### Step 3B: Run QMSE Hybrid (Alternative) (~30-60 min)

```bash
# Trainable hybrid model
python scripts/p7_qmse_hybrid.py --p1-set-a --qmse-method bond_order
```

**This will:**
1. Encode SMILES → BondOrderMatrix (QMSE)
2. Train hybrid model (QMSE → VQC → MLP)
3. Run LOO-CV (20 folds)
4. Save trained models

**Expected output:**
```
P1 Set A — QMSE Hybrid QML
Encoded 20 molecules
Running Leave-One-Out CV (20 folds)...
  Fold 1/20: Predicted 0.543, True: 1
  ...

=== RESULTS ===
AUC: 0.XX
Accuracy: 0.XX
F1: 0.XX
```

---

## 📊 Understanding the Results

### QMSE Methods

| Method | Matrix Type | Information Encoded |
|--------|-------------|---------------------|
| **bond_order** | BondOrderMatrix | Bond topology, atomic charges, stereochemistry |
| **coulomb** | CoulombMatrix | 3D geometry, electrostatic interactions |

**Recommendation:** Start with `bond_order` (simpler, no 3D conformer needed)

---

### Success Criteria

#### Phase 1 (P1 Set A)
- ✅ QMSE matrices generated successfully
- ✅ Quantum circuits created
- ✅ Training completes (all folds)
- ✅ AUC ≥ 0.60 (random: 0.50, good: ≥0.70)
- ✅ Comparable or better than ECFP4 baseline

#### Quantum Advantage
- **Positive:** QMSE kernel > ECFP4 baseline
- **Neutral:** QMSE kernel ≈ ECFP4 baseline (still valid for dissertation)
- **Negative:** QMSE kernel < ECFP4 baseline (document as honest-negative)

---

## 🔧 Troubleshooting

### Problem: "Module 'qmse_lib' not found"

**Solution:**
```bash
# Ensure you're in the P7 directory
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML

# Check if qmse_lib exists
ls -la scripts/qmse_lib/
```

---

### Problem: "Molecule has X atoms, exceeds max_atoms=30"

**Solution:** Increase `--max-atoms`:
```bash
python scripts/p7_qmse_hybrid.py --p1-set-a --max-atoms 50
```

---

### Problem: Gradients vanishing (Approach 2 only)

**Solution 1:** Reduce circuit depth
```bash
python scripts/p7_qmse_hybrid.py --p1-set-a --depth 1
```

**Solution 2:** Change entangling gate
```bash
# Edit p7_qmse_hybrid.py: entangling='rzz' instead of 'cnot'
```

**Solution 3:** Use Approach 1 (kernel) instead
```bash
# No gradient training needed
python scripts/p7_phase1_poc.py --method bond_order
```

---

## 📂 Output Files

### Approach 1 (Kernel)
```
results/phase1_p1_set_a/qmse_kernel/
├── quantum_kernel_gram_matrix.npy
├── unitary_overlap_similarities.npy
├── svm_results.json
└── comparison_vs_ecfp4.json
```

### Approach 2 (Hybrid)
```
results/phase1_p1_set_a/qmse_bond_order/
├── results.json
├── model_fold_00.pt
├── model_fold_01.pt
└── ...
```

---

## 🎯 Next Steps After Phase 1

### If Successful
1. **Expand to P3 benchmark** (19,849 molecules)
   ```bash
   python scripts/p7_data_preparation.py --p3-only
   python scripts/p7_phase1_poc.py --p3-benchmark --method bond_order
   ```

2. **Ablation studies** (compare QMSE methods)
   ```bash
   # BondOrderMatrix
   python scripts/p7_phase1_poc.py --method bond_order
   
   # CoulombMatrix
   python scripts/p7_phase1_poc.py --method coulomb
   
   # Compare
   python scripts/p7_ablation_comparison.py
   ```

3. **Write manuscript** using P1-P5 template

---

### If Neutral/Negative Results
1. **Document as honest-negative** (still valid for dissertation)
2. **Analyze failure modes** (molecule size, circuit depth, encoding method)
3. **Compare with P3 quantum kernel results** (QKS from P3)
4. **Discuss in dissertation** (when quantum encoding helps vs doesn't)

---

## 📚 Key Differences from Original Scripts

| Original (p7_hybrid_vqc.py) | Revised (p7_qmse_hybrid.py) |
|----------------------------|----------------------------|
| Uses ECFP4 fingerprints | Uses QMSE matrices |
| Input: (batch, 2048) | Input: (batch, n_atoms, n_atoms) |
| Classical feature → Quantum | Molecular structure → Quantum |
| `smiles_to_ecfp4()` | `smiles_to_qmse_bond_order()` |

**Bottom line:** The revised approach properly uses quantum molecular encoding as the foundation, as you requested.

---

## 🚦 Status Indicators

### ✅ Ready to Run
- Environment created (`malaria_qml_hybrid`)
- All dependencies installed
- `verify_setup.sh` passes

### 🏃 Currently Running
- Data preparation completed
- Experiment in progress (see terminal output)

### ✅ Complete
- Results saved in `results/`
- Metrics logged in JSON
- Ready for manuscript writing

---

**Next:** Activate environment and run Step 2 (data preparation)!
