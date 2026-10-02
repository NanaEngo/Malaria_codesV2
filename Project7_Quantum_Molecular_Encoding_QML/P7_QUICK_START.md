# P7 Quick Start — Get Running in 30 Minutes

**Environment:** Server with `malaria_qml_hybrid` conda environment  
**Goal:** Phase 1 results (20 candidates, LOO-CV) → Paper writing

---

## ⚡ 30-Minute Quick Start

### Step 1: SSH to Server (2 min)
```bash
ssh your_server
cd ~/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML
```

### Step 2: Verify Environment (5 min)
```bash
conda activate malaria_qml_hybrid

# Quick check
python -c "import pennylane as qml; import torch; import rdkit; print('✓ Environment OK')"

# If any imports fail, see P7_SERVER_EXECUTION_PLAN.md Phase 0.2
```

### Step 3: Create Directories (1 min)
```bash
mkdir -p data/{p1_set_a,p3_benchmark,splits,provenance}
mkdir -p results/phase1_proof_of_concept
mkdir -p models/phase1
mkdir -p logs
```

### Step 4: Tell Me What to Create (2 min)

**I need to know:**

1. **Where is P1 Set A data?** 
   - Path to the 20 candidates from P1 V8?
   - Or should I extract from P1 canonical results?

2. **File format?**
   - CSV with columns: `SMILES, activity_label, mol_id`?
   - Or different format?

3. **Activity labels?**
   - Binary (0/1)?
   - From docking scores (threshold)?
   - Or pre-labeled?

4. **What scripts first?**
   - Option A: All 5 scripts (I create → you run in sequence)
   - Option B: One by one (I create → you test → next)

---

## 🎯 What Happens Next

### After I Create Scripts:

**You run on server:**
```bash
# 1. Data extraction (~10 min)
python scripts/p7_extract_p1_set_a.py

# 2. ANP metadata (~15 min)
python scripts/p7_compute_anp_metadata.py --dataset p1_set_a

# 3. ECFP4 baseline (~30 min)
python scripts/p7_baseline_ecfp4_mlp.py \
  --data data/p1_set_a/p1_set_a_20_candidates.csv \
  --output results/phase1_proof_of_concept/ \
  --cv loo

# 4. QFE quantum model (~2 hours)
python scripts/p7_arch1_quantum_feature_extractor.py \
  --data data/p1_set_a/p1_set_a_20_candidates.csv \
  --output results/phase1_proof_of_concept/ \
  --qubits 4 --depth 1 --entangling rzz --cv loo

# 5. Statistical comparison (~5 min)
python scripts/p7_phase1_statistical_tests.py \
  --ecfp4 results/phase1_proof_of_concept/ecfp4_mlp_loo_results.csv \
  --qfe results/phase1_proof_of_concept/qfe_4q_d1_loo_results.csv \
  --output results/phase1_proof_of_concept/
```

**Total runtime:** ~3 hours (mostly QFE training)

### You Transfer Results:
```bash
# On server
tar -czf p7_phase1_results.tar.gz results/ data/

# To local (adjust for your setup)
scp p7_phase1_results.tar.gz local:~/Downloads/
```

### We Write Paper:
**On your local machine (where we are now):**
- Extract results archive
- I'll analyze: AUC, gradient norms, quantum vs. classical
- We'll draft: Methods, Results, Tables, Figures
- Format: JCIM LaTeX template

---

## 📋 Decision Points

### Before I Create Scripts, Tell Me:

**A. Data Source**
- [ ] P1 Set A is already extracted (path: `___________`)
- [ ] Need to extract from P1 V8 results (I'll write extraction script)
- [ ] Need to create from scratch (provide SMILES list)

**B. Activity Labels**
- [ ] Binary labels already exist (0/1 or active/inactive)
- [ ] Derive from docking scores (threshold: `___________`)
- [ ] Use MPO scores (threshold: `___________`)

**C. ANP Reference Set**
- [ ] 396 ANP SMILES available (path: `___________`)
- [ ] Extract from ANPDB/AfroDb (I'll write fetcher)
- [ ] Skip ACSI for now (compute later)

**D. Script Creation Strategy**
- [ ] **Option A:** Create all 5 scripts now (I'll do it in one go)
- [ ] **Option B:** Create one-by-one (start with data extraction)

---

## 🚀 Recommended: Option A (All Scripts)

**If you choose Option A, I'll create:**

1. `scripts/p7_extract_p1_set_a.py` — Get 20 candidates
2. `scripts/p7_compute_anp_metadata.py` — Compute ACSI, Fsp³
3. `scripts/p7_baseline_ecfp4_mlp.py` — Classical baseline
4. `scripts/p7_arch1_quantum_feature_extractor.py` — Quantum hybrid
5. `scripts/p7_phase1_statistical_tests.py` — Compare results

**You run them in sequence on server (3 hours total)**

**Then we meet back here to write the paper!**

---

## ❓ Questions for You

**Before I start coding, please answer:**

1. **P1 Set A location?** (file path or "extract from P1 V8")
2. **Activity labels?** (already labeled or derive from scores?)
3. **ANP reference set?** (path or "I'll fetch it")
4. **Script strategy?** (all 5 now or one-by-one?)
5. **Any specific P1 candidates?** (e.g., PP-01, PP-15 from Set C instead of Set A?)

---

**Status:** Waiting for your inputs → Will create scripts → You run on server → We write paper  
**ETA to first results:** 3-4 hours after scripts are ready

