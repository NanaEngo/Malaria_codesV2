# P1 V7 - V5 Integration Plan

**Date:** 2026-01-11  
**Task:** Integrate V5 resources into V7 manuscript (following successful V4 integration pattern)  
**Status:** Planning

---

## 🎯 INTEGRATION STRATEGY

Following the successful V4 integration approach:
1. **Identify V5 unique resources** not already in V7
2. **Extract data and create tables** for SM
3. **Add explanatory text** to main manuscript
4. **Generate figures** if beneficial
5. **Update cross-references** throughout

---

## 📊 V5 RESOURCES AVAILABLE

### 1. Four-Target Vina Docking Data ✅ (Already in V7)
- **File:** `results/v5_four_target_vina_affinities.csv`
- **Content:** 17 candidates × 4 targets (PfDHFR, PfCRT, PfClpP, PfATP4)
- **Status:** ✅ **Already integrated into V7 main manuscript**
- **V7 Usage:** Main Results section, Table 2 (dual priority table)

### 2. Target-Specific Pocket Definitions
- **Files:**
  - `results/p1_v5_pocket_centers_verified.json`
  - `results/structural_pocket_dossier.md`
- **Content:** Grid box centers and dimensions for 4 targets
- **Status:** ✅ **Already integrated into V7 Methods** (added in Option 2)
- **V7 Usage:** Methods section with exact coordinates

### 3. Mutant Docking-RRS Pilot Data
- **Files:**
  - `results/rrs_pilot/c_rrs_pilot_per_target_v5.csv`
  - Various mutant docking outputs
- **Content:** PfDHFR (WT + N51I/C59R/S108N/I164L) and PfCRT (WT + K76T/K76A)
- **Status:** ⏳ **Potentially useful for SM supplementary analysis**
- **Note:** V7 uses P2 canonical RRS data (different provenance)

### 4. DEKOIS Benchmark Results
- **Files:**
  - `p1_enrichment_chembl_benchmark.csv`
  - `p1_enrichment_summary.txt`
  - Scripts: `compute_dekois_auc.py`, `p1_v5_rederive_dekois_pf_dhfr.py`
- **Content:** ROC-AUC 0.4964, PR-AUC 0.0340 for PfDHFR
- **Status:** ✅ **Already mentioned in V7 SM**
- **Potential Enhancement:** Add detailed DEKOIS table to SM

### 5. Binding Mode Analysis
- **Files:**
  - `manuscript/SM_Figure_S15_top10_binding_modes.pdf`
  - Various pose analysis scripts
- **Content:** Visual binding mode representations
- **Status:** ⏳ **Could be adapted for V7 SM**
- **Potential:** SM figure showing representative binding modes

### 6. Retrosynthesis Analysis
- **Files:**
  - `manuscript/SM_Table_S20_top10_retrosynthesis.tex`
  - `manuscript/SM_Table_S20_top10_retrosynthesis_askcos_stub.tex`
- **Content:** AskCos retrosynthetic analysis for top candidates
- **Status:** ⏳ **Could provide synthetic accessibility context**
- **Potential:** SM table showing synthetic routes

### 7. Reference Ligand Validation
- **Files:**
  - Multiple `reference_ligand_preflight*.json` files
  - `results/reference_ligands/` directory
- **Content:** Redocking validation for known ligands
- **Status:** ⏳ **Could strengthen validation narrative**
- **Potential:** SM table with redocking RMSD values

### 8. V5 Manuscript Figures
- **Location:** `manuscript/Graphics/`
- **Content:** Publication-quality figures from V5
- **Status:** ⏳ **Review for V7 adaptation**

---

## 📋 V5 INTEGRATION TASKS

### Priority 1: DEKOIS Enrichment Table (HIGHEST VALUE)

**Why:** Demonstrates docking validation with external benchmark
**What to do:**
1. Extract DEKOIS data from V5 files
2. Create SM Table: DEKOIS-2.0 PfDHFR benchmark results
3. Include: ROC-AUC, PR-AUC, EF@1/5/10/20%, active/decoy mean scores
4. Add reference to V7 SM section on docking validation

**Files to use:**
- `p1_enrichment_chembl_benchmark.csv`
- `p1_enrichment_summary.txt`

**Estimated time:** 1-2 hours  
**Output:** SM Table S11 (DEKOIS enrichment)

### Priority 2: Reference Ligand Redocking Table

**Why:** Validates docking protocol accuracy
**What to do:**
1. Extract redocking RMSD values for known ligands
2. Create SM Table: Reference ligand redocking validation
3. Include: Ligand name, PDB code, RMSD, success criterion (<2.0 Å)
4. Add reference in V7 Methods or SM

**Files to use:**
- `results/reference_ligand_preflight*.json`
- V5 redocking scripts output

**Estimated time:** 1-2 hours  
**Output:** SM Table S12 (redocking validation)

### Priority 3: Binding Mode Representative Figure (OPTIONAL)

**Why:** Visual support for binding predictions
**What to do:**
1. Review V5 binding mode figure (`SM_Figure_S15_top10_binding_modes.pdf`)
2. Adapt or regenerate for V7 top candidates (PP-06, PP-11, PP-15)
3. Add to V7 SM as SM Figure

**Files to use:**
- `manuscript/SM_Figure_S15_top10_binding_modes.pdf`
- Pose analysis scripts

**Estimated time:** 3-4 hours (if regeneration needed)  
**Output:** SM Figure (binding modes)

### Priority 4: Synthetic Accessibility Discussion (OPTIONAL)

**Why:** Addresses synthetic feasibility
**What to do:**
1. Review V5 retrosynthesis table
2. Extract synthetic accessibility metrics
3. Add brief discussion in V7 main text or SM

**Files to use:**
- `manuscript/SM_Table_S20_top10_retrosynthesis.tex`
- `r8b/askcos_cache.json`

**Estimated time:** 2-3 hours  
**Output:** Enhanced discussion + optional SM table

---

## 🚀 RECOMMENDED EXECUTION ORDER

### Session 1: DEKOIS Table (HIGH PRIORITY)

**Estimated time:** 1-2 hours

**Steps:**
1. Read `p1_enrichment_summary.txt` for key metrics
2. Read `p1_enrichment_chembl_benchmark.csv` for detailed data
3. Create `scripts/v7_generate_dekois_table.py`
4. Generate SM Table S11
5. Add cross-reference in V7 SM
6. Compile and verify

**Deliverable:** SM Table S11 with DEKOIS benchmarking results

### Session 2: Redocking Validation Table (MEDIUM PRIORITY)

**Estimated time:** 1-2 hours

**Steps:**
1. Parse `reference_ligand_preflight*.json` files
2. Extract RMSD values for known ligands
3. Create `scripts/v7_generate_redocking_table.py`
4. Generate SM Table S12
5. Add cross-reference in V7 Methods
6. Compile and verify

**Deliverable:** SM Table S12 with redocking validation

### Session 3: Binding Mode Figure (OPTIONAL, LOW PRIORITY)

**Estimated time:** 3-4 hours

**Steps:**
1. Review existing V5 figure
2. Decide: adapt existing or regenerate for V7 leads
3. If adapting: copy and adjust figure
4. If regenerating: use PyMOL/Chimera scripts
5. Add to V7 SM
6. Compile and verify

**Deliverable:** SM Figure showing binding modes

---

## ✅ WHAT'S ALREADY INTEGRATED FROM V5

The following V5 content is **already present in V7**:

1. ✅ **Four-target Vina data** - Main manuscript Table 2 (dual priority)
2. ✅ **Grid box specifications** - Methods section (exact coordinates)
3. ✅ **Target descriptions** - Introduction and Methods
4. ✅ **DEKOIS mention** - SM discusses benchmarking
5. ✅ **Polypharmacology concept** - Results and Discussion

---

## 📊 PRIORITY SCORING

| Resource | Scientific Value | Ease of Integration | Priority |
|----------|:----------------:|:-------------------:|:--------:|
| **DEKOIS enrichment table** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **🔴 HIGH** |
| **Redocking validation** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **🟡 MEDIUM** |
| **Binding mode figure** | ⭐⭐⭐ | ⭐⭐ | 🟢 LOW |
| **Synthetic accessibility** | ⭐⭐⭐ | ⭐⭐ | 🟢 LOW |

---

## 💡 KEY INSIGHTS

### 1. V5-V7 Relationship:
- V7 **inherits** V5's four-target docking data
- V7 **adds** P2's RRS mutant data for resilience scoring
- V7 **integrates** polypharmacology + mutation tolerance narrative
- V5 provides **validation** data (DEKOIS, redocking) not yet in V7 SM

### 2. What V5 Adds to V7:
- **External validation:** DEKOIS benchmark results
- **Protocol validation:** Reference ligand redocking
- **Visual support:** Binding mode representations
- **Synthetic context:** Retrosynthesis analysis

### 3. Integration Philosophy:
- Follow V4 pattern: **data tables + brief text + cross-references**
- Focus on **high-value, low-effort** additions
- Maintain **scientific rigor** (don't cherry-pick)
- Keep **SM comprehensive** (main text focused)

---

## 📁 FILES TO CREATE

### Scripts:
1. `scripts/v7_generate_dekois_table.py` - DEKOIS enrichment table
2. `scripts/v7_generate_redocking_table.py` - Redocking validation table
3. `scripts/v7_adapt_binding_figure.py` - Binding mode figure (optional)

### Tables:
1. `manuscript/tables/sm_table_dekois_enrichment.tex` - SM Table S11
2. `manuscript/tables/sm_table_redocking_validation.tex` - SM Table S12

### Documentation:
1. `P1_V7_V5_INTEGRATION_PLAN.md` - This file
2. `P1_V7_V5_INTEGRATION_COMPLETE.md` - Completion summary (to create)

---

## 🎯 SUCCESS CRITERIA

### V5 Integration Complete When:
- ✅ DEKOIS enrichment table added to SM
- ✅ Redocking validation table added to SM (optional but recommended)
- ✅ Cross-references added to main text/SM
- ✅ Manuscript compiles with 0 errors
- ✅ All tables referenced in text
- ✅ Documentation complete

### Optional Enhancements:
- ⏳ Binding mode figure adapted/regenerated
- ⏳ Synthetic accessibility discussion added

---

## 📈 EXPECTED IMPACT

### Scientific Quality:
- **Stronger validation narrative** - External benchmark + redocking
- **Enhanced reproducibility** - Protocol validation documented
- **Visual support** - Binding modes provide mechanistic insight

### Manuscript Competitiveness:
- **Reviewer appeal** - Demonstrates rigorous validation
- **JCIM standards** - Comprehensive supporting information
- **Transparency** - All validation data disclosed

---

## ⚠️ IMPORTANT NOTES

### V5 vs P2 RRS Data:
- V5 has **exploratory RRS pilot** (17 candidates, 2 targets, limited mutations)
- P2 has **canonical RRS** (different provenance, more extensive)
- V7 uses **P2 canonical RRS** for main results
- V5 RRS can be mentioned as **independent corroboration** but not primary data

### DEKOIS Caveat:
- ROC-AUC 0.4964 is **near-random** (95% CI includes 0.50)
- This is **expected for Vina** on DEKOIS (property-matched decoys)
- Must be presented **transparently** as protocol validation, not performance claim
- Main text already discusses scoring function limitations

### Provenance Discipline:
- All V5-derived content must cite V5 source files
- Maintain truthful labels (exploratory, pilot, etc.)
- Don't mix V5 and P2 provenance streams

---

## 🚀 RECOMMENDED START: PRIORITY 1 (DEKOIS TABLE)

**Reason:** Highest scientific value, easiest integration, strengthens validation

**First Command:**
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid
head -50 p1_enrichment_summary.txt
```

**Then:**
1. Extract metrics from summary
2. Create table generation script
3. Generate LaTeX table
4. Insert into V7 SM
5. Compile and verify

**Estimated time:** 1-2 hours  
**Output:** SM Table S11 (DEKOIS enrichment benchmark)

---

**V5 INTEGRATION PLAN COMPLETE - READY TO EXECUTE** 🎯
