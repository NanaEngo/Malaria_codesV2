# LISH-MoA external benchmark (P5/P3 bridge)

This directory is reserved for the isolated `P5_LISH_MOA_EXTERNAL_V1` analysis.
It is not part of the canonical P5 antimalarial panel or the canonical P3 AUC
benchmark until its audit gates pass.

## Execution order

1. Obtain the official Kaggle package outside Git and place the raw files in a private directory.
2. Run `p5_lish_moa_prepare.py --raw-dir ...` with no structure mapping first.
3. Audit `lish_moa_prepare_report.json` and `lish_moa_data_contract.md`.
4. If, and only if, a versioned mapping with unique `drug_id` rows is available, rerun with `--mapping-csv`. If several IDs resolve to one canonical SMILES, the preparer collapses them explicitly (labels=max, covariates=mean) and records the collision count.
5. Run the P5 phenotype benchmark; run structure-only only on the mapped artifact.
6. Run the P3 descriptor benchmark on the mapped artifact.
7. Treat QKS as a separate bounded experiment; it is not computed by the descriptor runner.

## Scientific boundary

MoA labels are phenotype-associated multi-label endpoints. They do not establish
causal target engagement, antimalarial activity, or resistance resilience.
Primary metric is mean column-wise log loss; macro AUPRC, AUROC, and calibration
are secondary. All splits occur after drug-level aggregation, so assay replicates
cannot cross train/test. Raw Kaggle files and credentials must not be committed.

## Live checkpoint — job 15273 (12 August 2026)

The phenotype benchmark was submitted through `scripts/p5_lish_moa_benchmark.sbatch` as SLURM job `15273`. The wrapper runs the phenotype-only `drug_grouped` condition with controls and then repeats it with `--exclude-controls`; a structure/scaffold run is conditional on a verified `lish_moa_structure_mapped.csv`, which was not present at submission. At the latest recorded checkpoint (approximately 13:56:07 UTC; historical status), the job was `RUNNING` on the production partition with 16 CPUs and 32 GB RAM. Only the preparation artifacts were present; final fold CSVs and metric JSON reports were not yet available. No result from this job is reportable or manuscript-ready until both phenotype reports and their fold-level audit have been checked.

## Result checkpoint — condition with controls COMPLETED (12 August 2026, ~14:05 UTC)

`p5_lish_moa_phenotype_drug_grouped_report.json` + `_folds.csv` produced and audited (25 folds, 0 NaN, stable per-seed AUROC). Summary over 25 folds (n = 3,289 drugs, 206 labels): mean column-wise log loss **0.02378**; macro-AUPRC **0.1428**; macro-AUROC **0.6435**; ≈72% of labels retain test-set variation per fold. Baseline = unweighted per-label logistic on phenotype features, drug-grouped split. ## Result checkpoint — condition without controls COMPLETED + comparison (12 August 2026, ~15:49 UTC)

`p5_lish_moa_phenotype_drug_grouped_no_controls_report.json` + `_folds.csv` produced and audited (25 folds, 0 NaN). Mean over 25 folds (n = 3,288 drugs, 206 labels): log loss **0.02389**; macro-AUPRC **0.1412**; macro-AUROC **0.6417**; per-seed AUROC 0.6378–0.6480.

**Comparison (reproducible: `scripts/p5_lish_moa_compare.py`):** removing the vehicle controls changes nothing material — Δlog loss = +0.00011, Δmacro-AUROC = −0.00177, Δmacro-AUPRC = −0.00152. **Verdict: baseline robust to control exclusion; benchmark final.** Locked grid: 5 seeds × 5 folds, `drug_grouped`, with controls — log loss 0.02378 (primary), macro-AUROC 0.6435, macro-AUPRC 0.1428. Any upstream P5 method must beat these values on the same fold grid.
