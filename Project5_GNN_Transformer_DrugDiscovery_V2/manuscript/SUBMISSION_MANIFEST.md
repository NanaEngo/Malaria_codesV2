# Submission Manifest — P5

**Journal:** Journal of Cheminformatics (Springer)
**Pages:** main 14 p. / cover 1 p. — no SM (none referenced), both counts from `pdfinfo` (verified 19/08/2026)
**Status:** Manuscript compiles clean; external ChEMBL CHEMBL364 validation and leak audit complete. Two provenance items open — see Open items below.
**Generated:** 2026-08-19 20:39 UTC

## File inventory (SHA-256)

All five rows recomputed in a single pass with `stat -c%s` and `sha256sum` against the
artifacts present at the Generated timestamp above.

| File | Size (B) | SHA-256 |
|---|---|---|
| P5_manuscript_V2608.tex | 40663 | `40f79b24cb10ad70997855d0ca2372102e0c8e7fd9f1f66ee813e1109d9a4e23` |
| P5_manuscript_V2608.pdf | 852244 | `61bb3c3deec033a67068e6544e6d559117e6180fa61630a734937e0cd90095c5` |
| Cover_Letter_P5_JCAMD.tex | 3838 | `b60f092dbebd75e5b2abb4c5745877e9869a77660e8a76e5b899b4e3cbeb82d9` |
| Cover_Letter_P5_JCAMD.pdf | 90120 | `d08fa6df99987dec3137312439bc76805cce15569bd77672a952a1b47dd797fe` |
| Bibliography_P5.bib | 11038 | `1902045dcb7fc53203430bab4598263bb1c9176dc0bc4e03acc302af078f4f50` |

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
- No SM file needed — no supplementary references in main.
- Manuscript compile verified at the Generated timestamp: `latexmk -g -pdf
  -interaction=nonstopmode -halt-on-error` exit 0, no `^!` lines, 0 undefined references,
  14 pages. `pdftotext | grep -c 'Bemis'` returns 4, so the scaffold reference resolved in
  the compiled output rather than only in the source.

## Open items (must close before submission)

1. **Stale label in a released artifact.** `results/p5_public_malaria_report.json` still
   carries `"dataset": "MoleculeNet malaria"`, a leftover from the abandoned MoleculeNet
   attempt. The numbers in that file are from CHEMBL364 — its `n` (22,267) matches
   `results/p5_public_chembl_malaria_disjoint.csv` exactly (22,268 lines less header), and
   `scripts/p5_public_benchmark.py:295` writes the corrected label. Only the on-disk string
   is wrong. Regenerating it means re-running the benchmark; hand-patching the string
   breaks the file's correspondence to its producing run. Author decision required
   (LED-007-R1).
2. **Untraced p-value.** The scaffold-split paired-*t* p-value is stored rounded to five
   decimals as `0.0`. A tree-wide search for the exact figure returns nothing, so only
   `p < 1e-5` is defensible. The manuscript's `p < 0.0001` is unaffected and the exact
   value must not be quoted (LED-007-R1).

## Prior-revision defect (recorded, not carried forward)

The previous manifest listed `Cover_Letter_P5_JoC.tex` at 4561 B with hash `d642d2b7…`.
That hash is the file's *current* hash, which the current 3775 B file also has — one byte
string cannot have two sizes, so that row was edited by hand rather than generated. Every
row above was produced by command in one pass to remove that class of error.

— **Verified 25 August 2026** (checksums recomputed after R-P5 refinements).
