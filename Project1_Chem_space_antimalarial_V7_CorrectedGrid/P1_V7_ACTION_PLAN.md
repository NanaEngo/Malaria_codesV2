# P1 V7 Manuscript Refinement - Action Plan
**Date:** August 11, 2026  
**Goal:** Transform V7 from technical report to publication-ready scientific paper for JCIM

---

## Phase 1: Immediate Narrative Refinement (Est. 3-4 hours)

### Task 1.1: Results Section Rewrite
**Priority:** CRITICAL  
**Estimated time:** 2 hours

**Current Issues:**
- Subsection titles read like report headers
- Leads with procedures instead of insights
- Technical details dominate narrative

**Actions:**
1. Rewrite all Results subsection titles to narrative style
2. Restructure paragraphs: insight → evidence → detail
3. Move excessive technical detail to methods or SI
4. Add transitional sentences between subsections

**Example Rewrites:**

| Current | Refined |
|---------|---------|
| "3.1 Chemical-space expansion preserved scaffolds while diversifying molecules" | "3.1 Scaffold-guided expansion generated diverse synthesizable candidates" |
| "3.2 Why four targets were retained" | "3.2 Mechanistic diversity guided target selection" |
| "3.3 The locked cohort spans four computational target profiles" | "3.3 Docking reveals complementary target-binding profiles" |
| "3.4 Per-target RRS separates mutation tolerance from target breadth" | "3.4 Mutation resilience varies independently of target breadth" |
| "3.5 Combining target breadth with mutation tolerance ranks the candidates" | "3.5 Joint prioritization identifies multi-target resilient candidates" |
| "3.6 Cross-metric associations were exploratory and mostly null" | "3.6 Chemical-space and network descriptors show limited correlation with resilience" |

###Task 1.2: Discussion Expansion
**Priority:** HIGH  
**Estimated time:** 1.5 hours

**Current State:** Good foundation (

533 words), needs depth

**Actions:**
1. **Add mechanistic interpretation paragraph** (~200 words)
   - Focus on PP-06 (PfCRT -7.91, A* RRS, 4/4 favorable)
   - Focus on PP-15 (RRS 111.7%, 4/4 favorable)
   - Focus on PP-11 (PfCRT-specific A* despite PfDHFR non-binding)
   - Structural features enabling breadth vs. specificity

2. **Add experimental validation roadmap** (~150 words)
   - Prioritization of PP-06, PP-15, PP-11 for biochemical assays
   - Mutant-panel testing strategy
   - MD validation on top candidates
   - Synthesis feasibility considerations

3. **Add comparison with computational antimalarial studies** (~200 words)
   - How this work complements recent ML/AI approaches
   - Novelty of per-target RRS vs. aggregate scoring
   - Position relative to recent QSAR/docking/virtual screening studies
   - Citations: recent 2024-2026 computational antimalarial papers

4. **Strengthen limitations paragraph** (~100 words)
   - Emphasize DEKOIS near-chance result for PfDHFR
   - Computational scores ≠ experimental affinity
   - Need for structural and biological validation
   - RRS is hypothesis-generating, not resistance proof

**Target Discussion length:** ~1100-1200 words (currently 533)

### Task 1.3: Introduction Polish
**Priority:** MEDIUM  
**Estimated time:** 30 minutes

**Actions:**
1. Add 2-3 sentences on PfClpP proteostasis biology (cite Tissawak2025)
2. Add 1-2 sentences on PfATP4 ion regulation (cite Haile2025)
3. Improve transition between paragraphs 2 and 3
4. Ensure first paragraph hooks reader with resistance crisis context

---

## Phase 2: Figure Generation (Est. 6-8 hours)

### Task 2.1: Workflow Schematic (Main Text, Priority Figure)
**Priority:** CRITICAL  
**Estimated time:** 2 hours

**Content:**
- Panel A: Chemical space funnel
  - 396 African NPs + 454 synthetics → 65,856 expanded → 19,913 prioritized
  - Show SELFIES/SMILES-VAE, clustering, MPO filtering
- Panel B: Target-anchored docking
  - 4 targets (PfDHFR/PfCRT/PfClpP/PfATP4)
  - Geometric gates
  - 17-member Set C → 68 pairs
- Panel C: Per-target RRS
  - WT vs. mutant comparison
  - Show separate PfDHFR (4 mutants) and PfCRT (2 mutants) panels
  - A*/B/C/D classification

**Tools:** Python matplotlib/seaborn + scientific illustration software  
**Style:** Clean, publication-quality, colorblind-safe palette

### Task 2.2: Binding Pose Gallery (Main or SI)
**Priority:** HIGH  
**Estimated time:** 3 hours

**Content:**
- PP-06 in PfCRT cavity (Y01 region, -7.91 kcal/mol)
- PP-15 in all 4 targets (RRS 111.7%, shows breadth)
- PP-11 in PfCRT (A* despite PfDHFR non-binding, interesting pattern)

**Layout:** 2×2 or 3×1 panel  
**Elements for each pose:**
- Protein surface (transparent)
- Ligand (sticks, colored by element)
- Key residues (labels for anchors: Ser252/His223/Asp219 for PfClpP, D451 for PfATP4, etc.)
- Distance annotations for critical interactions

**Tools:** PyMOL or ChimeraX + ray-traced rendering  
**Data source:** V7 docking results (need PDBQT/PDB files)

### Task 2.3: Docking Validation Figure (SI)
**Priority:** HIGH  
**Estimated time:** 1.5 hours

**Content:**
- **Panel A:** Re-docking RMSD
  - 5 alignable ligands, all < 2.0 Å
  - Bar plot with 2.0 Å threshold line
  
- **Panel B:** MMV Malaria Box enrichment
  - ROC-AUC bars for 3 targets: PfDHFR 0.924, PfCRT 0.971, PfATP4 1.000
  - Include error bars/confidence intervals
  
- **Panel C:** DEKOIS PfDHFR (honest negative)
  - ROC curve showing AUC 0.496 (95% CI 0.404-0.589)
  - Highlight near-chance performance

**Tools:** Python matplotlib/seaborn  
**Data source:** BMAD report, V5 exploratory results

### Task 2.4: Target Score Distributions (SI)
**Priority:** MEDIUM  
**Estimated time:** 1 hour

**Content:**
- Violin or box plots for each target (PfDHFR, PfCRT, PfClpP, PfATP4)
- Show distribution of 17-member cohort
- Highlight top candidates (PP-06, PP-15, PP-11, PP-13)
- Show operational threshold (-6.0 kcal/mol) as dashed line

**Tools:** Python seaborn  
**Data source:** SM Table S3 (Vina scores)

### Task 2.5: Scaffold Diversity Figure (SI, optional)
**Priority:** LOW  
**Estimated time:** 2 hours

**Content:**
- Scaffold tree or chemical space projection (t-SNE/UMAP of Morgan fingerprints)
- Highlight Set C members
- Show scaffold recovery from African NP seeds

**Tools:** Python RDKit + matplotlib  
**Data source:** Chemical space analysis from methods

---

## Phase 3: Content Integration from V4/V5 (Est. 2-3 hours)

### Task 3.1: V5 Exploratory Polypharmacology Results
**Priority:** MEDIUM  
**Estimated time:** 1 hour

**Actions:**
1. Add paragraph to Results 3.5 or new 3.6:
   - "Within-target ranking analysis identified PP-06 as the only candidate in the top quartile on all four targets"
   - "The non-dominated Pareto front comprised PP-06, PP-03, PP-05, PP-13, and PP-10"
   - **Important:** Label as "exploratory within-cohort analysis" with appropriate caveats

2. Optional: Add SI figure showing within-target percentile heatmap

**Data source:** BMAD report § ("V5 within-target polypharmacology analysis")  
**Location:** `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/polypharmacology/`

### Task 3.2: Enhanced Scaffold Metrics from V4
**Priority:** LOW  
**Estimated time:** 30 minutes

**Actions:**
1. Add 2-3 sentences to Results 3.1 on scaffold diversity metrics
2. Reference any V4 scaffold analysis figures if adapted

### Task 3.3: Retrosynthesis Context (if relevant)
**Priority:** LOW (JCIM may not require this)  
**Estimated time:** 1 hour

**Decision needed:** Does JCIM audience expect synthesis discussion?
- If yes: Adapt V4 SM_Table_S20 for top candidates
- If no: Skip or minimal mention in Discussion

---

## Phase 4: Editorial Polish (Est. 2 hours)

### Task 4.1: Subsection and Paragraph Transitions
**Priority:** HIGH  
**Estimated time:** 1 hour

**Actions:**
1. Check every Results subsection for smooth lead-in
2. Add transitional sentences between major sections
3. Ensure Methods → Results → Discussion flow is logical
4. Remove remaining "we calculated", "we performed" passive constructions

### Task 4.2: Anti-AI Writing Scan
**Priority:** CRITICAL  
**Estimated time:** 30 minutes

**Actions:**
1. Run grep scan for banned patterns:
   ```bash
   grep -rniP '\b(delve|underscore|illuminate|elucidate|showcase|harness|leverage|scalable|robust|compelling|elevates|transforms|Furthermore,|Moreover,|In addition,|Notably,|Importantly|crucial|pivotal|unprecedented|groundbreaking)\b' manuscript/*.tex
   ```
2. Replace any hits with natural scientific language
3. Check for:
   - Overuse of "significant", "important", "key"
   - Excessive hedging ("may", "might", "could" in every sentence)
   - Repetitive sentence structures

### Task 4.3: Final Consistency Check
**Priority:** HIGH  
**Estimated time:** 30 minutes

**Checklist:**
- [ ] All figure references correct and sequential
- [ ] All table references correct
- [ ] All SI cross-references use `\Cref{SM-...}` format correctly
- [ ] All citations formatted per achemso style
- [ ] All numbers have units (siunitx format)
- [ ] All abbreviations defined at first use
- [ ] Abstract accurately reflects refined content
- [ ] Cover letter updated if needed

---

## Phase 5: Compilation and Verification (Est. 1 hour)

### Task 5.1: LaTeX Compilation
**Actions:**
1. Compile main manuscript:
   ```bash
   pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
   bibtex P1_V7_Integrated_Polypharmacology_RRS
   pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
   pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
   ```
2. Compile SI:
   ```bash
   pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
   bibtex P1_V7_Integrated_Polypharmacology_RRS_SM
   pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
   pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
   ```
3. Check for:
   - 0 fatal errors
   - 0 undefined references
   - 0 missing figures
   - Acceptable overfull/underfull boxes

### Task 5.2: Page Count and Word Count
**Actions:**
1. Verify main text page count (target ~18-20 pages)
2. Check word count (JCIM prefers concise, ~7000-8000 words)
3. Verify SI page count reasonable (~10-20 pages)

### Task 5.3: Final PDF Review
**Actions:**
1. Visual inspection of all figures (resolution, labels, colors)
2. Check table formatting
3. Verify SI cross-references work
4. Check TOC graphic quality

---

## Dependencies and Data Requirements

### Required Data Files (from results/)
1. **For binding pose visualization:**
   - Receptor PDB files (PfDHFR/7F3Y, PfCRT/6UKJ, PfClpP/2F6I, PfATP4/9N10)
   - Ligand PDBQT files for PP-06, PP-15, PP-11 (all 4 targets)
   - Docked pose coordinates

2. **For validation figures:**
   - Re-docking RMSD data
   - MMV enrichment raw scores
   - DEKOIS external validation scores (from V5 exploratory)

3. **For distribution plots:**
   - Raw Vina scores (already in SM tables, can extract)
   - RRS values (already in main tables)

4. **For exploratory polypharmacology:**
   - V5 within-target ranking CSV
   - Pareto front membership data

### Required Graphics Tools
- Python (matplotlib, seaborn, RDKit) ✓ (ML_env mamba)
- PyMOL or ChimeraX (for molecular visualization)
- Vector graphics editor (Inkscape or Illustrator, optional)

---

## Risk Assessment and Mitigation

### Risk 1: Data File Access
**Risk:** Some V7 docking output files may not be easily accessible  
**Mitigation:** 
- Start with figures that use tabulated data (distributions, validation)
- Request specific file paths from author if needed
- Can use V5 data with caveats if V7 poses unavailable

### Risk 2: Time Constraints
**Risk:** Full figure generation may take longer than estimated  
**Mitigation:**
- Prioritize critical figures (workflow schematic, validation)
- Defer optional figures (scaffold diversity) if time-limited
- Can submit with current figures + narrative refinement only

### Risk 3: Scope Creep
**Risk:** Integration of V4/V5 elements may complicate narrative  
**Mitigation:**
- Keep V5 exploratory results clearly labeled and bounded
- Don't force V4 elements if they don't fit naturally
- Focus on refinement over addition

---

## Success Criteria

### Minimum Success (Ready for initial submission)
- [x] Results section rewritten in narrative style
- [x] Discussion expanded to ~1100-1200 words
- [x] Workflow schematic figure added
- [x] One validation figure added (re-docking + MMV + DEKOIS)
- [x] Anti-AI scan clean
- [x] Compiles without errors

### Full Success (Publication-ready)
- [x] All Phase 1-4 tasks complete
- [x] All priority figures generated
- [x] V5 exploratory results integrated with caveats
- [x] Binding pose gallery for top 3 candidates
- [x] All editorial polish complete
- [x] Author-approved final version

---

## Timeline Summary

| Phase | Estimated Time | Priority |
|-------|----------------|----------|
| Phase 1: Narrative | 3-4 hours | CRITICAL |
| Phase 2: Figures | 6-8 hours | HIGH |
| Phase 3: Integration | 2-3 hours | MEDIUM |
| Phase 4: Polish | 2 hours | HIGH |
| Phase 5: Verification | 1 hour | CRITICAL |
| **Total** | **14-18 hours** | - |

**Recommended Execution:**
- **Session 1 (4 hours):** Phase 1 complete
- **Session 2 (4 hours):** Phase 2 Tasks 2.1-2.3 (workflow + poses + validation)
- **Session 3 (3 hours):** Phase 2 Task 2.4, Phase 3, Phase 4
- **Session 4 (2 hours):** Final polish, compilation, verification

---

## Next Immediate Actions

1. **Author Review:** Confirm priorities and approve action plan
2. **Data Access:** Identify and locate all required data files
3. **Begin Phase 1:** Start with Results section narrative rewrite (highest impact)
4. **Parallel Track:** Begin workflow schematic design while narrative work proceeds

---

## Questions for Author

1. **Priority:** Which figures are most critical for submission?
2. **V5 Integration:** Should we include exploratory polypharmacology results with caveats?
3. **Binding Poses:** Are V7 docking output files (PDBQT, PDB) easily accessible?
4. **Mechanistic Depth:** How much structural/mechanistic speculation for top candidates?
5. **Synthesis:** Does JCIM expect retrosynthesis discussion, or is this optional?
6. **Timeline:** What is the target submission date?

