# P7 Manuscript — Project Tracking Spine

**Created:** 2026-09-24  
**Journal:** RSC Digital Discovery (provisional)  
**Paper Type:** Full research article  
**Central Finding:** Quantum molecular encoding captures ANP stereochemistry — performance vs. classical fingerprints TBD

---

## Status

**Active Loop:** L2 — DRAFT  
**Beat Counter:** 3  
**Model:** Claude Sonnet 4.5  
**Status:** Methods complete; Introduction complete; waiting for full quantum results (LED-PENDING-001) before Results/Discussion

---

## Sprint Plan

### Phase 1: Evidence Gathering (L1)
- [ ] Read Phase 1 results (ECFP4 baseline, quantum kernel test)
- [ ] Create analysis ledger entries
- [ ] Interpret ECFP4 AUC = 0.467 (worse than random)
- [ ] Document quantum kernel technical demo (3 molecules)
- [ ] Identify missing results (17-molecule quantum comparison)
- [ ] Create claims-evidence matrix

### Phase 2: Drafting (L2)
- [x] Methods section (complete, 8 subsections)
- [x] Introduction section (complete, ANP-centered narrative)
- [ ] Results section (waiting for LED-PENDING-001: 17-molecule quantum kernel)
- [ ] Discussion (waiting for quantum vs. classical comparison)
- [ ] Abstract (needs central finding from Results)
- [ ] Cover letter (final step)

---

## Claims–Evidence Matrix

| Claim | Evidence (Ledger ID) | Citation | Status |
|-------|---------------------|----------|--------|
| ECFP4 baseline on P1 Set A | LED-001 | - | ✓ |
| Quantum kernel technical feasibility | LED-002 | Boy et al. 2025 | ✓ |
| Quantum vs. ECFP4 comparison (17 mol) | PENDING | - | ⏳ |
| ANP stereochemistry preservation | PENDING | - | ⏳ |
| Scaffold generalization | NOT_COMPUTED | - | Future |

---

## Missing Inputs

### Critical (Blocks Manuscript)
1. **Full 17-molecule quantum kernel results**
   - Status: Computation running or pending?
   - ETA: Unknown
   - Blocker: Cannot write Results/Discussion without this

2. **Statistical comparison**
   - Paired test: quantum vs. ECFP4
   - Effect size
   - Interpretation: advantage/equivalence/underperformance

### Important (Strengthens Manuscript)
3. **ANP metadata analysis**
   - ACSI distribution
   - Fsp³ distribution
   - Correlation with quantum kernel performance

4. **Kernel target alignment**
   - Does quantum kernel correlate with activity labels?

### Optional (Future Phases)
5. P3 benchmark (19,849 molecules)
6. Ablation studies
7. IBM Quantum hardware validation

---

## Journal Requirements (RSC Digital Discovery)

**Format:**
- LaTeX template: RSC article template
- Word limit: ~8,000 words (main text)
- Abstract: ~200 words
- References: Vancouver style (numbered)
- Figures: Vector format (PDF/SVG preferred)
- SI: Unlimited length

**Checklist:**
- [ ] Download RSC template
- [ ] Install RSC .bst file
- [ ] Check figure specifications
- [ ] Review author guidelines

---

## File Map

```
manuscript/
├── project-tracking.md          [this file]
├── outputs/
│   ├── analysis/
│   │   └── analysis-ledger.md   [L1 - complete]
│   ├── literature/
│   │   └── literature-map.md    [L1 - pending]
│   └── critical-reviews/        [L3 - future]
├── sections/
│   ├── abstract.tex             [L2 - pending results]
│   ├── introduction.tex         [L2 - ✓ complete]
│   ├── methods.tex              [L2 - ✓ complete]
│   ├── results.tex              [L2 - pending LED-PENDING-001]
│   └── discussion.tex           [L2 - pending results]
├── figures/                     [L1/L2]
└── main.tex                     [L2 - ready for compilation test]
```

---

## Review Log

*No reviews yet — manuscript not drafted*

---

## Notes

- **Data Quality Issue:** ECFP4 AUC = 0.467 (worse than random 0.5)
  - Possible causes: Class imbalance (15 inactive / 2 active), label quality, or genuinely difficult dataset
  - Must interpret honestly in ledger
  
- **Quantum Results:** Only 3-molecule technical demo available
  - Need full 17-molecule kernel to make claims
  - Current state: proof of technical feasibility only

- **ANP Identity:** Must emphasize African Natural Products throughout
  - High Fsp³, stereochemistry, 3D complexity
  - This is the scientific USP

- **Introduction Complete (2026-09-24):**
  - 5 paragraphs, ANP-centered narrative
  - Framing: ANP structural challenge → classical blind spots → QML opportunity → three research questions
  - Honest-negative commitment explicit
  - All citations marked [CITATION NEEDED] for L1 literature review
  - Aligns with P7_CENTRAL_QUESTIONS_V2609.md

- **Template Update — ChemRxiv Format (2026-09-24):**
  - **From:** ACS achemso format (journal-specific)
  - **To:** P2 ChemRxiv preprint format (standard article class, 11pt, A4, 1-inch margins)
  - **Author block:** Manual title + ORCID icons + affiliations (identical to P2 V2609C)
  - **Packages:** siunitx, cleveref, booktabs, tikz, natbib (numbers, sort&compress)
  - **Bibliography:** unsrtnat style (numbered, unsorted by author)
  - **Layout:** Single column, clean preprint format suitable for ChemRxiv/arXiv
  - **Compilation:** ✅ Successful (6 pages, 343 KB)
  - **Rationale:** Preprint-first strategy; convert to RSC template only if accepted

- **Portfolio Review & Refinements (2026-09-24):**
  - **Reviewer:** article-writing + scientific-writing skills
  - **Verdict:** ✅ PASS with minor refinements; quality matches P1/P2 standards
  - **Anti-AI scan:** 0 banned patterns detected
  - **Applied Priority 1 refinements:**
    1. ✅ Added P1 provenance (17 from 65,856 library, MPO ≥ 0.70, RRS across 4 targets)
    2. ✅ Added computational cost (13 hr single-thread, 1.6 hr with 8-core parallelization)
    3. ✅ Added activity label provenance (P1 docking thresholds, LED{001} reference)
    4. ✅ Added ECFP4 baseline context (P1 scaffold 69.3%, P3 AUC 0.9475)
    5. ✅ Quantified sample sizes with `\num{}` (siunitx formatting)
  - **Pending Priority 2 (after Results):**
    6. ⏳ Create TikZ TOC graphic (workflow diagram like P2)
    7. ⏳ Add LED citations in Methods (trace all numbers to analysis ledger)
  - **Applied Priority 3 (L1 loop):**
    8. ✅ Resolved 14/16 citation placeholders (WHO 2024, Gilmer2017 GNN, Morris2019 1-WL, Havlicek2019 quantum kernels, Tilly2022 quantum advantage, Lovering2009 Fsp³, Cao2022 QML, plus P1/P2/P3/P5 internal refs)
    9. ⏳ Add "drug resistance" keyword (pending)
    10. ⏳ Resolve AfroDb citation (2 placeholders remain)
  - **Document:** `outputs/critical-reviews/portfolio-review-P7.md` (7 sections, detailed refinements)
  - **Bibliography:** 20 entries added to `references.bib` (8 external, 4 internal P1-P5, 8 base)
  - **Compilation:** ✅ 7 pages, 361 KB PDF, 2 citation placeholders remaining

---

**Last Updated:** 2026-09-24  
**Next Action:** Wait for LED-PENDING-001 (17-molecule quantum kernel) before drafting Results
