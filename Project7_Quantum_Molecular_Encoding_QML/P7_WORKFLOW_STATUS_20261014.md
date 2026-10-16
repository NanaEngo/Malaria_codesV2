# P7 Workflow Status Report — 14 October 2026

**Time:** Active review session  
**Model:** Claude Sonnet 4.5  
**Skills Active:** article-writing + scientific-writing

---

## Executive Summary

**Overall Status:** 🟡 IN PROGRESS — Two critical workflows running, manuscript technically complete but needs provenance updates

**Key Finding:** Manuscript is 90% submission-ready but missing analysis ledger provenance for all Phase 1-6 results. Workflows are actively addressing this gap.

**Timeline to Submission (Option A):** 2-3 days after workflow completion

---

## Active Workflows (Both Running)

### Workflow 1: Investigation Audit
- **ID:** `wf_2d5857a8f6d1af28`
- **Type:** bundled://investigate
- **Agent:** wf-planner
- **Status:** Running (step: investigate)
- **Purpose:** Complete read-only audit of ALL P7 calculations
- **Output:** `manuscript/outputs/critical-reviews/calculation-review-20261014.md`
- **ETA:** ~30-45 minutes total
- **Current duration:** ~45 minutes (should complete soon)

**What it's doing:**
- Reading all result files in `results/phase{1..4}_*/`
- Cross-checking DAR §6 entries against actual JSON summaries
- Verifying manuscript claims have data support
- Identifying any orphan calculations or missing results
- Generating alignment table + refocus recommendation

### Workflow 2: Ledger Rebuild
- **ID:** `wf_a3c65f4f1d3d3902`
- **Type:** Generated 3-step sequence
- **Status:** Running (step 1 of 3)
- **Progress:**
  - [🔄 RUNNING] read-sources (wf-planner) — reading 12+ JSON files
  - [⏳ PENDING] write-ledger (wf-coder) — will write LED-003 to LED-017
  - [⏳ PENDING] verify (wf-coder) — will cross-check against DAR
- **Output:** Updated `manuscript/outputs/analysis/analysis-ledger.md`
- **ETA:** ~45-60 minutes total
- **Current duration:** ~45 minutes (step 1 completing)

**What it's doing:**
- **Step 1:** Extract exact values from all Phase 1-6 JSON summaries
- **Step 2:** Write 15 new ledger entries following article-writing template
- **Step 3:** Verify every entry against DAR §6 and flag discrepancies

---

## Manuscript Current State

### ✅ Complete Components

**Structure (17 pages, 800KB PDF):**
- Title page with ORCID links ✅
- Abstract (pending, needs ledger complete first) 🟡
- Introduction (5 paragraphs, ANP-centered) ✅
- Methods (8 subsections, full protocol) ✅
- Results (4 subsections, 5 tables, 5 figures) ✅
- Discussion (6 subsections, Scenario B framing) ✅
- Conclusion (honest-negative, hardware outlook) ✅
- References (bibliography started, needs completion) 🟡

**Figures (all generated, vector PDFs):**
1. `fig1_workflow.pdf` (117KB) — Workflow schematic ✅
2. `fig2_circuit.pdf` (106KB) — QFE circuit diagram ✅
3. `fig3_roc_curves.pdf` (36KB) — Phase 4 ROC curves (5 folds) ✅
4. `fig4_ablation_bar.pdf` (29KB) — Ablation bar chart (4q/6q/8q) ✅
5. `fig5_scaffold_gradient.pdf` (36KB) — Scaffold split + gradients ✅

**Data Provenance:**
- All Phase 1-6 calculations complete (Oct 2-5, 2026) ✅
- DAR §6 fully documented with SHA-256 hashes ✅
- Results files: 12 JSON summaries + CSV detail files ✅

### ⚠️ Critical Gap

**Analysis Ledger Outdated:**
- Last update: Sept 24, 2026 (3-molecule pilot)
- Missing: ALL Phase 1-6 results (15 entries)
- Impact: Every number in manuscript lacks LED-XXX provenance citation
- Violates: article-writing hard rule #3
- **Being fixed by:** Workflow 2 (ledger rebuild, running now)

### 🟡 Pending Items

**After Workflows Complete:**
1. Insert LED-XXX citations into manuscript (every AUC/Brier/gradient value)
2. Write Abstract (200 words) from complete ledger
3. Complete bibliography (20+ entries needed)
4. Run anti-AI scan (expected: 0 banned patterns)
5. Execute L3 review passes (adversarial, edge-case, peer-review)
6. Final audit checklist (L4)
7. Write cover letter (1 page)

---

## Scientific Content Summary

### Estimand: ECFP4-VQC Pipeline (EXPLORATORY, Complete)

**Central Question:**  
"Can quantum feature extraction (ECFP4→VQC→SVM) improve antimalarial activity prediction over classical ECFP4-SVM?"

**Answer:** Scenario B (competitive, not superior)

**Key Results:**
- **Phase 1 PoC (n=17, LOO-CV):** QFE AUC 0.933 vs ECFP4 0.833
- **Phase 4 Benchmark (n=1000, 5-fold CV):** QFE AUC 0.8474 ± 0.0129 vs ECFP4 0.8693 ± 0.0265
- **Phase 4 Ablation:** 4-qubit optimal > 6q > 8q (expressibility-trainability trade-off)
- **Phase 5 Scaffold (n=10K, 100% novel):** QFE AUC 0.7831 vs ECFP4 0.8413
- **Phase 6 HPO:** Best canonical AUC 0.8468 ± 0.0209 (trial 7: 4q-CZ-hidden64)

**Interpretation:**
- QFE consistently 2.5-5.8% below classical baseline
- Outperforms P3 quantum-inspired QKS (0.8385)
- No barren plateau at n=800, marginal (8.24%) at n=8K
- Neither method robust to scaffold novelty (both degrade ~6-11%)

**Scientific Validity:**
- All three outcomes (advantage/equivalence/underperformance) were pre-declared valid
- Honest-negative reporting follows P3 precedent
- Full provenance: SHA-256 hashes, frozen splits, gradient diagnostics
- Decision gates pre-registered and met

**Contribution:**
- First ECFP4-VQC demonstration at drug discovery scale (n=1K+)
- Expressibility-trainability trade-off documented (4q optimal)
- Marginal barren plateau at scale (first report for this architecture)
- Establishes Scenario B ceiling for ECFP4-starting quantum pipelines

---

## The Refocus Situation

**DAR §2 Refocus (Oct 6, 2026):**

AGENTS.md and DAR §2 document a refocus from ECFP4-VQC (archived as EXPLORATORY) to a new "structure-direct QMSE+TF hybrid" pipeline addressing stereochemical blind spots.

**Status of New Pipeline:**
- Phase A (preprocessing): ✅ Complete (19,849/19,849 molecules, 100% success)
- Phase B (smoke-test): ✅ Complete (PoC AUC 0.733, untuned)
- Phase C (HPO): 🔄 Trial 0 only (60 trials planned, ~2-3 days)

**Manuscript Mismatch:**

The current 17-page manuscript describes the **EXPLORATORY ECFP4-VQC** pipeline (complete data), NOT the new QMSE pipeline (incomplete). This creates a decision point.

---

## Decision Point: Which Paper to Finalize?

### ✅ Option A: ECFP4-VQC Manuscript (RECOMMENDED)

**Pros:**
- Complete data with full provenance
- Manuscript 90% ready (just needs ledger citations)
- Honest-negative Scenario B is scientifically valid contribution
- 2-3 day timeline to submission
- Does not compete with P1/P2 timelines
- QMSE can be separate paper when Phase C completes

**Cons:**
- Doesn't address the "new canonical" QMSE question
- EXPLORATORY label might seem less important

**Recommendation:** This is the pragmatic choice. Complete data, honest science, fast timeline.

### ⚠️ Option B: Wait for QMSE Phase C

**Pros:**
- Addresses "structure-direct encoding" question directly
- Potentially stronger scientific contribution if QMSE shows advantage

**Cons:**
- Phase C incomplete (trial 0 of 60)
- 2-3 day runtime minimum
- No guarantee QMSE > ECFP4-VQC
- Complete manuscript rewrite needed
- Delays P7 by 2-3 weeks
- Risk: if QMSE ≤ ECFP4, have TWO honest-negatives and no manuscript

**Recommendation:** High risk, uncertain payoff. Only if QMSE is strategically critical.

### 🤔 Option C: Hybrid Paper

**Pros:**
- Report both estimands

**Cons:**
- QMSE incomplete → unfair comparison
- Manuscript becomes unfocused
- Reviewers may see "two half-papers"

**Recommendation:** Not recommended unless QMSE Phase C completes AND shows clear advantage.

---

## Recommendations

### Immediate (Next 1-2 hours):

1. **Monitor workflows:** Both should complete within 60-90 minutes
2. **Review outputs:**
   - `manuscript/outputs/critical-reviews/calculation-review-20261014.md`
   - `manuscript/outputs/analysis/analysis-ledger.md`
   - `manuscript/outputs/analysis/ledger-rebuild-verification.md`
3. **Make decision:** Confirm Option A (ECFP4-VQC) vs Option B (wait for QMSE)

### If Option A (Recommended):

**Day 1 (Today):**
- ✅ Wait for ledger rebuild completion
- Insert LED-XXX citations into all manuscript sections
- Write Abstract from complete ledger
- Update project-tracking.md with Option A decision

**Day 2:**
- Complete bibliography (20+ entries)
- Run manuscript compilation tests
- Anti-AI scan (should be clean)
- Generate supplementary information file

**Day 3:**
- Execute L3 review passes (6 parallel reviews)
- Address CRITICAL + HIGH findings only
- Update manuscript based on reviews

**Day 4:**
- Final audit checklist (L4)
- Write cover letter (1 page, honest-negative framing)
- Generate submission package

**Day 5:**
- Submit to RSC Digital Discovery OR
- Preprint to ChemRxiv first (then journal)

### If Option B:

**Days 1-3:**
- Monitor QMSE Phase C HPO progress (60 trials)
- Hold all manuscript work

**After Phase C:**
- Rapid assessment: QMSE AUC vs 0.8693 baseline
- If advantage: Plan hybrid paper (Option C)
- If equivalent/worse: Execute Option A (ECFP4-VQC)

---

## Technical Quality Metrics

### ✅ Strengths

**Data Quality:**
- Full SHA-256 provenance for all datasets
- Frozen train/test splits (seed=42)
- Gradient diagnostics at every phase
- Statistical tests with effect sizes
- Ablation studies (4q/6q/8q)
- Honest-negative framing throughout

**Manuscript Quality:**
- 17 pages, proper structure (IMRAD)
- 5 vector figures (publication-ready)
- 5 tables with complete metrics
- Scenario B consistently framed
- Methods section reproducible
- Discussion addresses limitations

**Scientific Rigor:**
- Pre-registered decision gates
- Three outcome scenarios (A/B/C) pre-declared valid
- Cross-project consistency (P1/P3/P5 references)
- No barren plateau at n=800 documented
- Marginal plateau at n=8K flagged
- Scaffold generalization gap quantified

### ⚠️ Current Gaps

**Provenance:**
- Analysis ledger 6 weeks outdated (being fixed NOW)
- No LED-XXX citations in manuscript text
- Abstract not written (blocked on ledger)

**Bibliography:**
- Only ~12 entries, need 20+
- Several [PLACEHOLDER] entries
- Missing key QML references

**Review:**
- No L3 review passes executed yet
- No audit checklist run
- No cover letter written

---

## Success Criteria (Option A)

### Must-Have (Blocking Submission):

✅ Analysis ledger complete (LED-003 to LED-017) — IN PROGRESS  
⬜ Every manuscript number has LED-XXX citation  
⬜ Abstract written (200 words, Scenario B)  
⬜ Bibliography complete (20+ entries, no placeholders)  
⬜ LaTeX compiles cleanly (0 errors)  
⬜ All 5 figures included and rendering  
⬜ Cover letter written (1 page)  

### Should-Have (Quality Gates):

⬜ Anti-AI scan: 0 banned patterns  
⬜ L3 review: CRITICAL findings = 0, HIGH ≤ 3  
⬜ L4 audit: All rows PASS with evidence  
⬜ Supplementary information file generated  
⬜ Manuscript read-through by author  

### Nice-to-Have (Enhancement):

⬜ Graphical abstract (TOC graphic)  
⬜ Video abstract (optional for journal)  
⬜ Data repository DOI (Zenodo/Figshare)  
⬜ Code repository link (GitHub/GitLab)  

---

## File Locations

**Manuscript:**
- Main: `/home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/manuscript/main.tex`
- PDF: `manuscript/main.pdf` (17 pages, 800KB)
- Sections: `manuscript/sections/*.tex`
- Figures: `manuscript/figures/*.pdf` (5 files, all present)

**Data & Results:**
- DAR: `P7_DATA_ANALYSIS_REPORT.md` (canonical source of truth)
- Results: `results/phase{1..4}_*/*.{json,csv}` (12+ files)
- Ledger: `manuscript/outputs/analysis/analysis-ledger.md` (being rebuilt)

**Tracking:**
- Project spine: `manuscript/project-tracking.md`
- Urgent plan: `URGENT_LEDGER_RECONSTRUCTION_PLAN.md`
- This report: `P7_WORKFLOW_STATUS_20261014.md`
- Summary: `P7_MANUSCRIPT_REFINEMENT_SUMMARY.md`

**Workflow Outputs (Pending):**
- Investigation: `manuscript/outputs/critical-reviews/calculation-review-20261014.md`
- Verification: `manuscript/outputs/analysis/ledger-rebuild-verification.md`

---

## Next Action

**Immediate:** Wait for both workflows to complete (~15-30 minutes)

**Then:** Review outputs and make final decision (Option A recommended)

**After Decision:** Launch manuscript finalization workflow (citations + abstract + bibliography)

---

**Status:** 🟡 WORKFLOWS RUNNING  
**Timeline:** Option A = 2-3 days | Option B = 2-3 weeks  
**Recommendation:** Option A (ECFP4-VQC, complete data, honest-negative)  
**Blocker:** Analysis ledger rebuild (resolving NOW)

**Last Updated:** 14 October 2026, active session

