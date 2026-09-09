# Project2 — résultats canoniques et reproduction

**Dernière mise à jour : 30 août 2026**
**Statut :** docking/RRS/ACSI/PNS terminé ; cohorte parentale MD séparée ; pilote Set-C MD secondaire terminé ; full-panel MD-RRS non calculé par conception.

## Périmètre scientifique canonique

- **Set-C :** 17 candidats sélectionnés, 136 systèmes de docking PfDHFR/PfCRT.
- **Analyse RRS primaire :** 12 candidats avec scores WT éligibles pour PfDHFR et PfCRT.
- **Analyse de sensibilité :** 5 candidats PfCRT-only, non équivalents à l’analyse primaire.
- **Classes primaires :** A*:1, A:1, B:4, C:5, D:1.
- **Classes sur cibles disponibles :** A*:5, A:1, B:5, C:5, D:1.
- **Cohorte parentale MD :** 4 complexes WT indépendants, 10 ns chacun ; seul PfCRT–214 fournit un endpoint MM-GBSA interprétable.
- **Pilote Set-C MD :** 16 systèmes PP-01/PP-02, 10 ns chacun, résultats secondaires et exploratoires ; non fusionnés avec le RRS primaire.
- **Full-panel MD-RRS 17 × 8 :** `NOT_COMPUTED`.

Les scores Vina, RRS, ACSI, PNS, MD-RRS et MM-GBSA représentent des estimands distincts. Aucun résultat ne constitue une preuve expérimentale d’affinité, d’engagement de cible, de mécanisme d’action ou de contournement de la résistance.

## Sorties reproductibles principales

| Sortie | Rôle |
|---|---|
| `c_rrs_classification.csv` | Couverture et classes RRS par candidat |
| `c_rrs_sensitivity.csv` | Vue de sensibilité de la classification |
| `c_acsi_scores.csv` | Composantes brutes, normalisées et ACSI |
| `c_pns_ranking.csv` | Classement PNS avec imputation PfCRT documentée |
| `cross_metric_statistical_audit.csv` | Corrélations et p-values par ensemble d’analyse |
| `cross_metric_statistical_audit.json` | Paramètres statistiques et provenance |
| `pns_imputation_sensitivity.csv` | Sensibilité de rang à l’imputation PfCRT |
| `pns_imputation_sensitivity.json` | Métadonnées de sensibilité PNS |
| `p2_rigorous_audit_manifest.json` | Manifest de régénération des sorties |
| `lightweight_robustness/` | Sensibilités locales RRS : seuils WT, leave-one-mutant-out et perturbation bornée des scores |

## Audit de déblocage des résultats existants

Le manifeste `results/p2_results_unlock_manifest.json` et les audits versionnés associés dans le DAR confirment que la sensibilité PfCRT pH 5.2 (100/100) et la sensibilité PNS par imputation sont calculées. Elles sont distinctes du redocking multi-seed PP-01/PP-15 et de la sensibilité STRING 400/900, désormais documentés dans le DAR et leurs répertoires de résultats versionnés.

## Pilote Set-C MD

Les résultats du pilote sont conservés sous `results/set_c_md/` :

- `post_production_manifest_pilot.json` ;
- `set_c_trajectory_qc_pilot.csv` ;
- `md_rrs_pilot_PP01_PP02.csv` ;
- `md_rrs_discriminative_manifest.json` ;
- `mmgbsa_manifest.json` ;
- `mmgbsa_summary_pilot.csv` ;
- `md_vs_docking_comparison_pilot.csv`.

Le pilote utilise OpenFF 2.2.0 AM1-BCC avec une déviation de politique déclarée et approuvée par le PI. Il est limité à deux candidats, à une réplique et à 10 ns par système. Il ne doit pas être présenté comme une validation convergée du docking-RRS.

## Reproduction rapide

Depuis le répertoire `Project2_Polypharmacology_MD_ValidationV2607/` :

```bash
python scripts/p2_rigorous_audit.py
python -m pytest tests -q
```

Cet audit rapide ne lance ni docking, ni GROMACS, ni MM-GBSA. Il régénère les sorties compactes et vérifie les définitions RRS, la couverture, l’ACSI, le PNS et les statistiques descriptives. L’analyse locale supplémentaire peut être régénérée avec `python scripts/p2_lightweight_robustness.py`; ses sorties sont décrites dans `results/lightweight_robustness/README.md`.

La reproduction MD complète nécessite l’environnement et les fichiers de paramètres documentés dans les manifestes Set-C. Les trajectoires volumineuses ne sont pas incluses dans le dépôt de soumission ; les conclusions du manuscrit sont limitées aux résumés et endpoints explicitement archivés.

## Provenance et versions

Les fichiers source V2607 restent immuables. La release active V2609 est portée par :

- `manuscript/LaTeX/Polypharmacology_MD_Validation_V2609.tex` ;
- `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2609.tex` ;
- `manuscript/LaTeX/Cover_Letter_V2609.tex` ;

Les sources V2607 correspondantes sont conservées comme référence historique et ne doivent pas être écrasées :

- `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` ;
- `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex` ;
- `manuscript/LaTeX/Cover_Letter.tex` ;
- `manuscript/LaTeX/Bibliography_Polypharmacology_MD_Validation.bib`.

Les analyses historiques et scripts non canoniques sont conservés pour la provenance, mais ne doivent pas être utilisés pour régénérer les claims du manuscrit. Les fichiers contenant des statuts historiques doivent être interprétés avec les manifestes canoniques datés.

Une archive permanente versionnée doit être associée à la version effectivement soumise. Tant que le DOI n’est pas enregistré, aucune phrase ne doit laisser entendre qu’un dépôt Zenodo public est déjà disponible.
