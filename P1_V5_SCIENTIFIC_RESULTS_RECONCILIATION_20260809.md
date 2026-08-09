# P1 V5 scientific results and RRS reconciliation

**Date:** 9 August 2026  
**Phase:** `PRE_SUBMISSION_DEVELOPMENT`  
**Scope:** P1 V5 target-anchored Vina panel, exploratory four-target consensus, and exploratory docking-RRS integration with the P2 Set-C polypharmacology cohort.

## 1. Concrete results generated

### 1.1 Four-target Vina panel

The locked P1 V5 panel contains **17 candidates × 4 targets = 68 candidate–target pairs**. All 68 rows have finite Vina scores and passed the predeclared composite pose gate (rank-1 centroid in the box, target-anchor contact ≤ 10 Å, and ≥90% ligand atoms inside the box).

Target-specific score ranges are:

| Target | Structure | Range (kcal mol⁻¹) | Interpretation |
|---|---|---:|---|
| PfDHFR | 7F3Y | −6.35 to −4.86 | MTX A702 catalytic-site anchor |
| PfCRT | 6UKJ | −7.91 to −5.12 | Y01 membrane-cavity proxy; not an inhibitor anchor |
| PfClpP | 2F6I | −7.03 to −5.05 | Chain-A catalytic triad anchor |
| PfATP4 | 9N10 | −7.57 to −4.63 | Conserved P-type ATPase machinery; no co-crystallized inhibitor |

These values are Vina scoring-function outputs, not experimental affinities. They are not averaged across targets in the scientific interpretation because the pockets and structural evidence classes are heterogeneous.

Source: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/v5_four_target_vina_affinities.csv` and `v5_four_target_vina_review_table.json`.

### 1.2 Exploratory four-target consensus

A quarantined, reproducible descriptive consensus was computed as the arithmetic mean of the four target-specific Vina scores for each candidate. This is an **exploratory ranking only**, not a calibrated affinity and not a submission-ready claim.

| Rank | Candidate | Mean Vina score (kcal mol⁻¹) |
|---:|---|---:|
| 1 | PP-06 | −7.122 |
| 2 | PP-03 | −6.598 |
| 3 | PP-11 | −6.465 |
| 4 | PP-13 | −6.406 |
| 5 | PP-05 | −6.385 |
| 6 | PP-15 | −6.378 |
| 7 | PP-10 | −6.357 |
| 8 | PP-07 | −6.215 |
| 9 | PP-16 | −6.081 |
| 10 | PP-09 | −6.064 |
| 11 | PP-01 | −6.064 |
| 12 | PP-02 | −6.046 |
| 13 | PP-04 | −5.573 |
| 14 | PP-12 | −5.406 |
| 15 | PP-17 | −5.271 |
| 16 | PP-14 | −5.175 |
| 17 | PP-08 | −5.173 |

The complete artifact is `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/v5_consensus_four_target_exploratory.csv`; its provenance status is `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY`.

### 1.3 V5 mutant docking-RRS pilot

The mutant panel contains **136/136 finite Vina scores**: 17 candidates across PfDHFR WT + four mutants and PfCRT WT + two mutants. The per-target RRS definition was applied exactly as documented in P2:

\[
\mathrm{RRS}_{i,m,t}=100\times\frac{|S_{i,m,t}|}{|S_{i,WT,t}|},
\]

with wild-type denominators retained only when \(|S_{i,WT,t}|\geq 5.0\) kcal mol⁻¹.

| Target | n binders | Mean RRS | SD | Range | Per-target classes |
|---|---:|---:|---:|---:|---|
| PfDHFR | 17 | 99.559% | 0.841 | 98.4–101.6% | A*: 12; A: 5 |
| PfCRT | 17 | 100.229% | 1.032 | 99.3–104.1% | A*: 12; A: 5 |

This is a real computational result from the V5 mutant panel, but it is explicitly labelled `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY`. It must not be called MD-RRS and must not be merged into the canonical P2 RRS table without protocol reconciliation.

Source artifacts:

- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/rrs_pilot/c_rrs_pilot_per_target_v5.csv`
- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/rrs_pilot/rrs_pilot_provenance.json`

### 1.4 Target-normalised relative polypharmacology

Raw Vina scores are not averaged across heterogeneous targets. Instead, each candidate was ranked within each of the four target-specific V5 panels, converted to a percentile \((17-rank)/16\), and evaluated for multi-target breadth. **PP-06 is the only candidate in the top quartile on all four targets (4/4); PP-11 reaches the top quartile on 3/4 targets.** The non-dominated Pareto front contains **PP-06, PP-03, PP-05, PP-13, and PP-10**. This is a concrete relative polypharmacology result within the locked 17-candidate cohort; it is not an absolute cross-target affinity, experimental binding, or generalised enrichment claim.

Artifacts:

- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/polypharmacology/v5_within_target_polypharmacology.csv` (SHA-256 `62bda42732d4cacbc58093da8efe51098beae2ff4d4ec71c9a0bc4dd451b2f6e`)
- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/polypharmacology/v5_within_target_polypharmacology_provenance.json` (SHA-256 `8e73230f65f82437cc561cde3f77629497feadec664a0e27603525c65993fec6`)
- Figure: `v5_within_target_polypharmacology.png/.pdf`

The analysis is labelled `EXPLORATORY_RELATIVE_POLYPHARMACOLOGY_NOT_SUBMISSION_READY`; external validation requires a common target-stratified background/decoy panel.

### 1.5 Integrated V6 exploratory metrics

The exact-SMILES V6 join reproduces the P2 Set-C cohort of 17 candidates and combines target-wise V5 scores with the existing P2 RRS/ACSI/PNS source tables.

- RRS classes: **A*: 6, B: 5, C: 5, D: 1**.
- RRS mean: **81.698 ± 12.367**, range **68.175–111.653**.
- ACSI mean: **0.543 ± 0.153**, range **0.173–0.823**.
- PNS mean: **3.571 ± 1.560**, range **1.045–6.000**.
- High ACSI (`ACSI > 0.70`): **2/17 (11.8%)**.
- Spearman PNS–RRS: **ρ = −0.5588, p = 0.019709, n = 17**.
- Spearman ACSI–RRS: **ρ = −0.1324, p = 0.612593, n = 17**.

Under the pre-specified Bonferroni threshold \(\alpha=0.017\), neither association is significant. The PNS–RRS value is a nominal trend only.

The integrated table and figures are in:

- `Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/exploratory/derived/v6_integrated_candidate_metrics.csv`
- `Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/exploratory/figures/`
- `Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/exploratory/derived/v6_integrated_data_figures_provenance.json`

### 1.6 Independent computational redérivation of the archived DEKOIS PfDHFR benchmark

To obtain a concrete external performance result without inventing a four-target benchmark, the archived molecule-level DEKOIS PfDHFR panel was re-derived with an independent V5-local script. The inputs contain **40 experimentally labelled actives and 1,200 property-matched decoys**; the ranking score is `-vina_score`, so more-negative Vina scores rank higher. This is an independent computational redérivation of an archived panel, not an independent biological experiment.

| Metric | Result |
|---|---:|
| ROC-AUC | **0.4964** |
| Bootstrap 95% CI (10,000 replicates; seed 20260809) | **0.4038–0.5893** |
| PR-AUC | **0.0340** |
| EF at 1% / 5% / 10% / 20% | **0.00 / 0.50 / 1.00 / 1.00** |
| Mean active Vina score | **−6.989 ± 0.716 kcal mol⁻¹** |
| Mean decoy Vina score | **−7.018 ± 0.719 kcal mol⁻¹** |
| Active − decoy mean difference | **+0.028 kcal mol⁻¹** |

The result is essentially chance-level discrimination and does **not** support using this Vina protocol as a validated activity predictor for PfDHFR. It is nevertheless scientifically useful: it is a concrete negative external-enrichment result that constrains interpretation of the 17-candidate V5 docking matrix and argues against presenting docking scores as experimental affinity or prospective activity validation. The result does not demonstrate that the candidates are inactive, and it does not generalise to PfCRT, PfClpP, or PfATP4.

The redérivation reproduces the archived true-ROC summary (`AUC = 0.49640625`) while remaining distinct from the historical Vina-only V2 summary (`AUC = 0.450104`), because the archived summaries were generated from different score panels/protocol records. Neither historical value is overwritten.

Artifacts (all status `EXPLORATORY_EXTERNAL_ENRICHMENT_NOT_SUBMISSION_READY`):

- Script: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_rederive_dekois_pf_dhfr.py` (SHA-256 `7506f116987980233d06cee6d4dc35a077d2cb41ad542ffbbcc78d6d92971d48`)
- Metrics: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/external_validation/dekois_pf_dhfr/p1_v5_dekois_pf_dhfr_metrics.csv` (SHA-256 `9b5a19f916bc5b685b38277337b1e7c4b6f2f49eda3225eb9030191f04ebb621`)
- Provenance: `.../p1_v5_dekois_pf_dhfr_provenance.json` (SHA-256 `b5eef45a04d7c7da5887b0eb1583701c63860358806092240a9710b3faf09b67`)
- Figure: `.../p1_v5_dekois_pf_dhfr_roc_distribution.png/.pdf`

### 1.7 Isolated V5-protocol RRS reproduction (completed 9 August 2026)

To verify internal reproducibility of the V5 mutant-RRS pilot without touching canonical outputs, an isolated reproduction was executed in jobs **15013** (PfDHFR), **15014** (PfCRT), and **15015** (dependent post-processing).

**Exact outputs (all verified):**

- Vina raw scores: **136/136 rows** (85 PfDHFR + 51 PfCRT), 0 `failure.json`;
- Status per target: `VINA_GRID_DOCK_MUTANT_PANEL_RANK1_VERIFIED` (seed 0, exhaustiveness 16, num_modes 9);
- RRS recomputed: **34 rows (17 per target)**, mean RRS per candidate ≈ 99.9%, range 99.188–102.358%;
- Class distribution: **A*: 12, A: 5 per target — identical to the archived pilot (§1.3)**;
- Provenance records `canonical_outputs_modified=false` and `canonical_p2_rrs_overwritten=false`.

This confirms that the V5-protocol RRS result is internally reproducible from the frozen V5 raw-score chain. It does **not** change the relationship to canonical P2 (the V5 panel remains a distinct execution layer, ≈99.9% mean RRS versus P2 82.8%, as quantified in §4).

Artifacts (status `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY`):

- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/rrs_reproduction_20260809/vina_scores/v5_mutant_vina_scores_{PfDHFR,PfCRT,merged}.csv`
- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/rrs_reproduction_20260809/vina_scores/execution_provenance_{PfDHFR,PfCRT}.json`
- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/rrs_reproduction_20260809/c_rrs_reproduction_per_target.csv`
- `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/rrs_reproduction_20260809/reproduction_provenance.json`

## 2. Reconciliation with the canonical P2 RRS result

The V5 pilot RRS distribution is much narrower and closer to 100% than the canonical P2 Set-C RRS distribution (canonical range 68.175–111.653%, classes A*:6, B:5, C:5, D:1). This is **not a contradiction to be hidden** and is not evidence that either table is automatically invalid.

The two artifacts are not the same data layer:

1. V5 stores raw Vina scores with explicit candidate IDs, receptor labels, pose-gate metrics, and ligand/output hashes.
2. P2 canonical RRS stores post-processed ratios from `docking_mutants.csv`, with source-cohort hashes and a different raw-score provenance layer.
3. V5 uses a distinct mutant execution/receptor preparation chain, including the PfCRT K76T-background reversion convention documented in the V5 provenance.
4. P2 canonical values were generated before the V5 target-anchored replacement panel and were not recomputed from the V5 raw files.

Therefore:

- The V5 pilot is a **new exploratory docking-RRS panel**, not an independent replication of P2 RRS. A separately isolated V5-protocol reproduction was launched on 9 August 2026 as jobs `15013` (PfDHFR), `15014` (PfCRT), and dependent post-processing `15015`; it is not a common-protocol replication of P2. Outputs are under `results/exploratory/rrs_reproduction_20260809/` and cannot alter the canonical P2 table automatically.
- The canonical P2 RRS table remains the manuscript value until a planned reconciliation rerun maps identical raw inputs, receptor structures, mutation conventions, grid parameters, ligand preparation, Vina version/configuration, and score extraction rules.
- No V5 pilot class or correlation is imported into the canonical V6 manuscript yet.
- The discrepancy itself is a useful scientific QC result: the RRS distribution is sensitive to the raw docking panel and preparation protocol.

## 3. Reproducibility record

The following commands generated the current exploratory artifacts in the active `malaria_md` environment:

```bash
/home/nanaengo/miniforge3/envs/malaria_md/bin/python \
  Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_consensus_scoring.py
/home/nanaengo/miniforge3/envs/malaria_md/bin/python \
  Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_rrs_pilot.py
/home/nanaengo/miniforge3/envs/malaria_md/bin/python \
  Project1_Chem_space_antimalarial_V6_CorrectedGrid/scripts/v6_generate_integrated_data_figures.py \
  --internal-development
```

The execution date was **9 August 2026**, phase `PRE_SUBMISSION_DEVELOPMENT`. The V5 mutant docking provenance records AutoDock Vina **1.2.7**, Meeko **0.7.1**, RDKit **2025.3.6**, Python **3.11.15**, deterministic seed **0**, `num_modes=9`, and `exhaustiveness=16`. PfDHFR used the MTX A702 anchor with an 18 Å box; PfCRT used the Y01 proxy anchor with a 28 Å box. The execution scripts were `p1_v5_vina_dock_mutants.py` (SHA-256 `126be57392a29b1e854497e362388c79083947df44671dbbb3eb3c1feb3c4154`) and `p1_v5_rrs_merge_scores.py` (SHA-256 `c514799e41dc931b50855a0f98d06c73124b776be8d4586ca4fc7d31eef35b3f`). The merged source CSV hash was `b8acaca8bd7aff63718fc388c98c58d87a591c8620f6bf7022a07b1080c28a7c`; the receptor-frame audit hash was `89603d2021b2f57dc98dda9ec07784935318d1323b821ba67bbcf17140e8ae36`. These details reinforce that the V5 pilot is a distinct execution layer and not a byte-identical P2 rerun.

The resulting artifact hashes were:

| Artifact | SHA-256 |
|---|---|
| V5 exploratory consensus CSV | `0970cdc1b12825a1efd15f229a6c1b4dcde347ae919df21cffc24ea7659b3cb5` |
| V5 consensus provenance JSON | `e9a17f455ff2ae55cff4a20a146a491c3fb38f92913766a3e6998f39f110b564` |
| V5 exploratory RRS CSV | `1277a2659bc62ad4fd9b5e4ccdc8bd77b6f9c86ba550c64bcdf9d97562bb0c` |
| V5 RRS provenance JSON | `7ce25a861078ca2512dc6d10d939edc24a80a67edaecefc0e0d604e372237c75` |
| V6 integrated metrics CSV | `b9f598c4caeaf7776651eb77c2bcf7cab73f422db02e4e79dc38b900c7a2b9de` |
| V6 integrated provenance JSON | `5161d654f7630e8255d24ccba59177e2fba340cdec6c7ab8634245b59a88f53a` |

## 4. Exact V5–P2 raw-score reconciliation

The dedicated read-only implementation `Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_reconcile_rrs_panels.py` was executed on 9 August 2026. It mapped P2 SMILES to the V6 candidate IDs by exact canonical SMILES and normalised the V5 PfCRT WT label (`PfCRT_WT_K76` / `WT_K76`) to `WT`. All **136/136** expected shared candidate–target–state rows were recovered, with 17 rows for each of the eight states.

| Scope | *n* | Pearson *r* (*p*) | Spearman ρ (*p*) | Mean V5−P2 (kcal mol⁻¹) | MAE | RMSE |
|---|---:|---:|---:|---:|---:|---:|
| All states | 136 | 0.0227 (0.793) | 0.3114 (0.000224) | −1.082 | 1.737 | 3.035 |
| PfCRT | 51 | 0.7597 (1.0×10⁻¹⁰) | 0.7629 (7.7×10⁻¹¹) | +0.616 | 0.792 | 1.025 |
| PfDHFR | 85 | −0.1341 (0.221) | 0.2679 (0.0132) | −2.101 | 2.304 | 3.756 |

The largest differences are concentrated in PfDHFR WT and C59R states: PP-03 WT is V5 −9.264 versus P2 +10.30 kcal mol⁻¹; PP-01 WT is V5 −7.883 versus P2 +7.50; PP-11 C59R is V5 −7.931 versus P2 −0.02. This confirms that the V5 and P2 panels are not numerically interchangeable. The target asymmetry also argues against describing the discrepancy as a single global calibration offset.

Recomputing target-specific RRS directly from each raw panel (retaining only \(|S_{WT}|\geq5.0\) kcal mol⁻¹) gives:

| Raw panel | Target-specific rows | Candidate-level mean RRS ± SD | Candidate range | Candidates ≥80% |
|---|---:|---:|---:|---:|
| V5 | 34 (17 PfDHFR + 17 PfCRT) | 99.885 ± 0.754% | 99.188–102.358% | 17/17 |
| P2 | 29 (12 PfDHFR + 17 PfCRT) | 82.822 ± 10.757% | 71.716–105.782% | 8/17 |

The five missing P2 PfDHFR target rows are not missing data in the 136-row panel; they are excluded by the pre-specified WT binding threshold because their P2 WT baselines are below 5.0 kcal mol⁻¹. The V5 WT scores are all beyond that threshold. This denominator/binder-set difference is one mechanism by which the RRS distributions diverge, but it does not explain the underlying raw-score discordance. The canonical P2 class table remains unchanged; the V5 pilot remains a separate exploratory execution layer.

The machine-readable reconciliation is:

- CSV: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/reconciliation/v5_p2_raw_score_reconciliation.csv` (SHA-256 `137b221a5eded818dcf228af3eed628506971ea5c35bc576d0aaf7b488daa266`)
- JSON: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/reconciliation/v5_p2_raw_score_reconciliation.json` (SHA-256 `3bba94c5045a41a7057e0fc32d598be8ae329eda9a37f0fa57ad96aeb1739b14`)
- Script: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_reconcile_rrs_panels.py` (SHA-256 `37c756aad51cdf8268c7e5a1e62a357d86f7a2eb62a27bfc2188143e033161d1`)

The reconciliation is explicitly `EXPLORATORY_RECONCILIATION_NOT_SUBMISSION_READY` and does not constitute independent review, experimental validation, or an acceptance claim. The generated JSON also binds the reconciliation script SHA-256 (`37c756aad51cdf8268c7e5a1e62a357d86f7a2eb62a27bfc2188143e033161d1`) to the provenance record.

## 5. Reconciliation experiment required before a new headline claim

A valid comparison requires a paired, candidate-by-candidate rerun using one frozen protocol:

1. Freeze the 17 canonical SMILES and candidate hashes.
2. Freeze WT and mutant receptor PDB/PDBQT files and mutation numbering.
3. Freeze Vina version, exhaustiveness, box centers/sizes, protonation, charges, and random seeds.
4. Run the same 136 candidate–state pairs once, with immutable per-pair output hashes.
5. Recompute P2 RRS and V5 RRS from the same raw score table using one shared implementation.
6. Compare raw scores, ratios, rank correlation, Bland–Altman differences, class changes, and sensitivity to the \(|S_{WT}|\geq5.0\) threshold.

Until this experiment is complete, the scientifically defensible statement is: **P1 V5 has produced a complete target-anchored four-target docking panel and an exploratory mutant-RRS panel; P2 provides the canonical corrected RRS result; the two RRS layers are not yet directly comparable.**
