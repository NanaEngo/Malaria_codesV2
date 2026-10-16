# PhD Thesis Progress Map
**Title:** Quantum Machine Learning Approach for Malaria Drug Discovery  
**Author:** Vital SAO TEMGOUA  
**Target:** 150 pages  
**Current:** 141 pages ← **Updated after the 14 Oct 2026 P7-refinement + chapter-rebalance pass**

> **P7 refinement, mini-TOC repair and chapter rebalance checkpoint (14 Oct 2026):** Four work items in one pass. (1) **Per-chapter TOC boxes repaired for Chapters 2 and 3** — the boxes at the opening of Ch2/Ch3 were rendering empty because `\adjustmtc[3]` was applied a second time on top of the offset Chapter 1 already carries; the reader counter is cumulative, so Ch1 needs `+3` (frontmatter TOC/LOF/LOT consume writer slots 0–2 while the reader counter starts at 0) and Ch2/Ch3 need `+0`. Diagnosed from the `.log` (`minitoc I0006`: Ch2 read the empty slot `mtc8`, Ch3 the empty slot `mtc9`, against the real files `mtc5`/`mtc6`) and confirmed by `\typeout` probes of `\arabic{mtc}` at each box (4 / 8 / 9). Verified: all three chapter openings now carry a "Contents" box with their own sections+subsections (physical pp. 17, 51, 85). (2) **P7 adjustments integrated** (commits `21a3efd17`, `eaa1acf06`, `3f12a53de` + `P7_WORKFLOW_STATUS_20261014.md`, `manuscript/outputs/critical-reviews/calculation-review-20261014.md`, `docs/QMSE_VERIFICATION_REPORT.md`): Ch2 §2.7.4 gained the **QMSE stereochemistry verification** (R/S enantiomers → diagonal sign flip +108/−108 = 0.5·6³; Z/E butene → off-diagonal +18/−18; ECFP4 control Tanimoto = 1.0) and a new **phase-status table** (`tab:met_qmse_phases`) recording Phases A **and B** as *declared/recorded complete in the DAR but with no artifacts locatable at the 14 Oct audit → pending re-verification* (NPZ missing, `results/phase_b_smoke/` absent), Phase C *launched with no result files, log or running process*, Phase D pending → status remains `\textsc{not computed}`; Ch3 §3.6, the Ch3 synthesis, Gen_intro and Gen_con were harmonised ("recorded as frozen/confirmed", artifact verification open) so no passage asserts an unverified artifact as fact; the Coulomb-diagonal description was corrected to the frozen implementation (declared exponent e = 3, not 2.4). Ch3 §3.6 gained the completed **exploratory (ECFP4-VQC) execution record** — PoC 0.933 vs 0.833 with p = 0.250 failure-to-detect, width ablation 4q 0.8474 > 8q 0.8316 > 6q 0.8230 all above the 0.758 gate, HPO best 0.8468 (Δ = −0.0006), scaffold 0.7831 vs 0.8413, gradient diagnostics none at n=800 / 8.24% at n=8000 — plus **three harvested P7 figures** (`fig:res_p7_auc`, `fig:res_p7_ablation`, `fig:res_p7_scaffold`); Gen_intro/Gen_con/synthesis wording harmonised ("declared frozen", artifact verification open). (3) **Tables/figures gathered from the drafts** into `Graphics/`: `p7_qfe_workflow`, `p7_qfe_circuit`, `p7_exploratory_auc_folds`, `p7_exploratory_ablation`, `p7_exploratory_scaffold_gradient` (P7 manuscript), `p2_p2rank_pockets` (P2 V2609C SM → new Ch2 fig `fig:met_p2rank`), `p5_mol_rescue_top4`, `p5_learning_curves` (P5 V2609, held in reserve — not yet cited). New native tables: `tab:met_qmse_phases`, `tab:met_sensitivity`, `tab:met_benchmark_design` (Ch2), `tab:ch1_representation_map` (Ch1). (4) **Chapter rebalance toward parity with total ≤150**: Ch1 gained a targets subsection (DHFR/CRT/ATP4/ClpP + resistance genetics), a NISQ/noise subsection (Preskill2018), a trainability/expressibility subsection (Havlicek2019, Sim2019, McClean2018, Cerezo2023), a 3D/stereochemistry-aware representation subsection (new bib: Axen2017, Schreyer2012), a natural-product chemical-space subsection, a filled *empty* §1.4 "Limitations in handling high-dimensional data" subsection, a reporting-standards subsection, a docking-validation subsection and the representation-map table; Ch2 gained the 3D-comparator subsection, the combination/ablation design subsection, the pipeline-null and reference controls subsection, the Vina scoring-function description (Trott2009), the sensitivity-audit and benchmark-design subsections and the claim-ledger subsection. Also fixed **four previously uncited floats** (`fig:antimalaria_resistant`, `fig:res_targetwise`, `fig:res_persistence`, `fig:res_tne_reg`) and a cited-after-float case (`fig:dd_process`). Spans now **Ch1 pp. 1–34, Ch2 pp. 35–68, Ch3 pp. 69–111**, Gen Con 112–114, Bib 115–**141** (target 150; 9 pages of margin reserved for a future P7 Phase D section). Build: **141 pages, 0 errors, 0 undefined references/citations, 0 multiply-defined labels, all 3 minitoc boxes non-empty, every float cited, `git diff --check` clean.** Nothing committed or pushed.
>

> **Chapter 3 discussion-expansion checkpoint (14 Oct 2026):** Chapter 3 expanded from 32 to ~40 pages (document 111 → **119 pages**, target 150) with **nine new discussion subsections and two consolidation tables**, all built strictly from canonical values already in the thesis (no new numbers, no P7 comparative claims). (1) `sec:res_chemspace_discussion` — reads the scaffold paradox as a prediction for downstream models, states the two boundaries of centroid sampling (no property-space stratification; compute- not performance-statement), and presents a new **shortlist table** (`tab:res_shortlist`: PP-15/PP-01/PP-06/PP-13/PP-11/PP-05 with evidence bases). (2) `sec:res_validation_discussion` — why redocking/MMV/DEKOIS are complementary rather than contradictory (score-stratified MMV labels = retrodictive consistency; DEKOIS = external discrimination), plus a new **per-target campaign summary table** (`tab:res_target_summary`: receptor, site status, grid, score range, validation evidence per target). (3) `sec:res_dynamics_discussion` — static penalty as conservative bound; dynamics as specificity filter not second scorer; endpoint conditions (2/4 bound, K76A 7.75 kcal/mol spread vs 2.01 noise floor). (4) `sec:res_ceiling_discussion` — the three mechanisms locating the ceiling in input information (what encodings discard; panel geometry 632 scaffolds/19,836 + 74.2% prevalence; expressivity ≠ information, alignment 0.622 vs ΔAUC −0.006). (5) `sec:res_model_choice` — practical model-selection guidance: interpolation regime (0.001–0.007 AUC spread) → ECFP4–RF default; extrapolation tail (up to 0.053 deficit, capacity-sweep-bounded) → no architecture reliable; distance-aware triage as declared hypothesis. (6) `sec:res_qmse_status_discussion` — what the programme establishes (frozen 19,849 substrate; 17/17-fold end-to-end training) vs what it does not (0.733 smoke test ≠ benchmark; RQ5 remains *open* in claim-ledger sense). (7) `sec:res_representations_value` — the quantum-inspired descriptors' surviving contributions despite the null (diagnostic decomposition of the scaffold paradox; competence-without-predictive-gain; label-source-shift fragility as its own measurable property). (8) `sec:res_estimand_register` — new **estimand-register table** (`tab:res_estimand_register`: nine principal quantities × what each estimates × what it cannot support). (9) `sec:res_falsification` — explicit falsification conditions for the chapter's four central claims, including the predeclared scenario that would require revising the four-facet framing itself. Ch3 roadmap paragraph updated to name all nine. Build: **119 pages, 0 errors, 0 undefined references/citations, 0 multiply-defined labels**; all nine subsections verified present in rendered PDF and TOC; `git diff --check` clean. Nothing committed or pushed.
>
> **Unified-narrative refinement checkpoint (13 Oct 2026):** Thesis refined per `THESIS_REFINEMENT_PROMPT_20261012.md`. (1) **Gen_intro** — Statement of the problem rewritten from four independent problems into a single representational crisis with four interdependent facets (scaffold paradox / estimand divergence / quantum-inspired null result / learned-representation collapse) closed by a common-root-cause paragraph and the frozen-protocol consequence; Research questions restructured as one central question followed by the four-stage arc (Stage I–IV labels), with the six RQs preserved in order so RQ5 remains the fifth; objectives stage-aligned and split to seven (new: docking-validation objective with redocking/DEKOIS estimand boundaries); background QML passages de-hedged per the prompt's pattern ("holds the potential" → explicit hypothesis under test; platform "could result in" → "has been proposed for"; advantage claims → hypotheses under test). (2) **Ch3** — introduction rewritten as a single investigative arc with P7 as the in-progress culmination; new `\section{Structure-direct quantum molecular encoding}` (`sec:res_qmse`, §3.6, four subsections: archived exploratory ECFP4-VQC phase with AUC 0.8474 ± 0.0129, −2.5% vs matched ECFP4-RBF 0.8693 ± 0.0265, scaffold 0.7831, archived 06 Oct as EXPLORATORY/garbage-in-garbage-out; pipeline status Phase A frozen 19,849/19,849, Phase B smoke test AUC 0.733 = pipeline confirmation not benchmark, Phase C in progress, Phase D pending → NOT_COMPUTED; reformulated benchmark question vs classical 3D descriptors E3FP/USRCAT/Autocorr3D on high-ACSI quartiles under scaffold split with Cohen's-d decision machinery and three predeclared scenarios; six-part comparison standard for hardware-based claims); Synthesis renumbered §3.7 with cref to `sec:res_qmse`; bridge paragraph at end of §3.5. (3) **Ch2** — QMSE methods extended: declared classical 3D comparators + Cohen's d / ACSI-stratification decision rule for the pending benchmark. (4) **Gen_con** — closing paragraph rewritten into three principal contributions (frozen benchmark; resistance-aware workflow; representational-ceiling diagnosis with QMSE as testable hypothesis) plus three requirements for the QML programme (classical 3D baselines first; scaffold-separated evaluation; theoretical formalization before hardware claims). All numbers traced to P7 DAR / existing thesis canonical values; no P7 comparative claim added (status remains \textsc{not computed}). Build: 111 pages (target 150), 0 errors, 0 undefined references/citations, 0 multiply-defined labels; `git diff --check` clean. Nothing committed or pushed.

> **Chapter contents boxes checkpoint (08 Oct 2026):** Per-chapter table of contents reimplemented **exactly as `ThèseMbokop_V260112/Mbokop_ThesisV2509.tex` does it**, replacing the earlier custom-styled "In this chapter" mini-TOC (rejected): system package `minitoc` (no files copied) with defaults — default title "Contents", default depth (sections + subsections), no font/color customization — rendered as `\begin{tcolorbox}[beamer] \minitoc \end{tcolorbox}` followed by `\newpage`, placed only in the numbered chapters (1–3), matching their source exactly (their Introduction and Conclusion have no box, nor do ours); `\dominitoc` retained before `\tableofcontents`. **One necessary deviation:** Chapter 1 uses `\adjustmtc[3]` instead of the bare `\adjustmtc` — our frontmatter (TOC/LOF/LOT) consumes write-slots 0–2 while the mtc counter nets to 0, so a literal bare `\adjustmtc` misroutes every box by one slot (verified: Ch1 box empty, Ch2 box showed the General Introduction's entries, Ch3 box showed Ch1's); Mbokop's own frontmatter nets differently, where the bare command works. Verified on final PDF: 3 boxes titled "Contents" with each chapter's own sections+subsections, page numbers agreeing with the main TOC (1.1→p3, 2.1→p29, 3.1→p56); build 111 pp, 0 errors, 0 undefined references; `git diff --check` clean.
>
> **(Superseded) chapter mini-TOC checkpoint (08 Oct 2026):** Per-chapter mini tables of contents added, following the technique observed in `ThèseMbokop_V260112/Mbokop_ThesisV2509.tex` (minitoc in a tcolorbox after `\chapter`) but styled to the thesis design: system package `minitoc` loaded in the preamble (no files copied — it ships with TeX Live), `minitocdepth=1` (sections only, so each overview fits one screen), title "In this chapter" in blue sffamily, entries dotted with page numbers, rendered in a sharp-cornered `tcolorbox` (`arc=0mm`, `colback=blue!5!white`, `colframe=blue!75!black`) echoing the framed chapter titles. `\dominitoc` added before `\tableofcontents`; `\chaptertoc[<adjust>]` macro placed in General Introduction (`[3]` — the starred chapter needs +3 because the frontmatter TOC/LOF/LOT consume counter slots 0–2) and in Chapters 1–3 (no adjust; numbered `\chapter` steps the counter). General Conclusion excluded (no sections to list). The mtc routing was diagnosed empirically (counter at box time was 0/2/4/6 vs files 3/4/5/6 — an earlier Mbokop-style plain `\adjustmtc` in every box produced shifted/empty mini-TOCs). Verified: 4 boxes, each listing its own chapter's sections with page numbers matching the main TOC (e.g. 2.2 → p. 27 in both); build 106 pp, 0 errors, 0 undefined references; `git diff --check` clean.
>
> **Central-question refinement checkpoint (08 Oct 2026):** Thesis umbrella question harmonised across `Gen_intro.tex`, `Gen_con.tex` and `CENTRAL_QUESTIONS_PROJECTS.md` (hybrid framing: evaluation-standard umbrella + blind-spot sub-question; canonical wording in Gen_intro Research questions). Changes: statement of the problem extended to four problems (new encoding-level problem: no examined representation encodes stereochemistry/bond polarity/bond topology directly); research questions extended five → six (new RQ5: do stereochemical blind spots and scaffold-extrapolation failures persist under structure-direct quantum encoding; evaluation standard renumbered to RQ6); aim and objective list updated ("learned" representations added; new QMSE-overcoming-blind-spots objective); background time/cost claim demoted to attributed motivation with explicit no-claim coda ("no time-or-cost reduction is claimed by this work"); overview restatement aligned with umbrella wording; `CENTRAL_QUESTIONS_PROJECTS.md` gained a thesis-umbrella section, a P7 section (06 Oct QMSE question, Phases A–B computed / C–D pending) and P1–P7 synthesis; Gen_con records RQ5 as *open* under the claim ledger pending P7 Phase D. Build: 104 pages, 0 errors, 0 undefined references; `git diff --check` clean.
>
> **Early-P1 asset integration checkpoint (07 Oct 2026):** Figures, tables and measured values from the early chemical-space work (`Papers_P1_previously/`) integrated into Chapters 2–3 after provenance screening against P1 V8 canonical values. (1) **Ch2 §2.1:** VAE methods paragraph added (three-conv-layer SMILES-VAE architecture, Adam lr 0.001 / batch 128 / KL weight 0.5, 100 epochs, 150-trial Optuna search per latent dimensionality; the 32D-vs-64D choice framed as a measured trade-off, not a dominance claim) plus citations added in-text: `lzicar_cheese_2024` and `Nigam2021` on the expansion routes, `gomez2018automatic` on the VAE, `Akiba2019` on Optuna (whose bib entry's `&amp;` was repaired to `\&`, previously uncited and untriggered). (2) **Ch3 new prioritisation-diagnostics subsection** (label `sec:res_prioritisation`, placed after the scaffold-expansion results): expansion-route composition from the measured `r6_expansion_analysis` data (CHEESE 29,805 molecules / 394 scaffolds / diversity 0.013 / QED 0.697; STONED 35,198 / 13,378 / 0.380 / 0.497; seed sets 396/245/0.619/0.486 and 454/331/0.729/0.600; valid-structure fractions 0.992/1.000/0.985/0.915), with a **new figure** `p1_expansion_route_composition.pdf` generated by `My_PhD_Thesis/create_expansion_route_figure.py`; VAE validation (convergence std 0.022/0.036; 64D loss 50.62, reconstruction 93.23%; 32D 47.85, 94.18%) with the new 32D-vs-64D table (`tab:res_vae_comparison`) and figures `p1_vae_training_curves.pdf` + `p1_clustering_quality_comparison.pdf`; cluster structure (intra-cluster mean similarity 0.227 vs inter-cluster 0.101, ≈2.2×, cross-linked to the centroid pairwise 0.32 of the synthesis section) with `p1_intra_inter_similarity.pdf` + `p1_physchem_by_cluster.pdf`; predicted ADMET profiles by compound source (ADMET-AI, `Swanson2024` already in the bib) with `p1_admet_profiles.pdf`. **Provenance screening (superseded early values excluded):** early-draft 469 centroids → canonical 484 retained; early 65,853 route-count total not used (canonical 65,856 post-dedup total kept, route counts presented as pre-validation outputs); early redocking (10/10) and DUD-E-era enrichment figures NOT imported — the canonical honest validation record (4/5 poses + MTX failure, DEKOIS 0.450, two-arm control) stands; UMAP latent-space figure excluded because its compound-source labels were assigned by dataset row order (documented approximation, fails the thesis provenance standard); the R6 "alternative parameter" table rows are literature estimates and were not used. Build: 104 pages, 0 errors, 0 undefined references/citations; `git diff --check` clean.
>
> **Cross-project refinement checkpoint (06 Oct 2026):** Thesis realigned to the latest canonical states of all in-scope projects. (1) **P7 QMSE refocus integrated** (P7 DAR §2, 06 Oct): Gen_intro overview now names QMSE and its motivation (stereochemical collapse + scaffold extrapolation); Ch1 §5.1 gained a structure-direct-encoding paragraph (Boy et al. 2025, MLST 6, 045076) and the conclusion section extends the kernel discussion to QMSE; Ch2 gained a full QMSE methods subsection (`\subsection{Quantum molecular structure encoding...}`, label `sec:qmse_methods`) with BondOrderMatrix/CoulombMatrix definitions, the RX/RY/RZ + RXX/RYY/RZZ angle mapping, qml.qnn.KerasLayer + TF dense head, Phase A frozen encoding (19,849/19,849, 0 failures), Phase B pipeline-confirmation smoke test (17/17 folds, AUC 0.733 untuned, explicitly labelled a pipeline confirmation, not a benchmark), phases C/D declared pending with status NOT_COMPUTED, three predeclared scenarios, and the ECFP4-VQC exploratory archive (different estimand, no thesis claims); Ch3 synthesis rewritten around the refocus rationale. (2) **P2 V2609C ports**: WHO 2025/2026 regional resistance-isolate contextualization added to Gen_intro background and Ch1 emerging-resistance section (Pfkelch13 confirmed/suspected in ≥8 African countries; expanding pfk13 footprint; Pfcrt/Pfdhfr variant co-occurrence; 8 bib entries added incl. `who_malaria_2025`, `young2026artemisinin`, `Boy2025QMSE`); Gen_intro global figures updated to WMR 2025 (282M cases / 610k deaths, 2024); plant-species attribution (*Cryptolepis sanguinolenta*, *Enantia chlorantha*, *Artemisia* spp.) added to Ch3 §3.2.1; ACSI cohort distribution (mean 0.543, 2/17 above 0.70) added to Ch3 §3.2.5. (3) **P1 V8 port**: retrospective approved-drug control (R1.2: pyrimethamine ≈100% RRS on all four PfDHFR mutants, chloroquine ≈99% on K76T/K76A within the 99.4–100.5% null spread, artemisinin/cipargamin ≈113–118%, chloroquine/lumefantrine PfDHFR non-binders) added to Ch3 §3.2.6 as a second retrospective bound on the static estimand. (4) **General Conclusion written** (Gen_con.tex was an empty stub): five-paragraph synthesis of all studies with canonical values, limitations, claim-ledger framing, and the QMSE programme as forward direction. P3 V2609 and P5 V2609 values verified already aligned (no changes needed). Build: 99 pages, 0 errors, 0 undefined references/citations; `git diff --check` clean.
>
> **Chapter rebalance checkpoint (29 Sept 2026):** Chapters equalized at 24 pp each after the introduction restructure (Ch1: 1–24, Ch2: 25–48, Ch3: 49–72; document 96 pp). Additions were genuine content, not padding: Ch2 gained external-data versioning, the Wilson-interval rationale, the PNS formal definition (Eq. 2.x), and a Conclusion section (§2.9) on the Mbokop closing pattern; Ch3 gained the V2609C operational-guidance rules for resistance-aware triage (placed under §3.3 Resistance-aware scoring, where they belong) and a numbered Conclusion (§3.7). One residual "four projects" phrase fixed. Build: 96 pages, 0 errors, 0 undefined references.

> **Introduction structure checkpoint (29 Sept 2026):** Manuscript restructured on the Mbokop thesis model (`ThèseMbokop_V260112/Mbokop_ThesisV2509.tex`). General Introduction now follows the six-section pattern (Background of the study / Statement of the problem / Research questions / Aim and objectives / Significance / Organization of the thesis + Overview of the thesis argument), all in TOC. The previous narrative became the Background section; three new problem statements (representational, evaluative, resistance-aware) and five research questions were authored. Every chapter now opens with a numbered Introduction section with an explicit `\Cref`-based roadmap (1.1, 2.1, 3.1); the previously empty Chapter 1 introduction was written. Five hardcoded "Section X.Y.Z" references replaced with labelled `\Cref` cross-references; seven section labels added to Ch2, five to Ch3. cleveref chapter/section names configured in the preamble. Build: 94 pages, 0 errors, 0 undefined references.

> **Terminology + equalization checkpoint (29 Sept 2026):** (1) All "Project N" / standalone "PN" references removed from the manuscript body (Gen_intro, chap_lit_rev, chap_to_met, chap_res_dis); studies are now referred to descriptively (chemical-space study, resistance-scoring study, representation study, learned-representation study, quantum machine learning programme). (2) Three companion-study ChemRxiv DOIs added to `Bib_thesis_SAO.bib` and cited in Chapter 1: `Temgoua2026Grids` (10.26434/chemrxiv.15006437/v2), `Temgoua2026Topological` (10.26434/chemrxiv.15007167/v1), `Temgoua2026Pareto` (10.26434/chemrxiv.15007306/v1); 12 methodology references also added (Bickerton QED, SYBA, Ertl NPL, DiffDock, SWISS-MODEL, ProLIF, STRING, GROMACS, CHARMM36m, gmx_MMPBSA, MDAnalysis, ETKDG/RDKit). (3) Chapter 2 expanded 13→22 pages with genuinely missing methods content (prioritisation-term declarations, DiffDock consensus estimator, multi-seed + perturbation audits, PfCRT K76 restoration rationale, candidate selection cascade, estimand architecture + reference controls, eligibility-rule rationale, PNS robustness checks, conformer governance, kernel diagnostic hierarchy, MD cohort table, MM-GBSA decomposition + noise floor, ProLIF contact-level complement, label provenance, cohort chemical-space characterisation, compute environment + software table, enrichment-ceiling mechanics, conformal calibration + distance-aware triage rule, power analysis, hyperparameter governance, uncertainty taxonomy + formal test mechanics, claim-ledger convention, docking/MD/RRS-class summary tables). Chapter spans now equalized: Ch1 22 pp (1–22), Ch2 22 pp (24–45), Ch3 23 pp (46–68); total document 90 pp. Build: 0 errors, 0 undefined references, `git diff --check` clean.

> **V2609C figure refresh (29 Sept 2026):** Three P2 thesis figures were stale pre-V2609C versions and have been replaced with the canonical V2609C assets (checksums verified): `p2_rmsd_stability.pdf` ← `Figure3_RMSD_Stability.pdf` (nm axes, canonical R1 labels), `p2_prolif_heatmaps.pdf` ← `Figure4_ProLIF_Heatmaps.pdf` (canonical hotspot panels), `p2_cross_metric_correlation.pdf` ← `cross_metric_correlation.pdf` (declared 4-pair chart, replaces old 8×8 heatmap). RMSD and cross-metric captions rewritten to match; ProLIF caption already canonical.

> **V2609C integration checkpoint (29 Sept 2026):** Chapter 3 P2 section realigned to the canonical P2 manuscript `Project2_.../manuscript/V2609C/`: corrected PP-01 RMSD figure-caption values (backbone/ligand in Å from canonical R1), corrected ProLIF caption (Tyr16 100% occupancy in 5/6 PfCRT systems; Asp54/Leu46/Met55/Ile14 hotspots), added the 16-system Set-C MM-GBSA endpoint table (SD_prop convention) + PP-01 biophysical audit paragraph, added the retrospective ChEMBL genotype–phenotype fold-shift confrontation (28 compounds, ρ −0.13..0.19, direction agreement 28.6–41.7%), added the GNINA near-degenerate-agreement caveat, and added STRING-threshold (400/700/900) and ACSI ±20% weight sensitivity. Chapter 2 methods gained: GNINA/QuickVina cross-scoring subsection, retrospective ChEMBL confrontation protocol, and the MD-RRS_d distance-ratio definition. Chapter 1 lit review updated with estimand-divergence framing. P5 sections verified already claim-calibrated (commit 46926a4bd).

> **Scope note (28 Sept 2026):** The thesis now covers **five projects: P1, P2, P3, P5, P7**.
> P4 (MCTS/Pareto multi-objective optimization) and P6 (LISH-MoA phenotype baseline) have been
> removed from the manuscript — their results already belong to companion publications and must not
> be re-used here. P7 (true QML via QMSE) is in scope with framing only; its methods and results
> sections are yet to be written and its status remains NOT_COMPUTED until canonical runs exist.

## Thesis Structure

```
PhD_SAO_V250404.tex (Main File)
│
├── Front Matter (~5 pages)
│   ├── Cover Page ✅
│   ├── Table of Contents ✅
│   ├── List of Figures ✅
│   └── List of Tables ✅
│
├── General Introduction (~3 pages)
│   └── Gen_intro.tex ⏳ To review
│
├── Chapter 1: Literature Review (~30-35 pages) ✅ ENHANCED
│   ├── chap_lit_rev.tex (320 lines, up from 193)
│   │
│   ├── 1. Malaria Drug Discovery Background ✅
│   │   ├── 1.1 Overview of malaria biology
│   │   ├── 1.2 Pharmaceutical drug discovery process
│   │   ├── 1.3 Current treatments
│   │   └── 1.4 Emerging resistance issues
│   │
│   ├── 2. Natural Products in Drug Discovery ✅
│   │   ├── 2.1 Natural products as drugs
│   │   ├── 2.2 Successes of natural products
│   │   └── 2.3 Computational methods for NP analysis
│   │
│   ├── 3. Machine Learning in Drug Discovery ✅
│   │   ├── 3.1 Types of ML techniques
│   │   └── 3.2 Limitations in high-dimensional data
│   │
│   ├── 4. Quantum Computing Fundamentals ✅
│   │   └── 4.1 Quantum computing concepts
│   │
│   ├── 5. Quantum Machine Learning ✅ NEW ENHANCED
│   │   ├── 5.1 Recent QML algorithms
│   │   └── 5.2 Quantum applications for malaria
│   │
│   ├── 6. Computational Drug Discovery Methods ✅ NEW SECTION
│   │   ├── 6.1 Molecular docking (P1/P2 integrated)
│   │   ├── 6.2 Molecular dynamics (P2 integrated)
│   │   ├── 6.3 Chemical space exploration (P1 integrated)
│   │   └── 6.4 Resistance-resilient scoring (P2 integrated)
│   │
│   ├── 7. Molecular Representations for ML ✅ NEW SECTION
│   │   ├── 7.1 Classical fingerprints (P3/P5 baseline)
│   │   ├── 7.2 Graph neural networks (P5 honest-negative)
│   │   └── 7.3 Topological/quantum descriptors (P3 integrated)
│   │
│   ├── 8. Generative Models ✅ NEW SECTION
│   │   ├── 8.1 VAEs and GANs
│   │   └── 8.2 RL and multi-objective optimization
│   │
│   ├── 9. Integration of Workflows ✅ NEW SECTION
│   │   ├── 9.1 Validation cascades
│   │   └── 9.2 Prospective vs retrospective validation
│   │
│   └── 10. Conclusions and Future Perspectives ✅ NEW SECTION
│       └── Comprehensive synthesis of P1–P3, P5, and P7 findings
│
├── Chapter 2: Tools and Methods (~40 pages) ✅ **ENHANCED**
│   ├── chap_to_met.tex (850 lines, comprehensive)
│   │
│   ├── Implemented Sections ✅:
│   │   ├── 2.1 Chemical Space Construction (P1)
│   │   │   ├── Hybrid library construction (JT-VAE)
│   │   │   ├── Target selection (PfDHFR, PfCRT, PfATP4, PfClpP)
│   │   │   └── Physicochemical filtering
│   │   │
│   │   ├── 2.2 Molecular Docking Protocols (P1)
│   │   │   ├── AutoDock Vina methodology
│   │   │   ├── Docking validation (V7)
│   │   │   └── DEKOIS 2.0 benchmark
│   │   │
│   │   ├── 2.3 RRS and Polypharmacology (P2)
│   │   │   ├── Resistance-resilient score computation
│   │   │   ├── Polypharmacology network scoring
│   │   │   └── ACSI chemical space positioning
│   │   │
│   │   ├── 2.4 Molecular Dynamics Methods (P2)
│   │   │   ├── System preparation (OpenFF 2.2.0)
│   │   │   ├── Equilibration protocols (3-stage NPT)
│   │   │   └── MM-GBSA binding free energy
│   │   │
│   │   ├── 2.5 Molecular Descriptors (P3)
│   │   │   ├── ECFP4 baseline
│   │   │   ├── Topological fingerprints (GUDHI)
│   │   │   └── Quantum kernel similarity (Qiskit)
│   │   │
│   │   ├── 2.6 ML/DL Architectures (P3, P5)
│   │   │   ├── Random forest baseline (scikit-learn)
│   │   │   ├── Graph Isomorphism Networks (GIN)
│   │   │   └── Transformer architectures
│   │   │
│   │   └── 2.7 Statistical Validation (All projects)
│   │       ├── Cross-validation protocols
│   │       ├── Performance metrics (ROC-AUC, EF1%)
│   │       └── Multiple hypothesis testing
│   │
│   └── Delivered: 11 pages (comprehensive 8-section methodology)
│
├── Chapter 3: Results and Discussion (~21 pages so far) ✅ **CANONICAL RESULTS INTEGRATED**
│   ├── chap_res_dis.tex
│   │
│   ├── Implemented Sections ✅:
│   │   ├── 3.1 Chemical space construction and target-anchored docking
│   │   │   ├── Scaffold-guided expansion (novelty vs scaffold recovery)
│   │   │   ├── Four-target docking profile + protocol validation
│   │   │   └── Mutation resilience, joint prioritization, cross-metrics
│   │   ├── 3.2 Resistance-aware scoring and the static-to-dynamic estimand
│   │   │   ├── Cohort scope, class counts, threshold sensitivity
│   │   │   ├── Estimand divergence (7/8 matched mutant states)
│   │   │   ├── Parent-study MD stability and MM-GBSA feasibility
│   │   │   └── Interaction-fingerprint hotspots
│   │   ├── 3.3 Quantum-inspired and topological representations
│   │   │   ├── Scaffold-paradox decomposition (H0/H1)
│   │   │   ├── Tensor-network compression and information retention
│   │   │   ├── Activity benchmark + hybrid ablation
│   │   │   ├── Quantum kernel vs tuned RBF
│   │   │   ├── ECFP4-inclusive fusion and ChEMBL transfer
│   │   │   └── Scaffold-grouped re-evaluation + TDA/docking cross-link
│   │   ├── 3.4 Learned representations under chemical distribution shift
│   │   │   ├── Three partition families (random / scaffold / Butina)
│   │   │   ├── Distance-resolved deficit + structural cohorts
│   │   │   └── Topological salience and metric degeneracy
│   │   └── 3.5 Synthesis: the comparison standard for Project 7
│   │
│   └── Target: 50 pages (remaining: expanded discussion, P7 methods/results)
│
├── General Conclusion (~5 pages) ⏳ TO ENHANCE
│   └── Gen_con.tex
│
├── Bibliography (~15 pages) ⏳ TO COMPILE
│   └── Bib_thesis_SAO.bib
│
└── Appendices (~5-10 pages) 📋 OPTIONAL
    ├── Supplementary Tables
    ├── Extended Candidate Lists
    ├── Code Snippets
    └── Additional Figures
```

## Project Integration Map

```
┌─────────────────────────────────────────────────────────────┐
│                    THESIS CHAPTERS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Chapter 1 (Lit Review) ✅                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ P1: Chemical space (65,856 mol, 4 targets)          │   │
│  │ P2: RRS + polypharmacology (17 candidates)          │   │
│  │ P3: Quantum descriptors (QKS ≈ RBF)                 │   │
│  │ P5: GNN < ECFP4 (scaffold split)                    │   │
│  │ P7: True QML via QMSE (framing; NOT_COMPUTED)       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Chapter 2 (Methods) ⏳                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Detailed protocols for P1-P3, P5, P7                 │   │
│  │ Docking/MD/ML/QML methodologies                      │   │
│  │ Statistical frameworks                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Chapter 3 (Results) ⏳                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Comprehensive P1-P3/P5 results + P7 framing          │   │
│  │ Figures, tables, statistical analyses               │   │
│  │ Cross-project comparisons                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Page Count Projection

| Component | Current | Target | Status |
|-----------|---------|--------|--------|
| Front Matter + General Intro | vi (roman) | ~5 | ✅ Complete (4-section pattern + Overview of the thesis argument) |
| **Chapter 1** | **pp. 1–34** | **30-35** | ✅ Aligned to canonical values; targets/NISQ/trainability/3D-representation/limitations/reporting subsections added 14 Oct |
| **Chapter 2** | **pp. 35–68** | **40** | ✅ Aligned to canonical protocols; 3D comparators, combination/ablation design, pipeline-null controls, sensitivity audits, benchmark design, claim ledger added 14 Oct |
| Chapter 3 | pp. 69–111 | 50 | ✅ Canonical results + §3.6 P7 (exploratory record with 3 figures) + 9 discussion subsections |
| General Conclusion | pp. 112–114 | 5 | ✅ Three contributions + QML programme requirements |
| Bibliography | pp. 115–141 | 15 | ✅ Compiled with biber (7 new entries 14 Oct) |
| Appendices | 0 | 5-10 | 📋 Optional (not required to hit target) |
| **TOTAL** | **141** | **150** | ✅ **Under limit; 9 pages reserved for P7 Phase D results when canonical** |

## Enhancement Roadmap to 150 Pages

### ✅ Phase 1: Chapter 1 Enhancement (COMPLETE)
- [x] Integrate P1–P3, P5 findings (P7 framing only)
- [x] Add computational methods sections
- [x] Add molecular representations section  
- [x] Add generative models section
- [x] Add validation workflows section
- [x] Write comprehensive conclusions
- [x] Maintain scientific rigor and honest-negative reporting
- [x] Compile successfully (43 pages)

### ⏳ Phase 2: Chapter 2 Enhancement (NEXT PRIORITY)
**Target:** +35 pages (43 → 78 pages total)

Detailed methodology sections for:
- [ ] P1: Docking protocols (AutoDock Vina, grid parameters, scoring)
- [ ] P1: Chemical space generation (hybrid library construction)
- [ ] P2: MD simulation protocols (force fields, equilibration, production)
- [ ] P2: RRS computation methodology
- [ ] P3: Quantum descriptor calculation (QKS, TFP, TNE)
- [ ] P3: Machine learning protocols (ECFP4, RF, hybrid models)
- [ ] P7: QMSE/BondFeatureMap methods section (to be written; framing only for now)
- [ ] P5: GNN architectures (GIN, ChemBERTa implementation)
- [ ] P5: Training protocols (scaffold splits, cross-validation)
- [ ] Statistical analysis frameworks
- [ ] Validation methodologies

### ✅ Phase 3a: Chapter 3 canonical results integration (COMPLETE, 28 Sept 2026)
- [x] P1 results: expansion statistics, four-target docking validation, RRS classes, cross-metrics
- [x] P2 results: class counts, threshold sensitivity, estimand divergence, MD stability, ProLIF
- [x] P3 results: scaffold paradox, TNE compression/regression, benchmark + ablation, quantum kernel, fusion, transfer, scaffold-grouped re-evaluation, TDA cross-link
- [x] P5 results: three partition families, distance-resolved deficit, structural cohorts, salience
- [x] Cross-project synthesis + Project 7 comparison standard (framing only)
- [x] Figures/tables harvested from canonical project directories (see inventory below)
- [x] Chapter 1 and Chapter 2 realigned to canonical protocols and values

### ⏳ Phase 3b: Chapter 3 expansion (remaining ~29 pages)
- [ ] Full per-mutant and per-target supplementary tables
- [ ] Extended discussion of ensemble retention and label-source limits
- [ ] Project 7 methods and results (NOT_COMPUTED; framing only until canonical runs exist)

## Chapter 3 figure and table inventory (harvested 28 Sept 2026)

All assets were copied from the canonical project directories into `My_PhD_Thesis/Graphics/`.

| Thesis asset | Source | Project |
|---|---|---|
| `p1_v7_chemical_space_coverage.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p1_v7_targetwise_profile_summary.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p1_v7_rrs_mutation_profiles.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p1_v7_exploratory_metric_relationships.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p2_workflow.pdf` (from `p2_preview-1.pdf`) | `V2609C/Graphics/` | P2 |
| `p2_rmsd_stability.pdf` | `V2609C/Graphics/` | P2 |
| `p2_prolif_heatmaps.pdf` | `V2609C/Graphics/` | P2 |
| `p2_cross_metric_correlation.pdf` | `V2609C/Graphics/` | P2 |
| `p3_scaffold_paradox.pdf` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_persistence_diagrams.pdf` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_tensor_compression.pdf` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_tne_regression_summary.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_qkernel_benchmark.pdf` (from `applicability_domain.pdf`) | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_extval_internal_vs_external.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_tda_promiscuity.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_h1_rrs_violin.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p5_auc_benchmark.png` | `manuscript/V2609/figures/` | P5 |
| `p5_structural_complexity.png` | `manuscript/V2609/figures/` | P5 |
| `p1_expansion_route_composition.pdf` | **new** — generated by `My_PhD_Thesis/create_expansion_route_figure.py` from `Papers_P1_previously/r6_expansion_analysis/expansion_analysis_results.csv` (07 Oct 2026) | P1 (early) |
| `p1_vae_training_curves.pdf` | `Papers_P1_previously/Graphics/` (07 Oct 2026) | P1 (early) |
| `p1_clustering_quality_comparison.pdf` | `Papers_P1_previously/Graphics/` (07 Oct 2026) | P1 (early) |
| `p1_intra_inter_similarity.pdf` | `Papers_P1_previously/Graphics/` (07 Oct 2026) | P1 (early) |
| `p1_physchem_by_cluster.pdf` | `Papers_P1_previously/Graphics/` (07 Oct 2026) | P1 (early) |
| `p1_admet_profiles.pdf` | `Papers_P1_previously/Graphics/` (07 Oct 2026) | P1 (early) |
| `p5_salience.png` | `manuscript/V2609/figures/` | P5 |
| `p7_exploratory_auc_folds.pdf` (from `fig3_roc_curves.pdf`) | `Project7.../manuscript/figures/` (14 Oct 2026) | P7 |
| `p7_exploratory_ablation.pdf` (from `fig4_ablation_bar.pdf`) | `Project7.../manuscript/figures/` (14 Oct 2026) | P7 |
| `p7_exploratory_scaffold_gradient.pdf` (from `fig5_scaffold_gradient.pdf`) | `Project7.../manuscript/figures/` (14 Oct 2026) | P7 |
| `p7_qfe_workflow.pdf` (from `fig1_workflow.pdf`) | `Project7.../manuscript/figures/` (14 Oct 2026; harvested, not yet cited) | P7 |
| `p7_qfe_circuit.pdf` (from `fig2_circuit.pdf`) | `Project7.../manuscript/figures/` (14 Oct 2026; harvested, not yet cited) | P7 |
| `p2_p2rank_pockets.pdf` (from `figure_p2rank_boxes.pdf`) | `P2 .../manuscript/V2609C/Graphics/` (14 Oct 2026) | P2 |
| `p5_mol_rescue_top4.png`, `p5_learning_curves.png` | `P5 .../manuscript/V2609/figures/` (14 Oct 2026; harvested, not yet cited) | P5 |

Tables authored natively in Chapter 3 from the canonical result tables: P1 docking validation,
P1 per-candidate RRS classes, P2 MD stability metrics, P3 activity benchmark and hybrid ablation,
P5 three-partition benchmark, P5 structural-complexity cohorts. Added 07 Oct 2026: `tab:res_vae_comparison`
(32D vs 64D VAE model selection) authored from `Papers_P1_previously/vae_clustering_analysis/vae_comparison_table.tex`
after provenance screening. Excluded on provenance grounds: `si_figure_s14_umap_latent_space.png`
(row-order source labels), early redocking/enrichment figures (superseded validation round),
R6 alternative-parameter estimates.

### ⏳ Phase 4: Supporting Components
**Target:** +20 pages (123 → 143 pages total)

- [ ] Expand General Introduction (3 → 5 pages)
- [ ] Expand General Conclusion (2 → 5 pages)
- [ ] Compile bibliography with biber (0 → 15 pages)
- [ ] Add appendices (optional, 5-10 pages):
  - Extended candidate lists
  - Supplementary tables
  - Code snippets/pseudocode
  - Additional validation figures

### ⏳ Phase 5: Final Refinement
**Target:** 150 pages

- [ ] Final LaTeX compilation with bibliography
- [ ] Resolve all cross-references
- [ ] Verify figure/table numbering
- [ ] Proofread all chapters
- [ ] Ensure consistent notation
- [ ] Check page count distribution
- [ ] Final PDF generation

## Key Accomplishments (Chapter 1)

### Scientific Integrity Maintained
- ✅ **Honest-negative reporting:** P3 and P5 null/negative results presented transparently
- ✅ **Provenance boundaries:** Computational predictions clearly distinguished from experimental validation
- ✅ **No fabrication:** All numbers from canonical DARs
- ✅ **No overclaiming:** Quantum advantage not claimed; GNN limitations acknowledged

### Writing Quality Standards
- ✅ **Full paragraphs:** No bullet points in final text
- ✅ **Flowing prose:** Proper transitions and sentence variety
- ✅ **Anti-AI patterns avoided:** No "delve," "elucidate," "underscore," etc.
- ✅ **Citations integrated:** Natural in-text citations, not lists
- ✅ **Scientific tone:** Mechanistically grounded, precise language

### Technical Quality
- ✅ **LaTeX compilation:** 0 fatal errors
- ✅ **Cross-references:** All labels resolved
- ✅ **Figure integration:** References to existing P1–P3/P5 figures
- ✅ **Table references:** Citations to canonical result tables

## Timeline Estimate for Completion

| Phase | Estimated Time | Pages Added | Running Total |
|-------|---------------|-------------|---------------|
| Phase 1 (Ch 1) | ✅ Complete | +5-8 | 43 |
| Phase 2 (Ch 2) | 3-5 days | +35 | 78 |
| Phase 3 (Ch 3) | 5-7 days | +45 | 123 |
| Phase 4 (Support) | 2-3 days | +20 | 143 |
| Phase 5 (Refine) | 1-2 days | +7 | 150 |
| **TOTAL** | **11-17 days** | **+107** | **150** |

## Files Created/Modified

1. **Modified:**
   - `My_PhD_Thesis/Chapters/chap_lit_rev.tex` (193 → 320 lines)

2. **Created:**
   - `My_PhD_Thesis/CHAPTER1_ENHANCEMENT_SUMMARY.md` (this summary)
   - `My_PhD_Thesis/THESIS_PROGRESS_MAP.md` (this roadmap)

3. **Compiled:**
   - `My_PhD_Thesis/PhD_SAO_V250404.pdf` (43 pages)

## Next Immediate Actions

1. **Bibliography compilation:**
   ```bash
   cd My_PhD_Thesis
   pdflatex PhD_SAO_V250404.tex
   biber PhD_SAO_V250404
   pdflatex PhD_SAO_V250404.tex
   pdflatex PhD_SAO_V250404.tex
   ```

2. **Chapter 2:** ✅ aligned to canonical P1/P2/P3/P5 protocols (target IDs, docking parameters, RRS definition and classes, ACSI definition, PNS source, force fields, descriptors, GIN/transformer settings, partition families). Remaining: P7 QML methods section once the protocol is frozen.

3. **Chapter 3:** ✅ canonical P1–P3/P5 figures and tables integrated with the synthesis that sets the Project 7 comparison standard. Remaining: expanded discussion, per-mutant supplementary tables, P7 results section (NOT_COMPUTED — no claims until canonical runs).

4. **Generate figures:** Create schematics for any new sections using the scientific-schematics skill.

---

**Status:** Chapter 3 discussion expansion applied (14 Oct 2026) on top of the 13 Oct unified-narrative refinement. Build clean: **119 pages (≤150 target)**, 0 LaTeX errors, 0 undefined references/citations, 0 multiply-defined labels, `git diff --check` clean. Chapter spans (verified against the built TOC): Ch1 p1, Ch2 p26, Ch3 p52, Gen Con p91, Bib p94, end p119. Remaining growth options if further pages are wanted: per-mutant/per-target supplementary tables (Phase 3b), appendices, or P7 Phase C/D results when canonical runs exist (NOT_COMPUTED — §3.6 stays predeclared until then). Remaining human steps: visual proofread of new pages; author review before any commit.
