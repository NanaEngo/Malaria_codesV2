# Submission Manifest — P5

**Journal:** Journal of Computer-Aided Molecular Design (JCAMD, Springer Nature)
**Implementation audit:** `docs/P5V2_SUGGESTIONS_IMPLEMENTATION_MATRIX_20260827.md`; **JCAMD guideline audit:** `docs/JCIM_GUIDELINE_AUDIT_20260827.md`
**Pages:** main 16 p. / SI 3 p. / cover 1 p. — main count from `pdfinfo` (verified 27/08/2026); SI holds the full LISH protocol, complete metric set, and control-sensitivity table (Section S1) plus the post-hoc calibration metrics table (Section S2: ECE/MCE/Brier, 30 configurations), both referenced from the main text
**Status:** JCIM guideline audit completed locally; manuscript compiles clean; canonical and extended GNN analyses, molecule-disjoint ChEMBL CHEMBL364 transfer analysis, fold-level AUPRC, descriptor ablations/permutations, salience-stability audit, split metadata, chemical-standardization audit, and the extended ChemBERTa completion audit are synchronized. ChemBERTa is a separately versioned secondary analysis. Remaining release checks: final provenance/statistical review, Zenodo deposit, and final author metadata review. Acceptance-probability estimate (55 %, range 45–65 %) documented in `docs/P5V2_ACCEPTANCE_PROBABILITY_20260827.md`.
**Generated:** 2026-08-27 UTC (title, abstract, introduction, cover-letter, and secondary-campaign audit synchronization; final hashes regenerated after compilation).

## File inventory (SHA-256)

The six submission-file rows were recomputed in a single pass with `stat -c%s` and `sha256sum` against the
artifacts present after the final lightweight-robustness update.

| File | Size (B) | SHA-256 |
|---|---|---|
| P5_manuscript_V2608.tex | 44786 | `0a5744f2fa0fe8d0bf6bc3a79aba5347e20364396f0d80882bfa873058b4bf6f` |
| P5_manuscript_V2608.pdf | 888704 | `e04ab59b10e9d7b1271d125a0688e2b0d7fb50e32a4124d2af5ed022f811d4f6` |
| Cover_Letter_P5_JCAMD.tex | 4028 | `442310617707c16198addc8013e4411cb1739bf3b53deabfedbcf88e1b4d8a89` |
| Cover_Letter_P5_JCAMD.pdf | 90084 | `98c43cf50c8123dcb6302b3be03cd6896c194e644c811cd8683419670b80fb39` |
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

- External transfer analysis is the ChEMBL target CHEMBL364 (*P. falciparum*) IC50/EC50
  panel, molecule-disjoint from the canonical panel (n = 22,267). MoleculeNet was attempted
  and abandoned (S3 403, no working TDC loader) and contributes nothing to any reported
  result; earlier revisions of this manifest named it in error.
- Independent ChemBERTa scaffold replication verification PASS (Δmean −0.00014); this is secondary evidence and not a new primary estimate.
- JCAMD Declarations complete (Availability, Funding, Ethics, Use of AI).
- References: 26 distinct cited references and 26 BibTeX entries; 0 orphan and 0 missing citations.
- Secondary robustness artifacts are documented in `results/lightweight_robustness/README.md` and `results/extended_campaign_20260825/README.md`; they are not substituted for the canonical primary benchmark estimates.
- Supporting Information added 27/08/2026: `P5_SI_V2608.tex/.pdf` (3 pages) contains the full LISH phenotype-only protocol and results (Section S1) and the post-hoc calibration metrics (Section S2, Table S2: ECE/MCE/Brier for 25 GNN + 5 ChemBERTa configurations, pooled over 25 fold-seed records); the main text summarizes LISH and points to it (7 Section~S1 references) and cites the calibration table in the extensions paragraph (Section~S2).
- 27/08/2026 refinement: new Discussion subsection "Position relative to recent representation benchmarks" isolates the fold-independent-initialization, topological-fusion, and external-corroboration contributions against Guo & Ding 2026, the 25-embedding benchmark, and Boldini 2024; abstract, contribution statement, and highlights now lead with the fold-independent transformer-initialization protocol.
- Manuscript compile verified at the Generated timestamp: `latexmk -g -pdf
  -interaction=nonstopmode -halt-on-error` exit 0, no `^!` lines, 0 undefined references,
  16 pages (main) + 2 pages (SI) after the 27/08/2026 LISH-to-SI refactor. `pdftotext | grep -c 'Bemis'` returns 4, so the scaffold reference resolved in
  the compiled output rather than only in the source.

## Extended campaign status

- `results/extended_campaign_20260825/robustness/extended_analysis_summary.json`: `COMPUTED`.
- 25/25 configurations complete; 625 fold--seed records validated; all records have finite AUC/AUPRC.
- Three independent scaffold partitions, GNN descriptor permutations, fold-level AUPRC, and individual salience stability are now computed as secondary robustness analyses.
- ChEMBL threshold sensitivity is `COMPUTED_RF_ONLY` for four prespecified specifications; no full GIN or ChemBERTa threshold rerun is claimed.
- Extended ChemBERTa rerun: SLURM array `15490` with pinned snapshot revision `761d6a18cf99db371e0b43baf3e2d21b3e865a20`; all five partitions pass the 25-record audit (125/125 records and prediction files). Results remain separately versioned secondary evidence and do not replace canonical estimates.
- Optional calibration/OOD analyses and new architecture or cluster-split experiments remain `NOT_COMPUTED` and outside the current submission scope.

## Zenodo package status (refreshed 27 August 2026)

The package is built by `scripts/build_zenodo_package.py` into `zenodo_package_20260827/`
(+ `zenodo_package_20260827.tar.gz`) with a machine-readable manifest
`ZENODO_PACKAGE_MANIFEST.json` (schema v2).

- **27 files staged now** (25 base + `p5_benchmark.py` + `p5_sensitivity_gnn.sbatch`), status
  **`PENDING_SENSITIVITY_15617_NOT_UPLOADED`**: the 8 Levier-3 GNN sensitivity outputs
  (`results/p5_GIN_scaffold_*_sens_h64_d02.*` and `_sens_h256_d01.*`) are auto-included as
  soon as SLURM job **15617** produces them (35 files expected at completion).
- **Finalization procedure:** once job 15617 has finished and the fold-level gates are
  clean (25 records per config, finite metrics), re-run
  `python scripts/build_zenodo_package.py` — the manifest flips to
  `READY_FOR_UPLOAD_NOT_UPLOADED` with `sensitivity_files_pending: []`; then refresh the
  tarball, verify the reserved DOI `10.5281/zenodo.19608875`, and upload.
  An automated watcher `scripts/p5_zenodo_finalize.sh` (launched 27/08/2026) performs
  the wait-for-15617 + fold audit + rebuild + tarball refresh chain fail-closed and
  logs to `/tmp/p5_zenodo_finalize.log`; it stages and verifies but never uploads.
- Boundary unchanged: local staging only; no upload or DOI publication performed.

## Open items (must close before submission)

1. **Zenodo release:** upload the frozen package and verify the reserved DOI.
2. **Author metadata:** confirm ORCID identifiers, affiliations, and final author approval.
3. **JCIM portal checks:** confirm article type, required supplementary/graphical elements, and portal-specific formatting fields at submission.
4. **External p-value:** the JSON preserves the rounded computational value in
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

— **Refreshed 27 August 2026** (checksums and completion audit refreshed after scientific refinement and lightweight robustness analyses; extended ChemBERTa complete as secondary evidence).


## Current package hashes

The source was subsequently refined to present the molecular benchmark as primary, the LISH analysis as orthogonal, and robustness analyses separately from limitations. The final compilation and hashes below were regenerated after the severe editorial review.

- `P5_manuscript_V2608.tex` — `2b51211aff648c28a2a8993c573dd15fdcc33e01962cb985149028043df96aa2`
- `P5_manuscript_V2608.pdf` — `5b411a3c65d77b5a5fa7d8407c335945d2a6efdb2b6065f0650c24d1f03a8300`
- `Cover_Letter_P5_JCAMD.tex` — `35ab1fed1e4c43ee4b2921cde84ef4f918b5a9dcfe31fa88e5a49e5b02199abd`
- `Cover_Letter_P5_JCAMD.pdf` — `f999508ccda900ae9c94bae1262fcacc8ae9caa681ee8a63e0eadf6f5c3102b1`
- `Bibliography_P5.bib` — `d774573e285cd79bf309385f92820cf0f81207676c118f57f119a7386cfae3b8`
- `Table_P5_Study_Design.tex` — `c5e1a80986476b5f27ed4ad40794b0cabe103cfabe0a59d25557683c4d5c834f`
- `Table_P5_Effect_Summary.tex` — `c20ce8e50ed90349fada871bea9924bcc98a8be0cc1afd36e9a515bbf76482b3`
