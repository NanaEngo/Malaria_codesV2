# Malaria Codes V2 — Antimalarial Drug Discovery

Multi-project research codebase for computational antimalarial drug discovery, covering virtual screening, polypharmacology, quantum-inspired representations, Monte Carlo strategies, GNN/Transformer benchmarks, and LISH-MoA structure-phenotype prediction.

## Canonical project directories

| Project | Directory | DAR | Status |
|---------|-----------|-----|--------|
| P1 — Chem space + virtual screening | `Project1_Chem_space_antimalarial_V7_CorrectedGrid/` | [P1 DAR](Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_DATA_ANALYSIS_REPORT.md) | V7 JCIM submission-ready |
| P2 — Polypharmacology MD validation | `Project2_Polypharmacology_MD_ValidationV2607/` | [P2 DAR](Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md) | Set-C MD pilot complete; manuscript 30p/16p SM |
| P3 — Quantum-inspired representations | `Project3_Quantum_Inspired_RepresentationsV2607_V4/` | [P3 DAR](Project3_Quantum_Inspired_RepresentationsV2607_V4/P3_DATA_ANALYSIS_REPORT.md) | V2608 manuscript ready; Zenodo DOI reserved |
| P4 — Advanced Monte Carlo | `Project4_Advanced_Monte_CarloV2607_V2/` | [P4 DAR](Project4_Advanced_Monte_CarloV2607_V2/P4_DATA_ANALYSIS_REPORT.md) | v12 benchmark complete |
| P5 — GNN/Transformer drug discovery | `Project5_GNN_Transformer_DrugDiscovery_V2/` | [P5 DAR](Project5_GNN_Transformer_DrugDiscovery_V2/P5_DATA_ANALYSIS_REPORT.md) | Benchmark complete; Zenodo staged |
| P6 — LISH-MoA structure-phenotype | `Project6_LISH_MoA_Structure_Phenotype/` | [P6 DAR](Project6_LISH_MoA_Structure_Phenotype/P6_DATA_ANALYSIS_REPORT.md) | 7-arm scaffold complete; calibration + QKS computed |
| P7 — Quantum molecular encoding QML | `Project7_Quantum_Molecular_Encoding_QML/` | [P7 DAR](Project7_Quantum_Molecular_Encoding_QML/P7_DATA_ANALYSIS_REPORT.md) | Project init |

## Key documents

- **[AGENTS.md](AGENTS.md)** — Active project instructions, provenance rules, status table
- **[BMAD](BMAD_Q1_DATA_ANALYSIS_REPORT.md)** — Cross-project synthesis (headlines from all DARs)
- **[CENTRAL_QUESTIONS](CENTRAL_QUESTIONS_PROJECTS.md)** — Open research questions per project
- **[Integration roadmap](P1_P7_INTEGRATION_ROADMAP.md)** — Cross-project integration plan

## Structure

```
Malaria_codesV2/
├── Project1_.../ through Project7_.../   # Canonical project dirs (DAR + scripts + results)
├── _archives/                            # Superseded project versions (P1 V5, P3 V1/V2, P4 V1, P5 V1)
├── _archive_docs/                        # Superseded root-level docs (stale DARs, audit snapshots)
├── docs/                                 # Web research, audits, historical docs (gitignored)
├── vital_posters/                        # ICTP 2026 posters + abstracts (ictp_2026/, ictp_addis/, ictp_trieste/)
├── AGENTS.md                             # Active instructions
├── BMAD_Q1_DATA_ANALYSIS_REPORT.md       # Cross-project synthesis
├── CENTRAL_QUESTIONS_PROJECTS.md         # Open questions
└── P1_P7_INTEGRATION_ROADMAP.md          # Integration plan
```

## Reading order

1. `AGENTS.md` — understand provenance rules and current status
2. Per-project DAR — deep dive into any project
3. `BMAD_Q1_DATA_ANALYSIS_REPORT.md` — cross-project context
4. `CENTRAL_QUESTIONS_PROJECTS.md` — what remains unsolved
