# P2 — Reformulation de la question centrale

**Date** : 2026-09-08
**Statut** : Proposals for author review (plan mode)

---

## 1. Question actuelle

> « Does a resistance-aware docking workflow (RRS + PNS + ACSI) produce a coherent prioritization signal within a curated antimalarial candidate cohort, and is a short single-replicate MD stress test concordant with that docking-derived signal, or does it reveal non-equivalent quantities? »

### Forces
- Cadre méthodologique explicite (RRS, PNS, ACSI)
- Distinction claire entre les deux sous-questions
- Limite biologique bien posée

### Faiblesses
- « coherent » sous-vend le résultat (la stratification A\*/A/B/C/D est discriminante, pas seulement cohérente)
- Absence de ancrage clinique (résistance antipaludique)
- Le résultat riche — non-équivalence des estimateurs — est réduit à une opposition binaire
- Formulation passive

---

## 2. Options de reformulation

### Option A — Polypharmacologie + résistance (recommandée)

> **« Can resistance-aware polypharmacology docking prioritize antimalarial leads that retain activity across mutant panels, and does molecular dynamics corroborate or refute the docking-derived retention signal? »**

- Ancrage clinique (résistance)
- Nomme la stratégie (polypharmacologie)
- Oppose directement docking vs MD
- Le résultat positif (stratification) répond à la première partie ; le résultat négatif (non-équivalence) répond à la seconde

### Option B — Méthodologique

> **« Do docking-derived resistance-retention scores and short MD endpoints measure the same quantity in antimalarial lead prioritization? »**

- Compact, recentre sur la non-équivalence
- Ne met pas en avant le résultat positif

### Option C — Hypothèse-génératrice

> **« Is a resistance-aware docking prioritization of antimalarial candidates robust to structural scrutiny by short molecular dynamics simulations? »**

- Présente la question comme test de robustesse
- Moins ambitieux mais défendable

---

## 3. Plan d'implémentation — Option A

### 3.1 Périmètre des modifications

| Zone du manuscrit | Fichier | Lignes concernées | Type de changement |
|---|---|---|---|
| Titre | `V2609.tex` | 65 | Reformulation |
| Abstract | `V2609.tex` | 123–125 | Réécriture partielle |
| Introduction (question centrale) | `V2609.tex` | 141–143 | Reformulation du paragraphe |
| Discussion (ouverture) | `V2609.tex` | ~400–466 | Ajustement du narrative |
| Conclusion | `V2609.tex` | 467–469 | Alignement |
| Cover letter | `Cover_Letter_V2609.tex` | 38 | Reformulation |
| DAR §1 | `P2_DATA_ANALYSIS_REPORT.md` | 9–13 | Mise à jour |

### 3.2 Titre proposé

**Avant :**
> Resistance-Aware Docking Prioritization and Short MD Stress Tests Measure Non-Equivalent Quantities in an Antimalarial Candidate Cohort

**Après :**
> Resistance-Aware Polypharmacology Docking Prioritizes Antimalarial Leads but Short MD Reveals Non-Equivalent Estimands

**Justification :** Le nouveau titre nomme la stratégie (polypharmacology), le domaine (antimalarial leads), et le résultat clé (non-equivalent estimands). Il est plus court et plus mémorable.

### 3.3 Abstract — modifications ciblées

**Phrase d'ouverture (remplacer la question actuelle) :**

> « Can resistance-aware polypharmacology docking prioritize antimalarial leads that retain activity across mutant PfDHFR and PfCRT panels, and does short molecular dynamics corroborate or refute that signal? »

**Phrase de résultat positif (renforcer) :**

> « We computed a docking-derived resistance-retention score (RRS) on 136 PfDHFR and PfCRT wild-type and mutant systems for a 17-candidate African-natural-product cohort. The primary analysis on 12 two-target candidates yielded a **discriminant five-class stratification** (A\*: 1, A: 1, B: 4, C: 5, D: 1) that separates predicted wild-type potency from predicted mutant retention. »

**Phrase de résultat négatif (clarifier la non-équivalence) :**

> « A 16-system single-replicate MD pilot on two Set-C candidates did not recover the docking retention pattern; trajectory metrics and docking-RRS disagreed in direction for seven of eight mutant comparisons, **demonstrating that docking-RRS and MD-RRS are non-equivalent estimands rather than interchangeable measures of the same quantity**. »

**Phrase de conclusion (aligner) :**

> « Resistance-aware docking produces a stratified prioritization inside this computational panel, but the ranking is hypothesis-generating only and does not constitute a validated triage procedure. Short MD stress tests probe a different estimand and cannot serve as direct validation of docking-derived retention classes. »

### 3.4 Introduction — paragraphe central (lignes 141–143)

**Avant (3 phrases) :**
> « The central question is therefore twofold: (i) whether target-level docking-score retention (RRS) yields a computationally coherent prioritization signal inside this curated cohort, and (ii) whether a short single-replicate MD structural-stress test is concordant with that signal or instead demonstrates that the two approaches measure non-equivalent quantities. »

**Après (4 phrases) :**
> « The central question is therefore twofold: (i) whether resistance-aware polypharmacology docking can produce a **discriminant prioritization** that separates candidates by their predicted retention across clinically relevant mutant panels, and (ii) whether short molecular dynamics simulations **corroborate** the docking-derived retention signal or **refute** it by revealing that the two approaches measure non-equivalent biophysical quantities. The first question addresses whether RRS-based stratification is informative enough to generate hypotheses for downstream experimental testing. The second addresses whether MD, despite its richer representation of protein flexibility, converges on the same compound ranking — or instead exposes a fundamental mismatch between static docking scores and dynamic binding behavior. »

### 3.5 Discussion — paragraphes à ajuster

**Paragraphe « Non-equivalence of estimands » (existant, ~lignes 400–430) :**

Ajouter en ouverture :
> « The central question of this study asked whether docking-RRS and MD-RRS measure the same quantity. The answer is clearly negative: seven of eight mutant comparisons showed directional disagreement. This non-equivalence is not a failure of either method but a consequence of what each estimates — docking-RRS reflects a **static score ratio** between mutant and wild-type poses, while MD-RRS captures **dynamic binding persistence** under explicit solvent and protein fluctuations. The two quantities are expected to diverge when conformational selection or induced-fit effects alter the binding mode upon mutation. »

**Paragraphe « Practical implications » (ajouter après) :**

> « For antimalarial lead prioritization, this means that docking-based RRS can serve as a **first-pass computational filter** to stratify candidates, but it should not be treated as a validated prediction of resistance resilience. MD stress tests, even short ones, provide a **complementary but non-redundant** signal that probes a different aspect of the binding event. Future workflows should report both estimands separately rather than combining them into a single evidence narrative. »

### 3.6 Conclusion — modifications

**Avant (incipit) :**
> « A resistance-aware docking workflow (RRS + PNS + ACSI) produces a coherent computational prioritization signal… »

**Après (incipit) :**
> « Resistance-aware polypharmacology docking produces a discriminant prioritization signal inside the curated 17-candidate cohort… »

Puis, ajouter avant la dernière phrase :
> « The finding that docking-RRS and MD-RRS are non-equivalent estimands has a practical consequence: computational prioritization and structural scrutiny should be reported as parallel ranking dimensions with non-overlapping failure modes, not as convergent evidence of resistance resilience. »

### 3.7 Cover letter — phrase centrale

**Avant :**
> « The central question is whether a resistance-aware, target-level docking workflow (RRS + PNS + ACSI) produces a coherent prioritization signal inside a curated antimalarial cohort, and whether a short single-replicate MD structural-stress test is concordant with that signal or instead reveals non-equivalence. »

**Après :**
> « The central question is whether resistance-aware polypharmacology docking can prioritize antimalarial leads that retain activity across clinically relevant mutant panels, and whether short molecular dynamics simulations corroborate or refute that prioritization. We show that docking-based resistance-retention scoring produces a discriminant five-class stratification, but that short MD stress tests measure a non-equivalent quantity and therefore cannot validate the docking signal. »

### 3.8 DAR §1 — mise à jour

**Avant :**
> « Does a resistance-aware docking workflow (RRS + PNS + ACSI) produce a coherent prioritization signal within a curated antimalarial candidate cohort, and is a short single-replicate MD stress test concordant with that docking-derived signal, or does it reveal non-equivalent quantities? »

**Après :**
> « Can resistance-aware polypharmacology docking prioritize antimalarial leads that retain activity across mutant PfDHFR and PfCRT panels, and does short molecular dynamics corroborate or refute the docking-derived retention signal? »

**Bounded answer (ajuster) :**
> « (i) the docking workflow produces a **discriminant stratification** (classes A\*–D) that separates candidates by predicted wild-type potency and mutant retention; (ii) short MD stress tests are **not concordant** — directional disagreement in 7/8 mutant comparisons — demonstrating that docking-RRS and MD-RRS are **non-equivalent estimands**. Neither result establishes biological target engagement or resistance. »

---

## 4. Séquence d'implémentation

| Étape | Action | Fichier | Priorité |
|-------|--------|---------|----------|
| 1 | Valider la reformulation du titre avec les co-auteurs | `V2609.tex` | Haute |
| 2 | Réécrire l'abstract (phrases d'ouverture, résultat positif, résultat négatif, conclusion) | `V2609.tex` | Haute |
| 3 | Reformuler le paragraphe central de l'introduction (lignes 141–143) | `V2609.tex` | Haute |
| 4 | Ajuster la Discussion (ouverture + implications pratiques) | `V2609.tex` | Haute |
| 5 | Aligner la Conclusion (incipit + phrase sur la non-équivalence) | `V2609.tex` | Haute |
| 6 | Mettre à jour la cover letter | `Cover_Letter_V2609.tex` | Haute |
| 7 | Mettre à jour le DAR §1 | `P2_DATA_ANALYSIS_REPORT.md` | Moyenne |
| 8 | Vérifier la cohérence avec les keywords | `V2609.tex` l.83 | Basse |
| 9 | Relire les cross-references (Abstract↔Introduction↔Discussion↔Conclusion) |全局 | Haute |
| 10 | Compiler et vérifier 0 erreur / 0 warning | `pdflatex + bibtex` | Haute |

---

## 5. Risques et mitigations

| Risque | Mitigation |
|--------|-----------|
| Le titre « Non-Equivalent Estimands » peut sembler trop technique pour un lecteur non-spécialiste | Le sous-titre « polypharmacology docking prioritizes antimalarial leads » ancre le domaine ; le mot « estimands » est expliqué dans l'introduction |
| Réécrire l'abstract peut introduire des incohérences numériques | Relire chaque chiffre contre le DAR avant compilation |
| Les co-auteurs peuvent préférer une formulation plus prudente | Préparer les 3 options comme alternatives ; la décision finale appartient aux auteurs |
| Le paragraphe « Practical implications » en Discussion est nouveau — doit être validé scientifiquement | S'assurer qu'il ne prétend pas plus que les données ne supportent |

---

## 6. Critères de validation

- [ ] Titre ≤ 20 mots
- [ ] Abstract ≤ 150 mots (JCIM limit)
- [ ] La question centrale dans l'Introduction répond explicitement aux deux sous-questions
- [ ] La Conclusion reprend les mots-clés de la question (polypharmacology, prioritize, non-equivalent)
- [ ] Aucune nouvelle affirmation non supportée par les données
- [ ] 0 erreur LaTeX, 0 warning BibTeX
- [ ] Cover letter = 1 page, sans référence aux manuscrits compagnons
