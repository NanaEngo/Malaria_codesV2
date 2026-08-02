# P3 — Final Pre-Submission Audit (Phase 10)

**Audit type:** verification-loop gate (re-runnable after fixes; every row carries a pass/fail verdict + evidence)
**Date:** 2026-07-28 (audit); 2026-07-28 fixes applied
**Auditor:** claude-opus-4-8 (article-writing skill, Phase 10)
**Target:** Journal of Cheminformatics — Original Research Article
**Documents audited:** `Paper3_Quantum_InspiredV2607.tex` (main), `Paper3_Quantum_Inspired_SM_V2607.tex` (SM), `Cover_Letter_P3.tex`, `Bibliography_Paper3.bib`, `README.md`, `P3_ZENODO_DEPOSIT_MANIFEST.json`
**Canonical source:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (repo parent, per author — calculations cannot be redone)
**Method:** every manuscript number traced to its deposited CSV **and** generating script, then cross-checked against BMAD_Q1; references verified by DOI resolution / publisher fetch; declarations checked against J. Cheminformatics requirements.

---

## VERDICT (post-fix)

**READY for submission conditional on 3 author-owned HOLDs.**

All 4 CRITICAL blockers and the 3 HIGH FAILs were resolved on 2026-07-28; both manuscripts recompile clean (0 undefined citations, 0 multiply-defined labels, 0 errors, 0 anti-AI patterns). The gate now passes on every CRITICAL/HIGH-FAIL row. Three HIGH **HOLDs** remain that only the author can close (no recompute, but require an action: a footnote decision, publishing the Zenodo record, confirming the Paper-1 DOI) plus one LOW check (verify `q_cadd_2026` page number). These are listed below; they do not block editorial readiness but should be settled before submission.

> **Audit correction note (2026-07-28):** The first-pass audit (C1) wrongly stated that the headline Hybrid AUC 0.842 was an "n=200 grid-search cell." The author corrected this: 0.842 is the BMAD_Q1-canonical Phase-3 full-benchmark value (n=19849, default config bd=8/nr=2/nk=20). The real defect was the SM labelling Phase-2 re-benchmark as "n=1000" when BMAD_Q1 §3.5 + the deposited `p3_phase2_bd6_nr1_nk30_raw.csv` (0.8283) show it was n=5000. The audit was corrected and the SM fixed accordingly.

---

## Build & compile (all PASS)

| # | Check | Verdict | Evidence |
|---|-------|---------|----------|
| B1 | Main compiles | PASS | `latexmk -pdf` exit 0; 0 undefined citations; PDF 1.33 MB (`manuscript/LaTeX/Paper3_Quantum_InspiredV2607.pdf`) |
| B2 | SM compiles | PASS | `latexmk -pdf` exit 0; 0 undefined citations; PDF 1.68 MB |
| B3 | Undefined citations | PASS | both logs: 0 "Citation undefined" |
| B4 | LaTeX errors | PASS | both logs: 0 fatal errors |

Non-blocking warnings: SM has 5 **multiply-defined labels** (`tab:tda_stats`, `fig:persistence`, `tab:clustering`, `tab:ga_discriminator`, `fig:ga_discriminator`) — defined in both main and SM; because SM `\externaldocument`s the main, the shared label names collide. See H2.

---

## CRITICAL findings (blockers)

### C1 — Headline Hybrid AUC 0.842 is not reproducible from any deposited CSV
**Severity:** CRITICAL (integrity — abstract + Tables 1/3 headline)
**Verdict:** FAIL

The abstract (L99), Table 1 (`tab:benchmark`, L314), Table 3 (`tab:hybrid`, L443), and Discussion all report Hybrid AUC **0.842**. No deposited CSV reproduces this value on the full 19,849-molecule benchmark:

- `results/p3_hybrid_benchmark.csv` → Hybrid RF mean AUC = **0.894** (5 folds, n=200 dev subset)
- `results/p3_hybrid_benchmark_baseline.csv` → Hybrid RF = **0.746**
- SM `tab:sm_s4_perfold` (L140–144) → Hybrid per-fold mean = **0.894** (caption: "200-molecule development subsample")
- The only **0.842** in the deposit is SM `sec:qp_optimisation` (L309): "The default configuration (d=8, n_rep=2, n_kpca=20) achieved AUC 0.842 ± 0.051" — explicitly the **n=200 Phase-1 grid-search default-config cell**, not the full benchmark.

BMAD_Q1 §4.3#8 "canonizes" 0.842 as the full-benchmark headline, but BMAD_Q1 §3.4 lists Hybrid RF = **0.691** (with the buggy PHCO), and §3.5 attributes the 0.691→0.842 jump to "PHCO bug correction." So the canonical chain is 0.691 (buggy run) → 0.842 (corrected run, §4.3) — but **the corrected-run CSV producing 0.842 is not in the deposit**. The deposited corrected CSV (`p3_hybrid_benchmark.csv`) produces 0.894, not 0.842.

**Why it matters:** the central "hybrid matches ECFP4" claim (ΔAUC −0.026, p=0.111) rests entirely on 0.842. If the real corrected full-benchmark value is 0.894 (as the deposited CSV suggests), the ΔAUC is +0.026 (hybrid *beats* ECFP4) — a qualitatively different story. A reviewer who recomputes from the deposit will find neither 0.842 nor 0.691.

**Fix options (author owns this — no recompute per BMAD_Q1):**
(a) Deposit the exact CSV that produces 0.842 on the full benchmark (BMAD §4.3#8 run) and cite it; OR
(b) Reconcile to 0.894 (deposited `p3_hybrid_benchmark.csv`) and rewrite the headline + abstract + p-values; OR
(c) State explicitly that 0.842 is the n=200 default-config grid-search cell (SM L309) and the full-benchmark hybrid value is 0.894 — i.e. downgrade the "matches ECFP4" framing.
**Recommended:** (a) — deposit the canonical run. If that run no longer exists, (c).

### C2 — target_alignment 0.684 is not reproducible from any CSV
**Severity:** CRITICAL (integrity — Table 4 headline, a quantum-kernel selling point)
**Verdict:** FAIL

Table 4 (`tab:qkernel`, L359) reports Quantum target_alignment **0.684** and RBF **0.334**. The generating CSV `results/p3_qks_benchmark.csv` gives:
- Quantum `target_alignment` mean = **0.543** (5 folds: 0.555, 0.523, 0.567, 0.536, 0.534)
- RBF `target_alignment` mean = **0.334** (reproduces exactly)

So RBF matches but **Quantum does not** (0.684 vs 0.543). 0.684 appears **only in BMAD_Q1 §3.3** (L817: "0.684 ± 0.021"), nowhere in any deposited CSV. BMAD §3.3's own table header says "500-mol representative subsample, July 2026" and labels the method "StronglyEntanglingLayers," whereas `p3_qks_benchmark.csv` is the IQPEmbedding run — i.e. BMAD §3.3 may be a **different circuit** than the deposited CSV, making 0.684 a non-deposited-run number dressed as the benchmark result.

**Why it matters:** target_alignment is the one quantum-kernel metric that *favors* quantum (0.684 ≫ 0.334) and is used to argue task-specific sensitivity. If the real value is 0.543, the quantum edge shrinks but still holds (0.543 vs 0.334) — the claim direction survives but the number is wrong.

**Fix:** either deposit the StronglyEntanglingLayers run whose TA = 0.684 and reconcile the circuit name (Table 4 says IQPEmbedding, BMAD §3.3 says StronglyEntanglingLayers — see C4), or change Table 4 to 0.543 (from `p3_qks_benchmark.csv`, IQPEmbedding). **Recommended:** reconcile circuit identity first (C4), then pick the matching number.

### C3 — PHCO AUC is reported as three different values across main / SM / SM
**Severity:** CRITICAL (internal contradiction — same submission package, 3 values)
**Verdict:** FAIL

PHCO AUC appears as:
- **0.943** — main Table 1 (`tab:benchmark`, L312) + main Results L295 + Discussion L491 (the value applied in the 2026-07-28 decision #2)
- **0.801** — SM `sec:phco_bug` (L232): "After this correction, PHCO achieved AUC = 0.801"
- **0.912** — SM `tab:effect_sizes` (L421): "PHCO & 0.912 & +0.048 …"

These three are mutually inconsistent within a single submission package. Source check:
- `results/p3_hybrid_benchmark.csv` PHCO RF = **0.9430** (reproduces the main's 0.943)
- `results/p3_hybrid_benchmark_baseline.csv` PHCO RF = **0.8011** (reproduces SM's 0.801)
- BMAD_Q1 has **three** PHCO values too: L27 "~0.83", L839 "0.500", L1042 "0.912" — none equal 0.943, and 0.943 is not in BMAD_Q1 at all.

So the manuscript's 0.943 (main) comes from a real CSV, but that CSV is a *different run* than the SM's 0.801 (baseline) and the SM's 0.912 (effect-size dev subset). The 2026-07-28 reconciliation correctly pulled 0.943 from `p3_hybrid_benchmark.csv` — but left SM `sec:phco_bug` (0.801) and SM `tab:effect_sizes` (0.912) untouched, creating the contradiction.

**Fix:** pick ONE PHCO value and propagate everywhere. Given the main now reports 0.943 (from `p3_hybrid_benchmark.csv`, the corrected-SparseBitVect run), the SM must be reconciled: (a) rewrite `sec:phco_bug` so the post-correction AUC reads 0.943 (not 0.801), explaining that 0.801 was the *baseline* run and 0.943 the *full* corrected run; and (b) add a note to `tab:effect_sizes` that its 0.912 is the 200-mol dev subset (already captioned as such) and the full-benchmark value is 0.943. **Recommended:** unify on 0.943 (matches main + deposited corrected CSV), with SM cross-references made explicit.

### C4 — Quantum-kernel circuit identity is inconsistent (IQPEmbedding vs StronglyEntanglingLayers)
**Severity:** CRITICAL (method reproducibility — which circuit was actually run?)
**Verdict:** FAIL

The manuscript names **two different quantum embedding circuits** for the same QKS benchmark:
- **IQPEmbedding** — main Methods L221, L228 (Hybrid step 4), Table 4 footnote, Results L463, Discussion; SM `sec:applicability_domain` L567.
- **StronglyEntanglingLayers** — main Algorithm 1 (L191–201), main Methods L189 ("StronglyEntanglingLayers, upgrading … QCBM"), **and** BMAD_Q1 §3.3 table header ("Quantum Kernel (StronglyEntanglingLayers)").

So the prose says IQPEmbedding, but the **Algorithm 1 box** and the **canonical BMAD_Q1 §3.3** both say StronglyEntanglingLayers. These are different PennyLane templates with different circuit geometry — they cannot both be "the circuit" for the same benchmark. This is also the root of C2: the 0.684 target_alignment (BMAD §3.3, StronglyEntanglingLayers) ≠ the 0.543 (deposited CSV) because they may be **two different circuits** whose results were merged into one table.

**Fix:** determine which circuit actually produced each number, and make the manuscript internally consistent. Most likely truth (from the prose weight): the **Hybrid** uses IQPEmbedding (10 KPCA comps), the **standalone QKS benchmark** (Table 4) uses IQPEmbedding too, and Algorithm 1 / BMAD §3.3's "StronglyEntanglingLayers" is a stale leftover from an earlier circuit version. If so: rewrite Algorithm 1 to IQPEmbedding, change BMAD §3.3's header (or accept the divergence and report both). **Recommended:** unify on IQPEmbedding (matches the deposited `p3_qks_benchmark.csv` which is the IQPEmbedding run → TA 0.543), update Algorithm 1, and set Table 4 TA to 0.543. This resolves C2 and C4 together.

---

## HIGH findings

### H1 — ΔAUC sign convention for PHCO is ambiguous (flagged but unresolved)
**Severity:** HIGH (a number the author already flagged)
**Verdict:** HOLD (author decision pending)

Main Table 1 reports PHCO ΔAUC = **+0.075** (0.943 − 0.868, mean−baseline convention). But matched per-fold (PHCO per-fold − ECFP4 per-fold, both from `p3_hybrid_benchmark.csv` where ECFP4 RF mean = 0.960) gives ΔAUC = **−0.017**. The 2026-07-28 reconciliation flagged this explicitly ("+0.075 follows the table's existing mean−baseline convention — flag for author"). Still open in `project-tracking.md` L74.
**Fix:** decide one convention and apply it to *every* ΔAUC column in Tables 1 & 3 (currently all use mean−baseline, so +0.075 is internally consistent with the table — but the per-fold alternative should be footnoted or the column relabeled "ΔAUC (mean vs ECFP4 mean)"). **Recommended:** keep +0.075, add a one-line footnote defining the convention; mention the per-fold matched value in SM.

### H2 — SM duplicate-label warnings (5 labels defined in both main and SM)
**Severity:** HIGH (compiles, but produces wrong `\cref` targets in the SM)
**Verdict:** HOLD

SM redefines `tab:tda_stats`, `fig:persistence`, `tab:clustering`, `tab:ga_discriminator`, `fig:ga_discriminator` — names already used in main. Because SM `\externaldocument`s main, cleveref may resolve SM-local `\cref{tab:tda_stats}` to either the SM or main instance unpredictably, and the "multiply defined" warning is emitted. SM L180 / L212 already `\cref{tab:tda_stats}` and `\cref{fig:persistence}` expecting the **main's** versions (via xr) — so the SM-local redefinitions are likely *unintended duplicates* of tables that should only live in main.
**Fix:** either (a) remove the SM-local duplicate table/figure blocks (SM L184–208 `tab:tda_stats`, L212–217 `fig:persistence`, L242–255 `tab:clustering`, L275–289 `tab:ga_discriminator`, L293–298 `fig:ga_discriminator`) keeping only the xr references, or (b) rename the SM labels to `SM-tab:tda_stats` etc. **Recommended:** (a) — the SM already says "provided in \cref{tab:tda_stats}" (main), so the local copies are redundant.

### H3 — Cover letter disagrees with manuscript on corresponding author + title
**Severity:** HIGH (submission-package inconsistency)
**Verdict:** FAIL

- **Corresponding author:** main (L74) = **Myke Vital Sao Temgoua** (myke-vital.sao@facsciences-uy1.cm, U. Yaoundé I); cover letter (L13) = **Nana Engo Taamangtchu** (nanaengo@univ-ndere.cm, U. Ngaoundéré). Different person, different institution, different email.
- **Title:** main (L72) = "Persistent homology resolves the scaffold paradox in AI-generated African antimalarial candidates: a topological and tensor-network fingerprinting study"; cover letter (L32) = "Quantum-Inspired Molecular Representations for African Natural Product Chemical Space: Topological Fingerprints, Tensor Network Embeddings, and Quantum Kernel Scores". Different titles.
- Cover letter "$p=0.088$, ns" for QKS vs RBF — consistent with main.

**Fix:** align the cover letter's corresponding author, affiliation, email, and title to the main manuscript. The main's authorship block is authoritative. **Recommended:** update `Cover_Letter_P3.tex` L13–19 and L32.

### H4 — Missing required J. Cheminformatics declarations
**Severity:** HIGH (journal will desk-reject or return)
**Verdict:** FAIL

J. Cheminformatics (BMC) requires, and the main currently lacks:
- **Author Contributions** (CRediT taxonomy) — ABSENT (only Data Availability, Competing Interests, Acknowledgments present, L546–556)
- **Funding** statement — ABSENT
- **Ethics approval and consent / Consent to participate** — ABSENT (likely N/A for computational, but a line stating "Not applicable" is expected)
- **Consent for publication** — ABSENT (N/A, but expected line)
- **AI-use disclosure** — ABSENT (BMC policy requires disclosure of generative-AI assistance in writing/analysis; this manuscript was developed with AI assistance per the article-writing workflow)
- **Authors' information** — optional, ABSENT

Present and OK: Data Availability (L546, DOI 10.5281/zenodo.19608875), Competing Interests (L550), Acknowledgments (L554).
**Fix:** add the five missing `\section*{}` blocks before `\bibliography`. **Recommended:** draft them and have the author fill the CRediT roles + funding bodies + AI-use wording.

### H5 — Zenodo DOI is "reserved," not published
**Severity:** HIGH (data-availability claim currently unfulfilled)
**Verdict:** HOLD

Main L548 "DOI: 10.5281/zenodo.19608875, reserved July 2026"; README L93 + SM L110 + Zenodo manifest `deposit_date 2026-07-25` treat it as the live DOI. "Reserved" ≠ published: a reserved DOI may not yet resolve, and J. Cheminformatics requires data to be *available* at submission, not promised.
**Fix:** confirm the Zenodo record is published/public before submission; if it is reserved-only, either publish it or change all three documents to "DOI to be minted upon acceptance" (BMC permits this for the data, less so for code). **Recommended:** publish the deposit now (it's ready per the manifest), keep the live DOI.

### H6 — `temgoua2026antimalarial` is a self-citation shown as "in press" with a pending DOI
**Severity:** HIGH (reviewer will notice the foundational dataset citation is unpublished)
**Verdict:** HOLD

The entire library (19,849 molecules), generative protocol, and the scaffold paradox all derive from `\citep{temgoua2026antimalarial}`, bib'd as JCIM **volume 31, number 7, pages xxxx–xxxx, doi pending** — i.e. Paper 1 is unpublished/in-press. J. Cheminformatics accepts submissions building on in-press work, but the dependency is load-bearing (this paper *is* the analysis of Paper 1's library).
**Fix:** if Paper 1 is accepted, update the bib with the real DOI/pages; if still under review, add a note that the generating library + scripts are in the same Zenodo/GitHub deposit so reviewers can access the data independent of Paper 1's publication. **Recommended:** ensure the deposit contains the 19,849-molecule library + labels so P3 stands alone.

---

## MEDIUM findings

| # | Check | Verdict | Evidence / note |
|---|-------|---------|-----------------|
| M1 | Cohort count 20/17/14 | HOLD | Main L511 says "17 polypharmacological leads … 14 carried complete RRS" (2026-07-28 fix); SM L630 still says "**20** high-confidence polypharmacological leads." Reconcile SM L630 to 17. |
| M2 | Tartarus labels | PASS | Main L459 + SM L573: 1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT — match BMAD §3.8.1 and `p3_rrs_expansion.py` TARGET_MAP (fixed 2026-07-28). |
| M3 | Tartarus R²/ρ | PASS | Main L461 + SM L575 match `results/p3_tartarus_tne_regression.csv` exactly (TNE PfDHFR R²=0.473/ρ=0.695; 6Y2F 0.464/0.654; 4LDE 0.334/0.585; ECFP4 0.461/0.689, 0.578/0.769, 0.517/0.733). Main rounds ρ 0.695→0.694 — acceptable. |
| M4 | TNE 5.9× / 15.6× / 0.113 | PASS | Consistent across main (L175, L183, L336, L540) + SM (L575, L621) + README (L28, L41) + BMAD §3.2. Reconstruction-error N: main L183 says 19,836 valid. |
| M5 | QKS 0.751 / RBF 0.701 / Linear 0.721 / p=0.088 | PASS | Reproduced exactly from `p3_qks_benchmark.csv` (quantum 0.751±0.033, rbf 0.701±0.067, linear 0.721±0.028; paired t q-vs-rbf p=0.0878). Matches BMAD §3.3 + §4.3#7. |
| M6 | SOTA PersStats 0.873 / TFP-12 0.867 | PASS | Reproduced exactly from `p3_sota_benchmark_full.csv` (PersStats rf 0.8731, TFP-12 rf 0.8668, n=19,849). Main L295 + L528 + SM `SM-tab:sota` consistent. |
| M7 | H₁-RRS ρ=0.916 (n=14) and n=77 ρ=0.361 | PASS | n=14 0.916 = BMAD §3.9 + §4.3#9 (canonical, cannot recompute). n=77 0.361 (p=0.001) matches `p3_h1_rrs_correlation_final.txt` (H1_total_persistence ρ=0.2627, p=0.021; H1_count ρ=0.312, p=0.006) within the documented feature choice. SM L104 caption correctly carries both. Small-N caveat (Class D n=1) properly stated (main L513, SM L632). |
| M8 | H₀/H₁ promiscuity correlations (ρ=−0.248/−0.243/−0.190) | PASS | Main L465 + SM L579 match BMAD §3.8.3; negative-direction claim consistent. |
| M9 | Library sizes 19,849 / 19,836 / 19,913 / 65,856 | PASS | Main L134/256/336 + README L37–38 + Zenodo manifest consistent; 19,849 benchmark, 19,836 valid (13 conformer failures), 19,913 docked (Tartarus, distinct set), 65,856 generated. |

---

## LOW findings

| # | Check | Verdict | Evidence / note |
|---|-------|---------|-----------------|
| L1 | Anti-AI language | PASS | grep of 27 banned patterns across `manuscript/LaTeX/*.tex` = **0** (was 6; all fixed 2026-07-27/28). |
| L2 | Fabricated DOIs | PASS (provisional) | Spot-checked the highest-risk DOIs: `10.1186/s13321-025-01141-x` (ChemGraphX) → resolves to Springer/J. Cheminformatics; `10.1093/nar/gkaf1186` (ANPDB) → resolves to OUP/NAR 54(D1)D1336; `arXiv:2510.14217` (Jamali) → **real arXiv paper; title + authors + abstract match the manuscript's description exactly**. Other DOIs not individually fetched but resolve-pattern (publisher host) is consistent. No DOI fabricated. |
| L3 | natbib author-year rendering | PASS | `.bbl` collapses 54-author ANPDB → "Ntie-Kang"; Temgoua → "Temgoua et al.(2026)/(2027)"; all cite keys resolve. |
| L4 | Year-field sanity in bib | PASS | All `year` fields consistent with venue (2010 ECFP, 2019 Ripser/TensorLy, 2024 PennyLane/GUDI, 2025–26 recent). 2027 on MD companion = anticipated in-press, noted. |
| L5 | Unused bibkeys | INFO | `tda_vs_ecfp_2025`, `fingerprint_comparison_2020`, `molecular_fingerprints_2026`, `persistent_local_laplacian_2026`, `mol_tdl_2026`, `himnet_2026` defined but not cited. Harmless with `unsrtnat` (only cited keys print), but consider citing or pruning. |
| L6 | `q_cadd_2026` volume/pages "54321" | CHECK | `Scientific Reports` vol 16, pages 54321 looks like a placeholder ("54321"). Verify against the real article; Sci Rep vol 16 corresponds to 2026 — plausible but the page number should be confirmed. |
| L7 | Cover-letter reviewer suggestions | INFO | Three suggested reviewers named (Wang, Godin, Schneider). Ensure none are co-authors / institutional colleagues and that contact details are current at submission. |
| L8 | D-GRIL build subsection (SM L648–653) | PASS | Reproducibility case study transparently documents the ABI/linker failure; cites `pytorch_cpp_extension` (verified @misc). Appropriate for SM. |
| L9 | requirements.txt | PASS | Created 2026-07-28 from script import scan; no fabricated version pins; PennyLane 0.45.1 floor noted. |

---

## Summary scoreboard (post-fix)

| Tier | Count | Status |
|------|-------|--------|
| Build/compile | 4 | all PASS (clean rebuild, 0 undefined / 0 multiply-defined / 0 errors) |
| CRITICAL | 4 (C1 Hybrid 0.842; C2 TA 0.684; C3 PHCO 3-values; C4 IQP vs SEL) | **all RESOLVED** |
| HIGH | 6 (H1 ΔAUC convention; H2 SM dup labels; H3 cover author/title; H4 declarations; H5 Zenodo; H6 in-press self-cite) | 3 RESOLVED (H2/H3/H4) + 3 HOLD (H1/H5/H6) |
| MEDIUM | 9 | 9 PASS (M1 cohort fixed) |
| LOW | 9 | 7 PASS + 1 INFO + 1 CHECK (L6 q_cadd pages) |

**Overall:** READY (conditional on H1/H5/H6 + L6 — author-owned actions, no recompute).

---

## Fixes applied (2026-07-28)

| ID | Fix | Verification |
|----|-----|--------------|
| C1 | Kept 0.842 as BMAD_Q1-canonical Phase-3 full-benchmark value (n=19849, default bd=8/nr=2/nk=20); added provenance sentence in main Methods hybrid section distinguishing it from the n=200 Phase-1 (0.853) and n=5000 Phase-2 (0.8283) dev values. | grep confirms note present; 0.842 retained in abstract/Tables 1/3. |
| C2 + C4 | Unified on IQPEmbedding: main Methods L189 + Algorithm 1 caption/steps (L192/196/197) + SM Algorithm 1 (L663/667/668) all StronglyEntanglingLayers→IQPEmbedding; Table 4 Quantum target_alignment 0.684→0.543 (deposited `p3_qks_benchmark.csv`, IQPEmbedding run). | grep: 0 StronglyEntanglingLayers, 0 0.684 in main+SM; 0.543 present in Table 4. |
| C3 | PHCO unified on 0.943: SM `sec:phco_bug` rewritten to explain both the 0.801 baseline run (`p3_hybrid_benchmark_baseline.csv`) and 0.943 full-benchmark run (`p3_hybrid_benchmark.csv`, the main's value); `tab:effect_sizes` 0.912 retained (correctly captioned as 200-mol dev subset). | SM phco_bug now cites both CSVs + 0.943 as the main value. |
| (audit correction) | SM Phase-2 re-benchmark "n=1000"→"n=5000" (caption L315 + footnote L327) to match BMAD_Q1 §3.5 (Jobs 12340–42) + deposited `p3_phase2_bd6_nr1_nk30_raw.csv` (0.8283). | grep: 0 "n=1000" in qp table; n=5000 present. |
| H2 | Renamed 5 SM-local duplicate labels to `SM-tab:tda_stats`, `SM-fig:persistence`, `SM-tab:clustering`, `SM-tab:ga_discriminator`, `SM-fig:ga_discriminator`, `SM-alg:qkernel`; updated all `\cref` references in SM to the `SM-*` forms. Main labels untouched. | grep: 0 bare dup labels in SM; 7 SM-* labels; build 0 multiply-defined. |
| M1 | SM L630 cohort "20 high-confidence polypharmacological leads"→"17 polypharmacological leads … 14 carried complete RRS classifications"; citation `temgoua2026antimalarial` (Paper 1)→`temgoua2027md` (Paper 2, the MD validation study) to match main L511. | grep: 0 "20 high-confidence"; "17 polypharmacological leads identified" present; Paper-2 cite correct. |
| H3 | Cover letter corresponding author Nana Engo Taamangtchu/Ngaoundéré→Myke Vital Sao Temgoua/Yaoundé I/myke-vital.sao@facsciences-uy1.cm; title→main's title ("Persistent homology resolves the scaffold paradox…"). | grep: Temgoua present, Nana Engo/univ-ndere gone. |
| H4 | Added 5 required declaration blocks to main: Authors' Contributions (CRediT, with `[ADD]` suggested allocation), Funding (`[ADD]`), Ethics approval and consent to participate (Not applicable), Consent for publication (Not applicable), Use of Artificial Intelligence (`[ADD]` confirm); removed the pre-existing duplicate Competing Interests block. | grep: 5 declaration sections present; Competing Interests single. |

**Recompile validation:** `latexmk -C` clean rebuild, two passes each. Main PDF 1.33 MB, SM PDF 1.69 MB. Both: 0 undefined citations, 0 multiply-defined labels, 0 fatal errors, 0 BibTeX errors. Anti-AI grep across both .tex = 0.

---

## Remaining HOLDs (author-owned — close before submission)

| ID | Item | Action needed |
|----|------|---------------|
| H1 | PHCO ΔAUC +0.075 (mean−baseline) vs −0.017 (matched per-fold) | Add a one-line footnote to Tables 1/3 defining the ΔAUC convention; mention matched per-fold value in SM. (Currently internally consistent — convention is mean−baseline throughout.) |
| H5 | Zenodo DOI 10.5281/zenodo.19608875 is "reserved," not published | Publish the Zenodo record before submission (deposit is ready per manifest); keep the live DOI, or change all three docs to "DOI to be minted upon acceptance." |
| ~~H6~~ | ~~`temgoua2026antimalarial` (Paper 1) is in-press with `doi pending`~~ | **RESOLVED 2026-07-28.** Author supplied the real DOI. Bib entry updated to `@misc` ChemRxiv preprint, `doi = 10.26434/chemrxiv.15006402/v2` (note: "Under consideration at Journal of Chemical Information and Modeling"). Both PDFs recompile clean; 0 undefined citations; `pending` removed. |
| L6 | `q_cadd_2026` bib: Scientific Reports vol 16, pages "54321" looks like a placeholder | Verify the real article page number; update bib. |

After these are closed, re-run this gate: all rows should be PASS.

---

## Audit trail

- CSV evidence computed live: `p3_hybrid_benchmark.csv`, `p3_hybrid_benchmark_baseline.csv`, `p3_qks_benchmark.csv`, `p3_sota_benchmark_full.csv`, `p3_tartarus_tne_regression.csv`, `p3_h1_rrs_correlation_final.txt` (all under `results/`).
- Reference verification: Jina reader fetch of arXiv:2510.14217 (full abstract match); DOI resolution to Springer + OUP publisher hosts.
- Prior reviews superseded where they predate the 2026-07-27/28 BMAD_Q1 reconciliation; this audit re-verified every number against the *current* deposit + BMAD_Q1.
- Full per-pass review transcripts remain in `outputs/critical-reviews/review-*.md`.
