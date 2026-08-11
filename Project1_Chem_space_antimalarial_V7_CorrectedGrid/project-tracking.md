# P1 V7 — Project Tracking

- **Canonical tree:** `Project1_Chem_space_antimalarial_V7_CorrectedGrid/`
- **Parent inputs:** V4 chemical-space/MPO; V5 corrected target-anchored Vina; P2 corrected RRS/polypharmacology.
- **Current phase:** V7 evidence integration completed; automated integrity audit and manuscript rebuild passed, while independent structural review remains pending for any stronger submission-facing structural conclusion.
- **Status:** `EVIDENCE_INTEGRITY_PASS_PENDING_INDEPENDENT_REVIEW`
- **Independent review:** `PENDING_INDEPENDENT_REVIEW`; no self-authorization or bypass exists.
- **V5 evidence boundary:** 17 candidates × 4 target-anchored Vina outputs are complete raw evidence (68/68 composite-gate records), imported as pending/raw evidence, not silently promoted.
- **Molecular mapping:** `MOLECULAR_KEY_VERIFIED_ROW_WISE_CANONICAL_SMILES`; V7 manifest, V5 68-row manifest, P2 source, audit hash, and validator hash are bound in the V4 overlay provenance sidecar.
- **V4 replacement boundary:** uniform 2F6I array `13451`, rescue `13478`, and associated merge/audit jobs `13452`, `13479`, and `13972` have no active scheduler entry in the current query; final accounting states are not recoverable from that query. Audit `13972` rejected the panel (449/484 raw passes, 35 worker failures); partial output is not accepted and no replacement was promoted. V4 requires a distinct review artifact for this 484-centroid panel; the V7 four-target register covers only the V5 17×4 evidence and is not a substitute.
- **RRS boundary:** PfDHFR and PfCRT mutant RRS only; no PfClpP/PfATP4 RRS claim without a validated mutant panel.
- **MD boundary:** historical parent MD systems 201/438/164/214 remain separate from the 17-candidate V7 cohort.
- **Current integrated result (9 August 2026):** 17/17 candidate identities matched by canonical SMILES; 68/68 V5 target-wise Vina records passed the automated geometric gate; consolidated-table values were consistent with raw target CSVs (204 values checked, zero mismatches); the 136-row WT/mutant panel was complete; 82 RRS values were independently recomputed with zero mean/class/value mismatches. Derived outputs include the integrated 17-row metrics table and three regenerated 300-dpi figure files. These are reproducible computational outputs, not experimental or independent structural validation.
- **Manuscript state:** V7 main, SM, and cover letter rebuilt successfully (16, 5, and 1 pages, respectively); RRS eligibility is explicitly sourced from the separate `docking_mutants.csv` panel rather than the four-target V5 WT matrix; figures are synchronized into `manuscript/Graphics/`.
- **Refinement pass (10 August 2026):** main-text citations expanded 5 -> 23 references (resistance literature, African-NP space, SELFIES/PAINS, VAE, fingerprints, scoring-function caveats) using existing `Sao_Chim_Space.bib` entries; **new main-text RRS table** (`tab:rrs_main`, 17 candidates x per-mutant N51I/C59R/S108N/I164L/K76T/K76A + mean, exact values joined programmatically from `v7_candidate_manifest.csv` x `c_rrs_classification.csv`, classes A*:6/B:5/C:5/D:1, mean range 68.2-111.7); **TOC/abstract graphic** `Graphics/p1_v7_toc_graphic.pdf` (funnel + 17x4 Vina heatmap + RRS class bars); Discussion gains a combined RRS+polypharmacology readout. Compile clean: 0 errors, 0 undefined references.
- **Refinement pass 2 (10 August 2026):** added **combined polypharmacology--RRS prioritization table** (`tab:dual_priority`, all 17 candidates: RRS class + mean + $N_{\mathrm{fav}}$ targets with favorable Vina estimate $\leq$ -6.0 kcal/mol + explicit favorable-target list, sorted by $N_{\mathrm{fav}}$ then RRS$_{\mathrm{mean}}$; computed from `results/derived/v7_integrated_candidate_metrics.csv`); new Results subsection `Combining target breadth with mutation tolerance ranks the candidates`; Discussion re-aligned: **PP-15, PP-06, PP-11** are the only A* candidates favorable on all four targets (PP-15 highest cohort RRS mean 111.7%; PP-13 flagged as instructive counterexample — A* but only 2/4 favorable, separating the two axes). Main recompiled 18 p., SM 5 p., cover 1 p., 0 errors, 0 undefined refs.
- **Next gate:** rerun `scripts/v7_validate_evidence.py` after any source change, then provide the updated dossier to an independent reviewer. The register remains unsigned and fail-closed for submission-facing promotion, without blocking pre-submission scientific development.
- **Submission rule:** V7 may be drafted as a computational hypothesis-generating study, but final consensus/RRS/PNS claims require the signed independent-review artifact and accountable author approval.


---

## Enhancement Pass 1: V4 Resource Integration (11 January 2026)

**Objective:** Integrate physicochemical properties, drug-likeness, and ADMET content from V4 into V7 manuscript.

**Completed:**
- ✅ Created 3 SM tables: physicochemical properties (S4), drug-likeness compliance (S5), ADMET profile (S6)
- ✅ Enhanced main text: Introduction (accessibility gap), Methods (grid specifications), Results (cross-refs), Discussion (computational efficiency)
- ✅ Added Stumpfe2012 citation for activity cliffs
- ✅ Full compilation: 25 pages main, 10 pages SM, 0 errors, 0 undefined references

**Files created:**
- `scripts/v7_generate_physicochemical_table.py`
- `scripts/v7_generate_druglikeness_table.py`
- `scripts/v7_generate_admet_summary_table.py`
- `manuscript/tables/sm_table_physicochemical.tex`
- `manuscript/tables/sm_table_druglikeness.tex`
- `manuscript/tables/sm_table_admet_summary.tex`

**Documentation:** `P1_V7_FINAL_COMPLETION.md`

---

## Enhancement Pass 2: V5 Validation Integration (11 January 2026)

**Objective:** Integrate docking validation content (DEKOIS, MMV enrichment, redocking) from V5 into V7 manuscript.

**Completed:**
- ✅ Created 3 validation tables: enrichment validation, redocking validation, validation datasets summary
- ✅ Added SM Section S11: Docking validation and protocol assessment (4 subsections with narrative)
- ✅ Added main text cross-reference in Methods validation subsection
- ✅ Renumbered previous SM S11 → S12
- ✅ Full compilation: 25 pages main, 13 pages SM (+3 from Enhancement Pass 1), 0 errors, 0 undefined references

**Key validation metrics documented:**
- DEKOIS 2.0 external benchmark (PfDHFR): ROC-AUC 0.450 [0.367, 0.531] — near-random baseline, Vina-only
- MMV Malaria Box enrichment (Vina+DiffDock consensus): ROC-AUC 0.924-1.000 across 3 targets
- Redocking success: 4/5 ligands (80%) with RMSD < 2.0 Å

**Files created:**
- `manuscript/tables/sm_table_enrichment_validation.tex`
- `manuscript/tables/sm_table_redocking_validation.tex`
- `manuscript/tables/sm_table_validation_datasets.tex`

**Documentation:** `P1_V7_V5_INTEGRATION_COMPLETED.md`

**Status:** V7 manuscript contains comprehensive validation documentation spanning external benchmarks, positive-control enrichment, and pose reproduction. Transparent reporting of both capabilities (consensus strategy, redocking accuracy) and limitations (DEKOIS baseline, proxy ligands) meets JCIM methodological standards.

**Deferred optional enhancements:**
- Binding mode figure (V5 SM Figure S15 adaptation)
- Synthetic accessibility discussion (V5 SM Table S20 metrics)
- Rationale: Core validation integration is complete and sufficient for submission. Optional enhancements can be added during revision if requested by reviewers.

---

**Current manuscript state (11 January 2026):**
- Main text: 25 pages, 0 errors, 0 undefined references
- Supporting Information: 13 pages, 0 errors, 0 undefined references
- Sections: 12 SM sections (S1-S12), complete validation documentation (S11)
- Tables: 6 SM tables (S3 Vina matrix, S4 physicochemical, S5 drug-likeness, S6 ADMET, plus 3 validation tables in S11)
- Figures: Chemical space coverage, targetwise profile, RRS profiles, TOC graphic
- Citations: Complete bibliography with Bauer2013 (DEKOIS) reference
- Status: **Ready for JCIM submission** with comprehensive validation and transparent limitation reporting


---

## V7 Promotion to Canonical JCIM Submission Version (11 January 2026)

**Phase 1: Document Updates** ✅ COMPLETE

**Actions Completed:**
- ✅ AGENTS.md updated (V7 canonical, V6 moved to archive)
- ✅ submission_ACS_P1V7/ package created (main PDF, SM PDF, bibliography, auxiliary files)
- ✅ Promotion documentation created:
  - P1_V7_PROMOTION_PLAN.md
  - P1_V7_PROMOTION_SUMMARY.md
  - submission_ACS_P1V7/SUBMISSION_MANIFEST_V7.md
  - V7_PROMOTION_COMPLETE.md

**Phase 3: Pre-Submission Requirements** ⚠️ IN PROGRESS

**Actions Completed This Session:**
- ✅ Cover letter created: `manuscript/Cover_Letter_P1_V7.tex` (2 pages, compiled successfully)
- ✅ Pre-submission instructions: `PRE_SUBMISSION_INSTRUCTIONS.md` (complete guide with templates)
- ✅ Phase 3 status summary: `PHASE3_STATUS_SUMMARY.md` (tracking document)

**CRITICAL BLOCKERS (User Input Required):**
1. ⚠️ Add ORCID iDs for 5 authors (~15 min) — Requires actual ORCID values
2. ⚠️ Add funding acknowledgment (~5 min) — Requires funding details or "No funding" statement
3. ⚠️ Final author review of 38 pages (~2 hours) — Requires human review

**Estimated Time to Submission-Ready:** 2-3 hours

**V7 Final Metrics:**
- Main: 25 pages, 0 errors ✅
- SM: 13 pages, 0 errors ✅
- Cover Letter: 2 pages, compiled ✅
- SM Sections: 12 (S1-S12) ✅
- SM Tables: 9 (Vina matrix + 3 physicochemical + 3 validation + 2 RRS/cross-metric) ✅
- ORCIDs: 0/5 added ⚠️
- Funding: Not added ⚠️

**V7 Enhancements Over V6:**
- Validation documentation: +3 tables, +1 SM section (S11)
- Physicochemical characterization: +3 tables (S4-S6)
- Narrative quality: Results rewritten, Discussion expanded +125%
- Methodological rigor: Grid specifications, efficiency analysis
- Net page increase: +6 main (19→25), +8 SM (5→13)

**Next Steps:**
See `PRE_SUBMISSION_INSTRUCTIONS.md` for detailed templates and procedures.

**Status:** ⚠️ **Phase 3 in progress — 3 critical user actions required before submission**


---

## 2026-01-11: MPO and DiffDock Content Integration (Option 3 - Hybrid)

### Objective
Integrate V4's MPO and DiffDock mathematical formulations into V7 using Option 3 (Hybrid) approach - brief SM section with key equations that cross-references V4 companion manuscript for full validation.

### Implementation Details

**New SM Section S10:** "Multi-parameter optimization framework for upstream candidate selection"

**Added Content:**
1. **7 Mathematical Equations:**
   - Total MPO score (5 components + polypharmacology bonus)
   - Vina binding affinity (35% weight, min-max scaling)
   - **DiffDock confidence (25% weight, logistic sigmoid transformation)**
   - QED drug-likeness (20% weight, direct use)
   - ADMET composite (15% weight, 11-endpoint average)
   - Lipinski penalty (5% weight, proportional to violations)
   - Polypharmacology bonus (0.05 per target, capped +0.10)

2. **Component descriptions** and endpoint lists (11 ADMET parameters)
3. **Weight rationale:** Why 35/25/20/15/5 split (60% combined docking weight)
4. **Scope statement:** MPO as upstream filter, not Set-C validation
5. **Cross-reference** to companion manuscript for full methodology:
   - Centroid-based workflow (484 → 76 → 53 → 19,913)
   - Sensitivity analysis (25 perturbations, Spearman ρ = 0.792)
   - External validation (DEKOIS, MMV Malaria Box)

**Section Renumbering:**
- Old S10 (Reproducibility) → New S11
- Old S11 (Docking validation) → New S12 (subsections S12.1-S12.4)

**Main Text Update:**
- Cross-reference updated: "Section S11" → "Section S12" (validation section pointer)

### Compilation Results
- **Main:** 25 pages, 0 errors ✅
- **SM:** 17 pages (+4 from initial 13), 0 errors ✅
- **All citations resolved:** Swanson2024, Hughes2008, Gleeson2008, Lipinski2004 ✅
- **All cross-references working** ✅

### Key Design Choices (V7's Cautious Framing Preserved)
- Language: "computational prioritization evidence," "does not validate Set-C quality"
- Past tense: "candidates **were selected**" (selection criterion, not quality claim)
- NO terms: "secondary hits," "high-quality leads," "validated"
- Cross-reference companion manuscript for full validation
- Avoided duplicating DEKOIS/MMV content already in S12

### Files Modified
1. `manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.tex`
   - New Section S10 (~1.5 pages)
   - Renumbered S10→S11, S11→S12
2. `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`
   - Updated validation cross-reference (S11→S12)

### Documentation Created
- `V4_MPO_DIFFDOCK_CONTENT_ANALYSIS.md` - Detailed comparison V4 vs V7
- `V7_MPO_DIFFDOCK_INTEGRATION_COMPLETE.md` - Implementation summary

### Status
**COMPLETE** - Ready for final submission pending:
1. Regenerate submission package PDFs (include new S10)
2. Update SUBMISSION_MANIFEST_V7.md (SM page count 13→17)
3. Final author review of new S10 content

### Impact
- Transparent documentation of Set-C selection methodology
- DiffDock confidence transformation now explicitly defined
- MPO framework mathematically documented with cross-reference to full validation
- Maintains V7's target-anchored narrative (not library-screening focus)
- Evidence boundary preserved: computational prioritization, NOT biological validation
