# Targeted external docking replication — frozen plan

**Date:** 27 August 2026  
**Status:** `PLAN_FROZEN_PENDING_PANEL_AND_STRUCTURE_GATE`

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
