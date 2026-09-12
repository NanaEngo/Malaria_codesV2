# AGENTS.md — active project instructions

**Updated:** 12 September 2026
**Long-form historical instructions:** `docs/archive/md_full_20260812/AGENTS.md`

**P1 SOUMISSION JCIM = V8 (canonical):** `Project1_Chem_space_antimalarial_V7_CorrectedGrid/submission_ACS_P1V8/P1_Integrated_Polypharmacology_RRS_Main_V8.tex` (main 25 p.) + `_SM_V8.tex` (17 p.) + cover letter + Response to Reviewers; **package ACS auto-contenu `submission_ACS_P1V8/`**. **V8 supersedes V7** with complete revision updates, response-to-reviewers dossier, comprehensive validation (DEKOIS 2.0 external benchmark, MMV enrichment, redocking RMSD), physicochemical characterization, and enhanced narrative. Compilation V8 : main 25 p., SM 17 p., cover 1 p., response 5 p., 0 erreur / 0 réf. indéfinie ✅ — package révisé et ressoumis sur HPC.

**P2 SOUMISSION JCIM = V2609C (canonical):** `Project2_Polypharmacology_MD_ValidationV2607/manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex` (main 26 p.) + `_SM.tex` (19 p.) + cover letter (1 p.); **package ACS auto-contenu `submission_ACS_P2V2609C/`** (PDF + .bbl/.aux + .bib + figures vectorielles). **V2609C supersedes V2609B (12/09/2026)** with *Estimand Divergence* framing (87.5% static vs MD mismatch as a positive triage filter), denominator-unbiased RRS, 39-ligand GNINA CNN validation (100% Class-A agreement), African Natural Product chemical space profiling ($Fsp^3=0.22$, $QED=0.70$, $MPO=0.728$), ethnobotanical mapping, and WHO 2025/2026 regional resistance isolate contextualization. Compilation V2609C : main 26 p., SM 19 p., cover 1 p., 0 erreur / 0 réf. indéfinie ✅ — package techniquement prêt et synchronisé sur HPC (`/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/manuscript/V2609C/`).

## 1. Canonical source map

- **P1–P3 DAR:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
- **P4 DAR:** `P4_DATA_ANALYSIS_REPORT.md`
- **P5 DAR:** `P5_DATA_ANALYSIS_REPORT.md`
- **Master roadmap:** `P1_P5_RRS_POLYPHARMA_ROADMAP.md`
- **Document index:** `docs/MD_DOCUMENT_INDEX.md`
- **P1 V7 (JCIM submission):** `Project1_Chem_space_antimalarial_V7_CorrectedGrid/`
- **P2 V2609C (JCIM submission):** `Project2_Polypharmacology_MD_ValidationV2607/manuscript/V2609C/`
- **P3:** `Project3_Quantum_Inspired_RepresentationsV2607_V4/`
- **P4:** `Project4_Advanced_Monte_CarloV2607_V2/`
- **P5:** `Project5_GNN_Transformer_DrugDiscovery_V2609/`
- **P6:** `Project6_LISH_MoA_Structure_Phenotype/` (follow-up LISH-MoA; structure arm blocked pending mapping)

Read the relevant DAR before changing code, parameters, protocols, or manuscript claims.

## 2. Current project status

| Project | Status | Essential result or boundary |
|---|---|---|
| P1 | **V8 canonical (JCIM resubmitted)** | V8 enhanced + validated (DEKOIS/MMV/redocking + Response to Reviewers), 25 p. main / 17 p. SM / 1 p. cover / 5 p. response, package `submission_ACS_P1V8/` |
| P2 | **V2609C technically submission-ready (JCIM)** | V2609C enhanced + validated (*Estimand Divergence*, 39-ligand GNINA CNN, African NP chemical space profiling, ethnobotanical mapping), 26 p. main / 19 p. SM / 1 p. cover, package refreshed (`submission_ACS_P2V2609C/`); live HPC triplicate/pH 5.2 daemon active |
| P3 | Benchmarks complete | ECFP4 0.9475; hybrid 0.8876; QKS ≈ RBF; no quantum advantage claimed; JCAMD manuscript ready |
| P4 | v12 benchmark complete | Random 0.6724 > MCTS 0.6649; Pareto front is a separate pre-activity artifact; JCAMD manuscript ready |
| P5 | Benchmark complete | ECFP4-RF dominates under scaffold split; topological fusion is modestly complementary; phenotype-only LISH-MoA baseline complete; JCAMD manuscript ready |
| P6 | Planned follow-up | LISH-MoA structure–phenotype study; no molecular arm until a versioned drug_id→SMILES mapping passes audit |

## 3. Live P2 jobs

The Set-C pilot has 16 prepared and equilibrated systems (PP-01/PP-02 × PfDHFR/PfCRT mutation states) under OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P explicit-solvent protocol. Production array `15320` completed all 16/16 trajectories. On 12 September 2026, an automated background daemon (`/home/nanaengo/hpc_md_execution.log`) was initialized on `penavoraserver` (`100.73.21.40`, environment `malaria_md` with RDKit 2025.03.6 and GROMACS `/usr/bin/gmx`):

- **15320:** completed canonical 16-system production array; all 16 trajectories passed QC (`setc_p2_minheavy_5A_ge10percent_v1`).
- **HPC Triplicate & pH 5.2 Daemon (12 Sept 2026):** Active on `penavoraserver` (`/home/nanaengo/hpc_md_execution.log`) for:
  1. Triplicate MD ($3 \times 10\text{ ns}$) verification on Class-A* lead `PP-01` (`PP-01_PfCRT_WT`, `PP-01_PfCRT_K76T`, `PP-01_PfDHFR_WT`) fulfilling Soares et al. (2023) JCIM 3-replicate guidelines.
  2. Vacuolar pH 5.2 PfCRT protonation audit (protonated His97/His53 and ligand basic sites under acidic digestive vacuole environment).
- Post-QC chain (`set_c_trajectory_qc.py`, `p2_setc_md_rrs.py`, `gmx_MMPBSA`) complete for canonical pilot; secondary triplicate trajectories remain auxiliary reviewer-response evidence and do not block V2609C submission.

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
