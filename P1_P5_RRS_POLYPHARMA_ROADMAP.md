# Master Roadmap P1–P5 — active plan

**Version:** 1.11 — 12 August 2026
**Purpose:** current decisions and next actions only.
**Detailed history:** `docs/archive/md_full_20260812/P1_P5_RRS_POLYPHARMA_ROADMAP.md`

## 1. Source-of-truth map

| Project | Active DAR | Manuscript/workspace | Current state |
|---|---|---|---|
| P1 | `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | `Project1_Chem_space_antimalarial_V6_CorrectedGrid/` | V6 submission-oriented; final author metadata/read-through remain |
| P2 | `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | `Project2_Polypharmacology_MD_ValidationV2607/` | Docking-RRS complete; Set-C MD-RRS pending |
| P3 | `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | `Project3_Quantum_Inspired_RepresentationsV2607/` | Canonical benchmarks and external validation complete |
| P4 | `P4_DATA_ANALYSIS_REPORT.md` | `Project4_Advanced_Monte_CarloV2607/` | v12 scalar benchmark and Pareto analysis complete |
| P5 | `P5_DATA_ANALYSIS_REPORT.md` | `Project5_GNN_Transformer_DrugDiscovery/` | Benchmark and external validation complete |

## 2. Project priorities

### P1 — V6 submission package

- Keep V6 as the submission-oriented workspace; V4/V5 remain evidence/remediation layers.
- Preserve the corrected 2F6I accounting and the 17×4 target-wise Vina table.
- Finish ORCID/funding metadata and final author read-through before deposit.
- Do not promote exploratory V5 consensus/RRS as independent biological validation.

### P2 — RRS/polypharmacology plus MD

- Canonical cohort: 17 Set-C candidates, per-target docking-RRS classes A*:6/B:5/C:5/D:1.
- The bounded pilot contains 16 prepared systems (PP-01/PP-02 × PfDHFR/PfCRT mutation states) using the explicitly documented OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P deviation.
- **Live witness only:** `15254` equilibration complete → `15259` production running for isolated `PP-01_PfDHFR_WT` → `15260` QC pending (`afterok:15259`).
- This is not the full 16-system production chain. `md_rrs_status=NOT_COMPUTED` until complete trajectories pass QC.
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
| 1 | Monitor 15259 and allow 15260 to run only after successful completion | Production complete + trajectory hashes |
| 2 | Launch/verify the full candidate-specific Set-C production chain | Complete panel, no witness-only promotion |
| 3 | Run trajectory QC, then MD-RRS only on PASS-QC rows | Predeclared bound-fraction rule |
| 4 | Complete P1/P3/P4/P5 metadata, deposits, and author read-through | Submission package audit |

## 5. Archive and maintenance

Long-form job narratives, obsolete estimates, intermediate roadmaps, and superseded audits are preserved in `docs/archive/md_full_20260812/`. Active files should receive only concise checkpoints and links to machine-readable evidence.
