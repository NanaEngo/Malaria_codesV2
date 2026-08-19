# Central Questions of the Projects

This document states the scientific questions addressed by Projects P1–P5 and the evidence-bounded answers currently supported by the canonical analyses. Docking, scoring functions, molecular descriptors, and model outputs are computational evidence; they do not by themselves establish experimental potency, target engagement, binding, or resistance circumvention.

## P1: Polypharmacology and Mutational Resilience

### Central question
Can target breadth and mutation resilience be evaluated as distinct, complementary computational properties when prioritising African-natural-product-inspired antimalarial chemotypes?

### Subquestions

1. Which members of the locked 17-member Set-C cohort show broad computational docking profiles across PfDHFR, PfCRT, PfClpP, and PfATP4?
2. How are mutation-resilience estimates distributed across the PfDHFR and PfCRT mutant panels when the RRS denominator is defined per target and non-binding wild-type targets are excluded?
3. Does the network-based PNS correlate with the mutation-aware RRS?
4. Does the docking protocol show enrichment against an external validation set, and what does a null result imply for interpretation?

### Answering results

1. The Set-C cohort was selected as a polypharmacology-oriented, enriched hypothesis cohort rather than a prevalence sample. The four-target wild-type matrix contains 68 candidate–target records that passed the defined geometric pose-quality gate. PP-06 is among the strongest target-profile candidates and is top-quartile across all four target profiles. The joint breadth-plus-A* RRS readout identifies PP-15, PP-06, and PP-11 as the three candidates favourable on all four target profiles and assigned to class A*. These are computational docking profiles, not experimentally demonstrated multi-target binding.
2. Per-target RRS classified the 17 candidates as **A\***: 6, **B**: 5, **C**: 5, and **D**: 1, with an observed range of 68.2–111.7%. The RRS calculation used genuine wild-type binders only (\(|S_{\mathrm{Vina,WT}}| \geq 5.0\) kcal mol\(^{-1}\)); non-binding wild-type targets were not used as denominators. The PfDHFR and PfCRT mutant panels therefore provide a mutation-resilience analysis separate from the four-target wild-type docking matrix.
3. PNS–RRS showed a negative exploratory association (Spearman \(\rho=-0.559\), \(p=0.020\), \(n=17\)), but it did **not** survive the Bonferroni threshold of approximately 0.017. The relationship is therefore a hypothesis-generating trend, not a confirmed association. ACSI–RRS was also not significant (\(\rho=-0.132\), \(p=0.613\)).
4. External PfDHFR DEKOIS validation was approximately null (canonical Vina-only protocol: ROC AUC 0.450, 95% CI 0.367–0.531). This result does not support external enrichment of the docking score and reinforces the need to treat the docking outputs as target-specific computational prioritisation rather than calibrated activity predictions. Any alternative AUC from a different scoring or subset analysis must not be conflated with this canonical value.

### Scientific interpretation and limits

P1 separates three quantities that should not be collapsed into one score: chemical-space novelty, target breadth, and mutation resilience. The principal output is a testable prioritisation map for biochemical, cellular, mutant-panel, and molecular-dynamics follow-up. The Set-C selection creates enrichment and limits prevalence-based interpretation. No experimental IC\(_{50}\)/EC\(_{50}\), confirmed target engagement, or resistance circumvention is claimed.

## P2: Polypharmacology, Resistance Resilience, and Molecular-Dynamics Filtering

### Central question
Can a target-specific, resistance-aware computational workflow distinguish polypharmacology-oriented antimalarial candidates from apparent scoring artefacts and identify which docking hypotheses remain physically plausible after molecular-dynamics analysis?

### Subquestions

1. How do the 17 Set-C candidates distribute across the PfDHFR and PfCRT wild-type/mutant docking panels under a per-target RRS definition?
2. Does PNS capture a relationship with RRS, ACSI, or wild-type docking affinity?
3. Do short production molecular-dynamics simulations preserve the docked binding mode for representative wild-type complexes?
4. Which MM-GBSA values are interpretable after trajectory-level binding and force-field quality control?
5. What does the P2 analysis contribute beyond a single-target MPO ranking?

### Answering results

1. The canonical Set-C analysis comprises 17 polypharmacology-oriented candidates and 136 WT/mutant docking systems: 85 PfDHFR systems (wild type plus four mutants per candidate) and 51 PfCRT systems (wild type plus two mutants per candidate). Per-target RRS yielded six A\*, five B, five C, and one D profiles. The former PP-11 PfDHFR C59R “knockout” interpretation was attributable to a non-binding wild-type denominator and was removed from the biological interpretation; PP-11 is classified on its PfCRT-binding layer.
2. PNS–RRS was negative but exploratory (\(\rho=-0.559\), \(p=0.020\), \(n=17\)) and failed Bonferroni correction. ACSI–RRS was not supported (\(\rho=-0.132\), \(p=0.613\)); RRS–wild-type score was also not significant (\(\rho=-0.433\), \(p=0.082\)). The mean ACSI was 0.543, with 2/17 candidates (11.8%) above 0.70, 10/17 moderately NP-like, and 5/17 below 0.50.
3. In the representative 10-ns wild-type MD systems, only PfCRT–214 and PfATP4–438 retained bound ligands after trajectory re-analysis. PfClpP/PfClpR-labelled 164 and PfDHFR–201 showed ligand dissociation or incorrect placement, with minimum protein–ligand distances of approximately 67.4 and 78.2 Å and no retained contacts. These outcomes demonstrate that MD is a necessary post-docking plausibility filter, not that all docking hits are validated binders.
4. Only PfCRT–214 yielded a valid interpretable MM-GBSA result in the canonical re-analysis (\(\Delta G=-18.25\pm0.40\) kcal mol\(^{-1}\)). The PfClpR system (PDB 4GM2; 164-labelled cohort) and PfDHFR–201 dissociated and were not interpreted as binding energies. PfATP4–438 was excluded because of a CHARMM36-to-AMBER conversion artefact producing a non-physical van der Waals inflation. No Set-C-specific MM-GBSA result is claimed unless separately documented.
5. P2 contributes a framework for separating target breadth, mutation resilience, chemical identity, trajectory retention, and end-point energy quality. Its principal scientific value is the identification of failure modes—target mixing, non-binding denominators, ligand dissociation, and force-field conversion artefacts—that would otherwise inflate confidence in computational prioritisation.

### Scientific interpretation and limits

P2 is a computational validation and quality-control study centred on polypharmacology and resistance resilience. RRS, PNS, ACSI, docking, MD, and MM-GBSA address different evidence layers and should not be treated as interchangeable measures. The cohort is enriched, the MD trajectories are short, and experimental potency and target engagement remain unmeasured.

## P3: Quantum-Inspired Representations

### Central question
Do quantum-inspired and topological hybrid representations improve antimalarial activity prediction relative to classical machine-learning fingerprints?

### Subquestions

1. Does a QK+TFP+TNE hybrid outperform ECFP4 under the canonical panel and cross-validation protocol?
2. Does the quantum kernel provide an advantage over matched classical kernels?
3. How robust are TFP and TNE representations on full-scale and external panels?
4. Do the representations add predictive value, diagnostic value, or both?

### Answering results

1. The canonical hybrid random-forest model reached AUC 0.8876 ± 0.0065, below the ECFP4 baseline of 0.9475 ± 0.0045. The ablation identified QK as the largest hybrid contributor (\(\Delta\) approximately −0.040 when removed), but the combined model did not exceed ECFP4.
2. The six-qubit quantum kernel was statistically comparable to the matched RBF kernel at the tested scales; no quantum advantage was established. The quantum-inspired component is therefore complementary rather than demonstrably superior for this task.
3. TNE was valid for 19,836/19,849 molecules on the canonical panel, with 13 failures. The broader external ChEMBL label-source-shift panel contains 22,447 molecules; 351 TNE embeddings failed (1.6%), leaving 22,096 complete cases for the descriptor sensitivity analysis. Separately, 180 canonical-SMILES overlaps with the P5 panel were excluded to create the molecule-disjoint public evaluation panel of 22,267 compounds used for the ECFP4–GIN transfer benchmark. The intention-to-evaluate analysis retained the 351 failures as zero-vector penalties, and the complete-case sensitivity analysis gave the same qualitative ranking. Neither external analysis establishes biological or universal molecule-disjoint generalisation beyond its stated panel.
4. The results support a distinction between descriptive/topological information and predictive superiority. TFP, TNE, and QKS may provide complementary representations, but the tested evidence does not establish improved activity prediction over ECFP4.

### Scientific interpretation and limits

P3 is an honest-negative benchmark of quantum-inspired and topological representations. It does not claim quantum advantage, prospective binding prediction, or general superiority across molecular datasets. Conclusions are bounded by the panel, descriptor construction, kernel protocol, and tested sample sizes.

## P4: Pareto-Guided Monte Carlo Search for Antimalarial Molecular Design

### Central question
Does a chemistry-informed Pareto-guided Monte Carlo tree search provide useful multi-objective candidate-set exploration beyond what is visible from a single scalar ranking in a constrained antimalarial fragment space?

### Distinct estimands

P4 deliberately separates two analyses:

1. **Scalar search-efficiency benchmark:** peak scalar reward under a common budget, compared across MCTS, random, greedy, and genetic-algorithm search.
2. **Candidate-level Pareto geometry:** the trade-offs retained in a non-dominated archive when potency, accessibility, resistance-informed similarity, and polypharmacology-informed proxies are examined jointly.

These estimands use different objective definitions and must not be interpreted as one pooled performance measure.

### Subquestions

1. Does MCTS obtain a higher scalar reward than random, greedy, or genetic search under a common budget?
2. Does a Pareto archive retain chemically distinct potency–accessibility–resistance–polypharmacology compromises that scalarisation can hide?
3. Which components contribute most strongly to the observed search behaviour in the factorial ablation?
4. Is the added value of MCTS scalar optimisation, candidate-set coverage, or transparent decision support?

### Answering results

1. In the primary 20-seed, 1,000-iteration benchmark with the public-activity proximity term, random search achieved the highest mean reward (0.6724 ± 0.0056), followed by MCTS+ScafVAE (0.6649 ± 0.0068), GA (0.6453 ± 0.0124), and greedy search (0.4278 ± 0.0000). MCTS was below random (paired \(t_{19}=-4.97\), \(p=0.000085\)) but above GA (\(t_{19}=6.95\), \(p<0.0001\)).
2. The separate, secondary pre-activity analysis used a distinct objective vector and identified four non-dominated profiles with hypervolume 1.2366 under min–max normalisation and reference point 1.1. This hypervolume is not directly comparable with the primary scalar reward. The front retains different potency–accessibility–proxy compromises that are not represented by a single scalar optimum. Because some proxy values were re-derived or excluded when invariant, this is a candidate-set geometry analysis rather than a prospective validation of a four-objective optimiser.
3. The factorial ablation identified the ScafVAE policy (+0.148), Pareto-front component (+0.108), and large vocabulary (+0.079) as the largest positive main effects under that ablation configuration. These effects should not be read as direct comparisons with the primary scalar benchmark because the oracle configuration differs.
4. The evidence supports a limited conclusion: random search is a strong scalar baseline, whereas MCTS offers transparent exploration of objective-space compromises. P4 does not establish scalar superiority, biological activity, or experimental resistance mitigation.

### Scientific interpretation and limits

P4’s contribution is methodological and decision-oriented: it separates search efficiency from multi-objective coverage. Resistance and polypharmacology terms are computationally informed proxies, not direct mutant assays or four-target biological measurements. The Pareto analysis is secondary and objective-specific; the QMC/DMC candidate-level results were not publication-grade and are not used to support the manuscript’s conclusions.

## P5: GNN and Transformer Drug Discovery

### Central question
Do graph neural networks and pretrained sequence transformers improve antimalarial activity prediction beyond a compact ECFP4–random-forest baseline when chemical scaffolds are held out?

### Subquestions

1. Do GNNs and transformers outperform ECFP4 under scaffold-separated evaluation?
2. Does topological fusion with TFP or TNE improve a base GIN?
3. Does representation–task alignment matter more than model scale on this panel?
4. Are the conclusions stable under random and scaffold splits?

### Answering results

1. No. ECFP4–RF remained strongest: AUC 0.9433 on the random split and 0.8300 on the scaffold split. On the scaffold split, ChemBERTa reached 0.7867, GIN 0.8047, GIN–TNE 0.8090, and GIN–TFP 0.8138. Every learned arm was significantly below ECFP4–RF after multiplicity correction.
2. GIN–TFP had a higher mean scaffold-split AUC than base GIN (0.8138 versus 0.8047). This is a descriptive improvement; it should not be called statistically significant unless a corresponding predeclared paired test is reported.
3. The results favour representation–task alignment over model scale for this curated antimalarial panel. The conclusion is an honest negative: larger or more complex models did not improve predictive ranking relative to ECFP4 under the tested protocols.
4. The ordering remained unfavourable to learned models under both random and scaffold evaluation, although all conclusions remain bounded by the panel, labels, split design, and model configurations.

### Scientific interpretation and limits

P5 supports ECFP4–RF as a strong baseline and treats TFP/TNE fusion as complementary descriptive modelling rather than an automatic route to higher predictive performance. The scaffold split is the principal generalisation test; the results do not establish universal superiority of fingerprints or universal inferiority of deep models.

## Cross-project synthesis

Across P1–P5, the programme produces a consistent methodological message:

1. **Separate evidence layers.** Docking scores, RRS, PNS, ACSI, MD, MM-GBSA, molecular descriptors, and predictive AUCs answer different questions.
2. **Use strong baselines.** ECFP4 remains difficult to exceed in P3 and P5; random search remains difficult to exceed on P4’s scalar objective.
3. **Treat negative results as results.** Null DEKOIS enrichment, non-significant PNS–RRS association, no quantum advantage, and the failure of larger models to beat ECFP4 define the limits of the tested approaches.
4. **Prioritise transparent decision support.** P1/P2 provide target- and mutation-aware hypotheses; P4 provides Pareto trade-off visibility; P3/P5 identify when complex representations do not improve prediction.
5. **Bound all claims.** The projects generate computational hypotheses and reproducible comparisons; experimental potency, target engagement, resistance circumvention, and prospective clinical utility remain to be tested.
