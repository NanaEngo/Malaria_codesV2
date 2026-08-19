# P4 — project tracking (spine)

**Active loop:** **L4 COMPLETE 2026-08-18 / V1–V2 diff audit 2026-08-19** — Pre-submission audit passed all 9 gates; 3 CRITICAL items fixed via Option A (Greedy rerun 0.6676, fragment priors → heuristic, multi-obj v12 rerun); 5 HIGH items fixed; manuscript CLEARED FOR SUBMISSION to Journal of Cheminformatics · **Next:** first submission (L5) · **beat:** 12 · **opened:** 2026-08-18

**L3 summary:** Adversarial (3C+2H+4M+4L) · Edge-case (1H+2M) · Peer (3 reviewer objections) · Critical-think (1H+2M, no overclaim) · ScholarEval (3.94/5.0) · Prose (4.5/5, 0 AI patterns) · Structure (4.5/5, sound) · Files: `outputs/critical-reviews/review-*-20260818.md` + `L3-SUMMARY-20260818.md`

**Historical context:** L1+L2 done · L3+L4 self-verified 2026-08-16 (maker=checker, insufficient) · independent review 2026-08-17 verdict "No — qualified-negative" — 3 CRITICAL + 6 HIGH defects survive, all author decisions, central negative result untouched · figures fixed and verified 2026-08-17 · provenance lock green · manifest current as of 2026-08-17 21:26 build

> **Checkpoint 2026-08-15.** L1 reconciliation complete; L2 fixes applied; main + SM compile clean
> (0 errors / 0 undefined / 0 overfull, 14 pp., 20 refs). **The L3 battery was launched and all 7
> passes died on the session usage limit. No review files were written — `outputs/critical-reviews/`
> does not exist. L3 must be re-run from scratch.**
>
> *Superseded 2026-08-17 on the last sentence only.* `outputs/critical-reviews/` now exists and holds
> one file, `review-claim-ledger-20260817.md`, the record of the maker ≠ checker gate. The 2026-08-15
> statement stands as history: those seven passes did die and wrote nothing.
>
> **Applied this session:** C2 `\\num` render bug · C3 xr-hyper/cleveref rebuild failure ·
> H2 two HV conventions documented · H3 WHO figures corrected to 263 M / 597 000 ·
> M1 siunitx decimal grouping · M2 RF script paths · M3 SYBA/SA duplication · M4 SM data availability ·
> O4 cross-paper citations to P2/P3 · O5 British spelling · M5 missing method citations
> (SYBA, Ertl SA, QED, MCTS/PUCT, scikit-learn).
>
> **Still blocked on author:** C1 (missing `benchmark_v12_allfrag/` raw artifact; the numbers themselves
> are ledger-backed by DAR §1.12, and the author has directed that the table stay as is). H1 is closed:
> the author ruled the vocabulary is **the v12 set — full = 80, medium = 37** — and the manuscript and SM
> now say so.
>
> **BMAD_Q1 compliance pass (authoritative `../BMAD_Q1_DATA_ANALYSIS_REPORT.md`).** Its §3 and
> cross-project rule 3 fix P2's canonical resistance layer as **docking-derived**; full-panel
> MD-RRS is `NOT_COMPUTED`. Three sentences added earlier this session had described
> `Temgoua2026b` as "the companion molecular-dynamics study" and promised its per-target WT/mutant
> ratios as a "mechanistically grounded" resistance dimension — an uncomputed MD claim propagating
> into P4. All three rewritten to name the companion **polypharmacology** study and its
> **docking-derived** ratios, with an explicit statement that no molecular-dynamics resistance
> quantity enters this work. `PfClpR` corrected to `PfClpP` per the §3 identity boundary. The P3
> descriptor sentence now states complementarity to established fingerprints rather than
> superiority, matching §4 ("no quantum advantage is claimed"). Rebuild clean, 14 pp.

## Target

| Field | Value |
|---|---|
| Paper | P4 — Pareto-guided MCTS for antimalarial candidate generation |
| Journal | **Journal of Cheminformatics** (Springer) |
| Type | Original research (methods/benchmark) |
| Stage | Refined draft, compile-clean; pre-submission audit |
| Central claim | Pareto-MCTS does **not** beat Random on scalar reward; its value is auditable multi-objective candidate-set geometry |

## Environment

| Item | Value |
|---|---|
| venv | `/home/tchapet/VirtualEnv/bin/python3` |
| Working folder | `Project4_Advanced_Monte_CarloV2607_V2` (untracked copy of tracked `Project4_Advanced_Monte_CarloV2607`; author will commit as new version) |
| skill_checksum | `3febe7a48ff8133f0f19322792a831b3d2ebefa2df50b4cbbc81f66ee3359a2f` |
| Skill drift | `~/.opencode` only — deliberate host fork, expected |
| Anti-AI baseline | 0 banned patterns (2026-08-15) |

## Ledger (two-tier — hard rule 3)

| Tier | Path | Lines |
|---|---|---|
| Active summary | `../P4_DATA_ANALYSIS_REPORT.md` | 58 |
| Long form (authoritative, has §1.8 / §1.12 / §6.12) | `../docs/archive/md_full_20260812/P4_DATA_ANALYSIS_REPORT.md` | 542 |

No `outputs/analysis/analysis-ledger.md` is created: the DAR **is** the ledger for this project. New calculations append to the long form.

## File map

| File | Role |
|---|---|
| `manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex` | main, 385 lines |
| `manuscript/LaTeX/P4_Pareto_MCTS_JoC_SM.tex` | SM S1–S6, 274 lines |
| `manuscript/LaTeX/Cover_Letter_P4_JoC.tex` | cover, 60 lines |
| `manuscript/LaTeX/P4_Bibliography.bib` | refs |
| `manuscript/LaTeX/SUBMISSION_MANIFEST.md` | **current as of 2026-08-17 21:26 UTC** — regenerated in one pass after the second (reproducibility) cycle; O1 closed |
| `P4_ADVERSARIAL_AUDIT_MITIGATION_JoC_V12.md` | risk register |
| `P4_TODO2608.md` | cross-paper TODO |
| `results/benchmark_molecules_opt_v12/` | canonical scalar benchmark (job 12865, 20 seeds) |
| `results/pareto/` | pre-activity Pareto front |

## Canonical numbers (v12-activity scalar benchmark)

| Method | Mean reward ± SD |
|---|---:|
| Random | 0.6724 ± 0.0056 |
| MCTS + ScafVAE | 0.6649 ± 0.0068 |
| GA | 0.6453 ± 0.0124 |
| Greedy | 0.4278 ± 0.0000 |

MCTS vs Random: paired t₁₉ = −4.97, p = 0.000085, Δ = −0.0075, 95 % CI [−0.0107, −0.0043].
MCTS vs GA: t₁₉ = 6.95, p < 0.0001. Bonferroni threshold 0.025 (2 primaries).
Pre-activity Pareto front: 4 non-dominated solutions, HV = 1.2366, SA constant 3.0 → SA⁻¹ = 0.778.
Ablation (2⁵, 160 runs): ScafVAE +0.148 · Pareto +0.108 · large vocabulary +0.079.

## Decisions (2026-08-15, author)

1. Work in `_V2`; commit as a new version afterwards.
2. **Zenodo dropped.** Repo-only data availability (`github.com/NanaEngo/Malaria_codesV2`). TODO P0 Zenodo rows closed as superseded — no DOI to insert.
3. Session scope: reconcile numbers vs DAR → cross-paper one-liners + British spelling → full L3 battery → regenerate manifest last.

## Open items

| # | Item | State |
|---|---|---|
| O1 | `SUBMISSION_MANIFEST.md` stale — header said generated 2026-08-15 11:53 UTC while the source had advanced, both `.tex` rows moved again on 2026-08-17 (five hypervolume-description edits), and the header page counts (13 / 4 / 2) disagreed with the L4 note (14 / 4 / 2) | **closed 2026-08-17 19:47** — regenerated whole-file in one pass, not row by row, and only after the replot and the rebuild that followed it, so no row records a superseded file. 7 inventory rows + 15 graphics rows re-hashed; header now reads 14 / 4 / 2 and `20 references`; the in-file STALE banner is replaced by a build-currency note. Ordering is verifiable from mtimes — replot source 13:39, figures 20:38:57, `refined.pdf` 20:39:15, `SM.pdf` 20:39:16 — so neither PDF predates the figures it embeds. `p4_hv_vs_ref.png` is kept and hashed but its row is labelled unused, per the disposition note below. Two figure sizes forecast before this pass (267128 B, 315206 B) were superseded by it and are recorded as such. **Re-run on author instruction at 21:26 the same day and regenerated again in one pass, so the manifest now describes the 21:26 build:** the re-run doubles as a figure reproducibility check — all six data-figure PNGs are byte-identical (same sizes, same SHA-256), while the six figure `.pdf` sidecars keep their byte sizes but take new hashes and the two documents move a few bytes (`refined.pdf` 554945 → 554946 B, `SM.pdf` 315239 → 315242 B) as the embedded creation date is re-encoded; page counts unchanged at 14 / 4. Mtimes for that pass: figures 22:07:40–41 local, `refined.pdf` 22:13:25, `SM.pdf` 22:13:26. The 19:47 sizes and hashes are superseded but kept in the manifest's O1 note for the record |
| O2 | Reconcile every manuscript number against DAR long form | **done** — every number traces to a named artifact; the only ledger-only set is `tab:allfrag` (DAR §1.12), disclosed in Data availability |
| O3 | `v12-allfrag` result in DAR long form (Random 0.6701 ± 0.0108 > MCTS 0.6488 ± 0.0152, Δ = −0.0214, 19/20 seeds; structural cause §1.12) — confirm whether main text reports it | **done** — reported as Table 4 (`tab:allfrag`) and now also in the abstract; retained as is per author instruction |
| O4 | Cross-paper one-liners: RRS/PNS → P2, topology → P3 | **done** — and the internal series labels were subsequently removed: the companion studies are named by subject, not by "P2"/"P3", which collided with the Pareto candidate labels |
| O5 | British-spelling sweep across main/SM/cover | **done** — 0 US spellings, 0 banned anti-AI patterns |
| O6 | Full L3 review battery | **done 2026-08-16, self-verified** — reopened at author request and run inline rather than as a 7-agent fan-out to `outputs/critical-reviews/`: the harness forbids unrequested Agent calls and the author asked for no report file. 7/7 BMAD_Q1 compliance checks PASS, no overclaim found; every surviving defect was formatting or internal consistency. Maker = checker |
| O7 | Human visual PDF inspection + submission zip (author task) | **partly discharged 2026-08-17** — all 7 files under `manuscript/LaTeX/Graphics/` were inspected at final printed size against their source tables; every numeric element matches `tab:sm_pareto`, `tab:sm_benchmark`, `tab:sm_diversity` and `tab:sm_component_ablation`, and no figure contradicts a table. Four defects logged, all originating in `scripts/p4_replot_publication.py`: (1) `rrs_pns_profile` — x tick labels collide in **both** panels, `MCTS+ScafVAE` and `Genetic algorithm` overprinting as one string [print-blocking]; (2) `scaffold_diversity` — legend drawn inside the data region over the markers, and the provenance footer overprints the fourth legend entry [print-blocking, worst of the six]; (3) `p4_evidence_overview` panel B — the P1 point (MPO 0.910, SYBA 1.000) is plotted but unlabelled while P2/P3/P4 are labelled, inconsistent with `pareto_front.png` [content]; (4) `benchmark_efficiency` — Greedy and GA sit left of the first labelled log tick with no minor-tick labels, so their x values are unreadable at print size [legibility]. Separately, `p4_hv_vs_ref.png` is stylistically orphaned: default matplotlib blue rather than the Okabe-Ito palette, no provenance footer, no `.pdf` sidecar, clipped title ("…to reference" should read "…to reference point"), and it is cited in neither `.tex` — the manifest's replot note covers only "all six data figures". **All four defects were then fixed in the source of `scripts/p4_replot_publication.py` the same day, the script was re-run, and the re-rendered files were re-inspected at printed size — 4/4 confirmed gone** (see the review-log rows below). One second-pass residual was fixed in the source and has now reached disk: lifting the `scaffold_diversity` legend left the provenance footer's opaque background masking the lowest MCTS marker, so a blank band is reserved by extending the lower y limit by 14 % of the data range, and the figure was re-rendered on 2026-08-17 at 20:38:57 (269940 B, 2716 × 2362 px) with both PDFs rebuilt from it afterwards. Still open and author-owned: human sign-off on the re-rendered figures and the rebuilt PDFs, the disposition of `p4_hv_vs_ref.png`, the `MCTS+ScafVAE` annotation sitting tight against the right spine in `benchmark_efficiency` (cosmetic), and the submission zip |
| O8 | Suggested reviewers — contact details + conflict check (author task) | open |
| O9 | 20-seed validated pre-activity SYBA rerun (`results/pareto_syba_validated/`) — not required for the evidence-bounded submission | deferred, documented |
| O10 | `scripts/p4_verify_v11_checks.py` asserts v11 values and reads the superseded `results/benchmark_molecules_opt/` — it cannot pass against the v12 manuscript | **closed 2026-08-17 — retired in place, not ported.** Every check group in the file is v11-era: the diversity expectations (mcts 0.8023, random 0.7806, ga 0.8332/17/0.85) now fail against `results/diversity/p4_diversity_metrics.csv` *itself*, which holds 0.7732 / 0.8046 / 0.7761-12-0.600; the canonical rewards 0.7335/0.7276/0.7027/0.6147 are v12's 0.6724/0.6649/0.6453/0.4278; both paired *t* values (−2.41, 5.55) are v12's −4.97 and 6.95; the seed-win count 5/20 is 1/20; both wall-clock checks (82.2 s, 42.4 s) are 92.1 s and 50.4 s, outside the ±5 s tolerance coded in the file; and 4 of 8 SM string greps plus all 9 main-text greps look for literals absent from the v12 sources. Porting would mean replacing ~30 constants and the input directory — i.e. writing a new verifier that duplicates `scripts/p4_pareto_provenance_check.py` (Pareto front, active objectives, HV 1.2366), `scripts/p4_n2_power_test.py` (selection-ablation ΔHV) and the 2026-08-17 recomputation. Mechanism: a `RETIRED 2026-08-17` module docstring naming every stale assertion class and its v12 replacement, plus an early `sys.exit(0)` unless `P4_RUN_RETIRED_V11_CHECKS=1`. Exit 0, not 1, so a `scripts/p4_verify_*.py` sweep does not read "deliberately not run" as a verification failure. The v11 constants are kept verbatim below the gate as the historical v11 record, so no git history is lost and no future reader can run the file, see a wall of FAILs and conclude the v12 manuscript is wrong |
| O11 | Selection-ablation hypervolumes of SM S5 (15.56 scalar-proxy / 15.49 Pareto-restricted, bound 19.45) | **closed 2026-08-17** — both values, the merged front sizes (60 / 54 after deduplication) and the per-seed front sizes are recorded in `P4_NOVELTY_EXPERIMENTS.md` §N2 and in the long-form DAR l. 498, and `scripts/p4_novelty_n2.sbatch` confirms the 5-seed × 700-iteration budget in executable form. The deposited 1.0628 / 0.6380 are the search-time front-internal indicator, a different quantity, so the "convention-dependent conclusion" reading is withdrawn. Residual, not a blocker: the two values are ledger-recorded rather than stored in a CSV, so reproducing them needs a `p4_merge_pareto_fronts.py` re-run under the shared normalisation |

## Non-goals (do not reopen)

- No claim that MCTS beats Random on mean scalar reward.
- No QMC/DMC publication claims (Tier 2 DMC population collapse).
- No "illustrative/simulated" diversity figures in the main text.
- No softening of the Random > MCTS ranking in abstract or discussion.

## Review log

| Date | Pass | Verdict | Evidence |
|---|---|---|---|
| 2026-08-15 | L1 number reconciliation | 3 CRITICAL/HIGH fixed, 2 blockers open | `outputs/analysis/number-reconciliation-20260815.md` |
| 2026-08-15 | L3 battery | **NOT RUN** — all 7 passes died on session limit | no files written |
| 2026-08-15 | L4 pre-submission audit | **13 PASS / 4 FAIL**, re-run after fixes → **17 PASS / 1 FAIL** | commands below |
| 2026-08-15 | Figure regeneration | all 6 data figures rebuilt, no value changed | `scripts/p4_replot_publication.py` |
| 2026-08-15 | Claim calibration (abstract / Limitations / Conclusions) | 7 defects fixed, self-review only — **maker = checker, not yet independently confirmed** | subsection below |
| 2026-08-16 | Verification-script currency | `p4_pareto_provenance_check.py` current; `p4_verify_v11_checks.py` **stale (v11)** | subsection below |
| 2026-08-16 | Claim calibration — closure | Abstract and Conclusions re-verified, no change needed; Limitations fixed (1 edit, row 8); **self-review only** | subsection below |
| 2026-08-16 | PDF rebuild | **NOT RUN** — `latexmk` refused 19× by the host Bash safety classifier (intermittent and command-agnostic, not permanently down — it came back up on 2026-08-17 and then refused again the same day); source is ahead of both PDFs | O1 stays open |
| 2026-08-16 | Funding statement | corrected on author instruction — hedge removed, duplicated HPC sentence deleted from Funding | subsection below |
| 2026-08-16 | L3 re-run — BMAD_Q1 compliance + internal consistency | **7/7 compliance PASS**, no overclaim; 12 defects found (10 fixable, 2 author decisions) | subsection below |
| 2026-08-16 | L4 re-run | 10 findings closed in 13 edits (8 main `.tex`, 5 SM `.tex`); 4 rows **blocked** on the Bash classifier; **self-verified** | subsection below |
| 2026-08-17 | From-primary-source recomputation | 7 claim groups reproduced from the deposited CSV/JSON; 1 description defect fixed in 5 places (hypervolume is 4-objective, not 3); 1 provenance gap opened and closed the same day (O11), which also closes H2 of the number reconciliation; 1 own earlier finding withdrawn; **same party — maker ≠ checker still UNSATISFIED** | subsection below |
| 2026-08-17 | Figure inspection at final printed size | **7/7 inspected**; every numeric element traced to `tab:sm_pareto`, `tab:sm_benchmark`, `tab:sm_diversity` or `tab:sm_component_ablation` and **no figure contradicts a table**; **0 numeric defects, 4 rendering defects** (2 print-blocking: `rrs_pns_profile` tick-label collision in both panels, `scaffold_diversity` legend over data + footer over legend; 1 content: unlabelled P1 in `p4_evidence_overview` panel B; 1 legibility: unlabelled log minor ticks in `benchmark_efficiency`); `p4_hv_vs_ref.png` additionally flagged as off-palette, footer-less, sidecar-less and cited in neither `.tex` | O7 partly discharged; all four fixed in source, re-rendered and re-confirmed the same day |
| 2026-08-17 | O10 disposition | `scripts/p4_verify_v11_checks.py` **retired in place, not ported** — every check group asserts a v11 value, the diversity block fails against the live `p4_diversity_metrics.csv` itself, and one input directory is superseded; gated behind `P4_RUN_RETIRED_V11_CHECKS=1` and exits 0 so a `p4_verify_*` sweep does not read "deliberately not run" as a failure; v11 constants kept verbatim below the gate as the historical record | O10 closed |
| 2026-08-17 | Selection-ablation front sizes | the ledger's merged front sizes are reproducible from the deposited CSVs: `results/pareto/n2_proxy_merged.csv` holds 71 data rows with 11 duplicate SMILES = **60 unique**, `n2_pareto_merged.csv` holds 56 with 2 duplicates = **54 unique**, both exactly as recorded in `P4_NOVELTY_EXPERIMENTS.md` §N2. **Counted by hand from a visual read — one tier below a mechanical `sort -u \| wc -l`, which still needs the Bash classifier.** The hypervolumes 15.56/15.49 remain ledger-recorded and require re-running the merge under the shared normalisation | strengthens O11; row-count gap resolved, no defect |
| 2026-08-17 | Figure defect repair (source only) | all 4 rendering defects fixed in `scripts/p4_replot_publication.py` in 10 edits, **every one layout-only** — no plotted value, axis range, statistic or caption touched, so the existing captions stay valid and no reported number can move: new `LABEL_WRAP` two-line method names in both `fig_rrs_pns` panels; `fig_diversity` legend moved above the axes in 2 columns, figure height 92 → 100 mm, opaque bbox on the provenance footer; new per-candidate `LAB_OFFSET` in `_pareto_axes` pushing the P1 label leftwards with `zorder=6` and a 10 % x margin; explicit x ticks 2/5/10/20/50/100 s in `fig_efficiency` with minor ticks suppressed via `ax.set_xticks([], minor=True)`; plus a cosmetic `_mnum()` helper bracing the unary minus in `fig_overview`'s mean annotation. `NullLocator` was tried and reverted — it draws a Pyright `unknown import symbol` in this environment, and the plain Axes call has identical effect with no new import | **the script has NOT been re-run** (Bash classifier), so every PNG/PDF under `Graphics/` still shows all four defects; O7 and O1 stay open |
| 2026-08-17 | **Replot–rebuild–manifest cycle (beat 8)** | the three-step cycle left owed by beat 7 is **closed in one pass**, and it supersedes the "NOT RUN" verdicts of the 2026-08-16 PDF-rebuild row and the "script has NOT been re-run" caveat of the row above. (1) `scripts/p4_replot_publication.py` re-run, `exit=0`, all twelve PNG/PDF files of the six data figures rewritten, consistency printout reproducing `tab:sm_benchmark` exactly (Random 0.6724 ± 0.0056 / 50.4 s, MCTS+ScafVAE 0.6649 ± 0.0068 / 92.1 s, GA 0.6453 ± 0.0124 / 2.0 s, Greedy 0.4278 ± 0.0000 / 1.9 s), so the footer-band residual is now on disk (`scaffold_diversity.png` 269940 B, 2716 × 2362 px). (2) `latexmk -pdf -interaction=nonstopmode -halt-on-error` on both documents, both `exit=0`, stderr empty, **0 errors / 0 undefined / 0 overfull / 0 underfull / 0 rerun-requested**; `pdfinfo` gives 14 pp. main and 4 pp. SM. Figure mtimes (20:38:57) precede both PDFs (20:39:15, 20:39:16), so neither PDF predates the figures it embeds. (3) `SUBMISSION_MANIFEST.md` regenerated **as a whole, not patched row by row** — 7 files + 15 graphics re-hashed in one pass, STALE banner replaced by a build-currency note, `p4_hv_vs_ref.png` labelled unused. All layout-only: no plotted value, statistic or caption changed, so every table–figure agreement established on 2026-08-17 still holds | O1 and the O7 figure residual closed; **maker ≠ checker still UNSATISFIED** — the cycle is mechanical (three command exit codes), so it needs no independent checker, but the claim-to-ledger audit it unblocks does |
| 2026-08-17 | **Cycle re-run + figure reproducibility check (beat 8, second pass)** | the same three-step cycle was run again on author instruction at 21:26 UTC. All three commands `exit=0` with empty stderr, the same clean log counts (0 errors / 0 undefined / 0 overfull / 0 underfull / 0 rerun-requested), `pdfinfo` again 14 / 4, and the consistency printout again reproducing `tab:sm_benchmark` exactly. **The re-run doubles as a figure reproducibility check and it passes:** all six data-figure PNGs are byte-identical to the 19:47 pass — same sizes and same SHA-256, `scaffold_diversity.png` again 269940 B at 2716 × 2362 px — so the rasters that reach the page are deterministic given the deposited inputs, and no plotted value, axis range or annotation moved. Everything that did change is an embedded creation timestamp: the six figure `.pdf` sidecars hold their byte sizes exactly (18416, 22013, 25042, 21592, 38165, 16661) but take new hashes, and the two documents shift by a few bytes as the date string is re-encoded (`refined.pdf` 554945 → 554946 B, `SM.pdf` 315239 → 315242 B). `SUBMISSION_MANIFEST.md` was regenerated whole-file in one pass against this build — eight new hashes, two new sizes, header 19:47 → 21:26 UTC, blockquote mtimes updated — and a note records that the 19:47 figures are byte-identical and that the O1 note's sizes are the previous build | manifest current as of the 21:26 build; PDF non-determinism documented, PNG determinism proven; **maker ≠ checker still UNSATISFIED** |
| 2026-08-17 | **Independent claim-to-ledger review — the maker ≠ checker gate (beat 8, third pass)** | run on author instruction, *"launch a read-only agent with fresh context on the claim-to-ledger mapping"*. A separate agent with fresh context and read-only tools produced the findings; this session then re-verified each one from primary source **trying to reject it** (step 5.2). Verdict **"No — qualified-negative"**: the gate ran, it is not satisfied. **3 CRITICAL upheld** — (1) Greedy is scored under a different rule from every method it is compared to (`p4_mcts_benchmark.py:179` returns `oracle(state)` where Random at :147 and GA at :215 return `best_reward`), which is aggravated by `refined.tex:318` stating that very rule and `:282` claiming its correction as contribution (iii); (2) fragment priors are heuristic by their own source comment, described in `refined.tex:313` as ChEMBL27-derived; (3) `p4_benchmark_multiobj.py:27` reads the v11 `benchmark_molecules_opt` while `_v12` also exists. **1 CRITICAL WITHDRAWN** — the alleged activity-panel substitution does not exist: counting both files by command gives 22447 rows / 19321 active in `p5_public_chembl_malaria.csv` (matching `SM.tex:97` and the three scripts that read it) and 19836 / 14721 in `p5_canonical_panel.csv` (matching `refined.tex:288` and `p4_activity_rf_oracle.json`) — two different panels, each cited correctly, so it is re-graded to MEDIUM for the undisclosed 74.2 % class prevalence. That withdrawal is why the count fell from four to three, and it is this record's clearest evidence that a finding is worth only the command that re-derives it. **6 HIGH upheld** — methane-vs-benzene root between the two sbatch configurations, three of five "retained" hyperparameters never screened (the "32 configurations" identifies the screen as `QUICK_GRID`, $2^{5}$ cells, whose level sets contain none of $pw_{\alpha}=0.5$, $pw_{k}=1.0$, $T=0.8$ — each the runner's own default, which is why the marginals are identical at 0.3165), **retained $\nu=0.01$ at `refined.tex:103` against a runner default of 0.05 with nothing on disk stating which value ran — found by neither checker, surfaced while verifying DC4**, Table 4 with no primary artifact, an environment file that does not exist, and an untraced 30-iteration screening budget. **1 checker HIGH REJECTED** (progressive widening "5--20": the alleged manuscript range exists in neither document, and `refined.tex:313` matches `p4_mcts_agent.py:381` exactly) and **1 RE-GRADED HIGH → MEDIUM** (the 2.6× factor traces and its arithmetic checks; the defect is confounding, not provenance). Both rejected items had inaccurate line citations, which is how they were caught — the checker is itself fallible. **The central negative result is untouched by every finding, in either direction.** | `outputs/critical-reviews/review-claim-ledger-20260817.md`; DC1 **run** (119 values: 109 TRACED / 6 MISMATCH / 4 UNTRACED — row inventory **NOT PERSISTED**, regenerable only by re-running DC1, never from memory), DC2 **PASS** (Abstract/Conclusions containment holds, all signs correct), DC3 **PASS** (both hypervolume conventions consistent, non-comparability declared in all three places, no defect above LOW), DC4 **PASS on negative-result integrity** (no softening, no sign or bound error at any of the five signed-effect sites in `refined.tex`; `SM.tex` carries no inferential statistic at all) **/ FAIL on Limitations completeness** (two paragraphs at `:284`--288 cover fragment vocabulary and computational proxies only; six further items are disclosable today); **all four done-criteria closed**; **gate ran, verdict negative — no CRITICAL fix applied, all three are author decisions** |
| 2026-08-19 | **V1–V2 diff audit (beat 12)** | Full three-way diff (`diff -u`) of all three `.tex` files between `Project4_Advanced_Monte_CarloV2607` (V1) and `Project4_Advanced_Monte_CarloV2607_V2` (V2). SHA-256 confirmed all three differ. Direction: **V2 is uniformly ahead of V1 on every hunk.** Every line present in V1 but absent in V2 is superseded content — wrong values (Greedy=0.4278 vs corrected 0.6676; old `tab:front_comp` numbers 13.85/18.99/etc.; WHO figures 247M/619k vs correct 263M/597k), old intro wording ("P2 reference chemotypes"), old abstract without CI/bound/allfrag sentence, bad figure paths (bare `rrs_pns_profile.pdf`, `.png` instead of `.pdf`), old funding statement, old Data Availability, missing HV bound clarification and HV-convention non-comparability paragraph, typos (`l.w SYBA`, `\\num`, `an within-ablation`, `S[table-format=1.3]`), cramped cover-letter formatting (`\small`, 1.7 cm margins, `itemsep=0pt`), old S6 data-availability sentence, `\end{table}Random search` run-together, `group-minimum-digits=4`. **No V1-only content was identified as suitable for porting; no files were modified.** Compile verification immediately after: all three `latexmk` exit 0, 0 errors, 0 undefined refs, 0 overfull boxes, page counts 14 / 4 / 2 — identical to the L4-cleared 2026-08-18 build. | No files changed; compile state preserved |

### From-primary-source recomputation — 2026-08-17 (same party, NOT independent)

Every independent-checker route for the claim-to-ledger audit was mechanically blocked, so the author
authorised a from-primary-source re-derivation instead: recompute the reported numbers directly from the
deposited CSV/JSON with read-only tools, artifact wins on any disagreement. **This is a recomputation,
not an independent review.** It was produced and checked by the same party that made the edits, so it
does **not** satisfy maker ≠ checker — see the closing paragraph.

Reproduced from primary artifacts, no discrepancy:

1. `tab:sm_component_ablation` — all ten marginal level means and all five Δ recomputed to 3 dp from the
   160 `Reward` values in `results/ablation/p4_ablation_config_{0..31}.csv`. The 32-cell × 5-replicate
   balanced design and *n* = 80 per level were confirmed from file contents, not from the caption. Effect
   ordering ScafVAE (0.14769) > Pareto (0.10829) > vocabulary (0.07862) > *c*_PUCT (0.05451) >
   temperature (0.01243) holds.
2. `tab:sm_vocabulary_ablation` — means and sample SDs to 4 dp from the 40 per-seed files: all
   0.62400/0.00562, aromatic-only 0.54971/0.00304, medium 0.62835/0.00484, minimal 0.61827/0.00966.
3. The ANOVA rebuilt from the raw values: grand mean 0.605075, SSB 0.041388, SSW 0.0014186, df 3/36 →
   **F = 350.1**, matching `p4_ablation_anova.csv` (350.099). Tukey medium−minimal *q* = 5.079 →
   *p*_adj ≈ 0.005 against the reported 0.0052; full−medium *q* = 2.17, not significant.
4. Reward weight vectors — v12 five-weight sum = 1.000, full seven-component sum = 1.000.
5. `tab:sm_diversity` cell-for-cell against `results/diversity/p4_diversity_metrics.csv`, and the RF
   activity-oracle panel against `results/pareto/p4_activity_rf_oracle.json` (19836 molecules, 14721
   active, 5-fold CV AUC 0.9479 ± 0.0040). The RF-check panel is distinct from the 22447/19321 ChEMBL
   reward panel and the two were kept separate throughout.
6. `tab:pareto` and `tab:sm_pareto` against `results/pareto/merged_pareto_front.csv`.
7. `tab:front_comp` cell-for-cell against `results/pareto/p4_multiobj_front_summary.csv` — hypervolume
   13.845/16.589/15.488/15.523/18.988, C-metric 0.0588/0.7647/0.0/0.0/0.8235, and the IGD, IGD_loo and
   spread columns all matching at the displayed precision. All five values sit under the cross-method
   bound of 19.45, internally consistent with the $2.1^{4}$ box.

One description defect found and fixed. The hypervolume 1.2366 is computed over **four** active
objectives (MPO, SYBA, RRS, PNS), not three. Three independent locks: `merged_pareto_front_recompute.log`
lists all four in `active_objectives`; `syba` takes four distinct values in the merged front so
`_detect_active_objectives()` (`scripts/p4_mcts_pareto.py:148-200`) retains it and drops only `sa`
(constant 3.0); and a genuine three-objective recompute gives 1.1244, not 1.2366. The value was right,
the count and the bound were not — the front-internal bound is $1.1^{4} = 1.4641$, not $1.1^{3} = 1.331$.
**Third lock re-derived independently 2026-08-18** by `scripts/p4_hv_independent_recheck.py`, which
re-implements the algorithm from the spec and computes HV by exact inclusion--exclusion over the 15
nonempty subsets of the 4 front points, importing nothing from `p4_mcts_pareto`. It passed the required
gate first — four-objective 1.236644 against the published 1.2366, and agreement with `pymoo` to 1e-9 —
then resolved the three-objective figure to its subset: **dropping `syba` gives 1.124376**, the quoted
1.1244 exactly. Caveat the 4-decimal form hid: dropping `pns` instead gives **1.124289**, a different
subset agreeing to 4 decimals and differing at the 5th, so "1.1244" does not identify which objective
was omitted and the figure should be cited at six digits. The lock itself is unaffected — `syba` is
non-constant on this front, so *any* three-objective recompute is the wrong computation.
Fixed in five places: main `.tex` abstract l. 63, `tab:front_comp` caption l. 217 (which also
cross-referenced `sec:oracles` where the convention is defined in `sec:pareto`), Pareto-front-maintenance
paragraph l. 327; SM `.tex` S1 SYBA paragraph ll. 78-85 and S2 hypervolume paragraph ll. 103-112.
**No numeric result changed.** The methods paragraph keeps the honesty framing that SYBA was constant
during the search and re-evaluated only for the displayed front, so the four-dimensional indicator
characterises the reported front and not the information available to the search.

Not a defect, deliberately left alone. The `(1.1+1)^{4} = 19.45` bound of the cross-method convention
looks wrong beside $1.1^{4}$ but is internally consistent: that convention normalises across methods to
$[0,1]$ **first** and negates **after**, giving $[-1,0]$ and a box width of 2.1 per dimension. Both
conventions use the same four objectives; only the negate/normalise order differs. A mechanical 3 → 4
substitution would have broken this.

One provenance gap opened as **O11** and was closed the same day, with an earlier reading of it
withdrawn. The selection-ablation hypervolumes of SM S5 (15.56 scalar-proxy, 15.49 Pareto-restricted) are
recorded in `P4_NOVELTY_EXPERIMENTS.md` §N2 ll. 96-102 as the **merged-deduplicated** front
hypervolumes — 60 unique points for scalar-proxy and 54 for Pareto-restricted, with per-seed front sizes
[30, 31, 66, 19, 39] and [34, 32, 40, 46, 18] — and independently in the long-form DAR at l. 498, already
logged PASS at `outputs/analysis/number-reconciliation-20260815.md:27`. The budget is confirmed twice: in
prose at `P4_NOVELTY_EXPERIMENTS.md:93` and in executable form by `scripts/p4_novelty_n2.sbatch`, a 5-seed
array (`--array=0-4%5`) with `N_ITERATIONS` defaulting to 700 and passed explicitly as 700 in both
documented invocations, medium vocabulary, *c*_PUCT = 5.0, policy temperature 0.8, benzene root, 10 steps —
the same configuration as S1. The implementing script therefore *was* located; the earlier "not located"
statement was wrong.

The "convention-dependent conclusion" reading is **withdrawn**. It compared 15.56/15.49 against the 1.0628
and 0.6380 held in the `hypervolume` column of `n2_proxy_merged.csv` and `n2_pareto_merged.csv` and read
the difference as a +66 %-versus-+0.4 % flip. Those columns are the per-run search-time front-internal
indicator, a different quantity on a different basis — not a second measurement of the cross-method
hypervolume — so the two are not alternative values of the same number and no flip exists. The SM's
"neither rule showed a measurable advantage at the tested budget" is verifiable: the per-seed ΔHV vector in
§N2, [−1.7757, +0.2712, +1.8072, +1.1154, +1.2410], is the same vector frozen into the self-test of
`scripts/p4_n2_power_test.py`, and all five reported statistics reproduce by hand — mean +0.53182, SD
1.40202, paired *t* = 0.848, MDE 1.7566 at *n* = 5 and 0.87830 at *n* = 20, ratio 0.6055 — so the effect
sits below the minimal detectable difference even at the larger sample. The 15.49 shared with GA's front
hypervolume is a rounding coincidence: GA's exact value is 15.488134565469615.

Residual, recorded as a provenance tier rather than a discrepancy: 15.56/15.49 are ledger-recorded rather
than stored in a CSV, one tier weaker than `tab:front_comp`, whose five rows were verified exactly against
`results/pareto/p4_multiobj_front_summary.csv` (HV 13.845/16.589/15.488/15.523/18.988, with C-metric, IGD,
IGD_loo and spread all matching at the displayed precision). Reproducing them requires re-running
`p4_merge_pareto_fronts.py` under the shared normalisation. Closing O11 also closes finding **H2** of
`outputs/analysis/number-reconciliation-20260815.md` ("two hypervolume conventions, one of them
undefined"), whose disposition was "add the second HV convention to Methods + caption" — done in the five
edits above.

`tab:allfrag` was not re-derived — its per-seed files are not in the deposit (disclosed in Data
availability), it is ledger-backed by DAR §1.12, and it is retained as is per author instruction.

Checker currency. `scripts/p4_pareto_provenance_check.py` asserts only on 1.2366 (l. 142) and on `sa`
being inactive (l. 146); `scripts/p4_verify_v11_checks.py` greps both `.tex` as plain text without
asserting on the changed strings. Both were checked **before** the edits were applied; neither breaks.

Harness note, correcting both the 2026-08-16 entry and an earlier note in this subsection. The Bash safety
classifier is **intermittent, not permanently down**: it recovered briefly during this pass, then refused
again with the same message (`claude-opus-5 is temporarily unavailable, so auto mode cannot determine the
safety of Bash right now`). The note written mid-pass claiming it was "back up" is therefore too strong and
is corrected here. `latexmk` was not run. O11 was closed from deposited documentation using read-only tools
rather than from a pymoo recompute, and the power-test statistics were verified by hand with no tool at
all. Two small read-only checks are still outstanding and remain harmless: an exact `wc -l` on
`n2_proxy_merged.csv` and `n2_pareto_merged.csv` to confirm their row counts against the ledger's 60/54,
and the merged-hypervolume recompute as confirmation — no longer a blocker for either.

Maker ≠ checker is **still UNSATISFIED**. A from-primary-source recomputation lowers the chance of an
arithmetic or transcription error, and it did catch a real defect that six prior self-review passes
missed. It is not a substitute for a second party: the same agent chose which artifacts to trust, which
comparisons to make and when to stop. An independent review of the claim-to-ledger mapping has still not
been run.

### L3 + L4 re-run 2026-08-16 (self-verified)

BMAD_Q1 compliance, 7/7 PASS. (1) IC₅₀/EC₅₀ boundary — 3 occurrences (main ll. 288 ×2, 332), all framing the ChEMBL panel as training/reference; l. 288 states explicitly that activity proximity measures similarity to known actives rather than IC₅₀ or EC₅₀. (2) Rule 3 (never convert docking-RRS into MD-RRS) held in its strongest form: l. 332 "no molecular-dynamics resistance quantity enters the present work"; l. 292 "neither would convert a docking-derived signal into a dynamics-derived one". (3) Rule 5 (no claim from an incomplete job) — the `tab:allfrag` per-seed files are absent and this is disclosed twice (ll. 346, 358); the table stays as is per author instruction. (4) P3 complementarity wording at l. 292 matches the "no quantum advantage" restriction. (5) P2 numbers PASS by absence — none are restated. (6) PfClpP gene identifier correct at l. 332. (7) No v11-era CI leak: only the v12 CI appears (ll. 63, 272, 342).

Fixes applied — main `.tex` (8 edits): l. 205 `l.w SYBA` → `low SYBA`; ll. 133, 153, 165 raster `.png` → vector `.pdf`; l. 217 caption dropped a promised plain `IGD` column that does not exist and a stray hyphen in `IGD-${}_{\mathrm{loo}}$`; l. 232 "The IGD columns" → singular, one column exists; l. 254 `tab:allfrag` preamble `lccccc` → `lcccc` (6 columns declared against 5 header and 5 body cells — **no cell value touched**, all 16 numbers intact); l. 352 added the missing `IGD` abbreviation.

Fixes applied — SM `.tex` (5 edits): the four-component objective vector at ll. 61–62 excluded only SA at l. 65, leaving the "three active (non-constant) objectives" at l. 98 unexplained — a bridging clause now ties the constant-SYBA fact already stated in the same section to the exclusion, so the count closes without changing it; l. 100 `$\mathbf{r}=\num{1.1}$` gained the "in each active dimension" qualifier the main text already carries at l. 327; l. 157 raster → vector; l. 231 "an within-ablation" → "a"; l. 235 `S[table-format=1.3]` → `c`, matching every other table in both files (the body already used `\num{}` throughout, so nothing relied on `S` alignment).

Referred to the author, not changed. `Graphics/p4_hv_vs_ref.png` is an orphan — its only reference anywhere is the `SUBMISSION_MANIFEST.md` inventory row; no `\includegraphics` and no generating script mention it. Either drop the row or label it unused when the manifest is regenerated. Separately, `Graphics/rrs_pns_profile.pdf` is included twice — main l. 172 (`fig:rrs_pns`) and SM l. 141 (`fig:sm_rrs_pns`) — with near-identical captions; a JoC editor would likely flag the duplication, but removing a figure is an author scope decision.

Blocked, not asserted. The PDF rebuild, the `pdfinfo` page count (header "main 13 p." against the L4 note's 14), the 0-overfull confirmation and SHA-256 regeneration all require a compile. `latexmk` and the manual `pdflatex` fallback are still refused by the host Bash safety classifier (19 refusals, unchanged this pass — no new attempt was made). Unblock in-session with:

```
! cd manuscript/LaTeX && latexmk -pdf -interaction=nonstopmode -halt-on-error P4_Pareto_MCTS_JoC_SM.tex && latexmk -pdf -interaction=nonstopmode -halt-on-error P4_Pareto_MCTS_JoC_refined.tex
```

Maker ≠ checker is **not** satisfied for this pass either. Every finding above was produced and verified by the same party. An independent review of the claim-to-ledger mapping has still not been run.

Harness note. The `pre:edit-write:gateguard-fact-force` hook scopes its required facts **per target file**: a single facts message covering both `.tex` files opened the gate for the main article and was denied for the SM (`denial #4 this session`). Facts must be restated, naming the specific file, in a message that precedes its first edit.

### Verification scripts — currency check 2026-08-16

Two checker scripts exist in `scripts/`. They are not equivalent and must not be run interchangeably.

| Script | State | Detail |
|---|---|---|
| `p4_pareto_provenance_check.py` | **current** | `MANUSCRIPT_TABLE`, `MANUSCRIPT_HYPERVOLUME = 1.2366` and `seed_to_label = {13: P1, 18: P2, 5: P3, 6: P4}` match main Table 2 and SM `tab:sm_pareto` cell for cell. Its own note (ll. 26–28) requires lockstep updates if the LaTeX tables change; no table changed this session, so nothing is owed. Needs `syba` + `p4_mcts_pareto` on the path to execute. |
| `p4_verify_v11_checks.py` | **stale — do not run** | Asserts v11 values (diversity 0.8023/0.7806/0.0/0.8332; benchmark 0.7335/0.7276/0.7027/0.6147; *t* = −2.41, *p* = 0.026; `wins == 5`; times 82.2/42.4 s) and reads the superseded `results/benchmark_molecules_opt/`, not the canonical `..._v12/`. It fails against the present v12 manuscript by construction. **Author decision needed: retire it or port it to v12.** It was not rewritten here — silently editing a checker so that it passes is exactly the failure mode the gate exists to catch. |

Typography: `IC50`/`EC50` set as `IC\textsubscript{50}`/`EC\textsubscript{50}` in the main Methods (l. 332); the SM already used `IC$_{50}$`.

### Funding statement — corrected 2026-08-16

Author instruction: *"Please, concerning the funding, this research does not receive any funding. Can
you correct the funding statement in the manuscript?"* One edit, main `.tex` l. 370. Two defects were
present and both are closed:

1. **The claim was hedged.** "This research received no specific external funding" is a narrower
   statement than the author's — it concedes non-specific or internal funding by implication, which is
   the standard wording for work that *did* draw on institutional support. Replaced with an absolute
   declaration in BMC/Springer house form: no funding, no grants, no sponsorship, no financial support
   of any kind, from any organisation, for the work reported.
2. **The HPC sentence sat under `Funding`.** "Computational resources were provided by the University
   of Yaoundé I HPC facility" appeared **verbatim** in both Acknowledgements (l. 367) and Funding
   (l. 370). In-kind computational resources declared under a *Funding* heading read to an editor as a
   declared funding source, which contradicts the no-funding declaration in the sentence immediately
   before it. Deleted from Funding only. Acknowledgements l. 367 still carries the identical sentence,
   so no provenance was lost — the facility is still credited, in the section where in-kind support
   belongs.

Scope verified before and after by `grep -rniE "funding|funded|grant|financial support|sponsor" *.tex`
over `manuscript/LaTeX`: exactly two hits, both in the main article (l. 369 heading, l. 370 statement).
The SM and the cover letter contain no funding text, so nothing else is owed an update. Prose-only, no
table cell and no number touched, so `scripts/p4_pareto_provenance_check.py` needs no lockstep change.
The main `.tex` size and SHA-256 have changed again: the funding fix joins calibration row 8 in the set
of source changes the one-pass manifest regeneration (O1) must cover.

### Claim calibration — 2026-08-15, closed 2026-08-16

Author instruction: *"Do what you need to do about abstract, limitations and conclusions."* Eight
edits, each traced to a named artifact. No number was introduced that is not already in the ledger
or stated upstream in the same document.

| # | Location | Defect | Fix and source |
|---|---|---|---|
| 1 | abstract, main l. 63 | means only; no effect size, no interval, no HV convention | added Δ = −0.0075, 95 % CI [−0.0107, −0.0043], *p* = 0.000085, the allfrag Δ = −0.0214, and the HV bound 1.331 (SM S2) |
| 2 | Highlights, main l. 73 | RRS and PNS collapsed into a single resistance claim | split into "resistance-informed chemotype-similarity proxy" and "polypharmacology-informed docking proxy" (SM S1) |
| 3 | Limitations, main l. 288 | internal series label "P4 best-in-seed molecules" | "best-in-seed molecules of the present benchmark" |
| 4 | Limitations, main l. 288 | "Tanimoto to P5 actives" — internal label, panel unnamed | named the reward panel: the 19 321 active entries of the ChEMBL IC₅₀/EC₅₀ set (SM l. 91). The random forest was trained on the separate 19 836-molecule panel, so "the same panel" was false |
| 5 | Conclusions, main l. 344 | "invisible to scalar aggregation" (P3 *is* recovered above w ≈ 0.997); "P2 dominates most of the weight space" (misuses *dominates* — all four front points are non-dominated by construction); "the same activity panel" | argmax wording with 95.6 % / 0.3 %, traced to main l. 193 and `tab:scalar_sweep`; "an overlapping public activity panel" |
| 6 | Conclusions, main l. 346 | "code and released data needed to reproduce the analyses are available" — contradicted l. 358 | narrowed, with an explicit cross-reference to Data availability and `tab:allfrag` |
| 7 | Methods, main l. 332 and SM l. 70 | internal label "P2" for the companion study, colliding with Pareto candidate P2 | named the companion resistance-profiling and network studies instead |
| 8 | Limitations, main l. 288 (applied 2026-08-16) | the random-forest consistency check was called "the oracle" | renamed to "the classifier". `grep -n oracle` over the main `.tex` returns 11 hits; the other 10 all denote the reward/scoring oracle, including `\subsection{Scoring oracles}` (l. 329) and "The activity oracle scores a molecule by…" (l. 332), matching `OracleAggregator` in `AGENTS.md` l. 29. The mislabel also undercut the separation asserted three clauses later ("orthogonal in model class---a random forest on ECFP4 rather than a maximum-Tanimoto rule"). Antecedent verified in situ: "a random forest classifier" sits in the preceding clause of the same sentence. No number changed |

Verification sweep, `grep -nE '\bP[1235]\b'` over both `.tex` files: no internal series label survives.
The eight remaining `P[1-4]` hits (main ll. 185–187, 193, 197, 203, 205, 344) are Pareto-candidate
references and must stay. **maker ≠ checker is not satisfied for this pass**: an independent review of
the claim-to-ledger mapping still has to run before submission.

**Pass closed 2026-08-16.** All three sections are complete in source. Abstract (ll. 59–65) and
Conclusions (ll. 339–346) were re-read against the SM tables and need no further change: every number
in them traces to `tab:sm_benchmark`, `tab:sm_pareto` or the DAR, Greedy correctly carries no $\pm$SD,
and the argmax wording of l. 344 matches `tab:scalar_sweep`. Limitations needed exactly one fix,
row 8. The change is prose-only and touches no table cell, so neither
`scripts/p4_pareto_provenance_check.py` nor the SM is owed a lockstep update.

**The built PDFs are behind the source.** Two prose fixes have been applied to the main `.tex` since
the last build — calibration row 8 (Limitations, l. 288) and the Funding rewrite (l. 370) — but
`latexmk` has been refused 19 times by the host's Bash safety classifier ("claude-opus-5 is
temporarily unavailable… auto mode cannot determine the safety of Bash"). The classifier is **down,
not intermittent** — the
refusal text states that "reading files, searching code, and other read-only operations do not
require the classifier", so a `grep` succeeding between refusals carries no information about whether
a build will pass. Do not read a passing read-only command as a signal to retry the build; wait for
the classifier itself to recover. It is also **command-agnostic**: the manual `pdflatex` fallback in
`AGENTS.md` §5.4 is refused identically, so no choice of command helps. Consequences:
`SUBMISSION_MANIFEST.md` cannot be regenerated (its
four `.tex`/`.pdf` SHA-256 rows are stale, and hashing now would record superseded PDFs with
cryptographic precision), so O1 and the **STALE** marker in the file map both stay open because both
are still true. The manifest now carries an in-file STALE banner and its provenance notes record the
calibration pass, so the file cannot be mistaken for a packaging list. Retry the build before any
submission packaging.

> **Superseded 2026-08-17 19:47.** Kept as dated history, not as current state. The Bash classifier
> recovered, `latexmk` ran clean on both documents, and the replot–rebuild–manifest cycle was completed
> in one pass, so the two claims above are now false: `SUBMISSION_MANIFEST.md` has been regenerated
> from the working tree, and the STALE banner and the file-map STALE marker are both gone. See O1.

### L4 re-run — 2026-08-15, after fixes

- **Table 4 provenance — reclassified PASS.** DAR long-form §1.12 (job 15133) confirms all 16 cells
  of `tab:allfrag` exactly. The earlier FAIL conflated *ledger-backed* with *raw-artifact-deposited*;
  only the second is missing. Table retained as is, per author instruction.
- **Data availability — PASS.** The statement now discloses that the full-vocabulary run's per-seed
  outputs are not in the deposit, so the "all data available" claim is no longer overstated.
- **Mathematical notation — PASS.** PUCT equation rewritten with $Q(s,a)=W(s,a)/N(s,a)$ defined and
  the virtual-loss term $-\nu N(s,a)/\max_b N(s,b)$ included; matches `p4_mcts_agent.py:329,341-342`.
- **Manifest integrity — PASS.** `SUBMISSION_MANIFEST.md` regenerated: 7 files + 11 graphics hashed,
  page counts corrected to 14 / 4 / 2.

**Last FAIL — closed 2026-08-15.** The fragment-vocabulary contradiction (Limitations said ~108
fragments, while the ablation and Table 4 said full = 80 / medium = 37) was an author decision, and
the author ruled: **the v12 set, full = 80, medium = 37**. Applied in the main article and in the SM,
whose vocabulary-ablation caption (`tab:sm_vocabulary_ablation`) now states that its *all* condition is
the earlier development vocabulary and not the 80-fragment v12 full set. L4 stands at **18 PASS / 0 FAIL**
on the automated rows.

**What the L4 all-pass does not cover.** Three items remain, none of them automatable:

1. **maker ≠ checker.** L1, L4 and the claim-calibration pass were all run by the same agent that made
   the edits. An independent review of the claim-to-ledger mapping has not been run.
2. **Visual inspection at printed size.** The six regenerated figures were verified numerically against
   their source CSVs but not inspected as printed output; the three-panel overview is the likeliest place
   for label collisions.
3. **Missing raw artifact (C1).** `results/benchmark_v12_allfrag/` is still absent. Table 4 is
   ledger-backed by DAR §1.12 and retained as is per author instruction; the Data availability section
   discloses the gap.

### L4 result — 2026-08-15

FAIL rows (gate does not pass until all four clear):

1. **Data availability** — `results/benchmark_v12_allfrag/` absent; never committed on any branch
   (`git rev-list --all --objects | grep allfrag` → empty). Backs Table 4. Owner: author (recover
   from cluster job 15133 or withdraw table).
2. **Analysis provenance** — same artifact; Table 4's four rows are the only orphan numbers left.
   Every other number traces to a named artifact.
3. **Manifest integrity** — all four SHA-256 in `SUBMISSION_MANIFEST.md` stale against the current
   files; page counts also wrong (claims cover 1 p., actual 2 p.). Owner: regenerate last.
4. **Mathematical notation** — the displayed PUCT equation writes $Q(s,a)/N(s,a)$ without defining
   $Q$; the code computes `q = child.value / max(child.visits,1)`, i.e. accumulated value over
   visits (`p4_mcts_agent.py:329`). Under the conventional reading of $Q$ as the mean action value
   the equation double-normalises. The equation also omits the virtual-loss term the code
   subtracts, `vl = ν · N_child / N_max` (`p4_mcts_agent.py:341-342`), whose form is never given.

PASS rows: journal fit · title/abstract · novelty statement · literature positioning · method
completeness · result-claim consistency (except Table 4) · figure/table quality (7/7 graphics
present) · reference quality (20 refs, 16 DOIs, 0 placeholders) · code availability · supplementary
(S1-S6) · ethical declarations (9/9 incl. AI-use) · language quality (0 anti-AI, 0 US spellings) ·
ledger currency (DAR 12-13 Aug newer than newest result 11 Aug).
