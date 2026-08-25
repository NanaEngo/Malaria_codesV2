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

Update 2026-08-25: the drug_id hex identifiers are not publicly resolvable (see `docs/P6_RESEARCH_DOSSIER.md`); coverage must therefore be measured empirically after signature-based matching against CMap2020. The audit above gains two mandatory fields: per-drug match score and margin to second-best match, with the ambiguity threshold frozen before any model run.

### 4.1 Mapping audit — EXECUTED 2026-08-25 (strategy B, PRISM viability)

Verified outputs of `scripts/p6_phase1_prism.py` (HPC run, env qom):

| Audit item | Value |
|---|---|
| Mapped rows / unique drug_id | 3289 / 3289 |
| Coverage of the 3,289 drug-level rows | **100 %** (`drugid_to_smiles_v2.csv`) |
| Match method | Pearson r, max-pooled over PRISM compounds, 100 shared cell lines, dose-collapsed by median |
| Frozen threshold | null q=0.9999 → 0.4993 (cell-line permutation, seed 42) |
| Score distribution | median 0.358, max 0.831 |
| Matches above threshold | 248/3289 (7.5 %) |
| Ambiguous margin (<0.01) | 705 rows |
| Canonical-SMILES collisions | 1566 rows — resolve before split (§5) |
| Functional gate (HDAC) | 9/18 kaggle `hdac_inhibitor` drugs matched a PRISM compound with 'hdac' MoA (~50 % vs ~1–2 % random) |
| SMILES source | PRISM treatment-info column; multi-component entries (comma-separated) must be split before RDKit validation |
| Invalid/unparseable SMILES | not yet computed (RDKit pass deferred to Phase 2 prep) |

Provenance hashes:
`drugid_to_smiles_v2.csv` SHA-256 `b6abe4d1a4f81cfb9870a644327cd7a3e2ee1a8bf2f4930312f4f10d099696c9`;
`prism_threshold.json` SHA-256 `2a0b3416577a9734db84cdf4980add629ca96efbfcd4e9e1076a892b63df33e5`.
Negative result retained for provenance: L1000 expression matching (`drugid_to_pert_v1.csv`) gave 0/3289 above its own null threshold — cross-campaign expression ceiling ≈ noise floor (dossier §5.1).

### 4.2 Validation pass — EXECUTED 2026-08-25 (`scripts/p6_phase1_validate.py`, RDKit 2026.03.5)

Multi-component SMILES entries are split (',' and '.'), the largest fragment by heavy-atom count is kept, re-canonicalized with RDKit, and collision groups are assigned over identical canonical SMILES.

| Audit item | Value |
|---|---|
| Rows / source coverage | 3289 / 100 % |
| Valid fraction after salt-stripping | **100 %** |
| Unique molecules | 1722 |
| Collision groups (>1 drug) | 794 |
| Multi-component raw entries | 1622 (max 7 components) |

Frozen data contract: `data/mappings/drugid_to_smiles_contract.json`
(SHA-256 `565a6e1b1a630e53d793b66368725cd13e3549846a486292cc73d9f3d0618b03`),
artifact `drugid_to_smiles_v2_validated.csv`. Collision groups must not cross
train/test folds (§5). Phase 1 is closed; Phase 2 may start on the exact mapped cohort.

## 5. Leakage and statistics gates

Aggregation occurs before splitting. Canonical-SMILES collisions are resolved before splitting. No assay replicate, duplicated structure, or collision group may cross train/test. The primary split is drug-grouped; scaffold-held-out performance is sensitivity analysis. All arms use the same seeds and folds. Pairwise comparisons use seed/fold-paired statistics and BH-FDR or a predeclared family-wise correction.

## 6. Prohibited claims

Do not claim that MoA labels establish causal target engagement, antimalarial activity, resistance resilience, or superiority of molecular representations unless the corresponding evidence is directly generated and audited. Do not compare LISH log loss/AUROC numerically with P5 antimalarial ROC-AUC as if they were the same estimand.

## 7. Promotion rule

A Project 6 manuscript may be drafted only after a frozen mapping audit and complete model matrix. If every molecular arm fails to improve on ECFP4-RF, the result may still be publishable as an honest-negative representation benchmark, but only with a justified question and complete uncertainty reporting. If no structure mapping is obtained, retain the phenotype-only result as a documented baseline and do not force a separate paper.
