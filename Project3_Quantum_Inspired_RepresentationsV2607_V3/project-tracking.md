# P3 — Project Tracking

## Status
- **Active loop:** L1 EVIDENCE, beat 1 — **returned from L4** on 2026-08-08 after the mandatory
  sibling-folder check found the manuscript's headline cohort undeposited in this worktree.
- **L1 gate: re-established** — ledger entries L121/L122/L123 added; L106 and L112 superseded.
- **L2 draft gate: PASS (verified)** — main 20 pp, SM 20 pp, both
  `fatal=0 undef_ref=0 undef_cite=0`. The previous PASS was recorded against an SM that did
  **not** compile: 44 fatal errors from cross-document `\cref{M-...}`. Fixed 2026-08-08.
- **Manuscript base:** `manuscript/LaTeX/Paper3_Quantum_InspiredV2608.tex` (2026-08-08)
- **Folder head:** this folder (`_V3`). Supersedes the old spine claim that `_V2607` was active.
- Last updated: 2026-08-08
- Model in use: Claude Opus 5

## 2026-08-08 audit — what the sibling check found

The spine said active loop = L4, L1 = PASS, both documents compiling. Three of those were wrong.

| # | Finding | Resolution |
|---|---|---|
| D1 | Six sites quoted MW-only `ρ_partial = −0.018, p = 0.69` with **no deposited source file** in either folder. The only MW-only run was n = 77 (−0.0219 / 0.8507). | Numbers vindicated: `BMAD_Q1_DATA_ANALYSIS_REPORT.md:1770` records them for the n = 494 cohort, and rerunning `p3_h1_rrs_mw_only.py` on that cohort returned **−0.0180 / 0.6903** and MW ancillary **0.5042**, matching the text. Deposited. **L121.** |
| D2 | Manuscript reported n = 494; ledger L106/L112 documented n = 77. The n = 494 outputs lived only in `_V2607`, so this worktree could not reproduce its own headline. | Pulled the n = 494 chain into `_V3`; n = 77 files preserved under `results/superseded_n77/`. **L121 supersedes L106 + L112.** |
| D3 | Co-author results dated 2026-08-07 (`p3_resistance_benchmark.*`, `p3_docking_scores.csv`, newer `p3_rrs_expansion.py`) were in neither the ledger nor the manuscript. | Pulled in and ledgered. **L122**, then **L123** after adding the missing size control. |
| D4 | SM did **not** compile — 44 fatal errors, all from `\cref{M-tab:...}`; `cleveref` cannot consume the `hyperref`-style `\newlabel` records `xr-hyper` imports. Pre-existing (reproduced on untouched `_V2607` files). | Converted the 8 cross-document `\cref{M-...}` to `Table~\ref{M-...}`. SM 44 → 0. |
| D5 | `p3_resistance_benchmark.py:65-66` fits a separate `StandardScaler` on the **test** fold — the same train/test scaling mismatch the manuscript reports fixing as C3 in the QKS benchmark. | Not edited (co-author file). The replacement analysis `p3_resistance_size_baseline.py` fits on train folds only; see the AUC correction below. |
| D6 | Ledger's own "Gate status (L1)" block still reads FAIL while the spine claimed PASS. | Left as-is pending the L1 re-gate; the two must be reconciled before any L4 claim. |

**Number correction, needs author sign-off:** the co-author's headline `H1+H0 AUC = 0.8749`
is an artefact of D5. Same features, same folds, scaler fitted on train only: **0.8937**. The
mismatch was *costing* 0.019 AUC. The four other feature sets in that file (`pers_img`,
`H0_stats`, `H1_stats`, `betti`) carry the same defect and have **not** been re-run — none of
them may be quoted until they are.

**New manuscript content (L123):** Discussion §"Integration with Resistance-Resilient MD
Validation" gained a paragraph, and the SM gained
§"Resistance-resilience classification with a molecular-size control"
(`SM-tab:resistance_benchmark`). Claim as written: four size descriptors alone reach AUC
0.868; topology adds +0.026 (fold-paired *p* = 0.0030); topology+size adds only +0.005 more.
Stated as a small reproducible increment over size, not as a topological explanation of
resistance.

### Open after this beat
- [ ] Re-run the four remaining feature sets in `p3_resistance_benchmark.py` with the scaler fix (D5).
- [ ] ECFP4 arm on the same 2051 compounds — without it, "topology beats size" stands but "topology is the right descriptor" does not (L123 caveat d).
- [ ] Justify or derive the Class A threshold RRS ≥ 8.0 (L122 caveat b).
- [ ] Repeated-CV or scaffold-split significance for the +0.026 increment; 5 shared folds are not independent (L123 caveat a).
- [ ] Reconcile the ledger's "Gate status (L1)" block with the fix queue, then re-gate L1 (D6).
- [ ] Decide whether `p3_docking_scores.csv` (1.1 MB, pulled from `_V2607`) belongs in the Zenodo deposit manifest.
- Python venv: `/home/tchapet/VirtualEnv` (3.12.3) — active
- `skill_checksum`: `3febe7a48ff8133f0f19322792a831b3d2ebefa2df50b4cbbc81f66ee3359a2f`
- Anti-AI scan on V2608: **0 hits**

## Folder decision (2026-08-06)

Three P3 folders now exist under `Malaria_codesV2/`:

| Folder | Role |
|---|---|
| `Project3_..._V2607` | **ACTIVE.** Working folder. Holds V2608, the canonical HPC results, and this spine. |
| `Project3_..._V2607_save` | Frozen backup taken 2026-08-06 before any edit. Byte-identical to V2607 at that moment (`diff -rq` = 0). Do not edit. |
| `Project3_..._V2607_V2` | **SUPERSEDED.** Its manuscript carries pre-HPC numbers (ECFP4 0.949, Hybrid 0.842, TFP 0.877, and `TFP = 0.587` which exists in no file). Keep for history; do not draft from it. |

Rationale: the `_V2` folder had the better bookkeeping (spine + ledger) but the worse science.
V2608 resolves the headline-number problems that `_V2`'s Phase-13 gate was still chasing, so the
bookkeeping was rebuilt here rather than the science backported there.

## Journal Target
- Journal: **Journal of Cheminformatics**
- Template: not yet downloaded — currently generic `article` + natbib. `[ADD: J. Cheminform. template + .bst]`
- Word/abstract limits: `[ADD: confirm from author guidelines]`
- Deadline: none set

## What V2608 already fixed (relative to the superseded `_V2` branch)
- ECFP4 0.949 → **0.948**, TFP 0.877 → **0.876**, Hybrid 0.842 (provisional) → **0.888** (canonical rerun)
- `TFP = 0.587` — the `_V2` Phase-13 CRITICAL — **gone**
- Partial-correlation follow-up (old E-2) **completed**: H₁ collapses under adjustment
- TNE ablation reported honestly (`Δ = +0.011`, i.e. removing TNE helps) in Table 2 and text
- Runtime claim tightened "under 30 min" → "under 15 min", consistent with L104 + L105
- New title: *Topological and tensor-network representations resolve chemical paradoxes in African antimalarial natural products*
- New opening paragraph anchoring on the WHO/artemisinin-resistance problem

## Fix Queue

Ordered by what blocks submission. IDs `F*` are this session's; `C*`/`M*` are audit-v3's.

### CRITICAL — blocks the L1 gate
| ID | Issue | Ledger | Action | Status |
|----|-------|--------|--------|:------:|
| F1 / C1 | Promiscuity: main claims N = 17,011, ρ = −0.248/−0.243/−0.190; only deposited file gives N = 19,900, ρ = −0.159/−0.153/−0.161 | L109 | Clarified in main §3.7 + SM §15.2: N=17,011 is merged complete set (`p3_tda_promiscuity.csv`); exploratory N=19,900 documented in `p3_tartarus_tda_spearman.csv` | ✅ RESOLVED |
| F2 / C2 | `p3_scalability_results.csv`: `pairs = 820` for n = 40 (C(40,2) = 780); `total_time_s` excludes the 11.93 s UMAP step | L110 | Dropped extrapolation; quoted measured canonical runtimes in SM Table S7 (8.1 min TNE, 6.4 min TDA, 817s QK) | ✅ RESOLVED |
| F3 / C3 | SM Table S2 TDA stats stale — 12 values differ from `p3_tda_summary.txt` | L105 | Regenerated Table S2 (`SM-tab:tda_stats`) from `p3_tda_summary.txt` (H0 count 38.0417, H0 min max pers 1.4800, H2 max count 4.0) | ✅ RESOLVED |
| F4 | Abstract "pilot n = 14: ρ = 0.947" traces to no file | L107 | Qualified as H1 total persistence pilot on n=14 in abstract/text, aligned with deposited `p3_polypharm_tfp_rrs.csv` | ✅ RESOLVED |
| **F5** | MW-only partial correlation "p = 0.85" (5 occurrences) | L112 | Reproduced & deposited in `p3_h1_rrs_mw_only.{csv,txt}` (ρ = -0.0219, p = 0.8507) | ✅ RESOLVED |
| F11 | Polypharmacology dependent variable mis-stated | L109 | Corrected text to match 0-3 count | ✅ RESOLVED |
| F12 | SM figure caption asserts "error bars = 95% bootstrap CI" | L109 | Removed unverified CI claim from caption | ✅ RESOLVED |

### HIGH
| ID | Issue | Ledger | Action |
|----|-------|--------|--------|
| F6 | 92.6% / 69.3% carry the paper's framing but are companion-paper results with no local source | L108 | Cite with a table/section pointer into `temgoua2026antimalarial` |
| F7 / M2 | "no statistically significant difference" at p = 0.060 with QK numerically lower is read as parity | L103 | Already partly reworded in V2608; verify no "parity" survives, and never assert equivalence from a df = 4 null |
| F8 / M3 | Paired t-tests on 5 overlapping folds — df = 4, inflated t | L102, L103 | Add bootstrap or DeLong CIs; state the power limitation |
| F9 / M6 | Fusion weights 0.10/0.10/0.80 tuned on an unnamed set | L102 | Name the tuning set (Phase-2 n = 5,000) or use nested CV |
| F10 / M4 | Multiplicity correction applied to 7 classical comparisons only; headline tests uncorrected | L101–L103 | Define one comparison family, correct once |

### MEDIUM — audit-v3 M5, M7–M17 (effect sizes, TNE runtime contradiction, versions/seeds table, SVM-vs-RF Methods mismatch, Zenodo upload, SM structure). Full list in `P3_ADVERSARIAL_AUDIT_V3_20260802.md`.

## Review Log
| Pass | Date | Lens | Verdict | Report |
|------|------|------|---------|--------|
| AUDIT-V3 | 2026-08-02 | co-author full adversarial audit | 3 CRITICAL, 17 MAJOR | `P3_ADVERSARIAL_AUDIT_V3_20260802.md` |
| L1-REANCHOR | 2026-08-06 | ledger rebuilt vs canonical data | GATE FAIL — 2 CRITICAL, 2 unsourced | `outputs/analysis/analysis-ledger.md` |
| L3-B | 2026-08-06 | statistics & inference | 5 CRITICAL, 8 HIGH, 15 MED/LOW | `review-B-statistics.md` |
| L3-C | 2026-08-06 | adversarial peer review | **REJECT in current framing** — 7 CRITICAL | `review-C-adversarial.md` |
| L3-D | 2026-08-06 | editorial / LaTeX / venue fit | Not submittable — 2 CRITICAL, 10 HIGH | `review-D-editorial.md` |
| L3-A | 2026-08-06 | numeric provenance | **NOT RUN** — killed by session limit before writing | — |

### L3-A gap
The numeric-provenance pass never produced a report. Its remit overlaps heavily with the
L1 re-anchor performed the same day (L101–L111), which classified every abstract and table
number against the deposited files. The remaining uncovered part is the **SM-only** numeric
sweep — SM tables not shared with the main text were never systematically checked.
**Re-run pass A against the SM before the L4 audit.**

## Submission-blocking findings from L3 (2026-08-06)

These sit above the F-queue below: each one alone stops submission.

| ID | Finding | Verified how |
|----|---------|--------------|
| **S1** | **The benchmarked TFP is not the TFP the Methods define.** Methods (main:159) define a 12-dimensional vector. `scripts/p3_hybrid_benchmark.py:1276` sets `--tfp-enriched default=True`, building a 78-dim vector. Pass C reproduced both: 78-dim → 0.8759 (the published 0.876); 12-dim as defined → 0.8473. The Limitations paragraph asserts enrichment gave "no improvement … consistent with the canonical 0.876" — false by +0.029, and the canonical number *is* the enriched one | Flag default confirmed at `p3_hybrid_benchmark.py:1276` |
| **S2** | **The complementarity claim was never tested.** Repeated 5× that these descriptors are complementary to ECFP4. The experiment that tests it (ECFP4 + TFP/TNE/QK concatenation) does not exist — `p3_hybrid_benchmark.csv` holds no ECFP4-augmented row. The hybrid contains no ECFP4 at all | Descriptor set enumerated from the CSV |
| **S3** | **No scaffold-aware split on a library that is 69.3 % seed scaffolds.** Plain `StratifiedKFold`; the strings "scaffold split", "GroupKFold", "leakage" appear nowhere in either document. Labels are themselves another ML model's output (Ersilia `eos80ch`), so the ranking may partly measure kinship with the label generator | Pass C; consistent with L101 caveat |
## Folder scheme (renamed 2026-08-06)

| Folder | Role |
|---|---|
| `Project3_..._V2607` | **V1 — co-author's folder, pristine.** Restored from the pre-edit backup. Read-only reference. Diff against it at the start of every session. |
| `Project3_..._V2607_V2` | Superseded (pre-HPC numbers). History only. |
| `Project3_..._V2607_V3` | **ACTIVE.** This folder. |

**Authoritative values file: `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (repo parent). Check every session.**
Now **v51, 180,168 B, 2026-08-02** (was v37/161,509 B). P4 split out at v47 into `P4_DATA_ANALYSIS_REPORT.md`; BMAD_Q1 now covers P1–P3 only.

Cross-checks done 2026-08-06:
- BMAD_Q1's "TFP-Enriched" is **32 features** (SOTA, n = 5,000) with ΔAUC < 0.01 — *not* the canonical 78-feature vector, where enrichment is worth ≈ 0.03. Different descriptors; no conflict. Confirms the L114 finding.
- BMAD_Q1 v51 has **no** scaffold-split or stacking analysis. Its "leakage" entries (M1, ~line 1891) are transductive **UMAP** leakage in `p3_hybrid_benchmark.py:820-824` (job 12696 = 0.8968 excluded, inflated ~+0.05) — a different problem. S2/S3 are new work, not contradictions.

### BMAD_Q1 resolution of the two open items (2026-08-06) — L119, L120

| Item | Verdict from the authoritative file |
|---|---|
| **92.6% / 69.3% provenance** | **Found, and the manuscript misattributes them.** §1.3 line 110 verbatim: *"Scaffold recovery rate: 69.3% (70/101 seed scaffolds recovered in the library of 20,702)."* 92.6% = ECFP4-unreachable fraction on 5,000 generated + 396 seeds. Both are **P1** quantities; BMAD_Q1's scaffold table is for the 65,856-molecule P1 library. The P3 manuscript presents both as properties of its own 19,836 panel — four denominators in play (5,396 / 20,702 / 65,856 / 19,836) |
| **ECFP4 + QK fusion** | **Absent from the authoritative record.** Every hybrid there is TFP+TNE+QK *without* ECFP4 (canonical 0.8876 job 12699; n=5,000 pre-phase 0.8423). The S2 gap is real and still open — needs HPC |

Fixed: the scaffold-split argument now rests on a measurement of the P3 panel itself (632 Murcko / 324 generic), not on borrowed P1 figures.
**Still open — 6 remaining `69.3%` uses** in abstract, Introduction N6, Results §3.7, Figure 3 caption and Conclusion carry the scaffold-paradox framing and need their denominators attached or the claim recast.
Cross-check that held: BMAD_Q1 benzene = 8.41% of 65,856; my largest P3 scaffold = 8.4% of 19,836.
Note: in v51 the manuscript-ready claims are **§5.3**, not §4.3.

### Status 2026-08-06 (second pass): S2 and S3 refined

Ran `scripts/p3_s2s3_refine.py` → `results/p3_s2s3_refine.{csv,txt}`. Ledger L117, L118.

| ID | Refined outcome |
|----|-----------------|
| **S2** | **My earlier "refuted" verdict was wrong.** Stacked ensemble = 0.9502 vs ECFP4 0.9505, Δ = −0.0003, p = 0.20 — **not significant**. Every *concatenation* loses (naive −0.039, block-weighted −0.040, top-k −0.046, ECFP4+TFP −0.018), and the loss scales with fingerprint displacement, so the drop was feature dilution. Correct claim: complementarity **absent**, not refuted. L117 supersedes L115 |
| **S3** | Held under 10× `GroupShuffleSplit`. ECFP4 0.8392 [0.8015, 0.8769]; TFP-78 0.7437; TFP-12 0.6609; TNE 0.6506. Scaffolds 632 Murcko / **324 generic**. CIs wide (±0.024–0.069) — quote intervals. L118 refines L116 |

Manuscript updated accordingly: abstract, Results scaffold paragraph (now CI-based), Discussion, Conclusion, Limitations. Compile clean, main 20 pp / SM 19 pp, 0 errors.

### Status 2026-08-06: S1, S2, S3 ADDRESSED

New experiment: `scripts/p3_s1s3_benchmark.py` → `results/p3_s1s3_benchmark.{csv,txt}`.
RF-200, 5-fold, seed 42, canonical panel (19,836 molecules). Ledger L114–L116.

| ID | Outcome | Manuscript change |
|----|---------|-------------------|
| **S1** | Confirmed and sharpened. Three TFPs exist: 12 (Methods definition) → AUC 0.851; 33 (`--no-tfp-enriched`) → 0.871; 78 (default, benchmarked) → 0.882. **Neither flag setting yields the Methods' 12-dim vector** | Methods §2.3.3 now defines both core and enriched TFP and states the 78-feature vector is what is benchmarked; the false "enrichment showed no improvement" sentence in Limitations replaced with the measured 0.851 vs 0.882 |
| **S2** | **Refuted, not merely untested.** ECFP4+TFP78+TNE = 0.9113 vs ECFP4 alone 0.9505; Δ = −0.0392, t = −19.58, p = 4.0 × 10⁻⁵. Adding the quantum-inspired descriptors makes ECFP4 significantly *worse* | All four complementarity claims rewritten to report the measured result. Discussion now frames the descriptors as diagnostic, not additive, and states explicitly that weighted/stacked fusion was not tested |
| **S3** | Confirmed, large. 19,836 molecules → **629 Bemis–Murcko scaffolds** (largest = 8.4%). GroupKFold drops every descriptor; mean −0.1248. ECFP4 0.951 → 0.842; TFP-12 worst at −0.177 | New "Scaffold-aware evaluation" paragraph in Results; abstract now reports both splits; Limitations opens with the scaffold-diversity constraint |

**Caveat carried into the ledger, not hidden:** S2 tested *naive concatenation* only. Appending 270 dense features to 2048 sparse bits changes RF feature sampling, so part of the drop is dilution. QKS could not be included — no precomputed kernel feature matrix, O(N²) to rebuild. `[ADD: HPC run of ECFP4+TFP+TNE+QK]`

**Replication caveat:** this run gives ECFP4 = 0.9505 against the deposited 0.9475, so it is not bit-exact with the original pipeline. Orderings and gaps are the robust findings; pass C reached the same S1 conclusion from an independent implementation.

### Status 2026-08-06: S4, S5, S6 FIXED

| ID | Fix applied | Verification |
|----|-------------|--------------|
| **S4** | `xr-hyper` → `xr` (SM:41); `\input` repointed from `../../results/...` to a local copy `manuscript/LaTeX/p3_effect_sizes_table.tex` (SM:399) | SM `latexmk` **exit 0**, 0 errors, 0 undefined refs/citations, 19 pp. Main **exit 0**, 0 errors, 0 undefined. Compiled in an isolated LaTeX-only mirror — i.e. the self-contained submission package now builds |
| **S5** | Truncated Methods sentence restored (main:219). Phase-2 values quoted from the deposited rows; the undeposited Phase-1 AUC (0.8534 ± 0.0490) **not** reinstated — replaced by an `[ADD]` placeholder | L113; all three Phase-2 AUCs read directly from `p3_phase2_bd6_*_raw.csv` |
| **S6** | **Not a fabrication after all.** New script `scripts/p3_h1_rrs_mw_only.py` reproduces the claimed values exactly: p = 0.8507 (text says 0.85), H₁–MW ρ = 0.7183 (text says 0.718). Outputs deposited as `results/p3_h1_rrs_mw_only.{txt,csv}`. Manuscript text stands unchanged | L112 supersedes the incorrect L111 |

**Build order matters:** compile SM first, then main, then repeat — main's `SM-*` cross-references need the SM `.aux`. Building main first yields 22 spurious undefined refs.

**Still open from D:** 7 multiply-defined citations in main (unprefixed `\externaldocument` at main:48) — outside S4–S6 scope.

| **S4 (original)** | **The SM does not compile.** `latexmk` exit 12, 44 error lines. Cause: `xr-hyper` (SM:41) + underscored external filename (SM:52). Separately, SM:399 `\input`s a path outside the manuscript tree, so the SM cannot build from a self-contained submission package. The committed SM PDF is not reproducible from committed sources | Compiled in an isolated mirror **and** in a rebuilt relative tree — exit 12 both ways, 44 errors with `results/` present |
| **S5** | **Methods sentence truncated mid-clause** at main:219 — "a grid search evaluated 60 combinations" ends with no period, and Phase 2 of the protocol that fixes every quantum result is never described | Read directly |
| **S6** | **The MW-only partial correlation (p = 0.85) is from an analysis never run** — see L111. The Limitations paragraph rests entirely on it | Script + outputs checked |

## Missing Inputs
- `[ADD]` J. Cheminform. template, `.bst`, abstract/word limits
- `[CITATION NEEDED]` source file for the n = 14 pilot correlation (F4)
- `[CITATION NEEDED]` precise pointer for 92.6% / 69.3% in the companion paper (F6)
- `[ADD]` Zenodo deposit completed and DOI resolving before submission (audit-v3 M10)
- `[ADD]` software versions + seeds table (audit-v3 M8)

## File Map
```
manuscript/LaTeX/
  Paper3_Quantum_InspiredV2608.tex        ← ACTIVE main
  Paper3_Quantum_Inspired_SM_V2608.tex    ← ACTIVE SM
  Paper3_Quantum_InspiredV2607.tex        ← previous, superseded
  Paper3_Quantum_InspiredV2607_refined.tex← intermediate, superseded
  Cover_Letter_P3.tex
  Bibliography_Paper3.bib
results/                                   ← canonical data (see ledger for the 10 anchor files)
outputs/analysis/analysis-ledger.md        ← evidence spine
outputs/critical-reviews/                  ← review reports
P3_ADVERSARIAL_AUDIT_V3_20260802.md        ← co-author audit, 2026-08-02
project-tracking.md                        ← this file
```

## Next
1. Execute the **L4 SUBMIT final submission audit** (`references/audit-checklist.md`).
2. Generate the submission audit report in `outputs/critical-reviews/final-audit.md`.
3. Verify LaTeX submission package readiness for Journal of Cheminformatics.
