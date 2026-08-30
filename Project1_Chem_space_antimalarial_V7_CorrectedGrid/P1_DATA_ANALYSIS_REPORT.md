# P1 — Data Analysis Report (canonical)

**Project**: Project 1 — Chem-space antimalarial / polypharmacology-oriented RRS framework
**Canonical directory**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/`
**Manuscript target**: *J. Chem. Inf. Model.* (JCIM, ACS)
**Author**: Myke Vital Sao Temgoua
**Last refreshed**: 2026-08-29
**Status**: submission-ready package (`INTERNAL_WORK_AUTHORIZED`), awaiting author Paragon Plus deposit

> **Canonical scope rule.** This is the only P1 DAR. All P1-related analyses (V4–V7
> cohort, evidence, figures, tables, scripts) are recorded here. The legacy P1 V5
> results-only snapshot was moved to `_archives/P1_V5_CorrectedGrid_archived_20260829/`
> on 2026-08-29 and remains available for traceability. Earlier V4 results live in
> `Project1_Chem_space_antimalarial_V4_CorrectedGrid/` (not archived — still
> cited by V7 chemical-space-coverage provenance; do not delete).

---

## 1. Executive summary

P1 is a purely computational framework that asks whether **target breadth** and
**mutation resilience** can be evaluated as **distinct, complementary properties**
when prioritising antimalarial chemotypes. The headline deliverables are:

1. A 17-member polypharmacology-oriented Set-C cohort, derived from
   \num{396} African natural products and \num{454} synthetic antimalarials
   (merged chemical space: \num{65856} molecules, \num{19913} computationally
   prioritised synthesizable leads).
2. A per-target resistance-resilience score (**RRS**) for PfDHFR (4 mutant
   alleles: N51I, C59R, S108N, I164L) and PfCRT (2 mutant alleles: K76T, K76A),
   defined so that non-binding wild-type targets are excluded from the
   denominator.
3. A dual-priority table combining RRS, ACSI (PNS/ACSI/ADMET) and
   AutoDock-Vina scores for the four anchor targets PfDHFR (7F3Y), PfCRT (6UKJ),
   PfClpP (2F6I), PfATP4 (9N10).
4. RRS-class distribution for the 17 cohort: **6 A* / 5 B / 5 C / 1 D**
   (RRS span \numrange{68.2}{111.7}).
5. Cross-metric associations: **PNS--RRS ρ = -0.559** (p ≈ 0.02, *not*
   significant after Bonferroni multiplicity correction); ACSI--RRS ρ = -0.132
   (n.s.); RRS--wild-type-score ρ = -0.433.
6. A 25-page main PDF + 17-page Supporting Information PDF, compiled with
   0 errors and 0 undefined references, packaged in `submission_ACS_P1V7/`
   with manifest SHA-256, cover letter, and graphics.

The 17×4 Vina pose panel passed the composite biological gate per target
(catalytic triad PfClpP/2F6I, Y01 cavity PfCRT/6UKJ, folate pocket PfDHFR/7F3Y,
conserved P-type ATPase catalytic machinery PfATP4/9N10). Docking-protocol
validation is documented in the manuscript (redocking 5/5 RMSD < 2.0 Å,
MMV ROC-AUC 0.924–1.000, DEKOIS 0.45 [0.37–0.53] honest-negative).

**Boundary statement.** The framework defines testable hypotheses about
chemotype breadth and mutation resilience; it does **not** establish potency,
target engagement, or resistance circumvention. All numerical claims are
internally audited and traceable to source CSVs (per
`P1_DEVELOPMENT_PHASE.json`, 10/08/2026 author decision: option A —
internal work authorised; no formal third-party review required before
submission).

---

## 2. Authorisation register (P1_DEVELOPMENT_PHASE.json + v7_review_register.json)

| Field | Value |
|---|---|
| `phase` | `PRE_SUBMISSION_DEVELOPMENT` |
| `development_execution_authorized` | `true` |
| `exploratory_internal_work_enabled` | `true` |
| `scientific_qc_enabled` | `true` |
| `editorial_submission_restrictions_active` | `false` |
| `automatic_post_submission_switch` | `false` |
| `decision_date_utc` | `2026-08-09T00:00:00Z` |
| `author_decision` (register) | `LIFT_PENDING_INDEPENDENT_REVIEW` (2026-08-10) |
| `accepted_for_full_run` | `false` (truthful provenance; not an execution block) |
| `target_decisions` | PfDHFR/PfCRT/PfClpP/PfATP4 → `AUTHOR_ACCEPTED_INTERNAL` |
| `reactivation_rule` | Dormant until author explicitly confirms submission **and** explicitly requests reactivation of submission/review restrictions |

**Implication for downstream agents.** The register's `INTERNAL_WORK_AUTHORIZED`
status permits scientific development, figure generation, and DAR updates
without further escalation. Promoting a claim to "third-party accepted" or
editing the register to simulate external acceptance is **prohibited**.

---

## 3. Headline numbers

| Metric | Value | Source |
|---|---|---|
| Merged chemical space | \num{65856} | V4 hybrid library (`p1_scaffold_tanimoto.csv`, sha256 `3573b33d…`) |
| African natural products | \num{396} | V4 source |
| Synthetic antimalarials | \num{454} | V4 source |
| Computationally prioritised leads | \num{19913} | V5/V6 selection |
| Set-C polypharmacology cohort | 17 (PP-01…PP-17) | `results/v7_candidate_manifest.csv` (sha256 `37b203fa…`) |
| Docking pairs (17×4) | 68 (all PASS geometric gate) | `results/derived/v7_integrated_candidate_metrics.csv` |
| Vina score range | \qtyrange{-7.91}{-4.63}{\kilo\calorie\per\mole} | main §Results |
| RRS class A* / B / C / D | 6 / 5 / 5 / 1 | `awk -F, '$6' integrated_candidate_metrics.csv` |
| RRS numeric span | \numrange{68.2}{111.7} | main §Results |
| Per-target RRS alleles | PfDHFR: N51I, C59R, S108N, I164L (4) ; PfCRT: K76T, K76A (2) | SM §S7 |
| PNS--RRS ρ | \num{-0.559} (p ≈ 0.02, *n.s. after Bonferroni*) | main + SM §S8 |
| ACSI--RRS ρ | \num{-0.132} (n.s.) | SM §S8 |
| RRS--wild-type-score ρ | \num{-0.433} | SM §S8 |
| Redocking RMSD | 5/5 < 2.0 Å | SM §S12 |
| MMV ROC-AUC (per target) | 0.924 – 1.000 | SM §S12 |
| DEKOIS honest-negative ROC-AUC | 0.45 [0.37 – 0.53] | SM §S12 |

The full RRS-class table, dual-priority matrix and cross-metric scatter are
rendered in the main manuscript (compiled PDF) and Supporting Information
sections S7–S9.

---

## 4. Canonical directory inventory

```
Project1_Chem_space_antimalarial_V7_CorrectedGrid/     ← canonical (this report)
├── AGENTS.md                                  (root, project-level)
├── P1_DEVELOPMENT_PHASE.json                  (authorisation register, schema v3)
├── README.md
├── GIT_PUSH_METHODS_CORRECTION_20260111.md
├── GIT_PUSH_SUMMARY_20260111.md
├── ORCID_COMPLETE_20260111.md
├── ORCID_SUBMISSION_INSTRUCTIONS.md
├── project-tracking.md
├── P1_V4_RESOURCE_INVENTORY.md
├── manuscript/                                (LaTeX source, bibliography, tables)
│   ├── P1_V7_Integrated_Polypharmacology_RRS.tex        (246 lines)
│   ├── P1_V7_Integrated_Polypharmacology_RRS_SM.tex     (224 lines)
│   ├── Cover_Letter_P1_V7.tex
│   ├── acs-P1_V7_Integrated_Polypharmacology_RRS.bib
│   ├── acs-P1_V7_Integrated_Polypharmacology_RRS_SM.bib
│   ├── Sao_Chim_Space.bib                    (~270 entries, journal names verified)
│   ├── achemso.bst
│   ├── SUBMISSION_MANIFEST.md                (status note)
│   ├── Graphics/
│   └── tables/
│       ├── sm_table_admet_summary.tex
│       ├── sm_table_druglikeness.tex
│       ├── sm_table_enrichment_validation.tex
│       ├── sm_table_physicochemical.tex
│       ├── sm_table_redocking_validation.tex
│       └── sm_table_validation_datasets.tex
├── scripts/                                  (10 scripts, all v7_*)
│   ├── v7_apply_review.py
│   ├── v7_generate_acs_toc.py
│   ├── v7_generate_admet_summary_table.py
│   ├── v7_generate_chemical_space_coverage.py
│   ├── v7_generate_druglikeness_table.py
│   ├── v7_generate_integrated_data_figures.py
│   ├── v7_generate_physicochemical_table.py
│   ├── v7_review_gate.py
│   ├── v7_review_payload.py
│   └── v7_validate_evidence.py
├── results/
│   ├── v7_candidate_manifest.csv             (17 rows + header; sha256 37b203fa…)
│   ├── v7_review_register.json                (v2 register)
│   ├── derived/                              (CSV tables referenced by manuscript)
│   │   ├── v7_druglikeness_compliance.csv         (17 rows + header)
│   │   ├── v7_integrated_candidate_metrics.csv    (17 rows + header; canonical RRS table)
│   │   ├── v7_physicochemical_properties.csv      (17 rows + header)
│   │   └── v7_integrated_data_figures_provenance.json
│   ├── exploratory/
│   │   ├── derived/v7_integrated_candidate_metrics.csv
│   │   ├── derived/v7_integrated_data_figures_provenance.json
│   │   └── figures/                            (5 PDF/PNG figure triples)
│   ├── figures/                              (4 figure triples: chemical space, RRS mutation, exploratory, targetwise)
│   │   ├── p1_v7_chemical_space_coverage.{pdf,png}        + _provenance.json
│   │   ├── p1_v7_exploratory_metric_relationships.{pdf,png}
│   │   ├── p1_v7_rrs_mutation_profiles.{pdf,png}
│   │   └── p1_v7_targetwise_profile_summary.{pdf,png}
│   └── validation/
│       ├── v7_integrity_audit.json            (0 errors, AUDIT_WARN_REVIEW_REQUIRED)
│       └── v7_review_dossier.md               (4 targets EVIDENCE_COMPLETE_AWAITING_REVIEW)
└── submission_ACS_P1V7/                      (Paragon Plus package, 31 files, manifest SHA-256)
    ├── P1_V7_Integrated_Polypharmacology_RRS.pdf         (25 p., 449 KB, 0 errors)
    ├── P1_V7_Integrated_Polypharmacology_RRS_SM.pdf      (17 p., 524 KB, 0 errors)
    ├── P1_V7_main.pdf                                    (alias, 451 KB)
    ├── P1_V7_SM.pdf                                      (alias, 525 KB)
    ├── Supporting_Information.pdf                        (alias, 525 KB)
    ├── Cover_Letter_P1_V7.{tex,pdf}                      (1 p., 77 KB)
    ├── P1_V7_Integrated_Polypharmacology_RRS.{tex,aux,bbl,blg,log,out}
    ├── P1_V7_Integrated_Polypharmacology_RRS_SM.{tex,aux,bbl,blg,log,out}
    ├── P1_V7_main.{tex,aux,bbl,blg,log,out}
    ├── P1_V7_SM.{tex,aux,bbl,blg,log,out}
    ├── acs-P1_V7_main.bib / acs-P1_V7_SM.bib / Sao_Chim_Space.bib
    ├── Figure_2_rrs_mutation_profiles.pdf
    ├── Figure_3_exploratory_metric_relationships.pdf
    ├── Figure_S_chemical_space_coverage.pdf
    ├── Figure_S_targetwise_profile_summary.pdf
    ├── Graphics/                                  (TIF + PDF versions of TOC graphic)
    │   ├── p1_v7_toc_graphic.pdf
    │   ├── p1_v7_toc_graphic_ACS.tiff
    │   └── p1_v7_toc_graphic_ACS_1200dpi.tiff
    ├── tables/                                   (6 SM tables)
    ├── PARAGON_PLUS_CHECKLIST.md                 (12-08-2026 v1.1)
    ├── README_SUBMISSION_ACS.md
    ├── SUBMISSION_MANIFEST.md                    (canonical)
    └── SUBMISSION_MANIFEST_V7.md
```

---

## 5. Source artifacts — every CSVV/JSON referenced by the manuscript

All artifacts are 17-row + header (or single-record) deterministic outputs of
`scripts/v7_*` (see §6 for the runbook). The four CSVs that the main
manuscript and SM depend on are:

| Path (relative to canonical dir) | Rows | sha256 (file:line of provenance) | Used in |
|---|---:|---|---|
| `results/v7_candidate_manifest.csv` | 17 + h | `37b203fa…` (`v7_integrity_audit.json`) | main §2, SM §S1 |
| `results/derived/v7_integrated_candidate_metrics.csv` | 17 + h | (regenerated by `v7_generate_integrated_data_figures.py`) | main §3, SM §S7–S9 |
| `results/derived/v7_physicochemical_properties.csv` | 17 + h | (regenerated) | SM §S4 |
| `results/derived/v7_druglikeness_compliance.csv` | 17 + h | (regenerated) | SM §S5 |
| `results/validation/v7_integrity_audit.json` | n/a | (regenerated by `v7_validate_evidence.py`) | SM §S1 |

The 5 figure triples (each PDF + PNG + optional provenance JSON) cover the
main figures and SM S2 (chemical-space coverage), S3 (RRS mutation profiles),
S8 (exploratory metric relationships), and a targetwise profile summary.

---

## 6. Reproducibility runbook

The V7 pipeline is deterministic (numpy + RDKit + Vina already executed; the
V7 scripts only regenerate CSVs/figures from the manifest + external docking
files). Re-execute from the canonical directory:

```bash
cd Project1_Chem_space_antimalarial_V7_CorrectedGrid

# 1. Re-audit evidence integrity (writes results/validation/v7_integrity_audit.json)
python3 scripts/v7_validate_evidence.py

# 2. Regenerate the 3 CSVs (druglikeness, physicochemical, integrated metrics)
python3 scripts/v7_generate_druglikeness_table.py
python3 scripts/v7_generate_physicochemical_table.py
python3 scripts/v7_generate_integrated_data_figures.py

# 3. Regenerate the SM tables
python3 scripts/v7_generate_admet_summary_table.py
python3 scripts/v7_generate_chemical_space_coverage.py

# 4. Regenerate the 4 figure triples
python3 scripts/v7_generate_integrated_data_figures.py    # also writes 2 figures

# 5. Build the submission package (PDFs already in submission_ACS_P1V7/)
cd submission_ACS_P1V7
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex   # 25 p.
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex # 17 p.
pdflatex Cover_Letter_P1_V7.tex                       # 1 p.
```

Re-running `v7_validate_evidence.py` should reproduce `accepted_for_full_run=false`
with **0 errors** and the same warning set (`AUDIT_WARN_REVIEW_REQUIRED`,
`INDEPENDENT_REVIEW_PENDING`, `RRS_V5_JOIN_VERIFIED_BY_CANONICAL_SMILES`).

---

## 7. Manuscript structure (compiled PDF layout)

### 7.1 Main manuscript (25 p., `P1_V7_Integrated_Polypharmacology_RRS.tex`)

- §1 Introduction (L46) — RRS as distinct, complementary property to breadth
- §2 Materials and Methods (L55) — chemical space, docking, RRS, statistical audit
- §3 Results (L86) — 17×4 docking panel, RRS classes, cross-metric analysis
- §4 Discussion (L191) — hypotheses, evidence boundaries, limitations
- §5 Conclusion (L221) — testable hypotheses, not potency claims
- Associated Content, Author Contributions, Notes, Data Availability, Acknowledgments

### 7.2 Supporting Information (17 p., `P1_V7_Integrated_Polypharmacology_RRS_SM.tex`)

- S1 Cohort and evidence boundaries
- S2 Chemical-space coverage and target-anchored docking
- S3 Target-anchored docking matrix (68 pose panel)
- S4 Physicochemical properties of Set-C candidates
- S5 Drug-likeness compliance
- S6 ADMET profile summary
- S7 RRS definition and class summary
- S8 Exploratory cross-metric analysis
- S9 Target evidence classes and limitations
- S10 Multi-parameter optimisation framework (MPO, *new in V7*)
- S11 Reproducibility and availability
- S12 Docking validation and protocol assessment (redocking, MMV, DEKOIS)

### 7.3 Submission package integrity

- `submission_ACS_P1V7/SUBMISSION_MANIFEST.md` — canonical manifest with SHA-256
  inventory (excludes itself to avoid self-reference). 31 files.
- `submission_ACS_P1V7/PARAGON_PLUS_CHECKLIST.md` v1.1 (12-08-2026) — step-by-step
  ACS Paragon Plus checklist for JCIM deposit.
- `submission_ACS_P1V7/README_SUBMISSION_ACS.md` — auxiliary instructions.

---

## 8. Validation gates (passed)

| Gate | Status | Evidence |
|---|---|---|
| Manifest 17×4 join via canonical SMILES | ✅ | `v7_integrity_audit.json` (0 errors, 1 warning) |
| 17-row dual-priority table numerics | ✅ | SM §S7 + audit log 10/08/2026 |
| 4 cross-metric correlations | ✅ | main §3, SM §S8 |
| 68 docking pairs (geometric pose quality) | ✅ | `v7_integrated_candidate_metrics.csv` |
| Per-target biological anchor | ✅ | `v7_review_dossier.md` (4 × EVIDENCE_COMPLETE_AWAITING_REVIEW) |
| Redocking 5/5 RMSD < 2.0 Å | ✅ | SM §S12 |
| MMV ROC-AUC ≥ 0.924 per target | ✅ | SM §S12 |
| DEKOIS honest-negative ≈ 0.45 | ✅ | SM §S12 |
| LaTeX compile 0 errors / 0 undefined refs (main + SM) | ✅ | `.log` files in `submission_ACS_P1V7/` |
| Authorisation register consistent | ✅ | `v7_review_register.json` status `INTERNAL_WORK_AUTHORIZED` |
| Independent third-party review | ❌ **not required** (option A, 10/08/2026) | author decision, register §author_decision |

---

## 9. Known limitations and boundary statements

1. **Computational only.** No potency, target engagement, or resistance
   circumvention is established. SM §S9 records the per-target evidence
   classes (catalytic triad PfClpP/2F6I, Y01 cavity PfCRT/6UKJ membrane
   mimetic, folate pocket PfDHFR/7F3Y, conserved P-type ATPase catalytic
   machinery PfATP4/9N10).
2. **RRS wild-type exclusion.** Per-target RRS denominators exclude non-binding
   wild-type targets, so RRS is **not** a normalised survival probability
   relative to wild type; it is a mutation-resilience index anchored to the
   binding-competent cohort.
3. **Multiplicity.** Cross-metric associations are reported with Bonferroni
   correction; only the unadjusted PNS--RRS ρ = -0.559 is suggestive.
4. **No third-party review.** Register truthful provenance: `accepted_for_full_run`
   remains `false`; the `INTERNAL_WORK_AUTHORIZED` status is the author's
   own scientific-responsibility attestation, not external acceptance.
5. **Cohort size.** n=17 Set-C polypharmacology cohort; results are
   hypothesis-generating, not population-level conclusions.
6. **PNS imputation sensitivity and ACSI weight sensitivity** are documented
   in SM §S8; both are stable to the explored ranges but are noted as
   methodological limitations in the manuscript.

---

## 10. Repository hygiene

| Item | Status |
|---|---|
| P1 V5 results-only directory | archived to `_archives/P1_V5_CorrectedGrid_archived_20260829/` (4 vina pdbqt + 2 receptor pdb, 2.3 MB) on 2026-08-29 |
| P1 V4 chemical-space source | retained at `Project1_Chem_space_antimalarial_V4_CorrectedGrid/` (sha256 `3573b33d…` referenced by V7 chemical-space coverage provenance) — do not delete |
| P1 V6 | merged into V7 (no separate `V6_CorrectedGrid` directory) |
| P1 V7 canonical location | `Project1_Chem_space_antimalarial_V7_CorrectedGrid/` (this report) |
| Duplicates inside canonical dir | `manuscript/SUBMISSION_MANIFEST.md` (status note) vs `submission_ACS_P1V7/SUBMISSION_MANIFEST.md` (canonical SHA-256 manifest). The latter is authoritative. |
| Untracked / oversized artifacts | none for P1 V7; `submission_ACS_P1V7/Graphics/*.tiff` are present but not git-tracked due to size |

---

## 11. Cross-references

- **BMAD** (`BMAD_Q1_DATA_ANALYSIS_REPORT.md`) — Q1 cross-project synthesis;
  the P1 row in §6 reports headline metrics from this DAR.
- **P2 DAR** (`Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md`)
  — the Set-C 17-member cohort originates in P2 (`c_pns_ranking.csv` →
  `v7_candidate_manifest.csv` via canonical-SMILES join).
- **P5 DAR** (`Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md`)
  — downstream polypharmacology modelling; cohort = Set-C + P5 GNN/Transformer
  training set.
- **`docs/CENTRAL_QUESTIONS_PROJECTS.md`** — cross-project scientific questions;
  P1 Q2 (RRS-resilience reasoning) is the central scientific hypothesis that
  this manuscript operationalises.
- **`docs/P1_P7_INTEGRATION_ROADMAP.md`** (root) — long-term integration plan
  between P1 chemical-space cohort and P7 quantum molecular encoding.

---

## 12. Outstanding work and next actions

1. **Author Paragon Plus deposit.** Checklist is in
   `submission_ACS_P1V7/PARAGON_PLUS_CHECKLIST.md` v1.1; the only blockers are
   author-controlled (ORCID records, metadata confirmation, final read-through).
2. **Independent structural review (optional, post-submission).** Register
   records that the author has elected option A (no pre-submission
   independent review required for purely computational JCIM submission).
3. **P5 audit #2 (`p5_nn_tanimoto_deciles.py` + `.sbatch`)** — referenced in
   P5 DAR; untracked. Deferred to a P5-focused session.
4. **BMAD update.** The next BMAD refresh should re-pull P1 headline numbers
   from this DAR; the current BMAD §6 P1 row is consistent (verified 2026-08-29).

---

*End of P1 Data Analysis Report — canonical, exhaustive, 2026-08-29.*
