# P1 ← P2 Reusable Outputs: What to Copy vs Re-run

**Date**: 2026-09-09  
**Purpose**: Identify P2 outputs that can be directly reused for P1 vs what needs P1-specific computation  
**Key Insight**: **P1 and P2 share the exact same 17-compound cohort (Set C)** — massive reuse opportunity

---

## Executive Summary

**Critical Discovery**: P1 Set A (17 compounds) = P2 Set C (17 compounds) — **identical cohort verified by SMILES**

This means:
- ✅ **P2's statistical framework outputs are directly applicable** (correlations, bootstrap CI, power analysis)
- ✅ **P2's multi-seed results for PP-01 are P1-relevant** (PP-01 is a P1 compound)
- ✅ **P2's ACSI/PNS calculations are P1-ready** (same compounds)
- ⚠️ **P2's docking scores need adaptation** (different grid boxes, different mutations)

**Time Savings**: Instead of re-running statistical framework (5 days), we copy P2 outputs (1 hour)

---

## Cohort Identity Verification

### P1 Set A (from V7)
```
PP-01, PP-02, PP-03, ..., PP-17
Total: 17 compounds
Selection: MPO ≥ 0.70, SYBA > 0, SI > 10
Source: P1 DAR Table 2
```

### P2 Set C
```
PP-01, PP-02, PP-03, ..., PP-17
Total: 17 compounds
Selection: MPO ≥ 0.70, SYBA > 0, SI > 10
Source: P2 DAR §2
```

### Verification
From P2 DAR:
> "A cohort audit confirmed exact identity for all 17 PP-01--PP-17 SMILES; the overlap and shared workflow provenance preclude independent-replication claims."

**Conclusion**: **100% cohort overlap** — P2 computational outputs on Set C are P1-relevant

---

## Category 1: DIRECTLY REUSABLE (Copy, Don't Re-run)

### 1.1 Statistical Framework Outputs ✅

**P2 File**: `results/cross_metric_statistical_audit.csv`

**Contents**:
- 100,000-permutation p-values
- 10,000-bootstrap 95% CI
- Bonferroni-corrected p-values
- Both n=12 (complete two-target) and n=17 (available-target) analyses

**P1 Use**: 
- **Copy directly** to support Table S6 correlations
- **Extract method** from P2 for missing N_fav vs RRS correlation
- **Reuse bootstrap framework** without re-running

**Reusable Values** (from P2):
```csv
Analysis: complete_two_target_12
PNS_vs_RRS: ρ=-0.210, p=0.514, CI=[-0.758, 0.543]
ACSI_vs_RRS: ρ=-0.406, p=0.192, CI=[-0.892, 0.286]
RRS_vs_WT_anchor: ρ=-0.166, p=0.604, CI=[-0.730, 0.593]

Analysis: available_17
PNS_vs_RRS: ρ=-0.559, p=0.022, CI=[-0.789, -0.135]
ACSI_vs_RRS: ρ=-0.132, p=0.612, CI=[-0.693, 0.442]
```

**P1 Action**:
```bash
# Copy P2 statistical outputs
cp P2/results/cross_metric_statistical_audit.csv \
   P1/results/p2_statistical_reference.csv

# Copy manifest
cp P2/results/p2_rigorous_audit_manifest.json \
   P1/results/p2_statistical_reference_manifest.json
```

**Time Saved**: 5 days (don't need to re-run 100k permutations)

---

### 1.2 ACSI Scores ✅

**P2 File**: `results/c_acsi_scores.csv`

**Contents**:
- ACSI scores for all 17 PP-01...PP-17 compounds
- Component breakdown (D_DrugBank, D_ANPDB, fsp3, NPL)
- Normalized and raw values

**P1 Use**:
- **Copy directly** for SI Table S_NEW5 (ACSI column)
- **Extract formulas** from P2 script for Methods §2.4.2
- **Reference values** for correlation analysis

**P1 Action**:
```bash
cp P2/results/c_acsi_scores.csv P1/results/p1_acsi_from_p2.csv
```

**Time Saved**: 1 day (ACSI computation already done)

---

### 1.3 PNS Scores ✅

**P2 File**: `results/c_pns_ranking.csv`

**Contents**:
- PNS scores for all 17 compounds
- Imputation sensitivity (zero-to-double PfCRT centrality)
- Rank stability analysis

**P1 Use**:
- **Copy directly** for SI Table S_NEW5 (PNS column)
- **Extract formula** from P2 for Methods §2.4.1
- **Reference imputation sensitivity** for robustness

**P2 Bonus**: Already has STRING threshold sensitivity (400/700/900)
```
results/string_threshold_sensitivity_20260829/
├── summary.json
└── pns_ranking_threshold_sensitivity.csv
```

**P1 Action**:
```bash
cp P2/results/c_pns_ranking.csv P1/results/p1_pns_from_p2.csv
cp -r P2/results/string_threshold_sensitivity_20260829 \
      P1/results/p1_string_sensitivity_from_p2/
```

**Time Saved**: 1 day (PNS + sensitivity already computed)

---

### 1.4 ACSI Weight Sensitivity ✅

**P2 Files**:
- `results/c_acsi_weight_sensitivity.csv`
- `results/c_acsi_weight_sensitivity.json`

**Contents**:
- 8 perturbation scenarios (±20% per weight)
- Spearman ρ vs baseline: 0.9167–0.9804
- Top-5 Jaccard overlap: 0.6667–1.0000

**P1 Use**:
- **Copy directly** to support Methods caveat
- **Reference in Discussion** for weight robustness claim
- **No need to re-run** (same cohort, same weights)

**P1 Action**:
```bash
cp P2/results/c_acsi_weight_sensitivity.* P1/results/p1_acsi_sensitivity_from_p2.*
```

**Time Saved**: 2 days (sensitivity analysis already done)

---

### 1.5 Multi-Seed PP-01 Results ✅

**P2 File**: `results/pp01_docking_20260829/multiseed_canonical_summary.json`

**Contents**:
- PP-01 × 2 WT targets × 5 seeds
- PfDHFR: mean −7.499 ± 0.021 kcal/mol, canonical −7.500 inside spread
- PfCRT: mean −9.250 ± 0.015 kcal/mol, canonical −9.300 within 0.05
- **Uses P1-V2 canonical grids** (critical!)

**P1 Use**:
- **Copy directly** as proof-of-concept for multi-seed protocol
- **Reference in Methods** "seed sensitivity was assessed for candidate PP-01 (representative)"
- **Extract protocol** from manifest

**P1 Action**:
```bash
# Copy PP-01 multi-seed results
cp P2/results/pp01_docking_20260829/multiseed_canonical_summary.json \
   P1/results/p1_pp01_multiseed_from_p2.json

# Extract protocol
grep "protocol" P2/results/pp01_docking_20260829/multiseed_canonical_summary.json \
  > P1/results/p1_multiseed_protocol_reference.txt
```

**Insight from P2**: 
> "Mode-1 affinity is reproducible across seeds to within 0.05 kcal/mol on both WT targets"

**P1 Benefit**: **Directly addresses R2 Major #9** for at least one compound without re-running

**Time Saved**: 2 days (for PP-01, which is a priority compound)

---

### 1.6 Power Analysis Function ✅

**P2 Location**: `P2/scripts/p2_rigorous_audit.py` (lines ~350–380)

**Function**:
```python
def compute_power(n: int, rho: float, alpha: float = 0.017) -> float:
    """Post-hoc power for Spearman correlation test."""
    from scipy.stats import norm
    z_alpha = norm.ppf(1 - alpha / 2)
    # Fisher Z-transformation
    z_beta = 0.5 * np.log((1 + rho) / (1 - rho)) * np.sqrt(n - 3)
    power = 1 - norm.cdf(z_alpha - z_beta)
    return power
```

**P1 Use**:
- **Copy function** directly (no modification needed)
- **Compute for P1**: n=17, ρ=0.5, α=0.017 → power=0.37 (matches reviewer)

**P1 Action**:
```python
# In p1_statistical_audit.py
from p2_rigorous_audit import compute_power  # or copy function

# Compute for reviewer's scenario
power = compute_power(n=17, rho=0.5, alpha=0.017)
print(f"Power to detect ρ=0.5 at n=17, α=0.017: {power:.2f}")
# Output: 0.37 (matches reviewer's calculation)
```

**Time Saved**: 3 hours (don't need to derive formula)

---

### 1.7 Honest-Negative Reporting Patterns ✅

**P2 Patterns** (from DAR):
- Status labels: `COMPUTED`, `NOT_COMPUTED`, `EXPLORATORY`, `FAILED_NUMERICAL_QC`
- Boundary statements: "computational record, not biochemical affinity"
- Limitations: upfront in abstract, detailed in methods
- Null distribution: explicit quantification of noise floor

**P1 Use**:
- **Copy language patterns** for manuscript revision
- **Adapt status labels** for P1 results
- **Reference framing** for RRS > 100% interpretation

**Examples to Reuse**:
```
From P2 Abstract:
"This computational analysis does not establish biochemical affinity, 
target engagement, or resistance phenotype."

From P2 Limitations:
"10 ns measures local geometry, not affinity; this does NOT demonstrate resistance."

From P2 RRS:
"RRS is a hypothesis about relative mutant sensitivity, not a measurement 
of mutant free-energy difference."
```

**P1 Action**: Copy patterns into manuscript drafts

**Time Saved**: Qualitative (strengthens manuscript integrity)

---

## Category 2: ADAPT & EXTEND (Modify P2 outputs for P1)

### 2.1 RRS Classification ⚠️

**P2 File**: `results/c_rrs_classification.csv`

**P2 Mutations**:
- PfDHFR: N51I, C59R, S108N, I164L (same as P1 ✅)
- PfCRT: K76T, K76A (same as P1 ✅)

**P2 Grid Boxes**: Different from P1 (P2 uses Set-C-specific grids)

**P1 Need**: 
- **Re-dock with P1 grids** (T1.1, T1.2, T1.3)
- **Reuse RRS calculation logic** from P2
- **Reuse class definitions** (A*/A/B/C/D boundaries)

**P1 Action**:
```python
# Copy RRS calculation function from P2
from p2_rigorous_audit import classify_rrs, compute_rrs

# Apply to P1 docking scores (after re-docking)
p1_rrs = compute_rrs(
    wt_scores=p1_wt_docking_scores,
    mut_scores=p1_mut_docking_scores,
    threshold=5.0,  # Same as P2
)

# Classify using P2's logic
p1_classes = [classify_rrs(values, wt_anchor) for values in p1_rrs]
```

**What to Reuse**: Function logic, class definitions, null distribution concept  
**What to Re-run**: Docking with P1-specific grids

---

### 2.2 N_fav Calculation ⚠️

**P2 File**: `results/c_rrs_classification.csv` (has N_fav column)

**P2 Approach**: Rank-based within-target favorability (after reviewer feedback)

**P1 Need**:
- **Compute N_fav for P1 docking scores** (after re-docking)
- **Reuse rank-based logic** from P2 (addresses R2 Major #2)
- **Compute correlation with RRS** (addresses R2 Major #1)

**P1 Action**:
```python
# Copy rank-based N_fav function from P2
def compute_nfav_rank_based(scores_matrix, percentile=50):
    """P2-style within-target rank-based favorability."""
    n_compounds, n_targets = scores_matrix.shape
    n_fav = np.zeros(n_compounds)
    
    for target_idx in range(n_targets):
        scores = scores_matrix[:, target_idx]
        threshold = np.percentile(scores, percentile)
        favorable = scores <= threshold  # More negative = better
        n_fav += favorable
    
    return n_fav

# Apply to P1 scores
p1_nfav = compute_nfav_rank_based(p1_docking_matrix, percentile=50)
```

**What to Reuse**: Rank-based logic, percentile approach  
**What to Re-run**: Calculation on P1 docking scores

---

### 2.3 Null Distribution Protocol ⚠️

**P2 Protocol** (from DAR §4.0):
> "Pseudo-mutant wild-type receptors: wild-type structures processed through 
> the mutant preparation pipeline but with no mutation applied."

**P2 Output**: Not explicitly in P2 results (described in text)

**P1 Need**:
- **Implement P2's protocol** for P1 receptors
- **Generate P1-specific null distribution** (T1.3.2)
- **Reuse statistical analysis** from P2

**P1 Action**:
```python
# Follow P2's protocol
def generate_null_rrs(compounds, wt_receptor, pseudo_mut_receptor):
    """P2-style null distribution generation."""
    null_rrs_values = []
    
    for compound in compounds:
        score_wt = dock(compound, wt_receptor)
        score_pseudo = dock(compound, pseudo_mut_receptor)
        null_rrs = (score_pseudo / score_wt) * 100
        null_rrs_values.append(null_rrs)
    
    null_stats = {
        "mean": np.mean(null_rrs_values),
        "std": np.std(null_rrs_values),
        "ci_95": np.percentile(null_rrs_values, [2.5, 97.5]),
    }
    return null_stats

# Run for P1 receptors
p1_null = generate_null_rrs(p1_compounds, p1_wt_receptors, p1_pseudo_mut)
```

**What to Reuse**: Protocol concept, statistical analysis  
**What to Re-run**: P1-specific docking (68 poses)

---

## Category 3: SCRIPTS ONLY (Copy code, run on P1 data)

### 3.1 Multi-Seed Launcher Script ✅

**P2 File**: `scripts/p2_targeted_redock_multiseed.sh`

**Reusability**: 100% — just change input paths

**P1 Action**:
```bash
# Copy script
cp P2/scripts/p2_targeted_redock_multiseed.sh \
   P1/scripts/p1_multiseed_validation.sh

# Adapt paths in script
sed -i 's|P2|P1|g' P1/scripts/p1_multiseed_validation.sh
sed -i 's|Set-C|Set-A|g' P1/scripts/p1_multiseed_validation.sh

# Run for P1 compounds
export P1_COMPOUND=PP-02
export P1_TARGET=PfDHFR
export P1_CONFIRM=APPROVED
sbatch P1/scripts/p1_multiseed_validation.sh
```

**Time Saved**: 11 days (script development)

---

### 3.2 GNINA Rescoring Script ✅

**P2 File**: `scripts/p2_gnina_consensus_rescore.py`

**Reusability**: 90% — change input directories

**P1 Action**:
```bash
# Copy script
cp P2/scripts/p2_gnina_consensus_rescore.py \
   P1/scripts/p1_gnina_rescore.py

# Run on P1 DEKOIS results
python P1/scripts/p1_gnina_rescore.py \
  --poses P1/results/dekois_apo_poses/ \
  --receptor P1/data/receptors/pfdhfr_7f3y_apo.pdbqt \
  --output P1/results/dekois_gnina/
```

**Time Saved**: 5 days (rescoring implementation)

---

### 3.3 Statistical Audit Script ✅

**P2 File**: `scripts/p2_rigorous_audit.py`

**Reusability**: 80% — adapt data loading, keep analysis

**P1 Action**:
```python
# Copy script
cp P2/scripts/p2_rigorous_audit.py \
   P1/scripts/p1_statistical_audit.py

# Modify data loading section (lines ~100-150)
# Change: "results/c_rrs_classification.csv" → "results/p1_table1.csv"
# Change: column names to match P1 structure
# Keep: all statistical functions (100k perm, 10k bootstrap, power)

# Run
python P1/scripts/p1_statistical_audit.py --seed 42
```

**Time Saved**: 5 days (statistical framework)

---

### 3.4 Preparation Manifest Script ✅

**P2 File**: `scripts/md_forcefield_manifest.py`

**Reusability**: 100% — generic provenance tracking

**P1 Action**:
```bash
cp P2/scripts/md_forcefield_manifest.py \
   P1/scripts/p1_preparation_manifest.py

# Run for each P1 receptor
python P1/scripts/p1_preparation_manifest.py \
  --receptor P1/data/receptors/pfdhfr_7f3y_wt.pdb \
  --output P1/results/manifests/pfdhfr_wt_manifest.json
```

**Time Saved**: 2 days (manifest system development)

---

## Summary: Copy vs Re-run Decision Matrix

| Item | P2 Output | P1 Action | Time Saved | Priority |
|------|-----------|-----------|------------|----------|
| **Statistical framework** | `cross_metric_statistical_audit.csv` | **COPY** + extend for N_fav | 5 days | P0 |
| **ACSI scores** | `c_acsi_scores.csv` | **COPY** directly | 1 day | P0 |
| **PNS scores** | `c_pns_ranking.csv` | **COPY** directly | 1 day | P0 |
| **ACSI sensitivity** | `c_acsi_weight_sensitivity.*` | **COPY** directly | 2 days | P1 |
| **STRING sensitivity** | `string_threshold_sensitivity_20260829/` | **COPY** directly | 1 day | P2 |
| **PP-01 multi-seed** | `pp01_docking_20260829/` | **COPY** as reference | 2 days | P1 |
| **Power analysis function** | `p2_rigorous_audit.py` function | **COPY** code | 3 hours | P0 |
| **Honest-negative patterns** | P2 DAR language | **COPY** patterns | Qualitative | P1 |
| **RRS calculation** | P2 script logic | **ADAPT** for P1 grids | Re-run needed | P0 |
| **N_fav calculation** | P2 rank-based logic | **ADAPT** for P1 scores | Re-run needed | P0 |
| **Null distribution** | P2 protocol (text) | **IMPLEMENT** for P1 | Re-run needed | P0 |
| **Multi-seed launcher** | `p2_targeted_redock_multiseed.sh` | **COPY** script, adapt paths | 11 days | P0 |
| **GNINA rescoring** | `p2_gnina_consensus_rescore.py` | **COPY** script, adapt paths | 5 days | P0 |
| **Statistical audit** | `p2_rigorous_audit.py` | **COPY** script, adapt data | 5 days | P0 |
| **Preparation manifest** | `md_forcefield_manifest.py` | **COPY** script | 2 days | P1 |

**Total Time Saved by Copying P2 Outputs**: **~15 days**  
**Total Time Saved by Copying P2 Scripts**: **~28 days**  
**Combined Time Savings**: **~30 days** (matches earlier calculation)

---

## Immediate Action Plan

### Today (1 hour)
```bash
cd Project1_Chem_space_antimalarial_V7_CorrectedGrid

# Create P2 reference directory
mkdir -p results/p2_reference_outputs

# Copy directly reusable P2 outputs
cp ../Project2_Polypharmacology_MD_ValidationV2607/results/cross_metric_statistical_audit.* \
   results/p2_reference_outputs/

cp ../Project2_Polypharmacology_MD_ValidationV2607/results/c_acsi_scores.csv \
   results/p2_reference_outputs/

cp ../Project2_Polypharmacology_MD_ValidationV2607/results/c_pns_ranking.csv \
   results/p2_reference_outputs/

cp ../Project2_Polypharmacology_MD_ValidationV2607/results/c_acsi_weight_sensitivity.* \
   results/p2_reference_outputs/

cp -r ../Project2_Polypharmacology_MD_ValidationV2607/results/pp01_docking_20260829 \
      results/p2_reference_outputs/

cp -r ../Project2_Polypharmacology_MD_ValidationV2607/results/string_threshold_sensitivity_20260829 \
      results/p2_reference_outputs/

# Copy P2 scripts
mkdir -p scripts/from_p2
cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_rigorous_audit.py \
   scripts/from_p2/

cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_targeted_redock_multiseed.sh \
   scripts/from_p2/

cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_gnina_consensus_rescore.py \
   scripts/from_p2/

cp ../Project2_Polypharmacology_MD_ValidationV2607/scripts/md_forcefield_manifest.py \
   scripts/from_p2/

# Create inventory
cat > results/p2_reference_outputs/README.md <<'EOF'
# P2 Reference Outputs for P1 Revision

These files are copied from P2 (Project2_Polypharmacology_MD_ValidationV2607) 
because P1 Set A and P2 Set C are the exact same 17 compounds (PP-01...PP-17).

## Directly Reusable Outputs

1. `cross_metric_statistical_audit.csv` - 100k permutation p-values, 10k bootstrap CI
2. `c_acsi_scores.csv` - ACSI for all 17 compounds
3. `c_pns_ranking.csv` - PNS for all 17 compounds
4. `c_acsi_weight_sensitivity.*` - Robustness analysis
5. `pp01_docking_20260829/` - Multi-seed validation for PP-01
6. `string_threshold_sensitivity_20260829/` - PNS robustness

## Usage

These outputs can be:
- **Referenced in P1 Methods** (same cohort, same protocol)
- **Cited in P1 SI** (supporting analysis)
- **Extended for P1-specific analyses** (e.g., N_fav vs RRS correlation)

## Provenance

Source: Project2_Polypharmacology_MD_ValidationV2607/results/
Date copied: 2026-09-09
P2 Status: JCIM submission-ready
Cohort verification: 100% SMILES match (17/17 compounds)
EOF

echo "✅ P2 outputs copied to results/p2_reference_outputs/"
echo "✅ P2 scripts copied to scripts/from_p2/"
```

### Tomorrow (Day 2)
1. Adapt `p2_rigorous_audit.py` for P1 data structure
2. Use copied ACSI/PNS values in SI Table S_NEW5
3. Reference PP-01 multi-seed results in Methods

---

## Benefits of This Approach

### 1. Time Savings
- **Don't re-run 100k permutations** (P2 already did)
- **Don't recompute ACSI** (P2 already did)
- **Don't recompute PNS** (P2 already did)
- **Don't redevelop multi-seed protocol** (P2 already debugged)

### 2. Quality Assurance
- **P2 outputs are PI-approved** for JCIM submission
- **P2 scripts are battle-tested** (5 failed attempts debugged)
- **P2 statistics are gold-standard** (100k perm, 10k bootstrap)

### 3. Consistency
- **Same cohort** → same ACSI/PNS
- **Same methods** → reproducible results
- **Same statistical framework** → comparable analyses

### 4. Provenance
- **P2 outputs are versioned** with SHA-256
- **P2 scripts are documented** with manifests
- **P2 protocols are audited** with QC gates

---

## Conclusion

**Key Decision**: 
- ✅ **COPY** P2 outputs for statistical framework, ACSI, PNS, sensitivities
- ⚠️ **ADAPT** P2 scripts for multi-seed, GNINA, statistical audit
- ❌ **RE-RUN** P1-specific docking (different grids), RRS (different scores), N_fav (different scores)

**Time Saved**: ~15 days from copying outputs, ~13 days from copying scripts = **~28 days total**

**Recommendation**: 
1. **Today**: Copy all P2 outputs and scripts (1 hour)
2. **Tomorrow**: Create inventory and verify cohort match
3. **Day 3**: Start adapting scripts for P1 data

---

**Document**: P1 ← P2 reusable outputs identification  
**Status**: ANALYSIS_COMPLETE  
**Next Action**: Execute copy commands (1 hour)  
**Cross-Reference**: `P1_P2_CROSS_LEARNING_REFINEMENTS.md`, `P1_REVISION_ACCELERATED_PLAN.md`
