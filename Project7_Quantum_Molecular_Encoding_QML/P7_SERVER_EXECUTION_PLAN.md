# P7 Server Execution Plan — Step-by-Step Implementation

**Created:** 24 September 2026  
**Environment:** `malaria_qml_hybrid` (server)  
**Strategy:** Run computations on server → Transfer results to local → Write paper locally

---

## 📋 Execution Phases

### **PHASE 0: Environment Verification (10 minutes)**
Verify `malaria_qml_hybrid` environment has required packages

### **PHASE 1: Data Extraction & ANP Annotation (1 hour)**
Extract P1 Set A, P3 benchmark, compute ANP metadata (ACSI, Fsp³)

### **PHASE 2: Classical Baselines (2 hours)**
ECFP4-MLP and GNN baselines on P1 Set A (LOO-CV)

### **PHASE 3A: QFE Proof-of-Concept (1 day)**
Quantum Feature Extractor on P1 Set A (4-qubit, depth 1)

### **PHASE 3B: Architecture Comparison (2 days)**
QFE vs. Q-GNN vs. QKT on P1 Set A

### **PHASE 4: P3 Benchmark (1 week)**
Best architecture on P3 cohort (19,849 molecules, 5-fold CV)

### **PHASE 5: Ablation Studies (3 days)**
Circuit depth, qubit count, entangling gates, ANP stratification

### **PHASE 6: External Validation (3 days)**
Scaffold split on 10K sample, ANP class analysis

---

## 🚀 START HERE: Phase 0 — Environment Verification

### Step 0.1: Check Python Environment

**On server, run:**
```bash
# Activate environment
conda activate malaria_qml_hybrid

# Verify Python version
python --version  # Should be 3.9+

# Check critical packages
python -c "import pennylane; print(f'PennyLane: {pennylane.__version__}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import rdkit; print(f'RDKit: {rdkit.__version__}')"
python -c "import sklearn; print(f'scikit-learn: {sklearn.__version__}')"

# Check optional packages
python -c "import torch_geometric; print(f'PyG: {torch_geometric.__version__}')" || echo "PyG not installed"
python -c "import qiskit; print(f'Qiskit: {qiskit.__version__}')" || echo "Qiskit not installed"
```

**Expected output:**
- PennyLane: 0.32+
- PyTorch: 2.0+
- RDKit: 2023.03+
- scikit-learn: 1.3+
- PyG: 2.3+ (optional for Q-GNN)
- Qiskit: 0.44+ (optional for IBM hardware)

### Step 0.2: Install Missing Dependencies

**If any packages missing, run:**
```bash
conda activate malaria_qml_hybrid

# Core packages (if missing)
pip install pennylane pennylane-lightning
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
conda install -c conda-forge rdkit
pip install scikit-learn pandas numpy

# Optional (for Q-GNN)
pip install torch-geometric
pip install pyg-lib torch-scatter torch-sparse -f https://data.pyg.org/whl/torch-2.0.0+cpu.html

# Optional (for IBM Quantum hardware)
pip install qiskit qiskit-aer pennylane-qiskit

# Additional utilities
pip install matplotlib seaborn
```

### Step 0.3: Verify Project Structure

**On server, run:**
```bash
cd ~/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
ls -la

# Should see:
# scripts/
# data/
# results/
# models/
# docs/
# P7_DATA_ANALYSIS_REPORT.md
# environment.yml
```

**Create missing directories:**
```bash
mkdir -p data/{p1_set_a,p3_benchmark,external,splits,provenance}
mkdir -p results/{phase1_proof_of_concept,phase2_benchmark,phase3_scaffold}
mkdir -p models/{phase1,phase2,phase3}
mkdir -p logs
```

---

## 📊 Phase 1: Data Extraction & ANP Annotation

### Step 1.1: Extract P1 Set A (20 candidates)

**Script:** `scripts/p7_extract_p1_set_a.py`

**Purpose:** Extract 20 top candidates from P1 V8 canonical results

**Input:**
- `../Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/set_a_top_20_candidates.csv`
- Or equivalent from P1 V8 submission package

**Output:**
- `data/p1_set_a/p1_set_a_20_candidates.csv`
  - Columns: `mol_id, SMILES, MPO, docking_scores (4 targets), activity_label`

**Run:**
```bash
cd ~/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
python scripts/p7_extract_p1_set_a.py
```

### Step 1.2: Extract P3 Benchmark (19,849 molecules)

**Script:** `scripts/p7_extract_p3_benchmark.py`

**Purpose:** Extract P3 canonical cohort with activity labels and splits

**Input:**
- `../Project3_Quantum_Inspired_RepresentationsV2607_V4/data/canonical_panel_19849.csv`
- `../Project3_Quantum_Inspired_RepresentationsV2607_V4/data/splits/5fold_splits.json`

**Output:**
- `data/p3_benchmark/p3_benchmark_19849.csv`
  - Columns: `mol_id, SMILES, activity_label, fold`
- `data/splits/p3_5fold_splits.json`

**Run:**
```bash
python scripts/p7_extract_p3_benchmark.py
```

### Step 1.3: Compute ANP Metadata

**Script:** `scripts/p7_compute_anp_metadata.py`

**Purpose:** Compute ACSI, Fsp³, ANP classification for all molecules

**Computations:**
1. **ACSI** (African-Chemotype Structural Index):
   - Tanimoto similarity to 396 ANP reference set
   - Mean of top-5 nearest neighbors
   
2. **Fsp³** (Fraction sp³ carbons):
   - `Fsp3 = (# sp³ carbons) / (# all carbons)`
   
3. **Stereocenter count:** Count R/S chiral centers

4. **Ring count:** Number of rings (SSSR)

5. **Macrocycle detection:** Any ring ≥12 atoms

6. **ANP class assignment:**
   - Indole alkaloids (indole + alkaloid features)
   - Prenylated flavonoids (flavonoid + prenyl)
   - Quassinoids (triterpenoid scaffold)
   - Simple phenolics (aromatic + OH)
   - Synthetic (ACSI < 0.3)

**Output:**
- `data/p1_set_a/p1_set_a_anp_metadata.csv`
- `data/p3_benchmark/p3_benchmark_anp_metadata.csv`

**Run:**
```bash
python scripts/p7_compute_anp_metadata.py --dataset p1_set_a
python scripts/p7_compute_anp_metadata.py --dataset p3_benchmark
```

### Step 1.4: Create Data Manifest (Provenance)

**Script:** `scripts/p7_create_data_manifest.py`

**Purpose:** Freeze data provenance (hashes, sources, timestamps)

**Output:**
- `data/provenance/data_manifest.json`

**Format:**
```json
{
  "p1_set_a": {
    "source": "Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/",
    "n_molecules": 20,
    "sha256": "...",
    "timestamp": "2026-09-24T12:00:00Z"
  },
  "p3_benchmark": {
    "source": "Project3_Quantum_Inspired_RepresentationsV2607_V4/data/",
    "n_molecules": 19849,
    "sha256": "...",
    "timestamp": "2026-09-24T12:05:00Z",
    "splits": "5fold_canonical"
  }
}
```

**Run:**
```bash
python scripts/p7_create_data_manifest.py
```

---

## 🧪 Phase 2: Classical Baselines

### Step 2.1: ECFP4 Baseline (P1 Set A)

**Script:** `scripts/p7_baseline_ecfp4_mlp.py`

**Purpose:** Classical baseline for comparison (ECFP4 → MLP)

**Architecture:**
- Input: ECFP4 (2048-bit)
- MLP: 2048 → 128 → 64 → 32 → 1 (Sigmoid)
- Loss: Binary cross-entropy
- Optimizer: Adam (lr=0.001)

**Validation:** Leave-One-Out CV (n=20)

**Output:**
- `results/phase1_proof_of_concept/ecfp4_mlp_loo_results.csv`
  - Columns: `fold, y_true, y_pred, auc, accuracy, f1`
- `results/phase1_proof_of_concept/ecfp4_mlp_loo_summary.json`
  - Mean AUC ± std, training time

**Run:**
```bash
python scripts/p7_baseline_ecfp4_mlp.py \
  --data data/p1_set_a/p1_set_a_20_candidates.csv \
  --output results/phase1_proof_of_concept/ \
  --cv loo
```

### Step 2.2: GNN Baseline (P1 Set A)

**Script:** `scripts/p7_baseline_gnn.py`

**Purpose:** Graph neural network baseline (no quantum)

**Architecture:**
- GIN (3 layers, 64-dim hidden)
- Global mean pooling
- MLP: 64 → 32 → 1

**Validation:** Leave-One-Out CV

**Output:**
- `results/phase1_proof_of_concept/gnn_loo_results.csv`
- `results/phase1_proof_of_concept/gnn_loo_summary.json`

**Run:**
```bash
python scripts/p7_baseline_gnn.py \
  --data data/p1_set_a/p1_set_a_20_candidates.csv \
  --output results/phase1_proof_of_concept/ \
  --cv loo
```

---

## ⚛️ Phase 3A: QFE Proof-of-Concept

### Step 3.1: QFE Architecture (4-qubit, depth 1)

**Script:** `scripts/p7_arch1_quantum_feature_extractor.py`

**Purpose:** First hybrid quantum-classical model

**Architecture:**
```
SMILES → ECFP4 (2048-bit) 
       → Classical encoder: Linear(2048 → 4)
       → Quantum circuit (4 qubits, depth 1, RZZ entangling)
       → Measurement: Pauli-Z expectations (4-dim)
       → Classical decoder: MLP(4 → 64 → 32 → 1)
```

**Quantum Circuit:**
```python
# Data encoding
for i in range(4):
    qml.RY(encoded_features[i], wires=i)

# Variational layer (trainable)
for i in range(4):
    qml.RX(theta[i, 0], wires=i)
    qml.RY(theta[i, 1], wires=i)
    qml.RZ(theta[i, 2], wires=i)

# Entangling (RZZ)
for i in range(3):
    qml.RZZ(theta_ent[i], wires=[i, i+1])

# Measurement
return [qml.expval(qml.PauliZ(i)) for i in range(4)]
```

**Validation:** Leave-One-Out CV

**Output:**
- `results/phase1_proof_of_concept/qfe_4q_d1_loo_results.csv`
- `results/phase1_proof_of_concept/qfe_4q_d1_loo_summary.json`
- `results/phase1_proof_of_concept/qfe_4q_d1_gradient_norms.csv` (barren plateau check)

**Run:**
```bash
python scripts/p7_arch1_quantum_feature_extractor.py \
  --data data/p1_set_a/p1_set_a_20_candidates.csv \
  --output results/phase1_proof_of_concept/ \
  --qubits 4 \
  --depth 1 \
  --entangling rzz \
  --cv loo \
  --backend default.qubit
```

**Expected runtime:** ~2 hours on CPU (statevector simulator)

### Step 3.2: Gradient Analysis

**Purpose:** Verify no barren plateaus (quantum gradients propagate)

**Check:**
- Log ||∇_θ L|| after each epoch
- Alert if ||∇_θ L|| < 10⁻⁶ (vanishing gradient)

**Output:**
- `results/phase1_proof_of_concept/qfe_gradient_analysis.png`
  - Plot: Epoch vs. gradient norm

---

## 📈 Phase 3B: Compare QFE vs. Baselines

### Step 3.3: Statistical Comparison

**Script:** `scripts/p7_phase1_statistical_tests.py`

**Purpose:** Paired t-test: QFE vs. ECFP4 vs. GNN

**Tests:**
1. QFE vs. ECFP4: Paired t-test on LOO-CV AUCs (n=20 folds)
2. QFE vs. GNN: Paired t-test
3. Effect size: Cohen's d

**Output:**
- `results/phase1_proof_of_concept/statistical_comparison.csv`
  - Columns: `comparison, mean_diff, t_stat, p_value, cohens_d, interpretation`
- `results/phase1_proof_of_concept/comparison_boxplot.png`

**Run:**
```bash
python scripts/p7_phase1_statistical_tests.py \
  --ecfp4 results/phase1_proof_of_concept/ecfp4_mlp_loo_results.csv \
  --gnn results/phase1_proof_of_concept/gnn_loo_results.csv \
  --qfe results/phase1_proof_of_concept/qfe_4q_d1_loo_results.csv \
  --output results/phase1_proof_of_concept/
```

### Step 3.4: Phase 1 Decision Gate

**Criteria:**
✅ **PASS:** QFE ≥ 80% of ECFP4 performance  
✅ **PASS:** Quantum gradients propagate (||∇_θ L|| > 10⁻⁶)  
✅ **PASS:** Training converges (loss decreases)  

**If PASS:** Proceed to Phase 4 (P3 Benchmark)  
**If FAIL:** Debug → ablate circuit config → retry

---

## 📝 Summary: What You'll Run on Server (Phase 0-3)

**Total estimated time:** 1-2 days

```bash
# Phase 0: Environment
conda activate malaria_qml_hybrid
python -c "import pennylane, torch, rdkit, sklearn; print('Environment OK')"

# Phase 1: Data
python scripts/p7_extract_p1_set_a.py
python scripts/p7_extract_p3_benchmark.py
python scripts/p7_compute_anp_metadata.py --dataset p1_set_a
python scripts/p7_create_data_manifest.py

# Phase 2: Baselines
python scripts/p7_baseline_ecfp4_mlp.py --data data/p1_set_a/p1_set_a_20_candidates.csv --output results/phase1_proof_of_concept/ --cv loo
python scripts/p7_baseline_gnn.py --data data/p1_set_a/p1_set_a_20_candidates.csv --output results/phase1_proof_of_concept/ --cv loo

# Phase 3A: QFE
python scripts/p7_arch1_quantum_feature_extractor.py --data data/p1_set_a/p1_set_a_20_candidates.csv --output results/phase1_proof_of_concept/ --qubits 4 --depth 1 --entangling rzz --cv loo --backend default.qubit

# Phase 3B: Analysis
python scripts/p7_phase1_statistical_tests.py --ecfp4 results/phase1_proof_of_concept/ecfp4_mlp_loo_results.csv --gnn results/phase1_proof_of_concept/gnn_loo_results.csv --qfe results/phase1_proof_of_concept/qfe_4q_d1_loo_results.csv --output results/phase1_proof_of_concept/
```

**Transfer to local:**
```bash
# On server, create archive
cd ~/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
tar -czf p7_phase1_results.tar.gz results/phase1_proof_of_concept/ data/

# Transfer (adjust path/method for your setup)
scp p7_phase1_results.tar.gz local_machine:~/Downloads/
```

---

## ✅ What I'll Create Next (Scripts)

Let me know and I'll create:

1. **`scripts/p7_extract_p1_set_a.py`** — Extract P1 Set A from canonical results
2. **`scripts/p7_compute_anp_metadata.py`** — Compute ACSI, Fsp³, ANP class
3. **`scripts/p7_baseline_ecfp4_mlp.py`** — ECFP4-MLP baseline
4. **`scripts/p7_arch1_quantum_feature_extractor.py`** — QFE hybrid model
5. **`scripts/p7_phase1_statistical_tests.py`** — Statistical comparison

**Which should I start with?** Or should I create all 5 scripts in sequence?

---

**Status:** Ready for Phase 0 environment verification  
**Next:** Your confirmation → I'll create the scripts → You run on server → Results come back for paper writing