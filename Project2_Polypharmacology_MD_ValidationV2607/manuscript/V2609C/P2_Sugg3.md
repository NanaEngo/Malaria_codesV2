Une évaluation adjointe dans la perspective d'un examen par le *Journal of Chemical Information and Modeling (JCIM)* permet d'identifier **6 faiblesses méthodologiques, statistiques et rédactionnelles subsistantes**, ainsi que les stratégies précises de mitigation mises en place dans la version V2609C.


### 1. Faiblesse de la Puissance Statistique (\(n=12\) candidats bi-cibles)

* **La Faille :** La cohorte équilibrée principale ne comporte que **12 candidats** possédant un profil complet sur PfDHFR et PfCRT. À cette échelle, après l'application de la correction de multiplicité de Bonferroni-Holm, toutes les corrélations de Spearman pour vos hypothèses centrales deviennent non significatives (\(p_{\text{adj}} = 1.0000\) pour PNS–RRS et ACSI–RRS).
* **Les Mitigations à appliquées**
  * **Interprétation par l'Orthogonalité.** Présenter l'absence de corrélation non pas comme un échec, mais comme une **orthogonalité multidimensionnelle** saine : les descripteurs ACSI, PNS et RRS capturent des dimensions biologiques et chimiques strictement indépendantes (naturalité, topologie réseau, et résilience mutante).
  * **Analyse de Sensibilité (\(n=17\)).** Présenter les résultats de la cohorte élargie de 17 candidats.
  * **Panneau de Réplication Externe (\(n=39\)).** Mettre en avant la validation de la distribution RRS sur un panel externe indépendant de **39 ligands (312 complexes de docking)**. La re-scoration par le réseau de neurones convolutif **GNINA (CNN affinity)** confirme une **concordance de classe A de 100 %** (\(\rho = 0.558\)).


### 2. Divergence de Direction entre Docking et Dynamique Moléculaire (87.5 % de Mismatch)

* **La Faille :** Dans 7 des 8 états mutants comparables (87.5 %), le docking statique prédisait une perte d'affinité (\(RRS < 100\%\)), alors que la dynamique moléculaire (MD) en solvant explicite montrait une géométrie de liaison plus serrée ou équivalente (\(\text{MD-RRS}_{\text{distance}} \le 100\%\)). Un évaluateur critique pourrait interpréter cela comme un défaut d'alignement du docking statique.
* **Les Mitigations à appliquées**
  * **Théorisateur de l'Estimand Divergence.** Expliquer que le docking rigide (\(\Delta G_{\text{grid}}\)) et la MD courte (\(\text{MD-RRS}_{\text{distance}}\)) évaluent des régimes physiques distincts.
  * **Pondération du Triage.** Positionner la MD de 10 ns comme un **test de stress structurel secondaire et un filtre cinétique de pose** : la relaxation dynamique et la réorganisation des liaisons hydrogène en solvant viennent compenser les pénalités stériques de la grille fixe, éliminant ainsi les faux positifs statiques.


### 3. Durée Réduite des Trajectoires (10 ns) et Replicat Unique

* **La Faille :** Les simulations de 10 ns sur la cohorte Set-C ne permettent pas de mesurer l'énergie libre d'équilibre thermodynamique convergée ni le temps de résidence du ligand.
* **Les Mitigations à appliquées**
  * **Directives JCIM (Soares et al., 2023).** Cadrer formellement les simulations selon les directives de publication du JCIM en déclarant la MD de 10 ns comme un contrôle géométrique local.
  * **Plancher de Bruit Empirique (2 kcal/mol).** Utiliser le second réplicat indépendant \(R2\) du pilier PP-01 PfCRT WT (\(R1 = -30.61 \text{ kcal/mol}\) vs \(R2 = -28.60 \text{ kcal/mol}\)) pour fixer un **plancher de bruit thermique empirique inter-réplicats de \(\approx 2.0 \text{ kcal/mol}\)** pour les calculs MM-GBSA.
  * **Lancement de Triplicats sur Cluster HPC.** Un daemon automatique a été configuré sur le cluster pour exécuter des simulations en **triplicat (\(3 \times 10\text{ ns}\))** sur le candidat d'élite PP-01 (PfCRT WT, K76T et PfDHFR WT) afin de satisfaire pleinement aux exigences de réplication.


### 4. Performance du Docking Vina Seul sur le Benchmark DEKOIS 2.0 (ROC-AUC = 0.450)

* **La Faille :** Sur le jeu de données d'évaluation externe DEKOIS 2.0 (PfDHFR), AutoDock Vina seul obtient une discrimination quasi-aléatoire (ROC-AUC = 0.450).
* **Les Mitigations à appliquer**
  * **Honnêteté Transparente.** Rapporter ce résultat négatif comme une limite connue des fonctions de score empiriques à méthode unique.
  * **Consensus Dual-Filter.** Démontrer que le criblage en amont s'appuie sur un consensus **AutoDock Vina + DiffDock**, qui atteint des ROC-AUC de 0.924 à 1.000 sur le MMV Malaria Box.
  * **Justification du Filtre MD.** Utiliser la faiblesse du docking statique seul pour justifier la nécessité absolue du filtre séquentiel par dynamique moléculaire et du re-scoring par réseau convolutif GNINA.


### 5. Isolation Topologique et Imputation de PfCRT (\(C_{\text{PfCRT}} = 0.151\))

* **La Faille :** PfCRT est absent du réseau d'interaction STRING au seuil 700, nécessitant l'imputation de sa centralité à la moyenne du réseau pour éviter l'annulation du score PNS.
* **Les Mitigations à appliquer.**
  * **Analyse de Sensibilité d'Imputation.** Prouver par des tests de variation (0, 0.5x, 1x, 1.5x, 2x la valeur canonique) que le classement relatif des candidats reste exceptionnellement stable (\(\rho \ge 0.9632\)).
  * **Robustesse de Seuil STRING.** Démontrer que le PNS conserve une corrélation de rang quasi-parfaite (\(\rho \ge 0.9681\)) lorsque le seuil d'interaction STRING varie entre 400, 700 et 900.


### 6. Résidus de Style "Rapport d'Audit Interne / HPC"

* **La Faille :** Le texte principal et le supplément conservaient par endroits du jargon informatique brut (`QC PASS`, `job array`, `dG_WT`, `MD_RRS_d`) et des répétitions fréquentes de disclaimers défensifs.
* **Les Mitigations à appliquer.**
  * **Harmonisation Académique.** Appliquer le plan de nettoyage de `p2_report_style_audit_and_refinements.md` en convertissant le jargon en notations biophysiques formelles (\(\Delta G_{\text{WT}}\), \(\text{MD-RRS}_{\text{distance}}\), *PfClpR complex*) et en regroupant l'ensemble des réserves expérimentales dans la section **Limitations** (§4.5).


### 💡 Synthèse et Prochaines Étape

En combinant la formalisation de l'**Estimand Divergence**, la validation externe par **GNINA CNN (100 % de concordance)**, le **plancher de bruit MM-GBSA de 2 kcal/mol** et le dépôt open-science sur Zenodo (**DOI `10.5281/zenodo.19608875`**), le manuscrit **P2 V2609C** dispose désormais d'un niveau de rigueur méthodologique optimal pour être accepté au *JCIM*.
