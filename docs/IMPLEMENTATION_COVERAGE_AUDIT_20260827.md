# Implementation coverage audit — 28 August 2026 (updated 20:10Z)

> **Snapshot 28 Aug 2026 20:10Z** — coverage gate for P2/P5 V2/P6. Companion: `WEB_RESEARCH_P2_P5V2_P6_REINFORCEMENT_20260827.md` and `GITHUB_APPS_SURVEY_20260827.md`. See DARs for live status.

## Purpose

This document reconciles the active P2, P5 V2, and P6 Markdown plans with versioned scripts and artifacts. A documented recommendation is not treated as a result unless its required artifact and validation gate exist.

## P2

| Planned item | Evidence | Status |
|---|---|---|
| External 40-ligand panel, identity and overlap audit | `external_docking_panel_candidate_40_manifest.json` | `COMPLETED` |
| Eight receptor states and protocol reconciliation | `external_docking_protocol_reconciliation.json` | `COMPLETED` |
| Vina 1.2.7, exhaustiveness 64, 25 Å V2 grids | reconciliation JSON/MD and preflight | `COMPLETED` |
| Isolated docking runner | `scripts/p2_external_docking_replication.sbatch` | `COMPLETED` |
| Fail-closed 312-record aggregator (39 ligands × 8 states, EXT-039 declared EMBED_FAILURE) | `scripts/p2_external_docking_aggregate.py` | `COMPLETED; VALIDATED_BLOCKED` |
| External docking scores | 312/312 valid pdbqt (after repair: 6 salts, 2 OBabel, 1 time-limit, EXT-039 excluded) | `COMPLETED 27 Aug 2026` |
| External RRS | 39 ligands, 38 Class A + 1 Class D, bootstrap CI95 mean 100.45 [99.59–101.32] | `COMPLETED 28 Aug 2026` |
| PP-15 single-ligand pilot (docking + MD) | `pp15_docking_20260828/` + `pp15_md_20260828/` (2 WT systems) | `COMPLETED 28 Aug 2026` (pre-equil PASS, EXPLORATORY_SINGLE_LIGAND_PILOT) |
| PP-01 PfDHFR_I164L rerun (production + QC + MM-GBSA) | `runs/20260825T063226Z/replicate_1` | `PRODUCTION+QC DONE 28 Aug 2026; MM-GBSA FAILED_NUMERICAL_QC (frame 901 BOND overflow)` |
| Priority 3C short-MD extension | plan only; requires post-docking decision | `PLANNED / NOT_COMPUTED` |
| §8quater RRS/polypharma per-target bootstrap CI95 + MD-filter retention | PLANNED_SECONDARY (extends 312-record panel) | `PLANNED_SECONDARY` |

## P5 V2

| Planned item | Evidence | Status |
|---|---|---|
| Five partition ChemBERTa campaign | 5 summaries and 125 prediction files | `COMPLETED` |
| Seed-fold completeness and finite-file audit | `chemberta_completion_audit_20260827.json` | `COMPLETED` |
| Extended GNN aggregates and paired contrasts | `robustness/extended_model_aggregates.csv`, `paired_ablation_contrasts.csv` | `COMPLETED_SECONDARY` |
| Scaffold/split and chemical audits | `robustness/split_audit.json`, `chemical_standardization_audit.json` | `COMPLETED_SECONDARY` |
| **Calibration metrics** (ECE/MCE/Brier 30 configs) | `calibration_20260827/calibration_summary.csv` + 30 reliability JSON | `COMPLETED 27 Aug 2026` (was NOT_COMPUTED) |
| RRS/polypharma calibration extensions | `calibration_by_rrs_class.csv` (300 records) + `polypharma_subset_auc.csv` (120 rows: 60 complete + 60 available) | `COMPUTED_SECONDARY 28 Aug 2026` |
| Light GNN hyperparameter sensitivity (job 15617) | `_sens_h64_d02` + `_sens_h256_d01` configs | `COMPLETED 27 Aug 2026` |
| OOD distance-to-neighbor analysis | requires new locked protocol | `NOT_COMPUTED` |
| Calibration slope/intercept fits + recalibrated variants | requires new locked protocol | `NOT_COMPUTED` |
| Canonical claim replacement by extended results | prohibited by project boundary | `NOT_AUTHORIZED` |
| Zenodo package 31/31 staged | `zenodo_package_20260827/` + tarball | `READY_FOR_UPLOAD_NOT_UPLOADED` |

## P6

| Planned item | Evidence | Status |
|---|---|---|
| Versioned drug_id–SMILES mapping | `data/mappings/drugid_to_smiles_contract.json` | `COMPLETED` |
| Mapping coverage, collisions, label audit | `results/p6_phase2/p6_mapping_and_label_audit_20260827.json` | `COMPLETED` |
| Collision-safe fold metrics | phenotype, structure, fusion, GIN/GIN-TFP/GIN-TNE/ChemBERTa fold/report files | `COMPLETED 27 Aug 2026` for collision_group (4 molecular arms) |
| Log loss, AUROC, AUPRC, Brier, ECE | existing fold reports and cross-project audit | `COMPLETED` for collision_group |
| Scaffold-held-out runs (`--dump-predictions` patch) | `predictions/p6_lish_moa_phenotype_scaffold/` (25/25 DONE 18:11Z) | `phenotype DONE 18:11Z; structure 14-20/25 + both 7-11/25 RUNNING 28 Aug 16:19Z` |
| Per-label rare-label table | aggregate label audit exists; dedicated manuscript table not identified | `PARTIAL; DAR-LEVEL ONLY` |
| Calibration/reliability plots | blocked on `--dump` completion (structure/both scaffold) | `NOT_COMPUTED` (per-label); unblocked for phenotype scaffold |
| QKS sensitivity | requires separately frozen kernel protocol | `NOT_COMPUTED_BOUNDED_QKS_NOT_AUTHORIZED` |
| Attention fusion vs polypharma | future work; intermediate cross-modal attention + ≥2-target subset | `PLANNED_SECONDARY_BLOCKED_ON_DUMP` |

## Validation performed

- P5 completion audit: 5/5 partitions, 125/125 records, 125/125 prediction files.
- P5 calibration: 30 configurations, 30 reliability JSON, ECE/MCE/Brier pooled over 25 fold-seed records.
- P5 RRS/polypharma: 17/19,836 panel molecules matched to P2 RRS; 300 cal-by-class records, 120 polypharma AUC rows.
- P6 fold files: 25 rows and finite summary metrics for collision_group arms (phenotype, structure, fusion, GIN/GIN-TFP/GIN-TNE/ChemBERTa).
- P6 phenotype scaffold --dump: 25/25 csv complete at 18:11Z.
- P2 external docking: 312/312 valid pdbqt (repair ledger: 6 salts, 2 OBabel, 1 time-limit, EXT-039 declared EMBED_FAILURE).
- P2 PP-15: pre-equilibration audit PASS for 2 WT systems; production pending equilibration.
- P2 PP-01 PfDHFR_I164L: production COMPLETE 17:25Z; QC PASS (bound_frac 1.0, 2.86 Å, 10.0 ns); MM-GBSA FAILED_NUMERICAL_QC frame 901.
- Python compilation and JSON validation pass.
- `git diff --check` pass.

## Current scheduler boundary

P5 artifacts are complete and secondary; P6 scaffold molecular arms (structure, both) RUNNING 28 Aug 16:19Z with --dump-predictions. P2 PP-01 I164L MM-GBSA FAILED_NUMERICAL_QC (PBC overflow frame 901); K76A peer rerun also BOND overflow — not a production blocker since canonical endpoints are retained.

## Deliberate non-implementation

The following remain explicitly `NOT_COMPUTED` (not inferred from unrelated outputs): P2 priority 3C short-MD extension; P5 OOD distance-to-neighbor analysis; P5 calibration slope/intercept fits; P5 cluster-based split retraining; P6 QKS sensitivity; P6 per-label calibration plots (until scaffold dumps complete); P6 attention fusion.
