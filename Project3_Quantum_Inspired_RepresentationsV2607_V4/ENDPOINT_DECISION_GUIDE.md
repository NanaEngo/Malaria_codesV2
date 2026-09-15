# Reviewer 1 Endpoint-Specific Request: Decision Guide

**Date:** 2026-09-15  
**Context:** P3 V2609 JCAMD resubmission

## What Reviewer 1 Actually Requested

> "I would advise the authors to benchmark their descriptors against EC fingerprints **across many ChEMBL endpoints** and **check for which of them (if there is any!) their descriptors can give you a decent model and the classical ones cannot**. [...] If there is at least **ONE** target for which you can get a decent model with your descriptors but you cannot with classical ones, then your descriptors are good."

**Key Requirements:**
1. **Multiple separate endpoints** (not one pooled dataset)
2. **One assay per endpoint** (homogeneous: same target, same measurement type)
3. **Per-endpoint comparison** (descriptor vs ECFP4 for each endpoint separately)
4. **Success criterion:** At least ONE endpoint where descriptor > ECFP4

---

## Your Three Options

### Option 1: Implement Endpoint-Specific Analysis ✓ (Addresses Request)

**What to Do:**
1. Run audit script (provided: `scripts/p3_chembl_endpoint_audit.py`)
2. If viable endpoints exist (n ≥ 5-10), proceed with analysis
3. Implement per-endpoint benchmark (3-5 days of work)
4. Update manuscript/SI with results tables
5. Resubmit with completed analysis

**Pros:**
- ✓ Directly addresses Reviewer 1's central request
- ✓ Could discover endpoint-specific advantages
- ✓ Strengthens scientific contribution
- ✓ Shows responsiveness to reviewer feedback

**Cons:**
- ✗ Requires 3-5 days of additional work
- ✗ May still show ECFP4 > all descriptors (honest negative)
- ✗ Risk of finding insufficient viable endpoints
- ✗ Delays resubmission

**When to Choose:** If you have time and want to fully satisfy reviewer request

---

### Option 2: Maintain Narrow Scope + Honest Acknowledgment ⚠️ (Current State)

**What to Do:**
1. Keep current manuscript as-is
2. Response to Reviewers honestly states: "endpoint-specific analysis not implemented"
3. Frame as computational-label benchmark + exploratory transfer
4. Submit and let editor/reviewer decide if scope is acceptable

**Pros:**
- ✓ Can submit immediately (no additional analysis)
- ✓ Scientifically honest (no false claims)
- ✓ Existing analysis is rigorous within its scope
- ✓ Honest-negative conclusion is valuable

**Cons:**
- ✗ Does NOT address Reviewer 1's central request
- ✗ Risk of rejection or major revision request
- ✗ Reviewer may insist on endpoint-specific analysis

**When to Choose:** If time-constrained and willing to accept revision risk

---

### Option 3: Audit First, Then Decide (Recommended) 📋

**What to Do:**
1. **TODAY:** Run audit script to see if viable endpoints exist
2. **Decision point:**
   - If ≥5 viable endpoints → Proceed with Option 1
   - If 1-4 viable endpoints → Decide based on time constraints
   - If 0 viable endpoints → Must use Option 2 (analysis not feasible)

**Pros:**
- ✓ Data-driven decision (don't commit blind)
- ✓ Low cost to run audit (1-2 hours)
- ✓ Know feasibility before committing effort
- ✓ Can explain to reviewer if analysis proves infeasible

**Cons:**
- ✗ Adds 1 day before final decision
- ✗ May reveal uncomfortable truth (analysis is/isn't feasible)

**When to Choose:** THIS IS THE RECOMMENDED APPROACH

---

## Implementation Timeline (If Proceeding with Option 1)

### Day 1: Audit Phase
- **Morning:** Run `p3_chembl_endpoint_audit.py`
- **Afternoon:** Review results, select 5-10 best endpoints
- **Output:** Endpoint list with assay_ids, targets, n, balance

### Day 2-3: Analysis Phase
- Retrieve full datasets for selected endpoints
- Apply descriptor pipeline (ECFP4, TFP, TNE, QKS, hybrid)
- Run scaffold-grouped CV per endpoint
- Compute statistics (AUC, CI, p-values, multiplicity correction)
- **Output:** `results/p3_chembl_endpoint_benchmark_v1/` with per-endpoint CSVs

### Day 4: Integration Phase
- Create results table (Endpoint | Target | n | AUC_ECFP4 | AUC_TFP | AUC_TNE | AUC_QKS | p-value)
- Add table to SI as new section
- Update Response to Reviewers with completed analysis
- Recompile manuscripts
- **Output:** Updated manuscript package

### Day 5: Verification & Submission
- Independent verification of results
- Final proofreading
- Submit to journal

**Total Effort:** 3-5 full days

---

## Recommended Script to Run NOW

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607_V4

# Activate environment with chembl_webresource_client
conda activate malaria_md  # or your P3 environment

# Run audit (takes 10-30 minutes)
python scripts/p3_chembl_endpoint_audit.py

# Review output
cat results/p3_chembl_endpoint_audit.json
```

**The audit will tell you:**
- How many viable endpoints exist
- Their characteristics (target, n, balance)
- Whether Option 1 is feasible

---

## Decision Matrix

| Audit Result | Time Available | Recommended Action |
|--------------|----------------|-------------------|
| ≥10 endpoints | ≥5 days | **Option 1** (full implementation) |
| 5-9 endpoints | ≥3 days | **Option 1** (focused implementation) |
| 1-4 endpoints | ≥3 days | **Option 1** (limited implementation) + caveat |
| 1-4 endpoints | <3 days | **Option 2** (narrow scope) |
| 0 endpoints | Any | **Option 2** (analysis infeasible, document why) |

---

## What Each Option Means for Resubmission

### If Option 1 (Endpoint-Specific Analysis):

**Response to Reviewer 1:**
> "We have implemented endpoint-specific ChEMBL benchmarking as requested. We identified [N] homogeneous endpoints (one assay_id, one target, one measurement type per endpoint) meeting our frozen protocol criteria (n≥500, both classes≥100). Per-endpoint results are presented in SI Table SX. [Outcome: ECFP4 remained strongest across all endpoints / Descriptor X outperformed ECFP4 on Y endpoints]. This analysis directly addresses your request to test whether any descriptor can outperform classical fingerprints on at least one experimental endpoint."

**Manuscript Changes:**
- Add SI section: "Endpoint-specific ChEMBL benchmark"
- Add SI table: Per-endpoint results
- Update main text Discussion with endpoint findings
- Update abstract if results change conclusions

---

### If Option 2 (Narrow Scope):

**Response to Reviewer 1:**
> "We acknowledge that the requested endpoint-specific ChEMBL benchmark (one assay_id, one target, one measurement type per endpoint) was not implemented in this revision. Our current ChEMBL analysis (n=22,447) pools multiple P. falciparum assays under a single IC50 threshold and represents an exploratory label-source-shift analysis only. Implementing homogeneous endpoint-level benchmarking would require retrieving individual assay-level data, applying within-assay active/inactive definitions, and reporting descriptor performance per assay—a substantive new analysis beyond the scope of this revision. We have explicitly limited the ChEMBL analysis to exploratory transfer and make no claim to address the endpoint-specific requirement."

**Manuscript Changes:**
- None required (already done in current version)
- Maintain honest scope statements
- Keep pooled ChEMBL as exploratory only

**Risk:** Reviewer/editor may require endpoint analysis for acceptance

---

## My Recommendation

**Run the audit script TODAY.** It costs 1-2 hours and tells you whether Option 1 is even feasible.

**Then decide based on audit results:**

1. **If audit shows ≥5 viable endpoints AND you have 3-5 days:**
   → **Do the endpoint-specific analysis** (Option 1)
   → This fully satisfies reviewer request
   → Worth the investment for clean acceptance

2. **If audit shows 0-4 endpoints OR you lack time:**
   → **Submit with narrow scope** (Option 2)
   → Document why in Response (infeasible or time-limited)
   → Let editor/reviewer decide if acceptable

**Why this is the right approach:**
- ✓ Data-driven decision
- ✓ No wasted effort (audit is quick)
- ✓ Honest with reviewer about feasibility
- ✓ Maximizes acceptance probability given constraints

---

## Questions to Consider

Before running audit, ask yourself:

1. **Time:** Do you have 3-5 days available for additional analysis?
2. **Priority:** Is P3 acceptance time-critical, or can it wait?
3. **Risk tolerance:** Willing to risk revision request if you don't do endpoint analysis?
4. **Scientific value:** Would endpoint-specific results strengthen the paper beyond reviewer requirements?

**If answers are mostly "yes"** → Run audit, likely proceed with Option 1  
**If answers are mostly "no"** → Option 2 (narrow scope) is reasonable

---

## Next Immediate Action

```bash
# 1. Run the audit (provided script)
cd Project3_Quantum_Inspired_RepresentationsV2607_V4
python scripts/p3_chembl_endpoint_audit.py

# 2. Review results
less results/p3_chembl_endpoint_audit.json

# 3. Make informed decision based on:
#    - Number of viable endpoints found
#    - Your available time
#    - Risk tolerance for revision
```

**Expected audit runtime:** 10-30 minutes (depends on ChEMBL API response times)

**You'll then know exactly what's feasible and can make a data-driven decision.**
