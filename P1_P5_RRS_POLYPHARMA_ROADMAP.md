# Master Roadmap P1–P6 — active plan

**Version:** 1.13 — 13 August 2026
**Purpose:** current decisions and next actions only.
**Detailed history:** `docs/archive/md_full_20260812/P1_P5_RRS_POLYPHARMA_ROADMAP.md`

## 1. Source-of-truth map

| Project | Active DAR | Manuscript/workspace | Current state |
|---|---|---|---|
| P1 | `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | `Project1_Chem_space_antimalarial_V7_CorrectedGrid/` | V7 submission-ready (JCIM); funding + final author read-through remain |
| P2 | `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | `Project2_Polypharmacology_MD_ValidationV2607/` | Docking-RRS complete; production 15320 active; Set-C MD-RRS pending |
| P3 | `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | `Project3_Quantum_Inspired_RepresentationsV2607/` | Canonical benchmarks and external validation complete |
| P4 | `P4_DATA_ANALYSIS_REPORT.md` | `Project4_Advanced_Monte_CarloV2607/` | v12 scalar benchmark and Pareto analysis complete |
| P5 | `P5_DATA_ANALYSIS_REPORT.md` | `Project5_GNN_Transformer_DrugDiscovery/` | Benchmark and external validation complete |\n| P6 | `Project6_LISH_MoA_Structure_Phenotype/P6_DATA_ANALYSIS_REPORT.md` | `Project6_LISH_MoA_Structure_Phenotype/` | Planned; structure mapping required; no molecular arm run |

## 2. Project priorities

### P1 — V7 submission package

- Keep V7 as the submission-oriented workspace (supersedes V6 on 11/08/2026: validation tables DEKOIS/MMV/redocking, physicochemical characterization, ORCID ×5); V6/V4/V5 remain evidence/remediation layers.
- Package `submission_ACS_P1V7/` verified auto-contained (12/08/2026): main 25 p. / SM 17 p. / cover 1 p., 0 undefined refs, xr aux included, `git diff --check` PASS.
- Preserve the corrected 2F6I accounting and the 17×4 target-wise Vina table.
- Finish ORCID/funding metadata and final author read-through before deposit.
- Do not promote exploratory V5 consensus/RRS as independent biological validation.

### P2 — RRS/polypharmacology plus MD

- Canonical cohort: 17 Set-C candidates, per-target docking-RRS classes A*:6/B:5/C:5/D:1.
- The bounded pilot contains 16 prepared systems (PP-01/PP-02 × PfDHFR/PfCRT mutation states) using the explicitly documented OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P deviation.
- CPU witness `15259` and dependent QC `15260` were stopped after a partial 858-ps trajectory; that output is non-canonical.
- GPU benchmark `15262` passed at 19.816 ns/day using mixed offload (`-nb gpu -pme gpu -bonded cpu -update cpu`).
- **Witness completed:** `15270` completed one `PP-01_PfDHFR_WT` 10-ns GPU trajectory at 28.169 ns/day without fatal/LINCS/NaN indicators; it is stability evidence only.
- The corrected versioned 16-system equilibration completed `15288` with 16/16 terminal outputs. Gate `15312` passed the exact 16/16 preflight. Production `15313` was stopped fail-closed after a GROMACS 2025.4 CLI audit found unsupported `mdrun -seed`; `15317` was then stopped after detecting an ns-to-step conversion error in the generated MDP. No trajectory is reportable. The corrected MDP passes exact-step and GPU smoke tests. Final gate `15319` passed 16/16 and production `15320` is active under `%1`; task 0 confirms 5,000,000 steps / 10,000 ps with GPU offload. No MD-RRS result is available yet.
- The previous wrong-root equilibration 15275 was cancelled; its 69-file hash snapshot is retained as non-canonical. `md_rrs_status=NOT_COMPUTED` until complete trajectories pass QC.
- Historical 15106/15111/15117 records are superseded; historical four-parent MD remains separate from Set-C.

### P3 — quantum-inspired representations

- Canonical headline: ECFP4 0.9475 ± 0.0045; hybrid RF 0.8876 ± 0.0065; QKS ≈ RBF.
- Keep the 351 TNE failures and complete-case/ITT distinction visible.
- Finalise deposit and author review; do not add new claims without a source-bound analysis.

### P4 — Pareto MCTS

- Canonical scalar benchmark: Random 0.6724 > MCTS 0.6649 > GA 0.6453 > Greedy 0.4278.
- Keep the four-point pre-activity Pareto front (HV 1.2366) separate from v12 scalar results.
- QMC Tier 2 remains diagnostic, not publication-grade.

### P5 — GNN/Transformer benchmark

- ECFP4-RF remains strongest under scaffold split (0.8300); GIN-TFP adds modest complementary signal (0.8138 vs GIN 0.8047).
- Preserve the honest-negative narrative and external replication.
- Finish deposit and final author review.

### P6 — LISH-MoA structure–phenotype follow-up

- Project 6 is an independent follow-up study, not a P5 revision.
- The locked phenotype-only reference is log loss 0.02378, macro-AUROC 0.6435, and macro-AUPRC 0.1428 on 3,289 drugs and 206 labels.
- Molecular arms (ECFP4, GNN, ChemBERTa, TFP/TNE, QKS) are **not run** because no versioned `drug_id → SMILES` mapping is available.
- Reopen only after mapping provenance, collision handling, drug-grouped/scaffold splits, ECFP4 baseline, and paired statistics pass the P6 gates.

## 3. Non-negotiable evidence rules

1. Every result must map to a frozen input, script, parameters, and QC/provenance record.
2. Keep P1 Set A, P2 MD Set B, and P2 Set-C separate.
3. RRS is per target; exclude WT non-binders (`|ΔG_WT| < 5.0 kcal mol⁻¹`).
4. Docking-RRS is not MD-RRS. MD-RRS requires complete trajectories and PASS QC.
5. Label all outputs `VALIDATED`, `EXPLORATORY`, `FAILED`, `PENDING`, or `NOT_COMPUTED`.
6. Never overwrite a canonical result; create a versioned output and a short dated checkpoint.

## 4. Immediate action queue

| Priority | Action | Gate |
|---:|---|---|
| 1 | Monitor production 15320 to completion and verify trajectory/checkpoint hashes | All 16 production systems complete |
| 2 | Run aggregate trajectory QC on production 15320 after all 16 tasks terminate | Exactly 16 PASS-QC rows |
| 3 | Run trajectory QC, then MD-RRS only on PASS-QC rows | Predeclared bound-fraction rule |
| 4 | Complete P1/P3/P4/P5 metadata, deposits, and author read-through | Submission package audit |

## 5. Archive and maintenance

Long-form job narratives, obsolete estimates, intermediate roadmaps, and superseded audits are preserved in `docs/archive/md_full_20260812/`. Active files should receive only concise checkpoints and links to machine-readable evidence.
