# P1 JCIM Revision Documentation — Navigation Guide

**Project**: Project 1 — Chemical Space Antimalarial / Polypharmacology-Oriented RRS Framework  
**Manuscript**: "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis"  
**Journal**: *J. Chem. Inf. Model.* (JCIM)  
**Status**: Major Revision Required — Resubmission Encouraged  
**Created**: 2026-09-09

---

## 📋 Document Overview

This directory contains comprehensive documentation for responding to JCIM reviewer feedback. Use this navigation guide to access the appropriate document for your role and purpose.

### Core Documents

| Document | Purpose | Primary Audience | Status |
|----------|---------|------------------|--------|
| **`P1_REVISION_ROADMAP_R1.md`** | Complete technical roadmap with all issues, actions, timelines | PI, computational lead | ✅ COMPLETE |
| **`P1_REVISION_EXECUTIVE_SUMMARY.md`** | Quick-reference summary of critical issues and timeline | All team members, administrators | ✅ COMPLETE |
| **`P1_REVISION_TASK_TRACKER.md`** | Day-to-day task checklist with progress tracking | Project manager, daily execution | ✅ INITIALIZED |
| **`P1_REVISION_RESPONSE_TEMPLATE.md`** | Draft point-by-point response to reviewers | PI, manuscript writer | ⚠️ TEMPLATE |
| **`README_REVISION.md`** | This navigation guide | New team members, collaborators | ✅ CURRENT |

### Supporting Documents

| Document | Purpose |
|----------|---------|
| **`docs/P1_Reviewers_comments_JCIM.md`** | Original reviewer feedback (source material) |
| **`P1_DATA_ANALYSIS_REPORT.md`** | Current V7 canonical results and provenance |
| **`P1_DEVELOPMENT_PHASE.json`** | Authorization register for pre-submission work |

---

## 🎯 Quick Start by Role

### **If you are the PI / Project Lead:**
1. **Start here**: `P1_REVISION_EXECUTIVE_SUMMARY.md` (10-minute read)
2. **Then review**: `P1_REVISION_ROADMAP_R1.md` (comprehensive technical details)
3. **Decision needed**: Approve execution plan and authorize cluster resources
4. **Next steps**: Assign task owners in `P1_REVISION_TASK_TRACKER.md`

### **If you are the Computational Chemist / Executor:**
1. **Start here**: `P1_REVISION_TASK_TRACKER.md` (your daily checklist)
2. **Technical details**: `P1_REVISION_ROADMAP_R1.md` (specific actions for each task)
3. **Original feedback**: `docs/P1_Reviewers_comments_JCIM.md` (understand reviewer intent)
4. **Progress tracking**: Update checkboxes in tracker daily

### **If you are a Collaborator / Structural Biologist:**
1. **Start here**: `P1_REVISION_EXECUTIVE_SUMMARY.md` → T1.1 (PfCRT modeling request)
2. **Technical specs**: `P1_REVISION_ROADMAP_R1.md` → T1.1.1 (detailed requirements)
3. **Timeline**: Week 1–3 consultation needed

### **If you are the Manuscript Writer:**
1. **Start here**: `P1_REVISION_RESPONSE_TEMPLATE.md` (draft responses)
2. **Fill in placeholders**: After computational tasks complete (Week 8+)
3. **Cross-reference**: `P1_REVISION_ROADMAP_R1.md` for exact text revisions

### **If you are New to the Project:**
1. **Start here**: This document (you are here!)
2. **Understand current state**: `P1_DATA_ANALYSIS_REPORT.md`
3. **Understand feedback**: `docs/P1_Reviewers_comments_JCIM.md`
4. **Understand plan**: `P1_REVISION_EXECUTIVE_SUMMARY.md`

---

## 📊 Revision Status at a Glance

| Aspect | Current State | Target State |
|--------|---------------|--------------|
| **Verdict** | Major revision required | Resubmission encouraged by both reviewers ✅ |
| **Critical Issues** | 9 blockers identified | All must be resolved for submission |
| **Computational Work** | V7 submitted (2026-08-30) | ~1,600 new docking jobs required |
| **Timeline** | Not started | 10–12 weeks to submission-ready (Tier 1+2) |
| **Repository** | Private (404 error) | Must be public with DOI immediately ⚠️ |
| **Key Fixes** | PfCRT K76, DEKOIS artifact, RRS batch effect | Require new structures + re-docking |

---

## 🔥 Immediate Actions Required (Week 1)

### Priority 0 (Can Start Today)
1. ✅ **Read this guide** and familiarize yourself with document structure
2. 🟦 **Make repository public** (T1.6.1 — 30 minutes, enables reviewer verification)
3. 🟦 **Add MIT License** (T1.6.2 — 15 minutes)
4. 🟦 **Define PNS/ACSI** (T1.8 — 3 days, enables correlation reproduction)
5. 🟦 **Secure cluster allocation** (50–100 nodes × 3 weeks starting Week 4)

### Priority 1 (Week 2–3 Setup)
6. ⬜ **Contact structural biologist** for PfCRT 3D7 homology modeling consultation
7. ⬜ **Install rescoring software** (CNN-Score, RF-Score-VS — may have dependencies)
8. ⬜ **Prepare apo PfDHFR structure** (T1.2.1 — strip MTX from 7F3Y)

---

## 📈 Timeline Overview

```
Week 1 (Now):        Repository + definitions + planning
Weeks 2–3:           Protocol corrections (structures, grid, pipeline)
Weeks 4–6:           Large-scale docking (~1,600 jobs, parallelized)
Weeks 7–8:           Analysis & recomputation
Weeks 9–10:          Manuscript revision + response letter
Weeks 11–12:         Optional enhancements (retrospective validation)
Target submission:   2026-11-18 (10 weeks) or 2026-12-02 (12 weeks)
```

---

## 🎓 Understanding the Reviewer Feedback

### What Reviewers Liked ✅
- Honest reporting (no score-to-affinity conversion, no cross-target composites)
- Transparent null results
- Clear separation of evidence layers
- Sound scientific instinct (independence hypothesis)
- Genuine accessibility case

### Critical Flaws Identified ❌
1. **PfCRT K76 grid problem**: Residue 76 outside docking box, wild-type is already K76T mutant
2. **DEKOIS artifact**: Retained methotrexate → EF@1% = 0 (worse than random)
3. **RRS batch effect**: Wild-type/mutant prep inconsistency dominates signal
4. **Missing correlation**: N_fav vs RRS_mean (ρ=+0.515) not reported
5. **Cross-target threshold**: −6.0 kcal/mol cutoff violates within-target design
6. **Repository 404**: No data verification possible
7. **Single-seed docking**: PP-15 marginal, seed variability not assessed
8. **PNS/ACSI undefined**: Used in Abstract/Results but never defined
9. **Table S8 contradiction**: Text says "no PfClpP redocking" but table shows "1 success"

### Strategic Solution (Reviewer 2's Recommendation)
**Use ligand-free receptors + standardized preparation + rescoring** — this single approach addresses multiple problems simultaneously and aligns with best practices (Hany et al. 2025).

---

## 📚 Document Contents Summary

### 1. `P1_REVISION_ROADMAP_R1.md` (Complete Technical Roadmap)

**Length**: ~15,000 words  
**Sections**:
- Executive Summary
- Reviewer Consensus & Strategic Priorities
- **Tier 1**: 9 CRITICAL blockers with detailed actions (T1.1–T1.9)
- **Tier 2**: 8 REQUIRED fixes (T2.1–T2.8)
- **Tier 3**: 4 RECOMMENDED enhancements (T3.1–T3.4)
- Implementation Timeline (week-by-week)
- Deliverables Checklist
- Risk Assessment & Contingency Plans
- Success Criteria
- Reviewer Response Strategy
- Resource Requirements

**Use for**: Understanding *what* to do, *why* it's needed, *how* to do it, and *when* to do it.

### 2. `P1_REVISION_EXECUTIVE_SUMMARY.md` (Quick Reference)

**Length**: ~3,000 words  
**Sections**:
- Verdict & Reviewer Consensus
- Critical Issues (9 items, color-coded 🔴)
- Required Fixes (8 items, table format)
- Recommended Enhancements (4 items)
- Timeline Summary (3 tracks: fast/strong/full)
- Resource Needs
- Critical Path Diagram
- Risk Mitigation
- Success Criteria
- Next Actions (immediate)

**Use for**: Quick orientation, stakeholder briefing, timeline planning.

### 3. `P1_REVISION_TASK_TRACKER.md` (Daily Execution Checklist)

**Length**: ~8,000 words  
**Sections**:
- Task breakdown by tier (T1.1–T1.9, T2.1–T2.8, T3.1–T3.4)
- Checkboxes for each sub-action (⬜ / 🟦 / ✅ / ⛔ / ⚠️)
- Owner, priority, deadline, dependencies, risks for each task
- Week-by-week milestones
- Cluster jobs summary
- Risk register
- Daily log template
- Completion criteria

**Use for**: Day-to-day progress tracking, sprint planning, identifying blockers.

### 4. `P1_REVISION_RESPONSE_TEMPLATE.md` (Reviewer Response Draft)

**Length**: ~20,000 words  
**Sections**:
- Cover Letter (draft)
- Point-by-point response to Reviewer 1 (2 major concerns)
- Point-by-point response to Reviewer 2 (9 major + 7 minor points)
- Summary of Changes (computational, text, tables/figures)
- Closing Remarks

**Use for**: Writing the formal response letter after computational work completes. Contains pre-drafted acknowledgments, explanations, and manuscript change descriptions. **Fill in bracketed placeholders [X], [Y] with actual results.**

---

## 🛠️ Technical Requirements

### Computational Resources
- **Cluster**: 50–100 nodes for 3 weeks (Weeks 4–6)
- **Storage**: ~500 GB for docking outputs
- **Software**: 
  - AutoDock Vina 1.2.7
  - OpenBabel
  - RDKit 2025.03.6
  - CNN-Score (Hany et al.)
  - RF-Score-VS (Hany et al.)
  - PyMOL or MODELLER (homology modeling)

### Personnel
- **Computational chemist**: 8 weeks full-time (lead)
- **Structural biologist**: 1 week consultation (PfCRT modeling)
- **Data scientist**: 3 days (statistics, power analysis)
- **Technical writer**: 1 week (manuscript revision)

### Budget Estimate
- **Cluster time**: $500–1,000 (if not free academic allocation)
- **Software licenses**: $0–500 (academic vs commercial)
- **Total**: ~$1,500 maximum

---

## ⚠️ High-Risk Items & Contingencies

| Risk | Likelihood | Mitigation | Contingency |
|------|------------|------------|-------------|
| **PfCRT 3D7 structure unavailable** | Medium | Commission homology modeling | Withdraw PfCRT from RRS panel (still publishable with PfDHFR alone) |
| **CNN-Score install fails** | Medium | Contact Hany et al. for support | Report DEKOIS improvement without rescoring (apo alone may suffice) |
| **RRS null = no signal** | Low-Med | Control experiment to separate batch from mutation | Reframe as honest-negative result ("protocols cannot resolve mutation effects") |
| **Top candidates change** | Medium | Sensitivity analysis | Expand validation list from 3 to 5–7 compounds |

---

## 📞 Contacts & Resources

### Key Citations to Review
- **Hany et al. (2025)**: Drug Des. Devel. Ther., DOI 10.2147/DDDT.S537065 (DEKOIS rescoring protocol)
- **Kim et al. (2019)**: Nat. Commun. (PfCRT drug-interaction cavity)
- **Gómez-Bombarelli et al. (2018)**: ACS Cent. Sci. 4, 268–276 (SMILES VAE, correct citation for Ref. 19)

### Software Resources
- **CNN-Score / RF-Score-VS**: [Repository links from Hany et al. paper]
- **DEKOIS 2.0**: http://www.dekois.com/
- **PyMOL**: https://pymol.org/ (academic license)
- **MODELLER**: https://salilab.org/modeller/ (academic license)

### Data Repositories
- **GitHub**: https://github.com/NanaEngo/Malaria_codesV2 (make public!)
- **Zenodo**: Link after archival → DOI

---

## ✅ Success Criteria

### Minimum for Resubmission (Tier 1 + Tier 2)
- [ ] All 9 critical blockers resolved (T1.1–T1.9)
- [ ] All 8 required fixes applied (T2.1–T2.8)
- [ ] Repository public with Zenodo DOI
- [ ] ~1,600 new docking calculations complete
- [ ] Tables 1 & 2 recomputed with corrected data
- [ ] Manuscript Methods/Results/Discussion updated
- [ ] Response letter drafted
- [ ] PDF compiles with 0 errors

### Strong Revision (+ Tier 3 Select)
- [ ] Minimum criteria ✅
- [ ] Retrospective antimalarial validation (T3.1) OR
- [ ] Hany et al. cross-validation (T3.4)

### Ideal Revision (All Tiers)
- [ ] Strong criteria ✅
- [ ] Preliminary experimental data (T3.2)

---

## 📝 Version History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-09-09 | 1.0 | Initial roadmap, executive summary, task tracker, response template | Kiro AI + MVST |
| [Future] | 1.1 | Progress updates, completion tracking | [To be updated] |

---

## 🎯 Next Steps

### Today (2026-09-09)
1. ✅ **Review all four documents** (roadmap, summary, tracker, response template)
2. 🟦 **Hold team meeting**: Assign task owners, confirm timeline feasibility
3. 🟦 **Make repository public** (T1.6.1 — highest priority, enables immediate reviewer verification)
4. 🟦 **Secure cluster allocation** for Weeks 4–6

### This Week (2026-09-09 to 2026-09-16)
5. 🟦 **Add MIT License** (T1.6.2)
6. 🟦 **Define PNS and ACSI** (T1.8 — enables correlation reproduction)
7. 🟦 **Contact structural biologist** (PfCRT modeling consultation)
8. 🟦 **Install rescoring software** (CNN-Score, RF-Score-VS)

### Week 2 Kickoff (2026-09-16)
9. ⬜ Begin protocol corrections (T1.1.1, T1.2.1, T1.3.1)
10. ⬜ Daily progress logging in task tracker

---

## 📧 Questions or Issues?

- **Technical questions**: Refer to `P1_REVISION_ROADMAP_R1.md` detailed actions
- **Timeline questions**: Refer to `P1_REVISION_EXECUTIVE_SUMMARY.md` timeline section
- **Daily execution questions**: Refer to `P1_REVISION_TASK_TRACKER.md`
- **Response writing questions**: Refer to `P1_REVISION_RESPONSE_TEMPLATE.md`

---

**Document**: Navigation guide for P1 JCIM revision  
**Status**: CURRENT  
**Last Updated**: 2026-09-09  
**Maintainer**: Project Lead

---

*Remember: Both reviewers explicitly encourage resubmission. The work is substantial but achievable in 10–12 weeks. The core scientific framework is sound — we just need stronger methodological rigor.*

**Let's get started! 🚀**
