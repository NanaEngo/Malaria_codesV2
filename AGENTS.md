# AGENTS.md — active project instructions

**Updated:** 12 August 2026
**Long-form historical instructions:** `docs/archive/md_full_20260812/AGENTS.md`

## 1. Canonical source map

- **P1–P3 DAR:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
- **P4 DAR:** `P4_DATA_ANALYSIS_REPORT.md`
- **P5 DAR:** `P5_DATA_ANALYSIS_REPORT.md`
- **Master roadmap:** `P1_P5_RRS_POLYPHARMA_ROADMAP.md`
- **Document index:** `docs/MD_DOCUMENT_INDEX.md`
- **P1 V6:** `Project1_Chem_space_antimalarial_V6_CorrectedGrid/`
- **P2:** `Project2_Polypharmacology_MD_ValidationV2607/`
- **P3:** `Project3_Quantum_Inspired_RepresentationsV2607/`
- **P4:** `Project4_Advanced_Monte_CarloV2607/`
- **P5:** `Project5_GNN_Transformer_DrugDiscovery/`

Read the relevant DAR before changing code, parameters, protocols, or manuscript claims.

## 2. Current project status

| Project | Status | Essential result or boundary |
|---|---|---|
| P1 | V6 submission-oriented | V4 2F6I accounting complete; V5 17×4 Vina evidence complete; exploratory outputs remain labelled |
| P2 | Docking-RRS complete; MD-RRS pending | 17 Set-C candidates; A*:6/B:5/C:5/D:1; no Set-C MD-RRS yet |
| P3 | Benchmarks complete | ECFP4 0.9475; hybrid 0.8876; QKS ≈ RBF; no quantum advantage claimed |
| P4 | v12 benchmark complete | Random 0.6724 > MCTS 0.6649; Pareto front is a separate pre-activity artifact |
| P5 | Benchmark complete | ECFP4-RF dominates under scaffold split; topological fusion is modestly complementary |

## 3. Live P2 jobs

The bounded Set-C pilot has 16 prepared systems (PP-01/PP-02 × PfDHFR/PfCRT mutation states) under the PI-approved documented OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P policy deviation.

- **15254:** isolated `PP-01_PfDHFR_WT` equilibration witness complete; hashed `npt.gro`/`npt.cpt`.
- **15259:** isolated witness production running; latest recorded marker step 378000, time 756 ps, target 5,000,000 steps/10 ns. Log: `Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_publication_witness_v8_20260811/PP-01_PfDHFR_WT/runs/publication_witness_20260811/replicate_1/production.log`.
- **15260:** witness QC pending with `afterok:15259`.
- **Full Set-C MD-RRS:** `NOT_COMPUTED`; no witness-only result may be promoted.
- Historical 15106/15111/15117 identifiers are superseded.

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

- P1 V6 is the designated submission workspace; V4/V5 evidence is not silently merged into V6.
- P3 canonical sources are `Paper3_Quantum_InspiredV2608.tex` and `Paper3_Quantum_Inspired_SM_V2608.tex`; older versions are archived inside the P3 manuscript directory.
- P4 manuscript prose must distinguish v12 scalar benchmark from the historical pre-activity Pareto front and must not present Tier 2 QMC diagnostics as validated energies.
- P5 manuscript prose must retain the honest-negative scaffold result and must not claim universal GNN/Transformer inferiority.
- Zenodo remains `reserved / upload pending` until the upload and DOI are verified.

## 6. Pre-submission development policy

P1–P5 remain in author-controlled pre-submission development. No administrative or independent-review status blocks scientific work before submission. Provenance, identity, numerical, geometry, runtime, and QC safeguards remain mandatory. Submission does not automatically change this policy; only explicit author instruction may activate submission-facing review gates.

## 7. Maintenance rule

Keep this file operational and short. Put historical job narratives, superseded plans, long audit prose, and version histories in `docs/archive/` or the relevant project archive. Add a dated checkpoint to the relevant DAR when a validated result changes the scientific status.
