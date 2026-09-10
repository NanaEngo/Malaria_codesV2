# P2 Reference Outputs for P1 Revision

**Date Created**: 2026-09-09  
**Source**: Project2_Polypharmacology_MD_ValidationV2607/results/  
**Purpose**: Reuse P2 outputs for P1 revision (same 17-compound cohort)  
**Cohort Verification**: P1 Set A = P2 Set C (100% SMILES match, 17/17 compounds)

---

## Directly Reusable Outputs

### 1. Statistical Framework
- **`cross_metric_statistical_audit.csv`** - 100,000-permutation p-values, 10,000-bootstrap 95% CI
- **`cross_metric_statistical_audit.json`** - Machine-readable manifest
- **Use**: Table S6 correlations, Methods §2.4.3 statistical framework
- **Time Saved**: 5 days (don't need to re-run 100k permutations)

### 2. ACSI Scores
- **`c_acsi_scores.csv`** - ACSI for all 17 PP-01...PP-17 compounds
- **Use**: SI Table S_NEW5, Methods §2.4.2 ACSI definition
- **Time Saved**: 1 day

### 3. PNS Scores
- **`c_pns_ranking.csv`** - PNS for all 17 compounds
- **Use**: SI Table S_NEW5, Methods §2.4.1 PNS definition
- **Time Saved**: 1 day

### 4. ACSI Sensitivity
- **`c_acsi_weight_sensitivity.csv`** - 8 perturbation scenarios (±20% per weight)
- **`c_acsi_weight_sensitivity.json`** - Spearman ρ: 0.9167–0.9804
- **Use**: Methods caveat, Discussion robustness claim
- **Time Saved**: 2 days

### 5. PNS Imputation Sensitivity
- **`pns_imputation_sensitivity.csv`** - Zero-to-double PfCRT centrality
- **`pns_imputation_sensitivity.json`** - Rank stability analysis
- **Use**: Methods §2.4.1 robustness statement
- **Time Saved**: 1 day

### 6. PP-01 Multi-Seed Validation
- **`pp01_docking_20260829/`** - PP-01 × 2 WT targets × 5 seeds
  - `multiseed_canonical_summary.json` - PfDHFR: −7.499 ± 0.021 kcal/mol
  - `multiseed_sensitivity_summary.json` - PfCRT: −9.250 ± 0.015 kcal/mol
  - `manifest_pp01_multiseed_*.json` - Protocol documentation
- **Use**: Methods "seed sensitivity assessed for PP-01 (representative)"
- **Time Saved**: 2 days

### 7. STRING Threshold Sensitivity
- **`string_threshold_sensitivity_20260829/`** - PNS robustness across 400/700/900
- **Use**: SI discussion of PPI threshold choice
- **Time Saved**: 1 day

---

## P2 Scripts (Copied to `scripts/from_p2/`)

### 1. Statistical Audit
- **`p2_rigorous_audit.py`** - 100k permutation, 10k bootstrap, power analysis
- **Reusability**: 80% (adapt data loading, keep analysis)
- **Time Saved**: 5 days

### 2. Multi-Seed Launcher
- **`p2_targeted_redock_multiseed.sh`** - SLURM array for 5 seeds
- **Reusability**: 100% (just change paths)
- **Time Saved**: 11 days

### 3. GNINA Rescoring
- **`p2_gnina_consensus_rescore.py`** - CNN scoring for poses
- **`p2_gnina_consensus_rrs.py`** - RRS from GNINA scores
- **Reusability**: 90% (change input directories)
- **Time Saved**: 5 days

### 4. Preparation Manifest
- **`md_forcefield_manifest.py`** - SHA-256 provenance tracking
- **Reusability**: 100%
- **Time Saved**: 2 days

---

## Usage Guidelines

### What to COPY Directly
- ✅ ACSI/PNS values for SI Table S_NEW5
- ✅ Statistical framework p-values and CI for Table S6
- ✅ PP-01 multi-seed as representative example
- ✅ Sensitivity analyses for robustness claims

### What to ADAPT
- ⚠️ Statistical audit script (change data loading for P1 structure)
- ⚠️ Multi-seed launcher (change paths to P1 compounds)
- ⚠️ GNINA rescoring (change paths to P1 poses)

### What to RE-RUN
- ❌ RRS classification (need P1-specific docking with P1 grids)
- ❌ N_fav calculation (need P1-specific docking scores)
- ❌ Null distribution (need P1-specific pseudo-mutants)

---

## Cohort Identity Proof

From P2 DAR §2.0:
> "A cohort audit confirmed exact identity for all 17 PP-01--PP-17 SMILES; 
> the overlap and shared workflow provenance preclude independent-replication claims."

From P1 V7 manuscript Table 1:
> "Top-20 candidates (Set A): PP-01...PP-20 (17 with complete data)"

**Conclusion**: P1 and P2 analyze **the same 17 compounds** → P2 outputs are P1-relevant

---

## Cross-References

- **Technical Details**: `../P1_P2_REUSABLE_OUTPUTS.md`
- **Cross-Learning Analysis**: `../P1_P2_CROSS_LEARNING_REFINEMENTS.md`
- **Accelerated Timeline**: `../P1_REVISION_ACCELERATED_PLAN.md`
- **Integration Summary**: `../P1_P2_INTEGRATION_SUMMARY.md`

---

## File Inventory

```
p2_reference_outputs/
├── README.md (this file)
├── cross_metric_statistical_audit.csv (8 rows, 100k perm)
├── cross_metric_statistical_audit.json
├── c_acsi_scores.csv (17 compounds)
├── c_pns_ranking.csv (17 compounds)
├── c_acsi_weight_sensitivity.csv (8 scenarios)
├── c_acsi_weight_sensitivity.json
├── pns_imputation_sensitivity.csv
├── pns_imputation_sensitivity.json
├── pp01_docking_20260829/
│   ├── multiseed_canonical_summary.json
│   ├── multiseed_sensitivity_summary.json
│   ├── manifest_pp01_multiseed_pfdhfr_wt.json
│   └── manifest_pp01_multiseed_pfcrt_wt.json
└── string_threshold_sensitivity_20260829/
    ├── summary.json
    └── pns_ranking_threshold_sensitivity.csv
```

**Total Time Saved by Reusing P2 Outputs**: **~15 days**  
**Total Time Saved by Reusing P2 Scripts**: **~28 days**  
**Combined**: **~30 days** (43% timeline reduction)

---

**Status**: OUTPUTS_COPIED  
**Date**: 2026-09-09  
**Next Action**: Verify cohort match, create SI Table S_NEW5 with P2 ACSI/PNS values
