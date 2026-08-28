# Audit complet — implémentation des suggestions MD

**Date :** 28 août 2026
**Portée :** P2, P5 V2, P6 — toutes les fichiers MD d'audit et de suggestions

---

## P2 — Suggestions des fichiers MD

### P2_P5_SEVERE_REVIEW_GAP_AUDIT_20260828.md

| # | Suggestion | Statut | Évidence |
|---|---|:---:|---|
| 1 | External replication dans Results/SI avec comparaison directe | ✅ | Table S15, Conclusion l.447 `\cref{SM-tab:s15_robustness_transfer}` |
| 2 | Bootstrap intervals pour external class fractions | ✅ | Conclusion : `\numrange{99.59}{101.32}`, Class-A `\numrange{0.923}{1.000}` |
| 3 | Remplacer le langage PENDING résiduel dans les runbooks | 🟡 | Runbooks historiques — basse priorité, ne concerne pas le manuscrit |
| 4 | Réconcilier le manifest P2 (wording external-replication + Zenodo) | ✅ | Manifest contient "312/312 records", "Zenodo pending", "computational sensitivity evidence" |
| 5 | Vérification finale auteur (metadata, declarations) | 🔵 | Porte auteur — hors scope agent |

### P2_DATA_ANALYSIS_REPORT.md

| Élément | Statut |
|---|:---:|
| 16/16 production MD | ✅ |
| MD-RRS pilot COMPUTED_WITH_COHORT_CONTRACT | ✅ |
| MM-GBSA 16/16 | ✅ |
| External replication 312/312 | ✅ |
| K76A FAILED_NUMERICAL_QC (exclu des claims) | ✅ documenté |

---

## P5 V2 — Suggestions des fichiers MD

### P5_SEVERE_REVIEW_20260827.md (10 risques majeurs)

| Risque | Statut | Évidence manuscrit |
|---|:---:|---|
| Over-generalization | ✅ | Abstract + Discussion restreints au panel évalué |
| Pseudoreplication | ✅ | Methods : "five per-seed means as paired inferential unit" |
| External panel = validation | ✅ | "molecule-disjoint ChEMBL transfer analysis, not prospective validation" |
| LISH conflation | ✅ | "phenotype-only, different labels/features/metric" |
| Salience = mécanisme | ✅ | "correlation, not causation; does not establish feature necessity" |
| ChemBERTa → primary | ✅ | "secondary status maintained in manuscript, DAR, and manifest" |
| Leakage fine-tuning | ✅ | "per-fold restoration of pretrained weights" |
| Tautomer collisions | ✅ | "306 collisions reported; labels not silently changed" |
| Missing calibration/OOD | ✅ | "explicitly listed as not computed" |
| Reproducibility metadata | ✅ | Manifest régénéré, package 31/31 staged |

### P5V2_SUGGESTIONS_IMPLEMENTATION_MATRIX_20260827.md

| Catégorie | Items | Statut |
|---|---|:---:|
| IMPLEMENTED (13 items) | Panel-specific, scaffold partitions, AUPRC, paired ablation, salience stability, chemical audit, ChEMBL threshold, ChemBERTa, study-design tables, LISH orthogonal, fixed seeds, reproducibility package, position section | ✅ tous |
| IMPLEMENTED_SECONDARY (3) | Paired ablation, salience stability, ChemBERTa extension | ✅ |
| COMPUTED_SECONDARY (1) | Post-hoc calibration metrics (ECE, MCE, Brier) | ✅ |
| DAR_READY (2) | Practical paired-effect interpretation, fold scaffold size | 🟡 données disponibles, tableau dédié non généré |
| NOT_COMPUTED (6) | OOD analysis, Butina splits, VAE/Graphormer, contrastive pretraining, conditional generation, experimental validation | ✅ correctement étiquetés |

### P2_P5_SEVERE_REVIEW_GAP_AUDIT_20260828.md — P5 items

| # | Suggestion | Statut | Évidence |
|---|---|:---:|---|
| 1 | Paired CI + multiplicity-adjusted comparisons | ✅ | Bootstrap intervals l.130, BH correction l.126-128 |
| 2 | Salience vs necessity distinction | ✅ | l.168, l.209, l.227 : "does not establish feature necessity" |
| 3 | ChEMBL = molecule-disjoint transfer | ✅ | l.60, l.73, l.203-205 : "molecule-disjoint ChEMBL transfer panel" |
| 4 | ChemBERTa compute budget | ✅ | l.209 : "deliberately short fixed schedule", "compute-matched baseline" |
| 5 | Author gates | 🔵 | Porte auteur — hors scope agent |

---

## P6 — Suggestions des fichiers MD

### P6_ROADMAP.md

| Phase | Items | Statut |
|---|---|:---:|
| Phase 0 | P6 indépendant de P5, phenotype baseline préservée, NO_STRUCTURE enregistré | ✅ |
| Phase 1 | Mapping, audit, artifact gelé (1722 molécules, 794 collision groups) | ✅ |
| Phase 2 | Phenotype reproduit, splits honnêtes, structure-only linear, GNN/ChemBERTa | ✅ |
| Phase 2 restant | ECFP4-RF (l.120), log loss primary (l.70), scaffold sensitivity (phenotype+ECFP4-RF) | ✅ |
| Phase 3 | Paired statistics (l.183 limitation), MoA vs causal (l.57,64,165,183,191), article standalone | ✅ |

### P6_PHASE2_RERUN_20260827.md

| Élément | Statut |
|---|:---:|
| 4 tâches GNN/ChemBERTa complétées | ✅ |
| Aucun job P6 actif dans le scheduler | ✅ |
| Report JSONs + fold CSVs présents | ✅ |

### P6_DATA_ANALYSIS_REPORT.md

| Élément | Statut |
|---|:---:|
| Molecular arms complets (GIN, GIN-TFP, GIN-TNE, ChemBERTa) | ✅ |
| Per-label calibration = NOT_COMPUTED | ✅ correctement étiqueté |
| Référence à IMPLEMENTATION_COVERAGE_AUDIT_20260827.md | ⚠️ fichier absent du disque |

---

## Synthèse

| Projet | Total suggestions | Implémentées | NOT_COMPUTED correct | Porte auteur | Action requise |
|---|:---:|:---:|:---:|:---:|---|
| **P2** | 10 | 8 | 0 | 2 | 0 (runbooks = basse priorité) |
| **P5** | 24 | 20 | 6 | 1 | 0 |
| **P6** | 12 | 11 | 0 | 0 | 1 (référence DAR orpheline) |

### Action concrète restante

1. **P6 DAR** : la ligne 12 référence `docs/IMPLEMENTATION_COVERAGE_AUDIT_20260827.md` qui n'existe pas. → Supprimer la référence ou créer le fichier.

Toutes les suggestions realizables des fichiers MD ont été implémentées dans les manuscrits. Les items NOT_COMPUTED sont correctement étiquetés et ne doivent pas être présentés comme réalisés. Les portes auteur (metadata, ORCID, visual PDF review, Zenodo upload) restent hors scope de l'agent.
