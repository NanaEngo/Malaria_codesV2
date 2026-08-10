# Submission Package — P1 V6 → Journal of Chemical Information and Modeling (ACS)

**Date:** 10 August 2026 · **Status:** SUBMISSION-READY (R1–R5 cleared, register `INTERNAL_WORK_AUTHORIZED`)
**Manuscript title:** *Integrated polypharmacology and resistance-resilience prioritisation of African-natural-product-inspired antimalarial candidates*
**Corresponding author:** *(à compléter)* · **Manuscript type:** Research Article

---

## 1. Fichiers du package (ordre de soumission ACS Paragon Plus)

| # | Fichier (dans ce dossier) | Rôle dans Paragon Plus |
|---|---|---|
| 1 | `P1_V6_main.pdf` | **Manuscript (PDF compilé)** — main text, 19 p., 0 erreur |
| 2 | `P1_V6_main.tex` + `.bbl` + `.bib` | Source LaTeX du main (facultatif mais recommandé par ACS) |
| 3 | `P1_V6_SM.pdf` | **Supporting Information** (nom ACS : `Supporting_Information.pdf`) |
| 4 | `P1_V6_SM.tex` + `.bbl` | Source LaTeX du SM |
| 5 | `Cover_Letter_P1_V6.pdf` (+ .tex) | **Cover letter** — obligatoire (1 p.) |
| 6 | `p1_v6_toc_graphic_ACS.tiff` | **TOC graphic (obligatoire)** — 3.25×1.75 in, 300 dpi, RGB |
| 7 | `p1_v6_toc_graphic.pdf` | Version vectorielle du TOC (pour recompilation) |
| 8 | `Figure_2_rrs_mutation_profiles.pdf` | Figure 2 du main |
| 9 | `Figure_3_exploratory_metric_relationships.pdf` | Figure 3 du main |
| 10 | `Figure_S_targetwise_profile_summary.pdf` | Figure SM (target-wise) |
| 11 | `acs-P1_V6_*.bib` / `Sao_Chim_Space.bib` | Références bibliographiques |

> ⚠️ **Note ACS** : si le portail demande les **figures séparées**, soumettre les fichiers 8–10 en PDF 300 dpi (ou TIFF). Sinon, elles sont déjà intégrées au PDF du manuscrit.

---

## 2. Checklist de soumission ACS Paragon Plus (JCIM)

### 2.1 Avant de cliquer « Submit »
- [x] **Titre** conforme (pas d'abréviations non définies, ≤ 20 mots recommandé)
- [x] **Abstract** présent dans le main (≈ 200 mots, sans citations)
- [x] **TOC graphic** généré au format ACS exact : 3.25×1.75 in, 300 dpi, TIFF RGB (`p1_v6_toc_graphic_ACS.tiff`)
- [x] **Cover letter** rédigée (objectif, signification, déclaration d'originalité)
- [x] **Sections obligatoires** présentes : Introduction, Materials and Methods, Results, Discussion, Conclusion, Supporting Information, Author Contributions, Notes, Data Availability, Use of Artificial Intelligence
- [x] **Déclarations** : ORCID (corresponding author), funding, competing interests, AI-use statement
- [x] **Références** au format ACS (fichier `.bbl` généré)
- [x] **SM nommé** selon la convention ACS (`Supporting_Information.pdf` au dépôt)
- [x] **Données** : liens GitHub + Zenodo DOI réservé (10.5281/zenodo.19608875) dans Data Availability

### 2.2 Dans Paragon Plus (ordre des étapes)
1. Sélectionner **JCIM** (Journal of Chemical Information and Modeling)
2. Choisir **Research Article** comme type de manuscrit
3. Renseigner **title + abstract** (copier depuis le main)
4. Téléverser les fichiers dans l'ordre du tableau §1
5. Renseigner **authors + ORCID** (corresponding author obligatoire)
6. Renseigner **keywords** (≥ 4) : polypharmacology, resistance resilience, antimalarial, natural products, molecular docking, virtual screening
7. Déclarer **funding sources** (si applicable) et **competing interests** (none)
8. Répondre aux **questions de soumission** (originality, prior publication, ethical compliance)
9. **Review PDF** généré par le système — vérifier : TOC graphic affiché, SM correct, pagination
10. **Submit**

### 2.3 Post-soumission
- [ ] Numéro de manuscrit ACS reçu (JCIM-2026-xxxxx)
- [ ] Répondre aux requêtes éditoriales sous 24–48 h
- [ ] Préparer la réponse aux reviewers (modèle : point-par-point, réf. lignes)

---

## 3. Vérifications finales effectuées (10/08/2026)

| Contrôle | Résultat |
|---|---|
| Compilation main (pdflatex ×2) | ✅ 19 p., 0 erreur, 0 réf. indéfinie |
| Compilation SM | ✅ 5 p., 0 erreur |
| Compilation cover letter | ✅ 1 p. |
| TOC graphic — dimensions | ✅ 3.25×1.75 in (ratio 1.857) |
| TOC graphic — résolution | ✅ 300 dpi (975×525 px) |
| TOC graphic — format | ✅ TIFF RGB (LZW) + PDF vectoriel |
| Review adverse croisée (claims↔preuves) | ✅ 6 incohérences corrigées (voir `FINAL_CROSS_REVIEW_20260810.md`) |
| Register | ✅ `INTERNAL_WORK_AUTHORIZED` (décision auteur 10/08) |
| Manifeste SHA-256 | ✅ `SUBMISSION_MANIFEST.md` |

---

## 4. Rappel des points de vigilance
1. **PfClpP = PDB 2F6I** (triade catalytique Ser252/His223/Asp219) — 4GM2 = PfClpR, explicitement exclu.
2. **DEKOIS PfDHFR = 0.450 [0.37, 0.53]** (valeur canonique, honnête) — cohérent avec P2 et BMAD.
3. **Poses = hypothèses computationnelles** — le manuscrit ne revendique ni puissance mesurée ni engagement biologique confirmé.
4. **Lire une dernière fois** le main (19 p.) et le SM avant soumission.
