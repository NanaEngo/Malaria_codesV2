# P1 V8 — Revision Status vs. Reviewer Comments (Audit, updated 2026-09-09)

**Manuscript:** "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis" (JCIM revision, V8)
**Canonical workspace:** `Project1_Chem_space_antimalarial_V7_CorrectedGrid/submission_ACS_P1V8/`
**Audit basis:** `Reviewers_Comments.md`, `REVIEWER_AUDIT_P1_V7.md`, committed V8 sources, this session's recomputations (corrected PfCRT re-dock, pipeline-null control, per-target-median favorability, corrected cross-metric statistics, figure annotations, retrospective antimalarial validation), and the canonical data files.

---

## Executive summary

All reviewer-critical computational items from the committed V8 draft are now **computed
and reflected in the manuscript**:

1. **R2.3 (critical):** all 17 candidates re-docked against the corrected 3D7-like LYS-76
   PfCRT receptor on the cavity-anchored V2 grid (68 runs, all finite). SM S3 (PfCRT column),
   Table 1 (PfCRT RRS with corrected WT denominator), and Table 2 (per-target-median N_fav)
   regenerated from these runs. Corrected WT scores: mean −8.42 (range −12.01 to −6.37).
2. **R2.5 (blocking, now closed):** pipeline-null control computed (corrected WT passed
   through the mutation pipeline without mutation). Null RRS 99.4–100.5 % brackets the
   80 %/70 % class boundaries; K76T 99.1–100.6 %, K76A 99.4–100.4 %. The corrected PfCRT
   channel carries **no detectable K76T/K76A signal** for this panel; PfCRT RRS values near
   100 % are neutral-within-null. Documented in new SM §S12.7.
3. **R2.2:** per-target-median favorability adopted (reviewer's within-target definition);
   Table 2 and N_fav–RRS recomputed (ρ = +0.714, p = 0.0013, permutation p = 0.0019).
4. **R2.1:** cross-metric statistics recomputed on the corrected matrix (PNS–RRS −0.714,
   ACSI–RRS −0.190, RRS–|S_WT| +0.691, N_fav–RRS +0.714); power caveat retained.
5. **R2m.6:** Figure 2 regenerated with ρ/p/n annotations.
6. **R1.2:** retrospective docking of five approved antimalarials **completed** (40 runs;
   `results/retrospective_approved_antimalarials_20260909/`): honest-negative result — the
   framework does not recover the clinical pyrimethamine→PfDHFR or chloroquine→PfCRT K76T
   resistance signatures (RRS ≈ 100 % on both panels, within the pipeline-null spread),
   reported as such in SI Table S6 and M §4.5.

All reviewer-requested computations are complete as of 2026-09-09. Remaining author item:
**R2.6** repository release + Zenodo DOI (author admin; checklist in
`P1_R26_RELEASE_CHECKLIST.md`).

---

## Issue-by-issue status

Legend: ✅ done · 🔧 fixed this session · ⚠️ partial · ❌ open (author/external)

| # | Issue | Status | Where / notes |
|---|-------|:------:|---------------|
| R1.1 | Uneven structural evidence across targets | ✅ | Introduction + Methods §2.3 frame targets as non-equivalent anchors; evidence-class gradient explicit. |
| R1.2 | Retrospective validation vs approved antimalarials | ✅ | 40-run campaign complete (5 drugs × 7 receptor states + 5 WT re-docks): honest-negative — pyrimethamine RRS ≈ 100 % on all four PfDHFR mutants, chloroquine ≈ 99 % on K76T/K76A, within the pipeline-null spread; chloroquine/lumefantrine PfDHFR non-binders. SI Table S6 + M §4.5. |
| R2.1 | N_fav–RRS correlation + power | ✅ | Corrected matrix: ρ=+0.714, p=0.0013, permutation p=0.0019 (significant at α=0.017); power caveat (80 % power only at |ρ|≥0.62) in Discussion §4.1 and SM §S8. |
| R2.2 | −6.0 threshold performs cross-target comparison | ✅ | Per-target-median favorability adopted (PfDHFR −5.92, PfCRT −8.06, PfClpP −6.02, PfATP4 −6.38); Table 2 + N_fav–RRS recomputed; fixed −6.0 retired from text/tables. |
| R2.3 | PfCRT 6UKJ K76T + grid box (CRITICAL) | ✅ | Corrected LYS-76 receptor; cavity-anchored V2 grid (152.99, 151.042, 159.379; 25 Å; exhaustiveness 32); 68-run re-dock complete; SM S3/Table 1/Table 2 regenerated; class counts now 7/4/6/0. |
| R2.4 | DEKOIS worse-than-random + Hany citation | ✅ | Hany et al. 2025 cited and discussed (SM §S12.2); EF@1 %/EF@5 % reported (0.00); **controlled two-arm re-run completed 2026-09-09** (`results/dekois_mtxstripped_20260909/`, 2 × 1239 dockings, exh 32): retained-MTX AUC 0.502 [0.423, 0.586] vs MTX-stripped 0.563 [0.477, 0.646], overlapping CIs, EF@1 % = 0 in both arms → honest-negative, retained-MTX blockade NOT supported; two rows added to the enrichment table, narrative updated in SM §S12.2, main §2.3.1/§4.5, response R2.4. |
| R2.5 | WT/mutant batch-effect null (was blocking) | ✅ | Pipeline-null control computed (SM §S12.7): null 99.4–100.5 %, K76T 99.1–100.6 %, K76A 99.4–100.4 %; max deviation from null 1.2 pp (K76T) / 0.5 pp (K76A); 80 %/70 % boundaries inside null spread; PfCRT channel reported neutral-within-null. >100 % RRS values explained (M §3.4). |
| R2.6 | Repository 404 / no DOI | ❌ | Author action: make repo public, add license + release tag, Zenodo DOI, update Data Availability. |
| R2.7 | PNS/ACSI undefined | ✅ | Methods §2.5 formulas + SM S8 sensitivity table. |
| R2.8 | SI Table S11 contradictions | ✅ | Validation tables rebuilt separating full-ligand vs fragment/cofactor redocking; MMV rows labelled retrodictive. |
| R2.9 | Single seed; PP-15 marginal | ✅ | Five-seed runs disclosed with protocol separation (SI Table S12); seed dispersion < 0.06 kcal/mol bounds N_fav sensitivity; per-target-median margins reported in response letter. |
| R2m.1 | Duplicated paragraph | ✅ | Single occurrence remains. |
| R2m.2 | VAE citation | ✅ | `gomez2018automatic` cited. |
| R2m.3 | 99.3 % framing | ✅ | Reframed as 263,424 → 1,936 calculations with retention caveat. |
| R2m.4 | Notation | ✅ | No ΔG notation; SM §S7 uses |S_Vina| consistently. |
| R2m.5 | S12 numbering; decoy counts | ✅ | Single S12 block (S12.1–S12.7, naturally numbered); decoys 1,200 consistent. |
| R2m.6 | Figure 2 ρ/p/n | ✅ | Regenerated with ρ/p/n annotations from corrected data (PNS–RRS −0.714, p=0.0013; ACSI–RRS −0.190, p=0.465; n=17). |
| R2m.7 | MPO sensitivity deferred | ✅ | SM §S10.2 includes essential numbers (25 perturbations, ρ=0.792 top-1000). |

---

## Computations completed this session (2026-09-09)

All reproducible from versioned scripts and CSVs; none invented or silently repaired.

1. **Corrected PfCRT re-dock (R2.3/R2.5):** `scripts/p1_r23_pfcrt_redock.py` — 17
   candidates × 4 pipeline-identical receptors (corrected LYS-76 WT, K76T, K76A, NULL) on
   the V2 grid. Results: `results/pfcrt_redock_v2grid_20260909/{scores.csv,run.log,receptors/}`.
2. **Revised RRS/classes/N_fav (R2.2/R2.3):** `scripts/p1_r23_rrs_recompute.py` —
   `results/pfcrt_redock_v2grid_20260909/{revised_rrs_and_nfav.csv,revision_summary.json}`.
   Class counts A*: 7, B: 4, C: 6, D: 0; RRS range 73.2–115.6; N_fav–RRS ρ=0.714
   (p=0.0013, perm p=0.0019).
3. **Corrected cross-metric statistics (R2.1):** PNS–RRS −0.714 (p=0.0013); ACSI–RRS −0.190
   (p=0.465); RRS–mean|S_WT| +0.691 (p=0.0021); PNS–mean|S_WT| −0.375 (p=0.138). All on
   the corrected matrix (n=17).
4. **Figure 2 (R2m.6):** `scripts/v8_figure2_annotations.py` → annotated PDF/PNG in
   `submission_ACS_P1V8/Graphics/`; RRS heatmap and target-wise summary regenerated with the
   corrected PfCRT channel.
5. **Retrospective antimalarial validation (R1.2):** `scripts/p1_r12_retrospective.py` —
   40 completed runs (5 approved drugs × 7 receptor states + 5 PfDHFR-WT re-docks after the
   stripped-receptor fix); results in `results/retrospective_approved_antimalarials_20260909/`.

## Manuscript/supplement updates applied this session

- **Main (`P1_V8_main.tex`):** abstract (corrected classes, RRS–|S_WT| ρ=0.691), §3.4
  (PP-11/100 %-ratio paragraph), Table 1 (corrected PfCRT RRS + classes), Table 2 + caption
  (per-target medians, corrected N_fav), §3.6 cross-metric paragraph, §4.1 power paragraph,
  §4.2 top-candidate narrative, §4.5 experimental sequence (five top candidates).
- **SM (`P1_V8_SM.tex`):** S3 matrix (corrected PfCRT column + caption), S7 class counts and
  definitions, S8 cross-metric table + permutation paragraph, S12.4 text, new §S12.7
  (corrected re-dock + pipeline-null control), distribution table regenerated
  (`tables/sm_table_vina_distributions.tex`).

## Cross-referencing refactor (label-driven, 2026-09-09)

All section/table references between the main text, the SM, and the response letter are now
label-driven (`\label` + `\Cref` via `xr` + `cleveref`); no `\section*` and no hard-coded
``Section S#.#'' / ``Table S#'' numbers remain in the main or SM.

- **SM:** all 13 sections and 8 subsections converted from `\section*{S#. ...}` to numbered
  `\section`/`\subsection` with labels `sec:sm_*`; preamble sets `\SectionNumbersOn` +
  `\renewcommand{\thesection}{S\arabic{section}}`. Natural numbering shifted the S12 block
  from S12.0–S12.6 to **S12.1–S12.7** (S10.1/S10.2 unchanged). Internal ``Section S#'' /
  ``Table S#'' refs replaced by `\Cref`; SM now also references the main text
  (`\Cref{M-...}`: Sections 1, 2.2, 2.3, 2.3.1, 2.4, 2.5, 2.6, 3.6, 4.1; Equation (1)).
- **Main:** labels added to all sections/subsections (`sec:intro` … `sec:disc_validation`);
  hard-coded SM refs replaced by `\Cref{SM-...}` (rendering ``Section S12.7'', ``Table S6'',
  ``Tables S10, S11 and S13'' …).
- **Response letter:** `xr` + `cleveref` + `\externaldocument[M-]{P1_V8_main}` +
  `\externaldocument[SM-]{P1_V8_SM}` added; all ~30 ``M \S#.#'' / ``SI \S#.#'' / ``Table S#''
  refs in the authors' text converted to `\Cref` (reviewer quotes kept verbatim).
- **Table-number alignment:** auto-numbered SM tables are S1–S13 (matrix = S1, retrospective =
  S6, distributions = S7, cross-metric = S8, imputation = S9, enrichment = S10, redocking =
  S11, multi-seed = S12, datasets = S13); all text now agrees with the rendered captions.
- **Cover letter:** corrected class counts, RRS range, and cross-metric ρ values.
- **Response letter (`Response_to_Reviewers_P1_V8.tex`):** R2.1/R2.2/R2.3/R2.5/R2.9/R2m.6
  updated with computed results; R1.2/R2.4/R2.6 status explicit.

## Verdict

**READY FOR AUTHOR REVIEW** (all reviewer-critical items computed, including the R2.4
two-arm DEKOIS re-run reported as honest-negative). The only remaining item is author/external:
R2.6 repository release + Zenodo DOI (checklist `P1_R26_RELEASE_CHECKLIST.md`).