# BMAD Q1 Data Analysis Report — active summary

**Scope:** P1–P3 only. P4 and P5 have dedicated DARs.
**Updated:** 12 August 2026
**Long-form history:** `docs/archive/md_full_20260812/BMAD_Q1_DATA_ANALYSIS_REPORT.md`

## 1. Executive status

| Project | Current status | Submission-relevant conclusion |
|---|---|---|
| **P1** | V6 is the submission-oriented workspace; V4/V5 provide corrected evidence and remediation layers | Chemical-space novelty, target-wise docking, and computational RRS/polypharmacology are reportable only within their stated provenance boundaries |
| **P2** | Canonical 17-member Set-C cohort and docking-RRS/ACSI/PNS analysis complete; candidate-specific MD is still incomplete | Docking-RRS is canonical; Set-C MD-RRS is not yet computed |
| **P3** | Canonical classical, hybrid, QKS, TNE/TDA, and external-validation analyses complete | Quantum-inspired descriptors are complementary; no quantum advantage over RBF or ECFP4 is claimed |

## 2. P1 — chemical space, docking, and RRS/polypharmacology

### Canonical findings

- The P1 chemical-space library contains **65,856 molecules**; **92.6%** are ECFP4-unreachable from the seed space and scaffold recovery is **69.3%**.
- The V4 2F6I/PfClpP remediation accounts for all **484** centroid attempts: **458 PASS**, **1 PENDING**, **15 protocol exclusions** for unsupported boron chemistry, **5 DOCKED_GATE_FAILED**, and **5 EMBED_FAILURE**. This is a provenance/remediation result, not experimental validation.
- V5 contains **68/68 finite target-wise Vina records** for 17 candidates × 4 targets. Scores remain target-specific and are not averaged as a common affinity scale.
- The V5 mutant pilot contains **136/136 finite docking scores** for PfDHFR/PfCRT. It is exploratory and must not replace the canonical P2 RRS table.
- V6 integrates the exact 17-member cohort by canonical SMILES. The submission package is numerically audited; independent structural review remains a provenance item, not an experimental result.

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

### Live Set-C execution checkpoint — 12 August 2026

The bounded **16-system pilot** (PP-01/PP-02 × PfDHFR/PfCRT mutation states) is prepared under the PI-approved OpenFF 2.2.0 AM1-BCC + CHARMM36m/TIP3P policy deviation. The live jobs are an **isolated `PP-01_PfDHFR_WT` witness**, not the full panel:

- **15254:** equilibration complete; hashed `npt.gro`/`npt.cpt` produced.
- **15259:** witness production running; latest recorded marker approximately 378,000/5,000,000 steps (756 ps/10 ns).
- **15260:** witness QC pending with `afterok:15259`.
- **Full-panel MD-RRS:** `NOT_COMPUTED`; no witness-only or incomplete result may be promoted.
- Historical 15106/15111/15117 identifiers are superseded.

## 4. P3 — quantum-inspired representations

Canonical full-library results:

| Representation/model | AUC |
|---|---:|
| ECFP4 | 0.9475 ± 0.0045 |
| Hybrid RF | 0.8876 ± 0.0065 |
| TFP | 0.8759 |
| TNE | 0.7219 |

Removing QK reduces hybrid AUC by **0.040**; TFP contributes **0.014**; TNE is mildly negative in the ablation. QKS re-runs show quantum ≈ RBF at n=5,000 and n=19,849; no quantum advantage is claimed. External descriptor analyses retain the **351 TNE failures** as an explicit ITT/complete-case sensitivity issue rather than hiding them. The external QKS pilot (n=150) gives quantum **0.8385** versus RBF **0.8423**, p=0.374; this is an external replication of equivalence, not an advantage.

## 5. Minimal provenance map

| Result layer | Source evidence | Status |
|---|---|---|
| P1 V5 target-wise Vina | `Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/` | finite raw records; exploratory where labelled |
| P2 canonical RRS/ACSI/PNS | `Project2_Polypharmacology_MD_ValidationV2607/results/c_rrs_classification.csv`, `c_acsi_scores.csv`, `c_pns_ranking.csv` | canonical docking-derived |
| P2 live MD | `Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_publication_witness_v8_20260811/` | witness production pending QC |
| P3 external validation | `Project3_Quantum_Inspired_RepresentationsV2607/results/` | canonical/external sensitivity outputs |

## 6. Cross-project rules

1. Preserve canonical input, script, parameter, and hash provenance for every result.
2. Keep P1 Set A, P2 MD Set B, and P2 polypharm Set C disjoint.
3. Never convert docking-RRS into MD-RRS; MD-RRS requires complete trajectories and PASS QC.
4. Keep failed, pending, exploratory, and historical outputs visible but clearly labelled.
5. Do not update manuscript claims from an incomplete job.

## 7. Next actions

- **P1:** complete author metadata/funding items and final author read-through for V6.
- **P2:** finish the isolated witness chain, then run the full candidate-specific production/QC chain before MD-RRS integration.
- **P3:** preserve the honest-negative external validation framing and complete repository deposit preparation.
- **All:** keep this summary short; place detailed job narratives and superseded decisions in the archive.
