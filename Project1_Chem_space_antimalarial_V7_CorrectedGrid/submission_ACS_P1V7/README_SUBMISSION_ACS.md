# Submission Package — P1 V7 → Journal of Chemical Information and Modeling (ACS)

**Date:** 10 August 2026 · **Status:** SUBMISSION-READY (R1–R5 cleared, register `INTERNAL_WORK_AUTHORIZED`)
**Manuscript title:** *African Natural-Product-Inspired Antimalarial Polypharmacology: Computational Resistance Hypotheses*
**Corresponding author:** *(à compléter)* · **Manuscript type:** Research Article

---

## 1. Fichiers du package (ordre de soumission ACS Paragon Plus)

| # | Fichier (dans ce dossier) | Rôle dans Paragon Plus |
|---|---|---|
| 1 | `P1_V7_main.pdf` | **Manuscript (PDF compilé)** — main text, 25 p., 0 erreur |
| 2 | `P1_V7_main.tex` + `.bbl` + `.bib` | Source LaTeX du main (facultatif mais recommandé par ACS) |
| 3 | `P1_V7_SM.pdf` | **Supporting Information** (17 p.; nom ACS : `Supporting_Information.pdf`) |
| 4 | `P1_V7_SM.tex` + `.bbl` | Source LaTeX du SM |
| 4b | `P1_V7_main.aux` + `P1_V7_SM.aux` | **⚠️ REQUIS pour la recompilation** — le main et le SM se référencent croisément via `\usepackage{xr}` + `\externaldocument` (`\cref{SM-...}` / `\cref{M-...}`). Sans ces `.aux`, la recompilation produit des références non résolues. |
| 5 | `Cover_Letter_P1_V7.pdf` (+ .tex) | **Cover letter** — obligatoire (1 p.) |
| 6 | `p1_v7_toc_graphic_ACS.tiff` | **TOC graphic (obligatoire)** — 3.25×1.75 in, 300 dpi, RGB |
| 7 | `p1_v7_toc_graphic.pdf` | Version vectorielle du TOC (pour recompilation) |
| 8 | `Figure_2_rrs_mutation_profiles.pdf` | Figure 2 du main |
| 9 | `Figure_3_exploratory_metric_relationships.pdf` | Figure 3 du main |
| 10 | `Figure_S_targetwise_profile_summary.pdf` | Figure SM (target-wise) |
| 11 | `Figure_S_chemical_space_coverage.pdf` | Figure SM (couverture chimique) |
| 12 | `acs-P1_V7_*.bib` / `Sao_Chim_Space.bib` | Références bibliographiques |

> ⚠️ **Note ACS** : si le portail demande les **figures séparées**, soumettre les fichiers 8–11 en PDF 300 dpi (ou TIFF). Sinon, elles sont déjà intégrées au PDF du manuscrit.

---

## 2. Checklist de soumission ACS Paragon Plus (JCIM)

### 2.1 Avant de cliquer « Submit »
- [x] **Titre** conforme (pas d'abréviations non définies, ≤ 20 mots recommandé)
- [x] **Abstract** présent dans le main (≈ 200 mots, sans citations)
- [x] **TOC graphic** généré au format ACS exact : 3.25×1.75 in, 300 dpi, TIFF RGB (`p1_v7_toc_graphic_ACS.tiff`)
- [x] **Cover letter** rédigée (objectif, signification, déclaration d'originalité)
- [x] **Sections obligatoires** présentes : Introduction, Materials and Methods, Results, Discussion, Conclusion, Associated Content, Author Contributions, Notes, Data Availability, Acknowledgments
- [x] **Déclarations** : ORCID (corresponding author), funding, competing interests, AI-use statement
- [x] **Références** au format ACS (fichier `.bbl` généré)
- [x] **SM nommé** selon la convention ACS (`Supporting_Information.pdf` au dépôt)
- [x] **Données** : dépôt GitHub et manifeste de checksums indiqués dans Data Availability; le DOI Zenodo reste réservé et n’est pas présenté comme un dépôt public

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
| Compilation main (pdflatex + BibTeX + final passes) | ✅ 25 p., 0 erreur, 0 réf. indéfinie |
| Compilation SM (pdflatex + BibTeX + final passes) | ✅ 17 p., 0 erreur |
| Compilation cover letter | ✅ 1 p. |
| TOC graphic — dimensions | ✅ 3.25×1.75 in (ratio 1.857) |
| TOC graphic — résolution | ✅ 300 dpi (975×525 px) |
| TOC graphic — format | ✅ TIFF RGB (LZW) + PDF vectoriel |
| Review adverse croisée (claims↔preuves) | ✅ 6 incohérences corrigées (voir `FINAL_CROSS_REVIEW_20260810.md`) |
| Register | ✅ `INTERNAL_WORK_AUTHORIZED` (décision auteur 10/08) |
| Package-only recompilation | ✅ main + SM, BibTeX et pdflatex: rc=0; `Graphics/` présent |
| Manifeste SHA-256 | ✅ `SUBMISSION_MANIFEST.md` (31 fichiers) |

---

## 4. Régénération du package (après modification des manuscrits)

```bash
cd Project1_Chem_space_antimalarial_V7_CorrectedGrid
# 1. Recompiler le main + SM (pdflatex x2 : SM d'abord, puis main — ordre requis pour xr)
#    puis recopier les PDFs ET les .aux (nécessaires aux références croisées xr) :
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS.pdf   submission_ACS_P1V7/P1_V7_main.pdf
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.pdf submission_ACS_P1V7/Supporting_Information.pdf
cp manuscript/Cover_Letter_P1_V7.pdf                      submission_ACS_P1V7/Cover_Letter_P1_V7.pdf
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS.bbl   submission_ACS_P1V7/P1_V7_main.bbl
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS.aux   submission_ACS_P1V7/P1_V7_main.aux
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.aux submission_ACS_P1V7/P1_V7_SM.aux
cp -a manuscript/Graphics/. submission_ACS_P1V7/Graphics/
cp manuscript/Graphics/p1_v7_chemical_space_coverage.pdf submission_ACS_P1V7/Figure_S_chemical_space_coverage.pdf
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.pdf submission_ACS_P1V7/Supporting_Information.pdf
# 2. Régénérer le TOC (script reproductible : PDF vector + TIFF RGB 300 dpi + TIFF 1200 dpi) :
/home/nanaengo/miniforge3/envs/malaria_md/bin/python scripts/v7_generate_acs_toc.py
cp manuscript/Graphics/p1_v7_toc_graphic*.pdf manuscript/Graphics/p1_v7_toc_graphic_ACS*.tiff submission_ACS_P1V7/
# 3. Régénérer le manifeste SHA-256 :
/home/nanaengo/miniforge3/envs/malaria_md/bin/python ../scripts/make_submission_manifests.py
```

> ⚠️ Le TOC 1200 dpi (`p1_v7_toc_graphic_ACS_1200dpi.tiff`) est fourni pour le line art contenant du texte (recommandation ACS ≥ 1200 dpi) ; le TIFF 300 dpi satisfait le minimum pour images couleur/grayscale.
> ⚠️ **ORCID** : à renseigner dans Paragon Plus (étape auteurs) — le .tex ne contient pas d'ORCID (convention ACS).

## 5. Rappel des points de vigilance
1. **PfClpP = PDB 2F6I** (triade catalytique Ser252/His223/Asp219) — 4GM2 = PfClpR, explicitement exclu; PfATP4 = PDB 9N10.
2. **DEKOIS PfDHFR = 0.450 [0.37, 0.53]** (valeur canonique, honnête) — cohérent avec P2 et BMAD.
3. **Poses = hypothèses computationnelles** — le manuscrit ne revendique ni puissance mesurée ni engagement biologique confirmé.
4. **Lire une dernière fois** le main (25 p.) et le SM (17 p.) avant soumission.
