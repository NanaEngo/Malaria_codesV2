# External docking launch status — updated 27 August 2026

- Production array: `15605` (`p2_external_docking_replication_production.sbatch`, 40 tasks, `0-39%8`)
- Output directory: `external_docking_run_20260827/`
- Panel: `external_docking_panel_candidate_40.csv` (40 ligands × 8 states = 320 systems)

## Progress

- 15 ligands complete 8/8; 3 in flight at the last check; 20 pending; array ETA ~2.5–3.5 h.
- Two ligand-preparation failures recorded (NOT docking failures):
  - **EXT-008** — RDKit 3D embedding failed at seed 42 (long C₁₂-lysine peptoid chain);
    repaired with `useRandomCoords=True` across seeds (validated locally).
  - **EXT-019** — SMILES carries a `.Cl` counterion → 2 fragments, Meeko rejection;
    repaired by taking the largest fragment (free base), validated locally.

## Finalization chain (fail-closed)

Run `scripts/p2_external_docking_finalize.sh` once the array leaves the queue:

1. Wait for array `15605` completion.
2. Integrity audit → `BLOCKED` with gaps = {EXT-008, EXT-019} only.
3. Declared repair (`p2_external_docking_repair.sh`, ledger
   `external_docking_repair_ledger.json`, frozen panel CSV untouched) → 16 states re-docked.
4. Re-audit → `PASS_READY_FOR_AGGREGATION` at 320/320.
5. Aggregate → `external_docking_scores.csv` (320 records + sha256).
6. RRS post-processing → `external_docking_rrs_20260827.csv/.json`
   (frozen estimand: |S_mutant,t|/|S_WT,t| × 100, WT non-binders < 5.0 kcal/mol
   excluded per target, per-mutant mean across binding targets, canonical classes).

Outputs are docking-derived replication evidence only (NOT experimental
validation, NOT an MD estimate). Historical job `15512` is superseded by `15605`.
