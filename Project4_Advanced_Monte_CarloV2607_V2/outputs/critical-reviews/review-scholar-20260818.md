# ScholarEval Assessment — P4 Pareto-MCTS Manuscript

**Date:** 2026-08-18  
**Reviewer:** Scholar-evaluation dimensions (evidence-based scoring)  
**Scope:** Quality assessment across standard evaluation dimensions

---

## Done-criteria status

| Criterion | Status |
|---|---|
| 1. All ScholarEval dimensions scored with evidence | **PASS** — 8 dimensions scored |
| 2. Scores in structured format for revision tracking | **PASS** — table below |
| 3. Overall assessment documented | **PASS** — see summary |
| 4. Findings to file | **PASS** — this file |

---

## Overall assessment

**Publication readiness:** **MINOR REVISION**

**Summary:** Technically sound negative result with honest reporting. Three CRITICAL legacy issues require author disposition before submission. Once addressed, suitable for Journal of Cheminformatics.

---

## Dimension scores (1-5 scale, 5 = excellent)

| Dimension | Score | Evidence |
|---|---|---|
| **Novelty** | 3.5 | Multi-objective MCTS is known (Mothra 2024); contribution is domain-specific integration (antimalarial, RRS/PNS proxies) + honest negative scalar result + decision-support framing. Incremental but solid. |
| **Rigor** | 4.0 | Statistical tests appropriate (paired t, ANOVA, Bonferroni). 20-seed benchmark. Negative result reproducible across vocabularies. **Deduction:** 3 CRITICAL provenance issues (Greedy rule, fragment priors, v11 data). |
| **Clarity** | 4.0 | Methods detailed, figures clear, tables well-labeled. Two hypervolume conventions explicitly marked non-comparable (excellent). **Minor:** Some parameters underspecified (benzene SMILES, vocabulary path). |
| **Reproducibility** | 3.5 | Repository provided, directory structure documented. **Gaps:** Table 4 per-seed files absent (disclosed), environment file referenced but missing, 2 parameters ambiguous. Expert can reproduce with code access. |
| **Significance** | 3.0 | Honest negative result is valuable but incremental. Decision-support framing is useful. Domain application (antimalarial + RRS/PNS) is niche. Pareto front analysis is descriptive, not transformative. |
| **Writing quality** | 4.5 | Clear, concise, appropriately cautious language. No AI-smell detected. British spelling consistent. Technical terms well-defined. **Minor:** Some long sentences in Discussion. |
| **Ethics & transparency** | 5.0 | **Excellent.** Negative result honestly reported in Abstract. Limitations paragraph upfront about computational proxies. Greedy bug documented (even if not fixed). Data availability explicit about Table 4 gap. AI use disclosed. |
| **Contribution claims** | 4.0 | Claims appropriately bounded ("computational proxies", "testable prioritisation set"). No overclaiming. **Deduction:** Contribution (iii) claims rollout fix while Greedy code unfixed (CRITICAL-1). |

**Mean score:** 3.94 / 5.0 ≈ **4.0** (Good, minor revision needed)

---

## Dimension details

### 1. Novelty (3.5/5)

**Strengths:**
- Honest negative result (Random > MCTS) is publication-worthy
- Domain integration (antimalarial, RRS/PNS) is new combination
- Decision-support framing (Pareto vs scalar) is clear conceptual contribution
- Scaffold-aware fragment policy is technical contribution

**Limitations:**
- Pareto-MCTS framework is established (Mothra, ParetoDrug, CombiMOTS)
- Negative scalar result is honest but not surprising (tree convergence is known issue)
- RRS/PNS are computational proxies, not biological validation

**Competitive position:** Solid domain application paper, not methodological breakthrough.

---

### 2. Rigor (4.0/5)

**Strengths:**
- Statistical tests appropriate and correctly applied
- 20-seed benchmark with proper power
- Paired design for seed-matched comparison
- Bonferroni correction documented
- Factorial ablation well-designed (2^5, balanced)
- Hypervolume conventions carefully separated

**Critical gaps:**
- CRITICAL-1: Greedy rule contradiction (terminal vs intermediate)
- CRITICAL-2: Fragment prior source (heuristic vs ChEMBL27-derived)
- CRITICAL-3: Multi-objective benchmark uses v11 not v12 data
- HIGH: Hyperparameter "retained" vs "used" (3 never screened)

**Why still 4.0?** Core statistical framework is sound; provenance issues are fixable.

---

### 3. Clarity (4.0/5)

**Strengths:**
- Figures excellent (integrated evidence overview, Pareto front)
- Tables well-structured with clear captions
- Two hypervolume conventions explicitly non-comparable (3 warnings)
- Methods section detailed
- Abstract structured (Background/Methods/Results/Conclusions)

**Minor gaps:**
- Initial benzene SMILES not specified
- Fragment vocabulary path not in Methods
- "1000 iterations" vs "2000 iterations" discrepancy (caption vs ledger)
- Progressive widening "5--20" is approximate (actually 5--31 at N=1000)

---

### 4. Reproducibility (3.5/5)

**Strengths:**
- GitHub repository provided
- Directory structure documented
- MIT license stated
- Random seeds fixed and documented
- Statistical tests fully specified

**Gaps:**
- Table 4 per-seed files absent (disclosed but unusual)
- Environment file referenced (line 356) but doesn't exist
- Some parameters require code inspection (attachment points, vocabulary source)
- No Docker/Conda environment for one-command reproduction

**Assessment:** Reproducible by competent expert **with repository**, not from manuscript alone.

---

### 5. Significance (3.0/5)

**Strengths:**
- Honest negative result publication is valuable (prevents file-drawer bias)
- Decision-support framing is useful conceptual contribution
- Four-method benchmark is thorough
- Domain application (antimalarial design) is important problem

**Limitations:**
- Negative scalar result limits immediate practical impact
- Pareto front is descriptive, not validated experimentally
- RRS/PNS proxies lack biological validation
- Fragment vocabulary constraint limits generalization
- Contribution is incremental application, not methodological advance

**Impact forecast:** Modest. Will be cited for honest negative reporting and decision-support framing, not as breakthrough.

---

### 6. Writing quality (4.5/5)

**Strengths:**
- Clear, direct prose
- No AI-detectable patterns (no "delve", "leverage", "underscore")
- Technical terms well-defined
- Appropriate caution ("computational proxies", "testable prioritisation")
- British spelling consistent
- Active voice where appropriate

**Minor issues:**
- Some Discussion sentences are long (line 270-271: 3-clause sentence)
- Occasional passive where active would be clearer
- "Approximately" overused (2.6× rollout factor, 5--20 progressive widening)

**Anti-AI scan:** 0 banned patterns detected.

---

### 7. Ethics & transparency (5.0/5)

**Exemplary:**
- Negative result in Abstract first sentence of Results
- Limitations paragraph explicitly disclaims biological validation
- Table 4 gap disclosed in Data availability
- AI use disclosed ("AI assistants...support code development")
- Greedy bug is documented even if not fixed
- No author conflicts stated
- Computational proxies consistently labeled as such
- No overclaiming detected

**This is model scientific transparency.**

---

### 8. Contribution claims (4.0/5)

**Appropriate claims:**
- "MCTS did not improve scalar reward" — **honest**
- "computational proxies and do not substitute for experimental validation" — **bounded**
- "testable prioritisation set" — **appropriately cautious**
- No biological validation claimed

**Problematic claim:**
- Line 282 contribution (iii): "rollout-degradation failure mode is diagnosed and corrected"  
  **But:** Greedy still runs unfixed rule (CRITICAL-1)  
  **Deduction:** 1 point for contradiction

---

## Revision tracking baseline

**Baseline scores for revision comparison:**

| Dimension | Current | Target after fixes |
|---|---|---|
| Novelty | 3.5 | 3.5 (unchanged) |
| Rigor | 4.0 | 4.5 (after CRITICAL fixes) |
| Clarity | 4.0 | 4.5 (after parameter specs) |
| Reproducibility | 3.5 | 4.0 (after env file + specs) |
| Significance | 3.0 | 3.0 (unchanged by fixes) |
| Writing | 4.5 | 4.5 (minor polishing) |
| Ethics | 5.0 | 5.0 (already excellent) |
| Claims | 4.0 | 4.5 (after CRITICAL-1 fix) |

**Target mean after minor revision:** 4.2 / 5.0 (from current 3.94)

---

## Recommendation for authors

**Before submission:**
1. **MUST address:** CRITICAL-1, CRITICAL-2, CRITICAL-3 (all require author decisions)
2. **Should address:** HIGH findings (hyperparameter language, vocabulary confound link, proxy disclosure placement)
3. **Nice to have:** MEDIUM findings (class prevalence, Bonferroni clarity, Greedy diversity fix)

**After fixes:** Suitable for Journal of Cheminformatics. Expect 1-2 rounds of minor revision focusing on:
- Reviewer objection #2 (negative result justification)
- Reviewer objection #3 (proxy validation gap)
- Statistical/methodological details

**Estimated outcome:** Accept after minor revision (70% confidence), given honest reporting and solid execution despite negative result.
