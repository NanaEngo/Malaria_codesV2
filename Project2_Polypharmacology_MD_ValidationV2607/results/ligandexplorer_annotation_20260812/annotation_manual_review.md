# LigandExplorer structural annotation — manual review record

**Run:** 15272  
**Date:** 12 August 2026  
**Role:** structural ligand annotation only  
**Backend/device:** GNN / CPU  
**LigandExplorer commit:** `d47eea0d033bb2127ee6836445554881c59edc8e`

## Scope

LigandExplorer was run on the four accepted P2 receptor structures:

- `2F6I` — PfClpP
- `7F3Y` — PfDHFR
- `6UKJ` — PfCRT
- `9N10` — PfATP4

`4GM2` was excluded because it represents PfClpR rather than the active PfClpP paralog.

## Observed output

| PDB | Target | Valid ligand-box JSON artefacts | Status |
|---|---|---:|---|
| 2F6I | PfClpP | 0 | `NO_CLASSIFICATION_ARTIFACT` |
| 7F3Y | PfDHFR | 4 | `LIGAND_BOX_ARTIFACT_PRESENT` |
| 6UKJ | PfCRT | 2 | `LIGAND_BOX_ARTIFACT_PRESENT` |
| 9N10 | PfATP4 | 0 | `NO_CLASSIFICATION_ARTIFACT` |

The valid artefacts are spatial ligand-box JSON files. Their filenames encode LigandExplorer's emitted ligand-category labels; the JSON files contain box coordinates and dimensions. They are not standalone calibrated classification-probability outputs. No calibrated confidence or biological-activity estimate is present in these artefacts.

## Verdict

The process returned exit code 0, but the fail-closed provenance audit classifies the run as:

`COMPLETED_PARTIAL_REQUIRES_MANUAL_REVIEW`

This is a partial structural annotation, not a complete four-receptor annotation. The output may support a limited structural-context note after manual inspection of the receptor/ligand records. It must not be used to claim:

- IC50/EC50 or antimalarial activity;
- experimental target engagement;
- docking affinity or docking-RRS validation;
- MD stability or MD-RRS validation;
- experimentally demonstrated polypharmacology.

The annotation therefore remains an auxiliary provenance result and does not modify candidate selection, docking scores, RRS, PNS, ACSI, MD, or the P2 manuscript's quantitative claims.

## Reproducibility artefacts

- Input archive: `p2_receptor_panel.zip`
- Full provenance: `annotation_provenance.json`
- Per-PDB artefact audit: `annotation_provenance.json` → `artifact_audit`
- Runtime logs: `ligandexplorer.stdout.log`, `ligandexplorer.stderr.log`
- Runner: `scripts/p2_ligandexplorer_annotation.py`
