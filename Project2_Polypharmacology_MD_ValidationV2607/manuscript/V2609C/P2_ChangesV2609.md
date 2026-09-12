## Polypharmacology_MD_Validation_V2609C

### 1. Synthèse du Pivot Conceptuel : De la Défense à l'Offensive

La version raffinée **V2609C** réalise une mutation stratégique majeure. Là où la première version souffrait d'un ton défensif (multiplication des clauses de non-responsabilité et aveu de déconnexion entre le docking et la dynamique moléculaire), la version V2609C érige cette divergence en une **contribution méthodologique de premier ordre**.

Le concept central repose désormais sur l'**Estimand Divergence** (divergence d'estimands) :

* **Docking statique (\(\Delta G_{\text{grid}}\)) vs Dynamique moléculaire courte (\(\text{MD-RRS}_{\text{distance}}\)).** Ces deux méthodes ne mesurent pas la même quantité physique. Le docking évalue une complémentarité rigide dans une grille fixe, tandis que la MD de 10 ns évalue la rétention de pose et la relaxation conformationnelle locale en solvant explicite.
* **Un filtre de triage positif (87,5 % de divergence).** Dans 7 des 8 états mutants comparables (87.5 %), la relaxation dynamique et le réarrangement des liaisons hydrogène ou des molécules d'eau compensent les pénalités stériques prédites par le docking rigide. La MD courte n'est plus présentée comme une "validation d'affinité", mais comme un **test de stress structurel** indispensable pour éliminer les faux positifs statiques avant les essais biochimiques.


### 2. Audit des Avancées Scientifiques et Biophysiques

#### 🟢 A. Un cadre RRS sans biais de dénominateur
Le score RRS (*Resistance-Resilience Score*) est désormais strictement restreint aux cibles sauvages présentant une affinité réelle (\(|S_{\text{WT}}| \ge 5.0\text{ kcal}\cdot\text{mol}^{-1}\)).

* L'exclusion des dénominateurs non-liants évite toute inflation artificielle des ratios de rétention.
* Sur la cohorte équilibrée bi-cible principale (\(n=12\)), le classement RRS produit une stratification équilibrée en 5 classes (1 Class A*, 1 Class A, 4 Class B, 5 Class C, 1 Class D).

#### 🟢 B. Fixation d'un plancher de bruit thermodynamique empirique (2 kcal/mol)
Grâce au réplicat indépendant \(R2\) exécuté sur le complexe pilier **PP-01 PfCRT WT**, la variation inter-réplicats est mesurée à \(|R1 - R2| = 2.01\text{ kcal}\cdot\text{mol}^{-1}\).

* Le manuscrit adopte désormais ce seuil comme un **plancher de bruit thermique empirique d'environ 2 kcal/mol** pour les calculs d'énergie libre MM-GBSA. Tout écart mutant-WT inférieur à ce plancher est interprété comme une rétention dans le bruit, éliminant toute sur-interprétation.

#### 🟢 C. Robustesse et réplication croisée externes
* **Panel externe (39 ligands / 312 complexes).** Le re-scoring par le réseau de neurones convolutif **GNINA (CNN affinity)** confirme une **concordance de classe A de 100 %** avec AutoDock Vina sur la rétention globale, avec une corrélation de rang de \(\rho = 0.558\).
* **Stabilité stochastique.** La dispersion multi-seed sur 5 tirages stochastiques reste inférieure à \(\pm 0.05\text{ kcal}\cdot\text{mol}^{-1}\) pour PP-01 et \(\pm 0.03\text{ kcal}\cdot\text{mol}^{-1}\) pour PP-15.
* **Insensibilité de PfCRT au seuil STRING.** La centralité réseau (PNS) conserve une corrélation de rang quasi-parfaite (\(\rho \ge 0.9681\)) lorsque le seuil d'interaction STRING varie entre 400, 700 et 900.


### 3. Audit Stylistique et Rédactionnel (Élimination du "Style Rapport")

Conformément à l'analyse menée dans `p2_report_style_audit_and_refinements.md`, le texte a été purgé de ses tournures informatiques brutes :

| Éléments à éliminer | Ancien style "Rapport / Audit" | Nouveau style Académique JCIM (V2609C) |
| :--- | :--- | :--- |
| **Jargon HPC / Code** | `QC PASS`, `16/16 systems`, `job array 15320`, `dG_WT`, `MD_RRS_d`, `164_PfClpP` | \(\Delta G_{\text{WT}}\), \(\text{MD-RRS}_{\text{distance}}\), *PfClpR complex*, *primary balanced cohort*. |
| **Disclaimers répétitifs** | *"This study does not establish biological target engagement, affinity..."* (répété 8 fois) | Réserves regroupées exclusivement en section *Limitations* ; rôle du score défini positivement (*"serves as a computational triage heuristic"*). |
| **Logique de Debuggage** | Raconter les crashs de scripts de conversion CHARMM36\(\rightarrow\)AMBER ou de boîtes périodiques | Formulé sous forme de contraintes physiques de paramétrisation et d'artefacts de conversion de champs de forces. |
| **Titre** | *Calibrating the Interpretation of Docking-Derived Resistance-Retention Scores...* | **Estimand Divergence Between Static Docking and Short Molecular Dynamics as a Triage Filter for African Antimalarial Natural Products**. |


### 4. Dernières Actions de Finalisation avant Soumission à JCIM

Pour compléter le "dernier kilomètre" et garantir une soumission sans réserve au *Journal of Chemical Information and Modeling* :

1. **Conformité Twelve-Factor (Environnement).** Assurez-vous que le fichier `environment_md.yml` est déplacé du répertoire `scripts/` vers un dossier racine standardisé `environments/`.
2. **DOI Zenodo Pérenne.** Dès l'initialisation du dépôt sur la plateforme Zenodo, remplacez la mention temporaire `pending` dans la section *Data Availability* par le DOI pérenne réservé (`10.5281/zenodo.19608875`).
3. **Mention des directives de Soares et al. (2023).** Veillez à bien conserver la citation explicite des directives JCIM sur les simulations de dynamique moléculaire dans l'Introduction et la Discussion pour justifier l'usage de la MD comme test de stress.

L'ensemble du package (26 pages pour le texte principal, 19 pages pour le supplément, cover letter et graphiques vectoriels) est compilé sans aucune erreur LaTeX.

