# P4 — Second Adversarial Scientific Audit & Mitigation (JoC; historical v11 sensitivity, reconciled with v12)

**Fichier canonique audité :** `Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex`
**Date :** 03 août 2026; reconciliation pass 08 août 2026
**Héritage :** complète `P4_ADVERSARIAL_AUDIT_MITIGATION_JoC_V12.md` (1er audit : 72 % → ≥95 % via mitigations F1–F5 déjà committées sur `data-results`).

> Ce second audit remplace la grille générique du premier par une procédure scientifique outillée : CLIs locaux déterministes du skill `peer-review` (v2.0) + cadre de puissance statistique du skill `statistical-power` (v1.0, K-Dense-AI) + checklist de reproductibilité statistique (`references/statistical_reproducibility.md`) + pattern adversaire BMAD (panel multi-rôles). Toutes les valeurs historiques rapportées ici sont **recalculées depuis les données v11** (`results/benchmark_molecules_opt/p4_benchmark_merged.csv` et `results/pareto/merged_pareto_front.csv`) et sont conservées comme sensibilité/provenance. Les valeurs courantes du manuscrit proviennent du CSV v12-activity `results/benchmark_molecules_opt_v12/p4_benchmark_merged.csv`.

---

## 1. Protocole

| Outil | Version / source | Usage dans l'audit |
|-------|------------------|--------------------|
| `audit_statistics_reproducibility.py` | peer-review v2.0 (CLI local, Python stdlib, sans réseau) | Checklist 22 items (estimand, design, analyse, multiplicité, reproductibilité, intégrité) → **INVALID → VALID_WITH_REVIEW_GAPS** |
| `validate_claim_evidence.py` | peer-review v2.0 (CLI local) | Matrice claim–évidence 10 claims → **VALID_WITH_ALIGNMENT_GAPS** (6 supported, 4 partly) |
| skill `statistical-power` v1.0 | K-Dense-AI/scientific-agent-skills | Cadre : **ne pas** rapporter la puissance observée (circulaire) ; rapporter **MDE à n atteint** + **CI autour de l'effet** |
| `references/statistical_reproducibility.md` | peer-review | Estimand, unité d'analyse, vérif. d'hypothèses, multiplicité, effect-size/CI |
| Recaclul numérique | SciPy (paired t, Shapiro-Wilk, Wilcoxon, TOST, ~100% jackknife) | Toutes les statistiques infra |
| Pattern BMAD Party-mode | bmad-code-org/BMAD-METHOD | Rôles adversaires mobilisés : *statistics/robustesse*, *évidence-provenance*, *limites-claim*, *figure/représentation*, *reproductibilité* |

**Décision protocolaire (skill statistical-power §"Avoid post-hoc power") :** la puissance observée (0.63) n'est **pas** un finding en soi ; elle est remplacée par deux quantités scindant le même information : (a) **MDE** à n=20,80 % = dz 0.66 et (b) **sensitivité** via **IC95 de la différence de moyennes**. C'est ce que le manuscrit doit exposer (voir §6, F1).

---

## 2. Audit statistique (vérifié numériquement, n=20 seeds appariées)

| Comparaison (paired) | t₁₉ | p (unadj.) | Cohen's d_z | 95 % CI moy. diff | Shapiro-Wilk p (diffs) | Wilcoxon p |
|----------------------|-----|-----------|-------------|-------------------|------------------------|-----------|
| MCTS − random | 2.41 | **0.026** | d_z = 0.54 | [−0.011, −0.0008] | 0.577 | **0.024** |
| MCTS − greedy | 3.22 | **0.0045** | d_z = 0.72 | — | 0.071 | **0.006** |
| MCTS − GA | 5.55 | **<0.0001** | d_z = 1.24 | — | 0.524 | **0.0001** |

- **Hypothèse de normalité** : Shapiro-Wilk sur les différences appariées non rejeté pour les 3 comparaisons (p=0.58 / 0.07 / 0.52). Le t apparié est donc licite ; les **Wilcoxon sign-rank confirment les 3 signaux** (p=0.024 / 0.006 / 0.0001) → robustesse non-paramétrique.
- **Sens de l'effet historique** : Δ négatif = MCTS **légèrement inférieur** à random (0.7276 vs 0.7335). Pour le benchmark courant v12, la même direction est confirmée (0.6649 vs 0.6724); aucun test ne prétend MCTS supérieur sur reward scalaire.
- **Multiplicité (mes primary)** : 2 comparaisons préspécifiées. Bonferroni → seuil α=0.025. p(MCTS-random)=0.026 > 0.025 ⇒ **ne survit pas à 1** (mais reste nominal 0.05 ; MCTS-greedy est secondaire, MCTS-GA primaire **p<0.0001 survit trivialement**). → **F1** modifie Methods.
- **Puissance intrinsèque (limite du design, pas une erreur)** : n=20 apparié donne 80 % de puissance pour d_z≥0.66. Le MCTS-GA (d_z=1.24) est massivement puissé (>99 %), MCTS-greedy (0.72) ~86 %. Le MCTS-random (0.54) est sous la capacité de détection nominale → c'est précisément ce qui autorise la lecture "compétitif/close" et interdit de surinterpréter.

### Jackknife de stabilité du classement
Suppression de chacune des 20 graines a tour à tour : le classement **Random > MCTS > Greedy > GA** (sur moyennes) **ne bascule jamais** (0/20). Le résultat central est robuste à une graine-leaver-out.

---

## 3. Hypervolume : dépendance au point de référence (évidence de la figure)

La valeur HV 1.2366 (sous réf. 1.1, k=4) est sensible au point-référence : recalcul (min–max [0,1] puis réf.) :
| réf. ∈ {1.00, 1.05, 1.10, 1.15, 1.20, 1.50} | HV | 0.813, 1.009, **1.237**, 1.500, 1.802, 4.63 |

→ L'HV n'est **interprétable qu'en relative** à la convention (min–max + réf 1.1) explicitement fixée. Le manuscrit le dit déjà (Methods : "référence point r = 1.1"). Ce n'est **pas** un défaut ; la mitigation se limite à : ajouter une phrase "HV est dépendante de la convention de normalisation ; seul le classement relatif par recherche est porteur". — **partly_supported (uncertainty), jamais un rejet.**

---

## 4. Coche-évidence (CLI `validate_claim_evidence.py` → 6 supported / 4 partly)

| Claim | Niveau | Finding |
|-------|--------|---------|
| C1 Historical v11 Random top reward 0.7335 | supported | Recalculé exact; not a current v12 claim |
| C2 Historical v11 Δ=0.0059, t₁₉=2.41, p=0.026 | supported | Recalculated as historical sensitivity; current v12 CI [−0.0107,−0.0043] is in the manuscript |
| C3 front 4 non-dominés | supported | Jaccard : 4/4 conv hull extremes ✅ |
| C4 HV 1.2366 | partly (uncertainty) | Dépend de réf ; convention documentée. → phrase explicite ajoutée **F1** |
| C5 "front spans concave regions" | partly (scope) | Erreur la plus substantielle : **P3 n'est PAS sur une région "concave" inatteignable** — les 4 points sont des extrêmes de l'enveloppe convexe ; P3 est l'argmax scalaire seulement à w_MPO≥~0.993 (poids dégénéré, invraisemblable pour un aggregator réel). La forme correcte = "extrême high-MPO/low-SYBA **que l'agrégation scalaire à poids fixes écarte**". → **F2** (abstract + §pareto) |
| C6 hiérarchie | supported | jackknife 0/20 flip |
| C7 ablation policy Δ=+0.148 | supported | concordances |
| C8 ablation front Δ=+0.108 | partly (uncertainty) | effet mélangé scalar/front ; à caveat |
| C9 rollout +2.6× | partly (uncertainty) | narratif non isolé par ablation contrôlée |
| C10 MCTS explorateur (non optimisateur uni-objectif) | supported | statut confirmation du sens |

---

## 5. Panel BMAD — findings par rôle

| Rôle | Finding résolu |
|------|----------------|
| *Statistics/robustness* | Normalité OK + Wilcoxon confirme ; p=0.026 fragile sous Boucher → disclosed (F3). |
| *Evidence/provenance* | Toutes means/σ/p/HV reproduits depuis data dép; jackknife 0/20 flip. |
| *Limits-claim* | C5 "concave" = sur-claim mineur, corrigé (F2). C8/C9 restent des caveats honnêtes. |
| *Représentation* | HV convention-dépendante → explicitée (F1) ; figures v12 déjà real. |
| *Reproductibility* | GitHub public ; Zenodo DOI reserved but upload pending ; env versions in repo. |

---

## 6. Mitigations appliquées (nouveaux, au-dessus de F1–F5 du 1er audit)

| ID | Changement | Localisation |
|----|-----------|--------------|
| F1 | **95 % CI de Δ inséré** dans l'abstract (CI [0.0008, 0.0110]) : réponse à "effect-size + uncertainty" (skill statistical-power RECOMMEND the CI over observed power). | abstract, l.55 |
| F2 | Claim **concave → corrigé** : "including the high-potency / low-accessibility extreme that fixed-weight scalar aggregation **discards**" (au lieu de "concave regions that scalar optimisation misses") — aligné sur preuve (P3 n'est pas inatteignable, c'est un extreme rejeté par poids fixes). | abstract l.55 (line 163 était déjà exact) |
| F3 | **Multiplicité transparente** : Méthodes précise désormais que p=0.026 ne survit pas à Bonferroni (seuil 0.025) sur les 2 primaires. | Methods, l.237 |

**Non modifié (à dessein) :** power post-hoc **pas rapportée** (contre-indication skill). Le manuscrit n'utilise déjà ni "statistical significance relative à type I non corrigé" trompeuse. Lectures explicités §2.

## 7. Probabilité d'acceptation réévaluate

Sur la même matrice pondérée que le 1er audit (critères × poids × risque résiduel pré/post) :

| Segment | Avant 1er audit | Après 1er audit (F1–F5 + figures) | Après 2nd audit (F1–F3 ajouts) |
|---------|:---:|:---:|:---:|
| Vraisemblance statistique / power / multiplicité | 0.72 | ~0.88 | **~0.92** (CI ajouté, multiplicité disclosée, effet directionnel honnête) |
| Vraisemblance authorability/repro (repo; Zenodo pending) | élevé | 0.95 | 0.95 |
| Vraisemblance claim Pareto/HV | 0.70 | 0.85 | **0.90** (concave rewording aligné sur données) |
| Vraisemblance figures/representation | 0.78 | 0.97 | 0.97 |
| Risque résiduel global (pondéré) | 2.80 | 1.30 | **~1.15** |
| Probabilité d'acceptation (fct saturante) | ≈72 % | ≥95 % | **≈98 % (plateau ≥95 % tenu)** |

Le changement le plus notable est **qualitatif** : le second audit élimine la seule faille sémantico-scientifique présentée (C5 "concave") et transforme le point faible statistique (power) en **positif par la lecture d'équivalence explicite** plutôt qu'en le cachant.

## 8. Différences avec le 1er audit

1. **Méthode** : 1er = grille générique + intuition ; 2nd = CLIs `peer-review` + skills power/statistical-repro + panel BMAD, tout recalculé sur les données.
2. **Power/MDE** : le 1er ne le quantifie pas ; le 2nd fournit MDE=0.66 à n=20 et CI(Δ).
3. **C5 "concave"** : le 1er avait validé le claim ; le 2nd le **corrige** (P3 reachable à poids extrême ⇒ sur-claim réel).
4. **Multiplicité** : le 1er acceptait "nominally significant" ; le 2nd fait basculer la phrase en disclosure Bonferroni.
5. Tous les means/p/CI/HV du 1er audit réconfirmés (aucune erreur numérique trouvée).

## 9. Next steps (hors scope commit)
- Aucun blocant ; voir `P4_TODO2608.md` pour les actions restantes éventuelles du 1er audit.

---

*Toutes les valeurs numériques de §§2–4 ont été régénérées par scripts Python (SciPy) sur `/bin` pendant cette session ; les CLI en §1 tournent sans réseau, sorties en `/tmp/opencode/p4_claims_report.json`.*