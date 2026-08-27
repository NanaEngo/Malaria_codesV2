# External docking panel candidate — 40 ligands

**Status:** `CANDIDATE_PANEL_AUDITED_PENDING_AUTHOR_FREEZE`  
**Important:** this is a panel candidate only. No docking, RRS calculation, or biological validation has been performed.

## Construction

Source: the molecule-disjoint ChEMBL-derived *P. falciparum* panel used by the related P5 transfer benchmark.

The panel was constructed deterministically by:

1. reading the source CSV without changing its activity labels;
2. confirming unique canonical-SMILES rows;
3. checking exact SMILES overlap against the 17 P2 Set-C candidates;
4. sorting by `pchembl`, then canonical SMILES;
5. selecting 40 evenly spaced rows across the sorted activity range.

No P2 docking score, RRS value, class, or MD result was used in selection.

## Audit summary

- Source rows: 22,267.
- Source unique SMILES: 22,267.
- Exact overlap with P2 candidates: 0.
- Duplicate rows removed: 0.
- Candidate panel size: 40.
- Activity labels: 34 active, 6 inactive.
- `pchembl` range in candidate panel: 3.96–11.00; median 6.74.

The exact panel and hashes are recorded in:

```text
external_docking_panel_candidate_40.csv
external_docking_panel_candidate_40_manifest.json
```

## Remaining gates

This panel is not yet frozen for docking. Before execution, verify:

- the seven receptor-state structures;
- exact grid centers and dimensions;
- ligand preparation and protonation behavior;
- pinned docking software and exhaustiveness;
- output and failure handling;
- absence of duplicate structures after the project’s actual ligand standardization procedure.

If any gate fails, the panel remains a feasibility artifact and no docking job should be submitted.
