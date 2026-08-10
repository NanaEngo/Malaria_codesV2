# Checklist Paragon Plus — P1 V6 pour JCIM

**Version** 1.0 — 10 août 2026
**Document cible** : `P1_V6_Integrated_Polypharmacology_RRS` (19 p. main, 7 p. SM)
**URL** : https://acs.manuscriptcentral.com/ (sélectionner JCIM)

---

## Étape 0 — Prérequis (avant de se connecter)

| # | Action | Statut | Détail |
|---|--------|--------|--------|
| 0.1 | Avoir un compte ORCID pour chaque auteur | ⏳ | Créer/compléter sur https://orcid.org — **obligatoire ACS** |
| 0.2 | Avoir un compte ACS Paragon Plus | ⏳ | https://acs.manuscriptcentral.com/ — les auteurs peuvent avoir un compte |
| 0.3 | Vérifier que les PDF compilent proprement | ✅ | Main 19 p., SM 5 p., **0 erreur, 0 référence indéfinie** |
| 0.4 | Vérifier que le package de soumission est complet | ✅ | `submission_ACS_P1V6/` — 31 fichiers, avec `Graphics/` et manifeste SHA-256 (vérifié) |

---

## Étape 1 — Connexion et initialisation

| # | Action | Valeur/Chemin |
|---|--------|---------------|
| 1.1 | Aller sur https://acs.manuscriptcentral.com/ | |
| 1.2 | Se connecter (ou créer un compte « Author ») | Compte du corresponding author (Serge Guy Nana Engo) |
| 1.3 | Cliquer **« Author Dashboard »** → **« Start New Submission »** | |
| 1.4 | Sélectionner **« Journal of Chemical Information and Modeling »** | JCIM dans la liste déroulante |
| 1.5 | Sélectionner le type **« Research Article »** | |

---

## Étape 2 — Type, Titre et Résumé

| # | Action | Valeur |
|---|--------|--------|
| 2.1 | **Type** | Research Article |
| 2.2 | **Titre** | African Natural-Product-Inspired Antimalarial Polypharmacology: Computational Resistance Hypotheses |
| 2.3 | **Résumé** _(copier-coller du .tex, max ~250 mots)_ | Le résumé commence par « Polypharmacology could make antimalarial discovery less vulnerable to single-target resistance… » — disponible dans `P1_V6_Integrated_Polypharmacology_RRS.tex` lignes 27–52. Inclure le paragraphe complet. |
| 2.4 | **Abstract/TOC Graphic** — sélectionner le fichier | Uploader `p1_v6_toc_graphic_ACS.tiff` (3.25×1.75 in, 300 dpi, RGB, LZW) |
| 2.5 | Vérifier que le TOC graphic apparaît correctement dans l'aperçu | L'aperçu montre l'image redimensionnée au format ACS standard |

---

## Étape 3 — Upload des fichiers

### Ordre recommandé ACS pour LaTeX :

| # | Champ dans Paragon Plus | Fichier à uploader | Note |
|---|------------------------|-------------------|------|
| 3.1 | **Manuscript File** (PDF) | `P1_V6_main.pdf` | Le PDF compilé final — **ACS préfère PDF pour la review** |
| 3.2 | **LaTeX Source Files** (optionnel mais recommandé) | Option 1 : zip contenant les fichiers ci-dessous. Option 2 : uploader chaque fichier séparément | Si LaTeX est demandé, voir §7 |
| 3.3 | **Supporting Information** | `Supporting_Information.pdf` | Nommé exactement **Supporting_Information.pdf** (convention ACS) |
| 3.4 | **Cover Letter** | `Cover_Letter_P1_V6.pdf` | 1 page, datée 10 août 2026 |
| 3.5 | **Table of Contents Graphic** | `p1_v6_toc_graphic_ACS.tiff` | **Format requis ACS :** TIFF RGB 300 dpi, 3.25×1.75 in (975×525 px) |
| 3.6 | **Figure files** _(séparément si demandé)_ | `Figure_2_rrs_mutation_profiles.pdf`<br>`Figure_3_exploratory_metric_relationships.pdf`<br>`Figure_S_targetwise_profile_summary.pdf`<br>`Figure_S_chemical_space_coverage.pdf` | ACS peut demander les figures en fichiers séparés au format EPS/PDF/TIFF |

### Règles de nommage ACS Paragon Plus :
- Le fichier main doit s'appeler `manuscript.pdf` ou `P1_V6_main.pdf` (accepté)
- Supporting Information = **`Supporting_Information.pdf`** (exactement ce nom — convention ACS)
- Cover Letter = `Cover_Letter_P1_V6.pdf` (accepté)
- TOC Graphic = `p1_v6_toc_graphic_ACS.tiff` (accepté tout nom décrivant le contenu)

---

## Étape 4 — Auteurs

ACS exige la saisie manuelle de chaque auteur dans Paragon Plus (même si le .tex contient déjà les noms).

| # | Auteur | Prénom | Nom | Email | Affiliation | ORCID requis |
|---|--------|--------|-----|-------|-------------|--------------|
| 4.1 | **Corresponding** | Serge Guy | Nana Engo | — (renseigner dans Paragon Plus) | University of Yaoundé I, Cameroon | **✅ Oui — obligatoire ACS** |
| 4.2 | Co-auteur | Myke Vital Sao | Temgoua | myke-vital.sao@facsciences-uy1.cm | University of Yaoundé I, Cameroon | **✅ Oui** |
| 4.3 | Co-auteur | Jean-Pierre | Tchapet Njafa | — | University of Yaoundé I, Cameroon | **✅ Oui** |
| 4.4 | Co-auteur | Penabei | Samafou | — | Université de Sherbrooke, Canada | **✅ Oui** |
| 4.5 | Co-auteur | Wilfred Fon | Mbacham | — | University of Yaoundé I, Cameroon | **✅ Oui** |

### Instructions :
1. Cliquer **« Add Author »** pour chaque auteur
2. Renseigner **prénom, nom, email, affiliation** exactement comme dans le .tex
3. Saisir le numéro **ORCID** (format `0000-0002-XXXX-XXXX`) — chaque auteur doit avoir un ORCID
4. Le corresponding author **doit** être coché comme **« Corresponding Author »**
5. Vérifier l'**ordre des auteurs** : Temgoua → Tchapet Njafa → Samafou → Mbacham → **Nana Engo** (dernier = corresponding)

---

## Étape 5 — Reviewers

| # | Action | Recommandation |
|---|--------|---------------|
| 5.1 | Suggérer des reviewers (optionnel mais utile) | Préparer 3–5 noms d'experts en : (a) chimie computationnelle anti-paludisme, (b) chimie des produits naturels africains, (c) docking/RRS. |
| 5.2 | Opposer des reviewers (optionnel) | Saisir max 3 noms de concurrents directs ou collaborateurs récents |
| 5.3 | **Note ACS :** l'éditeur sélectionne les reviewers ; les suggestions ne sont pas contraignantes mais prises en compte | |

---

## Étape 6 — Détails et Commentaires

| # | Champ | Valeur |
|---|-------|--------|
| 6.1 | **Funding sources** | Aucun financement spécifique déclaré (le manuscrit dit « no competing financial interest »). Si applicable, saisir l'organisme et le numéro de subvention. |
| 6.2 | **Cover letter comments** (optionnel) | Texte libre résumant la contribution (déjà dans la cover letter PDF) |
| 6.3 | **Special issue** (si applicable) | Non |
| 6.4 | **Has this manuscript been submitted before?** | Non |
| 6.5 | **Are there any ethical concerns?** | Non |
| 6.6 | **SI for review only** | Décocher si le SI doit accompagner la publication ; cocher si review-only |
| 6.7 | **Déclarations complémentaires** (si demandé par le formulaire) | • No competing financial interest<br>• AI-assisted code/data-analysis use disclosed in Acknowledgments<br>• Data available at GitHub with checksum manifest |

---

## Étape 7 — Fichiers LaTeX (optionnel — pour production après acceptation)

ACS demande les fichiers source LaTeX uniquement **après acceptation**. Pour la soumission initiale, le PDF suffit. Après acceptation, fournir :

| Fichier | Chemin dans le package |
|---------|----------------------|
| `P1_V6_main.tex` | `submission_ACS_P1V6/P1_V6_main.tex` |
| `P1_V6_main.bbl` | `submission_ACS_P1V6/P1_V6_main.bbl` |
| `P1_V6_main.aux` | `submission_ACS_P1V6/P1_V6_main.aux` |
| `P1_V6_SM.tex` | `submission_ACS_P1V6/P1_V6_SM.tex` |
| `P1_V6_SM.bbl` | `submission_ACS_P1V6/P1_V6_SM.bbl` |
| `P1_V6_SM.aux` | `submission_ACS_P1V6/P1_V6_SM.aux` |
| `Sao_Chim_Space.bib` | `submission_ACS_P1V6/Sao_Chim_Space.bib` |
| `Sao_Chim_Space.bib` | `submission_ACS_P1V6/Sao_Chim_Space.bib` (bibliographie commune main/SM) |
| `Cover_Letter_P1_V6.tex` | `submission_ACS_P1V6/Cover_Letter_P1_V6.tex` |
| Figures ×3 | `submission_ACS_P1V6/Figure_*.pdf` |
| TOC graphic PDF | `submission_ACS_P1V6/p1_v6_toc_graphic.pdf` |
| TOC graphic TIFF | `submission_ACS_P1V6/p1_v6_toc_graphic_ACS.tiff` |

→ Compresser l'ensemble dans une archive zip `P1_V6_source.zip` avant l'upload.

---

## Étape 8 — Vérification finale et soumission

| # | Action | Détail |
|---|--------|--------|
| 8.1 | Lire l'**aperçu PDF** généré par Paragon Plus | Vérifier que tous les caractères (grec, SI, formules) s'affichent correctement. **Attention :** le convertisseur ACS peut avoir des problèmes avec certains caractères Unicode — vérifier les lettres accentuées et le texte en indice/exposant. |
| 8.2 | Vérifier les **métadonnées extraites** par le système | Titre, résumé, auteurs, mots-clés — s'assurer que tout a été correctement parsé depuis le PDF |
| 8.3 | Vérifier le **Supporting Information** | S'assurer que le PDF du SI s'ouvre correctement (7 p.) |
| 8.4 | Vérifier le **TOC Graphic** | L'image apparaît-elle dans l'aperçu aux bonnes dimensions ? |
| 8.5 | Vérifier la **Cover Letter** | Datée, signée, fichier attaché |
| 8.6 | **Cliquer « Approve Submission »** | Confirmation finale |

---

## Récapitulatif des fichiers à uploader

| Fichier | Taille | Rôle |
|---------|--------|------|
| `P1_V6_main.pdf` | ~464 KB | Main manuscript (19 p.) |
| `Supporting_Information.pdf` | ~369 KB | Supplementary Information (7 p.) |
| `Cover_Letter_P1_V6.pdf` | ~130 KB | Cover letter (1 p.) |
| `p1_v6_toc_graphic_ACS.tiff` | ~Variable | TOC graphic (3.25×1.75 in, 300 dpi, RGB) |
| `Figure_2_rrs_mutation_profiles.pdf` | ~Variable | Figure séparée |
| `Figure_3_exploratory_metric_relationships.pdf` | ~Variable | Figure séparée |
| `Figure_S_targetwise_profile_summary.pdf` | ~Variable | Figure SI séparée |
| *(après acceptation)* `P1_V6_source.zip` | ~Variable | Sources LaTeX complètes |

---

## Problèmes connus ACS Paragon Plus (checklist de sécurité)

| Risque | Mitigation |
|--------|-----------|
| L'aperçu PDF modifie la mise en page | Toujours **télécharger l'aperçu PDF généré par le système** et vérifier page par page |
| Caractères accentués mal rendus (Yaoundé, indices) | Vérifier que `é`, `è`, `ê` s'affichent dans l'aperçu |
| Tableaux larges dépassent des marges | Les tableaux `tabularx` de P1 V6 passent — vérifier dans l'aperçu |
| Supporting Information mal nommé | **Doit** s'appeler `Supporting_Information.pdf` — sinon le système ne le reconnaît pas |
| TOC graphic trop grand/ratio incorrect | Notre TOC est exactement 3.25×1.75 in (ratio 1.857) — **conforme ACS** |
| Références non résolues dans l'aperçu | Les `.bbl` et `.aux` doivent accompagner le .tex — déjà présents dans le package |

---

## Notes par action

| # | Action | Qui |
|---|--------|-----|
| 0.1 | Créer/connecter les ORCID des 5 auteurs | Tous les auteurs |
| 0.2 | Se créer un compte Paragon Plus | S.G. Nana Engo (corresponding) |
| 8 | Soumettre le manuscrit | S.G. Nana Engo |
| Post-soumission | Suivre le statut dans Author Dashboard | S.G. Nana Engo |

---

## Temps estimé de soumission
- **Configuration initiale** (ORCID, comptes) : 1–2 jours
- **Soumission dans Paragon Plus** (8 étapes) : ~30–45 min
- **Vérification finale** : ~15 min