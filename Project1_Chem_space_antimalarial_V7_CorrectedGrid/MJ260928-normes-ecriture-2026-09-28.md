# Normes d'écriture scientifique — Malaria Journal : abstract, conclusion et manquements par section (P1 V8)

* **Manuscrit** : `submission_ACS_P1V8/P1_Integrated_Polypharmacology_RRS_Main_V8.tex` (5 914 mots LaTeX, 248 lignes) + `P1_Integrated_Polypharmacology_RRS_SM_V8.tex` (2 765 mots) + `tables/*.tex` (11 tableaux SM importés)
* **Venue cible** : *Malaria Journal* (BMC / Springer Nature, ISSN 1475-2875) — décision d'envoi 28/09/2026, après refus JCIM (V8, 16/09) et desk-reject Digital Discovery (27/09)
* **Date** : 2026-09-28
* **Portée** : normes de rédaction et conformité *Guide for authors* uniquement. Les contrôles de compilation (`0 ??` dans les logs, labels résolus) sont repris ici uniquement quand ils bloquent la soumission (§5, §6). **Les chiffres ne sont couverts par aucun gate** : vérification manuelle, protocole anti-hallucination (§7).

---

## 0. Méthode

1. *Guide for authors* de Malaria Journal lu en trois sources : PDF officiel `1475-2875.pdf` (mirror WHU — sections Research : title page, abstract, Background, Methods, references, figures), page `malariajournal.biomedcentral.com/submission-guidelines` (format souple, graphical abstract, cover letter) et page `link.springer.com/journal/12936/submission-guidelines` (template LaTeX SN encouragé ; section **Declarations obligatoire**, abstract ≤ 350 mots — extrait de la sous-page `/review`).
2. Relecture intégrale du main (§1–§3), du SM (§4) et des back-matters, avec comptages automatisés : longueur des phrases (> 45 mots), orphelins (`\label` sans `\Cref`/`\ref`), résolution des renvois croisés main ↔ SM, existence des figures.
3. Chaque allégation greffable a été revérifiée ; **une allégation est infirmée** (§7, `V5`) et **deux défauts de cohérence numérique sont confirmés** (`V2`, `V6`).
4. Toute référence destinée au `.bib` (ou toute exigence citée ici) doit rester sourcée dans §10 — règle anti-hallucination identique au dépôt ASOC.

**Seuils du guide retenus** : abstract ≤ **350 mots**, **structuré en 4 parties** (*Background* = contexte+but ; *Methods* = y compris **tests statistiques** ; *Results* ; *Conclusions* = implications) · abréviations minimisées, **0 citation dans l'abstract** · title page : noms, adresses et **e-mails de tous les auteurs** + auteur correspondant indiqué · **énoncé éthique dans Methods** (nom de l'organe, n° d'approbation — ou « not applicable » pour une étude in silico) · competing interests déclarés en cover letter **et** dans le manuscrit · **section `Declarations` obligatoire** (ethics/consent, competing interests, funding, availability of data, authors' contributions, acknowledgements) · cover letter : pourquoi MJ + politiques éditoriales + competing interests + **approbation de tous les auteurs** · références numérotées dans l'ordre de citation, crochets carrés · **envoi initial en format souple** (un fichier Word/PDF avec figures, légendes et SI ; formatage du journal exigé seulement **après le premier tour de relecture**) · template **Springer Nature LaTeX encouragé** (conversion donc **différée**, cf. §5) · légende figure : titre ≤ 15 mots + détail ≤ 300 mots, raster ≥ 300 dpi · graphical abstract téléversable après peer review · matériel reproductible librement disponible (Zenodo ✓).

Répartition du main : Introduction 417 mots · Methods 1 601 · Results 1 319 · Discussion 1 414 · Conclusion 63 · back matter 198. SM : 13 `\section`, 9 `\subsection`, 14 tableaux (3 inline + 11 `\input{tables/…}`), 2 figures. Références : 29 (`bibitem` du `.bbl`).

---

## 1. Abstract (main l. 36–44)

### 1.1 Conformité

| Norme | État |
|---|---|
| ≤ 350 mots | ✅ **233** (nettoyage LaTeX) — marge de +117 mots pour la restructuration |
| Aucune référence bibliographique | ✅ 0 `\cite` |
| Structure 4 parties Background/Methods/Results/Conclusions | ❌ **non structuré** — un bloc continu, question ouvrante (style ACS) |
| Abréviations minimisées | ⚠️ `PNS`, `ACSI`, `Vina` employés sans développement ; `RRS` développé ✅ |
| Tests statistiques cités dans Methods | ⚠️ seulement « After multiplicity correction » — nommer le test (Spearman, Bonferroni) |
| Autonome | ✅ question → méthode → résultats → conclusion calibrée |

### 1.2 Manquements

| # | Grav. | Manquement | Correction |
|---|---|---|---|
| **A1** | **haute** | **Abstract non structuré** alors que le guide impose 4 sections nommées. C'est l'item de non-conformité le plus visible (screening desk). | Restructurer en *Background / Methods / Results / Conclusions* ; budget 233 → ≤ 350 mots largement suffisant. La question ouvrante migre vers Background déclaratif. |
| **A2** | **haute** | Phrase de **61 mots** (« Per-target RRS was calculated … null range 99.4–100.5 % ») : panneau de mutations + exclusion de dénominateur + correction PfCRT + contrôle null empilés. Ouverture en question de **46 mots**. | Scinder en 3 phrases dans Methods/Results restructurés. La restructuration libère l'espace nécessaire. |
| **A3** | moyenne | **Graphe TOC dans l'abstract** (`\includegraphics{p1_v7_toc_graphic.pdf}`, l. 39–41) — sans objet BMC ; le graphical abstract se téléverse **séparément, après peer review**. | Retirer le bloc `center` de l'abstract ; conserver le fichier pour l'upload optionnel. |
| **A4** | moyenne | Surclaim : « \num{19913} computationally prioritized **synthesizable** leads » vs corps (l. 88) : « computational prioritization rather than **confirmed synthetic feasibility** ». | « prioritized, synthesizability-predicted candidates » ou supprimer « synthesizable ». |
| **A5** | moyenne | `PNS`/`ACSI` cités dans l'abstract sans jamais y être développés (ils ne le sont que Results l. 187). | Dans Conclusions restructuré, soit développer en 1 mot, soit ne mentionner que la corrélation neutre (ACSI). |
| **A6** | basse | Fermeture sur la réserve (« …they do not establish potency, target engagement, or resistance circumvention »). | En partition *Conclusions*, finir sur l'implication (hypothèses testables prioritaires), la réserve devenant l'avant-dernière phrase. |

---

## 2. Conclusion (main l. 223–224)

### 2.1 Conformité

| Norme | État |
|---|---|
| Réponse à la question (pas seulement reformulation) | ✅ « value is hypothesis generation: which chemotypes and target–mutation combinations should be tested next » |
| Aucune donnée nouvelle | ✅ aucun chiffre absent des Results |
| Aucune nouvelle citation | ✅ 0 `\cite` |
| Limites | ⚠️ implicites (« null findings and wild-type non-binding exclusions ») — les limites vivent en Discussion l. 221 |
| Implication / prospective | ⚠️ une seule phrase, aucune nommant la stratégie expérimentale (déjà §5.5) |

### 2.2 Manquements

| # | Grav. | Manquement | Correction |
|---|---|---|---|
| **C1** | moyenne | **Conclusion très courte (63 mots, 2 phrases)** et sans énoncé d'implication pour un lecteur malariologue (que faire avec les 5 candidats A* ?). | Ajouter 1 phrase reliant aux 5 candidats prioritaires (PP-15/05/06/11/13) et aux assays de §5.5 — sans nouveau chiffre. |
| **C2** | basse | La *abstract-Conclusion* (A6) et cette Conclusion doivent rester cohérentes après restructuration (test « conclusion creep »). | Test 2 colonnes après réécriture : une ligne par affirmation. |

---

## 3. Manquements par section — texte principal

### 3.1 `Introduction` (417 mots) → renommer `Background`

| Grav. | Manquement | Correction |
|---|---|---|
| **haute** | **Incohérence CPU-hours** : l. 49 « 500–1000 CPU-hours **per target-ligand combination** » vs Methods l. 57 « 500–1000 CPU-hours **per target** for full libraries » vs Discussion l. 210 « from an estimated 2600–5300 CPU-hours » pour 263 424 dockings. Lu littéralement, l. 49 est faux d'un facteur ~10⁴. | Corriger l. 49 en « per target for full libraries » (wording Methods) ; vérifier que 4 × (500–1000) ≈ 2600–5300 est cohérent (≈ 2000–4000, écart à documenter ou reformuler « 2600–5300 » en « ≈ 4 × 500–1000 »). |
| moyenne | Titre `Introduction` alors que la structure MJ s'ouvre sur **`Background`**, rédigé pour non-spécialiste, se terminant par « what is being reported ». | Renommer en `Background` ; la dernière phrase (« We asked whether … ») fait déjà office d'annonce — la formuler explicitement comme « This article reports … ». |
| basse | La contribution est annoncée en 3e paragraphe (l. 51) — acceptable, mais l'« accessibility gap » (l. 49) mène le lecteur hors malaria un moment. | Léger rééquilibrage : nommer le bénéfice malariologique avant le bénéfice computationnel. |

### 3.2 `Materials and Methods` (1 601 mots, 7 sous-sections)

| Grav. | Manquement | Correction |
|---|---|---|
| **haute** | **Phrase de 90 mots** (l. 78, règles de classes RRS A*/A/B/C/D) — la phrase la plus longue du manuscrit. | Découper : une phrase par classe ou liste à puces. |
| **haute** | **Énoncé éthique absent** : le guide exige une déclaration dans Methods (« A statement to this effect must appear in the Methods section »). Étude purement in silico → « Ethical approval: Not applicable. No human or animal data… » | Ajouter une mini-subsection `Ethics approval and consent to participate` en fin de Methods (ou premier item des Declarations, **et** une ligne dans Methods). |
| moyenne | **8 phrases > 45 mots** (72 : cible PfDHFR ; 65 : cible PfCRT ; 53 : grilles ; 50 : redocking ; 70 : DEKOIS ; 56 : comparaison deux bras ; **90** : classes RRS ; 61 : ACSI). | Scinder les 8 — concentration du défaut dans cette section. |
| moyenne | **Abréviations non développées au premier usage** : `PAINS` (l. 57), `QED` (l. 57), `ADMET` (l. 57), `PNS` et `ACSI` (premier emploi l. 80–81, développées seulement Results l. 187), `STRING` (l. 81). | Développer à l'entrée (règle BMC/MJ : abréviations définies au premier usage). |
| moyenne | Famille de tests ambiguë : « **Three** exploratory correlations were corrected with Bonferroni α = 0.017 » (l. 81) alors que Results en rapporte **cinq** (voir R1). | Définir explicitement les 3 hypothèses déclarées + statut des autres (exploratoires non corrigées). |
| basse | Premier renvoi de tableau : `\Cref{tab:dual_priority}` en Methods (l. 81) alors que Table 1 = `tab:rrs_main` (Results l. 99) → l'ordre de mention contredit la numérotation. | Retirer le `\Cref` de Methods (« in the joint prioritization readout (Results) »). |

### 3.3 `Results` (1 319 mots, 6 sous-sections)

| Grav. | Manquement | Correction |
|---|---|---|
| **haute** | **Multiplicité incohérente** (R1) : α = 0.017 = Bonferroni(3), mais `N_fav`–RRS (4ᵉ corrélation rapportée) est déclarée « significant at α = 0.017 » (l. 187) sans faire partie des 3 déclarées ; 5 corrélations rapportées au total (PNS–RRS, ACSI–RRS, RRS–WT, PNS–WT, N_fav–RRS). L'abstract aligne 3 + ACSI. | Déclarer la famille exacte (soit 4 avec `N_fav`–RRS, soit 3 + permutation séparée) dans Methods **et** Results **et** abstract, ou corriger le statut de `N_fav`–RRS. |
| **haute** | Phrase de **81 mots** (l. 99, ré-évaluation PfCRT + contrôle null). | Scinder en 3 (protocole / résultat / conséquence pour les classes). |
| moyenne | **Redondance Methods ↔ Results** : la justification du panel 4 cibles est répétée quasiment verbatim (l. 65 Methods vs l. 91 Results : « designed to probe mechanistically distinct antimalarial vulnerabilities … PfClpP … PfATP4 … »). | En Results, garder seulement ce qui est **nouveau** (la couverture observée) et renvoyer à Methods pour le rationnel. |
| moyenne | « Study's limited power » énoncé deux fois à 8 lignes d'intervalle (l. 189 fin Results **et** l. 197 Discussion, avec le même power analysis). | Une occurrence détaillée en Discussion (l. 197) ; en Results, une clause courte avec renvoi. |
| basse | « 94.1 % Lipinski-compliant » (bibliothèque, l. 57) vs « 100 % Lipinski and Veber » (cohort 17, l. 94) — deux populations, susceptible de confusion pour un relecteur. | Marquer explicitement « within the 17-member cohort » (déjà partiellement fait) et renvoyer au §Methods pour la bibliothèque. |

### 3.4 `Discussion` (1 414 mots, 5 sous-sections)

| Grav. | Manquement | Correction |
|---|---|---|
| moyenne | Le paragraphe « The study has substantial limitations » (l. 221) est **noyé dans la sous-section `Experimental validation strategy`** — convention BMC : sous-section `Limitations` identifiable. | Extraire en sous-section dédiée (ou renommer la sous-section « Validation strategy and limitations »). |
| moyenne | Dernière phrase de l. 221 (« The next experiments should combine biochemical … assays, resistance-mutant assays, orthogonal binding methods, and candidate-specific molecular dynamics ») **répète quasi verbatim** l'ouverture de §5.5 (l. 215). | Supprimer le doublon ; garder l'énoncé unique en ouverture de la sous-section. |
| basse | Power analysis en doublon avec Results l. 189 (cf. R-4). | Cf. R-4. |
| ✓ | Aucune phrase > 45 mots non signalée au-delà des 2 notées (48 : power ; 62 : rétrospective antimalarials) — les scinder. | 2 scissions. |

### 3.5 Back matter (sections ACS)

| Grav. | Manquement | Correction |
|---|---|---|
| **haute** | En-têtes ACS absents du standard MJ : `Associated Content` + `Supporting Information Available`, `Notes` (competing interests), `Data Availability`, `Acknowledgments` + environnement `acknowledgement` achemso (« No external funding »). **Aucune section `Declarations`.** | Remplacer par le bloc **Declarations** BMC : *Ethics approval and consent to participate* (Not applicable) · *Consent for publication* (Not applicable) · *Competing interests* (reprendre le texte de `Notes`) · *Funding* (« No external funding was received ») · *Availability of data and materials* (texte Data Availability, DOI Zenodo ✓) · *Authors' contributions* (texte existant ✓) · *Acknowledgements* (texte AI + remerciements). « Supporting Information » → « Additional file(s) / Supplementary Information ». |
| moyenne | **Title page** : e-mails d'**un seul** auteur sur 5 (`\email` M.V.S.T.) ; auteur correspondant non explicitement indiqué (`\correlemail` absent). Le guide exige e-mails pour **tous** les auteurs + corresponding indiqué. | Ajouter les 5 e-mails et marquer le corresponding author. |
| moyenne | Déclaration IA noyée dans Acknowledgments ; politique Springer Nature attend une disclosure lisible (usage IA dans la préparation) + « no generative AI as author » (déjà présent ✓). | Conserver le contenu, le placer sous l'intitulé attendu par le portail SN (section dédiée ou item Declarations). |
| basse | `Acknowledgments` → graphie BMC **`Acknowledgements`**. | Renommer. |

---

## 4. SM — `P1_..._SM_V8.tex` + `tables/*.tex`

### 4.1 Contrôles structurels (faits mesurés)

| Contrôle | Résultat |
|---|---|
| Taille | 2 765 mots, **13 `\section`**, 9 `\subsection`, 14 tableaux, 2 figures |
| Renvois main → SM | **12 `\Cref{SM-…}`**, tous résolus (labels vérifiés dans le SM **et** `tables/` : `tab:rrs_classes`, `tab:crossmetric`, `tab:admet`, `tab:druglikeness`, `tab:s_pns_sensitivity`, `tab:sm_retrospective_antimalarials`, `tab:sm_vina_distributions` ✓) |
| Renvois SM → main | 11 `\Cref{M-…}` (eq:rrs, sec:methods_*, tab:rrs_main, tab:dual_priority) — préfixe `M-` via `\externaldocument[M-]` |
| Logs | **0 `??`** dans les deux logs — mais logs du **10/09** alors que les `.tex` sont du **16/09** → voir V1 (§7) |
| Figures SM | 2 ; **`fig:targetwise_summary` jamais référencée nulle part** |
| Tableaux SM jamais pointés | **4** : `tab:physichem`, `tab:sm_redocking_validation`, `tab:sm_validation_datasets` (+ `fig:targetwise_summary`) — 0 `\Cref` dans SM comme dans main |
| Labels de sections jamais référencés | 22/23 labels `sec:` du main + la plupart du SM — **normal** (article à sections numérotées, pas de défaut de renvoi) |

### 4.2 Manquements de rédaction

| Grav. | Manquement | Correction |
|---|---|---|
| moyenne | 4 flottants SM jamais pointés (§4.1) — tables et figure produites mais non citées. | Citer chaque table dans la prose du SM correspondante (« Table S… ») ou retirer les flottants inutiles. |
| moyenne | Le SM emploie « Supporting Information » (vocabulaire ACS) ; attendu BMC : « Supplementary Information / Additional file ». | Remplacer à la conversion (§5) ; non bloquant au premier envoi souple. |
| basse | Le SM cite `M-sec:methods_*` mais aucune section du main ne renvoie `SM-sec:` hors les 4 renvois de validation — dépendance acceptable, à re-vérifier après restructuration de l'abstract. | Revérifier après Pass A. |

---

## 5. Conversion ACS → Malaria Journal — décision et checklist

**Décision (règle de moindre coût)** : le format de soumission MJ est **souple** (« manuscripts can be uploaded as a single Microsoft Word file… journal-specific formatting is required only once manuscripts have completed one round of peer review »). **Donc : envoyer le PDF achemso compilé (JCIM-style) en soumission initiale, sans conversion de template.** La conversion vers le template LaTeX Springer Nature (`sn-article`) ne se fera **que si** MJ la demande après le premier tour — ni maintenant ni en Pass A/B.

| # | Item | Blocage premier envoi ? |
|---|---|---|
| 1 | Abstract structuré 4 parties (A1) | **Oui** (screening) |
| 2 | Bloc `Declarations` + énoncé éthique Methods (E, M2) | **Oui** (obligatoire) |
| 3 | Title page : 5 e-mails + corresponding (E) | **Oui** (guide) |
| 4 | Cover letter MJ : pourquoi MJ + politiques + competing interests + approbation des 5 auteurs | **Oui** (le `Cover_Letter_P1_V8.tex` JCIM est obsolète ; le `Response_to_Reviewers` **ne pas** l'envoyer) |
| 5 | Recompilation & vérification du PDF (V1) | **Oui** (logs antérieurs au texte) |
| 6 | Renommer `Introduction` → `Background` | Souhaitable, non bloquant |
| 7 | Graphe TOC hors abstract (A3) ; graphical abstract en upload séparé optionnel | Souhaitable |
| 8 | Mots-clés (actuellement 8) — borne non précisée dans le guide PDF consulté ; pratique SN ≤ 10 → **garder 8**, vérifier au portail | Non bloquant |
| 9 | Références numérotées ordre de citation — style jcisd8 conforme en principe ; vérifier sur le PDF | Non bloquant (reformatage SN plus tard) |
| 10 | **Waiver APC Research4Life Group A** : demander **au moment de la soumission** (portail BMC) | **Oui** (financier) |
| 11 | Conversion template SN LaTeX + « Supporting Information » → « Supplementary Information » | **Non — différée** après 1er tour |

---

## 6. Synthèse par gravité

| Zone | Haute | Moyenne | Basse |
|---|---|---|---|
| Abstract (§1) | 2 | 3 | 1 |
| Conclusion (§2) | 0 | 1 | 1 |
| Sections principales (§3) | 5 | 10 | 5 |
| Back matter (§3.5) | 1 | 2 | 1 |
| SM (§4.2) | 0 | 2 | 1 |
| Process (§5, V1) | 1 | 0 | 0 |
| **Total** | **9** | **18** | **9** |

**Les 6 corrections à plus fort impact (ordre recommandé) :**

1. **Restructurer l'abstract en Background/Methods/Results/Conclusions** (A1+A2+A6) — règle non négociable du guide, premier point de screening.
2. **Ajouter le bloc `Declarations` + l'énoncé éthique `Not applicable` dans Methods** (§3.5, M2) — obligatoire ; sans cela le système de soumission signale un manque.
3. **Recompiler et revalider le PDF** (V1) — logs du 10/09 pour un texte du 16/09 ; le « 0 ?? » constaté porte sur un artefact périmé.
4. **Corriger l'incohérence CPU-hours** (l. 49 vs l. 57 vs l. 210) — défaut de cohérence interne qu'un relecteur calcule en 30 s (V2).
5. **Déclarer la famille de tests de multiplicité** (R1/V6) — 3 déclarées, 5 rapportées, 4ᵉ « significant » ; identique dans Methods, Results et abstract.
6. **Cover letter Malaria Journal + title page (5 e-mails, corresponding) + waiver R4L** (§5 items 3–4, 10) — condition d'entrée du portail.

Puis : scinder les 15 phrases > 45 mots (2 abstract + 8 Methods + 3 Results + 2 Discussion) ; développer PAINS/QED/ADMET/PNS/ACSI/STRING au premier usage ; extraire `Limitations` ; dédoublonner panel-rationale et power analysis ; retirer le graphe TOC.

---

## 7. Vérifications factuelles — allégations confirmées ou infirmées

| Allégation issue de la relecture | Vérification | Verdict |
|---|---|---|
| **V1** Logs à jour | `.log` = 10/09 12:25 ; `.tex` = 16/09 07:46 (main **et** SM) | ✅ **confirmé — recompiler avant envoi** |
| **V2** Contradiction CPU-hours | l. 49 « per target-ligand combination » vs l. 57 « per target for full libraries » vs l. 210 « 2600–5300 CPU-hours » pour 263 424 dockings (= 65 856 × 4 ✓) | ✅ **confirmé — l. 49 est erronée** |
| **V3** Moyennes RRS du tableau | PP-15 = (123.2+112.7+125.9+131.8+100.1+100.1)/6 = 115.6 ✓ ; PP-01 = 90.5 ✓ ; PP-17 = 73.2 ✓ ; PP-10 = 84.0 ✓ ; PP-02 = 100.1 ✓ | ✅ confirmé (toutes recalculées) |
| **V4** Comptages de classes | tableau : A* = 7 (PP-01/02/05/06/11/13/15), B = 4, C = 6 → 17 ✓ ; abstract « seven A*, four B, six C » ✓ | ✅ confirmé |
| **V5** « Six candidates 4/4, five A* » | `N_fav`=4 : PP-15, 05, 06, 11, 13, **03**(C) = 6 ; dont 5 A* ✓ | ✅ confirmé |
| **V6** Famille Bonferroni | Methods « Three exploratory correlations » vs 5 corrélations rapportées Results l. 187, dont `N_fav`–RRS déclarée significative à α = 0.017 | ✅ **confirmé — incohérence à corriger** |
| **V7** Cohérence abstract ↔ Results (corrélations) | ρ = −0.714 / +0.691 / 0.714 / −0.190 ; p = 0.0013 / 0.0021 / 0.465 — identiques | ✅ confirmé |
| **V8** 68 = 17 × 4 ; plages globales | −12.01 (PfCRT min) … −4.63 (PATP4 max) = plages par cible ✓ | ✅ confirmé |
| **V9** Renvois SM | 12 `SM-` + 11 `M-` tous résolus ; labels vérifiés dans SM **et** `tables/` | ✅ confirmé |
| **V10** Figures du main existent | 3 PDF présents dans `Graphics/` (TOC + 2 figures) | ✅ confirmé |
| **V11** « 0 ?? » = PDF sain | logs du 10/09 seulement (V1) | ⚠️ **valable pour l'artefact périmé, pas pour le texte courant** |

---

## 8. Enrichissement externe — risque de desk-reject Malaria Journal

Les motifs de desk-reject BMC/MJ, par ordre : **hors scope** (uniquement malaria — notre titre/abstract sont malaria-first ✓), **manque d'éthique/déclarations** (couvert Pass A), **format/langue**, puis **portée des conclusions**.

| ID | Grav. | Constat local | Norme externe | Action |
|---|---|---|---|---|
| **X1** | moyenne | Le corps ne contient aucune phrase reliant explicitement l'article aux *Aims & scope* de MJ (« malaria in its broadest sense », « bench to bedside **and to the field** ») ; la justification n'existera que dans la cover letter. | Comme pour ASOC, le relecteur anonyme lit le **manuscrit**, pas la cover letter. | 1 phrase de scope en fin de Background : contribution au volet **résistance/in silico** de la découverte antipaludique, ancrée en Afrique (65 856 molécules issues de NP africains). |
| **X2** | moyenne | Étude sans donnée humaine/animale : absence actuelle de toute mention éthique. | MJ : statement obligatoire dans Methods ; pour in silico : « Not applicable ». | Couvert par M2 + §5 item 2. |
| **X3** | moyenne | Résultats nuls assumés (DEKOIS AUC 0.45, PfCRT null, ACSI–RRS ns) — atout si cadré, risque si perçu comme « rien de nouveau ». | Les guides des résultats négatifs (Lakens, Altman & Bland) exigent taille d'effet + intervalle, pas seulement ns. | Le papier le fait déjà (IC 95 %, power analysis n=17, permutation) ✅ — **ne rien ajouter**, mais l'annoncer dans Background (« a calibrated negative result is informative »). |
| **X4** | basse | Preprint : Zenodo DOI public (10.5281/zenodo.22696778) ; ChemRxiv non déposé. | SN autorise les preprints ; MJ offre le partenariat « In Review » (Research Square, gratuit, optionnel). | Optionnel : activer In Review ou déposer ChemRxiv **avant** soumission pour timestamper. |
| **X5** | basse | Waiver R4L Group A : à demander au portail. | Règle : demande **au moment de la soumission**. | Couvert par §5 item 10. |

**Points déjà acquis** : scope malaria ✓ ; abstract < 350 ✓ 0 citation ✓ ; chiffres cohérents (§7) ; renvois résolus ✓ ; Zenodo + manifeste de checksums ✓ ; limitation/power analysis au-dessus de la médiane ✓ ; AUC DEKOIS déclarée **contre** nous (honnêteté) ✓ ; 29 références (pas de limite MJ, mais « avoid excessive referencing » — 29 est sobre) ✓.

---

## 9. Plan d'action — 3 passes

**Pass A — bloquant (avant toute rédaction fine)**

> Ordre : ce §9 prime sur §6 en cas de divergence.

1. **Recompiler** main + SM (pdflatex + bibtex + xr), vérifier `0 ??`, `0 undefined`, rafraîchir les logs (V1).
2. **Restructurer l'abstract** en Background/Methods/Results/Conclusions ≤ 350 mots (A1, A2, A4, A5, A6) ; retirer le graphe TOC (A3).
3. **Éthique + Declarations** : ligne « Ethical approval: Not applicable » dans Methods ; bloc Declarations complet (§3.5) en remplacement de Associated Content/Notes/Data Availability/Acknowledgments.
4. **Title page** : 5 e-mails + corresponding author.
5. **Cover letter Malaria Journal** (4 points du guide : suitability, policies, competing interests, approbation des 5 auteurs) ; exclure `Response_to_Reviewers` du paquet.
6. **Waiver R4L** coché au portail.

**Pass B — forces argumentatives (un relecteur les posera)**

7. **V2** : corriger « per target-ligand combination » (l. 49) et réconcilier avec 2600–5300 CPU-hours.
8. **R1/V6** : déclarer la famille Bonferroni exacte (Methods + Results + abstract).
9. Scinder les 15 phrases > 45 mots (priorité : classes RRS 90 w, PfCRT 81 w, panneau cibles 72 w).
10. Développer PAINS, QED, ADMET, PNS, ACSI, STRING au premier usage ; retirer `\Cref{tab:dual_priority}` de Methods.
11. **X1** : phrase de scope MJ en fin de Background ; renommer `Introduction` → `Background`.

**Pass C — lisibilité & finitions**

12. Extraire `Limitations` (l. 221) ; supprimer la phrase dupliquée §5.5 ; dédoublonner le power analysis (R-4).
13. Dédoublonner le rationnel panel Methods l. 65 ↔ Results l. 91.
14. SM : citer ou retirer `tab:physichem`, `tab:sm_redocking_validation`, `tab:sm_validation_datasets`, `fig:targetwise_summary`.
15. Relecture PDF finale : 3 figures, 2 tables main, 14 tables SM, test 2 colonnes abstract ↔ Conclusion (C2).

**Hors périmètre (décision explicite)** : conversion au template Springer Nature LaTeX, reformatage des références, renommage Supporting → Supplementary Information — **différés après le premier tour de relecture** (§5).

---

## 10. Sources consultées (2026-09-28)

Toute norme invoquée ici doit rester sourcée dans cette liste ; toute référence bibliographique ajoutée au `.bib` doit d'abord être vérifiée via l'API CrossRef (protocole anti-hallucination).

**Guide for authors Malaria Journal**
- PDF officiel *Instructions for Malaria Journal authors* (ISSN 1475-2875, mirror `apps.lib.whu.edu.cn/ensci/editnew/upfile/1475-2875.pdf`) — sections Research : title page, abstract structuré 350 mots, Background, statement éthique dans Methods, competing interests en cover letter, références numérotées, légendes figure/table, 300 dpi.
- `malariajournal.biomedcentral.com/submission-guidelines` — format souple du premier envoi, cover letter, graphical abstract après peer review.
- `link.springer.com/journal/12936/submission-guidelines` — template LaTeX SN encouragé ; `…/review` : « Declarations section obligatoire ; Abstract ≤ 350 mots ».
- Article exemple Afify & Potter, *Malar J* 19:127 (2020) — mise en page réelle des *Ethics declarations* (Ethics approval / Consent / Competing interests).

**Contexte décision 28/09 (paquet de soumission)**
- Refus JCIM de la V8 (16/09/2026) ; desk-reject Digital Discovery DD-ART-09-2026-000744 (27/09/2026) ; file d'attente validée : Malaria Journal → Acta Tropica → PLOS NTDs → J. Cheminformatics → PLOS ONE/Sci Reports.
- Research4Life Group A (Cameroun) : waiver APC intégral BMC/Springer Nature — demande à la soumission.
- Dépôt Zenodo : DOI 10.5281/zenodo.22696778 (MIT, manifeste de checksums).
