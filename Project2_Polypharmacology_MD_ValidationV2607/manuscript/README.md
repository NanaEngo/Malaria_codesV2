# P2 manuscript — release index

## Canonical release: V2609C

- **Target journal:** *Journal of Chemical Information and Modeling* (ACS)
- **Main manuscript:** `V2609C/Polypharmacology_MD_Validation_V2609C.tex`
- **Supporting Information:** `V2609C/Polypharmacology_MD_Validation_SM_V2609C.tex`
- **Cover letter:** `V2609C/Cover_Letter_V2609C.tex`
- **Bibliography:** `V2609C/Project2_Polypharmacology_MD_Validation.bib`
- **Manifest:** `V2609C/SUBMISSION_MANIFEST_V2609C.md`
- **Graphics:** `V2609C/Graphics/`

`V2609C/` is the only active manuscript source directory. Its source files, tables, bibliography, graphics, and release manifest form the canonical package. PDFs are generated release products; auxiliary files and logs are disposable build artefacts and must not be edited by hand.

## Historical release: V2609B

`V2609B/` contains the retained V2609B manuscript, Supporting Information, cover letter, tables, bibliography, graphics, and compiled release products. It is an archive for provenance and comparison, not an active source for new claims. Its archive manifest is `V2609B/SUBMISSION_MANIFEST_V2609B.md`.

Older V2607/V2609 variants, displaced source files, and generated leftovers are retained under `../docs/archive/manuscript/` and are not submission sources.

## Scientific scope

The canonical manuscript reports a computational-prioritisation and interpretation-calibration study, not an experimental validation study. The Set-C cohort contains 17 candidates and 136 PfDHFR/PfCRT docking systems. Docking-derived RRS, ACSI, and PNS are separate estimands:

- **RRS:** target-specific retention of empirical AutoDock Vina score under six mutant states. The primary analysis uses 12 candidates with eligible WT scores for both PfDHFR and PfCRT; five PfCRT-only candidates form a coverage-limited sensitivity set.
- **ACSI:** a cohort-normalised chemical-space descriptor relative to the declared reference fingerprints and molecular descriptors.
- **PNS:** a STRING-centrality-weighted WT docking-score ranking. PfCRT centrality is imputed and evaluated by sensitivity analysis; PNS is not a target-essentiality or polypharmacology measurement.

The parent-study MD cohort contains four WT complexes. A secondary 16-system Set-C pilot (PP-01/PP-02) has trajectory QC and MM-GBSA outputs but is not merged into the primary docking-RRS analysis. The seven-of-eight directional difference is a protocol-local observation that docking-score retention and short-MD local geometry are not interchangeable; it is not a general failure rate, an affinity estimate, or a biological resistance signal.

## Reproducibility entry points

Run from the Project2 directory:

```bash
conda run -n malaria_md python scripts/p2_rigorous_audit.py
conda run -n malaria_md python -m pytest tests -q
```

The rigorous audit regenerates the compact RRS, ACSI, PNS, and cross-metric outputs listed in `results/README.md`. Its inferential outputs are descriptive because the candidate cohort was selected before the audit.

## Evidence and reporting boundaries

- Vina scores are docking scores, not binding free energies.
- RRS is not a biochemical resistance measurement.
- The A*/A potency discriminator uses the weakest eligible WT target, not a strongest-target anchor.
- Class D is the residual class in which no available mutant RRS reaches 80%; it is not defined by an unsupported 60% cutoff.
- The five PfCRT-only candidates are never described as equivalent to complete two-target candidates.
- MM-GBSA values are system-specific endpoint diagnostics with within-trajectory variation, not thermodynamic confidence intervals.
- Full-panel MD-RRS remains `NOT_COMPUTED`; the pilot is single-replicate and secondary.
- No target engagement, pathway mechanism, clinical efficacy, or resistance circumvention is claimed.

## Supporting documentation

- `../P2_DATA_ANALYSIS_REPORT.md` — active data-analysis report and provenance summary.
- `../results/README.md` — result-file inventory and evidence boundaries.
- `../docs/Methods/` — detailed MD and MM-GBSA protocol notes.
- `../docs/P2_V2609_MD_AUDIT_MATRIX.md` — archive and cleanup policy.

If a narrative file disagrees with a machine-readable audit output, the output and the current V2609C source must be reconciled before release.
