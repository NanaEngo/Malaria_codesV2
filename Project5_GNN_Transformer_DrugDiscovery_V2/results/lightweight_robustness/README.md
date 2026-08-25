# P5 V2 — Lightweight robustness artifacts

**Date:** 25 August 2026  
**Status:** computed secondary analyses; canonical benchmark outputs were not overwritten.

## Inputs

- Canonical panel: `../p5_canonical_panel.csv`
- Official frozen splits: `../../Project5_GNN_Transformer_DrugDiscovery/results/`
- Split SHA-256 values verified against `../SHA256SUMS`

The frozen split files were read in place from the V1 artifact directory. They were not copied,
regenerated, or modified.

## Completed analyses

### Chemical audit

Script: `../scripts/p5_scientific_audit.py`

- scaffold train--test overlap: 0 for all 25 scaffold fold--seed records;
- scaffold test prevalence: 0.586--0.862;
- bounded ECFP4 Tanimoto audit: 500 train and 100 test molecules evaluated per fold;
- mean maximum Tanimoto range: 0.292--0.388 scaffold versus 0.477--0.568 random;
- aggregate salience: top 10% share 17.7% for TFP and 18.0% for TNE.

The Tanimoto analysis is bounded and descriptive; it is not a full all-pairs similarity census.
Individual salience vectors were not archived, so per-run top-k stability is not computed.

### ECFP4 controls

- distance-weighted kNN, k=5:
  - random: AUC 0.9166, AUPRC 0.9562;
  - scaffold: AUC 0.7110, AUPRC 0.8467.
- logistic regression, C=1, sparse scaling, liblinear:
  - random: AUC 0.8790, AUPRC 0.9456;
  - scaffold: AUC 0.7063, AUPRC 0.8542.

The AUPRC values above are computed for these lightweight controls only. Canonical neural
prediction probabilities are not archived, so no neural AUPRC is claimed.

These controls are secondary evidence that the RF result should not be generalized to every
ECFP4 learner. They do not constitute a new neural-model benchmark.

## Not computed

- AUPRC for canonical neural models: prediction probabilities are not archived in canonical CSVs.
- New GIN/TFP/TNE ablation or descriptor-permutation training.
- Additional scaffold partitions with model retraining.
- ChEMBL threshold sensitivity reruns.
- Full standardization audit for tautomers, salts, and stereoisomers.
