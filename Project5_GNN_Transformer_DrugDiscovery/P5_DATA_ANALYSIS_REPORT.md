# P5 Data Analysis Report — active summary

**Scope:** GNN/Transformer drug-discovery benchmark on the canonical P3-derived antimalarial panel.
**Updated:** 25 August 2026
**Long-form history:** `docs/archive/md_full_20260812/P5_DATA_ANALYSIS_REPORT.md`

## 1. Central question

Do learned graph and sequence representations outperform or complement classical fingerprints on a chemically challenging antimalarial panel under random and scaffold splits?

## 2. Canonical panel and protocol

- Panel: **19,836 molecules**, inherited from P3 for direct comparability.
- Splits: fixed random and scaffold splits; five-fold evaluation with repeated seeds.
- Primary metric: ROC-AUC; comparisons are paired on the five per-seed means and corrected with BH-FDR. Displayed ± values are population SD across those five per-seed means; raw 25-fold SDs remain in `results/p5_replication_stats.csv` as `std25`.
- Classical reference: ECFP4-RF.
- Topological fusion: GIN with TFP/TNE features from P3.

## 3. Canonical benchmark

| Model | Random AUC | Scaffold AUC |
|---|---:|---:|
| **ECFP4-RF** | **0.9433 ± 0.0003** | **0.8300 ± 0.0023** |
| ChemBERTa | 0.9121 ± 0.0012 | 0.7867 ± 0.0054 |
| GIN | 0.9098 ± 0.0022 | 0.8047 ± 0.0141 |
| GIN-TFP | — | 0.8138 ± 0.0107 |
| GIN-TNE | — | 0.8090 ± 0.0149 |

Under scaffold splitting, all learned arms remain below ECFP4-RF. GIN-TFP modestly improves over base GIN, but does not close the baseline gap. This is the central honest-negative result, not a failed project.

## 4. External validation and interpretation

The public ChEMBL-derived panel contains **22,447** unique canonical compounds after activity and structure filtering (`p5_public_chembl_malaria.csv`). A canonical-SMILES overlap of **180 compounds** with the P5 panel was excluded, yielding the molecule-disjoint evaluation panel of **22,267** compounds (`p5_public_chembl_malaria_disjoint.csv`). The disjoint panel reproduces the ordering: ECFP4-RF reaches **0.9190** under scaffold split versus **0.8843 ± 0.0021** for GIN (Δ=0.0346, p=3.35×10⁻⁶). These values are a transfer test, not a claim of biological generalisation to every malaria assay; the source outputs and filtering provenance are stored under `Project5_GNN_Transformer_DrugDiscovery/results/`. The separate count of **351 TNE failures** belongs to the P3 descriptor-sensitivity analysis on the broader 22,447-compound panel; it is not a failure count for the P5 ECFP4–GIN benchmark.

Salience analysis identifies persistent-homology/TFP dimensions as interpretable contributors, but salience is model-specific and is not mechanistic evidence. The study supports a practical conclusion: larger learned models do not provide a free predictive advantage over a strong fingerprint baseline at this panel size, while topological fusion can add complementary signal.

## 5. Extended robustness campaign — completed 25 August 2026

A separate, versioned campaign was executed after the canonical benchmark was frozen. It does not overwrite or silently replace the canonical estimates in Section 3.

### 5.1 Design and provenance

- Campaign directory: `Project5_GNN_Transformer_DrugDiscovery_V2/results/extended_campaign_20260825/`.
- Configuration: `campaign_config.json`; producer: `scripts/p5_extended_campaign.py`.
- Post-processing/audit: `scripts/p5_extended_analysis.py`.
- Panel: the frozen 19,836-molecule P5 panel; graph cache read from the V1 artifact and not modified.
- Seeds: 0–4; five folds per seed; 50 epochs maximum; early stopping patience 10; hidden dimension 128; dropout 0.1; AdamW learning rate 1e-3 and weight decay 1e-4; batch size 512.
- Partitions: `canonical_random`, `canonical_scaffold`, and three independent scaffold assignments (`novel_101`, `novel_202`, `novel_303`).
- Configurations: GIN; GIN-TFP native/permuted; GIN-TNE native/permuted.
- Completeness gate: exactly 25 unique fold–seed records per configuration, finite AUC/AUPRC values, and archived fold-level predictions.

The campaign passed the gate: **25/25 configurations**, **625/625 fold–seed records**, and 625 fold-level prediction files. It was executed through SLURM jobs 15463/15464 after a nounset-safe environment correction; the initial failed initialization jobs 15437/15438 produced no scientific results and are retained only as scheduler provenance.

### 5.2 Secondary performance results

On the three novel scaffold partitions, native models produced the following mean ROC-AUC ranges across 25 fold–seed records:

| Configuration | Novel-partition AUC range | Novel-partition AUPRC range |
|---|---:|---:|
| GIN | 0.7886–0.7967 | 0.9025–0.9101 |
| GIN-TFP | 0.8013–0.8105 | 0.9115–0.9160 |
| GIN-TNE | 0.7976–0.8008 | 0.9105–0.9125 |

The three novel partitions preserve the broad scaffold-shift behavior observed in the canonical benchmark. These are robustness estimates under independently generated partitions, not replacements for the primary canonical table and not evidence that any architecture is universally superior.

### 5.3 Descriptor permutation and salience stability

Native-minus-permuted AUC differences were computed as paired contrasts on five per-seed means. GIN-TFP showed positive differences on all three novel partitions (0.0054–0.0139). GIN-TNE showed positive differences on `novel_101` and `novel_303` (0.0092 and 0.0053) and essentially no difference on `novel_202` (-0.0002). Exact sign-flip tests on five paired means were not significant for the novel partitions; the small computational unit is therefore retained as an explicit limitation.

Individual projection-weight vectors were archived for all 20 fusion configurations. For native models across the canonical scaffold and novel partitions, mean pairwise Spearman correlation was 0.755–0.829 for TFP and 0.789–0.835 for TNE; mean top-10% Jaccard overlap was 0.374–0.399 and 0.274–0.326, respectively. These are descriptive stability measures, not causal attributions.

### 5.4 Chemical and ChEMBL robustness audits

The chemical standardization audit found 19,836 valid SMILES, zero exact duplicate rows, zero parent-fragment duplicate rows, and 306 tautomer-collision rows. Labels were not changed. The four prespecified ChEMBL threshold specifications were recomputed with ECFP4-RF only; scaffold AUC ranged from 0.9271 to 0.9608. No full GIN threshold rerun was performed.

### 5.5 Evidence boundary

The extended results provide completed AUPRC, scaffold-partition, descriptor-permutation, salience-stability, and chemical-audit evidence. They remain secondary because the original canonical manuscript estimates were produced under a prior frozen run. A separate extended ChemBERTa rerun was submitted as SLURM array 15490 after the pinned pretrained snapshot became available; at this DAR update it is `RUNNING/PENDING`, with no completed fold result and no metric authorized for interpretation. Per-scaffold error decomposition and prospective experimental validation remain unavailable. All campaign results must be reported with their versioned directory and explicit status.

## 6. Limitations

- The panel is curated and activity labels are inherited; it is not a prospective clinical dataset.
- Scaffold split is a chemical extrapolation test, not a temporal or prospective validation.
- GNN/Transformer performance is architecture- and training-budget-dependent.
- External validation does not replace experimental activity measurements.

## 7. LISH-MoA external mechanism benchmark — completed phenotype-only reference (12 August 2026)

A separate external benchmark is approved for development under the identifier `P5_LISH_MOA_EXTERNAL_V1`. It is an orthogonal multi-label pharmacology task, not a replacement for the molecule-disjoint ChEMBL malaria activity validation and not a direct validation of antimalarial target engagement.

### Data contract and evidence boundary

The raw Kaggle package must contain `train_features.csv`, `train_targets_scored.csv`, and `train_drug.csv`; `train_targets_nonscored.csv` is optional and may be used only for declared auxiliary pre-training. The preparation script will emit a machine-readable audit before any model run. Repeated assay observations are grouped by `drug_id`; labels use an explicitly named `ever_observed_MoA` (maximum across assay conditions). Control samples (`cp_type=ctl_vehicle`) are reported separately, with an optional with/without-control sensitivity run. No direct `drug_id -> SMILES` mapping is assumed. A structure-only arm is enabled only when a versioned mapping with unique `drug_id` rows is supplied; canonical-SMILES collisions are collapsed before splitting and all coverage/collision/unmapped counts are recorded.

### Locked evaluation design

- Phenotype-only arm: gene-expression/cell-viability features plus dose/time metadata → 206 scored MoA labels.
- Structure-only arm: ECFP4 and, where available, GNN/Transformer representations → aggregated drug-level MoA labels.
- Optional multimodal arm: structure plus phenotype, treated as a separate exploratory model.
- Primary metric: mean column-wise log loss; secondary metrics: macro/micro AUPRC, macro AUROC, mean Brier score, and expected calibration error.
- Splits: drug-grouped split first; Bemis–Murcko scaffold split for structure-mapped data. No assay replicate may occur across train and test.
- Nonscored targets are not part of the headline evaluation and cannot be used to imply improved scored-label generalization.

### Data-access checkpoint — public annotated mirror (12 August 2026)

No Kaggle credential is available on the HPC node. The reproducible fallback is the public annotated archive documented at `https://github.com/pablormier/kaggle-lish-moa-annotated`, which states that it combines the original competition data and retains the training subset (`n=23,814`, 206 scored labels). The official organizer mapping repository is `https://github.com/LISHarvard/moa_challenge`. The archive will be downloaded outside Git, hashed before conversion, and treated as a provenance-preserving mirror rather than as a new experimental dataset. The raw archive and any credentials remain excluded from the repository.

**Execution checkpoint:** the mirror was downloaded on 12 August 2026 to `/home/nanaengo/lish_moa_data/`; SHA256 is `bc151c7788fea242d2ff0b0f6260bec4df6a09bb395ff4607a34a86a545e77dd` (64,614,297 bytes). Its extracted plain CSV contains 23,814 training observations, 772 gene features, 100 viability features, and 608 labels, with the first 206 treated as scored labels according to the mirror documentation. No SMILES are present; therefore only the phenotype-only P5 arm can proceed from this artifact. Structure-based P3/P5 arms remain `BLOCKED_NO_STRUCTURE_MAPPING`.

**Superseded historical execution checkpoint — job 15273 (12 August 2026; observation timestamp approximately 13:56:07 UTC, derived from `StartTime + RunTime`):** This is a historical checkpoint, not a current-status guarantee. At that observation, SLURM reported `RUNNING` on `penavoraserver` (`production` partition; 16 CPUs; 32 GB RAM), with `RunTime=01:33:34`, `StartTime=12:22:33`, and a four-hour hard limit ending at `16:22:33`. The wrapper executes two declared phenotype-only conditions sequentially: (i) `drug_grouped` with controls and (ii) `drug_grouped` with `--exclude-controls`; the optional structure/scaffold command is conditional on the later presence of `results/lish_moa/lish_moa_structure_mapped.csv`, which was absent at this checkpoint. The Python process was active at approximately 100% CPU, while the SLURM stdout/stderr files remained empty because the script does not emit intermediate metrics. Only preparation artifacts were present (`lish_moa_prepare_report.json`, `lish_moa_data_contract.md`, and `lish_moa_drug_level.csv`); no fold CSV or metric JSON was available yet. The remaining wall-clock allowance at observation was approximately 2 h 26 min, but completion time could not be estimated more precisely without intermediate checkpoints. Status: `LISH_MOA_P5_PHENOTYPE_RUNNING`; no number from this job may enter the manuscript until both report JSON files and fold CSVs are parsed and pass the predefined audit gates.

**Audited result checkpoint — condition (i) with controls COMPLETED (12 August 2026, ~14:05 UTC):** `p5_lish_moa_phenotype_drug_grouped_report.json` and `p5_lish_moa_phenotype_drug_grouped_folds.csv` were produced and **pass the fold-level audit gate**: 25 rows (5 seeds × 5 folds, 5 folds per seed), 0 NaN/inf values, `n_drugs = 3289`, `n_labels = 206`. Mean metrics over 25 folds: **mean column-wise log loss = 0.02378** (primary), **macro-AUPRC = 0.1428**, **macro-AUROC = 0.6435**, mean Brier = 0.00374, mean ECE = 0.00376. Per-seed macro-AUROC is stable (0.6398–0.6465), indicating no seed pathology. Labels with test-set variation: 140–155 per fold (mean 148.2 / 206), i.e. ≈72% of MoA labels retain discriminative signal under drug-grouped splits; the remainder are too rare for fold-level AUROC and are excluded from the macro average per fold. Protocol: unweighted per-label logistic baseline on phenotype features, drug-level aggregation — deliberately the weakest benchmark arm, so any upstream method must beat 0.6435 macro-AUROC on the same fold grid. Interpretation field of the report: "MoA-associated prediction; not causal target engagement". At this earlier checkpoint, condition (ii) with `--exclude-controls` was still RUNNING; its report JSON and folds CSV were not yet present. This status was superseded by the completed condition-(ii) audit below.

**Result checkpoint — condition (ii) without controls COMPLETED (12 August 2026, ~15:49 UTC) + conditions comparison:** `p5_lish_moa_phenotype_drug_grouped_no_controls_report.json` and `_folds.csv` were produced and **pass the same fold-level audit gate** (25 folds, 0 NaN, report/fold mean consistent). Mean over 25 folds (n = 3,288 drugs, 206 labels): log loss **0.02389**, macro-AUPRC **0.1412**, macro-AUROC **0.6417**, Brier 0.00375, ECE 0.00381; per-seed AUROC stable (0.6378–0.6480). **Comparison (both conditions fully audited; reproducible via `scripts/p5_lish_moa_compare.py` → `results/lish_moa/p5_lish_moa_conditions_comparison.json`):** removing the vehicle controls changes nothing material — Δlog loss = +0.00011, Δmacro-AUROC = −0.00177, Δmacro-AUPRC = −0.00152 (n_drugs 3,289 → 3,288). **Verdict: the phenotype-driven baseline is robust to control exclusion; the locked benchmark is now final** — log loss 0.02378 (primary), macro-AUROC 0.6435, macro-AUPRC 0.1428 on the 25-fold drug-grouped grid with controls. Both conditions are documented and the manuscript gate is satisfied: any upstream P5 method must beat 0.6435 macro-AUROC (or 0.02378 log loss) on the same fold grid.

### Completion status and retained scope

The phenotype-only benchmark is complete and has passed the predefined audit gates: both declared conditions contain 25 fold records (5 seeds × 5 drug-grouped folds), zero NaN/inf metric cells, and report/fold means that agree. The reproducible comparison is implemented in `scripts/p5_lish_moa_compare.py`; the audited comparison JSON and fold outputs are retained under `results/lish_moa/`. The structure-only and scaffold branches remain intentionally unexecuted because no versioned drug--SMILES mapping with unique `drug_id` rows is available. The completed result is therefore a bounded phenotype-only reference, not a structure-to-MoA benchmark.

### Decision — no structure-model gain claim on LISH-MoA at present

**Decision status: `DO_NOT_RUN_STRUCTURE_ARM` / `NO_LISH_MOA_MODEL_GAIN_CLAIM`.** The existing P5 molecular GNN, ChemBERTa, GIN--TFP, and GIN--TNE models must not be evaluated on the LISH grid, and their molecular ROC-AUC results must not be compared with the LISH phenotype-only baseline. The current artifact has no versioned mapping with unique `drug_id` rows; without it, molecular features, canonical-SMILES collision handling, and scaffold-held-out splits cannot be audited. A newly designed phenotype-only neural model would be a different experiment and could not support a claim about the molecular representations studied in P5. The LISH result therefore remains an orthogonal phenotype reference only.

A future structure-based LISH arm may be opened only after all of the following are recorded: (i) the exact mapping release and hash, with unique `drug_id` rows; (ii) mapping coverage, invalid-SMILES count, duplicate-ID count, and an explicit canonical-SMILES collision-collapse policy; (iii) molecule-disjoint drug-grouped and Bemis--Murcko scaffold splits with no replicate leakage; (iv) an ECFP4--RF reference on the same folds; (v) independently trained GNN, ChemBERTa, and GIN--TFP/GIN--TNE arms with declared hyperparameters; and (vi) paired fold/seed comparisons with multiplicity correction. Any resulting gain would be a LISH MoA-associated prediction result, not evidence of causal target engagement, antimalarial activity, or resistance resilience.

### Interpretation boundary

A predicted MoA-associated profile is not proof of direct target engagement or causality. LISH-MoA results may support biological representation transfer in P5, but cannot be used to claim antimalarial activity, resistance resilience, or PfDHFR/PfCRT/PfATP4/PfClpP engagement.

## 8. Current manuscript status

The canonical P5 V2608 manuscript now reports the audited LISH phenotype-only reference as a separate public benchmark, with explicit non-comparability to the molecular ROC-AUC results and an explicit boundary against causal target-engagement claims. The active narrative remains the honest-negative molecular benchmark plus interpretable topological complementarity; no claim that GNNs or Transformers universally underperform is made.

## 9. Next actions

1. Preserve the fixed panel/splits and the leak-audited benchmark outputs.
2. Finalise the deposit manifest and Zenodo/GitHub release.
3. Complete author-level metadata and final prose review.
4. Keep exploratory generation or larger-model experiments out of the submission package unless they answer a pre-specified question.
