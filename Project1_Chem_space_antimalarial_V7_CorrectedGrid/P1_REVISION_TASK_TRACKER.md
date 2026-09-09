# P1 Revision Task Tracker — JCIM R1

**Version**: V7 → V8 (First Revision)  
**Target**: JCIM resubmission  
**Started**: 2026-09-09  
**Target Completion**: 2026-11-18 (10 weeks)  

**Status Legend**:  
- ⬜ Not started  
- 🟦 In progress  
- ✅ Complete  
- ⛔ Blocked  
- ⚠️ Issue/Risk  

---

## TIER 1: CRITICAL BLOCKERS (Required for Submission)

### T1.1 — PfCRT Structure & Grid Correction
**Owner**: [Assign]  
**Priority**: P0 (blocks all PfCRT work)  
**Deadline**: Week 3 (2026-09-30)  

- [ ] ⬜ **T1.1.1** Obtain/model 3D7 wild-type PfCRT (K76 as lysine)
  - [ ] Literature search for 3D7 structure
  - [ ] If unavailable: Commission homology modeling
  - [ ] Verify K76 identity: `grep "LYS A  76" structure.pdb`
  - **Output**: `pfcrt_3d7_wt_model.pdb`
  - **Deadline**: 2026-09-23

- [ ] ⬜ **T1.1.2** Re-anchor grid to Kim et al. cavity
  - [ ] Calculate cavity centroid from Kim et al. coordinates
  - [ ] Set box edge ≥38.9 Å (verify all K76 atoms inside)
  - [ ] Validate cavity volume ≥500 Å³
  - **Output**: `pfcrt_gridbox_v2.txt`
  - **Deadline**: 2026-09-25

- [ ] ⬜ **T1.1.3** Re-dock PfCRT panel (255 poses)
  - [ ] 17 compounds × 3 alleles (WT/K76T/K76A) × 5 seeds
  - [ ] Vina 1.2.7, exhaustiveness=32
  - [ ] Seeds: 0, 42, 123, 456, 789
  - [ ] QC: Verify ≥1 pose contacts K76 per compound
  - **Output**: `results/pfcrt_panel_corrected/`
  - **Deadline**: 2026-10-14

- [ ] ⬜ **T1.1.4** Recompute PfCRT RRS values
  - [ ] Update Table 1 PfCRT column
  - [ ] Document class changes (A*/B/C/D) for 6 affected compounds
  - [ ] Update manuscript text
  - **Deadline**: 2026-10-21

**Status**: ⬜ Not started  
**Dependencies**: None  
**Risks**: 3D7 structure may require modeling (Medium risk)

---

### T1.2 — DEKOIS Benchmark Re-run (Ligand-Free PfDHFR)
**Owner**: [Assign]  
**Priority**: P0 (blocks PfDHFR validation)  
**Deadline**: Week 6 (2026-10-21)  

- [ ] ⬜ **T1.2.1** Strip MTX from PfDHFR receptor
  - [ ] `grep -v "A 702" 7F3Y_processed.pdb > 7F3Y_apo.pdb`
  - [ ] Verify no HETATM in binding pocket
  - **Output**: `pfdhfr_7f3y_apo.pdb`
  - **Deadline**: 2026-09-23

- [ ] ⬜ **T1.2.2** Re-run DEKOIS 2.0 benchmark
  - [ ] 78 actives + 1200 decoys (verify count)
  - [ ] Vina 1.2.7, exhaustiveness=32, seed=0
  - [ ] Calculate ROC-AUC, EF@1%, EF@5%
  - [ ] Target: EF@1% > 0
  - **Output**: Enrichment plot + statistics
  - **Deadline**: 2026-10-07

- [ ] ⬜ **T1.2.3** Implement Hany et al. rescoring
  - [ ] Install CNN-Score and RF-Score-VS
  - [ ] Apply to Vina poses
  - [ ] Compare Vina raw vs CNN vs RF-Score-VS
  - [ ] Target: worse-than-random → better-than-random
  - **Output**: Rescored ROC-AUC comparison table
  - **Deadline**: 2026-10-14

- [ ] ⬜ **T1.2.4** Re-dock Set C on apo PfDHFR
  - [ ] 17 compounds × 4 alleles × 5 seeds = 340 poses
  - [ ] Update PfDHFR panel scores
  - **Output**: Updated PfDHFR RRS
  - **Deadline**: 2026-10-14

- [ ] ⬜ **T1.2.5** Update manuscript
  - [ ] Replace SM §S12 DEKOIS section
  - [ ] Add "ligand-free apo receptor" to Main §2.3
  - [ ] Cite Hany et al. 2025 explicitly
  - **Deadline**: 2026-11-04

**Status**: ⬜ Not started  
**Dependencies**: None  
**Risks**: CNN-Score/RF-Score-VS installation may have issues (Medium risk)

---

### T1.3 — Wild-Type/Mutant Preparation Consistency & RRS Null
**Owner**: [Assign]  
**Priority**: P0 (blocks all RRS work)  
**Deadline**: Week 6 (2026-10-21)  

- [ ] ⬜ **T1.3.1** Standardize receptor preparation pipeline
  - [ ] Document unified protocol: `preparation_protocol_v2.md`
  - [ ] Apply to 11 structures (PfDHFR: 5, PfCRT: 3, others: 3)
  - [ ] Same protonation, charge, minimization for all
  - **Deadline**: 2026-09-30

- [ ] ⬜ **T1.3.2** Generate RRS null distribution
  - [ ] Dock 17 compounds vs pseudo-mutant WT (no mutation, mutant pipeline)
  - [ ] Calculate mean, SD, 95% CI of null
  - **Output**: 17 null RRS values
  - **Deadline**: 2026-10-14

- [ ] ⬜ **T1.3.3** Redefine RRS class boundaries
  - [ ] Place boundaries at null_mean ± 2×SD
  - [ ] Update classification logic
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.3.4** Re-dock entire mutation panel (765 poses)
  - [ ] PfDHFR: 17 × 6 alleles (WT+4mut+pseudo) × 5 seeds = 510
  - [ ] PfCRT: 17 × 3 alleles × 5 seeds = 255
  - [ ] Total: ~765 docking jobs
  - **Output**: Recomputed Table 1
  - **Deadline**: 2026-10-14

- [ ] ⬜ **T1.3.5** Explain RRS > 100% cases
  - [ ] Analyze PP-15 (all 4 PfDHFR mutations improve binding)
  - [ ] Check pose quality, structural rationale
  - [ ] Add paragraph to Results/Discussion
  - **Deadline**: 2026-11-04

**Status**: ⬜ Not started  
**Dependencies**: T1.3.1 blocks T1.3.2 and T1.3.4  
**Risks**: Null distribution may overlap all observed RRS (High risk → honest negative)

---

### T1.4 — Missing Correlation (N_fav vs RRS_mean)
**Owner**: [Assign]  
**Priority**: P1  
**Deadline**: Week 7 (2026-10-28)  

- [ ] ⬜ **T1.4.1** Compute N_fav vs RRS_mean correlation
  - [ ] Spearman ρ with 95% CI (bootstrap)
  - [ ] Verify ρ ≈ +0.515
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.4.2** Add to Table S6
  - [ ] Insert as first row
  - [ ] Format: `N_fav vs RRS_mean | +0.515 [CI] | 0.034 | n.s.†`
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.4.3** Revise independence interpretation
  - [ ] §4.1: Replace "demonstrate" with "limited power"
  - [ ] Add power analysis (n=17, power=0.37)
  - [ ] Acknowledge positive association may exist
  - **Deadline**: 2026-11-04

- [ ] ⬜ **T1.4.4** Resolve PNS–RRS "trend" inconsistency
  - [ ] Reclassify p=0.020 as n.s. with power caveat
  - **Deadline**: 2026-11-04

- [ ] ⬜ **T1.4.5** Add limitation statement
  - [ ] §4.4 or new §4.5: Sample size limits power
  - **Deadline**: 2026-11-04

**Status**: ⬜ Not started  
**Dependencies**: Requires updated RRS values from T1.1.4, T1.3.4  
**Risks**: Low

---

### T1.5 — Within-Target Favorability Definition
**Owner**: [Assign]  
**Priority**: P1  
**Deadline**: Week 7 (2026-10-28)  

- [ ] ⬜ **T1.5.1** Define within-target favorability by rank
  - [ ] Method: Top 50% (≥9/17) or top tertile (≥6/17)
  - [ ] Alternative: Target-specific score threshold
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.5.2** Recompute Table 2
  - [ ] Rank compounds within each target
  - [ ] Count favorable ranks (N_fav_rank)
  - [ ] Recompute Set C class (I/II/III)
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.5.3** Recompute Set C prioritization
  - [ ] Verify PP-01/PP-02/PP-15 unchanged or document shifts
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.5.4** Remove "a priori" language
  - [ ] §2.5: Replace with within-target rank justification
  - **Deadline**: 2026-11-04

- [ ] ⬜ **T1.5.5** Add sensitivity analysis
  - [ ] Test 50th vs 67th percentile thresholds
  - [ ] Output: Supplementary table
  - **Deadline**: 2026-10-28

**Status**: ⬜ Not started  
**Dependencies**: None  
**Risks**: Top candidates may change (Medium risk)

---

### T1.6 — Repository Access & Archival DOI
**Owner**: [Assign]  
**Priority**: P0 (enables reviewer verification immediately)  
**Deadline**: Week 1 (2026-09-16)  

- [ ] ⬜ **T1.6.1** Make repository public
  - [ ] GitHub → Settings → Visibility → Public
  - [ ] Verify from incognito browser
  - **Deadline**: 2026-09-11

- [ ] ⬜ **T1.6.2** Add software license
  - [ ] Add MIT License to repository root
  - **Deadline**: 2026-09-11

- [ ] ⬜ **T1.6.3** Create release tag
  - [ ] Tag: `v1.0-JCIM-R1`
  - [ ] Add changelog documenting changes from V7
  - **Deadline**: 2026-11-11

- [ ] ⬜ **T1.6.4** Archive to Zenodo
  - [ ] Link GitHub → Zenodo
  - [ ] Create release → auto-archive
  - [ ] Obtain DOI
  - [ ] Add DOI badge to README
  - **Deadline**: 2026-11-11

- [ ] ⬜ **T1.6.5** Embed critical data in SI
  - [ ] Table S_NEW1: Wild-type Vina scores
  - [ ] Table S_NEW2: Mutant Vina scores
  - [ ] Table S_NEW3: SHA-256 checksums
  - **Deadline**: 2026-11-04

- [ ] ⬜ **T1.6.6** Update Data Availability statement
  - [ ] Add Zenodo DOI
  - [ ] Reference embedded tables
  - **Deadline**: 2026-11-04

**Status**: ⬜ Not started  
**Dependencies**: None (can start immediately)  
**Risks**: Low (administrative only)

---

### T1.7 — Multi-Seed Docking for Top Candidates
**Owner**: [Assign]  
**Priority**: P1  
**Deadline**: Week 6 (2026-10-21)  

- [ ] ⬜ **T1.7.1** Re-dock Set C with 5 seeds (340 poses)
  - [ ] 17 compounds × 4 targets × 5 seeds
  - [ ] Seeds: 0, 42, 123, 456, 789
  - **Output**: Score matrix with mean, SD, min, max
  - **Deadline**: 2026-10-14

- [ ] ⬜ **T1.7.2** Compute score dispersion statistics
  - [ ] Metrics: Mean±SD, max seed-to-seed diff, CV
  - **Output**: Table S_NEW4
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.7.3** Recompute N_fav with seed variability
  - [ ] Use mean score for favorability
  - [ ] Compare single-seed vs multi-seed N_fav
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.7.4** Assess PP-15 classification stability
  - [ ] Check if score mean ± SD crosses threshold
  - [ ] Add statement about marginal favorability
  - **Deadline**: 2026-10-21

- [ ] ⬜ **T1.7.5** Update Methods section
  - [ ] §2.3.1: Change seed=0 to "Five independent seeds"
  - [ ] §2.5: Flag seed-dependent classifications
  - **Deadline**: 2026-11-04

**Status**: ⬜ Not started  
**Dependencies**: Can run in parallel with T1.1.3, T1.2.4, T1.3.4  
**Risks**: Low

---

### T1.8 — PNS and ACSI Definitions
**Owner**: [Assign]  
**Priority**: P1  
**Deadline**: Week 1 (2026-09-16)  

- [ ] ⬜ **T1.8.1** Add definitions to Methods
  - [ ] §2.4 or new §2.4.1: Formulas for PNS and ACSI
  - [ ] Document reference sets and software
  - **Deadline**: 2026-09-12

- [ ] ⬜ **T1.8.2** Add abbreviations
  - [ ] First use: Spell out with abbreviation
  - [ ] Add to abbreviations list if required
  - **Deadline**: 2026-09-12

- [ ] ⬜ **T1.8.3** Provide values in SI
  - [ ] Table S_NEW5: PNS and ACSI for 17 compounds
  - [ ] Include intermediate components
  - **Deadline**: 2026-09-16

- [ ] ⬜ **T1.8.4** Document reproducibility
  - [ ] SI §S11: Add "PNS and ACSI Calculation"
  - [ ] Include code snippet or pseudocode
  - **Deadline**: 2026-09-16

**Status**: ⬜ Not started  
**Dependencies**: None (can start immediately)  
**Risks**: Low

---

### T1.9 — Table S8 Contradiction Resolution
**Owner**: [Assign]  
**Priority**: P2  
**Deadline**: Week 8 (2026-11-04)  

- [ ] ⬜ **T1.9.1** Resolve PfClpP redocking claim
  - [ ] Withdraw PfClpP row from Table S8
  - [ ] State "validation limited to cavity identification"
  - **Deadline**: 2026-10-28

- [ ] ⬜ **T1.9.2** Remove or label MMV rows
  - [ ] Keep with footnote: "circular by construction"
  - **Deadline**: 2026-10-28

- [ ] ⬜ **T1.9.3** Downgrade validation language
  - [ ] Caption: "protocol assessment" not "reliability"
  - [ ] Text: "validation" → "assessment"
  - **Deadline**: 2026-10-28

- [ ] ⬜ **T1.9.4** Add honest negative framing
  - [ ] §S12: DEKOIS provides independent assessment
  - **Deadline**: 2026-10-28

**Status**: ⬜ Not started  
**Dependencies**: None  
**Risks**: Low

---

## TIER 2: REQUIRED FIXES (Necessary for Acceptance)

### T2.1 — Duplicate Paragraph Removal
- [ ] ⬜ Remove duplicate on p. 18
- [ ] ⬜ Verify p. 17 version matches Table 1
- [ ] ⬜ Proofread for other duplications
- **Deadline**: 2026-11-04
- **Effort**: 30 minutes

### T2.2 — Citation Correction (VAE)
- [ ] ⬜ Add Gómez-Bombarelli et al. 2018 citation
- [ ] ⬜ Replace/supplement Ref. 19 where SMILES VAE discussed
- [ ] ⬜ Check for other generic-vs-specific citation errors
- **Deadline**: 2026-11-04
- **Effort**: 30 minutes

### T2.3 — Cost Reduction Framing
- [ ] ⬜ Revise §4.4: Clarify 99.3% relative to exhaustive, not alternatives
- [ ] ⬜ Add limitation: Active-compound retention unknown
- [ ] ⬜ Optional: Add retention experiment
- **Deadline**: 2026-11-04
- **Effort**: 1 hour (text) or 1 week (experiment)

### T2.4 — RRS Notation Consistency
- [ ] ⬜ Find-replace: ΔG → S_Vina in RRS context
- [ ] ⬜ Verify Table 1 caption and footnotes
- **Deadline**: 2026-11-04
- **Effort**: 30 minutes

### T2.5 — SI Section Numbering & Decoy Count
- [ ] ⬜ Renumber duplicate §S12
- [ ] ⬜ Verify DEKOIS decoy count (1199 vs 1200)
- [ ] ⬜ Correct Tables S7 and S8
- [ ] ⬜ Add footnote if discrepancy due to preprocessing
- **Deadline**: 2026-11-04
- **Effort**: 1 hour

### T2.6 — Figure 2 Annotation
- [ ] ⬜ Add text to Figure 2: "ρ = -0.559, p = 0.020, n = 17"
- [ ] ⬜ Ensure annotation doesn't obscure data
- **Deadline**: 2026-11-04
- **Effort**: 30 minutes

### T2.7 — MPO Sensitivity Analysis
- [ ] ⬜ Add MPO sensitivity summary to §S10
- [ ] ⬜ Test weight perturbation (±20%)
- [ ] ⬜ Add enrichment validation summary
- **Deadline**: 2026-10-28
- **Effort**: 1 week (if exists) or 3 weeks (new)

### T2.8 — Target Structural Evidence Quality
- [ ] ⬜ Create Table S_NEW6: Target evidence quality
- [ ] ⬜ Columns: Target, PDB, resolution, ligand?, mutants?, evidence class
- [ ] ⬜ Add discussion to §4.3 (Limitations)
- [ ] ⬜ Optional: Down-weight low-evidence targets (sensitivity)
- **Deadline**: 2026-10-28
- **Effort**: 2 days

---

## TIER 3: RECOMMENDED ENHANCEMENTS (Strengthen Impact)

### T3.1 — Retrospective Validation (Known Antimalarials)
- [ ] ⬜ Assemble 50–100 known antimalarials + inactive analogs
- [ ] ⬜ Dock validation set vs 4 targets
- [ ] ⬜ Compute ROC-AUC, EF@1%, EF@5%
- [ ] ⬜ Add to §S12 as "Retrospective Antimalarial Scaffold Validation"
- **Deadline**: 2026-11-11 (optional)
- **Effort**: 3–4 weeks

### T3.2 — Preliminary Experimental Validation
- [ ] ⬜ Collaborate for IC50 data (1–3 candidates)
- [ ] ⬜ Obtain binding assay (SPR/ITC/thermal shift) for 1 candidate
- [ ] ⬜ Add Results subsection
- [ ] ⬜ Update §5 Conclusion
- **Deadline**: 2026-12-23 or later (optional)
- **Effort**: 3–6 months

### T3.3 — Public Benchmark Repository
- [ ] ⬜ Package DEKOIS + retrospective antimalarials + Set C
- [ ] ⬜ Provide standardized scoring protocol
- [ ] ⬜ Enable community comparison
- **Deadline**: 2026-11-18 (optional)
- **Effort**: 2 weeks

### T3.4 — Hany et al. Cross-Validation
- [ ] ⬜ Apply CNN-Score/RF-Score-VS to Set C
- [ ] ⬜ Compare top-ranked candidates
- [ ] ⬜ Report rank correlation
- [ ] ⬜ Add to Discussion
- **Deadline**: 2026-11-11 (optional)
- **Effort**: 2 weeks

---

## Progress Tracking

### Week-by-Week Milestones

**Week 1 (2026-09-09 to 2026-09-16)**:
- [ ] T1.6 Repository public + license (immediate)
- [ ] T1.8 PNS/ACSI definitions
- [ ] Planning: Secure cluster allocation

**Week 2–3 (2026-09-16 to 2026-09-30)**:
- [ ] T1.1.1–1.1.2 PfCRT structure + grid
- [ ] T1.2.1 PfDHFR apo structure
- [ ] T1.3.1 Standardized preparation pipeline

**Week 4–6 (2026-09-30 to 2026-10-21)**:
- [ ] T1.1.3 PfCRT docking (255 poses)
- [ ] T1.2.2 + T1.2.4 DEKOIS + PfDHFR Set C (400 poses)
- [ ] T1.3.2 + T1.3.4 Null distribution + mutation panel (765 poses)
- [ ] T1.7.1 Multi-seed Set C (340 poses)
- **Total**: ~1,760 docking jobs (parallelized)

**Week 7–8 (2026-10-21 to 2026-11-04)**:
- [ ] T1.2.3 Rescoring implementation
- [ ] T1.3.2–1.3.3 RRS null analysis
- [ ] T1.4 Correlation reanalysis
- [ ] T1.5 Within-target favorability
- [ ] T1.1.4, T1.3.4, T1.7.3 Recompute Tables 1 & 2
- [ ] T2.7 MPO sensitivity
- [ ] T2.8 Target evidence table

**Week 9–10 (2026-11-04 to 2026-11-18)**:
- [ ] All Tier 2 items (T2.1–T2.6)
- [ ] T1.9 Table S8 resolution
- [ ] Update all Methods/Results/Discussion
- [ ] Regenerate figures and tables
- [ ] Revision letter writing

**Week 11–12 (2026-11-18 to 2026-12-02)** [Optional]:
- [ ] T3.1 Retrospective validation
- [ ] T3.4 Hany cross-validation

---

## Resource Allocation

### Cluster Jobs Summary
| Task | Jobs | Priority | Start | End |
|------|------|----------|-------|-----|
| T1.1.3 PfCRT panel | 255 | P0 | Week 4 | Week 6 |
| T1.2.2 DEKOIS | 1278 | P0 | Week 4 | Week 5 |
| T1.2.4 PfDHFR Set C | 340 | P0 | Week 4 | Week 6 |
| T1.3.2 Null distribution | 85 | P0 | Week 5 | Week 6 |
| T1.3.4 Mutation panel | 765 | P0 | Week 4 | Week 6 |
| T1.7.1 Multi-seed | 340 | P1 | Week 4 | Week 6 |
| **Total** | **~3,063** | — | — | — |

**Note**: Many jobs overlap; wall-time ≈3 weeks with 50–100 node cluster.

### Personnel Hours
- Computational chemist: 8 weeks × 40 hrs = 320 hrs
- Structural biologist: 1 week × 8 hrs = 8 hrs
- Data scientist: 3 days × 8 hrs = 24 hrs
- Technical writer: 1 week × 40 hrs = 40 hrs
- **Total**: ~392 hrs

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Contingency |
|------|------------|--------|------------|-------------|
| PfCRT 3D7 unavailable | Medium | High | Commission modeling | Withdraw PfCRT from RRS |
| CNN-Score install fails | Medium | Medium | Contact Hany et al. | Report DEKOIS without rescoring |
| RRS null = no signal | Low-Med | Critical | Control experiment | Honest negative result |
| Top candidates change | Medium | Medium | Sensitivity analysis | Expand to 5–7 candidates |
| Cluster access delayed | Low | High | Reserve early | Request priority queue |

---

## Daily Log Template

```markdown
### Date: YYYY-MM-DD
**Tasks Completed**:
- [ ] Task ID: Description

**Tasks In Progress**:
- [ ] Task ID: Description (% complete)

**Blockers**:
- Issue description, owner, resolution plan

**Tomorrow's Plan**:
- [ ] Task ID: Goal

**Notes**:
- Any observations, decisions, or risks
```

---

## Completion Criteria

### Tier 1 Complete When:
- [ ] All 9 critical issues (T1.1–T1.9) marked ✅
- [ ] All new tables (S_NEW1–S_NEW5) generated
- [ ] Tables 1 & 2 recomputed with corrected data
- [ ] Repository public with DOI
- [ ] Manuscript Methods/Results/Discussion updated

### Tier 2 Complete When:
- [ ] All 8 required fixes (T2.1–T2.8) marked ✅
- [ ] Table S_NEW6 added
- [ ] All notation inconsistencies resolved
- [ ] All figures regenerated

### Ready for Submission When:
- [ ] Tier 1 ✅
- [ ] Tier 2 ✅
- [ ] Revision letter drafted
- [ ] Co-author review complete
- [ ] PDF compiled with 0 errors
- [ ] Supplementary materials finalized

---

**Document**: Task tracking checklist for P1 JCIM R1  
**Status**: INITIALIZED  
**Last Updated**: 2026-09-09  
**Next Review**: Weekly progress meetings
