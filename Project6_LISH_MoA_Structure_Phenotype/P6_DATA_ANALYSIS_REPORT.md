# Project 6 Data Analysis Report — LISH-MoA structure–phenotype follow-up

**Version:** 0.1  
**Updated:** 12 August 2026  
**Status:** planning / structure mapping required  
**Scope:** Project 6 only; it does not modify P5 canonical results.

## 1. Decision record

`NO_STRUCTURE_MODEL_RUN_20260812`

The available LISH-MoA artifact is phenotype-only. It contains drug-level aggregation and MoA-associated labels but no versioned `drug_id → SMILES` mapping. Consequently, the molecular arms are blocked and no structure-based gain is claimed.

## 2. Locked phenotype reference

| Quantity | Locked value |
|---|---:|
| Drug-level rows | 3,289 |
| Scored labels | 206 |
| Grid | 5 seeds × 5 drug-grouped folds |
| Primary mean column-wise log loss | 0.02378 |
| Macro-AUROC | 0.6435 |
| Macro-AUPRC | 0.1428 |

Reference artifacts are maintained under `Project5_GNN_Transformer_DrugDiscovery/results/lish_moa/`. The phenotype result is a baseline for Project 6, not a P5 molecular validation.

## 3. Planned estimands

Primary: mean column-wise log loss at the drug level.  
Secondary: macro-AUPRC, macro-AUROC, mean Brier score, calibration error, label coverage, and failure counts.

Candidate arms, evaluated on one identical mapped cohort and fold grid:

1. phenotype-only baseline;
2. ECFP4-RF;
3. GNN baseline;
4. GIN-TFP;
5. GIN-TNE;
6. ChemBERTa, if the tokenization and training budget are documented;
7. structure + phenotype fusion as a predeclared exploratory arm;
8. QKS only as a bounded, separately reported sensitivity analysis.

## 4. Required mapping audit

Before any model run, produce a versioned mapping report containing:

- source URL/archive and SHA-256;
- mapping row count and unique `drug_id` count;
- coverage of the 3,289 drug-level rows;
- invalid/unparseable SMILES;
- duplicate `drug_id` rows;
- canonical-SMILES collisions and their resolution;
- final molecule count and a frozen output hash.

Recommended interpretation: ≥90% coverage may support a primary mapped analysis if missingness is reported; lower coverage is exploratory unless representativeness is demonstrated.

## 5. Leakage and statistics gates

Aggregation occurs before splitting. Canonical-SMILES collisions are resolved before splitting. No assay replicate, duplicated structure, or collision group may cross train/test. The primary split is drug-grouped; scaffold-held-out performance is sensitivity analysis. All arms use the same seeds and folds. Pairwise comparisons use seed/fold-paired statistics and BH-FDR or a predeclared family-wise correction.

## 6. Prohibited claims

Do not claim that MoA labels establish causal target engagement, antimalarial activity, resistance resilience, or superiority of molecular representations unless the corresponding evidence is directly generated and audited. Do not compare LISH log loss/AUROC numerically with P5 antimalarial ROC-AUC as if they were the same estimand.

## 7. Promotion rule

A Project 6 manuscript may be drafted only after a frozen mapping audit and complete model matrix. If every molecular arm fails to improve on ECFP4-RF, the result may still be publishable as an honest-negative representation benchmark, but only with a justified question and complete uncertainty reporting. If no structure mapping is obtained, retain the phenotype-only result as a documented baseline and do not force a separate paper.
