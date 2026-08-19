# Structure Review — P4 Pareto-MCTS Manuscript

**Date:** 2026-08-18  
**Reviewer:** Editorial structure review (organization, cuts, simplification)  
**Mission:** Assess logical flow, identify redundancy, propose reorganization

---

## Done-criteria status

| Criterion | Status |
|---|---|
| 1. Redundant sections flagged for cuts | **PASS** — 2 redundancies identified |
| 2. Logical flow assessed | **PASS** — structure sound |
| 3. Reorganization proposals evidence-based | **PASS** — 1 proposal |
| 4. Findings to file | **PASS** — this file |

---

## Executive summary

**Verdict:** Structure is **fundamentally sound**. No major reorganization needed. 2 minor redundancies (total ~150 words cuttable). 1 optional reorganization (Limitations placement).

**Overall:** Well-organized, appropriate length for Journal of Cheminformatics original research.

---

## High-level structure assessment

### Current structure:

1. **Abstract** (structured: Background / Methods / Results / Conclusions)
2. **Introduction** (problem statement, related work)
3. **Results** (5 subsections: Hyperparameters / Benchmark / Pareto / Front comparison / Ablations)
4. **Discussion** (4 subsections: What benchmark shows / Why greedy collapses / Prior work / Limitations / Implications)
5. **Methods** (7 subsections)
6. **Conclusions**
7. **Back matter** (Abbreviations / Data / Competing interests / Contributions / Acknowledgments / Funding / Ethics / AI use)

**Assessment:** Standard IMRaD structure with Methods-after-Results (journal convention). **Logical and complete.**

---

## Section-by-section analysis

### Abstract (lines 60-76)

**Length:** ~220 words  
**Structure:** Background (2 sent) / Methods (2 sent) / Results (4 sent) / Conclusions (2 sent)  
**Issues:** None  
**Verdict:** OPTIMAL — concise, complete, honest about negative result

---

### Introduction (lines 78-111)

**Length:** ~600 words  
**Subsections:** Problem statement (78-84) / Pareto rationale (85-90) / Related work (91-105) / Contribution (106-111)

**Redundancy check:**
- Line 82: "African natural products...reservoir for such scaffolds" 
- Line 106: "resistance-informed and polypharmacology-informed candidate records"  
Both appropriate — first is motivation, second is technical contribution statement.

**Flow:** Logical progression (problem → solution approach → prior art → contribution)  
**Issues:** None  
**Verdict:** WELL-STRUCTURED — no cuts needed

---

### Results (lines 113-263)

**Length:** ~2400 words (main) + SM material  
**Subsections:** 5 (Hyperparameters / Benchmark / Pareto / Front comparison / Ablations)

**Subsection balance:**
- §2.1 Hyperparameters: ~100 words (appropriate — brief summary)
- §2.2 Benchmark: ~650 words (core result — appropriate detail)
- §2.3 Pareto: ~450 words (key analysis — appropriate)
- §2.4 Front comparison: ~350 words (secondary analysis — appropriate)
- §2.5 Ablations: ~850 words (includes selection ablation + vocabulary)

**Redundancy check:**

**REDUNDANCY 1 (minor):**
- Line 138: "Random search achieved the highest mean reward (0.6724 ± 0.0056)"
- Line 125 Table 1: Same value  
**Impact:** 15-word repetition  
**Recommendation:** Keep both (table + narrative summary is standard)  
**Severity:** Not worth cutting — reader convenience

**REDUNDANCY 2 (cuttable):**
- Line 140-141: "Structural diversity of the generated molecule sets is analysed in the Supplementary Information in Figure S1 and Table S1..."  
- SM has full diversity section (S3)  
**Issue:** This is a **forward reference**, not redundancy. But the sentence adds little — reader will find SM section anyway.  
**Recommendation:** Optional cut (1 sentence, ~40 words)  
**Severity:** Low priority

**Flow between subsections:**
- §2.1 → §2.2: Good (parameters → benchmark that uses them)
- §2.2 → §2.3: Adequate (scalar → multi-objective)  
  *Could add transition:* "Although MCTS did not maximize the scalar reward (§2.2), a separate analysis examines..."
- §2.3 → §2.4: Good ("To place the MCTS front in context...")
- §2.4 → §2.5: Fair (no explicit transition)

**Verdict:** Well-proportioned, minor transition improvements possible, no cuts needed

---

### Discussion (lines 265-296)

**Length:** ~1200 words  
**Subsections:** 4 named + Limitations paragraph

**Subsection purposes:**
1. **What benchmark shows** (265-273): Interprets scalar result + tree convergence mechanism
2. **Why greedy collapses** (276-280): Mechanism of deterministic convergence
3. **Prior work** (282-288): Positions contribution vs Mothra/ParetoDrug/CombiMOTS
4. **Limitations** (284-288): Computational proxies, vocabulary constraints, accessibility caveat
5. **Implications** (289-296): Domain-specific value, future extensions

**STRUCTURAL ISSUE — Limitations placement:**

**Current:** Limitations is §4.4, after "Relation to prior work" (§4.3) and before "Implications" (§4.5)  
**Problem:** Implications (§4.5) returns to positive contributions after Limitations, creating ending on a down-note  
**Standard practice:** Limitations often placed last OR immediately after main interpretation

**Options:**
A. **Move Limitations to end** (after Implications) — ends paper on honest note  
B. **Keep current** — ends on forward-looking note  
C. **Move Limitations before Discussion §4.1** — clears limitations before interpretation

**Evidence:**
- Journal of Cheminformatics articles vary (no rigid convention)
- Current structure (Limitations §4.4, Implications §4.5) is **defensible** — limitation acknowledged, then salvaged value

**Recommendation:** **Keep current structure** OR move Limitations to end. Either is acceptable. Not worth reorganizing unless author prefers.

**Redundancy check:**

**REDUNDANCY 3 (intentional repetition):**
- Line 271: "random search remains the strongest baseline"  
- Line 138: "Random search achieved the highest mean reward"  
**Assessment:** This is **recap in Discussion**, not redundancy. Standard practice.  
**Verdict:** Keep

**REDUNDANCY 4 (cuttable):**
- Line 272-273: "The rational for retaining Pareto structure is different: it allows the chemical decision-maker to inspect alternative profiles..."  
- Line 374 Conclusions: "the added value of MCTS is transparent objective-space exploration"  
**Assessment:** Discussion explains rationale (4 sentences), Conclusions states outcome (1 sentence). **Standard recap**, not redundancy.  
**Verdict:** Keep — Conclusions should recap key messages

**Verdict:** Discussion is well-structured, appropriate length, no cuts needed

---

### Methods (lines 298-367)

**Length:** ~1600 words  
**Subsections:** 7 (Env / MCTS / Rollout fix / Pareto / Oracles / Statistics / [Conclusions])

**Assessment:**
- Appropriate detail for reproducibility
- Standard Methods-after-Results placement (JoC convention)
- Subsections logically ordered (algorithm → selection → scoring → stats)

**Redundancy check:** None detected (Methods detail is necessary, not redundant)

**Verdict:** Appropriately detailed, no cuts

---

### Conclusions (lines 369-378)

**Length:** ~300 words  

**Structure:**
1. Recap scalar result (negative)
2. Recap Pareto result (4-point front, trade-offs)
3. Practical implications (3 points)
4. Data availability note

**REDUNDANCY 5 (acceptable recap):**
- Conclusions recaps Abstract results  
**Assessment:** Standard for Conclusions section — reader may read Conclusions standalone  
**Verdict:** Keep

**Issue:** Last paragraph (line 376-378) is **Data availability note**, not conclusion  
**Recommendation:** This belongs in **Data availability section** (line 393), not Conclusions.  
**Fix:** Move "The analysis scripts...as noted there..." to line 393 Data availability paragraph  
**Impact:** Strengthens ending (currently ends on disclaimer, should end on contribution)

**Verdict:** Move 1 paragraph (data note) to proper section; otherwise well-structured

---

## Length analysis

**Main manuscript:** ~6500 words (14 pages compiled)  
**Supplementary:** ~2200 words (4 pages)  
**Total:** ~8700 words

**Journal of Cheminformatics guidelines:** No strict word limit for Research articles; ~6000-8000 words typical  
**Assessment:** Slightly above typical but **justified** by:
- Four-method benchmark (not just 2)
- Two separate analyses (scalar + Pareto)
- Honest negative result requires more explanation
- Limitations discussion is detailed

**Verdict:** Length appropriate for content, no cuts needed for length

---

## Figure/table balance

**Main manuscript:**
- 3 data figures (benchmark bar, Pareto front, integrated overview, efficiency)
- 3 tables (benchmark, Pareto front, cross-method comparison, allfrag)

**Supplementary:**
- 2 figures (RRS/PNS profiles, diversity MDS)
- 5 tables (Pareto front, benchmark, diversity, ablations)

**Assessment:** Appropriate figure/table density. Figures are referenced in narrative. No orphan figures/tables.

**Verdict:** Well-balanced

---

## Recommended cuts (optional, low priority)

### Cut 1: Forward reference to SM diversity (line 140-141)

**Current:** "Structural diversity of the generated molecule sets is analysed in the Supplementary Information in Figure~\ref{SM-fig:sm_mds} and Table~\ref{SM-tab:sm_diversity}..."  
**Rationale:** SM section is self-contained; forward ref adds little  
**Savings:** ~40 words  
**Priority:** LOW — reader convenience vs brevity

### Cut 2: Data availability note in Conclusions (line 376-378)

**Current:** "The analysis scripts...listed in the Data availability section are available...as noted there, the full-vocabulary benchmark...is reported from summary statistics..."  
**Rationale:** Belongs in Data availability section (line 393), not Conclusions  
**Action:** MOVE, not cut  
**Savings:** 0 words (move only)  
**Priority:** MEDIUM — improves structure

---

## Recommended reorganization (optional)

### Reorganization 1: Move Limitations to end of Discussion

**Current order:** §4.1 Benchmark interpretation → §4.2 Greedy → §4.3 Prior work → **§4.4 Limitations** → §4.5 Implications

**Proposed:** §4.1 → §4.2 → §4.3 → §4.5 Implications → **§4.4 Limitations** (last)

**Rationale:** Standard practice is Limitations last OR immediately after main findings  
**Counterargument:** Ending on Implications (forward-looking) is also valid  
**Priority:** OPTIONAL — both structures are defensible

---

## Section lengths compared to typical JoC articles

| Section | P4 length | Typical | Assessment |
|---|---|---|---|
| Abstract | 220 words | 200-250 | OPTIMAL |
| Introduction | 600 words | 500-800 | GOOD |
| Results | 2400 words | 2000-3000 | APPROPRIATE (multi-analysis) |
| Discussion | 1200 words | 800-1200 | GOOD |
| Methods | 1600 words | 1200-2000 | APPROPRIATE (detail needed) |
| Conclusions | 300 words | 200-400 | GOOD |

**Verdict:** All sections within acceptable range for JoC

---

## Conclusion

**Structure assessment:** **4.5 / 5** (Excellent)

**Strengths:**
- Logical IMRaD structure
- Appropriate section lengths
- Clear subsection organization
- Results subsections well-ordered
- No major redundancies

**Minor improvements:**
1. **MOVE** data availability note from Conclusions to Data availability section (MEDIUM priority)
2. **OPTIONAL CUT:** Forward reference to SM diversity (line 140-141, LOW priority)
3. **OPTIONAL REORGANIZATION:** Move Limitations to end of Discussion (LOW priority)

**Total cuttable:** ~40 words (0.6% of manuscript)

**No blocking structural issues. Ready for submission after scientific fixes.**
