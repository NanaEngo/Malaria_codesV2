# P3 — Project Tracking

## Status
- Current phase: 10 (Final Pre-Submission Audit) — GATE PASSED (conditional); fixes applied 2026-07-28
- Current section: READY for submission conditional on 3 author-owned HOLDs (H1 ΔAUC footnote, H5 publish Zenodo, H6 Paper-1 DOI) + L6 q_cadd page verify
- Last updated: 2026-07-28
- Model in use: claude-opus-4-8
- Active CLIs: Claude Code only (external CLIs not detected this session)
- skill_checksum: c65634e86b24011d0dbd1c238f6243000fe37b9d14d74c6951807d9493b6f75b

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
- [ ] (Optional) Phase 10 final pre-submission audit — after CRITICAL fixes applied

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
| PHASE10-FIX | 2026-07-28 | fixes applied | ALL 4 CRITICAL + 3 HIGH FAIL RESOLVED. C1: kept 0.842 (BMAD_Q1-canonical n=19849) + provenance note (SM n=1000→5000 typo fixed). C2+C4: unified IQPEmbedding, TA 0.684→0.543 (deposited), Algorithm 1 rewritten in main+SM. C3: PHCO unified 0.943 + baseline/dev explanation. H2: 5 SM dup labels→SM-*. M1: SM cohort 20→17 + Paper-1→Paper-2 cite. H3: cover letter→Temgoua+main title. H4: +5 declarations (CRediT/Funding/Ethics/Consent/AI-use [ADD] placeholders). Recompile clean: 0 undefined/0 multiply-defined/0 errors, anti-AI=0. READY conditional on H1/H5/H6 HOLDs + L6. | final-audit.md updated |

## Missing Inputs / Resolved
- [RESOLVED] H₁-RRS canonical ρ = 0.312 (H1_count, p=0.006, n=77) per p3_h1_rrs_correlation_final.csv; 0.916 in no CSV; drop n=14 pilot (A-C1)
- [RESOLVED] Tartarus labels: 1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT (CSV); SM L573 + p3_rrs_expansion.py TARGET_MAP wrong (A-C4)
- [RESOLVED] Zenodo DOI 10.5281/zenodo.19608875 — insert in main L548; deposit missing p3_polypharm_tfp_rrs.csv; complete upload (A-H9/C-EC15)
- [OPEN] 20 leads vs n=14 — still unexplained (A-M1)
- [OPEN] Wesołowski et al., 2025 — no bibkey; add entry or remove citation (D)
- [OPEN] J. Cheminformatics template + abstract/length requirements — confirm before submission (D)
- [OPEN follow-up analysis] partial-correlate H₁ persistence vs RRS controlling for MW/ring count/H₀/Fsp³ (E-2)
- [OPEN follow-up analysis] external ChEMBL/DrugBank generalization test (E-5)
- [BLOCKING] headline ECFP4 0.868/Hybrid 0.842 — no deposited CSV reproduces (deposited 0.819/0.746); deposit reproducing run OR correct headline (A-C2/C-EC10)

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

## File Map
- manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex — main (565 lines)
- manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex — SM (686 lines)
- manuscript/LaTeX/Bibliography_Paper3.bib — references (629 lines)
- manuscript/LaTeX/Graphics/ — 8 figures
- scripts/ — 40 analysis scripts
- results/ — 45 CSVs (figures/, p3_chembl_validation/, p3_effect_sizes/, p3_physical_validation/, p3_rrs_expansion/)
- outputs/critical-reviews/ — review-plan.md + per-pass review files
- P3_ADVERSARIAL_AUDIT_MITIGATION.md, P3_SUBMISSION_ROADMAP_85PCT.md, P3_Stategic_85PA.md, P3_ZENODO_DEPOSIT_MANIFEST.json, README.md — existing planning docs
