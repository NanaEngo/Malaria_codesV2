# Submission Manifest — P5

**Journal:** Journal of Cheminformatics (Springer)
**Pages:** main 14 p. / cover 1 p. — no SM (none referenced), main count from `pdfinfo` (verified 25/08/2026)
**Status:** Manuscript compiles clean; canonical and extended GNN analyses, external ChEMBL CHEMBL364 validation, fold-level AUPRC, descriptor ablations/permutations, salience-stability audit, split metadata, and chemical-standardization audit are synchronized. Extended ChemBERTa rerun is active under SLURM array 15490 and is not yet integrated. Remaining release checks: ChemBERTa audit, Zenodo deposit, and final author metadata review.
**Generated:** 2026-08-26 UTC (manuscript refinement and compilation)

## File inventory (SHA-256)

The six submission-file rows were recomputed in a single pass with `stat -c%s` and `sha256sum` against the
artifacts present after the final lightweight-robustness update.

| File | Size (B) | SHA-256 |
|---|---|---|
| P5_manuscript_V2608.tex | 45178 | `e66768f826c939c33c9fe4235874b5247c4c916b15cc91ecc04945e0e12f7a52` |
| P5_manuscript_V2608.pdf | 857463 | `21b8bbbda5a6ecc73a7f6c3670468dac2f983173d0ed18b7ba966001d4e8e4b9` |
| Cover_Letter_P5_JCAMD.tex | 3838 | `b60f092dbebd75e5b2abb4c5745877e9869a77660e8a76e5b899b4e3cbeb82d9` |
| Cover_Letter_P5_JCAMD.pdf | 90120 | `ce0af0b47c5b515affcd9d68cd245d6cc16e2862d66769d5f964723c3a18aa48` |
| Bibliography_P5.bib | 10640 | `ed095e4661616d1d4a1d9e9e6839446646844dc516526140b194256488459b72` |
| scientific_audit_20260825.json | 77204 | `61d9869aedf76b0bda0017b3a4a6dba9f676bd3349f948cecb9fd5e50fa18b70` |

A PDF row only means something if the PDF postdates its sources, so that was checked rather
than assumed. `P5_manuscript_V2608.pdf` is newer than both `P5_manuscript_V2608.tex` and
`Bibliography_P5.bib` (`test -nt`, both true at the Generated timestamp), so the compiled
artifact reflects the current source and the current bibliography — including the
Bemis--Murcko scaffold definition and its reference, added after the previous manifest.
Cover-letter rows renamed to `_P5_JCAMD.*` and refreshed; the other
three moved.

## Notes

- External transfer benchmark is the ChEMBL target CHEMBL364 (*P. falciparum*) IC50/EC50
  panel, molecule-disjoint from the canonical panel (n = 22,267). MoleculeNet was attempted
  and abandoned (S3 403, no working TDC loader) and contributes nothing to any reported
  result; earlier revisions of this manifest named it in error.
- Independent replication verification PASS (Δmean −0.00014).
- JCAMD Declarations complete (Availability, Funding, Ethics, Use of AI).
- References: 26 distinct cited references and 26 BibTeX entries; 0 orphan and 0 missing citations.
- Secondary robustness artifacts are documented in `results/lightweight_robustness/README.md` and `results/extended_campaign_20260825/README.md`; they are not substituted for the canonical primary benchmark estimates.
- No SM file needed — no supplementary references in main.
- Manuscript compile verified at the Generated timestamp: `latexmk -g -pdf
  -interaction=nonstopmode -halt-on-error` exit 0, no `^!` lines, 0 undefined references,
  14 pages. `pdftotext | grep -c 'Bemis'` returns 4, so the scaffold reference resolved in
  the compiled output rather than only in the source.

## Extended campaign status

- `results/extended_campaign_20260825/robustness/extended_analysis_summary.json`: `COMPUTED`.
- 25/25 configurations complete; 625 fold--seed records validated; all records have finite AUC/AUPRC.
- Three independent scaffold partitions, GNN descriptor permutations, fold-level AUPRC, and individual salience stability are now computed as secondary robustness analyses.
- ChEMBL threshold sensitivity is `COMPUTED_RF_ONLY` for four prespecified specifications; no full GIN or ChemBERTa threshold rerun is claimed.
- Extended ChemBERTa rerun: SLURM array `15490` submitted with pinned snapshot revision `761d6a18cf99db371e0b43baf3e2d21b3e865a20`; task 0 `RUNNING`, tasks 1–4 `PENDING`, no completed metric yet. No extended ChemBERTa result is authorized for manuscript interpretation until all five partitions pass the 25-record audit.

## Open items (must close before submission)

1. **Zenodo release:** upload the frozen package and verify the reserved DOI.
2. **Author metadata:** confirm ORCID identifiers, affiliations, and final author approval.
3. **External p-value:** the JSON preserves the rounded computational value in
   `paired_t_pvalue_rounded` and the reportable bound in `paired_t_pvalue_reporting`; the
   manuscript reports only the bounded form.

## Prior-revision defect (recorded, not carried forward)

The previous manifest listed `Cover_Letter_P5_JoC.tex` at 4561 B with hash `d642d2b7…`.
That hash is the file's *current* hash, which the current 3775 B file also has — one byte
string cannot have two sizes, so that row was edited by hand rather than generated. Every
row above was produced by command in one pass to remove that class of error.

## Secondary robustness inventory

The following versioned artifacts are part of the scientific audit record and are not replacements for the canonical benchmark:

- `results/lightweight_robustness/README.md`
- `results/lightweight_robustness/p5_lightweight_summary_20260825.json`
- `results/lightweight_robustness/p5_knn_ecfp4_k5_random_baseline.json`
- `results/lightweight_robustness/p5_knn_ecfp4_k5_random_results.csv`
- `results/lightweight_robustness/p5_knn_ecfp4_k5_scaffold_baseline.json`
- `results/lightweight_robustness/p5_knn_ecfp4_k5_scaffold_results.csv`
- `results/lightweight_robustness/p5_logistic_ecfp4_C1_random_baseline.json`
- `results/lightweight_robustness/p5_logistic_ecfp4_C1_random_results.csv`
- `results/lightweight_robustness/p5_logistic_ecfp4_C1_scaffold_baseline.json`
- `results/lightweight_robustness/p5_logistic_ecfp4_C1_scaffold_results.csv`
- `results/lightweight_robustness/p5_replication_stats_rederived.csv`
- `results/lightweight_robustness/p5_replication_stats_rederived.json`

— **Verified 25 August 2026** (checksums recomputed after scientific refinement and lightweight robustness analyses; extended ChemBERTa remains pending).


## Current package hashes

- `P5_manuscript_V2608.tex` — `2b51211aff648c28a2a8993c573dd15fdcc33e01962cb985149028043df96aa2`
- `P5_manuscript_V2608.pdf` — `5b411a3c65d77b5a5fa7d8407c335945d2a6efdb2b6065f0650c24d1f03a8300`
- `Cover_Letter_P5_JCAMD.tex` — `35ab1fed1e4c43ee4b2921cde84ef4f918b5a9dcfe31fa88e5a49e5b02199abd`
- `Cover_Letter_P5_JCAMD.pdf` — `f999508ccda900ae9c94bae1262fcacc8ae9caa681ee8a63e0eadf6f5c3102b1`
- `Bibliography_P5.bib` — `d774573e285cd79bf309385f92820cf0f81207676c118f57f119a7386cfae3b8`
- `Table_P5_Study_Design.tex` — `c5e1a80986476b5f27ed4ad40794b0cabe103cfabe0a59d25557683c4d5c834f`
- `Table_P5_Effect_Summary.tex` — `c20ce8e50ed90349fada871bea9924bcc98a8be0cc1afd36e9a515bbf76482b3`
