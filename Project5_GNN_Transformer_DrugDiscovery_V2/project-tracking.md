# P5 — Project Tracking Spine (Loop State)

**Created:** 2026-08-19  
**Last updated:** 2026-08-19 14:30 UTC  
**Active loop:** L3 beat 2 closed — all nine MEDIUM adjudicated. Next: L4 audit re-run  
**Beat counter:** 6 (L0→L1→L2→L3→L4→L3′)  
**Model in use:** claude-opus-5

---

## Journal Target

**Journal:** Journal of Cheminformatics (Springer Nature)  
**Type:** Original research (benchmark study)  
**Template:** Springer article class (11pt, a4paper)  
**Word limit:** None specified (14 pages current draft, `pdfinfo`)  
**Abstract format:** Structured abstract with Contribution and Keywords  
**Submission requirements:**
- Main manuscript: LaTeX source + compiled PDF
- Cover letter: included (`Cover_Letter_P5_JoC.tex`)
- Figures: PDF/PNG in `results/figures/`
- Data availability: Zenodo DOI reserved (10.5281/zenodo.19608875, upload pending)
- Code availability: GitHub public repository
- Declarations: funding, competing interests, author contributions (all present in V2608)

---

## Central Finding (One Sentence)

Under scaffold-separated evaluation of 19,836 antimalarial natural products, ECFP4-RF (AUC 0.8300) significantly outperforms all learned representations (GIN, GIN-TFP, GIN-TNE, ChemBERTa), defining an honest-negative benchmark where topological fusion adds interpretable signal without closing the predictive gap.

---

## Project Stage & Intake Answers

**A. Starting point:** Complete dataset with finished benchmark results  
**B. Paper type:** Original research — honest-negative benchmark study  
**C. Field:** Computational chemistry / cheminformatics / antimalarial drug discovery  
**D. Methods:** Graph neural networks (GIN), transformer (ChemBERTa), topological data analysis (TFP/TNE), ECFP4 fingerprints, random forest, scaffold splits, DeLong tests, BH-FDR correction  
**E. Software:** PyTorch Geometric 2.8.0, transformers 5.14.1, RDKit, scikit-learn; versions locked in requirements.txt  
**F. Code availability:** Planned GitHub release + scripts in `scripts/`  
**G. Output wanted:** Manuscript finalization → L4 submission package

---

## Current State Summary

### Completed Work
✅ **Benchmark complete:** 5 models × 2 splits × 5 folds × 5 seeds = 250 evaluations  
✅ **External validation:** Public ChEMBL malaria panel (22,267 compounds, molecule-disjoint)  
✅ **Statistical analysis:** Paired DeLong tests, BH-FDR correction  
✅ **Interpretability:** Salience analysis on TFP/TNE fusion heads  
✅ **LISH-MoA phenotype reference:** Orthogonal MoA benchmark (phenotype-only, 3,289 drugs, 206 labels)  
✅ **Manuscript V2608:** LaTeX source complete, compiles without errors, 14 pages  
✅ **Cover letter:** JoC submission letter complete  
✅ **Figures:** Benchmark bar chart, learning curves, salience heatmaps

### Evidence Boundary
- Panel: curated antimalarial natural products (n=19,836), inherited from P3
- Scaffold split: Bemis-Murcko chemical extrapolation, not temporal validation
- Learned models: architecture/hyperparameter dependent
- External validation: public ChEMBL transfer, not prospective clinical data
- LISH-MoA: phenotype-only reference, no structure-MoA claim
- **No claim:** experimental IC50/EC50, target engagement, resistance circumvention

---

## Sprint Plan (Loop-Driven)

| Loop | Status | Gate | Result |
|------|--------|------|--------|
| **L0 SETUP** | ✅ Done | Scaffold + spine + journal recorded | Venv verified, 303 skills, 0 AI patterns baseline |
| **L1 EVIDENCE** | ✅ Done | All 10 ledger entries complete with interpretations | Gate 2 PASS: 10/10 interpretations, 0 missing |
| **L2 DRAFT** | ✅ Done | 19 LED citations inserted, 2 orphans (Methods context) | Gate 4 PASS: All results LED-backed |
| **L3 REVIEW** | ✅ Beat 1 done | 7 verification passes (0 CRITICAL, 3 HIGH, 9 MEDIUM, 4 LOW) | ACCEPT after MINOR REVISION; 3 HIGH fixes applied |
| **L4 SUBMIT** | 🔄 Beat 2 running | Beat-1 PASS voided — it graded a manifest since replaced | Manifest regenerated 20:39 UTC against current artifacts; 17-row audit being written to `outputs/critical-reviews/final-audit.md` |
| **L3′ REVIEW** | ✅ Beat 2 done | All 9 MEDIUM adjudicated: M1/M4/M5/M8 applied, M2/M3/M6/M7/M9 satisfied unedited | 3 blockers left, all author decisions |

---

## Claims–Evidence Matrix

| Claim | Ledger Entry ID | Citation Status | Evidence Type |
|-------|----------------|-----------------|---------------|
| ECFP4-RF scaffold AUC 0.8300 | LED-001 | ✅ | Canonical benchmark JSON |
| GIN scaffold AUC 0.8047 | LED-002 | ✅ | Canonical benchmark JSON |
| GIN-TFP scaffold AUC 0.8138 | LED-003 | ✅ | Canonical benchmark JSON |
| GIN-TNE scaffold AUC 0.8090 | LED-004 | ✅ | Canonical benchmark JSON |
| ChemBERTa scaffold AUC 0.7867 | LED-005 | ✅ | Canonical benchmark JSON |
| All GNN/transformer < ECFP4-RF (BH-FDR) | LED-006 | ✅ | Paired DeLong + BH correction |
| External ECFP4-RF 0.9190 vs GIN 0.8843 | LED-007-R1 | ✅ | Public ChEMBL CHEMBL364 validation (LED-007 superseded, retained for audit — do not cite) |
| TFP persistent-image dominant salience | LED-008 | ✅ | Salience analysis JSON |
| TNE top dimensions 68/43/92/66/165 | LED-009 | ✅ | Salience analysis JSON |
| LISH phenotype log-loss 0.02378, macro-AUROC 0.6435 | LED-010 | ✅ | LISH phenotype-only reference |
| LISH feature counts 772 gene / 100 viability / 3 condition | LED-011 | ✅ | Direct header count of the fitted drug-level table |
| ECFP4-RF random-split AUC (secondary baseline) | LED-012 | ✅ | Canonical benchmark JSON, protocol identical to LED-001-R1 |
| Random-split AUC of all four learned arms, one BH-FDR family | LED-013 | ✅ | Paired *t*-test on 5 per-seed means + joint BH correction |
| ChemBERTa scaffold replication AUC 0.7908 | LED-014 | ✅ | Separate training run, secondary estimate (primary is LED-005) |

---

## Missing Inputs / Blockers

Every canonical result is computed and ledgered. Three items still block submission, two of
which need an author decision rather than more work.

1. **Stale dataset label in a released artifact** (author decision).
   `results/p5_public_malaria_report.json` reads `"dataset": "MoleculeNet malaria"`, left over
   from a MoleculeNet attempt that was abandoned (S3 403, no working TDC loader). The numbers
   are from CHEMBL364: the file's `n` (22,267) matches
   `results/p5_public_chembl_malaria_disjoint.csv` exactly, and
   `scripts/p5_public_benchmark.py:295` writes the corrected label. Only the string is wrong.
   Regenerating the file means re-running the benchmark; hand-patching the string severs the
   file from its producing run. Neither option is mine to pick (LED-007-R1).

2. **Untraced p-value.** The scaffold-split paired-*t* p-value is stored rounded to five
   decimals as `0.0`, and a tree-wide search for the exact figure returns nothing. Only
   `p < 1e-5` is defensible. The manuscript's `p < 0.0001` is unaffected, and the exact value
   must not be quoted anywhere (LED-007-R1).

3. **Misplaced replication paragraph** (author decision, finding S2). A
   `\noindent\textbf{Secondary scaffold-only replication.}` paragraph sits inside
   §Availability, where a reader looking for data-access information will not expect a result.
   Moving it changes section structure, so it waits for the author.

A fourth provenance item is now on the same author-decision footing: the split metadata in
`scripts/p5_make_splits.py:118-119` contradicts the code it describes. Details in the beat-2
review log below.

Also open, ordinary work rather than a blocker: the L4 audit needs a full re-run against the
current manifest, and Zenodo upload for the reserved DOI is still pending. All nine L3 MEDIUM
findings are adjudicated as of beat 2.

---

## File Map (Key Locations)

```
Project5_GNN_Transformer_DrugDiscovery_V2/
├── project-tracking.md                    ← This file (spine)
├── README.md                              ← Project summary
├── requirements.txt                       ← Locked dependencies
├── manuscript/
│   ├── P5_manuscript_V2608.tex           ← Main manuscript (14 pages, compiles clean)
│   ├── P5_manuscript_V2608.pdf           ← Compiled PDF
│   ├── Cover_Letter_P5_JoC.tex           ← Cover letter
│   ├── Bibliography_P5.bib               ← References
│   └── SUBMISSION_MANIFEST.md            ← Submission checklist
├── results/
│   ├── p5_canonical_panel.csv            ← Panel (19,836 molecules)
│   ├── p5_replication_stats.csv          ← Canonical benchmark stats
│   ├── p5_replication_verification.json  ← Replication verification
│   ├── p5_public_chembl_malaria_disjoint.csv  ← External validation (22,267)
│   ├── p5_public_malaria_report.json     ← External validation results
│   ├── figures/                          ← All manuscript figures
│   └── lish_moa/                         ← LISH phenotype-only reference
├── scripts/
│   ├── p5_benchmark.py                   ← Main benchmark runner
│   ├── p5_data.py                        ← Data loading & featurization
│   ├── p5_models.py                      ← Model definitions
│   ├── p5_figure.py                      ← Figure generation
│   ├── p5_interpretability.py            ← Salience analysis
│   └── [30+ analysis scripts]
└── outputs/
    └── analysis/
        └── analysis-ledger.md            ← 12 entries / 11 slots (LED-007 superseded by -R1)
```

---

## Review Log (L3 Findings)

**Session:** 2026-08-19 10:30–10:40 UTC  
**Reviewer:** Independent verification (7 batches via sequential maker≠checker passes)

### Summary by Severity

| Severity | Count | Batches |
|----------|-------|---------|
| CRITICAL | 0 | — |
| HIGH | 3 | Adversarial (2), Peer Review (1) |
| MEDIUM | 9 | Adversarial (3), Edge-Case (1), Peer Review (1), Prose (3), Structure (1) |
| LOW | 4 | Adversarial (2), Peer Review (1), Structure (1) |

**Overall Verdict:** ACCEPT after MINOR REVISION (3 HIGH fixes required)

### HIGH-Priority Fixes (Required)

1. **H1 (Adversarial):** LISH non-comparability warning placement — move explicit statement immediately after LISH numbers (Results §2.2, line ~146)
2. **H2 (Adversarial):** External validation reframing — change from cautionary to strengthening tone (Limitations §4.5, line ~387)
3. **H3 (Peer Review):** GIN architecture details — add activation function, dropout, batch norm to Methods §6.3 (line ~443)

### MEDIUM-Priority Fixes (Recommended)

1. **M1 (Adversarial):** ✅ APPLIED beat 2 — fold-independent init 0.15 inflation claim needs citation/data (Methods §6.4, line ~451)
2. **M2 (Adversarial):** ✅ SATISFIED, no edit — salience caveat-first phrasing already in place: line 140 opens on "examined descriptively", the claim is scoped to "largest raw mean projection-weight magnitude" rather than importance, line 142 states non-necessity and non-causality, and caption line 147 closes "not a causal attribution"
3. **M3 (Adversarial):** ✅ SATISFIED, no edit — Abstract line 42 closes on "a panel-specific, controlled negative benchmark", which is the honest-negative framing in the reviewer's own terms
4. **M4 (Edge-Case):** ✅ APPLIED beat 2 — TNE failure handling in Methods (§6.1, add zero-vector policy)
5. **M5 (Peer Review):** ✅ APPLIED beat 2 — LISH feature counts (Methods §6.5, line ~456: add "772 gene + 100 viability")
6. **M6 (Prose):** ✅ SATISFIED, no edit — TFP block structure stated in three places and arithmetically consistent: Results line 140 gives 33 + 25 + 20 = 78, and caption line 147's ranges 0–32 / 33–57 / 58–77 yield the same three widths
7. **M7 (Prose):** ✅ SATISFIED, no edit — line 83 defines "MoA-associated prediction rather than causal target engagement" and cites `\citep{Trapotsi2022MoA}`
8. **M8 (Prose):** ✅ APPLIED beat 2 — Bemis–Murcko scaffold definition added at Methods line 197 with `\citep{bemis_murcko_1996}`; new `.bib` entry at `Bibliography_P5.bib:266-275`
9. **M9 (Structure):** ✅ SATISFIED, no edit — no redundancy to consolidate. Exactly one scaffold-definition site exists (Methods line 197); Limitations line 173 uses "disjoint" for external-panel compound overlap, a different claim

### Files Written

- `outputs/critical-reviews/review-adversarial.md` (124 lines, detailed findings)
- `outputs/critical-reviews/review-consolidated-batches-2-7.md` (283 lines, Batches 2–7)

---

## Review Log — beat 2 (L3′)

**Session:** 2026-08-19 11:40–12:30 UTC  
**Scope:** apply the three number-bearing MEDIUM findings, then repair the artifacts they invalidated

### Fixes applied to `manuscript/P5_manuscript_V2608.tex`

| Finding | What changed | Backing |
|---|---|---|
| M1 | The 0.15 inflation figure was stated as a result; it is now attributed to the fold-independent-initialization protocol and no longer reads as a measured quantity | No ledger entry supports it as a measurement, so it could not stay a claim |
| M4 | Methods §6.1 now states the zero-vector policy for molecules RDKit cannot parse on the external panel | `scripts/p5_public_benchmark.py:282–290` |
| M5 | Methods §6.5 now gives the LISH feature counts explicitly (772 gene + 100 viability + 3 condition) | LED-011, header count of the fitted drug-level table |

Post-edit gates: `latexmk -pdf -interaction=nonstopmode -halt-on-error` exit 0, no `^!` lines,
13 pages at that point. The spine had said 11, which was stale; it was corrected then, but only
in one of four places, and the M8 edit later took the document to 14. Every page count in this
file and in the manifest now reads 14 and comes from `pdfinfo`, not from memory.
Anti-AI scan on the three edited passages: 0 banned patterns.

### A1 — MoleculeNet naming, resolved where it was mine to resolve

`manuscript/SUBMISSION_MANIFEST.md` named MoleculeNet twice as the external benchmark. That is
generated documentation shipping with the submission, and it was wrong: the external panel is
ChEMBL CHEMBL364. Both mentions are corrected and the abandoned MoleculeNet attempt is now
described as contributing nothing to any reported result. The same wrong string inside
`results/p5_public_malaria_report.json` was **not** touched — that is a released artifact, and
both ways of fixing it cost something the author has to weigh (blocker 1 above).

### Manifest regenerated

`manuscript/SUBMISSION_MANIFEST.md` was rewritten at 12:27 UTC, again at 14:30 UTC, and last at
20:39 UTC, which is the Generated timestamp it now carries — the M8 edit changed the `.tex`,
the `.bib` and the `.pdf` after the first rewrite, so three of the five hashes from 12:27 were
already dead by the time the beat ended. All five size/SHA-256 rows
recomputed in one pass with `stat -c%s` and `sha256sum`, because the previous manifest could not
have been: it listed `Cover_Letter_P5_JoC.tex` at 4561 B carrying hash `d642d2b7…`, which is the
hash of the current 3775 B file. One byte string cannot have two sizes, so that row had been
hand-edited. Recorded in the manifest under "Prior-revision defect". The manifest now also
carries the two open provenance items and an honest Status line in place of the previous
submission-ready claim.

### M2, M3, M6–M9 adjudicated — five needed no edit

Six MEDIUM findings remained after the three number-bearing ones were applied. Auditing them
against the source turned up only one that was actually unsatisfied. That ratio is worth
recording rather than hiding: the beat-1 reviewer was reading section summaries, not line
numbers, so it flagged as missing several guards the manuscript already carried.

| Finding | Verdict | What decided it |
|---|---|---|
| M2 | SATISFIED | Caveat precedes the numbers, not just follows them — line 140 opens on "examined descriptively", line 142 denies necessity and causality, caption line 147 closes "not a causal attribution". The emphasized claim is a weight magnitude, not an importance |
| M3 | SATISFIED | Abstract line 42 closes on "a panel-specific, controlled negative benchmark" |
| M6 | SATISFIED | 33 + 25 + 20 = 78 at line 140; caption ranges 0–32 / 33–57 / 58–77 give the same widths. Consistent, so nothing to explain further |
| M7 | SATISFIED | Line 83 defines the term by contrast with causal target engagement and cites `Trapotsi2022MoA` |
| M8 | **APPLIED** | Only genuine gap. Definition added at Methods line 197 + new `.bib` entry |
| M9 | SATISFIED | One definition site, not two. Line 173's "disjoint" is about compound overlap on the external panel |

M8's gates: `latexmk -g -pdf -interaction=nonstopmode -halt-on-error` exit 0, 0 `^!` lines,
0 undefined references, 14 pages. `.bbl` carries `Bemis and Murcko(1996)]{bemis_murcko_1996}`,
and `pdftotext … | grep -c 'Bemis'` returns 4 — the citation resolved in the compiled output,
not only in the source. Anti-AI scan on line 197: 0 patterns.

Two related repairs in the same beat: the claims matrix now cites LED-007-R1 rather than the
superseded LED-007, and `scripts/p5_make_splits.py:51` now states plainly that val and train
share scaffolds, so early stopping measures optimization on the training chemical distribution
and only the test fold estimates scaffold shift. That docstring was checked against the code it
documents (`p5_make_splits.py:75-83`) and against the manuscript sentence that depends on it.

### Still open at end of beat 2

The L4 audit needs a full re-run: its beat-1 PASS was measured against the manifest that has
since been replaced, and five MEDIUM verdicts have landed since. Three submission blockers
remain, all listed above — two are author decisions, one is a paragraph relocation.

### New author-decision item — split metadata contradicts the split code

`scripts/p5_make_splits.py` lines 118 and 119 both describe validation as
`"val = last 20% of train"`. Neither is what the code does. Both paths shuffle and then take a
**first** slice (`val, train = rest[:n_val], rest[n_val:]` at line 81; the same shape at line
102), and the scaffold path's `n_val` is a fifth of *rest*, not of *train*. The module docstring
adds a third mismatch: line 10 credits `RDKit MurckoDecompose` while line 45 calls
`MurckoScaffold.MurckoScaffoldSmiles`.

None of this changes any reported number — the shuffle makes "first" and "last" equivalent in
distribution, and the scaffold/random split geometry is unaffected. But these three strings are
copied verbatim into the released `results/p5_splits_info.json`, so correcting the source
without re-running severs that artifact from the code that produced it, and re-running
regenerates 50 frozen split files that the whole benchmark is keyed to. Frozen splits are
frozen (AGENTS.md rule). Author decision.

---

## Context Budget Tracking

| Session | Reading (tokens) | Loop | Action |
|---------|------------------|------|--------|
| 2026-08-19 07:41 | ~68k | L0 | Setup + intake + spine creation |
| 2026-08-19 11:40 | ~120k (2 compactions) | L3′ | M1/M4/M5 applied; manifest regenerated; spine reconciled with reality |

---

## Python Environment

**Path:** `/home/tchapet/VirtualEnv/bin/python3` (symlink to system python3)  
**Status:** ✅ Active and verified

---

## Skill Registry

**Primary location:** `~/.claude/skills` (303 skills)  
**Drift detected:** `.opencode/skills/article-writing/SKILL.md` (expected host fork)  
**Canonical checksum:** `3febe7a48ff8133f0f19322792a831b3d2ebefa2df50b4cbbc81f66ee3359a2f`

---

## Notes

1. **Honest-negative framing:** This is a controlled negative result, not a failed study. The contribution is methodological transparency and interpretability.
2. **Evidence boundary maintained:** No claims about experimental potency, target engagement, or resistance circumvention.
3. **LISH-MoA scope:** Phenotype-only reference; no structure-MoA comparison due to missing drug-SMILES mapping.
4. **External validation:** ChEMBL malaria panel reproduces ECFP4-RF > GIN ordering on molecule-disjoint data.
5. **Zenodo status:** DOI reserved (10.5281/zenodo.19608875) but upload not yet complete.

---

*This spine is the single source of truth for loop state. Read this file at every session start.*
