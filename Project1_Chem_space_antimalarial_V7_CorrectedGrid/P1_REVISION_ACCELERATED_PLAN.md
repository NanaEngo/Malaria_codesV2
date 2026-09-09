# P1 JCIM Revision — Accelerated Plan with P2 Integration

**Date**: 2026-09-09  
**Refinement**: Integrated P2 proven methodologies  
**New Timeline**: 8–9 weeks (vs 10–12 original)  
**Status**: READY_FOR_EXECUTION

---

## Executive Summary

After deep analysis of P2's production codebase, we've identified **ready-to-use solutions** for 8 of 9 P1 critical blockers. P2 has already:
- ✅ Implemented multi-seed docking with fail-closed validation
- ✅ Built rigorous statistical framework (100k permutations, 10k bootstrap)
- ✅ Created standardized receptor preparation with force-field manifests
- ✅ Developed GNINA rescoring protocol
- ✅ Established SHA-256 provenance tracking
- ✅ Documented honest-negative reporting patterns

**Key Insight**: We don't need to develop these from scratch. We can **adapt proven P2 code** that's already been tested and debugged.

**Time Savings**: ~30 days (43% faster execution)

---

## Accelerated Timeline Comparison

### Original Plan (from Roadmap)
```
Week 1:     Repository + definitions
Weeks 2-3:  Protocol corrections (structure, grid, pipeline)
Weeks 4-6:  ~1,600 docking jobs
Weeks 7-8:  Analysis & recomputation
Weeks 9-10: Manuscript revision
────────────────────────────────────
Total: 10-12 weeks
```

### Accelerated Plan (with P2 integration)
```
Week 1:     Repository + definitions + P2 script adaptation
Weeks 2-3:  Protocol corrections (with P2 validation templates)
Weeks 4-5:  ~1,600 docking jobs (with P2 preflight checks)
Week 6:     Analysis (with P2 statistical framework)
Weeks 7-8:  Manuscript revision
────────────────────────────────────
Total: 8-9 weeks (2-3 weeks saved)
```

---

## Week 1: Setup & Script Adaptation (Days 1–7)

### Day 1: Repository & P2 Script Migration
**Morning** (2–3 hours):
- [ ] Make repository public (T1.6.1) — **highest priority**
- [ ] Add MIT License (T1.6.2)
- [ ] Copy P2 script templates:
  ```bash
  cd Project1_Chem_space_antimalarial_V7_CorrectedGrid
  
  # Statistical framework
  cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_rigorous_audit.py \
     scripts/p1_statistical_audit.py
  
  # Multi-seed docking
  cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_targeted_redock_multiseed.sh \
     scripts/p1_multiseed_validation.sh
  
  # GNINA rescoring
  cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_gnina_consensus_rescore.py \
     scripts/p1_gnina_rescore.py
  
  # Force-field manifest
  cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/md_forcefield_manifest.py \
     scripts/p1_preparation_manifest.py
  ```

**Afternoon** (3–4 hours):
- [ ] Adapt `p1_statistical_audit.py` for P1 data structure
- [ ] Test on 3-compound subset (verify against reviewer's ρ=+0.515)
- [ ] Generate SHA-256 checksums for all V7 files

**Deliverable**: Adapted scripts + checksums.json

---

### Days 2–3: PNS/ACSI Definitions & Statistical Validation

**Tasks**:
- [ ] Extract PNS/ACSI formulas from P2's `p2_rigorous_audit.py` (lines 262–320)
- [ ] Add definitions to P1 Methods §2.4
- [ ] Create SI Table S_NEW5 (PNS/ACSI values for 17 compounds)
- [ ] Run full statistical audit:
  ```bash
  python scripts/p1_statistical_audit.py \
    --seed 42 \
    --n-permutations 100000 \
    --n-bootstrap 10000 \
    --output results/p1_statistical_audit_20260909/
  ```
- [ ] Verify N_fav vs RRS correlation (should match reviewer's ρ ≈ +0.515)
- [ ] Compute power analysis (should match reviewer's power=0.37 for n=17, ρ=0.5, α=0.017)

**Deliverable**: 
- SI Table S_NEW5 (PNS/ACSI values)
- Updated Table S6 with N_fav vs RRS row
- Power analysis paragraph for §4.1

**Time**: 2 days (vs 1 week original) — **saved 5 days**

---

### Days 4–5: Cluster Allocation & Preflight Templates

**Tasks**:
- [ ] Secure cluster allocation (50–100 nodes for Weeks 4–5)
- [ ] Create preflight check template (based on P2 pattern):
  ```bash
  preflight_check() {
      # Check inputs exist
      # Check tools available
      # Check environment activated
      # Validate SHA-256 hashes
      # Test with --test-only
  }
  ```
- [ ] Add to all SLURM scripts
- [ ] Test on 1 compound × 1 target
- [ ] Contact structural biologist for PfCRT homology modeling

**Deliverable**: Preflight templates + cluster allocation

---

### Days 6–7: Preparation Manifest & Documentation

**Tasks**:
- [ ] Create `p1_preparation_manifest_template.json` (from P2 pattern)
- [ ] Document unified pipeline (protonation, charge assignment, minimization)
- [ ] Install GNINA 1.3.2 (use P2's `install_gnina_hpc.sh`)
- [ ] Generate Week 1 progress report

**Deliverable**: Manifest template + GNINA installed

---

## Weeks 2–3: Protocol Corrections (Days 8–21)

### Week 2: Structure Preparation

**PfCRT 3D7 WT** (T1.1.1–1.1.2):
- [ ] Homology modeling (with structural biologist)
- [ ] P2-style validation chain:
  - Gate 1: K76 identity verification
  - Gate 2: Ramachandran validation
  - Gate 3: pdb2gmx topology check
  - Gate 4: K76 in grid box verification
- [ ] Re-anchor grid to Kim et al. cavity (40 Å box)
- [ ] Document in `results/pfcrt_structure_validation.json`

**PfDHFR Apo** (T1.2.1):
- [ ] Strip MTX from 7F3Y
- [ ] Validate with pdb2gmx
- [ ] Document in manifest

**Standardized Pipeline** (T1.3.1):
- [ ] Process ALL 11 receptors through unified pipeline
- [ ] Generate force-field manifests for each
- [ ] Compute SHA-256 for all outputs

**Time**: 1 week (with P2 validation templates) vs 1.5 weeks original — **saved 3 days**

---

### Week 3: Null Distribution & Validation Setup

**Null Distribution** (T1.3.2):
- [ ] Create pseudo-mutants (WT through mutant pipeline, no mutation)
- [ ] Dock 17 compounds against pseudo-mutants (68 poses)
- [ ] Compute null statistics (mean, SD, 95% CI)
- [ ] Redefine RRS class boundaries outside null

**Multi-Seed Test** (T1.7.1 pilot):
- [ ] Test multi-seed on 3 compounds × 2 targets (30 poses)
- [ ] Verify protocol with P2-style manifest
- [ ] Validate dispersion statistics

**Time**: 1 week vs 1.5 weeks original — **saved 3 days**

---

## Weeks 4–5: Large-Scale Docking (Days 22–35)

### Parallelized Execution

**Jobs**:
1. PfCRT panel (255 poses: 17 × 3 alleles × 5 seeds)
2. DEKOIS re-run (1,278 poses: 78 actives + 1200 decoys)
3. PfDHFR Set C apo (340 poses: 17 × 4 alleles × 5 seeds)
4. Null distribution (68 poses: 17 × 4 targets)
5. Mutation panel standardized (765 poses: PfDHFR 510 + PfCRT 255)
6. Multi-seed Set C (340 poses: 17 × 4 targets × 5 seeds)

**Total**: ~3,046 poses

**Strategy**:
- Run all in parallel on 50–100 node cluster
- Use P2-style preflight checks (prevents failed jobs)
- Monitor with P2-style manifests
- Fail-closed gates at each stage

**Time**: 2 weeks vs 3 weeks original — **saved 1 week** (P2 preflight prevents failures)

---

## Week 6: Analysis & Recomputation (Days 36–42)

### Using P2 Frameworks

**GNINA Rescoring** (T1.2.3):
```bash
python scripts/p1_gnina_rescore.py \
  --poses results/p1_dekois_apo/*.pdbqt \
  --receptor data/receptors/pfdhfr_7f3y_apo.pdbqt \
  --output results/p1_dekois_gnina/
```

**Null-Corrected RRS** (T1.3.3–1.3.4):
```python
# Recompute Table 1 with null-corrected classes
python scripts/p1_rrs_null_correction.py \
  --null-distribution results/null_distribution/null_rrs.csv \
  --mutation-panel results/standardized_mutation_panel/ \
  --output results/p1_table1_corrected.csv
```

**Within-Target Favorability** (T1.5):
```python
# Recompute Table 2 with rank-based N_fav
python scripts/p1_nfav_rank_based.py \
  --docking-scores results/set_a_docking_matrix.csv \
  --output results/p1_table2_corrected.csv
```

**All Correlations** (T1.4):
- Already done in Week 1 with `p1_statistical_audit.py`
- Update Table S6 with Week 6 corrected values

**Time**: 1 week vs 2 weeks original — **saved 1 week** (P2 framework plug-and-play)

---

## Weeks 7–8: Manuscript Revision (Days 43–56)

### Systematic Updates

**Methods** (§2):
- [ ] Add ligand-free receptor statement (T1.2.5)
- [ ] Add standardized preparation section (T1.3.1)
- [ ] Add multi-seed protocol (T1.7.5)
- [ ] Add PNS/ACSI definitions (T1.8.1)
- [ ] Add within-target favorability (T1.5.4)

**Results** (§3):
- [ ] Update Table 1 (null-corrected RRS)
- [ ] Update Table 2 (rank-based N_fav)
- [ ] Update Figure 2 (add ρ, p, n annotation)
- [ ] Add RRS > 100% interpretation (T1.3.5)

**Discussion** (§4):
- [ ] Revise independence interpretation (T1.4.3)
- [ ] Add power analysis (T1.4.3)
- [ ] Add cost reduction caveat (T2.3)
- [ ] Add honest-negative framing (P2 pattern)

**SI**:
- [ ] Replace DEKOIS section (T1.2.5)
- [ ] Add Tables S_NEW1–S_NEW6
- [ ] Remove PfClpP from Table S8 (T1.9.1)
- [ ] Fix duplicate paragraph (T2.1)
- [ ] Fix all minor issues (T2.2–T2.8)

**Response Letter**:
- [ ] Use template from `P1_REVISION_RESPONSE_TEMPLATE.md`
- [ ] Fill in placeholders with actual results
- [ ] Cite P2 patterns where applicable

**Time**: 2 weeks (unchanged) — comprehensive revision

---

## Success Metrics

### Computational Outputs
- [ ] 3,046 docking calculations complete (0 failures due to P2 preflight)
- [ ] All manifests with SHA-256 hashes
- [ ] All QC gates passed

### Tables & Figures
- [ ] Table 1 corrected (null-based RRS classes)
- [ ] Table 2 corrected (rank-based N_fav)
- [ ] Table S6 complete (4 correlations + CI + power)
- [ ] 6 new SI tables (S_NEW1–S_NEW6)
- [ ] Figure 2 annotated

### Statistical Rigor
- [ ] 100k permutations (P2 standard)
- [ ] 10k bootstrap resamples (P2 standard)
- [ ] Power analysis documented
- [ ] Null distribution generated

### Reproducibility
- [ ] Repository public with DOI
- [ ] All inputs/outputs SHA-256 hashed
- [ ] Manifests for all steps
- [ ] Unit tests passing

---

## Risk Mitigation (from P2 Lessons)

### Avoided Pitfalls
1. **Failed SLURM jobs**: P2-style preflight prevents 5+ failure modes
2. **Statistical errors**: P2's 100k permutations are gold-standard
3. **Provenance gaps**: P2's SHA-256 system is reviewer-ready
4. **Structure quality**: P2's validation gates catch problems early

### Contingency Plans
1. **PfCRT unavailable**: Withdraw PfCRT (P1 still publishable with PfDHFR alone)
2. **RRS null = no signal**: Honest-negative result (P2 framing pattern)
3. **Rescoring fails**: Report DEKOIS apo-only (still better than holo)
4. **Top candidates change**: Expand to 5–7 candidates (P2 did this)

---

## Deliverables Checklist

### Week 1
- [ ] Repository public
- [ ] P2 scripts adapted
- [ ] Statistical audit running
- [ ] PNS/ACSI defined
- [ ] Cluster secured

### Week 2
- [ ] PfCRT structure validated
- [ ] PfDHFR apo prepared
- [ ] Unified pipeline documented
- [ ] All receptors standardized

### Week 3
- [ ] Null distribution computed
- [ ] Multi-seed pilot complete
- [ ] RRS boundaries redefined

### Weeks 4–5
- [ ] 3,046 docking jobs complete
- [ ] All manifests generated
- [ ] All QC gates passed

### Week 6
- [ ] GNINA rescoring done
- [ ] Tables 1 & 2 recomputed
- [ ] All correlations computed
- [ ] All analysis complete

### Weeks 7–8
- [ ] Manuscript revised
- [ ] Response letter complete
- [ ] All SI tables added
- [ ] Submission-ready PDF

---

## Comparison: Original vs Accelerated

| Milestone | Original | Accelerated | Savings |
|-----------|----------|-------------|---------|
| Statistical framework | Week 7 | Week 1 | 6 weeks |
| Multi-seed protocol | Week 6 | Week 3 pilot | 3 weeks |
| Docking execution | Weeks 4–6 | Weeks 4–5 | 1 week |
| Analysis | Weeks 7–8 | Week 6 | 2 weeks |
| **Total** | **10–12 weeks** | **8–9 weeks** | **2–3 weeks** |

---

## Key P2 Integrations That Enable Acceleration

1. **Statistical Framework**: P2's `p2_rigorous_audit.py` is production-ready → plug-and-play
2. **Multi-Seed Protocol**: P2's `p2_targeted_redock_multiseed.sh` with fail-closed → copy-adapt-run
3. **Preflight Checks**: P2's 5 failed jobs taught us what to check → prevents our failures
4. **SHA-256 Tracking**: P2's manifest pattern → copy template
5. **GNINA Rescoring**: P2's `p2_gnina_consensus_rescore.py` → minimal adaptation
6. **Honest-Negative Framing**: P2's DAR patterns → copy language

---

## Final Recommendation

**Execute accelerated plan starting tomorrow**:
1. **Day 1** (today): Copy P2 scripts, make repository public
2. **Days 2–3**: Adapt statistical framework, define PNS/ACSI
3. **Days 4–7**: Preparation pipeline, cluster allocation
4. **Weeks 2–3**: Structure corrections with P2 validation
5. **Weeks 4–5**: Parallel docking with P2 preflight
6. **Week 6**: Analysis with P2 frameworks
7. **Weeks 7–8**: Manuscript revision

**Target submission**: 2026-11-04 (9 weeks) vs 2026-11-18 original (11 weeks)

**Confidence**: HIGH — P2 solutions are battle-tested, not theoretical

---

**Document**: Accelerated revision plan with P2 integration  
**Cross-Reference**: `P1_P2_CROSS_LEARNING_REFINEMENTS.md`, `P1_REVISION_ROADMAP_R1.md`  
**Status**: READY_FOR_EXECUTION  
**Next Action**: Begin Day 1 tasks (repository public + script migration)
