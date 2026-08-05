# Application formelle de `scientific-agent-skills` — Audit P3 & P4

**Date :** 05 août 2026
**Skills appliqués :** `scientific-writing` (v2.0), `peer-review` (v2.1), `literature-review` (v1.7) — repo `/tmp/opencode/scientific-agent-skills` (K-Dense-AI, commit 831d49e)
**Périmètre :** P3 (`Paper3_Quantum_InspiredV2608.tex` + `Bibliography_Paper3.bib`) et P4 (`P4_Pareto_MCTS_JoC_refined.tex` + `P4_Bibliography.bib`)
**Outils locaux exécutés :** `check_references.py`, `check_consistency.py` (offline, sans réseau)

---

## 1. Audit des références (`check_references.py`)

Manifests construits par conversion automatique des `.bib` → schéma `source_manifest_template.json` (E001…E0xx). Script : `audits/scientific-agent-skills/bib2manifest.py`.

| Projet | Sources auditées | Erreurs | Warnings | Statut |
|--------|:---------------:|:-------:|:--------:|:------:|
| **P3** | 66 | **0** | 12 | ✅ pass |
| **P4** | 33 | **0** | 12 | ✅ pass |

Warnings restants = `NO_IDENTIFIER_TO_CHECK` (entrées sans DOI/PMID/URL dans le `.bib`, à vérifier par un humain) :
- **P3 (6)** : temgoua2027md (manuscrit compagnon, en préparation), giotto-tda, TensorLy, molecular_fingerprints_2026 (marquée *Unused*), interactive_visualization, WHO 2024.
- **P4 (6)** : CombiMOTS (résolu après correction, cf. §3), RDKit, PennyLane, scikit-learn, Noisy Networks, P1 (résolu après correction), WHO 2024.

### Corrections appliquées (issues réelles trouvées)

1. **P4 — doublons P1 (2 erreurs `POSSIBLE_DUPLICATE_TITLE`)** : trois entrées identiques de la même référence P1 (`temgoua2026antimalarial`, `Temgoua2026`, `Temgoua2026a`). Seule `Temgoua2026a` était citée → suppression des deux doublons non cités. **→ 0 erreur.**

2. **Référence P1 alignée sur le DOI ChemRxiv** (exigence utilisateur) : les 3 bib pointent désormais sur `doi.org/10.26434/chemrxiv.15006437/v1` :
   - P3 `Bibliography_Paper3.bib` : déjà conforme ✅
   - P4 `P4_Bibliography.bib` : était `J. Chem. Inf. Model., Submitted` → corrigé vers ChemRxiv + DOI ✅
   - P5 `Bibliography_P5.bib` : déjà conforme ✅

### Vérification usage citations (0 `MISSING`, excédent d'`UNUSED`)

| Projet | Clés bib | Citations tex | Non citées | Manquantes |
|--------|:-------:|:------------:|:----------:|:----------:|
| P3 | 66 | 37 | 29 | **0** |
| P4 | 33 | 13 (main+SM+cover) | 20 | **0** |

Aucune citation non résolue. Les clés non citées sont du bib conservé (dont `molecular_fingerprints_2026` explicitement marquée *Unused -- retained for completeness*). Recommandation : nettoyage éventuel lors de la soumission, non bloquant.

## 2. Audit de cohérence numérique (`check_consistency.py`)

Manifests : `audits/scientific-agent-skills/p3_consistency.json` (34 faits), `p4_consistency.json` (18 faits) — valeurs récurrentes cross-sections (abstract/results/discussion) extraites du texte.

| Projet | Faits | Résultats | Erreurs | Statut |
|--------|:-----:|:---------:|:-------:|:------:|
| **P3** | 34 | 34 | **0** | ✅ pass |
| **P4** | 18 | 18 | **0** | ✅ pass |

Faits P3 vérifiés : AUC ECFP4 0.948 / TFP 0.876 / TNE 0.722 / Hybride 0.888 ; ablations QKS −0.040, TFP −0.014, TNE +0.011 ; QK vs RBF n=5000 (0.820/0.826, p=0.419) et n=19849 (0.823/0.829, p=0.060) ; H1–RRS ρ=0.312 (p=0.0057, n=77), pilot ρ=0.947 ; Tanimoto 92.6 % / scaffold 69.3 %.
Faits P4 vérifiés : rewards Random 0.7335 / MCTS 0.7276 / Greedy 0.7211 / GA 0.7027 ; Δ=0.0059, t₁₉=2.41, p=0.026 ; Pareto 4 solutions, HV 1.2366 ; ablations policy +0.148, Pareto +0.108.

## 3. Audit littérature (gaps & nouveauté) — `literature-review`

Vérification web des claims SOTA (titres/DOI/venues réels) :

| Claim (P4) | Référence | Vérifié | Correction |
|------------|-----------|:-------:|------------|
| Mothra : Pareto-MCTS SMILES | JCIM 64(19):7291–7302, 2024, doi 10.1021/acs.jcim.4c00759 | ✅ | — |
| ParetoDrug : target-aware Pareto MCTS | Commun. Biol. 7:1074, 2024, doi 10.1038/s42003-024-06746-w | ✅ | — |
| CombiMOTS : dual-target PMCTS | **ICML 2025** (PMLR 267:56650–56691) — le bib citait uniquement le preprint arXiv 2604.23307 | ✅ | **Upgrade preprint → publication ICML 2025** (auteurs/venue/pages corrigés) |

| Claim (P3) | Référence | Vérifié |
|------------|-----------|:-------:|
| PACTNet : compression topologique de GNN | arXiv 2508.07807 (NeurIPS 2025) | ✅ |
| jamali2025spectral : spectres vs généralisation | arXiv 2510.14217 | ✅ |

Cohérence narrative : la nouveauté P4 (« premier Pareto-MCTS à intégrer RRS/PNS antipaludique comme objectifs actifs ») est exacte au regard des trois SOTA vérifiés (Mothra/ParetoDrug optimisent affinité/drug-likeness/toxicité ; CombiMOTS cible dual-target). La discussion P3 reliant TFP/TNE à la catégorie « local 3D kernel » de jamali2025spectral correspond aux conclusions du papier.

## 4. Rapport de compliance (`scientific-writing`)

- **Pas de fabrication** : aucune citation/DOI/URL inventé — toutes les références ajoutées (WHO 2024, Ariey 2014, Ashley 2018, CombiMOTS-ICML) sont issues des sources vérifiées P1 ou de la vérification web de ce jour.
- **Cohérence méthodes/résultats** : 0 mismatch (§2).
- **Négatifs rapportés** : P3 (QK ≈ RBF, hybride < ECFP4, H1–RRS médié par la taille), P4 (random > MCTS sur récompense scalaire) — conformes à la règle « report negative/null findings ».
- **Limitations explicites** : présentes dans les deux manuscrits (labels computationnels, split scaffold proxy, cohorte taille-contrôlée).
- **À faire par un humain avant soumission** : ouvrir et confirmer chaque entrée sans identifiant (liste §1), valider l'authorship/CRediT, et le DOI Zenodo P3.

## 5. Livrables

- `audits/scientific-agent-skills/p3_source_manifest.json`, `p4_source_manifest.json` (audit références)
- `audits/scientific-agent-skills/p3_consistency.json`, `p4_consistency.json` (audit cohérence)
- Corrections dans les `.bib` (P3 : rien ; P4 : doublons P1 supprimés, P1→ChemRxiv, CombiMOTS→ICML 2025)
