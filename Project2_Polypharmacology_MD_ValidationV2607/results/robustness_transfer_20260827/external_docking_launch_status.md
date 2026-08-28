# External docking launch status — updated 27 August 2026

- Production array: `15605` (`p2_external_docking_replication_production.sbatch`, 40 tasks, `0-39%8`)
- Output directory: `external_docking_run_20260827/`
- Panel: `external_docking_panel_candidate_40.csv` (40 ligands × 8 states)

## Array 15605 result

Initially completed with **243/320 valid poses**; the declared repair subsequently yielded **312/312 valid poses** after excluding EXT-039 as `EMBED_FAILURE`. The 10 missing ligands were attributable to four distinct,
systematic ligand-preparation reasons (none a docking failure). All are handled as
declared cases in `external_docking_repair_ledger.json` (frozen panel CSV untouched):

- **(A) salt/counterion** — EXT-019 (.Cl), EXT-021 (.2Cl), EXT-032 (.2Cl), EXT-033
  (.Cl), EXT-036 (.2Cl), EXT-037 (.oxalate): largest-fragment free base.
- **(B) RDKit distance-geometry failure** — EXT-008 (69 heavy atoms, 52 rotatable
  bonds), EXT-038: Open Babel `--gen3d` fallback, then SDF → Meeko PDBQT.
- **(C) SLURM time-limit partial** — EXT-007 killed at 3/8: only the 5 missing states
  re-docked, existing poses retained.
- **(D) declared EMBED_FAILURE** — **EXT-039** (folded cyclic ether macrocycle): no 3D
  coordinates under RDKit distance geometry, RDKit random-coords, or OBabel `--gen3d`
  within reasonable compute. Excluded **by declaration**, not silently dropped.

**Repaired panel target: 39 ligands × 8 states = 312 records.**

## Finalization chain (fail-closed)

`scripts/p2_external_docking_repair.sh` is launched (log `/tmp/p2_repair.log`) and
re-docks the 9 reparator ligands (salt 6 + OBabel 2 + EXT-007's 5 missing states =
69 states). Then run `scripts/p2_external_docking_finalize.sh` once it completes:

1. Wait for array `15605` completion (already out of queue).
2. Integrity audit → gaps = {EXT-007(subset), EXT-008, EXT-019, EXT-021, EXT-032,
   EXT-033, EXT-036, EXT-037, EXT-038}; EXT-039 is excluded by declaration.
3. Declared repair ledger written; all 9 reparator ligands re-docked.
4. Re-audit → `PASS_READY_FOR_AGGREGATION` at **312/312** (EXT-039 excluded).
5. Aggregate → `external_docking_scores.csv` (312 records + sha256).
6. RRS post-processing → `external_docking_rrs_20260827.csv/.json`
   (frozen estimand: |S_mutant,t|/|S_WT,t| × 100, WT non-binders < 5.0 kcal/mol
   excluded per target, per-mutant mean across binding targets, canonical classes;
   EXT-039 exclusion recorded).

Outputs are docking-derived replication evidence only (NOT experimental
validation, NOT an MD estimate). Historical job `15512` is superseded by `15605`.