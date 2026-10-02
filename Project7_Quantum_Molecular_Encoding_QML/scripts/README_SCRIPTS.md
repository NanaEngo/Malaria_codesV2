# P7 Scripts Overview

All scripts for Phase 1 execution on server.

## Created Scripts (Ready to Use):

### 1. **p7_explore_p1_data.py** ✓
**Purpose:** Find and inspect available P1/P2 data  
**Usage:**
```bash
python scripts/p7_explore_p1_data.py
```
**Output:** List of found data files with paths

---

### 2. **p7_extract_p1_set_a.py** ✓
**Purpose:** Extract 20 candidates from P1 (or 17 from P2 Set C)  
**Usage:**
```bash
# Auto-search for Set A
python scripts/p7_extract_p1_set_a.py

# Use Set C instead
python scripts/p7_extract_p1_set_a.py --use-set-c

# Manual file
python scripts/p7_extract_p1_set_a.py --input path/to/data.csv
```
**Output:** `data/p1_set_a/p1_set_a_N_candidates.csv`

---

### 3. **p7_compute_anp_metadata.py** ✓
**Purpose:** Compute ACSI, Fsp³, stereocenter count, ANP class  
**Usage:**
```bash
python scripts/p7_compute_anp_metadata.py --dataset p1_set_a
```
**Output:** `data/p1_set_a/*_anp_metadata.csv`

---

### 4. **p7_baseline_ecfp4_mlp.py** ✓
**Purpose:** Classical baseline (ECFP4 → MLP)  
**Usage:**
```bash
python scripts/p7_baseline_ecfp4_mlp.py \
  --data data/p1_set_a/p1_set_a_20_candidates.csv \
  --output results/phase1_proof_of_concept/ \
  --cv loo \
  --device cpu
```
**Output:**
- `results/phase1_proof_of_concept/ecfp4_mlp_loo_results.csv`
- `results/phase1_proof_of_concept/ecfp4_mlp_loo_summary.json`

---

### 5. **p7_arch1_quantum_feature_extractor.py** (Creating next)
**Purpose:** Quantum Feature Extractor (QFE) - hybrid model  
**Usage:**
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
**Output:**
- `results/phase1_proof_of_concept/qfe_4q_d1_loo_results.csv`
- `results/phase1_proof_of_concept/qfe_4q_d1_loo_summary.json`
- `results/phase1_proof_of_concept/qfe_gradient_norms.csv`

---

### 6. **p7_phase1_statistical_tests.py** (Creating next)
**Purpose:** Compare QFE vs. ECFP4 with statistical tests  
**Usage:**
```bash
python scripts/p7_phase1_statistical_tests.py \
  --ecfp4 results/phase1_proof_of_concept/ecfp4_mlp_loo_results.csv \
  --qfe results/phase1_proof_of_concept/qfe_4q_d1_loo_results.csv \
  --output results/phase1_proof_of_concept/
```
**Output:**
- `results/phase1_proof_of_concept/statistical_comparison.csv`
- `results/phase1_proof_of_concept/comparison_boxplot.png`

---

## Execution Order (Phase 1):

```bash
# 1. Find data
python scripts/p7_explore_p1_data.py

# 2. Extract data
python scripts/p7_extract_p1_set_a.py  # or --use-set-c

# 3. Compute ANP metadata
python scripts/p7_compute_anp_metadata.py --dataset p1_set_a

# 4. Classical baseline (~30 min)
python scripts/p7_baseline_ecfp4_mlp.py \
  --data data/p1_set_a/p1_set_a_*_candidates_anp_metadata.csv \
  --output results/phase1_proof_of_concept/ \
  --cv loo

# 5. Quantum model (~2 hours)
python scripts/p7_arch1_quantum_feature_extractor.py \
  --data data/p1_set_a/p1_set_a_*_candidates_anp_metadata.csv \
  --output results/phase1_proof_of_concept/ \
  --qubits 4 --depth 1 --entangling rzz --cv loo

# 6. Statistical comparison (~5 min)
python scripts/p7_phase1_statistical_tests.py \
  --ecfp4 results/phase1_proof_of_concept/ecfp4_mlp_loo_results.csv \
  --qfe results/phase1_proof_of_concept/qfe_4q_d1_loo_results.csv \
  --output results/phase1_proof_of_concept/
```

**Total time:** ~3 hours

---

## Transfer Results to Local:

```bash
# On server
cd ~/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
tar -czf p7_phase1_results.tar.gz results/phase1_proof_of_concept/ data/p1_set_a/

# Copy to local (adjust for your setup)
scp p7_phase1_results.tar.gz local_machine:~/Downloads/
```

---

## Status:

- [x] p7_explore_p1_data.py
- [x] p7_extract_p1_set_a.py
- [x] p7_compute_anp_metadata.py
- [x] p7_baseline_ecfp4_mlp.py
- [ ] p7_arch1_quantum_feature_extractor.py (creating next)
- [ ] p7_phase1_statistical_tests.py (creating next)

**Next:** Creating quantum model script...
