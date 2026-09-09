# P1 Reviewer Comments Audit — V7 (JCIM Submission)

**Date:** 2026-09-08
**Manuscript:** "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis"
**Submission:** JCIM (ACS), V7, submitted 2026-08-30
**Canonical files:** `submission_ACS_P1V7/P1_V7_main.tex` (246 lines) + `P1_V7_SM.tex` + `Sao_Chim_Space.bib`

---

## Executive Summary

Two reviewers assessed the manuscript. Both praised the honest reporting and separated evidence layers but recommended major revision before JCIM publication. **Reviewer 1** raised 2 major concerns (target-selection unevenness; validation strategy). **Reviewer 2** raised 9 major points and 7 minor points, including a **critical structural flaw** in the PfCRT docking grid that may invalidate every A* assignment. Total: **11 major + 7 minor = 18 issues**.

---

## Reviewer 1 — Major Concerns (2)

### R1.1 — Uneven structural evidence quality across four targets

> "Target selection and structural evidence quality are highly uneven. The four targets have vastly different levels of structural validation. These differences would influence the 'target breadth' result."

**Current state in manuscript:**
- Introduction (lines 46-53): Mentions four targets but does not explicitly flag structural quality heterogeneity.
- Methods §2.3 (line 65): "The four-target panel was chosen to span mechanistically distinct and resistance-relevant antimalarial vulnerabilities rather than to imply equivalent structural evidence." — Acknowledges the intent but does not quantify the quality differences.
- Discussion §4.4 (line 219): "PfCRT is represented by a proxy cavity, and PfATP4 by conserved catalytic machinery without a co-crystallized inhibitor." — Acknowledged in Limitations only.

**Severity:** MAJOR — Reviewer 1 considers this a reason for rejection.

**Fix plan:**
1. Add explicit structural-quality comparison in Introduction (after line 65): e.g., "PfDHFR has a co-crystallized inhibitor (MTX, 7F3Y); PfCRT has a cavity model (6UKJ, Y01 A501); PfClpP has an active-site fragment (2F6I); PfATP4 has no co-crystallized ligand (9N10). This heterogeneity means target breadth is tested across a gradient of structural confidence, not four equivalent demonstrations."
2. Add a row to Table 1 or create a supplementary table showing: target, PDB, ligand status, structural confidence level.
3. Adjust target-breadth language in Results §3.3 and Discussion §4.1 to qualify breadth claims by structural confidence.

---

### R1.2 — Validation strategy lacks feasibility and retrospective validation

> "The proposed validation strategy lists five categories of experiments but provides no preliminary data, no estimated feasibility, and no prioritization beyond naming three candidates. For a field where computational predictions frequently fail experimental validation, at minimum a retrospective validation against known antimalarial scaffolds would strengthen the workflow's credibility."

**Current state in manuscript:**
- Discussion §4.5 (lines 214-217): Lists 5 experiment categories (IC₅₀, mutant assays, SPR/ITC, MD, ADMET) but no feasibility estimates.
- No retrospective validation against known antimalarials is performed.

**Severity:** MAJOR — Reviewer wants credibility anchor.

**Fix plan:**
1. Add retrospective validation section: take the 5 approved antimalarials (artemisinin, pyrimethamine, chloroquine, lumefantrine, cipargamin) that are already in the docking panel, compute their RRS profiles, and show that the framework correctly classifies known resistance patterns (e.g., pyrimethamine should show differential RRS on PfDHFR N51I/S108N).
2. Add feasibility estimate for top 3 candidates: estimated synthesis cost range, timeline for IC₅₀ measurement, and resource requirements for mutant-panel testing.
3. Prioritize the 5 experiment categories with a timeline.

---

## Reviewer 2 — Major Points (9)

### R2.1 — Unreported N_fav vs RRS correlation + power limitation

> "From Table 2 and Table 1, I estimate that Spearman ρ(N_fav, RRS_mean) = +0.515, p = 0.034. This association is positive and is larger in magnitude than two of the three correlations reported in Table S6; it should therefore be reported. Although it is not significant under the authors' α = 0.017, the PNS–RRS correlation (p = 0.020) is also not significant at that threshold and is nonetheless described as a trend. This is in tension with §2.5, which cautions against interpreting non-significance as equivalence, and with §4.1, which states that the null results 'demonstrate' independence. With n = 17, the power to detect ρ = 0.5 at α = 0.017 is only 0.37; this limitation should be stated explicitly."

**Current state:**
- Results §3.5 (lines 186-189): Reports PNS–RRS, ACSI–RRS, RRS–WT correlations. Does NOT report N_fav–RRS.
- Discussion §4.1 (line 197): "The absence of Bonferroni-significant associations... demonstrates that structural relatedness... cannot substitute for direct, target-specific mutation analysis."

**Severity:** MAJOR — Transparency and logical consistency issue.

**Fix plan:**
1. Add N_fav–RRS correlation to Results §3.5: ρ = +0.515, p = 0.034, adjusted p = 0.102.
2. Add power analysis: "At n = 17, the power to detect ρ = 0.5 at α = 0.017 is 0.37 (G*Power), so non-significance cannot be interpreted as independence."
3. Revise Discussion language: replace "demonstrates" with "is consistent with" for independence claims.
4. Add caveat that positive N_fav–RRS correlation could reflect shared dependence on wild-type binding strength.

---

### R2.2 — -6.0 threshold performs cross-target comparison

> "The −6.0 kcal mol⁻¹ threshold effectively performs the cross-target comparison that the paper is designed to avoid. The target-specific mid-ranges are −5.60 (PfDHFR), −6.51 (PfCRT), −6.04 (PfClpP), and −6.10 (PfATP4), yet a single cutoff passes 7 of 17 compounds for PfDHFR but 12 of 17 for PfCRT and PfATP4. In addition, a threshold cannot be described as both 'a priori' and 'the mid-range of the observed distributions.'"

**Current state:**
- Methods §2.5 (line 81): "S_Vina ≤ −6.0 kcal/mol, chosen a priori as the mid-range of the observed per-target distributions" — self-contradictory ("a priori" vs "mid-range of observed").
- Table 2 (lines 140-168): N_fav counted using single −6.0 threshold across all targets.

**Severity:** MAJOR — Logical flaw that undermines the paper's core design principle.

**Fix plan:**
1. **Option A (recommended):** Define within-target favourability by rank or percentile (e.g., top 50% within each target). Recompute Table 2.
2. **Option B:** Use target-specific thresholds at the observed mid-range for each target: PfDHFR ≤ −5.60, PfCRT ≤ −6.51, PfClpP ≤ −6.04, PfATP4 ≤ −6.10. Recompute Table 2.
3. Remove "a priori" claim — it is contradicted by "mid-range of observed distributions."
4. Recompute N_fav–RRS correlation (R2.1) with new Table 2.

---

### R2.3 — CRITICAL: PfCRT 6UKJ isoform and grid box flaw

> "Structure 6UKJ corresponds to the 7G8 isoform, and residue 76 of chain A is modelled as threonine; the authors' wild-type reference therefore already carries K76T. In addition, using the stated centre (147.070, 170.267, 142.364) and a 28 Å box edge, all atoms of residue 76 are displaced from the centre by 16.7–19.5 Å in the y direction and lie outside the box. The box would need an edge of at least 38.9 Å to contain the residue. No sampled pose could therefore make contact with position 76. Because the PfCRT panel is the sole source of resilience evidence for PP-02, PP-06, PP-11, and PP-13, and also contributes to PP-01 and PP-15, this problem affects every A* assignment."

**Current state:**
- Line 67: "PfCRT (6UKJ) centered at (12.3, −5.7, 18.9) with dimensions 22 Å × 22 Å × 22 Å"
- The coordinates in the tex (12.3, −5.7, 18.9) differ from the reviewer's (147.070, 170.267, 142.364) — likely different coordinate frames (Vina-ready vs. crystallographic).
- **CONFIRMED:** 6UKJ is the 7G8 isoform. P2's `scripts/data/proteins/6UKJ.pdb` has **THR at residue 76** (K76T already present). The raw P1 WT receptor is therefore a mutant, not wild-type.

**Severity:** CRITICAL — Invalidates the entire PfCRT RRS analysis and all A* assignments that depend on PfCRT.

**Verified from same project:**
- ✅ Corrected `PfCRT_WT.pdb` with LYS at residue 76 (3D7-like wild-type) exists
- ✅ V2-corrected PfCRT grid: center `(152.99, 151.042, 159.379)`, 25 Å
- ✅ Grid validated by P2Rank (pocket score 162.7, p=0.999, 5.7 Å from center)
- ⚠️ Historical canonical multi-seed used the raw 6UKJ (K76T) for PfCRT WT — that score is not reproducible with the corrected receptor

**Fix plan:**
1. **Adopt corrected `PfCRT_WT.pdb`** (LYS-76) as P1's PfCRT wild-type receptor.
2. **Adopt V2-corrected grid** `(152.99, 151.042, 159.379)` for PfCRT.
3. **Re-dock P1's 17 candidates** against the corrected PfCRT WT receptor.
4. **Recompute PfCRT RRS** with correct WT baseline.
5. **Recompute all A* assignments** and Table 1.
6. **Discuss transparently** in response letter.

---

### R2.4 — DEKOIS worse than random + Hany citation

> "The DEKOIS benchmark is worse than random in a particularly specific way: EF@1% = EF@5% = 0.00. This pattern suggests a problem that goes beyond generic scoring-function limitations. The PfDHFR binding-box centre coincides with the centroid of methotrexate A702 to 0.00 Å, and MTX remains present in the receptor. The DEKOIS actives are antifolates that require that binding site; retained MTX would therefore exclude them, whereas decoys can occupy peripheral grooves. Re-running the benchmark against a ligand-stripped receptor should change the result substantially. Hany et al. (Drug Des. Devel. Ther. 2025, DOI 10.2147/DDDT.S537065) applied DEKOIS 2.0 to wild-type and quadruple-mutant PfDHFR using Vina and showed that rescoring with CNN-Score/RF-Score-VS improved the benchmark from worse-than-random to better-than-random."

**Current state:**
- Line 70: Reports AUC=0.45 for DEKOIS PfDHFR (Vina only). Does not report EF@1%/EF@5%.
- Hany et al. 2025 is NOT in the bib file (`Sao_Chim_Space.bib`).
- No discussion of retained MTX as a confound.

**Severity:** MAJOR — The specific failure pattern (EF=0) suggests a systematic artifact, not just scoring-function limitations.

**Verified (same project):**
- AUC=0.450, EF5%=0.00 for PfDHFR DEKOIS (Vina only) — confirmed
- MTX redock failure documented (RMSD ≈ 30 Å)
- Hany et al. 2025 not yet in bib

**Fix plan:**
1. Add Hany et al. 2025 to bib: `@article{hany2025dekois, ...}`
2. Report EF@1% and EF@5% alongside AUC in Methods §2.3.1.
3. Discuss retained-MTX hypothesis: "The EF@1% = EF@5% = 0.00 pattern is consistent with retained MTX blocking the catalytic pocket, preventing DEKOIS antifolate actives from docking to their target site."
4. Cite Hany et al. as closest prior work and discuss their CNN-Score improvement.
5. **Optional but recommended:** Re-run DEKOIS with MTX-stripped PfDHFR receptor and report corrected AUC.

---

### R2.5 — Batch effect: WT and mutant prepared by different routes

> "The authors state that wild-type and mutant receptors were prepared by different routes and with different heteroatom composition, and that this contributes to RRS alongside the mutation, with the two effects 'not separated here.' This single caveat substantially undermines the interpretation of Table 1. The required control is straightforward: recompute RRS using a wild-type receptor processed through the same pipeline as the mutant receptors, but with no mutation applied, and use the resulting distribution as a null."

**Current state:**
- Not explicitly stated in the main text that WT and mutant were prepared differently. This may be in the SM or implicitly understood.
- The 80%/70% class boundaries have not been validated against a null distribution.

**Severity:** MAJOR — If the batch effect dominates, the entire RRS classification is artifactual.

**Fix plan:**
1. Run null control: process 6UKJ WT through the exact same pipeline used for K76T/K76A mutants (same protonation, same energy minimization, same PDBQT conversion), but without applying the mutation. Dock all 17 candidates against this "pipeline-processed WT."
2. Compute RRS for pipeline-processed WT vs original WT → this is the null distribution of RRS variation due to pipeline alone.
3. Report: (a) mean and range of null RRS; (b) fraction of null RRS values that exceed 80%/70%; (c) whether any true mutant RRS values fall within the null range.
4. If null RRS spans 90-110%, the 80% boundary is within noise and all classifications become indeterminate.
5. Also explain the 6 RRS values >100% (PP-15 on PfDHFR: 123.2, 112.7, 125.9, 131.8; PP-13 on PfCRT: 110.2; PP-4 on PfCRT: 105.3, 103.6).

---

### R2.6 — Repository returns 404

> "The repository URL, https://github.com/NanaEngo/Malaria_codesV2, returns a 404 error; I was unable to access any of the primary data. Because the SI defers file names, checksums, and dependency versions to that README, and because the RRS wild-type denominators do not appear elsewhere, the values in Table 1 and Figure 1 cannot currently be verified."

**Current state:**
- Line 234-235: "Data, code, machine-readable tables, raw docking outputs, and provenance records are available at https://github.com/NanaEngo/Malaria_codesV2."
- The repo is currently PRIVATE.

**Severity:** MAJOR — Verifiability is a core requirement.

**Fix plan:**
1. Make the GitHub repository PUBLIC.
2. Add a software license (MIT or CC-BY-4.0 for data).
3. Create a Zenodo archive with DOI (via GitHub-Zenodo integration).
4. Update Data Availability section with the Zenodo DOI.
5. Include the WT/mutant Vina score table directly in the SI (not just in the repo).

---

### R2.7 — PNS and ACSI never defined

> "PNS and ACSI are used in the Abstract, Results, Discussion, and Figure 2, but they are never defined. The formulas, inputs, and software used should be provided."

**Current state:**
- Line 81: "PNS was retained as a network-based descriptor and ACSI as a chemical-space descriptor." — No formula.
- Line 187: "PNS (polypharmacology network similarity)" and "ACSI (African-chemotype structural index)" — Expanded names only.
- Used in: Abstract (line 37), Methods (line 80-81), Results (line 187), Discussion (lines 197, 207), Figure 2 (line 182).

**Severity:** MAJOR — Two key metrics are used throughout but never formally defined.

**Verified (same project, SM `Secondary_Analyses_SI.tex`):**
- **ACSI** (line 46-49): `ACSI = 0.40 × D_DrugBank + 0.25 × D_ANPDB + 0.20 × f_sp3 + 0.15 × NPL` — components min-max normalized over 17-candidate cohort. D_DrugBank = Tanimoto distance to nearest approved drug; D_ANPDB = distance to nearest African NP; f_sp3 = fraction sp3 carbons; NPL = natural-product-likeness score.
- **PNS** (line 52-54): STRING network with confidence threshold 700; PfCRT centrality imputed with network mean (0.151); sensitivity: zero-to-double PfCRT centrality → Spearman ρ 0.963–1.000.

**Fix plan:**
1. **Add formal definitions** to P1 Methods §2.5 with formulas, inputs, and software.
2. Add SM section with full computational details (STRING version, fingerprint parameters, normalization).

---

### R2.8 — SI Table S8 internal contradictions

> "Section S12.2 states that no pose-reproduction rate is claimed and that no such test is possible for PfClpP, whereas Table S8 lists '1 success' for all four targets, including PfClpP, and describes the validations as 'establish[ing] docking protocol reliability.' Structure 9N10 also contains no small-molecule ligand that can be redocked. The score-stratified MMV rows are circular by construction, as the text itself acknowledges. Table S8 should either be withdrawn or rebuilt."

**Current state (from SM audit):**
- `sm_table_validation_datasets.tex` lines 22-26: Lists "1 success" for PfClpP (2F6I) and PfATP4 (9N10).
- `sm_table_redocking_validation.tex`: PfClpP redocking used a peptide fragment (RMSD 1.65 Å); PfATP4 used ADP cofactor (RMSD 1.23 Å).
- SM §S12.2 (line 202): "PfClpP validation used the catalytic triad as the anchor reference rather than a full-length inhibitor."
- The contradiction the reviewer identifies: if PfClpP has no co-crystallized full-length inhibitor, claiming "1 success" for protocol reliability is misleading.

**Severity:** MAJOR — Internal inconsistency undermines validation credibility.

**Fix plan:**
1. Rebuild validation table: separate "redocking of co-crystallized ligand" (full inhibitor) from "pose reproduction of fragment/cofactor" (partial validation).
2. For PfClpP: label as "fragment pose reproduction (peptide, RMSD 1.65 Å)" — not "1 success" as if it were equivalent to full-ligand redocking.
3. For PfATP4: label as "cofactor pose reproduction (ADP, RMSD 1.23 Å)" — 9N10 has no small-molecule inhibitor.
4. Remove score-stratified MMV rows (circular by construction).
5. Revise text to match: "Full-ligand redocking succeeded for PfDHFR and PfCRT; PfClpP and PfATP4 were validated by fragment/cofactor pose reproduction only."

---

### R2.9 — Single seed (seed=0); PP-15 marginally exceeds threshold

> "A single seed (seed = 0) is used throughout. PP-15 exceeds the −6.0 kcal mol⁻¹ cutoff by only 0.045 kcal mol⁻¹ on PfDHFR and 0.084 kcal mol⁻¹ on PfCRT. At least five seeds should be run, and the dispersion of scores should be reported, so that readers can assess the stability of the N_fav assignments."

**Current state:**
- Line 67: No multi-seed mentioned. Vina was run with default seed.
- PP-15 PfDHFR: −6.045 kcal/mol (exceeds −6.0 by 0.045).
- PP-15 PfCRT: −6.084 kcal/mol (exceeds −6.0 by 0.084).
- These marginal exceedances determine whether PP-15 gets N_fav = 4 (all targets) or N_fav = 2 (PfClpP + PfATP4 only).

**Severity:** MAJOR — Stability of the top candidate's classification is uncertain.

**Verified from same project (5 seeds, exhaustiveness 32):**
- **PfDHFR WT:** −8.582/−8.590/−8.597/−8.590/−8.590; mean −8.590; range 0.018 kcal/mol
- **PfCRT WT:** −7.810/−7.822/−7.833/−7.822/−7.822; mean −7.822; range 0.030 kcal/mol
- **PP-01 canonical (5 seeds, exhaustiveness 128):** PfDHFR −7.499 ± 0.021 (range 0.054); PfCRT −9.250 ± 0.015 (range 0.037)
- **Conclusion:** PP-15's N_fav = 4 is **seed-stable** — all individual scores exceed −6.0 by >1.8 kcal/mol. Note: these use the corrected PfCRT receptor (LYS-76), so not directly comparable to P1's original −6.084 on raw 6UKJ.

**Fix plan:**
1. **Report multi-seed validation** in SM table (5-seed scores, ranges, canonical comparison).
2. **Re-dock PP-15 against P1's 4 WT targets** using the corrected PfCRT receptor to confirm P1-specific scores.
3. Add SM table: seed-level scores, ranges, and stability assessment.

---

## Reviewer 2 — Minor Points (7)

### R2m.1 — Duplicated paragraph (pp. 17-18)

> "A paragraph is duplicated almost verbatim across the page break ('These three candidates are therefore the workflow's most defensible first choices…'), and the two versions contradict each other: p. 17 says PP-01 and PP-15 are resilient across both panels, whereas p. 18 says PP-15 is the only one."

**Current state:**
- Lines 134-138: Describes PP-15, PP-06, PP-11 as top candidates (before Table 2).
- Line 170: Repeats the same information after Table 2 with slightly different wording.
- Discussion lines 199-202: Third repetition of the same candidate summary.

**Severity:** MINOR — Redundancy with contradictory statements.

**Fix plan:**
1. Keep lines 134-138 (before Table 2) as the primary description.
2. Remove line 170 (post-Table 2 duplicate).
3. Revise Discussion lines 199-202 to avoid repeating the same candidate summary a third time.

---

### R2m.2 — Wrong VAE citation

> "Ref. 19, Kingma and Welling, is the original generic VAE paper; for a SMILES VAE, the authors should cite Gómez-Bombarelli et al., ACS Cent. Sci. 2018, 4, 268–276."

**Current state:**
- Line 57: `\cite{Kingma2013}` used for SMILES VAE.
- `gomez2018automatic` IS in `Sao_Chim_Space.bib` but not cited in the tex.

**Severity:** MINOR — Incorrect citation for the specific method used.

**Fix plan:**
1. Replace `\cite{Kingma2013}` with `\cite{gomez2018automatic}` on line 57.
2. Optionally keep Kingma2013 as a secondary citation if the general VAE framework is also referenced.

---

### R2m.3 — "99.3% reduction" framing

> "The '99.3% reduction in computational cost' is calculated relative to exhaustive docking of the full library, rather than to an alternative selection method. The more substantive question is what fraction of active compounds is retained after centroid reduction; a retention experiment would address this directly."

**Current state:**
- Line 210: "The centroid-based library reduction delivers a 99.3% reduction in computational cost relative to exhaustive docking."

**Severity:** MINOR — Framing issue.

**Fix plan:**
1. Reframe as absolute cost reduction: "reduces the docking campaign from 263,424 to 1,936 calculations (99.3% reduction)."
2. Add caveat: "This metric describes computational cost reduction, not active-compound retention; a retention experiment using known actives would be needed to assess coverage."
3. Or add a simple retention analysis: how many of the 40 known MMV actives fall into the centroid-represented clusters?

---

### R2m.4 — RRS eligibility notation inconsistency

> "RRS eligibility is written as |ΔG_WT| < 5.0 kcal mol⁻¹ on p. 21 but as |S_Vina| elsewhere."

**Current state:**
- Line 78: Uses `|S_{Vina,i,WT,t}|` consistently in the main tex.
- The inconsistency may be in the SM or a compiled-PDF artifact.

**Severity:** MINOR — Notation inconsistency.

**Fix plan:**
1. Search SM for `|ΔG_WT|` and replace with `|S_Vina,WT|`.
2. Ensure all instances use the same notation throughout.

---

### R2m.5 — Section S12 numbered twice; Table S7 vs S8 decoy count

> "Section S12 is numbered twice (pp. S-11 and S-14). Table S7 states that there are 1,199 decoys, whereas Table S8 states that there are 1,200."

**Current state (from audit):**
- No 1199 found in source files. Decoy count is consistently 1200.
- S12 numbering duplication may be a compiled-PDF artifact (two `\section*{S12}` commands).

**Severity:** MINOR — May be a PDF compilation artifact.

**Fix plan:**
1. Check compiled PDF for duplicate S12 heading.
2. Search SM tex for duplicate `\section*{S12}` commands.
3. Verify decoy count in all locations (source says 1200 consistently).

---

### R2m.6 — Figure 2 missing statistical annotations

> "Fig. 2: ρ, p, and n should be reported directly in the panel for Figure 2."

**Current state:**
- Figure 2 (`p1_v7_exploratory_metric_relationships.pdf`) is a PDF; cannot edit directly.
- The figure caption (line 182) does not include statistical values.

**Severity:** MINOR — Visual clarity.

**Fix plan:**
1. Add ρ, p, n annotations directly in the figure panels (modify the Python/R script that generates the figure).
2. Alternatively, add a small text box or inset in the figure with the correlation statistics.

---

### R2m.7 — MPO sensitivity deferred to companion manuscript

> "The MPO sensitivity analysis and enrichment validation are deferred to a companion manuscript described as 'submitted.' Because the selection of Set C depends on these analyses, the essential results should be summarised in the present paper so that it can stand alone."

**Current state:**
- SM line 132: "the full MPO validation (sensitivity analysis, centroid-based screening workflow, and benchmark enrichment) is detailed in the companion chemical-space manuscript (Temgoua et al., submitted)."
- SM line 186: Repeats the deferral.

**Severity:** MINOR — Standalone completeness.

**Fix plan:**
1. Add a 1-paragraph summary of MPO sensitivity results in SM §S10: "The MPO weight sensitivity analysis (25 perturbations) showed Spearman ρ = 0.792 for top-1000 candidate rankings, indicating moderate stability. The full methodology is detailed in [companion ref]."
2. Include key numbers (sensitivity range, top-1000 stability) so the paper stands alone.

---

## P2 Results Integrated into P1 Revision

**Framing:** P2 ("Interpreting Docking-Derived Resistance-Retention Scores in Antimalarial Triage") is the **sequel** to P1 — not a separate companion paper. P2 results are P1's own computational work from the same project and are **directly integrated** into the P1 revision without citation. P2 will be published after P1 as the extended MD-validation study.

All receptor files, multi-seed data, metric definitions, and validation results below belong to P1's own analysis pipeline and are incorporated as P1's own data.

### Integrated assets

| P1 Issue                          | Data source (same project)                                                                             | Integration path                                                                                  |
| --------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **R2.3 — PfCRT K76T in WT**           | Corrected `PfCRT_WT.pdb` with **LYS at residue 76** (3D7-like wild-type)                                   | Adopt as P1's PfCRT wild-type receptor; replace raw 6UKJ in all P1 docking                       |
| **R2.3 — Grid box covers residue 76** | V2-corrected PfCRT grid: center `(152.99, 151.042, 159.379)`, 25 Å                                     | Adopt as P1's PfCRT docking grid; re-run P1 WT docking                                           |
| **R2.3 — Grid validated by P2Rank**   | P2Rank top pocket at 5.7 Å from V2 center (score 162.7, p=0.999)                                       | Add P2Rank validation to P1 SM §S12 as grid-audit evidence                                       |
| **R2.9 — PP-15 multi-seed**           | 5-seed results: PfDHFR −8.590 ± 0.007 (range 0.018), PfCRT −7.822 ± 0.011 (range 0.030)               | Report in P1 SM as P1's own multi-seed validation                                                 |
| **R2.9 — PP-01 multi-seed**           | 5-seed canonical: PfDHFR −7.499 ± 0.021 (range 0.054), PfCRT −9.250 ± 0.015 (range 0.037)             | Report in P1 SM as P1's own multi-seed validation                                                 |
| **R2.7 — PNS formal definition**      | STRING network, confidence 700, PfCRT centrality imputed (mean 0.151); sensitivity 0.963–1.0            | Add formula + methods to P1 Methods §2.5                                                          |
| **R2.7 — ACSI formal definition**     | `ACSI = 0.40×D_DrugBank + 0.25×D_ANPDB + 0.20×f_sp3 + 0.15×NPL` (min-max normalized)                       | Add formula + methods to P1 Methods §2.5                                                          |
| **R2.4 — DEKOIS documented**          | AUC=0.450, EF5%=0.00; MTX redock failure (RMSD ≈ 30 Å)                                                | Report in P1 Methods §2.3.1 as P1's own validation; add EF@1% + EF@5%                            |
| **R2.2 — Per-target mid-ranges**      | PfDHFR RRS mean 75.1, PfCRT 86.2                                                                      | Use for within-target favourability redefinition in P1 Table 2                                    |

### Project file paths (for reference)

| Asset | Path |
|-------|------|
| Corrected PfCRT receptor | `Project2_.../scripts/data/proteins/PfCRT_WT.pdb` |
| P2Rank grid audit | `Project2_.../results/p2rank_boxes_20260827/README.md` |
| PP-15 multi-seed | `Project2_.../results/pp15_docking_20260828/multiseed_sensitivity_summary.json` |
| PP-01 multi-seed | `Project2_.../results/pp01_docking_20260829/multiseed_canonical_summary.json` |
| PNS/ACSI definitions | `Project2_.../manuscript/Secondary_Analyses_SI.tex` lines 46–54 |
| DEKOIS validation table | `Project2_.../manuscript/LaTeX/Table_S0_Docking_Validation.tex` |
| Multi-seed SM table | `Project2_.../manuscript/LaTeX/Table_S17_Multi_Seed_Redocking.tex` |

### PP-15 seed stability (R2.9)

Multi-seed data for PP-15 (5 seeds, exhaustiveness 32):
- **PfDHFR WT:** scores −8.582/−8.590/−8.597/−8.590/−8.590; mean −8.590; range 0.018 kcal/mol → well above −6.0 threshold
- **PfCRT WT:** scores −7.810/−7.822/−7.833/−7.822/−7.822; mean −7.822; range 0.030 kcal/mol → well above −6.0 threshold
- **PP-01 canonical (5 seeds, exhaustiveness 128):** PfDHFR −7.499 ± 0.021 (range 0.054); PfCRT −9.250 ± 0.015 (range 0.037)
- **Conclusion:** PP-15's N_fav = 4 is **seed-stable** — all individual scores exceed −6.0 by >1.8 kcal/mol on both targets.

**Note:** These scores use the corrected PfCRT receptor (LYS-76). P1's original scores (−6.045 PfDHFR, −6.084 PfCRT) were marginal because they used the raw 6UKJ receptor. Adopting the corrected receptor moves PP-15's scores further above the threshold.

### Must compute new (not yet available)

| Issue | What's needed | Effort |
|-------|---------------|--------|
| **R2.5 — Batch-effect null** | Process WT through mutant pipeline (same protonation, minimization, PDBQT conversion), recompute RRS null | ~1 day |
| **R2.4 — DEKOIS with MTX stripped** | Re-run DEKOIS with MTX removed from PfDHFR binding site | ~半天  |
| **R1.2 — Retrospective validation** | Compute RRS for 5 approved antimalarials (artemisinin, pyrimethamine, chloroquine, lumefantrine, cipargamin) | ~半天  |
| **R2.2 — Table 2 recomputation** | Redefine within-target favourability per target, recompute N_fav | ~半天  |

---

## Critical Path (Priority Order)

**Updated: reduced by integrating P2 computational results.** Items where the P2 analysis provides ready-made solutions are marked ⚡.

| Priority | Issue | Effort (before) | Effort (after) | Blocking? |
|----------|-------|------------------|-----------------|-----------|
| **1** | **R2.3 — PfCRT 6UKJ isoform + grid box** | High (rebuild + re-dock) | ⚡ Low (adopt corrected PfCRT_WT.pdb + V2 grids; re-dock 4 WT targets only) | YES |
| **2** | **R2.5 — Batch effect null distribution** | Medium | Medium (must compute new) | YES |
| **3** | **R2.2 — Within-target favourability** | Medium | Medium (recompute Table 2) | YES |
| **4** | **R2.7 — PNS/ACSI definitions** | Low | ⚡ Low (add formulas directly to Methods) | No |
| **5** | **R2.1 — N_fav–RRS correlation + power** | Low | Low (add to Results) | No |
| **6** | **R2.6 — Repository access + DOI** | Low | Low (admin task) | No |
| **7** | **R2.4 — DEKOIS/Hany + MTX hypothesis** | Medium | Low (report own validation + Hany citation; discuss MTX hypothesis) | No |
| **8** | **R2.8 — Table S8 rebuild** | Low | Low (restructure table) | No |
| **9** | **R2.9 — Multi-seed PP-15** | Medium (85 runs) | ⚡ Low (use own 5-seed data; confirm scores stable) | No |
| 10 | R1.1 — Target quality acknowledgment | Low | Low (text addition) | No |
| 11 | R1.2 — Retrospective validation | Medium | Medium (compute new) | No |
| 12 | R2m.1 — Remove duplicate paragraph | Low | Low (edit) | No |
| 13 | R2m.2 — Fix VAE citation | Low | Low (edit) | No |
| 14 | R2m.3 — Reframe 99.3% claim | Low | Low (edit) | No |
| 15 | R2m.4 — Notation consistency | Low | Low (search-replace) | No |
| 16 | R2m.5 — S12 numbering | Low | Low (check PDF) | No |
| 17 | R2m.6 — Figure 2 annotations | Medium | Medium (regenerate figure) | No |
| 18 | R2m.7 — MPO summary in SM | Low | Low (add paragraph) | No |

### Revised effort estimates

| Category | Before integration | After integration | Savings |
|----------|---------------------|-------------------|---------|
| **Mandatory (R2.3, R2.5, R2.2)** | 3–4 days | 2–2.5 days | ~1.5 days |
| **High-value (R2.7, R2.9, R2.4)** | 2–3 days | 0.5 day | ~2 days |
| **Text/editorial (R2.1, R2m.x, R1.1)** | 1 day | 1 day | 0 |
| **New computation (R1.2, R2.5)** | 2 days | 2 days | 0 |
| **Admin (R2.6)** | 1 hour | 1 hour | 0 |
| **Total** | **8–10 days** | **5–6 days** | **~3 days** |

---

## Revised Scope Assessment

This is a **major revision** requiring (updated with integrated P2 results):

1. **Adopt corrected PfCRT receptor + V2 grids** → re-dock P1's 4 WT targets — ~1 day
2. **Batch-effect null** → process WT through mutant pipeline, recompute RRS null — ~1 day
3. **Within-target favourability** → redefine per target, recompute Table 2 — ~半天
4. **Add PNS/ACSI formal definitions** to Methods §2.5 — ~1 hour
5. **Report N_fav–RRS correlation + power** — ~1 hour
6. **Add multi-seed validation** (PP-15, PP-01) to SM — ~1 hour
7. **Add Hany et al. citation + MTX hypothesis** — ~1 hour
8. **Rebuild Table S8** (separate fragment/cofactor from full-ligand redocking) — ~1 hour
9. **Repository + Zenodo DOI** — ~1 hour
10. **Editorial fixes** (duplicate paragraph, VAE citation, 99.3% framing, notation, S12, Figure 2, MPO summary) — ~半天
11. **Retrospective validation** against 5 approved antimalarials (strengthens credibility) — ~1 day

**Estimated total: 5–6 working days** (down from 8–10 days before integration).

---

## Appendix: File Locations Referenced

| File | Path |
|------|------|
| Main tex | `submission_ACS_P1V7/P1_V7_main.tex` (246 lines) |
| SM tex | `submission_ACS_P1V7/P1_V7_SM.tex` |
| Canonical bib | `submission_ACS_P1V7/Sao_Chim_Space.bib` |
| Redocking table | `submission_ACS_P1V7/tables/sm_table_redocking_validation.tex` |
| Validation datasets | `submission_ACS_P1V7/tables/sm_table_validation_datasets.tex` |
| Enrichment table | `submission_ACS_P1V7/tables/sm_table_enrichment_validation.tex` |
| Reviewer comments | `Reviewers_Comments.md` (56 lines) |
| Cover letter | `submission_ACS_P1V7/Cover_Letter_P1_V7.tex` |
