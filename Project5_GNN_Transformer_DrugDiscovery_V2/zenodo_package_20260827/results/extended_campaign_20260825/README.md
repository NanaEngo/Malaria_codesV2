# P5 V2 extended campaign — 25 August 2026

**Status:** `COMPUTED` for the GNN matrix and all declared post-processing audits.

This campaign is a versioned secondary robustness analysis. It does not overwrite or silently replace the canonical manuscript estimates.

## Completed matrix

- 5 partitions: `canonical_random`, `canonical_scaffold`, `novel_101`, `novel_202`, `novel_303`;
- 5 configurations per partition: GIN, GIN-TFP native/permuted, GIN-TNE native/permuted;
- 5 seeds × 5 folds per configuration;
- 25 configurations × 25 records = 625 fold-seed evaluations;
- fold-level test probabilities and AUPRC archived;
- individual salience vectors archived for the 20 fusion configurations.

Training used the frozen P5 panel and graph cache, the declared 50-epoch/10-patience AdamW protocol, and GPU execution under the recorded environment. New scaffold partitions are independent greedy scaffold assignments with zero train-test scaffold overlap; their exact indices and hashes are recorded under `splits/` and `campaign_config.json`.

## Main secondary observations

On the three new partitions, native mean ROC AUC was:

- GIN: 0.7886–0.7967;
- GIN-TFP: 0.8013–0.8105;
- GIN-TNE: 0.7976–0.8008.

Native mean AUPRC ranged from 0.9025 to 0.9160 across these native configurations. These values are secondary robustness estimates, not replacements for the primary canonical table.

Descriptor permutation reduced mean AUC numerically for GIN-TFP on all three new partitions (native-minus-permuted ΔAUC 0.0054–0.0139). GIN-TNE showed positive differences on two partitions and essentially no difference on `novel_202`. Exact sign-flip tests on the five per-seed means were not significant for the new partitions. Therefore the result supports, but does not prove, a modest contribution from the native descriptor arrays.

## Salience stability

For native fusion models across the canonical scaffold and three novel partitions:

- TFP pairwise Spearman correlation: 0.755–0.829;
- TFP top-10% Jaccard overlap: 0.374–0.399;
- TNE pairwise Spearman correlation: 0.789–0.835;
- TNE top-10% Jaccard overlap: 0.274–0.326.

These are stability diagnostics for projection-weight patterns. They are not causal feature attributions or pharmacophore claims.

## Additional audits

- Chemical standardization: 19,836 valid SMILES; zero exact duplicate rows; zero parent-fragment duplicate rows; 306 tautomer-collision rows. Labels were not altered.
- ChEMBL threshold sensitivity: four prespecified RF-only specifications completed; scaffold AUC 0.9271–0.9608. No full GIN threshold rerun was performed.

## Deliberate boundaries

ChemBERTa was not rerun because pretrained weights were not available locally. Per-scaffold error decomposition was not added. The extended GNN results must not be presented as a new universal ranking claim, and canonical historical AUPRC values must not be backfilled from these distinct reruns.

## Reproduction

```bash
/home/nanaengo/miniforge3/envs/malaria_md/bin/python3 scripts/p5_extended_analysis.py
```

The analysis script fails closed if any expected configuration lacks exactly 25 unique seed-fold records or contains invalid metrics.
