# Targeted external docking replication — frozen plan

**Date:** 27 August 2026  
**Status:** `EXECUTED_AND_AUDITED_312_OF_312`

## Objective

Test whether the P2 docking-derived WT/mutant RRS pattern transfers to a genuinely non-overlapping external ligand panel. This is a docking replication, not experimental validation and not an MD study.

## Proposed panel

Use the already audited ChEMBL-derived *P. falciparum* panel only as a source of external ligand structures. Select 20–50 valid canonical SMILES after:

1. exact canonical-SMILES exclusion against all 17 P2 candidates;
2. exact duplicate removal;
3. retention of source identifiers and activity provenance;
4. selection before inspecting any newly calculated RRS values;
5. preserving a broad activity distribution rather than selecting favorable compounds.

The present ChEMBL artifact cannot itself validate RRS biology because it has no paired PfDHFR/PfCRT WT–mutant measurements.

## Frozen target panel

- PfDHFR: WT, N51I, C59R, S108N, I164L;
- PfCRT: WT, K76T, K76A.

The RRS remains the existing P2 estimand:

\[
\mathrm{RRS}=|S_{mutant}|/|S_{WT}|\times100,
\]

with target-specific WT denominators below 5.0 kcal mol⁻¹ excluded.

## Protocol lock

Before any run, freeze and hash:

- receptor structures and mutation-generation procedure;
- grid centers and dimensions;
- ligand preparation and protonation rules;
- docking software/version;
- exhaustiveness and seed policy;
- failure and missing-data rules;
- panel-selection file.

No grid optimization, post hoc ligand selection, or silent structural repair is permitted after docking starts.

## Go/no-go gates

Proceed only if:

- at least 20 valid non-overlapping ligands remain;
- all source and panel files are hashed;
- all seven receptor states pass structural audit;
- exact P2 grids and parameters are reproducible;
- the panel is frozen before docking.

Stop if any of these conditions fails. In particular, activity labels must not be substituted for mutation-resolved WT/mutant scores.

## Resource estimate

The preparation phase is light CPU work. Docking is a moderate CPU/HPC task, approximately 140–350 ligand-state runs for 20–50 ligands across seven states, before failed or ineligible cases. MD is not required.

No scheduler submission has been made. The plan requires an explicit author authorization after the panel and structure gates pass.

## Execution and finalization (updated 27 August 2026)

Array `15605` (40 tasks, `p2_external_docking_replication_production.sbatch`) is the
authorized run. It initially produced 243/320 valid poses; the missing states were repaired under the declared ledger, yielding 312/312 valid poses after excluding EXT-039 as EMBED_FAILURE. The 10 missing ligands failed for
**four distinct, systematic ligand-preparation reasons** (none a docking failure), and
are handled as declared, transparent cases recorded in
`external_docking_repair_ledger.json` (the frozen panel CSV is untouched):

- **(A) salt/counterion** — EXT-019 (.Cl), EXT-021 (.2Cl), EXT-032 (.2Cl), EXT-033
  (.Cl), EXT-036 (.2Cl), EXT-037 (.oxalate): largest-fragment free base.
- **(B) RDKit distance-geometry failure** — EXT-008 (69 heavy atoms, 52 rotatable
  bonds), EXT-038: Open Babel `--gen3d` (force-field 3D) fallback, then SDF → Meeko
  PDBQT.
- **(C) SLURM time-limit partial** — EXT-007 killed at 3/8: only the 5 missing states
  re-docked, existing poses retained.
- **(D) declared EMBED_FAILURE** — **EXT-039** (folded cyclic ether macrocycle): no 3D
  coordinates under RDKit distance geometry, RDKit random-coords, or OBabel `--gen3d`
  within reasonable compute. It is excluded **by declaration**, not silently dropped.
  The panel target is therefore **39 ligands × 8 states = 312 records**.

**Finalization chain (fail-closed, `p2_external_docking_finalize.sh`):**

1. Wait for array `15605` to leave the queue.
2. `p2_external_docking_repair.sh` — declared repair of the 9 reparator ligands
   (salt 6 + OBabel 2 + EXT-007's 5 missing states = 69 states), record the ledger.
3. `p2_external_docking_integrity_audit.py` — 312/312 eligible records with finite
   Vina scores (EXT-039 excluded by declaration) → `PASS_READY_FOR_AGGREGATION`, else
   abort (no aggregation).
4. `p2_external_docking_aggregate.py` — `external_docking_scores.csv`
   (312 records + sha256) → `READY_FOR_RRS_POSTPROCESSING`.
5. `p2_external_docking_rrs.py` — frozen RRS estimand
   (|S_mutant,t|/|S_WT,t| × 100; WT non-binders < 5.0 kcal/mol excluded per target;
   per-mutant mean across binding targets; canonical dual-criterion classes) →
   `external_docking_rrs_20260827.csv/.json`, with the EXT-039 exclusion recorded.

Outputs are docking-derived replication evidence only; they are not experimental
validation and not an MD estimate.
