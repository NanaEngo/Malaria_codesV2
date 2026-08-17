# Project 6 — Structure–phenotype prediction of mechanism-of-action profiles

**Status:** `PLANNED — NO STRUCTURE ARM COMPUTED`  
**Date established:** 12 August 2026  
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

The current LISH package has no versioned, auditable structure mapping. Therefore Project 6 has **not** run ECFP4, GNN, ChemBERTa, TFP, TNE, or QKS on LISH-MoA. No gain claim is authorized.

The P5 scripts remain the preparation reference:

- `Project5_GNN_Transformer_DrugDiscovery/scripts/p5_lish_moa_prepare.py`
- `Project5_GNN_Transformer_DrugDiscovery/scripts/p5_lish_moa_benchmark.py`

Raw competition files and credentials remain outside Git.

## Reopening gates

The structure arm can open only when all gates pass:

1. versioned mapping with exactly one row per `drug_id`;
2. archive hash, source provenance, coverage, invalid-SMILES, and canonical-collision report;
3. explicit collision policy before splitting (labels=max, phenotype covariates=mean, IDs retained);
4. identical mapped cohort for every model;
5. drug-grouped splits and scaffold-held-out sensitivity without structure leakage;
6. ECFP4-RF baseline on the exact same folds;
7. paired seed/fold comparisons with multiplicity correction;
8. complete failure accounting for TFP/TNE and bounded, separately labelled QKS computation.

## Manuscript boundary

P5 remains the primary antimalarial GNN/Transformer benchmark. Project 6 may cite P5 as prior work, but it must have its own title, abstract, methods, data contract, results, limitations, and submission package. A successful result would support only MoA-associated prediction; it would not validate P5's antimalarial activity claim or establish biological target engagement.
