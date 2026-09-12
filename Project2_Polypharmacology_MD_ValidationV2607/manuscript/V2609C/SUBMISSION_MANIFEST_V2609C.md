# P2 V2609C — Canonical manuscript manifest

**Target journal:** *Journal of Chemical Information and Modeling* (ACS)  
**Release:** V2609C  
**Status:** `AUTHOR_REVIEW_REQUIRED; SUBMISSION_NOT_AUTHORIZED`  
**Prepared:** 11 September 2026

## Canonical layout

`manuscript/V2609C/` is the only active manuscript source directory. `manuscript/V2609B/` is retained as the historical V2609B release; older variants and generated leftovers are archived under `docs/archive/manuscript/`.

## Source files

- `Polypharmacology_MD_Validation_V2609C.tex` — main manuscript.
- `Polypharmacology_MD_Validation_SM_V2609C.tex` — Supporting Information.
- `Cover_Letter_V2609C.tex` — cover letter.
- `Project2_Polypharmacology_MD_Validation.bib` — bibliography used by the V2609C sources.
- `Secondary_Analyses_SI.tex` — secondary-analysis SI content.
- `Table_RRS_Primary.tex` and `Table_S*.tex` — table inputs.
- `Graphics/` — graphics referenced by the V2609C sources.

The `Bibliography_*.bib`, generated `acs-*.bib`, `.aux`, `.bbl`, `.blg`, `.log`, and PDFs are generated or historical products, not alternate source inputs. A final PDF may be retained only after the source package is frozen and inspected.

## Scientific contract

- Set-C docking: 17 candidates and 136 WT/mutant systems.
- Primary target-balanced RRS: 12 candidates with eligible PfDHFR and PfCRT WT denominators; classes A* = 1, A = 1, B = 4, C = 5, D = 1.
- Available-target sensitivity: 17 candidates; classes A* = 5, A = 1, B = 5, C = 5, D = 1.
- Set-C MD pilot: 16 systems, PP-01/PP-02, one 10 ns production trajectory per system; all passed the declared geometric QC.
- Docking/MD directional comparison: 8 matched mutant rows with both required WT anchors; 7 divergent and 1 concordant.
- Set-C MM-GBSA: 16 canonical endpoint rows (12 mutants + 4 WT baselines), each with 100 stored snapshots; the displayed uncertainty is SD$_{prop}$, not SEM.
- PP-01 PfCRT K76A diagnostic: canonical −35.29, SD$_{prop}$ 1.17, SEM 0.50; second reportable trajectory −27.54, SD$_{prop}$ 1.89, SEM 0.28; absolute difference 7.75 kcal mol⁻¹.
- PP-01 PfCRT WT diagnostic: offset 2.01 kcal mol⁻¹; not applied to the dimensionless MD distance ratio.
- PP-15: two WT feasibility endpoints outside the Set-C MD pilot; no mutant or RRS estimate.
- Full-panel Set-C MD-RRS (17 × 8 = 136 planned comparisons): `NOT_COMPUTED` by design.
- M1 replicated 100 ns campaign: `NOT_COMPUTED / NOT_REPORTABLE / NOT_INTEGRATED`.

## Interpretation boundary

The Set-C candidates and parts of the docking provenance overlap with an upstream library workflow. That workflow is cited only for provenance and methodological context; V2609C does not present an independent validation of it. The 7/8 result is a protocol-local observation that docking-score retention and short-MD local geometry are not interchangeable under the tested protocols. It is not a general docking-failure rate, a pose-accuracy determination, or a biological resistance signal.

The paper's methodological contribution is therefore bounded: it makes the estimand separation explicit, reports operational stability and its limits, and uses the small MD pilot to expose a calibration boundary. It does not establish affinity, residence time, target engagement, mechanism of action, or resistance resilience.

## Reproducible build

Run from the project root:

```bash
cd manuscript/V2609C
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2609C.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2609C.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2609C.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2609C.tex
pdflatex -interaction=nonstopmode -halt-on-error Cover_Letter_V2609C.tex
```

The order establishes the `.aux` files required by `xr` before the final cross-reference passes. Compile with the `malaria_md` environment when available.

## Verification gates

Before author authorization:

1. Confirm no fatal errors, undefined references, undefined citations, or `??` markers.
2. Confirm all Set-C MM-GBSA table values are labelled SD$_{prop}$ and that SEM is used only where supported.
3. Confirm the K76A 7.75 kcal mol⁻¹ diagnostic is separated from the WT diagnostic.
4. Confirm the 7/8 denominator excludes the four PP-02/PfDHFR rows without a docking WT anchor.
5. Confirm no energy offset is applied to the dimensionless MD distance ratio.
6. Confirm `NOT_COMPUTED`, `NOT_REPORTABLE`, and non-independent provenance boundaries remain explicit.
7. Run `conda run -n malaria_md python -m pytest tests/ -q`.
8. Run `git diff --check`.
9. Inspect the final PDFs at normal scale, especially wide SI tables and figures.
10. Stage only approved P2 V2609C files; exclude unrelated P1/P6 changes and scratch outputs.
11. Record final source hashes and the verified archive DOI before submission.

## Current gate

```text
Canonical data = FROZEN
V2609C sources = ACTIVE
V2609B = HISTORICAL ARCHIVE
Set-C MD pilot = SECONDARY, SINGLE-REPLICATE, STRUCTURAL STRESS TEST
Full-panel MD-RRS = NOT_COMPUTED
M1 = NOT_COMPUTED / NOT_REPORTABLE / NOT_INTEGRATED
Submission = AUTHOR REVIEW REQUIRED; NOT AUTHORIZED
```
