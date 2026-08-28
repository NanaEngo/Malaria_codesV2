# P6 submission manifest — working draft

**Target recommendation:** Journal of Computer-Aided Molecular Design (JCAMD), subject to final author verification of current Springer requirements.

## Rationale
JCAMD is the better fit than JCIM for this manuscript because the central contribution is a computational molecular-modeling benchmark with explicit structure mapping, leakage control, graph/descriptor/transformer comparisons, and reproducibility boundaries. The manuscript does not present a new validated chemical method, a quantum-computing advance, or experimentally anchored molecular design result that would strengthen a JCIM submission.

## Current manuscript
- `P6_manuscript_V2608.tex`
- Main text: complete working draft
- Biological validation: not performed and not claimed
- Author list, affiliations, declarations, funding, conflicts, and final references: require accountable-author completion

## Evidence included
- 3,289 drug-level rows and 206 labels
- 100% mapped coverage
- 1,722 unique molecules and 794 collision groups
- Five seeds × five collision-group folds
- GIN, GIN-TFP, GIN-TNE, and ChemBERTa molecular arms
- Phenotype reference and audited baseline comparisons
- TFP/TNE failure accounting

## Explicitly not computed
- Per-label calibration plots and calibration slope/intercept
- QKS sensitivity
- Scaffold-held-out runs for the four new molecular arms
- Prospective or experimental biological validation

## Submission gate
Do not mark `READY_FOR_SUBMISSION` until:
1. scaffold molecular-arm results are either computed and audited or removed from the claimed analysis scope;
2. paired uncertainty and multiplicity treatment is added for any comparative superiority statement;
3. all references are verified;
4. declarations and authorship are completed;
5. the current JCAMD instructions are checked by the authors;
6. the final PDF, source, figures, tables, and data/code manifest are reconciled.
