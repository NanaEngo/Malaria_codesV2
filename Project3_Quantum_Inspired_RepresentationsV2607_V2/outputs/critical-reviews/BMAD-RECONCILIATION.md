# P3 Fix Queue — BMAD_Q1 Reconciliation (2026-07-27)

**Supersedes** `FIX-QUEUE.md` (which was based on deposited CSVs; several of its CRITICAL findings are REVERSED by the authoritative source).

**Authoritative source (per author):** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (repo parent dir, 1967 lines) contains all canonical calculated values; calculations cannot be redone. §3 = P3 analyses, §4.3 = "Manuscript-Ready Quantitative Claims". The main manuscript largely MATCHES BMAD_Q1; the deposited CSVs the review agents checked were often intermediate/non-canonical runs.

## REVERSED by BMAD_Q1 (main was correct; CSV-based finding was wrong)
- **C1 (ρ=0.916):** BMAD_Q1 §3.9 + §4.3#9 canonize ρ=0.916 (p<0.0001, n=14, H₁ total persistence). Main matches. **KEEP 0.916.** (SM's 0.947 is wrong → fixed to 0.916; the n=77 expansion 0.361 is a separate later analysis not in §3.9 — decision pending.)
- **C2 (headline 0.868/0.842):** BMAD_Q1 §4.3#8 canonizes ECFP4 0.868 vs Hybrid 0.842 (p=0.111). Main matches. **KEEP.** Fix = deposit the reproducing CSV (the 0.819/0.746 CSV is non-canonical). ⚠️ BMAD_Q1 §3.4 lists Hybrid=0.691 (with PHCO 0.500) vs §4.3 Hybrid=0.842 — internal discrepancy (§3.5 attributes it to "PHCO bug correction"). **Decision pending: 0.842 (§4.3) vs 0.691 (§3.4).**
- **C3 (TDA<ECFP4):** BMAD_Q1 §3.4 canonizes TFP=0.586 (unbalanced) as the headline; "TDA doesn't beat ECFP4" is the canonical claim. The balanced SOTA (TFP-12 0.867, PersStats 0.873) is a separate SM analysis. **DOWNGRADED to HIGH framing:** surface the balanced SOTA in main text; don't flatly claim "TDA inferior" without acknowledging the balanced result.
- **C9 (H₁→promiscuity):** BMAD_Q1 §3.8.3 shows H₁ entropy ρ=−0.190 (p<10⁻¹³⁷, significant). Main uses H₁ entropy. The earlier "refuted by H1_max_pers ρ=−0.002" checked the wrong H₁ feature. **REVERSED — claim supported.** Caveat: H₀ count (−0.248) is the stronger correlate (size effect); worth a sentence.
- **H2 (TNE 5.9×/38):** BMAD_Q1 §3.2 canonizes 5.9× (real) / 15.6× (padded), 38 atoms. Main matches. Reversed (p3_tne_summary.txt 6.1×/39 is non-canonical).
- **H4 (13 failures):** BMAD_Q1 §3.1 says TDA had 13 failures (no 3D embedding). Main L256 matches. Reversed.
- **H5 (ECFP4 Tartarus baselines):** BMAD_Q1 §3.8.1 = ECFP4 PfDHFR 0.4508/0.683, 6Y2F 0.5701/0.762, 4LDE 0.5154/0.733. Main L461 matches. **SM L575 is the one that's off (0.461/0.689, 0.578, 0.517) → fix SM.**
- **qkernel target_alignment 0.684:** BMAD_Q1 §3.3 = 0.684. Main matches. Reversed (CSV 0.543 non-canonical).

## STANDS (fix — confirmed against BMAD_Q1)
- **C5 Tartarus labels:** SM L573 wrong (6Y2F/PfCRT, 4LDE/PfClpP) → fix to 1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT (BMAD_Q1 §3.8.1; also fix p3_rrs_expansion.py TARGET_MAP). ✅ applied to SM.
- **C6 65,856→19,849:** BMAD_Q1 canonizes 19,849 for all P3 benchmarks (§3.1/§3.2/§3.4). Fix Methods L134/L238. (pending)
- **H1 qkernel p-value:** BMAD_Q1 §3.3 + §4.3#7 = p=0.088 (QK vs RBF). Main L359 says p=0.312 → fix to 0.088. (pending)
- **H6 0.936/0.105:** BMAD_Q1 §3.3 says "removed as unsupported." Main still cites 0.936/0.105 → remove/soften. (pending)
- **SM promiscuity L579:** wrong (−0.167/−0.161, from the Tartarus spearman) → fix to BMAD_Q1 §3.8.3 (H0 count −0.248, H0 entropy −0.243, H1 entropy −0.190, N=17,011). ✅ applied.
- **SM Tartarus R² L575:** stale ECFP4 values → fix to BMAD_Q1 §3.8.1. ✅ applied.
- **SM H1-RRS 0.947→0.916:** ✅ applied (n=77 0.361 clause pending decision #3).
- **C10 Zenodo DOI:** insert 10.5281/zenodo.19608875 in main L548; p3_polypharm_tfp_rrs.csv lives in Project2/results (BMAD_Q1 §3.9) — fix the Data Availability path. (pending)
- **H8 citations, H9 SM Discussion cut, H10 R7-R10 residue, H11 README, H16 requirements.txt, H17 anti-AI:** unchanged (not number-dependent). (pending)

## DECISIONS NEEDED (step 1)
1. **Hybrid AUC:** 0.842 (BMAD_Q1 §4.3, matches main) or 0.691 (BMAD_Q1 §3.4)? §3.5 says the difference is "PHCO bug correction."
2. **PHCO:** 0.500 (BMAD_Q1 §3.4, buggy) or 0.801 (SM bug-fix § + deposited CSV, corrected)?
3. **n=77 H₁-RRS expansion:** keep (corrected to 0.312 H1_count / 0.263 total persistence per the n=77 CSV) or remove (keep only the canonical n=14 ρ=0.916 per BMAD_Q1 §3.9)?

---

## STATUS — updated 2026-07-27 (editorial batch applied)

### ✅ Applied this session (unambiguous, no decision required)
- **SM number fixes (prior session):** Tartarus labels L573, Tartarus R² L575, promiscuity L579, H₁-RRS 0.947→0.916.
- **Main number fixes (prior session):** C6 Methods 65,856→19,849 (L134 framing, L238 CV set); H1 qkernel p 0.312→0.088 (L359).
- **H17 anti-AI (6 hits, all resolved; grep now 0):** Cover L34 "We demonstrate"→direct statement (+ 15.6×→5.9× real-atom for manuscript consistency); main L118 "robust"+"rigorous"+R7–R10 reviewer residue reframed; main L325 "robust SELFIES"→"SELFIES"; main L379 "robust baseline"→"reliable baseline"; main L479 "We demonstrate"→"Persistent homology resolves"; SM L608 mirror "robust"→"reliable".
- **H10 R7–R10 reviewer-response residue:** main L118 paragraph reframed (removed "peer review"/"review critiques"/(R7)–(R10)); main L349 "reviewer question R8 regarding the robustness"→"assess the stability of clustering-based enrichment metrics".
- **H8 citations:** Wesołowski bare-text `(Wesołowski et al., 2025)` → `\citep{wesolowski2025spectral}` in main L497 + SM L594; `@misc{wesolowski2025spectral}` added to bib (⚠️ FLAG: full bibliographic details/DOI to be confirmed — web search found no verifiable record; no DOI fabricated). SM manual `[1]` footnote (L658/L662) → `\citep{pytorch_cpp_extension}`; `@misc{pytorch_cpp_extension}` added. Dual `temgoua2026antimalarial`/`temgoua2027md` bibkeys: **no action** (Pass D §3.1 confirmed both keys defined and used correctly).
- **H11 README:** N1–N4 internal-ID labels removed; TNE 15.6×→5.9× real / 15.6× padded (L28 novelty table + L41 descriptors); 10-fold→5-fold CV (L43); wrong filename `Paper3_Quantum_Inspired_v0.7_V2607.tex`→`Paper3_Quantum_InspiredV2607.tex` (L62); `conda activate malaria_md`→venv+`pip install -r requirements.txt` (L73); 19,913 docked vs 19,849 benchmark clarified (L37–38).
- **H16 requirements.txt:** created at repo root from `scripts/*.py` import scan (no fabricated version pins; PennyLane 0.45.1 floor noted from SM).

### ⏸️ HELD — pending the five decisions (step 1)
- **H6 (0.936/0.105):** main L347/L353/L501/L530 still cite 0.936/0.105; BMAD_Q1 §3.3 says "removed as unsupported" → awaiting decision #4 (remove + reframe generically, or replace with deposited v1 0.885/0.867).
- **C10 (Zenodo DOI):** main L548 still placeholder `10.5281/zenodo.XXXXXXX, to be minted upon acceptance` → awaiting decision #5 (insert 10.5281/zenodo.19608875 as live, or reconcile all three docs to "pending"). README L92 + SM L110 already cite 19608875 as live.
- **H9 (SM duplicated Discussion, L585–643):** NOT cut — entangled with decisions #1 (Hybrid 0.691 vs 0.842 at SM L596) and #4 (0.936/0.105 at SM L596). Pass D recommends cutting the "Mechanistic explanation for classical fingerprint superiority" subsection (SM L589–596) as a main-Discussion duplicate; deferred until #1/#4 resolved so the cut and the number fixes land together.
- **Script fix (TARGET_MAP):** `scripts/p3_rrs_expansion.py` Tartarus labels still swapped (6y2f/PfCRT, 4lde/PfATP4 → should be 6y2f/PfATP4, 4lde/PfCRT per BMAD_Q1 §3.8.1). Mechanical; will apply with the number batch.

### Decisions resolved (2026-07-27)
1. **Hybrid AUC (0.842 vs 0.691) — NO CHANGE NEEDED.** Main correctly uses 0.842 as the current hybrid (10-component kernel PCA); 0.691 is consistently framed as the historical "v2 single-scalar QK density" (L230, L491, L503). BMAD §3.5 confirms "0.842 in v0.7, 0.691 in BMAD v19." The main's explanation (single-scalar → 10-component) is internally consistent; the ablation 0.608 (vs BMAD §3.4's 0.605 for the 0.691-run) are from different runs, both correct.
2. **PHCO (0.500 vs 0.801) — HELD (needs author).** Main reports 0.500 (buggy) in table (L312) and prose (L295, L491) and draws a *scientific conclusion*: "pharmacophore-based bit vectors provide no discriminative information." SM §phco_bug documents 0.500 was a bug (SparseBitVect all-zero) → corrected AUC 0.801. Fixing the main requires: (a) corrected full table row (only RF AUC 0.801 known; SVM/other columns + ΔAUC uncertain), (b) reversal of a scientific conclusion the author should own. **Blocker for this one item.**
3. **n=77 H₁-RRS expansion — NO CHANGE NEEDED.** Main uses 0.916 (n=14) = §4.3#9 canonical ✓; SM L639's n=77 0.361 (p=0.001, 500 processed) exactly matches BMAD July-25 corrected value (line 1633) ✓.
4. **H6 0.936/0.105 — APPLIED.** Removed all 4 main occurrences (L347, L353, L501, L530) and 1 SM occurrence (L596); reframed generically as "artefact of hyperparameter miscalibration, no deposited result file supports the earlier headline." Verified 0.936/0.105 grep = 0 post-fix.
5. **C10 Zenodo DOI — APPLIED.** Main L548 updated from `10.5281/zenodo.XXXXXXX, to be minted upon acceptance` → `10.5281/zenodo.19608875, reserved July 2026` (matches BMAD line 43 + README L92 + SM L110).

### Also applied this batch
- **Script TARGET_MAP** (`scripts/p3_rrs_expansion.py` L37–41): swapped 6y2f=PfCRT/4lde=PfATP4 → 6y2f=PfATP4/4lde=PfCRT (BMAD §3.8.1). Labels only, no values recomputed.

### Build validation (2026-07-27)
- `latexmk -pdf` clean build: both main (1.3 MB) and SM (1.7 MB) compiled successfully.
- Zero undefined citations (including `wesolowski2025spectral`, `pytorch_cpp_extension`).
- Zero fatal errors.
- Pre-existing warnings (xr external document not found, SM duplicate labels in post-`_bibliography` section) unrelated to this session's edits.

### Remaining items after this session
1. **PHCO table + interpretation (decision #2) — RESOLVED 2026-07-28.** Author directed: check CSVs first; use 5-fold mean AUC. Source `results/p3_hybrid_benchmark.csv` (columns `descriptor,classifier,fold,auc,accuracy,f1`) PHCO RF 5-fold means: AUC **0.943**, Accuracy **0.860**, F1 **0.883**; ΔAUC = 0.943 − 0.868 = **+0.075**. Applied: table row L312 (0.500/0.525/0.689/−0.368 → 0.943/0.860/0.883/+0.075); prose L295 + L491 rewritten (removed "ECFP4 highest AUC" + "PHCO 0.500 exactly random → no discriminative information"; now PHCO 0.943 slightly above ECFP4, pharmacophores discriminative when properly encoded). Cross-doc `\cref{sec:phco_bug}` replaced with plain "Supplementary Material" (main only `\externaldocument`s Project2, not the SM). Recompile clean (0 undefined citations, PDF 1.33 MB). ⚠️ Note: corrected PHCO 0.943 > ECFP4 0.868 by simple mean, but per-fold matched ΔAUC = −0.017 (ECFP4 per-fold mean in same CSV = 0.960); the +0.075 follows the table's existing mean−baseline convention — flag for author if the convention should switch to matched per-fold.
2. **Wesołowski reference details — RESOLVED 2026-07-28.** Real reference supplied by author: Jamali, Cheng, Vargas-Hernández (2026), "Spectral Analysis of Molecular Features: When Richer Features Do Not Guarantee Better Generalization," arXiv:2510.14217. Placeholder `@misc{wesolowski2025spectral}` → `@misc{jamali2026spectralanalysismolecularfeatures}`; both `\citep` (main L497, SM L594) updated. Prose unchanged — existing description accurately matches the paper's real finding (ECFP-positive vs 3D-negative spectral correlation). Full clean rebuild (`latexmk -C`) purged stale aux/bbl; 0 undefined citations.
3. **H9 SM Discussion cut — RESOLVED 2026-07-28.** Author confirmed: cut. Removed the duplicate "Mechanistic explanation for classical fingerprint superiority" subsection (was SM L589–596) and replaced with a brief pointer to the main Discussion (retains Jamali citation + ablation numbers — no unused-citation warning). Kept the "Quantum kernel density vs classical fingerprint discriminator" subsection (experimental details, per Pass D). SM recompile clean.
4. **20 leads / n=14 clarity — RESOLVED 2026-07-28.** BMAD_Q1 §3.9: the 20 = P2's top-20 *single-target* candidates (line 18); the 17 = polypharmacological leads (line 976), distinct from the top-20 (line 549); the 14 = the 17 with complete RRS data (lines 978, 982: 3A+1A*+2B+7C+1D). Main L511 "20 high-confidence polypharmacological leads" conflated the two cohorts → corrected to "17 polypharmacological leads...; of these, 14 carried complete resistance-resilience (RRS) classifications and formed the analysis cohort." Bridges to n=14 in L513. ⚠️ FLAG: changed 20→17; revert if the top-20 was intended for another reason.
5. **C3 balanced SOTA framing — RESOLVED 2026-07-28.** Author chose Option A: surface the class-weighted results in the main. Applied two additions to the main: (i) Results L295 — after "standalone TFP and TNE descriptors perform substantially below the classical baselines," added a sentence noting that the SM's class-weighted benchmark shows PersStats (0.873) and TFP-12 (0.867) reach ECFP4-parity (ΔAUC=+0.005, p>0.05), indicating topological features carry ECFP4-comparable discriminative signal once the 75.9%/24.1% class imbalance is addressed; (ii) Discussion/Limitations L528 — after "TDA does not outperform ECFP4 overall... a valid negative result," added a qualifying sentence noting the configuration-dependence and the class-weighted parity. Recompile clean (0 undefined, 0 errors).
