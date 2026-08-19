# P2 Set-C — Processus détaillé des actions parallèles (13/08/2026)

> **Checkpoint de sécurité :** l’équilibrage `15288` a terminé 16/16. Le gate `15312` a passé le préflight. Les productions `15308` et `15313` ont été arrêtées fail-closed après détection de défauts de staging/compatibilité ; aucun résultat de production n’est reportable. Le launcher corrigé a passé `grompp` et un smoke test `mdrun` GPU de 10 pas ; le MDP 10 ns contient exactement 5 000 000 pas. La soumission finale `15319 → 15320` est active ; `15320_0` confirme 5 000 000 pas / 10 ns avec GPU PP/PME. Les 15 autres tâches restent sérialisées sous `%1`.

> **Contexte actualisé** : le témoin GPU `PP-01/PfDHFR-WT` (job 15270) est terminé ; il s’agit d’une vérification isolée, non d’une validation de cohorte.
> Machine : 48 CPU / 125 Go, un seul GPU NVIDIA A4000 disponible → une seule production GPU active à la fois.
> **Verdict GPU** : le benchmark terminé 15262 a validé l’offload mixte `-nb gpu -pme gpu -bonded cpu -update cpu` à 19.816 ns/jour, sans erreur fatale ni LINCS ; 15270 a passé `grompp` et ne montre pas d’erreur fatale/LINCS au dernier checkpoint. Statut autorisé : `GPU_PATH_STABLE_FOR_SERIAL_PRODUCTION`, pas `COHORT_VALIDATED`.
> `MD-RRS = NOT_COMPUTED` jusqu’à 16 lignes QC PASS (pilot, fail-closed).

> **Branche indépendante terminée :** LigandExplorer job `15272` a exécuté une annotation structurale CPU-only des ligands présents dans `2F6I`, `7F3Y`, `6UKJ` et `9N10` avec le backend GNN. `4GM2` est exclu (PfClpR, pas PfClpP). La provenance résout le commit `d47eea0d033bb2127ee6836445554881c59edc8e`. Le retour système est 0, mais l’audit fail-closed trouve 4 artefacts JSON de ligand-box pour `7F3Y`, 2 pour `6UKJ`, et aucun artefact de ligand-box pour `2F6I` ou `9N10` : statut final `COMPLETED_PARTIAL_REQUIRES_MANUAL_REVIEW`. Cette branche ne modifie ni le classement des candidats, ni le docking-RRS, ni le MD, ni le MD-RRS. Sortie : `results/ligandexplorer_annotation_20260812/`; revue : `results/ligandexplorer_annotation_20260812/annotation_manual_review.md`.

## 1. Objectif

Débloquer le MD-RRS pilot PP-01/PP-02 (16 systèmes) **sans interrompre** le témoin GPU actif :
1. Équilibrer les 15 autres systèmes (CPU seul, en parallèle du témoin).
2. Préparer la chaîne GPU aval (production en série sur le seul GPU).
3. QC trajectoires puis MD-RRS après complétude des 16.

## 2. État actuel (audit)

| Ressource | Statut |
|---|---|
| GPU A4000 (16 Go) | réservé à une seule production ; 15262 stable, 15270 témoin terminé |
| CPU | ~40 cœurs libres |
| RAM | ~119 Go disponibles |
| `set_c_preparation_20260812_v1/*` | 16/16 préparations/équilibrations PASS ; gate 15319 PASS ; production 15320 active sous `%1` |
| `results/md_systems/set_c/*` | ancienne racine non canonique ; ne pas réutiliser |
| `MD-RRS` | `NOT_COMPUTED` |

## 3. Étape 1 — Équilibrer les 15 autres (CPU, parallèle)

**Script** : `p2_setc_equilibrate.py` (`-nb cpu -pme cpu -update cpu`, aucun GPU).

**Soumission d’équilibrage historique** (racine versionnée obligatoire ; `15288` est terminé ; ne pas relancer l’équilibrage) :
```bash
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
ROOT="$PWD/results/md_systems/set_c_preparation_20260812_v1"
sbatch --export=ALL,P2_SETC_ROOT="$ROOT" scripts/p2_setc_equilibrate_final.sbatch
```
- `do-15%4` : auto-skip si `npt.gro` présent (ex. I164L).
- ~4×8 = 32 cœurs, ~12 Go × 4 ; ne vole pas les 8 cœurs `-pin on` du témoin.
- Durée : ~8–14 h/système, 4 lots → ~32–56 h.

**Vérif** : chaque système doit produire `npt.gro`, `npt.cpt`, `md.mdp`.

## 4. Étape 2 — Préparer la production GPU en série (sans lancer)

Un seul GPU → séquencement obligatoire. Le benchmark 15262 donne un ordre de grandeur conservateur de 10 ns / 19.816 ns/jour = **~12.1 h de production par système**, hors préparation, transfert et reprise ; la durée réelle sera recalibrée après la clôture de 15270. Pour 16 systèmes, prévoir **~8 jours de temps GPU brut** sur un seul A4000, et non une promesse d’ETA de soumission.

**Plan de cohorte** : après clôture propre du témoin 15270, vérifier les 16 manifests puis lancer les productions des systèmes équilibrés en série : PP-01 et PP-02 × PfDHFR (WT, N51I, C59R, S108N, I164L) et PfCRT (WT, K76T, K76A). Utiliser un chemin de sortie pilot versionné, un nom de système explicite par tâche et une dépendance `afterany` contrôlée afin qu’un échec individuel n’empêche pas les systèmes suivants ; chaque échec reste cependant `NON-PASS` et bloque le MD-RRS agrégé. **Prérequis de soumission** : le launcher GPU dédié doit être versionné et validé avec `#SBATCH --gres=gpu:1`, `#SBATCH --array=0-15%1`, `--system-name "$SYS"` et les flags offload mixtes ; `p2_setc_production.sbatch` est CPU-only et ne doit pas être réutilisé comme launcher GPU. Ne pas promouvoir le témoin comme résultat MD-RRS.

**Critère de passage GPU** : chaque production doit fournir un `production.xtc`, `production.tpr`, checkpoint et log non vides, sans fatal error/LINCS/NaN, avec températures et énergies contrôlées. Le verdict de stabilité GPU est révisable si 15270 ou un système de cohorte échoue ces contrôles.

## 5. Étape 3 — QC + MD-RRS (après 16 trajectoires complètes)

**Scripts vérifiés** (compile OK, env `malaria_md`) :
- `p2_setc_trajectory_qc.py` — bound-fraction (≤5 Å, ≥10 %, max_frames 2000).
- `p2_setc_md_rrs.py` — fail-closed : exige 16 lignes `qc_status=PASS`.

**Soumission** :
```bash
# afterany: produire le manifeste terminal même après un échec ; le wrapper reste fail-closed.
sbatch --dependency=afterany:${PROD_JOB_ID} \
  --export=ALL,P2_PRODUCTION_JOB_ID=${PROD_JOB_ID},P2_EQUILIBRATION_JOB_ID=${EQ_JOB_ID},P2_SETC_COHORT_MODE=pilot \
  scripts/p2_setc_qc_and_md_rrs.sbatch
```
**Sorties** : `set_c_trajectory_qc_pilot.csv`, `md_rrs_pilot_PP01_PP02.csv`, `post_production_manifest_pilot.json`. Les 16 systèmes doivent être présents avant le QC agrégé ; un QC individuel précoce est diagnostique seulement et ne peut pas déclencher MD-RRS.

## 6. Interdits (ne pas faire)

- Aucun 2ᵉ job GPU (1 seul A4000 → ralentirait le témoin).
- Ne pas toucher `set_c_publication_gpu_v2_20260812/` (sorties du témoin).
- Ne pas lancer QC/MD-RRS avant 16 trajectoires completes.
- Pas de réclamation manuscrit provenant d'un job incomplet.
- Pas de job ID historique en dur dans les wrappers réutilisables.

## 7. Résumé des commandes

```bash
# 1. Équilibration CPU (parallèle, job corrigé 15288)
ROOT="$PWD/results/md_systems/set_c_preparation_20260812_v1"
sbatch --export=ALL,P2_SETC_ROOT="$ROOT" scripts/p2_setc_equilibrate_final.sbatch

# 2. [après fin témoin + préflight] Production GPU séquentielle des systèmes restants
#    → 15 autres systèmes si PP-01/PfDHFR-WT est accepté ; sinon 16 systèmes
#    → ~12.1 h/système d’après le benchmark conservateur 15262
#    → production 15320 active sous %1 ; aprèsany contrôlé seulement pour le wrapper QC terminal

# 3. [après 16 prod] QC + MD-RRS pilot
# afterany: produire le manifeste terminal même après un échec ; le wrapper reste fail-closed.
sbatch --dependency=afterany:${PROD_JOB_ID} \
  --export=ALL,P2_PRODUCTION_JOB_ID=${PROD_JOB_ID},P2_EQUILIBRATION_JOB_ID=${EQ_JOB_ID},P2_SETC_COHORT_MODE=pilot \
  scripts/p2_setc_qc_and_md_rrs.sbatch
```