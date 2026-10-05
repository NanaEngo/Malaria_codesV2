# P7 Manuscript — Project Tracking Spine

**Created:** 2026-09-24  
**Journal:** RSC Digital Discovery (provisional)  
**Paper Type:** Full research article  
**Central Finding:** Quantum molecular encoding captures ANP stereochemistry — performance vs. classical fingerprints TBD

---

## Status

**Active Loop:** L2 — DRAFT  
**Beat Counter:** 5  
**Model:** Claude Sonnet 4.5  
**Status:** Introduction ✅ · Methods ✅ · Results ✅ · Discussion ✅ · Conclusion ✅ · HPO canonical re-run ✅ — Phase 6 canonical result recorded (AUC 0.8468 ± 0.0209; 05 Oct 2026). Abstract now unblocked. HPO full 50-trial run continuing in background (PID 2011099). Pending: Abstract, IBM hardware section, final review passes.

---

## Sprint Plan

### Phase 1: Evidence Gathering (L1) ✅ COMPLETE
- [x] Read Phase 1 results (ECFP4 baseline, quantum kernel test)
- [x] Create analysis ledger entries
- [x] Document quantum kernel technical demo
- [x] Identify missing results → resolved via Phase 4/5 execution
- [x] Create claims-evidence matrix

### Phase 2: Drafting (L2) ✅ COMPLETE (core sections)
- [x] Methods section (complete, 8 subsections)
- [x] Introduction section (complete, ANP-centered narrative)
- [x] **Results section** (complete, 05 Oct 2026 — 5 tables, 4 subsections, all numbers from DAR)
- [x] **Discussion section** (complete, 05 Oct 2026 — 6 subsections, 5 limitations)
- [x] **Conclusion section** (complete, 05 Oct 2026 — Scenario B, HPO gate, hardware outlook)
- [ ] Abstract (write after Phase 6 HPO results, as finding may update)
- [ ] Cover letter (final step)

### Phase 3: Figures & SI
- [ ] Figure 1: workflow schematic
- [ ] Figure 2: QFE circuit diagram
- [ ] Figure 3: Phase 4 ROC curves (5 folds)
- [ ] Figure 4: ablation bar chart (4q / 6q / 8q)
- [ ] Figure 5: Phase 5 scaffold-split AUC + gradient norms
- [ ] SI: gradient norm distributions, per-fold tables

### Phase 4: Review & Finalize
- [ ] Execute Phase 6 HPO (p7_phase6_qfe_optuna_hpo.py) — incorporate results
- [ ] IBM Quantum hardware section (Phase 6B)
- [ ] Independent review passes
- [ ] Anti-AI scan
- [ ] Audit checklist
- [ ] Cover letter

---

## Claims–Evidence Matrix

| Claim | Evidence (Ledger ID) | Citation | Status |
|-------|---------------------|----------|--------|
| QFE achieves AUC 0.933 on P1 Set A (LOO-CV) | DAR Phase 1 PoC | — | ✅ COMPUTED |
| ECFP4-MLP achieves AUC 0.833 on P1 Set A | DAR Phase 1 PoC | — | ✅ COMPUTED |
| QFE 4q AUC 0.8474 ± 0.0129 on P3 sub n=1000 | DAR Phase 4 | — | ✅ COMPUTED |
| 4-qubit optimal vs 6q/8q (ablation) | DAR Phase 4 ablation | — | ✅ COMPUTED |
| QFE AUC 0.7831 under scaffold split (n=10K) | DAR Phase 5 | — | ✅ COMPUTED |
| Barren plateau marginal at n=8K (8.24%) | DAR Phase 5 gradient diag. | — | ✅ COMPUTED |
| No barren plateau at n=800 (0.0%) | DAR Phase 4 gradient diag. | — | ✅ COMPUTED |
| Scenario B: competitive, not superior | DAR Phase 4–5 | — | ✅ CONFIRMED |
| HPO (12 trials): best 2-fold AUC 0.8487 (trial 7: 4q, CZ, hidden=64) | DAR Phase 6 HPO; `results/phase4_hpo/qfe_hpo_study.db` | — | ✅ EXPLORATORY |
| HPO canonical 5-fold re-run (trial 7): AUC 0.8468 ± 0.0209 | DAR Phase 6; `results/phase4_hpo/qfe_4q_d1_cz_hpo_canonical_cv5_summary.json` | — | ✅ CANONICAL |
| CZ variant equiv. to RZZ; Phase 4 4q-rzz remains optimal | DAR Phase 6 decision gate (Δ = −0.0006, below 0.8574 threshold) | — | ✅ CONFIRMED |
| IBM hardware noise-affected AUC | NOT_COMPUTED | — | ⏳ Phase 6B pending |

---

## Missing Inputs

### Now Resolved (previously blocked)
- [x] **Full QFE results across scales** — Phases 1, 4, 5 all complete (DAR canonical)
- [x] **Statistical comparison** — Scenario B confirmed at all scales
- [x] **ANP metadata** — Fsp³ 0.217, ACSI 0.213, 10 stereocenters, 16 synthetic analogues
- [x] **Ablation study** — 4q optimal documented
- [x] **Phase 6 HPO canonical result** — trial 7 best config (4q, CZ, hidden=64) AUC 0.8468 ± 0.0209 (5-fold CANONICAL, 05 Oct 2026); decision gate BELOW; Phase 4 4q-rzz confirmed optimal

### Still Pending
1. **Full HPO 50-trial completion** (running in background, PID 2011099)
   - Will provide importance plots and history — supplements manuscript §HPO
   - Does NOT block abstract or any current claims (canonical re-run already done)
2. **IBM Quantum hardware run** (Phase 6B)
   - Required for hardware-realistic performance claim
3. **Manuscript figures** (5 main figures + SI — PDFs already generated)
4. **Abstract** (NOW UNBLOCKED — write from current canonical results)

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

**Last Updated:** 2026-10-05 — Results, Discussion, Conclusion drafted from DAR canonical data; Sprint Plan updated; Claims–Evidence Matrix resolved; Phase 6 HPO script ready to execute
**Previous:** 2026-09-24 — Introduction complete; Methods complete; portfolio review applied
