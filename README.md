# Malaria_codesV2 — project entry point

**Updated:** 12 August 2026
**Purpose:** computational antimalarial discovery across chemical space, docking/RRS, quantum-inspired representations, Monte Carlo generation, and GNN/Transformer benchmarking.

## Read first

1. `AGENTS.md` — active workflow and provenance rules.
2. `docs/MD_DOCUMENT_INDEX.md` — Markdown source map and archive policy.
3. The relevant DAR:
   - P1–P3: `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
   - P4: `P4_DATA_ANALYSIS_REPORT.md`
   - P5: `P5_DATA_ANALYSIS_REPORT.md`
4. `P1_P5_RRS_POLYPHARMA_ROADMAP.md` — current action queue.

## Project status

| Project | Workspace | Status |
|---|---|---|
| **P1** | `Project1_Chem_space_antimalarial_V6_CorrectedGrid/` | V6 is submission-oriented; V4/V5 remain evidence/remediation layers |
| **P2** | `Project2_Polypharmacology_MD_ValidationV2607/` | Docking-RRS/polypharmacology complete; Set-C MD-RRS pending |
| **P3** | `Project3_Quantum_Inspired_RepresentationsV2607/` | Canonical benchmarks and external validation complete |
| **P4** | `Project4_Advanced_Monte_CarloV2607/` | v12 scalar benchmark and Pareto analysis complete |
| **P5** | `Project5_GNN_Transformer_DrugDiscovery/` | Benchmark and public-panel validation complete |

## Current scientific conclusions

- **P1/P2:** chemical novelty, target-wise docking, and per-target docking-RRS support computational prioritisation; they do not establish IC₅₀/EC₅₀, target engagement, or experimental resistance circumvention.
- **P2:** canonical Set-C RRS classes are A*:6/B:5/C:5/D:1. The live MD chain is an isolated `PP-01_PfDHFR_WT` witness: 15254→15259→15260; full-panel MD-RRS remains `NOT_COMPUTED`.
- **P3:** ECFP4 remains stronger than the hybrid; QKS is statistically comparable to RBF, not superior.
- **P4:** Random exceeds MCTS on the canonical scalar reward, while the Pareto front retains multi-objective trade-offs.
- **P5:** ECFP4-RF dominates learned models under scaffold split; GIN-TFP provides modest complementary signal.

## Canonical submission locations

- P1 V6: `Project1_Chem_space_antimalarial_V6_CorrectedGrid/manuscript/`
- P2: `Project2_Polypharmacology_MD_ValidationV2607/manuscript/LaTeX/`
- P3: `Project3_Quantum_Inspired_RepresentationsV2607/manuscript/LaTeX/`
- P4: `Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/`
- P5: `Project5_GNN_Transformer_DrugDiscovery/manuscript/`
- Submission overview: `README_SUBMISSION.md`
- Zenodo status: `README_ZENODO.md` (reserved DOI; upload pending)

## Repository rules

- Keep P1 Set A, P2 MD Set B, and P2 Set-C disjoint.
- Freeze inputs, scripts, parameters, hashes, and QC before promoting a result.
- Distinguish `VALIDATED`, `EXPLORATORY`, `FAILED`, `PENDING`, and `NOT_COMPUTED`.
- Never treat docking-RRS as MD-RRS or a computational score as experimental activity.
- Historical long-form Markdown is archived under `docs/archive/`; generated `graphify-out/` and dependency documentation are not evidence sources.
