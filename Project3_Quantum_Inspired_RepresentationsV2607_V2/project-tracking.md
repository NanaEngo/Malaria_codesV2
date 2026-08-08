# P3 — Project Tracking

## Status
- Current phase: 13 complete (L1 gate check) → Phase 14 next (fix C1 + 5 HIGH)
- Active loop: **L1 EVIDENCE**, beat 1 — re-entered from L3 because the gate found a number conflict
- **L1 gate: FAIL** — 1 CRITICAL, 5 HIGH, 10 MEDIUM. Full matrix: `outputs/analysis/claims-evidence-matrix.md`
- Current section: manuscript compiles clean and reads clean; the blocker is evidence provenance, not prose
- Last updated: 2026-07-31
- Model in use: Opus 5 (1M context)
- Active CLIs: pdflatex / latexmk / git / gh — conda/mamba/singularity absent
- skill_checksum: 3febe7a48ff8133f0f19322792a831b3d2ebefa2df50b4cbbc81f66ee3359a2f (canon: ~/.kiro/skills/article-writing/SKILL.md)
- NOTE: BMAD_Q1_DATA_ANALYSIS_REPORT_V1.md preserved at parent dir (150,772 bytes); current authority is BMAD_Q1_DATA_ANALYSIS_REPORT.md (161,509 bytes, v37, 2026-07-30)

## Environment
- Python venv: /home/tchapet/VirtualEnv (Python 3.12.3) — activated before any Python
- Venv activated: yes (per-call)
- ⚠️ README says `conda activate malaria_md`; venv/conda mismatch — scripts needing conda-only deps flagged [UNVERIFIED-needs-conda]

## Journal Target
- Journal: Journal of Cheminformatics (chosen this session; README also lists Nature Computational Science)
- Template: none downloaded yet — generic `article` + natbib (J. Cheminformatics template to confirm)
- Word limit: TBD (Pass D flagged abstract/DA-statement checks)
- Submission deadline: none set

## Sprint Plan
- [x] Phase 0: startup, scans, anti-AI scan (6 banned patterns found)
- [x] Phase 5 PLAN: read main + SM + prior audit; review-plan.md (18 verified seed findings)
- [x] Phase 5 DELEGATE: 5 parallel review passes (A-E) — all completed (A/D/E retried after 429/502 infra errors)
- [x] Phase 5 VERIFY: all 5 passes checked vs done-criteria — ACCEPTED; consolidated fix queue in outputs/critical-reviews/FIX-QUEUE.md
- [x] Phase 5 follow-up: death-angle [to verify] angles routed through A/B/C CSV verification — 5 resolved, 2 open (partial-correlation H₁ vs size; external generalization) as future analyses
- [x] Phase 10: final pre-submission audit — final-audit.md written; all 4 CRITICAL + 3 HIGH resolved 2026-07-28
- [x] **Phase 11 (2026-07-31): V1→V2 sync complete**
  - [x] BMAD_Q1 v37 delta reviewed (new classical benchmark, ρ=0.312, hybrid provisional, JAX/precompute)
  - [x] Files copied V1→V2: p3_tda_promiscuity.png, p3_tne_parity.png, persistence_diagrams.{png,pdf,json}, p3_classical_benchmark_19849.{py,csv,txt}, p3_generate_persistence_diagrams.py (→scripts/)
  - [x] Paper3_Quantum_InspiredV2607.tex synced: V1 body (lines 1–559) + V2 declarations tail (correct DA, CRediT, Funding, Ethics, Consent, AI-use)
  - [x] Anti-AI fixes: R7-R10 reviewer residue removed (line 118), "robust" ×2 replaced, "We demonstrate" replaced → anti-AI scan = 0
  - [x] Figure 1 replotted: new population-scale 3-panel (H0 KDE / H1 hexbin / H2 scatter, 19,849 mol) — persistence_diagrams.png (481 KB, 300 DPI) + .pdf (152 KB)
  - [x] analysis-ledger.md created: 11 entries (L001–L011) covering all canonical numbers
  - [x] Compile: 24 pages, 0 errors, 0 undefined citations, anti-AI=0
- [x] **Phase 11b (2026-07-31): Second V1→V2 sync pass (scripts, README, reports)**
  - [x] p3_effect_sizes.py: fixed — now loads per-fold AUC from canonical CSV (was buggy hardcoded values with TFP=TNE copy-paste error)
  - [x] p3_physical_validation.py: updated TNE loading logic (improved header detection)
  - [x] p3_hybrid_benchmark.py: updated — JAX/GPU/precompute-kernel additions (best_device(), --precompute-kernel, --device CLI)
  - [x] New sbatch/shell scripts copied: p3_hybrid_5000_gpu.sbatch, p3_hybrid_5000_precompute.sbatch, p3_hybrid_5000.sbatch, p3_hybrid_full_19849.sbatch, p3_hybrid_smoke_fast.sbatch, run_p3_poly_n500.sh, run_p3_poly_n1000.sh
  - [x] reports/ folder created with P3_QKS_JAX_GPU_OPTIMIZATION_REPORT.md
  - [x] README.md synced from V1 (corrected status, corrected results, 5-fold CV, 19,849 primary)
  - [x] p3_polypharm_qks.csv + p3_polypharm_summary.txt copied to results/p3_physical_validation/
  - [x] p3_rrs_expansion.py: V2 version KEPT (V2 has correct TARGET_MAP per BMAD_Q1 §3.8.1; V1 had wrong mapping)
  - [x] Figure 1 confirmed correct: p3_tda_fingerprints.csv identical in V1/V2 (MD5 match); population-scale 3-panel figure is the right implementation of V1 caption
  - [x] Compile: up-to-date, 0 errors, anti-AI=0, 0 undefined citations
- [x] **Phase 12 (2026-07-31): L3 fresh review pass on updated V2 manuscript**
  - [x] `outputs/critical-reviews/review-l3-phase12.md` — verdict 0 CRITICAL / 0 HIGH open, 3 MEDIUM author-owned HOLDs
  - [x] Fixed in that pass: Algorithm 1 `StronglyEntanglingLayers` → `IQPEmbedding` (L189/192/196/197); `tab:qkernel` TA/p corrections
  - [x] Compile: 24 pages, 0 errors, 0 undefined citations, anti-AI = 0
- [x] **Phase 13 (2026-07-31): L1 gate check — claims-evidence matrix vs ledger → GATE FAIL**
  - [x] `outputs/analysis/claims-evidence-matrix.md` written: 16 claim groups BACKED, 15 unmapped
  - [x] Ledger extended L012–L014 (GA discriminator, hyperparameter optimisation, enriched-TFP/SOTA benchmark)
  - [x] Headline-number conflict RESOLVED — see below; stale `[BLOCKING]` line superseded
  - [x] 1 CRITICAL found: **TFP AUC 0.587 (L533, L546) contradicts Table 1 (0.877) and exists in no deposited file**
  - [x] 5 HIGH found: 78-vs-32 enriched features; untraceable Silhouette values; two undeposited Phase-2 hyperparameter runs; `tab:qkernel` p-value column basis; ΔAUC column retained for rows Table 2's caption disowns
- [ ] **Phase 14 (NEXT): close C1 + the 5 HIGH, then re-run the L1 gate**
- [ ] **Phase 15: pull the 3 co-author files that are newer in the V1 folder (see Sibling-Sync Gap below)**

## Critical Review Log
| Pass | Date | Lens | Key findings | Status |
|------|------|------|--------------|--------|
| PLAN | 2026-07-27 | read-through | 18 seed findings (5C/6H/7M) in review-plan.md | done |
| A | 2026-07-27 | numbers→CSV+script | 5 CRITICAL: ρ=0.916 unreproducible (CSV n=77→0.312 count/0.067 pers NS); headline 0.868/0.842 in no CSV (deposited 0.819/0.746); PHCO 0.500 stale (fixed 0.801 in CSV); Tartarus SM labels wrong; 65,856 vs 19,849. +9 HIGH | done ✓ |
| B | 2026-07-27 | adversarial+scientific-CT | 4 CRITICAL: ρ overclaim; quantum-advantage falsified (p≈0.26); "First" claims refuted; H₁→promiscuity refuted by CSV (ρ=−0.002). +5 HIGH | done ✓ |
| C | 2026-07-27 | ScholarEval+edge+repro | ScholarEval ≈4.5/10 (analysis 3, method 4, repro 4 weakest); "TDA<ECFP4" refuted by own balanced SOTA (TFP-12 0.867, PersStats 0.873 > 0.868); headline not reproducible; PHCO contradiction; 8 scripts exist, seed-42, no version pinning. 16 edge cases | done ✓ |
| D | 2026-07-27 | anti-AI+prose+structure+fit | 6 anti-AI hits (robust×4, "we demonstrate"×2) w/ rewrites; SM Discussion dup; R7-R10 residue; Wesołowski missing bib; DOI placeholder; README stale | done ✓ |
| E | 2026-07-27 | death-angle (generative) | 9 angles (POV×3, nail×4, scale×2); 7 [to verify] routed (5 resolved by A/B/C, 2 open) | done ✓ |
| FIX | 2026-07-27 | consolidation | 10 CRITICAL / 17 HIGH / MEDIUM-LOW tail in FIX-QUEUE.md | done ✓ |
| PHASE10 | 2026-07-28 | verification-loop gate | verdict NOT READY: 4 CRITICAL (Hybrid 0.842 not in any CSV; TA 0.684 not in any CSV [CSV=0.543]; PHCO 3-values main/SM/SM 0.943/0.801/0.912; IQP vs StronglyEntanglingLayers circuit mismatch); 3 HIGH FAIL (cover author/title; missing CRediT+Funding+Ethics+AI-use; ); 3 HIGH HOLD (ΔAUC convention; Zenodo reserved; in-press self-cite); 8/9 MEDIUM PASS; references verified (arXiv:2510.14217 real, DOIs resolve) | final-audit.md written |
| PHASE12 | 2026-07-31 | L3 fresh review (post-sync) | 0 CRITICAL / 0 HIGH open; C1 Algorithm 1 IQPEmbedding + C2 tab:qkernel fixed in-pass; 3 MEDIUM author HOLDs | `review-l3-phase12.md` |
| PHASE13 | 2026-07-31 | L1 gate — claims→ledger map | **GATE FAIL.** 1 CRITICAL (TFP 0.587 vs 0.877, in no file), 5 HIGH (78-vs-32 features; untraceable Silhouette; 2 undeposited Phase-2 runs; tab:qkernel p-basis; ΔAUC retained on disowned rows), 10 MEDIUM orphans. Headline 0.868/0.949 conflict resolved — stale BLOCKING line superseded. Ledger L012–L014 added | `claims-evidence-matrix.md` |
| PHASE10-FIX | 2026-07-28 | fixes applied | ALL 4 CRITICAL + 3 HIGH FAIL RESOLVED. C1: kept 0.842 (BMAD_Q1-canonical n=19849) + provenance note (SM n=1000→5000 typo fixed). C2+C4: unified IQPEmbedding, TA 0.684→0.543 (deposited), Algorithm 1 rewritten in main+SM. C3: PHCO unified 0.943 + baseline/dev explanation. H2: 5 SM dup labels→SM-*. M1: SM cohort 20→17 + Paper-1→Paper-2 cite. H3: cover letter→Temgoua+main title. H4: +5 declarations (CRediT/Funding/Ethics/Consent/AI-use [ADD] placeholders). Recompile clean: 0 undefined/0 multiply-defined/0 errors, anti-AI=0. READY conditional on H1/H5/H6 HOLDs + L6. | final-audit.md updated |

## Sibling-Sync Gap (found 2026-07-31, NOT yet closed)

The Phase-11/11b sync pulled the main `.tex`, the bibliography, scripts and figures from the V1 folder, but three files are **newer in `Project3_Quantum_Inspired_RepresentationsV2607` (co-author folder)** than here:

| File | V1 folder (co-author) | V2 folder (here) |
|------|----------------------|------------------|
| `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex` | 2026-07-30 07:17 | 2026-07-28 16:02 |
| `manuscript/LaTeX/Cover_Letter_P3.tex` | 2026-07-29 15:25 | 2026-07-28 11:40 |
| `results/p3_effect_sizes/p3_effect_sizes.csv` | 2026-07-29 15:25 | 2026-07-27 07:58 |

The SM is two days behind. **Do not edit the SM here until this is diffed and merged** — any edit made now overwrites co-author work. Scheduled as Phase 15; deferred by author decision this session.

## V1→V2 Delta Summary (2026-07-31)
**Authority:** BMAD_Q1_DATA_ANALYSIS_REPORT.md (161,509 bytes, v37, 2026-07-30)
**V1 folder:** Project3_Quantum_Inspired_RepresentationsV2607 (parent dir)

Key changes incorporated into V2:
1. Classical benchmark rerun: ECFP4=0.949 (was 0.868), TFP=0.877, TNE=0.722, PHCO=0.897 (bug fixed). Source: p3_classical_benchmark_19849.csv
2. H1-RRS lead: ρ=0.312 (n=77) now lead; pilot ρ=0.947 (n=14) retained as context
3. Figure 1: new 3-panel population-scale (H0 KDE / H1 hexbin / H2 scatter) generated from p3_tda_fingerprints.csv
4. New figures added: p3_tda_promiscuity.png, p3_tne_parity.png
5. QKS polypharmacology: AUC 0.747 vs RBF 0.737 (fully resolved, no longer placeholder)
6. Hybrid benchmark: AUC 0.842 now PROVISIONAL (original run not reproducible; HPC rerun job 12621 in progress)
7. Methods: n=19,849 as primary benchmark clarified throughout (not 65,856)
8. Data availability: DOI 10.5281/zenodo.19608875, GitHub https://github.com/Vital-Sao/Malaria_codes
9. All declarations filled (CRediT, Funding, Ethics, Consent, AI-use)

## Missing Inputs / HOLDs (current as of 2026-07-31)
- [RESOLVED] H₁-RRS canonical ρ = 0.312 (H1_count, p=0.006, n=77) per p3_h1_rrs_correlation_final.csv; 0.916 in no CSV; drop n=14 pilot (A-C1)
- [RESOLVED] Tartarus labels: 1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT (CSV); SM L573 + p3_rrs_expansion.py TARGET_MAP wrong (A-C4)
- [RESOLVED] Zenodo DOI 10.5281/zenodo.19608875 — insert in main L548; deposit missing p3_polypharm_tfp_rrs.csv; complete upload (A-H9/C-EC15)
- [OPEN] 20 leads vs n=14 — still unexplained (A-M1)
- [OPEN] Wesołowski et al., 2025 — no bibkey; add entry or remove citation (D)
- [OPEN] J. Cheminformatics template + abstract/length requirements — confirm before submission (D)
- [OPEN follow-up analysis] partial-correlate H₁ persistence vs RRS controlling for MW/ring count/H₀/Fsp³ (E-2)
- [OPEN follow-up analysis] external ChEMBL/DrugBank generalization test (E-5)
- ~~[BLOCKING] headline ECFP4 0.868/Hybrid 0.842 — no deposited CSV reproduces~~ → **SUPERSEDED 2026-07-31 (Phase 13).** The manuscript now uses ECFP4 = 0.949 everywhere (abstract, Tab.1, Tab.2, Discussion, Conclusion), which `p3_classical_benchmark_19849.csv` reproduces exactly. 0.868 survives only in the `tab:hybrid` caption, correctly named as the superseded baseline. Hybrid 0.842 is still non-reproducible and is now labelled provisional at all 12 occurrences and excluded from every conclusion. Residual issue → H5b below.

### BMAD_Q1 authority reconciliation (2026-07-31, full 2,018-line read) — supersedes the list below where they differ

Authority: `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (161,509 bytes, v37, 2026-07-30). Full detail in `outputs/analysis/claims-evidence-matrix.md` §G.

- **C1 CONFIRMED — take TFP = 0.877.** §3.4 line 841, from `p3_classical_benchmark_19849.py`, n=19,849, RF 200 trees, seed 42. Repeated at lines 20 and 29. The manuscript's 0.587 is in no result file and in no BMAD table (BMAD's only 0.587 is line 550, a logS solubility mean). Rewrite L533 and L546; L533's "poor activity prediction" premise does not survive at 0.877.
- **0.877 vs 0.867 explained, not a defect.** SOTA benchmark uses `class_weight='balanced'` (BMAD L1773/L1777), classical benchmark does not. Quote 0.877 for the headline ranking, 0.867 only inside the class-weighted topological comparison.
- **H1 CONFIRMED — 32 features, not 78.** BMAD L1758, L1771. Note BMAD's E.1 table mixes n=19,849 and n=5,000 rows (its own note, L1785); take both members of any pair from one file.
- **H3 RETRACTED — my error.** All three Phase-2 runs are deposited: `p3_phase2_bd6_nr1_nk30_raw.csv`, `..._nr6_nk30_raw.csv`, `..._nr6_nk20_raw.csv`; BMAD L882–884. The original finding checked `p3_quantum_params_sweep.csv` alone.
- **NEW HIGH — Phase-1 grid misdescribed.** Manuscript L228 says 27 combos, r∈{1,3,6}, k∈{10,20,30}. BMAD L856: 60 combos, r∈{1,2,3,4,6}, k∈{5,10,20,30}, Job 7962, terminated at 50/60. Truncation undisclosed.
- **NEW HIGH — QKS ran on 500 molecules, not 10,000.** BMAD §3.3 L815/L823 and summary L20. Manuscript says 10,000 in five places (Tab.1 fn L323, Tab.2 fn L457, Tab.3 caption L357, §4.5 L351, Methods L238). BMAD's inventory L1741 still says 10,000 — internally inconsistent, but §3.3 is the dated ground-truth section.
- **NEW HIGH — target alignment 0.684 vs 0.543.** BMAD §3.3 L820 gives 0.684 ± 0.021; manuscript and ledger carry 0.543 from `p3_qks_summary.txt`. PHASE10-FIX changed 0.684 → 0.543 on the CSV's authority, against the rule that BMAD outranks intermediate CSVs. **Author ruling needed.**
- **NEW — circuit name.** BMAD §3.3 L817 labels the QKS column "StronglyEntanglingLayers"; Phase 12 unified on `IQPEmbedding` citing §3.4, which is the classical benchmark section and names no circuit.
- **H2 unchanged, now weaker.** No Silhouette, no 0.229, no CH or DB index anywhere in BMAD's 2,018 lines.
- **M9, M10 CLOSED.** BMAD §3.2 L804–811 (19,836 valid / 13 failed / 15.6× / 0.113 / 20 min) and §3.1 L796 (H₀ mean 38, SD 7) confirm them.

**Revised count: 1 CRITICAL, 7 HIGH, 8 MEDIUM.**

### Tartarus regressor conflict — RESOLVED 2026-08-02

Main text L463 said Random Forest; ledger L006 said Ridge. Settled against the source code: `scripts/p3_physical_validation.py` is the only script writing `p3_tne_regression.csv`, and it imports `RandomForestRegressor` (L65) and instantiates it for both the TNE and ECFP4 arms (L239, L252) with `n_estimators=100, random_state=42`. No `Ridge` import exists. **Main text was correct; the ledger was the defective record** — L006 corrected.

Tartarus itself does not settle it: the platform (Nigam et al., NeurIPS 2023, arXiv:2209.12487) supplies the docking objectives for exactly the three targets used here (`get_1syh_score`, `get_6y2f_score`, `get_4lde_score`) but prescribes no regressor for descriptor evaluation — surrogate models appear only in its photovoltaics task. The estimator choice is the authors' and Random Forest is defensible.

Applied to the manuscript: Methods L463 and the Fig.3 caption now state 100 trees, `random_state=42`, 5-fold CV. Previously neither stated the tree count, and the two analyses differ (100 here vs 200 in the classical benchmark, L001).

**[NEW OPEN — docking engine]** Manuscript says QuickVina throughout. Tartarus ships both `qvina` and `smina`, and its documentation describes scoring with smina. Confirm which binary the docking run invoked.

### New from the L1 gate (Phase 13) — all block submission
- **[CRITICAL C1]** TFP AUC **0.587** at L533 and L546 contradicts Table 1 (0.877) and appears in no deposited file. The two real values are 0.877 (`p3_classical_benchmark_19849.csv`) and 0.867 (`p3_sota_benchmark_full.csv`, ledger L014). L533 builds the paper's central "biophysical paradox" argument on 0.587; at 0.877 that framing does not hold. **Author decision required** — rewrite against the real value, or name and deposit the configuration that produced 0.587.
- **[HIGH]** L546 "enriched TFP (78 features)" — the deposited run has 32 (L014). The *conclusion* (no improvement, ΔAUC = −0.0002) is correct; the count and the AUC are not.
- **[HIGH]** Silhouette 0.350 / 0.229 / 0.180 (Tab.4, L353, L503, Methods L234) — no source CSV, no script mentions `silhouette`. CH and DB indices are promised in Methods and never reported.
- **[HIGH]** Phase-2 hyperparameter comparisons d=6,r=6,k=30 (0.8121) and d=6,r=6,k=20 (0.8047) at Methods L228 — `p3_quantum_params_sweep.csv` holds one row only. The 27-combination Phase-1 grid described in Methods is also not deposited (3 rows exist).
- **[HIGH]** `tab:qkernel` Linear row: p = 0.198 under a header reading "p vs. RBF"; ledger L009 records 0.063 vs QK. One of the two is wrong.
- **[HIGH]** ΔAUC column is still printed in Tab.1 and Tab.2 for the provisional rows whose comparisons the Tab.2 caption says were withdrawn (each value = `AUC − 0.949`, the exact cross-baseline subtraction disclaimed).
- **[MEDIUM]** TNE reconstruction error 0.098 vs 0.137, and mode-3 factor matrix vs molecular volume ρ = 0.71 (L503) — no source, no script. Two of the three pillars of the TNE information-retention argument.
- **[MEDIUM]** Unexplained: `p3_classical_benchmark_19849.csv` gives TFP 0.877, `p3_sota_benchmark_full.csv` gives TFP-12 0.867 — same n, same classifier family, same fold count. One run differs in a way nothing records.
- **[MEDIUM ×8]** Orphan groups with a source but no ledger entry: `tab:tda_stats` (48 values), accuracy/F1 columns for QKS + Hybrid + ablations, the "TFP + ECFP4" row, compute timings, dataset provenance, 19,913 Tartarus leads, 19,836/13/99.93 % TDA success, TNE compression arithmetic. Detail in `outputs/analysis/claims-evidence-matrix.md` §D.

## BMAD_Q1 Reconciliation (2026-07-27)
Authoritative values source: BMAD_Q1_DATA_ANALYSIS_REPORT.md (parent dir) — per author, all canonical numbers; cannot recompute. Reconciliation REVERSED several FIX-QUEUE CRITICALs (C1 ρ=0.916 KEEP; C2 0.868/0.842 KEEP; C3→HIGH framing; C9 H1→promiscuity SUPPORTED; H2/H4/H5 + qkernel target_alignment reversed — main matches BMAD_Q1; the divergent CSVs were non-canonical). Real fixes localized to SM wrong values (Tartarus labels L573, R² L575, promiscuity L579, H1-RRS 0.947→0.916 — APPLIED) + main Methods 65,856→19,849, qkernel p 0.312→0.088, remove 0.936/0.105, Zenodo DOI + editorial (anti-AI, SM Discussion cut, R7-R10, citations, README, requirements.txt). Decisions pending (step 1): Hybrid 0.842 vs 0.691; PHCO 0.500 vs 0.801; n=77 H1-RRS expansion keep/remove. See outputs/critical-reviews/BMAD-RECONCILIATION.md.

## Editorial Batch (2026-07-27)
- ✅ **Applied (unambiguous):** 6 anti-AI rewrites (grep now 0); R7–R10 reviewer residue removed (main L118 reframed + L349 de-reviewerised); Wesołowski bare-text → `\citep` (@misc added, later replaced — see 2026-07-28); SM manual `[1]` footnote → `\citep{pytorch_cpp_extension}` (@misc added); README fixed (N1–N4 labels removed, TNE 5.9× real/15.6× padded, 5-fold CV, filename, venv activation, 19,913 docked vs 19,849 benchmark); `requirements.txt` created from script import scan.
- ⏸️ ~~Held (pending the 5 BMAD_Q1 decisions)~~ → all resolved 2026-07-27/28 (see Decisions Batch below).

## Decisions Batch (2026-07-27 → 2026-07-28) — ALL RESOLVED
- ✅ **H6 0.936/0.105:** removed from main (L347/353/501/530) + SM (L596); reframed generically (BMAD §3.3: "removed as unsupported"). Grep = 0.
- ✅ **C10 Zenodo DOI:** main L548 → `10.5281/zenodo.19608875, reserved July 2026` (matches README + SM + BMAD line 43).
- ✅ **Decision #1 (Hybrid 0.842 vs 0.691):** no change — main correctly frames 0.691 as the historical v2 single-scalar, 0.842 as the current 10-component hybrid (BMAD §3.5).
- ✅ **Decision #3 (n=77 H₁-RRS):** no change — main 0.916 (n=14) = §4.3#9; SM 0.361 (n=77) = BMAD July-25 corrected value.
- ✅ **Script `p3_rrs_expansion.py` TARGET_MAP:** swapped 6y2f/4lde labels → `6y2f=PfATP4, 4lde=PfCRT` (BMAD §3.8.1).
- ✅ **PHCO (decision #2):** table L312 `0.500/0.525/0.689/−0.368` → `0.943/0.860/0.883/+0.075` (5-fold RF means from `p3_hybrid_benchmark.csv`); prose L295 + L491 rewritten (removed "ECFP4 highest AUC" + wrong "no discriminative information" conclusion; PHCO 0.943 discriminative after SparseBitVect bug fix). ⚠️ ΔAUC +0.075 uses mean−baseline convention; matched per-fold = −0.017 (flagged).
- ✅ **Wesołowski → Jamali reference:** real ref supplied — Jamali, Cheng, Vargas-Hernández (2026), arXiv:2510.14217. `@misc{wesolowski2025spectral}` → `@misc{jamali2026spectralanalysismolecularfeatures}`; both `\citep` (main L497, SM L594) updated. Full clean rebuild purged stale aux/bbl.
- ✅ **H9 SM duplicated Discussion:** cut "Mechanistic explanation for classical fingerprint superiority" subsection (was SM L589–596); replaced with brief pointer to main (retains Jamali cite). Kept the discriminator experimental-details subsection.
- ✅ **20 leads / n=14 clarity:** main L511 "20 high-confidence polypharmacological leads" → "17 polypharmacological leads...; of these, 14 carried complete RRS classifications and formed the analysis cohort" (BMAD §3.9: 20 = P2 single-target top-20; 17 = polypharm leads; 14 = with complete RRS). ⚠️ changed 20→17; revert if top-20 intended for another reason.
- ✅ **C3 balanced SOTA framing (Option A):** added class-weighted-parity acknowledgment to main Results L295 + Discussion/Limitations L528 — PersStats 0.873 / TFP-12 0.867 vs ECFP4 0.868 (ΔAUC +0.005, ns), sourced from SM `SM-tab:sota`. Qualifies "TDA does not outperform ECFP4" as configuration-dependent.
- **Build status:** both manuscripts compile clean (latexmk, 0 undefined citations, 0 errors); main PDF 1.33 MB, SM PDF 1.68 MB.
- Full per-item detail in `outputs/critical-reviews/BMAD-RECONCILIATION.md` §STATUS + §Remaining items (now all RESOLVED).

## Open follow-ups (RESOLVED 2026-07-28 — see PHASE10-FIX above + final-audit.md "Fixes applied")

**✅ RESOLVED this session (all verified by grep + clean rebuild):**
- C1: 0.842 kept as BMAD_Q1-canonical full-benchmark (n=19849) + provenance note; SM "n=1000"→"n=5000" typo fixed.
- C2+C4: IQPEmbedding unified (main+SM Algorithm 1 rewritten); Table 4 Quantum TA 0.684→0.543 (deposited CSV).
- C3: PHCO unified on 0.943 (main + SM phco_bug baseline/full explanation; SM effect_sizes 0.912 = dev-subset, captioned).
- H2: 5 SM duplicate labels → SM-*; crefs updated; build 0 multiply-defined.
- M1: SM cohort 20→17 + cite Paper-1→Paper-2.
- H3: cover letter → Temgoua (U. Yaoundé I, myke-vital.sao@facsciences-uy1.cm) + main title.
- H4: +5 declarations (Authors' Contributions, Funding, Ethics, Consent, AI-use) with [ADD] placeholders for author to fill.

**⚠️ REMAINING HOLDs (author-owned, no recompute — close before submission):**
- H1 PHCO ΔAUC +0.075 (mean−baseline) vs −0.017 (matched per-fold) — add footnote to Tables 1/3 defining convention.
- H5 Zenodo DOI 10.5281/zenodo.19608875 "reserved" → publish record (or switch all docs to "to be minted upon acceptance").
- ~~H6 temgoua2026antimalarial (Paper 1) in-press, doi pending~~ → RESOLVED: real ChemRxiv DOI supplied (10.26434/chemrxiv.15006402/v2); bib @article→@misc preprint entry, "under consideration at JCIM" noted. Recompile clean.
- L6 q_cadd_2026 pages "54321" looks placeholder — verify against real article.

**✍️ AUTHOR-FILL placeholders added (H4):** CRediT role assignments (Authors' Contributions), Funding bodies/grant numbers, AI-use disclosure wording — review the [ADD] blocks in main before submission.

**Build status post-fix:** main 1.33 MB + SM 1.69 MB compile clean; 0 undefined / 0 multiply-defined / 0 errors / anti-AI=0.

## Prior open follow-ups (kept for history)
- ~~PHCO ΔAUC convention~~ → H1 (still open).
- ~~20→17 cohort change at L511~~ → main + SM both done.
- ~~Zenodo deposit reserved~~ → H5 (still open).
- ~~Optional Phase 10 audit~~ → DONE 2026-07-28 (final-audit.md); fixes applied.

## File Map (updated 2026-07-31)
- manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex — main (610 lines, synced from V1 2026-07-31)
- manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex — SM (686 lines)
- manuscript/LaTeX/Bibliography_Paper3.bib — references (629 lines)
- manuscript/LaTeX/Graphics/ — 11 figures (added: p3_tda_promiscuity.png, p3_tne_parity.png, persistence_diagrams.png [new 3-panel], persistence_diagrams.json)
- scripts/ — 42 analysis scripts (added: p3_classical_benchmark_19849.py, p3_generate_persistence_diagrams.py, p3_plot_persistence_diagrams_population.py)
- results/ — CSVs (added: p3_classical_benchmark_19849.csv, p3_classical_benchmark_19849_summary.txt)
- scripts/p3_replot_figures_v2.py — NEW 2026-08-02; regenerates 5 alternative "v2" figures from deposited CSVs. Originals untouched; author to choose. Run: `/home/tchapet/VirtualEnv/bin/python3 scripts/p3_replot_figures_v2.py`
- manuscript/LaTeX/Graphics/*_v2.{png,pdf} — **ADOPTED 2026-08-02**: main manuscript now renders `persistence_diagrams_v2.pdf` (Fig.1), `p3_tne_regression_v2.png` (Fig.3), `p3_tda_promiscuity_v2.png` (Fig.4), `h1_rrs_class_violin_v2.png` (Fig.5), `p3_ga_discriminator_v2.png` (Fig.6). All five captions rewritten to match what the new panels draw. Originals still on disk and unreferenced — revert by restoring the old paths and captions from git.
  - Label rename: `fig:tne_parity` → `fig:tne_regression` (the panel is a metric comparison, not a parity plot); the single `\cref` at L465 updated.
  - Caption content changes worth re-reading: Fig.1 drops the exemplar annotations (not drawn in v2, see ledger L010); Fig.4 now states that 45 vectorised components were tested and excluded, and that no CIs exist; Fig.5 now says Class~A/B only with the 423 unclassified compounds excluded, replacing the old Class~A-vs-D wording that the data never supported.
  - Build after the swap: 24 pages, 0 errors, 0 undefined references, 0 undefined citations, anti-AI scan 0.
- outputs/analysis/analysis-ledger.md — 14 entries (L001–L014); L012–L014 added 2026-07-31 (Phase 13)
- outputs/analysis/claims-evidence-matrix.md — CREATED 2026-07-31 (Phase 13); claim → ledger-ID map, gate verdict FAIL
- outputs/critical-reviews/review-l3-phase12.md — L3 fresh review, 2026-07-31
- outputs/critical-reviews/ — review files from prior passes
- project-tracking.md — this file
