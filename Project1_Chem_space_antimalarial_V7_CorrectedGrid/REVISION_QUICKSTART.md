# P1 JCIM Revision — Quick Start Card

**Status**: Major Revision Required → Resubmission Encouraged ✅  
**Timeline**: 10–12 weeks to submission-ready  
**Effort**: ~1,600 new docking calculations + manuscript rewrite

---

## 🚦 VERDICT

✅ **Both reviewers appreciate honest reporting and encourage resubmission**  
❌ **9 critical flaws must be fixed (computational + text)**  
🎯 **Core science is sound — methodological rigor needs strengthening**

---

## 🔥 TOP 3 CRITICAL ISSUES

### 1. **PfCRT K76 Grid Problem** (Reviewer 2, Major #3)
- **Issue**: Residue 76 is 16.7–19.5 Å outside docking box; wild-type is already K76T mutant
- **Impact**: Every A* RRS assignment invalid
- **Fix**: Obtain 3D7 WT structure, expand box to 40 Å, re-dock 255 poses
- **Effort**: 2–3 weeks

### 2. **DEKOIS Worse-Than-Random** (Reviewer 2, Major #4)
- **Issue**: Retained methotrexate → EF@1% = 0
- **Impact**: Protocol validation fails
- **Fix**: Strip MTX, re-run DEKOIS on apo PfDHFR, implement Hany et al. rescoring
- **Effort**: 3–4 weeks

### 3. **RRS Batch Effect** (Reviewer 2, Major #5)
- **Issue**: WT/mutant different prep → batch effect dominates signal
- **Impact**: RRS interpretation unreliable
- **Fix**: Standardize pipeline, generate null distribution, re-dock 765 poses
- **Effort**: 4–5 weeks

---

## 📋 ALL 9 CRITICAL BLOCKERS

| # | Issue | Reviewer | Effort |
|---|-------|----------|--------|
| **T1.1** | PfCRT K76 grid problem | R2 Major #3 | 2–3 weeks |
| **T1.2** | DEKOIS worse-than-random | R2 Major #4 | 3–4 weeks |
| **T1.3** | RRS batch effect | R2 Major #5 | 4–5 weeks |
| **T1.4** | Missing N_fav vs RRS correlation | R2 Major #1 | 1 week |
| **T1.5** | Cross-target threshold | R2 Major #2 | 1 week |
| **T1.6** | Repository 404 error | R2 Major #6 | 1–2 days |
| **T1.7** | Single-seed docking | R2 Major #9 | 2 weeks |
| **T1.8** | PNS/ACSI undefined | R2 Major #7 | 3 days |
| **T1.9** | Table S8 contradiction | R2 Major #8 | 2 days |

---

## ⏱️ TIMELINE (10 Weeks)

```
┌─────────────────────────────────────────────────────────────┐
│ Week 1:  Repository public + PNS/ACSI + planning            │
│ Week 2–3: PfCRT structure, apo PfDHFR, standardized prep    │
│ Week 4–6: ~1,600 docking jobs (PARALLELIZED)                │
│ Week 7–8: Analysis, recompute Tables 1 & 2                  │
│ Week 9–10: Manuscript revision + response letter            │
│ Target:   2026-11-18 submission                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 IMMEDIATE ACTIONS (TODAY)

### Can Start Right Now (No Dependencies)
1. ✅ **Read**: `README_REVISION.md` (this directory)
2. 🟦 **Repository public**: GitHub Settings → Visibility → Public (30 min)
3. 🟦 **Add MIT License**: Copy to repository root (15 min)
4. 🟦 **Team meeting**: Assign owners, confirm resources

### This Week
5. 🟦 **Define PNS/ACSI**: Add formulas to Methods (3 days)
6. 🟦 **Cluster allocation**: Reserve 50–100 nodes for Weeks 4–6
7. 🟦 **Contact structural biologist**: PfCRT homology modeling
8. 🟦 **Install software**: CNN-Score, RF-Score-VS (rescoring)

---

## 📚 DOCUMENT MAP

| Document | Use When You Need... |
|----------|---------------------|
| **`README_REVISION.md`** | Overview & navigation (start here!) |
| **`P1_REVISION_EXECUTIVE_SUMMARY.md`** | Quick briefing for stakeholders |
| **`P1_REVISION_ROADMAP_R1.md`** | Full technical details & actions |
| **`P1_REVISION_TASK_TRACKER.md`** | Daily execution checklist |
| **`P1_REVISION_RESPONSE_TEMPLATE.md`** | Draft response letter (Week 9+) |

---

## 💡 KEY STRATEGIC INSIGHT

**Reviewer 2's Solution Solves Multiple Problems:**

> Use **ligand-free receptors** + **standardized preparation** + **rescoring** (Hany et al. 2025)

This single approach addresses:
- ✅ DEKOIS artifact (apo structure)
- ✅ RRS batch effect (standardized prep)
- ✅ Protocol validation (rescoring improves enrichment)

**Follow this recommended path — it's the most efficient route to acceptance.**

---

## 🎓 WHAT REVIEWERS LIKED (Keep This!)

✅ Honest reporting (no score-to-affinity conversion)  
✅ Transparent null results  
✅ Separation of evidence layers  
✅ No cross-target composites  
✅ Sound scientific instinct  
✅ Genuine accessibility case  

**Preserve these strengths while fixing technical flaws.**

---

## 📊 COMPUTATIONAL WORKLOAD

### Total Docking Jobs: ~1,600

| Task | Jobs | Priority | Weeks |
|------|------|----------|-------|
| PfCRT panel (corrected) | 255 | P0 | 4–6 |
| DEKOIS re-run | ~1,280 | P0 | 4–5 |
| PfDHFR Set C (apo) | 340 | P0 | 4–6 |
| Mutation panel (standardized) | 765 | P0 | 4–6 |
| Multi-seed Set C | 340 | P1 | 4–6 |
| **Total** | **~2,980** | — | — |

**Note**: Jobs overlap; wall-time ≈3 weeks with 50–100 node cluster.

---

## ⚠️ TOP 3 RISKS

| Risk | Contingency |
|------|-------------|
| **PfCRT 3D7 unavailable** | Withdraw PfCRT from RRS (still publishable) |
| **RRS null = no signal** | Reframe as honest-negative ("protocols can't resolve mutations") |
| **Rescoring install fails** | Report DEKOIS without rescoring (apo alone may suffice) |

**All risks have acceptable fallback plans.**

---

## ✅ SUCCESS = TIER 1 + TIER 2

### Minimum for Resubmission
- [ ] 9 critical blockers fixed (T1.1–T1.9)
- [ ] 8 required fixes applied (T2.1–T2.8)
- [ ] Repository public + DOI
- [ ] Tables 1 & 2 recomputed
- [ ] Response letter complete

### Strong Revision (Recommended)
- [ ] Minimum ✅
- [ ] Retrospective validation (known antimalarials) OR
- [ ] Hany et al. cross-validation

---

## 📞 KEY RESOURCES

### Must-Read Citations
- **Hany et al. (2025)**: Drug Des. Devel. Ther. DOI 10.2147/DDDT.S537065 (rescoring)
- **Kim et al. (2019)**: Nat. Commun. (PfCRT cavity)
- **Gómez-Bombarelli et al. (2018)**: ACS Cent. Sci. (correct VAE citation)

### Software
- AutoDock Vina 1.2.7
- CNN-Score / RF-Score-VS (Hany et al.)
- PyMOL or MODELLER (homology modeling)

---

## 🚀 FIRST 3 STEPS

1. **Read** `README_REVISION.md` (10 min)
2. **Make repository public** (30 min) — **highest priority**
3. **Review** `P1_REVISION_EXECUTIVE_SUMMARY.md` (20 min)

**Then hold team meeting to assign owners and confirm timeline.**

---

## 💪 YOU CAN DO THIS

✅ Reviewers explicitly encourage resubmission  
✅ Core science is sound  
✅ All issues are fixable  
✅ Clear roadmap exists  
✅ 10–12 weeks is achievable  

**The work is substantial but straightforward. Follow the roadmap, execute systematically, and you'll have a strong revision.**

---

**Document**: Quick-start reference card  
**Full Details**: See `README_REVISION.md`  
**Date**: 2026-09-09

**GO! 🚀**
