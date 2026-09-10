# P2 — Reconfiguration after P1 reviewer revision

**Date:** 2026-09-10  
**Project:** `Project2_Polypharmacology_MD_ValidationV2607/`  
**Upstream companion:** P1 V8 revision, `Project1_Chem_space_antimalarial_V7_CorrectedGrid/`  
**Document type:** scientific reconfiguration and implementation plan  
**Status:** Phase 0 complete (plan + claim matrix written 2026-09-10); Phase 1 claim registry written; Phase 1 crosswalk written; ready for Phase 2 (re-analyze existing results) and Phase 4 (manuscript rewrite)

> **Source-of-truth rule:** `P2_DATA_ANALYSIS_REPORT.md` remains the numerical authority. This plan does not promote `NOT_COMPUTED`, `FAILED`, `EXPLORATORY`, or non-canonical outputs. Any future change to a number, protocol, cohort, or claim must first be recorded in the P2 DAR and then propagated to the manuscript.

---

## 1. Executive decision

P1 V8 has absorbed a substantial fraction of the former P2 validation narrative: the corrected PfCRT channel, pipeline-null control, within-target favourability, seed sensitivity, DEKOIS two-arm analysis, retrospective antimalarial panel, and PNS–RRS sensitivity analyses now support the P1 revision. P2 should therefore **not remain a second, broader “MD validation” of P1**.

The recommended reconfiguration is a narrower methodological study:

> **P2 becomes an estimand-calibration and computational-triage study that tests whether docking-derived mutant-retention scores are operationally reproducible and whether they agree with a prespecified short-MD local-geometry diagnostic.**

The principal scientific contribution is not that MD validates P1. The contribution is that the combined record shows where the following quantities cease to be interchangeable:

1. empirical docking-score retention;
2. local structural retention during a short explicit-solvent trajectory;
3. an endpoint MM/GBSA estimate;
4. experimental affinity, target engagement, or resistance phenotype.

The existing P2 evidence is sufficient for this **calibration-boundary** paper if the claims are reduced accordingly. It is not sufficient for a biological validation paper, a thermodynamic free-energy paper, or an independent replication of P1.

---

## 2. Central question

### Primary question

> **Within the frozen P1-derived Set-C panel, does a docking-derived mutant-retention ratio provide a reproducible, protocol-stable computational triage signal that agrees directionally with a prespecified short-MD local-geometry retention metric for matched wild-type/mutant complexes?**

This question is falsifiable and does not presuppose concordance. It has two explicit components:

- **Operational reproducibility:** Does the docking-derived RRS remain materially stable under the declared seed, input, score-perturbation, and scoring-layer controls?
- **Estimand concordance:** For the matched rows for which both quantities exist, does the direction of docking-RRS agree with the direction of the short-MD geometry ratio?

### Primary decision rule

The primary conclusion should be based on the predeclared pair of outcomes:

| Outcome | Current canonical evidence | Interpretation |
|---|---:|---|
| Docking-RRS operational stability | PP-01 and PP-15 seed controls are stable at approximately the reported sub-0.1 kcal mol⁻¹ scale; additional perturbation and external-panel diagnostics exist | Conditional stability of a computational ranking protocol, not score accuracy or biological validity |
| Docking/MD directional concordance | 7/8 matched comparisons diverge; one is directionally concordant | Evidence that the two measurements are not interchangeable under the tested protocols |

The second result should be the narrative centre of P2. It is more defensible and more distinct from P1 than another presentation of the RRS class table.

### Secondary questions

1. How sensitive are RRS classes to WT eligibility, 70/80% class thresholds, score perturbations, and near-threshold values?
2. Do GNINA rescoring and the external docking panel reproduce a class-level retention pattern without being treated as independent biological validation?
3. What does the single-replicate MM/GBSA layer add, and what uncertainty does it fail to quantify?
4. What minimum biochemical, biophysical, and replicated-MD evidence would be required before “resistance resilience” could be evaluated as a biological claim?

---

## 3. Audit of the P1 → P2 transfer

### 3.1 What P1 has now absorbed from P2

P1 V8 includes or cites results originating in the P2 layer, including:

- PNS–RRS and `N_fav`–RRS analyses;
- the partial PNS–RRS analysis controlling for molecular weight and scaffold prevalence;
- P2-derived context for docking-score robustness and MM/GBSA interpretation;
- the Set-C/P2 interpretation that ratios above 100% indicate score retention or scoring noise, not gain-of-function;
- the distinction between docking-RRS and MD/MM/GBSA quantities.

This transfer is scientifically useful, but it changes the independence structure. P2 cannot present these same analyses as an external validation of P1. P1 and P2 share candidates, source chemistry, target panels, workflows, or derived quantities.

### 3.2 P1 evidence that should be treated as upstream context in P2

P1 V8 now provides the following relevant context:

- 65,856 starting molecules and 19,913 filtered candidates;
- a 17-member Set-C polypharmacology-oriented cohort;
- 68/68 candidate–target docking records passing the declared geometric gate;
- corrected 3D7-like PfCRT LYS-76 wild-type preparation and cavity-anchored grid;
- pipeline-null PfCRT control;
- within-target median favourability definition;
- five-seed sensitivity records;
- DEKOIS 2.0 retained-MTX versus stripped-receptor comparison;
- retrospective docking of five approved antimalarials, which did not recover the clinical resistance signatures.

P2 may cite these as **upstream design context, protocol provenance, or boundary evidence**. P2 must not call them independent validation, because the P1-derived Set-C, input preparation, or shared docking provenance overlap with P2.

### 3.3 Numerical quantities that must not be silently merged

The following are different estimands and must remain separately labelled:

| Quantity | P1 V8 | P2 canonical layer | Required treatment |
|---|---:|---:|---|
| P1 corrected RRS/PNS matrix | 17 candidates, P1 corrected PfCRT channel | Not the P2 primary matrix | Cite as upstream companion context only |
| P2 target-balanced PNS–RRS | — | rho = -0.2098, adjusted p = 1.0000, n = 12 | P2 descriptive primary-cohort analysis; no biological independence claim |
| P2 coverage-sensitive PNS–RRS | — | rho = -0.5588, adjusted p = 0.0667, n = 17 | Exploratory sensitivity only; unequal target coverage |
| P2 partial PNS–RRS | Referred to in P1 response as companion context | raw rho = -0.2098 to partial rho = -0.6154, n = 12 | Post-selection sensitivity; not external validation; local TDA inputs are not an independent dataset |
| P1 DEKOIS | AUC near chance in retained and stripped arms | Reused as context | Protocol-transfer boundary, not P2 biological validation |
| P2 Set-C MD-RRS | — | 16 systems, PP-01/PP-02 pilot contract | Secondary geometry estimand; full 17-candidate panel remains `NOT_COMPUTED` |

**Required editorial correction:** wherever P1 wording describes P2 as “corroborating” the P1 association, it should say that the P2 layer provides a **non-independent, post-selection sensitivity analysis under a related computational pipeline**. That wording preserves the result without overstating its evidential status.

---

## 4. Canonical P2 evidence after the audit

### 4.1 Primary docking cohort

- Set-C: 17 candidates and 136 PfDHFR/PfCRT docking systems.
- Complete two-target estimand: 12 candidates.
- PfCRT-only sensitivity records: 5 candidates; not evidence-equivalent to the complete panel.
- Target-balanced RRS classes: A* = 1, A = 1, B = 4, C = 5, D = 1.
- PNS–RRS target-balanced association: rho = -0.2098, permutation p = 0.5144, adjusted p = 1.0000, n = 12.
- Coverage-sensitive association: rho = -0.5588, adjusted p = 0.0667, n = 17; exploratory only.
- ACSI, PNS, and RRS are distinct ranking dimensions; no causal network interpretation is permitted.

### 4.2 Set-C MD pilot

- 16 systems: PP-01/PP-02 × PfDHFR/PfCRT WT/mutant states.
- 10 ns per system; one canonical production replicate per system in the pilot contract.
- All 16 trajectories passed the declared geometric QC.
- MD-RRS is a ratio of local trajectory-geometry metrics, not an affinity, residence-time, kinetic, or free-energy measurement.
- Among the eight rows with both a docking WT reference and a matched MD comparison, seven directions diverge and one is concordant.
- The full-panel 17 × 8 MD-RRS analysis remains `NOT_COMPUTED` by design.

### 4.3 MM/GBSA endpoint layer

- 16 finite Set-C endpoint rows: 12 mutant states plus four WT baselines.
- 8/12 mutant ratios exceed 100%; this is interpreted as retention or endpoint/scoring variability, not gain-of-function.
- The endpoint method is single-replicate for most systems and does not provide replicate-level thermodynamic uncertainty.
- PP-01 PfCRT K76A has a documented inter-replicate difference of 7.75 kcal mol⁻¹; this is a strong warning against treating the within-trajectory error bar as the uncertainty of the binding estimate.
- The PfATP4 parent-system +473 kcal mol⁻¹ result is a conversion artifact and is not reportable as an affinity estimate.

### 4.4 Robustness and transfer diagnostics

The following may remain in P2, but only under explicit labels:

- seed sensitivity: operational reproducibility;
- score perturbation and RRS-margin analysis: rule sensitivity;
- GNINA: alternative scoring-layer sensitivity on the same poses;
- external 39-ligand/312-state panel: computational transfer/replication under different provenance, not experimental validation;
- P2Rank and ProLIF: pocket and interaction diagnostics;
- PNS/ACSI analyses: descriptive post-selection ranking analyses.

None of these establishes experimental target engagement or resistance phenotype.

---

## 5. Recommended P2 scope and title

### Recommended title

> **Calibration Limits of Docking-Derived Mutant-Retention Scores Revealed by a Short Molecular-Dynamics Stress Test**

This title identifies the methodological object and the principal negative result. It avoids “validated resistance,” “binding affinity,” and “resistance-resilient lead.”

### Acceptable alternatives

1. **Docking-Derived Mutant-Retention Scores as Computational Triage Signals: An Estimand Audit with a Short Molecular-Dynamics Pilot**
2. **Separating Docking Retention from Dynamic Retention in Computational Antimalarial Prioritisation**

### Claims P2 may make

- The workflow produces a reproducible, auditable computational prioritisation record under declared inputs and rules.
- Docking-derived RRS can be stable as an operational ranking signal under selected seed and input controls.
- The short-MD geometry metric measures a different quantity from docking-RRS.
- In the matched pilot rows, the two directions diverged in seven of eight comparisons.
- MM/GBSA endpoints are useful as protocol diagnostics only when their sampling and replicate limitations are explicit.
- PP-01 is a candidate for experimental follow-up because it passed a bounded computational pilot gate, not because it is a validated lead.

### Claims P2 must not make

- “RRS measures resistance resilience.”
- “MD validates the docking ranking.”
- “MM/GBSA provides the binding free energy” for these single-replicate endpoints.
- “PP-01 is a robust dual-target lead.”
- “PP-02 is biologically eliminated.”
- “GNINA or the external panel independently validates P1.”
- “No effect” from a non-significant test; use “no association was detected under this analysis.”
- “The PNS–RRS association proves independence” or proves a biological network mechanism.

---

## 6. Evidence architecture for the reconfigured paper

The manuscript should use the following hierarchy.

| Level | P2 estimand | Evidence | Permitted interpretation | Explicitly not shown |
|---|---|---|---|---|
| 1. Primary | Operational stability and within-panel docking-RRS triage | 17-candidate Set-C; 12 complete two-target records; frozen score tables and manifests | Computational prioritisation under the declared protocol | Affinity, engagement, biological resistance |
| 2. Concordance test | Directional agreement between docking-RRS and MD local geometry | 8 matched comparisons; seven divergent | Non-equivalence of the tested estimands | Which method is biologically correct |
| 3. Endpoint diagnostic | MM/GBSA within-protocol contrasts | 16 endpoints, mostly single replicate | Sampling-/protocol-sensitive diagnostic | Converged or calibrated free energy |
| 4. Sensitivity | Seeds, perturbations, GNINA, external panel, P2Rank, ProLIF | Versioned secondary outputs | Operational robustness and boundary diagnostics | Independent biological replication |
| 5. Technical | QC, hashes, manifests, force-field and topology checks | Run and post-production records | Procedural reproducibility | Scientific validity of the biological hypothesis |
| 6. Unobserved | WT/mutant biochemical activity, target engagement, parasite phenotype | No canonical measurements | No claim | All biological resistance conclusions |

This table should appear in the Supporting Information and be summarized in the main text as an evidence-boundary figure or compact table.

---

## 7. Implementation plan

### Phase 0 — Freeze the boundary before editing prose

**Deliverable:** `P2_RECONFIGURATION_PLAN_P1_P2_20260910.md` plus a versioned claim–evidence matrix.

**Status: ✅ COMPLETE** (2026-09-10). Plan written; claim matrix updated to `docs/P2_V2609_CLAIM_EVIDENCE_PROVENANCE.md` with 20 claims (C01–C20), 8 forbidden claims (F01–F08), P1→P2 crosswalk (8 quantities), and 6-tier evidence hierarchy.

Actions completed:

- [x] Freeze the current P2 DAR as the numerical authority for this planning cycle.
- [x] Record that P1 V8 is the upstream companion and not an independent P2 validation set.
- [x] Create a crosswalk for every P1-derived quantity used by P2: source file, script, cohort, target panel, seed, grid, ligand preparation, and permitted interpretation.
- [x] Create a claim registry with IDs C01–C20 + F01–F08.
- [x] Mark every claim as `PRIMARY`, `CENTRAL`, `SECONDARY`, `TECHNICAL`, `NOT_COMPUTED`, or `UNOBSERVED`.
- [x] Do not start M1 or any new docking/MD campaign as part of this documentation change.

**Exit criterion met:** no manuscript claim can use a P1 number without a P1/P2 provenance label and an explicit independence status.

### Phase 1 — Rebuild the P2 estimand contract

Create a machine-readable or tabular contract containing, for each analysis:

- population and denominator;
- target and mutation state;
- receptor and ligand preparation hashes;
- grid file and dimensions;
- Vina version, exhaustiveness, and seed policy;
- primary/secondary status;
- output file and generating script;
- uncertainty type;
- permitted and forbidden interpretation.

The contract must explicitly separate:

1. P2 target-balanced docking-RRS (`n=12`);
2. P2 available-target sensitivity (`n=17`);
3. P2 MD pilot (`PP-01/PP-02`, 16 systems);
4. parent-study systems;
5. PP-15 single-ligand pilot;
6. external docking panel;
7. P1 V8 correction/validation outputs.

**Exit criterion:** all denominators and cohort identities are visible in one place; no cohort is silently merged.

### Phase 2 — Re-analyze existing results without changing the canonical estimands

Use existing scripts and versioned outputs where possible. Do not replace canonical values during this phase.

#### 2.1 Docking-RRS stability

Report, as sensitivity analyses:

- PP-01 and PP-15 multi-seed dispersion using the exact canonical ligand preparation and grid;
- RRS class stability under the existing bounded score perturbation audit;
- margins to the 70% and 80% operational thresholds;
- target-balanced versus available-target class counts;
- external panel RRS as a descriptive transfer record.

Do not convert seed dispersion into a confidence interval for biological resistance.

#### 2.2 Docking–MD concordance

Predeclare the directional rule before any new plotting:

- docking RRS below 100% = less favourable mutant score under the docking ratio convention;
- MD geometry ratio above 100% = larger mean minimum distance than the corresponding WT under the current metric;
- the comparison is made only on matched rows with a valid WT anchor for both quantities;
- frames are not independent observations; the unit is the system or candidate–mutation state.

Report the existing seven-of-eight divergence as a descriptive result with its exact denominator and scope. Do not use a p-value from eight heterogeneous rows as proof of general non-concordance.

#### 2.3 MM/GBSA recalibration

Retain the values only as endpoint diagnostics. Add a table with:

- number of trajectories and independent replicas;
- number of frames;
- SD versus SEM convention;
- PBC treatment;
- numerical-QC status;
- whether the endpoint is canonical, diagnostic, or non-reportable;
- inter-replicate differences where available.

The PP-01 PfCRT K76A 7.75 kcal mol⁻¹ inter-replicate difference should be used as an explicit example of why frame-level error bars do not represent replicate uncertainty.

#### 2.4 PNS and ACSI demotion

Keep PNS/ACSI as secondary descriptors of candidate context. Move their detailed formulas and sensitivity results to the SI. The main text should state that these are post-selection, cohort-dependent ranking dimensions and are not causal biological measures.

#### 2.5 DEKOIS and P1 validation demotion

P2 should cite P1’s DEKOIS and retrospective-panel results as protocol-boundary evidence. P2 should not repeat the full P1 validation narrative or use it to claim P2’s independent performance.

**Exit criterion:** the P2 result hierarchy is visible before any title/abstract rewrite.

### Phase 3 — Decide whether to run the strengthened M1 campaign

M1 is currently `NOT_COMPUTED / NOT_REPORTABLE` for its authorized estimand: the 12-replicate, 100 ns contract has no complete set of 12 trajectories with QC and provenance reconciliation. Local execution records also describe a partial PP-01 PfDHFR WT trajectory of approximately 23–25 ns; that partial artifact is not a completed M1 replicate and must not support a 100 ns, convergence, affinity, or resistance claim. It may be archived as a separate protocol-level stress-test appendix only after the DAR explicitly reconciles its final duration, QC, hashes, and allowed interpretation.

#### Option A — recommended for the immediate reconfiguration

Do not launch new simulations. Reconfigure P2 around the existing calibration record:

- primary result: operational docking-RRS stability and auditability;
- central secondary result: seven-of-eight docking/short-MD directional divergence;
- MM/GBSA: endpoint limitation case study;
- no claim of MD convergence or thermodynamic validation.

This is the lowest-risk route and avoids turning a documentation problem into a new incomplete production campaign.

#### Option B — strengthened MD robustness extension, only after author authorization

If the scientific objective is to retain a substantial MD contribution, complete a bounded replication design:

- four pillar states: PP-01 PfDHFR WT, PP-01 PfCRT WT, PP-01 PfDHFR N51I, PP-01 PfCRT K76T;
- three independent replicas per state;
- 100 ns per replica, if the throughput and allocation are feasible;
- one task at a time on the GPU resource unless a validated concurrency test supports more;
- analysis unit = replica, never frame;
- analysis plan frozen before looking at final outcomes.

This campaign would test inter-replicate structural variability for a small pillar set. It would **not** validate the full 17-candidate RRS panel and would not make the full-panel MD-RRS computable.

Mandatory preflight corrections before any M1 relaunch:

- use the canonical source path `results/md_systems/set_c_preparation_20260812_v1/`;
- remove unsupported `tc-integrator` settings;
- use a wall-time allocation compatible with the observed throughput;
- verify exact ns-to-step conversion with a 10-step smoke test and a short GPU test;
- do not pass unsupported `mdrun -seed` options;
- stage all topology and force-field dependencies inside the run contract;
- require `grompp`, production, trajectory-QC, and post-processing exit codes to pass independently;
- record environment, command, hashes, and scheduler provenance for every replica.

M1 integration gate:

- 12/12 replicas complete, or a prespecified fail-closed status with no partial inference for the 100 ns M1 estimand; a partial trajectory, if retained, is separately labelled archival stress-test evidence and cannot substitute for a replicate;
- trajectory QC passes for every included replica;
- convergence and between-replica summaries are computed at replica level;
- no frame-level pseudoreplication;
- the DAR is updated before any manuscript change;
- the author decides whether M1 is a robustness appendix or a main-text result.

### Phase 4 — Rewrite the manuscript around the central question

#### Abstract

Use five elements:

1. **Problem:** docking-derived mutant-retention ratios are useful triage quantities but are not biological resistance measurements.
2. **Objective:** test operational stability and agreement with a short-MD structural metric.
3. **Methods:** 17 candidates, 12 complete two-target records, 16-system pilot, explicit estimand separation.
4. **Results:** stable selected docking controls, seven-of-eight directional divergence, endpoint/MM/GBSA limitations, and no biological validation.
5. **Conclusion:** reproducible computational prioritisation is supported; docking retention and dynamic retention are not shown to be equivalent.

Required sentence:

> *The study supports computational prioritisation but does not establish biological target engagement, affinity, or resistance resilience.*

#### Introduction

Four paragraphs are sufficient:

1. resistance and the need for testable multi-target hypotheses;
2. distinction between empirical docking scores and thermodynamic quantities;
3. the methodological gap: conflating triage, structural diagnostics, and validation;
4. the falsifiable central question and evidence boundaries.

#### Methods

Recommended sections:

1. Study design and estimands;
2. P1-derived cohort and selection conditioning;
3. Docking, WT eligibility, and RRS;
4. PNS/ACSI as secondary descriptors;
5. MD pilot and trajectory QC;
6. MM/GBSA endpoint protocol and uncertainty conventions;
7. Sensitivity and transfer diagnostics;
8. Statistical analysis and unit of inference;
9. Provenance, software, and data availability.

#### Results

Recommended order:

1. cohorts and estimands;
2. docking-RRS operational stability;
3. target-balanced versus available-target sensitivity;
4. docking/MD directional comparison;
5. MM/GBSA endpoint diagnostics;
6. secondary GNINA/external/pocket/interaction audits;
7. P1 interface and non-independence boundary;
8. evidence-scope summary.

#### Discussion

The first paragraph should state the central result: the workflow is auditable as computational triage, while the tested short-MD metric does not reproduce the docking direction in most matched pilot comparisons. The discussion should offer multiple plausible explanations—different estimands, rigid versus dynamic receptor treatment, preparation/force-field differences, short duration, and single-replicate sampling—without selecting one as proven.

#### Conclusion

Use the following logic:

> The workflow provides a reproducible way to rank candidates and expose uncertainty. The present data do not validate docking-derived resilience as a physical or biological property. The short-MD pilot is best interpreted as a structural stress test showing that docking retention and dynamic retention are not interchangeable under the tested protocols. PP-01 is a candidate for experimental follow-up, not a validated dual-target or resistance-resilient lead.

### Phase 5 — Supporting Information and provenance package

Add or maintain the following SI items:

- cohort/estimand table with `n=12`, `n=17`, and pilot denominators;
- P1→P2 provenance and non-independence crosswalk;
- complete WT/mutant score table;
- seed and exact-input sensitivity table;
- RRS threshold-margin table;
- docking-versus-MD row-level comparison;
- MM/GBSA endpoint table with SD/SEM/replicate labels;
- software/version/force-field/seed/hash manifest;
- evidence-layer table separating primary, secondary, technical, and unobserved quantities;
- explicit list of `NOT_COMPUTED`, failed, withdrawn, and non-reportable outputs.

### Phase 6 — Experimental validation roadmap, kept outside current claims

P2 should end with a concrete validation sequence rather than implying that the current computations are sufficient:

1. recombinant PfDHFR WT and N51I/C59R/S108N/I164L paired activity measurements;
2. PfCRT WT/K76T/K76A transport or binding-compatible assay under an explicitly justified membrane/protonation protocol;
3. orthogonal biophysical confirmation for the highest-priority compounds;
4. isogenic parasite or suitable cellular mutant-panel phenotyping;
5. prospective comparison of predicted RRS with measured WT/mutant activity;
6. only after those steps, evaluation of whether a computational RRS relates to resistance resilience.

The current P2 paper should call these **required next measurements**, not completed validation.

### Phase 7 — Final quality gates

Before an author can authorize a P2 submission:

- run the P2 unit tests in `malaria_md`;
- regenerate only versioned secondary analyses from declared scripts;
- compile main, SI, and cover letter twice;
- verify no undefined cross-references or stale numerical values;
- run `git diff --check`;
- verify every table/figure denominator and unit;
- verify that the full-panel MD-RRS remains `NOT_COMPUTED` unless a separate contract is completed;
- verify that M1 is either fully integrated through the DAR or explicitly excluded;
- verify public data/code availability under the current ACS policy;
- perform an author-level read of all claims, especially those transferred into P1 V8.

Suggested local validation commands, subject to the active environment and project instructions:

```bash
cd Project2_Polypharmacology_MD_ValidationV2607
python3 -m pytest tests/ -q
cd manuscript/LaTeX
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2609.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2609.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2609.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2609.tex
git diff --check
```

No command above should be interpreted as authorization to launch HPC production, upload data, or alter canonical results.

---

## 8. Web research and how it changes the plan

The following sources were searched on 2026-09-10. Publisher pages were used where accessible; ACS pages that returned HTTP 403 were cross-checked through indexed metadata, DOI records, or the accessible full-text source. These sources inform the plan; they do not replace local evidence verification.

| Source | Relevant finding | Consequence for P2 |
|---|---|---|
| ACS JCIM Author Guidelines, updated 2026-08-27, https://researcher-resources.acs.org/publish/author_guidelines?coden=jcisd8 | JCIM emphasizes molecular modeling with methodological or experimental value, states that straightforward single-target docking without adequate experimental validation is not considered, and applies ACS Research Data Policy Level 2 with a required Data Availability Statement | P2 must be framed as a methodological/calibration contribution with explicit negative evidence, not as routine docking or biological validation; the archive and data statement are submission gates |
| Soares et al., “Guidelines for Reporting Molecular Dynamics Simulations in JCIM Publications,” 2023, DOI: `10.1021/acs.jcim.3c00599`, https://pubmed.ncbi.nlm.nih.gov/37191169/ | Reporting should include starting coordinates, force field, conditions, replica simulations, and convergence; related JCIM guidance emphasizes at least three replica copies for MD studies | The existing 10 ns single-replicate pilot must remain secondary and non-thermodynamic. Any M1 extension needs independent replicas and a replica-level convergence plan |
| Abraham et al., “Sharing Data from Molecular Simulations,” 2019, DOI: `10.1021/acs.jcim.9b00665`, and ACS reproducibility editorial, DOI: `10.1021/acs.jcim.0c01389` | Molecular-simulation results require transparent methods and shareable data for reproducibility | P2 needs a complete input/output/hash manifest, not only a PDF and summary tables |
| Bauer et al., “Evaluation and Optimization of Virtual Screening Workflows with DEKOIS 2.0,” JCIM 2013, DOI: `10.1021/ci400115b`, https://pubmed.ncbi.nlm.nih.gov/23705874/ | DEKOIS 2.0 uses challenging, property-matched actives/decoys to avoid artificial enrichment and evaluate screening workflows | P1’s near-chance DEKOIS result is valuable as a boundary/transfer result; it cannot be converted into evidence of target biology or used as a generic score-quality certificate |
| Hany et al., “Benchmarking the Structure-Based Virtual Screening Performance of Wild-Type and Resistant PfDHFR Using Docking and Machine Learning Re-Scoring,” DDDT 2025, DOI: `10.2147/DDDT.S537065`, https://www.tandfonline.com/doi/full/10.2147/DDDT.S537065 | In a PfDHFR WT/Q benchmark, Vina performance was target/protocol dependent and CNN/RF rescoring improved screening metrics in that benchmark | P2 may discuss scoring-layer dependence, but must not transplant Hany et al.’s enrichment to the P2 cohort or call GNINA rescoring independent validation |
| AutoDock Vina FAQ, https://autodock-vina.readthedocs.io/en/latest/faq.html | Vina performance varies by target; the algorithm is stochastic; exact reproducibility requires identical inputs and parameters plus the same seed; search-space size and receptor preparation matter | Seed controls are meaningful only with exact canonical ligand, receptor, grid, and parameters. P2’s recovered PP-01/PP-15 controls should be described as protocol reproducibility, not accuracy |
| Genheden and Ryde, “The MM/PBSA and MM/GBSA methods to estimate ligand-binding affinities,” 2015, DOI: `10.1517/17460441.2015.1032936`, https://www.tandfonline.com/doi/full/10.1517/17460441.2015.1032936 | MM/PBSA and MM/GBSA require calibration, testing, and validation; their performance is method- and system-dependent | P2 should use “endpoint diagnostic” and report its sampling/replicate limits rather than “binding free energy” without qualification |
| Xu et al., “Sampling Challenges of MM/PBSA Binding Energy Calculations,” J. Phys. Chem. B 2025, DOI: `10.1021/acs.jpcb.5c04908`, https://pubmed.ncbi.nlm.nih.gov/41160056/ | The accuracy of MM/PBSA depends on force field and statistical quality of sampling | The 7.75 kcal mol⁻¹ PP-01 PfCRT K76A inter-replicate difference is a central P2 limitation, not a footnote |
| DUDE-Z, Stein et al., JCIM 2021, DOI: `10.1021/acs.jcim.0c00598`, https://dudez.docking.org/ | Public property-matched decoys and bootstrap tooling support target-specific docking benchmarking | Any future P2 benchmark should be target-specific, property-matched, and predeclared; generic decoy enrichment is insufficient |

### Web-research limitation

Some ACS and PubMed pages were not directly extractable in this environment because of HTTP 403/cookie restrictions. The DOI, title, journal, year, and key indexed claims were cross-checked through official ACS search results, PubMed search results, and accessible full-text pages where available. Before submission, an author should re-open the official publisher pages and verify current journal policy wording.

---

## 9. Decision gates and recommended status

### Gate G1 — Reconfiguration accepted

Required:

- title and central question changed to the calibration/triage scope;
- P1 is labelled upstream companion context;
- no P1-derived number is called independent P2 validation;
- P2 primary and secondary estimands are separated.

### Gate G2 — Existing-data manuscript eligible for author review

Required:

- all current canonical values reconcile to the P2 DAR;
- seven-of-eight divergence is reported with its correct matched-row denominator;
- MM/GBSA uncertainty language is corrected;
- full-panel MD-RRS remains explicitly `NOT_COMPUTED` by design, and the 100 ns M1 estimand remains `NOT_REPORTABLE`; any partial M1 trajectory is either excluded or separately labelled archival stress-test evidence after DAR reconciliation;
- PNS/ACSI are demoted to secondary, post-selection descriptors;
- data/code/hash manifest is complete.

### Gate G3 — Optional M1 integration

Required only if M1 is resumed:

- complete replica contract;
- 12/12 trajectories and QC records, or explicit fail-closed exclusion;
- replica-level analysis and convergence diagnostics;
- DAR update before manuscript update;
- author decision on main text versus SI placement.

### Recommended current status

```text
P2 = RECONFIGURE AS COMPUTATIONAL ESTIMAND-CALIBRATION STUDY
Canonical data = FROZEN
P1/P2 independence = NOT CLAIMED
Existing MD pilot = SECONDARY, SINGLE-REPLICATE, STRUCTURAL STRESS TEST
Full-panel MD-RRS = NOT_COMPUTED
M1 100 ns contract = NOT_COMPUTED / NOT_REPORTABLE / NOT INTEGRATED; partial trajectory = archival-only candidate pending DAR reconciliation
Manuscript = REWRITE REQUIRED BEFORE SUBMISSION DECISION
Submission = NOT AUTHORIZED
```

### Bottom-line recommendation

Proceed with **Option A** first: reconfigure and rewrite P2 using the existing canonical record, without launching another campaign. Treat the docking–MD divergence and the MM/GBSA inter-replicate sensitivity as the scientific result. Consider **Option B** only if the authors explicitly decide that a replicated MD robustness paper is worth the additional cost and accept that it will still be a structural-calibration study, not a biological validation of P1.

---

## 10. Audit provenance

### Local sources reviewed

- `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_DATA_ANALYSIS_REPORT.md`
- `Project1_Chem_space_antimalarial_V7_CorrectedGrid/Reviewers_Comments.md`
- `Project1_Chem_space_antimalarial_V7_CorrectedGrid/submission_ACS_P1V8/Response_to_Reviewers_P1_V8.tex`
- `Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md`
- `Project2_Polypharmacology_MD_ValidationV2607/P2_Sugg.md`
- `Project2_Polypharmacology_MD_ValidationV2607/docs/P2_V2609_IMPLEMENTATION_PLAN.md`
- `Project2_Polypharmacology_MD_ValidationV2607/docs/P2_V2609_NARRATIVE_PIVOT_PLAN.md`
- `Project2_Polypharmacology_MD_ValidationV2607/docs/P2_V2609_MD_AUDIT_MATRIX.md`
- `Project2_Polypharmacology_MD_ValidationV2607/manuscript/LaTeX/SUBMISSION_MANIFEST_V2609.md`
- `Project2_Polypharmacology_MD_ValidationV2607/manuscript/LaTeX/Cover_Letter_V2609.tex`
- existing `graphify-out/` graph and query output for P1/P2 code relationships

### Scope note

This is an internal planning document, not a peer-review report and not a submission-ready manuscript section. It contains implementation decisions and audit boundaries that should be translated into scientific prose only after the DAR, claim matrix, and author review are updated.
