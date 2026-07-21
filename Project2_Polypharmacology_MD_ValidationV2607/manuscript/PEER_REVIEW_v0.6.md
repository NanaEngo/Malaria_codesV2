# Peer Review Report — Paper 2 Draft v0.6/v0.7

**Reviewer:** Internal (AI-assisted)  
**Date:** 4 July 2026  
**Target:** JCIM (IF 5.6)  
**Status:** Pre-submission review

---

## Summary

This manuscript presents a computational framework for validating polypharmacological antimalarial leads against African-prevalent resistance mutations using MD (30,000 ns) and MC (2.2M steps) across 220 protein-ligand systems. Four novel metrics (RRS, ACSI, PNS, MC-enhanced MM-GBSA) are introduced. The work addresses a genuine gap: no prior study systematically validates polypharmacological leads against African resistance mutations across multiple targets.

**Overall assessment:** Strong conceptual framework and methods, but the manuscript is incomplete (all Results tables empty, no figures). Major revisions needed before submission.

---

## Major Issues

### M1. Results section completely empty (CRITICAL)

All six Results subsections are empty (lines 231–367). Tables `tab:homology`, `tab:rrs`, `tab:pns`, `tab:mmgbsa`, `tab:crossmetric` contain no data. Figures `fig:acsi`, `fig:ppi`, `fig:rmsd`, `fig:crossmetric` are referenced but do not exist.

**Action:** Cannot submit until all Results are populated. This is expected given simulations haven't run, but the manuscript should not be submitted in this state.

### M2. Abstract claims "four novel metrics" but MC is a fifth

The abstract (line 102) states "four novel metrics" but the MC sampling is now described as a separate method in Methods (line 211). The Conclusion (line 439) also says "Three novel scoring metrics" (RRS, ACSI, PNS), which conflicts with the abstract's "four."

**Action:** Clarify whether MC-enhanced MM-GBSA is the fourth metric or a validation method. Update abstract and conclusion to be consistent: either "four metrics" (RRS, ACSI, PNS, MC-MM-GBSA) or "three metrics + MC validation."

### M3. ORCID placeholder

Line 76: `ORCID: 0000-0000-0000-0000` — must be replaced with actual ORCID before submission.

### M4. MC section added post-hoc — needs stronger justification

The MC section (lines 211–215) was added after v0.6. The manuscript needs:
- A sentence in the Introduction motivating MC as complement to MD (e.g., "MC explores conformational states not accessible within MD timescales")
- A reference supporting MC for binding free energy landscapes
- Discussion of MC results in the Discussion section (currently absent)

### M5. Remaining fictitious bibliography entries

11 entries still have `Author, A. and Author, B.` placeholders:
- `computational_mutations_2025`
- `africa_resistance_2026`
- `pfk13_resistance_2026`
- `global_resistance_landscape_2026`
- `anpdb_researchgate_2026`
- `value_addition_african_np_2025` (has DOI, needs author verification)
- `addressing_infectious_diseases_africa_2025` (has URL, needs author verification)
- `multi_target_antimalarials_2025` (has DOI, needs author verification)
- `mmgbsa_best_practices_2025` (has DOI, needs author verification)
- `network_pharmacology_malaria_2025` (has URL, needs author verification)
- `md_antimalarial_2026`

**Action:** Verify all via CrossRef before submission. JCIM will reject with fictitious references.

---

## Minor Issues

### m1. Force field mismatch discussion is brief

The Limitations section (lines 427–431) mentions the AMBER14/CHARMM36m mismatch but doesn't quantify the expected offset. Consider citing a benchmark study comparing these force fields for protein-ligand binding.

### m2. RRS formula clarity

Line 179: "The overall RRS for each compound is the mean across all mutants tested" — this is ambiguous. Does it mean:
- (a) Mean of per-mutant RRS values? or
- (b) RRS computed from mean ΔG across mutants?

**Action:** Clarify with equation: $\mathrm{RRS}_i = \frac{1}{M}\sum_{m=1}^{M} \mathrm{RRS}_{i,m}$

### m3. ACSI weights not empirically justified

Line 187: "The weights (0.40, 0.25, 0.20, 0.15) reflect the relative discriminatory power" — this is stated without evidence. The sensitivity analysis (Table S6) will help, but the manuscript should acknowledge that weights are initially set heuristically.

### m4. PNS uses Vina scores, not MD

The PNS (line 195) uses $\Delta G_{i,j}$ from Vina docking, not from MD/MM-GBSA. This should be explicitly stated, as readers may assume PNS uses MD-derived binding energies.

### m5. Cross-metric analysis: n=20 is small

With only 20 candidates, Spearman correlations will have wide confidence intervals. Consider reporting effect sizes (Cohen's d) alongside p-values.

### m6. Figures referenced but missing

Lines 294, 318, 329, 370 reference figures that don't exist. The `generate_all_figures.py` script exists but needs data.

### m7. "April 2026" literature search date

Line 119: "literature search: April 2026" — update to actual search date before submission.

### m8. Data Availability: GitHub URL may be wrong

Line 450: `https://github.com/Vital-Sao/Malaria_codes` — verify this is the correct GitHub username.

---

## Suggestions for Improvement

### S1. Add a system count breakdown table

Currently the 220 systems are described in text (line 131). A table showing:
| Category | Ligands | Targets | Systems | MD (ns) |
|----------|---------|---------|---------|---------|
| WT | 20 | 4 | 80 | 16,000 |
| Mutants | 20 | 6 | 120 | 12,000 |
| Controls | 5 | 4 | 20 | 2,000 |
| **Total** | — | — | **220** | **30,000** |

would improve clarity.

### S2. Add a flowchart of the computational workflow

A figure showing: Candidates → Homology Modeling → System Preparation → MD → MC → Analysis → Metrics would help readers follow the pipeline.

### S3. Consider adding MM-GBSA decomposition figure

Per-residue energy decomposition is mentioned (line 209) but no figure is planned for it. A heatmap of key binding site residues would strengthen the structural analysis.

### S4. Address n=20 statistical power

With n=20, the study is underpowered for detecting moderate correlations (ρ=0.5 requires n>25 for 80% power). Acknowledge this in Limitations.

---

## Verdict

| Criterion | Score | Comment |
|-----------|-------|---------|
| Novelty | 8/10 | First MD+MC validation of polypharmacological leads against African resistance mutations |
| Methods | 7/10 | Well-described but MC section needs integration; FF mismatch needs discussion |
| Results | 1/10 | All tables empty, no figures |
| Discussion | 6/10 | Good hypothesis framing but no MC discussion, no data to interpret |
| Writing | 7/10 | Clear, JCIM-appropriate style; minor inconsistencies |
| References | 4/10 | 11 entries still fictitious |

**Recommendation:** Major revision. Cannot submit until Results are populated and fictitious references are fixed.

---

*Review generated 4 July 2026.*
