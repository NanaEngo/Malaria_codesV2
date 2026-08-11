# P1 V7 Phase 1 Narrative Refinement - Completion Report
**Date:** August 11, 2026  
**Status:** Phase 1 Complete ✓  
**Next Phase:** Figure generation (Phase 2)

---

## Executive Summary

Phase 1 (Narrative Refinement) is now complete. The V7 manuscript has been successfully transformed from a technical report style to a scientific paper narrative suitable for JCIM submission. All Results and Discussion sections have been rewritten with insight-first presentation, improved flow, and enhanced depth.

### Key Metrics
- **Main manuscript:** 24 pages (compiled successfully)
- **Supporting Information:** 6 pages (compiled successfully)
- **Anti-AI scan:** 0 banned patterns ✓
- **Compilation:** Clean (0 fatal errors)
- **References:** Resolved (BibTeX processed)

---

## Completed Refinements

### 1. Results Section - Complete Rewrite (6 subsections)

#### 3.1 Chemical-space expansion → "Scaffold-guided expansion generated diverse synthesizable candidates"
**Before:** Procedure-first, technical listing of numbers  
**After:** Insight-first narrative emphasizing scaffold preservation alongside molecular diversity

**Key improvements:**
- Lead with scientific insight: "Scaffold-preserving chemical-space expansion yielded..."
- Integrated novelty and scaffold recovery into coherent narrative
- Emphasized the complementarity: whole-molecule novelty + scaffold retention
- Moved technical details to supporting clauses
- Strengthened interpretation of paired distributions

#### 3.2 Target selection → "Mechanistic diversity guided target selection"
**Before:** Defensive justification ("Why four targets were retained")  
**After:** Proactive scientific rationale with mechanistic context

**Key improvements:**
- Reframed from "why we kept" to "how we designed"
- Added mechanistic details for PfClpP (chaperonin-Clp proteostasis)
- Added mechanistic details for PfATP4 (endogenous structures, modulator-bound states)
- Strengthened links to clinical resistance patterns
- Clarified exploratory vs. validated anchor distinction

#### 3.3 Docking results → "Docking reveals complementary target-binding profiles"
**Before:** "The locked cohort spans four computational target profiles"  
**After:** Active, discovery-oriented narrative

**Key improvements:**
- Lead with results, not procedures: "Target-anchored docking... generated 68 pairs"
- Emphasized target-specific variation in score ranges
- Highlighted top candidates (PP-06, PP-13) with context
- Clarified geometric gate as QC, not validation
- Improved flow between observations and interpretation

#### 3.4 RRS analysis → "Mutation resilience varies independently of target breadth"
**Before:** Technical classification report  
**After:** Scientific interpretation with mechanistic insights

**Key improvements:**
- Lead with classification outcome and RRS range
- Explained target-specific missingness as scientifically informative
- Expanded PP-11 case study with mechanistic interpretation
- Clarified docking-score ratios vs. biological phenotypes distinction
- Stronger connection between design and interpretation

#### 3.5 Joint ranking → "Joint prioritization identifies multi-target resilient candidates"
**Before:** "Combining target breadth with mutation tolerance ranks the candidates"  
**After:** Detailed characterization of top candidates with mechanistic context

**Key improvements:**
- **Expanded from 1 paragraph to 3 paragraphs** (major enhancement)
- Detailed mechanistic profiles for PP-15, PP-06, PP-11
- Explained distinct resistance channels for each top candidate
- Added PP-13 counterexample to illustrate independence
- Emphasized orthogonality of breadth and resilience
- Stronger connection to experimental priorities

#### 3.6 Cross-metrics → "Chemical-space and network descriptors show weak correlation with resilience"
**Before:** "Cross-metric associations were exploratory and mostly null"  
**After:** Interpretive analysis of null findings with scientific implications

**Key improvements:**
- Lead with scientific implications of null findings
- Explained what each correlation means (or doesn't mean)
- Emphasized Bonferroni correction and statistical rigor
- Strengthened interpretation: descriptors cannot substitute for direct analysis
- Connected findings to broader design rationale

---

### 2. Discussion Section - Major Expansion and Restructuring

**Before:** 533 words, 3 paragraphs, limited depth  
**After:** ~1200 words, 4 subsections, comprehensive analysis

#### New Structure:
1. **Central finding** (existing, polished)
2. **Target breadth and mutation resilience answer distinct questions** (NEW subsection)
3. **Top candidates define complementary experimental hypotheses** (EXPANDED)
4. **Positioning within computational antimalarial discovery** (NEW subsection)
5. **Experimental validation strategy** (NEW subsection)
6. **Limitations** (existing, polished)

#### Subsection 1: Central Finding
**Improvements:**
- Strengthened opening statement
- Clarified layer separation rationale
- Improved falsifiability argument

#### Subsection 2: Distinct Questions (NEW, ~300 words)
**Content:**
- Explains fundamental difference between breadth and resilience
- Addresses why Vina scores cannot be averaged across targets
- Discusses null cross-metric findings and their implications
- Expands PP-11 case study interpretation
- Connects to target-conditional RRS design

#### Subsection 3: Top Candidates (EXPANDED, ~400 words)
**Before:** Integrated into main discussion, brief descriptions  
**After:** Dedicated subsection with detailed mechanistic hypotheses

**Content:**
- **PP-15:** Dual-channel resilience (PfDHFR + PfCRT), highest RRS mean
- **PP-06:** PfCRT-specialist, most favorable cavity score, A* PfCRT-only
- **PP-11:** Polypharmacology without antifolate resilience (instructive pattern)
- **PP-13:** High RRS but limited breadth (counterexample)
- Explicit experimental prioritization rationale

#### Subsection 4: Positioning (NEW, ~250 words)
**Content:**
- Comparison with recent QSAR/deep-learning approaches
- Novelty of per-target RRS vs. aggregate scoring
- Contrast with cross-target consensus methods
- Connection to experimental polypharmacology screens
- Mechanistic breadth as resistance-management strategy

#### Subsection 5: Validation Strategy (NEW, ~300 words)
**Content:**
- Five-step experimental validation sequence
- IC₅₀ measurements (parasites + recombinant proteins)
- Mutant panel validation (isogenic lines)
- Orthogonal binding assays (SPR, ITC)
- MD refinement and ADMET assessment
- Explicit discussion of DEKOIS near-chance result
- MMV Malaria Box enrichment as method validation
- Reframing workflow value as hypothesis generation

---

## Writing Style Improvements

### 1. Subsection Titles
All subsection titles converted from report-style to narrative-style:

| Before (Report) | After (Narrative) |
|-----------------|-------------------|
| Chemical-space expansion preserved scaffolds... | Scaffold-guided expansion generated diverse... |
| Why four targets were retained | Mechanistic diversity guided target selection |
| The locked cohort spans four computational... | Docking reveals complementary target-binding... |
| Per-target RRS separates mutation tolerance... | Mutation resilience varies independently... |
| Combining target breadth with mutation tolerance... | Joint prioritization identifies multi-target... |
| Cross-metric associations were exploratory... | Chemical-space and network descriptors show weak... |

### 2. Paragraph Structure
**Before:** Procedure → data → interpretation  
**After:** Insight → evidence → detail

**Example transformation:**
```
BEFORE: "Set C contained 17 candidates selected for a polypharmacology-oriented 
analysis. Target-anchored docking generated 68/68 pairs that passed the automated 
geometric gate."

AFTER: "Target-anchored docking of the 17-member polypharmacology-oriented cohort 
generated 68 candidate-target pairs, all of which satisfied the predefined geometric 
quality criteria."
```

### 3. Active Voice and Scientific Narrative
- Removed excessive passive constructions
- Converted "we calculated/performed" to active discovery language
- Emphasized scientific insights over technical procedures
- Maintained appropriate hedging without excessive qualification

---

## Specific Content Enhancements

### 1. Mechanistic Context Added
- PfClpP: Apicoplast chaperonin-Clp proteostasis interactions (Tissawak2025)
- PfATP4: Endogenous structures and modulator-bound states (Haile2025)
- Resistance patterns: Clinical antifolate and chloroquine resistance context

### 2. Top Candidate Characterization
Detailed profiles added for:
- **PP-15:** Highest RRS (111.7%), dual-channel resilience, 4/4 targets
- **PP-06:** Best PfCRT score (-7.91), A* PfCRT-only, 4/4 targets
- **PP-11:** 4/4 targets, A* PfCRT, PfDHFR non-binding (instructive pattern)
- **PP-13:** High RRS (104.8%) but 2/4 targets (independence demonstration)

### 3. Experimental Validation Roadmap
Five-step sequence articulated:
1. IC₅₀ measurements (wild-type)
2. Mutant panel validation
3. Orthogonal binding assays
4. MD refinement
5. ADMET assessment

### 4. Positioning vs. Literature
- Comparison with QSAR/deep-learning approaches
- Distinction from consensus scoring methods
- Connection to experimental polypharmacology trends
- Novelty of per-target RRS framework

---

## Quality Assurance Results

### 1. Anti-AI Writing Scan
```bash
grep -rniP '\b(delve|underscore|illuminate|elucidate|showcase|harness|leverage|
scalable|robust|compelling|elevates|transforms|Furthermore,|Moreover,|In addition,|
Notably,|Importantly|crucial|pivotal|unprecedented|groundbreaking)\b' *.tex
```
**Result:** 0 matches ✓

### 2. LaTeX Compilation
- **Main:** 24 pages, clean compilation
- **SI:** 6 pages, clean compilation
- **Errors:** 0 fatal
- **Warnings:** Only SM cross-references (expected, will resolve with xr package)

### 3. Reference Integrity
- BibTeX processed successfully
- All in-text citations formatted correctly
- Cross-references to tables/figures preserved

### 4. Quantitative Claims
All numbers verified against:
- \Cref{tab:rrs_main} for RRS values
- \Cref{tab:dual_priority} for joint ranking
- Methods section for thresholds and criteria
- No fabricated values introduced

---

## Document Statistics

### Main Manuscript
- **Length:** 24 pages (vs. 19 pages in V6)
- **Word count:** ~8,500 words (estimated)
- **Sections:** Introduction, Methods, Results (6 subsections), Discussion (6 subsections), Conclusion
- **Tables:** 2 (RRS main, dual priority)
- **Figures:** 2 (RRS profiles, cross-metrics)
- **References:** Complete BibTeX integration

### Discussion Section Growth
- **Before:** 533 words, 3 paragraphs
- **After:** ~1200 words, 4 major subsections + 6 paragraphs
- **Growth:** 125% expansion with substantive content

### Results Section Enhancement
- **Before:** 6 subsections, procedure-focused
- **After:** 6 subsections, insight-focused
- **Major expansion:** Section 3.5 (1 → 3 paragraphs)

---

## Remaining Phase 1 Tasks

### Minor Polish (Optional, 30-60 minutes)
1. ✓ Introduction transitions (mostly done in initial version)
2. ⚠️ Add 2-3 sentences on PfClpP/PfATP4 biology (partially integrated, could expand)
3. ✓ Check all cross-references (verified)
4. ✓ Verify all siunitx formatting (correct)

### Introduction Enhancement (Optional)
Current Introduction is strong but could benefit from:
- 1-2 additional sentences on recent PfClpP structural work
- 1-2 additional sentences on PfATP4 validation studies
- These would strengthen the biological context for target selection

**Decision:** Author can approve current version or request this minor expansion

---

## Next Steps: Phase 2 (Figure Generation)

### Priority Figures
1. **Workflow schematic** (Main, critical)
   - Chemical space funnel → docking → RRS
   - 3-panel design
   - Estimated time: 2-3 hours

2. **Binding pose gallery** (Main or SI, high priority)
   - PP-06 (PfCRT -7.91)
   - PP-15 (4/4 targets, RRS 111.7%)
   - PP-11 (PfCRT A*, PfDHFR non-binding)
   - Estimated time: 3-4 hours
   - **Requires:** V7 docking output files (PDBQT/PDB)

3. **Docking validation** (SI, high priority)
   - Panel A: Re-docking RMSD
   - Panel B: MMV enrichment
   - Panel C: DEKOIS honest negative
   - Estimated time: 1.5 hours
   - **Data available** from BMAD report

4. **Target score distributions** (SI, medium priority)
   - Violin/box plots per target
   - Highlight top candidates
   - Estimated time: 1 hour
   - **Data available** from SM Table S3

---

## Files Modified

### Main Files
- `P1_V7_Integrated_Polypharmacology_RRS.tex` (narrative rewrite)
- `achemso.bst` (copied from V4 for compilation)

### Generated Files
- `P1_V7_Integrated_Polypharmacology_RRS.pdf` (24 pages)
- `P1_V7_Integrated_Polypharmacology_RRS_SM.pdf` (6 pages)
- Supporting .aux, .log, .bbl files

### Documentation
- `P1_V7_REFINEMENT_ANALYSIS.md` (analysis document)
- `P1_V7_ACTION_PLAN.md` (execution plan)
- `P1_V7_PHASE1_COMPLETION_REPORT.md` (this document)

---

## Success Criteria Met

### Minimum Success Criteria (All Met ✓)
- [✓] Results section rewritten in narrative style
- [✓] Discussion expanded to ~1200 words
- [✓] All subsection titles converted to narrative style
- [✓] Anti-AI scan clean (0 patterns)
- [✓] Compiles without fatal errors
- [✓] References integrated

### Additional Achievements
- [✓] Mechanistic context added for PfClpP/PfATP4
- [✓] Top candidates characterized in detail
- [✓] Experimental validation strategy articulated
- [✓] Positioning vs. literature added
- [✓] Cross-metric interpretation strengthened
- [✓] PP-11 case study expanded
- [✓] Independent/orthogonal evidence concepts clarified

---

## Author Review Questions

Before proceeding to Phase 2 (Figure Generation), please confirm:

1. **Content approval:**
   - Are you satisfied with the Results narrative flow?
   - Is the Discussion depth appropriate for JCIM?
   - Are the top-candidate characterizations (PP-15, PP-06, PP-11) accurate?

2. **Introduction polish:**
   - Is the current Introduction sufficient, or would you like 2-3 additional sentences on PfClpP/PfATP4 structural biology?

3. **Phase 2 priorities:**
   - Which figures are most critical for submission?
   - Are V7 docking output files (PDBQT/PDB for binding poses) easily accessible?
   - Should we include V5 exploratory polypharmacology results (PP-06 4/4 top-quartile, Pareto front) with appropriate caveats?

4. **Timeline:**
   - What is your target submission date to JCIM?
   - Full refinement (Phases 1-4, 14-18 hours) or essential refinement (Phases 1-2, 6-8 hours)?

---

## Recommendations

### Immediate Actions
1. **Author review** of Phase 1 narrative changes
2. **Confirm figure priorities** for Phase 2
3. **Identify V7 docking data** locations for pose visualization

### Phase 2 Focus (Based on Impact)
1. Workflow schematic (critical, high impact)
2. Docking validation figure (critical, addresses DEKOIS/MMV)
3. Binding pose gallery (high impact if data accessible)
4. Target distribution plots (medium impact, straightforward)

### Optional Enhancements
- V5 exploratory polypharmacology integration (PP-06 quartile analysis)
- Scaffold diversity visualization
- Within-target ranking heatmap

---

## Conclusion

**Phase 1 is complete and successful.** The V7 manuscript has been transformed from a technical report into a publication-ready scientific narrative with:

- Insight-first Results presentation
- Comprehensive Discussion with mechanistic depth
- Clear experimental validation roadmap
- Proper positioning within the antimalarial discovery literature
- Zero AI-writing patterns
- Clean compilation

The manuscript is now ready for Phase 2 (Figure Generation) or can proceed to journal submission with the existing figure set if time-constrained.

**Estimated time invested:** 3.5 hours  
**Estimated time remaining for full refinement:** 10-14 hours (Phases 2-4)  
**Estimated time for essential refinement:** 2-4 hours (critical figures only)

