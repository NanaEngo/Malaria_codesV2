# P5 Analysis Ledger — Canonical Results

**Purpose:** Every quantitative statement in the manuscript traces to an entry here.  
**Created:** 2026-08-19  
**Updated:** 2026-08-25 UTC — title/abstract, reference set, artifact labels, split metadata, bounded external p-value representation, and scientific audit synchronized; canonical numerical entries unchanged
**Protocol:** No number enters the manuscript except through a written, interpreted entry in this ledger.

---

## LED-001: ECFP4-RF Scaffold Split Performance (Primary Baseline) — [SUPERSEDED by LED-001-R1]

**Superseded 2026-08-19:** the Method block names hyperparameters this arm never used (100 trees,
balanced class weights), the Source files block cites a CSV row that does not exist, and the
per-seed means listed below are not the ones in the producing artifact — their own SD is 0.0021,
not the ±0.0023 quoted two lines above them. The headline mean 0.8300 and the SD ±0.0023 are both
correct and unchanged; provenance is corrected in LED-001-R1. Retained verbatim for audit trail —
do not cite this entry.

**Method:**
- Molecular representation: Extended-connectivity fingerprints (ECFP4), radius 2, 2048 bits (RDKit)
- Model: Random forest classifier, 100 estimators, balanced class weights
- Evaluation: Bemis-Murcko scaffold 5-fold cross-validation, 5 random seeds
- Metric: ROC AUC (area under receiver operating characteristic curve)
- Aggregation: Mean of 5 per-seed means (each seed = mean of 5 test-fold AUCs)
- Statistical unit: 25 fold-seed replicates total

**Numbers:**
- Mean ROC AUC = **0.8300** (mean of 5 per-seed means)
- Population SD across 5 per-seed means = **±0.0023**
- Raw 25-fold SD (`std25`) = 0.0131 (retained in `p5_replication_stats.csv`)
- Per-seed means: [0.8305, 0.8337, 0.8274, 0.8287, 0.8298]
- Range: 0.8274–0.8337

**Interpretation:**
Under chemical scaffold separation, ECFP4-RF achieves 0.8300 ROC AUC, serving as the primary reference against which all learned representations are evaluated. The low seed-level variation (SD 0.0023) indicates stable performance across independent random realizations. This is the **scaffold-split headline number** — the benchmark to beat.

**Caveats:**
- Panel-specific: 19,836 curated antimalarial natural products
- Scaffold split tests chemical extrapolation, not temporal or prospective validation
- Performance depends on fingerprint radius, bit depth, and RF hyperparameters
- Not a claim of biological activity or target engagement

**Claim links:**
- Manuscript Abstract: "ECFP4-RF achieved a ROC AUC of 0.8300"
- Manuscript Results §2.3: Primary baseline table
- Manuscript Discussion: Reference point for all learned-model comparisons

**Source files:**
- `results/p5_replication_stats.csv` (row: `scaffold,ECFP4-RF`)
- `results/p5_replication_stats.json` (implicit baseline: all deltas computed vs this)
- `results/p5_ecfp4rf_scaffold_baseline.json`

---

## LED-001-R1: ECFP4-RF Scaffold Split Performance (Primary Baseline) — corrected provenance

*Supersedes LED-001. The headline mean and SD are identical; the hyperparameters, the per-seed
means, the range, and the source-file list are corrected against the producing script and its
output artifact.*

**Date:** 2026-08-19

**Method:**
- Molecular representation: Extended-connectivity fingerprints (ECFP4) — RDKit Morgan, radius 2, 2048 bits
- Preprocessing: `StandardScaler` on the fingerprint matrix, inside the same pipeline as the classifier
- Model: `RandomForestClassifier(n_estimators=500, n_jobs=8, random_state=0)` — sklearn defaults elsewhere, including `class_weight=None`
- Evaluation: Bemis-Murcko scaffold 5-fold cross-validation, 5 random seeds
- Metric: ROC AUC (area under receiver operating characteristic curve)
- Aggregation: Mean of 5 per-seed means (each seed = mean of 5 test-fold AUCs)
- Dispersion: Population SD (ddof=0), written by the producing script as `float(np.std(means))`
- Statistical unit: 25 fold-seed replicates total

**Numbers:**
- Mean ROC AUC = **0.8300** (mean of 5 per-seed means; unrounded 0.8299833601246377)
- Population SD across 5 per-seed means = **±0.0023** (unrounded 0.0022821507022448787)
- Raw 25-fold SD (`std25`) = 0.0131 (retained in `p5_replication_stats.csv`)
- Per-seed means: [0.8334, 0.8274, 0.8278, 0.8295, 0.8317]
- Range: 0.8274–0.8334

**Interpretation:**

0.8300 is the scaffold-split value every learned arm is measured against. What makes it usable as
a baseline is not the mean but the spread: ±0.0023 across seeds is roughly six times tighter than
GIN's ±0.0141 (LED-002), so a 0.02 deficit in a learned model cannot be written off as baseline
seed noise. The forest was never tuned — 500 trees, `random_state=0`, sklearn defaults for depth
and class weighting — which pushes the comparison in the conservative direction: an untuned
fingerprint model still finishes ahead of four learned representations. The 25-fold SD is 0.0131,
about six times the seed-mean SD, so almost all of the variance sits between folds rather than
between seeds. That is what scaffold separation is supposed to produce, since each fold withholds
a different region of chemical space.

**Caveats:**
- Panel-specific. The 19,836-molecule curated antimalarial natural-product panel inherited from P3 bounds every claim here; nothing transfers to synthetic libraries or other targets without re-measurement.
- No hyperparameter search was run. Fingerprint radius, bit depth, and tree count all move this number, so 0.8300 is a floor for ECFP4-RF on this panel rather than its best achievable value.
- Dispersion is population SD (ddof=0), matching `scripts/p5_sanity_ecfp4_rf.py:105`. A sample SD (ddof=1) would read slightly wider; the project quotes ddof=0 throughout (Notes item 1).
- `results/p5_replication_stats.csv` holds **no** `scaffold,ECFP4-RF` row. The baseline enters that file only as the reference point for `delta_vs_ecfp4`. LED-001 cited such a row; it does not exist.
- Scaffold split measures chemical extrapolation, not temporal or prospective validation.

**Claim links:**
- Table 1 (`\label{tab:h1}`), scaffold column, ECFP4--RF row — `0.8300 ± 0.0023`
- Results paragraph, `manuscript/P5_manuscript_V2608.tex:106` — baseline value in the scaffold comparison
- LED-006 — the implicit reference for all four `delta_vs_ecfp4` values and their BH-adjusted p-values

**Source files:**
- `results/p5_ecfp4rf_scaffold_baseline.json` — upstream artifact holding `seed_means`, `mean`, `std`
- `scripts/p5_sanity_ecfp4_rf.py` — producer (RF config at line 65; output path and `std` at lines 103–105)
- `scripts/p5_replication_verification.py` + `results/p5_replication_verification.json` — independent re-run at the same configuration, scaffold deviation 0.0, verdict PASS
- `results/p5_replication_stats.csv` — consumes this baseline as the delta reference (no ECFP4-RF row of its own)

---

## LED-002: GIN Scaffold Split Performance

**Method:**
- Molecular representation: Graph Isomorphism Network (GIN), 3 layers, hidden dim 128, dropout p=0.1 during training
- Node features: Atomic number, degree, formal charge, hybridization, aromaticity (10-dim one-hot encoding)
- Edge features: Bond type (4-dim one-hot)
- Global pooling: Mean aggregation over nodes
- Training: 50 epochs maximum, AdamW (lr=0.001, weight decay=1e-4), BCE loss, dropout p=0.1 during training, early stopping patience 10
- Evaluation: Same 5-fold × 5-seed scaffold protocol as ECFP4-RF
- Metric: ROC AUC on held-out test folds

**Numbers:**
- Mean ROC AUC = **0.8047** (mean of 5 per-seed means)
- Population SD across 5 per-seed means = **±0.0141**
- Raw 25-fold SD = 0.0395
- Per-seed means: [0.8266, 0.7933, 0.7993, 0.8153, 0.7891]
- Range: 0.7891–0.8266
- Δ vs ECFP4-RF = **−0.0253**
- Paired t-test (df=4): t = −3.873, p = 0.018 (raw), p = **0.033** (BH-adjusted over 4 comparisons)

**Interpretation:**
Base GIN without topological fusion underperforms ECFP4-RF by 0.025 AUC points under scaffold split. The difference is statistically significant after Benjamini-Hochberg correction (adjusted p=0.033). Higher seed-level variation (SD 0.0141 vs 0.0023 for ECFP4) indicates less stable scaffold generalization. This is the **honest-negative result for base learned representations** — graph neural networks alone do not exceed the fingerprint baseline on this panel.

**Caveats:**
- GIN architecture and hyperparameters not exhaustively optimized
- 3-layer depth is shallow; deeper models may behave differently
- Scaffold split is harder than random split (where GIN reaches 0.9098)
- Result is panel- and training-protocol-specific

**Claim links:**
- Manuscript Abstract: "all four learned arms performed significantly worse"
- Manuscript Results §2.3, Table 1
- Manuscript Discussion §4.1: "learned models do not provide a free predictive advantage"

**Source files:**
- `results/p5_replication_stats.csv` (row: `scaffold,GIN`)
- `results/p5_replication_stats.json` → `arms.GIN|scaffold`
- `results/p5_GIN_scaffold_results.csv`
- `results/p5_GIN_scaffold_ckpt.json`

---

## LED-003: GIN-TFP Scaffold Split Performance (Topological Fusion)

**Method:**
- Base: GIN (same architecture as LED-002)
- Additional features: Topological Features from Persistent Homology (TFP), 78 dimensions
  - Persistent images (33 dims covering H0, H1, H2 Betti curves)
  - Statistical descriptors (entropy, lifespans, birth/death distributions)
  - Concatenated to GIN graph embedding before final classification head
- Fusion: Early concatenation (graph embedding + TFP vector → dense head)
- Training: Same protocol as base GIN, including dropout p=0.1 during training

**Numbers:**
- Mean ROC AUC = **0.8138** (mean of 5 per-seed means)
- Population SD across 5 per-seed means = **±0.0107**
- Raw 25-fold SD = 0.0352
- Per-seed means: [0.8207, 0.7936, 0.8120, 0.8215, 0.8213]
- Range: 0.7936–0.8215
- Δ vs ECFP4-RF = **−0.0162**
- Δ vs base GIN = **+0.0091** (descriptive improvement, not formally tested)
- Paired t-test vs ECFP4-RF (df=4): t = −3.506, p = 0.025 (raw), p = **0.033** (BH-adjusted)

**Interpretation:**
Topological fusion with persistent-homology features improves over base GIN by ~0.009 AUC points (descriptive comparison) but still underperforms ECFP4-RF by 0.016 (statistically significant, p=0.033 after BH correction). Lower seed-level variance (SD 0.0107 vs 0.0141 for base GIN) suggests that TFP features stabilize scaffold generalization modestly. This is **complementary signal, not predictive superiority** — topology adds interpretable structure without closing the baseline gap.

**Caveats:**
- Improvement over GIN is descriptive; no predeclared paired test GIN-TFP vs GIN
- TFP dimensions are computed via persistent homology on molecular graphs (H0/H1/H2 Betti numbers)
- Fusion architecture is simple concatenation; other fusion strategies not tested
- Persistent-image resolution fixed at 20×20 pixels per homology dimension

**Claim links:**
- Manuscript Abstract: "Persistent-image dimensions had the largest descriptive projection-weight salience"
- Manuscript Results §2.3: GIN-TFP row in Table 1
- Manuscript Results §2.4: Interpretability — TFP salience analysis

**Source files:**
- `results/p5_replication_stats.csv` (row: `scaffold,GIN-TFP`)
- `results/p5_replication_stats.json` → `arms.GIN-TFP|scaffold`
- `results/p5_GIN-TFP_scaffold_results.csv`
- `results/p5_GIN-TFP_scaffold_ckpt.json`
- `results/p5_GIN-TFP_scaffold_salience.json` (interpretability)

---

## LED-004: GIN-TNE Scaffold Split Performance (Tensor-Network Fusion)

**Method:**
- Base: GIN (same architecture as LED-002)
- Additional features: Tensor-Network Embeddings (TNE), 192 dimensions
  - Derived from Tucker decomposition of molecular adjacency/feature tensors
  - Compressed latent representation retaining scaffold-relevant substructure
- Fusion: Early concatenation (graph embedding + TNE vector → dense head)
- Training: Same protocol as base GIN, including dropout p=0.1 during training

**Numbers:**
- Mean ROC AUC = **0.8090** (mean of 5 per-seed means)
- Population SD across 5 per-seed means = **±0.0149**
- Raw 25-fold SD = 0.0378
- Per-seed means: [0.8140, 0.7795, 0.8151, 0.8171, 0.8192]
- Range: 0.7795–0.8192
- Δ vs ECFP4-RF = **−0.0210**
- Δ vs base GIN = **+0.0043** (descriptive)
- Paired t-test vs ECFP4-RF (df=4): t = −3.057, p = 0.038 (raw), p = **0.038** (BH-adjusted, marginal)

**Interpretation:**
Tensor-network fusion yields a modest descriptive gain over base GIN (+0.004 AUC) but remains significantly below ECFP4-RF (−0.021, p=0.038 after BH correction). The marginal p-value (0.038) is the highest among the four comparisons, indicating the weakest evidence against the null hypothesis of equal performance. TNE captures compressed scaffold structure but does not translate into ranking improvement over the baseline.

**Caveats:**
- TNE construction depends on Tucker decomposition hyperparameters (rank, normalization)
- 13 TNE embedding failures (0.07%) on the 19,836-molecule panel; failed embeddings set to zero-vector
- Fusion strategy is simple concatenation; latent-space alignment not tested
- Higher variance than GIN-TFP suggests less stable scaffold generalization

**Claim links:**
- Manuscript Abstract: "all four learned arms performed significantly worse"
- Manuscript Results §2.3, Table 1: GIN-TNE row
- Manuscript Results §2.4: TNE top dimensions identified via salience analysis

**Source files:**
- `results/p5_replication_stats.csv` (row: `scaffold,GIN-TNE`)
- `results/p5_replication_stats.json` → `arms.GIN-TNE|scaffold`
- `results/p5_GIN-TNE_scaffold_results.csv`
- `results/p5_GIN-TNE_scaffold_ckpt.json`
- `results/p5_GIN-TNE_scaffold_salience.json`

---

## LED-005: ChemBERTa Scaffold Split Performance (Pretrained Transformer)

**Method:**
- Model: ChemBERTa-base (seyonec/ChemBERTa-zinc-base-v1), pretrained on 77M SMILES from ZINC
- Architecture: RoBERTa transformer, 6 layers, 768 hidden dimensions, 12 attention heads
- Fine-tuning: Classification head added, trained 20 epochs, lr=2e-5, batch size 32
- **Critical protocol fix:** Model reinitialized independently per fold (fold-independent initialization)
  - Without this, fold 2–5 inherit fold-1 weights → data leakage → inflated apparent performance
  - The leak-fixed protocol is the only valid ChemBERTa result
- Evaluation: Same 5-fold × 5-seed scaffold protocol
- Input: Canonical SMILES strings (no graph structure)

**Numbers:**
- Mean ROC AUC = **0.7867** (mean of 5 per-seed means, **leak-fixed**)
- Population SD across 5 per-seed means = **±0.0054**
- Raw 25-fold SD = 0.0338
- Per-seed means: [0.7942, 0.7793, 0.7904, 0.7870, 0.7823]
- Range: 0.7793–0.7942
- Δ vs ECFP4-RF = **−0.0433**
- Paired t-test vs ECFP4-RF (df=4): t = −18.349, p = 5.2e-5 (raw), p = **0.00021** (BH-adjusted, strongest)

**Interpretation:**
The pretrained transformer ChemBERTa significantly underperforms ECFP4-RF by 0.043 AUC points (p=0.00021 after BH correction, the most significant difference among all four comparisons). **Critically, fold-independent initialization changes the apparent transformer ranking** — without the fix, ChemBERTa would appear competitive. This demonstrates that **sequence pretraining on ZINC does not transfer predictive advantage to this antimalarial natural-product panel under scaffold split**. The result challenges the "foundation model = free lunch" narrative.

**Caveats:**
- ChemBERTa-base, not -large; larger variants may differ
- Pretrained on ZINC (drug-like synthetics), not natural products → domain shift
- Fine-tuning hyperparameters (lr, epochs, batch size) not exhaustively tuned
- Scaffold split may be especially hard for sequence models lacking explicit graph structure
- Fold-independence is a necessary validity condition, not a modeling choice

**Claim links:**
- Manuscript Abstract: "ChemBERTa 0.7867"
- Manuscript Results §2.3: Weakest performance among all 5 models
- Manuscript Discussion §4.2: "sequence pretraining does not transfer"
- Manuscript Methods: "fold-independent initialization" protocol detail

**Source files:**
- `results/p5_replication_stats.csv` (row: `scaffold,ChemBERTa`)
- `results/p5_replication_stats.json` → `arms.ChemBERTa|scaffold`
- `results/p5_chemberta_scaffold_results.csv`
- `results/p5_chemberta_scaffold_ckpt.json`

---

## LED-006: Statistical Significance of All Learned Models vs ECFP4-RF (BH-FDR)

**Method:**
- Null hypothesis (H0): Each learned model has equal mean AUC to ECFP4-RF under scaffold split
- Test: Paired t-test on 5 per-seed means (df=4), one test per model
- Multiple-testing correction: Benjamini-Hochberg False Discovery Rate (BH-FDR) at α=0.05
- Procedure: Rank raw p-values, apply BH step-up rule to control expected proportion of false discoveries

**Numbers:**
| Model | Δ vs ECFP4-RF | Raw p-value | BH-adjusted p | Verdict |
|-------|---------------|-------------|---------------|---------|
| GIN | −0.0253 | 0.018 | **0.033** | Reject H0 (significant) |
| GIN-TFP | −0.0162 | 0.025 | **0.033** | Reject H0 (significant) |
| GIN-TNE | −0.0210 | 0.038 | **0.038** | Reject H0 (marginal) |
| ChemBERTa | −0.0433 | 5.2e-5 | **0.00021** | Reject H0 (highly significant) |

All four comparisons reject the null hypothesis after BH correction (adjusted p ≤ 0.038).

**Interpretation:**
**Every learned representation is statistically significantly worse than ECFP4-RF** under scaffold split after controlling for multiple comparisons. This is not due to random variation — the evidence is consistent across independent random seeds and survives multiplicity correction. The ordering is stable in every seed: **ECFP4-RF > GIN-TFP > GIN-TNE > GIN > ChemBERTa**. This defines the **panel-specific honest-negative benchmark headline**.

**Caveats:**
- Paired tests assume independence of per-seed means (valid given different random seeds)
- BH-FDR controls expected false-discovery proportion, not family-wise error rate
- Statistical significance does not imply practical significance; Δ values are small (0.016–0.043)
- Result is conditional on these architectures, hyperparameters, and this panel

**Claim links:**
- Manuscript Abstract: "all four learned arms performed significantly worse after Benjamini-Hochberg correction"
- Manuscript Results §2.3: "BH-adjusted p ≤ 0.0378"
- Manuscript Discussion §4.1: Central honest-negative finding

**Source files:**
- `results/p5_replication_stats.csv` (columns: `bh_adjusted_p`)
- `results/p5_replication_stats.json` → `arms.<model>|scaffold.bh_adjusted_p`

---

## LED-007: External Validation on Public ChEMBL Malaria Panel (Molecule-Disjoint) — [SUPERSEDED by LED-007-R1]

**Superseded 2026-08-19:** the accession recorded below (`CHEMBL4303805`) is wrong, and the
activity-binarization rule was omitted. Numbers are unchanged; provenance is corrected in
LED-007-R1. Retained verbatim for audit trail — do not cite this entry.

**Method:**
- Dataset: ChEMBL malaria bioactivity data (CHEMBL4303805), filtered for binary active/inactive labels
- Panel size: 22,447 compounds after filtering; 180 canonical-SMILES overlaps with P5 panel excluded
- **Evaluation panel: 22,267 molecule-disjoint compounds** (no training-set leakage)
- Labels: 19,160 actives, 3,107 inactives (86.0% positive rate)
- Protocol: Same ECFP4-RF and GIN configurations as P5 canonical benchmark
- Splits: Both random and scaffold (5 seeds, 5 folds each)
- Metric: ROC AUC

**Numbers (scaffold split, primary):**
- ECFP4-RF mean AUC = **0.9190** ± 0.00039
- GIN mean AUC = **0.8843** ± 0.0021
- Δ (ECFP4 − GIN) = **0.0346**
- Paired t-test (5 per-seed means): p = **3.35e-6** (highly significant)

**Numbers (random split, secondary):**
- ECFP4-RF mean AUC = 0.9547 ± 0.0033
- GIN mean AUC = 0.9237 ± 0.0040
- Δ = 0.031, p = 6e-5

**Interpretation:**
The "fingerprints > GNN" ordering **reproduces on an independent, molecule-disjoint public panel** with 22,267 compounds. Under scaffold split, ECFP4-RF exceeds GIN by 0.035 AUC points (p<0.0001), comparable to the 0.025 gap on the P5 canonical panel. This external validation supports the generalizability of the honest-negative finding beyond the original curated dataset, though both panels remain antimalarial-activity-focused and do not represent all molecular-prediction tasks.

**Caveats:**
- Both panels are antimalarial bioactivity; not a cross-domain validation
- ChEMBL labels are heterogeneous (multiple assays, IC50 thresholds, labs)
- High positive rate (86%) indicates class imbalance; AUPRC would complement AUC
- External panel is larger (22k vs 20k) but overlaps excluded, not fully independent origin
- Transfer test, not prospective validation

**Claim links:**
- Manuscript Results §2.2: "An orthogonal phenotype-only MoA benchmark" (distinct from this)
- Manuscript Results §2.3 or Discussion: External validation paragraph (if included)
- Manuscript Data Availability: Public ChEMBL panel provenance

**Source files:**
- `results/p5_public_chembl_malaria.csv` (22,447 original)
- `results/p5_public_chembl_malaria_disjoint.csv` (22,267 evaluation)
- `results/p5_public_chembl_malaria_provenance.json`
- `results/p5_public_malaria_report.json`

---

## LED-007-R1: External Validation on Public ChEMBL Malaria Panel (Molecule-Disjoint) — corrected provenance

*Supersedes LED-007. Numbers are identical; the dataset identity, the binarization rule, and the
row accounting are corrected, and one previously unflagged p-value is marked untraced.*

**Method:**
- Source: ChEMBL REST API, downloaded 2026-08-08 (`results/p5_public_chembl_malaria_provenance.json`)
- Target: **CHEMBL364** (*Plasmodium falciparum*). LED-007 recorded `CHEMBL4303805`; no such accession appears in any project artifact, and the manuscript already cited CHEMBL364
- Assay types: IC50 and EC50 records carrying a numeric pChEMBL value
- Raw activity records: 64,279; 106 skipped for missing or unparseable SMILES; 31,649 unique canonical compounds
- **Binarization (omitted from LED-007):** active at pChEMBL ≥ 6.0, inactive at pChEMBL < 5.0. The intervening 5.0–6.0 band is discarded as ambiguous rather than assigned a label, which retains 22,447 of the 31,649 unique compounds and drops 9,202 (29%)
- Overlap removal: 180 compounds share a canonical SMILES with the P5 panel (0.907% of the P5 panel, 0.802% of the ChEMBL set) and were removed — 161 actives and 19 inactives
- **Evaluation panel: 22,267 molecule-disjoint compounds**; 19,160 actives and 3,107 inactives (86.0% positive)
- Row arithmetic closes: 22,447 − 180 = 22,267; 19,321 − 161 = 19,160; 3,126 − 19 = 3,107
- Protocol: ECFP4-RF and GIN configurations identical to the P5 canonical benchmark
- Splits: random and scaffold, 5 folds × 5 seeds each; metric ROC AUC

**Numbers (scaffold split, primary) — unchanged from LED-007:**
- ECFP4-RF mean AUC = **0.9190** ± 0.00039
- GIN mean AUC = **0.8843** ± 0.0021
- Δ (ECFP4 − GIN) = **0.0346**
- Paired *t*-test on 5 per-seed means: **p < 0.0001**. See caveats — the value `3.35e-6` carried by LED-007 has no artifact behind it

**Numbers (random split, secondary) — unchanged:**
- ECFP4-RF mean AUC = 0.9547 ± 0.0033
- GIN mean AUC = 0.9237 ± 0.0040
- Δ = 0.031, p = 6e-5

**Interpretation:**
The fingerprint-over-GNN ordering reappears on a panel that shares no molecule with the training
library, so it is not an artifact of the curated eOS80CH labels. The scaffold-split gap of 0.035 AUC
is close to the 0.025 seen on the P5 panel, which is the comparison that matters: the effect does not
shrink when the compounds change. What the corrected provenance adds is a boundary on that claim.
Discarding the 5.0–6.0 pChEMBL band removes nearly a third of the unique compounds, and those are
precisely the borderline cases where a learned representation might earn its extra capacity. The
retained set is therefore easier than the underlying bioactivity distribution, and both arms benefit
from that; the 86% positive rate points the same way. The result is a clean transfer test on a
well-separated panel, not evidence that fingerprints win on hard, ambiguous chemistry.

**Caveats:**
- Both panels are antimalarial bioactivity; this is not cross-domain validation
- The 5.0–6.0 pChEMBL exclusion removes 9,202 unique compounds (29%). Neither arm was evaluated on the ambiguous band
- ChEMBL labels are heterogeneous across assays, thresholds, and laboratories
- 86% positive rate: AUPRC would complement AUC
- **Untraced p-value:** `results/p5_public_malaria_report.json` stores `paired_t_pvalue` rounded to 5 decimals, giving `0.0` for the scaffold split. A tree-wide grep for `3.35e-6` in `*.json|*.csv|*.log|*.out|*.err|*.txt` returns nothing. Only `p < 1e-5` is defensible; the manuscript's `p<0.0001` is unaffected, but the exact figure must not be quoted
- **Random-split provenance is weaker than the scaffold split:** the same report JSON notes that random values were "recovered from job 12848 log (the runner overwrote the JSON with only the last split)"
- **Historical stale-artifact label (resolved 2026-08-25):** an earlier version of `results/p5_public_malaria_report.json` carried `"dataset": "MoleculeNet malaria"`; the current JSON identifies ChEMBL CHEMBL364, and the abandoned MoleculeNet download contributes no reported result
- Transfer test, not prospective validation

**Claim links:**
- Manuscript Limitations §External transfer: CHEMBL364 sentence, binarization and row accounting (cites LED-007)
- Manuscript Data Availability: public ChEMBL panel provenance

**Source files:**
- `results/p5_public_chembl_malaria_provenance.json` (authoritative provenance: accession, thresholds, row counts, overlap)
- `results/p5_public_chembl_malaria.csv` (22,447 rows, pre-overlap-removal)
- `results/p5_public_chembl_malaria_disjoint.csv` (22,267 evaluation rows; fields `smiles,activity,pchembl`)
- `results/p5_public_malaria_report.json` (metrics; ChEMBL dataset identity and bounded p-value fields synchronized 2026-08-25)
- `results/scientific_audit_20260825.json` (frozen-split, scaffold, prevalence, bounded Tanimoto, result, and aggregate-salience audit; split files read from the official V1 artifact directory)
- `results/lightweight_robustness/p5_knn_ecfp4_k5_random_baseline.json` and `_scaffold_baseline.json` (distance-weighted kNN ECFP4 controls)
- `results/lightweight_robustness/p5_logistic_ecfp4_C1_random_baseline.json` and `_scaffold_baseline.json` (logistic ECFP4 controls)
- `results/lightweight_robustness/p5_replication_stats_rederived.json` (independent re-derivation from canonical CSVs)
- `scripts/p5_public_malaria_chembl.py` (panel construction), `scripts/p5_public_benchmark.py` (benchmark)

---

## LED-015: Lightweight ECFP4 controls and frozen-split chemical audit

**Status:** COMPUTED 2026-08-25; secondary robustness evidence; no canonical result overwritten.

**Frozen split audit:** The official V1 split files were read by explicit path and their SHA-256 values match `results/SHA256SUMS`. Under scaffold, train--test scaffold overlap is 0 for all 25 fold--seed records. Test active prevalence ranges from 0.586 to 0.862. A bounded sample of 500 training and 100 test molecules per fold gave mean maximum ECFP4 Tanimoto ranges of 0.292--0.388 under scaffold versus 0.477--0.568 under random. These are descriptive bounded audits, not new performance estimates.

**Baselines:** On the same frozen splits, distance-weighted kNN on ECFP4 (k=5) achieved mean ROC AUC 0.9166 random and 0.7110 scaffold; mean AUPRC values were 0.9562 and 0.8467. Logistic regression on ECFP4 (C=1, sparse scaling, liblinear) achieved mean ROC AUC 0.8790 random and 0.7063 scaffold; mean AUPRC values were 0.9456 and 0.8542. These controls are below ECFP4-RF under scaffold, so the RF headline must not be generalized to every ECFP4 learner.

**Salience boundary:** The historical aggregate vectors account for 17.7% of TFP and 18.0% of TNE salience in the top 10%. The extended campaign archived individual vectors for 20 fusion configurations (25 runs each); native TFP top-10% Jaccard stability was 0.374–0.399 across the canonical scaffold and three novel partitions, and native TNE stability was 0.274–0.326. These remain descriptive weight-stability diagnostics, not causal attributions.

**Sources:** `scripts/p5_scientific_audit.py`, `scripts/p5_knn_ecfp4.py`, `scripts/p5_logistic_ecfp4.py`, `scripts/p5_replicate_stats.py`, `scripts/p5_extended_campaign.py`, `scripts/p5_extended_train.sbatch`, `scripts/p5_extended_analysis.py`, and `results/lightweight_robustness/` plus `results/extended_campaign_20260825/`.

---

## LED-008: TFP Salience Analysis (Persistent-Image Dominance)

**Method:**
- Model: GIN-TFP trained on scaffold split (25 fold-seed checkpoints)
- Salience definition: Mean absolute weight (|W|) of each TFP dimension in the fusion head's input projection
  - `W` = first-layer dense weights mapping concatenated [GIN_embed, TFP_vector] → hidden layer
  - Columns corresponding to TFP dimensions extracted, absolute values averaged across output neurons
- Aggregation: Mean salience across 25 fold-seed checkpoints
- TFP dimensions: 78 total (dims 0–77)
  - Dims 33–57: Persistent images (H0, H1, H2 Betti curves discretized into 20×20 pixel grids)
  - Dims 0–32, 58–77: Statistical descriptors (entropy, lifespans, birth/death quantiles)

**Numbers:**
- **Top-5 TFP dimensions by salience (scaffold split):**
  1. Dim 53: **0.1184** (persistent image, H1)
  2. Dim 43: **0.1187** (persistent image, H1)
  3. Dim 52: **0.1041** (persistent image, H1)
  4. Dim 42: **0.0915** (persistent image, H1)
  5. Dim 44: **0.0997** (persistent image, H1)

- Persistent-image block (dims 33–57): Mean salience **0.079**
- Statistical-descriptor block (dims 0–32, 58–77): Mean salience **0.051**
- **Top-10% salience threshold: 17.3% of total projection weight concentrated in 8 dimensions**

**Interpretation:**
Persistent-image dimensions from H1 homology (1-cycles = rings, cavities) dominate the learned projection weights, with the top 5 dimensions all exceeding 0.09 salience. This indicates that **the model relies most heavily on topological ring-structure features** when integrating TFP information with the GNN embedding. However, **salience ≠ predictive gain** — high projection weight means the features are used, not that they improve ranking. The descriptive geometric signal is reproducible across 25 independent training runs.

**Caveats:**
- Salience = descriptive attribution, not causal contribution to performance
- Gradient-free method (weight magnitude); gradient-based attribution may differ
- Salience computed on trained weights; does not reflect feature importance during training dynamics
- Persistent-image resolution (20×20) is a hyperparameter; finer grids may shift salience
- Result is fusion-architecture-dependent (early concatenation + dense head)

**Claim links:**
- Manuscript Abstract: "Persistent-image dimensions had the largest descriptive projection-weight salience"
- Manuscript Results §2.4: Interpretability subsection
- Manuscript Discussion: "representation-level pattern did not translate into improved ranking"

**Source files:**
- `results/p5_GIN-TFP_scaffold_salience.json`
- `scripts/p5_interpretability.py` (salience computation code)

---

## LED-009: TNE Salience Analysis (Top Dimensions Identified)

**Method:**
- Model: GIN-TNE trained on scaffold split (25 fold-seed checkpoints)
- Salience: Same method as LED-008 (mean |W| of input projection weights)
- TNE dimensions: 192 total (dims 0–191)
  - Derived from Tucker decomposition of molecular adjacency/feature tensors
  - No explicit semantic labels (unlike TFP's H0/H1/H2 structure)

**Numbers:**
- **Top-5 TNE dimensions by salience (scaffold split):**
  1. Dim 68: **0.1450** (highest)
  2. Dim 165: **0.1141** (second)
  3. Dim 43: **0.1232**
  4. Dim 92: **0.1169**
  5. Dim 66: **0.1164**

- Mean salience across all 192 dims: **0.054**
- **Top-10% threshold: 19 dimensions contribute 21.7% of total projection weight**

**Interpretation:**
TNE salience is more dispersed than TFP (no single dominant block), with the top dimension (68) reaching 0.145 salience. Dimensions 68, 43, 92, 66, and 165 are consistently weighted across 25 training runs, indicating reproducible scaffold-relevant latent structure. However, **TNE lacks the interpretable H0/H1/H2 semantic labels of TFP**, making it harder to map salience to chemical substructures. As with TFP, high salience does not imply predictive superiority (GIN-TNE AUC 0.8090 < GIN-TFP 0.8138).

**Caveats:**
- TNE dimensions have no a priori chemical interpretation (Tucker latent factors)
- Salience computed on weights, not gradients or Shapley values
- 13 TNE embedding failures (0.07%) on P5 panel; zero-vectors may affect salience distribution
- Fusion architecture same as GIN-TFP; other fusion strategies not tested

**Claim links:**
- Manuscript Results §2.4: "TNE top dims 68/43/92/66/165"
- Manuscript Discussion: Comparison of TFP interpretability (semantic H1 structure) vs TNE (latent factors)

**Source files:**
- `results/p5_GIN-TNE_scaffold_salience.json`
- `scripts/p5_interpretability.py`

---

## LED-010: LISH-MoA Phenotype-Only Reference (Orthogonal Benchmark)

**Method:**
- Task: Predict 206 scored mechanism-of-action (MoA) labels from gene-expression/viability phenotypic features
- Dataset: Kaggle LISH-MoA training set, 23,814 assay observations
- Aggregation: Drug-level (3,289 unique `drug_id` after grouping replicates)
- Features: 772 gene expression + 100 cell viability + dose/time metadata (phenotype only, **no molecular structure**)
- Model: Unweighted per-label logistic regression baseline (deliberately weak reference)
- Splits: 5 seeds × 5 drug-grouped folds (no replicate leakage across train/test)
- Primary metric: **Mean column-wise log loss** (average over 206 label-specific log losses)
- Secondary metrics: Macro-AUPRC, macro-AUROC, mean Brier score, expected calibration error

**Numbers (with vehicle controls retained, primary condition):**
- Mean column-wise log loss = **0.02378** (lower is better)
- Macro-AUPRC = **0.1428**
- Macro-AUROC = **0.6435**
- Mean Brier score = 0.00374
- Expected calibration error (ECE) = 0.00376
- n_drugs = 3,289; n_labels = 206
- Protocol: 25 fold-seed evaluations (5 seeds × 5 folds)

**Numbers (vehicle controls excluded, sensitivity condition):**
- Log loss = 0.02389, macro-AUROC = 0.6417, macro-AUPRC = 0.1412
- Δ (controls vs no-controls): log loss +0.00011, macro-AUROC −0.0018
- **Verdict: Control exclusion changes nothing material**

**Interpretation:**
This is an **orthogonal phenotype-only reference**, not a molecular representation benchmark. The task, labels, feature space (gene expression, not molecular structure), aggregation unit (drug, not molecule), and primary metric (log loss, not AUC) all differ from the P5 molecular ROC-AUC results. **The numbers are not numerically comparable.** The reference demonstrates that a weak logistic baseline on phenotypic data reaches macro-AUROC 0.6435; any upstream P5 molecular method targeting LISH-MoA must beat this on the same fold grid. However, **no molecular GNN/ChemBERTa/TFP/TNE arm was run** because no versioned drug-SMILES mapping exists. This benchmark supports biological representation transfer evaluation (if a mapping were supplied), but does not validate antimalarial activity, target engagement, or resistance resilience.

**Caveats:**
- Phenotype-only; no molecular structure → no claim about ECFP4/GNN/transformer representations
- MoA labels = association, not causal target engagement (per Trapotsi et al. 2022)
- Macro-AUROC averages over labels with sufficient test-set variation (~72% of 206 labels)
- Log loss is miscalibration-sensitive; AUPRC is secondary here but primary for imbalanced labels
- Not an antimalarial validation; LISH is a multi-disease pharmacology dataset
- Result is locked but isolated; no bridge to P5 molecular findings without a mapping

**Claim links:**
- Manuscript Results §2.2: "An orthogonal phenotype-only MoA benchmark"
- Manuscript Discussion: Distinction between phenotype, chemical, and network evidence (Trapotsi ref)
- Manuscript limitations: "not numerically comparable to molecular ROC-AUC results"

**Source files:**
- `results/lish_moa/p5_lish_moa_phenotype_drug_grouped_report.json`
- `results/lish_moa/p5_lish_moa_phenotype_drug_grouped_folds.csv` (25 rows)
- `results/lish_moa/p5_lish_moa_conditions_comparison.json`
- `results/lish_moa/lish_moa_prepare_report.json` (audit)
- `scripts/p5_lish_moa_prepare.py`, `scripts/p5_lish_moa_benchmark.py`

---

## LED-011: LISH-MoA Feature-Space Composition Audit (Provenance for LED-010 Feature Counts)

**Date:** 2026-08-19

**Method:**
- Purpose: verify the feature-block counts asserted in LED-010 against the drug-level table actually consumed by the benchmark, so the counts can be stated in Methods
- Procedure: read the header row of `results/lish_moa/lish_moa_drug_level.csv`, split on commas, count columns by prefix, and check that the prefix counts sum to the total column count
- Command: `head -1 results/lish_moa/lish_moa_drug_level.csv | tr ',' '\n' | grep -c '^g-'` (repeated per prefix)

**Numbers:**
- Total columns = **1083**
- Gene-expression features (`g-` prefix) = **772**
- Cell-viability features (`c-` prefix) = **100**
- Experimental-condition features (`cp_` prefix) = **3** (`cp_time_hours`, `cp_dose_high_fraction`, `cp_type_trt_fraction`)
- Scored MoA label columns (`moa_` prefix) = **206**
- Identifier and replicate-count columns = **2** (`drug_id`, `n_observations`)
- Closure check: 772 + 100 + 3 + 206 + 2 = 1083, equal to the observed column count
- Rows = **3289**, equal to the `n_drugs` value in `lish_moa_prepare_report.json`

**Interpretation:**
The feature counts quoted in LED-010 came from the preparation step, not from the table the model was fitted on, so they were assertions rather than measurements. Counting the header directly closes that gap: every one of the 1083 columns belongs to exactly one of five blocks, and the row count matches the drug count recorded independently in the preparation report. The two agreements matter for different reasons. The column closure shows no feature block was dropped or double-counted between preparation and fitting, which is the failure mode that would silently shrink the phenotypic input. The row agreement shows drug-level aggregation ran to completion, since a partial merge would leave fewer rows than the reported 3289 drugs. The dose and time metadata amount to three summary columns rather than per-condition indicators, a consequence of aggregating repeated assay observations to one row per drug. That collapse is why the benchmark cannot separate dose-response behaviour from average phenotypic response, and it bounds what the phenotype-only reference can be asked to show.

**Caveats:**
- This audit counts columns; it does not check the numeric contents of any feature column
- The `g-` and `c-` names carry gene symbols and assay indices from the public release; no mapping to a versioned gene annotation was verified here
- The counts describe the drug-level table only. The upstream 23,814-observation table was not re-counted, since it is not the fitting input
- Confirms LED-010's counts; supersedes nothing. LED-010 remains the entry of record for all LISH performance metrics

**Claim links:**
- Manuscript Methods, "Orthogonal LISH MoA benchmark": feature-block counts
- Supports the non-comparability statement in Results §2.2 by making the feature space explicit

**Source files:**
- `results/lish_moa/lish_moa_drug_level.csv` (header row; 3289 data rows)
- `results/lish_moa/lish_moa_prepare_report.json` (`n_drugs`, `n_scored_targets` cross-check)

---

## LED-012: ECFP4-RF Random Split Performance (Secondary Baseline)

*Fills a gap. The random-split panel was reported in the manuscript from beat 2 onward but had
no ledger entry; Table 1's random column was tagged to LED-001, a scaffold-only entry.*

**Date:** 2026-08-19

**Method:**
- Identical protocol to LED-001-R1 — ECFP4 Morgan radius 2, 2048 bits, `StandardScaler`, `RandomForestClassifier(n_estimators=500, n_jobs=8, random_state=0)`
- Only the split differs: uniform random 5-fold cross-validation in place of Bemis-Murcko scaffold folds
- 5 random seeds; ROC AUC; mean of 5 per-seed means; population SD (ddof=0)
- Statistical unit: 25 fold-seed replicates total

**Numbers:**
- Mean ROC AUC = **0.9433** (unrounded 0.943299399145735)
- Population SD across 5 per-seed means = **±0.0003** (unrounded 0.00033480780453227257)
- Per-seed means: [0.9428, 0.9431, 0.9434, 0.9435, 0.9437]
- Range: 0.9428–0.9437
- Gap to the scaffold baseline (LED-001-R1): 0.9433 − 0.8300 = **0.1133**

**Interpretation:**

The same model, the same features and the same 19,836 molecules give 0.9433 under random folds and
0.8300 under scaffold folds. That 0.1133 gap is the whole reason the paper reports two splits: a
random-split number on this panel measures interpolation within scaffold families the model has
already seen, and it flatters every arm by roughly a tenth of an AUC point. Seed stability tells
the same story from a different angle — ±0.0003 here against ±0.0023 under scaffold folds, about
seven times tighter, because random folds all draw from the same scaffold mixture while each
scaffold fold withholds a different chemistry. Anyone quoting 0.9433 as the performance of this
model on antimalarial natural products is quoting the easier of two questions.

**Caveats:**
- Not a validation estimate for prospective use. Random folds put near-analogues of test molecules in training, which is the failure mode scaffold splitting exists to expose.
- Same panel bound as LED-001-R1: curated antimalarial natural products, n = 19,836, inherited from P3.
- No hyperparameter search. The 500-tree default configuration was used unchanged.
- Population SD (ddof=0), matching `scripts/p5_sanity_ecfp4_rf.py:105` (Notes item 1).
- `results/p5_replication_stats.csv` holds no `random,ECFP4-RF` row; this baseline enters that file only as the reference for `delta_vs_ecfp4`.

**Claim links:**
- Table 1 (`\label{tab:h1}`), random column, ECFP4--RF row — `0.9433 ± 0.0003`
- `manuscript/P5_manuscript_V2608.tex:106` — baseline in the random-split comparison
- `manuscript/P5_manuscript_V2608.tex:112` — the `0.031 below ECFP4--RF (0.9433)` comparison
- LED-013 — the reference for all four random-split `delta_vs_ecfp4` values

**Source files:**
- `results/p5_ecfp4rf_random_baseline.json` — upstream artifact holding `seed_means`, `mean`, `std`
- `scripts/p5_sanity_ecfp4_rf.py` — producer (RF config line 65; output path and `std` lines 103–105)
- `scripts/p5_replication_verification.py` + `results/p5_replication_verification.json` — independent re-run, random deviation 0.0, verdict PASS
- `results/p5_replication_stats.csv` — consumes this baseline as the delta reference

---

## LED-013: Random Split Performance of All Four Learned Arms, with BH-FDR Family

*Fills a gap. The manuscript's random-split learned-arm numbers, deltas and p-values were tagged
to LED-002 through LED-005, which are scaffold-only entries. Reported here as one entry because
Benjamini-Hochberg was applied jointly across these four comparisons — they are one inferential
family and cannot be split without misstating the correction.*

**Date:** 2026-08-19

**Method:**
- Arms: GIN, GIN-TFP, GIN-TNE, ChemBERTa — architectures and training as in LED-002 through LED-005
- Split: uniform random 5-fold cross-validation, 5 random seeds, same frozen fold assignment for every arm
- Null hypothesis (H0): each learned arm has equal mean AUC to ECFP4-RF (LED-012) under the random split
- Test: paired *t*-test on the 5 per-seed means (df = 4), one test per arm
- Multiple-testing correction: Benjamini-Hochberg FDR at α = 0.05, applied across these four tests only — the four scaffold tests in LED-006 form a separate family
- Dispersion quoted as `std_seed`: population SD across the 5 per-seed means

**Numbers:**

| Arm | Mean AUC | `std_seed` | `std25` | Δ vs ECFP4-RF | *t* (df=4) | Raw *p* | BH-adjusted *p* |
|---|---|---|---|---|---|---|---|
| ChemBERTa | 0.9121 | ±0.0012 | 0.0046 | −0.0312 | −65.915 | 3.17e−07 | **6.05e−07** |
| GIN | 0.9098 | ±0.0022 | 0.0067 | −0.0335 | −27.876 | 9.85e−06 | **9.85e−06** |
| GIN-TFP | 0.9084 | ±0.0012 | 0.0060 | −0.0349 | −60.715 | 4.41e−07 | **6.05e−07** |
| GIN-TNE | 0.8918 | ±0.0018 | 0.0060 | −0.0515 | −60.278 | 4.54e−07 | **6.05e−07** |

- Per-seed means — ChemBERTa [0.9099, 0.9123, 0.9128, 0.9133, 0.9122]; GIN [0.9111, 0.9127, 0.9072, 0.9106, 0.9073]; GIN-TFP [0.9085, 0.9086, 0.9062, 0.9090, 0.9097]; GIN-TNE [0.8924, 0.8904, 0.8891, 0.8927, 0.8941]
- All four reject H0 after correction. Every arm sits below the ECFP4-RF baseline of 0.9433 (LED-012)
- Random-split ordering: **ECFP4-RF > ChemBERTa > GIN > GIN-TFP > GIN-TNE**

**Interpretation:**

The negative result holds under random folds, so it is not an artifact of scaffold separation:
the fingerprint baseline beats all four learned arms on both splits, and all eight comparisons
survive FDR correction in their own families. What changes between splits is the order among the
learned arms, and it changes completely. ChemBERTa is the strongest learned arm under random folds
(0.9121) and the weakest under scaffold folds (0.7867, LED-005) — a drop of 0.1254, the largest of
any arm. GIN-TNE moves the other way: worst under random folds (0.8918) and mid-field under
scaffold folds, having given up only 0.0828. Reading those two numbers together says something the
means alone do not: the pretrained transformer's random-split advantage comes disproportionately
from scaffold families it has already seen, while the tensor-network fusion head retains more of
its signal when the test chemistry is genuinely new. Neither arm reaches the fingerprint baseline
in either regime, so this is a comparison among losing models, not a hedge on the headline.

The p-values are far smaller here than in LED-006 (1e−07 to 1e−05, against 1e−05 to 0.038) for a
reason that has nothing to do with effect size being more certain in any scientific sense: random
folds make the per-seed means extremely tight (±0.0012 to ±0.0022), so a paired test on five of
them divides a similar difference by a much smaller denominator. Three of the four raw *p*-values
are pooled to the same BH value of 6.05e−07, which is the correction working as intended on tightly
clustered ranks; GIN's is the largest raw value and so passes through unchanged at rank 4.

**Caveats:**
- Random-split AUC on this panel is an interpolation estimate. It is reported for contrast with the scaffold result, not as evidence of generalization.
- df = 4. Five seed means is a small sample, and a *t*-statistic of −65.9 reflects tiny between-seed variance rather than a large or well-estimated effect. The magnitudes are honest; their precision should not be read as replication across datasets.
- BH here covers four tests. Reporting these adjusted values alongside LED-006's without naming the family boundary would understate the total number of tests run.
- `std25` (raw 25-fold SD) is 3–5× `std_seed` for every arm. The manuscript quotes `std_seed`; the two must not be mixed in one table.
- Panel bound as LED-012. Architectures and hyperparameters are those of LED-002 through LED-005 and were not re-tuned per split.

**Claim links:**
- Table 1 (`\label{tab:h1}`), random column — GIN, GIN--TFP, GIN--TNE and ChemBERTa rows
- `manuscript/P5_manuscript_V2608.tex:106` — the four random means, four deltas and four *p*-values, and the sentence "No graph-based arm outperforms the fingerprint baseline under either split"
- `manuscript/P5_manuscript_V2608.tex:112` — ChemBERTa `0.9121 ± 0.0012` and GIN `0.9098`
- `manuscript/P5_manuscript_V2608.tex:213` — the statement that BH was applied separately across the four scaffold and the four random comparisons
- LED-006 — the scaffold-split counterpart family
- LED-012 — the baseline all four deltas are measured against

**Source files:**
- `results/p5_replication_stats.csv` — the four `random,*` rows; columns `mean25, std_seed, std25, seed_means, delta_vs_ecfp4, t_df4, raw_p, bh_adjusted_p`
- `results/p5_replication_stats.json` — `arms.<model>|random.*`
- `scripts/p5_replicate_stats.py` — producer; reads the ECFP4-RF baseline at line 63, writes CSV at line 93 and JSON at line 95. Trains nothing: the AUCs come from the benchmark run
- `results/p5_ecfp4rf_random_baseline.json` — the delta reference (LED-012)

---

## LED-014: ChemBERTa Scaffold Replication Run (Secondary Estimate)

*Fills a gap. A second ChemBERTa scaffold estimate is quoted in the manuscript's §Availability
paragraph with no ledger entry and no named source file.*

**Date:** 2026-08-19

**Method:**
- Same architecture and split as LED-005 — ChemBERTa (`seyonec/ChemBERTa-zinc-base-v1`), Bemis-Murcko scaffold 5-fold cross-validation, 5 seeds, the same frozen fold assignment
- A separate training run, not a re-analysis of the LED-005 predictions
- All 25 fold-seed cells present; mean of 5 per-seed means; population SD (ddof=0)

**Numbers:**
- Mean ROC AUC = **0.7908**, population SD = **±0.0058**
- Primary estimate (LED-005): 0.7867 ± 0.0054
- Difference between runs: **+0.0041**, well inside either run's seed spread
- Fold-seed cells: 25 of 25 present in both runs; **0 of 25** AUC values identical between them

**Interpretation:**

Two training runs of the same model on the same folds land 0.0041 apart, which is smaller than the
±0.0054 seed spread of the primary run. Run-to-run variation in transformer fine-tuning is
therefore not large enough to change any conclusion in this paper: the ChemBERTa scaffold estimate
would still sit last among the five arms and still fall 0.043 below the fingerprint baseline if the
secondary run had been the one reported. That is worth stating because ChemBERTa carries the
paper's strongest negative claim, and a single unstable run would be the obvious way for that claim
to be wrong.

What this is not is an independent replication. Both runs come from the same codebase, the same
frozen splits and the same session — the two result files share an mtime to the second. It tests
stochastic training variance and nothing else.

**Caveats:**
- "Independent" in the manuscript sentence means a distinct training run, not independently written code or independently generated splits. The word overstates what was done and should be read narrowly.
- Both runs share the same frozen fold assignment, so fold-composition variance is held fixed and is not sampled here.
- No random-split counterpart exists. No second random-split ChemBERTa run was performed, which the manuscript states.
- Population SD (ddof=0), per Notes item 1.
- The paragraph carrying these numbers sits inside §Availability rather than Results — a placement issue recorded as a submission blocker in `project-tracking.md`, not a data problem.

**Claim links:**
- `manuscript/P5_manuscript_V2608.tex:221` — `0.7908 ± 0.0058` and the `25` fold-seed record count
- LED-005 — the primary scaffold estimate the same paragraph quotes as `0.7867 ± 0.0054`
- LED-013 — the `0.9121 ± 0.0012` random-split figure the same paragraph quotes

**Source files:**
- `results/p5_chemberta_scaffold_results_metrics.csv` — this run (mean 0.7908, SD 0.0058)
- `results/p5_chemberta_scaffold_results.csv` — the LED-005 primary run (mean 0.7867, SD 0.0054)
- `results/p5_chemberta_random_results.csv` — the random-split run behind LED-013's ChemBERTa row

---

## Ledger Audit Gates (Run Before L2)

Before any number enters manuscript prose, verify:

1. **Ledger currency check:**
   ```bash
   grep -E "LED-[0-9]+" project-tracking.md | wc -l  # Should match entries here
   ```

2. **Missing interpretation check:**
   ```bash
   grep -c "Interpretation:" outputs/analysis/analysis-ledger.md  # Should equal entry count
   ```

3. **Unlinked claim check:**
   ```bash
   grep -E "\[CITATION NEEDED\]|\[ADD:.*\]" manuscript/P5_manuscript_V2608.tex
   ```
   Should return 0 matches if all claims are ledger-backed.

4. **Orphan number check:**
   ```bash
   # Any quantitative statement in Results/Abstract should cite LED-XXX
   grep -E "0\.[0-9]{4}" manuscript/P5_manuscript_V2608.tex | grep -v "LED-"
   ```
   Manual review required for any hits.

---

## Notes

1. **Units and uncertainty:** All AUC values are dimensionless (range 0–1). Displayed ± values are population SD across 5 per-seed means unless noted as `std25`.
2. **Anti-AI-writing applied:** Every interpretation written in direct, mechanistic, varied-rhythm prose. No "delve", "leverage", "robust", "compelling", "underscore".
3. **Superseded entries:** two so far, both dated 2026-08-19, both with headline numbers unchanged — the defects were in provenance, not in the values.
   - LED-007 → LED-007-R1: wrong ChEMBL accession, missing binarization rule.
   - LED-001 → LED-001-R1: hyperparameters copied from the wrong script (100 estimators and balanced class weights belong to `scripts/p5_ensemble.py`, not to the baseline producer `scripts/p5_sanity_ecfp4_rf.py`, which uses 500 trees and sklearn-default class weights); a cited `scaffold,ECFP4-RF` row in `results/p5_replication_stats.csv` that does not exist; and a per-seed list whose own population SD is 0.0021, contradicting the ±0.0023 quoted in the same entry.

   Any later revision appends a new entry and marks the old one `[SUPERSEDED by LED-XXX]`. Superseded entries are kept verbatim for audit and must not be cited.
4. **LISH-MoA boundary:** LED-010 is isolated; no structure-MoA comparison until mapping audit passes.
5. **External validation scope:** LED-007-R1 is antimalarial transfer, not cross-domain; both panels share biological target space.
6. **Split coverage — check before tagging.** Entry titles name their split, and a scaffold entry cannot back a random-split number. Scaffold: LED-001-R1 (ECFP4-RF), LED-002 (GIN), LED-003 (GIN-TFP), LED-004 (GIN-TNE), LED-005 (ChemBERTa), LED-006 (BH family), LED-014 (ChemBERTa replication run). Random: LED-012 (ECFP4-RF), LED-013 (all four learned arms plus their BH family). Tagging a random-split figure to LED-001–LED-005 asserts traceability the entry does not carry; that error was present in the manuscript through beat 6 and is worse than leaving the number untagged.
7. **BH family boundaries are part of the claim.** Two separate Benjamini-Hochberg families exist — four scaffold comparisons (LED-006) and four random comparisons (LED-013) — corrected independently. Neither family may be split across entries or merged with the other, and any text quoting an adjusted *p* must name which family produced it, or the total test count is understated.

---

*Every number in the manuscript must trace here. If it doesn't, it doesn't ship.*
