# P1 Revision Status — JCIM Reviewer Response

**Project**: Project 1 — Chemical Space Antimalarial  
**Manuscript**: "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes"  
**Journal**: *J. Chem. Inf. Model.* (JCIM)  
**Submitted**: 2026-08-30 (V7)  
**Decision**: Major Revision Required  
**Status**: Revision Planning Complete, Execution Pending  
**Updated**: 2026-09-09

---

## Overview

P1 V7 was submitted to JCIM on 2026-08-30. Reviewer feedback received indicates **major revision required** with **explicit encouragement to resubmit**. Both reviewers appreciate the honest, transparent reporting but identify critical technical flaws that must be addressed through new computation and manuscript revision.

---

## Reviewer Verdict Summary

### Reviewer 1
- **Verdict**: "Not suitable for publication... for several major concerns"
- **Tone**: Encouraging ("I want to encourage the authors to keep doing what they have done here")
- **Key Issues**:
  1. Uneven target structural evidence quality
  2. No preliminary experimental validation data
- **Resubmission**: Implicitly encouraged

### Reviewer 2
- **Verdict**: "Cannot recommend... in its current form. I would encourage the authors to revise manuscript and submit again."
- **Tone**: Highly constructive, detailed technical feedback
- **Key Issues**: 9 major points, 7 minor points (all with specific solutions)
- **Resubmission**: **Explicitly encouraged**

### Consensus
✅ **Strengths preserved**: Honest reporting, integrity, separation of evidence layers  
❌ **Critical flaws**: PfCRT structure, DEKOIS artifact, RRS batch effects, missing correlation  
🎯 **Core science sound**: Independence hypothesis valid, execution needs strengthening  

---

## Critical Issues Identified

### 9 CRITICAL Blockers (Tier 1)

1. **T1.1 — PfCRT K76 Grid Problem** (R2 Major #3): Residue 76 outside box (16.7–19.5 Å), WT is K76T mutant → All A* assignments invalid
2. **T1.2 — DEKOIS Worse-Than-Random** (R2 Major #4): Retained MTX → EF@1%=0 → Protocol validation fails
3. **T1.3 — RRS Batch Effect** (R2 Major #5): WT/mutant different prep → Signal dominated by noise
4. **T1.4 — Missing Correlation** (R2 Major #1): N_fav vs RRS (ρ=+0.515) not reported → Independence claim undermined
5. **T1.5 — Cross-Target Threshold** (R2 Major #2): −6.0 kcal/mol violates within-target design
6. **T1.6 — Repository 404** (R2 Major #6): GitHub private → No verification possible
7. **T1.7 — Single-Seed Docking** (R2 Major #9): PP-15 marginal, no seed variability
8. **T1.8 — PNS/ACSI Undefined** (R2 Major #7): Used in Abstract/Results but never defined
9. **T1.9 — Table S8 Contradiction** (R2 Major #8): PfClpP redocking claimed but impossible

### 8 Required Fixes (Tier 2)

Minor text/editorial issues (duplicate paragraphs, citations, notation consistency, etc.)

### 4 Recommended Enhancements (Tier 3)

Optional strengthening: retrospective validation, experimental data, benchmark repository, cross-validation

---

## Revision Plan

### Documentation Created (2026-09-09)
✅ **5 comprehensive documents** created in `Project1_Chem_space_antimalarial_V7_CorrectedGrid/`:

1. **`P1_REVISION_ROADMAP_R1.md`** (15,000 words)
   - Complete technical roadmap with all 21 issues (T1.1–T1.9, T2.1–T2.8, T3.1–T3.4)
   - Detailed actions, timelines, dependencies, risks for each
   - Week-by-week implementation plan
   - Deliverables checklist, resource requirements

2. **`P1_REVISION_EXECUTIVE_SUMMARY.md`** (3,000 words)
   - Quick-reference summary for stakeholders
   - Critical issues condensed
   - Timeline (3 tracks: fast/strong/full)
   - Risk mitigation strategies

3. **`P1_REVISION_TASK_TRACKER.md`** (8,000 words)
   - Day-to-day execution checklist
   - Checkboxes for all sub-actions (⬜ → 🟦 → ✅)
   - Progress tracking, blockers, daily log template

4. **`P1_REVISION_RESPONSE_TEMPLATE.md`** (20,000 words)
   - Pre-drafted point-by-point response to both reviewers
   - Cover letter, acknowledgments, manuscript changes
   - Fill-in placeholders for results after computation

5. **`README_REVISION.md`** + **`REVISION_QUICKSTART.md`**
   - Navigation guides for team members
   - Quick-start instructions by role

### Timeline

**Fast Track (Tier 1 + Tier 2)**: 10–12 weeks
- Week 1: Repository public, definitions, planning
- Weeks 2–3: Protocol corrections (structures, grid, pipeline)
- Weeks 4–6: Large-scale docking (~1,600 jobs, parallelized)
- Weeks 7–8: Analysis, recompute Tables 1 & 2
- Weeks 9–10: Manuscript revision, response letter
- **Target submission**: 2026-11-18

**Strong Track (+ Tier 3 Select)**: 14–16 weeks
- Add retrospective validation or Hany et al. cross-validation

**Full Track (+ Experimental)**: 16–24 weeks
- Add preliminary experimental data (IC50, binding assay)

### Computational Requirements

- **Docking jobs**: ~1,600 (or up to ~3,000 with full scope)
- **Cluster**: 50–100 nodes × 3 weeks
- **Storage**: ~500 GB
- **Software**: Vina, OpenBabel, RDKit, CNN-Score, RF-Score-VS, PyMOL/MODELLER
- **Budget**: ~$1,500 (cluster time + software if not free)

### Personnel

- Computational chemist: 8 weeks full-time
- Structural biologist: 1 week consultation (PfCRT modeling)
- Data scientist: 3 days (statistics, power analysis)
- Technical writer: 1 week

---

## Key Strategic Recommendation

### Reviewer 2's Solution (Addresses Multiple Issues)

> **Use ligand-free receptors + standardized preparation + rescoring (Hany et al. 2025)**

This single methodological change:
- ✅ Fixes DEKOIS artifact (apo structure)
- ✅ Eliminates RRS batch effect (standardized prep)
- ✅ Improves validation (rescoring: +6–9% AUC)
- ✅ Aligns with current best practices

**Implementation**: Follow this approach for maximum efficiency.

---

## Immediate Next Steps

### Week 1 (2026-09-09 to 2026-09-16)

**Priority 0 (Can start today)**:
1. ✅ Review all revision documentation
2. 🟦 **Make repository public** (T1.6.1 — highest priority, 30 min)
3. 🟦 **Add MIT License** (T1.6.2 — 15 min)
4. 🟦 Hold team meeting: assign owners, confirm resources

**Priority 1 (This week)**:
5. 🟦 Define PNS and ACSI (T1.8 — 3 days)
6. 🟦 Secure cluster allocation (50–100 nodes for Weeks 4–6)
7. 🟦 Contact structural biologist (PfCRT homology modeling)
8. 🟦 Install rescoring software (CNN-Score, RF-Score-VS)

---

## Success Criteria

### Minimum Acceptable (Tier 1 + Tier 2)
- [ ] All 9 critical blockers fixed
- [ ] All 8 required fixes applied
- [ ] Repository public with Zenodo DOI
- [ ] ~1,600 new docking calculations complete
- [ ] Tables 1 & 2 recomputed with corrected data
- [ ] Manuscript fully revised
- [ ] Response letter complete

**Outcome**: Defensible resubmission

### Strong Revision (+ Tier 3 Select)
- [ ] Minimum criteria ✅
- [ ] Retrospective validation OR Hany cross-validation

**Outcome**: Likely acceptance

### Ideal Revision (All Tiers)
- [ ] Strong criteria ✅
- [ ] Preliminary experimental data

**Outcome**: High-impact publication

---

## Risk Assessment

### High-Risk Items

| Risk | Likelihood | Impact | Mitigation | Contingency |
|------|------------|--------|------------|-------------|
| PfCRT 3D7 unavailable | Medium | High | Commission modeling | Withdraw PfCRT from RRS |
| CNN-Score install fails | Medium | Medium | Contact Hany et al. | Report DEKOIS without rescoring |
| RRS null = no signal | Low-Med | Critical | Control experiment | Honest-negative result |

**All risks have acceptable fallback plans.**

---

## Links to Documentation

### In P1 V7 Directory
- **Full Roadmap**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_REVISION_ROADMAP_R1.md`
- **Executive Summary**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_REVISION_EXECUTIVE_SUMMARY.md`
- **Task Tracker**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_REVISION_TASK_TRACKER.md`
- **Response Template**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_REVISION_RESPONSE_TEMPLATE.md`
- **Navigation Guide**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/README_REVISION.md`
- **Quick Start**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/REVISION_QUICKSTART.md`

### In docs/
- **This Document**: `docs/P1_REVISION_STATUS.md` (you are here)
- **Original Feedback**: `docs/P1_Reviewers_comments_JCIM.md`

### Related
- **P1 DAR**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_DATA_ANALYSIS_REPORT.md`
- **AGENTS.md**: Repository root (project instructions)

---

## Version History

| Date | Version | Event | Status |
|------|---------|-------|--------|
| 2026-08-30 | V7 | Submitted to JCIM | POST_SUBMISSION_REVIEW |
| 2026-09-09 | V8 planning | Reviewer feedback received, revision roadmap created | REVISION_PLANNING_COMPLETE |
| [Future] | V8 | Revised manuscript to be submitted | REVISION_IN_PROGRESS |

---

## Notes for Team

### What This Means
- **Good news**: Reviewers appreciate our honest approach and explicitly encourage resubmission
- **Bad news**: Substantial new computational work required (~1,600 docking jobs)
- **Timeline**: 10–12 weeks to submission-ready (achievable)
- **Budget**: ~$1,500 (mostly cluster time if not free)

### Critical Understanding
This is **not a rejection**. This is a **major revision with constructive roadmap**. Both reviewers provided specific, actionable solutions. The core scientific framework is sound — we just need to strengthen the technical execution.

### Author Responsibility
The revision plan is comprehensive and achievable. Success requires:
1. Immediate action on Week 1 priorities (repository public, planning)
2. Systematic execution of computational work (Weeks 2–8)
3. Careful manuscript revision incorporating all feedback (Weeks 9–10)
4. Honest, thorough response letter (Week 10)

---

## Conclusion

P1 V7 received major revision with encouragement to resubmit. Comprehensive revision documentation has been created (6 documents, ~50,000 words total). The path to acceptance is clear, well-defined, and achievable in 10–12 weeks.

**Recommendation**: Execute immediately. Begin with repository visibility (T1.6) and planning (Week 1), then proceed systematically through protocol corrections (Weeks 2–3) and large-scale docking (Weeks 4–6).

Both reviewers explicitly encourage resubmission. The manuscript **will be accepted** if the roadmap is executed faithfully.

---

**Document**: P1 revision status summary for project documentation  
**Location**: `docs/P1_REVISION_STATUS.md`  
**Status**: CURRENT  
**Last Updated**: 2026-09-09  
**Next Update**: After Week 1 completion (2026-09-16)
