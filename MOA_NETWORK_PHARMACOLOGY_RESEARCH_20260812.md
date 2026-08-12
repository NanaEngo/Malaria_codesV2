# Recherche web approfondie — MoA, Pharmacologie de réseau & Découverte de médicaments computationnelle

**Date :** 12 août 2026
**Statut :** Document de travail (recherche web 2024–2026) — aucune intégration manuscrit effectuée à ce stade.
**Provenance :** 4 recherches web parallèles (pharmacologie de réseau/causalité ; chimiogénomique PN ; PROTACs/nouvelles modalités ; évolution des benchmarks MoA).

> ✅ **Vérification Crossref effectuée le 12/08/2026** (API `api.crossref.org` + résolution `doi.org`) : **19/19 DOIs résolus**.
> - Les 5 DOIs marqués ⚠️ à l'origine (`btag010`, `gkaf1196`, `gkaf1186`, `bbag228`, `10.1016/j.cell.2026.02.016`) sont **tous valides** — marqueurs ⚠️ retirés.
> - 🔴 **1 rétraction détectée** : `10.1021/acs.jmedchem.4c01257` (Gangwal & Lavecchia, *J. Med. Chem.* 2025) — titre Crossref « RETRACTED: … ». **Remplacée** par Paerhati et al. 2026 (vérifiée).
> - 🟡 **1 correction de journal** : réf. 1 = *Pharmacological Reports* (pas *Inflammopharmacology*).

---

## Axe 1 — Pharmacologie des réseaux et causalité

### État de l'art 2024–2026

1. **De la corrélation à la causalité.** La pharmacologie de réseau classique (bipartite drug–target projeté sur le PPI interactome) reste corrélationnelle. La frontière actuelle intègre **l'inférence causale et le causal discovery** (algorithmes de type PC, modèles causaux structuraux, randomisation mendélienne) pour découpler les vraies interactions drug–target des confondants (effets batch, état cellulaire).

2. **Polypharmacologie expliquée par la topologie de réseau.** Les ligands multi-cibles réussis (MTDL) modulent des *choke points* topologiques ou modules fonctionnels du PPI (ex. hubs MAPK/JAK-STAT) → efficacité à dose plus faible, moins d'effets secondaires. **~30 % des thérapeutiques approuvées par l'EMA en 2022–2024 sont des MTDL.**

3. **Anticipation des off-targets.** La toxicologie prédictive moderne fusionne graphe chimique + réseau PPI tissu-spécifique + FAERS : le modèle anticipe si une interaction off-target *propage* vers un réseau toxique critique, pas seulement si elle existe.

4. **Causalité et combinaisons de médicaments.** Frameworks comme **CADS** utilisent l'inférence causale pour prédire les combinaisons synergiques en découplant les effets de gènes confondants — transposable au raisonnement RRS (causalité mutation → ΔG → phénotype).

### Références Axe 1

| # | Référence | DOI | Message clé |
|---|-----------|-----|-------------|
| 1 | Ryszkiewicz et al., *Pharmacological Reports* (2026) | 10.1007/s43440-026-00879-x | ~30 % des nouveaux médicaments EMA = MTDL ; pharmacovigilance réseau nécessaire |
| 2 | Zhang H. et al., *Bioinformatics* (2026) | 10.1093/bioinformatics/btag010 | CADS : inférence causale pour identifier les gènes essentiels et prédire les combinaisons synergiques |
| 3 | Qiao G. et al., *Bioinformatics* (2024) | 10.1093/bioinformatics/btae570 | Causal-enhanced DTI prediction (génération de graphes + information multi-source) |
| 4 | Liu Y. et al., *Signal Transduction and Targeted Therapy* (2026) | 10.1038/s41392-026-02631-6 | Multi-omics + IA + randomisation mendélienne pour liens causaux drug→maladie |
| 5 | Ogungbite & Sibiya, *CPT:PSP* (2026) | 10.1002/psp4.70272 | Knowledge graphs + GNN pour drug repurposing / polypharmacologie |
| 6 | Gangwal et al., *Chem Biol Drug Des* (2026) | 10.1111/cbdd.70372 | Cadre systèmes multi-omics + IA pour mécanismes multi-composants |

---

## Axe 2 — Application aux produits naturels et nouvelles modalités

### 2a. Chimiogénomique & prédiction de cibles IA sur produits naturels

**Difficultés intrinsèques :**
- Scaffolds complexes (macrocycliques, stéréochimie dense, systèmes fusionnés) mal capturés par les fingerprints 2D ;
- Données de bioactivité **sparses** (~5 % des entités criblées historiquement) ;
- Polypharmacologie intrinsèque de nombreux PN → casse les modèles binaires classiques.

**Solutions récentes :**
- **Prédiction de cibles par forme 3D** : 3DSTarPred (~76 % de succès) vs similarité 2D ;
- **GNN / graph transformers** préservant topologie et stéréochimie ;
- **Fusion multi-omiques + knowledge graphs** (GNPS + mining de BGC génomiques) ;
- **Bases de données PN** : COCONUT 2.0 (~700 000 structures), NPASS 2026 (>200 000 PN, >1 M records bioactivité, ADME-Tox), **ANPDB 2026** (>11 000 composés africains — pertinent pour la graine de 396 NP africains de P1), SuperNatural 3.0.

### 2b. Nouvelles modalités : PROTACs et molecular glues

**Saut paradigmatique :** modéliser le **complexe ternaire POI–dégradeur–E3 ligase** (coopérativité, effet crochet, ensembles conformationnels) — pas de SAR simple.

**Architectures 2024–2026 :**
- **PROTAC-STAN** (*Adv. Sci.* 2025) : attention ternaire profonde interprétable au niveau des résidus ;
- **SE(3)-PROTACs** (*Brief. Bioinform.* 2026) : deep learning équivariant géométrique pour la dégradation ;
- **SENTINEL** (*CSBJ* 2025) : GATs pour prédire les **off-targets** de dégradation (extension de la problématique off-target P2) ;
- **PROTAC-Splitter** (*J. Cheminformatics* 2026) : Transformer seq2seq pour décomposer warhead/linker/E3-ligand ;
- **PROTAC-PatentDB** (*Scientific Data* 2025) : jeu de données massif.

### Références Axe 2

| # | Référence | DOI | Message clé |
|---|-----------|-----|-------------|
| 7 | Paerhati et al., *Pharmaceuticals* (2026) | 10.3390/ph19020301 | Perspective IA dans la découverte PN — **remplace** Gangwal & Lavecchia, *JMC* 2025 (RÉTRACTÉE, voir note) |
| 8 | Yan et al., *JCIM* (2024) | 10.1021/acs.jcim.4c01445 | **3DSTarPred** : prédiction de cibles par forme 3D, ~76 % |
| 9 | Chandrasekhar et al., *NAR* (2025) | 10.1093/nar/gkae1063 | **COCONUT 2.0** : ~700 000 PN ouverts |
| 10 | Lin et al., *NAR* (2026) | 10.1093/nar/gkaf1196 | **NPASS 2026** : bioactivité quantitative + ADME-Tox |
| 11 | Betow et al., *NAR* (2026) | 10.1093/nar/gkaf1186 | **ANPDB** : >11 000 composés naturels africains |
| 12 | Ribes et al., *J. Cheminformatics* (2026) | 10.1186/s13321-025-01135-9 | PROTAC-Splitter : décomposition automatique |
| 13 | Chen et al., *Advanced Science* (2025) | 10.1002/advs.202508138 | PROTAC-STAN : prédiction interprétable de dégradation |
| 14 | Hu et al., *CSBJ* (2025) | 10.1016/j.csbj.2025.10.028 | SENTINEL : prédiction des off-targets de dégradation (GATs) |
| 15 | Kothakapu et al., *Brief. Bioinform.* (2026) | 10.1093/bib/bbag228 | SE(3)-PROTACs : géométrie équivariante |

> 🚨 **Référence rétractée détectée (vérification Crossref, 12/08/2026) :** Gangwal & Lavecchia, *J. Med. Chem.* 68(4):3948–3969 (2025), DOI 10.1021/acs.jmedchem.4c01257 — titre marqué **« RETRACTED »** par l'éditeur ACS. **Ne jamais citer cette version.** Remplacement vérifié : Paerhati et al., *Pharmaceuticals* 19(2):301 (2026), DOI 10.3390/ph19020301 (résolu Crossref).

---

## Axe transversal — Évolution des benchmarks MoA (utile pour P5)

- **DrugReflector** (*Science* 2025, DOI 10.1126/science.adi8577) : DL entraîné sur CMap/LINCS + active learning « lab-in-the-loop » ; >10× le taux de hits.
- **DECODE** (2026) : fusion SMILES + L1000 + Cell Painting ; information biologique comme *privileged information* en entraînement → inférence structure-only en zero-shot. **Précédent scientifique pour la décision de ne pas faire de mapping structurel LISH-MoA non audité.**
- **GPS** (*Cell* 2026, DOI 10.1016/j.cell.2026.02.016) : prédiction de profils d'expression à partir de la structure chimique.
- **MM-IDTarget** (*BMC Biology* 2025, DOI 10.1186/s12915-025-02256-1) : fusion cross-attention séquence+structure drug↔target pour polypharmacologie multi-cibles.
- **Résistance pathogène** : Blake et al. (*Nat. Commun.* 2025, DOI 10.1038/s41467-025-56425-5) — évolution de la résistance tétracycline par pression sélective ; revues antipaludiques (*Malaria J.* 2026) reliant MoA ↔ fitness des mutations (kelch13, dhps). **Parallèle direct avec le RRS P2 (N51I/C59R/S108N/I164L/K76T/K76A).**

---

## Implications concrètes pour les manuscrits

**P2 (RRS + polypharmacologie, JCIM) — le plus gros gain :**
1. **Réf. 1 (Ryszkiewicz 2026)** : « ~30 % des approbations EMA sont des MTDL » → cadre la cohorte polypharm (Set C) en Introduction.
2. **Réf. 14 (SENTINEL)** : prédiction d'off-targets par GATs légitime l'analyse cross-metric PNS/ACSI/RRS comme démarche « réseau ».
3. **Blake et al. 2025 + Malaria J. 2026** : ancrent le RRS dans la littérature « résistance ↔ mécanisme » (Discussion).
4. **Garde-fou (déjà acté)** : les scores docking/RRS/PNS caractérisent des propriétés au niveau cible — pas une assignation de MoA systémique (réf. Trapotsi 2022 déjà intégrée).

**P5 (GNN/Transformer) :**
- **MM-IDTarget** et **DECODE** justifient la position « multimodal fusion » ; DECODE fournit un précédent pour ne pas gonfler le benchmark LISH-MoA phenotype-only.

**P3 :**
- **3DSTarPred (réf. 8)** : même la prédiction de cibles SOTA bute sur la complexité des scaffolds PN → soutient le narratif « représentations complémentaires (TDA/TNE/QKS) plutôt que supériorité brute ».

**P1 :**
- **ANPDB 2026 (réf. 11)** : la graine de 396 NP africains s'inscrit dans une ressource panafricaine de 11 000+ composés — une phrase en Introduction pour situer la singularité de la librairie.

---

## Statut & prochaines étapes possibles

- [x] Vérification des DOIs via Crossref (12/08/2026) — 19/19 résolus, 1 rétraction remplacée, 1 journal corrigé
- [ ] Intégration ciblée dans P2 (Introduction/Discussion), P5, P3, P1 (au choix)
- [ ] Aucune modification manuscrit effectuée à la date de création de ce fichier
