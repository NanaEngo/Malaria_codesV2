# P1 V7 Continuation Guide - Where to Resume

**Last Updated:** 2026-01-11  
**Current Status:** Phase 2 in progress (40% complete)  
**Last Action:** Integrated physicochemical and drug-likeness tables into V7 SM

---

## 🎯 QUICK RESUME - START HERE

When you resume work on V7 manuscript enhancement, **start with one of these three options:**

### Option A: ADMET Profile Table (RECOMMENDED - Highest Value)

**Why start here:**
- Highest scientific value for drug discovery manuscript
- Addresses safety and selectivity concerns
- Required for comprehensive candidate profiling

**What to do:**
```bash
# Check if ADMET data exists in BMAD
cd /home/vital/Documents/GitHub/Malaria_codesV2
grep -A 20 "PP-01\|PP-02\|PP-03" BMAD_Q1_DATA_ANALYSIS_REPORT.md | grep -i "CYP\|hERG\|DILI\|SI_pred"
```

**If data found:** Extract from BMAD and generate table  
**If data missing:** Run ADMET-AI predictions on 17 SMILES  
**Estimated time:** 2-4 hours  
**Output:** SM Table S6 (ADMET profile)

### Option B: Scaffold Analysis Table (ALTERNATIVE - Clear Path)

**Why start here:**
- Clear implementation path (no data dependencies)
- Demonstrates structural diversity
- Supports NP-relatedness claims

**What to do:**
1. Create `scripts/v7_generate_scaffold_table.py`
2. Extract Bemis-Murcko scaffolds from SMILES
3. Calculate Tanimoto to ANPDB seed compounds
4. Generate LaTeX table and insert as SM Table S7

**Estimated time:** 2-3 hours  
**Output:** SM Table S7 (scaffold analysis)

### Option C: Main Text Enhancements (ALTERNATIVE - High Priority)

**Why start here:**
- Improves narrative flow and scientific positioning
- Makes manuscript more competitive for JCIM
- Well-defined tasks with clear examples

**What to do:**
1. Enhance Introduction (accessibility gap, hybrid rationale)
2. Enhance Methods (grid boxes, centroid background)
3. Enhance Results (named lead analysis PP-06/PP-11/PP-15)
4. Enhance Discussion (efficiency, activity cliffs, positioning)

**Estimated time:** 3-4 hours  
**Output:** Enhanced V7 main text

---

## 📂 KEY FILES TO KNOW

### Data Files (YOUR CANONICAL DATA):
- **V7 integrated metrics:** `results/derived/v7_integrated_candidate_metrics.csv` (17 candidates, all metrics)
- **Physicochemical properties:** `results/derived/v7_physicochemical_properties.csv` (generated 2026-01-11)
- **Drug-likeness compliance:** `results/derived/v7_druglikeness_compliance.csv` (generated 2026-01-11)

### Manuscript Files:
- **V7 Main:** `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex` (24 pages)
- **V7 SM:** `manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.tex` (8 pages, sections S1-S10)
- **BMAD (data authority):** `/home/vital/Documents/GitHub/Malaria_codesV2/BMAD_Q1_DATA_ANALYSIS_REPORT.md`

### Scripts Created (REUSABLE):
- **Physicochemical table:** `scripts/v7_generate_physicochemical_table.py` ✅
- **Drug-likeness table:** `scripts/v7_generate_druglikeness_table.py` ✅
- **ADMET table:** `scripts/v7_generate_admet_table.py` (TO CREATE)
- **Scaffold table:** `scripts/v7_generate_scaffold_table.py` (TO CREATE)

### Documentation:
- **Progress report:** `P1_V7_PHASE2_PROGRESS_REPORT.md`
- **Session summary:** `P1_V7_PHASE2_SESSION_SUMMARY.md`
- **This guide:** `P1_V7_CONTINUATION_GUIDE.md`

---

## ✅ WHAT'S DONE (Don't Redo)

### Phase 1 (Narrative Refinement): COMPLETE
- ✅ Results section rewritten (report → narrative, 6 subsections)
- ✅ Discussion expanded (+125%, now ~1200 words, 4 subsections)
- ✅ Anti-AI scan passed (0 patterns detected)
- ✅ Compilation successful (Main 24 pages, SM 6 pages → now 8 pages)

### Phase 2 (Tables Generated): COMPLETE
- ✅ SM Table S4: Physicochemical properties (17 candidates, 11 properties)
- ✅ SM Table S5: Drug-likeness compliance (Lipinski, Veber, QED, NPL)
- ✅ Both tables integrated into V7 SM
- ✅ Section numbering updated (S4-S10)
- ✅ Compilation verified (0 errors)

### Key Findings (Already Established):
- ✅ 100% Lipinski/Veber compliance (17/17 candidates)
- ✅ Mean QED 0.703 (moderate-to-high drug-likeness)
- ✅ 94.1% NP-relatedness (16/17 have NPL > 0)
- ✅ Favorable ADME properties (MW 271.9 Da, logP 2.84, TPSA 66.3 ų)

---

## 🔄 WHAT'S LEFT TO DO

### Must-Have (for submission):
1. ⏳ **ADMET profile table** (SM Table S6) - 2-4 hours
2. ⏳ **Scaffold analysis table** (SM Table S7) - 2-3 hours
3. ⏳ **Main text enhancements** - 3-4 hours
   - Introduction: accessibility gap + hybrid rationale
   - Methods: grid boxes + centroid background
   - Results: named lead analysis (PP-06, PP-11, PP-15)
   - Discussion: efficiency + activity cliffs + positioning
4. ⏳ **Cross-reference updates** - 1 hour

**Estimated total:** 8-12 hours

### Nice-to-Have (optional):
1. ⏳ **Stage-specific activity table** (SM Table S8) - 2-3 hours (if eos80ch data available)
2. ⏳ **Binding mode figures** (SM Figure) - 4-8 hours (if pose files available)
3. ⏳ **Copy V4 figures** - 30 min (physicochemical violin plot, enrichment curves)

**Estimated total:** 6-11 hours

---

## 🚀 HOW TO START (Step-by-Step)

### If Starting with ADMET Table:

```bash
# Step 1: Check for existing ADMET data in BMAD
cd /home/vital/Documents/GitHub/Malaria_codesV2
grep -B 2 -A 10 "CYP\|hERG\|DILI" BMAD_Q1_DATA_ANALYSIS_REPORT.md | grep -i "PP-"

# Step 2a: If data found, extract and format
# (Create extraction script based on BMAD structure)

# Step 2b: If data missing, install ADMET-AI
mamba activate ML_env
pip install admet-ai

# Step 3: Create ADMET table generation script
# Copy structure from v7_generate_physicochemical_table.py
nano scripts/v7_generate_admet_table.py

# Step 4: Run script
python scripts/v7_generate_admet_table.py

# Step 5: Insert table into V7 SM (after current S5, renumber S6→S7, etc.)
# Step 6: Compile and verify
cd manuscript
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
```

### If Starting with Scaffold Analysis:

```bash
# Step 1: Create scaffold analysis script
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project1_Chem_space_antimalarial_V7_CorrectedGrid
nano scripts/v7_generate_scaffold_table.py

# Step 2: Run script
mamba run -n ML_env python scripts/v7_generate_scaffold_table.py

# Step 3: Insert table into V7 SM
# Step 4: Compile and verify
cd manuscript
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
```

### If Starting with Main Text Enhancements:

```bash
# Step 1: Read V4 Introduction for accessibility gap argument
cd /home/vital/Documents/GitHub/Malaria_codesV2
nano Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Antimalarial_Candidates_African_NP_V2607.tex

# Step 2: Read V7 Main to find insertion points
nano Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex

# Step 3: Add enhancements section by section
# (Introduction, Methods, Results, Discussion)

# Step 4: Compile and verify
cd Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
```

---

## 📊 PROGRESS DASHBOARD

### Overall Progress: 40% Complete

```
Phase 1 (Narrative):     [████████████████████] 100% ✅
Phase 2 (Tables):        [████████░░░░░░░░░░░░]  40% 🔄
  - Physicochemical:     [████████████████████] 100% ✅
  - Drug-likeness:       [████████████████████] 100% ✅
  - ADMET:               [░░░░░░░░░░░░░░░░░░░░]   0% ⏳
  - Scaffold:            [░░░░░░░░░░░░░░░░░░░░]   0% ⏳
  - Stage-specific:      [░░░░░░░░░░░░░░░░░░░░]   0% ⏳ (optional)
Phase 2 (Main Text):     [░░░░░░░░░░░░░░░░░░░░]   0% ⏳
  - Introduction:        [░░░░░░░░░░░░░░░░░░░░]   0%
  - Methods:             [░░░░░░░░░░░░░░░░░░░░]   0%
  - Results:             [░░░░░░░░░░░░░░░░░░░░]   0%
  - Discussion:          [░░░░░░░░░░░░░░░░░░░░]   0%
Phase 2 (Figures):       [░░░░░░░░░░░░░░░░░░░░]   0% ⏳ (optional)
```

### Manuscript Stats:
- **V7 Main:** 24 pages (ready for enhancements)
- **V7 SM:** 8 pages (needs +2-4 pages)
- **Target:** Main 20-25 pages, SM 10-15 pages
- **Quality:** Publication-ready formatting ✅

---

## 💡 TIPS FOR EFFICIENT CONTINUATION

### 1. Use Existing Scripts as Templates
- `v7_generate_physicochemical_table.py` is your template
- Copy structure for ADMET and scaffold scripts
- Reuse LaTeX table formatting patterns

### 2. Work in Batches
- Generate all remaining tables first (2-3 hours)
- Then insert all into SM together (1 hour)
- Then enhance main text (3-4 hours)
- Finally compile and verify (1 hour)

### 3. Verify After Each Step
```bash
# Quick compilation check
pdflatex -interaction=nonstopmode P1_V7_Integrated_Polypharmacology_RRS_SM.tex | grep -i "error\|warning"
```

### 4. Keep BMAD as Authority
- Always check BMAD first for existing data
- Don't regenerate what already exists
- BMAD is the canonical source for P1-P3

### 5. Test Scripts on Small Sample First
- Test on PP-01 to PP-03 before running full 17
- Verify output format before generating LaTeX
- Check one table insertion before doing all

---

## 📞 QUICK REFERENCE

### Python Environment:
```bash
mamba activate ML_env
```

### Key Imports (for new scripts):
```python
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem
from pathlib import Path
```

### Compilation Command:
```bash
cd manuscript
pdflatex -interaction=nonstopmode P1_V7_Integrated_Polypharmacology_RRS.tex
pdflatex -interaction=nonstopmode P1_V7_Integrated_Polypharmacology_RRS_SM.tex
```

### Data Location:
```
results/derived/v7_integrated_candidate_metrics.csv  # Main data
results/derived/v7_physicochemical_properties.csv    # Generated
results/derived/v7_druglikeness_compliance.csv       # Generated
```

---

## ✅ SUCCESS CRITERIA (When Done)

### Phase 2 Complete When:
- ✅ SM has physicochemical properties table (DONE)
- ✅ SM has drug-likeness compliance table (DONE)
- ⏳ SM has ADMET table (or note "not available")
- ⏳ SM has scaffold analysis table
- ⏳ Main Introduction has accessibility argument
- ⏳ Main Discussion has V4 efficiency context
- ⏳ Main Discussion has named lead analysis
- ⏳ All tables cross-referenced in text
- ⏳ Manuscript compiles with 0 errors

### Ready for Submission When:
- All must-have tasks complete
- V7 Main: 20-25 pages
- V7 SM: 10-15 pages
- 0 compilation errors
- All cross-references working
- Cover letter updated

---

## 🎯 RECOMMENDED START: OPTION A (ADMET)

**Reason:** Highest scientific value, addresses key reviewer concerns about safety/toxicity

**First Command:**
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2
grep -B 2 -A 10 "CYP\|hERG\|DILI" BMAD_Q1_DATA_ANALYSIS_REPORT.md | grep -i "PP-"
```

**If data found:** Proceed with ADMET table generation  
**If data missing:** Switch to Option B (Scaffold) or Option C (Main Text)

---

**RESUME POINT MARKED - GOOD LUCK! 🚀**

