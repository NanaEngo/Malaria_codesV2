# P3 Critical Review — Pass C: ScholarEval scoring + Edge-case/boundary hunting + Reproducibility

**Manuscript:** *Persistent homology resolves the scaffold paradox in AI-generated African antimalarial candidates* (Paper 3, target: Journal of Cheminformatics)
**Pass:** scholar-eval-and-edge-cases (Opus 4.8)
**Date:** 2026-07-27
**Scope:** REVIEW ONLY — no manuscript/script files edited. All numbers traced to source CSV + generating script.
**Env:** `source /home/tchapet/VirtualEnv/bin/activate` (Python 3.12.3). No conda `malaria_md` deps required for the CSV checks performed here.

---

## LENS 1 — ScholarEval-style quantitative scoring (1–10)

Scores anchored to file:line evidence. Scale: 1 = reject-level, 10 = exemplary.

| # | Dimension | Score | One-line rationale (anchor) |
|---|-----------|------|------------------------------|
| a | Problem formulation | **6** | The scaffold-paradox framing (92.6% Tanimoto vs 69.3% scaffold recovery) and H₀/H₁ decomposition (main L325, L477) is genuinely well-motivated, but the central question "does TDA beat ECFP4?" is answered oppositely in main (L295: "ECFP4 achieves the highest AUC") vs the SM SOTA benchmark (SM L508/L524: PersStats rf=0.8731 > ECFP4 0.868) — the problem is framed around a negative result the authors' own balanced benchmark contradicts. |
| b | Novelty | **5** | Combining PH + Tucker TNE + QKS applicability domain on African NP space is a reasonable package, but each piece is incremental; QKS shows no advantage after RBF tuning (main L347, L501); the most novel claim (H₁–RRS ρ=0.916) rests on an n=14 pilot that attenuates to ρ=0.312 at n=77 (SM L104, `p3_h1_rrs_correlation_final.csv`). |
| c | Methodology rigour | **4** | Headline benchmark (main L299) uses unbalanced classifiers on a 75.9/24.1 imbalanced set (15,063 active/4,786 inactive, `p3_labels_production.csv`), depressing TFP to 0.587, while the authors' own class-weighted SOTA run gives TFP-12=0.867 and PersStats=0.873 (`p3_sota_benchmark_full.csv`); GA-discriminator benchmark is seed-contaminated and acknowledged-but-unaddressed (main L376–379); 5-fold (not 10-fold) CV. |
| d | Analysis quality | **3** | Headline numbers do not reproduce from deposited full-library CSV (`p3_hybrid_benchmark_baseline.csv`: ECFP4 rf=0.819 vs headline 0.868, −0.049; Hybrid rf=0.7455 vs 0.842, −0.096); four+ conflicting RRS ρ values; PHCO conclusion contradicts own SM (main 0.500 "no discriminative info" vs SM L232 0.801 "carries info after bug fix"). |
| e | Writing/clarity | **5** | Prose is generally readable and the negative-result framing is commendable, but main and SM tell divergent stories on two substantive conclusions (PHCO, TDA-vs-ECFP4), Discussion is duplicated SM↔main (SM L585–663), citations are malformed (main L497, SM L594 bare `(Wesołowski et al., 2025)`, SM L658 manual `[1]`), and README is stale (10-fold, N1–N4, 15.6×). |
| f | Reproducibility | **4** | Seeds are pinned (random_state=42 across all 8 cited scripts; conformer seed 42 via `ETKDGv3` at `p3_tda_pipeline.py:391,418`) and all 8 cited scripts exist — BUT there is NO `requirements.txt`/`environment.yml` (no version pinning anywhere except a lone "PennyLane 0.45.1" in the data-availability sentence, main L548); the Zenodo-named file `p3_polypharm_tfp_rrs.csv` (main L548) is MISSING; no clustering/Silhouette CSV deposited; the "0.936 vs 0.105" cautionary tale (main L347/L501) does not match the deposited v1 summary (`p3_qks_summary_v1.txt`: quantum=0.885, rbf=0.867, p=0.38 n.s.). |
| g | Limitations honesty | **7** | Genuinely the strongest dimension: NISQ caveat stated upfront (main L120), RBF-tuning cautionary tale is a real methodological contribution (main L499–503), n=14/Class-D-n=1 caveat explicitly flagged (main L513, L528), D-GRIL build failure documented transparently (SM L655–662), computational labels flagged as non-experimental (main L528). Deducted because the honesty lives mostly in the SM while the main headlines the un-caveated numbers (0.916, 0.500). |

### Overall weighted score

Weights (J. Cheminformatics priorities): problem 1.0, novelty 1.0, methodology 1.5, analysis 1.5, writing 0.5, reproducibility 1.5, limitations 0.5 (sum 7.5).

Weighted sum = 6·1.0 + 5·1.0 + 4·1.5 + 3·1.5 + 5·0.5 + 4·1.5 + 7·0.5 = 6 + 5 + 6 + 4.5 + 2.5 + 6 + 3.5 = **33.5 / 7.5 ≈ 4.5 / 10**.

### Three dimensions most limiting acceptance
1. **(d) Analysis quality — 3/10.** Headline benchmark numbers fail to reproduce from the deposited full-library CSV; multiple cross-document numerical contradictions (RRS, PHCO, TFP, promiscuity, Tartarus ECFP4 R²).
2. **(c) Methodology rigour — 4/10.** Unbalanced headline benchmark on a 76/24 imbalanced set manufactures the central "TDA fails" negative result that the authors' own balanced SOTA run refutes (TFP 0.587 → 0.867); contaminated GA-discriminator benchmark.
3. **(f) Reproducibility — 4/10.** No dependency pinning, a Zenodo-named file is absent, key per-fold/silhouette source data not deposited, and the flagship cautionary tale's numbers don't match the deposited v1.

---

## LENS 2 — Edge-case / boundary hunting + reproducibility

Severity legend: CRITICAL = blocks acceptance / invalidates a headline claim; HIGH = major reviewer objection; MEDIUM = needs correction.

### EC-1 — GA-discriminator seed-identical contamination (acknowledged) [HIGH]
- **Anchor:** main L376–379; `p3_ga_discriminator.csv` (AUC_Tanimoto=1.0 at N=50/100/200/500; AUC_QK=0.4252/0.4811/0.4755/0.5114).
- **Does acknowledging it rescue the AUC=1.0 triviality?** No. The authors write that AUC=1.0 "is a trivial consequence of poisoning the generated set with seed-identical molecules" (L376–377). Disclosure converts a hidden flaw into a disclosed-but-**unaddressed** one: the benchmark was never re-run with seed-identical molecules excluded (or with >2 SELFIES mutations so generated molecules cannot equal their seed). As implemented, the benchmark cannot separate the discriminator's true power from the leakage artifact, so it is **uninformative for its stated purpose** (comparing QK density vs Tanimoto as a GA discriminator). It only demonstrates that an 8-D UMAP-reduced QK cannot detect near-identical molecules — unsurprising and not a "boundary condition" so much as a null result. **Implication:** the GA-discriminator subsection (main L372–379, L600–608) should be reframed as a negative result or re-run with de-duplicated generated sets; in its current form it does not support the applicability-domain claim it is marshalled for.

### EC-2 — PHCO SparseBitVect bug: a correctness bug in a reported baseline [CRITICAL]
- **Anchor:** SM L229–232 (bug + fix → AUC 0.801); main L312/L491 (report AUC 0.500, "exactly random"); `p3_hybrid_benchmark_baseline.csv` (PHCO rf mean = 0.8011 — **exactly** the SM's bug-fix value).
- **Severity rationale:** This is not a cosmetic discrepancy — it is a **direct main↔SM scientific contradiction on a substantive conclusion.** The SM documents that the Gobbi 2D-pharmacophore `SparseBitVect` → `ConvertToNumpyArray` silently yields an all-zero vector (AUC 0.500), correctable via `GetOnBits()`, after which PHCO = 0.801. The deposited full-library baseline CSV confirms PHCO rf = 0.8011. Yet the **main text reports 0.500 and concludes "pharmacophore-based bit vectors provide no discriminative information for this library"** (L295, L491) — the exact opposite of the SM's corrected conclusion. The main manuscript therefore ships the **buggy** value and a wrong interpretive claim, while its own SM and CSV contain the fix. **Implication:** the main must adopt 0.801 (the corrected, deposited value) and reverse the "no discriminative information" sentence; until then a reported baseline is wrong.

### EC-3 — D-GRIL `libc10.so` build failure documented as a "reproducibility case study" [HIGH]
- **Anchor:** SM L655–662.
- **Is documenting a failed build an acceptable substitute for benchmarking against SOTA?** No. The paper invokes D-GRIL (main L124) and TopologyNet (main L123, L124) as the SOTA comparators for PH-based methods, then benchmarks against **neither**: D-GRIL never ran (ABI mismatch, `mpml.so` failed to load), and TopologyNet is replaced by an "analog" MLP-on-PersStats (SM L530–551, `p3_topologynet_analog.csv`: MLP=0.799 vs RF=0.860) that is explicitly acknowledged as a weaker surrogate ("on summary statistics alone, RF is the more appropriate classifier", SM L551). Documenting a build barrier is honest and useful, but it does not constitute the SOTA comparison the Related Work (main L122–124) sets up. **Implication:** the SOTA-comparison claim is not substantiated; the paper compares against its own RF/SVM baselines and an MLP analog, not against D-GRIL or TopologyNet. This should be stated as a limitation, not framed as a completed benchmark.

### EC-4 — 8-qubit UMAP-to-8D resolution bottleneck [HIGH]
- **Anchor:** main L203, L376–379, L528 ("resolution bottleneck of the UMAP dimensionality reduction to 8 dimensions"); `p3_qks_benchmark.csv`.
- **Does it undermine the QKS/applicability-domain claims?** Substantially, yes — and the authors half-admit it. The QKS and the QK-density discriminator both operate on ECFP4(2048) → UMAP(8D) → [-1,1], a 256× compression that the GA-discriminator result shows destroys near-neighbour resolution (AUC 0.425–0.511). The standalone QKS AUC=0.751 (`p3_qks_benchmark.csv` mean) is therefore bounded by what 8 UMAP dims retain, not by the quantum circuit's expressivity — so the "kernel indistinguishability after RBF tuning" finding (main L499–503) may reflect UMAP information loss rather than a property of quantum kernels. The applicability-domain framing (main L368–370, "native Hilbert-space boundary condition") is undercut because the Hilbert space is fed 8-D pre-compressed features. **Implication:** QKS/AppD claims should be qualified as "8-D UMAP-reduced" throughout, and the applicability-domain advantage over Tanimoto (claimed at L370) is not demonstrated (the one head-to-head test, EC-1, shows Tanimoto superior).

### EC-5 — Single-library generalizability (African NP seeds only) [MEDIUM]
- **Anchor:** main L528 ("library is biased toward the chemical space of its 396 African NP and 454 synthetic drug seeds; generalization … remains to be tested"); L116/L118 (only `temgoua2026antimalarial` seeds).
- **Implication:** Every result (TFP, TNE, QKS, H₁–RRS, scaffold paradox) is conditioned on one generative pipeline's output from one seed library. The "scaffold paradox" may be an artifact of STONED-SELFIES mutation statistics on this particular seed set rather than a general phenomenon. The cross-paper H₁–RRS link is doubly confined (one library + n=14). Stated as a limitation but the title/abstract universalise it ("resolves the scaffold paradox").

### EC-6 — n=14 / Class-D-n=1 small-sample boundary — WORSE than the plan states [CRITICAL]
- **Anchor:** main L511/L513/L520/L528 (n=14, "Class A n=3, Class D n=1"); SM L104/L639; **definitive source `p3_h1_rrs_correlation_final.txt` (2026-07-25): "Class A: 46, Class B: 31, Class C: 0, Class D: 0" at n=77**.
- **Finding beyond the seed list:** The definitive cohort is **Class A=46, Class B=31, Class C=0, Class D=0** — i.e., in the expanded/valid analysis there is **no Class D compound at all**, and Class A = 46 (not 3). The manuscript's "Class A n=3, Class D n=1" (L513, L528) describes the tiny pilot subset only, while the headline ρ=0.916 (abstract L99, L513, L520) is the pilot value. The canonical correlation at n=77 is **ρ=0.3124 (H₁_count), p=0.0057** (`p3_h1_rrs_correlation_final.csv`), which the manuscript **never reports in the main text** (the SM reports 0.361, a third value, at L104/L639). So: (i) the headline "ρ=0.916, n=14" overstates a result whose definitive value is ρ=0.31; (ii) the "Class D n=1" caveat is moot — the definitive cohort has Class D=0; (iii) a 3× attenuation (0.916→0.312) on expanding from 14 to 77 is a strong signal the pilot correlation is unstable. **Implication:** the abstract/conclusion headline number is the pilot, not the definitive result; the main must report the n=77 value and the actual class composition, or drop the RRS claim to hypothesis-generating status in the abstract.

### EC-7 — Silhouette 0.350 vs pre-registered ">0.35" target [MEDIUM]
- **Anchor:** main L234 (target "Silhouette > 0.35"), L349/L389 (achieved 0.350); SM L250.
- **Finding:** Achieved 0.350 equals, not exceeds, the pre-registered target; the phrasing "exceeding the VAE baseline" (L349, L485) is loose (0.350 vs 0.229 exceeds the VAE baseline, but does not exceed the >0.35 target). Additionally **no clustering/Silhouette source CSV exists** in the results tree (`find` for *cluster*/*silhou* returns nothing) → the 0.350/0.229/0.180 values are [UNVERIFIED] from deposited data. **Implication:** restate as "meets the 0.35 target" (not "exceeds >0.35") and deposit the clustering CSV.

### EC-8 — 5-fold CV on 19,849 with 75.9/24.1 imbalance: fold-level variance adequacy [HIGH]
- **Anchor:** main L238/L299 (5-fold); `p3_labels_production.csv` (15,063 active / 4,786 inactive = 75.9/24.1); SM effect-size table L415–424 (Power column).
- **Finding:** 5-fold on 19,849 gives ~3,970/fold (~3,013 active / ~957 inactive) — minority-class count per fold is adequate for AUC point estimation, but **5 folds yields only 5 data points for the paired t-test**, giving low power: the SM's own power column shows Hybrid Δ=+0.066 at power 0.263 and TFP+ECFP4 at power 0.195 (SM L422–423) — i.e., the equivalence/non-inferiority claims are **underpowered**. Combined with the unbalanced classifier issue (EC-9), the headline "Hybrid matches ECFP4 (p=0.111)" (main L428) is a non-rejection from an underpowered test, not evidence of equivalence (the authors half-acknowledge this at L428, but the abstract L99 still universalises it). **Implication:** 10-fold or repeated CV would be expected for the equivalence framing; report fold-level variance for the full-library run (currently only the 200-mol dev-set per-fold table is deposited, SM L125–171).

### EC-9 — (Beyond seed list) Headline benchmark uses unbalanced classifiers; balanced SOTA run refutes the central negative result [CRITICAL]
- **Anchor:** main L295 ("ECFP4 achieves the highest AUC 0.868"), L310 (TFP=0.587), L528 ("TDA does not outperform ECFP4"); `p3_hybrid_benchmark_baseline.csv` (TFP rf=0.5827, unbalanced); `p3_sota_benchmark_full.csv` + `p3_sota_benchmark_full_summary.txt` (TFP-12 rf=0.8668, PersStats rf=0.8731, **class_weight='balanced'**, n_estimators=500, n=19,849).
- **Finding:** The headline benchmark (`p3_hybrid_benchmark_baseline.csv`) uses unbalanced RF/SVM on a 76/24 imbalanced set, yielding TFP=0.587. The authors' own SOTA benchmark on the **same 19,849 library** with `class_weight='balanced'` yields TFP-12=0.867 and PersStats=0.873 — the latter **numerically exceeding ECFP4 (0.868)** (SM L508/L524, summary txt: "PersStats: ΔAUC = +0.0063 (better)"). The 0.587→0.867 gap (0.28 AUC) is attributable to class balancing. **Implication:** the paper's central negative result ("TDA does not outperform ECFP4", L528; "ECFP4 achieves the highest AUC", L295) is an artifact of unbalanced training and is contradicted by the authors' own balanced benchmark. The main text never surfaces the PersStats=0.873 result. This is the single most damaging internal inconsistency.

### EC-10 — (Beyond seed list) Headline benchmark numbers do not reproduce from deposited full-library CSV [CRITICAL]
- **Anchor:** main Table 1 L305–315 (ECFP4=0.868, FCFP4=0.845, MACCS=0.831, AP=0.840, BPF=0.822, TFP=0.587, TNE=0.606, PHCO=0.500, Hybrid=0.842); `p3_hybrid_benchmark_baseline.csv` (full-library, 90 rows, accuracy granularity 0.69/0.74/0.79 → ~3,970/fold).
- **Finding:** Recomputing rf means from the deposited full-library CSV: ECFP4=0.8192 (headline 0.868, **−0.049**), FCFP4=0.8166 (0.845, −0.028), MACCS=0.8006 (0.831, −0.030), AP=0.8230 (0.840, −0.017), BPF=0.7712 (0.822, −0.051), TNE=0.5596 (0.606, −0.046), Hybrid=0.7455 (0.842, **−0.096**). Only TFP (0.5827 vs 0.587, −0.004) and PHCO-rf (0.8011, see EC-2) match. Every classical baseline is ~0.03–0.05 lower in the CSV than headline; Hybrid is 0.096 lower. The headline numbers therefore come from a **non-deposited or differently-configured run** (the Hybrid 0.842 plausibly from the optimized-weight Phase-2 kernel-PCA run, main L228, whose per-fold CSV is not in the deposit). **Implication:** the headline Table 1 is not reproducible from the deposited benchmark CSV; either the CSV or the table must be reconciled, and the full-library per-fold data for the headline Hybrid must be deposited.

### EC-11 — (Beyond seed list) The "0.936 vs 0.105" RBF-tuning cautionary tale is not reproducible from the deposited v1 [HIGH]
- **Anchor:** main L347/L501/L530 ("QK 0.936 vs RBF 0.105, p=0.0003"); `p3_qks_summary_v1.txt` + `p3_qks_benchmark_v1.csv`.
- **Finding:** The deposited untuned v1 summary shows quantum=0.8852±0.066, **rbf=0.8669±0.050**, linear=0.8649, quantum-vs-rbf **p=0.3823 (not significant)** — i.e., RBF=0.867 (not 0.105) and the difference was already non-significant. The v1 CSV shows per-fold rbf gammas of 0.005/5.0/0.01 (inner-CV-tuned), so this v1 is not a "default-gamma" run. The "0.105 RBF / 0.936 quantum / p=0.0003" numbers must come from an **even earlier, un-deposited run**. **Implication:** the paper's most-touted methodological lesson rests on numbers not present in the deposit; the deposited v1 does not show the claimed artefact. Either deposit the true default-gamma run or correct the cited numbers.

### EC-12 — Promiscuity correlations: two different datasets, two different conclusions (main vs SM) [HIGH]
- **Anchor:** main L465 (H₀ count −0.248, H₀ entropy −0.243, H₁ entropy −0.190, N=17,011); SM L579 (H₀ max persistence −0.167, H₁ entropy −0.161); sources `p3_physical_validation/p3_tda_promiscuity.csv` (N=17,011: H₀_count −0.2478, H₁_entropy −0.1896) vs `p3_tartarus_tda_spearman.csv` (N=19,900: H₀_max_pers −0.1670, H₁_entropy −0.1612).
- **Finding:** Main and SM pull promiscuity from two different analyses (N=17,011 vs N=19,900) that rank different features as the strongest correlate (main: H₀_count; SM/tartarus: H₀_max_pers). Neither N matches 19,849. The mechanistic sentence in main L465 ("lower topological complexity in ring structures (H₁) …") is supported by H₁_entropy −0.190 in the N=17,011 set but H₁_entropy is only −0.161 (4th-ranked) in the N=19,900 set. **Implication:** pick one canonical promiscuity analysis and cite it consistently; the current state presents two incompatible "topological signature of polypharmacology" claims.

### EC-13 — Sample-size contradiction 65,856 vs 19,849 (unexplained 46,007-molecule drop) [HIGH]
- **Anchor:** main L134 ("65,856 molecules"), L238 ("5-fold CV on all 65,856 molecules"), L256/L299 (19,849); `eos80ch_malaria_final_activity.csv` (65,856 rows), `p3_tda_fingerprints.csv` (19,849 rows), `c6_primary_leads_synthesisable.csv` (19,913 rows).
- **Finding:** Methods states the CV is "on all 65,856 molecules" (L238) but the benchmark set is 19,849 (Results L256). The drop 65,856→19,849 = **46,007 molecules** is never explained; L256 only mentions "13 failed conformers" (19,849→19,836). The 19,849 appears to be the synthesizable-leads subset (c6 = 19,913), not "all 65,856." **Implication:** Methods L238 is wrong (CV is on 19,849, not 65,856); add a sentence explaining the 65,856 → 19,849 filter.

### EC-14 — Tartarus target/PDB labels contradict across main, SM, and ChEMBL section [HIGH]
- **Anchor:** main L459 (1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT); SM L573 (1SYH/PfDHFR, **6Y2F/PfCRT homologue, 4LDE/PfClpP homologue**); SM L448 ChEMBL (PfDHFR/7F3Y, PfATP4/9N10, PfCRT/6UKJ); sources `p3_tartarus_tne_regression.csv` + `p3_physical_validation/p3_tne_regression.csv` (both label 6Y2F=PfATP4, 4LDE=PfCRT).
- **Finding:** The **main matches the CSVs** (6Y2F/PfATP4, 4LDE/PfCRT); the **SM L573 contradicts both** (6Y2F/PfCRT, 4LDE/PfClpP). The ChEMBL enrichment (SM L448) uses a third PDB set (7F3Y/9N10/6UKJ) — arguably legitimate (different structures for known-actives enrichment) but contributes to three labelings. Additionally main vs SM pull slightly different Tartarus numbers from two CSVs (main ECFP4 R²=0.570/0.515 from `physical_validation`; SM 0.578/0.517 from `tartarus`). **Implication:** fix SM L573 to match the CSVs and main; consolidate to one Tartarus CSV.

### EC-15 — Zenodo deposit references a non-existent file [HIGH]
- **Anchor:** main L548 ("the cross-paper H₁/RRS analysis dataset (`p3_polypharm_tfp_rrs.csv`)");
- **Finding:** `p3_polypharm_tfp_rrs.csv` does **not exist** anywhere in the results tree (`find` returns nothing). The actual RRS files are `p3_rrs_tfp_final.csv` (501 rows) and `p3_h1_rrs_correlation_final.csv` (12 rows). **Implication:** either create the named file or correct the deposit inventory; a reviewer following the data-availability statement will hit a dead link.

### EC-16 — No dependency pinning; ETKDG vs ETKDGv3 method drift [MEDIUM]
- **Anchor:** main L144 ("ETKDG generator with random seed 42"), L548 ("PennyLane 0.45.1"); code `p3_tda_pipeline.py:103,418` (`AllChem.ETKDGv3()`), `p3_tne_pipeline.py:82`, `p3_rrs_tfp_expansion.py:89`.
- **Finding:** No `requirements.txt`/`environment.yml`/`setup.py`/`pyproject.toml` exists in the project, so library versions are unpinned except the single "PennyLane 0.45.1" mention. The manuscript says "ETKDG" (L144) but all three conformer-generating scripts use **ETKDGv3** — a different algorithm (v3 ≠ v1), which changes 3D coordinates and therefore every persistence diagram. **Implication:** add a pinned requirements file; correct "ETKDG" → "ETKDGv3" in Methods.

---

## Reproducibility verdict per cited script

All 8 cited scripts **exist** in `scripts/`. Seed pinning (`random_state=42`) is present in all. **No script pins library versions** and there is no requirements/environment file. Conformer seed 42 is in the code (`ETKDGv3`, not the "ETKDG" stated in the manuscript).

| Script | Exists | Seed-pinned | Version-pinned | Evidence (file:line) |
|--------|:------:|:-----------:|:--------------:|----------------------|
| `p3_physical_validation.py` | yes | yes (42) | no | `scripts/p3_physical_validation.py:230,243,375,391,406,411` (RF/SVM/StratifiedKFold/UMAP/PCA `random_state=42`); bootstrap `seed=42` L494; conformer ETKDGv3 not here |
| `p3_tda_pipeline.py` | yes | yes (42) | no | `:391` `random_seed: int = 42`; `:417-418` `params = AllChem.ETKDGv3(); params.randomSeed = random_seed` (≠ manuscript "ETKDG" L144) |
| `p3_tne_pipeline.py` | yes | partial | no | `:82` `AllChem.ETKDGv3()` (no explicit `randomSeed` set — relies on RDKit default, NOT 42); no RF/CV seed in this file |
| `p3_qks_benchmark.py` | yes | yes (42) | no | `:121,127,402,453,520` (UMAP/PCA/StratifiedKFold/SVC `random_state=42`) |
| `p3_hybrid_benchmark.py` | yes | yes (42) | no | `:259,264,267,424,473,540,547,551,646,654` (Pipeline/UMAP/RF/SVC/StratifiedKFold `random_state=42`) |
| `p3_rrs_tfp_expansion.py` | yes | partial | no | `:89` `AllChem.ETKDGv3()` (no explicit `randomSeed`); Spearman/permutation in `p3_rrs_tfp_merge.py` [UNVERIFIED — merge script not inspected for seed] |
| `p3_sota_benchmark.py` | yes | yes (42) | no | `:163,167,180` (RF/SVC/StratifiedKFold `random_state=42`, `class_weight='balanced'`) |
| `p3_topologynet_analog.py` | yes | yes (42) | no | `:116,143,170` (StratifiedKFold/RF/MLP `random_state=42`) |

**Conformer-seed claim verification:** The manuscript (L144) says "ETKDG generator with random seed 42." The code uses `AllChem.ETKDGv3()` with `params.randomSeed = random_seed` (default 42) in `p3_tda_pipeline.py:418` — so the seed IS pinned in the TDA pipeline. **However**, `p3_tne_pipeline.py:82` and `p3_rrs_tfp_expansion.py:89` instantiate `ETKDGv3()` **without setting `randomSeed`**, so TNE and RRS-TFP conformers rely on the RDKit default seed (not explicitly 42) — a partial seed-pinning gap. And all three use **ETKDGv3**, contradicting the manuscript's "ETKDG" (v1).

**Cross-checked CSV ↔ script ↔ manuscript reconciliations:**
- QKS gamma-tuned benchmark: `p3_qks_benchmark.csv` → quantum=0.751, rbf=0.701, linear=0.721 — **reproducible** (matches main L359, L501).
- SOTA full benchmark: `p3_sota_benchmark_full.csv` (n=19,849) → PersStats rf=0.8731, TFP-12 rf=0.8668 — **reproducible** and matches SM L508, but **contradicts** main L295/L310/L528 (see EC-9).
- TopologyNet analog: `p3_topologynet_analog.csv` → MLP=0.799, RF=0.860 — **reproducible** (matches SM L543).
- GA discriminator: `p3_ga_discriminator.csv` → matches main Table 4 / SM Table S6 exactly — **reproducible** (but see EC-1, the benchmark is contaminated).
- Hybrid headline benchmark: `p3_hybrid_benchmark_baseline.csv` → **does NOT match** main Table 1 (see EC-10) — **not reproducible**.
- Silhouette 0.350/0.229/0.180: **no source CSV deposited** — [UNVERIFIED].
- RRS ρ=0.916: `p3_h1_rrs_correlation_final.csv` gives ρ=0.3124 (H₁_count, n=77) — headline **not reproducible** (see EC-6).
- "0.936 vs 0.105" cautionary tale: `p3_qks_summary_v1.txt` gives 0.885 vs 0.867, p=0.38 — **not reproducible** (see EC-11).

---

## Summary of strengths (for balance, per plan §4)
Genuine negative-result reporting (QKS no advantage after RBF tuning; TFP/TNE don't beat ECFP4 on the unbalanced headline benchmark); the RBF-tuning cautionary tale is a real methodological contribution in spirit; Bonferroni correction + Cohen's d effect sizes (SM L402–428); ChEMBL external-validation attempt (SM L463–488); power-analysis mention (SM L427); open data/code deposit intent (Zenodo + GitHub, main L548); NISQ-era caveat stated upfront (main L120); D-GRIL build barrier documented transparently (SM L655–662); all 8 cited scripts exist and pin seeds to 42.

## Top findings to relay
- **CRITICAL EC-9/EC-10:** Headline "TDA does not outperform ECFP4" (main L528) is refuted by the authors' own class-balanced SOTA benchmark (PersStats=0.873 > ECFP4=0.868, `p3_sota_benchmark_full.csv`); TFP jumps 0.587→0.867 with balancing. Headline Table 1 numbers don't reproduce from the deposited full-library CSV (`p3_hybrid_benchmark_baseline.csv`: ECFP4 0.819 vs 0.868).
- **CRITICAL EC-2:** Main ships the buggy PHCO=0.500 and concludes "no discriminative information" (L491) while the SM (L232) and deposited baseline (0.801) document the fix — a direct main↔SM scientific contradiction.
- **CRITICAL EC-6:** Definitive RRS cohort (`p3_h1_rrs_correlation_final.txt`) is Class A=46/B=31/C=0/**D=0** at n=77, ρ=0.312 — the abstract's ρ=0.916/n=14 is the pilot and the "Class D n=1" caveat is moot (definitive cohort has no Class D).
- **HIGH EC-1/EC-3/EC-11:** GA-discriminator benchmark seed-contaminated (acknowledged, unaddressed); D-GRIL never ran so no true SOTA comparison; the "0.936 vs 0.105" cautionary tale doesn't match the deposited v1 (0.885 vs 0.867).
- **HIGH EC-15/EC-16:** Zenodo-named `p3_polypharm_tfp_rrs.csv` is missing; no requirements.txt (no version pinning); ETKDG vs ETKDGv3 method drift.
