# Project2 scripts

Run commands from `Project2_Polypharmacology_MD_ValidationV2607/`. The
canonical computational audit is deterministic and fail-closed on cohort
identity.

## Canonical metric audit

```bash
mamba run -n qom python scripts/p2_rigorous_audit.py
```

`p2_rigorous_audit.py` re-analyses the committed candidate-selection, docking,
ACSI, and PNS tables. It does not launch docking, MD, or network retrieval. It
writes the RRS target-coverage records, mutually exclusive class labels,
permutation/bootstrap cross-metric audit, PNS-imputation sensitivity, and a
provenance manifest.

The primary RRS estimand is the complete two-target PfDHFR/PfCRT panel. The
five candidates with only an eligible PfCRT WT denominator are retained as a
coverage-limited sensitivity analysis. A*/A uses the weakest eligible WT score
for the potency discriminator; Class D means no available mutant reaches 80%.

## Active analysis and figure scripts

- `md_calculate_rrs_acsi_pns.py` — production entry point for canonical RRS,
  ACSI, and PNS outputs; the canonical Set-C path delegates RRS generation to
  `p2_rigorous_audit.py`.
- `p2_acsi_weight_sensitivity.py` — candidate-cohort ACSI perturbation audit.
- `generate_radar_plots.py` — target-specific RRS radar figure.
- `generate_sm_figures.py` — supplementary figure generation.
- `generate_md_dock_rrs_scatter.py` — secondary Set-C MD-RRS versus docking-RRS
  scatter figure.
- `p2_setc_md_workflow.py`, `p2_setc_trajectory_qc.py`,
  `p2_setc_mmgbsa_aggregate.py` — secondary Set-C pilot workflow and QC.
- `p2_setc_mmgbsa_fix_pbc.py` — documented PBC-whole reruns for the two
  affected pilot systems.

The parent-study MD scripts and Set-C pilot scripts are separate from the
17-candidate docking estimand. Their outputs must not be silently merged into
`c_rrs_classification.csv`.

## Verification

```bash
mamba run -n qom python -m pytest tests -q
```

The tests validate manifests and machine-readable outputs without launching
expensive GROMACS or MM-GBSA calculations. All generated claims should retain
relative paths and source hashes; absolute workstation paths are not suitable
for manuscript provenance.

## Environment and external computation

The metric audit requires the project environment with Python, pandas, NumPy,
SciPy, and RDKit. Molecular dynamics additionally requires the documented
GROMACS/gmx_MMPBSA environment and is not part of the fast audit command.
Large trajectories are not required to reproduce the summary tables included
in the manuscript.
