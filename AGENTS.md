# AGENTS.md — active project instructions

**Updated:** 13 August 2026
**Long-form historical instructions:** `docs/archive/md_full_20260812/AGENTS.md`

**P1 SOUMISSION JCIM = V7 (canonical):** `Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex` (main 25 p.) + `_SM.tex` (17 p.) + cover letter; **package ACS auto-contenu `submission_ACS_P1V7/`** (PDF + .bbl/.aux pour xr + .bib). **V7 supersedes V6 (10/08/2026)** with comprehensive validation (DEKOIS 2.0 external benchmark, MMV enrichment, redocking RMSD — 3 tables + SM S11), physicochemical characterization (3 tables), enhanced narrative (Discussion +125%), methodological rigor (grid box specs, 99.3% cost reduction). **V4/V5/V6 = archives pré-soumission** (V4 : espace chimique + remédiation 2F6I 484 ; V5 : docking ciblé ; V6 : version 10/08/2026). Compilation V7 : main 25 p., SM 17 p., cover 1 p., 0 erreur / 0 réf. indéfinie ✅ — package techniquement prêt; restent la vérification des métadonnées en ligne, la lecture auteur finale et la revue structurale indépendante avant toute promotion soumission.

## 1. Canonical source map

- **P1–P3 DAR:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
- **P4 DAR:** `P4_DATA_ANALYSIS_REPORT.md`
- **P5 DAR:** `P5_DATA_ANALYSIS_REPORT.md`
- **Master roadmap:** `P1_P5_RRS_POLYPHARMA_ROADMAP.md`
- **Document index:** `docs/MD_DOCUMENT_INDEX.md`
- **P1 V7 (JCIM submission):** `Project1_Chem_space_antimalarial_V7_CorrectedGrid/`
- **P1 V6 (archive):** `Project1_Chem_space_antimalarial_V6_CorrectedGrid/`
- **P2:** `Project2_Polypharmacology_MD_ValidationV2607/`
- **P3:** `Project3_Quantum_Inspired_RepresentationsV2607/`
- **P4:** `Project4_Advanced_Monte_CarloV2607/`
- **P5:** `Project5_GNN_Transformer_DrugDiscovery/`\n- **P6:** `Project6_LISH_MoA_Structure_Phenotype/` (follow-up LISH-MoA; structure arm blocked pending mapping)

Read the relevant DAR before changing code, parameters, protocols, or manuscript claims.

## 2. Current project status

| Project | Status | Essential result or boundary |
|---|---|---|
| P1 | **V7 technically submission-ready (JCIM)** | V7 enhanced + validated (DEKOIS/MMV/redocking), 25 p. main / 17 p. SM / 1 p. cover, package refreshed; final author/metadata review and independent structural review remain |
| P2 | Docking-RRS complete; Set-C MD pilot in production | 17 Set-C candidates; A*:6/B:5/C:5/D:1; 16-system equilibration PASS; gate 15319 PASS; production 15320 task 0 RUNNING with exact 10-ns MDP; no Set-C MD-RRS yet |
| P3 | Benchmarks complete | ECFP4 0.9475; hybrid 0.8876; QKS ≈ RBF; no quantum advantage claimed |
| P4 | v12 benchmark complete | Random 0.6724 > MCTS 0.6649; Pareto front is a separate pre-activity artifact |
| P5 | Benchmark complete | ECFP4-RF dominates under scaffold split; topological fusion is modestly complementary; phenotype-only LISH-MoA baseline is complete and separate |
| P6 | Planned follow-up | LISH-MoA structure–phenotype study; no molecular arm until a versioned drug_id→SMILES mapping passes audit |

## 3. Live P2 jobs

The bounded Set-C pilot has 16 prepared and equilibrated systems (PP-01/PP-02 × PfDHFR/PfCRT mutation states) under the PI-approved documented OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P policy deviation. Production is active under the final corrected launcher; MD-RRS remains blocked until all 16 trajectories pass QC.

- **15270:** `p2_setc_gpu_witness` COMPLETED — isolated `PP-01_PfDHFR_WT` 10-ns witness at 28.169 ns/day; stability evidence only.
- **15282/15287:** previous corrected equilibration/gate pair canceled after the author-requested restart; retained as scheduler provenance only.
- **15288:** completed corrected 16-system CPU equilibration array; all 16 systems finalized with `rc=0` and non-empty `npt.gro`/`npt.cpt`.
- **15293:** historical gate failed before preflight because `set -u` exposed non-nounset-safe GMXRC variables; no production was promoted.
- **15307:** gate passed `16/16` and submitted production `15308`; `15308` was stopped after detecting missing staged topology dependencies and an incompatible `gen-vel` setting.
- **15312:** corrected gate passed `16/16` after the dependency-staging and continuation fixes, submitting production `15313`.
- **15313:** stopped fail-closed after GROMACS 2025.4 rejected the unsupported `mdrun -seed` option; no trajectory is reportable.
- **15317:** stopped fail-closed after detecting an ns-to-step conversion error (`5,000,000,000` instead of `5,000,000` for 10 ns); no trajectory is reportable. The corrected MDP passed exact-step and 10-step GPU smoke tests.
- **15319/15320:** final gate passed `16/16`; production array `15320` is active with `%1`, task 0 confirms `5,000,000` steps / `10,000 ps` and GPU PP/PME offload. No MD-RRS result exists yet.
- Historical 15106/15111/15117/15254/15259/15260 identifiers are superseded by the GPU witness chain.
- Post-QC chain (`set_c_trajectory_qc.py`, `p2_setc_md_rrs.py`) remains blocked for aggregate MD-RRS until all 16 production trajectories finish and pass QC.
- **Cleanup audit (13 Aug):** six failed production run directories and 1,087 autosave/backup files (~13.7 GB), plus ten untracked Antechamber/SQM/energy temporary files, were removed after reference-safety checks. The 428 exact diagnostic duplicates (~3.93 GB) and legacy `results/md_systems/set_c` root (~16 GB) were retained because historical scripts still reference them. The active `15320` run, logs, manifests, DARs, and unique historical evidence are protected. Twelve empty orphan directories outside the active preparation root were removed; active `runs/` placeholders were preserved.
- **Full Set-C MD-RRS:** `NOT_COMPUTED`; no witness-only result may be promoted.

## 4. Provenance rules

1. Freeze inputs, scripts, parameters, environment, and hashes before execution.
2. Never invent or silently repair values; record `FAILED`, `PENDING`, `EXPLORATORY`, and `NOT_COMPUTED` explicitly.
3. Never overwrite canonical results; use versioned output directories.
4. Keep P1 Set A, P2 MD Set B, and P2 Set-C disjoint.
5. RRS is per target: `|ΔG_mut,t| / |ΔG_WT,t| × 100`; exclude WT non-binders with `|ΔG_WT,t| < 5.0 kcal mol⁻¹`.
6. Docking-RRS and MD-RRS are different estimands. MD-RRS requires complete trajectories, trajectory hashes, PASS QC, and the predeclared analysis rule.
7. The OpenFF substitution for CGenFF must retain `policy_deviation.declared=true` and `policy_deviation.approved=true` in manifests.
8. Do not update manuscript claims from an incomplete or failed job.
9. Use `git diff --check` and a targeted validation command after documentation/code changes.
10. Git push is performed only after a validated milestone and explicit author instruction.

## 5. Manuscript and submission boundaries

- **P1 V7 is the designated JCIM submission workspace**; V4/V5/V6 evidence feeds V7 only through the documented integration (validation tables, physicochemical characterization); no silent merging of unlabelled exploratory outputs.
- **P1 V4 — Remédiation 2F6I/PfClpP TERMINÉE (09-10/08):** 484 = 458 PASS + 1 PENDING (171) + 15 exclusions boron (AD4) + 5 DOCKED_GATE_FAILED + 5 EMBED_FAILURE; artefact `results/pfclpp_2f6i_484_final_accounting.{csv,json}` + dossier prêt-à-signer `PFCLPP_2F6I_484_INDEPENDENT_REVIEW_DOSSIER.md`; registre `PENDING_INDEPENDENT_REVIEW` (réactivation à la demande de l'auteur).
- P3 canonical sources are `Paper3_Quantum_InspiredV2608.tex` and `Paper3_Quantum_Inspired_SM_V2608.tex`; older versions are archived inside the P3 manuscript directory.
- P4 manuscript prose must distinguish v12 scalar benchmark from the historical pre-activity Pareto front and must not present Tier 2 QMC diagnostics as validated energies.
- P5 manuscript prose must retain the honest-negative scaffold result and must not claim universal GNN/Transformer inferiority.
- Zenodo remains `reserved / upload pending` until the upload and DOI are verified.

## 6. Pre-submission development policy

P1–P5 remain in author-controlled pre-submission development. No administrative or independent-review status blocks scientific work before submission. Provenance, identity, numerical, geometry, runtime, and QC safeguards remain mandatory. Submission does not automatically change this policy; only explicit author instruction may activate submission-facing review gates.

### P1 component status (V7-era snapshot)

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| Librairie hybride (65,856 molécules) | ✅ Complété | 92.6% ECFP4-unreachable, 69.3% scaffold recovery |
| Top-20 candidats (Set A, MPO) | ✅ Complété | MPO 0.515–0.550, tous sélectifs (SI > 10) — disjoint des ensembles B/C P2 |
| Grilles V2 (4 cibles) | ✅ Déployé | pfDHFR, pfCRT, pfATP4, pfClpP |
| DEKOIS V2 (pfDHFR) | ✅ Terminé | AUC = 0.45 [0.37, 0.53] — Meeko uniforme |
| Redocking | ✅ Validé | RMSD < 2.0 Å toutes cibles |
| Validation Tartarus | ✅ Complété | ρ = 0.013 (p = 0.091), MPO orthogonal au docking |
| **Manuscrit V7 (JCIM, canonical)** | ✅ **Enhanced & technically ready** | Main 25 p., SM 17 p., cover 1 p., 0 erreur; DEKOIS/MMV/redocking + physicochemical tables; package `submission_ACS_P1V7/`; restent : métadonnées, lecture auteur, revue structurale indépendante |
| **Manuscrit V6 (archive)** | ✅ **Archive** | Étude intégrée RRS + polypharmacologie (Set C 17, classes A*:6/B:5/C:5/D:1) |
| **Manuscrit V4 (archive pré-soumission)** | ✅ **Remédiation 2F6I COMPLÈTE** | 484 = 458 PASS + 1 PENDING + 25 non-PASS; dossier prêt-à-signer; registre PENDING |
| **Cover Letter** | ✅ **Conforme** | 1 page, sans référence aux manuscrits compagnons |

## 7. Maintenance rule

Keep this file operational and short. Put historical job narratives, superseded plans, long audit prose, and version histories in `docs/archive/` or the relevant project archive. Add a dated checkpoint to the relevant DAR when a validated result changes the scientific status.
