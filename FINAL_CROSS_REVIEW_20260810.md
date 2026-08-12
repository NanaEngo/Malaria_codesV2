# Revue Adversaire Finale Croisée — Packages P1 V6 / P2 / P3 / P4 / P5

**Date :** 10 août 2026 · **Auteur :** revue adverse automatisée + humaine (auteur)
**Périmètre :** claims ↔ preuves, prose, formatage, cohérence croisée inter-packages — avant tout dépôt.

---

## Résumé exécutif

| Package | Journal | Compile | Claims↔preuves | Verdict |
|---|---|---|---|---|
| **P1 V6** | JCIM | ✅ 19 p. main | ✅ audité (2 corrections) | **PRÊT** |
| **P2** | JCIM | ✅ 25 p. main / 3 p. SM | ✅ audité (4 corrections) | **PRÊT** |
| **P3** | J. Cheminformatics | ✅ 13 p. main | ✅ cohérent BMAD | **PRÊT** |
| **P4** | J. Cheminformatics | ✅ 14 p. main | ✅ cohérent DAR | **PRÊT** |
| **P5** | J. Cheminformatics | ✅ 13 p. main | ✅ cohérent DAR | **PRÊT** |

**6 incohérences trouvées et corrigées.** Aucune restante.

---

## 1. Corrections appliquées (claims ↔ preuves)

### C1 — DEKOIS PfDHFR : P2 citait 0.509, valeur canonique = 0.450 ⚠️ MAJEUR
- **Preuve canonique :** `Project1_..._V2_CorrectedGrid/results/v2_dekois/dekois_v2_roc_auc.csv` → `roc_auc = 0.450104`, CI [0.3666, 0.5314], `ef_5pct = 0.000000`. BMAD : « DEKOIS V2 AUC = 0.45 [0.37, 0.53] ». P1 V6 : 0.45 [0.37, 0.53].
- **Écart :** P2 main L188 + L272 citaient « ROC-AUC 0.509 » ; Table S0 : 0.509 avec EF5% 0.51.
- **Correction :** main ×2 → `\num{0.450}` ; Table S0 → `0.450` et EF5% → `0.00` (valeur réelle du CSV canonique).
- **Pourquoi ça compte :** une valeur obsolète (0.509) contredit le manuscrit compagnon P1 V6 et le rapport BMAD ; un reviewer croisé P1/P2 détecterait la divergence.

### C2 — Table S0 P2 : ligne PfClpR copiée de PfATP4 (1.000/2.00/1.810) ⚠️ MAJEUR
- **Preuve :** `p1_enrichment_chembl_benchmark.csv` ne contient **que 3 cibles** (PfDHFR, PfCRT, PfATP4) — pas de PfClpP/PfClpR. Le MMV Malaria Box n'a jamais été docké sur 4GM2.
- **Écart :** la ligne PfClpR répétait exactement les valeurs PfATP4 (1.000 / EF5% 2.00 / BEDROC 1.810) — copier-coller non sourcé.
- **Correction :** ligne PfClpR → `{not evaluated}` ; caption précisé (« three targets with MMV docking data »).

### C3 — P2 : « across the four targets » (MMV) → « three evaluated targets » ⚠️
- Le MMV n'a couvert que 3 cibles. Corrigé main L188 + L272 (le PfClpP/4GM2 n'a pas de valeur MMV).

### C4 — P1 V6 : « the raw poses remain subject to independent structural review » = résidu de register 🟡
- Le register a été levé (`INTERNAL_WORK_AUTHORIZED`, décision auteur 10/08). La phrase « remain subject to review » contredisait l'état du register et sonnait « rapport en cours ».
- **Correction :** main + cover letter → « archived with full provenance in the repository for independent inspection ».

### C5 — P1 V6 : « MMV across the four targets » → « three targets with docking data » 🟡
- Cohérence avec la même correction C3 dans P2 (le CSV source n'a que 3 cibles).

### C6 — Table S0 P2 : ligne « PfDHFR Vina redock RMSD <2.0 » → {N/A} 🟡
- Le texte dit « MTX redocking failed (RMSD ≈ 30 Å) » — la ligne affichait <2.0, contradiction interne. Corrigé en {N/A} (cohérent avec caption).

---

## 2. Claims vérifiés et CONFORMES (pas de correction)

### P1 V6 (JCIM)
| Claim | Preuve | Statut |
|---|---|---|
| 65,856 molécules ; 396 ANP + 454 synthétiques ; 19,913 leads | BMAD §P1 | ✅ |
| Cohorte 17 membres ; 68/68 paires passent la gate géométrique | gate automatisée + register | ✅ |
| Scores −7.91 à −4.63 kcal/mol | Table Vina | ✅ |
| RRS : A*:6, B:5, C:5, D:1 ; étendue 68.2–111.7 | `c_rrs_classification.csv` | ✅ |
| PNS–RRS ρ=−0.559, ACSI–RRS ρ=−0.132, RRS–WT ρ=−0.433 | `cross_metric_matrix.csv` | ✅ |
| Redocking 5/5 alignables, MTX exclu (RMSD ≈ 30 Å) | Table S0 | ✅ |
| DEKOIS 0.45 [0.37, 0.53] | `dekois_v2_roc_auc.csv` | ✅ |
| PfClpP = 2F6I (triade Ser252/His223/Asp219), 4GM2 exclu | PDB | ✅ |

### P2 (JCIM)
| Claim | Preuve | Statut |
|---|---|---|
| 17 candidats × 8 états = 136 systèmes ; exhaustiveness 64 | scripts + CSVs | ✅ |
| MD : 40 ns (4×10 ns), 310.15 K ; PfCRT(214) et PfATP4(438) liés ; PfClpP(164)/PfDHFR(201) dissociés | trajectoires PBC-unwrapped | ✅ |
| MM-GBSA 214-PfCRT = −18.25 ± 0.40 kcal/mol | gmx_MMPBSA | ✅ |
| ACSI : 2/17 (11.8 %) > 0.70 ; moyenne 0.543 | `c_acsi_scores.csv` | ✅ |
| Tartarus ρ ≈ 0 (p ≈ 0.09) | BMAD ρ=0.013, p=0.091 | ✅ |
| 4GM2 = PfClpR, pas PfClpP | PDB | ✅ |

### P3 (J. Cheminformatics)
| Claim | Preuve | Statut |
|---|---|---|
| ECFP4 0.948 (canonique 0.9475), TFP 0.876, TNE 0.722 | job 12698 + BMAD | ✅ |
| Hybrid 0.888 (0.8876) ; ablation QK Δ=−0.040 | job 12699 + BMAD | ✅ |
| QKS ≈ RBF (p=0.060) ; externe 0.817 vs 0.847 (p=0.021) | jobs 12700 + extval | ✅ |
| TNE 6.1× compression, 192 dims, 19,836 mol. | job 11872 | ✅ |
| Extval ChEMBL 22,447 mol ; ECFP4 0.960 | `p3_extval` | ✅ |
| PHCO 0.896 (0.8959 arrondi) | job 12698 | ✅ |

### P4 (J. Cheminformatics)
| Claim | Preuve | Statut |
|---|---|---|
| v12 : random 0.6724 > MCTS 0.6649 > GA 0.6453 > greedy 0.4278 | DAR P4 §6 | ✅ |
| MCTS vs random : t₁₉=−4.97, p=0.000085, Δ=−0.0075, CI [−0.0107, −0.0043] | DAR P4 | ✅ |
| HV front post-hoc 1.2366 ; t₁₉=6.95 vs GA | DAR P4 | ✅ |
| 20 seeds ; ablation 5 seeds ; power analysis | DAR P4 | ✅ |

### P5 (J. Cheminformatics)
| Claim | Preuve | Statut |
|---|---|---|
| Scaffold : ECFP4 0.8300 > GIN-TFP 0.8138 > GIN-TNE 0.8090 > GIN 0.8047 > CB 0.7867 | DAR P5 + ckpt | ✅ |
| Random : 0.9433 / 0.9084 / 0.8918 / 0.9098 / 0.9121 | DAR P5 | ✅ |
| p appariées (df=4) + BH-FDR : 0.0330/0.0330/0.0378/0.0002 | DAR P5 + audit v2 | ✅ |
| Leakage ChemBERTa +0.15 corrigé ; réplication 0.7908 | job 12889 log | ✅ |
| 25 fold×seed par split ; splits figés | `p5_canonical_panel.csv` | ✅ |

---

## 3. Prose et formatage

- **siunitx/cleveref :** tous les nombres des 5 mains sont dans `\num{}`/`\qty{}`/`\si{}` (les « decimals hors \num » du grep étaient des faux positifs : `{0.559` = intérieur de `\num{0.559}`). ✅
- **Résidus de rapport :** aucun « pending/TODO/provisoire » restant. ✅ (la seule occurrence « future work » restante est légitime : limitations).
- **Journal J. Cheminformatics :** en-tête « Contribution » ✅ (P3 ajouté, P4/P5 alignés), Highlights ✅ (ajoutés P4/P5), Declarations ✅, graphical abstracts optionnels 920×300 ✅.
- **Cover letters :** P1 V6 corrigée (même phrase register) ; P2 sans DEKOIS (aucun risque) ; P3/P4/P5 cohérentes avec les mains.

## 4. Points de vigilance résiduels (non bloquants, à garder en tête)

1. **P1 V6 (19 p.) vs V4 (18 p.)** : le nombre de pages a légèrement changé après les corrections — vérifier que le format JCIM (20 p. max main) reste respecté. **19 p. OK.**
2. **P2 : le MD-RRS complet reste en attente** — les anciens jobs 15106/15111 sont supersédés; le témoin isolé 15254→15259→15260 est en cours et ne peut pas produire à lui seul un MD-RRS de cohorte. Le wording manuscript ne doit être mis à jour qu'après QC complet du panneau.
3. **Zenodo P3** : DOI réservé, upload différé par l'auteur — mention cohérente dans la Data Availability.
4. **PfClpP naming** : P1 V6 utilise correctement PfClpP (2F6I) et P2 utilise PfClpR (4GM2, avec note d'identité) — pas de conflit car chaque manuscrit documente sa propre cible. Les reviewers croisés verront une terminologie différente mais correctement justifiée.

---

## 5. Actions finales avant soumission (checklist)

- [x] Revue adverse croisée complète (claims↔preuves, prose, formatage)
- [x] Corrections appliquées + recompiles propres (P1 V6 19 p., P2 25/3 p., P3 13 p., P4 14 p., P5 13 p.)
- [x] Manifestes régénérés (0 fichier manquant)
- [ ] Lecture auteur finale (recommandé : P1 V6 + P2)
- [ ] Dépôt ACS (P1 V6, P2) / Springer (P3, P4, P5)
