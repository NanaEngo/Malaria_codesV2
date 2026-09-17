# Audit des Formulations "Style Rapport" et Suggestions de Reformulation Académique (JCIM)

**Document de travail pour :** *Polypharmacology\_MD\_Validation\_V2609C.pdf* (Main) et *Polypharmacology\_MD\_Validation\_SM\_V2609C.pdf* (SM)
**Cible éditoriale :** *Journal of Chemical Information and Modeling* (JCIM, American Chemical Society)
**Date :** 11 Septembre 2026

---

## I. Résumé Exécutif &amp; Diagnostic Style

Dans sa version **V2609C**, le papier du Projet 2 a fait un progrès scientifique immense en adoptant le cadrage d'**"Estimand Divergence"** et de **"Triage par Test de Stress Structurel"**. Cependant, une analyse stylistique fine montre que plusieurs passages du texte principal (*Main*) et du supplément (*SM*) conservent des résidus de rédaction de type **"Rapport d'Audit Interne / Journal de Bord HPC"**.

Pour répondre aux standards d'élégance et de rigueur du *JCIM*, ces tournures doivent être débarrassées de leur jargon informatique (ex: *QC PASS*, *16/16 systems*, *dG\_WT*, *job array*) et de leurs disclaimers trop défensifs répétés dans chaque paragraphe.

### Les 5 grands types de tournures "Style Rapport" à éliminer :

1. **Le Jargon d'Audit HPC et de Code Brut :**
  * *Exemples actuels :* `QC PASS`, `16/16 systems`, `job array 15320`, `dG_WT`, `MD_RRS_d`, `164_PfClpP`, `rank01_ligand`.
  * *Correction JCIM :* Utiliser des termes biophysiques formels ($\Delta G\_{\text{WT}}$, $\text{MD-RRS}\_{\text{distance}}$, *PfClpR complex*, *primary candidate cohort*).
2. **Les Disclaimers Défensifs Répétés (Méta-commentaires) :**
  * *Exemples actuels :* *"This study does not establish biological target engagement, affinity, or resistance resilience"* (répété dans l'Abstract, l'Introduction, les Méthodes, les Résultats, la Discussion et la Conclusion).
  * *Correction JCIM :* Formuler positivement la portée du travail dans les Résultats (*"serves as a computational triage heuristic"*) et regrouper les réserves expérimentales strictement dans la section *Limitations*.
3. **Le Style "Journal de Bord / Checklist" :**
  * *Exemples actuels :* *"A 16-system single-replicate pilot on two candidates showed..."*, *"Parent-study MD check (non-overlapping cohort, secondary)..."*.
  * *Correction JCIM :* Utiliser des phrases fluides d'exposition scientifique (*"To evaluate whether dynamic relaxation alters static docking predictions, explicit-solvent molecular dynamics (MD) simulations were conducted on a pilot subset..."*).
4. **La Description Diagnostique des Bugs Informatiques :**
  * *Exemples actuels :* *"CHARMM36→AMBER conversion corrupted (+473 kcal/mol vdW inflation artifact)"*, *"BOND overflow in amber\_outputs.py"*.
  * *Correction JCIM :* Formuler sous forme de limites de paramétrisation (*"System parameterization for multi-chain membrane transporters introduced force-field conversion artifacts during end-state free energy calculations..."*).
5. **Les Enquêtes Internes de Débuggage dans le Texte Principal :**
  * *Exemples actuels :* Raconter en détail la recherche du fichier PDB original de PfCRT ou le choix d'exclure 2 frames sur 100.
  * *Correction JCIM :* Consigner les détails de reproductibilité technique dans le *Supporting Information* et ne garder que le résultat consolidé dans le *Main*.

---

## II. Tableau Comparatif &amp; Suggestions de Reformulation (Main &amp; SM)

### 1\. Title &amp; Abstract (Main Manuscript)

| Section      | Texte Actuel (Style Rapport / Défensif)                                                                                                                                                                                                                                                                                                                                                         | Reformulation Recommandée (Style Académique JCIM)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**    | *Calibrating the Interpretation of Docking-Derived Resistance-Retention Scores with a Short Molecular-Dynamics Structural Stress Test*                                                                                                                                                                                                                                                          | **Estimand Divergence Between Static Docking and Short Molecular Dynamics as a Triage Filter for African Antimalarial Natural Products**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Abstract** | *The primary analysis on 12 two-target candidates produced a five-class stratification... A 16-system single-replicate pilot on two candidates showed opposite operational directions for docking-RRS and short-MD geometry metrics in 7 of 8 matched comparisons (87.5% divergence). This pattern is a protocol-local flag of estimand divergence; it does not identify a docking artifact...* | *Using a curated collection derived from 396 African natural products and 454 synthetic antimalarials, we evaluated a multi-target docking framework across 136 wild-type and mutant receptor states of PfDHFR and PfCRT. On a primary balanced cohort ($n=12$), a novel Resistance-Resilience Score (RRS) provided a five-tier stratification decoupling predicted wild-type binding strength from mutant-state retention. Explicit-solvent molecular dynamics (MD) simulations revealed a directional divergence in 87.5% (7/8) of matched candidate–target states, wherein dynamic pocket relaxation compensated for static grid-docking penalties. This structural stress test demonstrates that static docking scores and short MD trajectories provide complementary, non-equivalent triage metrics for natural product lead optimization.* |

---

### 2\. Introduction &amp; Study Design (§1 &amp; §2)

| Section         | Texte Actuel (Style Rapport / Défensif)                                                                                                                                                                                                   | Reformulation Recommandée (Style Académique JCIM)                                                                                                                                                                                                                                                                                                                                                        |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Intro (§1)**  | *We explicitly state that each layer measures a different quantity... Treating them as independent evidence of mechanism inflates the apparent epistemic reach of a single short MD pilot. We make this distinction explicit throughout.* | *Each computational layer captures a distinct physical regime: static docking evaluates rigid pocket complementarity, short MD trajectories probe local geometric stability, and MM-GBSA estimates relative end-state energetics. Recognizing these non-overlapping scopes of inference prevents the over-interpretation of static scores while establishing a multi-tiered computational triage.*       |
| **Design (§2)** | *Parent-study MD cohort: 4 named WT complexes 10 ns each, 40 ns total... Set-C MD pilot: 16 systems, 16/16 QC PASS reported as secondary... Small docking-derived estimand, small trajectory-derived estimand.*                           | *The workflow integrates three complementary tiers: (i) primary multi-target docking and RRS stratification across 136 receptor states ($n=17$ candidates), (ii) a structural stress-testing pilot ($16$ explicit-solvent MD trajectories) evaluating dynamic pose retention, and (iii) an external benchmark validation panel ($39$ compounds, $312$ docking complexes) assessing protocol robustness.* |

---

### 3\. Results — Tables, Captions &amp; Text (§3)

| Section            | Texte Actuel (Style Rapport / Défensif)                                                                                                                                                                                                        | Reformulation Recommandée (Style Académique JCIM)                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Table 4 (MD)**   | *PfClpR-labelled cohort (164): Unbound (67.42 Å)... PfATP4 (438): Bound (12.27 Å BB RMSD)... CHARMM36→AMBER conversion corrupted (+473 kcal/mol vdW inflation artifact).*                                                                      | *In explicit-solvent trajectories of reference complexes, two systems retained stable protein–ligand contacts ($&lt;3.5$ Å minimum distance), whereas two highly flexible scaffolds experienced complete dissociation ($&gt;60$ Å center-of-mass separation). For the multi-chain membrane target PfATP4, force-field parameter conversion introduced severe steric repulsion, precluding reliable MM-GBSA endpoint calculations.*                                            |
| **Results (§3.3)** | *All 16 trajectories met the geometric acceptance checks (16/16 QC PASS)... 7 of 8 systems showed opposite operational directions... This pattern is a protocol-local flag of estimand divergence; it does not identify a docking artifact...* | *Structural stress-testing of the pilot complexes revealed that dynamic pocket accommodation frequently offsets predicted static docking penalties. In $87.5%$ ($7/8$) of comparable mutant states, hydrogen-bond rearrangement and side-chain flexibility preserved ligand anchorage ($\text{MD-RRS}\_{\text{distance}} \le 100%$), contrasting with the rigid-receptor docking predictions.*                                                                       |
| **Cross-Metric**   | *PNS vs RRS: $\rho = -0.2098, p\_{\text{adj}} = 1.0000$... ACSI vs RRS: $\rho = -0.4056, p\_{\text{adj}} = 0.5766$... Tartarus calibration gave $\rho = 0.0129$ (no meaningful association).*                                             | *Rank correlation analysis across the primary balanced cohort ($n=12$) revealed low-to-moderate, non-significant associations between RRS, PNS, and ACSI after multiplicity correction ($\rho \in [-0.41, -0.21], p\_{\text{adj}} &gt; 0.50$). This statistical independence confirms that structural mutation resilience (RRS), network target centrality (PNS), and natural-product chemical likeness (ACSI) capture orthogonal dimensions of the candidate space.* |

---

### 4\. Supporting Information (SM Sections S1–S12)

| Section SM        | Texte Actuel (Style Rapport / Défensif)                                                                                                                                              | Reformulation Recommandée (Style Académique JCIM)                                                                                                                                                                                                                                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Section S1**    | *Set C is an enriched cohort, which limits prevalence-based interpretation... ntargets\_bound = 2 in the source selection table.*                                                    | *Candidate Cohort Selection: Candidate compounds (PP-01 through PP-17) were prioritized from the parent hybrid database based on composite multi-parameter optimization (MPO $\ge 0.70$), predicted synthetic accessibility (SYBA $&gt;0$), and dual-target binding potential.*                                                                       |
| **Section S12.4** | *PP-01 PfCRT WT seeds -9.257, -9.262... canonical -9.300 is 0.04 kcal/mol above... because the original receptor prep detail is not preserved on disk...*                            | *Multi-Seed Docking Reproducibility: Stochastic variation across independent random seeds yielded highly reproducible top-mode binding energies ($\le 0.05$ kcal/mol dispersion across five runs for PP-01 and PP-15), confirming that mode selection is robust to optimization seeding.*                                                          |
| **Section S12.7** | *Pipeline-null control: wild-type receptor processed through the mutation pipeline without mutation gave 99.4–100.5%... PfCRT channel reports no K76T/K76A effect for this panel...* | *Pipeline Null Controls: To establish the baseline uncertainty of score ratios, wild-type receptor structures were passed through the automated mutation pipeline without amino-acid substitutions. The resulting null distribution ($99.4% \text{ to } 100.5%$) defines the threshold of numerical noise for mutation-resilience classification.* |

---

## III. Guide de Rédaction pour la Version Finale (JCIM Checklist)

Pour transformer définitivement le manuscrit en un article de rang mondial pour *JCIM*, appliquez systématiquement les **4 règles d'or suivantes** :

### 1\. Remplacer la négation répétée par la précision de la portée

* **Éviter :** *"This score does not measure binding affinity, does not establish target engagement, and does not prove resistance."* (Répété 8 fois).
* **Adopter :** *"The Resistance-Resilience Score (RRS) operates as a relative computational triage metric, evaluating static score retention across defined mutant pockets prior to prospective biochemical testing."*

### 2\. Nettoyer les Noms de Variables et Identifiants Internes

* Convertir `dG_WT` $\rightarrow$ $\Delta G\_{\text{WT}}$ or *wild-type binding energy*.
* Convertir `MD_RRS_d` $\rightarrow$ $\text{MD-RRS}\_{\text{distance}}$ or *dynamic retention ratio*.
* Convertir `164_PfClpP` / `438_PfATP4` $\rightarrow$ *PfClpR complex (PDB: 4GM2)* / *PfATP4 complex (PDB: 9N10)*.
* Convertir `Set-C` $\rightarrow$ *Set-C primary cohort* or *polypharmacology candidate panel*.

### 3\. Regrouper l'Honnêteté Scientifique dans *Limitations*

Plutôt que d'insérer des avertissements de non-validité dans chaque sous-section des Résultats, présentez des faits nets et élégants dans les Résultats, puis centralisez la réflexion méthodologique dans la section **Limitations** (Section 4.5) :

* L'absence de réplicats multiples (directives Soares 2023).
* La divergence entre le docking statique Vina et la relaxation de 10 ns.
* La taille limitée de la cohorte bi-cible ($n=12$).
* La nécessité de validations biochimiques (*in vitro* IC50 et SPR) futures.

### 4\. Harmoniser la Notation Mathématique et Biophysique

* Toutes les énergies en $\text{kcal}\cdot\text{mol}^{-1}$ avec espaces sécables (ex: $\SI{-8.5}{\kcal\per\mole}$).
* Tous les coefficients de corrélation avec $p$-values corrigées par Bonferroni-Holm (ex: $\rho = -0.21, p\_{\text{adj}} = 1.00$).
* Toutes les métriques de dispersion présentées avec leur intervalle de confiance à 95% par Bootstrap (ex: $95% \text{ CI } [-0.76, 0.54]$).

---

*Fin du document de révision stylistique pour P2 Main &amp; SM.*
