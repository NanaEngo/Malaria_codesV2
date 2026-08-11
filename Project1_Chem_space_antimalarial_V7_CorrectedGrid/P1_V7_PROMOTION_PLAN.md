# P1 V7 Promotion to Canonical JCIM Submission Version

**Date:** 2026-01-11  
**Action:** Promote V7 from working version to canonical JCIM submission version  
**Previous Canonical:** V6 (August 10, 2026)  
**New Canonical:** V7 (January 11, 2026)

---

## Rationale for V7 Promotion

### V7 Enhancements Over V6

1. **Comprehensive Validation Documentation** (V5 Integration)
   - External benchmark validation (DEKOIS 2.0)
   - Positive-control enrichment (MMV Malaria Box)
   - Redocking validation with complete RMSD values
   - Transparent reporting of both capabilities and limitations

2. **Enhanced Physicochemical Characterization** (V4 Integration)
   - Complete physicochemical properties table
   - Drug-likeness compliance documentation
   - ADMET profile summary

3. **Improved Narrative Quality**
   - Results section rewritten from report-style to scientific narrative
   - Discussion expanded from 533 to ~1200 words
   - Anti-AI writing patterns eliminated

4. **Methodological Rigor**
   - Grid box specifications for all 4 targets
   - Computational efficiency discussion (99.3% cost reduction)
   - Enhanced cross-referencing between main text and SM

### Compilation Status

- **Main Text:** 25 pages, 0 errors, 0 undefined references ✅
- **Supporting Information:** 13 pages, 0 errors, 0 undefined references ✅
- **Total SM Sections:** 12 (S1-S12)
- **Total SM Tables:** 9 tables (Vina matrix + 3 physicochemical + 3 validation + 2 RRS/cross-metric)
- **Bibliography:** Complete with all required references ✅

---

## Promotion Execution Plan

### Phase 1: Document Updates (Priority 1)

#### 1.1. Update AGENTS.md
- [ ] Change header line from "V6 SOUMISSION JCIM PRÊT" to "V7 SOUMISSION JCIM PRÊT"
- [ ] Update P1 status table to reflect V7 as canonical
- [ ] Add V7 entry in project status table
- [ ] Move V6 to "archive versions" with V4/V5
- [ ] Update "Manuscrit V7" row with current status

#### 1.2. Update BMAD_Q1_DATA_ANALYSIS_REPORT.md
- [ ] Search for all V6 references
- [ ] Update manuscript version references to V7
- [ ] Verify data authority claims reference V7 files

#### 1.3. Create submission_ACS_P1V7/ Package
- [ ] Create directory structure
- [ ] Copy main PDF: `P1_V7_Integrated_Polypharmacology_RRS.pdf`
- [ ] Copy SM PDF: `P1_V7_Integrated_Polypharmacology_RRS_SM.pdf`
- [ ] Copy bibliography: `Sao_Chim_Space.bib`
- [ ] Copy auxiliary files: `.bbl`, `.aux` for cross-references
- [ ] Create package manifest

### Phase 2: Cross-Reference Verification (Priority 2)

#### 2.1. Internal Cross-References
- [ ] Verify all `\Cref{}` commands resolve in main text
- [ ] Verify all `\Cref{SM-*}` commands resolve to SM
- [ ] Check figure references point to existing graphics
- [ ] Check table references resolve correctly

#### 2.2. External Project References
- [ ] Search all markdown files for V6 mentions
- [ ] Update or clarify V6 → V7 where canonical version is implied
- [ ] Preserve V6 mentions where they refer to historical archive

### Phase 3: Submission Readiness (Priority 3)

#### 3.1. Author Metadata
- [ ] Add ORCID iDs for all 5 authors
- [ ] Verify email addresses current
- [ ] Verify affiliations current

#### 3.2. Funding Acknowledgment
- [ ] Add funding section if applicable
- [ ] Or add "No funding" statement

#### 3.3. Cover Letter
- [ ] Review existing cover letter structure
- [ ] Update to reference V7 enhancements
- [ ] Compile and verify

#### 3.4. Final Quality Checks
- [ ] Run final compilation check (main + SM)
- [ ] Verify page counts acceptable for JCIM
- [ ] Check all figures are 300+ DPI
- [ ] Verify all tables format correctly
- [ ] Check bibliography formatting (ACS style)

---

## Execution Order

**Immediate (Step 1):**
1. Update AGENTS.md P1 section (V6 → V7 canonical)
2. Create submission_ACS_P1V7/ package
3. Update project-tracking.md with promotion status

**Next Session (Step 2):**
4. Update BMAD references
5. Search and update cross-references across markdown files
6. Create V7 promotion summary document

**Pre-Submission (Step 3):**
7. Add ORCIDs to manuscript
8. Add funding acknowledgment
9. Update/create cover letter
10. Final quality verification

---

## Success Criteria

- [x] V7 manuscript compiles cleanly (0 errors)
- [x] V7 contains all V4 + V5 enhancements
- [ ] AGENTS.md reflects V7 as canonical
- [ ] submission_ACS_P1V7/ package created
- [ ] All cross-document references updated
- [ ] ORCIDs added (pre-submission)
- [ ] Funding added (pre-submission)
- [ ] Cover letter ready (pre-submission)

---

## Rollback Plan (If Needed)

If issues arise during promotion:
1. AGENTS.md rollback: Change canonical back to V6
2. Keep V7 as "enhanced working version"
3. Apply V7 enhancements to V6 instead (Option 1 fallback)

---

## Files to Track

**Updated:**
- `AGENTS.md` — P1 section, canonical version
- `BMAD_Q1_DATA_ANALYSIS_REPORT.md` — manuscript version references
- `Project1_Chem_space_antimalarial_V7_CorrectedGrid/project-tracking.md` — add promotion record

**Created:**
- `submission_ACS_P1V7/` directory
- `P1_V7_PROMOTION_SUMMARY.md` (after completion)

**Preserved (No Changes):**
- All V6 files remain as archive
- V4, V5 archive directories unchanged

---

**Status:** Ready to execute Phase 1 (Document Updates)
