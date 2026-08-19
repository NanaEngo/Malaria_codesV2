# Critical Thinking Review — P4 Pareto-MCTS Manuscript

**Date:** 2026-08-18  
**Reviewer:** Critical thinking / falsifiability assessment  
**Mission:** Examine causal claims, alternate explanations, overclaiming vs evidence

---

## Done-criteria status

| Criterion | Status |
|---|---|
| 1. Every causal claim examined for confounds | **PASS** — 4 causal claims assessed |
| 2. Negative result checked for alternates | **PASS** — 3 alternate explanations considered |
| 3. "Demonstrates/shows/validates" vs evidence | **PASS** — 6 strong verbs audited |
| 4. Findings to file | **PASS** — this file |

---

## Executive summary

**Verdict:** 0 CRITICAL + 1 HIGH + 2 MEDIUM. No unfalsifiable claims. Negative result honestly presented with alternate explanations acknowledged. One confound uncontrolled in ablation.

---

## Causal claims audit

### Claim 1: "ScafVAE policy causes +0.148 reward increase"

**Location:** Line 247, SM Table S4  
**Evidence:** $2^5$ factorial ablation, ScafVAE ON vs OFF

**Confounds checked:**
- Other factors varied simultaneously? YES — but factorial design isolates marginal effects ✓
- Same seeds across conditions? Text says "five replicates per cell" — design is crossed ✓
- Same oracle? Line 247: "distinct oracle-weight configuration from v12" — **ablation uses different reward than benchmark**

**Falsifiability:** Could measure ScafVAE effect under v12 oracle — **testable**

**Verdict:** CAUSAL claim supported by controlled design **within ablation's oracle**; generalization to v12 benchmark not claimed (appropriately cautious)

**Grade:** PASS (bounded claim)

---

### Claim 2: "Vocabulary expansion causes performance gain"

**Location:** Line 247 (ablation), Line 248 (allfrag benchmark)  
**Evidence:** Factorial ablation +0.079; ANOVA F=350.1 (p<10⁻²⁶)

**Confounds:**
- Vocabulary changed between eras: "earlier development vocabulary" (SM line 235) vs "80-fragment v12 set" (line 248)
- **Confound:** Line 248 allfrag shows MCTS deficit **widened** under full vocabulary (Δ=-0.0214 vs -0.0075)

**Alternate explanation:** Larger vocabulary helps when **all other factors controlled** (ablation) but **hurts MCTS relative to Random** in head-to-head (allfrag). Why?
→ Manuscript line 270: "tree concentrates evaluations on narrow set of paths after ~200 iterations...progressive widening...limits...to 5--20 out of 80"
→ Random samples all 80 uniformly; MCTS prunes to ~20 → Random explores 4× more diversity

**Causal claim status:** **Confounded by search-method interaction**. Vocabulary expansion does not universally improve MCTS; it helps when other factors favor exploration.

**Grade:** HIGH — confound is **disclosed** in Discussion (line 270) but not linked to vocabulary claim

**Recommendation:** Add one sentence: "The factorial ablation's vocabulary benefit was measured under conditions favoring exploration; in the head-to-head benchmark progressive widening limited MCTS to ~20 of 80 fragments, reducing the advantage."

---

### Claim 3: "Rollout fix increased reward by factor ~2.6"

**Location:** Line 318  
**Evidence:** "relative to agent without global best-molecule tracking"

**Confounds:**
- What else changed between v6 (pre-fix) and v11 (post-fix)? Prior review notes: "other changes landed between v6 and v11"
- No controlled A/B test reported (fix ON vs OFF, all else equal)

**Falsifiability:** Could run matched-seed comparison with/without fix — **testable** but not done

**Grade:** MEDIUM — factor is **attributed** but not **isolated** by controlled ablation. Manuscript acknowledges (line 318 "approximately") but doesn't state confounding.

---

### Claim 4: "Pareto selection causes +0.108 reward increase"

**Location:** Line 247, SM Table S4  
**Evidence:** Factorial design, Pareto ON vs OFF

**Confounds:** Same as Claim 1 — factorial isolates effect **within ablation oracle**

**Falsifiability:** Testable under any oracle  
**Grade:** PASS (bounded)

---

## Negative result: alternate explanations

### Central claim: "Random > MCTS on scalar reward"

**Evidence:** t₁₉ = -4.97, p = 0.000085, Δ = -0.0075 (medium vocab); Δ = -0.0214 (full vocab)

**Manuscript's explanation** (line 270-271):
"Tree convergence: with 1000 iterations and c_PUCT=5.0, search tree concentrates evaluations on narrow set of paths after ~200 iterations, whereas random search distributes same oracle budget across 1000 independent trajectories."

**Alternate explanation 1: Hyperparameter suboptimal**
- Screening used 30-iteration budget (line 100); production uses 1000
- 30-iteration regime may favor different c_PUCT than 1000-iteration
- **Falsifiability:** Re-screen at 1000 iterations
- **Manuscript defense:** None explicit — acknowledges "30 iterations" (line 100) but doesn't discuss cross-budget generalization
- **Status:** Plausible alternate, **not ruled out**

**Alternate explanation 2: Fragment vocabulary too constrained**
- 37-fragment medium set may not contain high-reward paths MCTS would find in open SMILES
- Random's broad sampling favors small vocabularies
- **Falsifiability:** Test on unconstrained SMILES generation
- **Manuscript defense:** Line 284: "fragment vocabulary...constrains accessible chemical space, so findings do not generalise automatically to open-ended SMILES"
- **Status:** **Acknowledged as limitation** ✓

**Alternate explanation 3: Reward function favors Random**
- Activity proximity is max-Tanimoto to known actives
- Random broad sampling → more likely to hit high-Tanimoto regions by chance
- MCTS policy bias → concentrates near ChEMBL27-informed priors
- **Falsifiability:** Test on reward without activity term
- **Manuscript defense:** v12 reward includes activity (weight 0.10); pre-activity Pareto uses different vector
- **Status:** Not explicitly discussed but implicitly addressed by two-reward design

**Verdict:** Manuscript's explanation (tree convergence) is **one** cause among several. **Alternate 1 (hyperparameter screening at wrong budget) is not ruled out.**

**Grade:** MEDIUM — negative result explanation is plausible but not uniquely determined

---

## "Demonstrates/shows/validates" verb audit

### Verb 1: "demonstrated" (line 103, Related Work)

**Claim:** "Mothra demonstrated that Pareto fronts reveal trade-offs"  
**Evidence:** Citation to Mothra paper  
**Appropriateness:** Citing prior work — **PASS**

### Verb 2: "shows" (line 138)

**Claim:** Table 1 "shows" Random > MCTS  
**Evidence:** Empirical data, 20 seeds, statistical test  
**Overclaim?** NO — direct observation, inferentially tested  
**Grade:** PASS

### Verb 3: "exposes" (line 202, Figure 2 caption)

**Claim:** Front "exposes potency--accessibility trade-offs"  
**Evidence:** P3 has MPO=0.946, SYBA=0.021; P2 has MPO=0.945, SYBA=1.000  
**Overclaim?** NO — descriptive, directly observable from table  
**Grade:** PASS

### Verb 4: "establishes" (not present in Results)

**Searched:** "establishes" appears 0 times in manuscript — **good restraint**

### Verb 5: "validates" (line 288)

**Claim:** "RF check...18 of 20 predicted active...This is **computational validation**, not experimental"  
**Evidence:** RF model, 5-fold CV AUC 0.9479  
**Overclaim?** NO — explicitly bounds as "computational", disclaims biological validation  
**Grade:** PASS

### Verb 6: "provides" (line 374 Conclusions)

**Claim:** "provides a **testable prioritisation set** for biochemical, cellular, and resistance-mutant follow-up"  
**Overclaim?** NO — offers for testing, doesn't claim validated  
**Grade:** PASS

**Verb audit summary:** Language is appropriately cautious. No overclaiming detected.

---

## Falsifiability assessment

### Can the central claim be falsified?

**Claim:** "MCTS does not improve scalar reward over Random"  
**Falsifiable?** YES
- Different hyperparameters could reverse result
- Different vocabulary could reverse result
- Different reward function could reverse result
- Different iteration budget could reverse result

**Has manuscript shown result is robust?** Partially:
- ✓ Tested across 2 vocabularies (medium, full) — deficit persists
- ✓ Tested 20 independent seeds — reproducible
- ✗ Not tested across hyperparameter variations beyond 32-config screening at 30-iter budget

**Grade:** Falsifiable and partially robustness-tested

### Can Pareto analysis be falsified?

**Claim:** "Front spans potency-accessibility trade-offs"  
**Falsifiable?** YES — could show all front points are dominated by a single scalar weighting, or that front collapses under different normalization

**Evidence:** Table 2 (scalar weight sweep) shows P3 optimal only at w_MPO > 0.997 — **demonstrates that trade-off is non-degenerate**

**Grade:** Falsifiable and supported

---

## Conclusion

**Causal claims:** Generally well-bounded. One HIGH confound (vocabulary benefit vs MCTS pruning interaction) should be linked.

**Negative result:** Honestly presented. Manuscript's explanation (tree convergence) is plausible but not uniquely determined. Alternate explanation (hyperparameter screening at 30-iter may not generalize to 1000-iter) not addressed.

**Overclaiming:** None detected. Language is cautious and appropriately bounded.

**Falsifiability:** Claims are testable and partially robustness-tested.

**Overall scientific integrity:** HIGH — honest negative result, bounded claims, no unfalsifiable assertions.
