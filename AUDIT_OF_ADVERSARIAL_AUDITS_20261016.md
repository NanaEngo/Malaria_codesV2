# Meta-Audit of the Four Adversarial Audit Reports (P1, P2, P5, P7)

**Date:** 16 October 2026
**Framework:** `scientific-critical-thinking` (claim–evidence, construct validity, bias, statistical unit) and `peer-review` (claim→evidence mapping, reproducible *evidence-bounded* assessment) — used as review scaffolds, not as merit scores.

**Status of the audited documents:** every finding below describes the four documents as they stood in **rev 1**. All four were subsequently repaired as **rev 2** (16 Oct 2026): commit pinning header, addendum folded into the body, retracted targets withdrawn, unlocatable citations removed, and the P1 root causes corrected against the canonical artifacts — and then extended as **rev 2.1** with a referee-facing *"wow factor"* section in each document (§10 below summarises the four and their evidence status). Where §2 and the revised documents differ, the revised documents are authoritative — the ledger here is the record of what was wrong and why.
**Audited documents**

| ID | Document |
|---|---|
| P1-A | `Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_ADVERSARIAL_AUDIT_AND_REFINEMENT.md` |
| P2-A | `Project2_Polypharmacology_MD_ValidationV2607/P2_ADVERSARIAL_AUDIT_AND_REFINEMENT.md` |
| P5-A | `Project5_GNN_Transformer_DrugDiscovery_V2609/P5_ADVERSARIAL_AUDIT_AND_REFINEMENT.md` |
| P7-A | `Project7_Quantum_Molecular_Encoding_QML/P7_ADVERSARIAL_AUDIT_REPORT.md` |

---

## 0. Method and scope (read this before trusting any verdict below)

Three independent evidence streams were used, in this order of precedence:

1. **Repository artifacts** (highest precedence for claims about this project's work) — receptor files, run manifests, `summary.json/.txt`, DARs, manuscripts, git trees.
2. **Versioned external records** — PDB/PDBe/RCSB REST, Europe PMC full text, DOI pages, arXiv listings.
3. **Search-indexed literature** — used only to test existence/attribution of cited works, never as evidence for a scientific mechanism.

Time-boxed limits of this pass (stated because the documents under audit do not state theirs):

- 25 claims/artifacts re-checked (table §2). Not every claim in the four documents was re-verified.
- Two search attempts per "does this citation exist?" question. Failure to locate a work is reported as **not locatable**, which is not the same as proof of non-existence.
- No re-execution of docking, MD, or QML pipelines. Nothing in this document is a reproduction.
- Items I did **not** check are listed in §9 rather than silently marked verified.

---

## 1. Headline verdict

The four audits do real diagnostic work — the P7 audit in particular is accurate on its build/provenance findings, and the P1/P5 construct-validity argument about `eos80ch` surrogate labels is substantively correct. But they share three defects that materially reduce their value:

1. **They were written against an obsolete snapshot of the tree.** At least four P1 "fatal flaws" were already tested (and in one case refuted) by controlled runs the project had completed weeks earlier and integrated into its own DAR.
2. **They contain two demonstrably wrong "✅ Verified" citations and at least four citations that cannot be located at all.** One wrong citation (the MTX root cause) is load-bearing for the P1 scorecard.
3. **Their addenda correct their own bodies, but the bodies were never edited.** Every one of the four appends an "Addendum v2 — Web-Verified" section that retracts or narrows a headline claim; the scorecards, novelty tables and action plans above those addenda still assert the retracted version.

Consequence: as written, the documents cannot be cited as "current state of the project". They should be converted into a single **audit register** (§7.1) with explicit statuses (`OPEN / FIXED / OBSOLETE / REFUTED`), commit pinning, and per-claim evidence links.

---

## 2. Verification ledger

Method codes: **R** = repository artifact read; **A** = external structured record (PDB REST, Europe PMC, arXiv API); **S** = search-indexed literature.

| # | Claim under audit | Method | Verdict |
|---|---|---|---|
| 1 | P1-A §1/§2.2: `PfDHFR` DEKOIS failure is *caused* by retained **MTX** blocking the pocket; fixing it is the "critical path" to `AUC > 0.75`, `EF@1% > 5.0` | R | **CONTRADICTED BY THE PROJECT'S OWN CONTROLLED RUN.** `results/dekois_mtxstripped_20260909/` (2026-09-09, status `JOB_COMPLETE`) ran the two-arm test: retained receptor AUC **0.5023** [0.4225, 0.5862], `EF@1%` **0.00**; MTX-**stripped** receptor AUC **0.5626** [0.4772, 0.6463], `EF@1%` **0.00**. ΔAUC +0.060 with overlapping bootstrap CIs. `P1_DATA_ANALYSIS_REPORT.md` §R2.4 concludes verbatim: *"removing MTX does not restore enrichment … Reviewer R2.4's MTX-blockade hypothesis is therefore **not supported**"*, attributing the null result to single-method Vina scoring and grid positioning. P1-A re-asserts the refuted hypothesis as a 🔴 CRITICAL root cause. |
| 2 | P1-A §2.2: the grid centre "coincided to **0.00 Å**" with co-crystallised MTX; box centre `(26.66, 42.19, 39.89)` | R | **FALSE AS RECORDED.** `scripts/p1_r24_dekois_mtxstripped.py` documents the actual protocol: grid centre `(1.33, −1.733, −23.842)`, 25 Å box, and *"MTX CoM in this frame is (7.44, 0.57, −29.74), ~8.9 Å from the grid center"*. The `(26.66, 42.19, 39.89)` triple occurs in `PfDHFR_WT_clean.pdb` as **B-factor values**, not coordinates — the number appears to have been lifted from the wrong column. |
| 3 | P1-A: `PfDHFR` = **1J3I**, whose co-crystallised ligand is MTX | A (PDBe/RCSB) | **WRONG ENTRY AND WRONG LIGAND.** Ligand inventory of `1J3I` = `HOH`, `NDP` (NADPH), `UMP`, `WRA` — **no MTX**. `1J3K` likewise. The DEKOIS "retained" arm used `Project2_.../data/proteins/7F3Y.pdbqt` (structure *Structure* 2022, MANORAA), which is the entry that retains MTX. |
| 4 | P1-A §2.1: `6UKJ` is the 7G8 (K76T) isoform | A (RCSB entry + FASTA) | **CORRECT.** Entry annotation reads `Plasmodium falciparum (isolate 7G8)`; citation Kim et al., *Nature* **576**, 315–320 (2019). |
| 5 | P1-A §2.1: residue 76 lies **16.7–19.5 Å outside** the docking box, so the primary RRS table is invalid | R | **OBSOLETE.** `results/pfcrt_redock_v2grid_20260909/manifest.json` (status `COMPUTED`, "V2-corrected grid") records grid centre `(152.99, 151.042, 159.379)`, 25 Å box, and *"residue 76 CA 11.2 Å from center"* → the CA is **inside** the box (half-edge 12.5 Å). The audit's geometry describes the superseded pre-R2.3 grid. |
| 6 | P1-A §4 "Novelty 4.1": no WT→WT* null control was computed — this must be built | R | **ALREADY IMPLEMENTED.** The same canonical run includes a `NULL` receptor (WT passed through the mutation script; sha256 pinned), with `rrs_null_pfcrt` = mean 100.0, range **[99.4, 100.5]**, and `max_abs_deviation_mutant_vs_null` = K76T 1.2, K76A 0.51. |
| 7 | P1-A §2.4: `ρ(N_fav, RRS_mean) = +0.515 (p = 0.034)` was omitted from the primary table | R | **STALE NUMBER.** Canonical corrected run reports `nfav_rrs_spearman` = **ρ 0.7137, p 0.0013** (100 000-permutation p = 0.00192). Quoting 0.515 understates the project's own corrected result. |
| 8 | P1-A §2.3 / P2-A §2.4: P1 V8 and P2 V2609C report the **same 17-molecule cohort** | R | **CORROBORATED.** `Project7_.../data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv` has 17 rows, `cohort_id = P2_SET_C_POLYPHARM_17`, candidate IDs `PP-01…PP-17`, and a single `p2_source_sha256`. The reuse is *documented in provenance columns*; the defect is naming (`"P1 Set A"` = `"P2 Set C"` = P7's cohort) and editorial overlap, not missing provenance. |
| 9 | P1-A: Hany et al. 2025 achieved `EF1% ≈ 28` (WT, PLANTS+CNN) and `≈ 31` (quadruple mutant, FRED+CNN) on DEKOIS 2.0 | A (Europe PMC, PMC12363558) | **CORRECT.** Paper reports `EF1% = 28.41` and `EF1% = 31.02`, and states ML rescoring improved AutoDock Vina "from worse-than-random to better-than-random". |
| 10 | P2-A §2.1: Soares et al., *JCIM* **63**(11), 3227–3229 (2023) requires ≥3 replicas and sets no ns cutoff | A/S | **CORRECT** (DOI 10.1021/acs.jcim.3c00599; authors Soares, Cournia, Naidoo, Amaro, Wahab, Merz). The addendum's correction of the body is right — and still not applied to the body. |
| 11 | P5-A §2.1: `eos80ch` is a classical fingerprint model; its labels may encode **stage-selectivity**, not general antiplasmodial activity | A (Europe PMC lineage) + R | **CORRECT AND STILL UNRESOLVED IN-REPO.** The model family is van Heerden, Turon, Duran-Frigola, Pillay, Birkholtz, *ACS Omega* **8**(46), 43813–43826 (2023), DOI 10.1021/acsomega.3c05664: models trained on asexual-blood-stage (126 374) and sexual/gametocyte (93 941) screening data to recognise **stage-specific** activity. Repo documentation (`Project3_.../manuscript/LaTeX/V2609/PLACEHOLDER_COMPLETION_GUIDE.md`, `SUBMISSION_READY.md`) declares only "Ersilia eos80ch computational predictions (threshold 0.5)" — the stage semantics are never stated. This affects P3, P5 **and** P7. |
| 12 | P5-A: Tursunbadalov & Tursunbadalov, arXiv:2607.06605 (2026) | A/S | **REAL.** Title matches; proposes the class-conditional (Mondrian) fix. |
| 13 | P5-A: Wee & Jiang, *JCIM* **65**(23), 12691–12706 (2025) | A (PubMed 41235667) | **REAL** (DOI 10.1021/acs.jcim.5c02266). |
| 14 | P7-A (ledger): Thanasilp et al., "Exponential concentration and untrainability in quantum kernel methods", ***Quantum* 8, 1481 (2024)** — marked ✅ Verified | S | **WRONG VENUE AND VOLUME.** The published version is *Nature Communications* **15**, 5200 (2024). |
| 15 | P7-A §11: Projected Quantum Kernels attributed to **"Huang et al., *Science* 2021"** | S | **WRONG VENUE.** PQKs/1-RDM projections are Huang et al., *Nature Communications* **12**, 2631 (2021), "Power of data in quantum machine learning". (The *Science* 2022 reference in the same document is a different paper and is cited correctly there.) |
| 16 | P7-A (ledger): Cerezo et al., *Nat. Commun.* 2025 — "confirm volume/page" | A/S | **RESOLVED:** *Nature Communications* **16**, 7907 (2025), DOI 10.1038/s41467-025-63099-6. |
| 17 | P7-A §3.2: Boy et al.'s contraction theorem is for repeated **linear** substructures, so ring extension is new/unproven | A (arXiv:2507.20422 abstract) | **CORRECT.** The abstract states: *"we further prove a fidelity-preserving chain-contraction theorem that reuses common substructures to cut qubit counts, with an application to long-chain fatty acids."* |
| 18 | P7-A §5/§6: five canonical scripts, three result directories and `fig6_phased_results.pdf` are missing from Git; raw `Δ` at `methods.tex:284` breaks pdflatex | R | **CONFIRMED against the canonical tree.** All eight paths `ABSENT`. `grep -n "Δ" Project7_.../manuscript/sections/methods.tex` → line 284: `(Δ~$= 0.003$` (raw U+0394 inside a mixed text/math fragment). |
| 19 | P1-A §4 + action step 5, and P5-A Novelty 1: **"Gabrani et al., *JCAMD* 2024"** — ECFP4-RF robustness across scaffold splits | S (2 queries) | **NOT LOCATABLE.** No such record; the only "Gabrani" hits are digital-pathology GNN papers by a different author. Cited with a specific finding and listed as a required action-plan citation. Treat as unverifiable; do not ship. |
| 20 | P1-A §4, P5-A Novelty 1: **"Tang et al., *Nature Machine Intelligence* 2025 — the 'fingerprint paradox'"** | S (2 queries) | **NOT LOCATABLE.** Zero hits for the named work. Treat as unverifiable; do not ship. |
| 21 | P5-A Novelty 3: **"Alvarsson et al., *JCIM* 2023 — Mondrian CP achieving exact 90% coverage on ChEMBL actives"** | S (2 queries) | **NOT LOCATABLE as stated.** The locatable lineage is Alvarsson & Norinder (2021), the CPSign paper (Arvidsson McShane et al., *J. Cheminform.*, 2024, DOI 10.1186/s13321-024-00870-9) and the 2025 conformal-prediction-in-cheminformatics review (Astigarraga et al., DOI 10.1016/j.ailsci.2025.100125 — confirm before citing). Replace. |
| 22 | P2-A §4 Novelty 1: **"Pandas et al., *JCTC* 2023 — MM-GBSA bootstrap ±1.5 kcal/mol"** (flagged ⚠️ in the addendum, still asserted in the body) | S (2 queries) | **NOT LOCATABLE.** Remove from the body, not just from the to-do list. |
| 23 | P2-A §4 Novelty 1: **"Mobley et al., *Ann. Rep. Comput. Chem.* 2021"** for MM-GBSA-vs-FEP practice, incl. "SD of 7.75 kcal/mol is typical" | S (2 queries) | **NOT LOCATABLE as cited.** The ARCC alchemical chapter is Shirts/Mobley/Chodera (2007). The quoted 7.75 kcal/mol is **this project's own measured spread** (PP-01 PfCRT WT) — presented as literature. That is a circular-citation defect, the most serious citation problem in the four documents. Correct anchor: Mey et al., *LiveCoMS* (2020), "Best Practices for Alchemical Free Energy Calculations [Article v1.0]" — retrieve the DOI/article number from the LiveCoMS record before citing. |
| 24 | P2-A addendum B1: Rocklin et al., *J. Chem. Phys.* **139**, 184103 (2013) for charge-changing alchemical corrections | A (PubMed 24320250) | **REAL**, and correctly used to bound scope. Strengthen with Grundschober et al., *JCTC* **21**(11), 5669 (2025) on the *limitations* of co-alchemical charge changes. |
| 25 | P1-A §3: "Eberhardt 2021" as a pipeline anchor | S | **REAL but mis-attributed in context** — Eberhardt et al. 2021 (*JCIM* **61**, 3891–3898) is **AutoDock Vina 1.2.0**, not GNINA. GNINA is McNutt et al. (2021); GNINA 1.3 (2025) is current. |

---

## 3. Critical findings, by failure type

### 3.1 Artifact-contradicted claims (P1-A)

The P1 scorecard's top two 🔴 CRITICAL rows are the DEKOIS/MTX causal story and the PfCRT box geometry. Both are contradicted by artifacts the same project produced on **9 September 2026** and integrated into `P1_DATA_ANALYSIS_REPORT.md`:

- **DEKOIS:** the two-arm MTX-stripped experiment is *already the correct design* and *already delivered a negative answer*. P1-A states the opposite conclusion with more confidence than the experiment that tested it. It also sets `AUC > 0.75 / EF@1% > 5.0` as a target for a rescue that the data says will not happen — and its own addendum v2 forbids pre-claiming exactly that number ("*pre-register the metric, do not pre-claim `AUC > 0.75`*"), i.e., §5 of the body is in direct contradiction with §A of its own addendum.
- **PfCRT:** the corrected receptor ("corrected 3D7-like wild-type (LYS-76), 6UKJ frame"), the cavity-anchored V2 grid, and the `NULL` self-mutation control are all implemented. P1-A §4 Novelty 3–4 therefore proposes, as new work, three things that exist.

Root cause of this class of error is procedural, not intellectual: **the audits do not pin a commit** and do not cite the artifact paths they inspected. Fix that (§7.1) and this failure mode disappears.

### 3.2 One residual geometry concern the audits and the project both under-specify

The canonical manifest justifies the corrected PfCRT grid with *"residue 76 CA 11.2 Å from center"*. In a 25 Å box the CA sits inside with only ~1.3 Å of margin, and CB sits ~1.5 Å further out. "Residue 76 is inside the box" is therefore true for the CA but not established for the whole residue. Both the DAR and any future audit should report **max atom distance of the residue from the centre (and the fraction of the residue inside)**, not the CA alone. This is a one-line change to the gate and it removes an obvious reviewer attack.

### 3.3 Citation-integrity failures

Two "✅ Verified" entries are wrong (ledger #14, #15), and five cited works cannot be located (#19–#23), one of which converts the project's own measurement into a literature claim (#23). The documents' ledgers mark claims "✅ Verified" without recording *what* was checked, *against what source*, or *when* — so the marks carry no information. A ledger entry without a DOI/URL and a date should be treated as unverified by default.

### 3.4 Statistical-unit incoherence across the four documents

Each document reasons about a different unit of inference and none of them reconciles:

- **P1-A** argues power at the level of 17 molecules and two-sided Spearman tests (correct diagnosis of the "accepting the null" fallacy, but no positive alternative).
- **P2-A** correctly identifies ligand-level pseudo-replication (8 "comparisons" from 2 ligands) but the body still reports the Wilson interval for 7/8 as if the denominator were 8.
- **P5-A** proposes scaffold-cluster bootstrap (sound) while its own headline comparison still rests on n = 5 seed means.
- **P7-A** proposes permutation tests on stereoisomer pairs without stating the clustering (chemistry series, scaffold families) that those pairs come from.

Program-level fix in §7.2.

### 3.5 Novelty proposals that propagate an unvalidated estimand

P7-A's Tier B/C benchmarks use P1/P2 **RRS** and the 87.5% static-vs-MD divergence as ground truth for a new method. But RRS's validity is precisely what P1-A §2.3 and P2-A §2.2 argue is unresolved. A new estimator cannot be validated against a contested label. Either (a) validate on external experimental fold-shift data first, or (b) frame the work as *estimand-relative* ("which estimator is self-consistent, and where do they diverge") — which is honest but must not be advertised as mechanistic ground truth.

---

## 4. What the audits get right (keep these)

- **P7-A §3.1 (CIP parity bug), §3.2 (8-atom truncation), §3.3 (2-D bond-length "Coulomb matrix"), §4.1 (non-entangling `R_z ⊗ R_z` "bond" encoding), §4.2 (SWAP test vs inversion test):** these are concrete, checkable implementation defects with correct RDKit/quantum-mechanics reasoning. The distinction between `CHI_TETRAHEDRAL_CW/CCW` traversal parity and CIP `R/S` is stated correctly and the proposed fix uses `FindMolChiralCenters`' returned label.
- **P7-A §5/§6 provenance and build failures:** reproduced exactly in this pass, including the raw `Δ`.
- **P5-A §2.1 construct-validity argument:** evaluating non-fingerprint architectures against a fingerprint-derived surrogate oracle is a genuine teacher–student confounder, and the audit's own addendum correctly refuses to over-claim it ("approximately aligned with ECFP-family features … test it empirically"). Verified lineage supports the stage-specificity caveat.
- **P5-A Novelty 4 (scaffold-clustered inference):** the right unit, correctly argued (out-of-fold predictions clustered by Bemis–Murcko scaffold), and it does not require new experiments.
- **P2-A §2.1 / §2.3:** the replica-count critique of the 10 ns single-replicate design is correct and correctly distinguishes "no ns cutoff exists" from "a design choice of ours". The PfCRT `K76T` electrostatic-barrier argument (Lys76⁺ → Thr76⁰, diprotonated weak-base substrate, acidic vacuole) is the correct biophysics and is the single most valuable scientific correction in the four documents.
- **P1-A §2.4:** naming the "accepting the null" fallacy at n = 17 is correct.
- **Addenda v2 of all four:** the *content* of the corrections is largely right (Soares pagination, 3 × 50 ns as design choice, ESS collapse under scaffold splits, Mondrian × weighting caveats, dequantization risk, `PH-QMSE` needing its own fidelity proof). The problem is that they never propagated upward.

---

## 5. Deep improvements — program level

### 5.1 Convert the four documents into one machine-checkable audit register

Replace four prose documents that each restate each other's findings with:

```
ADVERSARIAL_AUDIT_REGISTER.md      # human-readable, one row per finding
audit_register.json                # machine-checkable, CI-enforced
```

Row schema (one per finding):

| field | meaning |
|---|---|
| `id` | `P1-REC-003` (project–category–number) |
| `claim` | one sentence, falsifiable |
| `status` | `OPEN / FIXED / OBSOLETE / REFUTED / UNVERIFIED` |
| `evidence` | repo path **+ git blob sha256** and/or DOI |
| `check_cmd` | the exact command that falsifies it |
| `audited_at_commit` | `git rev-parse HEAD` at time of writing |
| `verified_by` / `verified_at` | who and when; empty ⇒ treat as unverified |

CI rule: fail the build if an `evidence` hash no longer resolves, or if a row is `OPEN` while its `check_cmd` passes. This is the only durable fix for §3.1 — it makes staleness a build error instead of a review finding.

### 5.2 Pin every audit and every downstream claim to a commit

Add to the header of each audit *and* each DAR section: `audited_at_commit: <sha>` plus `git status --porcelain` at capture time. The P7 audit's file links point at `/home/taamangtchu/Documents/Malaria_codesV2/...`, which is not the canonical tree defined in `AGENTS.md` §0 (`/home/nanaengo/Malaria_codesV2`) — evidence that the audit was authored against a different working copy. Use repo-relative paths only.

### 5.3 Replace "no significant effect ⇒ independence" with a positive equivalence test

For every claim of the form "X is independent of Y" (P1-A's correlation table, P2-A's divergence claim, P5-A's split comparisons): pre-declare a smallest effect size of interest (SESOI), then report a **TOST / ROPE** decision, not a failed rejection. The audits diagnose this fallacy (P1-A §2.4) but never supply the fix, so the manuscript still contains the fallacy.

### 5.4 Adopt one reporting standard per evidence type, declared in the methods

- MD: the JCIM reporting guideline (Soares et al. 2023) **plus** LiveCoMS Best Practices for Alchemical FE (Mey et al. 2020); deposit COMBINE/FAIR metadata.
- Virtual screening: report at a **fixed budget** with a bias-corrected enrichment metric; the traditional EF estimator is known to misestimate true enrichment (Brocidiacono et al., 2024 — see §5.5 for why this matters here).
- ML benchmarks: declare the data-generating process of the labels (oracle vs experiment), the split, the clustering, and the multiplicity policy — in a table, before the results.

### 5.5 Fix the enrichment-metric problem: `EF@1%` at 40 actives is noise

The project's own bootstrap CI quantifies this: with 40 actives and 1199 decoys, `AUC = 0.5023` has a 95% CI of **[0.4225, 0.5862]** — a half-width of ~0.08. `EF@1%` is computed from the top ~12 of 1240 ranked compounds, so its sampling variance swamps any effect the pipeline could plausibly produce. Number of actives, not docking quality, is the binding constraint on this benchmark.

Recommended for P1 (and any future enrichment claim):

1. Pre-register the metric set: **BEDROC(α = 20)**, `EF@5%`, and a bias-corrected EF, each with a scaffold-cluster bootstrap CI — never bare `EF@1%` from 40 actives.
2. Run a **power/CI simulation before the dock** (actives 40 → 400; decoys fixed ratio) and choose the panel size that makes a pre-declared effect detectable, or report the design as underpowered and demote the benchmark to descriptive.
3. Keep the existing two-arm retained-vs-stripped design as a permanent **protocol-sensitivity** table: it is honest, it is already computed, and it is more valuable to a reviewer than a rescued enrichment number.
4. Move the primary validity evidence for the docking setup off enrichment and onto **pose recovery**: crystallographic-ligand redocking RMSD for a control set (already available: pyrimethamine, cycloguanil, WR99210 on PfDHFR; CQ/PPQ on PfCRT), reported per ligand with the pose, not just "RMSD < 2.0 Å all targets".

---

## 6. Deep improvements — per project

### 6.1 P1 — chemical space, compression, RRS

| # | Improvement | Why (evidence) |
|---|---|---|
| P1-1 | Delete the MTX causal claim; replace with the completed two-arm protocol-sensitivity result and the DAR's own conclusion | Ledger #1–#2 |
| P1-2 | Retire `AUC > 0.75 / EF@1% > 5.0`; replace with the §5.5 pre-registered metric set | Ledger #1; CI width ±0.08 |
| P1-3 | Re-attribute the DEKOIS receptor to `7F3Y.pdbqt` (or whichever entry the retained arm used) with sha256; keep `1J3I`/`6UKJ` only where they are actually used | Ledger #2–#3 |
| P1-4 | Restate PfCRT corrections as *done* (corrected 3D7-like LYS-76 receptor, V2 cavity grid, `NULL` control) with the manifest as evidence; add the max-atom-distance check of §3.2 | Ledger #5–#6 |
| P1-5 | Compression: keep the DPP proposal but implement it as a low-rank/Nyström or greedy log-det selection, report the approximation error, and add Tanimoto-MaxMin as a baseline; report the **active-retention curve** `R(K)` over `K ∈ {100, 250, 484, 1000, 2500}` with scaffold-cluster CIs | The audit itself flags the 35 GB dense-kernel infeasibility — that correction belongs in the body |
| P1-6 | Replace the two unlocatable citations (#19, #20) with locatable evidence on representation robustness: Deng et al., *Nat. Commun.* (2023), DOI 10.1038/s41467-023-41948-6 (systematic study of key elements in molecular property prediction) and, for the modern fingerprint-foundation-model counterpoint, arXiv:2506.15792 (2025). Re-word the claim so it is supported by what those works actually report | Ledger #19–#20 |
| P1-7 | Recompute the "omitted correlation" from the canonical corrected artifacts (ρ = 0.7137) and harmonise the class counts (`A* = 7, B = 4, C = 6`) across P1/P2 text | Ledger #7; `revision_summary.json` |
| P1-8 | `Chiral-STONED`: bound the claim. Vina is weakly stereodiscriminating; present chirality locking as **library-coverage** novelty and add an enantiomer-pair control before claiming any docking-level stereoselectivity | P1-A addendum B3 is correct — it just never reached the body |

### 6.2 P2 — MD, free energy, estimand mapping

| # | Improvement | Why |
|---|---|---|
| P2-1 | Delete the "3 × 50 ns requirement" reading from the body; state it as a design choice with a convergence criterion | Ledger #10 |
| P2-2 | Replace the "7.75 kcal/mol is typical in the literature" sentence with the project's own measured spread, correctly attributed, plus Mey et al. (2020) as the practice anchor | Ledger #23 |
| P2-3 | Define the estimand mapping explicitly: `RRS ↔ ΔΔG_bind` (units, reference state, sign convention) **before** comparing estimators; report ΔΔG, not only the dimensionless ratio | P2-A addendum B2 |
| P2-4 | Alchemical route: restrict NEQ-FEP to net-charge-preserving substitutions (`S108N`, `I164L`, `N51I`) and mark `K76T`/`C59R` exploratory, with co-alchemical ion + finite-size treatment; cite Rocklin 2013 **and** the 2025 limitations paper | Ledger #24 |
| P2-5 | Convergence package per replicate: block-averaged ΔG vs block size, integrated autocorrelation time, replica-to-replica SD, and a pre-declared equilibration-exclusion rule. Report "not converged" when it is not | P2-A addendum C is right; make it a table |
| P2-6 | PfCRT claims: model the transporter in a membrane with pH 5.2 protonation, and either (a) estimate a transport-relevant quantity (pore hydration free-energy profile / PMF, gating coordinate) or (b) narrow the claim to binding-competence. A soluble-protein docking/MM-GBSA readout cannot establish efflux | P2-A §2.3 is the best science in the set; the body must not outrun it |
| P2-7 | Controls as a gate: pyrimethamine / cycloguanil (susceptible) vs WR99210 (resilient), CQ/PPQ/verapamil for PfCRT. Source the reference fold-shifts from primary literature with DOIs before looking at any model output | P2-A §4.4; prevents post-hoc control selection |
| P2-8 | Measure ns/day per system on the RTX A4000 and write the budget into the DAR **before** committing to the ensemble + FEP legs | P2-A addendum C; `AGENTS.md` §4 |
| P2-9 | Governance: one canonical manuscript version with a changelog; the tree now carries `V2609C`, `V2610C_save`, `Submission_JCIM`, `submission_ACS_P2V2609C` and ChemRxiv variants — a desk-rejection risk on its own | Ledger #8 class of defect |

### 6.3 P5 — surrogate labels, higher-order message passing, conformal triage

| # | Improvement | Why |
|---|---|---|
| P5-1 | Document the label semantics in the methods: `eos80ch` derives from stage-specific (ABS vs gametocyte) screening data; state which output and polarity were binarised at threshold 0.5, or drop the "malaria activity" framing | Ledger #11 — verified, and still absent from repo docs |
| P5-2 | Make the dual-oracle comparison co-primary: surrogate panel vs a pre-declared experimental panel (with InChIKey dedup against the surrogate set and reported scaffold overlap) | P5-A Novelty 1 is sound; publish the label provenance, not the caveat |
| P5-3 | Quantify teacher–student alignment instead of asserting a "theorem": sweep fingerprint radius/bit-length and fingerprint family (Morgan vs MACCS vs RDKit-FP), and report the agreement between teacher and student feature spaces | P5-A addendum C1. A "Surrogate-Oracle Bias Theorem" without a proof should be labelled a hypothesis |
| P5-4 | Conformal: implement class-conditional (Mondrian) CP first (<100 lines), then covariate-shift weighting with **ESS reported and a pre-declared ESS floor** falling back to unweighted split-conformal; state the assumption (covariate shift ≠ label shift) | P5-A addendum B1–B2; Tursunbadalov 2026 is the verified class-conditional fix |
| P5-5 | For triage semantics, prefer a **false-discovery-rate-controlling conformal selection** construction over prediction sets: the operational question is "which compounds do we route to physics", i.e. which selections are wrong, not which labels are uncertain | Directly answers the audit's own "Route to Physics Docking" idea with the estimator that matches it |
| P5-6 | Higher-order test: keep the 3-arm ablation, but add (a) a matched-parameter classical substructure baseline and (b) an identical hyperparameter-search budget across arms, and (c) a **stereo-aware fingerprint baseline** (ECFP is stereo-blind) to test the chirality claim cheaply | P5-A Novelty 2 + addendum C4; without (a)+(b) the "ring message passing works" gain is confounded with capacity |
| P5-7 | Statistical unit: scaffold-clustered bootstrap on out-of-fold predictions, with a mixed-effects logistic regression (scaffold random intercept) as a cross-check; report the effective number of clusters | P5-A Novelty 4 is the right call — make it the *only* inferential route in the paper |
| P5-8 | Replace citation #21 with locatable conformal-VS sources (CPSign, Arvidsson McShane et al. 2024, DOI 10.1186/s13321-024-00870-9; Astigarraga et al. 2025 review — verify; Tursunbadalov 2026) and state coverage per decile **and** per class | Ledger #21 |
| P5-9 | Keep the honest-negative scaffold result and the "no universal GNN inferiority" limitation verbatim from `AGENTS.md` §5 — the register makes it auditable | Project instruction |

### 6.4 P7 — QMSE, chirality, kernels, provenance

| # | Improvement | Why |
|---|---|---|
| P7-1 | Fix the two mis-attributed citations and add the resolved Cerezo reference | Ledger #14–#16 |
| P7-2 | Reorder the document: the non-entangling encoding is the **first** finding, not an addendum footnote. A product-state feature map is classically simulable by construction, and the benchmark literature finds entanglement removal often doesn't hurt | P7-A addendum B1–B2; Bowles et al. 2024; Cerezo et al. 2025 |
| P7-3 | Decisive first experiment (cheapest, most informative): compare the QMSE feature kernel against a **matched classical kernel on the identical hybrid Coulomb-adjacency features** (RBF/cosine). Parity ⇒ report parity and proceed only for the chirality question | Turns the audit's "claim ceiling" into a runnable gate |
| P7-4 | Pin the upstream implementation: the reference code for Boy et al. is public (`stfc/quantum-molecular-encodings`). Run their published benchmarks (state-phase classification, boiling-point regression) as a **regression test of the local port** before any ANP claim | Separates "our encoding is broken" from "QMSE is limited" — currently indistinguishable |
| P7-5 | Replace 8-atom SMILES slicing with an explicit, fidelity-checked reduction; report the fidelity `\|⟨ψ_full\|ψ_contracted⟩\|²` (or kernel-matrix agreement) on molecules small enough for the uncontracted reference, and the decay with the number of contracted rings | P7-A §3.2 + addendum B5; `PH-QMSE` needs its own fidelity proof, not an appeal to Boy et al. |
| P7-6 | Chirality: keep the `SO(3)`-invariant parity-odd volume, but prove invariance numerically (sign flip under reflection, invariance under rotation) on known enantiomer pairs, and include a **classical 3D chirality baseline** | Otherwise a "quantum chirality advantage" is unfalsifiable |
| P7-7 | Kernel diagnostics before AUC: report kernel-target alignment, effective dimension, off-diagonal variance scaling with `n ∈ {8, 12, 16, 20}`, and a shot/circuit cost table for the PQK-vs-fidelity comparison | P7-A Novelty 2; concentration is a *diagnosable* property |
| P7-8 | Provenance recovery as a gated deliverable: re-commit the five scripts + three result dirs, hash the benchmark CSVs into the manifest, fix the raw `Δ`, generate or drop `fig6_phased_results`, and add a CI LaTeX build | Ledger #18 (all confirmed) |
| P7-9 | Do not inherit RRS as ground truth (§3.5). Either use external experimental fold-shift data, or frame Tier B/C as *estimand-divergence* studies | Prevents building on a contested label |

---

## 7. Revised acceptance gates (replace prose gates with executable ones)

| Gate | Executable criterion |
|---|---|
| G-PROV | Every claim's evidence path resolves and its sha256 matches at the audit commit; no `file:///` absolute paths; `git status --porcelain` empty at capture |
| G-CITE | Every citation resolves to a DOI/arXiv record fetched and dated in the ledger; zero "✅" without source + date |
| G-P1-ENRICH | Metric set pre-registered (BEDROC(20), EF@5%, bias-corrected EF) with scaffold-cluster CI, **and** a power/CI simulation fixing the number of actives |
| G-P1-RECEPTOR | No unintended co-crystal ligand in any PDBQT; for every PfCRT state, report max atom distance of residue 76 (and fraction inside) from the box centre |
| G-P1-SEP | Set overlap computed by stereo-aware InChIKey **and** Murcko scaffold against P2 cohorts; any overlap declared in both manuscripts |
| G-P2-CONV | Per-replicate block-average + autocorrelation presented; a pre-declared exclusion rule; "converged" or "not converged" stated per system |
| G-P2-CONTROL | Controls (pyrimethamine/cycloguanil vs WR99210; CQ/PPQ/verapamil) reproduce the published ordering before any lead is discussed |
| G-P2-BUDGET | Measured ns/day × planned ns × systems ≤ available wall-clock, written into the DAR |
| G-P5-LABEL | Label semantics and binarisation rule documented; experimental panel deduplicated and its scaffold overlap reported |
| G-P5-CP | Mondrian coverage reported per class **and** per OOD decile; ESS reported with a pre-declared floor; failure to meet it ⇒ claim withdrawn |
| G-P5-STAT | Inference only via scaffold-clustered resampling (or mixed effects); no seed-level hypothesis tests |
| G-P7-DEQ | Matched classical kernel on identical features run first; report parity honestly |
| G-P7-FID | Contraction fidelity reported on the largest molecule for which the uncontracted circuit is computable |
| G-P7-BUILD | `pdflatex` (or the project engine) exits 0 with 0 undefined references in CI |

---

## 8. How to reproduce the repository-side checks

```bash
cd /home/nanaengo/Malaria_codesV2

# 1. The two-arm DEKOIS result that refutes the MTX root cause
cat zenodo_package_P1/results/dekois_mtxstripped_20260909/summary.txt
grep -n "MTX-blockade\|not supported" zenodo_package_P1/P1_DATA_ANALYSIS_REPORT.md

# 2. The recorded grid geometry and the ~8.9 A MTX offset
sed -n '1,60p' zenodo_package_P1/scripts/p1_r24_dekois_mtxstripped.py

# 3. Corrected PfCRT receptor, cavity grid, and the WT->WT* NULL control
cat zenodo_package_P1/results/pfcrt_redock_v2grid_20260909/manifest.json
cat zenodo_package_P1/results/pfcrt_redock_v2grid_20260909/revision_summary.json

# 4. Ligand inventory of the structures the P1 audit names
python3 - <<'PY'
import json,urllib.request
for pdb in ("1j3i","1j3k"):
    d=json.load(urllib.request.urlopen(f"https://www.ebi.ac.uk/pdbe/api/pdb/entry/molecules/{pdb}"))
    print(pdb, sorted({c for e in d[pdb] for c in e.get("chem_comp_ids",[])}))
PY

# 5. Cross-project cohort identity (P7 "Set A" == P2 "Set C")
cut -d, -f2,8 Project7_Quantum_Molecular_Encoding_QML/data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv | head

# 6. P7 provenance and build defects
for f in scripts/p7_qmse_preprocess.py scripts/p7_phase_d_canonical.py scripts/p7_stereo_probe.py \
         scripts/p7_ibm_kernel_aer.py scripts/p7_generate_fig6.py; do
  printf '%-42s %s\n' "$f" "$([ -e Project7_Quantum_Molecular_Encoding_QML/$f ] && echo PRESENT || echo ABSENT)"
done
grep -n 'Δ' Project7_Quantum_Molecular_Encoding_QML/manuscript/sections/methods.tex
ls Project7_Quantum_Molecular_Encoding_QML/manuscript/figures/fig6_phased_results.pdf 2>&1
```

---

## 9. Limits of this meta-audit (things I did not check)

Stated explicitly per the practice recommended in §5.1:

- **Not re-verified**: Tibshirani et al. (NeurIPS 2019), Bodnar et al. (NeurIPS 2021), Podkopaev & Ramdas (2021), Barber et al. (2023), Havlíček et al. (*Nature* 2019), Huang et al. (*Science* 2022), Gapsys et al. (*Chem. Sci.* 2020), Smallbone/Wicht PfCRT mechanism papers, and the P5-A/P7-A claims about internal AUC values. They are plausible and consistent with my knowledge, but that is not verification.
- **Not re-derived**: the P2 MM-GBSA spreads (7.75 kcal/mol; RRS up to 121.4%), the 87.5% divergence denominator, the P1 class counts, and the P5 seed-level p-values. These were taken from the documents/DARs as reported.
- **Not re-run**: any docking, MD, FEP, GNN, conformal or quantum pipeline. No claim here is a reproduction; the QML circuit defects are assessed from the code shown in the audit, not from my own reading of `p7_qmse_hybrid.py`.
- **Search-based verdicts are existence tests only** (#19–#23): "not locatable in two searches" is a reason not to cite, not proof of fabrication.
- **No judgement on publication merit**: nothing here recommends accept/reject at any venue, and no venue policy was consulted for this pass.

---

## 10. The "wow" factor — cross-project view (added in rev 2.1)

Each of the four documents now carries its own referee-facing section naming the single contribution that could make a referee or editor say *waouh*, with the evidence status of every number it quotes. They are deliberately of four **different kinds**, so the four papers do not cannibalise one another:

| Project | The "wow" in one line | Where | New evidence required |
|---|---|---|---|
| **P1** | Every resistance score is quoted against a **measured null band**, and the failing benchmark is shipped as a two-arm, one-variable experiment that reproduces the published baseline in its control arm | P1-A §7 | PfDHFR `NULL` control (≈ 5 dockings); per-target quantiles; pre-registered BEDROC/`EF@5 %` |
| **P2** | The **sign** of the resistance ratio becomes the hypothesis: `RRS > 100 %` at the vacuolar transporter is reframed as an *efflux-versus-occlusion* discriminator, tested with an observable the docking estimator does not share (pore hydration, residue-76 barrier, pH 5.2/7.4) | P2-A §6 | analysis of the **already-running** triplicate/pH daemon; classifier frozen on approved antimalarials first |
| **P5** | The fingerprint-versus-GNN gap is shown to be **partly a property of the label oracle** (measured alignment index), and out-of-distribution triage gets a finite-sample **false-discovery-rate guarantee** instead of hand-tuned thresholds | P5-A §6 | fingerprint-parameter sweep; dual-oracle panel; `CW-GIN` ablation at matched capacity and search budget |
| **P7** | A **refutation-ready quantum encoder**: its invariances are proved numerically before any ML claim, the published reference implementation is reproduced as a regression test, and the parity outcome that would end the programme is pre-registered | P7-A §8 | probe in CI (already passing); port regression; the R1 matched-classical-kernel rung |

**What is already measured rather than proposed.** The P7 probe (`Project7_Quantum_Molecular_Encoding_QML/scripts/p7_chirality_fingerprint_probe.py`, sha256 `565abd0b…`, RDKit 2026.03.4, read-only, exit 0) was added in rev 2.1 and upgrades P7-A §3.1 from a code-reading inference to a measurement: the raw chiral tag changed in **22 of 71** equivalent-SMILES variants (artemisinin **15/20**) while the CIP label was preserved in **71/71**; and a default Morgan fingerprint returns Tanimoto **1.0000** for enantiomer pairs where `includeChirality=True` returns **0.7333 / 0.5833**. P5-A §6.2 cites the same probe, because it is also the reason a stereo-aware classical baseline is mandatory there.

**Source confirmations made in rev 2.1 (beyond the "wow" sections).** P7-A §3.1, §4.1 and §4.2 are now verified against the tree at the pinned commit rather than from quoted excerpts: the parity-based R/S mapping sits at `scripts/qmse_lib/processing.py:33/44` and is turned into a diagonal sign flip at `scripts/qmse_lib/matrix.py:151/154–161`; the same bug is re-implemented in the project's own `test_qmse_stereochemistry.py:12–30`, so the regression test asserts the wrong invariant; the encoding loop (`scripts/p7_qmse_hybrid.py:156–163`) never reads the matrix diagonal; and the IBM kernel really does build a `2n+1`-qubit SWAP-test circuit (`scripts/p7_ibm_quantum_kernel_svm.py:226–276`). One rev 2 headline was corrected as a result: “no entanglement is generated” is too strong — the ansatz adds a fixed-strength `0.1` entangler between adjacent wires, molecularly uninformative but not absent.

**Consistency rule for the four "wow" sections.** None of them introduces a claim that the audits retract: no enrichment target, no quantum advantage, no universal GNN inferiority, no transport mechanism from a binding calculation, no `±1.0 kcal/mol` FEP precision, and no exact coverage target. Each section states what would **falsify** it, and each keeps the programme-level gates of §7 in force.
