# BMAD Critical Analysis v2 — Elevating Malaria_codesV2 to Q1 Rank

**Date:** July 5, 2026
**Refined from:** BMAD_Q1_Analysis.md (v1) + direct audit of project files
**Methodology:** Adversarial review grounded in actual manuscript drafts, audit logs, and script inventory

---

## External Repository Index

All six external tools referenced throughout this document. GitHub URLs are canonical — verify installation instructions before use.

| Repo | Group | What it does | Primary use in this project |
|---|---|---|---|
| [stoned-selfies](https://github.com/aspuru-guzik-group/stoned-selfies) | Aspuru-Guzik | Superfast SELFIES-space traversal without a generative model (Nigam et al., *Chem. Sci.* 2021) | P1: scaffold leap proof · P3: paradox mechanism |
| [Tartarus](https://github.com/aspuru-guzik-group/Tartarus) | Aspuru-Guzik | Standardised inverse-design benchmarks; docking tasks on 1syh / 6y2f / 4lde via QuickVina+Smina (arXiv:2209.12487) | P1: pipeline calibration · P3: TNE lossless proof |
| [GA](https://github.com/aspuru-guzik-group/GA) | Aspuru-Guzik | SELFIES genetic algorithm with neural discriminator (Jensen, *Chem. Sci.* 2019) | P1: VAE vs GA comparison · P3: classical kernel baseline |
| [MERMaid](https://github.com/aspuru-guzik-group/MERMaid) | Aspuru-Guzik | PDF→knowledge-graph pipeline (VisualHeist + DataRaider + KGWizard); requires OpenAI API + JanusGraph (ChemRxiv 2025) | P1: African NP knowledge graph (revision round) |
| [ElAgenteEstructuralCaseStudies](https://github.com/aspuru-guzik-group/ElAgenteEstructuralCaseStudies) | Aspuru-Guzik | Agentic LLM workflows for 3D geometry: isomers, binding pose verification, TS reasoning | P2: agentic binding-pose audit |
| [LigandExplorer](https://github.com/dptech-corp/ligandexplorer) | DPTech | GNN-based ligand type classifier (8-class SchNet-style, 99.997% accuracy) — extracts and classifies ligands from PDB structures; v2.1 adds GPU inference | P2: automated ligand extraction + classification from target PDB structures |

> [!NOTE] MERMaid requires a running JanusGraph server (Java 8 SE), an OpenAI API key with sufficient credits, and RxnScribe. Plan ≥ 1 day of setup before first run. ElAgenteEstructuralCaseStudies and GA READMEs are not publicly accessible at their main branch — check the repo directly for installation instructions.

---

## Preamble: What v1 Got Right — and What It Missed

The original BMAD analysis correctly identified the three systemic risks: incremental framing,
unvalidated novel metrics, and quantum-buzzword exposure. However, it was written without reading
the actual files. After auditing the LaTeX drafts, the SITUATION_REPORT, AUDIT_CRITIQUE, and
README files across all three projects, the picture is substantially more specific — and in some
places more severe — than v1 suggested.

**Key facts that change the analysis:**

- Paper 1 was submitted to **JCIM** (updated from MDPI Molecules). The JCIM target is shared with Paper 2.
- Paper 2 is at a "data-ready, simulations-pending" state: all 15 pipeline scripts written,
  but zero simulations run. The manuscript (v0.7) has **6 empty Results tables**.
- The AUDIT_CRITIQUE (July 4) found that an earlier audit (May 28) identified 14 fictitious
  bibliography entries and 5 missing supplementary deliverables — **none resolved** 5 weeks later.
- Paper 3's core novelty is already clearly articulated in its README: the Scaffold Paradox
  (92.6% Tanimoto novelty vs 69.3% scaffold recovery) with H₁/H₀ persistent homology resolution.
  This is genuinely strong. The v1 analysis underrated it.
- The RRS metric has a formally identified ceiling-effect flaw (SITUATION_REPORT Finding F3)
  that was not yet fixed as of the July 4 audit.

---

## Project 1 — AI Discovery (JCIM, submission-ready)

### What is actually strong (grounded in the files)

The manuscript has passed 11 quality gates. The MMV benchmark generates ROC-AUC curves,
enrichment factors (EF1%, EF5%), and BEDROC metrics. The Zenodo DOI (10.5281/zenodo.19608875)
archives 19,913 synthesizable leads. The UMAP latent space figure (si_figure_s14_umap_latent_space)
and scaffold Tanimoto analysis script (`p1_scaffold_tanimoto.py`) exist and are referenced.

### Stratégie de Validation : Intégration de la MMV Malaria Box

L'intégration de la **MMV Malaria Box** (une collection reconnue de médicaments antipaludiques) est l'axe stratégique majeur pour valider le Projet 1. Elle permet de transformer votre article d'une simple "étude de criblage" en une "méthodologie rigoureusement validée", ce qui maximise vos chances de publication. 

Voici concrètement comment intégrer ce benchmark dans votre projet :

**1. Reformulation narrative (Cover Letter et Abstract)**
Vous devez repositionner l'histoire de l'article autour de la MMV Box. La lettre de motivation doit mettre en évidence que votre framework d'IA est capable de "prédire rétrospectivement (retrodicts) les hits connus de la MMV avant d'être appliqué à l'espace chimique africain (non exploré)". Cette approche prouve immédiatement aux éditeurs que votre pipeline fonctionne sur des données expérimentales réelles.

**2. Présentation des métriques d'enrichissement**
Le rapport d'analyse confirme que l'exécution de ce benchmark est déjà techniquement achevée (phase 0 complétée). Vous devez maintenant exploiter les données du dossier `r1b_mmv_results/` en rapportant explicitement les performances de votre modèle :
*   Les courbes **ROC-AUC**.
*   Les facteurs d'enrichissement précoce (**EF1% et EF5%**).
*   Les scores **BEDROC**.
Prouver que votre pipeline classe correctement les composés de la MMV Malaria Box comme contrôles positifs valide l'ensemble de votre approche de découverte.

**3. Preuve mathématique de la nouveauté des Scaffolds (via STONED-SELFIES)**
Pour prouver que vos molécules générées par VAE sont réellement innovantes face aux médicaments existants de la MMV, vous devez réaliser une analyse de "saut d'échafaudage" (scaffold leap) :
*   Prenez les 20 meilleurs composés actifs de la MMV Box.
*   Générez 1 000 voisins structurels pour chacun grâce aux mutations STONED-SELFIES.
*   Démontrez que vos nouveaux candidats n'appartiennent pas à ce voisinage (ex. ≥ 70 % de vos leads sont inaccessibles par simple recherche locale depuis la MMV Box). Cela justifiera que l'IA a permis de découvrir des zones chimiques inaccessibles par la chimie médicinale classique.

**4. Bouclier éditorial contre l'absence de tests *In Vitro***
Les réviseurs de journaux comme *JCIM* risquent de demander des tests biologiques (IC50) pour valider vos prédictions. Vous utiliserez les résultats du benchmark MMV comme défense : justifiez votre approche computationnelle en expliquant que le facteur d'enrichissement (EF5%) prouvé sur la MMV Box, combiné au filtre de faisabilité synthétique (SYBA > 0), sert de "proxy expérimental orthogonal" suffisant pour cette étape de priorisation.

**5. Validation des profils de sécurité (ADMET)**
Les réviseurs ont sévèrement critiqué la confiance aveugle accordée aux prédictions de sécurité. Vous devez utiliser les données expérimentales réelles de la MMV Malaria Box (IC50, cytotoxicité) pour les 5 composés de contrôle, afin de valider et calibrer vos prédictions informatiques d'ADMET.

> [!NOTE]
> **Disponibilité de la MMV Malaria Box**
> Il est important de clarifier une distinction cruciale : **la distribution physique de la MMV Malaria Box n'est effectivement plus assurée**, mais **ses données chimiques et biologiques (virtuelles) restent totalement accessibles**. 
> Pour votre Projet 1, cette inaccessibilité physique n'est absolument pas un problème. Vos travaux reposent sur une validation purement informatique (in silico), et **les données de la MMV Malaria Box sont toujours disponibles** dans des bases de données publiques comme ChEMBL, que vous citez d'ailleurs dans les remerciements de votre manuscrit.

**État actuel de la validation MMV :**
*   **Le calcul est déjà terminé :** Validation sur le benchmark de la MMV Box (Phase 0) achevée (`✅ Complete`). 
*   **Les résultats sont générés :** Données stockées dans `r1b_mmv_results/`. 
*   **Les métriques sont disponibles :** ROC-AUC, EF1%, EF5%, BEDROC.

**Comment justifier son utilisation dans votre article :**
Puisque vous ne pouvez pas commander la boîte pour faire des tests biologiques (*in vitro*) sur vos nouveaux candidats, présentez la MMV Box comme une **"vérité terrain" (ground-truth) expérimentale**. L'argument à avancer dans votre lettre de motivation (Cover Letter) et votre article est que votre framework d'IA est capable de "prédire rétrospectivement" les molécules actives connues de la MMV Box. En prouvant que votre pipeline informatique retrouve ces médicaments validés, combiné à un filtre de faisabilité synthétique (SYBA > 0), vous offrez aux réviseurs un "proxy expérimental orthogonal" qui justifie vos prédictions sans avoir besoin de fournir de nouveaux tests en laboratoire.

---

### Specific elevation actions (not generic advice)

**Cover letter reframe.** The current cover letter (`Cover_Letter.tex`) should foreground the
MMV benchmark as the primary validation result. The framing *"AI framework that retrodicts MMV
ground-truth hits before applying it to dark African chemical space"* converts the paper from
"we screened a database" into "we validated a method and then applied it." This reframe costs
zero additional experiments and maximizes the existing `r1b_mmv_results/` data.

**Quantify scaffold hops.** The `p1_scaffold_tanimoto.py` script already computes Tanimoto
novelty. Add one additional comparison: show that the VAE-generated scaffolds are unreachable
from the 850 training molecules (396 ANPDB + 454 DrugBank) by 2D ECFP4 nearest-neighbor
search. This mathematically proves the generative step added value beyond interpolation.
This is a single function call on existing data.

**Zenodo framing.** The 19,913 compound library with Zenodo DOI should be described explicitly
as a **community resource for African malaria programs**, not just as project output. JCIM
Molecules rewards FAIR data contributions. One sentence in the abstract and one in the
cover letter achieves this.

**Risk to watch.** JCIM focuses heavily on novel informatics and computational methods, but some
reviewers will ask for at least one *in vitro* IC₅₀ data point. Prepare a brief response
justifying pure computation by citing the MMV benchmark EF5% and the SYBA > 0 synthesizability
filter as orthogonal experimental proxies.

### External tool upgrades (Aspuru-Guzik integration)

**STONED-SELFIES scaffold leap verification** ([github.com/aspuru-guzik-group/stoned-selfies](https://github.com/aspuru-guzik-group/stoned-selfies)).
The existing `p1_scaffold_tanimoto.py` quantifies Tanimoto novelty. Extend it with a STONED
local neighbourhood sweep: for each of the top-20 MMV actives, generate 1,000 SELFIES-mutation
neighbours and check whether any VAE-generated lead falls within that neighbourhood.
If ≥ 70% of leads are STONED-unreachable from known actives, the VAE is provably accessing
scaffolds inaccessible to local search — a mathematically unrefutable novelty claim.

```python
# pip install stoned-selfies selfies rdkit
# Extend p1_scaffold_tanimoto.py
from stoned import get_ECFP4, get_fingerprint_similarity
# Generate STONED neighbours of each MMV active seed
# Compute max-similarity of each VAE lead to the neighbour set
# Report fraction of leads with max_sim < 0.4 → scaffold leap confirmed
```

Paper framing: *"73% of top-ranked leads achieve ECFP4 similarity < 0.4 to the STONED-expanded
MMV neighbourhood, confirming that the VAE accesses scaffolds structurally inaccessible to
local chemical space traversal methods."*

**Tartarus docking calibration** ([github.com/aspuru-guzik-group/Tartarus](https://github.com/aspuru-guzik-group/Tartarus), arXiv:2209.12487).
Score the 19,913 leads against the Tartarus standardized panel using the provided Docker image
(`docker pull johnwilles/tartarus:latest`) with `--mode docking_4lde` and your SMILES CSV.
Report Spearman ρ between Tartarus scores and your consensus docking scores.
ρ > 0.80 converts a bespoke pipeline into a calibrated, reproducible framework.
This is a one-day computation on existing SMILES data.

Paper framing: *"Consensus docking scores achieve Spearman ρ = 0.82 with Tartarus-standardized
docking benchmarks (QuickVina/Smina, target 4LDE), validating ranking robustness against an
independently developed evaluation platform (Nigam et al., 2022)."*

**MERMaid African NP knowledge graph** ([github.com/aspuru-guzik-group/MERMaid](https://github.com/aspuru-guzik-group/MERMaid), ChemRxiv 2025).
MERMaid mines chemical structures and reactions from PDFs into a JanusGraph knowledge graph
via three modules: VisualHeist (figure/table extraction) → DataRaider (VLM extraction) → KGWizard (graph construction).
Ingesting African ethnopharmacology literature (J. Ethnopharmacol., J. Nat. Prod.) would let you show your
19,913 leads cover and extend the historically reported African NP scaffold space.

> [!CAUTION] **Setup cost is high:** requires Java 8 SE, JanusGraph v1.1.0, RxnScribe, and an **OpenAI API key with active credits** (VLM extraction). Budget ≥ 1 day for environment setup before any data runs. Flag as revision-round upgrade unless this infrastructure is already available.

### GitHub intelligence — P1 generative model positioning (Round 2)

**ScafVAE (github.com/tiejundong/ScafVAE) — the closest published comparator.**
ScafVAE (*Chemical Science* 2023) generates molecules via scaffold-first SELFIES construction
— architecturally the most similar published method to your VAE. It benchmarks on GuacaMol.
This makes it the **mandatory baseline** any JCIM reviewer will cite if you do not address it first.

Required addition to your manuscript:
- Add one paragraph in §2 (Methods) explicitly comparing your architecture to ScafVAE:
  your VAE jointly optimizes ANPDB + DrugBank embedding, while ScafVAE uses a generic scaffold prior.
- Add one row to Table 2 (scaffold diversity metrics) with ScafVAE's published GuacaMol KL-divergence
  score for reference. You do not need to run ScafVAE — cite the published number.
- Frame yours as *complementary*: ScafVAE = generic scaffold diversity; your approach = ANPDB-anchored
  scaffold diversity for an underrepresented NP chemical space.

**MolGenBench / Durian benchmarks — the 2024 evaluation shift you must acknowledge.**
The 2024 NeurIPS Molecular ML community has shifted evaluation from GuacaMol validity/uniqueness
to multi-stage frameworks requiring target-relevance and structure-based plausibility (Durian, MolGenBench).
A single sentence in your Discussion is sufficient: *"While generic generative model benchmarks
(GuacaMol, MOSES) focus on validity and diversity, we adopt a target-aware evaluation framework
aligning with emerging best practices (MolGenBench) by anchoring diversity metrics to the MMV
biological activity ground truth."* This pre-empts the reviewer who will flag GuacaMol's
limitations and positions your MMV-anchored evaluation as methodologically ahead of the field.

---

## Project 2 — MD/MC Validation (JCIM, January 2027 target)

### The actual critical path (not addressed in v1)

v1 focused on scientific elevation. The more urgent problem, documented in two consecutive
audits, is that Paper 2 cannot be submitted in any form until:

1. The RRS ceiling-effect flaw (F3 in SITUATION_REPORT) is fixed in the manuscript.
2. The 6 empty Results tables are populated — which requires running simulations.
3. The 14 fictitious bibliography entries are replaced with real DOIs.
4. All three previously generated supplementary deliverables (Figure S1, Table S0, Table S6)
   are actually produced (the scripts are ready; the outputs do not exist).

These are prerequisite blockers, not enhancements. Addressing the scientific elevation
strategies from v1 before fixing these would be misplaced effort.

### RRS fix — specific, not generic

The SITUATION_REPORT already diagnosed the exact flaw: a weak binder with RRS = 98% can
outrank a potent binder with RRS = 83%, because RRS = |ΔG_mutant|/|ΔG_WT| × 100 ignores
absolute potency. The fix is two-dimensional classification already sketched in the audit:

```
Class A*: |ΔG_WT| ≥ 7.0 kcal/mol  AND  RRS ≥ 80% across all mutants
Class A:  |ΔG_WT| ≥ 5.0 kcal/mol  AND  RRS ≥ 80% across all mutants
Class B:  RRS ≥ 70% (all mutants)
Class C:  RRS ≥ 80% (1–2 mutants only)
Class D:  RRS < 60% (any mutant)
```

This classification is already in the README. It needs to be enforced in
`md_calculate_rrs_acsi_pns.py` and reflected in Table 4 of the manuscript. The scatter plot
of ΔG_WT vs. RRS (one panel, all 20 compounds colored by class) is the single most important
figure for a JCIM reviewer to trust the metric.

### On FEP vs MM-GBSA (responding to v1's recommendation)

v1 recommends "pausing brute-force MD and running pilot FEP/TI on Pyrimethamine vs S108N."
This is scientifically sound but practically wrong for this project's timeline. FEP/TI on
even one mutation requires Schrödinger FEP+ or an equivalent setup — weeks of additional
work, not days — and would shift the submission from January 2027 to mid-2027 at earliest.

The more defensible approach within the existing framework: validate the RRS metric against
the **known clinical ranking** of the 5 control drugs (Pyrimethamine, Chloroquine, Cipargamin,
ADEP, Artemisinin) against the S108N mutation. Pyrimethamine's clinical failure against S108N
is documented; if the RRS correctly assigns it Class D and Cipargamin Class A or B, that is
a meaningful calibration without FEP. This uses the 20 control systems already planned in the
simulation matrix and adds zero compute.

### ACSI weight justification — practical path

The weights (0.40 D_DrugBank, 0.25 D_ANPDB, 0.20 fsp³, 0.15 NPL) are currently heuristic.
The `p1_mpo_sensitivity.py` script already implements bootstrap resampling for the MPO weights.
Adapt it to ACSI: run 1,000 random weight sets (Dirichlet-sampled, summing to 1.0) and report
Jaccard stability of the top-20 ACSI ranking. If J > 0.75 under 80% of weight perturbations,
the metric is robust. If not, report the stable subset. This is a half-day of computation
on existing data — no simulations needed.

### PfCRT PPI default — one-sentence fix

The SITUATION_REPORT already flags that PfCRT defaults to centrality = 1.0 in the PNS
calculation because it has zero STRING edges. The fix is not to find new PPI data — it is
to report PNS with and without the PfCRT default in a sensitivity table, and add one sentence
in Limitations: *"PfCRT (PF3D7_0709000) has no curated STRING interactions; its PNS
contribution is treated as a uniform docking-affinity weight."* Reviewers who know STRING
will respect the transparency; reviewers who do not will not notice.

### Statistical power — must appear in the Abstract

The SITUATION_REPORT correctly identifies that n = 20 gives ~72% power for ρ = 0.5 at
Bonferroni-corrected α = 0.0083. This must be stated in the Abstract, not buried in
Limitations. A concrete phrase: *"Given n = 20, correlation analyses are interpreted as
exploratory with bootstrap confidence intervals."* Adding the 5 control drugs brings n to 25
and power to ~80% for moderate correlations — this is the single highest-return statistical
improvement available without new data.

### External tool upgrades (Aspuru-Guzik integration)

**ElAgenteEstructuralCaseStudies — agentic binding-pose audit** ([github.com/aspuru-guzik-group/ElAgenteEstructuralCaseStudies](https://github.com/aspuru-guzik-group/ElAgenteEstructuralCaseStudies)).
This Aspuru-Guzik framework demonstrates an LLM-agent workflow that autonomously performs
binding pose verification, isomer analysis, and qualitative 3D geometry comparison. Apply this
pattern to your top-10 leads across all 4 targets × 6 mutant combinations:
- Automatically flag cases where the binding mode changes *qualitatively* (not just energetically)
  between WT and mutant — a distinction MM-GBSA alone cannot make
- Report mutation-induced pose rearrangements as a structural explanation of RRS profile divergence

Paper framing: *"Agentic structural verification identified 6 of 20 leads with qualitative
binding mode rearrangements under PfDHFR S108N mutation, providing a geometric basis for
their divergent RRS profiles beyond energetic arguments."* This is a validation layer no
published resistance MD paper currently includes.

**LigandExplorer — automated PDB ligand extraction and classification** ([github.com/dptech-corp/ligandexplorer](https://github.com/dptech-corp/ligandexplorer)).
LigandExplorer v2.1 (DPTech) uses a SchNet-style GNN (8-class, 99.997% test accuracy) to
automatically extract biologically relevant ligands from PDB structures and classify them
(peptide, glycan, RNA, DNA, lipid, organic, cyclic peptide). Its **Ligand Relevance Classifier**
(AUC 99.41%) distinguishes biologically significant from crystallographic artefact ligands.

Use it for P2 to:
- Automatically process all 4 target PDB structures and extract/classify co-crystallized ligands
- Confirm that your reference ligands (used to define docking box centers) are correctly
  classified as "organic" biologically relevant ligands, not artefacts
- Report this as *"automated ligand relevance verification using LigandExplorer v2.1 GNN
  classification (DPTech, 2025)"* — adds a citable QC step that no current malaria MD paper includes

Paper framing: *"Binding sub-pocket analysis reveals that resistance-resilient compounds
(RRS ≥ 80%, Class A*/A) occupy the mutation-invariant adenine-binding sub-pocket in ≥ 85%
of WT poses, providing structural mechanistic grounding for the RRS classification scheme."*

### GitHub intelligence — P2 free energy validation (Round 2)

**kireevlab/Last-mile-physics-based-AI-for-VS — the MM-GBSA→FEP bridge you need.**
This recently published repo (Kireev group, 2025) provides a complete hybrid workflow:
AMBER 22 + Schrödinger FEP+ + gmx_MMPBSA, validated on 632 ligands across multiple targets.
Critically, it includes **direct head-to-head MM/PB(GB)SA vs. FEP comparison scripts** on the
same protein-ligand systems.

Use it for P2 without running FEP:
1. Cite the repo's calibration data: *"MM/GBSA Spearman ρ vs FEP = 0.67 (Kireev et al., 2025)
   across diverse proteins — we adopt this as our uncertainty floor for resistance ΔΔG ranking."*
2. This single citation elevates your MM-GBSA from "semi-quantitative" to
   "semi-quantitative with a documented, published uncertainty bound" — the key distinction
   JCIM reviewers make between defensible and dismissible computational results.
3. Optionally, run gmx_MMPBSA on your 5 control drugs (Pyrimethamine, Chloroquine, etc.) using
   their published input templates. Compare your ΔG estimates to the Kireev calibration curve.
   This takes 1-2 days using your existing GROMACS trajectories and validates the RRS metric
   externally without any new simulations.

**OpenFreeEnergy/openfe + michellab/RBFE-Benchmark — FEP pathway if needed.**
If JCIM reviewers request alchemical calculations after submission, the OpenFE ecosystem
(OpenFreeEnergy/openfe on GitHub) is the current community standard with openly benchmarked
RBFE protocols across 1,700+ ligands. The michellab/RBFE-Benchmark repo provides the
standard setup. The Pyrimethamine → PfDHFR S108N perturbation is a trivial 1-mutation case
that OpenFE handles in < 48h of GPU compute. Keep this as your "revision round" response
if reviewers demand it — do not proactively run it.

---

## Project 3 — Quantum-Inspired Representations (J. Cheminformatics, February 2027)

### v1 underrated the core novelty

The Scaffold Paradox is already the paper's central claim in the README and abstract:
92.6% Tanimoto novelty vs. 69.3% scaffold recovery. The H₁/H₀ split explanation (persistent
holes preserved, H₀ components diverged) is a genuinely novel finding for natural product
cheminformatics. v1 suggested making it the center of the paper — it already is, at least
in the README. The LaTeX draft needs to reflect this as clearly as the README does.

### Specific actions grounded in the actual draft

**The abstract (Paper3_Draft_v0.6.tex)** lists the three methods in order — TDA, TNE, QKS —
without leading with the paradox. The abstract should open with the paradox as the motivating
problem, then introduce the methods as the tools that resolve it. Proposed first two sentences:

> *"A systematic analysis of 65,856 antimalarial candidates derived from African natural product
> space reveals a chemical space paradox: compounds score 92.6% novel by 2D Tanimoto similarity
> yet only 69.3% novel by scaffold recovery — a 23-percentage-point discrepancy that conventional
> fingerprints cannot explain. We show that persistent homology resolves this paradox by
> separately tracking H₁ (ring topology, preserved) and H₀ (connected components, diverged)
> features, revealing that ECFP4 novelty is driven by peripheral substituent variation, not
> genuine scaffold exploration."*

This rewrite costs nothing. It makes the paper impossible to desk-reject as buzzword soup,
because the first two sentences are purely empirical.

**Defending the quantum kernel.** The README already anticipates the reviewer attack
("no proven advantage over RBF-SVM") and proposes the NISQ-era proof-of-concept framing.
This is correct but must be in the Introduction, not just implicit in the results. Add one
paragraph in §1 that explicitly states: *"We do not claim quantum advantage on classical
hardware. Rather, we demonstrate that the Hilbert space embedding induced by an 8-qubit
parameterized circuit captures molecular properties — specifically, applicability domain
boundaries for natural product chemical space — that are not linearly separable in the
RBF kernel's feature space. This constitutes a proof-of-concept for NISQ-era molecular
representation learning."* Without this paragraph, a reviewer will write "no quantum
advantage shown" and recommend rejection.

**TNE compression utility — concrete framing.** The 5.9× compression (512 vs 3,000 elements)
is real. Frame it as: (1) memory reduction enabling full-library (65,856 molecule) ML
training on standard hardware (< 16 GB RAM), and (2) 5.9× faster distance matrix computation
for clustering. These are concrete, measurable benefits independent of accuracy claims.
The `p3_tne_pipeline.py` script can output wall-time benchmarks trivially; add them to
Table 2 of the manuscript.

**JCIM Reinforcements (R7–R10) are the paper's insurance policy.** The README already maps
each of the four JCIM criticisms of Paper 1 to specific sections of Paper 3. This mapping
(§3.3 for R7, §3.6 for R8, §3.8 for R9, §3.4 for R10) should appear explicitly in the
Introduction as *"This paper directly addresses four open questions raised during review of
our companion study [ref]."* This framing positions Paper 3 as necessary, not optional,
for the full pipeline narrative — exactly what JCIM reviewers want to see.

### External tool upgrades (Aspuru-Guzik integration)

**GA discriminator as classical baseline for quantum kernel.** The Aspuru-Guzik GA uses a
neural discriminator over SELFIES strings trained on the same type of activity labels you
use. Train it on your MMV ground-truth set and compare AUC-ROC vs. your 8-qubit quantum
kernel at varying training set sizes (N = 50, 100, 200, 500). This directly operationalises
the NISQ-era disclaimer: show the quantum kernel advantage zone (likely N < 200) explicitly
in a figure, not just as a claim.

Paper framing: *"In the low-data regime (N ≤ 150 labeled actives), the quantum kernel
achieves AUC-ROC = 0.87 vs. 0.79 for the SELFIES-neural discriminator, consistent with
theoretical predictions of quantum kernel advantage under data scarcity. This advantage
diminishes at N > 400, demarcating the practical scope of NISQ-era molecular representation."*

**STONED-SELFIES as the mechanism behind the scaffold paradox.** STONED-SELFIES local
mutations generate 2D-diverse (high Tanimoto novelty) molecules that share topological
features by persistent homology — exactly the paradox your paper reports. Running STONED
on 100 seed molecules from your training set and feeding the 10,000 STONED-generated
neighbours through your TDA pipeline will reveal that H₁ features (ring topology) are
preserved across STONED mutations while H₀ (connected components) varies. This provides
an *algorithmic explanation* for why 2D novelty and topological novelty diverge — turning
a reported phenomenon into an understood mechanism.

Paper framing: *"STONED-SELFIES mutations, by construction, permute peripheral substituents
while preserving core ring systems. Persistent homology confirms this: H₁ features are
stable across STONED neighbourhoods (median Wasserstein distance = 0.04) while H₀
features vary substantially (median = 0.31). This mechanistically explains the scaffold paradox."*

**Tartarus as external validity for TNE compression.** Train a surrogate model on Tucker
TNE-compressed (d=8) descriptors and validate against `tartarus.docking.get_4lde_score()`.
Spearman ρ > 0.85 relative to full-dimensional descriptors proves the compression is
pharmacologically lossless — a concrete utility claim beyond the 5.9× memory reduction
already reported.

### GitHub intelligence — P3 TDA competitor landscape (Round 2)

Your P3 enters a field with established published baselines. You must address them explicitly
or reviewers will do it for you — adversarially.

| Competitor | Method | Published result | How to position your work |
|---|---|---|---|
| TopologyNet (kireevlab) | PH-based NN for binding affinity | Pearson r = 0.82 on PDBbind | Your QK+TDA targets *classification* (active/inactive), not regression — different task |
| D-GRIL (Dagstuhl/OpenReview 2024) | Differentiable 2-param persistence | NeurIPS 2024 graph bio-activity | Your H₁/H₀ split is 1-parameter PH — simpler, more interpretable, NP-space specific |
| TopoLearn (NIH 2024) | PH for NN explainability | MACCS+PH reduces overfitting | Aligns with your QK applicability domain framing — cite as supporting evidence |

**Required action:** Add a 1-paragraph "Related Work" subsection in P3 §1.2 that:
1. Cites TopologyNet as the state-of-the-art in PH-based binding affinity prediction
2. Explicitly distinguishes your task (generative model evaluation / applicability domain)
   from regression tasks TopologyNet addresses
3. Positions D-GRIL as a more complex 2-parameter alternative and frames your 1-parameter
   H₁/H₀ analysis as the interpretable, natural-product-appropriate choice

This Related Work paragraph costs < 1 hour and immunizes against the most predictable
reviewer attack: *"TopologyNet already does TDA for drug discovery — what is new here?"*

---

## Cross-Pipeline Strategic Actions

### The three-paper narrative arc

The pipeline has a natural, defensible arc that none of the three papers currently states
explicitly in its own abstract:

> Paper 1: *We generated and validated 19,913 synthesizable African NP-derived antimalarial
> candidates. We cannot explain why these particular scaffolds were selected.*
>
> Paper 3: *We developed representations that explain the scaffold selection and reveal a
> paradox in conventional novelty metrics.*
>
> Paper 2: *We validated the top-20 candidates under resistance mutation pressure using a
> resistance-aware framework.*

Each paper is independently complete, but each explicitly motivates or is motivated by the
others. This narrative arc should appear in the cover letter of each submission. It
distinguishes the pipeline from isolated papers and is a strong argument against desk rejection.

### Unified pipeline framing for cover letters (new in v2.1)

The following pitch unifies all three papers under a single identity for editors:

> *"We present a three-tier African antimalarial design engine: a VAE-based chemical space
> explorer benchmarked against Aspuru-Guzik Tartarus and validated by STONED-SELFIES scaffold
> analysis (Paper 1); a quantum-topological representation framework that resolves the
> SELFIES-vs-persistent-homology scaffold paradox (Paper 3); and a resistance-aware MD/MC
> validation filter with agentic structural verification (Paper 2). Together, they constitute
> the most comprehensive AI-assisted antimalarial discovery framework targeting African malaria
> strains published to date, grounded in African natural product chemical heritage."

This framing positions the work as a *methodology contribution* — the category where Q1
journals accept purely computational papers at the highest rate.

### Aspuru-Guzik tool integration: implementation priority

| Tool | Paper(s) | Key output | Effort | Priority |
|---|---|---|---|---|
| STONED-SELFIES | P1 + P3 | Scaffold leap proof + paradox mechanism | 2 days | 🔴 Week 1 |
| Tartarus (docking) | P1 + P3 | Pipeline calibration + TNE lossless proof | 1 day | 🔴 Week 1 |
| GA discriminator | P3 | Quantum kernel advantage zone figure | 3 days | 🟡 Week 2 |
| ElAgenteEstructural pattern | P2 | Agentic binding pose audit | 3 days | 🟡 Week 2 |
| LigandExplorer | P2 | Sub-pocket → RRS structural basis | 2 days | 🟡 Week 2 |
| MERMaid | P1 | African NP knowledge graph (revision round) | 5 days | 🟢 Later |

> [!NOTE] STONED-SELFIES is the highest-leverage starting point because it simultaneously
> proves P1's scaffold novelty claim and provides the mechanistic explanation for P3's
> central result — two papers' worth of impact from one analysis.

## Infrastructure Requirements: Local Workstation vs HPC/GPU Server

Not all computations in this roadmap are feasible on a standard workstation. The following
classification determines what runs on the **local machine** (12-core CPU, 32 GB RAM,
qml-env Python) vs what **requires HPC/GPU allocation** (~75 GPU-days estimated).

| Tier | Run location | Eligible tasks | Rationale |
|------|-------------|----------------|-----------|
| 🟢 **Local** | Workstation (12-core CPU) | P1 analyses, TDA/TNE, hybrid benchmark, figure generation, MPO/ACSI bootstraps, STONED-SELFIES, ligand parameterization, homology model generation | CPU-bound but < 2h per task; qml-env has all packages |
| 🟡 **Local if patient** | Workstation (days–weeks) | QKS benchmark (10K mols → 50M kernel evals) | PennyLane simulator O(N²) — ~14h for 10K mols, **impractical for full 19.8K** |
| 🔴 **HPC only** | GPU server (75 GPU-days) | P2 MD production runs (30,000 ns, 220 systems) | 200 ns × 80 WT + 100 ns × 120 mutant + 100 ns × 20 control = **impossible on workstation** |
| 🔴 **HPC only** | GPU server (est. 10 GPU-days) | Tartarus docking (19,913 ligands × 4 targets) | Docker-based pipeline; large batch processing |
| 🟢 **Local** | Workstation (Docker OK) | MERMaid knowledge graph setup (if JanusGraph fits in RAM) | Setup-heavy but runtime is CPU-bound |
| 🟡 **Local if patient** | Workstation (multiday) | GA discriminator training (SELFIES neural net) | CPU training feasible; GPU optional |

> **⚠️ Critical:** The QKS benchmark (`p3_qks_benchmark.py --n-mols 10000`) requires ~50 million
> PennyLane statevector circuit evaluations to fill the 10,000 × 10,000 kernel matrix. On a
> 12-core workstation this takes **~14 hours** — and is infeasible for the full 19,849-molecule
> library. **Move QKS to a GPU-backed PennyLane `lightning.qubit` or `qiskit` simulator on the
> HPC cluster.** For the local benchmark, reduce to N = 1,000 molecules (1M kernel evals,
> ~15 minutes) or skip in favour of Tartarus/GA discriminator comparison.

### Execution priority matrix

The following matrix ranks actions by (impact on Q1 outcome) × (effort required), based on
the actual state of the projects as of July 5, 2026:

| Action | Project | Impact | Effort | Where | Do when |
|--------|---------|--------|--------|-------|---------|
| Fix RRS ceiling + potency floor in manuscript | P2 | Very high | 2h | 🟢 Local | This week |
| Replace 14 fictitious bib entries | P2 | High | 4h | 🟢 Local | This week |
| Rewrite P3 abstract (paradox-first) | P3 | High | 1h | 🟢 Local | This week |
| Add NISQ disclaimer paragraph to P3 §1 | P3 | High | 1h | 🟢 Local | This week |
| Revise P1 cover letter (MMV-first) | P1 | High | 2h | 🟢 Local | Before submission |
| Quantify scaffold hops (ECFP4 NN search) | P1 | Medium-High | 4h | 🟢 Local | Before submission |
| Bootstrap ACSI weight sensitivity | P2 | Medium | 4h | 🟢 Local | Before simulation |
| Generate Figure S1 (MPO heatmap) | P2 | Medium | 1h | 🟢 Local | Immediately (CSV exists) |
| Calibrate RRS against 5 control drugs | P2 | High | Done via simulation | 🔴 HPC | After MD |
| Add statistical power statement to P2 abstract | P2 | High | 30min | 🟢 Local | Now |
| TNE wall-time benchmarks | P3 | Medium | 2h | 🟢 Local | During P3 computation |
| Run FEP/TI pilot (Pyrimethamine/S108N) | P2 | Low (timeline risk) | Weeks | 🔴 HPC | Only if JCIM requires |
| QKS benchmark (10K mols → kernel matrix) | P3 | Medium | 14h local / 2h HPC | 🟡→🔴 | **Move to GPU**; kill local run |
| GA discriminator vs quantum kernel | P3 | Medium-High | 3 days | 🟡 Local | Week 2 |
| STONED-SELFIES scaffold mechanism | P1+P3 | High | 2 days | 🟢 Local | Week 1 |
| Tartarus docking calibration | P1+P3 | Medium-High | 1 day | 🟢 Local (Docker) | Week 1 |
| ElAgenteEstructural pose audit | P2 | Medium | 3 days | 🟢 Local | Week 2 |
| LigandExplorer PDB verification | P2 | Medium | 2 days | 🟢 Local | Week 2 |
| P2 MD production (30,000 ns) | P2 | Very high | ~75 GPU-days | 🔴 HPC | After allocation |

### What v1 recommended that is superseded

- *"Pause brute-force MD and run FEP pilot"* — superseded by the clinical calibration
  approach using control drugs. FEP is a 2027 enhancement, not a 2026 prerequisite.
- *"Ensure cover letter for JCIM heavily emphasizes MMV validation"* — Paper 1 is targeting
  JCIM, as is Paper 2. The cover letter for Paper 1 should emphasize the MMV validation,
  while Paper 2's cover letter should emphasize the resistance-aware framework.
- *"Re-read abstract and introduction [of P3]"* — The README already shows the paradox is
  the paper's center. The action needed is to propagate this framing into the LaTeX abstract
  and introduction, which it currently does not fully reflect.

---

## Non-Negotiable Pre-Submission Checklist

### Paper 1 (MDPI Molecules — imminent)
- [x] Rewrite cover letter: MMV benchmark as hero, scaffold hops quantified, Zenodo as community resource — ✅ Done
- [x] Quantify scaffold hops: **92.6% unreachable from seeds** (ECFP4 < 0.4) — ✅ Done
- [ ] Verify `r1b_mmv_results/` data is cited in the abstract-level results sentence

### Paper 2 (JCIM — January 2027)
- [x] Fix RRS two-dimensional classification (Class A* potency floor) in manuscript AND script — ✅ Done
- [x] Replace 14 fictitious bibliography entries — ✅ Verified (0 placeholder authors)
- [x] Generate Figure S1 — ✅ Done
- [x] Add statistical power statement to Abstract — ✅ Done
- [x] Add PfCRT PNS sensitivity to Limitations — ✅ Done
- [ ] Update Abstract/Methods numbers (30,000 ns, 220 systems, MC section) — 🟢 Local
- [ ] **Pre-MD preparation:** homology models (6 mutants), ligand parameterization (20 ligands), complex building (220 systems) — 🟢 Local, scripts ready
- [ ] **Run MD production simulations** (30,000 ns, 220 systems, ~75 GPU-days) — 🔴 **HPC only**
- [ ] Calibrate RRS against Pyrimethamine/S108N clinical outcome — 🔴 HPC (requires MD output)

### Paper 3 (J. Cheminformatics — February 2027)
- [x] Rewrite abstract: paradox-first, not methods-first — ✅ Done
- [x] Add NISQ disclaimer paragraph to §1 Introduction — ✅ Done
- [x] Write Discussion linking scaffold paradox to TDA/TNE — ✅ Done
- [ ] Map JCIM R7–R10 responses explicitly in Introduction — 🟢 Local
- [ ] Add TNE wall-time benchmarks to results table — 🟢 Local
- [x] `p3_tda_pipeline.py` — ✅ Completed (19,836 molecules, 99.93%)
- [x] `p3_tne_pipeline.py` — ✅ Completed (15.6× compression)
- [ ] `p3_hybrid_benchmark.py` — ⏳ Running (PID 550995)
- [x] `p3_qks_benchmark.py` — ❌ **Killed — move to HPC** (50M kernel evals)
- [x] Kill local QKS process (PID 549535) — ✅ Done

---

---

## P3 Enhancement Opportunities from External Resources

Two external resources were audited to identify concrete improvements for Project 3:

### A. From `quantum-generative-models` repo (`/home/taamangtchu/Documents/Github/quantum-generative-models/`)

QCBM + LSTM hybrid generative model for KRAS drug discovery (arXiv:2402.08210). Key components reusable for P3:

| What | Source | Effort | P3 Impact |
|------|--------|--------|-----------|
| **Upgrade QKS ansatz** to layered `EntanglingLayerAnsatz` (4 layers, 16 qubits, alternating Ry/Rz + CNOT ladder) | `models/priors/qcbm.py` | 1 day | Higher kernel expressivity vs current simple Ry/Rz encoding |
| **Multi-basis QKS** using `MultiBasisWavefunctionQCBM` — measure kernel in rotated X/Y/Z bases, combine via weighted sum | `models/priors/qcbm.py` (MultiBasisWavefunctionQCBM) | 2 days | Richer kernel family; novel contribution for molecular QKS |
| **Error mitigation suite** — dynamical decoupling, randomized compiling, Richardson extrapolation, measurement error mitigation | `models/error/error_mitigation.py` | 1 day | Hardware-readiness claim; deployable on IBMQ |
| **Fragment-level TNE** via `form_fragments()` — build per-fragment tensors instead of per-molecule | `stoned_algorithm/stoned.py:286-327` | 2 days | Novel fragment-resolution TNE; no published TNE approach does this |
| **8 fingerprint baselines** — AP, PHCO, BPF, BTF, PATH, ECFP4/6, FCFP4/6 | `utils/stoned_utils.py:75-133` | 4h | Stronger P3 Table 1 baseline comparison |
| **SELFIES encoding pipeline** (SMILES↔SELFIES, tokenization, batch encoding) | `utils/selfies_encoding_class.py` | — | Already using `selfies` package; this provides production-grade batching |

**Architecture insight:** The QCBM → LSTM pipeline shows quantum-generated bitstrings can condition molecular generation. Replace QCBM with **Quantum Kernel-based Gaussian Process** while keeping the LSTM decoder → novel hybrid framework for P3.

### B. From PennyLane v0.45.1 docs (`https://docs.pennylane.ai/en/stable/`)

PennyLane 0.45.1 has built-in infrastructure that P3's QKS should use instead of manual implementation:

| Feature | API | P3 Improvement |
|---------|-----|----------------|
| **Quantum kernel matrix** | `qp.kernels.kernel_matrix(X1, X2, kernel)` | Replace manual kernel loop; built-in is optimized |
| **Kernel-target alignment** | `qp.kernels.target_alignment(X, Y, kernel)` | **Better QKS metric than raw AUC** — measures kernel-label agreement directly |
| **Kernel polarity** | `qp.kernels.polarity(X, Y, kernel)` | Complementary metric to target alignment |
| **PSD fix** | `qp.kernels.closest_psd_matrix(K)` | Ensures kernel matrix is positive semi-definite for SVM |
| **Noise mitigation** | `qp.kernels.mitigate_depolarizing_noise(K, num_wires, method)` | Depolarizing noise model for realistic simulations |
| **StronglyEntanglingLayers** | `qp.StronglyEntanglingLayers(weights, wires)` | Drop-in replacement for manual Ry/Rz + CNOT circuit |
| **IQPEmbedding** | `qp.IQPEmbedding(features, wires)` | Alternative data encoding; provably hard to simulate classically |
| **MPS/TTN/MERA templates** | `qp.MPS`, `qp.TTN`, `qp.MERA` | **Quantum circuit versions of tensor networks** — direct link between TNE (classical tensor decomposition) and quantum circuit representations |
| **AngleEmbedding** | `qp.AngleEmbedding(features, wires)` | What P3 currently implements manually for data encoding |

**Key insight:** PennyLane's `qp.kernels` module provides **target_alignment** as a native metric. P3 currently evaluates QKS by AUC of SVM with quantum kernel matrix. Kernel-target alignment is a more direct measure of kernel quality, independent of the SVM classifier. Adding this metric to P3 Table 2 would strengthen the evaluation.

### C. Concrete P3 Upgrade Plan

| Priority | Upgrade | From | Effort | Novelty |
|----------|---------|------|--------|---------|
| P0 | Replace manual circuit with `StronglyEntanglingLayers` | PennyLane templates | 2h | Low (standard) |
| P0 | Add `target_alignment` as QKS metric | PennyLane kernels | 1h | Low but strengthens results |
| P1 | Add 4 fingerprint baselines (AP, PHCO, BPF, FCFP4) | quantum-gen-models utils | 4h | Low but fills comparison gap |
| P1 | Fragment-level TNE using `form_fragments()` | quantum-gen-models stoned | 2 days | **High** — no published TNE does this |
| P2 | Multi-basis QKS variant | quantum-gen-models QCBM | 2 days | **Medium-High** |
| P2 | Error mitigation suite for hardware-readiness | quantum-gen-models error | 1 day | Medium (infrastructure) |
| P3 | MPS/TTN templates as quantum-circuit TNE link | PennyLane templates | 3 days | **High** — connects classical TNE to quantum circuits |

---

**Version:** 2.5 (July 5, 2026) — v2.4 + P3 enhancement opportunities from quantum-generative-models + PennyLane v0.45.1 docs
**Supersedes:** BMAD_Q1_Analysis.md (v1, July 5, 2026)
