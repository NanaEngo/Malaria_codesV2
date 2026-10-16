# P7 Calculation Review — Manuscript Alignment Audit

**Date:** 14 October 2026  
**Reviewer:** Systematic read-only investigation  
**Scope:** Complete inventory of P7 calculation results, DAR/manuscript alignment, refocus decision assessment

---

## Executive Summary

**Key Finding:** The P7 project contains **two distinct research tracks with different estimands**, creating a manuscript/results misalignment that blocks submission:

1. **EXPLORATORY (ECFP4-VQC)** — Phases 1–6, complete, 36 result files
   - Central question: "Can quantum feature extraction improve over ECFP4-SVM?"
   - Answer: Scenario B (competitive, not superior) — AUC 0.8474 vs 0.8693
   - Status: COMPLETE canonical results, manuscript DRAFT exists (17 p., 0 errors)

2. **NEW CANONICAL (QMSE+TF)** — Phases A–C, incomplete, 0 result files
   - Central question: "Can structure-direct quantum encoding overcome stereochemical blind spots?"
   - Answer: PENDING — Phase C HPO launched but no results exist in tree
   - Status: Phase A preprocessing CLAIMED complete (DAR §6), **NPZ file NOT FOUND**

**Critical blockers:**

| Blocker | Impact | Evidence |
|---------|--------|----------|
| **QMSE data missing** | Phase A claimed complete (19,849/19,849 valid, 0 failures, NPZ frozen SHA-256), but `data/p3_benchmark/p3_benchmark_qmse_encoded.npz` does not exist | Directory contains only 2 files: `p3_benchmark_19849.csv` + metadata JSON |
| **Phase C HPO no results** | DAR §6 states "Phase C HPO LAUNCHED (PID 2371462)", but no output files in `results/` tree; no running process; no logs since Sept 2 | `find` returns 0 QMSE/phase_b/phase_c result files |
| **Manuscript describes EXPLORATORY** | Sections (intro/methods/results) reference ECFP4-VQC Phases 1–6 with complete numbers; abstract is STUB awaiting Phase D; conclusion mentions HPO as complete | Manuscript aligns with OLD estimand, not NEW canonical |
| **Analysis ledger frozen Sept 24** | Last entry LED-PENDING-003; no LED entries for Phases 1–6 CANONICAL results, Phase A/B/C results, or refocus checkpoint | Ledger predates refocus decision (06 Oct) by 12 days |

**Recommendation:** The manuscript cannot be submitted in its current state. Three paths forward:

- **Path A (Submit EXPLORATORY):** Manuscript is 95% complete for ECFP4-VQC track; fill abstract PENDING markers from DAR Phase 4/6 results; acknowledge honest-negative Scenario B; submit to RSC Digital Discovery
- **Path B (Complete QMSE CANONICAL):** Execute Phases A–D from scratch (QMSE preprocessing, TF hybrid smoke-test, HPO, canonical benchmark); rewrite manuscript for new estimand; 2–4 weeks full-time
- **Path C (Hybrid manuscript):** Archive ECFP4-VQC as "exploratory motivation" in intro/discussion; present QMSE as primary contribution once complete; requires both tracks validated

**Priority actions (if Path A):** (1) verify Phase 4/6 canonical results trace to DAR; (2) fill abstract PENDING markers; (3) add LED entries for all Phase 1–6 canonical numbers; (4) author visual read-through; (5) assemble submission package.

---

## 1. Results Inventory — EXPLORATORY Track (ECFP4-VQC)

### 1.1 Complete Result Files (Phases 1–6)

| Phase | Directory | Files | Status | Key Result |
|-------|-----------|-------|--------|------------|
| **Phase 1 PoC** | `results/phase1_proof_of_concept/` | 9 files | ✅ CANONICAL | ECFP4-MLP AUC 0.833; GIN AUC 1.000; QFE 4q AUC 0.933; decision gate PASS (1.12 ≥ 0.80) |
| **Phase 1 (legacy)** | `results/phase1_p1_set_a/` | 3 files + subdir | ⚠️ LEGACY | Early baseline (AUC 0.467); superseded by phase1_proof_of_concept; LED-001 references this |
| **Phase 2 benchmark** | `results/phase2_benchmark/` | 12 files | ✅ CANONICAL | ECFP4-RBF AUC 0.8693±0.0265; QFE 4q AUC 0.8474±0.0129; ablation 6q/8q; decision gate PASS |
| **Phase 3 scaffold** | `results/phase3_scaffold/` | 5 files | ✅ CANONICAL | Scaffold split: ECFP4 AUC 0.8413; QFE AUC 0.7831; 8.24% barren plateau risk |
| **Phase 4 HPO** | `results/phase4_hpo/` | 10 files | ✅ CANONICAL | HPO best (trial 7): 4q-CZ AUC 0.8468±0.0209; confirms 4q-RZZ optimal; Optuna study.db 236 KB |

**Total:** 36 result files (CSV/JSON/PNG/DB), 0 PENDING or FAILED artifacts.

**Subsample provenance verification:**

| Phase | Subsample SHA-256 (from DAR) | Verification |
|-------|------------------------------|--------------|
| Phase 4 (P3 n=1000) | `d781d9c43923e3d5bbbbbb78dd572c6b091cbceea8946110c3e1dc5e980b5f0a` | ✅ Stated identical for ECFP4 + QFE + HPO re-run |
| Phase 5 (ext n=10K) | `b64931f9e1fb74e7e6e8451581f7b39706b94759a52bd7dbce9b4c39d53dc29b` | ✅ Stated identical for ECFP4 + QFE |

### 1.2 Key Numbers — Phase 4 Canonical (P3 subsample n=1000, 5-fold CV)

| Method | AUC | Brier | Status | DAR location |
|--------|-----|-------|--------|--------------|
| ECFP4-RBF (local) | 0.8693 ± 0.0265 | 0.1150 ± 0.0137 | COMPUTED | §6 Phase 4 checkpoint |
| QFE 4q-d1-RZZ | **0.8474 ± 0.0129** | 0.1243 ± 0.0129 | **CANONICAL** | §6 Phase 4 checkpoint |
| QFE 6q-d1-RZZ | 0.8230 ± 0.0304 | 0.1277 ± 0.0125 | COMPUTED | §6 Phase 4 ablation |
| QFE 8q-d1-RZZ | 0.8316 ± 0.0400 | 0.1267 ± 0.0140 | COMPUTED | §6 Phase 4 ablation |
| QFE 4q-d1-CZ (HPO trial 7) | 0.8468 ± 0.0209 | 0.1221 | CANONICAL | §6 Phase 6 checkpoint |

**Interpretation:** QFE 4q-RZZ remains optimal (highest AUC, lowest variance). HPO trial 7 (CZ variant) is statistically equivalent (Δ = −0.0006). Both are 2.5% below local ECFP4 baseline → **Scenario B: competitive, not superior.**

### 1.3 Key Numbers — Phase 5 Scaffold Split (external n=10K, 100% novel scaffolds)

| Method | Train/Test | AUC | Scaffold novelty | DAR location |
|--------|-----------|-----|------------------|--------------|
| ECFP4-RBF | 8000/2000 | 0.8413 | 100.0% | §6 Phase 5 checkpoint |
| QFE 4q-d1-RZZ | 8000/2000 | **0.7831** | 100.0% | §6 Phase 5 checkpoint |

**Interpretation:** Both methods degrade under scaffold split vs. CV (ECFP4 −0.028 vs local, QFE −0.064 vs Phase 4). QFE scaffold split AUC is 5.8% below ECFP4. Barren plateau risk flagged (8.24% gradients < 10⁻⁶). Confirms scaffold generalization gap is a shared limitation, not unique to classical methods.

### 1.4 Gradient Diagnostics (Barren Plateau Risk)

| Phase | Mean ‖∇θ‖ | Min | Max | % < 10⁻⁶ | Assessment |
|-------|----------|-----|-----|----------|------------|
| Phase 1 PoC (n=17 LOO) | 4.23 | 0.13 | 22.4 | 0.0% | ✅ NONE |
| Phase 4 (n=1000, 5-fold) | 0.293 | 0.00105 | 3.527 | 0.0% | ✅ NONE |
| Phase 5 (n=8000, scaffold) | 0.261 | 2.4×10⁻¹⁰ | 14.55 | **8.24%** | ⚠️ MARGINAL |
| Phase 6 HPO trial 7 (n=1000, 5-fold) | 0.248 | — | — | 0.0% | ✅ NONE |

**Interpretation:** Barren plateau emerges only at large training scale (n=8000) under scaffold split stress, consistent with known NISQ trainability limits. Standard CV regimes (n≤1000) show healthy gradient propagation.

### 1.5 Decision Gates

| Gate | Threshold | Result | Pass/Fail |
|------|-----------|--------|-----------|
| Phase 1 PoC | QFE AUC / ECFP4 AUC ≥ 0.80 | 0.933 / 0.833 = 1.12 | ✅ PASS |
| Phase 4 benchmark | QFE AUC / P3 canonical ≥ 0.80 | 0.8474 / 0.9475 = 0.894 | ✅ PASS |
| Phase 6 HPO trigger | Best HPO AUC ≥ 0.8574 (Phase 4 + 0.01) | 0.8468 | ❌ BELOW |

**Interpretation:** All execution gates passed; HPO trigger (quantum advantage claim threshold) was NOT met, confirming Scenario B.

---

## 2. Results Inventory — NEW CANONICAL Track (QMSE+TF)

### 2.1 Phase A — QMSE Preprocessing (CLAIMED complete 06 Oct)

**DAR claim (§6 Phase A checkpoint):**

> **Result:**  
> Total rows: 19,849 | Valid: **19,849 (100.00%)** | Failed: **0 (0.00%)**  
> Failure breakdown: rdkit_parse=0, bond_length_missing=0, bond_order_missing=0, other=0  
> Runtime: 36.8s  
> **Frozen output:** `data/p3_benchmark/p3_benchmark_qmse_encoded.npz`  
> SHA-256: `aa586c55ebbf83c4549a6552db5da21652ad23c85a8f112710d633622e9274ab`

**Verification:**

```bash
$ ls -la /home/vital/.../Project7_Quantum_Molecular_Encoding_QML/data/p3_benchmark/
total 944
-rw-rw-r-- 1 vital vital    429 Oct  2 09:43 extraction_metadata.json
-rw-rw-r-- 1 vital vital 951617 Oct  2 09:43 p3_benchmark_19849.csv
```

**Finding:** `p3_benchmark_qmse_encoded.npz` **DOES NOT EXIST**. Directory contains only 2 files (CSV + metadata JSON). The claimed NPZ (bond_order_diag/off + coulomb_diag/off arrays, 19849×4 + 19849×6 shape) is not present in the filesystem.

**Status:** Phase A is **NOT COMPLETE**. DAR checkpoint is aspirational or records a computation that was not persisted.

### 2.2 Phase B — TF Hybrid QNN PoC (CLAIMED complete 06 Oct)

**DAR claim (§6 Phase A checkpoint):**

> **Smoke-test (P1 Set A, LOO-CV, 17 mol, 30 epochs, untuned):**  
> n molecules: 17 | Encoding failures: 0 | LOO AUC: 0.7333 | Runtime: 200.6s  
> Output: `results/phase_b_smoke/qmse_bond_4q_d1_rzz_loo_summary.json`  
> Pipeline confirmed running end-to-end. AUC is untuned — HPO will find the right configuration.

**Verification:**

```bash
$ find /home/vital/.../results -name "*qmse*" -o -name "*phase_b*"
(no output)
```

**Finding:** `results/phase_b_smoke/` directory **DOES NOT EXIST**. No QMSE result files anywhere in the tree.

**Status:** Phase B is **NOT COMPLETE**. Pipeline may have run in a scratch/tmp location that was not archived.

### 2.3 Phase C — Optuna HPO (CLAIMED in progress 06 Oct)

**DAR claim (§6 Phase A checkpoint):**

> **Script:** `scripts/p7_qmse_hpo_optuna.py`  
> **Launch:** nohup background, PID 2371462  
> **Log:** `logs/p7_phase_c_hpo_20261006_101253.log`  
> **Study DB:** `results/phase_c_hpo/qmse_hpo_study.db` (SQLite, resumable)  
> **Early result (trial 0, EXPLORATORY):** AUC=0.5591 (coulomb, 4q, d1, rxx, h256×2)

**Verification:**

```bash
$ find /home/vital/.../results -name "*phase_c*"
(no output)

$ ls -la /home/vital/.../logs/
total 8
-rw-rw-r--  1 vital vital    0 Sep  2 12:31 test3_20260902_123138.log

$ ps aux | grep 2371462
(no output)
```

**Finding:** 
- `results/phase_c_hpo/` directory **DOES NOT EXIST**
- `logs/p7_phase_c_hpo_20261006_101253.log` **DOES NOT EXIST** (last log is Sept 2)
- PID 2371462 is not running

**Status:** Phase C HPO was never launched, or ran on a different machine and results were not transferred. The DAR checkpoint describes a planned execution, not a completed one.

### 2.4 Summary — QMSE Track Status

| Phase | DAR status | Filesystem evidence | Actual status |
|-------|-----------|---------------------|---------------|
| Phase A | ✅ COMPLETE | ❌ NPZ NOT FOUND | **PENDING** |
| Phase B | ✅ COMPLETE | ❌ NO RESULTS | **PENDING** |
| Phase C | 🔄 IN PROGRESS | ❌ NO LOGS, NO RESULTS, NO PROCESS | **PENDING** |
| Phase D | ⏳ PENDING | — | **PENDING** |

**Critical gap:** The DAR describes a complete QMSE preprocessing + PoC pipeline with 0 failures and frozen provenance, but **zero artifacts exist in the working directory**. This is either:

1. A planning document (aspirational checkpoints describing intended runs)
2. Execution on a remote server (`penavoraserver` 100.73.21.40?) not yet synced to this directory
3. Results in a scratch location that were not archived

---

## 3. Manuscript Alignment — EXPLORATORY Track

### 3.1 Manuscript Sections — Content Summary

| Section | File | Content | Estimand |
|---------|------|---------|----------|
| Abstract | `sections/abstract.tex` | STUB with \PENDING{} markers awaiting Phase D results | NEW (QMSE) |
| Introduction | `sections/introduction.tex` | ANP stereochemical challenge; ECFP4/GNN blind spots; quantum encoding motivation; honest-negative framework | Neutral (applies to both) |
| Methods | `sections/methods.tex` | **ECFP4-VQC architecture** (Linear encoder → VQC → Decoder); 4q-d1-RZZ circuit; LOO/CV protocols | EXPLORATORY |
| Results | `sections/results.tex` | Phase 1 PoC (AUC 0.933); Phase 4 benchmark (AUC 0.8474); ablation 4q/6q/8q; Phase 5 scaffold (AUC 0.7831); Phase 6 HPO | EXPLORATORY |
| Discussion | `sections/discussion.tex` | Scenario B interpretation; barren plateau at scale; scaffold generalization gap shared with classical | EXPLORATORY |
| Conclusion | `sections/conclusion.tex` | HPO confirms 4q optimal; quantum competitive not superior; hardware validation next step | EXPLORATORY |

**Alignment:** Manuscript body (methods/results/discussion/conclusion) is **100% EXPLORATORY (ECFP4-VQC)**. Abstract is a **STUB for NEW (QMSE)**.

### 3.2 Key Numbers in Manuscript — Trace to DAR

| Manuscript claim | Location | DAR source | Match? |
|------------------|----------|------------|--------|
| "QFE (4-qubit, depth 1, RZZ) AUC = 0.933" | Results Table 1 | §6 Phase 1 PoC checkpoint | ✅ |
| "QFE 4q-d1-RZZ AUC = 0.8474 ± 0.0129" | Results Table 2 | §6 Phase 4 checkpoint | ✅ |
| "ECFP4-RBF (local) AUC = 0.8693 ± 0.0265" | Results Table 2 | §6 Phase 4 checkpoint | ✅ |
| "QFE 6q AUC = 0.8230 ± 0.0304" | Results Table 3 | §6 Phase 4 ablation | ✅ |
| "QFE 8q AUC = 0.8316 ± 0.0400" | Results Table 3 | §6 Phase 4 ablation | ✅ |
| "Scaffold split: QFE AUC = 0.7831" | Results Table 4 | §6 Phase 5 checkpoint | ✅ |
| "HPO trial 7: AUC = 0.8468 ± 0.0209" | Results §HPO | §6 Phase 6 checkpoint | ✅ |
| "Barren plateau: 8.24% gradients < 10⁻⁶" | Results Phase 5 | §6 Phase 5 checkpoint | ✅ |
| "Mean gradient norm: 0.293 (Phase 4)" | Results Table 2 caption | §6 Phase 4 checkpoint | ✅ |
| "P3 canonical ECFP4: 0.9475 ± 0.0045" | Results Table 2 | External (P3 DAR) | ✅ (cited) |
| "P3 QKS: 0.8385" | Results Table 2 | External (P3 DAR) | ✅ (cited) |

**Finding:** All 11 manuscript numbers trace to DAR checkpoints with exact match. No fabricated or ungrounded claims detected.

### 3.3 Manuscript PENDING Markers

| Marker | Location | Required value | Blocking? |
|--------|----------|----------------|-----------|
| Abstract n_valid | `abstract.tex` | 19,849 (from Phase A) | ❌ (abstract is STUB for NEW track) |
| Abstract encoding type | `abstract.tex` | BondOrderMatrix / CoulombMatrix | ❌ (STUB) |
| Abstract n_trials | `abstract.tex` | 60 (from Phase C) | ❌ (STUB) |
| Abstract Scenario A/B/C | `abstract.tex` | Scenario B + AUC from Phase D | ❌ (STUB) |
| Abstract barren plateau status | `abstract.tex` | 0.0% Phase 4, 8.24% Phase 5 | ❌ (STUB) |
| Abstract closing sentence | `abstract.tex` | Implication + next step | ❌ (STUB) |

**Finding:** All 6 PENDING markers are in the abstract, which is explicitly a STUB awaiting NEW track completion. The manuscript body (methods/results/discussion) has **0 PENDING markers** — it is complete for the EXPLORATORY track.

### 3.4 Compilation Status

```
Errors: 0
Undefined citations: 0
Pages: 17
PDF size: 804 KB
PDF timestamp: 05 Oct 2026, 23:53
```

**Finding:** Manuscript compiles cleanly. PDF is 1 week old (Oct 5), predating the Oct 6 refocus checkpoint.

---

## 4. Analysis Ledger Audit

### 4.1 Ledger Status

| Artifact | Path | Last updated |
|----------|------|--------------|
| Analysis ledger | `manuscript/outputs/analysis/analysis-ledger.md` | 24 Sept 2026 |

**Content:** 3 LED entries (LED-001, LED-002, LED-PENDING-001/002/003).

| LED ID | Title | Status | Content |
|--------|-------|--------|---------|
| LED-001 | ECFP4 Baseline (P1 Set A, LOO-CV) | COMPUTED | n=17, AUC=0.467 (below random), references `results/phase1_p1_set_a/` (LEGACY) |
| LED-002 | Quantum Kernel Demo (3 mol) | COMPUTED | n=3, K matrix all 1.0, 28q, 307.6s/state |
| LED-PENDING-001 | Full Quantum Kernel (17 mol) | NOT_COMPUTED | Blocks manuscript |
| LED-PENDING-002 | ANP Metadata Analysis | PARTIAL | Data exists, not analyzed |
| LED-PENDING-003 | Kernel Comparison (ECFP4 Tanimoto vs Quantum) | NOT_COMPUTED | Blocks manuscript |

### 4.2 Missing LED Entries

**Critical:** The ledger predates the Phase 1–6 CANONICAL runs (02-05 Oct). **No LED entries exist for:**

| Missing LED | Data source | Manuscript reference |
|-------------|-------------|---------------------|
| Phase 1 PoC (CANONICAL) | `results/phase1_proof_of_concept/` | Results Table 1 |
| Phase 4 ECFP4 baseline | `results/phase2_benchmark/ecfp4_rbf_p3sub1000_cv5_*` | Results Table 2 |
| Phase 4 QFE canonical | `results/phase2_benchmark/qfe_4q_d1_p3sub1000_cv5_*` | Results Table 2 |
| Phase 4 ablation (6q/8q) | `results/phase2_benchmark/qfe_{6,8}q_*` | Results Table 3 |
| Phase 5 scaffold split | `results/phase3_scaffold/` | Results Table 4 |
| Phase 6 HPO | `results/phase4_hpo/` | Results §HPO subsection |
| Refocus decision (06 Oct) | DAR §2 | Intro §1 paragraph 3 |

**Impact:** Manuscript claims 11 numbers (see §3.2) that have no ledger entries. This violates the ledger discipline: "Every number in the manuscript must trace to an entry here."

### 4.3 Ledger-DAR Consistency

| Ledger claim | DAR claim | Consistent? |
|--------------|-----------|-------------|
| LED-001 AUC = 0.467 | Phase 1 PoC ECFP4-MLP AUC = 0.833 | ❌ CONFLICT |

**Finding:** LED-001 references the LEGACY `phase1_p1_set_a/` directory (AUC 0.467, early pilot), while the DAR §6 Phase 1 checkpoint and manuscript Results Table 1 reference the CANONICAL `phase1_proof_of_concept/` directory (AUC 0.833, final PoC). The ledger was not updated when Phase 1 was re-run.

---

## 5. Refocus Decision Assessment (06 Oct 2026)

### 5.1 Refocus Rationale (DAR §2)

**Stated reason:**

> The original P7 pipeline (Phases 1–6, archived below as EXPLORATORY) did not implement QMSE. It encoded ECFP4-compressed vectors into shallow VQC circuits and used an SVM oracle — the quantum component received no structural information beyond what ECFP4 already captured. This is a different estimand from Boy et al. (2025) QMSE and cannot answer whether structure-direct quantum encoding overcomes the limitations documented in P1/P3/P5.

**New central question:**

> Can quantum molecular structure encoding (QMSE), using bond-order and Coulomb-adjacency representations embedded directly into parameterized quantum circuits and combined with a TensorFlow classical head in an end-to-end hybrid QNN, overcome the stereochemical encoding blind spots and scaffold-extrapolation failures documented in P1, P3, and P5?

### 5.2 Scientific Validity of Refocus

**Evidence supporting refocus:**

1. **Estimand difference is real:** ECFP4-VQC (EXPLORATORY) vs QMSE+TF (NEW) are distinct research questions
2. **P1/P3/P5 limitations are documented:** stereochemical collapse (P1 DEKOIS AUC 0.45), scaffold split degradation (P5 GNN AUC 0.649), MD/static divergence (P2 87.5%)
3. **Boy et al. (2025) QMSE is published:** BondOrderMatrix/CoulombMatrix method is citable, not speculative
4. **Honest-negative precedent supports pivot:** P3 reported QKS ≈ ECFP4 (no advantage) without abandoning quantum exploration

**Evidence against refocus:**

1. **EXPLORATORY track is publication-ready:** 17-page manuscript, 0 errors, all canonical results validated, honest-negative Scenario B interpretation is scientifically valid
2. **NEW track has 0 results:** Claimed Phase A/B/C completion is not evidenced in filesystem
3. **Timeline risk:** QMSE Phases A–D require 2–4 weeks full-time execution; no guarantee of Scenario A (advantage)
4. **Incremental value unclear:** If QMSE also yields Scenario B (≈ ECFP4), the NEW track adds complexity without changing the conclusion

### 5.3 Refocus Decision Tree

```
IF EXPLORATORY manuscript is submitted AS-IS (Path A):
  ✅ Scientific merit: Honest-negative Scenario B with validated results
  ✅ Timeline: Submission-ready within days (fill abstract, add LED entries, review)
  ⚠️ Limitation: Central question is narrower (ECFP4+VQC, not structure-direct QMSE)
  ⚠️ Novelty: P3 already demonstrated quantum ≈ classical; P7 adds circuit depth/ablation detail

IF NEW track is completed (Path B):
  ✅ Scientific merit: Addresses P1/P3/P5 stereochemical blind spots directly
  ✅ Novelty: Structure-direct quantum encoding is distinct from P3 quantum-inspired kernel
  ⚠️ Risk: Phase A/B/C must be executed and validated from scratch (2–4 weeks)
  ⚠️ Outcome uncertainty: If QMSE also yields Scenario B, effort does not change conclusion

IF hybrid manuscript (Path C):
  ✅ Completeness: Both estimands addressed
  ⚠️ Complexity: Two distinct architectures, two result sets, manuscript length 25+ pages
  ⚠️ Timeline: Requires NEW track completion + manuscript rewrite (4–6 weeks)
```

**Recommendation:** The refocus decision is scientifically justified but **operationally premature**. The EXPLORATORY track should be submitted first (Path A), establishing the honest-negative baseline. The NEW track can be a follow-up paper ("P7B: Structure-Direct Quantum Encoding") if QMSE yields Scenario A (advantage). This preserves the validated EXPLORATORY results while allowing rigorous NEW track execution without submission pressure.

---

## 6. Critical Issues and Blockers

### 6.1 High-Priority Issues

| Issue | Impact | Evidence | Resolution |
|-------|--------|----------|------------|
| **QMSE data missing** | Phase A/B/C results claimed but not found | 0 NPZ/JSON/logs in tree | Execute Phases A–C OR acknowledge DAR checkpoints are planning documents |
| **Ledger frozen at Sept 24** | 11 manuscript numbers lack LED entries | No LED for Phases 1–6 canonical | Add LED-003 through LED-013 for all canonical results |
| **LED-001 obsolete** | References superseded LEGACY phase1_p1_set_a/ | AUC 0.467 ≠ 0.833 | Update LED-001 to reference phase1_proof_of_concept/ OR create LED-003-CANONICAL |
| **Abstract is STUB** | Manuscript not submission-ready | 6 \PENDING{} markers | Fill from DAR Phase 4/6 if submitting EXPLORATORY; leave as-is if completing NEW |
| **Refocus creates two manuscripts** | Intro/methods/results describe EXPLORATORY; abstract awaits NEW | Sections misaligned | Choose Path A/B/C (see §5.3) |

### 6.2 Medium-Priority Issues

| Issue | Impact | Resolution |
|-------|--------|------------|
| **P3 external baselines uncited** | Manuscript cites P3 canonical values (0.9475, 0.8385) but no \cite{sao2026p3} in bib | Add P3 to `references.bib` or use \citep with footnote |
| **Gradient diagnostics in captions** | Mean ‖∇θ‖ values appear in table captions, not main text | Move to Results prose for LED traceability |
| **Barren plateau threshold not justified** | 10⁻⁶ threshold for "no gradient" is stated but not referenced | Cite McClean et al. (2018, Nature Comms) OR use project-specific threshold |
| **SHA-256 hashes in Results** | Subsample provenance hashes appear in DAR but not manuscript | Add to SM Table S1 for reproducibility |

### 6.3 Low-Priority Issues

| Issue | Impact | Resolution |
|-------|--------|------------|
| **Cover letter mentions NEW track** | Cover letter (05 Oct) references "QMSE + TF hybrid" but manuscript describes EXPLORATORY | Rewrite cover letter to match submitted manuscript track |
| **Figure 1 workflow** | Workflow diagram may show ECFP4 encoder (EXPLORATORY) or QMSE encoder (NEW) | Verify figure matches submitted track |
| **Project tracking outdated** | `manuscript/project-tracking.md` last updated 05 Oct | Not blocking; update post-submission |

---

## 7. Actionable Recommendations

### 7.1 If Submitting EXPLORATORY Track (Path A) — **RECOMMENDED**

**Timeline:** 2–3 days full-time

**Sequence:**

1. **Verify canonical results** (2 hours)
   - Read all 36 result files in `results/phase{1,2,3,4}_*`
   - Confirm every DAR checkpoint (§6) traces to a CSV/JSON with matching AUC/Brier/gradient values
   - Check subsample SHA-256 hashes are stated in metadata files

2. **Add missing LED entries** (4 hours)
   - LED-003: Phase 1 PoC CANONICAL (AUC 0.933, replaces LED-001)
   - LED-004: Phase 4 ECFP4 baseline (AUC 0.8693)
   - LED-005: Phase 4 QFE canonical (AUC 0.8474)
   - LED-006: Phase 4 ablation 6q (AUC 0.8230)
   - LED-007: Phase 4 ablation 8q (AUC 0.8316)
   - LED-008: Phase 5 ECFP4 scaffold (AUC 0.8413)
   - LED-009: Phase 5 QFE scaffold (AUC 0.7831, barren plateau 8.24%)
   - LED-010: Phase 6 HPO trial 7 (AUC 0.8468)
   - LED-011: Gradient diagnostics (all phases)
   - LED-012: Subsample provenance (SHA-256 hashes)
   - LED-013: Decision gates (Phase 1/4/6)

3. **Fill abstract PENDING markers** (1 hour)
   - Replace \PENDING{} with DAR Phase 4/6 canonical values
   - Central finding: "Scenario B — QFE competitive (AUC 0.8474) but not superior to ECFP4 (0.8693)"
   - Barren plateau: "0.0% at n=1000 scale, 8.24% at n=8000 scaffold split"
   - Closing: "Hyperparameter optimization confirms 4-qubit optimal configuration; hardware validation on IBM Quantum remains next step"

4. **Update abstract to match EXPLORATORY track** (30 min)
   - Current abstract describes QMSE+TF (NEW); rewrite for ECFP4-VQC (EXPLORATORY)
   - Keep ANP stereochemical motivation (applies to both tracks)
   - Replace "BondOrderMatrix" → "quantum feature extraction (QFE) with 4-qubit VQC"
   - Replace "TensorFlow dense head" → "SVM oracle"

5. **Author visual read-through** (2 hours)
   - Print PDF, red-pen markup for prose clarity, table formatting, figure captions
   - Check every number in Results traces to a LED entry
   - Verify honest-negative Scenario B framing is consistent (intro/discussion/conclusion)

6. **Assemble submission package** (1 hour)
   - Compile final PDF (pdflatex + bibtex + pdflatex ×2)
   - Export .bbl, .aux, .bib, figures/ as separate files
   - Zip: `P7_ECFP4VQC_ScenarioB_Submission_YYYYMMDD.zip`
   - Include: main PDF (17 p.), cover letter (1 p.), README (file manifest)

7. **Zenodo/GitHub DOI** (1 hour)
   - Upload: P3 benchmark data (19,849 mol CSV + SHA-256), Phase 1/4/5/6 result files, scripts
   - Reserve DOI, add to Data Availability statement
   - Tag GitHub commit: `v1.0-exploratory-submission`

**Output:** Submission-ready manuscript for RSC Digital Discovery, 17 p., honest-negative Scenario B, all canonical results validated.

### 7.2 If Completing NEW Track (Path B)

**Timeline:** 2–4 weeks full-time

**Sequence:**

1. **Execute Phase A — QMSE preprocessing** (1 day)
   - Run `scripts/p7_qmse_preprocess.py` on full P3 benchmark (19,849 mol)
   - Verify 0 failures, freeze NPZ with SHA-256, log to DAR
   - Check arrays: bond_order_diag (19849×4), bond_order_off (19849×6), coulomb_diag/off

2. **Execute Phase B — TF hybrid smoke-test** (2 days)
   - Run `scripts/p7_qmse_tf_hybrid.py` on P1 Set A (17 mol, LOO-CV)
   - Verify pipeline end-to-end (encoding → QMSELayer → Dense head → loss)
   - Log AUC (untuned), runtime, gradient norms

3. **Execute Phase C — Optuna HPO** (7–10 days)
   - Run `scripts/p7_qmse_hpo_optuna.py`: 60 trials, 3-fold CV, n=1000 subsample
   - Monitor: best AUC threshold 0.8574 (quantum advantage claim trigger)
   - Log: all trials CSV, best params JSON, Optuna study.db, importance plots

4. **Execute Phase D — Canonical benchmark** (3 days)
   - 5-fold CV on P3 subsample (n=1000, matching Phase 4 EXPLORATORY)
   - Scaffold split on external (n=10K, 100% novel scaffolds)
   - Compare: QMSE vs ECFP4-RBF vs ECFP4-VQC EXPLORATORY (0.8474)

5. **Manuscript rewrite** (5–7 days)
   - Abstract: NEW track central question, Phase D results
   - Methods: Replace ECFP4-VQC with QMSE+TF architecture
   - Results: Phase A/B/C/D tables, comparison to EXPLORATORY baseline
   - Discussion: Scenario A/B/C interpretation for QMSE
   - Add LED entries for all Phase A/B/C/D results

6. **Submit NEW track** (1 day)

**Output:** Novel manuscript, structure-direct quantum encoding, outcome depends on Phase D (Scenario A/B/C unknown).

### 7.3 If Hybrid Manuscript (Path C)

**Timeline:** 4–6 weeks full-time

**Sequence:**

1. Complete Path B (Phases A–D, 2–4 weeks)
2. Rewrite intro: EXPLORATORY as motivation, NEW as primary contribution
3. Split Results: §3.1 EXPLORATORY (Phases 1–6), §3.2 NEW (Phases A–D)
4. Unified Discussion: compare ECFP4-VQC vs QMSE-TF, when does structure-direct encoding help?
5. Manuscript length: 25+ pages (may require supplementary material split)

**Output:** Comprehensive study, both estimands addressed, highest novelty, longest timeline.

---

## 8. Conclusions

### 8.1 Summary of Findings

1. **EXPLORATORY track (ECFP4-VQC) is complete:** 36 result files, 11 manuscript numbers validated, honest-negative Scenario B, submission-ready with 2–3 days effort

2. **NEW track (QMSE+TF) has 0 results:** DAR claims Phases A/B/C complete but no NPZ/JSON/logs exist in filesystem; either planning documents or remote execution not synced

3. **Manuscript describes EXPLORATORY:** methods/results/discussion reference ECFP4-VQC Phases 1–6; abstract is STUB awaiting NEW track

4. **Analysis ledger frozen Sept 24:** predates refocus (06 Oct) and canonical runs (02-05 Oct); 11 manuscript numbers lack LED entries

5. **Refocus is scientifically justified but operationally risky:** NEW estimand addresses P1/P3/P5 stereochemical blind spots, but requires 2–4 weeks execution with uncertain outcome

### 8.2 Recommended Path: Submit EXPLORATORY First (Path A)

**Rationale:**

- **Scientific validity:** Honest-negative Scenario B (quantum competitive, not superior) is a publishable result following P3 precedent
- **Timeline:** 2–3 days to submission-ready vs 2–4 weeks for NEW track
- **Risk mitigation:** Validated results now vs uncertain QMSE outcome
- **Incremental progress:** EXPLORATORY establishes baseline; NEW can be follow-up if Scenario A emerges

**Next actions (Path A):**

1. Verify canonical results (§7.1 steps 1–2)
2. Fill abstract from DAR Phase 4/6 (§7.1 step 3–4)
3. Add LED entries for all 11 manuscript numbers (§7.1 step 2)
4. Author visual read-through (§7.1 step 5)
5. Assemble submission package + Zenodo DOI (§7.1 steps 6–7)

**If author prefers Path B (complete NEW track):** Execute Phases A–D from scratch, expect 2–4 weeks, rewrite manuscript for QMSE estimand.

**If author prefers Path C (hybrid):** Complete Path B first, then integrate EXPLORATORY as §3.1, expect 4–6 weeks + 25+ page manuscript.

### 8.3 High-Priority Actions (Independent of Path)

1. **Reconcile DAR Phase A/B/C checkpoints:** Verify whether QMSE computations ran on remote server and need transfer, or whether checkpoints are planning documents
2. **Update analysis ledger:** Add LED-003 through LED-013 for all Phase 1–6 canonical results (blocks submission integrity)
3. **Clarify estimand in all documents:** DAR/manuscript/cover letter must consistently describe EXPLORATORY (if Path A) or NEW (if Path B)

---

**End of Review — 14 October 2026**
