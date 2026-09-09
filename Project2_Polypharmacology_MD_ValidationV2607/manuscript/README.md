# Project2 manuscript — V2609 release

## Source and V2609 submission package

- **Target journal:** *Journal of Chemical Information and Modeling* (ACS)
- **Immutable source release:** `LaTeX/Polypharmacology_MD_Validation_V2607.tex`, `LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex`, `LaTeX/Cover_Letter.tex`
- **V2609 main release:** `LaTeX/Polypharmacology_MD_Validation_V2609.tex`
- **V2609 Supporting Information:** `LaTeX/Polypharmacology_MD_Validation_SM_V2609.tex`
- **V2609 cover letter:** `LaTeX/Cover_Letter_V2609.tex`
- **Bibliography:** `LaTeX/Bibliography_Polypharmacology_MD_Validation.bib`
- **V2609 submission manifest:** `LaTeX/SUBMISSION_MANIFEST_V2609.md`
- **Historical/canonical V2607 manifest:** `LaTeX/SUBMISSION_MANIFEST.md`

The V2607 LaTeX files are the immutable source release; the separately named V2609 LaTeX files are the active narrative-refinement release. The V2609 manifest is authoritative for the active release. Neither source set should be edited by hand after compilation. Compiled PDFs and auxiliary files are
regenerated from these sources and must not be edited by hand.

## Scientific scope

The manuscript reports a computational-prioritisation study, not an
experimental validation study. The canonical Set-C cohort contains 17
candidates and 136 PfDHFR/PfCRT docking systems. Docking-derived RRS, ACSI,
and PNS are separate estimands:

- **RRS:** target-specific retention of empirical AutoDock Vina score under six
  mutant states. The primary analysis uses 12 candidates with eligible WT
  scores for both PfDHFR and PfCRT; five PfCRT-only candidates are a
  coverage-limited sensitivity set.
- **ACSI:** cohort-normalised chemical-space positioning relative to DrugBank
  and ANPDB reference fingerprints, plus fraction sp3 and NPL descriptors.
- **PNS:** a STRING-centrality-weighted WT docking-score ranking. PfCRT
  centrality is imputed and is evaluated by sensitivity analysis; PNS is not a
  target-essentiality or polypharmacology measurement.

The separate parent-study MD cohort contains four WT complexes. Only the
PfCRT--214 system yielded an interpretable MM-GBSA endpoint. A secondary
16-system Set-C pilot (PP-01/PP-02) has trajectory QC and MM-GBSA outputs but
is not merged into the primary docking-RRS analysis.

## Reproducibility entry points

Run from the Project2 directory:

```bash
mamba run -n qom python scripts/p2_rigorous_audit.py
mamba run -n qom python -m pytest tests -q
```

The rigorous audit regenerates:

- `results/c_rrs_classification.csv`
- `results/c_rrs_sensitivity.csv`
- `results/cross_metric_statistical_audit.csv`
- `results/cross_metric_statistical_audit.json`
- `results/pns_imputation_sensitivity.csv`
- `results/pns_imputation_sensitivity.json`
- `results/c_acsi_scores.csv`
- `results/p2_rigorous_audit_manifest.json`

The audit uses seed 42, 100,000 permutations, and 10,000 bootstrap resamples.
Its inferential outputs are descriptive because the candidate cohort was
selected before the audit and is not an independent validation sample.

## Evidence and reporting boundaries

- Vina scores are docking scores, not binding free energies.
- RRS is not a biochemical resistance measurement.
- The A*/A potency discriminator uses the **weakest eligible WT target**, not
a strongest-target anchor.
- Class D is the residual class in which no available mutant RRS reaches 80%;
it is not defined by an unsupported 60% cutoff.
- The five PfCRT-only candidates are never described as equivalent to complete
PfDHFR/PfCRT candidates.
- MM-GBSA values are system-specific endpoint diagnostics with within-trajectory
variation, not thermodynamic confidence intervals.
- No target engagement, pathway mechanism, clinical efficacy, or resistance
circumvention is claimed.

## Supporting documentation

- `../P2_DATA_ANALYSIS_REPORT.md` — active data-analysis report and provenance
  summary.
- `../results/README.md` — result-file inventory and source boundaries.
- `Methods/` — detailed MD and MM-GBSA protocol notes.
- `../docs/P2_V2609_MD_AUDIT_MATRIX.md` — Markdown inventory and deletion policy.

Historical drafts are retained only in the repository archive and are not
submission sources. If a number in a narrative file disagrees with the
machine-readable audit outputs, the audit outputs and the current LaTeX source
must be reconciled before submission.
