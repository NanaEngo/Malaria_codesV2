# Step 1 — Independent external RRS replication feasibility

**Date:** 27 August 2026  
**Project:** P2 Polypharmacology MD Validation  
**Status:** `NO_GO_FOR_EXTERNAL_RRS_REPLICATION_WITH_LOCAL_ARTIFACTS`

## Scope

This audit assessed whether the locally available external artifacts could support an independent replication of the P2 WT/mutant relative-resistance score (RRS) analysis, without downloading new data or launching docking/MD calculations.

## Available external artifact

The P5 public panel was built from ChEMBL CHEMBL364 (*P. falciparum*) activity records and contains:

- 22,447 retained rows after activity/structure filtering;
- 22,267 molecule-disjoint rows in the reported transfer panel after excluding 180 canonical-SMILES overlaps with the P5 panel;
- columns sufficient for a general activity benchmark (`smiles`, binary `activity`, `pchembl`).

The provenance record identifies IC50/EC50 records aggregated into active/inactive labels. The artifact does **not** provide paired measurements or model scores for PfDHFR/PfCRT WT and mutant states.

## RRS requirements versus available fields

| Requirement for P2 RRS replication | Available locally | Consequence |
|---|---:|---|
| Non-overlapping ligand structures | Yes, for the P5 panel | Supports an activity-transfer audit only |
| Target-specific WT state | No | Cannot define the WT denominator |
| Target-specific mutant state | No | Cannot define the mutant numerator |
| Paired WT/mutant activity or score per ligand | No | Cannot calculate per-ligand RRS |
| P2 docking grids and target-state protocol | Not in the external panel | A new docking study would be required |
| Mutation-resolved experimental labels | No | Cannot test biological resistance transfer |

## Independence assessment

The ChEMBL panel is external to the P5 canonical panel for the reported molecule-disjoint benchmark, but it is not an independent replication of P2: it addresses a different estimand (general antimalarial activity classification rather than WT/mutant relative score change), and the current P2 audit contains no target-state-resolved external panel.

P1 is also unsuitable as an independent replication because the P1/P2 audit found 17/17 exact canonical-SMILES and identifier matches with shared workflow provenance.

## Decision

**No-go** for an independent external RRS replication using currently available local artifacts. No RRS value, class, or biological-transfer claim was generated.

**Go** for a future targeted docking replication if a genuinely non-overlapping ligand panel is assembled and the same target-state structures, grids, protonation rules, scoring settings, eligibility rules, and RRS estimand are frozen before execution. This would be a moderate CPU/HPC task, not an MD task.

## Permitted use in P2

The ChEMBL/P5 artifact may be cited only as related-project evidence for general activity-ranking transfer, with its own provenance and estimand. It must not be described as external validation of P2 RRS, mutant affinity, resistance resilience, target engagement, or polypharmacology.
