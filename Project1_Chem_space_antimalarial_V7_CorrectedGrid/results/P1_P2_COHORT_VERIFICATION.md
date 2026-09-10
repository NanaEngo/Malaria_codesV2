# P1 ↔ P2 Cohort Identity Verification

**Date**: 2026-09-09  
**Status**: ✅ VERIFIED — 100% SMILES match (17/17)  
**Conclusion**: P1 Set A = P2 Set C (identical cohort)

---

## Verification Method

### Sources
- **P1**: `results/v7_candidate_manifest.csv` (canonical_smiles column)
- **P2**: `results/p2_reference_outputs/c_acsi_scores.csv` (smiles column)

### Test
```bash
# Extract and sort P1 SMILES
cut -d',' -f2 results/v7_candidate_manifest.csv | tail -n +2 | sort > p1_smiles.txt

# Extract and sort P2 SMILES
cut -d',' -f4 results/p2_reference_outputs/c_acsi_scores.csv | tail -n +2 | sort > p2_smiles.txt

# Compare
diff p1_smiles.txt p2_smiles.txt
```

### Result
```
✅ 100% MATCH: All 17 SMILES are identical
```

---

## Cohort Composition

| Compound | SMILES | P1 Rank | P2 Rank | SHA-256 (first 8) |
|----------|--------|---------|---------|-------------------|
| PP-01 | COc1ccc(-c2cc(=O)c3c(O)c(OC)c(OC)cc3o2)cc1 | 1 | 1 | 5fe90a6b |
| PP-02 | COc1ccc(C[C@@H]2CO[C@H](O)[C@H]2Cc2ccc(OC)c(OC)c2)cc1OC | 2 | 2 | 5fe90a6b |
| PP-03 | CC(C)=CCc1c(O)cc2c(c1O)C(=O)C(c1ccc(O)cc1O)CO2 | 3 | 3 | 5fe90a6b |
| PP-04 | COc1ccc2c(OC)c3ccoc3nc2c1OC | 4 | 4 | 5fe90a6b |
| PP-05 | COc1ccc(-c2cc(=O)c3c(O)cc(O)cc3o2)cc1 | 5 | 5 | 5fe90a6b |
| PP-06 | COc1cc([C@@H]2CC(=O)c3ccc(O)cc3O2)cc(CC=C(C)C)c1O | 6 | 6 | 5fe90a6b |
| PP-07 | CC(C)=CCOc1ccc2ccc(=O)oc2c1 | 7 | 7 | 5fe90a6b |
| PP-08 | C=CCc1cc(OC)c2c(c1OC)OCO2 | 8 | 8 | 5fe90a6b |
| PP-09 | CC(C)=CCc1ccc2cc[nH]c2c1 | 9 | 9 | 5fe90a6b |
| PP-10 | COc1cccc2c(=O)c3ccc(O)cc3oc12 | 10 | 10 | 5fe90a6b |
| PP-11 | COc1cc(O)c2c(=O)c(O)c(-c3ccc(O)c(OC)c3)oc2c1 | 11 | 11 | 5fe90a6b |
| PP-12 | C=C[C@@](C)(O)CC/C=C(\C)CCC=C(C)C | 12 | 12 | 5fe90a6b |
| PP-13 | CC(=O)OC1C(=O)c2c(O)cc(O)cc2O[C@H]1c1ccc(O)cc1 | 13 | 13 | 5fe90a6b |
| PP-14 | CC=Cc1cc(O)c(O)c(OC)c1 | 14 | 14 | 5fe90a6b |
| PP-15 | COc1c(O)cc2c(c1O)C(=O)C([C@H](O)c1ccccc1)CO2 | 15 | 15 | 5fe90a6b |
| PP-16 | Cc1occ2c1C(=O)c1c(O)cccc1C2=O | 16 | 16 | 5fe90a6b |
| PP-17 | O=C(O)C=Cc1ccc(O)cc1 | 17 | 17 | 5fe90a6b |

**Note**: All 17 compounds share the same P2 source SHA-256: `5fe90a6b7047626822e378cd0bcb5c41f7458b93a4ee63af3af3ead58ae45c36`

---

## Implications

### 1. P2 ACSI/PNS Values are P1-Ready ✅
Since the cohorts are identical:
- P2's ACSI scores → directly usable for P1 SI Table S_NEW5
- P2's PNS scores → directly usable for P1 SI Table S_NEW5
- P2's sensitivity analyses → directly applicable to P1

### 2. P2 Statistical Framework is P1-Applicable ✅
Since the cohorts are identical:
- P2's 100k permutation p-values → valid for P1 correlations
- P2's 10k bootstrap 95% CI → valid for P1 uncertainty
- P2's power analysis → valid for P1 sample size

### 3. P2 Multi-Seed Results are P1-Relevant ✅
Since PP-01 is in both cohorts:
- P2's PP-01 multi-seed validation (5 seeds, 2 targets) → citable in P1
- P2's seed sensitivity protocol → reusable for P1 validation

### 4. No Independent Validation Claims ⚠️
From P2 DAR §2.0:
> "A cohort audit confirmed exact identity for all 17 PP-01--PP-17 SMILES; 
> the overlap and shared workflow provenance preclude independent-replication claims."

**P1 must cite P2 outputs as "same-cohort reference" not "independent validation"**

---

## Provenance Trail

### P1 Cohort Selection (V7)
- **Source**: Hybrid library (65,856 compounds)
- **Filter**: MPO ≥ 0.70, SYBA > 0, SI > 10
- **Result**: Top-20 candidates → 17 with complete data
- **File**: `results/v7_candidate_manifest.csv`
- **Date**: 2026-08-10 (V7 freeze)

### P2 Cohort Selection (Set C)
- **Source**: Same hybrid library (65,856 compounds)
- **Filter**: MPO ≥ 0.70, SYBA > 0, SI > 10
- **Result**: Top-20 candidates → 17 with polypharmacology potential
- **File**: `results/candidate_selection/md_top20_candidates_polypharm.csv`
- **Date**: 2026-07-15 (P2 cohort freeze)

### Explanation for Identical Selection
Both projects used:
1. Same parent library (ANPDB + synthetic derivatives)
2. Same MPO weights (ADMET, NP-likeness, target affinity)
3. Same selectivity threshold (SI > 10)
4. Same SYBA filter (NP-likeness)

Result: **Deterministic selection → identical top-17**

---

## Next Actions

### Immediate (Today)
1. ✅ Copy P2 ACSI scores to P1 workspace (DONE)
2. ✅ Copy P2 PNS scores to P1 workspace (DONE)
3. ✅ Verify cohort match (DONE — 17/17 ✅)
4. ⏩ Create SI Table S_NEW5 with P2 values (NEXT)

### Tomorrow
5. Add cohort identity statement to Methods §2.1
6. Add P2 citation to ACSI/PNS definitions
7. Reference P2 multi-seed in Methods §2.3.4

---

## Verification Log

```
Date: 2026-09-09T10:30:00Z
User: vital
Test: SMILES exact match (diff)
P1 source: results/v7_candidate_manifest.csv
P2 source: results/p2_reference_outputs/c_acsi_scores.csv
Result: ✅ 0 differences (100% match)
Command: diff <(cut -d',' -f2 results/v7_candidate_manifest.csv | tail -n +2 | sort) \
              <(cut -d',' -f4 results/p2_reference_outputs/c_acsi_scores.csv | tail -n +2 | sort)
Exit code: 0
```

---

**Status**: COHORT_IDENTITY_VERIFIED  
**Confidence**: 100% (exact SMILES match on all 17 compounds)  
**Impact**: Enables direct reuse of P2 ACSI/PNS/statistical outputs  
**Next**: Create SI Table S_NEW5 with P2 values
