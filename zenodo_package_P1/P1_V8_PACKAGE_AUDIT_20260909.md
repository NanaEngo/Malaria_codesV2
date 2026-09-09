# P1 V8 Package Audit — 2026-09-09

**Scope:** `submission_ACS_P1V8/` in-flight revision (main, SM, cover letter, tables, response letter)
**Method:** every number in the revised `.tex` cross-checked against the recomputed artifacts
(`results/pfcrt_redock_v2grid_20260909/`, `results/retrospective_approved_antimalarials_20260909/`,
`results/derived/v7_integrated_candidate_metrics.csv`, P2 `docking_mutants.csv`, P2 multiseed summaries).
R2.4 DEKOIS MTX-stripped re-run is **still executing** (retained arm 900/1240); untouched.

---

## 1. Verified: manuscript ⇄ artifact (all pass)

| Check | Scope | Result |
|---|---|---|
| PfCRT corrected WT scores | SM `tab:vina` PfCRT column vs `scores.csv` | 17/17 exact |
| RRS table `M-tab:rrs_main` | class, RRS_mean, K76T, K76A vs `revised_rrs_and_nfav.csv` | 17/17 |
| PfDHFR RRS columns (N51I/C59R/S108N/I164L) | recomputed from P2 `docking_mutants.csv` (RRS=100\|mut\|/\|WT\|) | 48/48 |
| RRS_mean recomputation | mean of all eligible mutant ratios (P2 PfDHFR + corrected PfCRT) | 17/17 |
| Class counts | artifact {A\*:7, B:4, C:6, D:0} vs tex "7/4/6/0" | ✅ |
| RRS range | 73.2–115.6 (artifact min/max) | ✅ |
| wt/mutant scores table | PfCRT WT/K76T/K76A columns vs `scores.csv` | 51/51 |
| Vina distributions (SM) | min/median/mean/max per target + ALL row vs recomputed | exact |
| Per-target medians | PfDHFR −5.92, PfCRT −8.06, PfClpP −6.02, PfATP4 −6.38 | exact |
| N_fav (dual priority table) | vs `N_fav_perTargetMedian` | 17/17 |
| Favorable-target lists | recomputed from per-target-median rule (score ≤ median) | 17/17 |
| Retrospective table | 22/22 RRS values vs `rrs_profiles.csv` (1 dp); non-binder dashes OK | ✅ |
| Cross-metric Spearman | PNS–RRS −0.714/p=0.0013; ACSI–RRS −0.190/p=0.465; RRS–WT +0.691/p=0.0021; PNS–WT −0.375/p=0.138; N_fav–RRS 0.714/p=0.0013 | exact |
| Permutation p | N_fav–RRS 0.0019 (100k) vs `revision_summary.json` | ✅ |
| Null control | K76T 99.1–100.6, K76A 99.4–100.4, null 99.4–100.5; max dev 1.2 pp (K76T) / 0.5 pp (K76A) | exact |
| P2Rank | score 162.66→162.7, p=0.999; pocket center (151.18,152.11,154.09) = 5.69 Å ≈ 5.7 from V2 grid center | ✅ |
| Multi-seed table | PP-15/PP-01 per-seed values vs P2 `multiseed_*_summary.json`; means/SDs hand-verified | exact |
| Companion P2 claims (SM S12) | 312/312 records, bootstrap RRS 100.45 [99.59,101.32], 212/272 = 77.9%, partial ρ=−0.6154 vs raw −0.2098 (n=12) | all in P2 report/artifacts |
| Abstract/cover-letter headlines | −12.01…−4.63 range, 68/68 gate, 99.1–100.6/99.4–100.5, ρ values, class counts | ✅ |
| Main-text score ranges | per-target ranges (SM table) match §3.3 text | ✅ |

## 2. Citations & cross-references

- **Citations:** 34 cited keys, **0 missing** from `Sao_Chim_Space.bib`. 91 entries uncited — the bib is a shared master file; cosmetic only, no action required.
- **Cross-references:** 59 `\ref`/`\Cref` targets across main/SM/cover/tables — **all resolve** (cross-document `SM-`/`M-` prefixes via `xr` verified; labels in `tables/*.tex` included).

## 3. Discrepancy — needs fixing

### R2.9 response letter: margin claim not reproducible
`Response_to_Reviewers_P1_V8.tex` (§R2.9) states:

> "the per-target-median favorability assignments (R2.2) have margins of at least 0.3 kcal/mol for all but three candidate–target pairs"

Direct computation on the corrected matrix gives **20 of 68 pairs** with |score − median| < 0.3 kcal/mol — not 3. Four pairs sit **exactly at** their target median (margin 0.00): PP-05 PfATP4, PP-10 PfClpP, PP-12 PfCRT, PP-13 PfDHFR. The correct statement is 48/68 pairs with margin ≥ 0.3. **Status: FIXED** — `Response_to_Reviewers_P1_V8.tex` §R2.9 now reads "48 of 68 candidate–target pairs at least 0.3 kcal mol⁻¹ from the relevant target median; the remaining 20 pairs lie within 0.3 kcal mol⁻¹, including four that sit exactly at the median…" with the boundary-sensitivity caveat. No other response-letter number failed.

## 4. Observations (author judgment)

1. **PP-01 PfDHFR WT = +7.50 kcal/mol** (P2 panel, positive score). The declared magnitude rule (|S_WT| ≥ 5) treats it as an eligible binder, so PP-01 carries PfDHFR RRS 86–88% and is classified A\*. Consistent with the documented framework, but a positive "WT binder" baseline is worth an explicit author sanity check (the main-matrix PP-01 PfDHFR value is −5.947 under the panel grid; the +7.5 arises under the P2 canonical grid).
2. **Retrospective null comparison** (main §4.5): pyrimethamine PfDHFR RRS 99.7–100.0 is compared to the *PfCRT-channel* null spread 99.4–100.5. Numerically overlapping, but the null is channel-specific; wording is acceptable as-is, flagging for awareness.
3. **SM multiseed caption** correctly discloses the PP-15 PfDHFR protocol gap (−8.59 vs −6.05) and PP-15 PfCRT gap (−7.82 vs −9.81) between the P2 canonical-grid runs and the corrected matrix — good provenance practice.

## 5. Open items (author/external)

| Item | Status | Where |
|---|---|---|
| **R2.4** MTX-stripped DEKOIS re-run | 🔄 running (retained 900/1240, 899 OK — one docking failure fail-closed; stripped arm queued) | see integration map below |
| **R2.6** repo release + Zenodo DOI | ❌ author action (locally-verifiable items confirmed: remote `git@github.com:NanaEngo/Malaria_codesV2.git`, `git diff --check` clean, README.md present, tables 11/11, scripts 6/6, Graphics 5/5, results dirs intact; LICENSE + release tag + DOI remain author-admin) | checklist in response letter + `P1_R26_RELEASE_CHECKLIST.md` (updated 2026-09-09: tables 10/10 → 11/11) |

## 5a. R2.4 integration map (prepared; apply when the run finishes)

The run is internally controlled: both arms dock the same 40 actives + 1200 decoys on the same
P2 canonical PfDHFR grid (center (1.33, −1.733, −23.842), 25 Å box, exhaustiveness 32, seed 42),
differing only in receptor (retained 7F3Y vs MTX-stripped `PfDHFR_WT_receptor.pdbqt`, verified
present: 9075 atoms, 0 MTX residues). Outputs will be `scores_{arm}.csv`, `metrics.csv`, `summary.json`
with ROC-AUC + 95% bootstrap CI, EF@1/5/10%, BEDROC(α=20), PR-AUC — same metrics as the current table.

When `results/dekois_mtxstripped_20260909/metrics.csv` exists, replace the 0.450/0.00/0.00/1.00/0.021/0.034
values (or report the new retained + stripped rows) in these **six** places:

1. `tables/sm_table_enrichment_validation.tex` — row 15 (PfDHFR DEKOIS row) + caption line 7 ("near-random ROC-AUC (0.450)")
2. `P1_V8_SM.tex` §S12.2 (line ~213) — "ROC-AUC of 0.450 [95% CI: 0.367--0.531]" prose + Hany sentence placement
3. `P1_V8_main.tex` §2.4 docking validation (line 70) — "ROC-AUC of \num{0.45} (95% CI \numrange{0.37}{0.53})"
4. `P1_V8_main.tex` §4.5 validation strategy (line 217) — "DEKOIS near-chance result (PfDHFR AUC \num{0.45}, 95% CI \numrange{0.37}{0.53})"
5. `Cover_Letter_P1_V8.tex` (line 43) — "DEKOIS 2.0, PfDHFR ROC-AUC \num{0.45}, reported honestly as near-chance"
6. `Response_to_Reviewers_P1_V8.tex` §R2.4 — resolve the `[TO COMPLETE --- re-run ... report the corrected AUC/EF]` marker
   and the "EF@1% = EF@5% = 0.00" framing with the stripped-arm result; then update `P1_V8_REVISION_STATUS.md` R2.4 row.

Caveat to carry into the write-up: the R2.4 comparison uses the **P2 canonical PfDHFR grid**
(1.33, −1.733, −23.842), which is the NADPH-adjacent grid the manuscript already flags as the reason
for the MTX redocking failure — not the panel grid declared in Methods ((−13.5, −1.8, −8.2), 25 Å).
The retained-vs-stripped contrast is still interpretable (same grid, receptor difference only), but the
stripped-arm AUC should be reported as "on the canonical grid" to stay consistent with the multiseed
table's protocol disclosure. If the stripped arm remains near-chance, the honest-negative framing in the
manuscript stands unchanged; if it improves, only the DEKOIS numbers change (RRS/class/N_fav are unaffected).

## 6. Bottom line

The V8 package is **numerically sound**: every finalized value in the revised main/SM/cover/tables traces to a recomputed artifact, citations and cross-references resolve, and all reviewer-critical items (R2.1–R2.3, R2.5, R2.7–R2.9, R1.2, R2m.1–R2m.7) are implemented. Exactly **one statement needed correction** (R2.9 margin claim — fixed), and the R2.4 results integration is pending compute completion.

## 7. Scientific-writing improvement pass (2026-09-09, skill: scientific-writing)

Applied the evidence-bound writing principles to main text + cover letter. All edits are prose-only; every number verified unchanged (spot-checked ρ/p, RRS range, class counts, per-target medians). Both PDFs rebuilt: 0 errors, 0 undefined refs/citations.

**Main text (`P1_V8_main.tex`):**
1. **§3.5 title contradiction fixed**: "Chemical-space and network descriptors show **weak** correlation with resilience" → "Network position and docking evidence show **selective** correlation with resilience". The old title contradicted the corrected results (three Bonferroni-significant associations) and would have undercut the R2.1 revision.
2. **Removed verbatim power-analysis duplication** (the same redundancy class the R2m.1 reviewer flagged): Results §3.5 now points to Discussion §4.2 (`\Cref{sec:disc_breadth}`) with a one-line summary instead of repeating the full n=17 / 80%-power / |ρ|≥0.62 statement twice.
3. **Verb-strength calibration**: "confirming that the workflow preserved privileged ring systems" → "indicating" (descriptive novelty statistics, not confirmation); "it demonstrates that mutation resilience can be target-specific" → "it illustrates" + dropped editorializing "correctly" (single exploratory case, not a demonstration).
4. Remaining strong verbs audited and retained only where scoped: 68/68 geometric-gate "confirms" (deterministic pass rate), MMV "demonstrates" (benchmark metric, immediately qualified), workflow "demonstrates" (efficiency claim with stated caveats).

**Cover letter (`Cover_Letter_P1_V8.tex`):**
1. **Stale SM stats corrected**: "17 pages, 12 sections, 9 tables" → "22 pages, 13 sections, 14 tables, 2 figures" (verified from the rebuilt SM PDF: S1–S14 tables, Figure S1–S2).
2. **Retrospective boundary check added as enhancement item** (was missing from the pitch despite being a completed reviewer item R1.2): five approved antimalarials, honest-negative result, SI Table S7 reference — the table number verified against the compiled SM.
3. Addressee verified current: Kenneth M. Merz Jr. remains JCIM Editor-in-Chief (ACS page, 2026) — no change needed.

**Verified against artifacts during the pass:** scaffold-similarity means (0.379 vs 0.206) → `p1_v7_chemical_space_coverage_provenance.json` (0.37877 vs 0.20625) ✓; SM table numbering for cover-letter refs (S2–S4 physchem/druglikeness/ADMET; S7 retrospective) ✓; EiC via web ✓.

## 8. Response-to-reviewers refinement pass (2026-09-09, skill: peer-review)

Every quantitative claim in `Response_to_Reviewers_P1_V8.tex` re-verified against artifacts; six substantive fixes applied. PDF rebuilt: 7 pages, 0 errors, 0 undefined refs.

**Fixes applied:**
1. **R1.2 candidate-list mismatch (real inconsistency):** response named *three* top candidates (PP-15, PP-06, PP-11) while the corrected re-dock moved PP-05/PP-13 into the A* 4/4 set — manuscript §4.6 now prioritizes *five* (PP-15, PP-05, PP-06, PP-11, PP-13). Both the prioritization item and the feasibility framing updated to five.
2. **R1.2 removed unsupported claim:** "docked the five approved antimalarials already represented in our pipeline" — the drugs were docked from explicit SMILES for the retrospective, not drawn from the pipeline; softened to match the manuscript's neutral phrasing.
3. **R2.5 old-spread correction:** response said the old PfCRT RRS spread was "80–110%" but the pre-revision table spans **70.4–110.2%** (PP-12 K76T = 70.4 is the minimum); corrected to the exact range.
4. **R2.9 seed-dispersion overclaim fixed:** the response implied the P2-protocol five-seed dispersion ($<0.06$ kcal/mol) directly bounds the corrected single-seed V2-grid N_fav assignments; rewritten to state it is a *scale reference* for that protocol, with the boundary analysis (20 pairs within 0.3 kcal/mol, 4 at median) identifying which assignments are single-seed-sensitive.
5. **Status section deduplicated:** "Completed for this revision:" appeared twice with items (i)–(iv) and (v)–(vi) split; merged into one list of six.
6. **Header NOTE refreshed:** no longer claims the bracketed items depend on the corrected-receptor/null/retrospective computations (all complete); now correctly scoped to R2.4 (run in progress) and R2.6 (author action).

**Re-verified as correct (no change):** R2.1 corrected-matrix ρ/p (0.714/0.0013/perm 0.0019; −0.714/0.0013; +0.691/0.0021); R2.2 per-target medians and retired-cutoff transparency (0.515/0.034); R2.3 grid center (152.99,151.042,159.379), P2Rank 162.7/0.999/5.7 Å, 68 runs all finite, mean −8.42 vs −6.19, class counts 6/5/5/1→7/4/6/0, RRS range 73.2–115.6; R2.4 EF@1/EF@5 = 0.00 + Hany citation; R2.5 null spans (99.4–100.5/99.1–100.6/99.4–100.4), max dev 1.2/0.5 pp, 272→212/272 (77.9%), MM-GBSA 0 weaker/1 tighter/max 5.37, bootstrap 100.45 [99.59,101.32], partial ρ −0.6154 vs −0.2098 (n=12); R2.6 WT/mutant table in SI; R2.7 PNS imputation 0.151 + sensitivity 0.963–1.000; R2.8 redocking RMSDs 1.42/1.78/1.65/1.23; R2m.2 Gómez-Bombarelli ACS Cent. Sci. 2018; R2m.5 decoy count 1,200; R2m.7 MPO ρ=0.792.