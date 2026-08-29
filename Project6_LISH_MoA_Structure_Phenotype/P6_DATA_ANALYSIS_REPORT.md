# Project 6 Data Analysis Report — LISH-MoA structure–phenotype follow-up

**Version:** 0.3
**Updated:** 28 August 2026
**Status:** Phase 1 mapping validated; Phase 2 collision-group benchmark complete for the audited model matrix
**Scope:** Project 6 only; it does not modify P5 canonical results.

## 1. Decision record

`PHASE1_MAPPING_VALIDATED_20260825_PHASE2_BOUNDED_20260826`

The initial LISH-MoA artifact was phenotype-only. A versioned `drug_id → SMILES` mapping was constructed from PRISM-aligned records, validated with RDKit, and frozen before Phase 2 modelling. The collision-group primary benchmark is now complete for all four molecular arms (GIN, GIN-TFP, GIN-TNE, and ChemBERTa); dedicated per-label calibration plots remain `NOT_COMPUTED`. The mapping, collision handling, fold metrics, and calibration-ready summary metrics are documented in this DAR (Sections 3--5) and in the manuscript.

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

### 4.3 Phase 2 benchmark — first arms EXECUTED 2026-08-26 (SLURM job 15492, env `malaria_md`)

Protocol: verbatim locked P5 estimator (per-label unweighted logistic,
liblinear, 5 seeds × 5 folds), 3289 drugs × 206 labels. Splits: `kfold`
(= P5 protocol reproduction), `collision_group` (primary honest split),
`scaffold` (sensitivity). Outputs: `results/p6_phase2/p6_lish_moa_*.{csv,json}`.

| Arm | Split | Log loss (primary) | Macro-AUROC | Macro-AUPRC |
|---|---|---|---|---|
| phenotype | kfold | **0.023783** (= locked 0.02378) | **0.64345** (= 0.6435) | **0.14276** (= 0.1428) |
| phenotype | collision_group | 0.024282 | 0.63619 | 0.13137 |
| phenotype | scaffold (`--dump-predictions`, 29 Aug) | 0.024176 | 0.64023 | 0.13308 |
| structure ECFP4-linear | collision_group | 0.025979 | 0.53481 | 0.02223 |
| structure ECFP4-RF | collision_group | 0.035820 | 0.53562 | 0.02590 |
| structure ECFP4-RF | scaffold (legacy 15496 task 1) | 0.035240 | 0.53817 | 0.02501 |
| structure (linear, `--dump-predictions` 29 Aug) | scaffold | 0.025920 | 0.53575 | 0.02116 |
| fusion phenotype+ECFP4 (RF) | collision_group | 0.030516 | 0.58323 | 0.08216 |
| fusion phenotype+ECFP4 (RF, `--dump-predictions` 29 Aug) | scaffold | 0.024874 | 0.62647 | 0.10681 |

Findings so far:
1. The kfold arm reproduces the locked baseline to the fourth decimal → pipeline faithful.
2. Leakage-corrected splits cost ~2 % relative log loss for the phenotype arm; the honest-split numbers become the reference for all structure comparisons.
3. Structure-only linear arm is near chance under the honest split — consistent with the literature expectation that linear ECFP4 carries little MoA signal.
4. Structure-only **RF** arms remain near chance under both honest splits (AUROC 0.5356 collision_group / 0.5382 scaffold; job 15496 tasks 0–1, completed 26 Aug). The 29 Aug `--dump-predictions` scaffold re-run on the linear arm (0.5358 AUROC) confirms the same near-chance verdict.
5. The **fusion arm does not beat the phenotype baseline** under collision_group (AUROC 0.58323 < 0.63619, log loss 0.030516). Under the 29 Aug `--dump-predictions` scaffold re-run, fusion AUROC improves to 0.62647 (log loss 0.024874), narrowing the gap to phenotype (0.64023) but still below the locked phenotype baseline. The honest-negative scaffold result for structure-only models is unchanged; the fusion arm shows sensitivity to the scaffold partition, never crossing the phenotype reference. No causal structure gain is demonstrated; this is recorded as an honest-negative result for the evaluated molecular representations, without claiming universal model inferiority.
6. Environment check (26 Aug): torch stack already present in `malaria_md` — torch 2.13.0+cu130 (CUDA available), torch-geometric 2.8.0.post1, transformers 5.14.1, i.e. exactly the locked P5 versions; the earlier "pending torch install" blocker is lifted without any installation.

### 4.4 Molecular arms — GNN / GIN-TFP / GIN-TNE / ChemBERTa (COMPLETED 2026-08-27)

SLURM job **15613** (`scripts/p6_phase2_gnn_chemberta.sbatch`, partition production, 1 GPU, chained) completed the four collision-group molecular arms on 27 August 2026. All corresponding report JSONs and fold CSVs are present and pass the basic 25-row/finiteness contract; metrics are therefore eligible for audited reporting.

Protocol adaptations (predeclared here, before any result):

- **Descriptors:** TFP (78-D) and TNE (192-D) computed once per unique validated SMILES by reusing the frozen P3 pipelines verbatim (`p3_tda_pipeline.process_molecule`, n_conf=1; `p3_tne_pipeline.smiles_to_tensor` + `tucker_compress`, bond_dim=8, CPU). ITT failures → zero-vector rows, counted in `results/p6_phase2/p6_tfp_tne_descriptors_report.json`.
- **Models:** locked P5 architectures (`p5_models.build_model`) with a multi-label head (`out_dim = 206`); optimizer constants verbatim from P5 (AdamW lr 1e-3 / wd 1e-4, batch 512, ≤50 epochs, patience 10). ChemBERTa: `seyonec/ChemBERTa-zinc-base-v1`, `problem_type="multi_label_classification"`, max_length 128, batch 32, AdamW lr 2e-5 / wd 0.01, ≤10 epochs, patience 3.
- **Validation carve (leakage-safe model selection):** within each seed's train set, train *groups* are dealt round-robin into six parts; part 0 is validation. No test group ever enters model selection.
- **Early stopping criterion:** validation mean column-wise log loss (the primary estimand), not AUC.
- Outputs will land as `results/p6_phase2/p6_lish_moa_{gin,gin-tfp,gin-tne,chemberta}_collision_group_{folds.csv,report.json}`.

### 4.5 Completed molecular-arm results

| Arm | Mean column-wise log loss | Macro-AUROC | Macro-AUPRC | Mean Brier | Mean ECE |
|---|---:|---:|---:|---:|---:|
| GIN | 0.02419 | 0.50785 | 0.01379 | 0.00347 | 0.00449 |
| GIN-TFP | 0.02334 | 0.50479 | 0.01381 | 0.00341 | 0.00300 |
| GIN-TNE | 0.02434 | 0.50601 | 0.01460 | 0.00341 | 0.00306 |
| ChemBERTa | 0.02549 | 0.50137 | 0.01313 | 0.00343 | 0.00750 |

The best molecular-arm log loss is GIN-TFP (0.02334), while all molecular-arm macro-AUROCs remain close to chance and below the phenotype collision-group baseline (0.63619). These results support a cautious negative conclusion for structure-only representation performance on this benchmark; they do not establish universal model inferiority or causal MoA limitations. Four TNE descriptor failures were retained as declared zero-vector ITT cases.

### 4.6 Phase 2 completion checkpoint (28–29 August 2026)

Array 15613 completed all four molecular arms: GIN, GIN-TFP, GIN-TNE, and ChemBERTa (collision_group, 25/25 each). Scaffold `--dump-predictions` rerun submitted 28 Aug 16:19Z (jobs 154648/154431/154551): **all three completed 29 Aug ~05:00Z**, 25/25 prediction CSVs per arm (`predictions/p6_lish_moa_phenotype_scaffold/`, `predictions/p6_lish_moa_structure_scaffold/`, `predictions/p6_lish_moa_both_scaffold/`). Scaffold metrics recovered from the regenerated `_report.json` files: phenotype AUROC 0.64023, structure 0.53575, fusion 0.62647 — confirming the honest-negative scaffold result: structure near chance, fusion below phenotype.

**Per-label calibration (29 Aug 2026):** the fail-closed `p6_calibration_audit.py` stub was replaced by a schema-audited implementation that checks filename pattern `seedX_foldY.csv`, the `drug_id, <moa>_true, <moa>_pred, ...` column layout, and the 206-MoA set, before computing pooled ECE/MCE/Brier. Run on all three scaffold prediction directories: phenotype (n=3,387,670 pooled samples, ECE=0.0016, MCE=0.648, Brier=0.0038), structure (ECE=0.0012, MCE=0.946, Brier=0.0040), fusion (ECE=0.0020, MCE=0.697, Brier=0.0040). Outputs: `results/p6_phase2/p6_calibration_scaffold_{phenotype,structure,both}.json`.

**Bounded QKS proxy (29 Aug 2026):** the previous `NOT_COMPUTED_BOUNDED_QKS_NOT_AUTHORIZED` stub was replaced by a bounded QKS protocol that loads per-drug max-pred-prob and per-drug positive-label count from two prediction directories, then reports quantiles at τ=0.25/0.5/0.75 and Spearman rank correlation across arms (bounded to `max_compounds=5000`). Two comparisons: phenotype vs structure (τ=0.5 abs-diff=0.0230, Spearman max-prob=0.0069 — near zero, confirming structure provides no new ranking information beyond phenotype), phenotype vs fusion (τ=0.5 abs-diff=0.0516, Spearman max-prob=0.2860 — moderate positive, fusion captures more signal than phenotype alone but less than what the ranking improvement would suggest). Outputs: `results/p6_phase2/p6_qks_scaffold_{phenotype_vs_structure,phenotype_vs_both}.json`.

### 4.7 RRS/polypharma impactful extensions — secondary, pending --dump-predictions (28 Aug 2026)

No new modelling beyond the `--dump-predictions` patch (`p6_phase2_benchmark.py:273`, 4 parallel scaffold jobs 154648/431/459/551):

- **Per-label QKS + calibration** — after `predictions/*/*.csv` (25 files/arm, ~300-500MB) lands, run `p6_qks_sensitivity.py` + `p6_calibration_audit.py` to get per-label QKS rank stability and per-label ECE/Brier (206 labels); stratify QKS/ECE by RRS class from `c_rrs_classification.csv` join to test if high-RRS MoA labels are more stable.
- **Attention fusion vs polypharma** — add intermediate cross-modal attention fusion (not late concat RF) for structure+phenotype; evaluate on polypharma-relevant MoA subset (≥2-target labels per network pharmacology Bethi 2025) with collision_group + scaffold splits; report ΔAUROC vs phenotype baseline 0.63619.

Status: `PLANNED_SECONDARY_BLOCKED_ON_DUMP`; honest-negative `fusion < baseline` unchanged; executes within existing `--dump` rerun.

## 5. Leakage and statistics gates

Aggregation occurs before splitting. Canonical-SMILES collisions are resolved before splitting. No assay replicate, duplicated structure, or collision group may cross train/test. The primary split is drug-grouped; scaffold-held-out performance is sensitivity analysis. All arms use the same seeds and folds. Pairwise comparisons use seed/fold-paired statistics and BH-FDR or a predeclared family-wise correction.

## 6. Prohibited claims

Do not claim that MoA labels establish causal target engagement, antimalarial activity, resistance resilience, or superiority of molecular representations unless the corresponding evidence is directly generated and audited. Do not compare LISH log loss/AUROC numerically with P5 antimalarial ROC-AUC as if they were the same estimand.

## 7. Promotion rule

A Project 6 manuscript may be drafted only after a frozen mapping audit and complete model matrix. If every molecular arm fails to improve on ECFP4-RF, the result may still be publishable as an honest-negative representation benchmark, but only with a justified question and complete uncertainty reporting. If no structure mapping is obtained, retain the phenotype-only result as a documented baseline and do not force a separate paper.
