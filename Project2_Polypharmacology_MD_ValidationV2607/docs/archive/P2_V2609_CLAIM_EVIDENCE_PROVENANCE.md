# P2 — Claim–Evidence–Provenance Matrix (Reconfiguration)

**Date:** 2026-09-10
**Scope:** Reconfigured P2 manuscript (estimand-divergence and computational-triage study for African antimalarial natural products)
**Canonical source:** `P2_DATA_ANALYSIS_REPORT.md`
**Upstream companion:** P1 V8 (`Project1_Chem_space_antimalarial_V7_CorrectedGrid/`)
**Policy:** No claim is promoted beyond the evidence level recorded in the DAR. P1-derived quantities are not independent P2 validation.

---

## 1. Evidence-level hierarchy (from reconfiguration plan §6)

| Level | Label | Permitted interpretation | Explicitly not shown |
|---|---|---|---|
| 1 | **PRIMARY** | Computational triage stability and within-panel docking-RRS operational record | Affinity, engagement, biological resistance |
| 2 | **CENTRAL** | Directional agreement (or non-agreement) between docking-RRS and MD local geometry | Which method is biologically correct |
| 3 | **NOVEL** | Estimand divergence as a diagnostic signal for African antimalarial natural products | Universal applicability; biological mechanism |
| 4 | **SECONDARY** | Sensitivity, transfer, and cross-metric diagnostics | Independent biological replication |
| 5 | **TECHNICAL** | QC, hashes, manifests, force-field and topology checks | Scientific validity of the biological hypothesis |
| 6 | **NOT_COMPUTED** | Intentionally absent; must remain explicit | All claims requiring these quantities |
| 7 | **UNOBSERVED** | No canonical measurements available | All biological resistance conclusions |

---

## 2. P1 → P2 non-independence crosswalk

P1 V8 has absorbed results originating in or overlapping with P2. P2 cannot present these as independent P2 validation. The following crosswalk records every P1-derived quantity used by P2:

| Quantity | P1 V8 location | P2 use | Independence status | Permitted P2 treatment |
|---|---|---|---|---|
| Set-C 17 candidates and 136 docking systems | P1 main + SM | P2 primary cohort | **Not independent** — same candidates, source chemistry, target panels, and workflow provenance | Upstream design context only; P2 does not revalidate P1 docking |
| PNS–RRS ρ = −0.714 (n=17) | P1 SM §cross-metric | P2 cites as companion context | **Not independent** — shared candidates and scoring protocol | Cite as upstream; P2's own ρ = −0.2098 (n=12) is the canonical P2 value |
| Partial PNS–RRS ρ = −0.6154 | P1 response §R9 | P2 cites as companion context | **Not independent** — uses P2's own docking RRS | Post-selection sensitivity; not external validation |
| DEKOIS 2.0 AUC 0.45 [0.37, 0.53] | P1 V8 SM | P2 cites as protocol-boundary evidence | **Not independent** — same docking protocol | Protocol-transfer boundary; not P2 biological validation |
| PfCRT corrected LYS-76 receptor | P1 V8 §null-control | P2 uses identical receptor | **Not independent** — same receptor preparation | Upstream protocol provenance |
| Candidate MPO selection | P1 V8 §cohort | P2 inherits selection conditioning | **Not independent** — same selection pipeline | Selection-conditioning caveat must be explicit |
| RRS class structure (A\*/A/B/C/D) | P1 V8 main | P2 inherits classification scheme | **Shared** — same class definitions | P2 may re-derive from its own canonical CSV; class scheme is shared methodology |
| Retention-not-gain interpretation | P1 V8 §interpretation | P2 adopts same reading | **Shared interpretive framework** | P2 applies independently to its own evidence |

**Required editorial rule:** Wherever P2 wording describes P1 results, it must say "upstream companion context" or "non-independent post-selection sensitivity analysis," never "independent validation."

---

## 3. Claim matrix

### 3.1 PRIMARY — Operational stability and docking-RRS triage

| ID | Claim | Manuscript location | Evidence / provenance | Level | Boundary |
|---|---|---|---|---|---|
| C01 | Set-C contains 17 candidates and 136 docking systems across PfDHFR and PfCRT | Methods, Results | `results/c_rrs_classification.csv`; DAR §2 | PRIMARY | Distinguish 12 complete two-target from 5 PfCRT-only candidates |
| C02 | Target-balanced RRS classes: A\* 1, A 1, B 4, C 5, D 1 | Primary RRS Results | `results/c_rrs_classification.csv`; DAR §2 | PRIMARY | Applies only to the n=12 complete-panel estimand |
| C03 | Docking-RRS is operationally stable under seed, input, and scoring-layer controls | Results (stability) | PP-01 multi-seed (DAR §9, ±0.05 kcal/mol); PP-15 multi-seed (DAR §8ter, ±0.03 kcal/mol); score perturbation audit (DAR §8, 77.9% class unchanged) | PRIMARY | Protocol reproducibility, not score accuracy or biological validity |
| C04 | RRS class sensitivity to threshold, perturbation, and eligibility rules is bounded | SI (margins, perturbation) | `results/v2609_rrs_margin_20260830/`; `results/c_acsi_weight_sensitivity.csv`; DAR §2, §9 | PRIMARY | Rule sensitivity, not biological calibration |

### 3.2 CENTRAL — Docking/MD directional divergence (main result)

| ID | Claim | Manuscript location | Evidence / provenance | Level | Boundary |
|---|---|---|---|---|---|
| C05 | For matched pilot rows with both docking and MD quantities, 7/8 comparisons diverge directionally | Results (central), Discussion | `md_vs_docking_comparison_pilot.csv`; DAR §5.1–5.2 | CENTRAL | Methodological divergence, not resistance or affinity evidence; denominator is 8 matched rows with a valid WT anchor, not 16 systems |
| C06 | MD-RRS_d range is 72.2–102.8 across 12 mutant states | Results (central) | `md_rrs_discriminative_pilot.csv`; DAR §5.1 | CENTRAL | Local geometry ratio within 10 ns; not an affinity, residence-time, or converged free-energy measurement |
| C07 | The single concordant case is PP-01 PfCRT K76T (docking looser, MD ratio 102.8 ≈ noise) | Results (central) | `md_vs_docking_comparison_pilot.csv`; DAR §5.2 | CENTRAL | One observation; not evidence that the methods agree in general |

### 3.3 NOVEL — Estimand divergence as diagnostic signal for African antimalarial NPs

| ID | Claim | Manuscript location | Evidence / provenance | Level | Boundary |
|---|---|---|---|---|---|
| C08 | The 87.5% divergence rate (7/8) constitutes a diagnostic signal identifying candidates whose docking ranking is likely an artifact of static pose scoring | Results (novel), Discussion | `md_vs_docking_comparison_pilot.csv`; DAR §5.1–5.2; dynamic docking paradigm (PMC6150405) | NOVEL | Specific to the tested Set-C panel and protocols; not a universal docking failure rate; denominator is 8 matched rows |
| C09 | African antimalarial natural products present molecular characteristics (rigidity, macrocycles, rare functional groups) that make them particularly susceptible to docking artifacts | Introduction, Discussion | Moyo et al. 2023 (PMC10567616); H3D/ZairaChem Nature Comms 2023 (s41467-023-41512-2); Ramírez & Caballero 2018 (PMC10395315); P2 molecular feature analysis | NOVEL | Descriptive; not a validated predictive model; feature-divergence correlation requires larger panel |
| C10 | Divergence rate for African NPs (87.5%) exceeds published rates for synthetic drug-like molecules in docking benchmarks | Discussion | Literature comparison (Ramírez & Caballero 2018, scoring function limitations RSC 2025); P2 divergence data | NOVEL | Cross-study comparison; different cohorts and protocols; not a direct head-to-head comparison |

### 3.4 SECONDARY — Sensitivity, transfer, and cross-metric diagnostics

| ID | Claim | Manuscript location | Evidence / provenance | Level | Boundary |
|---|---|---|---|---|---|
| C11 | PNS–RRS association is weak in the primary cohort (ρ = −0.2098, adjusted p = 1.0000, n=12) | Secondary Results | `results/cross_metric_statistical_audit.{csv,json}`; DAR §2–3 | SECONDARY | Descriptive; not evidence of independence or no relationship; post-selection |
| C12 | ACSI is a post-selection, cohort-dependent ranking descriptor | Secondary Results (SI formulas) | `results/c_acsi_scores.csv`; DAR §2 | SECONDARY | Not a causal biological measure; formulas moved to SI |
| C13 | GNINA CNN rescoring reproduces class-level retention on 38/38 eligible external ligands | Robustness/Discussion | GNINA consensus manifests; DAR §8quater.1 | SECONDARY | Same poses; not independent biological validation |
| C14 | External 39-ligand/312-state panel shows mean RRS ≈ 100.45; class-A fraction 0.974 | External docking | `external_vs_primary_bootstrap_20260828.json`; DAR §8 | SECONDARY | Computational transfer under different provenance; not experimental validation |
| C15 | DEKOIS 2.0 PfDHFR ROC-AUC is 0.45 [0.37, 0.53] | Discussion (protocol boundary) | DAR §3; P1 V8 SM | SECONDARY | Upstream companion context; protocol-transfer boundary; not P2 biological validation |

### 3.5 TECHNICAL — QC, endpoint diagnostics, and protocol records

| ID | Claim | Manuscript location | Evidence / provenance | Level | Boundary |
|---|---|---|---|---|---|
| C16 | 16/16 Set-C pilot trajectories pass geometric QC | Methods/Results (pilot) | `results/set_c_md/*` manifests; DAR §5 | TECHNICAL | Procedural reproducibility; not scientific validity |
| C17 | 16 finite MM-GBSA endpoint rows: 8/12 mutant ratios exceed 100% | Results (endpoint diagnostics) | `mmgbsa_summary_pilot.csv`; DAR §5.3 | TECHNICAL | Single-replicate endpoint ratios; not free-energy resilience; PP-01 PfCRT K76A inter-replicate Δ 7.75 kcal/mol demonstrates within-trajectory error ≠ replicate uncertainty |
| C18 | Parent-study MD: 4 complexes, 2 dissociated, 1 corrupted MM-GBSA, 1 interpretable endpoint | Discussion (protocol boundary) | parent-study manifests; DAR §4 | TECHNICAL | Structural check; not Set-C validation |
| C19 | STRING threshold sensitivity: PNS ranking robust at 400/700/900 (ρ = 0.9681–0.9975) | SI | `results/string_threshold_sensitivity_20260829/`; DAR §9 | TECHNICAL | Operational sensitivity; not biological network validation |

### 3.6 P1 BOUNDARY — Non-independence declarations

| ID | Claim | Manuscript location | Evidence / provenance | Level | Boundary |
|---|---|---|---|---|---|
| C20 | P2 Set-C is derived from P1; P2 is not an independent validation of P1 | Methods (estimand separation), Discussion | Crosswalk §2 above; DAR §0, §8 | PRIMARY | P2 may cite P1 as upstream context; P2 must not call any P1-derived result "independent P2 validation" |

### 3.7 NOT_COMPUTED — Intentionally absent quantities

| ID | Claim | Status | Required treatment |
|---|---|---|---|
| C21 | Full-panel MD-RRS (17 × 8 = 136 systems) | `NOT_COMPUTED` by design | Must remain explicit in all manuscript versions; cannot be promoted without a separate production contract |
| C22 | M1 replicated MD (12 trajectories × 100 ns) | `NOT_COMPUTED / NOT_REPORTABLE` | No completed trajectory set; partial artifacts are archival-only pending DAR reconciliation; no biological or convergence claim may be derived |
| C23 | Experimental PfDHFR/PfCRT WT-mutant activity (IC₅₀, SPR, transport) | `UNOBSERVED` | No canonical measurements; all biological resistance conclusions are outside P2 scope |

### 3.8 FORBIDDEN — Claims P2 must not make

| ID | Forbidden claim | Reason |
|---|---|---|
| F01 | "RRS measures resistance resilience" | RRS is a docking-score ratio; no experimental resistance measurement exists |
| F02 | "MD validates the docking ranking" | 7/8 diverge; the two estimands are not interchangeable |
| F03 | "MM-GBSA provides the binding free energy" | Single-replicate endpoint; not converged or calibrated |
| F04 | "PP-01 is a validated dual-target lead" | Follow-up candidate, not validated |
| F05 | "PP-02 is biologically eliminated" | Gate failure is computational, not biological |
| F06 | "GNINA/external panel independently validates P1" | Non-independent; same poses/provenance overlap |
| F07 | "PNS–RRS proves independence" or proves a biological network mechanism | Descriptive; not causal |
| F08 | "No effect" from a non-significant test | Use "no association was detected under this analysis" |

---

## 4. Required wording controls

1. Use **computational prioritisation**, **score retention**, **structural retention**, **protocol-local diagnostic**, **estimand divergence**, and **non-interchangeable quantities** where appropriate.
2. Do not use **validated**, **resistance-resilient lead**, **affinity**, **binding free energy**, **biological polypharmacology**, or **independent validation** for docking-RRS or the single-replicate pilot without an explicit limitation.
3. Keep `7/8` restricted to the **eight matched rows with a valid WT anchor for both quantities**; do not call it a percentage of all 16 systems.
4. Keep `8/12` restricted to the 12 mutant MM-GBSA ratios; WT rows are excluded from that denominator.
5. Keep the threshold-margin output separate from canonical class assignment.
6. PNS and ACSI formulas and sensitivity details belong in the SI; main text states they are post-selection descriptors.
7. P1 results must be labelled "upstream companion context" or "non-independent"; never "independent validation."
8. Markdown manual references may remain as written; LaTeX cross-references must use `cleveref` and `xr`.

---

## 5. Release gate

The reconfigured P2 manuscript may proceed to author review when:

- [ ] C01–C07 (PRIMARY + CENTRAL) are traceable to canonical DAR values and generating scripts;
- [ ] C08–C10 (NOVEL) are traceable to divergence data and literature context;
- [ ] C11–C15 (SECONDARY) are traceable with explicit non-independence labels;
- [ ] C16–C19 (TECHNICAL) are documented with QC status;
- [ ] C20 (P1 boundary) crosswalk is complete and visible in Methods;
- [ ] C21–C23 (NOT_COMPUTED/UNOBSERVED) remain explicit and unviolated;
- [ ] F01–F08 (forbidden claims) do not appear in any manuscript file;
- [ ] Main, SI, and cover letter compile without undefined references;
- [ ] No V2607 canonical value is overwritten;
- [ ] Author review confirms quantitative claims and submission scope.

---

## 6. Version history

| Date | Version | Change |
|---|---|---|
| 2026-08-30 | V2609 initial | C01–C16 matrix for V2609 narrative pivot |
| 2026-09-10 | Reconfiguration | Restructured for estimand-calibration scope; evidence hierarchy expanded to 6 tiers; 7/8 divergence promoted to CENTRAL; PNS/ACSI demoted to SECONDARY; P1 non-independence crosswalk added; forbidden claims F01–F08 added; claims expanded to C01–C20 |
| 2026-09-10 | Reframing | Added NOVEL level (estimand divergence as diagnostic signal for African NPs); claims C08–C10 added; scope expanded to malaria + African natural products; total claims now C01–C23 |
| 2026-09-10 | Literature integration | Deep web search (8 databases, 47 sources) integrated; C08–C10 evidence enriched with literature citations; 12 new references added to manuscript plan |
