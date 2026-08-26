# Submission Manifest — Project2

**Journal:** *Journal of Chemical Information and Modeling* (ACS)
**Updated:** 26 August 2026 (post-manuscript refinement and compilation)
**Package status:** canonical source files, Supporting Information and cover letter compile without fatal LaTeX errors after the graphics-path correction and final figure audit. DAR/manuscript reconciliation is recorded in `docs/P2_FINAL_RECONCILIATION_ETA_20260825.md`. The compact metric audit regenerates successfully. The full pytest suite passes in the `qom` environment. No Zenodo DOI is recorded yet; the archival deposit remains pending.

## Canonical evidence status

- Set-C docking cohort: 17 candidates, 136 WT/mutant systems.
- Target-balanced RRS panel: 12 candidates with eligible PfDHFR and PfCRT WT scores; six mutant-state ratios per candidate.
- Coverage-limited sensitivity panel: 5 PfCRT-only candidates; not equivalent to the complete panel.
- Parent-study MD: 4 WT complexes × 10 ns; 2 retained bound ligands, but only PfCRT--214 yielded an interpretable MM-GBSA endpoint estimate.
- Set-C MD pilot: 16 systems (PP-01/PP-02), all trajectory-QC PASS; secondary single-replicate MD-RRS and MM-GBSA only.
- RRS classes are mutually exclusive. A*/A use the minimum eligible WT docking-score magnitude; D means no available mutant RRS reaches 80%.
- Cross-metric uncertainty: 100,000 seeded permutations, 10,000 bootstrap resamples, and Bonferroni adjustment for H1--H3. These are descriptive after candidate selection, not independent validation.
- Full-panel 17-candidate MD-RRS: `NOT_COMPUTED` by design.

## Source and compiled-file checksums

Hash values below were recalculated after the latest source edits, metric-audit regeneration and LaTeX compilation.

| File | SHA-256 |
|---|---|
| `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` | `45273602e12e984db06f22198d75b696b0eee58a8116276d57f9729a2d6a6a2d` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.pdf` | `2e29aa65681d1d4d556f89cfd1e22dd92d01f6a32805e037c41a1160d4b68ce2` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.aux` | `dfe4a2cd709bfef58b14579ecbe7ddf5ea2568b7a4c6f8b39e7ad99e02e86507` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex` | `faea0af748c1ec255122e3269cf7978cfd0f8a3700e075e91988a7f2d3440ea1` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.pdf` | `6914d9d622be48fb12174261a64770616030a10e78bcdb13f337ae0f6f725c8c` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.aux` | `956f3b8d3ebdc9396d678584cd40ebb1b96d8b6f6b8911ad534b08657dee3553` |
| `manuscript/LaTeX/Cover_Letter.tex` | `8519d648124a45555cec868684336b4337593ddd1adcd83fd3ad280488052702` |
| `manuscript/LaTeX/Cover_Letter.pdf` | `548e85b113d53c8993c794ae5253dab9c7169ba7bb31b5ba1d0dc870ea6142d0` |
| `manuscript/LaTeX/Table_S0_Docking_Validation.tex` | `b6042ab5f393cf870452c94d436efa75f60bd70b7bc51dab95ee3ff1dc4da52a` |
| `manuscript/LaTeX/Table_S5_ADMET_CrossValidation.tex` | `794eedc9ba760cf22f5627a0a4a4b4afa3c0f8f90112dbf75d6e9e671183dc62` |
| `manuscript/LaTeX/Table_S6_ACSI_Weight_Sensitivity.tex` | `f1d762654213eb17c8192bd29e689c388aaecf3857997918086131738c2b0166` |
| `manuscript/LaTeX/Table_S8_Cohort_Estimands.tex` | `cfb9aa5f9f01a779e220de528de3752abe8a63a8c9f089f8fd73b6dafe9bf1e7` |
| `manuscript/LaTeX/Table_S9_PNS_Imputation_Sensitivity.tex` | `865acffb146cbcd3e698fc04d375accc7abb87051991812daaef550b133bdf1e` |
| `manuscript/LaTeX/Table_S12_RRS_By_Target.tex` | `PLACEHOLDER` |
| `manuscript/LaTeX/Table_S11_RRS_Threshold_Sensitivity.tex` | `PLACEHOLDER` |
| `manuscript/LaTeX/Bibliography_Polypharmacology_MD_Validation.bib` | `633e085bbb731fbab4f4362c6b4f31593edf744700911a976aea3084edd5f2b9` |
| `results/c_rrs_classification.csv` | `9ef22d0cf8c4ae920c5aa2330cef42f7e44d7e88a3a60783ca876be3ef2e089c` |
| `results/c_rrs_sensitivity.csv` | `1b9479bd922ffbda685f2dc28134d60bcdb4e0712f8083f81a8b76827c5e2f2d` |
| `results/cross_metric_statistical_audit.csv` | `0968f3c5fc30de9746b652d47cdacaf0bb2166e2b36c728a1d5c7efe2b436240` |
| `results/cross_metric_statistical_audit.json` | `17e654e53e35e5a55e9218562c1f334077b35dc344480199946ba2b71c2662f2` |
| `results/pns_imputation_sensitivity.csv` | `62a726f76eec05f077a9ff8d3e133a8a0dc7642d86191a8e462451524da61439` |
| `results/pns_imputation_sensitivity.json` | `decabf0a197a6eef20e231314816bc14b6a42beac58fd457280db55cac0a90e0` |
| `results/c_acsi_scores.csv` | `32f42a2ca60e20739a5577a2db01e918d429bba7c11795d3a37de1f3d9504261` |
| `results/p2_results_unlock_manifest.json` | `d68aa2ca0a2284f6a19c082f90429eddbfd33f2a6d650d3c8bfbc86a054e81b8` |

> The cover-letter PDF is now present and has been compiled successfully. The permanent Zenodo DOI remains pending.

## Existing-results unlock audit

The dated audit `docs/P2_RESULTS_UNLOCK_AUDIT_20260825.md` and
`results/p2_results_unlock_manifest.json` reconcile previously completed
results. The PfCRT pH 5.2 redocking is complete for 100/100 library ligands,
and the PNS imputation sensitivity is complete for 17 candidates. These are
separate from PP-01/PP-15 multi-seed redocking and STRING 400/900 network
matrices, which remain unavailable as dedicated source records.

## Lightweight robustness outputs

The local robustness extension is recorded separately from the canonical
manuscript estimand:

- `results/lightweight_robustness/rrs_threshold_sensitivity.csv`;
- `results/lightweight_robustness/rrs_leave_one_mutant_out.csv`;
- `results/lightweight_robustness/docking_score_perturbation.csv`;
- `results/lightweight_robustness/lightweight_analysis_manifest.json`.

Figure audit correction: duplicate/incorrect PPI and RMSD displays were removed from the main manuscript; the SI VAE figure was removed because it belongs to the separate Paper 1 chemical-space analysis. The retained figure set is now limited to the cohort workflow, PfCRT--214 RMSD/contact diagnostics, the cross-metric matrix, and the Set-C pilot scatter, plus the SI MPO and RRS displays.

These are descriptive, cohort-selected sensitivity analyses. They were not
used to replace the canonical RRS table and do not establish biological
validation. Multi-seed redocking and alternative PfCRT protonation remain
available only as fail-closed launcher/templates; no reviewed PP-01/PP-15
receptor, ligand and configuration triplet is present, so no additional score
is promoted. Short MD replicate execution is implemented as
an authorized SLURM launcher; the 16-system, three-replicate preflight passed,
but the authorized HPC witness attempts were stopped fail-closed because the execution node lacked the referenced `charmm36-jul2022.ff` installation and exposed GROMACS 2023.3 without GPU support; no valid new trajectory is reportable. The full diagnosis is recorded in `docs/P2_LIGHTWEIGHT_EXECUTION_STATUS_20260825.md` and the actual authorized submission failure is recorded in `docs/P2_SHORT_MD_EXECUTION_STATUS_20260825.md`.

## Machine-readable audit outputs

- `results/c_rrs_classification.csv`
- `results/c_rrs_sensitivity.csv`
- `results/cross_metric_statistical_audit.csv`
- `results/cross_metric_statistical_audit.json`
- `results/pns_imputation_sensitivity.csv`
- `results/pns_imputation_sensitivity.json`
- `results/c_acsi_scores.csv`
- `results/p2_rigorous_audit_manifest.json`

These outputs are regenerated by `scripts/p2_rigorous_audit.py` and include cohort hashes and relative provenance paths. Large trajectories are not needed to reproduce the compact docking, ACSI, PNS and statistical-audit tables.

## Verification record

```bash
python scripts/p2_rigorous_audit.py
mamba run -n qom python -m pytest tests -q

# From manuscript/LaTeX/
latexmk -pdf -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2607.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2607.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error Cover_Letter.tex

git diff --check
```

Observed validation:

- rigorous audit: PASS;
- pytest: **19 passed, 1 skipped** in the `qom` environment;
- main manuscript: compiled successfully after the graphics-path correction and figure de-duplication;
- Supporting Information: compiled successfully after SI figure renumbering and removal of the Paper 1 VAE display;
- cover letter: compiled successfully;
- non-fatal underfull boxes remain in dense tables/bibliography and require the final visual review;
- permanent Zenodo DOI: pending.

## Submission boundary

The manuscript reports computational prioritization only. It does not establish biological polypharmacology, target engagement, clinical efficacy, resistance circumvention, or converged mutant-state free energies. The Set-C pilot is secondary, single-replicate and limited to two candidates. The parent-study and Set-C pilot ligand parameterizations differ and must not be compared quantitatively across cohorts.


## Current package hashes

- `Polypharmacology_MD_Validation_V2607.tex` — `b79b2aa1a98e980df9b3ee6582ec4c5afc739467b93dad8ca2aec063c0745cb8`
- `Polypharmacology_MD_Validation_V2607.pdf` — `0fdc779b0ca0e46a9bbf9bae173c91f6cccd43cfd2e4cfc23cafc558cc0d483f`
- `Polypharmacology_MD_Validation_SM_V2607.tex` — `e0826bd443ba9e0f80cde5c300034c55c14a28088f3aa40036e6369c953009c0`
- `Polypharmacology_MD_Validation_SM_V2607.pdf` — `51235e022fa1a3229482572760a54b1b550169b49f5eb84cad714eba749ccf6e`
- `Table_S11_RRS_Threshold_Sensitivity.tex` — `ee374838b421a214c40e3d661f3770f9150231faeeb5660e7b25013cdd0a075a`
- `Table_S12_RRS_By_Target.tex` — `2d29c29d05f59fc06839ac37c11be9293066e29807a0d27f35e0ef7c47ccc40e`
