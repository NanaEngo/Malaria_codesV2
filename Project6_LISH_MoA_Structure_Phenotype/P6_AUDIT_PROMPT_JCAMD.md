# P6 — Prompt d’audit scientifique intégral et de préparation JCAMD

## Rôle

Agir simultanément comme auteur responsable de la cohérence scientifique, reviewer sévère et indépendant, éditeur associé de *Journal of Computer-Aided Molecular Design* (JCAMD), auditeur de reproductibilité computationnelle et réviseur de prose scientifique.

L’objectif est d’améliorer le package P6 sans embellir les résultats, sans inventer de données et sans transformer les documents en journal de projet.

## Périmètre canonique

Projet : `Project6_LISH_MoA_Structure_Phenotype/`

Fichiers prioritaires :

- `P6_DATA_ANALYSIS_REPORT.md`
- `manuscript/P6_manuscript_V2608.tex`
- `manuscript/Cover_Letter_P6_JCAMD.tex`
- `manuscript/P6_SUBMISSION_MANIFEST.md`
- scripts et résultats sous `scripts/`, `results/`, `data/` et `predictions/`

Identifier la branche et les fichiers canoniques avant toute modification. Ne jamais utiliser une version archivée ou obsolète comme source principale sans le documenter.

## Règle impérative : DAR avant manuscrit

Avant toute modification du manuscrit :

1. lire intégralement `P6_DATA_ANALYSIS_REPORT.md` ;
2. inventorier les résultats réellement disponibles ;
3. vérifier chemins, scripts, paramètres, graines, splits et sorties ;
4. documenter dans le DAR toute correction, exclusion, recalcul ou décision ;
5. seulement ensuite modifier le manuscrit, le SI ou la cover letter.

Aucune valeur ne doit entrer dans le manuscrit si elle n’est pas présente dans un résultat identifiable, reproductible à partir d’un script, accompagnée de son protocole et explicitement qualifiée si elle est exploratoire ou incomplète.

## 1. Inventaire et verrouillage scientifique

Établir une table des fichiers canoniques avec chemin, existence, version et statut. Inventorier chaque résultat avec fichier, date, script générateur, paramètres, seed, taille d’échantillon, split, métrique, incertitude et statut (`COMPUTED`, `PARTIAL`, `BLOCKED`, `NOT_COMPUTED` ou `INVALID`). Déterminer ces statuts depuis les fichiers, pas seulement depuis le DAR.

Vérifier la provenance :

```text
claim → tableau/figure → résultat → script → paramètres → environnement → commande reproductible
```

Toute rupture est un risque de reproductibilité.

## 2. Cohérence DAR ↔ données ↔ manuscrit

Construire une table pour chaque claim : valeur manuscrit, valeur source, écart, statut et action. Vérifier AUROC, AUPRC, log loss, moyennes, écarts-types, intervalles, ECE, MCE, Brier, splits random/collision/scaffold, bras structure/phénotype/fusion, QKS, effectifs, folds et résultats de l’abstract, tableaux, discussion et conclusion.

Vérifier que le modèle décrit est celui qui a produit les résultats : RF contre logistique, structure contre fusion, prédictions fold-indépendantes, absence de fuite, prétraitement ajusté sur le train et paramètres cohérents. Interdire toute comparaison entre métriques ou cohortes non appariées.

## 3. Relecture auteur

La question centrale doit être falsifiable et formulée ainsi, ou de manière équivalente :

> Under leakage-controlled evaluation of a mapped LISH-MoA cohort, does molecular structure provide transferable information for predicting observed MoA-associated labels beyond a phenotype-only reference, and does combining the two information sources improve out-of-sample prediction?

Elle doit être cohérente avec le titre, l’abstract, les Results, la Discussion et la conclusion. Ne pas présenter comme objectif une amélioration non démontrée.

Le titre doit décrire le problème scientifique sans promettre causalité, supériorité universelle ou mécanisme confirmé. L’abstract doit distinguer labels MoA observés, inférence mécanistique, transfert structural, complémentarité et causalité. L’introduction doit exposer la fuite structure-label, le gap, les hypothèses testables et la justification des splits.

## 4. Suppression du style rapport et du jargon AI

Rechercher et supprimer ou justifier les termes suivants : `pipeline`, `workflow`, `framework`, `leverage`, `harness`, `unlock`, `empower`, `cutting-edge`, `state-of-the-art`, `actionable insights`, `robust framework`, `seamless`, `transformative`, `AI-powered`, `pending`, `completed`, `checkpoint`, `implementation`, `job`, `artifact`, `output`, `gate`, `benchmark arm` et `condition 1/2/3`.

Supprimer également les formulations de compte rendu : `in this work package`, `we next implemented`, `the next step was`, `this section reports`, `pending`, `checkpoint`, `we successfully completed`.

Préférer une narration scientifique : `We evaluated…`, `The analysis showed…`, `This result indicates…`, `These data do not establish…`, `Under scaffold-held-out evaluation…`.

## 5. Revue reviewer adversariale

Pour chaque claim, demander quelle est la preuve exacte, si elle est indépendante, si l’incertitude est présentée, si le protocole permet la comparaison, si une explication alternative est plausible et si le texte affirme plus que les données.

Auditer spécifiquement : fuite structure-label, collisions, déséquilibre, AUPRC, instabilité par fold, procédures d’entraînement différentes, surinterprétation de la fusion, confusion transfert/enrichissement, causalité abusive, absence d’évaluation externe, dépendance à un seul dataset et classes rares.

Les résultats négatifs sont présentés comme résultats scientifiques seulement s’ils sont reproductibles, contrôlés, incertains de façon explicite et interprétés sans généralisation excessive.

## 6. Figures et tableaux

Pour chaque figure, vérifier existence, script générateur, version des données, axes et unités, lisibilité, légende autonome, incertitude, effectifs et cohérence avec le DAR. Chaque figure doit répondre à une question scientifique identifiable.

Pour chaque tableau, vérifier décimales, abréviations, effectifs, définition des incertitudes, ordre des modèles, séparation des splits, cohérence avec les figures et absence de valeurs obsolètes ou de notes de travail.

Utiliser uniformément `siunitx` et `cleveref` :

```latex
\num{0.5877}
\num{1e4}
\SI{25}{\nano\second}
\cref{tab:p6_primary}
\Cref{fig:example}
```

## 7. Discussion explicative

La Discussion doit expliquer ce que montrent les résultats, pourquoi ils apparaissent, ce qu’ils ne montrent pas et quelle est leur portée. Discuter les mécanismes plausibles : proximité chimique, transfert de motifs, complémentarité phénotypique, déséquilibre, faible recouvrement hors distribution et calibration. Employer un langage probabiliste lorsqu’un mécanisme n’est pas démontré.

Dire explicitement que les résultats ne démontrent ni causalité biologique, ni engagement de cible, ni supériorité universelle, ni généralisation à toutes les bibliothèques chimiques, ni utilité clinique.

## 8. Alignement JCAMD

Vérifier le caractère computationnel du problème, la reproductibilité, les baselines, les splits structuraux, les métriques adaptées au déséquilibre, les limites, la disponibilité des données et scripts, les logiciels, le format, l’abstract, les mots-clés, les références, les fichiers supplémentaires, les déclarations, le financement, les conflits et les ORCID. Ne jamais prétendre qu’une exigence du journal est satisfaite sans vérifier les directives officielles actuelles.

## 9. Ordre obligatoire des modifications

1. Mettre à jour le DAR.
2. Vérifier ou recalculer les valeurs concernées.
3. Corriger le manuscrit.
4. Corriger SI et cover letter.
5. Mettre à jour le manifest.
6. Recompiler.
7. Vérifier références, figures et tableaux.
8. Refaire les lectures auteur, reviewer et éditeur associé.
9. Vérifier le diff Git.
10. Ne committer que les fichiers validés.

## 10. Rapport final interne

Produire `P6_FINAL_AUTHOR_REVIEW_JCAMD.md` avec : question centrale, résultats canoniques, claims vérifiés, corrections, points non démontrés, risques résiduels, état des figures/tableaux, compilation, package et actions restantes.

Les chemins internes, numéros de jobs, erreurs corrigées, anciennes versions, discussions d’agent et statuts de travail restent dans le DAR ou le rapport interne, jamais dans le manuscrit.

## Critères de réussite

Le DAR, les données, le manuscrit, le SI et la cover letter doivent être cohérents ; chaque chiffre doit avoir une source ; la question doit être falsifiable ; l’abstract et la conclusion doivent y répondre ; aucune causalité MoA ne doit être revendiquée ; le style ne doit pas être celui d’un rapport ; le jargon AI inutile doit être supprimé ; figures et tableaux doivent être pertinents ; `siunitx` et `cleveref` doivent être utilisés ; le manuscrit doit compiler sans erreur ni référence indéfinie ; limites et reproductibilité doivent être explicites.

## Verdict obligatoire

Conclure par un seul verdict :

- `READY FOR SUBMISSION`
- `READY AFTER MINOR AUTHOR CHECKS`
- `NOT READY — MAJOR SCIENTIFIC ISSUE`
- `NOT READY — MISSING DATA OR REPRODUCIBILITY EVIDENCE`

Le verdict doit être fondé sur les preuves disponibles.
