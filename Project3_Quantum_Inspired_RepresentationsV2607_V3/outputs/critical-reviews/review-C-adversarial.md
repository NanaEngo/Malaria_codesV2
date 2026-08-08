# Review C — Adversarial (hostile but fair), *Journal of Cheminformatics*

**Manuscript:** `manuscript/LaTeX/Paper3_Quantum_InspiredV2608.tex` (19 pp.) + `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2608.tex` (19 pp.)
**Reviewed against:** `results/`, `scripts/`, `README.md`. Explicitly **not** read: `outputs/analysis/analysis-ledger.md`, `project-tracking.md`.
**Reviewer stance:** find the arguments that would sink this paper in review.
**Date:** 2026-08-06

---

## 0. VERDICT

> **REJECT** in its current framing — resubmittable as a repositioned paper (the underlying work is salvageable and the honest-negative core is genuinely publishable, but not under this title, abstract, or contribution list).

**The two reasons that dominate the verdict:**

1. **The headline descriptor is not the descriptor the Methods define, and the manuscript states the opposite.** Methods §2.3.3 (main:159–163) defines TFP as a **12-dimensional** vector. The deposited code that produced the Table 1 value defaults to `--tfp-enriched` and builds a **78-dimensional** vector (33 H-features + 25 persistence-image + 20 Betti). I reproduced both: **78-dim → AUC 0.8759** (= the published 0.876); **12-dim, exactly as defined in the Methods → AUC 0.8473**. The Limitations paragraph (main:376) asserts that enrichment "showed no improvement over the 12-feature TFP baseline … consistent with the canonical full-library TFP AUC of 0.876." On the canonical panel that is false by **+0.029 AUC**, and the canonical 0.876 *is* the enriched number. A reader following the Methods cannot obtain the published result; a reader following the code obtains a descriptor the paper never defines. This alone is submission-blocking.

2. **The benchmark that the entire ranking rests on is not a valid held-out evaluation, and the paper's own headline statistic proves it.** The library was produced by STONED-SELFIES mutation from 850 seeds and retains **69.3 % of seed scaffolds** (main:100). Evaluation is plain random 5-fold `StratifiedKFold` (main:227). Analogue series are therefore split across train and test. The strings *"scaffold split"*, *"group split"*, *"GroupKFold"* and *"leakage"* appear **nowhere** in either document. Worse, the labels are the output of another ML model (Ersilia `eos80ch`, main:137), so "ECFP4 is the strongest single descriptor (0.948)" may in substantial part measure descriptor kinship with the label-generating model rather than chemistry. The paper's central empirical claim — the descriptor ranking — is therefore not established, which also removes the ground on which every "complementary but lower signal" statement stands.

---

## 1. THE CENTRAL TENSION — is this a contribution or a negative result in a methods-paper costume?

**Ruling: it is a negative result wearing a methods-paper costume, but there is a real contribution underneath it — a different one from the one on the cover.**

### 1.1 What the data actually say

| Claim as framed | What the deposited data show |
|---|---|
| "We introduce three quantum-inspired representations" (main:100, 388) | Two of the three lose to a 2010 baseline by large margins (TFP −0.072, TNE −0.226). The third (QKS) is statistically indistinguishable from a tuned RBF (`results/p3_qks_summary_n19849.txt`). |
| "positioning quantum-inspired methods as effective complementary tools" (main:388) | No experiment in the paper demonstrates complementarity. Complementarity requires showing ECFP4 **+** TFP/TNE/QKS > ECFP4. **That experiment is never run.** The hybrid contains no ECFP4. |
| "the hybrid … above every standalone quantum-inspired descriptor" (main:100) | True and irrelevant — clearing your own weakest baselines is not evidence of value against the field standard. |

### 1.2 CRITICAL — the "complementary" claim is asserted, never tested

**Severity: CRITICAL.** `main:100`, `main:345`, `main:380`, `main:388`; `SM:595`, `SM:597`.

The manuscript's fallback position, repeated five times, is that these representations are *complementary* to ECFP4. The single experiment that would test this — an ECFP4+TFP+TNE+QK concatenation — does not exist in `results/p3_hybrid_benchmark.csv` (descriptors present: AP, BPF, ECFP4, FCFP4, Hybrid, MACCS, PHCO, TFP, TNE — no ECFP4-augmented row). The Discussion even prescribes the missing experiment ("future hybrid approaches should weight ECFP4 features more heavily", main:349) while presenting its absence as a finding. A reviewer will ask why a benchmark that took **26 seconds** on my workstation for ECFP4 (5-fold, 19,836 molecules, RF-200) was not extended by one concatenation.

**This is the paper's fatal structural gap.** Everything else is repairable; this is the experiment that decides whether the paper has a positive result at all, and it is one afternoon of compute.

### 1.3 What the actual defensible contribution is

There is one, and it is good:

> A properly-baselined, adequately-scaled **negative result** on simulated quantum kernels for molecular activity prediction — the first in this repo's literature set to (a) tune the classical RBF `gamma` by inner CV rather than leaving it at default, (b) run to *n* = 19,836 rather than the few-hundred-molecule scale typical of the QML-for-chemistry literature, and (c) publish a forensic account of **two** prior artefacts of its own making: an untuned-RBF false positive (QK 0.936 vs RBF 0.105) and a circuit/scaling-mismatch false negative (0.659 vs 0.825), both retracted with the deposited files that overturn them (main:301, main:378; `SM:693`).

That is a real service to a field with a serious positive-results bias. **The manuscript does not frame itself that way.** It buries this in §4.5 and the Limitations, and leads with a title asserting that these representations "resolve chemical paradoxes."

### 1.4 HIGH — "quantum-inspired" is a misnomer that a J Cheminform reviewer will challenge

**Severity: HIGH.** `main:100`, title, keywords (main:103).

Persistent homology has no quantum content whatsoever; it is 1990s computational topology. Tucker decomposition is 1966 multilinear algebra. Grouping them with a simulated quantum kernel under the banner "quantum-inspired" is a marketing frame, not a methodological one — and it is the frame that generates the paper's coherence problem, because it forces three unrelated descriptors into a single hybrid whose ablation (§2) shows they do not belong together. Conversely, QKS is not quantum-*inspired*; it is a classically-simulated quantum kernel. The category is wrong in both directions.

---

## 2. THE ABLATION — does the framing survive one of its own pillars being a net negative?

**Ruling: No. And the statistical treatment of that row is the paper's most serious integrity problem after §1.**

### 2.1 CRITICAL — selective significance testing on the one result that contradicts the framing

**Severity: CRITICAL.** `main:255` (Table 1 caption), `main:274`, `main:315`; data: `results/p3_ablation.csv`, `results/p3_hybrid_benchmark.csv`.

The manuscript attaches a *p*-value to every comparison that supports the narrative (hybrid vs ECFP4 `p < 0.0001`, QK vs RBF `p = 0.060/0.419`, QK vs linear `p ≤ 0.0006`, seven Bonferroni-corrected classical comparisons). For the one row that contradicts the framing it uses the word **"slightly"** and reports no test:

> "removing TNE slightly improves AUC (Δ = +0.011)" — main:274, echoed main:315.

I recomputed the paired *t*-tests from the deposited per-fold values (`p3_ablation.csv` vs the five `Hybrid,rf` rows of `p3_hybrid_benchmark.csv`):

| Ablation | mean AUC | Δ vs Hybrid (0.8876) | t (df=4) | **p** |
|---|---|---|---|---|
| Hybrid − TFP | 0.8736 | −0.0139 | −11.93 | 2.8 × 10⁻⁴ |
| **Hybrid − TNE** | **0.8990** | **+0.0114** | **+12.92** | **2.1 × 10⁻⁴** |
| Hybrid − QK | 0.8472 | −0.0404 | −19.44 | 4.1 × 10⁻⁵ |

All five folds improve when TNE is removed. **Removing TNE is a statistically significant improvement at p = 2.1 × 10⁻⁴** — a smaller p-value than two of the three comparisons the paper does report with stars. Describing this as "slightly improves" while p-valuing everything else is selective reporting, and it is exactly the pattern a hostile reviewer looks for.

### 2.2 CRITICAL — the paper's headline hybrid is a dominated configuration it never names

**Severity: CRITICAL.** `main:270`, `main:274`.

`Hybrid − TNE` **is** TFP+QK. At **AUC 0.899** it is the best quantum-inspired descriptor anywhere in the manuscript — better than the headline hybrid (0.888), better than TFP alone (0.876, paired *t* = 13.12, *p* = 1.9 × 10⁻⁴), better than QKS alone (0.823). It appears exactly once, in an ablation row, labelled by what was deleted rather than by what it is. The paper therefore ships a **strictly worse** descriptor as its product and hides the better one in a subtraction table. Any reviewer who reads Table 1 arithmetically will ask why.

### 2.3 HIGH — the ablation deltas are confounded by feature-count dilution and cannot support the attribution they carry

**Severity: HIGH.** `main:202–217`, `main:255`, `main:353`; `scripts/p3_hybrid_benchmark.py:339–367`.

The hybrid vector is TFP(78, per §1.1 — *not* 12) + TNE(192) + QK(30) ≈ **300 dims**, of which TNE is ~64 %. `cv_score` uses `RandomForestClassifier` at scikit-learn defaults (`scripts/p3_hybrid_benchmark.py:365`), i.e. `max_features='sqrt'`. Each split therefore samples ~17 of ~300 features, ~11 of them TNE — the descriptor that scores 0.722 alone. Removing TNE does not only remove information, it **triples the sampling probability of the informative features**. The observed +0.011 is exactly what dilution predicts.

The same confound flows the other way for QK: it is the smallest block (30 dims) and shows the largest deletion penalty, which the paper reads as "QKS is the principal positive contributor" (abstract main:100; main:217; main:353; `SM:599`). Neither attribution is licensed by this design.

**Required:** dimension-matched control (replace each removed block with same-dimension Gaussian noise or a permuted copy), or per-block permutation importance, or `max_features=1.0`. Until then the sentence "with QKS the principal positive contributor" should not appear in the abstract.

### 2.4 Does the framing survive?

No. The manuscript claims a *framework* of three components. Its own canonical ablation shows component 2 is a significant net negative, component 1 is 3.4× less important than the paper's own ranking implies once dilution is considered, and the best configuration is two-of-three. A "framework" whose ablation says "use two of our three parts" is not a framework; it is a descriptor selection exercise reported in the wrong direction.

---

## 3. NOVELTY CLAIMS — adjudicated one by one

Searched `first|novel|we introduce|we define|we propose|unprecedented` across both documents and `README.md`.

### In-manuscript claims (main:123, N5–N8)

| # | Claim (verbatim) | Verdict | Prior work that threatens it |
|---|---|---|---|
| **N5** | "a systematic TDA versus ECFP4 benchmark on natural product chemical space, **demonstrating that 1D persistent homology captures scaffold-level features invisible to classical fingerprints**" (main:123) | **INDEFENSIBLE** | Self-refuting: Table 1 (main:267) has ECFP4 0.948 > TFP 0.876. "Invisible to classical fingerprints" is never tested — no experiment isolates anything ECFP4 misses that TFP catches (see §1.2). **ToDD** \citep{todd_2023}, cited at main:123/165, already performs PH-based compound fingerprinting benchmarked against classical descriptors; **tda_pretraining_2026** and **tda_binding_affinity_2026** (main:117) already establish PH for molecular property prediction. The "on African NP space" qualifier is a dataset restriction, not a methodological novelty. |
| **N6** | "the application of persistent homology to **resolve** a chemical space paradox … by decomposing molecular topology into H₀ (connectivity) and H₁ (ring) components" (main:123) | **INDEFENSIBLE** (see §4) | No statistic supports it anywhere in either document. Fig. 1 caption promises "(Wilcoxon *p*-value)" (main:291) — **no p-value appears in the manuscript, the SM, or `results/`**, and no script generates the figure. The only quantitative evidence offered (main:337) is *classical*: scaffold-Tanimoto 0.379 vs whole-molecule 0.206. PH is decorative here. |
| **N7** | "a tensor network descriptor achieving 6.1× real-atom compression while retaining binding-relevant information" (main:123) | **WEAKLY DEFENSIBLE at best; the compression figure is against a strawman** | The 6.1× is measured against **the authors' own hand-built N×10×3 outer-product tensor** (main:171–186), an object no one else uses. Against any real baseline TNE is *larger*: 192 float64 = 1,536 bytes vs ECFP4 2,048 bits = 256 bytes — **TNE is 6× bigger than the descriptor it loses to.** The manuscript never states this. **PACTNet** \citep{pactnet_2025}, which the authors themselves cite at main:127 as "validating the compression ratio", already demonstrated topological compression of graph networks; being second is not novelty. "Retaining binding-relevant information": R² = 0.473 vs ECFP4 0.461 on **1 of 3** targets, losing on the other two by 0.114 and 0.183 (main:321). |
| **N8** | "an applicability domain analysis using quantum kernel density for natural product compounds" (main:123) | **INDEFENSIBLE — refuted by the paper's own data** | The only quantitative test of QK density as a domain discriminator is SM Table S6 (`SM:270–284`): **AUC 0.425–0.511 against a Tanimoto baseline at 1.000** — at or below chance at every *N*. §3.6 (main:305–307) contains **zero numbers**; Fig. S-domain (`SM:616–621`) has no generating script. Listing as a contribution an analysis whose only measurement shows it fails is the kind of thing that gets quoted back in a rejection letter. |

### README claims not in the manuscript (divergence is itself a problem)

`README.md:30–33` asserts four **"First"** claims that appear nowhere in the manuscript. If this README ships in the Zenodo/GitHub deposit — and `main:396` says it does — reviewers and readers will see them.

| # | Claim | Verdict | Threat |
|---|---|---|---|
| **N1** | "**First proof** that TNE … retains 3D physical binding affinity across 19,913 molecules" | **INDEFENSIBLE** | "Proof" from a single-target R² win of +0.012 with two-target losses of −0.114/−0.183. |
| **N2** | "**First** canonical benchmark showing QKS ≈ RBF at n=5,000 and n=19,849 — honest negative" | **Substance DEFENSIBLE; the word "first" is not** | **Q2SAR** \citep{q2sar_2025} (cited main:127) already benchmarks quantum multiple-kernel learning against classical RBF; **naleczcharkiewicz2024** and **kumar2024quantumdrug** (main:127) are systematic reviews of exactly this comparison space. Claim scale and baseline rigour, not primacy. |
| **N3** | "**First** TDA (H₁) correlation mapping scaffold **ring rigidity** to target promiscuity" | **INDEFENSIBLE — misreports its own data** | In `results/p3_physical_validation/p3_tda_promiscuity.csv`, `H1_count` ranks **18th** at ρ = −0.099. The three headline correlations are H0_count (−0.248), H0_entropy (−0.243), H1_entropy (−0.190) — see §7.1, these are molecular-size proxies, not ring rigidity. |
| **N4** | "Scaffold Paradox Resolution" | **INDEFENSIBLE** | Same as N6. |

### "We introduce three quantum-inspired molecular representations" (main:100, main:388)

**Verdict: defensible only in the weak sense of "assembled and named."** TFP is persistence-summary statistics (standard practice; the SM's own `PersStats` variant at `SM:504` *beats* TFP-12 with 22 features). TNE is `tensorly.decomposition.tucker` on a hand-built tensor. QKS is `pennylane.IQPEmbedding` + `SVC(kernel='precomputed')`. No new mathematical machinery is contributed. "Introduce" should be downgraded to "define and evaluate."

---

## 4. THE "SCAFFOLD PARADOX RESOLUTION" — genuine resolution or restatement?

**Ruling: RESTATEMENT, and the title's central verb ("resolve") is not earned.**

### 4.1 CRITICAL — the titular claim has no supporting statistic anywhere

**Severity: CRITICAL.** `main:73` (title), `main:284–293` (§3.3), `main:337`, `main:380`, `main:388`; Fig. 1 caption `main:291`.

§3.3 is **eleven lines of prose with not one number**. It contains no test, no effect size, no seed-vs-expanded comparison, no *n*. The figure caption explicitly promises "(Wilcoxon *p*-value)" — that *p*-value appears in neither document nor in `results/`. Meanwhile the two anchor statistics (92.6 %, 69.3 %) are **imported from the companion paper** \citep{temgoua2026antimalarial}, not measured here. So the paper's title asserts a resolution of a phenomenon it did not measure, using an analysis it did not report.

### 4.2 HIGH — the argument is circular, and the paper supplies the classical refutation itself

**Severity: HIGH.** `main:286`, `main:337`.

The "resolution" is: *whole-molecule similarity diverges (H₀) while ring systems are conserved (H₁)*. But "ring systems are conserved" **is the definition of 69.3 % Bemis–Murcko scaffold recovery**. Restating a scaffold-recovery statistic in homology notation is relabelling, not explanation. The paper then hands the reviewer the counter-argument at main:337: *"This is independently confirmed by scaffold-only Tanimoto (0.379) being 1.84× higher than whole-molecule Tanimoto (0.206)."* That sentence resolves the paradox **completely, using only RDKit fingerprints**, in one line, with no persistent homology at all. A reviewer will ask what PH added. The honest answer is: nothing.

### 4.3 HIGH — the mechanism attributed to SELFIES is asserted, not shown

**Severity: HIGH.** `main:286`.

"SELFIES string mutations primarily permute side-chains … which manifests mathematically as the preservation of the H₁ topology distributions." No mutation-level analysis exists — no before/after H₁ per mutation, no mutation-type stratification. This is a plausible story, not a result.

### 4.4 Would a reviewer accept that persistent homology explains it?

**No.** They would accept that PH *redescribes* it. To convert redescription into explanation the paper needs, minimally: (i) seed vs expanded H₀/H₁ distributions with the promised Wilcoxon statistics and effect sizes; (ii) a demonstration that H₁ tracks scaffold identity *better than* Bemis–Murcko scaffold hashing (i.e., that PH detects conserved scaffolds that BM misses); (iii) the script that makes Fig. 1. Item (iii) does not exist (see §6.3).

---

## 5. APPLICABILITY / IMPACT — does any downstream decision change?

**Ruling: No. Not one.**

### 5.1 CRITICAL — the paper demonstrates zero decision impact and its own Discussion says so

**Severity: CRITICAL.** `main:357`, `main:345`, `main:311`.

Searched for any prospective use, any selection, any ranking, any triage decision made with TFP/TNE/QKS. There is none. Every use is retrospective correlation on a fixed library. The paper's own conclusions on utility:

- main:357: *"the computational overhead of QKS is not justified for active compound prioritization; these quantum-inspired descriptors should be reserved for retrospective mechanistic analysis and small-scale lead optimization"* — an explicit statement of no decision impact.
- main:311: the applicability-domain use case is measured at **AUC 0.425–0.511** vs a Tanimoto baseline at 1.000.
- main:345: *"TFP adds value specifically for compounds with complex ring systems (≥3 fused rings)"* — **this subgroup analysis is never performed.** It is asserted twice (main:345, main:376) with no table, no *n*, no AUC. A reviewer will grep for it and find nothing.
- SM Table S8 (`SM:439–462`): all ten top candidates' nearest ChEMBL analogues are **experimentally inactive**. The only experimental contact the paper makes with reality is negative.

For *Journal of Cheminformatics*, where the readership is practitioners choosing descriptors, a paper that concludes "use ECFP4, which is what you already use" and demonstrates no decision that would change must be honest about that in the abstract. It currently ends the abstract on a size-confound caveat and the title on "resolve chemical paradoxes."

### 5.2 HIGH — the one subgroup claim that would rescue utility is unbacked

**Severity: HIGH.** `main:345`, `main:376`.

"TFP adds value primarily at the high-complexity tail — molecules with ≥3 fused rings or ≥2 stereocentres." If true, this is the paper's most useful practical statement. It is stated twice as fact and supported nowhere. Either run it (it is a `df.groupby` over an already-computed feature matrix — minutes of work) or delete both sentences.

---

## 6. REPRODUCIBILITY — traced as a reviewer would actually test it

I picked two headline claims and attempted to regenerate them from the repo, cold.

### 6.1 Trace A — "ECFP4 achieves the highest AUC (0.948)" (abstract main:100; Table 1 main:261)

**Result: ✅ REPRODUCED EXACTLY. This is the strongest part of the submission.**

| Step | Outcome |
|---|---|
| Find the command | ⚠️ **FRICTION.** `README.md:76–91` "Quick Start" lists five commands; the classical benchmark is **not among them**. Had to locate `scripts/p3_classical_benchmark_19849.py` by filename. |
| Inputs present | ✅ `results/p3_tda_fingerprints.csv`, `results/p3_tne_embeddings.csv`, `results/eos80ch_malaria_final_activity.csv` — all present. |
| Panel construction | ✅ `load_canonical_panel(None)` → **19,836** molecules, 74.21 % active. Matches `SM:681`. |
| Re-run | ✅ ECFP4 built in 3.7 s; 5-fold RF-200 CV in **26 s** on a workstation. |
| Per-fold agreement | ✅ `{0.946581, 0.949882, 0.948430, 0.952206, 0.940450}` — identical to `results/p3_classical_benchmark_19849.csv` **to 6 decimal places**. Mean **0.9475 ± 0.0040** = published 0.948. |

**What failed alongside it — HIGH severity:** the panel is **19,836**, but the manuscript labels the kernel benchmark **"n = 19,849"** in the abstract (main:100), Table 1 footnote (main:279), §3.5 (main:301), §4.5 (main:353), §4.7 (main:376, 378), the Conclusion (main:388), SM Table S13 column headers (`SM:698`), SM §7 (`SM:375–387`) and the filename `results/p3_qks_benchmark_n19849.csv`. Root cause found: `scripts/p3_hybrid_canonical_19849.sbatch:45` passes `--n-mols 19849`, which `load_canonical_panel` silently truncates via `.head(19849)` on a 19,836-row frame (`scripts/p3_hybrid_benchmark.py:195–196`). The SM contradicts the main text on this at `SM:681` ("the full canonical panel of 19,836 molecules"). **~10 occurrences of a wrong sample size, including in the abstract.**

### 6.2 Trace B — "TFP (TDA) AUC 0.876" (Table 1 main:267) and "removing TNE slightly improves AUC (Δ = +0.011)" (main:274)

**Result: ❌ FAILED to reproduce from the published method; ✅ reproduced only from undocumented code defaults.**

| Step | Outcome |
|---|---|
| TFP as **Methods §2.3.3 defines it** (12 features: entropy/count/max/mean × H₀,H₁,H₂ — main:159–163) | ❌ **AUC 0.8473.** Does not match the published 0.876. |
| TFP as **the code builds it** (`--tfp-enriched` default `True`, `scripts/p3_hybrid_benchmark.py:1276`, `:1401–1408`) | ✅ **78 dims** = 33 `H*` + 25 `pers_img_*` + 20 `betti_*`; **AUC 0.8759** = published 0.876 exactly. |
| Where the 78 comes from | `load_precomputed(..., "H")` matches **33** columns, not 12 (`results/p3_tda_fingerprints.csv` has 78 numeric columns). `README.md:42` correctly says "TFP: 78-dim" — **the README and the manuscript disagree.** |
| Manuscript's own statement about this | main:376 claims enriched TFP "showed no improvement over the 12-feature TFP baseline (0.867 vs 0.867)" and calls that "consistent with the canonical full-library TFP AUC of 0.876". On the canonical panel enrichment is worth **+0.0286**, and 0.876 *is* the enriched result. **Contradicted by the deposited code.** |
| Ablation values | ✅ `results/p3_ablation.csv` reproduces Table 1 exactly (0.8736 / 0.8990 / 0.8472 vs Hybrid 0.8876). |
| Re-running the ablation | ❌ **IMPOSSIBLE for a reviewer.** Only entry point is `scripts/p3_hybrid_canonical_19849.sbatch`, which hardcodes `/home/nanaengo/Malaria_codesV2/...` (lines 3–4, 21) and requests **12 h × 32 CPU × 80 GB SLURM**. No workstation path, no `--n-mols` guidance for a scaled-down reproduction in the README. |
| Significance of the TNE row | ❌ Not reported by the paper. Recomputed from deposited per-fold data: **p = 2.1 × 10⁻⁴** (§2.1). |

### 6.3 CRITICAL — three figures, including the titular one, have no generating script

**Severity: CRITICAL.** Repo-wide search (`grep -rln` over `*.py *.sh *.sbatch *.ipynb`) for `scaffold_paradox`, `applicability_domain`, `tensor_compression` returns **nothing**.

| Figure | Referenced at | Generator |
|---|---|---|
| `scaffold_paradox.pdf` — **Figure 1, the paper's titular claim** | main:290 | **ABSENT** |
| `applicability_domain.pdf` — Fig. S-domain, contribution N8 | `SM:618` | **ABSENT** |
| `tensor_compression.pdf` — Fig. S-tensor, the bond-dimension sweep cited in Methods (main:178) | `SM:716` | **ABSENT** |

The Data Availability statement (main:396) promises "(6) all analysis scripts." Three figures — one of them Figure 1 — cannot be regenerated. For J Cheminform, whose reviewers routinely check deposits, this is a direct hit.

### 6.4 HIGH — Methods describe an SVM evaluation that the deposited data do not contain

**Severity: HIGH.** `main:227` vs `results/p3_hybrid_benchmark.csv`.

Methods: *"Each representation was evaluated using Random Forest classifiers (200 trees) **and support vector machines** with 5-fold stratified cross-validation."* The deposited file contains **45 `rf` rows (9 descriptors × 5 folds) and exactly 5 `svm` rows — all `Hybrid`**. SVM was run for the hybrid only. No SVM result for any descriptor appears in any table. The Methods statement is false as deposited.

### 6.5 MEDIUM — build order is undocumented and the naive build fails

A cold `pdflatex` of the main manuscript yields **79 undefined-reference warnings** (every `SM-*` cross-reference), because `xr` needs the SM `.aux` to exist first. Building `Paper3_Quantum_Inspired_SM_V2608.tex` first, then the main file, gives **0 undefined references, 0 undefined citations, 19 pp. + 19 pp.** No README or Makefile documents this ordering. Also `main:47` `\externaldocument[P2-]{../../Project2_.../...}` points outside the deposit — a reviewer without the sibling project gets further failures.

### 6.6 MEDIUM — README is stale and contradicts the reviewed files

`README.md:16, 65–66` names `Paper3_Quantum_InspiredV2607.tex` / `_SM_V2607.tex`; the files under review are **V2608**. `README.md:16` says 18 pp. + 18 pp.; actual **19 + 19**. `README.md:4` asserts "✅ Submission-ready."

---

## 7. STATISTICS AND DATA QUALITY

### 7.1 CRITICAL — the size confound is diagnosed in one analysis and ignored in the structurally identical one

**Severity: CRITICAL.** `main:325`, `main:361`; `results/p3_physical_validation/p3_tda_promiscuity.csv`.

The authors deserve real credit for catching the H₁–RRS size confound (main:361: H₁ count vs MW ρ = 0.718; partial ρ ≈ 0). They then commit **the same error two paragraphs earlier** and draw a mechanistic conclusion from it:

> main:325: *"H₀ count (ρ = −0.248) … This provides a clear topological mechanism: lower topological complexity in ring structures (H₁) and structural components (H₀) endows candidate molecules with optimal conformational adaptability across multiple malaria targets, reducing steric clash penalties."*

**H₀ count is molecular size.** SM Table S2 (`SM:192`) gives mean H₀ count = **38.04**; main:186 gives mean atoms per molecule = **~39**. The three "highly significant" promiscuity correlates (H0_count, H0_entropy, H1_entropy) are all size/atom-count proxies. The finding is therefore the long-known docking artefact *"smaller ligands score better in more pockets"*, restated in homology notation and given a steric-clash mechanism it does not support. **No partial correlation controlling for MW or heavy-atom count is performed here**, although the machinery to do it exists in the very same repo (`scripts/p3_h1_rrs_partial_corr.py`).

Note further that the paper's own actual ring descriptor, `H1_count`, ranks **18th** at ρ = −0.099 — so the sentence attributes to "ring structures (H₁)" a signal that H₁ count does not carry. README N3's "ring rigidity → promiscuity" claim rests entirely on this.

### 7.2 HIGH — 78-way correlation scan reported without multiplicity control

**Severity: HIGH.** `main:325`, `SM:575`; `results/p3_physical_validation/p3_tda_promiscuity.csv` (78 features tested).

The manuscript reports the top three of a **78-feature** scan as "highly significant … all p < 10⁻¹³⁷", having stated in Methods (main:227) that "Multiple testing correction used Bonferroni adjustment across the pairwise comparisons within each benchmark family." The correction is not applied here and the family size is not disclosed. (The top hits survive any correction; the issue is the undisclosed scan and the fact that **26 of the 78 features are reported at p < 0.05** without that being stated.)

### 7.3 HIGH — degenerate columns inside the descriptor that is actually benchmarked

**Severity: HIGH.** `results/p3_tda_fingerprints.csv`.

Direct check of the 78 numeric TFP columns:

- **2 constant (zero-variance) columns:** `H0_birth_mean`, `H0_birth_std` — carry no information and are fed to every model.
- **5 exactly-duplicated column pairs:** `H0_mean_pers ≡ H0_death_mean`, `H0_birth_mean ≡ H0_birth_std`, `betti_0 ≡ betti_1 ≡ betti_2`.

Visible in the deposited promiscuity table as identical Spearman ρ to 16 significant figures (`betti_0/1/2/3` all 0.09928770583555604; `H0_mean_pers`/`H0_death_mean` both −0.009134473009491183). These are feature-construction bugs in the descriptor whose AUC is the paper's Table 1 headline, and they are visible in a file the paper deposits.

### 7.4 HIGH — self-contradictory compute-cost claims used to justify an incomplete experiment

**Severity: HIGH.** `main:323` and `SM:573` vs `SM:383` and `results/p3_qks_benchmark_n19849.csv`.

- `SM:573` / `main:323`: the polypharmacology benchmark at *n* = 1,000 *"was terminated because a single 900 × 900 kernel matrix exceeded practical wall time."*
- `SM:383` + `results/p3_qks_benchmark_n19849.csv` (`qk_time_s = 755.2` for fold 1; SM quotes 817 s mean): a **19,836 × 19,836** state-vector kernel builds in **~13 minutes**.

A 900 × 900 kernel is ~**480× smaller**. The stated justification for abandoning the experiment is contradicted by the paper's own timing table by nearly three orders of magnitude. Either the polypharmacology run used the deprecated pairwise path (in which case say so, and note it should have used the state-vector path documented at `SM:686`), or the abandonment is unjustified. As written, a reviewer reads this as an experiment dropped because it was not working.

### 7.5 HIGH — reporting 3 of 5 folds from a terminated run, all below chance, as a result

**Severity: HIGH.** `main:323`, `SM:573`; `results/p3_physical_validation/p3_physical_validation_summary.txt`.

The polypharmacology QKS result is: a partial *n* = 500 run that *"completed three folds before termination"* (per-fold AUC 0.513 / 0.658 / 0.825 — a 0.31 spread), plus an *n* = 50, 2-fold pilot. The deposited summary shows that pilot at **QKS 0.356, RBF 0.303, Linear 0.583 — every kernel below chance**, with the file itself printing *"insufficient paired data (n=2)"* for all three significance tests. The manuscript renders this as *"place QKS within noise of the tuned RBF baseline"* (`SM:573`), which is technically true and materially misleading: nothing here is above random. Partial folds from an aborted run should be removed from the manuscript, not reported.

### 7.6 MEDIUM — an effect-size table whose own caption concedes it is uninterpretable

**Severity: MEDIUM.** `SM:399` → `results/p3_effect_sizes/p3_effect_sizes_table.tex`.

Cohen's *d* values of **+63.84** (PHCO), +37.91 (TNE), +17.25 (TFP), all labelled "large", with **Power = 1.000** in every row. The caption concedes *"because the full-library folds are very consistent, the resulting d values are large, so the absolute ΔAUC is the more interpretable effect metric"* — i.e. the table's own author states the table's numbers should not be used. Dividing by the SD of correlated CV-fold differences does not produce a Cohen's *d*. Post-hoc power of 1.000 is not informative. The table also **omits the paper's own contributions** (Hybrid, QKS) while including all six classical baselines.

### 7.7 MEDIUM — inconsistent class-imbalance handling between the two benchmarks the SM compares

**Severity: MEDIUM.** `scripts/p3_hybrid_benchmark.py:362–367` vs `scripts/p3_sota_benchmark.py:163,167`.

The canonical benchmark uses `RandomForestClassifier(n_estimators=200, random_state=42)` with **no `class_weight`** on a 74/26 split. The SM SOTA benchmark (`SM:517`) uses `class_weight='balanced'`. `SM:520` then compares them ("PersStats + RF achieves AUC 0.873 … the corrected canonical-panel benchmark gives ECFP4 0.948 and TFP 0.876"), while also disclosing at `SM:517` that the SOTA run used **different labels entirely** (MPO-derived, 75.9/24.1) from the canonical eos80ch labels. Two of the SM's comparison tables are therefore not commensurable with Table 1, and the SM says so in a footnote rather than fixing it.

### 7.8 MEDIUM — a target set as a threshold, then reported as met to three significant figures

**Severity: MEDIUM.** `main:223` vs `SM:249`.

Methods: *"A TNE Silhouette > 0.35 was set as the target."* Result: exactly **0.350**. Setting a threshold and reporting the value equal to it invites the reading that the analysis was tuned to the target (the *k* = 484 choice is inherited, and no sensitivity to *k* is shown). Report the raw value without the pre-set target, and add a *k*-sweep.

### 7.9 MEDIUM — three different Silhouette baselines compared across incomparable dimensionalities

**Severity: MEDIUM.** `main:303`, `SM:241–254`.

Silhouette is computed in each descriptor's own space: TNE 192-D (continuous), VAE 64-D (continuous), ECFP4 2048-D (binary, Euclidean metric implied). Silhouette is not comparable across spaces of different dimension and metric type — the concentration of pairwise distances in 2048-D binary space guarantees ECFP4 loses. This is a dimensionality artefact presented as "more chemically coherent clusters." No chemical coherence measure (e.g. scaffold purity per cluster) is computed, despite "chemically coherent" being the claim.

### 7.10 LOW — Table 1 mixes provenances under one caption

`main:255` captions Table 1 "canonical panel 19,836 molecules" while the QKS row is footnoted as coming from a different benchmark at "n = 19,849" (main:279) — and PHCO/AP/BPF come from `p3_classical_benchmark_19849.csv` while Hybrid/ablation come from the hybrid rerun. Four provenances, one caption.

### 7.11 LOW — duplicate LaTeX label on one table

`main:256` `\label{tab:benchmark}` and `main:281` `\label{tab:hybrid}` both sit inside the same `table` environment; `\cref{tab:hybrid}` therefore resolves to Table 1 while reading as a second table. Compiles, but confuses.

---

## 8. LIMITATIONS SECTION — what is missing

The Limitations (main:374–380) is unusually candid about the H₁–RRS size confound and the QKS artefact history, and that candour is the best thing in the manuscript. But **every item below is a limitation I found in the paper's own deposited data and is absent from the section:**

| # | Missing limitation | Severity | Evidence |
|---|---|---|---|
| L1 | **No scaffold-, cluster-, or seed-group split.** Random `StratifiedKFold` on a library built by mutating 850 seeds with 69.3 % scaffold recovery ⇒ analogue leakage across folds, biased most toward local-substructure descriptors (ECFP4). Words "scaffold split", "GroupKFold", "leakage" appear nowhere. No intra-library nearest-neighbour Tanimoto is reported. | **CRITICAL** | main:227, main:100 |
| L2 | **Label circularity.** Ground truth is another ML model's output (Ersilia `eos80ch`). If that model is fingerprint-based, "ECFP4 wins" is partly tautological. The paper notes labels are computational (main:376) but never names this specific threat to its central ranking. | **CRITICAL** | main:137, main:376 |
| L3 | **The TFP benchmarked is 78-dim, not the 12-dim TFP defined in Methods** (+0.029 AUC of the published value comes from undocumented enrichment). Not disclosed; actively contradicted at main:376. | **CRITICAL** | §1.1, §6.2 |
| L4 | **Removing TNE significantly improves the hybrid (p = 2.1 × 10⁻⁴)**, and TFP+QK (0.899) beats the shipped hybrid (0.888). Described as "slightly improves" with no test. | **CRITICAL** | §2.1–2.2 |
| L5 | **Ablation deltas confounded with RF feature-count dilution** (TNE = 64 % of the hybrid vector, `max_features='sqrt'`). No dimension-matched control. | **HIGH** | §2.3 |
| L6 | **Promiscuity correlations are size proxies** (H₀ count ≈ atom count), with no partial correlation — the exact confound the paper controls for elsewhere. | **CRITICAL** | §7.1 |
| L7 | **No head-to-head against any learned representation** — no GNN, no ChemBERTa/MolFormer, no message-passing baseline, despite MolPROP being cited at main:127. The comparison set stops at 2010-era fingerprints. | **HIGH** | main:127, Table 1 |
| L8 | **TNE is 6× larger than ECFP4 in bytes** (192 float64 = 1,536 B vs 2,048 bits = 256 B). The 6.1× "compression" is measured only against the authors' own tensor construction. | **HIGH** | §3/N7 |
| L9 | **`fig:paradox`, `SM-fig:domain`, `SM-fig:tensor` have no generating scripts**, contradicting the Data Availability promise of "all analysis scripts." | **CRITICAL** | §6.3 |
| L10 | **Degenerate features** — 2 constant + 5 duplicate-pair columns inside the 78-dim TFP. | **HIGH** | §7.3 |
| L11 | **78-way promiscuity scan without multiplicity control**, contrary to the paper's own stated Bonferroni policy. | **HIGH** | §7.2 |
| L12 | **Single conformer per molecule** (ETKDG, seed 42, main:147). The entire TFP is 3D-conformer-dependent; no conformer-ensemble sensitivity is reported, although `p3_tda_pipeline.py:394` implements multi-conformer averaging and `p3_tda_fingerprints_pilot_conf50.csv` exists. The one experiment that would quantify TFP's conformational stability was run and is not reported. | **HIGH** | main:147 |
| L13 | **Only 5 CV folds** for every significance test (df = 4). The paper acknowledges limited power (main:227) but still reports `p = 0.060` as a "borderline trend" while treating `p = 0.419` as evidence of equivalence — the classic asymmetry. No equivalence test (TOST) is performed despite the central claim being a null. | **HIGH** | main:227, main:301 |
| L14 | **SVM results promised in Methods do not exist** for any descriptor except the hybrid. | **HIGH** | §6.4 |
| L15 | **No prospective or decision-level evaluation** of any kind (§5). | **HIGH** | §5.1 |
| L16 | **The Ersilia threshold (0.5) produces a 74/26 imbalance handled inconsistently** between the canonical benchmark (no `class_weight`) and the SM benchmarks (`class_weight='balanced'`, and different labels). | **MEDIUM** | §7.7 |
| L17 | **Silhouette compared across incomparable dimensionalities**; no *k*-sensitivity. | **MEDIUM** | §7.9 |

**The one limitation actually needed to make the paper's null result rigorous — an equivalence test with a pre-specified margin (L13) — is absent.** Without it, "no statistically significant difference" at *n* = 5 folds is an underpowered failure to reject, and the paper's best contribution (§1.3) is not yet established at the standard it needs.

---

## 9. WRITING AND PRESENTATION DEFECTS

### 9.1 CRITICAL — a sentence is truncated mid-clause in the Methods

**Severity: CRITICAL.** `main:219`.

> "Hyperparameter optimisation followed a two-phase protocol. In Phase~1 ($n = 200$), a grid search evaluated 60 combinations"

The sentence **ends there** — no verb completion, no period, no Phase 2 description. The next line is `\subsection{Clustering analysis}`. The entire two-phase hyperparameter protocol, which selects the *d* = 6 / *n*_rep = 1 / *n*_kpca = 30 configuration used everywhere in the paper, is described only in the SM (`SM:297–321`). An editor performing a completeness check will stop at this line. This is a desk-reject-class defect in a document labelled "Submission-ready."

### 9.2 MEDIUM — §3.6/§3.7 of the main text are verbatim duplicates of SM §10.1/§10.2

`main:307` ≡ `SM:563` (word-for-word except "dimension-collapsing"/"dimensionality-reduction"); `main:311` ≈ `SM:608`; `main:319–321` ≡ `SM:569–571`; `main:325` ≈ `SM:575`; `main:349` ≈ `SM:597`; `main:341` ≈ `SM:628–630`; `main:361` ≈ `SM:639`. Roughly **two pages of the main text are duplicated in the SM.** Given the manuscript is at 19 pp. and the README records a 26→18 p. trim, this duplication is the cheapest available cut.

### 9.3 MEDIUM — the abstract ends on a null result about a secondary analysis

`main:100`: the abstract's final and most memorable clause is the H₁–RRS size-confound collapse — a *cross-paper secondary* analysis. Meanwhile the abstract never states the primary practical conclusion (use ECFP4) as a conclusion, never mentions that removing TNE improves the hybrid, and asserts "QKS the principal positive contributor" (an artefact-confounded attribution, §2.3).

### 9.4 LOW — "6.1× real-atom mean compression" appears in the abstract without its baseline

`main:100`. A compression ratio is meaningless without naming what is compressed. Stating it in the abstract as a headline number, when the object compressed is the authors' own construction and the result is 6× larger than ECFP4 (§7/N7), is the abstract's weakest sentence.

### 9.5 LOW — README "First" claims not in the manuscript will ship in the deposit

`README.md:30–33`, referenced as part of the deposit at main:396. Four "First …" claims, three of which I judge indefensible (§3).

---

## 10. CONCRETE REFRAMING PROPOSAL

The current framing is unsupportable. Below are **actual replacement sentences**, not advice. They are drafted to be defensible against every objection in §1–§9 **using only data already in the repo**, plus the two experiments named in §11.

### 10.1 Title

> **Current:** "Topological and tensor-network representations resolve chemical paradoxes in African antimalarial natural products"
>
> **Replacement:** "When quantum-inspired representations do not help: a scale-resolved benchmark of persistent homology, tensor networks, and simulated quantum kernels against classical fingerprints on 19,836 African antimalarial candidates"

### 10.2 Abstract

> Molecular representation choice is routinely justified by appeals to topological or quantum structure that classical fingerprints are said to miss, but such claims are seldom tested against properly tuned classical baselines at scale. We define three such representations — a persistent-homology Topological Fingerprint (TFP), a Tucker-decomposition Tensor Network Embedding (TNE), and a simulated Quantum Kernel Score (QKS, 6-qubit IQPEmbedding) — and benchmark them on 19,836 antimalarial candidates derived from African natural-product chemical space, under both random and seed-group cross-validation. **None outperforms ECFP4.** Under random 5-fold CV, ECFP4 reaches AUC 0.948, ahead of atom-pair (0.940), BPF (0.939), FCFP4 (0.918), MACCS (0.905), 2D-pharmacophore (0.896), TFP (0.876) and TNE (0.722); under seed-group CV all descriptors fall by [X], confirming that a substantial part of the apparent performance of every descriptor reflects analogue leakage in a mutation-generated library. A concatenated TFP+TNE+QKS descriptor reaches 0.888, significantly below ECFP4 (p < 0.0001); its ablation shows that **removing TNE significantly improves the descriptor** (0.899, p = 2 × 10⁻⁴), so the best quantum-inspired combination is TFP+QKS, not the three-component hybrid. The simulated quantum kernel is statistically indistinguishable from a gamma-tuned RBF kernel at n = 5,000 (p = 0.42) and n = 19,836 (p = 0.06) while clearly beating a linear kernel (p ≤ 0.0006), and we show that two earlier headline results from our own pipeline — an apparent quantum advantage and an apparent quantum disadvantage — were artefacts of an untuned RBF baseline and of a train/test scaling mismatch respectively. We further show that two topological signals that appear predictive — H₁ count versus resistance-resilience score, and H₀ count versus multi-target binding — both collapse under control for molecular size (partial ρ ≈ 0). We conclude that ECFP4 remains the appropriate default for this chemical space, and we deposit the full descriptor matrices, kernel matrices and per-fold results so that the negative result can be contested rather than repeated.

### 10.3 Contribution list (replacing N5–N8 at main:123)

> Our contributions are: **(C1)** a descriptor benchmark on 19,836 natural-product-derived antimalarial candidates under both random and seed-group cross-validation, in which three quantum-inspired representations are each outperformed by ECFP4, with all per-fold results deposited; **(C2)** a scale-resolved null result for a simulated 6-qubit IQP quantum kernel against a gamma-tuned RBF baseline, at two sample sizes and with an explicit equivalence margin, together with the linear-kernel control that shows the comparison is not vacuous; **(C3)** a forensic retraction of two prior results from our own pipeline — an apparent quantum advantage traced to an untuned RBF `gamma`, and an apparent quantum disadvantage traced to a train/test scaling mismatch — with the deposited files that overturn each; **(C4)** two worked demonstrations that persistent-homology descriptors act as molecular-size proxies in this chemical space (H₁ versus resistance resilience, H₀ versus binding promiscuity), each surviving until a partial correlation is taken and neither surviving after; and **(C5)** an ablation showing that component concatenation in a hybrid descriptor can be net-negative, with the dimension-matched control needed to separate information loss from feature-sampling dilution.

### 10.4 Sentences that must be deleted or replaced verbatim

| Location | Delete / replace |
|---|---|
| main:73 (title) | replace per §10.1 |
| main:100 | "with QKS the principal positive contributor (ablation Δ = −0.040)" → **"the ablation is confounded by block dimensionality; a dimension-matched control shows [result]"** |
| main:123, N5 | "demonstrating that 1D persistent homology captures scaffold-level features invisible to classical fingerprints" → **delete** (contradicted by Table 1) |
| main:123, N8 | "an applicability domain analysis using quantum kernel density" → **"a demonstration that quantum kernel density fails as an applicability-domain discriminator (AUC 0.43–0.51) where Tanimoto distance succeeds trivially"** |
| main:274, main:315 | "dropping TNE slightly improves AUC (Δ = +0.011)" → **"removing TNE significantly improves AUC (Δ = +0.011, paired t = 12.9, p = 2.1 × 10⁻⁴); the two-component TFP+QKS descriptor at AUC 0.899 therefore supersedes the three-component hybrid"** |
| main:284–293 (§3.3) | replace the prose "resolution" with the seed-vs-expanded H₀/H₁ Wilcoxon statistics and effect sizes the figure caption already promises, **or** retitle to "§3.3 Topological restatement of the scaffold-recovery statistic" and state plainly that scaffold-only vs whole-molecule Tanimoto (0.379 vs 0.206) accounts for the observation without persistent homology |
| main:325 | "This provides a clear topological mechanism: … reducing steric clash penalties." → **"H₀ count is a molecular-size proxy (mean 38.0 versus mean 39 heavy atoms); after controlling for molecular weight the association is [X]. The unadjusted correlation is consistent with the known tendency of smaller ligands to obtain favourable docking scores against more pockets, and we make no mechanistic claim."** |
| main:345, main:376 | "TFP adds value specifically for compounds with complex ring systems (≥3 fused rings)" → **run the subgroup analysis, or delete both occurrences** |
| main:376 | "the enriched TFP (32 features …) showed no improvement over the 12-feature TFP baseline … consistent with the canonical full-library TFP AUC of 0.876" → **"The canonical TFP row (AUC 0.876) uses the 78-feature enriched descriptor (12 persistence summaries plus 21 further H-statistics, 25 persistence-image and 20 Betti-curve features). The 12-feature TFP defined in §2.3.3 attains AUC 0.847 on the same panel; enrichment is therefore worth +0.029 AUC here, in contrast to the n = 5,000 SOTA comparison in the SM."** — and **rewrite Methods §2.3.3 to define the 78-dim descriptor that was actually used** |
| main:388 | "positioning quantum-inspired methods as effective complementary tools" → **"Complementarity to ECFP4 was tested directly by concatenation (ECFP4+TFP+TNE+QKS, AUC [X] versus ECFP4 [Y]); [it does / does not] improve on ECFP4 alone."** |
| README.md:30–33 | delete all four "First …" formulations; replace with C1–C5 |

---

## 11. THE TWO EXPERIMENTS THAT WOULD TURN THIS INTO AN ACCEPTABLE PAPER

Both are cheap. My ECFP4 reproduction took **26 seconds** of CV on this workstation.

1. **The complementarity test (§1.2).** `cv_score(np.hstack([X_ecfp, X_tfp, X_tne, X_qk]), y, 'rf', 'ECFP4+Hybrid')`. One line; QK features already exist per-fold in the checkpoint. This is the experiment that decides whether the paper has a positive result. Run it and report it whichever way it falls.
2. **The seed-group split (§8/L1).** Group folds by seed molecule (or by Bemis–Murcko scaffold) instead of `StratifiedKFold`. **Blocker:** no seed/parent provenance column is deposited in `p3_tda_fingerprints.csv` or `p3_labels_production.csv` — a reviewer *cannot* perform this check even if they want to. Add the column to the deposit and rerun. Expect all AUCs to drop and the gaps to narrow; that result is more publishable than the current one, not less.

Secondary, all < 1 day: the dimension-matched ablation control (§2.3); the H₀-promiscuity partial correlation using the existing `p3_h1_rrs_partial_corr.py` machinery (§7.1); a TOST equivalence test on QK-vs-RBF (§8/L13); the conformer-ensemble sensitivity from the already-computed `p3_tda_fingerprints_pilot_conf50.csv` (§8/L12); the ≥3-fused-ring subgroup analysis (§5.2); scripts for the three orphan figures (§6.3); removal of the 2 constant + 5 duplicate TFP columns (§7.3).

---

## 12. WHAT THE PAPER DOES WELL (so the authors know what to protect)

Stated because a fair review says it, and because these are the parts the reframing must preserve:

- **The QKS retraction narrative (main:301, main:378, `SM:693`) is exemplary.** Publishing that your own headline quantum advantage was an untuned-`gamma` artefact, *and* that your subsequent quantum disadvantage was a scaling-mismatch artefact, with the files that overturn both, is rarer than it should be and is the single most valuable thing in this submission.
- **The H₁–RRS partial-correlation analysis (main:361, main:376)** is textbook confound control, honestly reported, with the pilot ρ = 0.947 → 0.312 → ~0 collapse laid out in full. It should be a model for §7.1.
- **The linear-kernel control (`SM:702`)** is what makes the QK-vs-RBF null non-vacuous. Many QML papers omit it.
- **The PHCO bug disclosure (`SM:228–231`)** — documenting that a silent `SparseBitVect` conversion failure had forced a descriptor to AUC 0.500, and correcting it to 0.896 — is exactly the right behaviour.
- **The ChEMBL negative result (`SM:439–462`)**, reported as a negative rather than spun.
- **Numerical reproducibility of the classical benchmark is excellent** — per-fold agreement to 6 decimal places, 26 s runtime, clean canonical-panel construction with an explicit no-silent-imputation guard (`scripts/p3_hybrid_benchmark.py:156–196`).

The scientific instincts here are sound. The framing is the problem: the manuscript is a careful negative-result paper that has been dressed as a methods paper, and the dress does not fit.

---

## 13. FINDINGS INDEX

### CRITICAL (11)
1. §1.2 — Complementarity to ECFP4 asserted 5×, never tested; the decisive experiment is absent. `main:100,345,380,388`
2. §2.1 — Selective significance testing: the one anti-narrative ablation row gets "slightly" and no p-value; recomputed p = 2.1 × 10⁻⁴. `main:274,315`
3. §2.2 — The shipped hybrid (0.888) is dominated by TFP+QKS (0.899), which appears only as an ablation subtraction. `main:270,274`
4. §4.1 — The titular "scaffold paradox resolution" has no statistic anywhere; Fig. 1 promises a Wilcoxon p-value that does not exist. `main:73,284–293,291`
5. §5.1 — Zero demonstrated decision impact; the Discussion states this itself. `main:357,345,311`
6. §6.2/§1.1 — Table 1 TFP (0.876) is a 78-dim descriptor; Methods define 12-dim (0.847); main:376 asserts the opposite. `main:159–163,267,376`
7. §6.3 — Figure 1 and two SM figures have no generating script, contradicting Data Availability. `main:290,396`; `SM:618,716`
8. §7.1 — Size confound diagnosed for H₁–RRS, ignored for H₀–promiscuity, with a steric mechanism claimed. `main:325`
9. §8/L1 — No scaffold/seed-group split on a mutation-generated library with 69.3 % scaffold recovery; leakage never discussed; provenance column not deposited. `main:227,100`
10. §8/L2 — Label circularity (ML-generated ground truth) never named as a threat to the central ranking. `main:137,376`
11. §9.1 — Methods sentence truncated mid-clause; the entire Phase-1/2 protocol is missing from the main text. `main:219`

### HIGH (13)
1. §1.4 — "Quantum-inspired" is a misnomer in both directions. `main:73,100,103`
2. §2.3 — Ablation confounded by RF feature-count dilution; attribution unlicensed. `main:202–217,255,353`
3. §3/N5 — "features invisible to classical fingerprints" self-refuted by Table 1; ToDD precedes. `main:123`
4. §3/N7 — 6.1× compression is against a self-built strawman; TNE is 6× larger than ECFP4 in bytes; PACTNet precedes. `main:123,171–186`
5. §3/N8 — Contribution N8 refuted by the paper's own AUC 0.425–0.511. `main:123,311`
6. §4.2 — Paradox "resolution" is circular; main:337 supplies the classical refutation. `main:286,337`
7. §4.3 — SELFIES mechanism asserted, no mutation-level analysis. `main:286`
8. §5.2 — "≥3 fused rings" subgroup claim stated twice, never run. `main:345,376`
9. §6.1 — n = 19,849 vs 19,836 mislabel in ~10 places including the abstract; SM contradicts main. `main:100,279,301,353,376,378,388`; `SM:681,698`
10. §6.4 — Methods claim SVM for every representation; deposited SVM rows exist only for the hybrid. `main:227`
11. §7.2 — 78-feature scan without the multiplicity control the Methods promise. `main:325`; `SM:575`
12. §7.3 — 2 constant + 5 duplicate columns inside the benchmarked descriptor. `results/p3_tda_fingerprints.csv`
13. §7.4/§7.5 — Compute-cost justification contradicted by own timing table by ~480×; 3-of-5 aborted folds and a below-chance 2-fold pilot reported as results. `main:323`; `SM:573,383`

Plus HIGH-severity limitation gaps L5, L7, L8, L10, L11, L12, L13, L14, L15 (§8).

### MEDIUM (9)
§6.5 build order undocumented / cold build gives 79 undefined refs · §6.6 README stale (V2607 filenames, 18 vs 19 pp.) · §7.6 Cohen's *d* = 63.84, power = 1.000, contributions omitted · §7.7 inconsistent `class_weight` + different label sets across compared benchmarks · §7.8 Silhouette target 0.35 → result exactly 0.350 · §7.9 Silhouette compared across incomparable dimensionalities, no *k*-sweep · §9.2 ~2 pp. of main text duplicated verbatim in SM · §9.3 abstract ends on a secondary null · §8/L16–L17.

### LOW (4)
§7.10 Table 1 mixes four provenances under one caption · §7.11 duplicate LaTeX label in one table environment · §9.4 compression ratio in abstract without baseline · §9.5 README "First" claims ship in the deposit.

**Counts — CRITICAL 11 · HIGH 13 · MEDIUM 9 · LOW 4.**

---

## 14. DONE-CRITERIA

| # | Criterion | Where met |
|---|---|---|
| 1 | Verdict on accept/major-revision/reject + the two dominating reasons | **§0** — REJECT (resubmittable as repositioned). Reason 1: benchmarked TFP (78-dim, 0.876) ≠ Methods TFP (12-dim, 0.847), with main:376 asserting the opposite — reproduced both. Reason 2: random CV on a seed-mutation library with 69.3 % scaffold recovery against ML-generated labels invalidates the central ranking; "leakage"/"scaffold split" appear nowhere. |
| 2 | Every "first"/novelty claim listed with defensible/indefensible verdict + the specific prior work that threatens it | **§3** — 4 in-manuscript (N5–N8), 4 README (N1–N4), plus "we introduce three representations." Threats named per claim: ToDD 2023, tda_pretraining_2026, tda_binding_affinity_2026 (N5); PACTNet 2025 (N7); Q2SAR 2025, naleczcharkiewicz2024, kumar2024quantumdrug (N2); self-refutation by Table 1 / SM Table S6 / p3_tda_promiscuity.csv (N5, N8, N3). |
| 3 | Concrete reframing proposal as actual sentences | **§10** — new title (§10.1), full replacement abstract (§10.2), replacement C1–C5 contribution paragraph (§10.3), and a delete/replace table of 11 specific verbatim sentence substitutions (§10.4). |
| 4 | Named reproducibility trace for two headline claims, with what succeeded and what failed | **§6** — **Trace A**, ECFP4 AUC 0.948 (`scripts/p3_classical_benchmark_19849.py`): SUCCEEDED, per-fold match to 6 dp in 26 s; FAILED alongside — command absent from README Quick Start, and n = 19,836 ≠ the "19,849" printed in the abstract (root cause: `p3_hybrid_canonical_19849.sbatch:45` + `p3_hybrid_benchmark.py:195`). **Trace B**, TFP 0.876 + ablation Δ = +0.011 (`scripts/p3_hybrid_benchmark.py`, `p3_hybrid_canonical_19849.sbatch`): FAILED from the published method (12-dim → 0.847), SUCCEEDED only from undocumented `--tfp-enriched` default (78-dim → 0.8759); ablation CSV values reproduce but the run is un-rerunnable (hardcoded `/home/nanaengo/` paths, 12 h × 32 CPU SLURM) and its significance (p = 2.1 × 10⁻⁴) is unreported. Additionally: Fig. 1 / Fig. S-domain / Fig. S-tensor have **no generating script at all**. |
