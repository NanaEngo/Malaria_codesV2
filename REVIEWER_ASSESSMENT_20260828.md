# Revue sévère — P2, P5 V2, P6

**Date :** 28 août 2026  
**Rôle :** Reviewer sévère + editorial board member rigoureux  
**Cibles :** JCIM (P2), JCAMD (P5 V2), JCAMD (P6)

---

## P2 — "Docking-Based Resistance-Aware Prioritization of Antimalarial Leads"

### Forces
- Séparation claire des estimands (docking-RRS, MD-RRS, MM-GBSA, PNS, ACSI)
- Limites scientifiques explicitement bornées à chaque étape
- Réplication externe complète (312/312) avec bootstrap
- Compilé sans erreur, 0 référence indéfinie

### Commentaires MAJEURS (nécessitent action avant soumission)

**M1. Absence de TOC graphique.**  
Le `\begin{tocentry}` est vide avec un commentaire disant "asset not present". JCIM exige un graphical abstract. Sans ce fichier, la soumission sera rejetée au desk.

**M2. Titre trop long (16 mots).**  
JCIM recommande ≤12 mots. Le titre actuel mélange méthodes et résultats. Proposition :  
*"Resistance-Aware Docking Prioritization of Antimalarial Leads from African Natural Products"*

**M3. Abstract trop dense (≈280 mots).**  
JCIM limite les abstracts à ≈150 mots. L'abstract actuel contient des résultats secondaires (PNS, ACSI, MM-GBSA) qui devraient aller dans le SI.

**M4. Référence `value_addition_african_np_2025` dans le texte principal.**  
Cette référence est citée dans l'Introduction et la Discussion. Vérifier que le texte cité correspond bien au papier Mayoka et non à une source alternative.

**M5. Table S15 — comparaison primaire/externe non explicitement discutée.**  
La réplication externe est ajoutée à la Conclusion mais pas discutée dans la section Discussion. Un reviewer demandera : comment les 39 ligands externes se comparent-ils aux 17 candidats Set-C en termes de couverture chimique ?

### Commentaires MINEURS

**m1.** Ligne 430 : `\qty{101.000}` dans la fraction Class-A bootstrap — semble être une erreur (devrait être `1.000`).

**m2.** La section "Consensus leads" (l. ~340) est vague : "intersection of high-RRS, high-ACSI, high-PNS" — combien de candidats exactement ?

**m3.** Les keywords contiennent "binding free energy" mais le texte dit explicitement que les scores Vina ne sont PAS des énergies de liaison. Supprimer "binding free energy" des keywords.

**m4.** Le paragraphe "Use of Artificial Intelligence" devrait être dans une section `\section*{}` plutôt qu'en texte courant.

---

## P5 V2 — "Scaffold-Controlled Evaluation of Molecular Representations"

### Forces
- Question scientifique claire et bornée
- Protocole de validation interne robuste (5 seeds × 5 folds)
- Initialisation fold-indépendante pour ChemBERTa (rarement rapportée)
- Salience vs. nécessité correctement distinguée
- Compilé sans erreur, 0 référence indéfinie

### Commentaires MAJEURS

**M1. Abstract non structuré.**  
JCAMD n'exige pas d'abstract structuré, mais l'abstract actuel fait ≈200 mots et mélange résultats primaires et secondaires. Réduire à ≈150 mots en ne gardant que le résultat principal.

**M2. La figure `p5_learning_curves` n'est pas décrite dans le texte.**  
Le texte dit "Validation trajectories across 50 training epochs document the optimization path" mais ne dit pas quelles courbes sont visibles ni combien de folds. La légende de la figure est générique.

**M3. Le paragraphe "Why fingerprints hold" est trop long (≈120 mots).**  
Il contient des répétitions de l'Introduction. Le reviewer demandera de le condenser.

**M4. La section "Robustness analyses" (l. ~195-200) est un bloc monolithique de ≈800 mots.**  
Diviser en sous-sections : (a) ChEMBL transfer, (b) GNN sensitivity, (c) ChemBERTa rerun, (d) Extended scaffold partitions, (e) Lightweight controls.

**M5. `ecfp_pretrained_2026` dans le bib mais pas cité dans le texte.**  
Vérifier s'il y a une référence orpheline.

### Commentaires MINEURS

**m1.** Le mot "emph" est utilisé à la place de `\emph{}` dans un endroit (ligne ~182 : "emph{almost no neural embedding}").

**m2.** La table `Table_P5_Effect_Summary.tex` est inputée mais pas référencée par `\cref`. Ajouter une référence.

**m3.** La section "List of Abbreviations" est inhabituelle pour JCAMD. La plupart des journaux la suppriment.

**m4.** Le paragraphe "Author contributions" dit "MVST conceived the study... and wrote the manuscript" — trop vague pour CRediT. Détailler les rôles.

---

## P6 — "Leakage-aware structure–phenotype prediction of MoA profiles"

### Forces
- Question scientifique pertinente et actuelle
- Contrôle de fuite (collision groups) rigoureux
- Résultat négatif honnêtement présenté
- Limites explicitement bornées

### Commentaires MAJEURS

**M1. Manuscrit trop court (5 pages).**  
JCAMD accepte des articles jusqu'à ≈25 pages. À 5 pages, le manuscrit manque de profondeur méthodologique. Il faut au minimum :
- une section Methods détaillée (modèles, hyperparamètres, protocole d'entraînement)
- une section Results plus complète (tableaux par split, par modèle)
- une Discussion approfondie

**M2. Absence de tableau principal format JCAMD.**  
La Table 1 unique ne montre que les résultats collision-group. Il manque :
- résultats par split (random, scaffold)
- intervalles de confiance
- comparaison avec les baselines (ECFP4-RF, phenotype-only)
- métriques secondaires (AUPRC, Brier, ECE)

**M3. Auteur non défini.**  
"Author list to be completed by the accountable authors" — inacceptable pour une soumission.

**M4. Pas de cover letter.**  
JCAMD exige une cover letter.

**M5. `\bibliography{references_pending}` — le nom du fichier est trompeur.**  
Renommer en `references.bib` ou `Bibliography_P6.bib`.

**M6. La discussion ne compare pas avec les résultats P5.**  
P6 utilise les mêmes modèles que P5 sur un dataset différent. Le reviewer demandera : pourquoi les résultats sont-ils différents ? (réponse : dataset, labels, task — mais il faut le dire explicitement).

### Commentaires MINEURS

**m1.** L'abstract ne mentionne pas le nombre de molécules uniques (1722) ni le nombre de collision groups (794).

**m2.** La section "Materials and methods" manque de détails sur :
- optimizer (AdamW ? learning rate ?)
- early stopping criteria
- hardware utilisé
- temps d'entraînement

**m3.** La figure `tab:p6_primary` n'est pas dans un environnement `figure` mais dans un `table`. Cohérence.

**m4.** Les références `tanner2025pfcrt` et `largermodels2026` sont dans le bib mais pas citées dans le texte. Les supprimer ou les citer.

---

## Priorités d'action par manuscrit

### P2 (avant soumission JCIM)
1. 🔴 Créer le graphical abstract (TOC entry)
2. 🔴 Réduire le titre à ≤12 mots
3. 🔴 Réduire l'abstract à ≈150 mots
4. 🟡 Corriger `\qty{101.000}` → `\num{1.000}`
5. 🟡 Définir précisément le nombre de candidats "consensus"
6. 🟡 Supprimer "binding free energy" des keywords

### P5 V2 (avant soumission JCAMD)
1. 🔴 Réduire l'abstract à ≈150 mots
2. 🔴 Diviser la section "Robustness analyses" en sous-sections
3. 🟡 Décrire les learning curves dans le texte
4. 🟡 Condenser "Why fingerprints hold"
5. 🟡 Vérifier `ecfp_pretrained_2026` orphelin
6. 🟡 Détailler CRediT

### P6 (avant soumission JCAMD)
1. 🔴 Étendre à ≈10-15 pages minimum
2. 🔴 Définir les auteurs
3. 🔴 Ajouter une cover letter
4. 🔴 Ajouter une section Methods complète
5. 🔴 Ajouter des tableaux par split avec IC
6. 🟡 Renommer `references_pending.bib`
7. 🟡 Comparer explicitement avec P5
