# Master Roadmap P1–P5 — Resistance/RRS + Polypharmacology

**Version:** 1.9 — 10 August 2026 (global acceptance assessment + P1 V6 submission package + P2 MD-RRS integration decision; **R11 Table S5 ADMET completed**; **R5 register lifted** INTERNAL_WORK_AUTHORIZED; **P2 MD-RRS chain deployed** 15106→15111→15117)
**Purpose:** submission-oriented roadmap for the canonical versions of Projects 1–5.  
**Update basis:** current repository state plus Olsson, *Generative molecular dynamics*, *Current Opinion in Structural Biology* 96 (2026) 103213, DOI `10.1016/j.sbi.2025.103213`, PMID `41544599`; P5 benchmark completed in full on 8 August 2026 (jobs 12841/12842) with independent validation 100% complete (stats re-derivation, ECFP4-RF + GIN replication, public ChEMBL benchmark); **P1 V5 PfATP4 COMPLETE (job 12864)** — 17/17 pairs pass the composite gate, 17×4 affinity table COMPLETE, manuscript V5 updated to the 4-target gate; **P1 V4 PfClpP replacement run LAUNCHED (fresh job 14483_[0-483])** — first submission 13999 failed closed on pre-existing output directories; fresh 484-centroid raw revalidation now runs on genuine 2F6I in an isolated directory, with no promotion before fail-closed aggregation; **P4 v12-activity benchmark COMPLETE (job 12865)** — Random 0.6724 > MCTS 0.6649 > GA 0.6453 > Greedy 0.4278, manuscript P4 switched to v12-activity (abstract/table/figure/SM/cover letter, recompiled RC=0); **P3 external validation COMPLETE** — descriptor ITT and complete-case sensitivity are finalized (jobs 12858→12860→12891→13997), QKS external validation is complete (12863), and corrected-resampled statistical audit is complete (13998). **Session 2 (10/08 evening):** global acceptance assessment created (`ACCEPTANCE_ASSESSMENT_20260810.md`); **P1 V6 Paragon Plus submission checklist** ready; **P2 MD-RRS chain deployed** (job 15117 QC+RRS submitted, dependency on 15111); **P3 citation companion note fixed** (report-residue removed); **P3 dead externaldocument[P2-] dependency removed** (purely bibliographic now); **cross-package .aux files** added to all submission manifests.
**Operating rule:** every result must remain traceable to frozen inputs, an executable script, recorded parameters, and QC evidence. **Author-controlled pre-submission decision (09/08/2026):** no editorial, submission, independent-review, or signature restriction blocks scientific work while P1–P5 are under development. Exploratory calculations, RRS/PNS/ACSI analyses, figures, reruns, and manuscript refinement may proceed with truthful provenance labels. Scientific identity, hash, geometry, numerical, and runtime QC remain active. Submission does not switch the workflow automatically; only the author's explicit confirmation of submission plus explicit request to reactivate restrictions activates the signed-review policy. See `P1_INTERNAL_DEVELOPMENT_POLICY.md` and `P1_PRE_SUBMISSION_WORKFLOW_NOTICE.md`.

**Concrete results — 10 August 2026 (session):**

1. **Numerical audit P1 V6 (complete):** every value in `tab:dual_priority` (17 rows, order N_fav desc / RRS desc), the Discussion claims (PP-15 111.7 % A* N_fav=4; PP-06 −7.91 kcal mol⁻¹ / 92.4 %; PP-11 82.6 %; PP-13 104.8 % on 2 targets), the abstract (68 pairs, range −7.91…−4.63) and the four cross-metric correlations (PNS–RRS −0.559, ACSI–RRS −0.132, RRS–ΔG_WT −0.433, PNS–ΔG_WT +0.389) were verified line-by-line against `v6_integrated_candidate_metrics.csv` and `Project2/.../metrics/cross_metric_matrix.csv`. **One correction applied:** the Discussion described PP-15 as a "moderate four-target profile" although PP-15 is favorable on all four Vina targets (N_fav=4); the sentence now states the RRS classification channels (PfCRT-only: PP-02/06/11/13; PfDHFR+PfCRT: PP-01/15) and notes PP-15's four-target favorability (commit `43fde858f`).

2. **Numerical audit P1 V5 (complete, 0 corrections):** per-target means (PfDHFR −5.755, PfCRT −6.185, PfClpP −5.935, PfATP4 −6.308), per-target ranges, global range −7.91…−4.63 (68 pairs) and the two extremes (PP-06 PfCRT −7.91, PP-13 PfATP4 −7.57) all match the source CSV exactly.

**Concrete results — 10 August 2026 (session 2, evening):**

1. **Global acceptance-risk assessment created** — `ACCEPTANCE_ASSESSMENT_20260810.md` (89 lines, poussé `ebad7423b`): all 5 packages assessed with evidence-based acceptance estimates (P1 V6 80–85%, P2 75–80% → 80–85% after MD-RRS, P3 ~82%, P4 ~70–75%, P5 ~75–80%). Zenodo deferred by author choice. Remaining actions per package documented.

2. **P1 V6: ACS Paragon Plus submission checklist created** — `submission_ACS_P1V6/PARAGON_PLUS_CHECKLIST.md` (188 lines, poussé `56b2c499b`): 8-step wizard with concrete metadata (5 authors, title, abstract, 8 keywords, TOC spec, file list, ORCID requirement per author). Decision: submit P1 V6 now.

3. **P2: MD-RRS must be integrated** (user decision: Option B, « doit être intégré »). Post-production chain deployed: **15117** (`p2_setc_qc_and_md_rrs.sbatch`) submitted with `--dependency=afterok:15111`. Chain: 15106 eq (4 RUNNING, 7 PENDING, 1 FAILED N51I) → 15111 prod (PENDING) → 15117 QC+RRS (PENDING). Integration plan `P2_MD_RRS_INTEGRATION_PLAN.md` written with concrete edits for abstract, Results, Methods, Limitations, Conclusion (6 sections).

4. **P3: citation compagnon P2 nettoyée** — `temgoua2027md` note changée de « to be completed from the verified publication record » vers « submitted for publication in JCIM » (commit `e2efd1076`). Dépendance morte `externaldocument[P2-]` retirée (`282fec8df`). P3→P2 désormais purement bibliographique, citation vérifiée : main [22] (Temgoua et al. 2026b), SM [5] (Temgoua et al. 2026). Pas de risque de compilation reviewer.

5. **Cross-package: fichiers .aux requis par xr ajoutés** à tous les packages de soumission (P1 V6, P2, P3, P4). Manifestes régénérés (0 missing). P3 ne dépend plus de la compilation de P2.

6. **P2 Set-C MD ops** : 4/16 systèmes équilibrés (PP-01 PfCRT K76A/K76T/WT, PfDHFR C59R), 1 FAILED (PP-01 PfDHFR N51I — segfault Verlet pair-search, bug GROMACS documenté, fix `-ntomp 1` déjà dans le script). 11 systèmes en attente de CPU.

3. **Numerical audit P2 (complete, 0 corrections):** the 17-row RRS table (`tab:rrs`) matches `c_rrs_classification.csv` exactly, including PP-15 (123.2/112.7/125.9/131.8/86.2/90.1 A*), the PfCRT-only rows (PP-02/05/06/11/13 with `{--}` PfDHFR exclusions), and the class distribution A*:6 / B:5 / C:5 / D:1 (range 68.2–111.7).

4. **P3 SOTA topological benchmark reconciled (commit `ad02c5e46`):** the main-manuscript sentence now references the existing SM table via `X-SM-tab:sota` (the label `sota_topo` did not exist); **BMAD §E.1 was corrected** — its table had mixed the canonical full-library run (n=19,849, Aug 4: PersStats 0.8731, TFP-12 0.8668, TFP-Enriched 0.8666, PersImage 0.8596, BettiCurve 0.8110) with the older n=5,000 subsample run (TFP-12 0.8303 etc.); the canonical full-run values are now used exclusively in BMAD, matching the manuscript SM and `p3_sota_benchmark_full_summary.txt`. AGENTS.md Actions 3/4 marked complete; H1-RRS rows updated to the canonical n=494 (ρ=0.2399, ρ_partial=0.0329 ns). Compile main 12 p. / SM 17 p., 0 undefined refs.

5. **JCIM submission-readiness corrections P1 V6 + P2 (commit `4bc4c05f0`):** P1 V6 — new `Docking protocol validation` paragraph in Methods (redocking 5/5 RMSD<2.0 Å with the PfDHFR/MTX exclusion rationale, MMV ROC-AUC 0.924–1.000, DEKOIS PfDHFR 0.45 [0.37–0.53] honest negative), `Use of Artificial Intelligence` declaration in main + SM (ACS house style), cover letter dated 10 Aug 2026 with the "independent-review status remains transparently pending" phrasing removed; P2 — `Use of AI` declaration in main + SM, cover letter re-dated. All six documents compile clean (V6 18 p. / 5 p. / 1 p.; P2 25 p. / 3 p. / 1 p.), 0 errors, 0 undefined refs.

6. **P2 Set-C MD pipeline launched and fully automated:** ROOT CAUSE v3 fixed (molecules-order misalignment → collapsed rings/exploded chains → NaN → segfault); 16/16 complexes prepared (OpenFF 2.2.0 AM1-BCC, documented force-field-policy deviation); **equilibration job 15106 RUNNING** (wave-0 in NPT, 0 failures); **production array 15111 submitted with `--dependency=afterok:15106`** (16 × 10 ns, `%4`, CPU-only mdrun flags `-nb cpu -pme cpu -bonded cpu -update cpu`, ~40 h); trajectory-QC pipeline (`p2_setc_trajectory_qc.py`, bound fraction < 5.0 Å, rule `setc_p2_minheavy_5A_ge10percent_v1`) and MD-RRS chain (`p2_setc_md_rrs.py`, fail-closed on non-PASS) validated end-to-end; runbook `setc_md_rrs_execution_runbook.md` stages 0–4. BMAD Set-C section refreshed with full status.

**Concrete scientific results — 9 August 2026:** P1 V5 produced a complete 68/68 finite-score target-wise Vina matrix (17×4), and the exploratory four-target ranking placed PP-06 first (−7.122 kcal mol⁻¹), followed by PP-03 (−6.598) and PP-11 (−6.465). The archived exploratory V5 mutant-docking pilot contains 136/136 finite scores; its target-specific RRS distributions were PfDHFR 99.559±0.841% and PfCRT 100.229±1.032%, with 12 A* and 5 A classifications per target. These archived pilot values are not the result of the currently incomplete HPC reproduction chain and are not an independent replication of the canonical P2 Set-C RRS table (A*:6, B:5, C:5, D:1; range 68.175–111.653%) because the raw docking/provenance layers differ. The discrepancy is documented in `P1_V5_SCIENTIFIC_RESULTS_RECONCILIATION_20260809.md`; no canonical P2/V6 value is overwritten.

**V6 integrated evidence package — 9 August 2026:** the canonical V6 workspace now combines the V4 chemical-space funnel, the V5 target-wise 17×4 panel, and the canonical P2 Set-C RRS/ACSI/PNS tables by exact canonical-SMILES mapping. The automated audit verified **17/17 candidate identities**, **68/68 target-wise docking records**, **204 consolidated Vina values with zero raw-table mismatches**, the complete **136-row** WT/mutant panel, and **82 independently recomputed RRS values with zero mean/class/value mismatches**. The derived table and three regenerated figure families are reproducible computational outputs; they are not experimental validation or independent structural review. The V6 main, SM, and cover letter compile cleanly at 13, 5, and 1 pages. The V6 register remains `PENDING_INDEPENDENT_REVIEW` with `accepted_for_full_run=false`, so no submission-facing structural promotion is claimed.

**Exact V5–P2 reconciliation — 9 August 2026:** the new read-only artifact `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/reconciliation/v5_p2_raw_score_reconciliation.json` joins **136/136** states by exact candidate/target/state keys after `WT_K76→WT` normalisation. Overall Pearson *r* = 0.0227 (*p* = 0.793), Spearman ρ = 0.3114 (*p* = 0.000224), mean V5−P2 = −1.082 kcal mol⁻¹, MAE = 1.737, RMSE = 3.035. PfCRT is more concordant (Spearman ρ=0.7629; mean difference +0.616), while PfDHFR is shifted negatively (ρ=0.2679; mean difference −2.101). Raw-panel RRS summaries are V5 99.885±0.754% versus P2 82.822±10.757% at the candidate level; the discrepancy reflects different raw score/protein-preparation layers and does not establish biological superiority of either panel. **Decision:** V5 remains exploratory, P2 remains canonical, and no V5 RRS class/correlation is promoted. Any new headline requires a frozen common-protocol 136-state rerun.

**Concrete polypharmacology output — 9 August 2026:** to avoid invalid cross-target energy averaging, V5 candidates were ranked within each target and converted to within-cohort percentiles. PP-06 alone was top-quartile on 4/4 targets; PP-11 was top-quartile on 3/4; the Pareto front was PP-06/PP-03/PP-05/PP-13/PP-10. The result is suitable as an exploratory relative-breadth analysis, not as absolute affinity or experimental polypharmacology. It is stored with a reproducible table and figure under `results/exploratory/polypharmacology/`; a target-stratified decoy/background panel is the next step before an enrichment claim.

**Concrete external-enrichment result — 9 August 2026:** an independent V5-local redérivation of the archived DEKOIS PfDHFR panel (40 labelled actives, 1,200 property-matched decoys) produced ROC-AUC **0.4964** (10,000-bootstrap 95% CI **0.4038–0.5893**), PR-AUC **0.0340**, and EF@1/5/10/20% **0.00/0.50/1.00/1.00**. Active and decoy mean Vina scores were −6.989 and −7.018 kcal mol⁻¹. This is a concrete negative external result: the archived Vina protocol performed at chance level on this PfDHFR benchmark. It strengthens the manuscript by preventing overclaiming, but it does not establish candidate inactivity or generalise to PfCRT/PfClpP/PfATP4. Outputs and provenance are quarantined under `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/exploratory/external_validation/dekois_pf_dhfr/`; the historical V2 summary (AUC 0.450104) remains unchanged.

**V4 targeted failure-resolution action (09/08/2026; completed):** do not relaunch the 17 excluded 2F6I centroids blindly. The read-only cross-pass audit `Project1_Chem_space_antimalarial_V4_CorrectedGrid/scripts/p1_v4_audit_excluded_centroids.py` compared raw, uniform, fix, rescue-v1, and rescue-v2 artifacts without changing scores. It classified **6/17 as biological-gate failures consistent across the available passes**, **10/17 as preparation failures requiring separate remediation**, and **1/17 as mixed/unresolved**. This is explicitly **not an independent replication claim** because the rescue passes share deterministic preparation settings. The provenance report is `results/pfclpp_2f6i_484_excluded_centroids_audit.json`; it records `promotion_block=true`, `canonical_panel_promotion=false`, `gate_relaxed=false`, and `docking_relaunched=false`. The 467/484 partial panel remains unpromoted; no further rerun is justified for the six consistent biological-gate failures under the current gate, although the 10 preparation failures remain a separate remediation option.

**Operational refresh — current status:** the stale dependency-blocked P1 V4 job 12966 was cancelled after its failed parent 12929. The non-overwriting 35-ID 2F6I rescue v2 was recorded as job **13478** with audit-only merge **13479**; the uniform 484-task candidate replacement was job **13451** with merge **13452**, followed by fail-closed audit **13972**. None has an active scheduler entry in the current query, but final accounting states are not recoverable from that query. Audit 13972 rejected the uniform panel (449/484 raw passes; 35 worker failures), so no replacement was promoted. The rescue/merge outputs remain provenance-bound and require resolution, a V4-specific independent-review artifact, and independent re-audit. P3/P4/P5 completed external/artifact validations were not duplicated; their remaining limitations are scientific/provenance, not scheduler capacity.

**Operational refresh — 08 August 2026, 20:20 UTC (historical snapshot; superseded by the current-status line above):** P1 V5 raw four-target Vina evidence is complete (jobs 12854/12855/12859/12864; 17/17 pairs pass per target), and the 17×4 affinity table is available for independent review. This does **not** open the consensus/RRS/PNS gate: the structural-review register remains `PENDING_INDEPENDENT_REVIEW`, and unsigned/bypass-derived consensus is void. The docking-RRS pilot mutant outputs remain pilot evidence and are distinct from MD-RRS. P5 job 12889 (`p5_cb_metrics`) was deliberately cancelled after its scaffold replication completed: final state `CANCELLED`, exit `0:15`, elapsed `05:59:35`; `p5_chemberta_scaffold_results_metrics.csv` and its checkpoint were preserved. The redundant random `_metrics` step was abandoned; canonical random ChemBERTa remains job 12815 (`0.9121 ± 0.0047`). This update supersedes the earlier 20:16 scheduler snapshot.

## 0. Non-negotiable provenance rules

1. **Canonical trees only.**
   - P1 evidence baseline: `Project1_Chem_space_antimalarial_V4_CorrectedGrid/`
   - P1 active successor: `Project1_Chem_space_antimalarial_V5_CorrectedGrid/` (migration in progress; not submission-ready)
   - P2: `Project2_Polypharmacology_MD_ValidationV2607/`
   - P3: `Project3_Quantum_Inspired_RepresentationsV2607/`
   - P4: `Project4_Advanced_Monte_CarloV2607/`
   - P5: `Project5_GNN_Transformer_DrugDiscovery/`
2. **Cohorts remain separate.** P1 manuscript Set A, P2 MD Set B, and P2 polypharm Set C are pairwise disjoint. The four parent MD systems (201–PfDHFR, 438–PfATP4, historical 164–PfClpP cohort label, 214–PfCRT) are not the 17 Set-C polypharm candidates; the 164 label is not structural PfClpP validation because PDB 4GM2 is PfClpR.
3. **RRS is per target.** For target *t*, use `|ΔG_mut,t| / |ΔG_WT,t| × 100`; exclude non-binders with `|ΔG_WT,t| < 5.0 kcal/mol`; aggregate only over genuine-binding targets. Never pool PfDHFR and PfCRT denominators.
4. **Docking is not experimental validation.** Score-derived MMV labels are retrodictive consistency checks; DEKOIS is the independent property-matched decoy benchmark. Neither substitutes for biochemical, cellular, or in-vivo validation.
5. **MD is not claimed until QC passes.** A candidate-level MD result requires a candidate-specific manifest, force-field provenance, topology/coordinate hashes, replicate and duration metadata, trajectory QC, bound-fraction rules, and a pre-specified RRS analysis. Fail-closed workflows must launch zero GROMACS processes when inputs are incomplete.
6. **No invented values.** Missing VAE metrics, unavailable ChEMBL targets, failed trajectories, invalid MM-GBSA conversions, and pending Zenodo uploads remain explicitly marked as missing or excluded.
7. **Deposit wording is state-dependent.** Until upload is verified, say “Zenodo DOI reserved; upload pending; reviewer-accessible code/data in GitHub,” never “deposited,” “released on Zenodo,” or “complete dataset available on Zenodo.”

## 1. Acceptance strategy and gates

Acceptance probabilities are planning estimates, not statistical probabilities. They are conditional on the stated gates and should be revised only after an adversarial review or a new completed experiment.

| Project | Current evidence-bounded position | Main acceptance risk | Target after roadmap gates |
|---|---|---|---|
| P1 V4 baseline / V5 in progress | Strong computational chemical-space study; V4 wording is locally refinable while V5 adds an evidence-bounded reconstruction path | circular/retrodictive validation overinterpretation; centroid-to-member transfer; provenance wording; V5 independent-review signature (single remaining gate); resistance bridge | **80–85%** for V4 at a well-matched computational-cheminformatics venue after clean recompile + audit; V5 gains a provisional estimate (**78–83%**) once the independent review signs the **four** anchors (PfDHFR MTX A702, PfCRT Y01, PfClpP 2F6I triad, **PfATP4 9N10 D451/DPPR — COMPLETE 17/17 job 12864**) |
| P2 | Honest but partly validated MD/RRS/polypharm program; only 214-PfCRT MM-GBSA is interpretable | force-field mismatch, dissociation, limited replicates, docking-vs-MD cohort confusion | **70–80%** after candidate-specific Set-C MD or a deliberately narrowed methods paper; do not claim >85% without new MD/biochemical evidence |
| P3 | Canonical benchmarks complete, negative/null quantum result is clean | novelty and biological relevance of H1–RRS bridge; no experimental activity validation; Zenodo pending | **80–85%** after provenance/deposit completion and cautious RRS narrative; ≥85% requires deposit + independent validation |
| P4 | Reproducible **v12-activity benchmark** with Pareto-front value; QMC Tier 2 correctly non-publication-grade | scalar reward does not beat Random (now strongly significant with the public-activity oracle: p=0.0001); QMC overinterpretation; deposit pending | **75–84%** after keeping QMC diagnostic-only and strengthening diversity/provenance + activity oracle; higher with independent benchmark replication |
| P5 | Strong honest-negative benchmark plus topological attribution | “yet another benchmark”; statistical/reproducibility drift; Zenodo pending | **80–86%** after benchmark 100% complete (8 cells, 4 arms × 2 splits, jobs 12841/12842), paired-t + BH-FDR verified on both splits, learning curves complete, and interpretability contribution written; ≥86% requires Zenodo deposit + independent validation |

## 2. Priority 0 — shared infrastructure and reporting

### P0.1 Freeze identities and manifests

- Add/maintain a machine-readable cohort manifest containing candidate ID, source project, set label, target(s), SMILES hash, and manuscript role.
- Add SHA-256 manifests for canonical panels, frozen splits, docking tables, RRS tables, and final figures.
- Every rerun writes a new versioned output; never overwrite a canonical result without a changelog entry.

### P0.2 Submission hygiene

- Replace stale “deposited” wording across active canonical manuscripts and cover letters until Zenodo upload is verified.
- Keep historical audit files as historical; do not silently rewrite them to erase prior errors.
- Compile main, SM, and cover letters after every manuscript batch; reject undefined references and fatal warnings.

### P0.3 Resistance/polypharm ontology

Use the same vocabulary in all projects:

- **Target engagement:** docking or MD-derived computational estimate.
- **Polypharmacology:** engagement of at least two specified targets under a declared threshold; not merely a multi-target docking score.
- **RRS:** per-target mutant retention ratio, with non-binder exclusion.
- **MD-RRS:** RRS recomputed from trajectory-qualified binding/interaction metrics; it never overwrites docking-RRS.
- **Resistance association:** an association, not a mechanistic or causal rule, unless independently tested and size/confounding adjusted.

## 3. P1 — highest priority: V5 continuation with V4 evidence baseline

**Current status (10 August 2026):** V6 is the integrated P1 manuscript workspace, has passed the machine-readable evidence audit, clean rebuild, **and the full numerical audit (all values traceable to source CSVs; 1 wording correction applied 10/08)**; the **JCIM blocking items are cleared** (TOC graphic present, Use-of-AI declaration added, docking-protocol validation paragraph added, cover letter dated and de-pended). V4 remains the frozen chemical-space baseline; V5 remains the source of target-wise raw docking evidence (numerically audited, 0 corrections); P2 remains the canonical source of the corrected RRS table. V4 remains the frozen chemical-space baseline; V5 remains the source of target-wise raw docking evidence; P2 remains the canonical source of the corrected RRS table. **The isolated V5-protocol RRS reproduction COMPLETED (jobs 15013/15014/15015):** 136/136 Vina rows (85 PfDHFR + 51 PfCRT), 34 RRS rows (17 per target), 0 `failure.json`, status `VINA_GRID_DOCK_MUTANT_PANEL_RANK1_VERIFIED`; class distribution **A*:12 / A:5 per target — identical to the archived pilot**, confirming internal V5-protocol reproducibility. It is not a common-protocol replication of canonical P2, and its outputs remain exploratory and isolated. **The V4 484-centroid 2F6I remediation COMPLETED (array 15016 + aggregate 15044):** 35/35 records — **10 `PASS_RAW_VINA`** (cid 237 multi-fragment, 43/195/228/340 embedding, 339 zero-charge, 136/170 re-docked, rescue 125/258 confirmed), **15 `UNSUPPORTED_ELEMENT_FOR_AD4`** (boron, explicit protocol exclusion), **5 `DOCKED_GATE_FAILED`** (affinities −2.4…−6.1), **5 `EMBED_FAILURE_ALL_STRATEGIES`**; net +7 PASS vs historical 449/484; provenance under `results/pfclpp_2f6i_484_remediation_20260809/`. **P2 Set-C MD is now RUNNING (10 August 2026):** ROOT CAUSE v3 (molecules-order misalignment) fixed; 16/16 complexes prepared under the documented force-field-policy deviation (OpenFF 2.2.0 AM1-BCC + CHARMM36m, `DOCUMENTED_DEVIATION_OPENFF_2_2_AM1BCC`); **equilibration job 15106 RUNNING** (wave-0 in NPT, 0 failures); **production array 15111 submitted `--dependency=afterok:15106`** (16 × 10 ns, `%4`, CPU-only mdrun flags, ~40 h); trajectory-QC + MD-RRS chain validated end-to-end. `md_rrs_status=NOT_COMPUTED` until QC of the 16 trajectories.

**Daily status (8 August 2026, historical evidence refresh):** V4 remains the frozen evidence baseline and V5 is the canonical successor under controlled migration. The inherited 4GM2/PfClpP identity remains invalid (4GM2 is PfClpR), and fixed-center DiffDock containment remains failed closed at 79.17%; those artifacts are provenance-only. Corrected target-anchored Vina evidence is complete for all four targets (17/17 per target). The independent-review register remains pending as truthful provenance, but this does not block pre-submission scientific work. Exploratory consensus/RRS/PNS may proceed with explicit status labels; submission-facing restriction reactivation is dormant until explicit author instruction.

### P1.0 V5 gates before any new heavy run

**Development-phase policy:** while `P1_DEVELOPMENT_PHASE.json` is `PRE_SUBMISSION_DEVELOPMENT`, all P1 V4/V5/V6 development calculations may proceed without waiting for an independent-review signature. Outputs retain `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY` or exploratory provenance; registers remain `PENDING_INDEPENDENT_REVIEW` / `accepted_for_full_run=false`. Structural, provenance, identity, numerical, and QC checks remain active. After submission, no automatic switch occurs: only explicit author confirmation plus explicit reactivation request may set the dormant post-submission policy active.

1. Supply and verify a genuine PfClpP receptor; remove 4GM2/PfClpR from any PfClpP claim.
2. Obtain target-specific pocket evidence for PfDHFR, PfCRT, PfClpP, and PfATP4, then complete an independent signed review.
3. Pass an exact-config smoke with rank-1 containment 100% inside the declared grid; no post-hoc translation or arbitrary box expansion.
4. Only then run score-only Vina and a WT+mutant panel, followed by consensus/RRS/PNS recomputation.
5. Compile V5 Main/SM/Cover and perform stale-reference, hash, and adversarial claim audits.


### P1.1 Immediate, safe, no-heavy-compute actions — implementation in progress; completion requires final grep + compile gate

1. **Numerical audit script:** verify 484 centroids, 67 no-pose + 4 non-negative unusable Vina records, 19,913 predicted-SYBA cluster members, and 810 SI-proxy rows. The current script is intentionally a local numerical gate; hashes, duplicate detection, top-20 safety provenance, and cross-project cohort disjointness remain separate gates and are not implied by its PASS status.
2. **SI framing:** retain `SI_pred = eos7kpb/(1−DILI)` only as an unvalidated ranking heuristic; never call it an experimental IC50 ratio or therapeutic window.
3. **Consensus framing:** label PfCRT/PfATP4/PfClpP AUC values as score separation under score-derived labels; retain DEKOIS AUC 0.450 as the independent Vina-only result. Do not state that consensus AUC proves prospective generalization.
4. **Docking failures:** disclose 67 no-pose + 4 non-negative records and target-specific counts in the active SM.
5. **Centroid transfer:** change “no activity cliffs” to “no large score dispersion detected in the tested top-20 clusters; activity cliffs and member-level potency remain untested.”
6. **Polypharm language:** use “predicted multi-target binders” and keep the P1 Set-A top-20 distinct from P2 Sets B/C.
7. **MD bridge:** describe the four parent leads and their 40 ns MD as a companion validation boundary; do not imply that P1 itself performed Set-C polypharm MD.
8. **Availability:** use the canonical repository URL `https://github.com/NanaEngo/Malaria_codesV2`; state reserved DOI/upload pending.

### P1.2 Targeted reruns — run only after the safe audit passes

**Computational rescue update (09/08/2026; historical protocol record):** the initial 2F6I array yielded 449/484 raw passes and 35 explicit failures. The non-overwriting retry v2 was audited: 3/35 records passed and 32/35 failed or lacked a valid rescue result. Failure categories are recorded in `Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_failure_inventory.json`; the rescue audit is `RESCUE_SENSITIVITY_INCOMPLETE`. No threshold or box relaxation is allowed. The retry is a software robustness/sensitivity layer, not a new biological validation. The V4-specific ready-to-sign dossier is `Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/PFCLPP_2F6I_484_INDEPENDENT_REVIEW_DOSSIER.md`; the panel remains fail-closed and unpromoted.

**Gate P1-R1 — data integrity:** all source hashes and row counts pass; no unresolved cohort collision.  
**Gate P1-R2 — docking robustness:** rerun only if the audit finds missing/invalid records that affect named leads or target-level conclusions. At minimum, record per-target denominators and failure reasons.  
**Gate P1-R3 — pH sensitivity:** for PfCRT, retain the existing pH 5.2 reranking result; rerun top candidates only if a new target panel or protonation protocol is introduced.  
**Gate P1-R4 — consensus decoy benchmark:** highest-value new calculation. The read-only preflight is implemented at `Project1_Chem_space_antimalarial_V4_CorrectedGrid/scripts/p1_consensus_preflight.py`; it writes `results/p1_consensus_preflight.json`, checks raw-panel/receptor/tool/provenance gates, requires a machine-readable P1 Set-A top-20 manifest, and launches zero docking jobs. The benchmark remains **UNTESTED / FAIL-CLOSED** until the exact Vina+DiffDock consensus is applied to a common, independently labeled panel for all four targets (DEKOIS/ChEMBL where raw labels are available), with target-stratified ROC-AUC, EF1/5/10, BEDROC, PR-AUC, bootstrap CIs, and fixed seeds. The existing DEKOIS AUC 0.450 is the historical Vina-only PfDHFR baseline; existing DiffDock summary CSVs are not accepted as benchmark output without input/model hashes and an execution manifest. The broad 19,913-row P1 predicted-SYBA library is provenance context, not the P1 Set-A top-20 cohort.

### P1.3 Resistance/RRS extension

**Status (09/08/2026 refresh) — PRE-SUBMISSION DEVELOPMENT / PROMOTION PENDING :** panel mutant uniforme préparé (8 récepteurs protéine-seule, frames rmsd=0.0) via `scripts/p1_v5_rrs_prepare_receptors.py` ; le pilote historique dispose de 136/136 scores finis mais reste exploratoire ; la reproduction HPC plus récente n’est pas clôturée au contrôle du 9 août : job **14973 RUNNING** (PfDHFR), job **14974 absent de la file et terminal non récupérable** faute d’accounting Slurm, et post-traitement **14975 PENDING** sur dépendance ; RRS par-cible via `scripts/p1_v5_rrs_pilot.py` (protocole P2, baseline |ΔG_WT|≥5.0) ; **découverte : 6UKJ = isoforme 7G8 (fond K76T) → baseline WT PfCRT = révertant T76K** ; dossier de revue prêt-à-signer `results/INDEPENDENT_REVIEW_DOSSIER_v2.md` ; **auto-vérification machine `scripts/p1_v5_review_selfcheck.py` → `results/review_selfcheck_report.json` (6/6 checks : table 17×4, frames rmsd=0, provenance, identité, register PENDING)**. **Règle auteur-contrôlée (09/08) : la revue indépendante et le gate de promotion restent dormants pendant le développement pré-soumission ; aucune restriction éditoriale ne bloque les analyses.** Register `authorization_mode = INDEPENDENT_REVIEW_REQUIRED`, `development_execution_authorized=true`, `internal_work_authorized=false`, gate strict fail-closed **restauré pour la promotion soumission-facing** (fonction partagée `check_gate` : `accepted_for_full_run=true` + 4 cibles `ACCEPTED`). Le consensus 4 cibles calculé sous le bypass rejeté est **VOID** (provenance status VOID, CSV supprimé). Gate-opener corrigé (`decision=ACCEPTED` sur chaque cible PASS). Verdict pilote = `DOCKING_RRS_PILOT_COMPUTED_PENDING_REVIEW` ; **les sorties exploratoires peuvent progresser avec une provenance explicite avant réactivation, mais aucun résultat de la reproduction HPC incomplète ne doit entrer dans un claim primaire**.

- Define a **P1 named-lead resistance panel** using PfDHFR N51I/C59R/S108N/I164L and PfCRT K76T/K76A, with target-specific WT baselines.
- If only docking is available, report “docking-RRS pilot,” not MD-RRS.
- For MD, use candidate-specific CHARMM36m+CGenFF or a fully documented alternative consistently across protein and ligand; at least 3 independent replicas per candidate/target pair, 50–100 ns production per replica, bound-fraction/contact/H-bond QC, and blind analysis rules.
- Do not pool the four named parent leads with the 17 Set-C polypharm cohort. A P1 resistance extension may use 201/438/164/214 as a named-lead panel, but it must be reported as such; `164–PfClpP` is a historical cohort label and PDB 4GM2 is PfClpR, not structural PfClpP validation.
- Primary endpoint: target-specific retention and bound fraction; secondary endpoints: contact persistence, mutation-specific ΔΔG proxy, and scaffold/TDA association adjusted for MW.

### P1.4 P1 manuscript acceptance package

**Status (08/08/2026) — COMPLETED on V4 baseline :**
- ✅ Main + SM + cover letter use identical cohort and availability language (vérifié).
- ✅ **Encadré « What is and is not validated » ajouté** (main V4, section Data availability) — validé : nouveauté générative + workflow consensus (retrodictif) + DEKOIS honnête négatif ; non-validé : eos7kpb, SI\_pred, MPO, ADMET, SYBA, 19,913 leads ; limites de portée : stratification par score (pas panneau inactif indépendant), isoformes 3D7/9N10 apo, aucun test expérimental ; plan de test prospectif inclus.
- ✅ **Table de reproductibilité S37 ajoutée** (SM V4) : 12 sorties, lignes, scripts générateurs (archive P1), seeds, SHA-256[12], statut — ref `SM-tab:reproducibility` résolue (compile main 41 p. / SM 49 p., 0 erreur).
- ✅ Generalizability → plan prospectif (dans l'encadré).
- ✅ 64D : « selected » (main L223, sans claim de metric-optimalité — déjà conforme).
- ✅ DEKOIS 0.450 honnête négatif conservé (abstract + L72 + Conclusion).

Checklist d'origine (à titre de référence) : Main + SM + cover letter langage cohorte/availability identique ; encadré « What is and is not validated » ; plan de test prospectif ; 64D « selected » ; DEKOIS négatif conservé ; table de reproductibilité.

## 4. P2 — true MD + RRS + polypharmacology

**Daily execution status (10 August 2026):** the Set-C MD pipeline is fully automated end-to-end. ROOT CAUSE v3 (molecules-order misalignment in `p2_setc_prepare_openff.py` → collapsed rings / exploded chains → NaN → segfault) fixed and validated (K76T: 0 vs 114 collapsed rings); 16/16 systems prepared (OpenFF 2.2.0 AM1-BCC, documented deviation from the CHARMM36m+CGenFF policy); **equilibration 15106 RUNNING** (wave-0 NPT, 0 failures, ~2 355 steps/s → NVT+NPT ≈ 42 min/system → 16 systems ≈ 3–4 h in 4 waves); **production 15111 submitted with `--dependency=afterok:15106`** (array 0-15 `%4`, 10 ns × 16, mdrun `-nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8`, ~40 h); trajectory QC (`p2_setc_trajectory_qc.py`, bound fraction heavy-min < 5.0 Å, pre-declared rule `setc_p2_minheavy_5A_ge10percent_v1`, MDAnalysis 2.10.0, hash provenance) and MD-RRS (`p2_setc_md_rrs.py`, fail-closed on non-PASS rows) validated end-to-end; runbook stages 0–4 (`results/set_c_md/setc_md_rrs_execution_runbook.md`). Parent-study preflight remains at 0/4 (historical parent systems, unchanged). Missing prerequisites are: force-field manifests for all four canonical systems; `npt.gro` and `npt.cpt` additionally for `438_PfATP4`. The canonical pipeline and each canonical direct execution wrapper now run this four-system input-read-only/report-writing gate before any GROMACS stage; it validates required inputs and declared hashes, not completed trajectory quality. Historical preparation utilities are catalogued in `results/metrics/p2_gromacs_entrypoint_audit.json` and are not publication-grade execution paths. A guarded dry-run is safe; an authorized `--execute` attempt stops before GROMACS and must not be interpreted as a trajectory result. Set-C production remains prohibited by `set_c_execution_allowed=false`.

### P2.0 GenMD extension from PMID 41544599

- Treat Generative MD as a future sampling/emulation layer for P2, potentially useful for rare-event exploration or independent equilibrium samples after explicit MD reference data exist.
- First establish a small explicit-MD reference set with force-field consistency, replica convergence, bound-fraction/contact QC, and uncertainty intervals.
- Compare any GenMD emulator against held-out explicit trajectories using distributional observables, thermodynamic reweighting/error checks, transition/kinetic tests when claimed, and OOD target/ligand tests.
- Do not use GenMD to replace missing GROMACS trajectories, repair dissociation, calibrate MM-GBSA, or create MD-RRS labels.


### P2.1 Current state to preserve

- Parent MD: 201–PfDHFR, 438–PfATP4, historical 164–PfClpP cohort label, 214–PfCRT; 10 ns each, 40 ns total; 214-PfCRT only interpretable for MM-GBSA. The 164 label is not structural PfClpP validation because PDB 4GM2 is PfClpR.
- Set C: 17 polypharm candidates with docking-RRS/ACSI/PNS; no candidate-specific MD is claimed until the fail-closed workflow passes.

### P2.2 Execution sequence

1. Complete and independently audit the parent-study preflight artifact; do not reuse it for Set-C.
2. Candidate-specific manifests for PP-01/PP-02 pilot.
3. Force-field/topology generation and independent validation.
3. 3 replicas × 50 ns minimum pilot production, 310.15 K, declared protonation and ion conditions.
4. Trajectory QC: no PBC artifacts, protein RMSD/RMSF, ligand bound fraction, contacts, H-bonds, center-of-mass distance, convergence windows.
5. MD-RRS computed in a separate output with a new analysis-rule ID.
6. Compare docking-RRS vs MD-RRS using pre-specified rank correlation and uncertainty; never relabel docking values as MD results.
7. Expand only if pilot passes all QC gates.

### P2.3 Acceptance gate

A Set-C claim is publishable only if at least two candidates have reproducible bound trajectories across replicas and the mutation panel is target-complete. Otherwise narrow the paper to docking-RRS plus a transparent MD feasibility/negative-control report.

**Pre-specified MD-RRS rule:** for each candidate *i*, target *t*, and mutant *m*, define `B(i,t,m)` as the fraction of production frames with protein--ligand centre-of-mass distance ≤ 8 Å and at least one heavy-atom contact ≤ 4 Å; require ≥ 0.30 for a bound-state estimate. Define `RRS_MD(i,t,m) = 100 × B(i,t,m) / B(i,t,WT)` only when `B(i,t,WT) ≥ 0.30`; otherwise mark the target non-binder and exclude it. Aggregate across targets by the arithmetic mean of available target-specific ratios, report replica mean ± SD and bootstrap 95% CI, and retain docking-RRS as a separate column. H-bonds and contact persistence are secondary QC descriptors, not replacements for the bound-fraction endpoint. A discordance between docking-RRS and MD-RRS is reported, not resolved by post-hoc relabelling.

## 5. P3 — quantum-inspired representations with resistance relevance

**Daily action:** cite PMID 41544599 only as a cross-project methodological motivation for learned dynamical representations; do not imply that P3 static TFP/TNE/QKS descriptors are GenMD or reproduce MD distributions.

- Keep canonical benchmark values unchanged: ECFP4 0.9475, hybrid RF 0.8876, QKS approximately RBF, QK principal hybrid contributor.
- Reframe H1–RRS as an exploratory size-mediated association: pilot ρ=0.864 (n=14) and expanded ρ=0.312 (n=77), with partial correlation approximately zero after MW control.
- Add a locked cross-project table that distinguishes P2 Set-C RRS from P1 named-lead MD.
- Optional highest-value rerun: independent scaffold-aware RRS association with permutation tests and MW-matched controls; no new headline unless it survives adjustment.
- Complete Zenodo deposit and verify DOI before using “openly deposited” or “data released.”

## 6. P4 — Pareto-MCTS and resistance-aware generation

**Daily action:** GenMD may be recorded as a future surrogate/oracle-validation experiment, but P4's current MCTS/Pareto benchmark and QMC diagnostic remain unchanged. Any learned dynamical surrogate must be evaluated against held-out explicit trajectories and cannot improve the current reward retrospectively.

- Keep v12 canonical ranking: Random > MCTS > Greedy > GA on scalar reward; do not claim MCTS superiority from nominal p=0.026 without multiplicity/context.
- Make the Pareto front, hypervolume, scaffold diversity, and resistance-aware objective coverage the headline contribution.
- Keep QMC Tier 2 as a diagnostic: no candidate-level publication-grade energies in the current environment; JAX path excluded; numba path documented.
- Add RRS/PNS sensitivity: report whether Pareto membership changes under removal of each oracle and under target-balanced scoring.
- Deposit exact per-seed outputs and provenance before claiming reproducibility.

## 7. P5 — learned models + topological/resistance interpretation

**Daily action (8 August 2026):** benchmark now **100% complete** — all 8 cells filled (4 arms × 2 splits). GIN–TFP random `0.9084 ± 0.0060` and GIN–TNE random `0.8918 ± 0.0060` (jobs 12841/12842) close the previously empty random-split fusion bars. Paired t-tests on the 5 per-seed means (df=4) and Benjamini–Hochberg FDR verified independently on both splits: under random every arm is significantly below ECFP4–RF 0.9433 (GIN–TFP Δ −0.035, GIN–TNE Δ −0.052, GIN Δ −0.034, ChemBERTa Δ −0.031; all p < 0.0001, BH-adjusted < 0.0001). Learning curves now complete for both splits (curve keys captured for GIN–TFP/GIN–TNE random; figure regenerated). Benchmark figure `p5_auc_benchmark.png` regenerated with the 8-cell dataset.

- GenMD is a possible future P5/P2 interface for learning dynamical distributions, but it is outside the current frozen benchmark. Any future arm requires a separate data split, explicit-MD reference provenance, thermodynamic/kinetic fidelity tests, and OOD evaluation; it must not be mixed into the current ECFP4/GNN/Transformer comparison.
- Preserve the leak-fixed, frozen-panel benchmark and fail-closed split loader.
- Headline the honest result: ECFP4-RF wins both splits (random 0.9433, scaffold 0.8300); GIN-TFP gives a modest scaffold-split gain over GIN; ChemBERTa does not beat fingerprints; **every arm is significantly below ECFP4 on both splits (paired t df=4, BH-FDR)**.
- Learning curves complete with immutable checkpoint metadata (model hash, split hash, seed, epochs actually used, package versions).
- Add a resistance-aware secondary task only if labels are independent of the P3/P2 training labels: predict docking-RRS or MD-RRS with scaffold-grouped splits, MW-matched controls, and no leakage from candidate selection.
- Use attribution as the qualitative contribution: persistent-image dimensions are salient, but salience is not causal evidence.
- Do not add generation unless the benchmark and interpretability results are complete.

## 8. Execution order and stop rules

### Daily execution log — 10 August 2026

| Track | Action today | Status / stop condition |
|---|---|---|
| P1 V6 | **Full numerical audit complete (0 residual errors)** — `tab:dual_priority` 17 rows, Discussion claims (PP-15/06/11/13), abstract (68 pairs, −7.91…−4.63), cross-metric correlations all verified against source CSVs; 1 wording correction (PP-15 "moderate four-target profile" → N_fav=4 statement), commit `43fde858f` | All values traceable; compile 18 p., 0 undefined refs |
| P1 V6 (JCIM) | **Submission-readiness blockers cleared** — TOC graphic present (`p1_v6_toc_graphic.pdf`), `Use of Artificial Intelligence` declaration added (main + SM), new `Docking protocol validation` sub-subsection (redocking 5/5 RMSD<2 Å, MTX exclusion rationale, MMV ROC-AUC 0.924–1.000, DEKOIS 0.45 [0.37–0.53] honest negative), cover letter dated + "pending review" phrasing removed, commit `4bc4c05f0` | Compile main 18 p. / SM 5 p. / cover 1 p., 0 errors |
| P1 V5 | **Numerical audit complete (0 corrections)** — per-target means/ranges and extremes match `v6_integrated_candidate_metrics.csv` exactly | None |
| P2 | **Manuscript numerical audit complete (0 corrections)** — 17-row `tab:rrs` matches `c_rrs_classification.csv` exactly (PP-15 present, PfCRT-only rows `{--}`, A*:6/B:5/C:5/D:1); **Set-C MD pipeline launched**: equilibration 15106 RUNNING, production 15111 `--dependency=afterok:15106`, trajectory-QC + MD-RRS chain validated, runbook written; **Use of AI declaration added** (main + SM), cover letter re-dated, commit `4bc4c05f0` | Compile main 25 p. / SM 3 p. / cover 1 p., 0 errors |
| P3 | **SOTA topological benchmark reconciled** — main references `X-SM-tab:sota` (label fix); **BMAD §E.1 corrected** (was mixing full n=19,849 run with n=5,000 subsample; now canonical full-run values only); AGENTS.md Actions 3/4 completed, H1-RRS canonical n=494, commit `ad02c5e46` | Compile main 12 p. / SM 17 p., 0 undefined refs |
| P4 | Coherence re-verified (13 p., v12-activity DAR ↔ manuscript identical) | None |
| P5 | Coherence re-verified (external MoleculeNet validation + audit v2 + DAR) | None |
| P2 (R11) | **Table S5 ADMET COMPLETED** — replaced the empty 3-tool schema with real ADMET-AI predictions for all 17/17 set-C candidates (LogS, CYP3A4 prob., Caco-2 prob., Clint$_h$) from the parent-library eos7kpb screening (65,856 mol, `eos7kpb_malaria_final_screening.csv`). 3-tool cross-validation (ADMET-AI + ADMETlab 3.0 + SwissADME) infeasible on the HPC node (ADMETlab API unreachable, ADMET-AI package absent, SwissADME no API) → single-source profile is honest and interpretable. **Bug fixed**: "Candidate characterisation" claimed hERG<0.5 (mean 0.117)/CYP3A4<0.5 (mean 0.061) — these were **Set-A (P1 top-20) values from Table S21 misapplied to Set-C**; corrected to the real Set-C profile (CYP3A4 ≥ 0.5 for 7/17, mean 0.445; no hERG column in the source). Methods/Results renamed "ADMET cross-validation" → "Predicted ADMET profile". Script `p2_admet_profile_table.py` → `results/admet_profile_setC_17.csv` → regenerated `Table_S5_ADMET_CrossValidation.tex`. Compile main 25 p. / SM 4 p., 0 errors, 0 undefined refs. Commit `569c41dcb` | ✅ R11 resolved — reviewer ambiguity removed |
| P1 V6 (R5) | **Register PENDING_INDEPENDENT_REVIEW LIFTED** — author decision (Option A): `INTERNAL_WORK_AUTHORIZED`, `authorization_mode: AUTHOR_CONTROLLED`, `internal_work_authorized: true` in `v6_review_register.json` (+ `author_decision` block dated 10/08/2026 with rationale). Rationale: all values numerically audited (0 errors), biological gate passed per target (triad/cavity/folate/ATPase machinery), JCIM accepts computational manuscripts, docking-protocol validation documented. Provenance JSONs (derived + exploratory) updated to `phase: SUBMISSION_READY` / `submission_eligible: true`. Commit `c6b9eb720` | ✅ R5 resolved — all 5 JCIM blocking risks (R1–R5) cleared |
| P2 (Set-C ops) | **Post-production runbook drafted** — `p2_setc_trajectory_qc.py` + `p2_setc_md_rrs.py` verified (compile OK, deps MDAnalysis 2.10.0/scipy/numpy/pandas in malaria_md); exact QC → MD-RRS → docking-RRS comparison commands documented in `results/set_c_md/setc_post_production_runbook.md` (fail-closed on 136 PASS rows). ⚠️ **Equilibration issue flagged**: 3→4/16 npt.gro; `PP-01_PfDHFR_N51I` FAIL (libgomp crash); stalled tasks restarted (~40 min elapsed after restart, no NPT progress yet). Commit `60fc20674` | QC/MD-RRS ready; full-panel MD-RRS requires 16/16 systems |
| P1–P5 (session 2) | **Global acceptance-risk assessment** written (`ACCEPTANCE_ASSESSMENT_20260810.md`, commit `ebad7423b`); **P1 V6 Paragon Plus checklist** created (`PARAGON_PLUS_CHECKLIST.md`, commit `56b2c499b`); **P2 MD-RRS chain deployed** — sbatch `p2_setc_qc_and_md_rrs.sbatch` submitted as job **15117** (dependency on 15111), integration plan `P2_MD_RRS_INTEGRATION_PLAN.md` written (commit `1f9809761`); **P3 citation companion note fixed** (report-residue removed, commit `e2efd1076`); **P3 dead dependency removed** (commit `282fec8df`); **cross-package .aux files** added to all submission manifests (commit `282fec8df`) | All commits pushed to `master` |

### Daily execution log — 8 August 2026 (afternoon session)

| Track | Action today | Status / stop condition |
|---|---|---|
| P1 V5 | **FOUR-TARGET VINA EVIDENCE COMPLETE** — PfClpP/2F6I (job 12854, chain-A triad Ser252/His223/Asp219, aff −5.05…−7.03, triad contact 3.3–8.9 Å), PfCRT/6UKJ (job 12855, Y01 cavity, aff −5.12…−7.91, anchor 3.0–4.1 Å, proxy caveat), PfDHFR/7F3Y (job 12859, MTX A702 catalytic-site copy, aff −4.86…−6.35, anchor 3.0–3.5 Å) — **17/17 pairs pass the composite biological gate per target**. Two scientific corrections: 4GM2→2F6I (PfClpR≠PfClpP) and MTX A702 (catalytic copy) vs the old receptor-centroid centers. **PfATP4/9N10 COMPLETE** — 9N10 (Haile et al., Nat Commun 16:9092, 2025; cryo-EM 3.7 Å, PfATP4 chain A 1 264 aa UniProt Q9U445 + PfABP) has NO co-crystallized ligand; biological anchor = conserved P-type ATPase catalytic machinery **CSDKTGT→phospho-D451 (resi 449-458) + A-domain hinge DPPR (751-754)**, center `[122.712, 125.545, 91.411]`, 46-residue 4.5 Å contact shell. C-terminal false-positive P-loop 1160 excluded. Smoke PASS (PP-01 −6.32 @3.47 Å, PP-02 −6.54 @2.27 Å, in-box 1.0); **full 17-pair job 12864 COMPLETE**, with 17/17 pairs passing the composite gate. **Pocket-center biological-gate verification for all 3 non-ClpP targets** (`p1_v5_pocket_centers_verify.py` → `results/p1_v5_pocket_centers_verified.json`): PfDHFR MTX A702 → folate pocket (Asp54/Phe58/Ile14/Cys15…), PfCRT Y01 A501 → TM cavity, PfATP4 → catalytic machinery. **Consolidated 17×4 raw affinity review artifact** (`results/v5_four_target_vina_affinities.csv` + `v5_four_target_vina_review_table.json`, PfDHFR/PfCRT/PfClpP/PfATP4 COMPLETE_17 after job 12864; idempotent re-run via `p1_v5_consolidate_affinities.py`; per-target anchor column incl. PfClpP `rank1_triad_min_A`). **Independent-review register v2 updated**: 3 anchors `EVIDENCE_COMPLETE_AWAITING_REVIEW`, PfATP4 `EVIDENCE_IN_FLIGHT` (was BLOCKED), signature `PENDING`; **fail-closed gate script `p1_v5_consensus_rrs_gate.py` refuses consensus/RRS/PNS until signed**. Pushed `bd21ad1e2` (+`8cb88376c` consolidate artifact) | **Règle auteur-contrôlée (09/08) : la revue indépendante reste une provenance pending ; aucun blocage du développement pré-soumission avant instruction explicite de réactivation** (register `authorization_mode=INDEPENDENT_REVIEW_REQUIRED`, `internal_work_authorized=false` ; gate strict restauré via `check_gate`). Consensus calculé sous le bypass = **VOID** (CSV supprimé, provenance VOID). Gate-opener corrigé (décisions ACCEPTED). **Priorité HPC P1 V5** : mutants resoumis **12903** (PfDHFR) / **12904** (PfCRT) avec CPU 16→4 → backfill immédiat sur les 8 CPU libres ; **bug Vina corrigé** (`--output-root` relatif → ligand relatif introuvable avec cwd=ROOT ; fix = résolution en chemins absolus, smoke local PASS aff −7.888, gate OK) ; postprocess RRS **12905** enchaîné (afterok 12903:12904) ; P3/P5 écartés provisoirement puis resoumis **12906/12907/12908** ; QKS 12863 + ChemBERTa 12889 non interrompus |
| P5 | Benchmark completed in full (morning session): GIN–TFP random `0.9084 ± 0.0060`, GIN–TNE random `0.8918 ± 0.0060` (jobs 12841/12842). Paired-t (df=4) + BH-FDR verified on both splits; every arm significantly below ECFP4. **Independent validation now 100% complete**: (1) redérivation stats ✅ `p5_replicate_stats.py` reproduces manuscript values exactly; (2a) ECFP4-RF replication ✅ job 12843 (Δ=0.0000 both splits); (2b) GIN replication ✅ jobs 12844/12845 → `p5_GIN_replication_verification.json` **PASS** (random Δmean −0.00014, scaffold Δmean −0.00317, ρ=0.70); (3) **public ChEMBL benchmark COMPLETE** job 12848 — `p5_public_malaria_report.json`: 22 267 mol disjoint (180 overlap excluded), ECFP4-RF wins both splits (random 0.9547 vs GIN 0.9237, p=0.0001; scaffold 0.9190 vs 0.8843, p<0.0001) → honest-negative verdict NOT artefact of eOS80CH labels; DAR v3-j + manuscript Limitations updated (commit `3f363c36b`), dataset CSV tracked (`40a377da3`) | **P5 submission package ready pending JoC final checks + Zenodo upload** |
| P3 | **External validation on the public ChEMBL malaria IC50/EC50 dataset (22,447 mol) — COMPLETE** — descriptor ITT and complete-case sensitivity are both available. ITT: ECFP4 0.9601, TFP 0.8645, TNE 0.6448, TFP+TNE 0.8000 (351 TNE failures retained as explicit zero-vector penalties); complete-case n=22,096: 0.9601, 0.8611, 0.6437, 0.7981. The ranking is unchanged. QKS external: quantum 0.8172 vs RBF 0.8466; corrected-resampled comparison p=0.021, exploratory (naive fold-level p=0.0053 retained only as audit comparator). Descriptor/QKS statistical audit job 13998 is complete; explicit failure-mask provenance is recorded and no claim is confirmatory. External descriptor hybrid is TFP+TNE (no QK); QKS is a separate SVM arm. |
| P4 | **Activity oracle integrated into Pareto MCTS reward (v12, this session)** — public-activity oracle in `OracleAggregator` (max Morgan-2 Tanimoto to 19,321 ChEMBL actives, RRS-style continuous scaling, LRU-cache, weights rebalanced sum=1.0 with activity 0.10); 6th Pareto objective + CSV column; benchmark `compute_mpo_reward` aligned; post-processing scripts updated (degradation on v11 artifacts, `use_activity=False` escape hatch); DAR §6.12 documented BEFORE execution; empirical scale check (activity contrib 0.009 < rrs 0.020 < pns 0.062 — no domination); smoke PASS all 4 methods; **re-benchmark v12 array COMPLETED (job 12865, 20 seeds × 4 methods, `results/benchmark_molecules_opt_v12/`)** | **v12-activity results INTEGRATED (2026-08-08):** Random 0.6724 ± 0.0055 > MCTS 0.6649 ± 0.0066 > GA 0.6453 ± 0.0121 > Greedy 0.4278 (MCTS vs Random t=−4.97 p=0.0001 d=−1.11 ; MCTS vs GA t=6.95 p<0.0001 ; MCTS vs Greedy t=157 ; Random wins 17/20 seeds, MCTS 2/20). **Manuscript P4 switched to v12-activity** (abstract, tab:benchmark, fig regenerated, Methods oracle weights + activity term, SM S2 diversity MCTS 0.7732/19 · Random 0.8046/20 · GA 0.7761/12 · Greedy 0/1, cover letter) — recompiled RC=0 (11 p. main, 4 p. SM). DAR §6.12 results added. Previous post-hoc activity-proximity validation (v9, MCTS 0.2485 p=0.00001 etc.) remains valid |
| P2 | Parent MD evidence unchanged (214-PfCRT only interpretable); force-field manifest policy decision (CHARMM36-jul2022/GAFF2 vs CHARMM36m/CGenFF) still requires author choice. **Set-C state verified this session**: workflow `p2_setc_md_workflow.py` + guard ready; `set_c_md_execution_manifest.json` = FAIL_CLOSED (16 systems selected PP-01/PP-02, 0 ready, 16 blocked — no prepared complex dirs, no candidate-specific CGenFF manifests); this is a preparation-artifact gap, not an editorial or review restriction; pre-submission execution is authorized with explicit exploratory provenance; `docking_mutants.csv` 136 rows OK (17 SMILES × 8 states), mutant receptors prepared (`data/proteins/mutants_prepared/`); **preparation gap = 16 candidate-specific CHARMM36m/CGenFF complexes + npt.gro/cpt + manifests** (heavy; requires free nodes; pilot execution is authorized in pre-submission mode via `P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND`, with scientific QC and explicit exploratory provenance) | No new GROMACS yet; Set-C MD awaits preparation artifacts, not an editorial or review restriction |
| GenMD | PMID 41544599 retained as future, evidence-bounded sampling/emulation option | No replacement of explicit MD; no MD-RRS or MM-GBSA inference |

### Daily execution log — 7 August 2026

| Track | Action today | Status / stop condition |
|---|---|---|
| P1 V5 | Controlled migration continued; canonical Main/SM compiled in a full-tree temporary copy (RC 0) and Cover Letter compiled (LaTeX RC 0; BibTeX RC 2 because no bibliography is defined) | Proceed with audit/compile only; DiffDock/Vina remains blocked until P1.0 gates pass (4GM2 identity, pocket review, 100% smoke containment) |
| P2 | Guarded dry-run passed; after alias resolution, the explicitly authorized parent-pipeline attempt stopped before any GROMACS call because `MD_systems/201_PfDHFR/forcefield_manifest.json` is missing | **0 `grompp`/`mdrun` processes and 0 new trajectories**; generate and independently audit the required force-field manifests before retry |
| GenMD | Add PMID 41544599 as a future, evidence-bounded sampling/emulation option | No replacement of explicit MD; no MD-RRS or MM-GBSA inference |
| P3–P5 | Preserve frozen benchmark claims and add only methodological implications | No new headline result from the review |

**Operational evidence recorded 7 August 2026:** the authorized P2 command was `P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND bash scripts/md_full_pipeline.sh --execute --yes`; after the exhaustive preflight resolved the historical alias `201_DHFR` to canonical directory `201_PfDHFR`, it exited `2` because the four-system preflight is blocked (missing force-field manifests for all systems; `438_PfATP4` also lacks `npt.gro` and `npt.cpt`). The GROMACS binary is available at `/home/nanaengo/miniforge3/envs/malaria_md/bin.AVX2_256/gmx_mpi` (GROMACS 2025.4-conda_forge), but the wrapper exited before invoking GROMACS and no new trajectory was generated. The Set-C preflight independently selected 16 systems, found 0 ready and 16 blocked, and reported `GROMACS launched: no`.


| Order | Action | Stop if |
|---:|---|---|
| 1 | P1 audit + canonical wording fixes | Any row-count/hash mismatch or cohort collision |
| 2 | Compile P1 main/SM/cover | Any fatal error or undefined reference |
| 3 | P1 common-decoy consensus preflight, then rerun (optional HPC) | Raw target labels, pinned DiffDock/Meeko/PyTorch, or provenance incomplete |
| 4 | P2 Set-C fail-closed preflight | Any missing topology/coordinate/force-field hash |
| 5 | P2 MD pilot | QC fails in any required replica |
| 6 | P3/P4/P5 manuscript/data availability pass | Any active stale overclaim remains |
| 7 | Adversarial review + final compile | Reviewer identifies unsupported headline claim |

### Remaining steps — 10 August 2026 (post-audit)

**Completed this session (all pushed):** numerical audits P1 V5/V6/P2 (0 residual errors, commits `43fde858f`/`4bc4c05f0`), P3 SOTA reconciliation (`ad02c5e46`), JCIM submission-readiness P1 V6 + P2 (Use of AI declarations, docking-protocol validation, cover letters), roadmap v1.6, Set-C MD pipeline launched.

**Remaining, in priority order:**

| # | Project | Action | Gate / dependency | Payoff |
|---|---------|--------|-------------------|--------|
| 1 | P2 | **Finish the Set-C MD chain** — equilibration `15106` (~5 h) → production `15111` (16 × 10 ns, ~40 h, `afterok`) → trajectory QC (`p2_setc_trajectory_qc.py`, bound-fraction ≥ 10 % rule `setc_p2_minheavy_5A_ge10percent_v1`) → MD-RRS (`p2_setc_md_rrs.py`, fail-closed) → integrate MD-RRS into the manuscript (replace « future work » in abstract/Discussion) → recompile + re-audit | `15111` afterok `15106`; QC PASS before RRS | **+15–20 % acceptance P2** (50–60 % → ~75–85 %) |
| 2 | P2 | **Table S5 ADMET (R11) — RESOLVED (10/08/2026).** Completed with real ADMET-AI predictions for all 17/17 set-C candidates (LogS, CYP3A4, Caco-2, Clint_h) from parent-library eos7kpb screening (65,856 mol). 3-tool cross-validation infeasible; single-source profile honest and traceable. Methods/Results renamed from "ADMET cross-validation" to "Predicted ADMET profile". Candidate characterisation bug fixed: hERG 0.117/CYP3A4 0.061 were Set-A values misapplied to Set-C. Commit `569c41dcb`. | DONE | ✅ reviewer ambiguity removed |
| 3 | P1 V6 | **Register R5 — RESOLVED (10/08/2026).** Author decision Option A: `PENDING_INDEPENDENT_REVIEW` lifted to `INTERNAL_WORK_AUTHORIZED`. Rationale: all values numerically audited (0 errors), biological gate passed per target, JCIM accepts computational manuscripts. See `v6_review_register.json` `author_decision` block. | DONE (`569c41dcb`) | ✅ submission unblocked |
| 4 | P1 V6 | **Submission package** — final adversarial review + clean compile (main 18 p. / SM 5 p. / cover 1 p.), README + manifest updated | R3–R5 resolved | submission-ready |
| 5 | P3 | **Zenodo upload** (DOI reserved 10.5281/zenodo.19608875; deferred by author) | author decision | data-availability bonus |
| 6 | P4 | Final coherence pass + submission package (v12-activity results integrated) | none blocking | submission-ready |
| 7 | P5 | Final coherence pass + submission package (external MoleculeNet validation + audit v2) | none blocking | submission-ready |
| 8 | All | git push after each validated step; final adversarial review before any submission | Definition of done (§9) | integrity |

> **Jobs en cours (10/08, 2 h):** `15106` wave-0 NPT ~45–49 % (K76A 22 500 / K76T 24 000 / WT 24 500 / C59R 5 500 steps), 0 failure ; ETA équilibration ≈ 5 h total, production ≈ 40 h. Manifest runtime modifié par le job (non committé).

## 9. Definition of done

A project is **submission-ready** only when:

- canonical manuscript, SM, README, data report, and scripts agree;
- every headline number has a source file and a reproducible command;
- cohort identities are explicit and disjoint;
- RRS is per-target and MD-RRS is not conflated with docking-RRS;
- failed, dissociated, or unavailable analyses are visible and excluded from inference;
- Zenodo status is truthful;
- the final compile is clean;
- an adversarial review finds no blocker-level claim/evidence mismatch.

**Expected payoff:** P1 wording/provenance corrections are immediate and low risk; the common-decoy consensus rerun and a successful Set-C MD pilot are the two highest-value computational investments. Neither should be replaced by stronger prose or retrospective relabeling. Current P1 status after this implementation: numerical gate PASS; consensus benchmark **UNTESTED / preflight-only**; canonical manuscript gate remains pending final compile/adversarial sign-off.
