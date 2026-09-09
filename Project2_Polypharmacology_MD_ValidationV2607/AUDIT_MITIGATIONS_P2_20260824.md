# P2 — Mitigations issues de l'audit adversarial (24 août 2026)

Prompt appliqué : `docs/PRX_PRXQuantum_adversarial_review_prompt.md` (183 lignes, §1bis standards externes).
Rapport d'audit : `docs/PRX_adversarial_review_P2_20260824.md` — verdict final **MINOR REVISION, 0 BLOCKER → GO soumission JCIM**.

## 1. Critiques résolues

| ID | Sévérité initiale | Objet | Mitigation |
|----|-------------------|-------|------------|
| C-P2-01 | BLOCKER | Manuscrit revendiquant un pilote Set-C non adossé à un état canonique | Preuves disque trouvées (`results/set_c_md/post_production_manifest_pilot.json` v3 : 16/16 production 15320 terminée, chaîne COMPLETE 2026-08-18T21:29Z, QC=0, MD-RRS=0) ; **DAR mis à jour** (racine `BMAD_Q1_DATA_ANALYSIS_REPORT.md` + présent rapport `P2_DATA_ANALYSIS_REPORT.md`) : statuts CANONICAL, MD-RRS `COMPUTED_WITH_COHORT_CONTRACT`, MM-GBSA `MMGBSA_COMPUTED` 16/16 ; artefacts superseded listés (témoins 15259/15260, tentatives cassées 15384/15385 → autorité 15386) |
| C-P2-02 | MAJOR | Incohérence force-field (GAFF2 vs OpenFF selon cohortes) | Méthodes rescopées L252 (cohorte parent = ACPyPE/GAFF2), L264 (pilote Set-C = CHARMM36m + OpenFF 2.2.0 AM1-BCC, déviation déclarée approuvée PI), limitation Discussion L715 étendue (pas de comparaison absolue inter-cohortes) ; DAR §5 corrigé pareil |
| C-P2-03 | MAJOR | Hygiène siunitx | `detect-all` supprimé (L28) ; 40× `\SI`→`\qty` (38 main + 2 SM) ; `$\qty{-18.25 \pm 0.40}{...}$` invalide → `$-\num{18.25} \pm \num{0.40}$\,\si{\kcalmol}` |
| C-P2-04…08 | MINOR | RRS>100 % non interprétés, dual IDs Rank-N/PP-xx sans crosswalk, natbib/achemso, D_ANPDB=0.000, TDA n≠17 | Documentés dans le rapport d'audit avec remèdes proposés (légende, tableau croisé, note caption) |

## 2. Renforcements structurels

- **Prompt adversarial régénéré** : l'ancien (413 lignes, contenu Floquet périmé) remplacé par une version P2 de 172→183 lignes, avec §1bis « Références externes contraignantes » (MM/GBSA relatif-only Roux & Chipot 2024 ; docking conditionnel JCAMD 2026 ; standards éditoriaux DDDT 2025 ; DEKOIS 2.0 PfDHFR ; canon structural PfCRT/PfDHFR ; bonnes pratiques GROMACS officielles).
- **Hiérarchie probante explicite** dans le prompt (LaTeX = texte, DAR = données, manifestes = statuts ; vocabulaire BLOCKER/MAJOR/MINOR/OK, CANONICAL/NON-CANONICAL/NOT_COMPUTED/WITHDRAWN, IDs C-P2-NN).
- **Vérification indépendante des comptes de classes** ligne à ligne : A*:1/A:1/B:4/C:5/D:1 (12/17 panneaux complets) ✓ ; A*:5/B:5/C:5/D:1 (17/17 cibles disponibles) ✓ ; ACSI>0.70 = Rangs 8+14 ✓.
- **Répertoire restructuré** : rapports d'audit déplacés vers `docs/` ; figures égarées à la racine du repo rendues au projet (`manuscript/Graphics/`) ; artefacts désuets supprimés (logs d'échec 15384/15385, junk LaTeX `.fls/.fdb/.blg/.out`, `__pycache__`).

## 3. État de conformité §1bis

> **Lecture actuelle des recommandations historiques.** Les éléments marqués « appliqué » ci-dessous sont vérifiés dans les sources canoniques et les artefacts présents. Les recommandations sans artefact source validé sont conservées comme travail futur, et non comme résultats réalisés.

| Standard | Statut |
|----------|--------|
| MM/GBSA classement relatif uniquement | ✅ respecté |
| Trajectoire unique courte = exploratoire | ⚠ cadré comme pilote secondaire |
| Honnêteté négative (PNS–RRS non significatif post-Bonferroni) | ✅ conservée |
| Déviation force-field déclarée et justifiée | ✅ PI-approved, documentée |
| Citation canon structural PfCRT 7G8 cryo-EM | 💡 suggérée pour la SI |

## 4. Recompilation

Main + SM : **0 erreur, 0 overfull, 0 référence indéfinie** (pdflatex allers-retours, 24 août).

## Mise à jour 24 août 2026 — application effective des points mineurs et du polissage (pass 2)

| Item | Statut | Application |
|---|---|---|
| C-P2-04 RRS>100 % | ✅ appliqué | Paragraphe d'interprétation inséré après les comptes de classes (PP-04 105.3/103.6, PP-13 110.2, PP-15 131.8 = rétention pleine dans le bruit ±1 kcal/mol, jamais un gain) ; même caveat ajouté à la légende SM tab:s8_setc_mmgbsa |
| C-P2-05 Double étiquetage Rank-N ↔ PP-xx | ✅ appliqué | Phrase de clarification en tête de §RRS : les labels PP-xx sont des alias des enregistrements MPO ; la correspondance label↔rang vit dans la table source-data lisible par machine |
| C-P2-06 natbib/achemso | ✅ vérifié | Compilation authoryear cohérente main+SM, 0 undefined après bibtex |
| C-P2-07 D_ANPDB=0.000 | ✅ appliqué | Clause ajoutée à la définition ACSI : 0.000 = minimum de cohorte sous min–max, pas distance nulle |
| C-P2-08 TDA n=14/n=77≠17 | ✅ appliqué | Clause « counts internal to that companion study… » au §TDA |
| PASS2 EN polish | ✅ appliqué | Orthographe US généralisée (26 occurrences), référence archive GNINA reformulée |
| 💡 Citation PfCRT 7G8 | ✅ appliqué | \citep{Kim2019PfCRT} sur PfCRT(6UKJ) + entrée bib Nature 576:315–320 (2019), doi:10.1038/s41586-019-1795-x |

Recompilation finale : main et SM → 0 erreur / 0 overfull / 0 undefined.

## Mise à jour 24 août 2026 — passe 3 (prose & intégration P2_Sugg)

- **Style rapport éliminé** : seule occurrence résiduelle (nom de fichier CSV brut en §ADMET) reformulée en prose (« the parent-library ADMET-AI screen of 65,856 molecules ») ; balayage complet main+SM : plus aucun identifiant de production (jobs 15259/15320/15385/15386, exit codes, manifests) dans le texte.
- **P2_Sugg.md — retenu** : la valeur d'imputation C_PfCRT = 0.151 était déjà publiée (§PNS, caption tab:PNS, Discussion) — faille #4 non applicable à V2607 ; ajout du compte explicite « huit des seize systèmes mutants > 100 % » en légende tab:s8 (vérifié sur mmgbsa_summary_pilot.csv).
- **Recompilation** : main et SM — 0 erreur / 0 overfull / 0 undefined.

## Passe 4bis — vérification R2 & réconciliation données (24 août 2026)

- **R2 (répliques vs JCIM)** : la phrase promise était absente du disque (grep 'pillar'=0). Appliquée : « Replicated simulations of at least one pillar system (the PP-01 wild type) would therefore be required before MM-GBSA-derived resilience statements enter routine use. » (Limitations, ¶1). ✅
- **Réconciliation MM-GBSA contre results/set_c_md/mmgbsa_summary_pilot.csv** : 12 systèmes mutants (16 lignes = 12 + 4 WT) ; 8/12 >100 % ; les 4 <100 confirmés au chiffre près (PP-01 PfCRT K76T 96,4 / PP-02 PfCRT K76A 97,8 / PP-02 PfDHFR C59R 95,7 / PP-02 PfDHFR S108N 89,8) ; moyenne ΔG −29,04 ± 3,00, étendue [−35,29 ; −24,53] ✓. Correction légende tab:s8 (SM) : « sixteen » → « twelve ». Main L617 validé tel quel.
- **Hygiène** : \SIrange déprécié → \qtyrange (L617) ; 'prioritised'→'prioritized' (×2).
- Recompilation main+SM : 0 erreur / 0 overfull / 0 undefined.

## Passe 4 — anticipation des referees sévères (R1–R10, 24 août 2026)

| # | Préoccupation | Mitigation appliquée |
|---|---|---|
| R1 | Circularité de sélection Set-C | ¶ Limitations « Cohort selection conditioning. » : les fréquences de classes caractérisent la cohorte sélectionnée par MPO, pas des taux de base ; distribution nulle sur bibliothèque non sélectionnée requise |
| R2 | Trajectoire unique vs attente JCIM de répliques | Framing honnête (abstract + Limitations) ; phrase système-pilote ajoutée en passe 4bis (« Replicated simulations of at least one pillar system (the PP-01 wild type) would therefore be required… ») |
| R3 | Incertitude des scores Vina (~±1 kcal/mol) supérieure à plusieurs marges de classe | ¶ Limitations « Docking-score uncertainty. » : valeurs proches de la frontière = rétention pleine dans le bruit, jamais un gain |
| R4 | Absence d’ancre expérimentale | ¶ Discussion : IC50 enzymatiques PfDHFR quadruple N51I/C59R/S108N/I164L (± mutants simples) ; SPR/MST sur protéoliposomes PfCRT K76T vs WT (PP-01/PP-15) |
| R5 | Robustesse au seuil STRING | ⚠️ corrigé après objection : aucune donnée multi-seuil n’existe ; la clause promettant 400/900 a été remplacée par une divulgation honnête non calculée (« dependence of the network-derived scores on this interaction-confidence cutoff was not systematically varied… pending an explicit threshold-sensitivity analysis ») |
| R6 | Pondérations ACSI arbitraires | Phrase Méthodes : stabilité du classement sous perturbations ±20 % par poids (ρ entre 0,9167 et 0,9804), chiffres identiques à l’abstract |
| R7 | 5 candidats PfCRT-only | Clause : protonations alternatives / redocking d’ensemble pourraient restaurer des scores PfDHFR éligibles (suivi) |
| R8 | Plancher de bruit MM-GBSA (8/12 ratios mutants >100 %) | Captions retention-not-gain + clause ΔΔG source-table ; réconciliation CSV complète (voir Passe 4bis) |
| R9 | Confusion TDA (provenance partagée) | Clause corrélation partielle contrôlant masse molaire et prévalence de scaffold |
| R10 | Dépôt des données attendu dès la soumission | Nouvelle section \section*{Data availability} : code, manifests et tables lisibles par machine archivés avec le dépôt projet ; archive Zenodo versionnée accompagnant la publication |

Recompilation main après correction R5 : 0 erreur.

## Passe figures — vérification de rendu réel (24 août 2026)

Méthode : test de rendu poppler (`pdftoppm -png -r 40` — syntaxe `-r 40` avec espace requise par poppler 26.07) + fraction d'encre PIL >0,5 %.

| Asset | Verdict |
|---|---|
| PPI_network.pdf | ❌ vecteur vide (stream 0 octet) → **remplacé** par le raster réel `PPI_network.png` (184 Ko), tex repointé ; Figure 2 rend désormais |
| rmsd_representative.pdf | ❌ stub 317 o → **remplacé** par `figure3_rmsd_stability.pdf` (40 Ko, encre 11,4 %), stub supprimé |
| p2_cohort_workflow.pdf | ✅ encre 32,2 % (fausse alerte initiale = bug de syntaxe `-r40`) |
| rrs_radar_profiles.pdf | ✅ encre 13,7 % |
| VAE_latent_space.pdf | ✅ encre 6,8 % |
| Figure_S1_MPO_sensitivity.pdf | ✅ encre 71,4 % |
| TOC_graphic.pdf | ✅ encre 24,3 % |
| figure3_rmsd_stability.pdf | ✅ encre 11,4 % |
| p2_setc_rrs_scatter.pdf | ✅ encre 9,1 % |

Recompile main ×2 : err=0, overfull=0 ; PDF 28 pages, pages_with_XObject=7/7, rasters=4.

## Passe lightweight (25 août 2026)

**Injection manuscrit (25 août)** : RUN1/R8 inséré après le ¶ MM-GBSA (0/12 plus faible significatif, 1 plus serré, max |ΔΔG|=5.37 kcal/mol) ; RUN2+RUN3 injectés dans la limitation « Statistical power » (ρ partiel −0.6154 ; IC95 classes [0.118,0.529]/[0.000,0.176] ; fraction MMG>100 % 0.667 [0.417,0.917]). Recompile main : 0 err / 0 overfull.
 — runs 1→2→3 exécutés (env `malaria_md`, seed 42)

| Run | Résultat clé |
|---|---|
| R8/1 ΔΔG±SD | 12 mutants tabulés (`results/lightweight_robustness/mmgbsa_ddeltaG_pilot.csv`); IC95 excluant zéro : **1/12** (0 affaiblissement significatif, 1 renforcement, max \|ΔΔG\|=5.37) → confirme « rétention, pas gain » |
| R9/2 Corrélation partielle | n=12 (panneau complet bi-cible) : ρ brut(PNS,RRS)=−0.2098 → ρ partiel \|MW+prévalence Murcko\|=**−0.6154** ; l'association se RENFORCE après conditionnement → non-artefact taille/scaffold (TDA compagne NON disponible localement — quantité propre au manuscrit, étiquetée honnête) |
| R3/3 Bootstrap classes | B=10⁴ sur n=17 : A* [0.118,0.529], B [0.118,0.529], C [0.118,0.529], D [0.000,0.176] ; fraction mutants MMG>100 % : 0.667 IC95 [0.417,0.917] ; pas de σ par score (CSV single-score → bootstrap cohorte uniquement, étiqueté honnête) |

Script: `scripts/lightweight_runs_20260825.py`; sorties: `results/lightweight_robustness/{mmgbsa_ddeltaG_pilot.csv, partial_corr_input_table.csv, lightweight_runs_summary.json}`.
