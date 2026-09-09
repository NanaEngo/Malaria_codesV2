Reviewer: 1

Comments:

This manuscript "Target breadth and mutation resilience in African-natural-product-
inspired antimalarial chemotypes: a computational analysis" presents an integrated

computational workflow that combines scaffold-guided chemical-space expansion of
African natural products and synthetic antimalarials with multi-target docking and a
per-target resistance-resilience score (RRS) derived from mutant docking. The authors
argue that target breadth and mutation resilience are independent, complementary
properties. The separation of evidence layers is appreciated, and several methodological
choices are honest and clearly reported. However, it is not suitable for publication in
JCIM for several major concerns.
1. Target selection and structural evidence quality are highly uneven. The four targets
have vastly different levels of structural validation. These differences would
influence the "target breadth" result.
2. While the authors frame this as hypothesis-generating research, the proposed
validation strategy lists five categories of experiments but provides no preliminary
data, no estimated feasibility, and no prioritization beyond naming three candidates.
For a field where computational predictions frequently fail experimental validation,
at minimum a retrospective validation against known antimalarial scaffolds would
strengthen the workflow's credibility.

Reviewer: 2

Comments:
First of all, I want to encourage the authors to keep doing what they have done here: honest reporting with integrity. The authors didn't convert Vina scores to affinities, refused a cross-target composite on correct grounds, reported a benchmark that is not in favor of their own protocol, excluded non-binding denominators rather than zero-filling them, and stated their limitations at unusual length.

However, in its current form, I am afraid I cannot recommend this manuscript for publication on JCIM. I would encourage the authors to revise manuscript and submit again.

The instinct behind the design is sound and should be retained: the layers of evidence should be kept separate, composite summaries should be avoided, and null results should be reported transparently. The case for accessibility for groups in endemic regions is likewise genuine and well argued. A stronger, and genuinely different, paper would result if the revised version used ligand-free receptors under a single protocol, demonstrated a non-random benchmark (rescoring in the manner described by Hany et al. would be the most straightforward route), placed a PfCRT anchor at the resistance cavity, provided a null distribution for RRS, defined within-target favourability explicitly, and included a maintained repository.


Major points

1. (§3.5, §4.1–4.2, Title, TOC) The independence claim rests on a correlation that was not reported. From Table 2 and Table 1, I estimate that Spearman ρ(N_fav, RRS_mean) = +0.515, p = 0.034. This association is positive and is larger in magnitude than two of the three correlations reported in Table S6; it should therefore be reported. Although it is not significant under the authors’ α = 0.017, the PNS–RRS correlation (p = 0.020) is also not significant at that threshold and is nonetheless described as a trend. This is in tension with §2.5, which cautions against interpreting non-significance as equivalence, and with §4.1, which states that the null results “demonstrate” independence. With n = 17, the power to detect ρ = 0.5 at α = 0.017 is only 0.37; this limitation should be stated explicitly.
2. (§2.5, §3.5, Table 2) The −6.0 kcal mol⁻¹ threshold effectively performs the cross-target comparison that the paper is designed to avoid. The target-specific mid-ranges are −5.60 (PfDHFR), −6.51 (PfCRT), −6.04 (PfClpP), and −6.10 (PfATP4), yet a single cutoff passes 7 of 17 compounds for PfDHFR but 12 of 17 for PfCRT and PfATP4. In addition, a threshold cannot be described as both “a priori” and “the mid-range of the observed distributions.” Favourability should be defined within each target, for example by rank or percentile, and Table 2 should be recomputed accordingly.
3. (§2.3, SI §S12) PfCRT — this issue should be checked first. Structure 6UKJ corresponds to the 7G8 isoform, and residue 76 of chain A is modelled as threonine; the authors’ wild-type reference therefore already carries K76T. In addition, using the stated centre (147.070, 170.267, 142.364) and a 28 Å box edge, all atoms of residue 76 are displaced from the centre by 16.7–19.5 Å in the y direction and lie outside the box. The box would need an edge of at least 38.9 Å to contain the residue. No sampled pose could therefore make contact with position 76. Because the PfCRT panel is the sole source of resilience evidence for PP-02, PP-06, PP-11, and PP-13, and also contributes to PP-01 and PP-15, this problem affects every A* assignment. I would recommend anchoring the search to the central negatively charged cavity identified by Kim et al. as the drug-interaction site and constructing a genuine 3D7-like wild-type reference.
4. (§2.3.1, SI §S12.1) The DEKOIS benchmark is worse than random in a particularly specific way: EF@1% = EF@5% = 0.00. This pattern suggests a problem that goes beyond generic scoring-function limitations. The PfDHFR binding-box centre coincides with the centroid of methotrexate A702 to 0.00 Å, and MTX remains present in the receptor. The DEKOIS actives are antifolates that require that binding site; retained MTX would therefore exclude them, whereas decoys can occupy peripheral grooves. Re-running the benchmark against a ligand-stripped receptor should change the result substantially. Hany et al. (Drug Des. Devel. Ther. 2025, DOI 10.2147/DDDT.S537065) applied DEKOIS 2.0 to wild-type and quadruple-mutant PfDHFR using Vina and showed that rescoring with CNN-Score/RF-Score-VS improved the benchmark from worse-than-random to better-than-random. This is the closest prior work to the present study and should be cited and discussed explicitly.
5. (§2.4, p. 21) The authors state that wild-type and mutant receptors were prepared by different routes and with different heteroatom composition, and that this contributes to RRS alongside the mutation, with the two effects “not separated here.” This single caveat substantially undermines the interpretation of Table 1. The required control is straightforward: recompute RRS using a wild-type receptor processed through the same pipeline as the mutant receptors, but with no mutation applied, and use the resulting distribution as a null. The authors’ own observation that mutant scores differ less from one another than each differs from the wild-type reference suggests that the batch effect may dominate the signal. The null spread should be reported alongside Table 1, and the A*, B, C, and D class boundaries should be placed outside that distribution. As currently defined, the 80% and 70% boundaries are almost certainly finer than the uncertainty. The authors should also explain the six RRS values above 100%, for which resistance mutations improve predicted binding; notably, all four PfDHFR mutations do so for PP-15, the authors’ top candidate.
6. (Data Availability, SI §S11, §S12) The repository URL, https://github.com/NanaEngo/Malaria_codesV2, returns a 404 error; I was unable to access any of the primary data. Because the SI defers file names, checksums, and dependency versions to that README, and because the RRS wild-type denominators do not appear elsewhere, the values in Table 1 and Figure 1 cannot currently be verified. The repository should be made publicly available with a software license, a release tag, and an archival DOI, for example through Zenodo. The wild-type/mutant score table should also be included in the SI itself.
7. (§2.5, §3.6, Table S6) PNS and ACSI are used in the Abstract, Results, Discussion, and Figure 2, but they are never defined. The formulas, inputs, and software used should be provided.
8. (SI Table S8 vs §S12.2) These two sections contradict one another. Section S12.2 states that no pose-reproduction rate is claimed and that no such test is possible for PfClpP, whereas Table S8 lists “1 success” for all four targets, including PfClpP, and describes the validations as “establish[ing] docking protocol reliability.” Structure 9N10 also contains no small-molecule ligand that can be redocked. The score-stratified MMV rows are circular by construction, as the text itself acknowledges. Table S8 should either be withdrawn or rebuilt.
9. (§2.3, §3.3) A single seed (seed = 0) is used throughout. PP-15 exceeds the −6.0 kcal mol⁻¹ cutoff by only 0.045 kcal mol⁻¹ on PfDHFR and 0.084 kcal mol⁻¹ on PfCRT. At least five seeds should be run, and the dispersion of scores should be reported, so that readers can assess the stability of the N_fav assignments.


Minor points

1. (pp. 17–18) A paragraph is duplicated almost verbatim across the page break (“These three candidates are therefore the workflow’s most defensible first choices…”), and the two versions contradict each other: p. 17 says PP-01 and PP-15 are resilient across both panels, whereas p. 18 says PP-15 is the only one. Table 1 indicates that PP-01 has values on both panels, so the statement on p. 17 appears to be the correct one. The duplicate should be removed.
2. (Ref. 19) Reference 19, Kingma and Welling, is the original generic VAE paper; for a SMILES VAE, the authors should cite Gómez-Bombarelli et al., ACS Cent. Sci. 2018, 4, 268–276.
3. (§4.4) The “99.3% reduction in computational cost” is calculated relative to exhaustive docking of the full library, rather than to an alternative selection method. The more substantive question is what fraction of active compounds is retained after centroid reduction; a retention experiment would address this directly.
4. (p. 21) RRS eligibility is written as |ΔG_WT| < 5.0 kcal mol⁻¹ on p. 21 but as |S_Vina| elsewhere. The notation should be made consistent, since the authors are otherwise rightly careful about this distinction.
5, (SI) Section S12 is numbered twice (pp. S-11 and S-14). Table S7 states that there are 1,199 decoys, whereas Table S8 states that there are 1,200.
6. (Fig. 2_ ρ, p, and n should be reported directly in the panel for Figure 2.
7. (SI §S10) The MPO sensitivity analysis and enrichment validation are deferred to a companion manuscript described as “submitted.” Because the selection of Set C depends on these analyses, the essential results should be summarised in the present paper so that it can stand alone.
