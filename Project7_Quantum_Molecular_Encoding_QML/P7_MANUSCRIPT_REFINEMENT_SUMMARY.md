# P7 Manuscript Refinement Summary — 14 October 2026

**Context:** Systematic review of P7 calculations and manuscript state for refinement toward submission.

---

## Current Situation Assessment

### Three Parallel Tracks Discovered

**Track 1: ECFP4-VQC Pipeline (EXPLORATORY - Complete)**
- **Scientific Question:** "Can quantum feature extraction improve ECFP4-SVM?"
- **Status:** All phases complete (Oct 2-5, 2026)
- **Key Result:** AUC 0.8468 ± 0.0209 (HPO canonical, 5-fold CV)
- **Scenario:** B (competitive, not superior to ECFP4)
- **Data Quality:** Full provenance, SHA-256 verified, all 6 phases documented
- **Manuscript:** Complete draft (Intro, Methods, Results, Discussion, Conclusion) describes this pipeline

**Track 2: QMSE+TF Hybrid (NEW CANONICAL - Incomplete)**
- **Scientific Question:** "Can structure-direct quantum encoding overcome stereochemical/scaffold blind spots?"
- **Status:** Phase A complete (preprocessing), Phase B smoke-test complete, Phase C trial 0 only
- **Key Result:** Phase A: 19,849/19,849 molecules encoded (100% success); Phase B: PoC AUC 0.733 (untuned)
- **Data Quality:** Phase A frozen with SHA-256; Phase C incomplete
- **Manuscript:** Not yet written (refocus happened Oct 6, AFTER manuscript draft)

**Track 3: Analysis Ledger (CRITICAL GAP)**
- **Last Update:** Sept 24, 2026 (3-molecule pilot only)
- **Missing:** ALL Phase 1-6 results (Oct 2-5)
- **Impact:** Every number in manuscript violates article-writing rule #3 (no provenance)
- **Status:** Rebuild workflow ACTIVE (LED-003 through LED-017)

---

## Active Workflows

### Workflow 1: Investigation (Read-Only Audit)
- **ID:** wf_2d5857a8f6d1af28
- **Status:** Running
- **Goal:** Complete inventory of all calculation results, verify DAR-manuscript alignment
- **Output:** `manuscript/outputs/critical-reviews/calculation-review-20261014.md`
- **ETA:** ~30-45 minutes

### Workflow 2: Ledger Rebuild (Documentation)
- **ID:** wf_a3c65f4f1d3d3902
- **Status:** Running (3 steps: read-sources → write-ledger → verify)
- **Goal:** Extract Phase 1-6 results into 15 new ledger entries (LED-003 to LED-017)
- **Output:** Updated `manuscript/outputs/analysis/analysis-ledger.md`
- **ETA:** ~45-60 minutes

---

## Key Findings

### ✅ Strengths

1. **Complete ECFP4-VQC data:** All phases executed, results validated, provenance clean
2. **Manuscript structure solid:** Intro, Methods, Results, Discussion follow proper narrative
3. **Honest-negative framing:** Scenario B properly acknowledged throughout
4. **HPO canonical validation:** Trial 7 re-run with 5-fold CV confirms Phase 4 result
5. **Statistical rigor:** Gradient diagnostics, ablation studies, scaffold split all documented

### ⚠️ Critical Issues

1. **Analysis ledger 6 weeks outdated:** Only contains Sept 24 pilot data
2. **Zero provenance for manuscript numbers:** Every AUC/Brier/gradient value lacks LED-XXX citation
3. **Refocus timing mismatch:** Manuscript describes EXPLORATORY; DAR §2 says NEW CANONICAL
4. **Decision point unresolved:** Which estimand to publish? (ECFP4-VQC complete vs QMSE incomplete)

### 📊 Data Inventory (from DAR §6)

**Phase 1 (PoC, n=17 LOO-CV):**
- ECFP4-MLP: AUC 0.833
- GIN: AUC 1.000 (overfitting)
- QFE 4q-d1-rzz: AUC 0.933
- Statistical tests: no significance (n=17 underpowered)

**Phase 4 (P3 subsample n=1000, 5-fold CV):**
- ECFP4-RBF: AUC 0.8693 ± 0.0265
- QFE 4q-d1-rzz: AUC 0.8474 ± 0.0129 (CANONICAL)
- QFE 6q: AUC 0.8230 ± 0.0304 (ablation)
- QFE 8q: AUC 0.8316 ± 0.0400 (ablation)
- Optimal: 4-qubit

**Phase 5 (Scaffold split n=10K):**
- ECFP4-RBF: AUC 0.8413
- QFE 4q-d1-rzz: AUC 0.7831
- Barren plateau: 8.24% batches (marginal risk)

**Phase 6 (HPO):**
- Best exploratory: trial 7 (4q, CZ, hidden=64), AUC 0.8487 (2-fold)
- Canonical re-run: AUC 0.8468 ± 0.0209 (5-fold)
- Decision gate: BELOW threshold (Δ = -0.0006)
- Conclusion: Phase 4 4q-rzz remains optimal

---

## Decision Point: Which Manuscript to Finalize?

### Option A: ECFP4-VQC (Fast Track — Recommended)

**Rationale:**
- Complete data (all phases, HPO canonical validation)
- Manuscript draft 90% complete
- Honest-negative Scenario B is scientifically valid
- Submission-ready in 2-3 days after ledger rebuild

**Remaining work:**
1. ✅ (Active) Rebuild analysis ledger with LED-003 to LED-017
2. Insert LED-XXX citations into manuscript
3. Write Abstract (now unblocked)
4. Generate 5 figures (ROC curves, ablation bar chart, scaffold split, circuit diagram)
5. Final review passes
6. Cover letter

**Timeline:** 3-4 days to submission

**Target journal:** RSC Digital Discovery (8,000 words, preprint-friendly)

**Scientific contribution:** 
- First demonstration of QFE at antimalarial prediction scale (n=1000+)
- Honest-negative Scenario B at multiple scales (n=17, n=1000, n=10K scaffold)
- Ablation study confirms 4-qubit optimal for NISQ-era ECFP4-VQC
- Expressibility-trainability trade-off documented
- Marginal barren plateau at n=8K training scale (first report)

---

### Option B: Wait for QMSE (High Risk)

**Rationale:**
- New canonical question (structure-direct encoding)
- Addresses stereochemical blind spots directly
- Potentially stronger scientific contribution

**Blockers:**
- Phase C HPO incomplete (trial 0 of 60)
- Estimated 2-3 days runtime (60 trials × 3-fold CV × 1000 subsample)
- No guarantee of better result than ECFP4-VQC
- Manuscript rewrite required (QMSE is different architecture)

**Risk:**
- If QMSE ≤ ECFP4-VQC, we have TWO honest-negatives and no manuscript
- Delay pushes into November (competes with P1/P2 submission timelines)

**Timeline:** +2-3 weeks from now

---

### Option C: Hybrid Paper (Two Estimands)

**Rationale:**
- Report both ECFP4-VQC (complete) and QMSE Phase A/B (incomplete)
- Frame as "two approaches to quantum encoding"

**Issues:**
- QMSE Phase C incomplete → can't compare fairly
- Manuscript becomes long (>10,000 words) and unfocused
- Reviewers may see it as "two half-papers"

**Not recommended** unless QMSE Phase C completes AND shows advantage

---

## Recommended Path Forward

### Immediate (Hours 0-4): Complete Ledger + Investigation

1. ✅ (Active) Wait for ledger rebuild workflow to complete
2. ✅ (Active) Wait for investigation workflow to complete
3. Review both reports for alignment issues
4. Make final decision: Option A / B / C

### Short-term (Days 1-2): Finalize ECFP4-VQC Manuscript (if Option A)

4. Insert LED-XXX citations into all manuscript sections
5. Write Abstract from complete ledger entries
6. Generate 5 figures:
   - Fig 1: Workflow schematic (TikZ)
   - Fig 2: QFE circuit diagram (TikZ)
   - Fig 3: Phase 4 ROC curves (matplotlib, 5 folds)
   - Fig 4: Ablation bar chart (4q/6q/8q)
   - Fig 5: Phase 5 scaffold split + gradient norms
7. Compile manuscript, check for LaTeX errors
8. Run anti-AI scan (should be 0 banned patterns)

### Review (Days 3-4): Article-Writing L3 Loop

9. Execute independent review passes:
   - `bmad-review-adversarial-general` (weakest arguments)
   - `bmad-review-edge-case-hunter` (boundary conditions)
   - `peer-review` (technical correctness)
   - `scientific-critical-thinking` (falsifiability)
   - `scholar-evaluation` (ScholarEval dimensions)
10. Address CRITICAL + HIGH findings
11. Run final audit checklist (L4)
12. Write cover letter

### Submission (Day 5): RSC Digital Discovery

13. Download RSC template (if converting from ChemRxiv format)
14. Convert figures to RSC specifications
15. Generate submission package
16. Upload to journal portal OR preprint to ChemRxiv first

---

## If QMSE Phase C Completes Before Decision

**Trigger:** Phase C HPO finishes with best AUC available

**Rapid assessment protocol:**
1. Check best QMSE AUC vs ECFP4 baseline (0.8693)
2. If QMSE > 0.87 (improvement): **Consider Option C** (hybrid paper)
3. If QMSE 0.82-0.87 (competitive): **Stick with Option A** (ECFP4-VQC only)
4. If QMSE < 0.82 (underperformance): **Definitely Option A** (ECFP4-VQC canonical)

**Do NOT delay ECFP4-VQC submission waiting for QMSE** unless QMSE Phase C shows clear advantage in first 10 trials

---

## Success Metrics

### For Option A (ECFP4-VQC submission)

✅ **Analysis ledger complete:** 15+ entries, all Phase 1-6 results
✅ **Manuscript alignment:** Every number has LED-XXX citation
✅ **Figures generated:** 5 main figures, vector format
✅ **Abstract written:** 200 words, reflects Scenario B
✅ **Review passes:** CRITICAL + HIGH findings resolved
✅ **Audit checklist:** All rows PASS with evidence
✅ **Cover letter:** 1 page, honest-negative framing
✅ **Submission package:** PDF + source + figures + SI

### For Option B (Wait for QMSE)

⏳ **Phase C completes:** 60 trials, best AUC > 0.87
⏳ **Canonical re-run:** 5-fold CV on best config
⏳ **Manuscript rewrite:** QMSE architecture, BondOrderMatrix encoding
⏳ **New figures:** QMSE-specific circuit, encoding comparison
⏳ **Submission:** +2-3 weeks from now

---

## Questions for Author

1. **Primary decision:** Option A (submit ECFP4-VQC now) or Option B (wait for QMSE Phase C)?
   - **My recommendation:** Option A (complete data, honest-negative is valid, 3-4 day timeline)

2. **Target journal confirmed?** RSC Digital Discovery (provisional) or other?

3. **Preprint strategy?** ChemRxiv first, then journal? Or direct submission?

4. **QMSE Phase C status?** Is it running? PID? Expected completion date?

5. **Priority vs P1/P2?** P1 V8 seeking new venue, P2 V2609C technically ready—does P7 compete?

---

## Next Steps (Waiting on Workflows)

### When Ledger Rebuild Completes (~60 min):

1. Read `manuscript/outputs/analysis/analysis-ledger.md`
2. Verify LED-003 through LED-017 are complete
3. Read `manuscript/outputs/analysis/ledger-rebuild-verification.md`
4. Launch manuscript citation insertion workflow

### When Investigation Completes (~45 min):

1. Read `manuscript/outputs/critical-reviews/calculation-review-20261014.md`
2. Review alignment table and missing entries
3. Confirm refocus recommendation
4. Update `manuscript/project-tracking.md` with decision

### After Both Complete (~90 min):

1. **Make final decision:** Option A / B / C
2. **If Option A:** Launch manuscript finalization workflow (citations + abstract + figures)
3. **If Option B:** Estimate QMSE Phase C completion, plan holding pattern
4. **If Option C:** Design hybrid paper structure, plan QMSE section integration

---

**Created:** 14 October 2026  
**Model:** Claude Sonnet 4.5  
**Status:** Awaiting workflow completion + author decision  
**Priority:** HIGH (blocks P7 submission timeline)

**Files to monitor:**
- `manuscript/outputs/analysis/analysis-ledger.md` (ledger rebuild)
- `manuscript/outputs/analysis/ledger-rebuild-verification.md` (verification)
- `manuscript/outputs/critical-reviews/calculation-review-20261014.md` (investigation)
- `manuscript/project-tracking.md` (decision tracking)

