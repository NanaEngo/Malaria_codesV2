# P5 — GNN/Transformer drug-discovery benchmark

**Status:** benchmark and public-panel validation complete; manuscript package requires final author/deposit checks.
**DAR:** `P5_DATA_ANALYSIS_REPORT.md`

## Scientific question

Do learned graph/sequence representations outperform or complement ECFP4 on a curated antimalarial panel under scaffold extrapolation?

## Canonical results

| Model | Random | Scaffold |
|---|---:|---:|
| **ECFP4-RF** | **0.9433 ± 0.0002** | **0.8300 ± 0.0023** |
| ChemBERTa | 0.9121 ± 0.0047 | 0.7867 ± 0.0338 |
| GIN | 0.9098 ± 0.0067 | 0.8047 ± 0.0395 |
| GIN-TFP | — | 0.8138 ± 0.0352 |
| GIN-TNE | — | 0.8090 ± 0.0378 |

On the independent public malaria panel (`n=22,267`), ECFP4-RF reaches 0.9190 versus GIN 0.8843 ± 0.0021 under scaffold split (Δ=0.0346, p=3.35×10⁻⁶). GIN-TFP adds modest complementary signal but does not surpass ECFP4-RF.

## LISH-MoA external extension (isolated, not yet computed)

A separate `P5_LISH_MOA_EXTERNAL_V1` pipeline is prepared under `scripts/p5_lish_moa_prepare.py` and `scripts/p5_lish_moa_benchmark.py`. It evaluates multi-label mechanism-of-action prediction with drug-level aggregation, mean column-wise log loss, macro-AUPRC/AUROC, and calibration-oriented reporting. A structure-only arm is enabled only after an audited one-to-one `drug_id → SMILES` mapping. This extension is not an antimalarial activity validation and does not alter the canonical panel or manuscript results until its mapping and leakage gates pass.

## Evidence boundary

The result is an honest-negative benchmark, not a claim that all GNNs or Transformers universally underperform. The panel is curated, scaffold split is a chemical extrapolation test, and external validation does not replace experimental activity measurements.

## Canonical locations

- Panel/splits/results: `results/`
- Scripts: `scripts/`
- Manuscript/figures: `manuscript/`
- Active DAR: `P5_DATA_ANALYSIS_REPORT.md`
- Strategic planning (non-canonical): `P5_STRATEGIC_PA90.md`
