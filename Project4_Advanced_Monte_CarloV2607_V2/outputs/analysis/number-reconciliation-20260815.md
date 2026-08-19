# P4 — number reconciliation, manuscript vs ledger

**Date:** 2026-08-15 · **Loop:** L1 beat 1 · **Scope:** every quantitative statement in
`P4_Pareto_MCTS_JoC_refined.tex` (383 l.) and `P4_Pareto_MCTS_JoC_SM.tex` (265 l.)

**Ledger consulted:**
- `../P4_DATA_ANALYSIS_REPORT.md` (active summary, 58 l.)
- `../docs/archive/md_full_20260812/P4_DATA_ANALYSIS_REPORT.md` (long form, 542 l. — authoritative)
- Source artifacts under `results/`

---

## Verified clean — traced to a named artifact

| Claim | Value | Source | Status |
|---|---|---|---|
| v12 scalar benchmark, 4 methods | 0.6724 / 0.6649 / 0.6453 / 0.4278 | DAR §2 + `results/benchmark_molecules_opt_v12/` | PASS |
| MCTS vs Random | t₁₉ = −4.97, p = 0.000085, Δ = −0.0075, CI [−0.0107, −0.0043] | DAR §2 | PASS |
| MCTS vs GA | t₁₉ = 6.95, p < 0.0001; Bonferroni 0.025 | DAR §2 | PASS |
| Greedy deficit 0.2446 below Random | 0.6724 − 0.4278 = 0.2446 | arithmetic | PASS |
| Pareto front, 4 points, HV 1.2366 | MPO/SYBA/SA⁻¹/RRS/PNS table | DAR §3, `results/pareto/` | PASS |
| SA⁻¹ transform | (10 − 3.0)/9 = 0.7778 → 0.778 | Methods, recomputed | PASS |
| Component ablation main effects | ScafVAE +0.148, Pareto +0.108, vocab +0.079 | recomputed from `results/ablation/p4_component_ablation_summary.csv` | PASS |
| c_PUCT 2.0 → 1.0 | 0.73123 − 0.67672 = 0.05451 → +0.055 | same CSV | PASS (manuscript correct) |
| Temperature effect | 0.71019 − 0.69776 = 0.01243 → +0.012 | same CSV | PASS (SM correct) |
| Front comparison table | HV 13.85/16.59/15.49/15.52/18.99; C 0.059/0.765/0.000/0.000/0.824; IGD_loo; spread | `results/pareto/p4_multiobj_front_summary.csv`, all 5 rows exact | PASS |
| Selection ablation | proxy 15.56 vs Pareto-only 15.49, 5 seeds × 700 it | DAR long form l. 498 | PASS |
| — the 15.49 collision with GA's front HV is a genuine coincidence, confirmed in the ledger | | | PASS |
| Scalar weight sweep | P3 argmax only at w_MPO ≳ 0.997 (0.3 % of weight space), 100001 grid points | DAR l. 498 | PASS |
| Reward weight vectors | default sums to 1.000; v12 reduced sums to 1.000 | recomputed | PASS |
| Vocabulary ANOVA | F = 350.1, p = 1.12e−26, Tukey p_adj = 0.0052 | DAR | PASS |
| Diversity | 0.7732 / 0.8046 / 0.0000 / 0.7761; scaffolds 19/20/1/12 | SM S3, `results/diversity/` | PASS |
| v12-allfrag values | 0.6701 ± 0.0108 / 0.6488 ± 0.0152 / 0.6427 ± 0.0138 / 0.4593; Δ = −0.0214; 19/20 seeds | DAR §1.12 — **numbers exact** | PASS (but see C1) |
| Structural deficit detail | ~200 iterations to convergence; PW 5–20 of 80; ~1000 vs ~200–300 unique molecules | DAR §1.12 | PASS |
| RF activity validation | n = 19836; CV AUC 0.9479 ± 0.0040; mean prob 0.676 ± 0.135; 18/20 active | `results/pareto/p4_activity_rf_oracle.json` | PASS |
| RF — Tanimoto aggregate | recomputed from the 20 per-seed rows: mean 0.24155, sample SD 0.05163 → **0.242 ± 0.052** | recomputed | PASS |
| RF — Pearson r | recomputed: r = 0.8027 → **0.803** | recomputed | PASS |

Two aggregates in the Limitations paragraph (Tanimoto mean ± SD, Pearson r) are **not stored** in
the JSON; they were recomputed from its 20 per-seed records and both round correctly.

---

## Findings

### CRITICAL

**C1 — `results/benchmark_v12_allfrag/` does not exist anywhere in the repository.**
DAR §1.12 records the experiment as job 15133 with outputs in `results/benchmark_v12_allfrag/`.
`find . -iname '*allfrag*'` over the whole of `Malaria_codesV2` returns nothing — absent from both
`Project4_Advanced_Monte_CarloV2607` and `..._V2`. This artifact backs `\Cref{tab:allfrag}`
(Results §Component and vocabulary ablations), the "deficit widens under the full vocabulary"
sentence in the Discussion, and the structural-cause argument that follows it. The Data availability
section lists only `benchmark_molecules_opt/` and `benchmark_molecules_opt_v12/` — the allfrag run
is not even claimed. For a journal that reviews reproducibility, a table with no deposited source is
a submission blocker. *Resolution requires the author: recover the job-15133 outputs and deposit
them, or withdraw Table 4 and the argument it supports.*

**C2 — LaTeX escape defect renders as literal text in the Results.**
`P4_Pareto_MCTS_JoC_refined.tex:137` contains `(\\num{0.6856})`. The doubled backslash makes `\\` a
line break, so the current PDF reads:

> "…and the highest individual seed (
> num0.6856)."

Verified with `pdftotext` on the deposited PDF, p. 4. Compilation gives no error, which is why the
0-undefined-reference check missed it. Mechanical fix.

### HIGH

**H1 — Fragment-vocabulary size is self-contradictory.**
Limitations (l. 285): "The fragment vocabulary (approximately \num{108} fragments…)".
Results (l. 247) and `tab:allfrag`: "the full \num{80}-fragment vocabulary"; medium = 37.
The ledger shows both are real but belong to different eras — DAR l. 212 labels the vocabulary
ablation's *All* condition "Full 108-fragment vocabulary", while DAR §1.12 defines
`FRAGMENT_SET=all` as 80 fragments against medium's 37. Both numbers appear within the same
manuscript subsection region, so a reader sees the "full" vocabulary described as 80 and the total
as 108. *Author decision needed:* state the v12-era counts throughout (37 / 80) and, if the older
108-fragment set matters, label it explicitly as the ablation-era vocabulary.

**H2 — Two hypervolume conventions, one of them undefined.**
Methods §Pareto front maintenance defines HV over min–max normalised objectives with reference
point r = 1.1 per active dimension, "so that the reported value lies in [0, 1.1]^k". For k = 4 that
caps HV at 1.4641, and the SM's 1.2366 obeys it. But `tab:front_comp` reports 13.85–18.99 and
§selection_ablation reports 15.56 / 15.49 — an order of magnitude outside the stated range, under a
caption that says only "a common min–max normalisation". Every one of those values traces exactly
to `p4_multiobj_front_summary.csv` and to DAR l. 498, so **no number is wrong**; what is missing is
the second convention's definition (normalisation basis and reference point). As written the two
sections contradict each other. Fix is a sentence in Methods plus a caption clause.

**H3 — WHO burden figures are attributed to the wrong report year.**
Introduction (l. 80): "\num{247} million cases and \num{619000} deaths in 2023
\citep{WHO2024MalariaReport}". The bibliography entry is *World Malaria Report 2024*, which reports
**263 million cases and 597 000 deaths for 2023**. The quoted 247 million / 619 000 are the 2021
figures from the *World Malaria Report 2022*. Both the numbers and the year are wrong for the cited
source. Opening-paragraph factual error against a source a malaria reviewer knows by heart.

### MEDIUM

**M1 — siunitx splits four-digit decimals throughout both documents.**
`group-minimum-digits = 4` (main l. 29, SM l. 29) applies grouping to the fractional part, so every
reward renders as "0.672 4 ± 0.005 6". 78 occurrences in the main PDF, same pattern in the SM.
Fix in the preamble: `group-digits = integer` with `group-minimum-digits = 5`, which leaves decimals
intact and still groups 19 321 / 22 447 / 619 000.

**M2 — the RF-validation script is not runnable by a reader.**
`scripts/p4_activity_rf_oracle.py` hardcodes `/home/nanaengo/Malaria_codesV2/...` for the P5 panel,
the v12 benchmark directory, the Pareto front and the output path. SM S6 states "the accompanying
scripts regenerate the reported analyses"; this one cannot, on any machine but the author's.

**M3 — objective list names accessibility twice.**
Results l. 112: "combined MPO, docking, synthetic accessibility, SA and public-activity proximity".
The v12 weight vector is w_MPO, w_docking, w_SYBA, w_SA, w_activity — the third term should read
SYBA, not "synthetic accessibility", which duplicates SA.

**M4 — SM data-availability statement is weaker than the main text's.**
SM S6 says only "the article's open computational materials"; the main text names
`https://github.com/NanaEngo/Malaria_codesV2` and lists five artifact classes. The SM should carry
the same URL.

### LOW

**L1 — ledger rounding, manuscript is correct.**
DAR long form l. 202 gives the c_PUCT effect as +0.054 and temperature as +0.011; the exact CSV
values are 0.05451 and 0.01243, so the manuscript's +0.055 and +0.012 are right and the ledger is
the file to correct.

---

## Disposition

| Finding | Fixable without author | Action |
|---|---|---|
| C1 | no | author must deposit job-15133 outputs or withdraw Table 4 |
| C2 | yes | mechanical |
| H1 | no | author picks the vocabulary numbers to standardise on |
| H2 | yes, as documentation | add the second HV convention to Methods + caption |
| H3 | yes | correct to 263 million / 597 000 for 2023 per the cited report |
| M1 | yes | preamble, both documents |
| M2 | yes | parameterise paths |
| M3 | yes | one word |
| M4 | yes | one sentence |
| L1 | yes | edit ledger, not manuscript |
