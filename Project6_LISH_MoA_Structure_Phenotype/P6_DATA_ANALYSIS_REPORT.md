# Project 6 Data Analysis Report — LISH-MoA structure–phenotype follow-up

**Version:** 0.6
**Updated:** 30 August 2026
**Status:** Phase 1 mapping validated; Phase 2 collision-group and scaffold benchmarks complete; pooled calibration, bounded QKS, prevalence-tertile sensitivity, and paired seed–fold variability available; attention-fusion cross-modal arm outside the present analysis.
**Central question (locked 30 Aug 2026):** Under leakage-controlled evaluation of a mapped LISH-MoA cohort, does molecular structure provide transferable information for predicting observed MoA-associated labels beyond a phenotype-only reference, and does combining the two information sources improve out-of-sample prediction?
**Long-form history:** `docs/P6_DAR_OPERATIONAL_LOG.md`

## 1. Decision record

`PHASE1_MAPPING_VALIDATED_20260825_PHASE2_BOUNDED_20260826`

The initial LISH-MoA artifact was phenotype-only. A versioned `drug_id → SMILES` mapping was constructed from PRISM-aligned records, validated with RDKit, and frozen before Phase 2 modelling. The collision-group primary benchmark is complete for all four molecular arms. Pooled scaffold calibration diagnostics computed for phenotype, ECFP4-RF structure, and late-concat fusion arms.

`ATTENTION_FUSION_DEFERRED_20260830` — cross-modal attention-fusion arm remains `PLANNED_SECONDARY` and is intentionally **not run**. The existing `COMPUTED` late-concat fusion addresses the multimodal branch as a bounded negative result: fusion remains below the phenotype baseline under the evaluated splits, while structure-only arms are near chance.

## 2. Locked phenotype reference

| Quantity | Locked value |
|---|---:|
| Drug-level rows | 3,289 |
| Scored labels | 206 |
| Grid | 5 seeds × 5 drug-grouped folds |
| Primary mean column-wise log loss | 0.02378 |
| Macro-AUROC | 0.6435 |
| Macro-AUPRC | 0.1428 |

Reference artifacts maintained under `Project5_GNN_Transformer_DrugDiscovery/results/lish_moa/`.

## 3. Planned estimands

Primary: mean column-wise log loss at the drug level.
Secondary: macro-AUPRC, macro-AUROC, mean Brier score, calibration error, label coverage, and failure counts.

Candidate arms (one identical mapped cohort and fold grid):
1. phenotype-only baseline
2. ECFP4-RF
3. GNN baseline
4. GIN-TFP
5. GIN-TNE
6. ChemBERTa
7. structure + phenotype fusion (predeclared exploratory)
8. QKS (bounded sensitivity analysis)

## 4. Phase 2 benchmark results

Protocol: verbatim locked P5 estimator (per-label unweighted logistic, liblinear, 5 seeds × 5 folds), 3289 drugs × 206 labels.

| Arm | Split | Log loss | Macro-AUROC | Macro-AUPRC |
|---|---|---|---|---|
| phenotype | kfold | **0.023783** | **0.64345** | **0.14276** |
| phenotype | collision_group | 0.024282 | 0.63619 | 0.13137 |
| phenotype | scaffold | 0.024176 | 0.64023 | 0.13308 |
| ECFP4-linear | collision_group | 0.025979 | 0.53481 | 0.02223 |
| ECFP4-RF | collision_group | 0.035820 | 0.53562 | 0.02590 |
| ECFP4-RF | scaffold | 0.035240 | 0.53817 | 0.02501 |
| fusion (phenotype+ECFP4-RF) | collision_group | 0.030516 | 0.58323 | 0.08216 |
| fusion (phenotype+ECFP4-RF) | scaffold | 0.030183 | 0.58774 | 0.08232 |

> **Model-unification decision record (30 Aug 2026, evening) — canonical ECFP4 baseline/fusion = RandomForest on every split.** A systematic source audit exposed a model mix-up: the manuscript labels the molecular baseline "ECFP4--RF" everywhere (Methods: `RandomForestClassifier`, 500 trees) and the collision-group table correctly uses the RF runs (`structure_collision_group_rf`, AUROC 0.53562; `both_collision_group_rf`, AUROC 0.58323), but the **scaffold** table and the scaffold calibration/QKS analyses had been pointed at the *unweighted-per-label logistic* runs (no `_rf` suffix): `p6_lish_moa_structure_scaffold_report.json` (AUROC 0.53749, logistic) and `p6_lish_moa_both_scaffold_report.json` (AUROC 0.63360, logistic). The two rows above labelled "ECFP4-RF | scaffold" (0.034690/0.53749/0.02290) and "fusion | scaffold" (0.024874/0.62647/0.10681) are therefore **logistic** values and must be replaced by the RF values. **Decision:** (i) canonical scaffold structure arm = the RF run `p6_lish_moa_structure_scaffold_rf` (AUROC 0.53817, log loss 0.035240, AUPRC 0.02501, Brier 0.00342, ECE 0.00221; 25/25 fold predictions present); (ii) the missing scaffold **fusion** RF run (`--features both --split scaffold --model rf --dump-predictions`) is being regenerated as **SLURM job 15717** (`scripts/p6_lish_moa_both_scaffold_rf.sbatch`, partition production, 16 CPU, 8 h, submitted 30 Aug ~20:15Z; an initial local front-end nohup attempt was killed as suboptimal — the SLURM queue was empty and the production node idle, so the batch slot gives a dedicated 16-CPU execution instead of front-end contention); (iii) SLURM job 15717 completed 30 Aug ~21:37Z; pooled scaffold calibration, the QKS phenotype-vs-structure pair, the QKS phenotype-vs-fusion pair, and the paired seed-fold uncertainty were all recomputed from the RF prediction directories and this table updated (fusion scaffold RF: log loss 0.030183, AUROC 0.58774, AUPRC 0.08232); (iv) the logistic scaffold runs (`structure_scaffold`, `both_scaffold`) are retained on disk for provenance but are **no longer cited** as the baseline/fusion; the fixed `protocol` string in the reports ("logistic baseline") is a script constant and is not a reliable model indicator — the reliable discriminator is the `_rf` filename suffix (script: `suffix = "" if model == logistic else f"_{model}"`). The honest-negative verdict is unchanged by this re-baselining.

### 4.1 Molecular arms — GNN / GIN-TFP / GIN-TNE / ChemBERTa

| Arm | Mean log loss | Macro-AUROC | Macro-AUPRC | Mean Brier | Mean ECE |
|---|---:|---:|---:|---:|---:|
| GIN | 0.02419 | 0.50785 | 0.01379 | 0.00347 | 0.00449 |
| GIN-TFP | 0.02334 | 0.50479 | 0.01381 | 0.00341 | 0.00300 |
| GIN-TNE | 0.02434 | 0.50601 | 0.01460 | 0.00341 | 0.00306 |
| ChemBERTa | 0.02549 | 0.50137 | 0.01313 | 0.00343 | 0.00750 |

### 4.2 Scaffold sensitivity analysis

| Arm | Mean log loss | Macro-AUROC | Macro-AUPRC | Mean Brier | Mean ECE |
|---|---:|---:|---:|---:|---:|
| GIN (scaffold) | 0.02474 | 0.50642 | 0.01509 | 0.00349 | 0.00493 |
| GIN-TFP (scaffold) | 0.02373 | 0.50077 | 0.01300 | 0.00343 | 0.00325 |
| GIN-TNE (scaffold) | 0.02429 | 0.50609 | 0.01399 | 0.00342 | 0.00318 |
| ChemBERTa (scaffold) | 0.02559 | 0.50344 | 0.01327 | 0.00344 | 0.00761 |

All four GNN scaffold arms remain at chance macro-AUROC (0.501–0.506), below the scaffold phenotype baseline (0.64023). The honest-negative structure-arm result extends to all four representation families under both collision-group and scaffold splits.

### 4.3 Pooled calibration

- Phenotype: ECE=0.0016, MCE=0.648, Brier=0.0038
- Structure: ECE=0.0012, MCE=0.3893, Brier=0.0034 (RF, scaffold)
- Fusion: ECE=0.0017, MCE=0.2590, Brier=0.0034 (RF, scaffold)

> **Calibration re-baselining complete (30 Aug 2026, job 15717 done):** under the model-unification decision, both molecular calibration rows now derive from the **RF** scaffold predictions. Structure (`predictions/p6_lish_moa_structure_scaffold_rf`): n=3,387,670 pooled observations, **ECE=0.0012, MCE=0.3893, Brier=0.0034**. Fusion (`predictions/p6_lish_moa_both_scaffold_rf`, regenerated from job 15717): **ECE=0.0017, MCE=0.2590, Brier=0.0034** (replaces the provisional logistic fusion row ECE 0.0020/MCE 0.697/Brier 0.0040). The manuscript `tab:p6_calibration` fusion row is updated to the RF values.

### 4.4 Bounded QKS (extended, 4 pairs)

| Pair | τ=0.5 abs-diff | Spearman max-prob |
|---|---:|---:|
| phenotype vs structure (RF) | 0.0229 | +0.0361 |
| phenotype vs fusion (RF) | 0.0329 | +0.4272 |
| phenotype vs GIN | 0.0467 | −0.0119 |
| phenotype vs ChemBERTa | 0.0537 | −0.0354 |

> **QKS reporting decision (30 Aug 2026) — pos-count Spearman dropped from the manuscript.** The QKS JSONs also record `spearman_pos_count` (1.000 for every pair): the per-drug positive-label count is the *same label vector* in both arms, so this is the correlation of a vector with itself and carries no information. The manuscript reports only the max-prob Spearman; the pos-count field remains in the archived JSONs for schema provenance but is not interpreted.

> **QKS re-baselining complete (30 Aug 2026, job 15717 done):** under the model-unification decision, both QKS pairs are recomputed on the **RF** scaffold predictions. Phenotype-vs-structure: τ=0.5 abs-diff **0.0229**, Spearman max-prob **+0.0361** (n=3,289). Phenotype-vs-fusion (RF fusion, regenerated): τ=0.5 abs-diff **0.0329**, Spearman max-prob **+0.4272** (replaces the logistic-fusion pair 0.068/0.283). The honest-negative reading is unchanged: the structure arm does not provide ranking information beyond the phenotype reference (near-zero cross-arm Spearman); the fusion arm shows moderate predicted-probability agreement consistent with its AUROC lift over structure alone.

> **DOI verification (30 Aug 2026) — all 5 DOIs in `Bibliography_P6.bib` resolve on Crossref.** `10.1039/D5DD00348B` (ChemBERTa-3, Digital Discovery 2026, 5, 662), `10.1186/s13321-025-01045-w` (J Cheminform), `10.64898/2026.04.22.720110` (MVCBench, bioRxiv), `10.64898/2026.02.03.703502` (Katsaouni & Schulz, bioRxiv), `10.1038/s41467-025-58244-0` (Tanner et al., Nat Commun). The `10.64898` prefix is the openRxiv bioRxiv/medRxiv prefix in force since 1 Dec 2025 (replacing `10.1101`), so the two bioRxiv entries are valid; no correction needed.

### 4.5 RRS-class proxy (prevalence-tertile stratification)

Per-MoA positive rate tertiles: Brier increases monotonically low→mid→high (~0.0007→~0.0022→~0.0075) across all 7 arms. Data-driven sensitivity, not a biological RRS classification.

### 4.6 Paired uncertainty mitigation

20,000 paired bootstrap resamples across seed–fold level. Intervals describe variation across declared resampling units; not population-level CIs. No superiority claim made.

## 5. Leakage and statistical interpretation

Aggregation before splitting. Canonical-SMILES collisions resolved before splitting. No assay replicate, duplicated structure, or collision group crosses train/test. Primary split is drug-grouped; scaffold-held-out is sensitivity. All arms use same seeds and folds.

## 6. Prohibited claims

Do not claim that MoA labels establish causal target engagement, antimalarial activity, resistance resilience, or superiority of molecular representations unless directly generated and audited. Do not compare LISH log loss/AUROC numerically with P5 antimalarial ROC-AUC.

## 7. Promotion rule

A P6 manuscript may be drafted only after a frozen mapping audit and complete model matrix. If every molecular arm fails to improve on ECFP4-RF, the result may still be publishable as an honest-negative, but only with a justified question and complete uncertainty reporting.
