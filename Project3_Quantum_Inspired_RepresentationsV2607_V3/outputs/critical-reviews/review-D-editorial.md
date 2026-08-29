# Review D — Editorial / Prose / LaTeX Hygiene

**Reviewer role:** independent editorial reviewer (no access taken to `outputs/analysis/analysis-ledger.md` or `project-tracking.md`).
**Date:** 2026-08-06
**Target venue:** *Journal of Cheminformatics* (BMC).

**Files reviewed**

| Role | Path |
|---|---|
| MAIN | `manuscript/LaTeX/Paper3_Quantum_InspiredV2608.tex` (433 lines) |
| SM | `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2608.tex` (731 lines) |
| COVER | `manuscript/LaTeX/Cover_Letter_P3.tex` (56 lines) |
| BIB | `manuscript/LaTeX/Bibliography_Paper3.bib` (66 entries) |

**Verdict:** Not submittable as-is. The SM does not compile (fatal, exit 12), the main text contains a sentence that stops mid-clause, the main manuscript's only Figure 1 is never cited, one table carries two labels, and ~40 % of the SM Discussion is a near-verbatim copy of the main-text Discussion. Prose quality is otherwise good — only 7 anti-AI regex hits across 1,220 lines, none in the cover letter.

---

## 1. ANTI-AI PROSE

### 1.1 Regex hits — complete list with replacements

Command run (per file):

```
grep -niP '\b(delve|underscore|illuminate|elucidate|showcase|harness|leverage|scalable|robust|compelling|elevates|transforms|Furthermore,|Moreover,|In addition,|Notably,|Importantly,|It is worth noting that|crucial|pivotal|unprecedented|groundbreaking|we demonstrate|our work establishes)\b' <file>
```

Total hits: **MAIN 5, SM 2, COVER 0.** (Search widened to inflected forms `leveraged/leverages/underscores/underscoring`; no additional hits.)

---

**[LOW] MAIN:121 — `robust`**
> "(R8) whether enrichment metrics are **robust** to clustering resolution, addressed in \cref{sec:tensor_clustering} (Tensor-Based Clustering);"

*Assessment:* legitimate technical usage ("robust to X" = invariant under X), not an AI evaluator. Keep, or tighten for precision:

**Replacement:** "(R8) whether enrichment metrics change when the clustering resolution is varied, addressed in \cref{sec:tensor_clustering} (Tensor-Based Clustering);"

---

**[MEDIUM] MAIN:286 — `robust`**
> "Concurrently, the **robust** SELFIES string syntax inherently preserves valid cyclic macro-structures, fused ring systems, and rigid core fragments from the African natural-product seeds, which manifests mathematically as the preservation of the H$_1$ topology distributions."

*Assessment:* "robust" + "inherently" + "manifests mathematically" is inflated. SELFIES' property is *closure* (every string decodes to a valid molecule), which is the precise claim.

**Replacement:** "Because every SELFIES string decodes to a syntactically valid molecule, ring closures survive character-level mutation, so the fused ring systems and rigid cores of the African natural-product seeds are carried into the expanded set — which is what the preserved H$_1$ persistence distributions record."

---

**[MEDIUM] MAIN:311 — `robust`**
> "...classical fingerprint-based distance metrics therefore provide a simpler, more **robust** applicability-domain baseline, while quantum kernel methods add value primarily for heterogeneous or out-of-distribution regimes."

*Assessment:* "more robust" is unquantified; the paper's own numbers (AUC 1.000 vs 0.425–0.511) say something stronger and more specific. Also "add value" is asserted without evidence in this paper.

**Replacement:** "For near-duplicate detection, then, ECFP4 Tanimoto distance is both simpler and far more accurate than quantum kernel density (AUC 1.000 versus 0.425–0.511); whether the quantum kernel is preferable on structurally heterogeneous or out-of-distribution sets was not tested here."

---

**[MEDIUM] MAIN:319 — `leveraged`**
> "To validate whether the TNE compression preserves binding-relevant geometry, we **leveraged** the Tartarus docking benchmark \citep{tartarus_2024}: \num{19913} primary leads docked with QuickVina against three targets..."

**Replacement:** "To test whether TNE compression preserves binding-relevant geometry, we used the Tartarus docking benchmark \citep{tartarus_2024}: \num{19913} primary leads were docked with QuickVina against three targets (1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT) on an HPC cluster."

---

**[MEDIUM] MAIN:378 — `underscore`**
> "These episodes **underscore** the importance of rigorous baseline tuning, circuit selection, and statistical power; QKS should therefore be positioned as a methodological, NISQ-era proof of concept rather than a predictive improvement."

*Assessment:* "underscore the importance of" is the canonical AI closing move, and "rigorous" adds nothing.

**Replacement:** "Both episodes were caused by a control we had not tuned or a circuit we had not checked, not by the quantum kernel itself; we therefore report QKS as a NISQ-era proof of concept rather than a predictive improvement."

---

**[MEDIUM] SM:569 — `leveraged`**
> "To validate whether the TNE compression preserves binding-relevant geometry, we **leveraged** the Tartarus docking benchmark \citep{tartarus_2024}..."

**Replacement:** same as MAIN:319. (Note: this paragraph is a 92 %-similar duplicate of MAIN:319 — see §3.3; the cleanest fix is to delete the SM copy entirely.)

---

**[MEDIUM] SM:608 — `robust`**
> "...classical fingerprint-based distance metrics provide a simpler and more **robust** baseline, while quantum kernel methods add value primarily for structurally heterogeneous or out-of-distribution regimes."

**Replacement:** same as MAIN:311.

---

### 1.2 Promotional / inflated phrasing the regex misses

| Sev | Loc | Text | Replacement |
|---|---|---|---|
| MEDIUM | MAIN:73 (title) | "**resolve** chemical paradoxes" | See §2.1 — plural + attribution both unsupported. |
| MEDIUM | MAIN:127 | "PACTNet \citep{pactnet_2025} showed that cellular complex topological features can **vastly** compress graph network sizes" | "PACTNet \citep{pactnet_2025} reported large reductions in graph-network size from cellular-complex topological features" — or give the reported factor. |
| MEDIUM | MAIN:127 | "Multimodal representation fusion is **equally effective** in deep learning" | "The same complementarity has been reported for deep-learning representations" |
| MEDIUM | MAIN:286 | "topological data analysis **establishes** that the computational expansion protocol achieves peripheral functional distinction without destroying the core target-recognition topologies" | "the H$_0$/H$_1$ decomposition is consistent with peripheral variation over a conserved ring core; it does not establish that target recognition is preserved, which was not tested." (The word "target-recognition" imports an untested binding claim.) |
| HIGH | MAIN:307 / SM:563 | "the quantum kernel density $\rho(x)$ supplies a **native** Hilbert-space boundary condition... This **furnishes a rigorous** applicability-domain metric for natural products that **avoids the dimension-collapsing artefacts** common to Tanimoto-based domain estimations." | This paragraph sits in **Results** and reports no result; worse, the paper's own §"Quantum kernel density vs. classical fingerprint discriminator" shows the quantum density *fails* (AUC 0.425–0.511) exactly where Tanimoto succeeds (1.000), so the claim is contradicted 4 lines later. Replace with: "We also assessed the quantum kernel as an applicability-domain score, computing the mean kernel similarity $\rho(x)$ of each candidate to the seed set, and benchmarked it against ECFP4 Tanimoto distance." |
| MEDIUM | MAIN:311, 345; SM:608 | "reveal a **clear hierarchy**" / "**perfect** separation" | "gave a consistent ordering" / "separated the two sets completely (AUC = 1.000), for the reason given below" |
| MEDIUM | MAIN:325 | "This provides a **clear topological mechanism**: lower topological complexity ... **endows** candidate molecules with optimal conformational adaptability" | A Spearman $\rho$ of $-0.19$ to $-0.25$ is a weak monotone association, not a mechanism. "One interpretation is that lower ring and component complexity leaves more conformational freedom for multi-target binding; the correlations are weak ($|\rho| \leq 0.25$) and this remains a hypothesis." |
| MEDIUM | MAIN:353 | "**A key finding** is that..." | "With the canonical 6-qubit circuit, the gamma-tuned RBF kernel and the quantum kernel..." (drop the self-signposting). |
| MEDIUM | MAIN:376 | "classical fingerprints **excel** at detecting local atom-level changes" | "classical fingerprints detect local atom-level changes directly" |
| LOW | MAIN:121 | "supplies the **rigorous** topological and tensor-network justification" | "supplies the topological and tensor-network analysis requested" |
| LOW | MAIN:194 | "UMAP with Jaccard metric **is the appropriate** dimensionality reduction for binary/count fingerprints." | Bare assertion with no citation. "UMAP with the Jaccard metric was used because the inputs are binary/count vectors \citep{...}." |
| LOW | SM:520 | "**Key findings:** (i) ..." | Fine in an SM, but four consecutive SM sections open with "Key findings:". Vary or drop. |

---

## 2. TITLE + ABSTRACT

### 2.1 [HIGH] "resolve" overclaims, and "tensor-network" is mis-credited

Current title (MAIN:73, mirrored in SM:71 and COVER:34):

> "Topological and tensor-network representations **resolve chemical paradoxes** in African antimalarial natural products"

Three problems, each traceable to the paper's own text:

1. **Plural "paradoxes" is unsupported.** Exactly one paradox is resolved — the scaffold paradox (MAIN:284–286, 337). The manuscript names a *second* paradox at MAIN:363 ("This correlation presents a biophysical paradox: why does TFP ... show a nominally significant correlation with resistance resilience?") and then explicitly **fails** to resolve it: "the partial-correlation analysis shows this signal is confounded by molecular size; the relationship is therefore hypothesis-generating" (MAIN:363). A title claiming plural resolutions is contradicted on page 12.
2. **"Tensor-network" contributed nothing to the resolution.** The scaffold paradox is resolved by persistent homology alone (H$_0$/H$_1$ decomposition, MAIN:286, 337). TNE plays no role; indeed the ablation shows removing TNE *improves* the hybrid (MAIN:274, $\Delta = +0.011$). Naming TNE in the resolving clause credits it with a result it did not produce.
3. **"Resolve" is stronger than the evidence.** What is shown is a *consistent decomposition* — H$_1$ distributions overlap while H$_0$ distributions diverge — which explains the arithmetic of 92.6 % vs 69.3 %. That is an explanation, not a resolution of a contradiction, and no causal or prospective test is reported.

Additionally, the title hides the paper's most defensible contribution, which is the honest negative: ECFP4 (0.948) beats everything, and the quantum kernel is statistically indistinguishable from a tuned RBF. The cover letter (COVER:38) leads with exactly this and is better positioned than the title.

**Alternative title 1 (recommended — matches the honest-negative framing):**
> "Persistent homology explains the scaffold paradox in African antimalarial natural products, but quantum-inspired descriptors do not outperform ECFP4"

**Alternative title 2 (benchmark-forward, safest for JCheminf scope):**
> "Topological, tensor-network and quantum-kernel molecular representations benchmarked against classical fingerprints on 19,836 African antimalarial candidates"

If the authors keep the current structure, the minimum fix is singular + correct attribution: "Persistent homology resolves the scaffold paradox in African antimalarial natural products: a benchmark of topological, tensor-network and quantum-kernel representations."

### 2.2 [HIGH] Abstract is unstructured; J. Cheminformatics requires structured

Measured (MAIN:99–101): **243 words, 7 sentences, 2,072 characters, single unbroken block.**

- **Length** is comfortably within the BMC 350-word cap. No problem there.
- **Structure is the problem.** BMC/*Journal of Cheminformatics* research articles require a structured abstract with explicit **Background / Results / Conclusions** headings. The current abstract has none. Verify against the current author instructions before resubmission, but as written it will bounce at technical check.
- **Density.** 7 sentences carry ~35 numerals. Sentences 3 and 6 each pack six statistics. The mean sentence is ~35 words; sentence 6 (the kernel comparison) is 58 words.
- **Keywords:** 8 (MAIN:103) — within the BMC 3–10 range. Fine.

**Suggested restructure (keeps every number, ~250 words):**

> **Background.** Computational drug discovery for neglected diseases faces a scaffold paradox: generated candidates reach 92.6 % Tanimoto diversity from their seeds while retaining 69.3 % of seed scaffolds. Classical extended-connectivity fingerprints do not separate these two levels of structure.
>
> **Results.** We define three quantum-inspired representations — a persistent-homology Topological Fingerprint (TFP), a Tucker-compressed Tensor Network Embedding (TNE, 6.1× real-atom mean compression), and simulated Quantum Kernel Scores (QKS) — and benchmark them on 19,836 African antimalarial candidates. ECFP4 remains the strongest single descriptor (AUC 0.948), ahead of AP (0.940), BPF (0.939), FCFP4 (0.918), MACCS (0.905), PHCO (0.896), TFP (0.876) and TNE (0.722). The hybrid TFP+TNE+QK descriptor reaches AUC 0.888, significantly below ECFP4 (*p* < 0.0001) but above every standalone quantum-inspired descriptor, with QKS the principal positive contributor (ablation Δ = −0.040). The quantum kernel is statistically indistinguishable from a gamma-tuned RBF baseline at every sample size (*p* = 0.060 at *n* = 19,849; *p* = 0.419 at *n* = 5,000) while beating a linear kernel (*p* ≤ 0.0006). H$_1$ count correlates with resistance-resilience scores (ρ = 0.312, *p* = 0.0057, *n* = 77) but the association vanishes after controlling for molecular weight (ρ_partial ≈ 0, *p* > 0.7).
>
> **Conclusions.** Persistent homology separates the ring topology preserved during generative expansion (H$_1$) from the atom-level connectivity that diverges (H$_0$), which accounts for the scaffold paradox. Quantum-inspired descriptors are useful as diagnostics, not as replacements for ECFP4 in primary screening.

### 2.3 [MEDIUM] "Introduction" should be "Background"

MAIN:109 uses `\section{Introduction}`. BMC/J. Cheminform research articles use **Background**. Cosmetic but caught at technical check.

---

## 3. STRUCTURE

### 3.1 [CRITICAL] Truncated sentence in Methods

**MAIN:219** — the paragraph ends mid-clause, with no period:

> "Hyperparameter optimisation followed a two-phase protocol. In Phase~1 ($n = \num{200}$), a grid search evaluated \num{60} combinations"

Verified in the rendered PDF (p. 6): "In Phase 1 (n = 200), a grid search evaluated 60 combinations" then a blank line and the next `\subsection`. **Phase 2 is never described in the main text at all**, even though the whole manuscript hinges on "the Phase-2 winning circuit" (MAIN:123, 192, 206) and "the Phase-2 optimum, $n_{\text{kpca}}=30$" (MAIN:206). The reader has no idea what Phase 2 was.

**Fix:** complete the sentence and add Phase 2, pulling from SM §14 (`sec:qp_optimisation`, SM:300–302):

> "Hyperparameter optimisation followed a two-phase protocol. In Phase 1 ($n = 200$) a grid search evaluated 60 combinations of bond dimension $d \in \{4,6,8\}$, IQPEmbedding repeats $n_{\text{rep}} \in \{1,2,3,4,6\}$ and kernel-PCA components $n_{\text{kpca}} \in \{5,10,20,30\}$ by 5-fold stratified cross-validation. In Phase 2 the three best combinations were re-benchmarked at $n = 5{,}000$; the winner ($d = 6$, $n_{\text{rep}} = 1$, $n_{\text{kpca}} = 30$, AUC $0.8283 \pm 0.0371$) is the canonical configuration used throughout (\cref{sec:qp_optimisation})."

### 3.2 [HIGH] The main manuscript's Figure 1 is never cited

`fig:paradox` (**MAIN:288–293**, `scaffold_paradox.pdf`) has **zero in-text callouts**. The subsection it illustrates (§3.3 Scaffold paradox resolution, MAIN:284–286) discusses the H$_0$/H$_1$ decomposition in prose and never points the reader at the figure. Consequence: the first figure the reader is *sent* to is Figure 2 (MAIN:380), so the main text cites its figures out of order (2 before 1).

**Fix:** add a callout in MAIN:286, e.g. "...which manifests as preserved H$_1$ and diverged H$_0$ persistence distributions (\cref{fig:paradox})."

### 3.3 [HIGH] Large-scale duplication between main text and SM

Automated paragraph similarity (difflib, paragraphs > 200 chars) found nine main-text paragraphs with a near-twin in the SM:

| MAIN line | SM line | Similarity | Content |
|---|---|---|---|
| 307 | 563 | **0.98** | "We frame the quantum kernel not merely as a binary classifier…" (verbatim except "dimension-collapsing" → "dimensionality-reduction") |
| 319 | 569 | **0.92** | Tartarus docking validation setup |
| 194 | 675 | **0.80** | Kernel value definition + UMAP input construction |
| 321 | 571 | 0.65 | Tartarus $R^2$ results per target |
| 325 | 575 | 0.57 | TDA–promiscuity correlations |
| 353 | 599 | 0.54 | Kernel comparison / no significant difference |
| 361 | 639 | 0.55 | H$_1$–RRS integration with MD study |
| 341 | 630 | 0.52 | TNE compression and scaffold information |
| 349 | 597 | 0.50 | Mechanistic explanation for ECFP4 superiority |

Structurally, **SM §16 (`Applicability domain and comparison with existing tools`, SM:555–582) and SM §17 (`Discussion`, SM:588–654) are a second copy of MAIN §3.6–3.9 and §4.1–4.6.** Reviewers reliably flag this as padding, and BMC's SM policy is that supplementary files hold material that does not fit the article, not a restatement of it.

**Fix:** delete SM §16 and the duplicated subsections of SM §17 (SM:555–643), keeping only what is genuinely SM-only: the D-GRIL build case study (SM:649–654) and the algorithm listing (SM:660–675). Move it under a neutral heading such as "Additional methodological notes".

### 3.4 [HIGH] The same figure appears in both documents

`h1_rrs_class_violin.png` is Figure 2 of the main text (MAIN:365–370) **and** Figure S1 of the SM (SM:101–106), with captions that are ~90 % identical. Pick one. Given it is discussed at length in MAIN §4.7, keep it in the main text and delete SM §1's figure (or replace the SM version with the size-controlled partial-correlation scatter, which is currently reported only as numbers).

### 3.5 [HIGH] Methods describe an analysis that has no Results

**MAIN:229–231** (§2.9 "Comparison with existing tools") promises two analyses:

> "TFP features were compared with ChemGraphX topological descriptors \citep{chemgraphx_2026} by computing Spearman correlations between corresponding entropy-based measures across the \num{65856}-molecule library. Fingerprint diversity was assessed using the Universal Molecular Fingerprint Highlighter (UMFH) framework \citep{umfh_2026} to compare the representational breadth of TFP, TNE, ECFP4, and MACCS."

**Neither appears anywhere in Results, Discussion or the SM.** The Results subsection with the matching title (MAIN:317–325) reports Tartarus docking, polypharmacology QKS and TDA–promiscuity instead. Grep confirms `ChemGraphX` occurs only at MAIN:123, 165, 231 (all framing, no numbers) and `UMFH` only at MAIN:123, 231.

**Fix:** either run and report the two comparisons, or delete MAIN:229–231 and the associated claims in the Introduction (MAIN:123: "We also compare our TFP with the ChemGraphX topological descriptor tool… and our diversity analysis with the UMFH framework").

### 3.6 [HIGH] A whole SM results block is invisible from the main text

The SM contains three ChEMBL sections (SM §12 enrichment, §13 experimental validation, Tables S9–S11) reporting the closest thing in this paper to experimental grounding — including three PfATP4 analogues with IC$_{50}$ 0.4–0.79 µM (SM:475–479). Grep: the string "ChEMBL" appears **0 times in the main manuscript**. The same is true of the Monte-Carlo uncertainty / conformal analysis (SM §10, Table S6): 0 mentions of "conformal" or "Monte Carlo" in the main text.

For a journal that expects the SM to *support* the article, results that the article never mentions read as orphaned. Either surface one sentence each in the main Results ("A ChEMBL analogue search over the 77-compound RRS cohort found seven analogues at Tanimoto ≥ 0.25 (3.0 %), three of them experimentally active against PfATP4 (SM §13)") or move them out.

### 3.7 [MEDIUM] Main-text Results subsection with no results

**MAIN:305–307** (§3.6 "Applicability domain analysis") is two sentences of framing and zero data — it defines what the quantum kernel density *is for* and then stops. It is also 0.98-identical to SM:563. Merge it into the opening of §3.7 (which does report the discriminator benchmark) or move to Methods.

### 3.8 [MEDIUM] SM "Data Availability" is stranded mid-document

**SM:108–110** places `\section*{Data Availability}` between SM §1 (cross-paper validation) and SM §2 (per-fold statistics), i.e. on page 2 of an 18-page document. Move to the end, or delete — the main manuscript already carries the full statement (MAIN:394–396).

### 3.9 [MEDIUM] Nothing appears after `\bibliography` in either document — PASS

Checked explicitly per the review brief:
- MAIN:430–433 — `\bibliographystyle` / `\bibliography` / `\end{document}`. Clean.
- SM:728–731 — `\bibliographystyle` / `\bibliography` / `\end{document}`. Clean.

### 3.10 [MEDIUM] Main text cites SM floats in near-random order

Order of first citation of SM floats in the main text (from the rendered PDF): **Fig S8 → Table S2 → Fig S2 → Table S14 → Table S3 → Fig S3 → Table S4 → Fig S9 → Fig S6 → Fig S7 → Table S12.** SM float numbering follows the SM's internal layout, not the order the article needs them. A reader following the article jumps S8 → S2 → S14 → S3 → S4 → S9 → S6 → S7 → S12.

**Fix:** reorder the SM so its floats appear in main-text citation order (this is the normal convention and requires only moving `\begin{figure}`/`\begin{table}` blocks). At minimum, move the Tucker bond-dimension figure (`SM-fig:tensor`, currently Fig S8, first cited at MAIN:178) near the front of the SM.

### 3.11 [MEDIUM] Fragile hand-built cross-document reference

**MAIN:137**: `(benchmark subsample class counts in the Supplementary Material, \cref{sec:qks_benchmark}.1)`. The trailing `.1` is manually appended to a `\cref` of an SM *subsection*. It currently renders as "**Section 17.1.1**" — correct by accident, and it will silently point at the wrong place the moment an SM section is added or moved.

**Fix:** add `\label{sec:qks_protocol}` to the `\subsubsection{Evaluation protocol}` at SM:680 and reference it directly.

### 3.12 [LOW] SM section-number comments do not match the sections

The `%%% N. TITLE` banner comments have drifted out of sync with the actual `\section` order: `% 2. TOPOLOGICAL FINGERPRINT STATISTICS` (SM:114) sits above `\section{Per-fold activity prediction statistics}`; `% 3. CLUSTERING QUALITY METRICS` (SM:222) sits above `\section{PHCO fingerprint extraction bug}`; the ChEMBL banners run 9 → 9C → 9B → 9D (SM:403, 431, 488, 523); `% 4. DISCUSSION` (SM:585) appears after section 16. Harmless to the reader but a maintenance hazard.

### 3.13 [LOW] Section balance

| Section | Words |
|---|---|
| Introduction | 1,110 |
| Methods | 1,573 |
| Results | 1,371 |
| **Discussion** | **1,776** |
| Conclusion | 291 |

Discussion is the longest section and exceeds Results by 30 %. Combined with §3.3 (the SM duplicates much of it) and §3.7, roughly 400 words of Discussion can go without loss. The Conclusion (291 words, MAIN:388) is a single paragraph that restates every number already in the Abstract and Discussion; ~150 words would serve better.

### 3.14 Float callout audit — complete

**MAIN (2 tables-worth of labels on 1 table, 2 figures):**

| Float | Label | Line | Cited at |
|---|---|---|---|
| Table 1 | `tab:benchmark` | 253 | 251, 301, 345, 376 |
| Table 1 (**same table**) | `tab:hybrid` | 281 | 217, 251, 315×2, 345, 353, 380 |
| Figure 1 | `fig:paradox` | 288 | **NONE — uncited** |
| Figure 2 | `fig:joint_h1_rrs` | 365 | 380 |

**SM (14 tables S1–S14, 9 figures S1–S9, 1 algorithm):**

| Float | Label | Line | Cited at |
|---|---|---|---|
| Fig S1 | `fig:h1_rrs` | 101 | SM 639, 641 |
| Table S1 | `tab:sm_s4_perfold` | 125 | SM 123 |
| Table S2 | `SM-tab:tda_stats` | 183 | MAIN 245, 247; SM 179 |
| Fig S2 | `SM-fig:persistence` | 211 | MAIN 247; SM 179 |
| Table S3 | `SM-tab:clustering` | 241 | MAIN 303; SM 237 |
| Table S4 | `SM-tab:ga_discriminator` | 270 | MAIN 311, 345; SM 268, 608 |
| Fig S3 | `SM-fig:ga_discriminator` | 286 | MAIN 311, 345; SM 268, 608 |
| Table S5 | `tab:qp_optimisation` | 306 | SM 302 |
| Fig S4 | `fig:qp_heatmap` | 323 | SM 304 |
| Fig S5 | `fig:qp_effects` | 330 | SM 304 |
| Table S6 | `tab:mc_uncertainty` | 346 | SM 344 |
| Table S7 | `tab:scalability` | 373 | SM 371 |
| Table S8 | `tab:effect_sizes` | (external `\input`) | SM 397 |
| Table S9 | `tab:chembl_enrichment` | 411 | SM 409 |
| Table S10 | `tab:chembl_validation_top10` | 439 | SM 437 |
| **Table S11** | `tab:chembl_validation` | **464** | **NONE — uncited** |
| Table S12 | `SM-tab:sota` | 496 | MAIN 376; SM 494, 544 |
| **Table S13** | `tab:topologynet_analog` | **531** | **NONE — uncited** |
| Fig S6 | `fig:sm_tda_promiscuity` | 577 | MAIN 325; SM 575 |
| Fig S7 | `SM-fig:domain` | 616 | MAIN 345 (SM never cites it) |
| Alg S1 | `SM-alg:qkernel` | 663 | MAIN 192, 194 |
| Table S14 | `SM-tab:qkernel` | 691 | MAIN 279, 301, 303, 311, 353; SM 599, 608, 681 |
| Fig S8 | `SM-fig:tensor` | 714 | MAIN 178, 297 (SM never cites it) |
| Fig S9 | `SM-fig:tne_parity` | 721 | MAIN 321 (SM never cites it) |

**[HIGH] Uncited floats — 3 total:**
1. **MAIN Figure 1** (`fig:paradox`, MAIN:288) — see §3.2.
2. **SM Table S11** (`tab:chembl_validation`, SM:464) — the expanded 77-compound ChEMBL search. The section text (SM:437) cites only Table S10; the S11 results (including the three active PfATP4 analogues) are never pointed at. Add "…are reported in \cref{tab:chembl_validation}" at SM:437.
3. **SM Table S13** (`tab:topologynet_analog`, SM:531) — the MLP-vs-RF comparison. SM:547 discusses the numbers ("The MLP underperforms RF by ΔAUC = −0.061") but never references the table. Add `\cref{tab:topologynet_analog}` at SM:529 or 547.

---

## 4. LaTeX / BIB HYGIENE (commands run)

### 4.1 Compilation

Both documents were compiled in an **isolated mirror** of the repo tree under the session scratchpad (sources, `Graphics/`, `Bibliography_Paper3.bib` and `results/p3_effect_sizes/` copied verbatim) so that nothing in the working tree was modified. Build loop: `latexmk -C`, then main → SM → main → SM → main with

```
latexmk -pdf -interaction=nonstopmode -file-line-error <file>.tex
```

**Result as the files stand today:**

| Document | Exit code | TeX errors (`file:line:`) | Undefined refs | Undefined citations | Multiply-defined | Pages |
|---|---|---|---|---|---|---|
| `Paper3_Quantum_InspiredV2608` | **0** | 0 | 0 | 0 | **7** (natbib citations) | 19 |
| `Paper3_Quantum_Inspired_SM_V2608` | **12** | **44** | 0 | **10** | 0 | 19 (corrupt) |

---

#### [CRITICAL] The SM does not compile — `xr-hyper` + underscored external filename

`latexmk` exit **12**; 44 TeX error lines. Quoted from `Paper3_Quantum_Inspired_SM_V2608.log`:

```
./Paper3_Quantum_Inspired_SM_V2608.tex:123: Missing $ inserted.
<inserted text>
                $
l.123 ...e main manuscript (\cref{M-tab:benchmark}
                                                  ).
./Paper3_Quantum_Inspired_SM_V2608.tex:123: Extra }, or forgotten $.
\@templabel ...}{Paper3_Quantum_InspiredV2608.pdf}
```

and, from the latexmk summary:

```
Latexmk: Summary of warnings from last run of *latex:
  Latex failed to resolve 10 citation(s)
Latexmk: Errors, so I did not complete making targets
Collected error summary (may duplicate other messages):
  pdflatex: Command for 'pdflatex' gave return code 1
```

**Root cause.** SM:41 loads `\usepackage{xr-hyper}` and SM:52 declares `\externaldocument[M-]{Paper3_Quantum_InspiredV2608}`. When the main `.aux` exists, `xr-hyper` builds a hyperlink target containing the external **filename**, `Paper3_Quantum_InspiredV2608.pdf`. That string contains `_`, which is catcode 8 (subscript) in text mode → "Missing $ inserted" at every `\cref{M-...}`. There are exactly 8 such references (SM:123, 127, 231, 302, 308, 498, 520 → `M-tab:benchmark`; SM:599 → `M-tab:hybrid`), producing 44 error lines.

**Consequences beyond the exit code:**
- The output is *visibly corrupt*. `pdftotext` on the freshly built SM, page 2: `Headline AUC values in the main manuscript (Table 1Paper3Q uantumI nspiredV 2608.pdf ) are from the canonical panel benchmark.` The internal filename is typeset into the caption.
- Because `pdflatex` aborts, **BibTeX never resolves the SM bibliography**: 10 undefined-citation warnings for `topologynet_2018`, `dgril_2026`, `jensen2019augmenting`, `tartarus_2024`, `jamali2025spectral`, `temgoua2027md`.
- The SM PDF currently committed at `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2608.pdf` renders "(Table 1)" correctly, so it was produced under a build state that no longer reproduces. **The committed PDF is not reproducible from the committed sources.** That alone is disqualifying for a cheminformatics venue that expects reproducibility.

**Fix (verified).** Changing SM:41 from `\usepackage{xr-hyper}` to `\usepackage{xr}` — which is what the main manuscript already uses (MAIN:46) — makes the SM compile clean. Re-running the full loop after that one-character-class change:

| Document | Exit | Errors | Undef refs | Undef cites | Multiply-def | Pages |
|---|---|---|---|---|---|---|
| MAIN | 0 | 0 | 0 | 0 | 7 | 19 |
| SM | **0** | **0** | **0** | **0** | 0 | 19 |

and page 2 now reads "…in the main manuscript (Table 1) are from the canonical panel benchmark." The only cost is that cross-document references stop being clickable. If clickable cross-doc links are wanted, the alternative fix is to rename both `.tex` files to underscore-free names (e.g. `Paper3-QuantumInspired-V2608.tex`).

---

#### [HIGH] The SM `\input`s a file from outside the manuscript directory

**SM:399**: `\input{../../results/p3_effect_sizes/p3_effect_sizes_table.tex}`

This escapes `manuscript/LaTeX/` two levels up into the analysis results tree. On my first build attempt (before I mirrored `results/`) this produced a **fatal** failure:

```
! LaTeX Error: File `../../results/p3_effect_sizes/p3_effect_sizes_table.tex' not found.
./Paper3_Quantum_Inspired_SM_V2608.tex:399: Emergency stop.
```

BMC submission requires a self-contained upload of the LaTeX sources. As written, the SM will not build on the publisher's compile farm. **Fix:** copy `p3_effect_sizes_table.tex` into `manuscript/LaTeX/` (e.g. as `table_effect_sizes.tex`) and `\input` it by bare filename; keep a build script that regenerates it from `results/`.

Note this also means Table S8 (`tab:effect_sizes`) is defined in a file outside the manuscript that I could not audit for caption/format consistency with the other SM tables.

---

#### [HIGH] Multiply-defined citations in the main manuscript (7 warnings)

```
Package natbib Warning: Citation `temgoua2027md' multiply defined.
Package natbib Warning: Citation `topologynet_2018' multiply defined.
Package natbib Warning: Citation `dgril_2026' multiply defined.
Package natbib Warning: Citation `jensen2019augmenting' multiply defined.
Package natbib Warning: Citation `tartarus_2024' multiply defined.
Package natbib Warning: Citation `jamali2025spectral' multiply defined.
Package natbib Warning: There were multiply defined citations.
```

**Root cause.** MAIN:48 declares `\externaldocument{Paper3_Quantum_Inspired_SM_V2608}` *without a prefix*, so the SM's `\bibcite` entries are imported wholesale into the main document's citation table, colliding with the main document's own entries for the 6 shared keys.

**Consequence.** The SM runs its own independent `unsrtnat` bibliography (BibTeX reports `You've used 6 entries` for the SM vs `37 entries` for the main). Under `unsrtnat` (numeric, order-of-appearance) the same work carries **different numbers in the two documents** — `topologynet_2018` is [1] in the SM but a different number in the article. Any reader cross-walking a citation between the two documents will be misled.

**Fix (both parts):**
1. Give the external document a prefix at MAIN:48 — `\externaldocument[SMX-]{Paper3_Quantum_Inspired_SM_V2608}` — which stops the bibcite collision. (Note this will require renaming main-text references to raw SM labels, currently `\cref{fig:sm_tda_promiscuity}` at MAIN:325 and `\cref{sec:qks_benchmark}` at MAIN:137.)
2. Better still for the reader: keep the SM's reference list but state at its head that numbering is independent of the article, or switch the SM to author–year output so no number collision is possible.

---

#### Also observed at compile time

- **[LOW]** MAIN:47 declares `\externaldocument[P2-]{../../Project2_Polypharmacology_MD_ValidationV2607/manuscript/LaTeX/Polypharmacology_MD_Validation_V2607}`. That `.aux` **does not exist** in the working tree, and grep shows **no `P2-` prefixed reference is used anywhere** in either document. Dead declaration that also escapes the manuscript directory — delete it.
- **[LOW]** Underfull `\hbox (badness 10000)` in the alignments at SM:359 and SM:385 (Tables S6 and S7 — two-column `tabularx` with a `S` column). Cosmetic.

### 4.2 Bibliography audit

Commands: key extraction with `grep -oP '^@\w+\{\s*\K[^,]+'`, citation extraction with `grep -ohP '\\cite[a-z]*\{\K[^}]+'` over MAIN + SM, then `comm`.

| Check | Result |
|---|---|
| Total entries | 66 |
| **Duplicate keys** | **0** — clean |
| Distinct keys cited (MAIN + SM) | 37 |
| Cited-but-missing-from-bib | **0** — clean |
| **Entries never cited** | **29** |
| Cited entries with no `doi =` field | **15 of 37 (41 %)** |

#### [MEDIUM] 29 uncited bib entries (44 % of the file)

```
activity_cliff_2026            addressing_infectious_diseases_africa_2025
contractn_2021                 data_reuploading_2020
deepmirror2026dd4gh            fingerprint_comparison_2020
giotto_tda_2021                gudhi_2024
healthpolicy2026dd4gh          himnet_2026
itensor_2026                   ml_quantum_chemistry_2026
mmv2026dd4gh                   molecular_fingerprints_2026
mol_tdl_2026                   napreca_2026
nvidia_gtc_2026                persistent_local_laplacian_2026
pfamr_2026                     plasmodb_2026
qiskit_2026                    qkdti_2025
qml_drug_discovery_2026        quantum_kernel_materials_2026
quimb_2024                     techinformed2026dd4gh
tn4ml_github                   topology_molecular_representations_2025
wwarn_2026
```

These are inert (BibTeX only emits cited entries), so they do not affect the PDF. But several are substantive and arguably *should* be cited — `giotto_tda_2021` and `gudhi_2024` are the two obvious alternative persistent-homology libraries a TDA reviewer will ask about versus Ripser; `quimb_2024` and `itensor_2026` are the standard tensor-network libraries versus TensorLy; `qiskit_2026` is the obvious alternative to PennyLane. Their presence-but-absence suggests the software-choice justification was drafted and dropped. Either cite them in §2.11 Software as the alternatives considered, or prune the file.

#### [MEDIUM] 15 of 37 cited entries lack a DOI

| Key | Type | Has instead |
|---|---|---|
| `temgoua2027md` | article | **nothing** |
| `pennylane_2024` | misc | **nothing** |
| `tensorly_2019` | article | **nothing** |
| `rdkit_2024` | misc | **nothing** |
| `umfh_2026` | article | **nothing** |
| `who2024malariareport` | techreport | **nothing** |
| `todd_2023` | inproceedings | url |
| `tda_review_2025` | article | url |
| `tensornet_2023` | inproceedings | url |
| `tn_efficient_2026` | article | url |
| `ripser_2019` | article | url |
| `tartarus_2024` | inproceedings | url |
| `pactnet_2025` | article | url |
| `q2sar_2025` | article | url |
| `jamali2025spectral` | article | url |

The six with **neither DOI nor URL** are the priority — BMC's reference style requires a DOI where one exists, and all six have one (`tensorly_2019` = JMLR, `ripser_2019` = J Appl Comput Topol 10.1007/s41468-021-00071-5, PennyLane = arXiv 1811.04968, WHO World Malaria Report = a WHO ISBN/URL). `temgoua2027md` (the companion MD paper) has neither DOI, URL nor eprint — if it is still unpublished it must be marked "submitted"/"in preparation" explicitly, because the main text leans on it for the entire §4.7 RRS analysis.

---

## 5. DECLARATIONS CHECKLIST

| Item | Status | Location | Note |
|---|---|---|---|
| **Data availability** | ⚠️ **Present but internally contradictory** | MAIN:394–396; SM:108–110; COVER:42 | See [HIGH] below |
| **Code availability** | ⚠️ **Partial** | MAIN:235 ("All code is available at the project repository"), MAIN:396 item (6) | No standalone heading; no version/tag/commit; no separate software licence statement beyond "MIT" applied to the repo as a whole. BMC folds code into "Availability of data and materials" — acceptable, but the sentence at MAIN:235 has no URL and duplicates MAIN:396 imprecisely. |
| **CRediT / Authors' contributions** | ✅ **Present, complete** | MAIN:402–404 | All 5 authors have roles; roles use CRediT vocabulary; ends with "All authors read and approved the final manuscript" as BMC requires. Heading is "Authors' Contributions" — BMC style is "Authors' contributions" (lowercase c). |
| **Funding** | ✅ **Present** | MAIN:406–408 | Standard no-funding declaration. Note tension with MAIN:400 / MAIN:227, which credit the "University of Yaoundé I HPC facility" and a 32-worker cluster — in-kind computational support is normally declared here too. |
| **Ethics approval and consent to participate** | ✅ **Present** | MAIN:410–412 | "Not applicable" with justification. Correct. |
| **Consent for publication** | ✅ **Present** | MAIN:414–416 | "Not applicable" with justification. Correct. |
| **Competing interests** | ✅ **Present** | MAIN:418–420 | "The authors declare no competing interests." Correct. |
| **AI-use disclosure** | ✅ **Present, strong** | MAIN:422–424 | Names the tool (Claude, Anthropic), the scope (code, analysis scripting, drafting/editing), asserts human review and responsibility, and states no AI authorship. Exceeds the minimum. |
| **Acknowledgements** | ✅ Present | MAIN:398–400 | |
| **List of abbreviations** | ❌ **Missing** | — | BMC requests one. The paper defines ≥ 12 (TFP, TNE, QKS, QK, ECFP4, FCFP4, AP, BPF, PHCO, MACCS, RRS, TDA, PH, CR, NISQ, IQP, TA, CH, DB, ECE). |
| **ORCID iDs** | ❌ **Missing** | MAIN:75–79 | Only the corresponding author has an email; no ORCIDs. BMC strongly encourages; required for the corresponding author at some BMC titles. |
| **Trial registration** | n/a | — | Not applicable to a computational study. |

### [HIGH] Data-availability statements contradict each other across three files

- **MAIN:396**: "All data … **will be deposited** on Zenodo (DOI: 10.5281/zenodo.19608875, **reserved**) … the deposit **will be made available upon publication**, and the repository is available to reviewers on request."
- **SM:110**: "All data supporting the main manuscript and this Supplementary Material **are publicly available** on Zenodo (DOI: https://doi.org/10.5281/zenodo.19608875)".
- **COVER:42**: "All data and code **are deposited** on Zenodo (DOI: …) and GitHub under the MIT licence."

The SM and cover letter assert present-tense public availability; the main manuscript says the deposit does not yet exist and access is by request. Two of the three are wrong, and an editor comparing the cover letter to the article will notice immediately. J. Cheminformatics expects data to be accessible to reviewers at submission; "available on request" is generally not accepted for a paper whose entire contribution is a benchmark.

**Fix:** make the Zenodo deposit and publish it (or create a reviewer-access token), then use one identical sentence in all three files. If the deposit genuinely cannot be public before acceptance, all three must say so consistently and the cover letter must supply the reviewer token.

### [MEDIUM] Heading names do not match BMC style

BMC/J. Cheminform expects a single **Declarations** block with fixed sub-headings. Current vs expected:

| Current (MAIN) | BMC expected |
|---|---|
| `Data Availability` | `Availability of data and materials` |
| `Authors' Contributions` | `Authors' contributions` |
| `Competing Interests` | `Competing interests` |
| `Acknowledgments` | `Acknowledgements` |
| (sections are free-standing) | wrap all of the above in `\section*{Declarations}` |
| — | add `Abbreviations` before Declarations |

---

## 6. SEVERITY SUMMARY

### CRITICAL (2)
1. **SM fails to compile**, exit 12, 44 TeX errors, 10 unresolved citations, and typesets the internal PDF filename into captions — `xr-hyper` + underscored external filename (SM:41 / SM:52; errors at SM:123, 127, 231, 302, 308, 498, 520, 599). The committed SM PDF is not reproducible from the committed sources. Verified fix: use `xr` instead of `xr-hyper`.
2. **Truncated sentence in Methods** (MAIN:219) — "a grid search evaluated 60 combinations" ends mid-clause with no period, and Phase 2 of the two-phase protocol is never described despite being cited as canonical throughout.

### HIGH (10)
3. Title overclaims: "paradoxes" plural (only one is resolved; the second is explicitly *not*, MAIN:363), and "tensor-network" is credited with a persistent-homology-only result (MAIN:73).
4. Abstract is unstructured (243 words, 7 sentences) where J. Cheminform requires Background/Results/Conclusions (MAIN:99–101).
5. **MAIN Figure 1 (`fig:paradox`, MAIN:288) is never cited**; consequently Figure 2 is cited before Figure 1.
6. Two SM tables uncited anywhere: **Table S11** (`tab:chembl_validation`, SM:464) and **Table S13** (`tab:topologynet_analog`, SM:531).
7. Nine main-text paragraphs duplicated in the SM at 0.50–0.98 similarity; SM §16–§17 (SM:555–654) are a second copy of the article's Discussion.
8. `h1_rrs_class_violin.png` appears as both MAIN Figure 2 and SM Figure S1 with near-identical captions.
9. Methods §2.9 (MAIN:229–231) promises ChemGraphX Spearman correlations and a UMFH diversity comparison; neither is reported anywhere (0 numeric results in either document).
10. ChEMBL validation (SM §12–13, Tables S9–S11) and the MC-uncertainty analysis (SM §10, Table S6) are never mentioned in the main text (`grep -ci chembl` on MAIN = 0).
11. SM `\input`s `../../results/p3_effect_sizes/p3_effect_sizes_table.tex` (SM:399) — outside the manuscript directory; fatal "Emergency stop" if the tree is not present, so the SM will not build from a self-contained submission package.
12. 7 multiply-defined citations in MAIN, caused by the unprefixed `\externaldocument` at MAIN:48; the SM's independent numeric bibliography gives the same works different numbers in the two documents.
13. Data-availability statements contradict each other across MAIN:396 ("will be deposited … upon publication"), SM:110 ("are publicly available") and COVER:42 ("are deposited").

### MEDIUM (17)
Anti-AI/inflated prose at MAIN:286, 311, 319, 378 and SM:569, 608 (6); inflated phrasing beyond the regex at MAIN:127 ×2, 286, 307/SM:563, 311, 325, 353, 376 (8 — the MAIN:307 case is contradicted 4 lines later and is arguably HIGH); `tab:hybrid` and `tab:benchmark` both label the same table (MAIN:256 + MAIN:281, both resolve to "Table 1") while MAIN:315 introduces it as if it were a second table; MAIN §3.6 (305–307) is a Results subsection with no results; SM Data Availability stranded at SM:108; SM floats cited from MAIN in scrambled order (S8→S2→S14→S3→S4→S9→S6→S7→S12); hand-built `\cref{sec:qks_benchmark}.1` at MAIN:137; "Introduction" should be "Background"; 29 uncited bib entries; 15 of 37 cited entries lack a DOI (6 lack DOI *and* URL); BMC declaration heading names and missing `Declarations` wrapper; missing Abbreviations list; SM:681 says the full panel is "19,836 molecules (14,721 active, 5,115 inactive)" while Table S14's own column header and all main-text references say *n* = 19,849 — one of the two labels is wrong.

### LOW (7)
MAIN:121 "robust to clustering resolution" (acceptable technical usage); MAIN:121 "rigorous"; MAIN:194 unsupported "is the appropriate"; SM:520 repeated "Key findings:" openings; dead `P2-` externaldocument at MAIN:47 (target `.aux` absent, no `P2-` reference used); SM banner comments out of sync with section order (SM:114, 222, 403/431/488/523, 585); underfull `\hbox` warnings at SM:359, 385; missing ORCIDs; Conclusion (291 words, MAIN:388) restates the Abstract verbatim in substance.

**Counts: CRITICAL 2 · HIGH 10 (11 with MAIN:307) · MEDIUM 17 · LOW 7 (9 items listed).**

---

## 7. DONE-CRITERIA COMPLIANCE

1. **Every anti-AI regex hit reported with line number and a written replacement sentence** — §1.1. All 7 hits (MAIN:121, 286, 311, 319, 378; SM:569, 608; COVER: none) quoted in context with a concrete replacement sentence each; 12 further inflated constructions the regex misses are tabulated in §1.2 with replacements.
2. **Compilation actually run, exit code and counts quoted from the log** — §4.1. `latexmk -pdf -interaction=nonstopmode -file-line-error`, isolated mirror, 5-pass loop. MAIN exit **0** / 0 errors / 0 undefined refs / 0 undefined citations / **7 multiply-defined**. SM exit **12** / **44** TeX error lines / 0 undefined refs / **10 undefined citations** / 0 multiply-defined. Log excerpts quoted verbatim, including the `\@templabel ...}{Paper3_Quantum_InspiredV2608.pdf}` line that identifies the cause and the `Emergency stop` from the missing `\input`. The `xr` fix was applied in the mirror and re-verified: SM exit **0**, 0 errors, 0 undefined refs, 0 undefined citations.
3. **Every float in both documents checked for an in-text callout; uncited floats listed** — §3.14. All 4 main-document labels (2 on one table + 2 figures) and all 24 SM floats (14 tables S1–S14, 9 figures S1–S9, 1 algorithm) tabulated with every citing line. Uncited: **MAIN Figure 1 (`fig:paradox`)**, **SM Table S11 (`tab:chembl_validation`)**, **SM Table S13 (`tab:topologynet_analog`)**.
4. **Declarations checklist with present/missing per item** — §5. 13 items: 7 present and complete, 2 present but flawed (data availability contradictory across three files; code availability partial), 2 missing (Abbreviations, ORCIDs), 1 n/a, plus a heading-name conformance table against BMC style.
