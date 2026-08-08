# P1 V5 — Dossier de revue indépendante (prêt-à-signer)

**Statut :** à soumettre à un relecteur indépendant (ne pas signer soi-même — le
register ne doit jamais être édité pour simuler une revue).
**Objet :** décision d'acceptation des **4 ancres structurales** de P1 V5 et du
**pilote docking-RRS** (panel mutants), conformément à
`results/structural_pocket_review_signature_protocol.md`.

---

## 1. Ce qui est demandé au relecteur

Vérifier, pour **chacune des 4 cibles**, que :
1. **L'identité de la cible/récepteur est correcte** (PDB, isoforme, chaîne).
2. **L'ancre biologique est justifiée** (résidus/ligand co-cristallisé, pas un
   centroïde arbitraire).
3. **L'équivalence de frame récepteur PDB ↔ PDBQT est exacte** (rmsd = 0).
4. **Le smoke/gate composite est passé** : 17/17 paires par cible, contact ancre
   ≤ 10 Å, ≥ 90 % des atomes dans la boîte, centroïde rank-1 dans la boîte.
5. Apposer la signature (identité, date, décision PASS/FAIL par cible) selon le
   protocole de signature (artifact + SHA-256 + signature détachée + clé publique).

---

## 2. Registre cible — évidences vérifiées (jobs SLURM, 08/08/2026)

| Cible | PDB | Ancre biologique | Centre (Å) | Boîte | Gate 17/17 | Affinités (kcal/mol) | Contact ancre | Job |
|---|---|---|---|---|---|---|---|---|
| **PfDHFR** | 7F3Y (X-ray 2.25 Å) | MTX **A702** (copie du site catalytique ; contacts Phe58/Phe116/Ile14/Ile164/Cys15/Asp54 ; B702 = miroir dimère, A704 = surface) | [−3.596, −5.249, −58.677] | 18³ | ✅ | −4.86 … −6.35 | 3.0–3.5 Å | 12859 |
| **PfClpP** | 2F6I (X-ray 2.45 Å, EC 3.4.21.92, UniProt O97252) | Triade catalytique chaîne A **Ser252/His223/Asp219** (Ser289 actif = Ser252, offset 37) — 4GM2 = PfClpR retiré | [−24.276, 17.28, −2.901] | 28³ | ✅ | −5.05 … −7.03 | 3.3–8.9 Å (triade) | 12854 |
| **PfCRT** | 6UKJ (cryo-EM 3.30 Å) | **Y01 A501** (cholestérol hémisuccinate) — **PROXY membranaire**, pas un inhibiteur (caveat maintenu) | centroïde Y01 A501 | 28³ | ✅ | −5.12 … −7.91 | 3.0–4.1 Å | 12855 |
| **PfATP4** | 9N10 (cryo-EM 3.70 Å, Haile et al. 2025) | Machinerie P-type catalytique **CSDKTGT→D451** (resi 449–458) + charnière A-domaine **DPPR** (751–754) ; P-loop C-ter 1160 exclu (faux positif) | [122.712, 125.545, 91.411] | 25³ | ✅ | −4.63 … −7.57 | D451/DPPR | 12864 |

**Artefacts de vérification :**
- `results/p1_v5_pocket_centers_verified.json` — vérification des centres par gate biologique
- `results/v5_four_target_vina_affinities.csv` + `v5_four_target_vina_review_table.json` — table consolidée 17×4 (COMPLETE_17)
- `results/target_identity_audit.json` v2 — 4GM2→2F6I, MTX A702, Y01 proxy, 9N10 D451/DPPR
- Par paire : `results/vina_dock_<PDB>_<TARGET>_17/<complex>/execution_provenance.json` + `vina_dock.log`

**Rapport d'auto-vérification machine (pour accélérer la revue) :**
`python scripts/p1_v5_review_selfcheck.py` → `results/review_selfcheck_report.json`
(6/6 checks : table 17×4, frames rmsd=0 sur 8 récepteurs, dirs de run + provenance,
audit d'identité, register PENDING). ⚠️ Ce rapport **ne remplace pas** la revue
indépendante : il régénère les quantités depuis les artefacts bruts pour que le
relecteur puisse les recroiser en minutes (hachages inclus) — il doit vérifier
lui-même le sens biologique (ancres, isoformes, caveats).

---

## 3. ⚠️ Découverte scientifique nouvelle (08/08/2026) — isoforme PfCRT 7G8

**PDB 6UKJ est l'isoforme 7G8 (CQ-résistante), qui porte déjà la mutation K76T**
(SEQRES : `...LSVSVMNTIFAKRTL...` ; position structurale 76 = THR). Conséquences
pour le panneau de résistance PfCRT :
- Le « WT » du run 17×4 (6UKJ) est en réalité un **fond K76T** — il ne peut pas
  servir de baseline WT pour un ratio RRS.
- Le pilote RRS utilise donc, **tous dans le frame 6UKJ** (ancre Y01 conservée) :
  - **WT-K76** = révertant T76→K76 (allèle sauvage) ;
  - **K76T** = 6UKJ tel quel (variant 7G8 résistant) ;
  - **K76A** = T76→A76.
- Les fichiers mutants P2 (`PfCRT_K76T/K76A.pdb`) sont **incompatibles de frame**
  avec 6UKJ (rmsd ≈ 3.6 Å, 232 résidus manquants) → **non utilisés** dans P1 V5.

---

## 4. Pilote docking-RRS (P1.3) — panel mutant uniforme (nouveau)

**Protocole uniforme protéine-seule** (pour un ratio RRS sans biais de contenu
ligand) : strip HETATM/H₂O/H + obabel `-xr` (H polaires) + gate composite
identique aux runs WT. Panel de 8 récepteurs, frames vérifiées rmsd = 0.0 :

| Cible | Récepteurs | Source / mutation | Ancre | Boîte |
|---|---|---|---|---|
| PfDHFR | WT, N51I, C59R, S108N, I164L | 7F3Y, mutagenèse backbone-préservante (7F3Y chaîne A) | MTX A702 | 18³ |
| PfCRT | WT-K76 (révertant), K76T (7G8), K76A | 6UKJ chaîne A T76→K / tel quel / T76→A | Y01 A501 | 28³ |

- Scripts : `scripts/p1_v5_rrs_prepare_receptors.py`, `scripts/p1_v5_vina_dock_mutants.py`,
  `scripts/p1_v5_rrs_pilot.py` (RRS par-cible, protocole P2 : |ΔG_mut,t|/|ΔG_WT,t|×100,
  baseline WT |ΔG_WT,t| ≥ 5.0, sans mélange de cibles) et
  `scripts/p1_v5_rrs_merge_scores.py` (fusion des CSVs par cible).
- Jobs : **12894** (PfDHFR, 5×17) et **12895** (PfCRT, 3×17) — soumis après le fix
  anti-clobber (CSV par cible `v5_mutant_vina_scores_<TARGET>.csv`, fusionné ensuite).
- Smoke validés : PfDHFR_N51I × PP-01 = −7.90 kcal/mol (ancre 0.40 Å) ;
  PfCRT_K76A × PP-01 = −8.26 (0.36 Å) — les poses reproduisent les positions
  des ligands co-cristallisés.
- Sorties : `results/rrs_pilot/receptors/`, `results/rrs_pilot/vina_scores/`
  (+ `c_rrs_pilot_per_target_v5.csv` via `p1_v5_rrs_pilot.py` — PILOT, non
  accepté tant que le register n'est pas signé).

---

## 5. Checklist de vérification du relecteur

- [ ] 7F3Y chaîne A : MTX A702 bien la copie du site catalytique (B702 miroir, A704 surface)
- [ ] 2F6I : triade Ser252/His223/Asp219 complète ; 4GM2 (PfClpR) absent de toute revendication
- [ ] 6UKJ : Y01 traité comme proxy membranaire, pas d'inhibiteur
- [ ] 9N10 : D451/DPPR (CSDKTGT) + charnière A-domaine ; P-loop 1160 exclu
- [ ] Équivalence de frame PDB↔PDBQT vérifiée pour les 4 WT + 8 récepteurs RRS (rmsd = 0)
- [ ] Gate composite 17/17 par cible (WT 17×4) ; gate du panel RRS sur les smokes
- [ ] Cohérence du protocole RRS avec P2 (per-target, sans mélange)
- [ ] Aucun score consensus/RRS/PNS utilisé dans le manuscrit avant signature

---

## 6. Bloc de signature (à compléter par le relecteur indépendant)

```
reviewer_identity      : ________________________________________
affiliation            : ________________________________________
review_date            : ____________
PfDHFR  : PASS / FAIL    commentaire : ____________________________
PfClpP  : PASS / FAIL    commentaire : ____________________________
PfCRT   : PASS / FAIL    commentaire : ____________________________
PfATP4  : PASS / FAIL    commentaire : ____________________________
RRS pilot (P1.3) : APPROVED / NOT APPROVED    commentaire : ______
signature (clé privée)  : voir protocole (artifact + SHA-256 + détaché + clé publique)
```

Après signature : mettre à jour `results/structural_pocket_independent_review.json`
(`status = STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED`, `accepted_for_full_run = true`,
`reviewer_identity`, `review_date`, `signed_review_artifact`, `signed_review_sha256`,
décisions PASS par cible) — **par la procédure de signature, jamais par édition directe**.

---

## 7. Procédure de signature (commandes exactes, openssl/gpg)

Le relecteur indépendant génère sa propre paire de clés (ou utilise sa clé
institutionnelle/privée de confiance) et signe le register JSON :

```bash
cd Project1_Chem_space_antimalarial_V5_CorrectedGrid/results

# 1) (si pas de clé existante) générer une clé privée ed25519 + certificat auto-signé
openssl genpkey -algorithm ed25519 -out reviewer_ed25519_private.pem
openssl pkey -in reviewer_ed25519_private.pem -pubout -out reviewer_ed25519_public.pem

# 2) hasher le register (état AVANT signature)
sha256sum structural_pocket_independent_review.json

# 3) signer le register JSON (signature détachée)
openssl pkeyutl -sign -inkey reviewer_ed25519_private.pem \
    -rawin -in structural_pocket_independent_review.json \
    -out structural_pocket_independent_review.json.sig
sha256sum structural_pocket_independent_review.json.sig

# 4) vérifier (indépendant du signataire) avec la clé publique
openssl pkeyutl -verify -pubin -inkey reviewer_ed25519_public.pem \
    -rawin -in structural_pocket_independent_review.json \
    -sigfile structural_pocket_independent_review.json.sig

# 5) clé publique livrée par un canal de provenance séparé (pas le même commit)
sha256sum reviewer_ed25519_public.pem
```

Alternative gpg (si préférée) : `gpg --detach-sign structural_pocket_independent_review.json`
produit `.sig` ; la clé publique est exportée via `gpg --export --armor` et livrée
par un canal de confiance séparé. **Une signature ne peut pas être simulée** : le
register ne doit jamais être modifié pour simuler une revue (protocole §3).

Ensuite, mettre à jour le register **par la procédure** (script dédié ou mise à
jour humaine tracée) avec les champs signés : `reviewer_identity`,
`review_date`, `signed_review_artifact` (= chemin du `.sig`),
`signed_review_sha256`, `detached_signature_sha256`,
`trusted_public_key_artifact`, `trusted_public_key_sha256`, décisions PASS ×4,
`accepted_for_full_run = true`. Le gate consensus/RRS/PNS s'ouvrira alors.
