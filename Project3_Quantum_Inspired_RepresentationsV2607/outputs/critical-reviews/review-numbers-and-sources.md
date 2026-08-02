# P3 Critical Review — Pass A: Numbers & Sources (Opus)

**Manuscript:** *Persistent homology resolves the scaffold paradox in AI-generated African antimalarial candidates* (Paper 3, target: J. Cheminformatics)
**Pass:** numbers-and-sources — trace every numeric claim to CSV + script; reconcile main ↔ SM ↔ README ↔ prior-audit.
**Date:** 2026-07-27 | **Reviewer gate:** REVIEW ONLY — no manuscript/script files were edited.
**ROOT:** `/home/tchapet/Documents/GitHub/SAO/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607`

Conventions: `main L99` = `manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex:99`; `SM L104` = `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex:104`. CSV ground truth verified by direct read/recompute (Python 3.12.3, `/home/tchapet/VirtualEnv`). Items I could not trace to a deposited file are marked `[UNVERIFIED]`.

---

## CRITICAL

### C1 — H₁-RRS Spearman ρ: four incompatible values; only one is in the deposited CSV, and it is H₁ *count*, not H₁ *persistence*

**Ground truth (`results/p3_h1_rrs_correlation_final.csv`, output of `scripts/p3_rrs_tfp_merge.py`, n=77; recomputed and confirmed):**
- `H1_count`: ρ=+0.3124, p=0.005679, n=77  ← the audit's "canonical 0.312"
- `H1_entropy`: ρ=+0.2544, p=0.025562, n=77
- `H1_total_persistence` (=H1_count×H1_mean_pers): ρ=+0.2627, p=0.020964, n=77
- `H1_max_pers`: ρ=+0.0674, p=0.560568, n=77 (n.s.)
- Class distribution at n=77: A=46, B=31, C=0, D=0 (`p3_h1_rrs_correlation_final.txt`).

**The four values in circulation:**
| Value | n | Where | In a deposited CSV? |
|---|---|---|---|
| 0.916, p<0.0001 | 14 | main L99 (abstract), L513, L520, L528, L532 | NO — pilot, not in any P3 results CSV |
| 0.947, p<0.0001 | 14 | SM L104, L639 | NO — pilot; **both RRS scripts' docstrings name 0.947 as the pilot headline** (`p3_rrs_expansion.py:5`, `p3_rrs_tfp_expansion.py:5`) |
| 0.361, p=0.001 | 77 | SM L104, L639 ("H₁ total persistence from 500 compounds") | NO — no recomputed H1 feature gives 0.361 (closest: H1_count 0.312, H1_total_pers 0.263) |
| 0.312, p=0.006 | 77 | prior audit `P3_ADVERSARIAL_AUDIT_MITIGATION.md` §Weakness#2 | YES — = `H1_count` (0.3124) |

**Conceptual mismatch (the load-bearing issue):** the manuscript frames the result as "H₁ **persistence** correlates with RRS" / "cycle rigidity" (main L99, L515, L520; SM L104, L639). But the only value that reaches significance at n=77 is **H1_count** (number of H₁ features ≈ ring *count*), ρ=0.312. The actual *persistence* features are weaker: H1_total_persistence ρ=0.263 (p=0.021), H1_max_pers ρ=0.067 (n.s.). So "H₁ persistence" and "H₁ count" genuinely differ, and the strongest signal is the count, not persistence.

**Recommended canonical value:** report the expanded n=77 result and drop the n=14 pilot from the abstract. Either (a) reframe as "H₁ ring **count** correlates with RRS: ρ=0.312, p=0.006, n=77" (matches `H1_count`, the audit's canonized value), or (b) keep the "persistence" framing and use `H1_total_persistence` ρ=0.263, p=0.021. The pilot 0.916/0.947 (n=14, Class A=3, D=1) is statistically uninformative and should appear only as a clearly-labelled superseded pilot, if at all.

**Wrong/stale occurrences to fix:**
- main L99 (abstract): `ρ=0.916, p<0.0001, n=14` → replace with canonical n=77 value.
- main L513: `ρ=0.916, p<0.0001, n=14` → same.
- main L520 (Fig caption): `ρ=0.916, p<0.0001, n=14` → same.
- main L528 (Limitations): `ρ=0.916, n=14` → same.
- main L532 (Discussion): `ρ=0.916, p<0.0001, n=14` → same.
- SM L104 (Fig S1 caption): `0.947 (pilot, n=14) → 0.361, p=0.001` → 0.947 matches the scripts but **0.361 is wrong** (not computed anywhere); replace 0.361 with 0.312 (H1_count) or 0.263 (H1_total_persistence).
- SM L639: `0.947 (pilot) → 0.361, p=0.001` → same correction.
- Audit doc §Weakness#2: correctly identifies 0.312 but mislabels it "H₁ persistence"; it is H1_count. (Audit is a review artifact, not the manuscript, but the mislabel propagated.)

### C2 — Headline benchmark ECFP4 0.868 / Hybrid 0.842 does NOT reproduce from the deposited full-library benchmark CSV

**Ground truth:** `results/p3_hybrid_benchmark_baseline.csv` (the only full 19,849-molecule benchmark CSV; produced by `scripts/p3_hybrid_benchmark.py`, which uses the FIXED PHCO `GetOnBits()` path). Recomputed RF means:
- ECFP4 rf = **0.8192** (main says 0.868), FCFP4 = 0.8166 (main 0.845), MACCS = 0.8006 (main 0.831), AP = 0.8230 (main 0.840), BPF = 0.7712 (main 0.822), PHCO = 0.8011 (main 0.500), TFP = 0.5827 (main 0.587), TNE = 0.5596 (main 0.606), **Hybrid rf = 0.7455** (main says 0.842).

The deposited baseline CSV gives ECFP4 0.819 / Hybrid 0.746 — not 0.868 / 0.842. The 200-mol dev-set file `p3_hybrid_benchmark.csv` gives ECFP4 rf 0.96 / Hybrid 0.894 — also not 0.868/0.842. The headline 0.868/0.842 is asserted in `P3_SUBMISSION_ROADMAP_85PCT.md:18-19` and the manuscript (main L99, L295, L438, L443, L491, L507, L530, L540) but **no deposited CSV reproduces it**. The only 19,849-molecule run approaching 0.868 is the class-weighted SOTA benchmark (`p3_sota_benchmark_full.csv`: TFP-12 rf=0.8668, PersStats rf=0.8731) — but that file has no ECFP4 row and uses `class_weight="balanced"` (`p3_sota_benchmark.py:163`), whereas `p3_hybrid_benchmark.py` does not balance classes.

**Impact:** the paper's central result (Hybrid matches ECFP4) is numerically unreproducible from the deposited benchmark CSV. Either a balanced full-library ECFP4/Hybrid run was never deposited, or the headline numbers are stale. **Source CSV for 0.868/0.842 = `[UNVERIFIED]`.**
**Fix:** re-run `p3_hybrid_benchmark.py` on the full 19,849 set (or deposit the run that produced 0.868/0.842) and reconcile `tab:benchmark`/`tab:hybrid` to the deposited per-fold CSV; state class-weighting explicitly.

### C3 — PHCO AUC has three values; the main's 0.500 contradicts the deposited fixed benchmark (0.801)

**Ground truth:** `p3_hybrid_benchmark.py:144-159` uses the FIXED extraction (`fp.GetOnBits()`), and `p3_hybrid_benchmark_baseline.csv` PHCO rf mean = **0.8011** → 0.801.
- main L295, L312, L491: PHCO AUC **0.500** ("exactly random") — the OLD buggy all-zero value; contradicts the deposited fixed baseline (0.801) and is used as an interpretive claim ("pharmacophore bit vectors provide no discriminative information").
- SM L232 (§phco_bug): PHCO **0.801** after the SparseBitVect fix — matches the deposited baseline CSV. ✓
- SM L421 / `p3_effect_sizes/p3_effect_sizes.csv`: PHCO **0.912** — the 200-mol dev-set value (different analysis).

**Fix:** main `tab:benchmark` PHCO must read 0.801 (per deposited baseline), not 0.500; delete the "exactly random / no discriminative information" interpretation at main L295 and L491. SM §phco_bug and the effect-size table are internally consistent but are different sample sizes (full vs 200-mol) — caption both clearly.

### C4 — Tartarus target/PDB labels contradict across main, SM, and the RRS script; 4LDE is labelled three different ways

**Ground truth (`results/p3_tartarus_tne_regression.csv`, the actual computed regression):**
- `PfDHFR (1SYH)`, N=11878; `PfATP4 (6Y2F)`, N=17075; `PfCRT (4LDE)`, N=17074.

| Source | 1SYH | 6Y2F | 4LDE | Matches CSV? |
|---|---|---|---|---|
| CSV (ground truth) | PfDHFR | PfATP4 | PfCRT | — |
| main L459 | PfDHFR | PfATP4 | PfCRT | ✓ |
| SM L573 | PfDHFR | **PfCRT** homologue | **PfClpP** homologue | ✗ (6Y2F, 4LDE wrong) |
| `p3_rrs_expansion.py` TARGET_MAP (L~30) | PfDHFR | **PfCRT** | **PfATP4** | ✗ (6Y2F/4LDE swapped) |
| SM ChEMBL enrichment L448-450 | PfDHFR/**7F3Y** | PfATP4/**9N10** | PfCRT/**6UKJ** | different PDB set (see C5/M16) |

So 4LDE is labelled PfCRT (CSV/main), PfClpP (SM L573), and PfATP4 (script) — three ways. The SM L573 labels are wrong; the script TARGET_MAP is swapped. Note the SM also internally contradicts itself: L466 states "PfClpP was excluded because no P. falciparum ClpP target exists in ChEMBL," yet L573 calls 4LDE a "PfClpP homologue."
**Fix:** SM L573 → `1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT` (match CSV/main); correct `p3_rrs_expansion.py` TARGET_MAP to `6y2f=PfATP4, 4lde=PfCRT` (this mislabelling affects the composite RRS target weighting).

### C5 — Methods says cross-validation on 65,856 molecules; Results/tables and all CSVs say 19,849

**Ground truth (CSV row counts):** `eos80ch_malaria_final_activity.csv` = 65,856 rows (the full generated library); `p3_tda_fingerprints.csv` = 19,849; `p3_tne_embeddings.csv` = 19,849; `p3_labels_production.csv` = 19,849 (15,063 active / 4,786 inactive = 75.9%).
- main L134: "primary dataset consists of 65,856 molecules" + "eos80ch … applied to all 65,856" — correct for the generated library. ✓
- main L238: "5-fold stratified cross-validation on **all 65,856** molecules" — **WRONG**; the benchmark ran on 19,849 (the primary-leads subset that passed into TDA/TNE). All benchmark tables (main L299, L432) and the SOTA summary (`p3_sota_benchmark_full_summary.txt`: "19849 molecules") confirm 19,849.
- main L242: "across the 65,856-molecule library" (ChemGraphX comparison) — also should be 19,849 if it uses the TFP features that only exist for 19,849.
- Results L256, L336, all tables: 19,849. ✓

**Fix:** main L238 (and L242) → 19,849 for the benchmark/TDA analyses; reserve 65,856 for the generated-library description (L134) only.

---

## HIGH

### H1 — Promiscuity correlations: main and SM cite two different CSVs (different N, different features, different values)

**Ground truth — two distinct "TDA vs #targets bound" files:**
- `results/p3_physical_validation/p3_tda_promiscuity.csv` (N=17,011): H0_count ρ=−0.2478 (p=2.54e-236), H0_entropy ρ=−0.2428 (p=1.18e-226), H1_entropy ρ=−0.1896 (p=1.91e-137). Confirmed identical in `p3_physical_validation_summary.txt`.
- `results/p3_tartarus_tda_spearman.csv` (N=19,900): H0_max_pers ρ=−0.1670 (p=2.17e-124), H1_entropy ρ=−0.1612 (p=7.13e-116).

- main L465: H0_count −0.248, H0_entropy −0.243, H1_entropy −0.190, N=17,011 → matches `p3_tda_promiscuity.csv`. ✓
- SM L579: H0 max persistence −0.167 (p<1e-124), H1_entropy −0.161 (p<1e-115) → matches `p3_tartarus_tda_spearman.csv` (N=19,900). ✓

Both are individually accurate, but main and SM report **different analyses** (N 17,011 vs 19,900; different feature selections; different H1_entropy values −0.190 vs −0.161) with no cross-reference. The N=17,011 set = `p3_merged_dataset.csv` (17,011 rows, the TDA+TNE+docking merge); N=19,900 is the Tartarus docking set.
**Fix:** pick one canonical promiscuity analysis (preferably N=17,011, the merged set, consistent with the rest of §Comparison) and use it in both main and SM; cite the CSV by name.

### H2 — `tab:qkernel` (main L357-361): AUCs match the CSV, but Quantum target_alignment and both p-values are wrong

**Ground truth (`results/p3_qks_benchmark.csv` + `p3_qks_summary.txt`):** Quantum AUC 0.7512, RBF 0.7007, Linear 0.7208; Quantum target_alignment 0.5432; paired t-test Quantum-vs-RBF p=0.0878, RBF-vs-Linear p=0.3905 (Quantum-vs-Linear p=0.0634).
- main L359: Quantum AUC 0.751 ✓, RBF 0.701 ✓, Linear 0.721 ✓.
- main L359: Quantum **target_alignment 0.684** ✗ (CSV 0.5432); RBF target_alignment 0.334 ✓ (0.3343).
- main L359: Quantum-vs-RBF **p=0.312** ✗ (CSV 0.0878); Linear-vs-RBF **p=0.198** ✗ (CSV 0.3905). (Note 0.312 == the H1-RRS canonical ρ — possible copy-paste.)
- The qualitative "all p>0.05, n.s." (main L501, L530) is correct; only the table's specific p-values/alignment are wrong.
**Fix:** main L359 → Quantum target_alignment 0.543; p(Quantum vs RBF)=0.088; p(Linear vs RBF)=0.391 (all n.s.).

### H3 — TNE compression: manuscript 5.9× (from 38 atoms) vs deposited TNE summary 6.1× (from 39 atoms)

**Ground truth (`results/p3_tne_summary.txt`):** "Mean atoms/molecule: 39.0; Real ratio (mean): 6.1×; Mean recon. error: 0.1130; Max: 0.2196; Padded ratio (N=100): 15.6×; Valid embeddings: 19,836 / Failed: 13."
- main L99, L175, L336, L540 and SM L628: real ratio **5.9×** based on **38** mean atoms (main L183 derives "10×38/64≈5.9×" "from TDA H₀ counts"). The TDA H0_count mean is 38.04 (`p3_tda_summary.txt`), but the TNE pipeline's own atom count is **39.0**, giving **6.1×**. The manuscript uses the TDA H0-count proxy (38) instead of the actual TNE atom count (39), so 5.9× ≠ the deposited 6.1×.
- 0.113 reconstruction error ✓ (matches); 0.220 max ✓ (main L336); 15.6× padded ✓; 192 elements ✓.
- README L28/L41 headline **15.6×** (padded) vs manuscript 5.9× — README overstates (see M14).
**Fix:** either report 6.1× / 39 atoms (matches `p3_tne_summary.txt`) or explicitly state "5.9× using TDA H0-count (38.04) as the atom proxy; the TNE pipeline reports 6.1× from the actual mean of 39 atoms." Recommend 6.1× as the canonical figure.

### H4 — main L256 misattributes 13 TNE conformer failures to the TDA pipeline

**Ground truth:** `p3_tda_summary.txt` → "Molecules processed: 19,849; Valid TFPs: 19,849; Failed (no 3D): 0." `p3_tne_summary.txt` → "Valid embeddings: 19,836; Failed: 13." So TDA had **0** failures (19,849 valid); TNE had **13** failures (19,836 valid).
- main L256: "Topological fingerprint analysis was completed for 19,849 molecules (**19,836 valid, 13 failed** due to 3D conformer generation errors)" — the 19,836/13 split belongs to TNE, not TDA.
- main L336: "Tensor network embedding was completed for all 19,849 molecules (19,836 valid, **matching the TDA success set**)" — the TDA success set is 19,849, not 19,836.
**Fix:** main L256 → "19,849 molecules (19,849 valid, 0 failed)" for TDA; move the 13-failure statement to L336 (TNE) and drop "matching the TDA success set."

### H5 — Tartarus ECFP4 baseline numbers: main L461 stale, SM L575 correct (main↔SM disagree)

**Ground truth (`p3_tartarus_tne_regression.csv`):** PfDHFR ECFP4 R²=0.4606, ρ=0.6892; 6Y2F ECFP4 R²=0.5781, ρ=0.7695; 4LDE ECFP4 R²=0.5174, ρ=0.7337. TNE values: 0.4731/0.6952, 0.4637/0.6541, 0.3336/0.5847.
- main L461 ECFP4: PfDHFR R²=**0.451**, ρ=**0.683** (CSV 0.4606/0.6892); 6Y2F R²=**0.570**, ρ=**0.762** (CSV 0.5781/0.7695); 4LDE R²=0.515, ρ=0.733 (CSV 0.5174/0.7337, close). TNE ρ PfDHFR main=0.694 vs CSV 0.6952.
- SM L575 ECFP4: PfDHFR R²=0.461, ρ=0.689; 6Y2F 0.578; 4LDE 0.517 — **matches the CSV**. ✓
**Fix:** update main L461 ECFP4 numbers to match the CSV / SM L575 (0.461/0.689, 0.578/0.769, 0.517/0.733).

### H6 — Effect-size table + SM Table S4: TFP and TNE have byte-identical values (bug)

**Ground truth:** `p3_effect_sizes/p3_effect_sizes.csv`: TFP and TNE rows are identical (Mean_AUC 0.630, Std 0.112, Δ 0.330, Cohen_d 2.49, p 0.0051, Power 0.981). `p3_hybrid_benchmark.csv` (200-mol dev set): TFP rf and TNE rf per-fold AUCs are identical (0.600/0.800/0.500/0.667/0.583) and TFP svm == TNE svm too — across all 5 folds, both classifiers. SM Table S4 (L146-156) reproduces these identical TFP/TNE rows.
**Impact:** TNE features are effectively duplicating TFP in the dev-set run (a load/merge bug in `p3_hybrid_benchmark.py`'s `load_precomputed` for the `tne_` prefix, or TNE not loaded). The effect-size Δ sign convention is also inverted vs `tab:benchmark` (here Δ = ECFP4−method on the dev set where ECFP4=0.96, so positive Δ means ECFP4 is better — opposite to the main benchmark's method−ECFP4 convention).
**Fix:** re-run the dev-set benchmark with TNE features actually loaded; correct the identical TFP/TNE rows in `p3_effect_sizes.csv` and SM Table S4; align Δ-sign convention with `tab:benchmark` or label both explicitly.

### H7 — "QK 0.936 vs RBF 0.105, p=0.0003" (untuned-artefact cautionary tale) is not in any deposited file

**Ground truth:** `p3_qks_summary_v1.txt` (the untuned/default-gamma run) gives Quantum AUC 0.8852, RBF 0.8669 (p=0.382) — not 0.936/0.105. No results `.txt`/`.csv`/script contains 0.936 or 0.105 (grep confirmed). The tuned run (`p3_qks_summary.txt`) gives 0.7512/0.7007.
- main L347, L353, L501, L530 cite "QK 0.936 vs RBF 0.105, p=0.0003" as the untuned artefact.
**Fix:** either deposit the run that produced 0.936/0.105 or correct the numbers to the v1 values (0.885/0.867) — the qualitative point (apparent advantage vanishes after tuning) survives, but the specific figures are `[UNVERIFIED]`.

### H8 — Ablation numbers: main reports full-library values (0.842/0.837/0.835/0.608) but the only deposited ablation CSV is the 200-mol dev set

**Ground truth:** `p3_ablation.csv` (200-mol dev set): Hybrid-TFP rf mean 0.862, Hybrid-TNE 0.873, Hybrid-QK 0.630. main L447-449 (`tab:hybrid` ablation): Hybrid 0.842, Hybrid−TFP 0.837, Hybrid−TNE 0.835, Hybrid−QKS 0.608. These do not match the dev-set CSV (and the Hybrid 0.842 itself doesn't reproduce from `p3_hybrid_benchmark_baseline.csv`, see C2).
**Fix:** deposit the full-library ablation CSV and reconcile `tab:hybrid` ablation rows to it.

### H9 — Data-availability DOI mismatch; Zenodo upload still pending

- main L548: "DOI: 10.5281/zenodo.**XXXXXXX**, to be minted upon manuscript acceptance."
- SM L110 and README L92: "10.5281/zenodo.19608875."
- Audit `P3_ADVERSARIAL_AUDIT_MITIGATION.md:155`: "Zenodo upload … still needed."
**Fix:** mint/finalize the Zenodo deposit and set a single DOI in main L548, SM L110, README L92.

---

## MEDIUM

### M10 — Tartarus per-target N: off-by-one (17,075 vs 17,074) and none equals 19,913; regression N also disagrees with the merged dataset

**Ground truth:** `p3_tartarus_tne_regression.csv` N = 11,878 / 17,075 / 17,074. Tartarus output (`Project2…/results/tartarus_output.csv`) = 19,913 data rows. `p3_merged_dataset.csv` = 17,011 rows; its non-NaN score counts are score_1syh=11,930, score_6y2f=17,011, score_4lde=17,010 — which do **not** equal the regression N (11,878/17,075/17,074). So the regression was run on a different/larger merge than `p3_merged_dataset.csv`.
- Why none equals 19,913: the regression requires a valid TNE embedding **and** a valid (non-NaN) docking score per target; many scores are missing, especially 1SYH/PfDHFR (only ~11,878 valid).
- 17,075 vs 17,074 off-by-one: one compound has a 6Y2F score but no 4LDE score (or a missing TNE row for one).
- main L459 "19,913 primary leads docked" ✓ (Tartarus row count); main L461 per-target N 11,878/17,075/17,074 ✓ (matches regression CSV).
**Fix:** state in Methods that per-target N < 19,913 because the regression uses the intersection of valid TNE embeddings and non-NaN docking scores; reconcile which merge produced the regression N (it is not `p3_merged_dataset.csv`).

### M11 — ChEMBL enrichment table (SM L448-450) has no source CSV; its PDB IDs (7F3Y/9N10/6UKJ) appear in no script

`p3_chembl_validation.py:44-46` maps targets to **ChEMBL IDs** (CHEMBL4296323/1795182/6066156), not PDB IDs. No script or CSV contains 7F3Y, 9N10, 6UKJ, or the enrichment figures (53/18, 73/87, 12/19, 5.43×). `p3_chembl_validation/p3_chembl_validation.csv` has only one row. The expanded ChEMBL validation table (SM L477-483) **does** match `p3_chembl_expanded.csv` exactly (compounds 12/29/47/65/75/76, IC50s 30/69/0.40/12.5/0.40/0.79 µM, Tanimotos) ✓.
**Fix:** deposit the docking-enrichment run that produced 7F3Y/9N10/6UKJ and the 5.43×/∞/1.46× figures, or mark the enrichment table `[UNVERIFIED]`.

### M12 — Clustering Silhouette 0.350 / VAE 0.229 / ECFP4 0.180: no source CSV

main L349, L389, L485; SM L250. No deposited CSV contains these Silhouette values (grep finds only incidental substring matches in task CSVs). The "TNE Silhouette > 0.35 target" (main L234) is equal (0.350), not exceeded — "exceeding the VAE baseline" (L485) is loose. `[UNVERIFIED — no Silhouette CSV deposited]`

### M13 — Quantum-parameter Phase-1 grid 0.8534±0.0490 (n=200) is not in the deposited sweep CSV

main L228 and SM L309 cite the n=200 grid optimum AUC 0.853±0.049. `p3_quantum_params_sweep.csv` and the three `p3_phase2_*_raw.csv` contain only the n=1000 re-benchmark rows (0.8283±0.0371, 0.8047±0.0354, 0.8121±0.0396 — all ✓ vs main L228 / SM L321-323). The 0.8534±0.0490 n=200 value is `[UNVERIFIED — not in deposited sweep CSV]`.

### M14 — README is stale vs manuscript (confirmed)

- README L43: "10-fold Stratified CV, Bonferroni-corrected Wilcoxon (p<0.01)" vs main 5-fold CV + paired t-tests (main L238, L299). ✗
- README L26-31: novelty labels **N1–N4** for THIS paper vs main L120 **N5–N8**. ✗ (numbering scheme inconsistent)
- README L28, L41: TNE **15.6×** (padded) as headline vs main 5.9×/6.1× real. Overstated. ✗
- README L62: filename `Paper3_Quantum_Inspired_v0.7_V2607.tex` vs actual `Paper3_Quantum_InspiredV2607.tex`. ✗
- README L73: `conda activate malaria_md` vs the active venv (`/home/tchapet/VirtualEnv`, Python 3.12.3). ✗ (mark `[UNVERIFIED-needs-conda]` for any malaria_md-only import)
- README L37 ("65,856 … (19,849 primary dataset)") and L38 ("19,913 × 3 targets") are correct. ✓
**Fix:** update README to 5-fold CV, N5–N8, 5.9×/6.1× real compression, correct filename, venv activation.

### M15 — MC-uncertainty table mislabelled and "MC dropout on RF" is a misnomer

`p3_mc_uncertainty_summary.txt`: "Descriptor: TFP+TNE" (no QK), "MC bootstrap samples: 50, Trees per bootstrap: 30" (bootstrap, not dropout). Values match SM L361-364 (AUC 0.5443 ✓, ECE 0.0037 ✓, coverage 0.950 ✓, set size 1.820 ✓).
- SM L355 captions it "Hybrid descriptor (TFP+TNE+**QK**)" — wrong; the run was TFP+TNE.
- SM L351 / main L226 "Monte Carlo (MC) **dropout** on the Random Forest" — RF has no dropout; this is bootstrap subsampling of trees.
**Fix:** SM L355 → "TFP+TNE"; reword "MC dropout" → "MC bootstrap" throughout.

### M16 — Polypharmacology Δ=+0.010 verifiable, but σ=0.008 is not

`p3_tartarus_poly_classification.csv`: QKS AUC 0.7475, RBF 0.7370 (Δ=+0.0105 ✓), RF(TNE) 0.8178, N=19,900, prevalence 10.31% ✓ (main L463, L365). The per-fold std-of-Δ σ=0.008 (main L365) is not verifiable — the CSV has only mean/std_AUC (QK std 0.0131, RBF std 0.0102), no per-fold Δ. `[UNVERIFIED — no per-fold polypharm data deposited]`

### M17 — "20 high-confidence leads" (main L511) vs "n=14" correlation (L513) unexplained

main L511 says "20 high-confidence polypharmacological leads"; L513/L520/L528 use n=14 for the H1-RRS correlation (Class A=3, D=1 ⇒ B+C=10). The 20→14 reduction is not explained; the n=77 expansion has Class A=46, B=31, C=0, D=0 (no Class D). **Fix:** state why 14 of the 20 leads enter the pilot correlation.

### M18 — Malformed citations / dual companion bibkeys

main L497 and SM L594: bare `(Wesołowski et al., 2025)` with no `\citep` key. SM L658: manual `[1]` footnote mixed with natbib authoryear. Companion-paper bibkey inconsistency: `temgoua2026antimalarial` (main L116) vs `temgoua2027md` (main L511) for the same companion study. **Fix:** add bibkeys; unify the companion citation.

### M19 — TDA statistics table: negligible 4th-decimal drift vs summary

`p3_tda_summary.txt` (19,849 run): H0_count mean 38.0417 (main/SM table 38.0452), H0_max_pers 2.7166 (table 2.7171), H1_entropy 1.6354 (table 1.6357), H1_max_pers 1.3916 (table 1.3918). Differences ≤0.0035 — likely rounding/run drift. LOW severity; note for reproducibility.

---

## Numbers that DO reproduce cleanly (verified, for the record)

- **Kernel benchmark AUCs** (main L359): Q 0.751 / RBF 0.701 / Linear 0.721 = means of `p3_qks_benchmark.csv` per-fold. ✓ (p-values/alignment wrong — see H2)
- **Polypharmacology** (main L463): QKS 0.747, RBF 0.737, prev 10.3% = `p3_tartarus_poly_classification.csv`. ✓
- **Promiscuity (main)** (main L465): H0_count −0.248, H0_entropy −0.243, H1_entropy −0.190, N=17,011 = `p3_tda_promiscuity.csv`. ✓ (SM uses a different file — see H1)
- **GA discriminator** (main L404-407; SM L283-286): 50/100/200/500, Tanimoto 1.0, QK 0.4252/0.4811/0.4755/0.5114 = `p3_ga_discriminator.csv`. ✓
- **Tartarus TNE R²/ρ** (main L461): 0.473/0.695, 0.464/0.654, 0.334/0.585 = `p3_tartarus_tne_regression.csv` TNE rows. ✓ (ECFP4 rows stale in main — see H5)
- **Tartarus per-target N** (main L461): 11,878/17,075/17,074 = regression CSV. ✓ (see M10 for the off-by-one / 19,913 explanation)
- **SOTA benchmark** (SM L508-517): PersStats rf 0.8731, TFP-12 0.8668, etc. = `p3_sota_benchmark_full.csv` (n=19,849 RF, n=5,000 SVM). ✓
- **TopologyNet analog** (SM L543-544): RF 0.860, MLP 0.799, Δ −0.061 = `p3_topologynet_analog.csv`. ✓
- **Quantum-param re-benchmark** (main L228; SM L321-323): 0.8283±0.0371, 0.8047±0.0354, 0.8121±0.0396 = `p3_phase2_*_raw.csv` / `p3_quantum_params_sweep.csv`. ✓
- **Scalability** (SM L390-391; main L507): 40 mol, 820 pairs, 6.41 s, 128 pairs/s = `p3_scalability_results.csv`. ✓
- **MC uncertainty values** (SM L361-364): 0.5443 / 0.0037 / 95.0% / 1.820 = `p3_mc_uncertainty_summary.txt`. ✓ (descriptor mislabelled — see M15)
- **TNE recon error / padded ratio** (main L183, L336): 0.113, 0.220 max, 15.6× padded = `p3_tne_summary.txt`. ✓ (real ratio 5.9× vs 6.1× — see H3)
- **ChEMBL expanded validation** (SM L477-483): all 7 rows = `p3_chembl_expanded.csv`. ✓
- **Sample sizes**: 65,856 generated (`eos80ch_malaria_final_activity.csv`); 19,849 benchmarked (`p3_tda_fingerprints.csv`, `p3_tne_embeddings.csv`, `p3_labels_production.csv`: 15,063 active/4,786 inactive). ✓

---

## Gate verdict

**NOT READY.** 5 CRITICAL numeric discrepancies block submission: (C1) the H₁-RRS ρ appears as four values, only one of which (H1_count=0.312, n=77) is in the deposited CSV, while the abstract headlines an unreproducible 0.916 (n=14) and the SM cites a wrong 0.361; (C2) the headline benchmark ECFP4 0.868/Hybrid 0.842 does not reproduce from `p3_hybrid_benchmark_baseline.csv` (0.819/0.746); (C3) main's PHCO 0.500 contradicts the deposited fixed baseline (0.801); (C4) Tartarus PDB→target labels contradict across main/SM/script (4LDE labelled three ways); (C5) Methods says CV on 65,856 but all CSVs/tables use 19,849. Plus 9 HIGH issues (two different promiscuity CSVs, wrong `tab:qkernel` p-values/alignment, 5.9× vs 6.1× TNE compression, misattributed TDA failures, stale Tartarus ECFP4 baselines in main, TFP=TNE identical-value bug, unreproducible 0.936/0.105, missing full ablation CSV, DOI mismatch). Every CRITICAL/HIGH item above is tied to a specific CSV ground-truth value and file:line.
