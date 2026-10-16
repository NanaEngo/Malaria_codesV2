# URGENT: P7 Analysis Ledger Reconstruction

**Date:** 14 October 2026  
**Priority:** CRITICAL - Blocks manuscript finalization  
**Issue:** Analysis ledger is 6 weeks outdated; manuscript cites results not in ledger

---

## Problem Statement

**Article-writing hard rule 3 violation:**
> "Data → Analysis → Manuscript. No number enters the manuscript except through a written, interpreted entry in `outputs/analysis/analysis-ledger.md`."

**Current state:**
- **Ledger last update:** 24 September 2026 (3-molecule pilot only)
- **Manuscript sections drafted:** 5 October 2026 (complete Phases 1-6)
- **Gap:** All Oct 2-5 Phase 1-6 results missing from ledger
- **Consequence:** Every AUC, Brier score, gradient norm in manuscript lacks provenance

---

## Missing Ledger Entries (from DAR §6)

### Phase 1 PoC (P1 Set A, LOO-CV, n=17)

**LED-003**: ECFP4-MLP Baseline (CORRECTED)
- Source: `results/phase1_proof_of_concept/ecfp4_mlp_loo_summary.json`
- AUC: 0.833 (not 0.467 as in old LED-001)
- Status: COMPUTED (02 Oct 2026)

**LED-004**: GIN Baseline
- Source: `results/phase1_proof_of_concept/gnn_loo_summary.json`
- AUC: 1.000 (overfitting caveat)
- Status: COMPUTED (02 Oct 2026)

**LED-005**: QFE 4q-d1-rzz (PoC)
- Source: `results/phase1_proof_of_concept/qfe_4q_d1_loo_summary.json`
- AUC: 0.933 ± (need to compute from 17 folds)
- Gradient norms: mean 4.23, range [0.13, 22.4]
- Barren plateau: NONE (0% below 1e-6)
- Status: COMPUTED (02 Oct 2026)

**LED-006**: Statistical Comparison (Phase 1)
- Source: `results/phase1_proof_of_concept/statistical_comparison_summary.json`
- QFE vs ECFP4: Δ Brier = -0.067, t = -1.194, p = 0.250
- QFE vs GNN: Δ Brier = +0.021, t = +1.391, p = 0.183
- Cohen's d: small effects
- Decision gate: 1.12 ≥ 0.80 PASS
- Status: COMPUTED (02 Oct 2026)

### Phase 4 Benchmark (P3 subsample n=1000, 5-fold CV)

**LED-007**: ECFP4-RBF Baseline (local, matched subsample)
- Source: `results/phase2_benchmark/ecfp4_rbf_p3sub1000_cv5_summary.json`
- AUC: 0.8693 ± 0.0265 (5 folds)
- Brier: 0.1150 ± 0.0137
- Subsample SHA-256: `d781d9c43923e3d5bbbbbb78dd572c6b091cbceea8946110c3e1dc5e980b5f0a`
- Runtime: 12.2s
- Status: COMPUTED (03 Oct 2026)

**LED-008**: QFE 4q-d1-rzz (P3 subsample, canonical)
- Source: `results/phase2_benchmark/qfe_4q_d1_p3sub1000_cv5_summary.json`
- AUC: 0.8474 ± 0.0129 (5 folds)
- Brier: 0.1243 ± 0.0129
- Gradient norms: mean 0.293, min 0.00105, max 3.527
- Barren plateau: 0.0% below 1e-6
- Runtime: 1095.0s (~18 min)
- Subsample SHA-256: identical to LED-007
- Status: COMPUTED (03 Oct 2026)

**LED-009**: QFE 6q-d1-rzz (ablation)
- Source: `results/phase2_benchmark/qfe_6q_d1_p3sub1000_cv5_summary.json`
- AUC: 0.8230 ± 0.0304
- Runtime: 1926.3s (~32 min)
- Status: COMPUTED (03 Oct 2026)

**LED-010**: QFE 8q-d1-rzz (ablation)
- Source: `results/phase2_benchmark/qfe_8q_d1_p3sub1000_cv5_summary.json`
- AUC: 0.8316 ± 0.0400
- Runtime: 2791.7s (~47 min)
- Status: COMPUTED (03 Oct 2026)

**LED-011**: Ablation Interpretation
- 4q optimal: highest AUC, lowest variance, shortest runtime
- 6q/8q degradation: expressibility-trainability trade-off
- Decision gate: all ≥ 0.80 PASS
- Status: INTERPRETED (03 Oct 2026)

### Phase 5 External Scaffold Split (n=10K, 100% novel scaffolds)

**LED-012**: ECFP4-RBF (scaffold split)
- Source: `results/phase3_scaffold/ecfp4_rbf_ext10k_scaffold_summary.json`
- AUC: 0.8413
- Brier: 0.1603
- Train: 8000, Test: 2000 (0 scaffold overlap)
- Runtime: 813.5s
- Status: COMPUTED (03 Oct 2026)

**LED-013**: QFE 4q-d1-rzz (scaffold split)
- Source: `results/phase3_scaffold/qfe_4q_d1_ext10k_scaffold_summary.json`
- AUC: 0.7831
- Brier: 0.2611
- Gradient norms: mean 0.261, 8.24% below 1e-6 (marginal barren plateau)
- Runtime: 16,035.5s (~4.45 hr)
- Status: COMPUTED (03 Oct 2026)

**LED-014**: Scaffold Generalization Gap
- ECFP4: -0.108 AUC (vs Phase 4 canonical P3 0.9475)
- QFE: -0.064 AUC (vs Phase 4 0.8474)
- QFE gap smaller in absolute terms but starts from lower baseline
- Neither method robust to 100% novel scaffolds
- Status: INTERPRETED (03 Oct 2026)

### Phase 6 HPO (Optuna, 12 trials, EXPLORATORY)

**LED-015**: HPO Best Configuration (trial 7, EXPLORATORY)
- Source: `results/phase4_hpo/qfe_hpo_summary.json`
- 2-fold AUC: 0.8487
- Params: 4q, d1, CZ, hidden=64, dropout=0.072, lr=2.21e-3
- Status: EXPLORATORY (05 Oct 2026)

**LED-016**: HPO Canonical Re-run (trial 7, 5-fold CV)
- Source: `results/phase4_hpo/qfe_4q_d1_cz_hpo_canonical_cv5_summary.json`
- AUC: 0.8468 ± 0.0209 (5 folds)
- Subsample SHA-256: verified identical to Phase 4 (LED-007/008)
- Gradient norms: mean 0.248, 0.0% below 1e-6
- Runtime: 3122s (52 min)
- Decision gate: Δ = -0.0006 vs Phase 4 4q-rzz → BELOW threshold 0.8574
- Conclusion: CZ ≈ RZZ; Phase 4 canonical remains optimal
- Status: CANONICAL (05 Oct 2026)

### ANP Metadata (P1 Set A)

**LED-017**: ANP Chemical Space Characterization
- Source: `data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv`
- Fsp³: mean 0.217, range [0.000, 0.600]
- ACSI: mean 0.213, range [0.088, 0.371]
- Stereocenters: 10 total across 17 molecules
- ANP class: 16 Synthetic, 1 Simple phenolic, 0 Macrocycles
- Status: COMPUTED (02 Oct 2026)

---

## Action Items

### Immediate (Hour 0-2): Rebuild Ledger

1. **Extract Phase 1-6 results** from JSON summaries into standardized ledger entries
2. **Each entry must include:**
   - Method with full parameters
   - Numbers with units & uncertainty (SD or 95% CI)
   - Written interpretation (2-3 sentences)
   - Caveats (1-2 sentences)
   - Links to manuscript claims
   - Source file path + SHA-256 where applicable
3. **Format:** Follow `article-writing/references/analysis-ledger.md` template
4. **Priority order:** LED-003 through LED-017 (15 entries)

### Hour 2-4: Manuscript Alignment Audit

5. **Read Results section** line-by-line
6. **For each number:** verify LED-XXX citation exists
7. **Flag violations:** any number without LED reference
8. **Check Discussion:** every interpretation must link to LED entry
9. **Verify uncertainty:** all ± values match ledger exactly

### Hour 4-6: Update Manuscript

10. **Add LED citations** to every quantitative statement
11. **Insert caveat footnotes** from ledger where needed
12. **Check Conclusion:** reflects Scenario B (LED-016 decision gate)
13. **Abstract:** write from complete ledger (now unblocked)

### Hour 6-8: Refocus Decision

14. **Read DAR §2 refocus rationale** (QMSE vs ECFP4-VQC)
15. **Author decision required:**
    - **Option A:** Keep EXPLORATORY manuscript (complete data, submit now)
    - **Option B:** Wait for QMSE Phase C (60 trials, ~2-3 days)
    - **Option C:** Hybrid manuscript (report both estimands)
16. **Update project-tracking.md** with decision

---

## Who Does What

**Investigation workflow (running):** Read-only audit, generate alignment report

**Coder agent (next):** Rebuild analysis-ledger.md with LED-003 through LED-017

**Author (user):** Make refocus decision (A/B/C above)

**Manuscript agent (after ledger):** Insert LED citations, compile, verify

---

## Success Criteria

✅ **Analysis ledger complete:**
- 15+ entries (LED-003 through LED-017)
- Every Phase 1-6 result documented
- All entries follow template format
- Provenance traceable to result files

✅ **Manuscript alignment verified:**
- Every number has LED-XXX citation
- No orphan numbers (typed from memory)
- Uncertainties match ledger exactly
- Interpretations consistent with ledger caveats

✅ **Refocus decision made:**
- Option A/B/C selected with rationale
- Project-tracking.md updated
- Sprint plan adjusted accordingly

---

## Timeline

- **Hour 0-2:** Ledger rebuild (LED-003 to LED-017)
- **Hour 2-4:** Alignment audit + violation report
- **Hour 4-6:** Manuscript updates (LED citations)
- **Hour 6-8:** Refocus decision + tracking update

**Total:** 8 hours to manuscript-ready state (assuming Option A)

---

**Created:** 2026-10-14  
**Status:** ACTIVE PLAN  
**Next Step:** Wait for investigation workflow completion, then launch ledger rebuild

