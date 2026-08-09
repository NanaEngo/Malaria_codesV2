# Master Roadmap P1–P5 — Resistance/RRS + Polypharmacology

**Version:** 1.5 — 9 August 2026 (V6 integrated evidence audit and manuscript completion)
**Purpose:** submission-oriented roadmap for the canonical versions of Projects 1–5.  
**Update basis:** current repository state plus Olsson, *Generative molecular dynamics*, *Current Opinion in Structural Biology* 96 (2026) 103213, DOI `10.1016/j.sbi.2025.103213`, PMID `41544599`; P5 benchmark completed in full on 8 August 2026 (jobs 12841/12842) with independent validation 100% complete (stats re-derivation, ECFP4-RF + GIN replication, public ChEMBL benchmark); **P1 V5 PfATP4 COMPLETE (job 12864)** — 17/17 pairs pass the composite gate, 17×4 affinity table COMPLETE, manuscript V5 updated to the 4-target gate; **P1 V4 PfClpP replacement run LAUNCHED (fresh job 14483_[0-483])** — first submission 13999 failed closed on pre-existing output directories; fresh 484-centroid raw revalidation now runs on genuine 2F6I in an isolated directory, with no promotion before fail-closed aggregation; **P4 v12-activity benchmark COMPLETE (job 12865)** — Random 0.6724 > MCTS 0.6649 > GA 0.6453 > Greedy 0.4278, manuscript P4 switched to v12-activity (abstract/table/figure/SM/cover letter, recompiled RC=0); **P3 external validation COMPLETE** — descriptor ITT and complete-case sensitivity are finalized (jobs 12858→12860→12891→13997), QKS external validation is complete (12863), and corrected-resampled statistical audit is complete (13998).
**Operating rule:** every result must remain traceable to frozen inputs, an executable script, recorded parameters, and QC evidence. **Author-controlled pre-submission decision (09/08/2026):** no editorial, submission, independent-review, or signature restriction blocks scientific work while P1–P5 are under development. Exploratory calculations, RRS/PNS/ACSI analyses, figures, reruns, and manuscript refinement may proceed with truthful provenance labels. Scientific identity, hash, geometry, numerical, and runtime QC remain active. Submission does not switch the workflow automatically; only the author's explicit confirmation of submission plus explicit request to reactivate restrictions activates the signed-review policy. See `P1_INTERNAL_DEVELOPMENT_POLICY.md` and `P1_PRE_SUBMISSION_WORKFLOW_NOTICE.md`.

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

**Current status (9 August 2026):** V6 is the integrated P1 manuscript workspace and has passed the machine-readable evidence audit and clean rebuild. V4 remains the frozen chemical-space baseline; V5 remains the source of target-wise raw docking evidence; P2 remains the canonical source of the corrected RRS table. **The isolated V5-protocol RRS reproduction COMPLETED (jobs 15013/15014/15015):** 136/136 Vina rows (85 PfDHFR + 51 PfCRT), 34 RRS rows (17 per target), 0 `failure.json`, status `VINA_GRID_DOCK_MUTANT_PANEL_RANK1_VERIFIED`; class distribution **A*:12 / A:5 per target — identical to the archived pilot**, confirming internal V5-protocol reproducibility. It is not a common-protocol replication of canonical P2, and its outputs remain exploratory and isolated. **The V4 484-centroid 2F6I remediation COMPLETED (array 15016 + aggregate 15044):** 35/35 records — **10 `PASS_RAW_VINA`** (cid 237 multi-fragment, 43/195/228/340 embedding, 339 zero-charge, 136/170 re-docked, rescue 125/258 confirmed), **15 `UNSUPPORTED_ELEMENT_FOR_AD4`** (boron, explicit protocol exclusion), **5 `DOCKED_GATE_FAILED`** (affinities −2.4…−6.1), **5 `EMBED_FAILURE_ALL_STRATEGIES`**; net +7 PASS vs historical 449/484; provenance under `results/pfclpp_2f6i_484_remediation_20260809/`. **P2 Set-C MD remains fail-closed at 0/16 ready systems**; the dependency audit shows the blocker is the **missing licensed CGenFF tool (`cgenff`)** required by the fail-closed `CHARMM36m + CGenFF + TIP3P` policy (OpenFF 2.2 / ACPYPE-GAFF2 are present but rejected as non-conforming provenance).

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

**Daily execution status (7 August 2026):** GROMACS is installed and the guarded launch path is available, but the four-system input/provenance preflight `scripts/p2_parent_md_preflight.py` reports **0/4 READY and 4/4 BLOCKED**. Missing prerequisites are: force-field manifests for all four canonical systems; `npt.gro` and `npt.cpt` additionally for `438_PfATP4`. The canonical pipeline and each canonical direct execution wrapper now run this four-system input-read-only/report-writing gate before any GROMACS stage; it validates required inputs and declared hashes, not completed trajectory quality. Historical preparation utilities are catalogued in `results/metrics/p2_gromacs_entrypoint_audit.json` and are not publication-grade execution paths. A guarded dry-run is safe; an authorized `--execute` attempt stops before GROMACS and must not be interpreted as a trajectory result. Set-C production remains prohibited by `set_c_execution_allowed=false`.

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
