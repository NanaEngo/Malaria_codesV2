# Malaria Codes V2 — Antimalarial Drug Discovery

Multi-project research codebase for computational antimalarial drug discovery, covering virtual screening, polypharmacology, quantum-inspired representations, Monte Carlo strategies, GNN/Transformer benchmarks, and LISH-MoA structure-phenotype prediction.

## Canonical project directories

| Project | Directory | DAR | Status |
|---------|-----------|-----|--------|
| P1 — Chem space + virtual screening | `Project1_Chem_space_antimalarial_V7_CorrectedGrid/` | [P1 DAR](Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_DATA_ANALYSIS_REPORT.md) | V7 JCIM submission-ready |
| P2 — Polypharmacology MD validation | `Project2_Polypharmacology_MD_ValidationV2607/` | [P2 DAR](Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md) | Set-C MD pilot complete; manuscript 30p/16p SM |
| P3 — Quantum-inspired representations | `Project3_Quantum_Inspired_RepresentationsV2607_V4/` | [P3 DAR](Project3_Quantum_Inspired_RepresentationsV2607_V4/P3_DATA_ANALYSIS_REPORT.md) | V2608 manuscript ready; Zenodo DOI reserved |
| P4 — Advanced Monte Carlo | `Project4_Advanced_Monte_CarloV2607_V2/` | [P4 DAR](Project4_Advanced_Monte_CarloV2607_V2/P4_DATA_ANALYSIS_REPORT.md) | v12 benchmark complete |
| P5 — GNN/Transformer drug discovery | `Project5_GNN_Transformer_DrugDiscovery_V2609/` | [P5 DAR](Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md) | Benchmark complete; Zenodo staged |
| P6 — LISH-MoA structure-phenotype | `Project6_LISH_MoA_Structure_Phenotype/` | [P6 DAR](Project6_LISH_MoA_Structure_Phenotype/P6_DATA_ANALYSIS_REPORT.md) | 7-arm scaffold complete; calibration + QKS computed |
| P7 — Quantum molecular encoding QML | `Project7_Quantum_Molecular_Encoding_QML/` | [P7 DAR](Project7_Quantum_Molecular_Encoding_QML/P7_DATA_ANALYSIS_REPORT.md) | Project init |

## Central questions

One-line scientific question per project, with the currently-supported evidence-bounded answer. Full statement, subquestions, and detailed evidence in [CENTRAL_QUESTIONS_PROJECTS.md](CENTRAL_QUESTIONS_PROJECTS.md).

| Project | Central question | Evidence-bounded answer |
|---------|------------------|-------------------------|
| **P1** | Can target breadth and mutation resilience be evaluated as distinct, complementary computational properties when prioritising African-natural-product-inspired antimalarial chemotypes? | Yes — separable via per-target RRS with non-binder exclusion; Set-C yields 6 A\* / 5 B / 5 C / 1 D profiles. External DEKOIS validation was approximately null (AUC 0.450), so docking is treated as target-specific prioritisation, not calibrated activity. |
| **P2** | Can a target-specific, resistance-aware computational workflow distinguish polypharmacology-oriented candidates from scoring artefacts and identify which docking hypotheses remain physically plausible after MD? | Partially. Per-target RRS classes established; only PfCRT–214 retained a valid MM-GBSA reading in the canonical re-analysis. PfClpR and PfDHFR–201 dissociated; PfATP4–438 excluded on a CHARMM36→AMBER conversion artefact. MD is a necessary post-docking plausibility filter. |
| **P3** | Do quantum-inspired and topological hybrid representations improve antimalarial activity prediction relative to classical ML fingerprints? | No. Hybrid AUC 0.8876 < ECFP4 0.9475; six-qubit QK not distinguishable from tuned RBF. Honest-negative — they add descriptive/topological value, not predictive value. |
| **P4** | Does chemistry-informed Pareto-guided MCTS provide useful multi-objective candidate-set exploration beyond a single scalar ranking in a constrained antimalarial fragment space? | Partially, but split by estimand. Scalar benchmark: Random 0.6724 > MCTS 0.6649 (honest-negative). Pareto geometry: 4 non-dominated profiles, HV 1.2366 — trade-offs hidden by any single scalar. |
| **P5** | Do GNNs and pretrained sequence transformers improve antimalarial activity prediction beyond a compact ECFP4–random-forest baseline when chemical scaffolds are held out? | No. ECFP4–RF 0.8300 > GIN–TFP 0.8138 > GIN–TNE 0.8090 > GIN 0.8047 > ChemBERTa 0.7867 (scaffold split). All learned arms significantly below ECFP4 after multiplicity correction. Representation–task alignment > model scale on this panel. |
| **P6** | Can a scaffold-aware multi-modal LISH-MoA model predict phenotype from structure with calibration evidence competitive with single-modal baselines? | Mixed. 7-arm scaffold benchmark complete; pooled calibration ECE 0.0006–0.0074; phenotype arm AUC 0.6402; QKS phenotype-vs-both Spearman 0.283. Scaffold-held-out GNN arms near chance (0.5008–0.5064). Cross-modal attention-fusion deferred (GPU contention). |
| **P7** | Quantum molecular encoding for QML — formulation stage. | No canonical results yet; environment setup in progress. |

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
