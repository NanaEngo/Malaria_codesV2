# BMAD Q1 Data Analysis Report — active summary

**Scope:** P1–P3 only. P4 and P5 have dedicated DARs.
**Updated:** 28 September 2026 (P1 §2/§6/§7 re-synced to the P1 V8 canonical state — V8 numbers, September R2 controls, executive-table refresh; plus the earlier P2 §3 re-sync — class-table correction, cross-metric estimand fix, GNINA timeline, checkpoint index; corrections flagged inline)
**Long-form history:** `docs/archive/md_full_20260812/BMAD_Q1_DATA_ANALYSIS_REPORT.md`

## 1. Executive status

| Project | Current status | Submission-relevant conclusion |
|---|---|---|
| **P1** | V8 canonical (JCIM resubmission REFUSED 16 Sept 2026 — seeking new venue, e.g. RSC Digital Discovery; package `submission_ACS_P1V8/`, DD cover in `submission_DD_P1V8/`) | V8: corrected PfCRT channel (RRS 99.1–100.6 %), RRS classes 7 A*/4 B/6 C/0 D, pipeline-null control, retrospective approved-drug control, two-arm DEKOIS (MTX-retained vs stripped, both null); Zenodo DOI public 10.5281/zenodo.22696778 |
| **P2** | V2609C canonical (JCIM submission-ready); package `submission_ACS_P2V2609C/` refreshed | *Estimand Divergence* framing (87.5%), denominator-unbiased RRS, 39-ligand GNINA CNN validation, African NP space ($Fsp^3=0.22$, $QED=0.70$), 3-layer audit completed (15-word title — the earlier “12 words” was a miscount, fixed 15 Sept; reserved Zenodo DOI 10.5281/zenodo.19608875, upload pending), and CUDA GROMACS array 15840 COMPLETE (exploratory 2 ns readout, no endpoints promoted) |
| **P3** | Canonical classical, hybrid, QKS, TNE/TDA, and external-validation analyses complete | Quantum-inspired descriptors are complementary; no quantum advantage over RBF or ECFP4 is claimed; JCAMD manuscript ready |

## 2. P1 — chemical space, docking, and RRS/polypharmacology

> **Canonical layer:** the authoritative P1 narrative is `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_DATA_ANALYSIS_REPORT.md` (V8, updated 10 September 2026; this file supersedes earlier V4–V7 snapshots). This section is an index-level mirror for cross-project readers; in any conflict the P1 DAR wins.

### Canonical findings (V8, corrected PfCRT channel)

- The P1 chemical-space library contains **65,856 unique molecules → 19,913 prioritised candidates** (MPO ≥ 0.70, SYBA > 0, SI > 10); the historical V4-era descriptors (92.6% ECFP4-unreachable, 69.3% scaffold recovery) remain the chemical-space novelty evidence.
- Docking: **68/68 candidate–target pairs** pass the geometric gate across 17 candidates × 4 targets (scores −12.01 to −4.63 kcal mol⁻¹); target-specific, never averaged as a common affinity scale.
- **PfCRT channel corrected (R2.3):** re-docked on the 3D7-like LYS-76 receptor with the cavity-anchored V2 grid — K76T/K76A produce no detectable score change (RRS 99.1–100.6 %) and the **pipeline-null control (R2.5)** gives the same distribution (99.4–100.5 %), so class boundaries are placed relative to the null. *(Correction 28-09-2026: this section previously displayed only the superseded V5-layer records — no PfCRT channel correction, no null control, no September controls; the V8 canonical numbers above are those of the P1 DAR and the V8 manuscript.)*
- **RRS classification on the corrected channel (null-anchored): 7 A\*, 4 B, 6 C, 0 D** (range 73.2–115.6 %). Favourability: within-target medians PfDHFR −5.92, PfCRT −8.06, PfClpP −6.02, PfATP4 −6.38 kcal mol⁻¹; N_fav–RRS ρ = +0.714 (permutation p = 0.0019) with the power limitation reported (R2.1); PNS–RRS ρ = −0.714 and RRS–|S_WT| ρ = +0.691 (Bonferroni α = 0.017, n = 17); ACSI–RRS ρ = −0.190 (n.s.).
- **September reviewer-driven controls (R1.2, R2.3, R2.4) — COMPLETE, machine-readable in `zenodo_package_P1/results/`:** retrospective docking of five approved antimalarials (negative recovery of clinical signatures, `retrospective_approved_antimalarials_20260909/`); PfCRT V2-grid re-dock (`pfcrt_redock_v2grid_20260909/`); two-arm DEKOIS MTX-retained vs MTX-stripped — both arms null for blockade, reported as a negative result (`dekois_mtxstripped_20260909/`). *(Correction 28-09-2026: these controls existed only in the P1 DAR and V8 manuscript; they were absent from this summary.)*
- V4 2F6I/PfClpP remediation (historical): all **484** centroid attempts accounted (458 PASS, 1 PENDING, 15 boron exclusions, 5 DOCKED_GATE_FAILED, 5 EMBED_FAILURE) — provenance/remediation result, not experimental validation.
- **Submission status:** V7 was validated 11/08/2026 and superseded by **V8** (response-to-reviewers dossier); the 16 Sept 2026 JCIM resubmission was **REFUSED** — a new venue is being sought (RSC Digital Discovery candidate, DD cover letter already assembled in `submission_DD_P1V8/`). The Zenodo deposit is **public**: DOI 10.5281/zenodo.22696778 (verified 16 Sept, supersedes reserved 22686176).

### Evidence boundaries

- Docking scores support prioritisation hypotheses, not measured binding or activity.
- RRS is per target and excludes non-binding WT denominators (`|ΔG_WT| < 5.0 kcal mol⁻¹`); class boundaries are anchored to the pipeline-null control, not to raw thresholds alone.
- The P1 V5 mutant-pilot layer (historical) and the P2 RRS layers use different receptor/preparation/execution provenance and are not interchangeable; the V5 workspace itself no longer exists in-tree (V4/V5/V7 evidence feeds V8 only through the documented integration).
- No IC₅₀/EC₅₀, target engagement, resistance circumvention, or biological polypharmacology is claimed without experimental evidence.

## 3. P2 — canonical RRS/polypharmacology source layer

> **Canonical layer:** the authoritative P2 narrative is `Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md` (updated 28 September 2026). This section is an index-level mirror for cross-project readers; in any conflict the P2 DAR wins.

The canonical Set-C cohort contains **17 polypharmacology-oriented candidates** and **136 WT/mutant docking systems**. Primary RRS classification (target-balanced complete two-target panel, n = 12):

| Class | Count |
|---|---:|
| A* | 1 |
| A | 1 |
| B | 4 |
| C | 5 |
| D | 1 |

Available-target sensitivity classification (17/17; the five PfCRT-only candidates are not evidence-equivalent to the two-target set): A* 5, A 1, B 5, C 5, D 1. *(Correction 28-09-2026: this section previously displayed a single-class table "A*: 6, B: 5, C: 5, D: 1" inherited from the superseded pre-rigorous-audit layer; the primary/available-target split above matches the canonical `c_rrs_classification.csv`.)*

Canonical cross-metric results (primary n = 12): PNS–RRS ρ = −0.2098 (permutation p = 0.5144; coverage-sensitive n = 17 variant ρ = −0.5588, p = 0.0222, adjusted p = 0.0667 — exploratory because target coverage is unequal); ACSI–RRS ρ = −0.4056 (p = 0.1922); RRS–weakest-eligible-WT-anchor ρ = −0.1661 (p = 0.6038). ACSI mean is **0.543**, with **2/17 (11.8%)** above 0.70. *(Correction 28-09-2026: the previously displayed values (ρ = −0.559/−0.132/−0.433 against a Bonferroni α = 0.017) mixed the coverage-sensitive and complete-two-target estimands; the canonical values are those above, per the `p2_rigorous_audit.py` re-analysis.)* These are docking-derived computational relationships.

Historical parent-lead MD remains separate: only PfCRT–214 has an interpretable MM-GBSA estimate (−18.25 ± 0.40 kcal mol⁻¹); dissociated systems and the 4GM2/PfClpR-labelled system are not promoted as PfClpP validation.

### Set-C pilot completion & post-production chain — CANONICAL (updated 24 August 2026)

The bounded **16-system pilot** (PP-01/PP-02 × PfDHFR/PfCRT mutation states) is prepared under the PI-approved OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P policy deviation. **Production array `15320` completed all 16/16 systems** with valid production trajectories (`production.xtc`, `production.cpt`, `production.log`):

| Batch | Tasks | Systems | Status |
|---|---|---|---|
| PP-01 DhFR × 5 | 0–4 | PP-01_PfDHFR_{WT,N51I,C59R,S108N,I164L} | ✅ COMPLETED |
| PP-01 CRT × 3 | 5–7 | PP-01_PfCRT_{WT,K76T,K76A} | ✅ COMPLETED |
| PP-02 DhFR × 5 | 8–12 | PP-02_PfDHFR_{WT,N51I,C59R,S108N,I164L} | ✅ COMPLETED |
| PP-02 CRT × 3 | 13–15 | PP-02_PfCRT_{WT,K76T,K76A} | ✅ COMPLETED |

GROMACS ran at 310.15 K with GPU flags `-nb gpu -pme gpu -bonded cpu -update cpu`; no fatal, LINCS, or NaN indicators in any production log. Equilibration array `15288` completed 16/16 with `rc=0` in the canonical preparation root `results/md_systems/set_c_preparation_20260812_v1/`.

**Post-production chain COMPLETE (20260818T212954Z)** — manifest `results/set_c_md/post_production_manifest_pilot.json` (schema v3, created 20260818T212251Z):
- Trajectory QC: `qc_exit_code=0` → `results/set_c_md/set_c_trajectory_qc_pilot.csv` (**PASS for all accepted rows**).
- MD-RRS: `md_rrs_exit_code=0` → `results/set_c_md/md_rrs_pilot_PP01_PP02.csv`, status **`COMPUTED_WITH_COHORT_CONTRACT`**, rule `setc_p2_minheavy_5A_ge10percent_v1`; both pilots classified **class A** across PfCRT+PfDHFR (`trajectory_count=8` per candidate); provenance in `md_rrs_pilot_PP01_PP02_provenance.json`.
- MM-GBSA Set-C (20260819): `results/set_c_md/mmgbsa_summary_pilot.csv` — **16 system rows** (PP-01/PP-02 × {PfCRT WT/K76T/K76A; PfDHFR WT/N51I/C59R/S108N/I164L}), 100 frames each, per-target `mmgbsa_rrs`; cross-metric comparison in `md_vs_docking_comparison_pilot.csv`; manifest `mmgbsa_manifest.json` (directory `mmgbsa_20260819/`).

Superseded / non-canonical: intermediate failed arrays `15308`, `15313`, `15317`; historical identifiers 15106/15111/15117/15254/15259/15260/15270/15274; the 20260819 re-run attempt logged in `logs/p2_setc_qc_rrs_15386.log` failed on an MDAnalysis API incompatibility (`XTCReader.timespan`) and is non-canonical — the authoritative QC/MD-RRS outputs are those of the completed chain above.

### 13 Aug storage cleanup (compressed 28-09-2026)

Failed run directories from `15308`/`15313`/`15317`, 1,087 autosave/backup files (~13.7 GB), and the 17 Aug comprehensive cleanup (non-canonical preparation/witness/diagnostic dirs, `HPC_ready/`, `models/aizynthfinder/`, misplaced trajectories, LaTeX build artifacts; project 51 → 39 GB) were removed under the approved safe-cleanup scope. Canonical `set_c_preparation_20260812_v1`, parent-MD evidence `MD_systems/`, runbooks, manifests, logs, and DARs were protected.

### 12 Aug scope decisions (compressed 28-09-2026)

- Pilot MD-RRS is a **two-candidate pilot** (PP-01/PP-02 × 8 states, cohort id `P2_SET_C_MD_RRS_PILOT_PP01_PP02`); the full-cohort contract (17 × 8 = 136 rows) is never silently replaced and remains NOT_COMPUTED.
- PlasmoDB/VEuPathDB stable IDs are target annotations only (PfDHFR `PF3D7_0417200`, PfCRT `PF3D7_0709000`, PfATP4 `PF3D7_1211900`, PfClpP `PF3D7_0307400`, PfClpR `PF3D7_1436800`); no pathway-enrichment claim.
- LigandExplorer job `15272` (commit `d47eea0d033bb2127ee6836445554881c59edc8e`): fail-closed audit found ligand-box JSON artefacts for `7F3Y` (4) and `6UKJ` (2) only → `COMPLETED_PARTIAL_REQUIRES_MANUAL_REVIEW`; auxiliary, no claim. Record: `results/ligandexplorer_annotation_20260812/annotation_manual_review.md`.

### Set-C MD readout (secondary, honest-negative)

Short-MD geometry and single-replicate MM-GBSA do **not** reproduce the docking-RRS direction: docking predicted weaker mutant scores for all 8 mutant states with a docking WT reference, while 7 of the 8 matched MD comparisons diverged (the *Estimand Divergence* observation; 7/8 = 87.5%, 95% Wilson CI 52.9–97.8%, n = 8, protocol-local per ADR-0002). No mutant shows a reproducible weaker-binding signature within 10 ns; MM-GBSA ratios > 100% are read as retention, not gain; PP-01 PfCRT K76A carries a 7.75 kcal/mol inter-replicate sensitivity; the WT replicate offset (2.01 kcal/mol) is the empirical inter-replicate noise floor. Full values: P2 DAR §4–§5 and manuscript Tables S8/S19.

### Checkpoints 25 Aug – 16 Sept 2026 (index; full narratives in the P2 DAR)

- **25–26 Aug:** R1–R10 adversarial mitigations; lightweight robustness runs (ΔΔG ± SD, partial Spearman control, cohort bootstrap); PP-01_PfCRT_WT replicate_1 GPU rerun (R2 pillar: R1 −30.61 vs R2 −28.60, offset 2.01 kcal/mol → noise floor); PP-01_PfCRT_K76A rerun (MM-GBSA BOND overflow; frame-880 lineage FAILED_NUMERICAL_QC; repaired-whole −27.54 ± 1.89 reportable as diagnostic only).
- **27–29 Aug:** robustness/transfer audit (LOCO, ±1 kcal/mol perturbations, ChEMBL feasibility = no independent RRS replication); external 39-ligand × 8-state docking replication (array 15605 + declared repairs, 312/312 records, 38/38 Class A, mean RRS 100.45); P2Rank pocket audit (exploratory); ProLIF IFP 16/16 (manuscript Figure 4); PP-01/PP-15 multi-seed redocking (dispersion ≤ 0.05 kcal/mol); STRING 400/700/900 sensitivity (ρ 0.9632–0.9975); 28 Aug secondary bootstrap + MD-filter gate (`results/rrs_polypharma_secondary_20260828/`, COMPUTED_SECONDARY, documented 28 Sept — see P2 DAR); RRS threshold-margin analysis (Table S18).
- **12–16 Sept:** V2609B → V2609C calibration (ADR-0002 framing; denominator-unbiased RRS; African NP chemical-space profiling; ethnobotanical mapping; 15-word title; INTEGRITY HOLD resolutions; ACS package refreshed and diff-verified); HPC array 15840 (2 ns exploratory replicates, 16/16 + relaunches 15851/15852; stability readout only — no endpoints promoted); M1 25 ns PP-01_PfDHFR_WT replicate (observation only); **triplicate Soares expectation NOT satisfied** (single surviving 25 ns trajectory; no new MD-RRS/MM-GBSA endpoints); 25 ns cap decision (50/100 ns extension scripts removed); vacuolar pH 5.2 PfCRT audit PLANNED; git sync `e3938fd61` + `1cb926d95`.

### GNINA status timeline (reconciled 28-09-2026)

- **12 Aug:** the generalized 17 × 4-panel GNINA statement was **withdrawn** — the preserved ligand-438 attempt produced an empty output (0 bytes); the tool register (`P2_GITHUB_TOOL_REGISTER_20260812.md`) is a historical HPC-era record not present in the current repository snapshot.
- **28 Aug:** bounded post-processing re-scoring of the external replication panel (39 ligands × 8 states = 312 poses, `results/robustness_transfer_20260827/gnina_consensus_20260828/`) completed: 312/312 finite CNN scores, **100% class-level agreement** with the frozen Vina estimand (38/38 eligible Class A; ligand-level ρ = 0.558; per-mutant rank transfer not claimed — Table S15; Vina-only remains canonical).
- Different scopes; **no full-panel Set-C GNINA claim exists**.

## 4. P3 — quantum-inspired representations

Canonical full-library results:

| Representation/model | AUC |
|---|---:|
| ECFP4 | 0.9475 ± 0.0045 |
| Hybrid RF | 0.8876 ± 0.0065 |
| TFP | 0.8759 |
| TNE | 0.7219 |

Removing QK reduces hybrid AUC by **0.040**; TFP contributes **0.014**; TNE is mildly negative in the ablation. QKS re-runs show quantum ≈ RBF at n=5,000 and n=19,849; no quantum advantage is claimed. External descriptor analyses retain the **351 TNE failures** as an explicit ITT/complete-case sensitivity issue rather than hiding them. The external QKS pilot (n=150) gives quantum **0.8385** versus RBF **0.8423**, p=0.374; this is an external replication of equivalence, not an advantage.

## 5. P3 external MoA extension — planned, not yet a canonical result

A separate P3/P5 extension is being implemented under `P5_LISH_MOA_EXTERNAL_V1`. LISH-MoA is a multi-label pharmacology benchmark (206 scored MoA labels), not an antimalarial activity panel. P3 may consume only the audited, structure-mapped drug-level artifact produced by the P5 preparation workflow; it must not alter the canonical P3 panel, splits, AUC tables, QKS conclusions, or manuscript headline.

The P3 external arm will compare ECFP4, TFP, TNE, and an explicitly labelled optional QKS analysis on the same mapped compounds. Mean column-wise log loss is primary, with macro/micro AUPRC and macro AUROC as secondary metrics. Splits must be grouped by `drug_id`, with scaffold-held-out sensitivity when structures are available.QKS remains separately bounded because its kernel cost is quadratic; `p3_lish_moa_qks_bounded.py` is available for a selected-label/cohort sensitivity analysis, but no such result is yet computed.
 Any unresolved structure mapping or descriptor failure is reported explicitly; no complete-case filtering may silently change the estimand. A public annotated mirror is now available for the data-access step (`pablormier/kaggle-lish-moa-annotated`; official mapping provenance `LISHarvard/moa_challenge`). It remains a mirror of the competition data, not a new biological validation source. Until its archive hash, extracted training rows, structure mapping, and all gates are available, this extension remains **planned / not computed** and cannot be cited as a P3 result.

## 6. Minimal provenance map

| Result layer | Source evidence | Status |
|---|---|---|
| P1 V8 canonical (docking/RRS, corrected PfCRT channel) | `Project1_Chem_space_antimalarial_V7_CorrectedGrid/` (workspace; V8 sources in `submission_ACS_P1V8/`), machine-readable archive `zenodo_package_P1/` (DOI 10.5281/zenodo.22696778) | canonical V8; V4/V5/V7 layers are historical inputs and the V5 workspace no longer exists in-tree |
| P2 canonical RRS/ACSI/PNS | `Project2_Polypharmacology_MD_ValidationV2607/results/c_rrs_classification.csv`, `c_acsi_scores.csv`, `c_pns_ranking.csv` | canonical docking-derived |
| P2 Set-C production | `Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_preparation_20260812_v1/` | 16/16 production trajectories completed; post-production chain COMPLETE; MD-RRS COMPUTED_WITH_COHORT_CONTRACT; MM-GBSA Set-C 16/16 |
| P3 external validation | `Project3_Quantum_Inspired_RepresentationsV2607/results/` | canonical/external sensitivity outputs |

## 6. Cross-project rules

1. Preserve canonical input, script, parameter, and hash provenance for every result.
2. Keep P1 Set A, P2 MD Set B, and P2 polypharm Set C disjoint.
3. Never convert docking-RRS into MD-RRS; MD-RRS requires complete trajectories and PASS QC.
4. Keep failed, pending, exploratory, and historical outputs visible but clearly labelled.
5. Do not update manuscript claims from an incomplete job.

## 7. Next actions

- **P1 (V8):** V8 canonical after the 16 Sept JCIM resubmission refusal; package `submission_ACS_P1V8/` verified (main 25 p. / SM 17 p. / cover 1 p. / response 5 p., 0 undefined refs) + Digital Discovery cover in `submission_DD_P1V8/`; Zenodo DOI public (10.5281/zenodo.22696778). Next: venue selection and format adaptation (RSC Digital Discovery candidate); no re-docking planned — all three September R2 controls are complete.
- **P2:** V2609C submission-ready (JCIM; package `submission_ACS_P2V2609C/` refreshed and diff-verified 16 Sept). No open compute item: the triplicate expectation is closed by the 25 ns cap author decision, the pH 5.2 audit remains planned, and daemon readouts (array 15840, M1 25 ns) are exploratory with no promotable endpoints. Next: any new endpoint requires a P2 DAR entry before any manuscript change.
- **P3:** preserve the honest-negative external validation framing and complete repository deposit preparation.
- **All:** keep this summary short; place detailed job narratives and superseded decisions in the archive.
