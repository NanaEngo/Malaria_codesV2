# Edge-Case Review — P4 Pareto-MCTS Manuscript

**Date:** 2026-08-18  
**Reviewer:** Independent edge-case hunter (fresh context, read-only)  
**Mission:** Test boundary conditions, walk branching paths, check extremes

---

## Done-criteria status

| Criterion | Status |
|---|---|
| 1. Every "for all" claim checked at boundaries | **PASS** — 6 universal claims tested |
| 2. Every Methods branch point examined | **PASS** — 4 conditionals walked |
| 3. Every numerical range tested at min/max | **PASS** — 3 ranges checked |
| 4. Findings to file | **PASS** — this file |

---

## Executive summary

**Verdict:** **0 CRITICAL** + **1 HIGH** + **2 MEDIUM**. All boundary conditions hold or are appropriately qualified. One unhandled edge case in progressive widening formula at N=0.

---

## HIGH

### HIGH-1 — Progressive widening formula undefined at N=0

**Location:** `refined.tex:313`  
**Formula:** `max(5, k·N^α)` with k=1.0, α=0.5

**Edge case:** At tree root, N(s)=0 before first visit → N^0.5 = 0^0.5 = 0 → max(5,0) = 5 actions

**Test:** Formula is well-defined at N=0 (returns 5). **But** at N=1: max(5, 1.0·1^0.5) = max(5,1) = 5; at N=4: max(5, 1.0·2) = max(5,2) = 5; at N=25: max(5, 5) = 5; **progressive widening only activates at N > 25.**

**Impact:** For first 25 visits to any node, exactly 5 actions are tried. This is consistent behavior but manuscript says "5--20 out of 80 fragments" (`refined.tex:270`) — **the range 5--20 requires N ∈ [25, 400]**. At N=1000 (1 seed's full budget): max(5, 31.6) ≈ 31 actions, not 20.

**Grade:** HIGH — formula is correct but numerical range statement is approximate

**Recommendation:** Either state "typically 5--31 expanded actions" or show N-dependent range

---

## MEDIUM

### MEDIUM-1 — Hypervolume at degenerate reference point

**Location:** `refined.tex:327`  
**Claim:** "reference point r=1.1 in each active dimension, so that the reported value lies in [0, 1.1]^k"

**Edge test:** What if **all** front points have objective value exactly 1.0 (normalized)?  
→ Each point is distance (1.1 - 1.0) = 0.1 from reference  
→ HV > 0 still defined

**What if a point exceeds reference?** Text says objectives normalized to [0,1], so r=1.1 is strictly worse. **But if normalization fails:** dominating the reference point makes HV undefined in standard formulation.

**Manuscript safety:** Methods states "min--max normalised to [0,1]" so values cannot exceed 1.0 → r=1.1 is always worse → safe.

**Grade:** MEDIUM (documentation) — boundary is safe but not explicitly stated

---

### MEDIUM-2 — Paired t-test at seed count boundary

**Location:** `refined.tex:138` and `refined.tex:351`  
**Claim:** Paired t-test, df=19

**Edge:** What if two seeds produce identical rewards for both methods?  
→ Paired difference = 0 for that seed  
→ Still valid t-test (zero contributes to mean Δ)

**What if all 20 seeds identical?**  
→ SD of differences = 0 → t undefined (0/0)  
→ Manuscript shows SD > 0 for both methods → cannot occur

**Grade:** MEDIUM (robustness check) — test is valid under observed variance

---

## Boundary conditions PASS

### BC-1 — "For all 20 seeds" claims

**Tested:**
- Random highest mean: ✓ stated as mean comparison, not per-seed claim
- Greedy deterministic (SD=0): ✓ holds at both vocabulary sizes (Table 1, Table 4)
- MCTS vs Random: "19 of 20 seeds" explicitly stated (line 248) — ✓ boundary disclosed

**Status:** PASS — claims appropriately bounded

### BC-2 — Fragment vocabulary extremes

**Min:** Aromatic-only (SM Table S5) — tested and reported as significantly worse  
**Max:** Full 80-fragment (Table 4) — tested  
**Edge:** Zero fragments → trivial (benzene only), not tested (reasonable exclusion)  

**Status:** PASS — meaningful range covered

### BC-3 — Seed count sensitivity

**Claim:** n=20 seeds for main benchmark  
**Edge:** What if n=1? Methods states "20 independent seeds" throughout — no generalization to n=1 claimed  
**Statistical power:** Discussed at line 196 (selection ablation): "minimal detectable effect is 1.76 at 5 seeds and would remain 0.88 even at 20 seeds"

**Status:** PASS — seed count justified, power analysis present

### BC-4 — Hypervolume convention boundary

**Two conventions used:** front-internal (bound 1.4641) vs cross-method (bound 19.45)  
**Edge:** What if conventions mixed?  
→ Manuscript explicitly warns "not numerically comparable" in THREE places (line 217 caption, SM line 109, line 327)  
→ Anti-comparison boundary is **well-defended**

**Status:** PASS — boundary protection excellent

---

## Methods branch points examined

### Branch-1: Oracle conditional on activity term

**Location:** Line 336-342 Methods  
**Conditional:** v12 benchmark disables RRS/PNS; Pareto analysis disables activity

**Edge:** What if both disabled simultaneously?  
→ Not claimed to occur  
→ Documented as mutually exclusive modes

**Status:** Handled — modes are orthogonal analyses

### Branch-2: SYBA search-time vs display

**Location:** SM line 78-85  
**Conditional:** "SYBA was constant during search...evaluated separately for displayed front"

**Edge:** What if SYBA non-constant during search?  
→ Text explicitly disclaims: "not evidence that informative SYBA values guided the search" (SM line 81)

**Status:** Boundary explicitly documented

### Branch-3: Pareto dominance when objective constant

**Location:** Line 327  
**Rule:** "constant objectives excluded from dominance"

**Edge:** What if ALL objectives constant?  
→ Cannot occur (MPO varies by construction)  
→ Reasonable implicit assumption

**Status:** Safe under study design

### Branch-4: Statistical test selection

**Location:** Line 351  
**Rule:** "Paired t-tests...two planned head-to-head comparisons"

**Edge:** What if unpaired or three-way?  
→ Pairing documented as seed-matched (line 351: "seed integers...fixed")  
→ Third comparison (MCTS vs Greedy) not tested — **appropriately omitted** (Greedy deterministic, no variance to test)

**Status:** Correct test selection

---

## Numerical ranges tested

### Range-1: Reward values [0, 1]

**Claim:** Scalar reward is normalized combination  
**Observed:** Table 1 shows 0.4278--0.6856  
**Theoretical max:** 1.0 (all components maximized)  
**Theoretical min:** 0.0  

**Edge:** Is 0.4278 (Greedy) close to lower bound?  
→ No claim that 0.4278 is absolute minimum  
→ Consistent with poor but valid molecule

**Status:** Range reasonable

### Range-2: Hypervolume [0, 1.4641]

**Observed:** 1.2366 (front-internal), 13.85--18.99 (cross-method)  
**Bounds:** Documented (1.1^4 and 19.45)  
**Edge:** Both within stated bounds ✓

**Status:** PASS

### Range-3: Tanimoto diversity [0, 1]

**Observed:** SM Table S3 shows 0.0000 (Greedy) to 0.8046 (Random)  
**Edge:** Perfect dissimilarity (1.0) not observed — reasonable (20 antimalarials share core features)  
**Zero dissimilarity:** Greedy only — consistent with deterministic collapse

**Status:** PASS

---

## Conclusion

One HIGH edge case: progressive widening "5--20" range statement is approximate (actual range at N=1000 is 5--31). Two MEDIUM documentation items. All tested boundaries hold. No unhandled critical edge cases detected.
