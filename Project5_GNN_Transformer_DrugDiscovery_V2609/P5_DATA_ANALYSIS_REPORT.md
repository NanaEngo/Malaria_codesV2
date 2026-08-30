# P5 Data Analysis Report — active summary

**Scope:** GNN/Transformer drug-discovery benchmark on the canonical P3-derived antimalarial panel.
**Updated:** 30 August 2026
**Release audit:** Reviewer #3 mitigation pass; P5V2 remains author-controlled and not uploaded.
**Conda environment**: `malaria_md` (Python 3.11, PyTorch 2.13.0, PyG 2.8.0, Transformers 5.14.1)
**Long-form history:** `docs/P5_DAR_OPERATIONAL_LOG.md`

## 1. Central question

Under chemical-distribution shift, does the representation–task alignment of learned graph and sequence models compensate for their out-of-distribution extrapolation deficit relative to ECFP4 fingerprints on a curated antimalarial natural-product panel, or are the fingerprint advantages confined to the out-of-distribution tail?

The original "outperform or complement" formulation is reframed here as a Molecular Out-Of-Distribution (MOOD) characterisation, in line with the 2024–2026 literature on real-world chemical shift \citep{sheridan2024realworld}, distance-aware uncertainty quantification \citep{unique2026uq}, and the limits of scaffold-based split conventions \citep{bash2025umap}.

## 2. Canonical panel and protocol

- Panel: **19,836 molecules**, inherited from P3 for direct comparability.
- Splits: fixed random and scaffold splits; five-fold evaluation with repeated seeds.
- Primary metric: ROC-AUC; comparisons are paired on the five per-seed means and corrected with BH-FDR.
- Classical reference: ECFP4-RF.
- Topological fusion: GIN with TFP/TNE features from P3.

## 3. Canonical benchmark

| Model | Random AUC | Scaffold AUC |
|---|---:|---:|
| **ECFP4-RF** | **0.9433 ± 0.0003** | **0.8300 ± 0.0023** |
| ChemBERTa | 0.9121 ± 0.0012 | 0.7867 ± 0.0054 |
| GIN | 0.9098 ± 0.0022 | 0.8047 ± 0.0141 |
| GIN-TFP | 0.9084 ± 0.0012 | 0.8138 ± 0.0107 |
| GIN-TNE | 0.8918 ± 0.0018 | 0.8090 ± 0.0149 |

Under scaffold splitting, all learned arms remain below ECFP4-RF. GIN-TFP modestly improves over base GIN, but does not close the baseline gap. This is the central honest-negative result, not a failed project.

## 4. External validation and interpretation

The public ChEMBL-derived panel contains **22,447** unique canonical compounds; after excluding 180 overlaps, the molecule-disjoint evaluation panel has **22,267** compounds. ECFP4-RF reaches **0.9190** under scaffold split versus **0.8843 ± 0.0021** for GIN. These values are a transfer test, not a claim of biological generalisation to every malaria assay.

## 5. Extended robustness campaign — headline results

### 5.1 Novel scaffold partitions

| Configuration | Novel-partition AUC range | Novel-partition AUPRC range |
|---|---:|---:|
| GIN | 0.7886–0.7967 | 0.9025–0.9101 |
| GIN-TFP | 0.8013–0.8105 | 0.9115–0.9160 |
| GIN-TNE | 0.7976–0.8008 | 0.9105–0.9125 |

### 5.2 Descriptor permutation

GIN-TFP showed positive differences on all three novel partitions (0.0054–0.0139). GIN-TNE positive on novel_101 and novel_303 (0.0092 and 0.0053). Exact sign-flip tests not significant; small computational unit retained as explicit limitation.

### 5.3 Chemical and ChEMBL audits

Chemical standardization: 19,836 valid SMILES, zero duplicates, 306 tautomer-collision rows. ChEMBL threshold specifications: scaffold AUC ranged from 0.9271 to 0.9608 (ECFP4-RF only).

### 5.4 Post-hoc calibration

ECE rises from ≈0.03 (random split) to ≈0.07–0.13 (scaffold/novel partitions); ChemBERTa shows the largest calibration error under scaffold shift (ECE 0.12–0.13).

### 5.5 NN-Tanimoto decile stratification

ECFP4-RF beats every learned arm in deciles 1–9; all five arms converge to ≈0.88 in decile 10. The fingerprint advantage is driven by the novel half of the test set, not by aggregate AUC averaging.

### 5.6 Butina scaffold-cluster split

| Arm | Butina AUC |
|---|---:|
| ECFP4-RF | 0.8331 |
| GIN-TFP | 0.8232 |
| GIN | 0.8202 |
| GIN-TNE | 0.8191 |
| ChemBERTa | 0.7776 |

ECFP4-RF above every learned arm, consistent with canonical scaffold-split ordering.

### 5.7 GNN capacity sensitivity

| Configuration | Scaffold AUC |
|---|---:|
| hidden=64 / dropout=0.2 | 0.8081 |
| hidden=128 / dropout=0.1 (canonical) | 0.8047 |
| hidden=256 / dropout=0.1 | 0.8000 |

All three remain below ECFP4-RF scaffold reference (0.8300); gain from enlarging GIN capacity is flat-to-negative.

### 5.8 Lightweight ECFP4 controls

| Control | Random AUC | Scaffold AUC |
|---|---:|---:|
| kNN (k=5) | 0.9166 | 0.7110 |
| Logistic (C=1) | 0.8790 | 0.7063 |

Both fall below ECFP4-RF on both splits. The ECFP4-RF advantage does not generalize to every ECFP4-based learner — the random-forest component is responsible for the bulk of the scaffold-split performance.

## 6. RRS/polypharma calibration extensions

Calibration per RRS class: ECE rises universally from random to scaffold/novel; no evidence that high-RRS candidates retain better calibration. Polypharma subset: n=6 available-target candidates (PP-01/02/06/11/13/15), all arms show negative ΔAUC vs single-target. Low n precludes bootstrap CI95; descriptive only.

## 7. Evidence status and limitations

All extended results are secondary robustness estimates. They do not replace the canonical benchmark. Per-scaffold error decomposition and prospective experimental validation remain unavailable. Calibration slope/intercept fits and recalibrated variants remain `NOT_COMPUTED`.

- The panel is curated and activity labels are inherited; it is not a prospective clinical dataset.
- Scaffold split is a chemical extrapolation test, not a temporal or prospective validation.
- GNN/Transformer performance is architecture- and training-budget-dependent.
- External validation does not replace experimental activity measurements.

## 8. LISH-MoA external benchmark

Phenotype-only baseline: log loss 0.02378, macro-AUROC 0.6435, macro-AUPRC 0.1428 (25-fold drug-grouped grid). Robust to control exclusion (Δlog loss = +0.00011). No structure-mapping arm executed. The existing molecular models must not be evaluated on LISH grid. Interpretation: MoA-associated prediction, not causal target engagement.

## 9. Current manuscript status

**Release status:** `COMPUTED_PRIMARY_PLUS_AUDITED_SECONDARY; MANUSCRIPT_READY_FOR_AUTHOR_REVIEW`.

**Final manuscript package:** main text 18 pages (`P5_manuscript_V2608.tex`), SI 6 pages (`P5_SI_V2608.tex`: S1 LISH, S2 calibration, S3 GNN hyperparameter sensitivity, S4 paired contrasts, Butina, NN-Tanimoto deciles), cover letter 1 page (tightened in the author pass). Zero LaTeX errors, zero undefined references. Zenodo package: 31/31 files staged, `READY_FOR_UPLOAD_NOT_UPLOADED`. Target journal: JCAMD.

**Editorial leviers applied (27 Aug 2026):**
1. Novelty discussion positioned against Guo & Ding 2026, 25-embedding benchmark, Boldini 2024.
2. LISH moved to SI (S1), main text keeps compact summary with 7 pointers.
3. GNN hyperparameter sensitivity added (§5.7).
4. Cover letter recentered on two contributions.
5. Abstract/Contribution/Highlights reformulated.

**Open items (author action only):** final target-journal confirmation, author names/affiliations/ORCID verification, visual PDF read-through, Zenodo upload with DOI verification, tagged GitHub release.

## 9b. Author / reviewer / editor-associate pass (30 Aug 2026) \u2014 trace

Author read, adversarial re-derivation, and AE verdict applied. Final compile: main **18 p.** / SI **6 p.** / cover **1 p.**, 0 errors, 0 undefined refs/citations.

**Author pass fixes:**
- SM \u00a71 duplicated sentence (LISH paragraph repeated verbatim) removed.
- Cover letter tightened from 2 p. to **1 p.** (margin 1.9\u21921.7 cm + prose trim).
- GIN--TFP primary locked at **0.8138 \u00b1 0.0107** (`p5_replication_stats.json`); an extended-campaign secondary recompute writes 0.8167 \u2014 gap ~0.003, manuscript cites the locked primary.

**Reviewer re-derivation (all \u2713):** ECFP4-RF 0.9433/0.8300; scaffold adjusted p 0.0330/0.0330/0.0378/0.0002; salience 0.0485/0.0790/0.0547 (top dims {42,43,52,53,54}, top-10% 0.177); ChEMBL 22447/22267; Butina 0.8331/0.8232/0.8202/0.8191. All confirmed against their source JSONs.

**Butina housekeeping fixed:** `butina_summary.json` held only ChemBERTa, all `BLOCKED` (summary script read old renamed path). Recomputed ChemBERTa 0.7776 from the 25 stored prediction CSVs (confirmed); regenerated the summary for all 5 arms on the canonical path. No manuscript number changed.

**AE verdict:** submit to JCAMD as a negative-result calibration study. Strength = bounded honesty; central reviewer risk (aggregate negative restates known benchmarks) countered by the NN-Tanimoto OOD-tail localisation and the two protocol safeguards.

## 10. Next actions

1. Preserve the fixed panel/splits and the leak-audited benchmark outputs.
2. Finalise the deposit manifest and Zenodo/GitHub release.
3. Complete author-level metadata and final prose review.
4. Keep exploratory generation or larger-model experiments out of the submission package.
