# BMAD Q1 Data Analysis Report — active summary

**Scope:** P1–P3 only. P4 and P5 have dedicated DARs.
**Updated:** 17 August 2026
**Long-form history:** `docs/archive/md_full_20260812/BMAD_Q1_DATA_ANALYSIS_REPORT.md`

## 1. Executive status

| Project | Current status | Submission-relevant conclusion |
|---|---|---|
| **P1** | V7 is the submission-oriented workspace (JCIM); V6/V4/V5 provide corrected evidence and remediation layers | Chemical-space novelty, target-wise docking, and computational RRS/polypharmacology are reportable only within their stated provenance boundaries |
| **P2** | Canonical 17-member Set-C cohort and docking-RRS/ACSI/PNS analysis complete; Set-C MD 13/16 production trajectories complete | Docking-RRS is canonical; Set-C MD-RRS not yet computed (pending 3 remaining trajectories + QC) |
| **P3** | Canonical classical, hybrid, QKS, TNE/TDA, and external-validation analyses complete | Quantum-inspired descriptors are complementary; no quantum advantage over RBF or ECFP4 is claimed |

## 2. P1 — chemical space, docking, and RRS/polypharmacology

### Canonical findings

- The P1 chemical-space library contains **65,856 molecules**; **92.6%** are ECFP4-unreachable from the seed space and scaffold recovery is **69.3%**.
- The V4 2F6I/PfClpP remediation accounts for all **484** centroid attempts: **458 PASS**, **1 PENDING**, **15 protocol exclusions** for unsupported boron chemistry, **5 DOCKED_GATE_FAILED**, and **5 EMBED_FAILURE**. This is a provenance/remediation result, not experimental validation.
- V5 contains **68/68 finite target-wise Vina records** for 17 candidates × 4 targets. Scores remain target-specific and are not averaged as a common affinity scale.
- The V5 mutant pilot contains **136/136 finite docking scores** for PfDHFR/PfCRT. It is exploratory and must not replace the canonical P2 RRS table.
- V7 integrates the exact 17-member cohort by canonical SMILES and supersedes V6 (validated 11/08/2026: DEKOIS/MMV/redocking tables, physicochemical characterization, ORCID ×5 collected). The submission package is numerically audited; independent structural review remains a provenance item, not an experimental result.

### Evidence boundaries

- Docking scores support prioritisation hypotheses, not measured binding or activity.
- RRS is per target and excludes non-binding WT denominators (`|ΔG_WT| < 5.0 kcal mol⁻¹`).
- V5 and P2 RRS layers use different receptor/preparation/execution provenance and are not interchangeable.
- No IC₅₀/EC₅₀, target engagement, resistance circumvention, or biological polypharmacology is claimed without experimental evidence.

## 3. P2 — canonical RRS/polypharmacology source layer

The canonical Set-C cohort contains **17 polypharmacology-oriented candidates** and **136 WT/mutant docking systems**. Per-target RRS classification is:

| Class | Count |
|---|---:|
| A* | 6 |
| B | 5 |
| C | 5 |
| D | 1 |

Canonical cross-metric results (n=17) are: PNS–RRS ρ=−0.559, p=0.020 (not significant after Bonferroni α=0.017); ACSI–RRS ρ=−0.132, p=0.613; RRS–ΔG_WT ρ=−0.433, p=0.082. ACSI mean is **0.543**, with **2/17 (11.8%)** above 0.70. These are docking-derived computational relationships.

Historical parent-lead MD remains separate: only PfCRT–214 has an interpretable MM-GBSA estimate (−18.25 ± 0.40 kcal mol⁻¹); dissociated systems and the 4GM2/PfClpR-labelled system are not promoted as PfClpP validation.

### Live Set-C execution checkpoint — 17 August 2026

The bounded **16-system pilot** (PP-01/PP-02 × PfDHFR/PfCRT mutation states) is prepared under the PI-approved OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P policy deviation. Production array **15320** (`%1` throttle on single A4000 GPU) has completed **13/16 systems** with valid production trajectories (production.xtc, production.cpt, production.log):

| Batch | Tasks | Systems | Status | Trajectory size |
|---|---|---|---|---:|
| PP-01 DhFR × 5 | 0–4 | PP-01_PfDHFR_{WT,N51I,C59R,S108N,I164L} | ✅ COMPLETED | ~1.2 GB each |
| PP-01 CRT × 3 | 5–7 | PP-01_PfCRT_{WT,K76T,K76A} | ✅ COMPLETED | ~854 MB each |
| PP-02 DhFR × 4 | 8–11 | PP-02_PfDHFR_{WT,N51I,C59R,S108N} | ✅ COMPLETED | ~1.2 GB each |
| PP-02 DhFR I164L | 12 | PP-02_PfDHFR_I164L | 🟢 RUNNING (ETA ~22:55 UTC) | writing |
| PP-02 CRT × 3 | 13–15 | PP-02_PfCRT_{WT,K76T,K76A} | ⏳ PENDING (queue) | — |

All 13 completed systems have `PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC` status. GROMACS runs at 310.15 K with GPU flags `-nb gpu -pme gpu -bonded cpu -update cpu`. No fatal, LINCS, or NaN indicators in any completed log. Tasks 13–15 will launch sequentially after task 12 finishes; estimated full completion: **~Aug 18, 17:00 UTC**. MD-RRS remains **`NOT_COMPUTED`** pending completion of all 16 QC passes. Historical 15106/15111/15117/15254/15259/15260/15270/15274 identifiers are superseded.

### Set-C production history — superseded gates (13 August 2026)

The 16-system equilibration array `15288` completed all tasks with `rc=0` in the **canonical preparation root** `results/md_systems/set_c_preparation_20260812_v1/` — all 16 systems produced `npt.gro` and `npt.cpt` there (verified: 16/16 present). The legacy root `results/md_systems/set_c/` contains only 1 `npt.gro` (PP-01_PfDHFR_I164L) and is non-canonical; the production workflow reads equilibrated inputs exclusively from the preparation root. Multiple intermediate production attempts (`15308`, `15313`, `15317`) were stopped due to workflow defects (missing topology staging, `continuation`/`gen_vel` conflict, `mdrun -seed` rejection, ns-to-step conversion error). All defects were corrected and validated. The final production array `15320` passed the `15319` gate with 16/16 preflight and is now **13/16 complete** (see checkpoint above). Historical gate identifiers are retained as non-canonical scheduler provenance.

### P2 storage and provenance cleanup audit — 13 August 2026

### Safe cleanup checkpoint — 13 August 2026

The six failed production run directories from `15308`, `15313`, and `15317` were removed under the approved safe-cleanup scope; their logs and manifests remain preserved. A second cleanup removed only **1,087 editor/GROMACS autosave or backup files** (`#...#`, `.bak`, `.backup`, `*~`; approximately **13.7 GB**) outside the active `15320` run, plus ten untracked Antechamber/SQM/energy temporary files. These artifacts were not referenced by the active workflow and do not contain canonical results.

On 17 August 2026, a comprehensive cleanup removed: (i) all non-canonical `set_c*` preparation/witness/gap-pilot/diagnostic directories (19 directories, ~11.5 GB), retaining only the canonical `set_c_preparation_20260812_v1` (19 GB); (ii) the `diagnostic_md_20260809/` directory (2.7 GB, 428 duplicate files — historical diagnostic launcher superseded); (iii) non-canonical `set_c_md` pilot/preflight/benchmark directories from superseded jobs (15308/15313/15317, ~56 MB); (iv) 40 non-canonical log files from stopped jobs; (v) misplaced trajectory files at project root and in `scripts/` (~4.7 GB); (vi) `HPC_ready/` directory (3.0 GB, old parent-MD packages); (vii) `models/aizynthfinder/` (754 MB, unreferenced); (viii) non-canonical P1 V4 remediation artifacts (65 MB); and (ix) LaTeX build artifacts (~274 MB). The active `15320` run, canonical preparation root, canonical historical parent-MD evidence (`MD_systems/`), runbooks, manifests, logs, and DARs remain protected. Project total is now 39 GB (down from 51 GB); disk usage is 63% (293/492 GB).

### P2 implementation decision — pilot MD-RRS and PlasmoDB annotation (12 August 2026)

The next MD-RRS implementation is explicitly a **two-candidate pilot**, not a 17-candidate validation: PP-01 and PP-02 × PfDHFR/PfCRT mutation states = **16 systems and 16 QC rows**. The full-cohort contract remains separately defined as 17 candidates × 8 states = 136 systems/rows and is not being silently replaced. Pilot outputs must use a distinct cohort identifier and output path (`P2_SET_C_MD_RRS_PILOT_PP01_PP02`; `md_rrs_pilot_PP01_PP02.csv`) and must never overwrite the canonical full-cohort output.

PlasmoDB/VEuPathDB stable 3D7 identifiers are added as target annotations only: PfDHFR `PF3D7_0417200`, PfCRT `PF3D7_0709000`, PfATP4 `PF3D7_1211900`, PfClpP `PF3D7_0307400`, and PfClpR `PF3D7_1436800`. This annotation documents target identity and mutation context; no PlasmoDB pathway-enrichment test is claimed because the study does not provide an independent multi-gene target set or an appropriate enrichment background. A dynamic pharmacophore occupancy analysis remains optional and cannot be reported before trajectory QC.

**Independent structural annotation branch — LigandExplorer (12 August 2026):** job `15272` ran the local LigandExplorer checkout with the GNN backend on CPU to annotate ligands present in the four accepted receptor structures (`2F6I`, `7F3Y`, `6UKJ`, `9N10`). `4GM2` was intentionally excluded because it is PfClpR rather than active PfClpP. The resolved LigandExplorer commit is `d47eea0d033bb2127ee6836445554881c59edc8e`. The process returned 0, but the fail-closed audit found valid ligand-box JSON artefacts for `7F3Y` (4) and `6UKJ` (2), and no ligand-box artefact for `2F6I` or `9N10`; the run is therefore `COMPLETED_PARTIAL_REQUIRES_MANUAL_REVIEW`, not a complete panel annotation. The output JSONs encode spatial ligand-box data and emitted category labels, not standalone calibrated classification probabilities, activity, or confidence estimates. This branch does not alter candidate selection, docking scores, docking-RRS, MD, or MD-RRS. The versioned runner is `Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_ligandexplorer_annotation.py`; the manual-review record is `results/ligandexplorer_annotation_20260812/annotation_manual_review.md`. No manuscript claim is promoted from this auxiliary result.

### P2 GitHub tool register and existing-use audit — 12 August 2026

The verified application register is maintained in `Project2_Polypharmacology_MD_ValidationV2607/P2_GITHUB_TOOL_REGISTER_20260812.md`. It records the distinction between installed software, executed workflows, and reportable results. GNINA is available as v1.3.2 (binary hash recorded in the P2 tool register), but the preserved ligand-438 attempt wrote an empty output file (0 bytes) and produced no reportable CNN score or pose. The generalized manuscript statement describing GNINA over the full 17 × 4 panel is therefore withdrawn until a complete non-empty output manifest is independently produced. PlasmoDB has already been used for stable target identifiers and mutation context (`results/plasmodb_target_annotation.csv`, Table S7), including the PfClpP/PfClpR identity boundary. A directly scripted WDK REST client has not been evidenced and is not required for the current four-target annotation. No pathway-enrichment analysis is performed or claimed. ProLIF and PLIP are the recommended next auxiliary tools, but only after QC-PASS trajectories or a predeclared static-pose subset, respectively; neither changes docking-RRS or authorizes incomplete MD-RRS promotion.

### P2 manuscript scientific revision checkpoint — 13 August 2026

The P2 manuscript was revised to present a scientific article centred on target-level resistance-aware prioritisation rather than an operational report. The Introduction and Discussion now distinguish docking-derived polypharmacology, PNS network weighting, ACSI chemical-space positioning, docking-RRS, trajectory stability, and MoA-level biological claims. Ryszkiewicz 2026, Trapotsi 2022, Sentinel 2025, and Blake 2025 are used as methodological context rather than as validation of the present predictions. The null correlation results are framed as absence of evidence in the sampled cohort, not as orthogonality, independence, or equivalence. The four-target rationale and the PfClpR/PfClpP identity boundary are explicit. The incomplete Set-C MD pilot remains excluded from the article; no MD-RRS is reported. Internal job identifiers, file-level failure narratives, and the unproductive Monte Carlo note were removed from the scientific prose. Main, Supporting Information, and cover letter recompiled successfully on 13 August 2026 with no fatal LaTeX errors or undefined references.

## 4. P3 — quantum-inspired representations

Canonical full-library results:

| Representation/model | AUC |
|---|---:|
| ECFP4 | 0.9475 ± 0.0045 |
| Hybrid RF | 0.8876 ± 0.0065 |
| TFP | 0.8759 |
| TNE | 0.7219 |

Removing QK reduces hybrid AUC by **0.040**; TFP contributes **0.014**; TNE is mildly negative in the ablation. QKS re-runs show quantum ≈ RBF at n=5,000 and n=19,849; no quantum advantage is claimed. External descriptor analyses retain the **351 TNE failures** as an explicit ITT/complete-case sensitivity issue rather than hiding them. The external QKS pilot (n=150) gives quantum **0.8385** versus RBF **0.8423**, p=0.374; this is an external replication of equivalence, not an advantage.

## 5. P3 external MoA extension — planned, not yet a canonical result

A separate P3/P5 extension is being implemented under `P5_LISH_MOA_EXTERNAL_V1`. LISH-MoA is a multi-label pharmacology benchmark (206 scored MoA labels), not an antimalarial activity panel. P3 may consume only the audited, structure-mapped drug-level artifact produced by the P5 preparation workflow; it must not alter the canonical P3 panel, splits, AUC tables, QKS conclusions, or manuscript headline.

The P3 external arm will compare ECFP4, TFP, TNE, and an explicitly labelled optional QKS analysis on the same mapped compounds. Mean column-wise log loss is primary, with macro/micro AUPRC and macro AUROC as secondary metrics. Splits must be grouped by `drug_id`, with scaffold-held-out sensitivity when structures are available.QKS remains separately bounded because its kernel cost is quadratic; `p3_lish_moa_qks_bounded.py` is available for a selected-label/cohort sensitivity analysis, but no such result is yet computed.
 Any unresolved structure mapping or descriptor failure is reported explicitly; no complete-case filtering may silently change the estimand. A public annotated mirror is now available for the data-access step (`pablormier/kaggle-lish-moa-annotated`; official mapping provenance `LISHarvard/moa_challenge`). It remains a mirror of the competition data, not a new biological validation source. Until its archive hash, extracted training rows, structure mapping, and all gates are available, this extension remains **planned / not computed** and cannot be cited as a P3 result.

## 6. Minimal provenance map

| Result layer | Source evidence | Status |
|---|---|---|
| P1 V5 target-wise Vina | `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/` | finite raw records; exploratory where labelled |
| P2 canonical RRS/ACSI/PNS | `Project2_Polypharmacology_MD_ValidationV2607/results/c_rrs_classification.csv`, `c_acsi_scores.csv`, `c_pns_ranking.csv` | canonical docking-derived |
| P2 Set-C production | `Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_preparation_20260812_v1/` | 13/16 production trajectories completed; MD-RRS NOT_COMPUTED |
| P3 external validation | `Project3_Quantum_Inspired_RepresentationsV2607/results/` | canonical/external sensitivity outputs |

## 6. Cross-project rules

1. Preserve canonical input, script, parameter, and hash provenance for every result.
2. Keep P1 Set A, P2 MD Set B, and P2 polypharm Set C disjoint.
3. Never convert docking-RRS into MD-RRS; MD-RRS requires complete trajectories and PASS QC.
4. Keep failed, pending, exploratory, and historical outputs visible but clearly labelled.
5. Do not update manuscript claims from an incomplete job.

## 7. Next actions

- **P1 (V7):** complete funding items and final author read-through for V7; package `submission_ACS_P1V7/` verified auto-contained (main 25 p. / SM 17 p. / cover 1 p., 0 undefined refs, 12/08/2026).
- **P2:** production `15320` is 13/16 complete (all PP-01 × 8 + PP-02 DhFR × 5 finished; PP-02_PfDHFR_I164L running; PP-02_PfCRT × 3 queued). ETA for full completion: ~Aug 18, 17:00 UTC. Next: run trajectory QC + MD-RRS wrapper only after all 16 trajectories pass declared QC contract. No MD-RRS claim permitted before complete PASS QC.
- **P3:** preserve the honest-negative external validation framing and complete repository deposit preparation.
- **All:** keep this summary short; place detailed job narratives and superseded decisions in the archive.
