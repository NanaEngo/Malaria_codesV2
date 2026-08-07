# P1 V4 final submission audit — 7 August 2026

## Scope

Canonical V4 sources only:

- `manuscript/Antimalarial_Candidates_African_NP_V2607.tex`
- `manuscript/Antimalarial_Candidates_African_NP_V2607_SM.tex`
- `manuscript/Cover_Letter.tex`

No scientific recalculation was performed. The final changes were wording-only: the SM redocking text no longer treats score context as proof of active-site placement, the consensus caption states that an inactive panel is required to quantify false-positive reduction, the main text avoids presenting the score-based MMV comparison as an external decoy benchmark, and 4GM2 is identified as PfClpR rather than PfClpP. The historical parent-MD label 164--PfClpP is retained explicitly as a cohort label with a separate receptor-identity caveat.

## Verification

| Check | Result |
|---|---|
| Main full-project temporary-clone compile | PASS; `pdflatex → bibtex → pdflatex → pdflatex` returned `0,0,0,0` |
| Supplementary full-project temporary-clone compile | PASS; returned `0,0,0,0` |
| Cover-letter compile | PASS; LaTeX returned `0,2,0,0` because the document has no bibliography and BibTeX reports no database; both final LaTeX passes returned `0` |
| Fatal LaTeX errors in final main/SM pass | None reported |
| Undefined-reference diagnostics in final main/SM pass | None reported by the compile audit |
| VAE/clustering N/A tables | Explicitly disclosed; no metric-optimality claim retained |
| SI proxy | Explicitly unvalidated and not a therapeutic-window claim |
| Redocking | 5/5 alignable and 5/10 overall context retained |
| Consensus false-positive claim | Bounded; independent inactive panel required |
| Data availability | Repository URL and pending Zenodo upload stated accurately |
| 4GM2 target identity | V4 text labels 4GM2 as PfClpR; historical 164--PfClpP parent-MD label is explicitly caveated |

## Decision

V4 is **submission-ready pending human author approval and the journal submission action**. This status is conditional on using the freshly compiled canonical sources after the 4GM2 identity correction. V5 remains a separate, non-submission-ready experimental branch.
