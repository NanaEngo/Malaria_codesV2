# Peer Review — P4 Pareto-MCTS Manuscript

**Date:** 2026-08-18  
**Reviewer:** Technical peer review (fresh context, reproducibility focus)  
**Mission:** Assess Methods reproducibility, statistical appropriateness, likely reviewer objections

---

## Done-criteria status

| Criterion | Status |
|---|---|
| 1. Methods reproducible by expert | **CONDITIONAL** — 2 parameters unspecified |
| 2. Statistical tests appropriate | **PASS** — correct tests, proper corrections |
| 3. Top 3 reviewer objections identified | **PASS** — listed below |
| 4. Findings to file | **PASS** — this file |

---

## Reproducibility assessment

### Can an expert reproduce the main result from Methods alone?

**Test:** Read Methods without Results/Discussion. Can you reimplement?

**YES (specified):**
- ✓ MCTS algorithm (PUCT formula line 307)
- ✓ Fragment vocabulary (medium = 37, full = 80)
- ✓ Benchmark: 20 seeds, 1000 iterations, 4 methods
- ✓ Progressive widening formula (line 313)
- ✓ Hypervolume conventions (line 327, both)
- ✓ Statistical tests (paired t, Bonferroni, ANOVA + Tukey)
- ✓ Diversity metrics (Tanimoto dissimilarity, Murcko scaffolds)
- ✓ RF validation (5-fold CV, ECFP4 features)

**NO (underspecified):**
- ✗ **Initial benzene:** Stated as "rooted at benzene" but SMILES not given (c1ccccc1 vs C1=CC=CC=C1)
- ✗ **Screening budget:** "30 iterations per run" stated (line 100) but allfrag "1000 search iterations" (line 248) — do both benchmarks use 1000 or does screening use 30?
- ⚠ **Fragment attachment:** "regiospecific attachment point" (line 300) — how determined? RDKit implicit or explicit?
- ⚠ **Vocabulary source:** "curated fragment vocabulary" — where is it? Repository path not in Methods

**Verdict:** **Reproducible by competent expert** with repository access. Two minor ambiguities resolvable from code.

---

## Statistical appropriateness

### Test 1: Paired t-test (MCTS vs Random)

**Reported:** t₁₉ = -4.97, p = 0.000085, two-sided  
**Appropriate?** YES
- Paired design justified (seed-matched)
- df = 19 correct for n=20 pairs
- Two-sided appropriate (no directional prior)
- Bonferroni for 2 primaries: threshold 0.025, both p < 0.025 ✓

**Assumptions met?**
- Normality: n=20 is borderline for CLT; should check but not fatal
- Independence: seeds are independent ✓
- Paired structure: same seeds, same budgets ✓

**Grade:** PASS

### Test 2: ANOVA + Tukey HSD (vocabulary ablation)

**Reported:** F₃,₃₆ = 350.1, p = 1.12×10⁻²⁶; Tukey medium-minimal p_adj = 0.0052  
**Appropriate?** YES
- One-way ANOVA correct for 4 independent groups
- df correct: between=3 (4 groups - 1), within=36 (40 total - 4 groups)
- Tukey HSD appropriate for all pairwise comparisons with FWER control
- Effect size huge (F=350) → robust to assumption violations

**Grade:** PASS

### Test 3: Confidence interval construction

**Reported:** 95% CI [-0.0107, -0.0043] for Δ = -0.0075  
**Check:** CI is symmetric around Δ? Half-width = (0.0107 - 0.0075) = 0.0032 vs (0.0075 - 0.0043) = 0.0032 ✓ symmetric  
**Width:** 0.0064 total, consistent with SE ≈ 0.0064/(2×2.093) ≈ 0.00153 for df=19  
**Plausible** from SD=0.0068

**Grade:** PASS

---

## Top 3 likely reviewer objections

### Objection 1: "Why is Greedy deterministic while text claims rollout fix?"

**Strength:** CRITICAL — direct contradiction documented in prior review  
**Manuscript defense:** Methods line 318 claims fix; code shows unfixed Greedy path  
**Reviewer reaction:** "Authors state contribution (iii) as fixing rollout degradation yet Greedy still runs unfixed rule. Which is correct?"

**Likelihood:** **CERTAIN** — any careful reviewer will catch this  
**Author must address:** Before submission

---

### Objection 2: "Negative result — why submit if MCTS doesn't beat Random?"

**Strength:** HIGH — negative results face higher bar  
**Manuscript defense:**
- Abstract explicitly states "MCTS did not improve scalar reward" (line 66)
- Contribution is Pareto candidate-set geometry, not scalar superiority
- Discussion §270 frames as "useful but non-triumphal position"
- Honest negative reporting (line 63: "Random > MCTS")

**Reviewer reaction:** "Appreciate honesty, but is multi-objective analysis alone sufficient contribution?"

**Likelihood:** LIKELY — at least one reviewer will question novelty  
**Mitigation:** Strong Related Work positioning; emphasize decision-support framing

---

### Objection 3: "Computational proxies — how do we know RRS/PNS are meaningful?"

**Strength:** MEDIUM-HIGH — validation gap  
**Manuscript defense:**
- Line 71: "computational proxies and do not substitute for experimental validation"
- Line 83: "resistance-informed" and "polypharmacology-informed" (not claiming biological validation)
- Discussion line 292: proxies "encode design-relevant context"
- Limitations line 288: "scoring functions are computational proxies"

**Reviewer reaction:** "Without experimental validation, how is Pareto front meaningful beyond curve-fitting?"

**Likelihood:** LIKELY — validation-focused reviewers  
**Mitigation:** RF activity check (18/20 predicted active) provides orthogonal computational validation

---

### Additional likely questions

4. **"Why not show actual Pareto fronts for Random/GA in Figure 2?"** (line 201) — only MCTS front visualized
5. **"Table 4 has no deposited per-seed files"** (disclosed at line 358 but unusual)
6. **"Fragment priors claimed ChEMBL27-derived but code says heuristic"** (CRITICAL-2)

---

##Methods clarity — minor improvements

### Improvement 1: Specify fragment vocabulary location

**Current:** "curated fragment vocabulary" (line 300)  
**Better:** "curated fragment vocabulary (repository path `data/fragments/medium_37.txt`)"

### Improvement 2: Clarify iteration counts

**Current:** "30 iterations per run" (screening, line 100); "1000 search iterations" (benchmark, line 125)  
**Better:** State explicitly that screening uses 30, production uses 1000 (or 2000 for MCTS/Random per caption)

**Note:** Caption line 125 says "1000" but ledger L-001 says "2000 iterations budget (MCTS/Random)" — **DISCREPANCY**

### Improvement 3: Make Bonferroni clearer

**Current:** "adjusted threshold 0.025" (line 351)  
**Better:** "family-wise error rate α=0.05 divided by 2 comparisons = 0.025 threshold; unadjusted p-values reported"

---

## Code/data availability check

**Stated:** Line 370-378 Data availability  
**Assessment:**
- ✓ Repository URL provided (github.com/NanaEngo/Malaria_codesV2)
- ✓ Directory structure documented
- ✓ MIT license stated
- ⚠ Table 4 disclosure: "per-seed output files are not part of this deposit" — **unusual but disclosed**
- ⚠ Environment file referenced (line 356) but doesn't exist per prior review

**Grade:** MOSTLY SUFFICIENT — one gap (environment file)

---

## Conclusion

**Reproducibility:** Adequate with minor ambiguities. Expert with repository access can reproduce.

**Statistical rigor:** Tests appropriate, properly applied, correctly reported.

**Likely objections:** Three major (Greedy contradiction, negative result justification, proxy validation); authors have prepared defenses for 2 of 3.

**Recommendation:** Address Greedy contradiction (CRITICAL-1) before submission. Other issues manageable in review response.
