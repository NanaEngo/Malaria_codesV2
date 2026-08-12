# P5 prose audit — 12 August 2026

## Verdict

The canonical P5 manuscript is written as a scientific research article with IMRAD structure, explicit estimands, reproducible split definitions, and bounded interpretation. The revision removed remaining report-like framing without changing the numerical results or the audit conclusions.

## Revisions applied

- Replaced the promotional/question-led title with a neutral benchmark title: **“Scaffold-controlled benchmarking of graph, transformer, and topological representations for antimalarial activity prediction.”**
- Recast the abstract from a rhetorical question into an objective–method–result–interpretation structure.
- Replaced the standalone “Contribution” and “Highlights” wording with claims about the study’s estimands and design.
- Removed the internal “same research programme” framing from the Introduction.
- Replaced “evaluation question,” “verdict,” and hypothesis-report headings with descriptive scientific section titles.
- Recast reproducibility as a result of the experimental design rather than as a project checkpoint.
- Reframed the LISH analysis as an orthogonal phenotype-only benchmark, with explicit non-comparability to molecular ROC-AUC results.
- Replaced checkpoint language with validation-optimal epoch selection in Results, captions, and Methods.
- Rewrote Discussion and Conclusion transitions to interpret evidence rather than enumerate project actions.
- Aligned the Journal of Cheminformatics cover letter with the new title and bounded benchmark framing.

## Evidence preserved

- Canonical panel: 19,836 molecules.
- Scaffold ECFP4-RF AUC: 0.8300.
- Scaffold GIN-TFP/TNE/GIN/ChemBERTa AUCs: 0.8138/0.8090/0.8047/0.7867.
- Corrected paired tests and BH-FDR interpretation.
- External molecule-disjoint ChEMBL transfer analysis.
- LISH phenotype-only reference and its non-comparability boundary.
- TFP/TNE salience as descriptive projection-weight evidence, not causal attribution.

## Remaining scientific boundaries

The article does not claim that GNNs or Transformers universally underperform, that topological salience proves feature necessity, that LISH MoA labels establish causal target engagement, or that computational rankings replace experimental activity measurements.

## Validation

After the prose revision, the manuscript and cover letter compile without fatal errors or unresolved references/citations. Figures and tables remain referenced by the canonical source. Final author review and package/deposit checks remain separate from the scientific prose audit.
