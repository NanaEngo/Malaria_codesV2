# P1 Revision Executive Summary — JCIM Reviewer Response

**Document**: Quick-reference guide for P1 V7→V8 revision  
**Full Roadmap**: `P1_REVISION_ROADMAP_R1.md`  
**Date**: 2026-09-09

---

## Verdict: Major Revision Required, Resubmission Encouraged

Both reviewers appreciate the honest, transparent reporting but identify **critical flaws**. Both explicitly encourage resubmission after fixes.

### Reviewer Consensus
✅ **Keep**: Honest reporting, separation of evidence layers, no score-to-affinity conversion, null results transparency  
❌ **Fix**: PfCRT structure problem, DEKOIS worse-than-random artifact, RRS batch effects, missing correlation, cross-target threshold

---

## Critical Issues (9 items — manuscript blocked without these)

### 🔴 BLOCKER 1: PfCRT K76 Problem (R2 Major #3)
**Issue**: Grid doesn't contain residue 76 (16.7–19.5 Å outside box). Wild-type is already K76T mutant (7G8 isoform).  
**Impact**: Every A* assignment invalid (affects 6 compounds).  
**Fix**: 
- Obtain 3D7 wild-type structure (K76 as lysine)
- Re-anchor grid to Kim et al. cavity, expand box to ≥38.9 Å
- Re-dock 17 compounds × 3 alleles × 5 seeds = 255 poses
- Recompute PfCRT RRS column in Table 1

**Effort**: 2–3 weeks

---

### 🔴 BLOCKER 2: DEKOIS EF@1% = 0 (R2 Major #4)
**Issue**: Retained methotrexate blocks DEKOIS actives → EF@1% = EF@5% = 0.00 (worse than random).  
**Fix**: 
- Strip MTX from 7F3Y → apo structure
- Re-run DEKOIS (78 actives + 1200 decoys)
- Implement Hany et al. 2025 rescoring (CNN-Score, RF-Score-VS)
- Re-dock Set C on apo PfDHFR (340 poses)

**Effort**: 3–4 weeks

---

### 🔴 BLOCKER 3: RRS Batch Effect (R2 Major #5)
**Issue**: Wild-type and mutants prepared by different routes → batch effect dominates mutation signal. Six RRS > 100% (mutations improve binding).  
**Fix**: 
- Standardize preparation pipeline (all structures same protocol)
- Generate RRS null distribution (pseudo-mutant WT)
- Redefine class boundaries outside null distribution
- Re-dock 17 × 6 PfDHFR alleles × 5 seeds = 510 poses
- Re-dock 17 × 3 PfCRT alleles × 5 seeds = 255 poses

**Effort**: 4–5 weeks

---

### 🔴 BLOCKER 4: Missing Correlation (R2 Major #1)
**Issue**: N_fav vs RRS_mean correlation (ρ ≈ +0.515, p=0.034) not reported. Contradicts independence claim.  
**Fix**: 
- Compute and report correlation in Table S6
- Revise §4.1: Replace "demonstrate independence" with "limited power to detect association" (n=17, power=0.37)
- Acknowledge positive association may exist

**Effort**: 1 week

---

### 🔴 BLOCKER 5: Cross-Target Threshold (R2 Major #2)
**Issue**: −6.0 kcal/mol threshold violates within-target design (passes 7/17 for PfDHFR but 12/17 for PfCRT).  
**Fix**: 
- Define favorability by within-target rank (top 50% or tertile)
- Recompute Table 2 N_fav
- Remove "a priori" language

**Effort**: 1 week

---

### 🔴 BLOCKER 6: Repository 404 (R2 Major #6)
**Issue**: GitHub repository private (404 error). No verification possible.  
**Fix**: 
- Make repository public
- Add MIT License
- Create release tag v1.0-JCIM-R1
- Archive to Zenodo → DOI
- Embed wild-type/mutant scores in SI (new Tables S_NEW1, S_NEW2)

**Effort**: 1–2 days

---

### 🔴 BLOCKER 7: Single-Seed Docking (R2 Major #9)
**Issue**: All docking uses seed=0. PP-15 exceeds threshold by only 0.045 kcal/mol (within noise).  
**Fix**: 
- Re-dock Set C with 5 seeds (0, 42, 123, 456, 789)
- Report mean ± SD per compound-target pair
- Recompute N_fav with seed variability

**Effort**: 2 weeks

---

### 🔴 BLOCKER 8: PNS/ACSI Undefined (R2 Major #7)
**Issue**: PNS and ACSI appear in Abstract, Results, Figure 2 but never defined.  
**Fix**: 
- Add formulas to Methods
- Provide values in SI (new Table S_NEW5)
- Document software and reference sets

**Effort**: 3 days

---

### 🔴 BLOCKER 9: Table S8 Contradiction (R2 Major #8)
**Issue**: Text says "no redocking for PfClpP" but Table S8 lists "1 success". Structure 9N10 has no ligand to redock.  
**Fix**: 
- Remove PfClpP row from Table S8
- Label MMV rows as circular
- Downgrade "validation" to "assessment"

**Effort**: 2 days

---

## Required Fixes (8 items — needed for acceptance)

| Item | Issue | Fix | Effort |
|------|-------|-----|--------|
| **T2.1** | Duplicate paragraph (pp. 17–18) | Remove duplicate, verify p. 17 | 30 min |
| **T2.2** | Wrong VAE citation | Add Gómez-Bombarelli et al. 2018 | 30 min |
| **T2.3** | Cost reduction framing | Revise §4.4, add retention caveat | 1 hour |
| **T2.4** | RRS notation inconsistency | Standardize to S_Vina | 30 min |
| **T2.5** | SI numbering + decoy count | Renumber §S12, fix 1199 vs 1200 | 1 hour |
| **T2.6** | Figure 2 missing stats | Add ρ, p, n annotation | 30 min |
| **T2.7** | MPO sensitivity deferred | Summarize in §S10 | 1–3 weeks |
| **T2.8** | Uneven target evidence (R1) | Add Table S_NEW6, discuss in §4.3 | 2 days |

---

## Recommended Enhancements (4 items — strengthen impact)

| Item | Enhancement | Benefit | Effort |
|------|-------------|---------|--------|
| **T3.1** | Retrospective validation (known antimalarials) | Credibility (R1 request) | 3–4 weeks |
| **T3.2** | Preliminary experimental data | High-impact support | 3–6 months |
| **T3.3** | Public benchmark repository | Community resource | 2 weeks |
| **T3.4** | Hany et al. cross-validation | Robustness evidence | 2 weeks |

---

## Timeline Summary

### Fast Track (Tier 1 + Tier 2 only): 10–12 weeks
- **Weeks 1–3**: Protocol corrections (PfCRT/PfDHFR structures, standardization)
- **Weeks 4–6**: Large-scale docking (~1,600 jobs, parallelized)
- **Weeks 7–8**: Analysis & recomputation
- **Weeks 9–10**: Manuscript revision

### Strong Track (+ Selected Tier 3): 14–16 weeks
- **Weeks 11–12**: Retrospective validation (T3.1)
- **Weeks 13–14**: Hany cross-validation (T3.4)

### Full Track (+ Experimental): 16–24 weeks
- **Weeks 11–24**: Preliminary experimental data (T3.2, depends on collaborator)

---

## Resource Needs

### Computational
- **Cluster**: 50–100 nodes × 3 weeks
- **Storage**: ~500 GB
- **Software**: Vina, OpenBabel, RDKit, CNN-Score, RF-Score-VS, PyMOL/MODELLER

### Personnel
- **Computational chemist**: 8 weeks full-time
- **Structural biologist**: 1 week consultation (homology modeling)
- **Data scientist**: 3 days (power analysis, statistics)
- **Technical writer**: 1 week

### Budget
- **Cluster time**: $500–1,000 (if not free)
- **Software**: $0–500 (academic licenses)
- **Total**: ~$1,500 max

---

## Critical Path (Dependencies)

```
Week 1: Repository public (T1.6) ──┐
                                    ├──→ Week 9–10: Manuscript revision
Week 1: PNS/ACSI definitions (T1.8)┘

Week 2–3: PfCRT structure (T1.1.1–1.1.2) ──→ Week 4–6: PfCRT docking (T1.1.3)
                                                           │
Week 2–3: PfDHFR apo (T1.2.1) ──→ Week 4–6: DEKOIS + PfDHFR docking (T1.2.2/T1.2.4)
                                                           │
Week 3: Standardized pipeline (T1.3.1) ──→ Week 4–6: Mutation panel (T1.3.4)
                                                           │
                                           ┌───────────────┘
                                           ↓
                        Week 7–8: Analysis (T1.2.3, T1.3.2–1.3.3, T1.4, T1.5, T1.7.3)
                                           │
                                           ↓
                                   Week 9–10: Revision
```

---

## Risk Mitigation

### HIGH RISK: PfCRT 3D7 structure unavailable
- **Mitigation**: Commission homology modeling or use PyMOL mutation
- **Contingency**: Withdraw PfCRT from RRS panel (still publishable with PfDHFR alone)

### MEDIUM RISK: RRS null distribution shows no signal
- **Mitigation**: Distinguish batch effect from mutation effect via controls
- **Contingency**: Reframe as honest-negative result ("current protocols cannot resolve mutation effects")

### LOW RISK: Within-target favorability changes top candidates
- **Mitigation**: Sensitivity analysis
- **Contingency**: Expand candidate list from 3 to 5–7

---

## Success Criteria

### Minimum (Tier 1 + Tier 2): Defensible Resubmission
✅ All critical issues fixed  
✅ Repository public with DOI  
✅ Multi-seed docking complete  
✅ RRS null distribution reported  
✅ Independence claim softened  

### Strong (+ Select Tier 3): Likely Acceptance
✅ Minimum criteria  
✅ Retrospective validation OR Hany cross-validation  

### Ideal (All Tiers): High-Impact Publication
✅ Strong criteria  
✅ Preliminary experimental data  

---

## Reviewer Response Strategy

### Tone
- **Acknowledge**: "We thank reviewers for recognizing our commitment to honest reporting."
- **Accept**: "We agree the issues are critical and have performed ~1,600 new calculations."
- **Reframe if needed**: If RRS null shows no signal → "honest negative demonstrating protocol limits"

### Key Messages
- "This revision includes substantial new work: ligand-free receptors, standardized preparation, multi-seed docking, and independent validation."
- "We have implemented Reviewer 2's recommended approach (Hany et al. 2025 protocol) which addresses multiple issues simultaneously."
- "The revised manuscript is now fully reproducible with public repository (DOI: 10.5281/zenodo.XXXXXXX) and embedded data tables."

---

## Next Actions (Immediate)

1. **Review roadmap** with co-authors and PI
2. **Secure cluster allocation** (50–100 nodes × 3 weeks)
3. **Contact structural biologist** for PfCRT homology modeling consultation
4. **Make repository public** (T1.6) — enables immediate reviewer verification
5. **Install rescoring software** (CNN-Score, RF-Score-VS) — may have dependencies
6. **Create revision tracking document** to log daily progress

---

## Conclusion

**Verdict**: Major revision, but **resubmission strongly encouraged** by both reviewers.

**Core message**: The scientific instinct is sound, the integrity is appreciated, but technical execution has critical flaws. All flaws are fixable with new computation.

**Strategic insight**: Ligand-free receptors + standardized preparation + rescoring (Reviewer 2's recommendation) solves multiple problems at once.

**Timeline**: 10–12 weeks to submission-ready revised manuscript (Tier 1+2).

**Recommendation**: **Execute immediately**. Begin with protocol corrections (Weeks 1–3) while securing cluster access for large-scale docking (Weeks 4–6).

---

**Document**: Executive summary of full roadmap  
**Full details**: See `P1_REVISION_ROADMAP_R1.md`  
**Status**: DRAFT — awaiting author authorization
