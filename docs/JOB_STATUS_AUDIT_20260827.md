# Job status audit — 28 August 2026 (updated 20:10Z)

> **Snapshot 28 Aug 2026 20:10Z** — point-in-time scheduler + file-gate state. Not a live dashboard; see `BMAD_Q1_DATA_ANALYSIS_REPORT.md` and `AGENTS.md` for canonical status.

## Live scheduler state

| Job | Project | State | Scheduler detail | Scientific status |
|---|---|---|---|---|
| `15512_[0-39%8]` | P2 external docking | `COMPLETED 27 Aug 18:11Z` (312/312 valid after repair) | Released after P5 audit | 39 ligands × 8 states; RRS computed (38 A + 1 D) |
| `15490_[0-4]` | P5 V2 ChemBERTa | `COMPLETED 27 Aug` (5 partitions, 125/125) | Task no longer queryable through `scontrol` | File-level campaign audit PASS |
| `15500` | P6 molecular arms | `COMPLETED 27 Aug` | No live scheduler record returned | All 4 collision_group arms present (GIN/GIN-TFP/GIN-TNE/ChemBERTa) |
| `15502` | P2 PP-01_PfCRT_WT rerun MM-GBSA | `COMPLETED 26 Aug 07:57Z` | Exit 0 | R2 Δ = −28.60 kcal/mol, SEM 0.43 |
| `15617` | P5 V2 GNN hyperparameter sensitivity | `COMPLETED 27 Aug` | Light GNN sens (h64/d02 + h256/d01) | 25 fold-seed per config, integrated in SI §S3 |
| `154648` | P6 phenotype scaffold --dump | `COMPLETED 28 Aug 18:11Z` (25/25 csv) | 8 cores CPU | Calibration-ready for phenotype scaffold |
| `154431` | P6 structure scaffold --dump | `RUNNING 28 Aug 16:19Z` (~02:50 elapsed) | 8 cores CPU, 14-20/25 csv | ETA ~15-20 min |
| `154551` | P6 both scaffold --dump | `RUNNING 28 Aug 16:19Z` (~02:50 elapsed) | 8 cores CPU, 7-11/25 csv | ETA ~40-50 min |
| PP-01_PfDHFR_I164L production | P2 | `COMPLETED 28 Aug 17:25Z` | 5M steps, 10 ns, 27.3 ns/day, 1.18G xtc | QC PASS; MM-GBSA FAILED_NUMERICAL_QC (BOND overflow frame 901) |
| PP-15 NPT | P2 PP-15 pilot | `RUNNING 28 Aug` | equilibration phase, not yet production | NPT at 64 min; production pending |

## P5 V2 completion audit (unchanged from 27 Aug)

The five ChemBERTa partitions passed the lightweight completion gate:

- `canonical_random`: 25/25 seed-fold files, non-empty, summary `COMPUTED`;
- `canonical_scaffold`: 25/25;
- `novel_101`: 25/25;
- `novel_202`: 25/25;
- `novel_303`: 25/25.

Total: 125/125 expected prediction files, with unique seed-fold keys. This confirms computational file completeness, not automatic promotion to canonical claims; the P5 DAR remains the first destination for provenance/statistical reconciliation.

## P5 V2 calibration (28 Aug 2026)

30 configurations (25 GNN-family + 5 ChemBERTa) calibrated post-hoc on archived fold-level predictions: `calibration_20260827/calibration_summary.csv` + 30 reliability JSON files. ECE rises from ≈0.03 (random) to ≈0.07–0.13 (scaffold/novel). Plus RRS/polypharma extensions: `calibration_by_rrs_class.csv` (300 records), `polypharma_subset_auc.csv` (120 rows: 60 complete two-target + 60 available-target).

## P2 external docking completion (27 Aug 2026)

312/312 valid pdbqt after repair ledger (6 salts/free-base, 2 OBabel fallback, 1 time-limit partial, EXT-039 declared EMBED_FAILURE excluded). RRS: 38 Class A + 1 Class D; bootstrap CI95 mean 100.45 [99.59–101.32].

## P6 scaffold --dump progress (28 Aug 2026)

- `phenotype_scaffold`: 25/25 DONE 18:11Z
- `structure_scaffold`: 14-20/25 RUNNING (2h50 elapsed)
- `both_scaffold`: 7-11/25 RUNNING (2h50 elapsed)

## P2 PP-01 PfDHFR_I164L MM-GBSA failure (28 Aug 2026)

MM-GBSA single rerun (`p2_setc_mmgbsa_single.py` PID 312119) returned `FAILED_NUMERICAL_QC`: frame 901 BOND overflow (2.19e7 kcal/mol). PBC-whole auto-retry did not trigger (K76A peer case also BOND overflow). Canonical endpoints retained per author decision; manuscript Limitations notes 7.75 kcal/mol inter-replicate sensitivity.

Validation: P5 completion gate passed; P5 calibration computed; P2 external docking 312/312 valid; P6 phenotype scaffold --dump complete; Python compilation and JSON validation pass; `git diff --check` passed.
