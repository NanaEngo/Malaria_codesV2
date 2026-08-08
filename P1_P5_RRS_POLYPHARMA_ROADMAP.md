# Master Roadmap P1–P5 — Resistance/RRS + Polypharmacology

**Version:** 1.2 — 8 August 2026 (daily update)  
**Purpose:** submission-oriented roadmap for the canonical versions of Projects 1–5.  
**Update basis:** current repository state plus Olsson, *Generative molecular dynamics*, *Current Opinion in Structural Biology* 96 (2026) 103213, DOI `10.1016/j.sbi.2025.103213`, PMID `41544599`; P5 benchmark completed in full on 8 August 2026 (jobs 12841/12842).  
**Operating rule:** no result is promoted to a manuscript claim unless it is traceable to a frozen input, an executable script, a recorded parameter set, and a completed QC gate.

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
| P1 V4 baseline / V5 in progress | Strong computational chemical-space study; V4 wording is locally refinable while V5 adds an evidence-bounded reconstruction path | circular/retrodictive validation overinterpretation; centroid-to-member transfer; provenance wording; V5 independent-review signature (single remaining gate); resistance bridge | **80–85%** for V4 at a well-matched computational-cheminformatics venue after clean recompile + audit; V5 gains a provisional estimate (**75–80%**) once the independent review signs the three anchors (PfDHFR MTX A702, PfCRT Y01, PfClpP 2F6I triad); PfATP4 excluded |
| P2 | Honest but partly validated MD/RRS/polypharm program; only 214-PfCRT MM-GBSA is interpretable | force-field mismatch, dissociation, limited replicates, docking-vs-MD cohort confusion | **70–80%** after candidate-specific Set-C MD or a deliberately narrowed methods paper; do not claim >85% without new MD/biochemical evidence |
| P3 | Canonical benchmarks complete, negative/null quantum result is clean | novelty and biological relevance of H1–RRS bridge; no experimental activity validation; Zenodo pending | **80–85%** after provenance/deposit completion and cautious RRS narrative; ≥85% requires deposit + independent validation |
| P4 | Reproducible v12 benchmark with Pareto-front value; QMC Tier 2 correctly non-publication-grade | scalar reward does not beat Random; QMC overinterpretation; deposit pending | **75–82%** after keeping QMC diagnostic-only and strengthening diversity/provenance; higher only with independent benchmark replication |
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

**Daily status (7 August 2026):** V4 remains the frozen evidence baseline and V5 is the canonical successor under controlled migration. V5 is not submission-ready: the inherited 4GM2/PfClpP identity is invalid (4GM2 is PfClpR), fixed-center DiffDock containment is 79.17%, and the independent structural-review register remains pending. No Vina, consensus, RRS, or PNS result is accepted from the inherited raw DiffDock artifacts.

### P1.0 V5 gates before any new heavy run

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

**Gate P1-R1 — data integrity:** all source hashes and row counts pass; no unresolved cohort collision.  
**Gate P1-R2 — docking robustness:** rerun only if the audit finds missing/invalid records that affect named leads or target-level conclusions. At minimum, record per-target denominators and failure reasons.  
**Gate P1-R3 — pH sensitivity:** for PfCRT, retain the existing pH 5.2 reranking result; rerun top candidates only if a new target panel or protonation protocol is introduced.  
**Gate P1-R4 — consensus decoy benchmark:** highest-value new calculation. The read-only preflight is implemented at `Project1_Chem_space_antimalarial_V4_CorrectedGrid/scripts/p1_consensus_preflight.py`; it writes `results/p1_consensus_preflight.json`, checks raw-panel/receptor/tool/provenance gates, requires a machine-readable P1 Set-A top-20 manifest, and launches zero docking jobs. The benchmark remains **UNTESTED / FAIL-CLOSED** until the exact Vina+DiffDock consensus is applied to a common, independently labeled panel for all four targets (DEKOIS/ChEMBL where raw labels are available), with target-stratified ROC-AUC, EF1/5/10, BEDROC, PR-AUC, bootstrap CIs, and fixed seeds. The existing DEKOIS AUC 0.450 is the historical Vina-only PfDHFR baseline; existing DiffDock summary CSVs are not accepted as benchmark output without input/model hashes and an execution manifest. The broad 19,913-row P1 predicted-SYBA library is provenance context, not the P1 Set-A top-20 cohort.

### P1.3 Resistance/RRS extension

- Define a **P1 named-lead resistance panel** using PfDHFR N51I/C59R/S108N/I164L and PfCRT K76T/K76A, with target-specific WT baselines.
- If only docking is available, report “docking-RRS pilot,” not MD-RRS.
- For MD, use candidate-specific CHARMM36m+CGenFF or a fully documented alternative consistently across protein and ligand; at least 3 independent replicas per candidate/target pair, 50–100 ns production per replica, bound-fraction/contact/H-bond QC, and blind analysis rules.
- Do not pool the four named parent leads with the 17 Set-C polypharm cohort. A P1 resistance extension may use 201/438/164/214 as a named-lead panel, but it must be reported as such; `164–PfClpP` is a historical cohort label and PDB 4GM2 is PfClpR, not structural PfClpP validation.
- Primary endpoint: target-specific retention and bound fraction; secondary endpoints: contact persistence, mutation-specific ΔΔG proxy, and scaffold/TDA association adjusted for MW.

### P1.4 P1 manuscript acceptance package

- Main + SM + cover letter use identical cohort and availability language.
- Add a concise “What is and is not validated” box or paragraph.
- Replace claims of generalizability with a prospective-test plan.
- Make the 64D choice “selected” if the underlying numeric metrics remain unavailable; never present N/A as evidence of superiority.
- Retain the honest negative DEKOIS result prominently; it improves credibility.
- Add a reproducibility table: input file, rows, script, seed, output hash, status.

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
| P1 V5 | **THREE-TARGET VINA EVIDENCE COMPLETE** — PfClpP/2F6I (job 12854, chain-A triad Ser252/His223/Asp219, aff −5.05…−7.03, triad contact 3.3–8.9 Å), PfCRT/6UKJ (job 12855, Y01 cavity, aff −5.12…−7.91, anchor 3.0–4.1 Å, proxy caveat), PfDHFR/7F3Y (job 12859, MTX A702 catalytic-site copy, aff −4.86…−6.35, anchor 3.0–3.5 Å) — **17/17 pairs pass the composite biological gate per target**; PfATP4/9N10 excluded (no co-crystallized anchor). Two scientific corrections: 4GM2→2F6I (PfClpR≠PfClpP) and MTX A702 (catalytic copy) vs the old receptor-centroid centers. Independent-review register v2 (`structural_pocket_independent_review.json`) marks the 3 anchors `EVIDENCE_COMPLETE_AWAITING_REVIEW`, signature `PENDING`; **fail-closed gate script `p1_v5_consensus_rrs_gate.py` refuses consensus/RRS/PNS until signed**. Raw 17×3 affinity table committed. Manuscript V5 migration-status notes updated; **compiles clean (RC=0)**. Pushed `8e8cc0ac4`→`3be618394`→`bf18bae58` | **Consensus/RRS/PNS/manuscript claims BLOCKED until an independent reviewer signs the register** — this is now the single P1 V5 gate |
| P5 | Benchmark completed in full (morning session): GIN–TFP random `0.9084 ± 0.0060`, GIN–TNE random `0.8918 ± 0.0060` (jobs 12841/12842). Paired-t (df=4) + BH-FDR verified on both splits; every arm significantly below ECFP4. Coherence re-verified this session: manuscript L146 public-validation numbers match `p5_public_malaria_report.json` exactly | **P5 submission package ready pending JoC final checks + Zenodo upload** |
| P3 | **External validation on the public ChEMBL malaria IC50/EC50 dataset (22,447 mol) in flight** — script `p3_external_validation.py` benchmarks ECFP4/TFP/TNE/Hybrid with the canonical 5-fold CV RF protocol + paired-t + BH-FDR; documented in BMAD before completion (workflow rule). Job 12860 (after killing 12858: ripser/BLAS thread thrashing fixed with OMP/MKL/OPENBLAS=1 exports, ~2× throughput). Pennylane/jax–numpy mismatch (jax 0.10.2 requires numpy≥2.0, env has 1.26.4) is local-only; the script copies canonical helpers without pennylane (no QK code executed) | **Job 12860 running (budget 8 h)**; integrate results into DAR/manuscript on completion |
| P4 | **Activity-proximity validation of generated molecules (post-hoc, reward unchanged)** — all 59 v9 generated molecules vs the 19,321 public actives: MCTS mean max-Tanimoto 0.2485 (p=0.00001), GA 0.2571 (p<0.00001), Random 0.2436 (p=0.0008), Greedy 0.3284 (n=1), baseline fragments 0.2150 → all methods significantly closer to known actives than chance. DAR P4 entry added; manuscript implication: 2–3 sentence Results paragraph + optional SM table | **Done; pending manuscript insertion** |
| P2 | Parent MD evidence unchanged (214-PfCRT only interpretable); force-field manifest policy decision (CHARMM36-jul2022/GAFF2 vs CHARMM36m/CGenFF) still requires author choice | No new GROMACS; Set-C MD blocked by policy + review gates |
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
