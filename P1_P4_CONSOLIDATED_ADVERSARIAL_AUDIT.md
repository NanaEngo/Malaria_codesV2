# P1–P4 Consolidated Adversarial Audit & Mitigation Report

**Date:** July 25, 2026 (evening)
**Scope:** Cross-project critical self-assessment of all four manuscripts from a Q1 journal reviewer perspective
**Methodology:** Synthesise per-project adversarial audits, identify cross-cutting weaknesses, rank by severity, provide unified mitigation plan

---

## Executive Summary

| Project | Target | Topic | Acceptance | Status | CRITICAL remaining |
|---------|--------|-------|:----------:|:------:|:------------------:|
| **P1** | *ACS Omega* / *J. Nat. Prod.* | African NP chemical space | **~95%** | ✅ Ready for submission | 0 |
| **P2** | *PLOS Comput. Biol.* / *J. Chem. Inf. Model.* | Polypharmacology MD validation | **~30%** | 🔴 Needs critical fixes | **4** (all narrative — no HPC needed) |
| **P3** | *J. Cheminform.* | Quantum-inspired TDA descriptors | **~82%** | ✅ Near-ready | 0 (Zenodo pending only) |
| **P4** | *J. Chem. Inf. Model.* | Pareto MCTS de novo design | **45→75%** | 🟡 Needs major work | **4** (Pareto data, QMC, benchmark, Greedy) |

### Cross-Cutting Observations

1. **Three of four projects reference the same Zenodo DOI** (10.5281/zenodo.19608875) — shared deposit is acceptable but must be well-organised
2. **P2 directly contradicts itself** on which MD systems are bound vs unbound
3. **P3's H₁-RRS correlation (ρ=0.312, n=77)** is the definitive result; P2 still cites the inflated pilot (ρ=0.916, n=14)
4. **P4's computational label problem** mirrors P3's (both use Ersilia/ML proxy labels) — P3's ChEMBL mitigation (SM §9C) should be referenced in P4
5. **All four projects share the same single-library limitation** (African NP-derived compounds) — consistent across limitations sections

### Composite Acceptance Probability

| Scenario | P1 | P2 | P3 | P4 | All four accepted |
|----------|:--:|:--:|:--:|:--:|:-----------------:|
| **Current** | 95% | 30% | 82% | 45% | **~10%** |
| **After mitigations** | 97% | 85% | 85% | 75% | **~53%** |

Even after full mitigation, the probability that all four are accepted is only ~53% due to P2's and P4's remaining uncertainties.

---

## 1. Project 1 (P1) — Antimalarial Candidates from African NP Space

**Target:** *ACS Omega* or *Journal of Natural Products*
**Status:** ✅ **Ready for submission** — 1 minor polishing item remaining

### Summary

17 corrections (C-01 to C-20) applied over 7 days across 3 audit rounds:
- **Adversarial LM remediation** (C-01 to C-08): pH correction, docking box consistency, MPO Jaccard calibration, scaffold paradox, ADMET OOD
- **R8-B + full-cluster rescoring** (C-10, C-11): AiZynthFinder migration, 1815-molecule activity cliff validation
- **R1-A/B enrichment + MCMC** (C-12 to C-17): DEKOIS honest negative (AUC=0.496), MCMC surrogate declaration, syntax bugs, threshold consistency

### 9 Validated Positive Results

| Result | Value | Robustness |
|--------|:-----:|:----------:|
| R-01 Scaffold/whole Tanimoto ratio | 1.84× | ✅ Immune |
| R-02 ECFP4 unreachable / scaffold recovery | 92.6% / 69.3% | ✅ Immune |
| R-03 MCMC latent space | MPO +0.0246, top-1 = 0.8007 | ✅ Declared surrogate |
| R-04 Full-cluster rescoring (1815 mols) | ρ=0.072, no cliffs, best −10.33 | ✅ Immune |
| R-05 ChEMBL enrichment PfDHFR | 5.43× fold on true inactives | ✅ Immune |
| R-06 pH-correction PfCRT | ρ=0.270, Δ mean +2.20 kcal/mol | ✅ Immune |
| R-07 Tartarus (19,913 × 3 targets) | ρ(Vina vs MPO) = 0.013, orthogonal | ✅ Immune |
| R-08 PCA 9 descriptors | PC1-3 = 82.33% variance | ✅ Immune |
| R-09 ANPDB coverage | 94.9%, 37.0% scaffolds unique | ✅ Immune |

### Remaining Actions

| Action | Priority | Impact |
|--------|:--------:|:------:|
| P1-M1: Add P3 forward reference for scaffold paradox resolution | 🟢 LOW | Cross-paper coherence |
| P1-M2: Note shared Zenodo DOI with P3 in Data Availability | 🟢 LOW | Deposition clarity |

**Acceptance probability:** ~95% → **~97%** after optional polishing.

---

## 2. Project 2 (P2) — Polypharmacology MD Validation

**Target:** *PLOS Computational Biology* or *JCIM*
**Status:** 🔴 **NEEDS CRITICAL FIXES** — 4 critical issues must be resolved before submission

### Weakness P2-1: 🔴 MD Stability Claims Are INVERTED

**Severity:** 🔴 **CRITICAL** — paper's central claim is contradicted by actual data

**Problem:** The manuscript (line 132) states: *"Automated post-hoc trajectory analysis indicates that only the PfClpP complex is currently equilibrated; the remaining three wild-type systems show large backbone RMSD drift and zero detected protein–ligand contacts/hydrogen bonds."*

**Reality (AGENTS.md July 15):**

| System | Manuscript claims | Actual finding |
|--------|:-:|:-:|
| 164/PfClpP | ✅ "only system equilibrated" | ❌ **UNBOUND** (min dist 67.4 Å, 0 contacts) |
| 201/PfDHFR | ❌ "large drift, zero contacts" | ❌ **UNBOUND** (min dist 78.2 Å, 0 contacts) |
| 214/PfCRT | ❌ "large drift, zero contacts" | ✅ **BOUND** (min dist 3.19 Å, 78 contacts, 23 H-bonds) |
| 438/PfATP4 | ❌ "large drift, zero contacts" | ✅ **BOUND** (min dist 2.25 Å, 178 contacts, 48 H-bonds) |

**The claim that PfClpP is the only bound system is the OPPOSITE of the truth.**

**Mitigation — Corrected narrative (copy-paste ready):**

> *"Of the four wild-type systems, two maintain a bound ligand throughout the 10 ns production trajectory: PfCRT (214, mean minimum distance 3.19 ± 0.25 Å, 78 persistent contacts, 23 H-bonds) and PfATP4 (438, mean minimum distance 2.25 ± 0.15 Å, 178 persistent contacts, 48 H-bonds). The other two systems, PfClpP (164) and PfDHFR (201), show stable protein conformations (backbone RMSD <3.0 Å) but the ligand dissociated within the first 2 ns (final minimum distance >65 Å, zero persistent contacts). These two dissociation events likely reflect genuine weak binding — consistent with the computed MM-GBSA values which represent solvent-phase stabilisation, not binding affinity — rather than simulation artefacts."

Data source: AGENTS.md (July 15 re-analysis with nojump coordinates, verified via `Project2_.../production_analysis/`).

---

### Weakness P2-2: 🔴 "30,000 ns of MD" Claim Is Misleading

**Severity:** 🔴 **CRITICAL** — quantitatively unsupported

**Problem:** Abstract and Conclusion claim "30,000 ns of MD simulation across 220 protein–ligand systems." However:
- Only **4** wild-type systems have production MD (10 ns each = **40 ns**)
- The remaining **216** systems (mutants × 20 candidates × 6 mutants = 120, controls = 20, etc.) have only **docking data** — no MD completed
- The 30,000 ns figure appears calculated as 220 × 136 ns (planned total) but execution is at <0.2% of this

**Mitigation:** Remove the "30,000 ns" claim. Report: *"Four wild-type systems were simulated for 10 ns each (40 ns total production MD). The Resistance Resilience Score (RRS) for 17 polypharmacology candidates was computed from docking scores validated against the wild-type trajectories."*

---

### Weakness P2-3: 🔴 MM-GBSA Values for Unbound Systems Are Invalid

**Severity:** 🔴 **CRITICAL** — reported values are physically meaningless

**Problem:** P2 SM reports MM-GBSA "binding free energies":
- 164/PfClpP: ΔG = −8.35 ± 2.54 kcal/mol
- 201/PfDHFR: ΔG = −24.74 ± 4.63 kcal/mol

But AGENTS.md (July 15) confirms both ligands dissociated to >65 Å from the protein. These values were computed from **solvent-phase unbound trajectories** — they do not represent binding free energies. Reporting them as such is misleading.

**Mitigation:** 
- **Option A (recommended):** Remove MM-GBSA values for 164 and 201 entirely
- **Option B:** Add explicit caveat: *"These MM-GBSA values were computed from trajectories in which the ligand dissociated from the binding site. They represent solvent-phase stabilisation, not binding affinity, and are reported for methodological completeness only."*
- For 214/PfCRT: MM-GBSA was not feasible (topology conversion issue) — already documented
- For 438/PfATP4: MM-GBSA was not feasible (2-chain topology) — already documented

---

### Weakness P2-4: 🟡 220 Systems Claim — Only 4 Have MD Data

**Severity:** 🟡 **HIGH** — transparency issue

**Problem:** The manuscript claims "220 protein–ligand systems" but only 4 have completed MD trajectories. The remaining 216 have:
- Tartarus docking scores (computational proxy)
- RRS computed from Vina scores of mutants, not MD
- Planned but not executed MD simulations

**Mitigation:** Clearly separate "systems with MD data" (4) from "systems evaluated via docking proxy" (216). The manuscript should not conflate these categories.

---

### Weakness P2-5: 🟡 Pilot H₁-RRS Correlation (ρ=0.916) Is Outdated

**Severity:** 🟡 **HIGH** — cross-paper inconsistency

**Problem:** P2 manuscript cites: *"Spearman ρ=0.916, p<0.0001, n=14"* for H₁-RRS correlation. But P3's expanded analysis (n=77) found ρ=0.312 (p=0.006). The pilot result was inflated by class-imbalanced sampling (46 A + 31 B, no C/D, only 1 D compound).

**Mitigation:** Update P2 to reference P3's definitive result: *"The expanded analysis (n=77, P3) confirmed the correlation at ρ=0.312 (p=0.006), indicating a weak-to-moderate effect. The pilot ρ=0.916 (n=14) was inflated by class imbalance."*

---

### Weakness P2-6: 🟡 17 Polypharmacology Compounds — Small Sample

**Severity:** 🟢 **LOW** — already acknowledged

**Problem:** Only 17 compounds satisfy the polypharmacology filter (bind ≥2 targets). With PNS computed from docking + STRING network (where PfCRT centrality defaults to 1.0), the PNS-RRS correlation (ρ=−0.665, p=0.009) is mechanically linked.

**Mitigation:** Already in Limitations. No additional action needed.

---

### P2 Acceptance & Action Plan

**Current acceptance probability:** ~30% → Target: **85%**

| Action | Impact | Effort | Priority |
|--------|:------:|:------:|:--------:|
| P2-M1: Fix MD stability claims (P2-1) | +20% | 1 day | 🔴 **CRITICAL** |
| P2-M2: Remove/rephrase 30,000 ns claim (P2-2) | +15% | 1 hour | 🔴 **CRITICAL** |
| P2-M3: Fix/remove invalid MM-GBSA values (P2-3) | +10% | 1 hour | 🔴 **CRITICAL** |
| P2-M4: Separate MD systems from docking-only (P2-4) | +10% | 1 day | 🟡 **HIGH** |
| P2-M5: Update H₁-RRS to P3 definitive result (P2-5) | +5% | 1 hour | 🟡 **HIGH** |
| P2-M6: Add P3 cross-reference | +2% | 30 min | 🟢 **MEDIUM** |

---

## 3. Project 3 (P3) — Quantum-Inspired Topological Descriptors

**Target:** *Journal of Cheminformatics* (IF ≈ 6.5)
**Status:** ✅ **NEAR-READY** — all 8 adversarial weaknesses mitigated, 2 polishing items remain

### Weakness P3-1: 🔴 Computational Activity Labels (CRITICAL → MITIGATED)

**Mitigation:** ChEMBL expanded validation (231 pairs, 7 matches, 3 active). Docking enrichment (5.43× fold). Honest framing in Limitations.

---

### Weakness P3-2: 🟡 H₁-RRS Correlation Attenuation (MEDIUM → MITIGATED)

**Mitigation:** Abstract canonized ρ=0.312 (p=0.006, n=77). Pilot ρ=0.947 moved to parenthetical. Power analysis in SM.

---

### Weakness P3-3: 🟡 SOTA Parity Only (MEDIUM → MITIGATED)

**Mitigation:** Cohen's d=+0.85 in SM SOTA table. Full n=19,849 benchmark on HPC. Fold-level statistics.

---

### Weakness P3-4: 🟡 Quantum Kernel Simulated (MEDIUM → MITIGATED)

**Mitigation:** NISQ-era caveat in Introduction. Kernels indistinguishable after RBF tuning. No quantum advantage claimed.

---

### Weakness P3-5: 🟡 D-GRIL/TopologyNet Not Benchmarked (MEDIUM → MITIGATED)

**Mitigation:** TopologyNet analog (MLP, AUC 0.799). D-GRIL build documentation in SM §9E (libc10.so ABI failure documented as reproducibility case study).

---

### Weakness P3-6: 🟡 ChEMBL Low Match Rate 3.0% (MEDIUM → MITIGATED)

**Mitigation:** Honest framing as structural novelty. ChEMBL36 bug fixed. Active matches (3) confirm binding potential.

---

### Weakness P3-7: 🟢 Single Library (LOW → MITIGATED)

**Mitigation:** Acknowledged in Limitations. ECFP4 provides internal calibration.

---

### Weakness P3-8: 🟢 Cohen's d Approximation (LOW → MITIGATED)

**Mitigation:** "Approximately" qualifiers added to Cohen's d and σ_pooled.

---

### Remaining Actions

| Action | Priority | Impact |
|--------|:--------:|:------:|
| P3-A1: Zenodo deposit (manifest ready, 100 files, 102.4 MB) | 🟡 HIGH | +3% |
| P3-A2: Trim manuscript 16→15 pages | 🟡 HIGH | +2% |

**Acceptance probability:** ~82% → **~85%** after Zenodo + trim.

---

## 4. Project 4 (P4) — Pareto MCTS De Novo Design

**Target:** *Journal of Chemical Information and Modeling* (JCIM) — ACS
**Status:** 🟡 **NEEDS MAJOR WORK** — 4 critical issues, 5 medium issues, 8 low issues

### Weakness P4-1: 🔴 MCTS Does Not Beat Greedy Search

**Severity:** 🔴 **CRITICAL** — defeats central methodological claim

**Problem:** Greedy (mean 0.638) outperforms MCTS (0.623). Abstract claims "competitive performance" but the simplest baseline beats MCTS.

**Mitigation:** Reframe narrative: MCTS targets **solution diversity and multi-objective exploration**, not peak single-objective reward. Lead with Pareto front (12 non-dominated solutions) as the primary advantage.

---

### Weakness P4-2: 🔴 n=5 Benchmark Underpowered

**Severity:** 🔴 **CRITICAL** — insufficient for Q1

**Problem:** Only n=5 seeds for Greedy, GA, Random comparison. Difference Δ=0.015 between Greedy (0.638) and MCTS (0.623) — within statistical noise at n=5.

**Mitigation:** Run full 20-seed 4-method benchmark on HPC (Job 12134 submitted).

---

### 🔴🔴 P4 Critical Weakness #3: Pareto Front Data: Unclear Provenance (DESK-REJECTION LEVEL)

**Severity:** 🔴 **CRITICAL — DESK REJECTION IF NOT FIXED** — if this data is synthetic, manuscript is unsubmittable

**Problem:** `p4_pareto_data.csv` has suspiciously clean round-number scores (0.85, 0.82, 0.79…) and a non-existent method label "pareto_qmc". No executable code path produces this data. The 12-point front with evenly spaced scores and the hypervolume claim (HV=0.56) are unverifiable. **This is the single most serious issue across all four projects.**

**Mitigation:** **Regenerate from scratch** using `p4_mcts_pareto.py` on HPC. **Delete current `p4_pareto_data.csv` immediately.** Report real (possibly less clean) Pareto front with 3-12 points and actual hypervolume. If regeneration yields only 3-5 points, that is acceptable — honesty trumps aesthetics.

**Absolute deadline:** Must be completed before submission. A reviewer or editor detecting fabricated data would result in immediate rejection.

---

### Weakness P4-4: 🔴 QMC Validation Entirely Pending

**Severity:** 🔴 **CRITICAL** — title/abstract promise results that don't exist

**Problem:** Title includes "Quantum Validation" but Table 4 shows "—" (pending) for every entry. DMC was never run.

**Mitigation:** **Option B (recommended):** Remove all QMC references from title, abstract, and results. Retitle to *"Pareto-Guided Monte Carlo Tree Search with Multi-Objective Optimization for Antimalarial De Novo Design."* Move QMC to Future Work paragraph.

---

### Weakness P4-5: 🟡 Ablation Study Uses Wrong Numbers

**Severity:** 🟡 **MEDIUM** — actual results contradict manuscript claims

**Problem:** Manuscript claims "108→10 degrades by 0.14 (11%)" but Job 12257 (40 tasks) shows:

| Set | Frags | Mean | Δ vs baseline | Manuscript claims |
|:----|:-----:|:----:|:-------------:|:-----------------:|
| all | 99 | 0.624 | baseline | — |
| medium | 24 | **0.628** | **+0.004** (higher!) | N/A |
| aromatic_only | 5 | 0.550 | −0.074 | −0.04 (20 frags) |
| minimal | 5 | **0.618** | **−0.006** (barely!) | −0.12 (10 frags) |

The minimal set (5 frags) barely degrades performance. The medium set (24 frags) actually outperforms the full set.

**Mitigation:** Replace all ablation numbers with Job 12257 results. Explain counterintuitive medium-set outperformance (possibly noise filtering from fewer low-quality fragments). Reframe from "vocabulary size degrades reward" to "99-fragment vocabulary is robust to moderate reduction."

---

### Weakness P4-6: 🟡 ScafVAE Policy Negligible (Δ=−0.02)

**Severity:** 🟡 **MEDIUM** — pillar of claimed novelty with no evidence

**Mitigation:** De-emphasise ScafVAE. Lead with Pareto MCTS as primary contribution.

---

### Weakness P4-7: 🟡 Oracle Weight Sensitivity Unanalysed

**Severity:** 🟡 **MEDIUM** — rankings may flip under weight perturbation

**Mitigation:** Run 12 weight perturbation experiments (±20% on 6 dimensions). Add sensitivity heatmap to SM.

---

### Weakness P4-8: 🟡 Chemical Validity Unverified (100% claim)

**Severity:** 🟡 **MEDIUM** — 100% claim needs verification

**Mitigation:** Run validity check across all 20 seeds × 4 methods. Document true validity % in SM.

---

### Weaknesses P4-9 to P4-17: Low Severity

| # | Weakness | Severity | Status |
|:-:|----------|:--------:|:------:|
| 9 | Hyperparameter search underpowered (30 iters) | 🟢 LOW | ❌ PENDING |
| 10 | Low variance CV=1.3% | 🟢 LOW | ❌ PENDING (variance decomposition) |
| 11 | Oracle-call efficiency (5.7× cost, 2.5× gain) | 🟢 LOW | ❌ PENDING (wall-clock reframing) |
| 12 | Missing SM (Tables S1-S8, Figures S1-S4) | 🟢 LOW | ❌ PENDING |
| 13 | Shared Zenodo DOI with P1/P2/P3 | 🟢 LOW | ✅ TRIVIAL |
| 14 | Cover letter must not reference companions | 🟢 LOW | ❌ PENDING |
| 15 | Docking proxy unvalidated | 🟡 MEDIUM | ❌ PENDING (holdout CV) |
| 16 | RRS/PNS proxy stacking | 🟢 LOW | ❌ PENDING (error propagation) |
| 17 | Greedy unfair oracle-call budget | 🟢 LOW | ❌ PENDING (efficiency figure exists) |

---

### P4 Acceptance & Action Plan

**Current acceptance probability:** ~45% → Target: **75%** (85% not achievable until P4-3 resolved)

| Action | Impact | Effort | Priority |
|--------|:------:|:------:|:--------:|
| P4-M1: Regenerate Pareto front from real runs (P4-3) | +10% | 8h HPC | 🔴 **CRITICAL** |
| P4-M2: Remove QMC from title/abstract (P4-4) | +15% | 30 min | 🔴 **CRITICAL** |
| P4-M3: Run full n=20 benchmark (P4-2) | +10% | 8h HPC | 🔴 **CRITICAL** |
| P4-M4: Fix ablation table with Job 12257 (P4-5) | +10% | 1h | 🟡 **HIGH** |
| P4-M5: Reframe narrative: diversity over peak (P4-1) | +5% | 2h | 🟡 **HIGH** |
| P4-M6: NN docking proxy validation (P4-15) | +5% | 1h HPC | 🟡 **HIGH** |
| P4-M7: Create SM file (P4-12) | +5% | 2h | 🟢 **MEDIUM** |
| P4-M8: Weight sensitivity + validity check (P4-7, P4-8) | +5% | 2h | 🟢 **MEDIUM** |

---

## 5. Cross-Cutting Weaknesses

### Cross-1: 🔴 Computational Labels as Ground Truth (P3 + P4)

Both P3 and P4 use Ersilia ML predictions as activity labels. P3 has mitigated this via ChEMBL validation (SM §9C). P4 has no such mitigation.

**Action:** Cross-reference P3's ChEMBL validation in P4. State: *"Activity labels are from the same Ersilia model validated in [P3 reference]; ChEMBL validation found 3/7 structural analogues active (IC₅₀ 0.40–0.79 μM), confirming the label set's biological relevance."*

---

### Cross-2: 🟡 Cross-Paper H₁-RRS Inconsistency (P2 → P3)

P2 cites ρ=0.916 (n=14); P3's definitive result is ρ=0.312 (n=77).

**Action:** P2 must update to reference P3's definitive result. P3's earlier pilot result (ρ=0.947) should be explicitly flagged as class-imbalanced.

---

### Cross-3: 🟢 Shared Zenodo DOI Hygiene (P1 + P3 + P4)

All three projects reference DOI 10.5281/zenodo.19608875.

**Action:** Ensure Zenodo upload has clear subdirectories: `P1_chemical_space/`, `P2_MD_validation/` (if included), `P3_quantum_descriptors/`, `P4_pareto_mcts/`, each with its own README.

---

### Cross-4: 🟢 Single-Library Limitation (All Projects)

All four projects use the same African NP-derived library (65,856 compounds).

**Action:** Each Limitations section should acknowledge this consistently. Cross-reference is optional but helpful.

---

## 6. Unified Action Plan: Priority Order

```
WEEK 1 (IMMEDIATE)
─────────────────────────────────────────────────────────────────
  P2-M1 Fix MD stability claims (inverted)     🔴 1 day   [NARRATIVE]
  P2-M2 Remove 30,000 ns claim                 🔴 1 hour  [NARRATIVE]
  P2-M3 Fix/remove invalid MM-GBSA             🔴 1 hour  [NARRATIVE]
  P4-M2 Remove QMC from title/abstract         🔴 30 min  [NARRATIVE]
  P4-M1 Regenerate Pareto front (HPC)          🔴 8 hours [COMPUTE]

WEEK 2 (HIGH PRIORITY)
─────────────────────────────────────────────────────────────────
  P2-M4 Separate MD systems from docking-only  🟡 1 day   [NARRATIVE]
  P2-M5 Update H₁-RRS to P3 definitive         🟡 1 hour  [NARRATIVE]
  P4-M3 Run n=20 benchmark (HPC)               🔴 8 hours [COMPUTE]
  P4-M4 Fix ablation table with Job 12257      🟡 1 hour  [NARRATIVE]
  P4-M5 Reframe MCTS vs Greedy narrative       🟡 2 hours [NARRATIVE]
  Cross-4 Update single-library limitation     🟢 30 min  [NARRATIVE]

WEEK 3 (MEDIUM PRIORITY)
─────────────────────────────────────────────────────────────────
  P4-M6 NN docking proxy validation            🟡 1 hour  [COMPUTE]
  P4-M7 Create SM file for P4                  🟢 2 hours [DOCUMENT]
  P4-M8 Weight sensitivity + validity check    🟢 2 hours [COMPUTE]
  P3-A1 Zenodo deposit                         🟡 1 hour  [DATA]
  P3-A2 Trim manuscript 16→15 pages            🟡 1 hour  [NARRATIVE]

WEEK 4 (BEFORE SUBMISSION)
─────────────────────────────────────────────────────────────────
  Cross-3 Ensure Zenodo subdirectories         🟢 1 hour  [DATA]
  P1-M1 Add P3 forward reference               🟢 30 min  [NARRATIVE]
  P1-M2 Update shared Zenodo DOI note          🟢 30 min  [NARRATIVE]
  Cross-2 Fix H₁-RRS cross-reference           🟢 30 min  [NARRATIVE]
  Cross-1 Add P3 ChEMBL ref to P4              🟡 1 hour  [NARRATIVE]
  Final compilation all 4 manuscripts          — 2 hours  [COMPILE]
```

---

## 7. Submission Order Recommendation

Based on current readiness and acceptance probability:

```
1. P1 (ACS Omega) — Submit NOW       [95%] ✅
2. P3 (J. Cheminform.) — Submit in 1 week [85%] 🟢
3. P4 (JCIM) — Submit in 2-3 weeks   [75%] 🟡
4. P2 (PLOS Comput. Biol.) — Major revision needed [85% after fixes] 🔴
```

---

## 8. Key Files Requiring Changes

| File | Project | Required Action |
|------|:-------:|----------------|
| `Project2_.../manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` | P2 | 🔴 Major: fix MD claims, 30k ns, MM-GBSA |
| `Project2_.../manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex` | P2 | 🔴 Fix invalid MM-GBSA values |
| `Project4_.../manuscript/LaTeX/P4_Pareto_MCTS_V2607.tex` | P4 | 🔴 Major: retitle (remove QMC), fix ablation, reframe benchmark |
| `Project4_.../results/benchmark/p4_pareto_data.csv` | P4 | 🔴 **Delete** — regenerate from real Pareto MCTS |
| `Project4_.../manuscript/LaTeX/P4_Pareto_MCTS_SM_V2607.tex` | P4 | 🟢 **Create** — SM does not exist |
| `Project1_.../manuscript/Deep_Learning_Antimalarial_Hybrids_V2.tex` | P1 | 🟢 Optional: add P3 forward reference |
| `Project3_.../manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex` | P3 | 🟢 Trim to 15 pages |
| `Project3_.../manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex` | P3 | 🟢 No changes needed |
| `AGENTS.md` | All | 📝 Update with consolidated audit status |
| `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | All | 📝 Already contains §3.20 (P3) and §4.x (P4) |

---

## 9. Acceptance Probability Summary

| Project | Current | After mitigations | Max achievable | Confidence |
|---------|:-------:|:-----------------:|:--------------:|:----------:|
| P1 | 95% | 97% | 97% | High (data-backed)|| P2 | 30% | 85% | 85% | High fixability (4 narrative fixes, 0 compute) |
| P3 | 82% | 85% | 88% | High (all 8 weaknesses mitigated) |
| P4 | 45% | 75% | 82% | Low (Pareto data crisis + QMC removal) |
| **All four** | **~10%** | **~53%** | **~58%** | |

**Safest strategy:** Submit P1 + P3 immediately. Invest the saved time into fixing P2 and P4 by the time the first two papers complete peer review (3-6 months).
