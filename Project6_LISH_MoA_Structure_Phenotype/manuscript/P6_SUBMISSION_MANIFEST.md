# P6 submission contents — 30 August 2026

**Target recommendation:** Journal of Computer-Aided Molecular Design (JCAMD), subject to final author verification of current Springer requirements.

**Locked central question:** Under leakage-controlled evaluation of a mapped LISH-MoA cohort, does molecular structure provide transferable information for predicting observed MoA-associated labels beyond a phenotype-only reference, and does combining the two information sources improve out-of-sample prediction? The question is agnostic about improvement and does not imply causal mechanism.

## Rationale
JCAMD is the better fit than JCIM for this manuscript because the central contribution is a computational molecular-modeling benchmark with explicit structure mapping, leakage control, graph/descriptor/transformer comparisons, and reproducibility boundaries. The manuscript does not present a new validated chemical method, a quantum-computing advance, or experimentally anchored molecular design result that would strengthen a JCIM submission.

## Current manuscript
- `P6_manuscript_V2608.tex`
- Main text: complete scientific draft; final author and journal-format checks remain
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

## Computed and audited
- Pooled scaffold calibration for phenotype, ECFP4-RF structure, and late-concat fusion
- Bounded QKS sensitivity for the declared arm pairs
- Paired seed--fold bootstrap variability summaries for scaffold comparisons
- Scaffold-held-out runs for the four GNN/ChemBERTa molecular arms

## Model-unification note (30 Aug 2026)
The ECFP4 baseline and the phenotype+ECFP4 fusion are RandomForest on every split. The scaffold structure arm is the RF run (AUROC 0.53817; the 0.53749 value previously reported was the per-label logistic run and is superseded). SLURM job 15717 (scaffold fusion RF) **completed** 30 Aug ~21:37Z; pooled calibration (fusion ECE 0.0017/MCE 0.2590/Brier 0.0034), QKS (phenotype-vs-fusion τ0.5 0.0329 / Spearman 0.427), and the paired seed-fold uncertainty summaries were re-derived from the RF prediction/fold outputs. The logistic scaffold runs remain on disk for provenance only and are no longer cited.

## Outside the present scope
- Reliability plots, calibration slope/intercept, and per-MoA ECE as inferential endpoints
- Full reference quantum-kernel implementation
- Prospective or experimental biological validation

## Remaining author-controlled checks
1. Verify all references and current JCAMD instructions.
2. Complete authorship, affiliations, declarations, and funding information.
3. Reconcile the final PDF, source, figures, tables, and data/code contents.
4. Keep all comparative statements exploratory unless a future study prespecifies an endpoint, multiplicity procedure, and independent validation cohort.
5. Keep pooled calibration distinct from the archived per-label Brier summaries and prevalence-tertile sensitivity analysis; neither is label-specific biological validation.
