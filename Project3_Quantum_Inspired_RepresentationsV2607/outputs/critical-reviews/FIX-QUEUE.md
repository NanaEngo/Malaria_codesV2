# P3 Consolidated Fix Queue — Phase 5 Critical Review (VERIFY complete)

**Manuscript:** *Persistent homology resolves the scaffold paradox in AI-generated African antimalarial candidates* (Paper 3) — target: Journal of Cheminformatics
**Date:** 2026-07-27
**Gate verdict:** **NOT READY for submission.** The manuscript's central headline numbers do not all reproduce from the deposited CSVs, and several load-bearing claims are refuted by the authors' own supplementary tables and result files. ScholarEval overall ≈ 4.5/10. The "85% ready" assessment is **not** supported by the deposited data.

**Sources (all in `outputs/critical-reviews/`):** `review-numbers-and-sources.md` (A), `review-claims-and-rigor.md` (B), `review-scholar-eval-and-edge-cases.md` (C), `review-editorial.md` (D), `review-death-angle.md` (E). This file reconciles them across passes (convergent findings flagged) and ranks by severity. Every CRITICAL item carries CSV ground truth + a suggested fix.

---

## CRITICAL (block submission — fix first)

### C1. H₁-RRS "biomarker" ρ=0.916 is unreproducible and overclaimed  ⟂ [A-C1, B-C1/C2, C-EC6, E]
- **CSV truth:** `results/p3_h1_rrs_correlation_final.csv` (n=77) → H1_count ρ=+0.312 (p=0.006), H1_total_persistence=0.263, H1_max_pers=0.067 (p=0.56, **NS**). At n=77, **Class C=0 and Class D=0**.
- 0.916 (n=14) appears in **no** P3 results CSV; the RRS scripts' docstrings name **0.947** as the pilot. SM L104/L639 cite **0.361** (n=77) — no recomputed H1 feature gives 0.361 (wrong).
- **Locations:** abstract L99, discussion L513, conclusion L532, fig caption L520, limitations L528.
- **Fix:** canonize the n=77 value (H1_count ρ=0.312, p=0.006) — or H1_total_persistence=0.263 if you prefer the persistence feature; drop the n=14 pilot from the abstract; remove "p<0.0001" and "biomarker/predictor"; reframe as hypothesis-generating; state that persistence did not replicate (0.067 NS) and the vulnerable class is absent at scale.

### C2. Headline ECFP4 0.868 / Hybrid 0.842 does NOT reproduce from any deposited CSV  ⟂ [A-C2, C-EC10]
- **CSV truth:** `p3_hybrid_benchmark_baseline.csv` (the only full 19,849-mol benchmark) → ECFP4 rf=**0.819**, Hybrid rf=**0.746**. The 200-mol dev set gives 0.96/0.894. **No deposited CSV gives 0.868/0.842** → source `[UNVERIFIED]`.
- This is the most dangerous finding: a reviewer requesting the reproducing CSV will find 0.819/0.746.
- **Fix:** either deposit the exact CSV/config that reproduces 0.868/0.842, or correct the headline to the deposited values (0.819/0.746) and re-derive every ΔAUC and p-value. Resolve before anything else — it determines what the paper actually claims.

### C3. "TDA does not outperform ECFP4" (TFP=0.587) contradicted by the authors' own class-balanced SOTA  ⟂ [C-EC9, B, E]  (three independent passes)
- **CSV truth:** `p3_sota_benchmark_full.csv` (class_weight='balanced', same 19,849) → TFP-12=**0.867**, PersStats=**0.873**, both **exceeding** ECFP4 0.868. Main's TFP=0.587 uses **unbalanced** classifiers on a 75.9/24.1 imbalanced set.
- The paper's central negative result is an artifact of not using class balancing.
- **Fix:** surface the balanced SOTA result in the main text; reconcile TFP=0.587 (unbalanced) vs TFP-12=0.867 (balanced) — determine whether it is class-weighting, feature definition (12-feat TFP vs 22-feat PersStats), or a load bug; restate the headline accordingly.

### C4. PHCO 0.500 (main) is the stale buggy value; fixed 0.801 is in the SM and the CSV  ⟂ [A-C3, C-EC2, B-M4]
- **CSV truth:** `p3_hybrid_benchmark_baseline.csv` PHCO rf=**0.801** (fixed `GetOnBits()` path in `p3_hybrid_benchmark.py`). Main ships 0.500 and concludes pharmacophores carry "no discriminative information" — directly contradicted by the SM bug-fix section (L232) and the CSV. SM effect-size table PHCO=0.912 is the 200-mol dev value.
- **Fix:** replace 0.500 with 0.801 in main (L295/L312/L491); delete the "exactly random / no discriminative information" conclusion; mention the SparseBitVect bug fix.

### C5. Tartarus target labels: SM wrong, script swapped, main correct  ⟂ [A-C4, B-H5/H6, C-EC14]
- **CSV truth** (`p3_tartarus_tne_regression.csv`): 1SYH/PfDHFR (N=11878), 6Y2F/PfATP4 (N=17075), 4LDE/PfCRT (N=17074) — matches main L459.
- SM L573 says 6Y2F/PfCRT, 4LDE/PfClpP (**wrong**; SM L466 itself says PfClpP doesn't exist — self-contradictory). `p3_rrs_expansion.py` TARGET_MAP has 6y2f/PfCRT, 4lde/PfATP4 (**swapped**). 4LDE is labelled three ways.
- **Fix:** correct SM L573 to match main/CSV; fix the script TARGET_MAP.

### C6. Methods says CV on 65,856; actually 19,849  ⟂ [A-C5, seed-S2]
- **CSV truth:** `p3_tda_fingerprints.csv`=19,849; `p3_labels_production.csv`=19,849 (15,063 active / 4,786 inactive); `eos80ch_malaria_final_activity.csv`=65,856. 65,856 is the generated library; only 19,849 were benchmarked. The 65,856→19,849 drop (≈46k) is unexplained (C-EC13).
- **Fix:** correct Methods L134/L238 to state 19,849 benchmarked; explain the 65,856→19,849 relationship.

### C7. "Quantum kernel polypharmacology advantage" is falsified  ⟂ [B-C3, E, A-H2]
- Δ=+0.010 AUC (σ=0.008) → Δ/σ≈1.25 → paired t (4 df) **p≈0.26**, not significant; no multiple-comparison correction; contradicts the manuscript's own "kernels statistically indistinguishable" conclusion (L347/L499) for a **smaller** effect.
- **Fix:** fold polypharmacology into "no quantum advantage"; delete the "task-specific quantum kernel sensitivity" exception (L365 footnote, L463, L532).

### C8. "First" novelty claims overstated or refuted by own data  ⟂ [B-C4, E]
- N5 "features ECFP4 cannot capture" — refuted by TFP+ECFP4 Δ=−0.003 (p=0.884, null incremental value). README N1 "First proof…retains binding affinity across 19,913" — negated by TNE losing on 2/3 Tartarus targets. README N2 "Quantum Advantage" — negated by C7.
- **Fix:** drop "First proof"/"Quantum Advantage"; reframe as "first systematic benchmark of TDA/TNE/QKS on African-NP space" with the negative results attached.

### C9. "H₁ ring complexity → promiscuity" mechanism refuted by own CSV  ⟂ [B-H2, A-H1]
- `p3_tda_promiscuity.csv`: H1_max_pers ρ=**−0.002** (p=0.795, ~zero). The real driver is H₀ (molecular size), |ρ|≈0.24 — a size/specificity effect, **not** a ring mechanism. (Main and SM also cite two different promiscuity CSVs: N=17,011 vs N=19,900 — different analyses.)
- **Fix:** delete the ring-complexity/conformational-adaptability narrative (L465); reframe as a size/specificity effect or remove the N3 claim.

### C10. Zenodo DOI placeholder + missing deposit file + upload pending  ⟂ [A-H9, D, C-EC15]
- Main L548 "10.5281/zenodo.XXXXXXX, to be minted" vs README L92 / SM L110 "10.5281/zenodo.19608875". The Data Availability statement names `p3_polypharm_tfp_rrs.csv`, which is **missing** from `results/`. Zenodo upload still pending (per prior audit).
- **Fix:** insert the real DOI; deposit the missing file; complete the Zenodo upload.

---

## HIGH (fix before submission)
- **H1.** `tab:qkernel` (main L359) wrong Quantum target_alignment (0.684 vs CSV 0.543) and p-values (0.312/0.198 vs CSV 0.0878/0.3905); AUCs match. [A-H2]
- **H2.** TNE 5.9×/38 atoms (main) vs deposited `p3_tne_summary.txt` 6.1×/39 atoms. [A-H3]
- **H3.** Main L256 misattributes 13 TNE failures to TDA (TDA summary: 0 failures). [A-H4]
- **H4.** Main L461 ECFP4 Tartarus baselines stale (0.451/0.683, 0.570/0.762 vs CSV 0.4606/0.6892, 0.5781/0.7695); SM L575 is correct — sync main to SM. [A-H5]
- **H5.** TFP and TNE byte-identical in `p3_effect_sizes.csv` and SM Table S4 (L146-156) — load bug. [A-H6, seed-S6/S12]
- **H6.** "QK 0.936 vs RBF 0.105" cautionary tale (main L347/L353/L501/L530) in no deposited file; v1 gives 0.885/0.867 (p=0.38 n.s.). [A-H7, C-EC11]
- **H7.** Ablation 0.842/0.608 (main) vs dev-set `p3_ablation.csv` (0.894/0.630); no full-library ablation CSV deposited. [A-H8]
- **H8.** Malformed citations: bare "(Wesołowski et al., 2025)" no bib key (main L497, SM L594); manual "[1]" footnote SM L658 mixed with natbib; dual companion bibkeys `temgoua2026antimalarial` vs `temgoua2027md`. [D, seed-S9]
- **H9.** SM "Discussion" (L582-644) duplicates main Discussion — cut to genuine supplementary content. [D, seed-S16]
- **H10.** R7-R10 reviewer-response residue in Introduction (L118) — reads as response-to-reviewers; remove for a standalone methods paper. [D]
- **H11.** README stale: 10-fold vs 5-fold; N1-N4 vs N5-N8; 15.6× vs 5.9×; 19,913 vs 19,849; wrong filename (L62); conda vs venv. [D, A, seed-S7]
- **H12.** H₁ rigidity → entropy → resilience (L515) unfalsifiable (invokes unmeasured ΔS_conf) — label as speculation. [B-H1]
- **H13.** Scaffold-paradox mechanism "H₁ preserved/H₀ diverges explains 92.6% vs 69.3%" (L330/L477) interpretive/tautological — soften "explains/resolves" to "consistent with"; add the Wilcoxon p/N or a controlling regression. [B-H3, E]
- **H14.** GA-discriminator AUC=1.0 is seed-contamination (acknowledged but unaddressed; benchmark uninformative). [C-EC1]
- **H15.** D-GRIL never ran (libc10.so build failure) — "reproducibility case study" is not a SOTA comparison. [C-EC3]
- **H16.** No `requirements.txt`/environment file; scripts pin `random_state=42` but not library versions; `p3_tne_pipeline.py:82` and `p3_rrs_tfp_expansion.py:89` use ETKDGv3 without `randomSeed`. [C]
- **H17.** Anti-AI: 6 banned patterns — `robust` ×4 (main L118/L325/L379, SM L608) and `we demonstrate` ×2 (main L479, cover L34); concrete rewrites in `review-editorial.md`. [D]

---

## MEDIUM/LOW (one-line; detail in the pass files)
Silhouette 0.350 = not >0.35 target + no source CSV (C-EC7); underpowered 5-fold on 75.9/24.1 imbalance (C-EC8); 8-qubit UMAP-to-8D bottleneck (C-EC4); single-library generalizability (C-EC5); Tartarus N off-by-one 17075/17074 + none=19913 (A); ChEMBL enrichment 7F3Y/9N10/6UKJ no source CSV (A); Phase-1 grid 0.854±0.049 not in sweep CSV (A); MC table mislabelled "TFP+TNE+QK" vs "TFP+TNE" + "MC dropout on RF" misnomer; Bootstrap MC AUC 0.5443 vs Hybrid CV 0.842 (E-7, A); promiscuity N=17011 vs N=19900 (C-EC12); 20 leads vs n=14 unexplained (A-M1, D); TDA 4th-decimal drift (A); abstract "ECFP4 cannot capture" overclaim (B-M3); "p<0.0001" with no test named (B-M5).

---

## Death-angle follow-up (E's `[to verify]` angles) — status
- **RESOLVED by A/B/C CSV work:** (1) ρ recomputation at n=77 → 0.312 count / 0.067 persistence NS, Class D=0; (3) TFP=0.587 vs 0.867 reconciliation → balanced-vs-unbalanced; (4) four ρ values → 0.312 canonical; (5) polypharm Δ → p≈0.26 falsified; (6) RRS + eos80ch both computational → ρ correlates two model outputs (strengthens the C1 overclaiming finding).
- **OPEN (need new analysis; not blocking this review):** (2) partial-correlation of H₁ persistence vs RRS controlling for MW/ring count/H₀/Fsp³/rotatable bonds — recommended to test whether H₁ is just a size proxy; (7) reconcile SM Bootstrap MC AUC 0.5443 vs Hybrid CV 0.842 (partially flagged — MC table mislabel). External ChEMBL/DrugBank generalization test — recommended future work.

---

## Strengths (preserve during revision)
Honest negative results (QKS no advantage after RBF tuning; TFP/TNE framing); the RBF-tuning cautionary tale is a genuine methodological contribution (but fix the 0.936/0.105 numbers to the deposited 0.885/0.867); Bonferroni + Cohen's d; ChEMBL external-validation attempt; power-analysis mention; open data/code intent; NISQ caveat; D-GRIL transparency. Limitations honesty scored 7/10 (the strongest dimension).

---

## ScholarEval (Pass C) — 1-10
Problem formulation 6 · Novelty 5 · Methodology rigour 4 · Analysis quality 3 · Writing/clarity 5 · Reproducibility 4 · Limitations honesty 7. **Overall ≈ 4.5/10.** Most limiting: analysis quality (3), methodology rigour (4), reproducibility (4).

---

## Recommended action order
1. **C2 + C3** — reconcile the headline benchmark numbers with the deposited CSVs (deposit the reproducing run OR correct to deposited values; surface the class-balanced SOTA). This determines what the paper actually claims.
2. **C1 + C7 + C8 + C9** — rewrite the abstract/conclusion around CSV-verified numbers; drop the ρ=0.916 biomarker, the quantum-advantage exception, the "First" claims, and the ring→promiscuity mechanism.
3. **C4 + C5 + C6** — fix the PHCO value, Tartarus labels, and the 65,856/19,849 methods statement.
4. **C10 + H8** — Zenodo DOI + missing file + citation hygiene.
5. **H1-H17 + MEDIUM/LOW** — table/number sync, structure (cut SM Discussion, remove R7-R10), README, anti-AI rewrites, reproducibility (`requirements.txt`, seeds).
6. **Open follow-up analyses** (partial-correlation H₁ vs size; external generalization) — run if feasible before resubmission.

---

*Integrity note: Pass E (death-angle) output is generative and unvalidated; its angles were routed through verification passes A/B/C before informing any finding above. No manuscript or script file was edited during this review.*
