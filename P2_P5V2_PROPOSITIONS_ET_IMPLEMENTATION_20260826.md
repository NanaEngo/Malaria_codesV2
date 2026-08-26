# P2 et P5 V2 — propositions d’amélioration scientifique

**Date :** 26 août 2026
**Périmètre :** manuscrit P2 JCIM et manuscrit P5 V2 JCAMD
**Principe :** améliorer l’article à partir des résultats vérifiés, sans ajouter de valeur, de test ou de conclusion non documentés.

## 1. Principes éditoriaux communs

Les deux manuscrits doivent être construits autour de questions scientifiques, et non autour de l’historique d’exécution. Chaque résultat doit être présenté selon l’ordre :

1. question ou hypothèse ;
2. méthode et unité d’analyse ;
3. résultat ;
4. interprétation proportionnée ;
5. limite pertinente.

Les identifiants de jobs, les états SLURM, les journaux d’exécution, les chemins de calcul et les décisions administratives restent dans les DARs et les manifestes, sauf lorsqu’un détail est nécessaire pour comprendre une analyse publiée.

## 2. P2 — ajouts et réorganisation proposés

### 2.1 Tableau question–mesure–portée

Ajouter un tableau conceptuel reliant chaque question à son estimand et à sa portée :

| Question | Mesure | Portée | Ne permet pas de conclure à |
|---|---|---|---|
| Sensibilité mutationnelle prédite | docking-RRS | rétention relative du score | résistance biologique |
| Position chimique | ACSI | position dans des espaces de référence | nouveauté pharmacologique ou activité |
| Contexte de réseau | PNS | pondération topologique du classement | essentialité ou causalité |
| Persistance structurale | analyse MD | compatibilité géométrique d’une pose | affinité expérimentale |
| Résumé énergétique | MM-GBSA | endpoint au sein d’un protocole | énergie libre expérimentale |

**Statut :** à intégrer dans le main ou le Supporting Information selon la place disponible.

### 2.2 Analyse par cible

**Statut :** calculée à partir de `results/c_rrs_classification.csv` et intégrée dans `Table_S12_RRS_By_Target.tex`. Parmi les candidats éligibles, le RRS moyen est de 75.1 pour PfDHFR (12 candidats) et 86.2 pour PfCRT (17 candidats). Ces résumés restent descriptifs et ne sont pas interprétés comme une différence de résistance biologique.

Présenter séparément les résultats PfDHFR et PfCRT lorsque les données vérifiées le permettent. Les distributions et dénominateurs doivent rester distincts ; aucune moyenne combinée ne doit masquer une différence de couverture ou de préparation structurale.

**Statut :** calculée et intégrée ; les chiffres sont descriptifs et limités aux dénominateurs disponibles.

### 2.3 Sensibilité des seuils RRS

Tester, selon un plan fixé avant calcul :

- seuil d’éligibilité WT de `5.0 kcal mol−1` ;
- seuil A*/A de `7.0 kcal mol−1` ;
- seuils de rétention `70 %` et `80 %` ;
- stabilité des classes et du classement.

Les résultats ne doivent pas être recalibrés après observation. S’ils ne sont pas calculés, le manuscrit doit dire que les seuils sont des règles de triage prédéfinies et non des seuils validés biologiquement.

**Statut :** calculé à partir de `results/lightweight_robustness/rrs_threshold_sensitivity.csv` et intégré au SI dans `Table_S11_RRS_Threshold_Sensitivity.tex`. Les résultats montrent que les comptes de classes de référence restent inchangés pour les seuils WT de 4.0–5.0 kcal mol−1, tandis que le resserrement des seuils de rétention à 80/90 % augmente la classe D de 1 à 9 candidats. Ces résultats restent des diagnostics de stabilité, non une calibration biologique.

### 2.4 P2 — discussion expérimentale

Ajouter un paragraphe final bref sur les tests nécessaires : essais enzymatiques PfDHFR WT/mutants et essais de liaison ou de transport PfCRT, avec comparaison prospective au classement RRS. Cette section doit rester une proposition de validation, non un résultat.

**Statut :** intégré lorsque compatible avec la place disponible ; aucun résultat expérimental n’est revendiqué.

## 3. P5 V2 — restructuration recommandée

### 3.1 Résultat principal

Le résultat central doit être formulé ainsi :

> Under the tested panel, split protocols, and training configurations, ECFP4–RF remained the strongest reference model. Topological fusion supplied complementary representation-level signal but did not provide a demonstrated predictive gain.

Cette formulation évite d’étendre le résultat à tous les GNN, Transformers ou jeux de données.

### 3.2 Section de robustesse distincte

Déplacer les éléments suivants hors de `Limitations` vers une sous-section `Robustness analyses` dans `Results` ou `Discussion` :

- panneau ChEMBL disjoint ;
- partitions scaffold supplémentaires ;
- permutation TFP/TNE ;
- stabilité de salience ;
- contrôles kNN et régression logistique ;
- audit de standardisation chimique ;
- analyse des seuils ChEMBL.

La section `Limitations` doit conserver uniquement les limites : panneau unique, labels de screening, choix architecturaux, budget d’entraînement, représentations 2D, proxy scaffold et absence de validation expérimentale.

**Statut :** réorganisation éditoriale réalisée dans la source V2 ; les résultats secondaires restent explicitement distincts du benchmark primaire.

### 3.3 LISH

Conserver LISH dans une sous-section séparée, courte et explicitement orthogonale :

1. tâche phénotypique ;
2. résultat du baseline ;
3. absence de mapping drug–SMILES ;
4. non-comparabilité avec les ROC-AUC moléculaires.

Les détails d’archive, de téléchargement, de chemins locaux et de suivi opérationnel doivent rester hors du manuscrit.

**Statut :** intégré dans la source V2, avec LISH maintenu comme analyse phénotypique orthogonale.

### 3.4 Tableau de design

Ajouter un tableau de synthèse : panel, tâche, baseline, modèles, splits, répétitions, métrique principale, unité statistique, correction multiple et analyse externe.

**Statut :** intégré lorsque compatible avec la place disponible ; aucun résultat expérimental n’est revendiqué.

### 3.5 Tableau des effets

Compléter le tableau principal avec, lorsque déjà disponible :

- différence d’AUC versus ECFP4–RF ;
- unité statistique ;
- p brut ;
- p ajusté ;
- précision de l’incertitude.

Ne pas présenter les cinq moyennes par seed comme 25 observations indépendantes.

**Statut :** partiellement déjà présent ; harmonisation recommandée.

### 3.6 Figure random versus scaffold

Créer une figure seulement si les données graphiques sont disponibles : AUC random en abscisse, AUC scaffold en ordonnée, un point par modèle et diagonale `y=x`. Elle illustrerait la perte de performance sous changement de scaffold sans ajouter de claim.

**Statut :** proposition ; non générée dans cette passe.

## 4. Analyses explicitement non réalisées

Les analyses suivantes ne doivent pas être présentées comme disponibles sans exécution et audit :

- sensibilité quantitative des classes RRS ;
- analyse statistique complète PfDHFR versus PfCRT si les sorties détaillées ne sont pas déjà validées ;
- calibration moléculaire complète des modèles P5 lorsque les probabilités canoniques ne sont pas disponibles ;
- comparaison structure–MoA LISH sans mapping drug–SMILES ;
- nouveau rerun ChemBERTa tant que la campagne reste incomplète.

## 5. Implémentation réalisée le 26 août 2026

La passe complémentaire du 26 août a également ajouté deux tableaux de synthèse au manuscrit P5 V2 : `Table_P5_Study_Design.tex` et `Table_P5_Effect_Summary.tex`. La section de robustesse a été séparée des limitations ; les limitations finales ne conservent que les bornes de portée scientifique.

- P2 : ajout de `Table_S11_RRS_Threshold_Sensitivity.tex` à partir de la sortie auditée de sensibilité des seuils ; intégration d’un résumé dans le main et le SM.
- P2 : ajout de `Table_S12_RRS_By_Target.tex` à partir du CSV canonique ; intégration des moyennes PfDHFR/PfCRT dans la définition de l’analyse RRS.
- P5 V2 : révision éditoriale appliquée dans le dossier V2 et recompilée séparément.
- Aucun calcul MD, docking ou expérimentation biologique n’a été lancé dans cette passe.

## 6. Critères de validation finale

Avant de considérer la révision prête :

- aucun chiffre nouveau sans source vérifiée ;
- concordance des dénominateurs et unités ;
- distinction primaire/secondaire/orthogonale explicite ;
- absence de jargon de suivi dans le texte soumis ;
- absence de revendication causale à partir d’une salience ou d’une prédiction ;
- compilation sans erreur ;
- citations et références croisées résolues ;
- `git diff --check` propre ;
- lecture humaine finale des claims scientifiques.
