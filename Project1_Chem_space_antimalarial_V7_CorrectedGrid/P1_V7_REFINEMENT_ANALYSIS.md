# P1 V7 Manuscript Refinement Analysis
**Date:** August 11, 2026  
**Target Journal:** Journal of Chemical Information and Modeling (JCIM)  
**Current Status:** V7 - Pre-submission refinement phase

---

## Executive Summary

The V7 manuscript presents an integrated computational workflow connecting African-natural-product-inspired chemical space to target-specific docking and mutation-resilience analysis. The manuscript is well-structured and scientifically sound, but needs refinement from "technical report" style to "scientific paper" narrative for JCIM submission.

### Key Strengths
- Clear separation of evidence layers (chemical space → docking → RRS)
- Honest reporting of computational limitations (DEKOIS AUC 0.45, exploratory status)
- Target-specific analysis avoiding uncalibrated cross-target averaging
- Complete provenance and reproducibility documentation

### Areas Requiring Refinement
1. **Narrative flow**: Transition from technical reporting to scientific storytelling
2. **Figure integration**: Enhance visual communication with additional graphics
3. **Discussion depth**: Expand mechanistic interpretation and biological context
4. **Comparison with V4/V5**: Integrate successful elements from previous versions

---

## Detailed Analysis

### 1. Manuscript Structure Assessment

#### Current Structure (V7)
- **Abstract:** Clear, bounded, appropriate caveats ✓
- **Introduction:** Strong framing, well-referenced
- **Methods:** Comprehensive, reproducible
- **Results:** Data-rich, but report-like presentation
- **Discussion:** Good but could be deeper
- **SI:** Adequate, well-organized

#### Comparison with V4
V4 focused on chemical-space expansion and 484-centroid docking. Key elements:
- Stronger emphasis on scaffold diversity metrics
- More detailed docking validation protocols
- Richer visual presentation of binding modes

#### Comparison with V5
V5 introduced 17×4 target matrix and methodological refinements:
- Four-target panel rationale more developed
- Within-target ranking and Pareto analysis
- Exploratory polypharmacology metrics

### 2. Missing or Underutilized Visual Elements

#### Available Graphics (V7 Graphics/)
1. `p1_v7_chemical_space_coverage.pdf` ✓ (used in SI)
2. `p1_v7_exploratory_metric_relationships.pdf` ✓ (used as Fig in main)
3. `p1_v7_rrs_mutation_profiles.pdf` ✓ (used as Fig in main)
4. `p1_v7_targetwise_profile_summary.pdf` ✓ (used in SI)
5. `p1_v7_toc_graphic.pdf` ✓ (abstract)

#### Missing Visual Elements (can be generated from BMAD or V4/V5)
1. **Main text additions:**
   - Chemical-space workflow schematic (funnel visualization)
   - Representative binding poses for top candidates (PP-06, PP-15, PP-11)
   - MPO score distribution across the library
   - Scaffold diversity tree/network
   
2. **SI additions:**
   - Docking validation results (re-docking RMSD, MMV enrichment)
   - Target structure overlays showing anchor residues
   - Per-target score distributions (violin plots or box plots)
   - PNS/ACSI distributions
   - Molecular weight / LogP distributions for Set C

#### Graphics Available from V4/V5 (can be adapted)
- V4: SM_Figure_S15_top10_binding_modes.pdf (binding pose gallery)
- V5: Within-target ranking figures
- V5: Geometric QC visualizations

### 3. Narrative Refinement Needs

#### Section-by-Section Analysis

**Introduction (currently strong, minor refinements)**
- ✓ Good framing of resistance as systems problem
- ✓ African NP chemical richness established
- **Enhance:** Add 1-2 sentences on recent PfClpP/PfATP4 biology discoveries
- **Enhance:** Strengthen transition between paragraphs 2 and 3

**Methods (comprehensive but technical)**
- ✓ Reproducible, detailed protocols
- **Refine:** Reduce jargon in chemical-space funnel description
- **Refine:** Add schematic figure to visualize workflow
- **Enhance:** Emphasize novelty of per-target RRS approach

**Results (data-rich but report-like)**
- **Problem:** Subsection titles read like report headers
- **Refine:** Convert to narrative flow with topic sentences
- **Refine:** Lead with scientific insight, not technical detail
- **Example current:** "The locked cohort spans four computational target profiles"
- **Example refined:** "Computational docking revealed diverse target profiles across the polypharmacology-oriented cohort"

**Discussion (good foundation, needs depth)**
- ✓ Honest about computational limitations
- ✓ Clear about non-interchangeability of metrics
- **Enhance:** Add mechanistic speculation for top candidates
- **Enhance:** Connect to recent antimalarial discovery trends
- **Enhance:** Discuss experimental validation strategy more explicitly
- **Add:** Comparison with related computational studies

### 4. Specific Content Enhancements

#### From BMAD Report - Available Results
1. **V5 within-target polypharmacology analysis** (exploratory but citable):
   - PP-06: only candidate in top quartile on all 4 targets
   - Pareto front: PP-06, PP-03, PP-05, PP-13, PP-10
   - Location: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/polypharmacology/`

2. **DEKOIS external validation** (honest negative result):
   - ROC-AUC 0.496 (95% CI 0.404-0.589) - near chance
   - Constrains PfDHFR interpretation but doesn't invalidate workflow
   - Location: V5 exploratory/external_validation/dekois_pf_dhfr/

3. **MMV Malaria Box enrichment** (positive result):
   - ROC-AUC 0.924-1.000 across three targets
   - Already mentioned but could be visualized

4. **Re-docking validation**:
   - 5/5 alignable ligands RMSD < 2.0 Å
   - 100% success rate
   - Could add visual comparison figure

#### From V4 - Successful Elements
1. Richer scaffold analysis
2. Top-10 binding mode gallery (SM_Figure_S15)
3. Retrosynthesis analysis (SM_Table_S20)

#### From V5 - Methodological Advances
1. Within-target ranking framework
2. Pareto analysis visualization
3. Geometric QC figures

---

## Recommended Refinement Actions

### Phase 1: Narrative Enhancement (Priority 1)
1. **Abstract**: Already excellent, minor polish only
2. **Introduction**:
   - Add transition sentence between para 2-3
   - Strengthen recent target biology citations (Tissawak2025, Haile2025)
3. **Methods**:
   - Add workflow schematic (chemical space → docking → RRS)
   - Reduce jargon in first two subsections
4. **Results**:
   - Rewrite subsection leads to narrative style
   - Move technical details to supporting clauses
   - Lead with insights, not procedures
5. **Discussion**:
   - Add 2-3 paragraphs on mechanistic insights for top candidates
   - Expand experimental validation roadmap
   - Add paragraph comparing to recent computational antimalarial studies

### Phase 2: Figure Additions (Priority 2)
1. **Main text additions:**
   - Figure 1: Workflow schematic (replaces or precedes current figures)
   - Figure: Representative binding poses for PP-06, PP-15, PP-11 (can use V4 gallery style)
   
2. **SI additions:**
   - Docking validation figure (re-docking RMSD + MMV enrichment bars)
   - Per-target score distribution figure (violin or box plots)
   - Scaffold diversity visualization

### Phase 3: Content Integration (Priority 3)
1. **From V5 exploratory results** (with appropriate caveats):
   - Within-target quartile analysis (PP-06 4/4 top quartile)
   - Pareto front membership
   
2. **From V4 successful elements**:
   - Binding mode gallery for top candidates
   - Enhanced scaffold metrics

3. **From BMAD**:
   - External validation figures (DEKOIS, MMV)
   - Re-docking validation visual

### Phase 4: Editorial Polish (Priority 4)
1. Check all subsection titles for narrative style
2. Ensure smooth transitions between sections
3. Remove remaining "report-like" phrasing
4. Strengthen topic sentences
5. Final anti-AI scan and prose polish

---

## Figure Generation Plan

### Required New Figures

1. **Workflow Schematic** (Main, Figure 1)
   - Chemical space funnel (396 ANP + 454 synthetics → 65,856 → 19,913)
   - Target-anchored docking (4 targets, geometric gates)
   - Per-target RRS calculation
   - Style: Clean, publication-quality flowchart

2. **Binding Pose Gallery** (Main or SI)
   - PP-06 in PfCRT cavity (-7.91 kcal/mol)
   - PP-15 in PfATP4 region (-7.02 kcal/mol)
   - PP-11 in all 4 targets (4/4 favorable)
   - Style: 2x2 or 3x1 panel with protein surface/key residues

3. **Docking Validation** (SI)
   - Panel A: Re-docking RMSD (5 ligands, all < 2.0 Å)
   - Panel B: MMV enrichment bars (PfDHFR 0.924, PfCRT 0.971, PfATP4 1.000)
   - Panel C: DEKOIS result (honest negative, AUC 0.496)
   - Style: Clean bar/scatter plots with error bars

4. **Target Score Distributions** (SI)
   - Violin or box plots for each target
   - Show 17-member cohort distribution
   - Highlight top candidates
   - Style: Consistent color scheme across targets

### Figures to Adapt from V4/V5

1. **V4 SM_Figure_S15**: Binding mode gallery (adapt for V7 top candidates)
2. **V5 within-target ranking**: Can be simplified/adapted if needed
3. **V5 geometric QC**: Already good, minor style updates only

---

## Writing Style Refinement Examples

### Example 1: Subsection Title
**Current (report-style):**
> "3.2 The locked cohort spans four computational target profiles"

**Refined (narrative-style):**
> "3.2 Target-anchored docking reveals diverse binding profiles"

### Example 2: Results Lead
**Current (procedure-first):**
> "Set C contained 17 candidates selected for a polypharmacology-oriented analysis. Target-anchored docking generated 68/68 pairs that passed the automated geometric gate."

**Refined (insight-first):**
> "All 68 candidate-target pairs in the polypharmacology-oriented cohort passed geometric quality criteria, revealing diverse binding profiles across the four mechanistically distinct targets. Score ranges varied by target, from −4.63 to −7.91 kcal/mol, with the most favorable estimates observed for PP-06 in the PfCRT cavity (−7.91) and PP-13 in the PfATP4 region (−7.57)."

### Example 3: Methods Description
**Current (jargon-heavy):**
> "Similarity-based expansion and SELFIES perturbation were followed by structure validation, deduplication, and PAINS filtering, producing 65,856 unique molecules."

**Refined (accessible):**
> "Chemical space exploration combined similarity-based expansion with SELFIES perturbation to generate structural diversity while maintaining synthesizable cores. After validation, deduplication, and filtering for pan-assay interference compounds (PAINS), the library comprised 65,856 unique molecules."

---

## Integration with Previous Versions

### Elements to Preserve from V6
- Current integrated RRS approach ✓
- Per-target analysis avoiding cross-target means ✓
- Honest reporting of computational limitations ✓
- Complete provenance ✓

### Elements to Add from V5
- Within-target quartile analysis (PP-06 4/4 top quartile) *
- Pareto front identification *
- Exploratory polypharmacology metrics *
(*with "exploratory" caveat)

### Elements to Add from V4
- Enhanced scaffold diversity metrics
- Binding mode visualizations
- Retrosynthesis context (if relevant for JCIM)

---

## Timeline and Dependencies

### Immediate Actions (can start now)
1. Narrative refinement of Results section
2. Discussion expansion
3. Figure planning and specification

### Requires Data Access
1. Binding pose visualization (need PDB/PDBQT files from V7 results)
2. Additional distribution plots (need raw score files)
3. Validation figure generation (need V5 exploratory data)

### Requires Author Decision
1. Whether to include V5 exploratory polypharmacology results
2. Level of mechanistic speculation for top candidates
3. Emphasis on experimental validation roadmap

---

## Quality Checklist

### Scientific Content
- [ ] All numbers traced to BMAD or results files
- [ ] Caveats appropriate for computational study
- [ ] Claims bounded and falsifiable
- [ ] Reproducibility complete

### Narrative Quality
- [ ] Abstract reads as scientific paper, not report
- [ ] Introduction flows naturally
- [ ] Results emphasize insights over procedures
- [ ] Discussion connects to broader antimalarial context
- [ ] No AI-writing patterns (delve, leverage, etc.)

### Visual Communication
- [ ] All figures publication-quality (300 dpi)
- [ ] Color schemes accessible (colorblind-safe)
- [ ] Captions self-contained
- [ ] Figure references integrated into text flow

### JCIM Requirements
- [ ] Format follows achemso template ✓
- [ ] References complete and formatted ✓
- [ ] SI appropriately detailed ✓
- [ ] Cover letter highlights novelty

---

## Next Steps

1. **Review this analysis** with the author for priorities
2. **Generate missing figures** based on priority ranking
3. **Refine narrative** section by section
4. **Integrate enhancements** from V4/V5 with appropriate caveats
5. **Final polish** and anti-AI scan
6. **Compile and verify** all changes

