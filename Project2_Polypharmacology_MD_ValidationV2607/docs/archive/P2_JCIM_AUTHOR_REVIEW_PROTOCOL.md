# P2 — Protocole d’audit auteur et de préparation JCIM

**Version:** 1.0  
**Portée:** DAR, manuscrit V2609, Supporting Information V2609, cover letter, résultats, scripts et manifestes P2  
**Environnement scientifique:** `malaria_md`  
**Règle:** `DAR avant manuscrit`

## Objectif

Auditer et améliorer le projet P2 afin que le manuscrit soit une étude scientifique de calibration et de triage computationnel, et non un rapport d’exécution. Toute affirmation doit être soutenue par une source canonique, une méthode identifiable et une limite d’interprétation explicite.

## Principes impératifs

1. Lire `AGENTS.md`, le DAR P2, les runbooks, les manifestes et les README avant toute modification.
2. Le DAR est la source de vérité. Toute correction du manuscrit est précédée d’une correction du DAR.
3. Distinguer les résultats primaires, secondaires, exploratoires, techniques, exclus et non calculés.
4. Ne jamais inventer de données, DOI, méthodes, paramètres, auteurs, financement ou validation.
5. Ne pas présenter une trajectoire unique comme une campagne de réplicats.
6. Ne pas présenter un score de docking, un MD-RRS géométrique ou un MM-GBSA endpoint comme une mesure biologique, une affinité convergée ou une résistance expérimentale.
7. Conserver les échecs numériques et les exclusions dans le DAR, sans les transformer en conclusions positives.
8. Ne pas supprimer un fichier scientifique avant vérification de sa non-canonicité, de son absence de référence et de son absence de rôle de provenance.

## Phase 1 — Cartographie de l’évidence

Construire une matrice :

| ID | Claim | Localisation DAR | Source primaire | Valeur source | Valeur DAR | Statut | Action |
|---|---|---|---|---|---|---|---|

Vérifier :

- nombres de candidats, systèmes, cibles, mutants et snapshots ;
- cohorte complète à deux cibles et cohorte PfCRT-only ;
- cohorte parent-study et cohorte Set-C ;
- RRS, PNS, ACSI, classes A*/A/B/C/D ;
- corrélations, permutations, bootstrap et corrections de multiplicité ;
- MD-RRS, distances minimales, bound fraction et contacts ;
- MM-GBSA, SEM, SD intra-trajectoire et SD propagée ;
- résultats DEKOIS, GNINA, P2Rank, ProLIF et redocking multi-seed ;
- exclusions, échecs PBC, échecs numériques et résultats non reportables.

Pour chaque valeur, consigner le dénominateur, l’unité, la provenance et la limite d’inférence.

## Phase 2 — Statuts et provenance

Rechercher les états suivants : `COMPUTED`, `COMPLETE`, `PASS`, `FAILED`, `FAILED_NUMERICAL_QC`, `NOT_COMPUTED`, `NOT_REPORTABLE`, `PENDING`, `EXCLUDED`, `ARCHIVED`, `SUPERSEDED`, `BY DESIGN`.

Vérifier que :

- les jobs terminés ne sont plus indiqués comme actifs dans les sections courantes ;
- les anciens états sont explicitement marqués `SUPERSEDED` ;
- le job, le script, l’environnement, les entrées, sorties, hashes et règles QC sont identifiables ;
- les paramètres de grille, préparation des ligands, force fields et protocoles sont distingués ;
- les analyses non indépendantes ne sont pas présentées comme validations externes.

## Phase 3 — Relecture scientifique auteur

Relire dans l’ordre : titre, abstract, introduction, méthodes, résultats, discussion, limitations, conclusion, SI et cover letter.

Pour chaque section, vérifier :

- question scientifique explicite ;
- estimand défini ;
- cohorte et dénominateur visibles ;
- résultats négatifs visibles ;
- incertitude correctement qualifiée ;
- séparation entre observation et interprétation ;
- alternatives explicatives présentes ;
- généralisation limitée au protocole et aux données ;
- distinction entre docking, géométrie MD, endpoint MM-GBSA et preuve biologique ;
- absence de conclusion clinique ou mécanistique non mesurée.

## Phase 4 — Suppression du report-style

Le manuscrit ne doit pas contenir de journal d’exécution, de liste de tâches ou de commentaire de gestion de projet.

À retirer ou transformer :

- IDs de jobs SLURM ;
- chemins complets de fichiers ;
- dates de lancement ;
- `pending`, `blocked`, `done`, `action required` ;
- « we verified », « we corrected », « previous version », « for submission » ;
- descriptions de copies de fichiers ou d’étapes internes.

Transformer les opérations en énoncés scientifiques :

> Periodic-boundary reconstruction was applied before endpoint analysis. Systems that failed numerical quality control were excluded from interpretation.

et non :

> We fixed the PBC problem and reran the job.

Les détails opérationnels restent dans le DAR et les manifestes, pas dans la prose scientifique.

## Phase 5 — Suppression de l’AI-jargon

Rechercher et reformuler les termes vagues ou promotionnels : `leverage`, `harness`, `unlock`, `empower`, `seamless`, `holistic`, `comprehensive`, `cutting-edge`, `state-of-the-art`, `powerful`, `novel`, `transformative`, `actionable insights`, `sheds light`, `paves the way`, `robust framework`, `game-changing`, `remarkably`, `exciting`, `unique opportunity`.

Remplacer par des formulations mesurables et falsifiables. Ne pas supprimer les termes scientifiques légitimes comme `robustness analysis`, `sensitivity analysis`, `structural retention` ou `endpoint estimate` lorsqu’ils sont définis.

## Phase 6 — Alignement JCIM

Vérifier :

- titre informatif et non promotionnel ;
- abstract autonome ;
- Introduction centrée sur une question et un gap ;
- Methods reproductibles ;
- Results séparés des interprétations ;
- Discussion explicative ;
- Limitations quantitatives ;
- conclusion proportionnée.

Les Methods doivent préciser logiciels et versions, force fields, paramétrisation, protonation, pH, température, sel, grilles, exhaustivité, préparation des ligands et récepteurs, modèles mutants, critères d’exclusion, définitions RRS/MD-RRS/MM-GBSA, PBC, frames, QC, réplication, seeds, tests statistiques, correction de multiplicité et disponibilité des données.

## Phase 7 — Audit adverse

Évaluer chaque claim selon :

| Claim | Evidence | Alternative explanation | Vulnerability | Mitigation | Residual risk |
|---|---|---|---|---|---|

### Reviewer méthodologie

- Les grilles et préparations sont-elles reproductibles ?
- Les seuils sont-ils calibrés ou opérationnels ?
- Les analyses partagent-elles la même cohorte ?
- Les résultats dépendent-ils d’un seul protocole ?

### Reviewer MD

- La durée et les réplicats sont-ils adaptés à la claim ?
- Les trajectoires dissociées sont-elles rapportées ?
- PBC et BOND overflow sont-ils traités honnêtement ?
- SEM et SD sont-ils correctement distingués ?

### Reviewer biologie

- La pertinence des mutations est-elle établie ?
- Polypharmacologie et résistance sont-elles distinguées des prédictions ?
- L’absence de validation expérimentale est-elle visible ?

### Reviewer statistique

- Les n sont-ils corrects ?
- Les tests sont-ils descriptifs ou confirmatoires ?
- Bootstrap et permutations sont-ils interprétés sans surinterprétation ?
- La sélection conditionnelle est-elle reconnue ?

### Éditeur JCIM

- La contribution est-elle une calibration utile ?
- Le papier est-il une étude et non un rapport ?
- Les figures et tableaux sont-ils nécessaires ?
- Les limites sont-elles visibles avant la conclusion ?

## Phase 8 — Figures et tableaux

Pour chaque display, vérifier existence, provenance, cohérence numérique, unités, dénominateurs, incertitudes, lisibilité, caption autonome, absence de redondance et séparation des cohortes.

| Display | Source | Claim | Numerical check | Formatting check | Decision |
|---|---|---|---|---|---|

Retirer les displays décoratifs, administratifs, redondants ou sans question scientifique.

## Phase 9 — LaTeX

### `siunitx`

Utiliser `\num{}`, `\qty{}` ou `\SI{}` pour les nombres et unités. Vérifier les milliers, signes explicites, intervalles, colonnes `S`, SEM, SD, CI95, `n`, `p`, `rho` et AUC.

### `cleveref`

Utiliser `\cref` ou `\Cref` pour figures, tables, équations et sections numérotées. Les sections non numérotées doivent être référencées textuellement si `cleveref` ne peut pas les résoudre. Les labels doivent être uniques et les labels `xr` préfixés entre main et SM.

## Phase 10 — Correction et traçabilité

Pour chaque problème critique ou majeur :

1. identifier la source ;
2. recalculer si nécessaire ;
3. corriger le DAR ;
4. enregistrer cause, correction, impact et fichiers ;
5. corriger le manuscrit et le SI ;
6. recompiler ;
7. refaire l’audit.

Si la preuve est insuffisante, réduire la claim, déplacer le résultat au SI, le marquer exploratoire ou le retirer.

## Validation finale

Utiliser l’environnement `malaria_md` :

```bash
conda run -n malaria_md python -m pytest tests/ -q
conda run -n malaria_md python -m py_compile scripts/*.py
```

Compiler avec `xr` dans l’ordre :

```bash
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2609.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2609.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2609.tex
pdflatex -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2609.tex
pdflatex -interaction=nonstopmode -halt-on-error Cover_Letter_V2609.tex
```

Vérifier les codes de retour, erreurs, références non définies, labels multiples, citations manquantes, warnings BibTeX, pages, figures et tableaux. Extraire le texte des PDF et rechercher `??`, `pending`, `blocked`, IDs de jobs et formulations opérationnelles.

## Livrables

Créer ou mettre à jour :

```text
P2_FINAL_AUTHOR_REVIEW_YYYYMMDD.md
```

Le rapport doit contenir : résumé, incohérences DAR↔résultats, claims↔preuves, audit adverse, audit de prose, audit report-style, audit AI-jargon, audit figures/tableaux, audit JCIM, corrections, risques résiduels et décision.

Checklist minimale :

| Item | Statut | Preuve |
|---|---|---|
| DAR cohérent | PASS/FAIL | fichier et lignes |
| Claims vérifiés | PASS/FAIL | matrice |
| Résultats canoniques identifiés | PASS/FAIL | manifest |
| MD correctement bornée | PASS/FAIL | Methods/Limitations |
| M1 correctement cadré | PASS/FAIL | SM/DAR |
| Figures cohérentes | PASS/FAIL | audit |
| Tables cohérentes | PASS/FAIL | audit |
| Prose scientifique | PASS/FAIL | audit |
| Pas de report-style | PASS/FAIL | scan |
| Pas d’AI-jargon | PASS/FAIL | scan |
| `siunitx` | PASS/FAIL | compilation |
| `cleveref` | PASS/FAIL | 0 `??` |
| Tests | PASS/FAIL | pytest |
| ORCID/funding/conflicts | HUMAN CHECK | Paragon Plus |
| Zenodo | HUMAN CHECK | dépôt |

Décision finale autorisée : `READY_FOR_AUTHOR_APPROVAL`, `READY_FOR_SUBMISSION`, `CONDITIONAL — CORRECTIONS REQUIRED` ou `NOT_READY — SCIENTIFIC BLOCKER`.

Ne jamais déclarer une acceptation future. Évaluer uniquement la préparation et les risques.
