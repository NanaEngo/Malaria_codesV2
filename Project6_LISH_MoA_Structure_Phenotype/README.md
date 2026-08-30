# Project 6 — Structure–phenotype prediction of mechanism-of-action profiles

**Status:** `PHASE 1 MAPPING VALIDATED — PHASE 2 COLLISION-GROUP BENCHMARK COMPLETE`
**Date established:** 12 August 2026; mapping validated 25 August 2026
**Relationship to P5:** independent follow-up study building on P5; not a revision or continuation of the canonical P5 manuscript.

## Scientific question

Can molecular structure, cellular phenotype, or their controlled fusion predict multi-label mechanism-of-action (MoA)-associated profiles under drug-level and scaffold-aware validation?

Project 6 is motivated by the completed phenotype-only LISH-MoA benchmark. It will test a new structure–phenotype question only after an auditable `drug_id → SMILES` mapping is available.

## Current evidence

The phenotype-only LISH-MoA baseline is complete and remains an orthogonal reference:

- 3,289 drug-level rows;
- 206 scored MoA labels;
- 5 seeds × 5 drug-grouped folds;
- primary mean column-wise log loss: **0.02378**;
- secondary macro-AUROC: **0.6435**;
- secondary macro-AUPRC: **0.1428**.

These metrics describe MoA-associated phenotype prediction. They do not establish causal target engagement, antimalarial activity, or resistance resilience, and they are not numerically comparable to P5 molecular ROC-AUC values.

## Blocked structure arm

A versioned, auditable structure mapping is now available: 3,289/3,289 drug-level rows are covered, all mapped structures pass validation after salt stripping, and the frozen contract records 1,722 unique molecules and 794 collision groups. Phase 2 was therefore executed under collision-group primary splits and is now complete for the audited molecular matrix. No gain claim is authorized: the audited molecular arms do not establish a structure-based performance advantage.

The P5 scripts remain the preparation reference:

- `Project5_GNN_Transformer_DrugDiscovery/scripts/p5_lish_moa_prepare.py`
- `Project5_GNN_Transformer_DrugDiscovery/scripts/p5_lish_moa_benchmark.py`

Raw competition files and credentials remain outside Git.

## Reopening gates and current benchmark status

The following gates have passed for the current Phase 2 benchmark:

1. versioned mapping with exactly one row per `drug_id`;
2. archive hash, source provenance, coverage, invalid-SMILES, and canonical-collision report;
3. explicit collision policy before splitting (labels=max, phenotype covariates=mean, IDs retained);
4. identical mapped cohort for every model;
5. drug-grouped splits and scaffold-held-out sensitivity without structure leakage;
6. ECFP4-RF baseline on the exact same folds;
7. paired seed/fold comparisons with multiplicity correction;
8. complete failure accounting for TFP/TNE and bounded, separately labelled QKS computation.

Completed Phase 2 results include phenotype-only baselines on k-fold, collision-group, and scaffold splits; ECFP4-linear and ECFP4-RF structure baselines; phenotype+ECFP4 fusion; the complete collision-group molecular matrix (GIN, GIN-TFP, GIN-TNE, and ChemBERTa); pooled calibration across arms; and the bounded QKS sensitivity (extended to four arm pairs). Dedicated per-label calibration **plots** remain `NOT_COMPUTED`; the bounded QKS sensitivity is `COMPUTED` (29 Aug 2026). Under the scaffold-held-out split all four molecular arms remain near chance (GIN 0.50642, GIN-TFP 0.50077, GIN-TNE 0.50609, ChemBERTa 0.50344 macro-AUROC, below the phenotype reference 0.64023). The cross-modal attention-fusion arm remains `PLANNED_SECONDARY` and is intentionally **not run** (decision 30 Aug 2026: the `COMPUTED` late-concat fusion is already an honest-negative below the phenotype baseline, and the single GPU is saturated by the active M1 production job). See `P6_DATA_ANALYSIS_REPORT.md` §1/§4.6 and `../docs/CENTRAL_QUESTIONS_PROJECTS.md` §P6.

## Manuscript boundary

P5 remains the primary antimalarial GNN/Transformer benchmark. Project 6 may cite P5 as prior work, but it must have its own title, abstract, methods, data contract, results, limitations, and submission package. A successful result would support only MoA-associated prediction; it would not validate P5's antimalarial activity claim or establish biological target engagement.
