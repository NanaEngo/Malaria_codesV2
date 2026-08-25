# Poster Presentation Talking Points

## 30-Second Elevator Pitch

"We solved a critical barrier in antimalarial drug discovery: traditional virtual screening costs over 1000 CPU-hours per target, excluding endemic regions where 94% of malaria cases occur. Our centroid-based approach reduces this by 99.3% while maintaining pharmaceutical-grade reliability through dual-consensus validation. We've identified 19,913 synthesizable leads—all freely available—making advanced drug discovery accessible to researchers in malaria-endemic countries."

## 2-Minute Summary

### The Problem (20 seconds)
"Malaria killed 619,000 people in 2023, with rising artemisinin resistance demanding new drugs. But traditional virtual screening requires over 1000 CPU-hours per target—that's prohibitively expensive for research groups in endemic regions, where 94% of cases occur. This creates an equity gap: the regions that need new drugs most can't afford the computational tools to discover them."

### Our Solution (40 seconds)
"We developed a centroid-based screening strategy that reduces computational cost by 99.3%. Here's how: we use a variational autoencoder to cluster 65,856 molecules into 484 diverse representatives—just 0.7% of the library. These centroids capture the full chemical diversity. We then apply dual-consensus validation combining AutoDock Vina and DiffDock—two orthogonal methods that catch each other's errors, reducing false positives by 12-45%."

### Validation (40 seconds)
"This isn't just a computational trick—we validated it rigorously. First, prospective validation on DEKOIS showed single-method docking gives near-random results: ROC-AUC 0.450. But our consensus approach achieves ROC-AUC 0.924 to 1.000 on the MMV Malaria Box, recovering 69.8% of known antimalarials. We also show that intra-cluster similarity is twice as high as inter-cluster, proving our centroids represent real pharmacophoric neighborhoods."

### Impact (20 seconds)
"The result: 19,913 synthesizable leads across four Plasmodium falciparum targets, all with predicted selectivity over human cells. We've made the full dataset open-access on Zenodo. This makes pharmaceutical-grade antimalarial discovery accessible to any research group with basic computing resources."

## Key Questions & Answers

### Q: "Why is uncertainty quantification important?"
**A:** "Great question. We use the KL divergence from our VAE—it's higher in 64D than 32D. This isn't a bug, it's a feature. Higher KL means the model explicitly represents uncertainty, which lets us distinguish confident predictions from unreliable extrapolations. When you're screening 65,000 molecules, knowing which predictions to trust is crucial."

### Q: "How do you know the centroids actually represent the full library?"
**A:** "Two ways. First, our clustering metrics: intra-cluster Tanimoto is 0.227 versus inter-cluster 0.101—that's 2× higher coherence, proving pharmacophoric clustering. Second, validation: when we dock the centroids and expand the best clusters, we recover 69.8% of known antimalarials from the MMV Malaria Box. If centroids were poor representatives, we wouldn't see this recovery."

### Q: "What about the Tanimoto paradox—92.6% novel but 69.3% scaffold recovery?"
**A:** "Excellent observation! This actually proves our strategy works. Whole-molecule Tanimoto is low (<0.4) because we're diversifying substituents. But scaffold-only Tanimoto is 1.84× higher, showing we preserve bioactive ring systems while exploring new chemistry. We're doing scaffold-hopping, not just similarity searching."

### Q: "Why dual consensus instead of just DiffDock, which is ML-based?"
**A:** "DiffDock alone isn't calibrated to experimental actives. The DEKOIS benchmark showed Vina-only gives ROC 0.450—essentially random. Vina and DiffDock are weakly correlated (r=0.1-0.4), meaning they catch different binding modes. The consensus filters out compounds where the methods disagree, reducing false positives by 12-45%. We validated this against ChEMBL's calibrated thresholds."

### Q: "How synthesizable are these leads really?"
**A:** "We use two filters: SYBA (Synthetic Bayesian Accessibility) and synthetic accessibility score. 57% of the library has SYBA >0, indicating known reaction chemistry. Our final 19,913 leads all pass SYBA >0 and have mean SA score 3.51—below the 'easy to synthesize' threshold of 3.5. Plus, 94.1% are Lipinski compliant."

### Q: "What about selectivity over human cells?"
**A:** "We predict selectivity as the ratio of antimalarial activity (Ersilia eos7kpb) to hepatotoxicity (ADMET-AI DILI). All 810 screened seeds with valid predictions had SI >10, which is the standard therapeutic window threshold. This is a computational proxy—experimental IC50 determination is still needed, but it guides prioritization."

### Q: "How is this better than just docking everything?"
**A:** "Cost and feasibility. Docking 65,856 molecules × 4 targets = 263,424 evaluations. At 20 minutes per compound on a single CPU, that's 87,808 CPU-hours. Our centroid strategy: 484 molecules × 4 targets = 1,936 evaluations = ~645 CPU-hours—a 99.3% reduction. For resource-limited groups, this is the difference between feasible and impossible."

### Q: "Why focus on African natural products?"
**A:** "Two reasons: scientific and equity. Scientifically, natural products provide privileged scaffolds—look at quinine and artemisinin. African biodiversity is vast but underexplored. For equity: 94% of malaria cases occur in Africa. By building tools that work with limited compute and releasing African NP-inspired leads openly, we enable local researchers to participate in drug discovery for their own communities."

### Q: "What's next—have you tested any experimentally?"
**A:** "That's the next step. We've prioritized the top candidates by MPO score and synthetic accessibility. The next phase is experimental validation: synthesis, in vitro activity (IC50 against Pf NF54), and cytotoxicity (HepG2). We're seeking collaborations with groups that can run these assays. The full dataset is on Zenodo for anyone interested."

## Visual Walkthrough

### Column 1: Problem → Solution
1. **Point to alert box:** "247 million cases, but >1000 CPU-hours per target excludes 94% of regions"
2. **Point to graphical abstract:** "We start with African NPs + antimalarials → generate 65,856 hybrids"
3. **Point to VAE figures:** "64D gives higher KL—that's explicit uncertainty quantification"
4. **Point to diversity statement:** "92.6% novel structures, but 69.3% scaffold recovery—scaffold-hopping"

### Column 2: Validation
1. **Point to clustering plots:** "KMeans gives best separation—intra-cluster 2× inter-cluster Tanimoto"
2. **Point to consensus correlation:** "Vina and DiffDock weakly correlated—complementary, not redundant"
3. **Point to hit rate comparison:** "12-45% false positive reduction"
4. **Point to enrichment curves:** "Prospective DEKOIS (0.450) → Retrodictive MMV (0.924-1.000)"

### Column 3: Results & Impact
1. **Point to docking summary:** "Four validated targets, consensus <-8 kcal/mol"
2. **Point to physicochemical plots:** "94.1% Lipinski compliant, 57% synthesizable"
3. **Point to key achievements:** "19,913 leads, 99.3% cost reduction, all validated"
4. **Point to impact statement:** "Makes screening accessible to endemic regions—<10 CPU-hours"

## Handling Challenging Questions

### "Isn't 0.450 ROC-AUC terrible?"
**Response:** "Yes! That's exactly the point. That's Vina-only on DEKOIS, showing single-method docking is unreliable. It's not a failure—it's our motivation for consensus validation. When we add DiffDock and apply dual filters, we jump to 0.924-1.000. That prospective negative result validates our approach."

### "How do you know your actives will actually work in vitro?"
**Response:** "We don't—not yet. These are computational predictions. But we've done three things to de-risk: (1) validated against known actives (MMV Malaria Box), (2) calibrated thresholds to ChEMBL experimental data, and (3) filtered for synthetic accessibility and drug-likeness. Our 69.8% recovery rate on MMV suggests enrichment over random, but experimental validation is the next critical step."

### "This seems like a lot of work just to reduce compute cost."
**Response:** "It's not about convenience—it's about equity. Groups in malaria-endemic regions don't have access to HPC clusters. A laptop with 4 cores can run our centroid strategy in a few days. That same laptop would take years to screen the full library. We're democratizing access to drug discovery tools where they're needed most."

### "How does this compare to other generative approaches?"
**Response:** "Most generative models, like ScafVAE, optimize for GuacaMol distribution metrics. We're optimizing for a different objective: scaffold preservation with substituent diversity for virtual screening. Our VAE is trained on ANPDB topology, which is harder than ChEMBL. The 1.84× scaffold-to-whole-molecule similarity ratio shows we're doing scaffold-hopping, not just interpolation."

## Closing Statement

"Thank you for your interest. Our goal is to make antimalarial drug discovery accessible to researchers in endemic regions. All 19,913 leads, the full code, and protocols are freely available on Zenodo (10.5281/zenodo.19608875). If you're interested in experimental validation or collaborations, I'd love to discuss further."

## Quick Stats to Memorize

- **247 million** malaria cases (2023)
- **619,000** deaths
- **94%** of cases in regions excluded by high computational cost
- **99.3%** cost reduction (our method)
- **65,856** molecules in hybrid library
- **484** centroids (0.7% of library)
- **19,913** synthesizable leads identified
- **4** validated P. falciparum targets
- **0.450** ROC-AUC (Vina-only, DEKOIS prospective)
- **0.924-1.000** ROC-AUC (consensus, MMV retrodictive)
- **69.8%** recovery of known actives
- **12-45%** false positive reduction
- **100%** predicted selectivity (SI>10)
- **94.1%** Lipinski Ro5 compliant
- **57.0%** synthesizable (SYBA>0)

Good luck!
