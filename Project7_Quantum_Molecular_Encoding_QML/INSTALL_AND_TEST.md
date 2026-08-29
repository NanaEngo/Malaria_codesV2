# P7 Installation and Testing Guide

**Date:** 28 August 2026  
**Purpose:** Install hybrid QML environment and verify all components work

---

## 📦 Installation

### Step 1: Create Conda Environment

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML

# Create environment (includes PyTorch, PennyLane, Qiskit, RDKit)
conda env create -f environment.yml

# This will take 5-10 minutes
```

**Expected output:**
```
Collecting package metadata...
Solving environment...
Preparing transaction...
Executing transaction...
...
# To activate this environment, use:
#   conda activate malaria_qml_hybrid
```

---

### Step 2: Activate Environment

```bash
conda activate malaria_qml_hybrid
```

**Verify activation:**
```bash
echo $CONDA_DEFAULT_ENV
# Should print: malaria_qml_hybrid
```

---

### Step 3: Verify Setup

```bash
# Run setup verification script
bash scripts/verify_setup.sh
```

**Expected output:**
```
======================================================================
P7 Setup Verification
======================================================================

1. Checking conda environment...
   ✅ Environment 'malaria_qml_hybrid' exists

2. Checking if environment is activated...
   ✅ Environment is activated

3. Checking Python packages...
   ✅ PyTorch 2.1.0
   ✅ PennyLane 0.34.0
   ✅ Qiskit 1.0.0
   ✅ RDKit 2023.3.1
   ✅ scikit-learn 1.3.0

4. Checking P7 scripts...
   ✅ scripts/p7_quantum_layers.py
   ✅ scripts/p7_training_utils.py
   ✅ scripts/p7_hybrid_vqc.py
   ✅ scripts/p7_data_preparation.py
   ✅ scripts/test_hybrid_implementation.py

5. Checking P7 modules can be imported...
   ✅ p7_quantum_layers imports successfully
   ✅ p7_training_utils imports successfully

======================================================================
✅ Setup verification complete!
======================================================================
```

---

## 🧪 Testing

### Step 4: Run Component Tests

```bash
# Run comprehensive test suite
python scripts/test_hybrid_implementation.py
```

This will test:
1. **Quantum layers** (VQC, QuantumFeatureExtractor, HybridQNN)
2. **Training utilities** (training loop, evaluation, logging)
3. **Model I/O** (save/load checkpoints)
4. **Metrics logging** (JSON provenance)
5. **End-to-end integration** (full pipeline)

**Expected output:**
```
======================================================================
P7 HYBRID QML IMPLEMENTATION TEST SUITE
======================================================================

Verifying all components before Phase 1 execution...

======================================================================
Test 1: Quantum Layers
======================================================================

1.1 VQCLayer...
  ✅ Forward pass OK: torch.Size([2, 4]) → torch.Size([2, 4])
  ✅ Gradient OK: norm = 0.123456

1.2 QuantumFeatureExtractor...
  ✅ Forward pass OK: torch.Size([2, 2048]) → torch.Size([2, 4])

1.3 HybridQNN (full model)...
  ✅ Forward pass OK: torch.Size([2, 2048]) → torch.Size([2, 1])
  ✅ Output range: [0.234, 0.789]
  ✅ Parameters: Total=10234, Quantum=32, Classical=10202

1.4 DualPathQuantumNet (ablation model)...
  ✅ With quantum: torch.Size([2, 2048]) → torch.Size([2, 1])
  ✅ Without quantum: torch.Size([2, 2048]) → torch.Size([2, 1])

✅ All quantum layer tests passed!

======================================================================
Test 2: Training Utilities
======================================================================

2.1 Creating dummy dataset...
  ✅ Train: 50 samples
  ✅ Val: 20 samples

2.2 Creating HybridQNN...
  ✅ Model created

2.3 Training for 3 epochs (test)...
  ✅ Training complete: 3 epochs
  ✅ Final train loss: 0.6234
  ✅ Final val AUC: 0.5678

2.4 Evaluating on validation set...
  ✅ AUC: 0.5678
  ✅ Accuracy: 0.6500
  ✅ F1: 0.6123

2.5 Checking gradient vanishing...
  ✅ Gradient status: healthy
  ✅ Gradient norm: 0.001234

✅ All training utility tests passed!

======================================================================
Test 3: Model I/O
======================================================================

3.1 Creating model...
  ✅ Quantum weights shape: (1, 4, 2)

3.2 Saving model...
  ✅ Model saved: /tmp/.../test_model.pt

3.3 Loading model...
  ✅ Model loaded successfully
  ✅ Weights match: True

✅ Model I/O tests passed!

======================================================================
Test 4: Metrics Logging
======================================================================

  ✅ Metrics saved: /tmp/.../test_metrics.json
  ✅ Metrics verified

✅ Metrics logging tests passed!

======================================================================
Test 5: End-to-End Integration
======================================================================

5.1 Creating synthetic dataset...
  ✅ Train: 80 samples, Test: 20 samples

5.2 Creating hybrid QML model...
  ✅ Model created

5.3 Training (5 epochs)...
  ✅ Training complete: 5 epochs
  ✅ Final train loss: 0.5234

5.4 Evaluating on test set...
  ✅ Test AUC: 0.6789
  ✅ Test Accuracy: 0.7000
  ✅ Test F1: 0.6543

5.5 Checking gradient behavior...
  ✅ Gradient status: healthy
  ✅ Gradient norm: 0.002345

5.6 Saving results...
  ✅ Model saved: final_model.pt
  ✅ Metrics saved: final_metrics.json

✅ End-to-end integration test passed!

======================================================================
TEST SUMMARY
======================================================================
Passed: 5/5
Failed: 0/5

======================================================================
✅ ALL TESTS PASSED!
======================================================================

🚀 System is ready for Phase 1 execution!

Next steps:
  1. Prepare data: python scripts/p7_data_preparation.py --p1-only
  2. Run Phase 1: python scripts/p7_hybrid_vqc.py --p1-set-a --qubits 4 --depth 2 --epochs 50

Expected time: ~30-60 minutes (CPU), ~10-20 minutes (GPU)
======================================================================
```

**Test duration:** ~2-5 minutes (depending on CPU speed)

---

## ✅ Success Checklist

After installation and testing, verify:

- [ ] Conda environment `malaria_qml_hybrid` created
- [ ] Environment activated (`echo $CONDA_DEFAULT_ENV` shows `malaria_qml_hybrid`)
- [ ] `verify_setup.sh` passes (all ✅)
- [ ] `test_hybrid_implementation.py` passes (5/5 tests)
- [ ] No gradient vanishing warnings
- [ ] Models can save/load correctly

If all boxes checked → **Ready for Phase 1 execution!**

---

## 🐛 Troubleshooting

### Problem: `conda: command not found`

**Solution:** Install Miniconda or Anaconda first
```bash
# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

---

### Problem: `Solving environment: failed`

**Cause:** Package conflicts or missing channels

**Solution 1:** Update conda
```bash
conda update -n base -c defaults conda
```

**Solution 2:** Try mamba (faster solver)
```bash
conda install mamba -n base -c conda-forge
mamba env create -f environment.yml
```

**Solution 3:** Install packages individually
```bash
conda create -n malaria_qml_hybrid python=3.10
conda activate malaria_qml_hybrid
conda install pytorch torchvision cpuonly -c pytorch
pip install pennylane pennylane-qiskit qiskit qiskit-aer
conda install -c conda-forge rdkit scikit-learn pandas matplotlib
```

---

### Problem: `ModuleNotFoundError: No module named 'torch'`

**Cause:** Environment not activated

**Solution:**
```bash
conda activate malaria_qml_hybrid
```

---

### Problem: `ImportError: cannot import name 'HybridQNN'`

**Cause:** Wrong directory

**Solution:**
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
python scripts/test_hybrid_implementation.py
```

---

### Problem: Tests run but show "⚠️ WARNING: Gradients vanishing"

**Diagnosis:** Quantum gradients collapsing (barren plateaus)

**Solutions:**
1. **Reduce circuit depth:** This is normal for deep circuits
   - Modify `p7_quantum_layers.py`: default `n_layers=1` instead of `n_layers=2`
2. **Change entangling gate:** Try RZZ instead of CNOT
3. **Increase learning rate:** Try `lr=0.05` instead of `lr=0.01`
4. **Use fewer qubits:** Try `n_qubits=4` (already default)

**Note:** If gradients vanish in tests but not consistently, this is OK for proof-of-concept. Monitor during Phase 1 execution.

---

### Problem: CUDA/GPU errors

**Solution:** Force CPU mode
```bash
# Edit environment.yml: change 'pytorch>=2.1.0' line to include 'cpuonly'
conda env update -f environment.yml --prune

# Or run scripts with --device cpu
python scripts/p7_hybrid_vqc.py --p1-set-a --device cpu
```

---

## 🎯 After Successful Testing

You're ready to proceed with Phase 1:

```bash
# 1. Prepare data (~1 minute)
python scripts/p7_data_preparation.py --p1-only

# 2. Optional: Run classical baseline for comparison
python scripts/p7_baseline_classical.py --p1-set-a

# 3. Run hybrid QML (main experiment)
python scripts/p7_hybrid_vqc.py --p1-set-a --qubits 4 --depth 2 --epochs 50

# Expected time: ~30-60 minutes on CPU
```

---

## 📊 What to Expect

### Phase 1 Execution Will:
1. Load P1 Set A (20 molecules)
2. Convert SMILES → ECFP4 fingerprints
3. Run LOO-CV (20 folds)
   - Each fold: train hybrid model (ECFP4 → VQC → MLP)
   - Predict on held-out molecule
   - Check gradient vanishing
4. Compute overall metrics (AUC, accuracy, F1)
5. Save results to `results/phase1_p1_set_a/hybrid_vqc/`

### Success Criteria:
✅ **No gradient vanishing** (or only occasional warnings)  
✅ **Training completes** (all 20 folds finish)  
✅ **AUC ≥ 0.60** (random: 0.50, good: ≥0.70)  
✅ **Hybrid ≥ 80% of classical** (if classical baseline run)  

### Next Actions Based on Results:
- **If successful:** Proceed to Phase 2 (P3 benchmark, ablation)
- **If gradients vanish:** Reduce depth, try different gates
- **If neutral results:** Document honest-negative, run ablation study

---

## 📝 Support

If you encounter issues not covered here:
1. Check error messages carefully
2. Review `docs/PROJECT_STRUCTURE.md` for file organization
3. Consult `QUICKSTART.md` for execution examples
4. Check conda environment: `conda list | grep -E "torch|pennylane|qiskit|rdkit"`

---

**Status:** Installation and testing guide complete ✅  
**Last updated:** 28 August 2026
