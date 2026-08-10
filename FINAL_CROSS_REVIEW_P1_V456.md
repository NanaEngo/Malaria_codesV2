# FINAL_CROSS_REVIEW_P1_V456 — Revue adverse croisée (10 août 2026)

**Portée :** cohérence claims ↔ preuves, prose (style publication), formatage des trois manuscrits
P1 canoniques **V4** (`Antimalarial_Candidates_African_NP_V2607`), **V5**
(`Antimalarial_Candidates_African_NP_V2608`) et **V6** (`P1_V6_Integrated_Polypharmacology_RRS`),
après la correction des références (`journaltitle` → `journal`).

**Méthode :** extraction des valeurs clés des 3 .tex + .bbl, croisement avec
`BMAD_Q1_DATA_ANALYSIS_REPORT.md` et les CSV sources (`c_rrs_classification.csv`,
`c_acsi_scores.csv`, `c_pns_ranking.csv`), recherche de résidus de registre interne
("unreviewed", "parent-study", "V5/V2607", "legacy/superseded"), audit siunitx/cleveref,
recompilation complète.

---

## 1. Architecture des trois manuscrits (rôles distincts — pas de doublon)

| Manuscrit | Rôle | État |
|---|---|---|
| **V4** — *Computational Discovery of Antimalarial Candidates from African Natural Product Chemical Space* | Espace chimique + funnel + overlay intégré (RRS/PNS/ACSI sur Set C) | ✅ Recompilé propre (19 p.) |
| **V5** — *Target-Anchored Computational Prioritization…* | Méthodologie docking ciblé (68 paires, poches biologiquement ancrées) — ne calcule **pas** de RRS/PNS sur ce panneau (déclaré explicitement) | ✅ Recompilé propre (5 p., 4 réf.) |
| **V6** — *From African-Natural-Product Chemical Space to Resistance-Resilience Hypotheses* | **Soumission JCIM** — étude intégrée RRS + polypharmacologie | ✅ Recompilé propre (19 p.) |

## 2. Vérifications numériques (claims ↔ preuves) — TOUTES CONFORMES

| Valeur | V4 | V5 | V6 | Source (CSV/BMAD) | Verdict |
|---|---|---|---|---|---|
| Librairie hybride | 65856 ✓ | 65856 ✓ | 65856 ✓ | BMAD 65,856 | ✅ |
| Leads prioritaires | 19913 ✓ | — (hors scope) | 19913 ✓ | BMAD 19,913 | ✅ |
| Cohort Set C | 17 ✓ | 17 ✓ | 17 ✓ | BMAD | ✅ |
| Paires candidat–cible | 68 ✓ | 68 ✓ | 68 ✓ | 17×4 | ✅ |
| Gate géométrique | centraide + ancre ≤10 Å + ≥90% | rank-1 + ancre + ≥90% | centraide + ancre ≤10 Å + ≥90% | registre | ✅ (formulations équivalentes) |
| Range Vina | — | −7.91…−4.63 ✓ | −7.91…−4.63 ✓ | table 17×4 | ✅ |
| Moyennes Vina / cible | −5.76/−6.19/−5.94/−6.31 | −5.755/−6.185/−5.935/−6.308 | — | table 17×4 | ⚠️ même valeur, précision 2 vs 3 décimales (cosmétique) |
| Classes RRS | A\*:6, B:5, C:5, D:1 ✓ | (hors scope, déclaré) | A\*:6, B:5, C:5, D:1 ✓ | `c_rrs_classification.csv` | ✅ |
| Range RRS | 68.18–111.65 (mean 81.70) ✓ | — | 68.2–111.7 ✓ | RRS_mean min/max/mean = 68.18/111.65/81.70 | ✅ (arrondi cohérent) |
| PNS | 1.04–6.00 ✓ | — | — | `c_pns_ranking.csv` min/max | ✅ |
| ACSI | 0.173–0.823, mean 0.543 ✓ | — | — | `c_acsi_scores.csv` (n=17, 2/17>0.70) | ✅ |
| Cross-metrics | — | — | −0.559/−0.132/−0.433/+0.389, ns Bonferroni ✓ | BMAD §2.7b | ✅ |
| DEKOIS PfDHFR | AUC 0.450 ✓ | — | AUC 0.45 (IC95 0.37–0.53), 40 actifs/1200 decoys ✓ | BMAD R1-A | ✅ |
| Enrichissement MMV | — | — | 0.924–1.000 (0.924/0.971/1.000) ✓ | BMAD (consensus Vina+DiffDock) | ✅ |
| Re-docking RMSD <2 Å | — | — | 5 ligands, MTX exclu (grid NADPH) ✓ | registre V5 | ✅ |

## 3. Corrections de prose appliquées (registre interne → langage publication)

| Fichier | Avant | Après |
|---|---|---|
| **V6 main** L61 | "parent-study MD top-20 candidates" | "P2 MD top-20 candidates" |
| **V6 main** L61 | "The four parent-study MD systems" | "The four P2 MD systems" |
| **V6 main** L69 | "parent-study dual-filter consensus" | "dual-filter consensus" |
| **V6 main** L77 | "four-target V5 wild-type matrix" | "four-target wild-type matrix" |
| **V6 main** L93 | "distinct V5 four-target wild-type matrix" | "distinct four-target wild-type matrix" |
| **V6 main** L95 | "the four-target V5 matrix is not used" | "the four-target wild-type matrix is not used" |
| **V6 main** L99 | "Equation~\ref{eq:rrs}" | "\Cref{eq:rrs}" (cleveref) |
| **V6 main** L190 | "The parent MD systems" | "The P2 MD systems" |
| **V6 SM** L27 | "parent-study MD top-20" ×2 | "P2 MD top-20" ×2 |
| **V6 SM** L72 | "four-target V5 wild-type matrix" | "four-target wild-type matrix" |
| **V4 main** L78 | "over 247 million cases and 619000 deaths reported in 2023" | "In 2023, WHO estimated approximately 263 million malaria cases and 597000 deaths" (**chiffres WMR 2024**) |
| **V4 main** L492 | "unreviewed target-anchored computational panel" | "declared target-anchored computational panel" |
| **V4 main** L492 | "historical centroid screen" / "sole historical GOOD hit" | "centroid screen" / "only GOOD hit" |
| **V4 main** L576 | "historical MMV positive-control analysis" | "MMV positive-control analysis" |
| **V4 main** L612 | "historical positive-control calibration" | "positive-control calibration" |
| **V4 main** L612 | "legacy DiffDock consensus and superseded four-target consensus are excluded" | "DiffDock consensus and four-target arithmetic consensus are excluded from the final overlay" |

## 4. Formatage et résidus

- **siunitx/cleveref :** V4 (34 \cref), V6 (\Cref) et V5 utilisent \num/\qty/\si et \cref —
  chargés via la classe/style (grep usepackage = 0 mais compilation OK). ✅
- **"TODO" (V4:10, V5:3, V6:4) :** faux positifs — sous-chaîne "toDo" dans **AutoDock**. ✅
- **V2607/V2608/V5 restants :** uniquement `\externaldocument[...]{..._SM}` (préambule xr) et
  chemins de dépôt GitHub (légitimes). ✅
- **"draft" (V4:1) :** rôle CRediT "Writing – Original Draft Preparation" — standard. ✅
- **Références :** rendu complet vérifié (page 17-18 du PDF V6 ; .bbl V4/V5 avec noms de journaux). ✅

## 5. Recommandations résiduelles (non bloquantes)

1. **Précision des moyennes Vina** (V4 2 décimales vs V5 3 décimales) : unifier si les deux
   manuscrits sont relus côte à côte (cosmétique, valeurs identiques).
2. **V4 vs V6 partagent l'overlay RRS/PNS/ACSI** (68 paires, classes, gate) : si V4 devait aussi
   être soumis, il faudrait un chevauchement textuel explicite + citation compagnon. V6 étant
   la soumission JCIM désignée, V4 reste l'archive de pré-soumission.
3. **AGENTS.md** indique encore "Manuscrit P1 canonique = V4" — à mettre à jour vers V6
   (soumission) lors de la prochaine révision du fichier.
4. N51I : aucun manuscrit ne dépend du MD-RRS N51I ; le QC ignorera proprement.

## 6. Validation finale

- **Recompilation :** V6 main+SM rc=0, V4 main+SM rc=0 — 0 erreur, 0 référence indéfinie.
- **Résidus corrigés :** grep `four-target V5|V5 wild-type|V5 matrix|parent-study|unreviewed|legacy DiffDock|superseded four` = **0** sur les 3 fichiers.
- **Package V6 resynchronisé** : P1_V6_main.pdf/SM.pdf/aux (xr) + Supporting_Information.pdf.
- **Claims ↔ données :** toutes les valeurs vérifiées traçables vers CSV/BMAD.

**Verdict :** les trois manuscrits sont cohérents entre eux et avec les données ; les résidus
de registre interne et l'erreur factuelle OMS ont été éliminés. **V6 est prêt pour Paragon Plus.**
