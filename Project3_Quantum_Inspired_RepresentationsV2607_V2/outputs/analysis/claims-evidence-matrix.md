# Claims–Evidence Matrix — P3 main manuscript

**Built:** 2026-07-31 (L1 gate check, Phase 13)
**Manuscript:** `manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex` (615 lines)
**Ledger:** `outputs/analysis/analysis-ledger.md` (entries L001–L014)
**Rule under test:** every quantitative statement in the manuscript names a ledger entry ID, and that entry names a source file.

**Gate verdict: FAIL** — 1 CRITICAL contradiction, 5 HIGH untraceable/inconsistent, 10 MEDIUM orphan groups.

> **§G supersedes parts of §B–§D.** After this matrix was first written, `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (the authoritative values file, 2,018 lines, v37) was read in full. It **retracts H3**, **confirms C1 and H1**, **closes M9/M10**, and **adds three new HIGH findings**. Read §G before acting on anything above. Revised count: 1 CRITICAL, 7 HIGH, 8 MEDIUM.

Related but distinct: `outputs/critical-reviews/review-claims-and-rigor.md` (Pass B, 2026-07-27) is an adversarial review of three headline claims written before the ledger existed. This file is the full claim → ledger-ID map.

---

## Legend

| Verdict | Meaning |
|---------|---------|
| BACKED | claim maps to a ledger entry, and that entry's source file reproduces the number |
| ORPHAN | number in the manuscript with no ledger entry |
| UNTRACEABLE | a ledger entry would have no source to point at — the number exists in no deposited CSV/TXT/script output |
| CONFLICT | manuscript states two different values for the same quantity, or contradicts its own source |

---

## A. BACKED claims

| # | Claim (manuscript location) | Value | Ledger | Source verified |
|---|---|---|---|---|
| A1 | Abstract, Tab.1 L309–316, Disc. L509/L513 — classical benchmark ranking | ECFP4 0.949, AP 0.941, BPF 0.939, FCFP4 0.920, MACCS 0.904, PHCO 0.897, TFP 0.877, TNE 0.722 | L001 | `p3_classical_benchmark_19849.csv` — per-fold ECFP4 [0.94930, 0.94928, 0.94890, 0.95050, 0.94690], mean 0.9490 ✓ |
| A2 | Abstract, §4.7 L531, Limitations L546, L550, Fig.5 caption — H₁-RRS lead | ρ = 0.312, p = 0.0057, n = 77 | L002 | `p3_h1_rrs_correlation_final.csv` ✓ |
| A3 | Abstract, L531, L533, L546 — H₁-RRS pilot | ρ = 0.947, p < 0.0001, n = 14 | L003 | `p3_h1_rrs_correlation_final.txt` (pilot section) ✓ |
| A4 | L531 — Class A vs Class D H₁ persistence | 3.74 ± 0.34 Å vs 1.73 Å (Class D n = 1) | L003 | ✓ caveat carried into text |
| A5 | Tab.3 footnote L369, §4.5 L467, L550 — QKS polypharmacology | AUC 0.747 vs RBF 0.737, Δ = +0.010, σ = 0.008, prevalence 10.3 % | L004 | `p3_qks_summary.txt` ✓ |
| A6 | Tab.3 L363–365, §4.6 L519, Conclusion L558 — kernel comparison | QK 0.751, RBF 0.701, Linear 0.721, all p > 0.05; TA 0.543 vs 0.334 | L004 / L009 | `p3_qks_summary.txt` ✓ (but see H4 on the p-value column) |
| A7 | L351, Tab.3 caption L357, L519, L548 — untuned-RBF artefact | QK 0.936 vs RBF 0.105, p = 0.0003 | L009 (interpretation) | ✓ recorded as superseded artefact |
| A8 | §4.5 L469, Fig.4 caption L481 — TDA promiscuity | H₀ count ρ = −0.248 (p = 2.54 × 10⁻²³⁶), H₀ entropy −0.243, H₁ entropy −0.190; N = 17,011 | L005 | `p3_tda_promiscuity.csv` ✓ |
| A9 | §4.4 L465, L550, Fig.3 — Tartarus TNE regression | PfDHFR R² 0.473 / ρ 0.694 (N 11,878); PfATP4 0.464/0.654 (17,075); PfCRT 0.334/0.585 (17,074); ECFP4 0.451/0.570/0.515 | L006 | `p3_physical_validation_summary.txt` ✓ |
| A10 | Tab.2 L442–453, and L432/L513/L521/L525/L548/L550/L558 — hybrid + ablation | Hybrid 0.842; −TFP 0.837; −TNE 0.835; −QKS 0.608; v2 scalar 0.691; p = 0.111; α/β/γ = 0.10/0.10/0.80 | L007 | ⚠ PROVISIONAL by construction — original run file missing; authority = BMAD_Q1 §3.5. Manuscript labels every instance "(p)"/provisional ✓ |
| A11 | Abstract, L120, §4.3 L495–497, Conclusion L558 — scaffold paradox | 92.6 % Tanimoto distinction, 69.3 % scaffold recovery, scaffold 0.379 vs whole 0.206, ratio 1.84× | L008 | ✓ |
| A12 | Fig.1 caption L289–293 | 587 molecules (3.0 %), H₀ median 1.60 Å, exemplars p̄ = 0.78 / 0.42 Å | L010 | `p3_tda_fingerprints.csv` ✓ |
| A13 | Bibliography — `q_cadd_2026` | `pages = {54321}` | L011 | flagged `[PLACEHOLDER — VERIFY]`, author action ✓ |
| A14 | Tab.5 L408–411, Fig.6 caption L419, L509, L546 — GA discriminator | Tanimoto AUC 1.0000 at all N; QK 0.4252 / 0.4811 / 0.4755 / 0.5114 | **L012 (new)** | `p3_ga_discriminator.csv` — exact match ✓ |
| A15 | Methods L228 — Phase-1 hyperparameter optimum | d = 6, r = 1, k = 30, AUC 0.8534 ± 0.0490 (n = 200) | **L013 (new)** | `results/figures/p3_qp_optimization_table.csv` row 2 = 0.8534 / 0.0489 ✓ (manuscript rounds σ up) |
| A16 | Methods L228 — Phase-2 confirmation | d = 6, r = 1, k = 30, AUC 0.8283 ± 0.0371 (n = 5000) | **L013 (new)** | `p3_quantum_params_sweep.csv` ✓ |

---

## B. CRITICAL

### C1 — TFP AUC 0.587 contradicts the manuscript's own Table 1 and every deposited benchmark

- **Locations:** line 533 — "why does the TFP perform poorly at predicting absolute antimalarial activity (AUC 0.587)"; line 546 — "the enriched TFP … showed no improvement over the 12-feature TFP baseline (AUC 0.587)".
- **Conflicting value in the same manuscript:** Table 1, Table 2, Abstract and Discussion all state TFP = **0.877**.
- **Source check:** no benchmark file contains a TFP AUC of 0.587. The two files that carry TFP are:
  - `p3_classical_benchmark_19849.csv` → TFP = 0.8767 (n = 19,849, RF, 5-fold)
  - `p3_sota_benchmark_full.csv` → TFP-12 rf = 0.86681 ± 0.00650 (n = 19,849); TFP-12 svm = 0.78572 (n = 5,000)
- **Effect:** line 533 builds the paper's central mechanistic argument — the "biophysical paradox" of poor activity prediction alongside strong resistance-resilience correlation — on a number 0.29 AUC below what the paper reports everywhere else. At TFP = 0.877 the paradox framing does not hold: TFP is a strong activity predictor, 0.072 behind ECFP4.
- **Required action:** author decision. Either (a) 0.587 is stale and both sentences are rewritten against 0.877, restating or dropping the paradox framing; or (b) 0.587 belongs to a specific configuration (SVM? subsample? enriched-only?) that must be named, deposited, and ledgered.

---

## C. HIGH

### H1 — "enriched TFP (78 features)" ≠ deposited 32 features

- **Location:** line 546 — "the enriched TFP (78 features including persistence images and Betti curves)".
- **Source:** `p3_sota_benchmark_full.csv` → `TFP-Enriched` has `n_features = 32`. `PersImage` = 25, `BettiCurve` = 20, `PersStats` = 22. No row has 78.
- **The conclusion survives:** TFP-Enriched rf 0.86656 vs TFP-12 rf 0.86681 → ΔAUC = −0.0002, genuinely no improvement. Only the feature count and the AUC are wrong.

### H2 — Silhouette values are untraceable

- **Location:** Table 4 (`tab:clustering`, L393–395), §4.5 L353, Discussion L503, Methods L234.
- **Values:** TNE 0.350, VAE latent 0.229, ECFP4 0.180; KMeans k = 484; stated target "> 0.35".
- **Source check:** no CSV in `results/` holds these as clustering metrics; no script in `scripts/` mentions `silhouette`. Calinski–Harabasz and Davies–Bouldin are promised in Methods L234 and never reported.
- **Weight:** Discussion L503 uses this as one of three pillars supporting TNE information retention.

### H3 — Two Phase-2 hyperparameter configurations have no deposited run

- **Location:** Methods L228 — "$d=6, r=6, k=30$: AUC 0.8121 ± 0.0396; $d=6, r=6, k=20$: AUC 0.8047 ± 0.0354".
- **Source:** `p3_quantum_params_sweep.csv` contains one row only — (6, 1, 30). Both comparison configurations are absent.
- Methods also describes a Phase-1 grid of d∈{4,6,8} × r∈{1,3,6} × k∈{10,20,30} = 27 combinations; `p3_qp_optimization_table.csv` holds 3 rows. The grid as described is not deposited.

### H4 — `tab:qkernel` p-value column basis disagrees with the ledger

- Table 3 header L361 reads `{$p$ vs.~RBF}`; the Linear row L365 gives `p = 0.198`.
- Ledger L009 records Linear `p = 0.063` against **QK**, not RBF.
- Either the manuscript reports a different, undeposited Linear-vs-RBF test, or the column header is wrong. Both cannot be right.

### H5 — Table 1 keeps ΔAUC for the provisional rows that Table 2 explicitly disowns

- `tab:hybrid` caption L436: "Statistical comparisons vs. ECFP4 have been removed because the hybrid/ablation values were generated with the previous 0.868 baseline and are not comparable to the corrected 0.949 baseline."
- Both tables nevertheless print a ΔAUC column for exactly those rows: QKS −0.198, Hybrid −0.107, TFP+ECFP4 −0.084, ablations −0.112 / −0.114 / −0.341. Each equals `value − 0.949`, i.e. precisely the cross-baseline subtraction the caption says was withdrawn.
- Dropping the p-values while keeping the differences reinstates the comparison the caption disclaims.

---

## D. MEDIUM — orphan groups (no ledger entry)

| # | Claim | Location | Note |
|---|---|---|---|
| M1 | `tab:tda_stats` — 48 values (mean/std/min/max × 12 TDA features) | L266–279 | L010 covers 4. Source is `p3_tda_fingerprints.csv`; entry needs writing. |
| M2 | Accuracy and F1 for QKS (0.680/0.710), Hybrid (0.745/0.758), ablations (0.740/0.753, 0.738/0.750, 0.593/0.408) | Tab.1, Tab.2 | L004/L007/L009 record AUC only. |
| M3 | Row "TFP + ECFP4 (p)" — 0.865 / 0.780 / 0.787 | Tab.1 L319, Tab.2 L448 | No ledger entry of any kind; not in `p3_classical_benchmark_19849.csv`. |
| M4 | TNE reconstruction error 0.098 (within 0.1 Tanimoto of a seed) vs 0.137 (atypical) | L503 | No source file. UNTRACEABLE. |
| M5 | Mode-3 factor matrix vs molecular volume, Spearman ρ = 0.71 | L503 | No source file; no script computes molecular volume. UNTRACEABLE. |
| M6 | Compute cost: TDA 6.4 min / 19 ms per molecule; TNE 20 min / 50–60 ms; conformer ~2 s; 12-core, 8 Joblib workers | L507, L525, L558 | No timing log deposited. `p3_scalability_results.csv` times the kernel path only. |
| M7 | Dataset provenance: 65,856 generated, 396 African NP seeds, 454 synthetic drugs, ANPDB 11,000, activity threshold 0.5 | L134 | Carried from Paper 1; entry must name the upstream source. |
| M8 | Tartarus: 19,913 primary leads docked | L463 | L006 gives per-target N (11,878 / 17,075 / 17,074); 19,913 unlinked. |
| M9 | TDA success: 19,836 valid, 13 failed, 99.93 % | L256, L340, L183 | Arithmetically consistent (19,836/19,849 = 99.935 %) but unledgered. |
| M10 | TNE arithmetic: 38 mean atoms → 5.9× real, 15.6× padded, 1140 → 192 elements, recon error 0.113 (max 0.220) | L175, L183, L340, L501 | Derivation shown in-text; 38.05 traces to `tab:tda_stats`. Still needs one entry. |

---

## E. Resolved this pass

**Headline-number conflict (spine `[BLOCKING]` line, dated 2026-07-27) — STALE, now closed.**

The spine recorded "headline ECFP4 0.868 / Hybrid 0.842 — no deposited CSV reproduces". Since the Phase-11 sync this no longer describes the manuscript:

- Abstract (L99), Table 1 (L309), Table 2 (L442), Discussion (L509, L513, L525, L548) and Conclusion (L558) all use **ECFP4 = 0.949**, which `p3_classical_benchmark_19849.csv` reproduces exactly.
- **0.868 survives in exactly one place** — the `tab:hybrid` caption (L436) — where it is named as the superseded baseline and used to justify withdrawing the statistical comparisons. That is the correct, honest use.
- Hybrid 0.842 remains non-reproducible, and the manuscript now says so at every occurrence (L317–318, L324, L432, L436, L447, L458, L513, L521, L525, L548, L550, L558). It is labelled provisional and excluded from every conclusion.

Residual issue arising from this: **H5** above.

Note also that `p3_hybrid_benchmark.csv` is a 90-row smoke-scale file (9 descriptors × 10 folds; fold accuracies computed on ~10 samples; ECFP4 mean 0.9557, Hybrid mean 0.5085, TFP 0.5558). It is **not** the source of Table 2 and must not be cited as such.

---

## F. Gate arithmetic

| Check | Result |
|-------|--------|
| Ledger entries carrying a written interpretation | 14 / 14 PASS |
| Ledger entries naming a source | 13 / 14 (L007 names BMAD_Q1 §3.5; original run file missing — declared) |
| Manuscript claim groups mapped to a ledger ID | 16 BACKED / 15 unmapped |
| Claims whose source reproduces the number | 16 BACKED · 4 UNTRACEABLE (H2, H3, M4, M5) · 1 CONFLICT (C1) |
| **L1 gate** | **FAIL** |

---

## G. Reconciliation against BMAD_Q1 (authority read in full, 2026-07-31)

Source: `/home/tchapet/Documents/GitHub/SAO/Malaria_codesV2/BMAD_Q1_DATA_ANALYSIS_REPORT.md`, 161,509 bytes, 2,018 lines, v37, dated 2026-07-30. Project rule: this file outranks intermediate CSVs.

### G1 — C1 CONFIRMED. Authoritative TFP value is **0.877**

BMAD_Q1 §3.4 line 841: `| TFP | 0.877 | 0.006 | −0.072 |`, produced by `p3_classical_benchmark_19849.py` on 19,849 molecules, RF 200 trees, `StratifiedKFold(random_state=42)`, dated 2026-07-29. Repeated in the executive summary at lines 20 and 29.

**0.587 appears nowhere in BMAD_Q1 as a TFP value.** The single occurrence of 0.587 in the report is line 550 — `normalised aqueous solubility (logS): mean = 0.587` — an unrelated physicochemical statistic.

Manuscript lines 533 and 546 must be rewritten to 0.877. Line 533 is the load-bearing one: its premise is that TFP predicts activity *poorly*, which at 0.877 (0.072 behind ECFP4, ahead of nothing-but-TNE) is not true. The "biophysical paradox" framing needs restating or dropping, not just a number swap.

### G2 — the 0.877 / 0.867 gap is explained, not a defect

`p3_sota_benchmark_full.csv` runs `class_weight='balanced'` against a 75.9 % / 24.1 % imbalance (BMAD_Q1 lines 1773, 1777); `p3_classical_benchmark_19849.csv` does not. Same library, different weighting. Quote **0.877** for the headline descriptor ranking and 0.867 only inside the class-weighted topological comparison. Never interchangeably. Removes the MEDIUM "unexplained discrepancy" raised in §D.

### G3 — H1 CONFIRMED: 32 features, not 78

BMAD_Q1 line 1758 (`TFP-Enriched | RF | … | 32`) and line 1771 ("TFP-Enriched (32 features) ≈ PersImage (25 features) ≈ TFP-12 (12 features)"). The manuscript's "78 features" at L546 has no source anywhere.

Caution when quoting the comparison: BMAD_Q1's E.1 table (lines 1755–1766) **mixes two sample sizes**. Its PersStats AUC cell is the n=19,849 value (0.8731); its TFP-Enriched, PersImage, TFP-12 and BettiCurve cells are n=5,000 values, as are all its accuracy and F1 cells. BMAD_Q1's own note at line 1785 documents the split. Take both members of any pair from the same file: n=19,849 → 0.86681 vs 0.86656 (Δ = −0.0002); n=5,000 → 0.8303 vs 0.8381 (Δ = +0.0078). The "no improvement" conclusion holds either way.

### G4 — H3 RETRACTED. The Phase-2 runs are deposited

BMAD_Q1 lines 882–884 name all three runs and their files; all three are present in `results/`:

| Combo | d | r | k | AUC (n=5,000) | σ | time (s) | Source |
|---|---|---|---|---|---|---|---|
| 1 (best) | 6 | 1 | 30 | 0.8283 | 0.0371 | 21,719 | `p3_phase2_bd6_nr1_nk30_raw.csv` |
| 2 | 6 | 6 | 30 | 0.8121 | 0.0396 | 28,282 | `p3_phase2_bd6_nr6_nk30_raw.csv` |
| 3 | 6 | 6 | 20 | 0.8047 | 0.0354 | 27,914 | `p3_phase2_bd6_nr6_nk20_raw.csv` |

The original finding checked only `p3_quantum_params_sweep.csv` and was wrong. Both values are BACKED.

### G5 — H3b (new HIGH): the Phase-1 grid is misdescribed

Manuscript L228: d ∈ {4,6,8} × r ∈ {1,3,6} × k ∈ {10,20,30} = 27 combinations.
BMAD_Q1 line 856: "Grid search over 3×5×4 = **60** combinations (bond_dim∈{4,6,8}, n_repeats∈{**1,2,3,4,6**}, n_kpca∈{**5**,10,20,30}). Job 7962 (sequential, ~8h) completed **50/60** combos before termination."

Wrong repetition set, wrong KPCA set, wrong total, and the truncation is undisclosed.

### G6 — H6b (new HIGH): the QKS evaluation set is 500, not 10,000

BMAD_Q1 §3.3 line 815 heads the table "5-fold Cross-Validation (**500-mol** representative subsample, July 2026)"; line 823 repeats it; the executive summary line 20 states "QKS benchmark on **500 molecules** (sub-sampled from the 10,000-molecule design target)".

The manuscript states 10,000 in five places: Tab.1 footnote L323, Tab.2 footnote L457, Tab.3 caption L357, §4.5 L351, and Methods L238. Ledger L009 inherited the same figure.

BMAD_Q1 contradicts itself here — the data inventory at line 1741 still lists 10,000 — but §3.3 is the dated results section carrying the "July 2026 Ground Truth" label and the v37 summary agrees with it. A 20× overstatement of the evaluation set is a reproducibility failure a referee will catch.

### G7 — H7b (new HIGH): target alignment 0.684 vs 0.543

BMAD_Q1 §3.3 line 820: `Target Alignment | 0.684 ± 0.021 | 0.334 ± 0.116 | — |`.
Manuscript Tab.3 and ledger L004/L009: 0.543, sourced from `p3_qks_summary.txt` (`target_alignment 0.5432 ± 0.0177`).

The spine records PHASE10-FIX (2026-07-28) deliberately changing 0.684 → 0.543 on the deposited CSV's authority. Under the standing rule that BMAD_Q1 outranks intermediate CSVs, that change went the wrong way. Author ruling needed; both values cannot stand.

### G8 — H8b (new): circuit name unresolved in the authority

BMAD_Q1 §3.3 line 817 labels the column "Quantum Kernel (**StronglyEntanglingLayers**)". Phase 12 unified the manuscript on `IQPEmbedding`, citing "BMAD_Q1 §3.4" — but §3.4 is the classical benchmark section and names no circuit. The QKS section of the authority still says StronglyEntanglingLayers.

### G9 — H2 unchanged and now weaker

No Silhouette value, no `0.229`, and no Calinski–Harabasz or Davies–Bouldin index appears anywhere in BMAD_Q1's 2,018 lines. Table 4 has neither a deposited source nor authority backing.

### G10 — M9 and M10 CLOSED

BMAD_Q1 §3.2 lines 804–811 confirm 19,836 valid / 13 failed, 15.6× padded compression, mean reconstruction error 0.1130, 20-minute runtime, 19,849 processed, and the 5.9× real ratio at ~38 atoms. §3.1 line 796 confirms H₀ count mean 38, SD 7. Both orphan groups now have an authoritative source; ledger entries still need writing, but nothing is unverified.
