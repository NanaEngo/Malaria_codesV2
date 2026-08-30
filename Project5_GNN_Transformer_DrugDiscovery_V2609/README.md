# P5 — GNN/Transformer drug-discovery benchmark

**Status:** benchmark and public-panel validation complete; manuscript package requires final author/deposit checks.
**DAR:** `P5_DATA_ANALYSIS_REPORT.md`

## Scientific question

Do learned graph/sequence representations outperform or complement ECFP4 on a curated antimalarial panel under scaffold extrapolation?

## Canonical results

The table reports mean ROC AUC ± population SD across the five per-seed means (each seed averages five test folds). Raw fold-level SD across all 25 records is retained separately in `results/p5_replication_stats.csv` as `std25`.

| Model | Random | Scaffold |
|---|---:|---:|
| **ECFP4-RF** | **0.9433 ± 0.0003** | **0.8300 ± 0.0023** |
| ChemBERTa | 0.9121 ± 0.0012 | 0.7867 ± 0.0054 |
| GIN | 0.9098 ± 0.0033 | 0.8047 ± 0.0141 |
| GIN-TFP | 0.9084 ± 0.0038 | 0.8138 ± 0.0107 |
| GIN-TNE | 0.8918 ± 0.0018 | 0.8090 ± 0.0149 |

On the independent public malaria panel (`n=22,267`), ECFP4-RF reaches 0.9190 versus GIN 0.8843 ± 0.0021 under scaffold split (Δ=0.0346, p=3.35×10⁻⁶). GIN-TFP adds modest complementary signal but does not surpass ECFP4-RF.

## LISH-MoA external extension (phenotype-only reference complete; structure arm not computed)

A separate `P5_LISH_MOA_EXTERNAL_V1` pipeline is prepared under `scripts/p5_lish_moa_prepare.py` and `scripts/p5_lish_moa_benchmark.py`. The audited phenotype-only baseline uses drug-level aggregation, mean column-wise log loss, macro-AUPRC/AUROC, and calibration-oriented reporting. The locked reference is log loss 0.02378, macro-AUROC 0.6435, and macro-AUPRC 0.1428 on 3,289 drugs and 206 labels. A structure-only arm remains disabled because no audited one-to-one `drug_id → SMILES` mapping is available. This extension is not an antimalarial activity validation and does not alter the canonical panel or manuscript molecular results.

## Evidence boundary

The result is an honest-negative benchmark, not a claim that all GNNs or Transformers universally underperform. The panel is curated, scaffold split is a chemical extrapolation test, and external validation does not replace experimental activity measurements.

## Canonical locations

- Panel/splits/results: `results/`
- Scripts: `scripts/`
- Manuscript/figures: `manuscript/`
- Active DAR: `P5_DATA_ANALYSIS_REPORT.md`
- Strategic planning (non-canonical): `P5_STRATEGIC_PA90.md`
