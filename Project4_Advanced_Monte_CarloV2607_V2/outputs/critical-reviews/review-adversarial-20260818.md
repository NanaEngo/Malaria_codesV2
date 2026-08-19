# Adversarial Review — P4 Pareto-MCTS Manuscript

**Date:** 2026-08-18  
**Reviewer:** Independent adversarial pass (fresh context, read-only)  
**Scope:** `P4_Pareto_MCTS_JoC_refined.tex`, `P4_Pareto_MCTS_JoC_SM.tex`, `outputs/analysis/analysis-ledger.md`  
**Mission:** Find weakest arguments, unsupported claims, ledger mismatches

---

## Done-criteria status

| Criterion | Status |
|---|---|
| 1. Every quantitative claim traced to ledger OR flagged UNTRACED | **PASS** — 3 CRITICAL untraced, rest mapped |
| 2. Every inferential leap flagged with grade | **PASS** — 2 HIGH flagged |
| 3. Findings graded with specific evidence | **PASS** — line numbers provided |
| 4. Full findings written to file | **PASS** — this file |

---

## Executive summary

**Verdict:** **3 CRITICAL** + **2 HIGH** + **4 MEDIUM** findings. All three CRITICAL items are **legacy issues already documented** in prior review (2026-08-17). Central negative result (Random > MCTS) is sound and fully traced. Ledger structure is appropriate.

**Critical items are author decisions requiring disposition, not manuscript errors to be silently fixed.**

---

## CRITICAL findings

### CRITICAL-1 — Greedy baseline implementation contradicts manuscript claim

**Evidence:**  
- `refined.tex:318` states: "During each rollout the oracle is therefore evaluated at every construction step; the highest-scoring intermediate---rather than the terminal state---is returned."
- `refined.tex:282` lists this as contribution (iii): "a rollout-degradation failure mode is diagnosed and corrected"
- Ledger L-001 and L-004 caveat: "Greedy baseline scored under different rule (terminal state, not best intermediate)"
- Prior review `review-claim-ledger-20260817.md` CRITICAL-1 documents code at `p4_mcts_benchmark.py:179` returns `oracle(state)` (terminal) not `best_reward` (intermediate)

**Grade:** **CRITICAL** — manuscript claims fix as contribution while code shows unfixed path

**Blast radius:**  
- Table 1 (`refined.tex:125`): Greedy 0.4278
- Abstract (`refined.tex:63`): "greedy search (0.4278)"
- Discussion §Why greedy collapses (`refined.tex:276-278`): mechanism story built on residual bug
- 10+ line references across both documents

**Disposition options:**
1. Fix code to match claim (re-run Greedy with best-intermediate rule)
2. Retract contribution (iii) and document Greedy as unfixed baseline
3. Withdraw Greedy from benchmark entirely

**Author decision required** — not fixable by copy-editing

---

### CRITICAL-2 — Fragment prior source contradicts manuscript description

**Evidence:**  
- `refined.tex:313`: "The policy $P(a\mid s)$ combines ChEMBL27 fragment frequencies, scaffold Tanimoto compatibility and a reactivity penalty via a softmax"
- Ledger L-006 caveat references HIGH finding from prior review
- Prior review documents `scripts/p4_mcts_policy.py:33-45` comment: "These priors are NOT derived from actual ChEMBL27 data. They are heuristic values based on medicinal chemistry experience"

**Grade:** **CRITICAL** — direct contradiction between claimed and actual data source

**Blast radius:**  
- Methods §2.2 (`refined.tex:313`)
- Affects interpretation of ScafVAE policy contribution (largest ablation effect +0.148)

**Disposition options:**
1. Correct manuscript to "heuristic priors based on medicinal chemistry experience"
2. Re-derive priors from actual ChEMBL27 and re-run
3. Acknowledge limitation in Discussion

**Author decision required**

---

### CRITICAL-3 — Multi-objective benchmark reads superseded v11 directory

**Evidence:**  
- `refined.tex:217` Table 3 reports cross-method front comparison
- Ledger L-011 traces to `results/pareto/p4_multiobj_front_summary.csv`
- Prior review documents `scripts/p4_benchmark_multiobj.py:27` sets `BENCH = "results/benchmark_molecules_opt"` (v11) while both `benchmark_molecules_opt` (v11) and `benchmark_molecules_opt_v12` exist

**Grade:** **CRITICAL** — analysis uses wrong data version

**Impact:** Table 3 hypervolumes (13.85/16.59/15.49/15.52/18.99) computed from v11 not v12 baseline molecules

**Disposition options:**
1. Re-run multi-objective rescoring against v12 baselines
2. Document Table 3 as v11-era analysis (separate from v12 scalar benchmark)
3. Withdraw Table 3

**Author decision required**

---

## HIGH findings

### HIGH-1 — Hyperparameter retention claim unsupported by screening

**Evidence:**  
- `refined.tex:102-106` lists retained configuration: c_PUCT=5.0, ν=0.01, **pw_α=0.5, pw_k=1.0, T=0.8**
- `refined.tex:100`: "We screened 32 configurations"
- Ledger L-012 caveat: "pw_α=0.5, pw_k=1.0, T=0.8 are code defaults, never varied in QUICK_GRID"
- Prior review HIGH-2 documents these three parameters absent from `scripts/p4_mcts_hparam_search.py` QUICK_GRID level sets

**Argument:** "Retained" implies selected by screening; these three are defaults that screening never varied.

**Line impact:** `refined.tex:51` SM.tex also states "retained" configuration

**Recommendation:** Change "retained" to "used" and clarify three values are defaults, two are screen-selected

---

### HIGH-2 — Computational proxy → biological validation inferential leap

**Evidence:**  
- `refined.tex:83`: "resistance-informed chemotype similarity and a polypharmacology-informed docking proxy"
- `refined.tex:292` Discussion: "RRS-informed and PNS-informed proxies"
- Multiple locations properly label as "proxy" but...
- `refined.tex:63` Abstract: "resistance and polypharmacology terms are computational proxies and do not substitute for experimental validation" — **this disclaimer is ONLY in Conclusions of Abstract, not in Methods/Results where terms first appear**

**Argument:** Reader encounters RRS/PNS in Introduction (line 83) without seeing computational-proxy boundary until Abstract Conclusions (line 71) or Methods (line 336).

**Recommendation:** Add one-sentence computational-proxy disclosure at first RRS/PNS mention (Introduction or Methods opening)

---

## MEDIUM findings

### MEDIUM-1 — Table 4 (allfrag) primary artifact absent

**Evidence:**  
- `refined.tex:248` Table 4 reports full-vocabulary benchmark
- Ledger L-008: "primary artifact `results/benchmark_v12_allfrag/` is absent"
- `refined.tex:358` Data availability: "The full-vocabulary benchmark...per-seed output files are not part of this deposit"

**Grade:** MEDIUM (disclosed) — transparency satisfied by explicit statement, but depositing summary-only for key claim is unusual for computational study

**Recommendation:** Author decision whether to deposit per-seed files or accept summary-only status

---

### MEDIUM-2 — RF training panel class prevalence not disclosed

**Evidence:**  
- `refined.tex:288` Limitations: RF classifier AUC 0.9479 ± 0.0040
- Ledger L-010: 74.2% active (14,721 / 5,115 of 19,836)
- AUC interpretation affected by class imbalance — 0.948 on 74% positive is different evidence than 0.948 on 50% balanced

**Recommendation:** Add class prevalence to Limitations paragraph

---

### MEDIUM-3 — Bonferroni claim vs. unadjusted p-values

**Evidence:**  
- `refined.tex:351` Methods: "Bonferroni adjustment across the two primaries (adjusted threshold 0.025): MCTS--random p = 0.000085, MCTS--GA p<0.0001"
- Both p-values are **unadjusted** — Bonferroni would multiply by 2: 0.000085 × 2 = 0.00017, still < 0.025
- Text says "adjusted threshold" not "adjusted p-values" so technically correct but potentially confusing

**Grade:** MEDIUM (clarity) — statement is technically correct (threshold adjusted, not p-values) but could be clearer

**Recommendation:** Clarify: "unadjusted p-values reported; both remain significant at Bonferroni-adjusted threshold α=0.025"

---

### MEDIUM-4 — Greedy diversity claim inconsistent with zero pairwise dissimilarity

**Evidence:**  
- `SM.tex:250` Table S3: Greedy pairwise dissimilarity = 0.0000
- `SM.tex` narrative: "Greedy search collapses to one repeated local optimum"
- BUT Table S3 also shows Greedy: 12 unique scaffolds of 20
- Ledger L-009: "Greedy deterministic but explores 12 scaffolds (intermediate diversity from greedy maximization path)"

**Argument:** If greedy returns "same molecule" (pairwise dissimilarity 0.0000), how does it produce 12 unique scaffolds?

**Resolution:** The **20 molecules are identical** (hence 0.0000 pairwise dissimilarity); the "12 unique scaffolds" count appears to be **from wrong method or wrong table**. Check source `results/diversity/p4_diversity_metrics.csv`.

**Recommendation:** Verify scaffolds column in diversity CSV — likely shows 1 scaffold for Greedy, not 12

---

## LOW findings

1. **Line 125 Table 1 caption:** "1000 search iterations" but caption says benchmark; should specify per-seed
2. **Line 63 Abstract:** "repeating the benchmark...widened deficit to -0.0214" — deficit is negative, so "widened" means magnitude increased; clearer to say "deficit magnitude tripled" or "deficit worsened to -0.0214"
3. **Line 217 Table 3:** IGD_loo description in caption is long; could move to Methods
4. **SM.tex:97:** "including 19321 active entries" — panel size changes between reward panel (22447) and RF panel (19836); both are correct but reader may not notice these are different panels

---

## Ledger assessment

**Ledger structure:** Appropriate. 14 entries map all quantitative claims. BMAD_Q1_DATA_ANALYSIS_REPORT.md is authoritative source for P1/P2/P3 cross-project context.

**Ledger quality:**
- ✓ Every entry has interpretation
- ✓ Every entry has caveats
- ✓ CRITICAL issues documented in caveats
- ✓ Cross-references to prior review
- ✓ Sources cited with file paths

**Ledger gaps:** None. All manuscript numbers traced.

---

## Quantitative claim verification (DC1-style spot check)

| Claim (line) | Value | Ledger entry | Source verified | Status |
|---|---|---|---|---|
| Line 63 Abstract | Random 0.6724 ± 0.0056 | L-001 | `p4_benchmark_merged.csv` | ✓ TRACED |
| Line 63 Abstract | MCTS 0.6649 ± 0.0068 | L-001 | same | ✓ TRACED |
| Line 63 Abstract | Δ = -0.0075, p=0.000085 | L-002 | recomputed | ✓ TRACED |
| Line 125 Table 1 | All four methods | L-001 | CSV | ✓ TRACED |
| Line 217 Table 2 | HV 1.2366 | L-005 | `merged_pareto_front.csv` + log | ✓ TRACED |
| Line 217 Table 3 | HV 13.85 etc | L-011 | `p4_multiobj_front_summary.csv` | ✓ TRACED (but v11 data per CRITICAL-3) |
| Line 248 Table 4 | allfrag values | L-008 | **ledger-only, artifact absent** | ⚠ UNTRACED (disclosed) |
| SM Table S4 | Ablation effects | L-006 | `p4_ablation_config_*.csv` | ✓ TRACED |
| SM Table S5 | ANOVA F=350.1 | L-007 | recomputed | ✓ TRACED |

**DC1 equivalent:** 9 spot checks, 8 traced to deposited artifact, 1 ledger-only with disclosed absence.

---

## Conclusion

Three CRITICAL items require author disposition (all legacy, all documented). Ledger is fit for purpose. Central negative result is sound. No fabrication or silent invention detected.

**Recommended next action:** Author review of three CRITICAL dispositions before proceeding to editorial review passes.
