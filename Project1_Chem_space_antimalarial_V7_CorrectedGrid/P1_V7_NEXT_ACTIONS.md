# P1 V7 Enhancement - Immediate Action Plan

**Created:** 2026-01-10  
**Status:** Phase 1 (Narrative Refinement) COMPLETE → Phase 2 (V4 Resource Integration) IN PROGRESS

---

## COMPLETED: Phase 1 Summary

✅ **Results section rewritten** (6 subsections, report→narrative)  
✅ **Discussion expanded** (+125%, now ~1200 words with 4 subsections)  
✅ **Anti-AI scan** (0 patterns detected)  
✅ **Compilation** (Main 24 pages, SI 6 pages, 0 errors)  

**Documents Created:**
- `P1_V7_REFINEMENT_ANALYSIS.md` - Comprehensive analysis
- `P1_V7_ACTION_PLAN.md` - Detailed 6-phase plan
- `P1_V7_PHASE1_COMPLETION_REPORT.md` - Phase 1 summary
- `P1_V7_BEFORE_AFTER_COMPARISON.md` - Changes log
- `P1_V4_RESOURCE_INVENTORY.md` - V4 resource catalog

---

## CURRENT TASK: V4 Resource Integration

### Critical Finding from BMAD

**Set-C Cohort (17 candidates: PP-01 to PP-17) is documented in BMAD:**
- Location: P2 section, Set-C analysis
- RRS: Mean 81.698 ± 12.367 (range 68.175–111.653)
- RRS Classes: A*:6, B:5, C:5, D:1
- PNS: Mean 3.571 ± 1.560
- ACSI: Mean 0.543 ± 0.153
- **68/68 target-wise Vina records** (17 × 4 targets: PfDHFR/PfCRT/PfClpP/PfATP4)

**V6 Integration Status:**
- V6 integrated V5 four-target panel with P2 Set-C RRS/PNS/ACSI
- Exact-SMILES canonical mapping complete
- All 17 candidates verified
- Data files in V6 results/exploratory/

---

## IMMEDIATE ACTIONS (Day 1)

### Action 1: Locate V7 Data Files

```bash
# Check V7 results directory structure
ls -la Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/

# Search for Set-C data files
find Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/ -name "*set*c*" -o -name "*PP-*"

# Check if V6 data was copied to V7
ls -la Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/exploratory/
```

### Action 2: Extract Set-C Data from V6 or BMAD

**Priority Data Needed:**
1. **17-candidate properties table** (MW, logP, HBD, HBA, TPSA, RB, fsp3, QED, SA, SYBA, NPL)
2. **ADMET profiles** (CYP450, hERG, DILI, SI_pred)
3. **Vina scores** (17×4 = 68 records)
4. **RRS/PNS/ACSI values** (already in BMAD)
5. **Scaffold analysis** (Bemis-Murcko, Tanimoto to seed NPs)
6. **Ersilia predictions** (eos7yti, eos7kpb, eos80ch)

**Source Options:**
- Option A: Extract from V6 `results/exploratory/derived/v6_integrated_candidate_metrics.csv`
- Option B: Parse from BMAD P2 section tables
- Option C: Run fresh analysis scripts on Set-C SMILES

### Action 3: Generate Critical SM Tables

**Table Priority (create in this order):**

1. **SM Table S1: Set-C Physicochemical Properties**
   - Format: 17 rows × (SMILES, MW, logP, HBD, HBA, TPSA, RB, fsp3)
   - Compare to V4 library statistics
   - Template: V4 SM physicochemical tables

2. **SM Table S2: Set-C Drug-Likeness Compliance**
   - Format: Lipinski violations, Veber, SYBA>0, NPL>0, SA<3.5, QED>0.70
   - Per-candidate compliance flags
   - Template: V4 SM-tab:druglikeness

3. **SM Table S3: Set-C ADMET Profile**
   - Format: 17 rows × (CYP2C9, CYP2C19, CYP3A4, CYP2D6, hERG, DILI, SI_pred)
   - Summary statistics
   - Template: V4 SM-tab:cyp450 + SM-tab:selectivity

4. **SM Table S4: Set-C Scaffold Analysis**
   - Format: Bemis-Murcko scaffolds, Tanimoto to nearest seed NP
   - NP-relatedness classification (Tanimoto ≥ 0.4)
   - Template: V4 SM-tab:scaffold_recovery

5. **SM Table S5: Set-C Stage-Specific Activity**
   - Format: eos80ch predictions (asexual vs sexual stages)
   - Template: V4 SM-tab:stage_activity

6. **SM Table S6: Set-C Vina Affinity Matrix**
   - Format: 17 candidates × 4 targets = 68 Vina scores
   - Mean/median per target
   - **Already in V7 main Results? Check current manuscript**

7. **SM Table S7: Set-C RRS/PNS/ACSI**
   - Format: 17 rows with RRS class, RRS value, PNS, ACSI
   - Cross-metric correlations
   - **Already in V7 SM? Check current manuscript**

### Action 4: Copy Essential V4 Figures

```bash
# Copy physicochemical violin plot
cp Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Graphics/phys_chem.pdf \
   Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript/Graphics/

# Copy enrichment validation figures if V7 needs them
cp Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Graphics/enrichment_roc_curves.pdf \
   Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript/Graphics/
```

### Action 5: Generate V7-Specific Binding Mode Figures

**CRITICAL: V7 needs interaction diagrams for PP-01 to PP-17**

**Check if docking pose files exist:**
```bash
# Search for PDBQT or PDB pose files
find Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/ -name "*.pdbqt" -o -name "*pose*.pdb"

# Or check V5/V6 for Set-C poses
find Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/ -name "*PP-*" -name "*.pdbqt"
find Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/ -name "*PP-*" -name "*.pdbqt"
```

**If poses exist, generate figures:**
- Use PyMOL or LigPlot+ to create 2D interaction diagrams
- Template: V4 `SM_Figure_S15_top10_binding_modes.pdf`
- Format: Multi-panel figure with 17 subpanels (or separate per target)
- Show: H-bonds, π-stacking, hydrophobic contacts, key residues

**If poses don't exist:**
- Extract from V5/V6 docking output
- Or note as limitation (docking performed, poses not archived)

---

## NEXT ACTIONS (Day 2)

### Action 6: Enhance V7 Main Text

**6.1 Introduction Enhancement**
- Add V4's accessibility gap argument (1000 CPU-hours barrier)
- Emphasize 94% malaria cases in endemic regions
- Strengthen hybrid NP+SD pharmacophore rationale

**6.2 Methods Enhancement**
- Add grid box specifications for all 4 targets (copy from V4 Methods)
- Add brief centroid-based sampling background (cite V4)
- Verify redocking validation section exists

**6.3 Results Enhancement**
- Verify all 7 Results subsections are narrative (not report-style)
- Add named lead analysis for top candidates (PP-06, PP-11, PP-15)
- Use V4 ligand 201/214/438 format as template

**6.4 Discussion Enhancement**
- Add computational efficiency context (99.3% cost reduction from V4)
- Add activity cliff discussion (centroid methodology limitation)
- Add literature positioning (V4's ANPDB coverage statistics)
- Expand on polypharmacology vs single-target optimization

### Action 7: Enhance V7 SM

**7.1 Insert Tables**
- Place SM Tables S1-S7 (created in Action 3) into V7 SM
- Follow V4 SM structure and formatting
- Add cross-references from main text

**7.2 Add Figures**
- Insert binding mode figures (if created in Action 5)
- Add V4 physicochemical violin plot if relevant
- Optional: VAE/clustering figures for Methods validation

**7.3 Add Methods Details**
- Port V4's MPO framework (if V7 discusses MPO for comparison)
- Port V4's ADMET 11-endpoint description
- Port V4's NP-relatedness filtering methodology

---

## DEPENDENCIES TO RESOLVE

### Question 1: Does V7 have complete Set-C data?
**Check:**
- V7 results/ directory structure
- Whether V6 data was copied to V7 during V6→V7 copy
- Whether BMAD P2 tables need to be regenerated

**If missing:** Extract from V6 or regenerate from SMILES

### Question 2: Does V7 have docking pose files?
**Check:**
- V7/V5/V6 results/ for PDBQT files
- Whether poses were archived or only scores kept

**If missing:** Note as limitation or extract from docking logs

### Question 3: What is V7 SM current state?
**Check:**
- How many tables/figures already in V7 SM?
- Is there a table for RRS/PNS/ACSI?
- Is there a table for Vina scores?

**Action:** Read V7 SM to assess gaps

### Question 4: Does V7 need enrichment validation?
**Check:**
- Whether V7 Results mentions MMV Malaria Box
- Whether V7 has DEKOIS or other benchmarks
- Whether V4's validation is cited

**Action:** Decide if V7 needs validation section or just cites V4

---

## FILES TO CREATE/UPDATE

### To Create:
1. SM Table S1-S7 (LaTeX tables)
2. Binding mode figures (PDF/PNG)
3. Named lead analysis subsection (LaTeX)
4. Enhanced Introduction paragraphs (LaTeX)
5. Enhanced Discussion subsections (LaTeX)

### To Update:
1. V7 main manuscript (Introduction, Methods, Results, Discussion)
2. V7 SM (insert tables, add figures, add Methods details)
3. V7 Graphics/ folder (copy figures from V4)

---

## SUCCESS CRITERIA

### Phase 2 Complete When:
✅ All 7 SM tables generated and inserted  
✅ Binding mode figures created or noted as unavailable  
✅ V7 main Introduction enhanced with accessibility argument  
✅ V7 main Discussion expanded with V4 context  
✅ V7 main Results includes named lead analysis  
✅ V7 SM includes ADMET/physicochemical/scaffold tables  
✅ All cross-references updated  
✅ Manuscript compiles without errors  

### Final Deliverable:
- **V7 Main:** 20-25 pages (JCIM limit ~25 pages)
- **V7 SM:** 8-12 pages (comprehensive tables + figures)
- **V7 Cover Letter:** 1 page (already exists?)
- **Compilation:** 0 errors, 0 undefined references
- **Figures:** All referenced figures exist in Graphics/

---

## NEXT IMMEDIATE STEP

**RIGHT NOW:** Check V7 data availability

```bash
# Execute these commands to assess V7 current state
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project1_Chem_space_antimalarial_V7_CorrectedGrid

# Check results directory
ls -la results/

# Check for Set-C data
find results/ -name "*PP-*" -o -name "*set*c*" | head -20

# Check current SM table/figure count
grep -c "\\begin{table}" manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.tex
grep -c "\\begin{figure}" manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.tex

# Check Graphics folder
ls manuscript/Graphics/
```

After this assessment, we can determine:
1. Whether to extract from V6 or regenerate data
2. Whether binding mode figures are feasible
3. Which SM tables already exist vs need creation
4. Next concrete file creation tasks

---

**END OF ACTION PLAN - READY TO EXECUTE**
